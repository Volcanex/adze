"""Filesystem helper that branches local-vs-remote per artist.

For local artists this is a thin wrapper over `_resolve_artist_file`-style
operations under `artists/<slug>/`. For external artists (those with a
`remote` block in their config — see external_artist.py) reads/writes
route through SSH to the remote Seed repo.

Surface (sync; existing endpoints are sync):

    read(slug, rel_path) -> str
    write(slug, rel_path, content) -> None
    list(slug, rel_dir=".") -> list[str]
    exec(slug, cmd, timeout=30) -> (exit, stdout, stderr)
    fetch_manifest(slug) -> dict   (always returns a dict; falls back to defaults)

Path-traversal guards apply to both backends. The remote backend rejects
unsafe paths *before* composing any SSH command — see `_safe_rel`.
"""
from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import List, Tuple

import external_artist


SSH_BASE_OPTS = [
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=3",
]


class RemoteError(Exception):
    """Base class for remote_fs failures."""


class RemoteAuthError(RemoteError):
    """SSH refused the key or the user."""


class RemoteUnreachable(RemoteError):
    """Could not reach the host (network, DNS, refused)."""


class RemoteCommandFailed(RemoteError):
    """A remote command exited non-zero."""

    def __init__(self, exit_code: int, stderr: str, cmd: str = ""):
        self.exit_code = exit_code
        self.stderr = stderr
        self.cmd = cmd
        super().__init__(f"remote command failed (exit {exit_code}): {stderr.strip()}")


class RemoteTimeout(RemoteError):
    """SSH timed out."""


class UnsafePathError(RemoteError):
    """A relative path tried to escape the artist root."""


# ---------------------------------------------------------------------------
# Path safety (applies to both backends)
# ---------------------------------------------------------------------------

def _safe_rel(rel_path: str) -> str:
    """Normalize a relative path; raise UnsafePathError on any escape attempt.

    Rejects: empty, NUL, absolute paths, backslashes, '..' segments. Returns
    the cleaned path (forward slashes, no leading slash).
    """
    if not rel_path or "\x00" in rel_path:
        raise UnsafePathError("empty or contains NUL")
    cleaned = rel_path.replace("\\", "/").lstrip("/")
    if not cleaned:
        raise UnsafePathError("path resolves to empty")
    parts = cleaned.split("/")
    if ".." in parts:
        raise UnsafePathError("'..' segment")
    return cleaned


# ---------------------------------------------------------------------------
# Local backend
# ---------------------------------------------------------------------------

def _local_root(slug: str) -> Path:
    return Path(f"artists/{slug}").resolve()


def _local_target(slug: str, rel_path: str) -> Path:
    rel = _safe_rel(rel_path)
    root = _local_root(slug)
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise UnsafePathError("resolves outside artist root")
    return target


def _local_read(slug: str, rel_path: str) -> str:
    target = _local_target(slug, rel_path)
    return target.read_text()


def _local_write(slug: str, rel_path: str, content: str) -> None:
    target = _local_target(slug, rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def _local_list(slug: str, rel_dir: str) -> List[str]:
    if rel_dir in ("", "."):
        target = _local_root(slug)
    else:
        target = _local_target(slug, rel_dir)
    if not target.is_dir():
        return []
    return sorted(p.name for p in target.iterdir())


def _local_exec(slug: str, cmd: str, timeout: int) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=str(_local_root(slug)),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# Remote backend
# ---------------------------------------------------------------------------

def _ssh_cmd(remote: dict, remote_cmd: str) -> List[str]:
    return [
        "ssh",
        "-i", remote["key"],
        *SSH_BASE_OPTS,
        remote["host"],
        remote_cmd,
    ]


def _classify_ssh_failure(returncode: int, stderr: str, cmd: str) -> RemoteError:
    """Map ssh exit codes / stderr patterns to typed errors.

    OpenSSH conventions: 255 means ssh itself failed (auth, connect, etc.).
    Anything else is the remote command's own exit code.
    """
    s = stderr.lower()
    if returncode == 255:
        if "permission denied" in s or "publickey" in s or "authentication" in s:
            return RemoteAuthError(stderr.strip() or "auth failed")
        if "could not resolve" in s or "connection refused" in s or "no route" in s or "connection timed out" in s:
            return RemoteUnreachable(stderr.strip() or "host unreachable")
        return RemoteUnreachable(stderr.strip() or "ssh failed")
    return RemoteCommandFailed(returncode, stderr, cmd)


def _run_ssh(remote: dict, remote_cmd: str, *, stdin: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    cmd = _ssh_cmd(remote, remote_cmd)
    try:
        proc = subprocess.run(
            cmd,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RemoteTimeout(f"ssh timed out after {timeout}s") from exc
    return proc.returncode, proc.stdout, proc.stderr


def _remote_full_path(remote: dict, rel_path: str) -> str:
    rel = _safe_rel(rel_path)
    return f"{remote['path'].rstrip('/')}/{rel}"


def _remote_read(remote: dict, rel_path: str) -> str:
    full = _remote_full_path(remote, rel_path)
    cmd = f"cat -- {shlex.quote(full)}"
    rc, out, err = _run_ssh(remote, cmd)
    if rc != 0:
        raise _classify_ssh_failure(rc, err, cmd)
    return out


def _remote_write(remote: dict, rel_path: str, content: str) -> None:
    full = _remote_full_path(remote, rel_path)
    parent = full.rsplit("/", 1)[0] or "/"
    cmd = f"mkdir -p -- {shlex.quote(parent)} && cat > {shlex.quote(full)}"
    rc, _, err = _run_ssh(remote, cmd, stdin=content)
    if rc != 0:
        raise _classify_ssh_failure(rc, err, cmd)


def _remote_list(remote: dict, rel_dir: str) -> List[str]:
    if rel_dir in ("", "."):
        full = remote["path"]
    else:
        full = _remote_full_path(remote, rel_dir)
    cmd = f"ls -1 -- {shlex.quote(full)}"
    rc, out, err = _run_ssh(remote, cmd)
    if rc != 0:
        raise _classify_ssh_failure(rc, err, cmd)
    return [line for line in out.splitlines() if line]


def _remote_exec(remote: dict, cmd: str, timeout: int) -> Tuple[int, str, str]:
    # Run inside the remote repo dir.
    wrapped = f"cd {shlex.quote(remote['path'])} && {cmd}"
    rc, out, err = _run_ssh(remote, wrapped, timeout=timeout)
    if rc == 255:
        raise _classify_ssh_failure(rc, err, wrapped)
    return rc, out, err


# ---------------------------------------------------------------------------
# Public surface — branches on artist remote-ness
# ---------------------------------------------------------------------------

def read(slug: str, rel_path: str) -> str:
    if external_artist.is_remote(slug):
        remote = external_artist.load_remote_config(slug)
        return _remote_read(remote, rel_path)
    return _local_read(slug, rel_path)


def write(slug: str, rel_path: str, content: str) -> None:
    if external_artist.is_remote(slug):
        remote = external_artist.load_remote_config(slug)
        _remote_write(remote, rel_path, content)
        return
    _local_write(slug, rel_path, content)


def list(slug: str, rel_dir: str = ".") -> List[str]:  # noqa: A001 — matches plan
    if external_artist.is_remote(slug):
        remote = external_artist.load_remote_config(slug)
        return _remote_list(remote, rel_dir)
    return _local_list(slug, rel_dir)


def exec(slug: str, cmd: str, timeout: int = 30) -> Tuple[int, str, str]:  # noqa: A001
    if external_artist.is_remote(slug):
        remote = external_artist.load_remote_config(slug)
        return _remote_exec(remote, cmd, timeout)
    return _local_exec(slug, cmd, timeout)


def fetch_manifest(slug: str) -> dict:
    """Always returns a dict. For local artists, returns defaults derived
    from local config. For remote artists, fetches `.adze-remote.json` from
    the remote repo root, merges with defaults, and caches the result.
    Malformed JSON falls back to defaults. Network/auth failures propagate.
    """
    if not external_artist.is_remote(slug):
        return external_artist.manifest_defaults(slug)
    remote = external_artist.load_remote_config(slug)
    full = f"{remote['path'].rstrip('/')}/{external_artist.MANIFEST_FILENAME}"
    cmd = f"cat -- {shlex.quote(full)} 2>/dev/null || true"
    rc, out, err = _run_ssh(remote, cmd)
    if rc == 255:
        raise _classify_ssh_failure(rc, err, cmd)
    raw = {}
    if out.strip():
        try:
            raw = json.loads(out)
        except json.JSONDecodeError:
            raw = {}
    merged = external_artist.merge_manifest(slug, raw)
    external_artist.cache_manifest(slug, merged)
    return merged
