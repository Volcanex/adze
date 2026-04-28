"""
Adze Vibe Coder — in-process agent loop.

Replaces the legacy `claude` CLI subprocess at admin_api.py:claude-stream.
Uses LiteLLM as the LLM transport so we can route OpenRouter -> Gemini
(or any other provider) without rewriting tool-calling glue.

Why hand-rolled instead of openhands-sdk:
  As of 2026-04, openhands-sdk's public docs don't cover custom tool
  definition, filesystem scoping, streaming callbacks, or session reset
  in production-confident detail. We need all four. The interface here
  (`run_turn`) is small enough to swap to openhands-sdk later when their
  docs catch up — replace the body of the while-loop, keep the event
  shape the SSE consumer expects.

Tool surface mirrors Claude Code semantics (Read/Write/Edit/Glob/Grep/
Bash/WebFetch) so the existing system-prompt docs in _shared/docs/*.md
keep working unchanged.

All filesystem and shell operations are path-scoped to the artist's
directory. Bash is further constrained by an allow-list mirroring the
one previously enforced by Claude CLI's --allowedTools at
admin_api.py:4695-4737.
"""

from __future__ import annotations

import os
import re
import json
import time
import shlex
import difflib
import fnmatch
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List, Union

try:
    import litellm
    litellm.drop_params = True  # ignore unsupported kwargs across providers
except ImportError as e:
    raise ImportError(
        "vibe_agent requires litellm. Install with: pip install litellm"
    ) from e


# ── Models ────────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "openrouter/anthropic/claude-sonnet-4.5"
SONNET_MODEL = DEFAULT_MODEL
HAIKU_MODEL = "openrouter/anthropic/claude-haiku-4.5"
PRO_MODEL = "openrouter/google/gemini-2.5-pro"
FLASH_MODEL = "openrouter/google/gemini-2.5-flash"
LITE_MODEL = "openrouter/google/gemini-2.5-flash-lite"

# Per-call model override via prompt prefix.
# Default = Claude Sonnet 4.5 (best tool-call reliability at long context).
# Cheap escape hatches stay available:
#   @haiku  — Claude Haiku 4.5 (fast + reliable, ~3× cheaper than Sonnet)
#   @pro    — Gemini 2.5 Pro (cheaper still, weaker on tools)
#   @flash  — Gemini 2.5 Flash (cheapest, weakest on tools)
#   @lite   — Gemini 2.5 Flash Lite (extreme cheap)
MODEL_PREFIXES = {
    "@sonnet ": SONNET_MODEL,
    "@haiku ": HAIKU_MODEL,
    "@pro ": PRO_MODEL,
    "@flash ": FLASH_MODEL,
    "@lite ": LITE_MODEL,
}


def _select_model(prompt: str, default: str = DEFAULT_MODEL) -> tuple[str, str]:
    """Strip and return (model, cleaned_prompt)."""
    for prefix, model in MODEL_PREFIXES.items():
        if prompt.startswith(prefix):
            return model, prompt[len(prefix):]
    return default, prompt


# ── Bash allow-list (mirrors admin_api.py existing list) ──────────────────────

BASH_ALLOWED = frozenset({
    "ls", "mkdir", "cp", "mv", "rm", "touch", "chmod", "chown", "ln",
    "basename", "dirname", "realpath", "readlink", "find", "tree", "pwd",
    "stat", "file", "du", "df",
    "cat", "head", "tail", "wc", "sort", "uniq", "diff", "comm",
    "sed", "awk", "tr", "cut", "paste",
    "grep", "egrep", "fgrep", "rg", "xargs", "tee", "rev", "fold",
    "echo", "printf", "yes",
    "python3", "python", "node", "npx", "ruby", "perl", "php", "bash", "sh",
    "pip", "pip3", "npm", "yarn", "pnpm",
    "curl", "wget", "http",
    "tar", "gzip", "gunzip", "bzip2", "zip", "unzip", "7z", "xz",
    "convert", "identify", "mogrify", "composite",
    "ffmpeg", "ffprobe", "sox", "soxi", "lame", "oggenc",
    "magick", "gifsicle", "optipng", "pngquant",
    "jq", "base64", "md5sum", "sha256sum", "openssl", "xxd", "od",
    "date", "env", "which", "whoami", "hostname", "uname", "id",
    "test", "true", "false", "sleep", "git",
})


# ── Filesystem facade (Root) ──────────────────────────────────────────────────
# Tools operate on a Root, not on a Path. LocalRoot wraps an on-disk artist
# directory; RemoteRoot delegates to remote_fs which routes operations over
# SSH to a Seed deployment. The agent loop and tool dispatch don't care which.

import remote_fs as _remote_fs  # noqa: E402
import external_artist as _external_artist  # noqa: E402


class _Root:
    """Filesystem facade scoped to one artist."""

    def read(self, rel: str) -> str: raise NotImplementedError
    def write(self, rel: str, content: str) -> None: raise NotImplementedError
    def exists(self, rel: str) -> bool: raise NotImplementedError
    def is_dir(self, rel: str) -> bool: raise NotImplementedError
    def list_files(self) -> List[str]: raise NotImplementedError  # all files, relative
    def grep(self, pattern: str, rel: str = ".") -> str: raise NotImplementedError
    def bash(self, command: str, timeout: int) -> tuple[int, str, str]: raise NotImplementedError
    def display(self) -> str: raise NotImplementedError


class LocalRoot(_Root):
    def __init__(self, path: Path):
        self.path = path

    def _resolve(self, given: str) -> Path:
        p = Path(given)
        if not p.is_absolute():
            p = self.path / p
        p = p.resolve()
        root_resolved = self.path.resolve()
        try:
            p.relative_to(root_resolved)
        except ValueError:
            raise PermissionError(
                f"Path '{given}' resolves outside the artist directory "
                f"({self.path.name}/). Refusing."
            )
        return p

    def read(self, rel: str) -> str:
        target = self._resolve(rel)
        if not target.exists():
            raise FileNotFoundError(f"{rel} does not exist")
        if target.is_dir():
            raise IsADirectoryError(f"{rel} is a directory; use Glob or Bash(ls)")
        return target.read_text(encoding="utf-8", errors="replace")

    def write(self, rel: str, content: str) -> None:
        target = self._resolve(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def exists(self, rel: str) -> bool:
        try:
            return self._resolve(rel).exists()
        except PermissionError:
            return False

    def is_dir(self, rel: str) -> bool:
        try:
            return self._resolve(rel).is_dir()
        except PermissionError:
            return False

    def list_files(self) -> List[str]:
        return sorted(
            str(p.relative_to(self.path))
            for p in self.path.rglob("*")
            if p.is_file()
        )

    def grep(self, pattern: str, rel: str = ".") -> str:
        target = self._resolve(rel)
        try:
            rg = subprocess.run(
                ["rg", "-n", "--no-heading", pattern, str(target)],
                capture_output=True, text=True, timeout=30,
            )
            if rg.returncode in (0, 1):
                return rg.stdout or "(no matches)"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        try:
            rx = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}")
        out: list[str] = []
        files = [target] if target.is_file() else target.rglob("*")
        for p in files:
            if not p.is_file():
                continue
            try:
                for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                    if rx.search(ln):
                        out.append(f"{p.relative_to(self.path)}:{i}:{ln}")
            except (UnicodeDecodeError, PermissionError):
                continue
        return "\n".join(out) or "(no matches)"

    def bash(self, command: str, timeout: int) -> tuple[int, str, str]:
        proc = subprocess.run(
            command, shell=True, cwd=str(self.path),
            capture_output=True, text=True, timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def display(self) -> str:
        return f"{self.path.name}/"


class RemoteRoot(_Root):
    """Routes every operation through remote_fs (SSH to a Seed deployment)."""

    def __init__(self, slug: str):
        self.slug = slug
        self._cfg = _external_artist.load_remote_config(slug)
        if not self._cfg:
            raise ValueError(f"artist '{slug}' has no remote config")

    def read(self, rel: str) -> str:
        try:
            return _remote_fs.read(self.slug, rel)
        except _remote_fs.RemoteCommandFailed as e:
            if "no such file" in e.stderr.lower() or "not found" in e.stderr.lower():
                raise FileNotFoundError(f"{rel} does not exist")
            raise

    def write(self, rel: str, content: str) -> None:
        _remote_fs.write(self.slug, rel, content)

    def exists(self, rel: str) -> bool:
        try:
            _remote_fs._safe_rel(rel)
        except _remote_fs.UnsafePathError:
            return False
        full = f"{self._cfg['path'].rstrip('/')}/{rel.lstrip('/')}"
        rc, _, _ = _remote_fs._run_ssh(self._cfg, f"test -e {shlex.quote(full)}")
        return rc == 0

    def is_dir(self, rel: str) -> bool:
        try:
            _remote_fs._safe_rel(rel)
        except _remote_fs.UnsafePathError:
            return False
        full = f"{self._cfg['path'].rstrip('/')}/{rel.lstrip('/')}"
        rc, _, _ = _remote_fs._run_ssh(self._cfg, f"test -d {shlex.quote(full)}")
        return rc == 0

    def list_files(self) -> List[str]:
        # Files only, relative to the remote root, excluding common noise.
        cmd = (
            f"cd {shlex.quote(self._cfg['path'])} && "
            "find . -type f "
            "-not -path './.git/*' "
            "-not -path './output/*' "
            "-not -path './__pycache__/*' "
            "-not -path './node_modules/*' "
            "| sed 's|^\\./||' | sort"
        )
        rc, out, err = _remote_fs._run_ssh(self._cfg, cmd)
        if rc != 0:
            raise _remote_fs._classify_ssh_failure(rc, err, cmd)
        return [line for line in out.splitlines() if line]

    def grep(self, pattern: str, rel: str = ".") -> str:
        target_rel = "" if rel in ("", ".") else rel
        if target_rel:
            _remote_fs._safe_rel(target_rel)
            full = f"{self._cfg['path'].rstrip('/')}/{target_rel}"
        else:
            full = self._cfg["path"]
        # grep -rn is universal; ripgrep is not guaranteed on the Seed box.
        cmd = f"grep -rn -- {shlex.quote(pattern)} {shlex.quote(full)} 2>/dev/null || true"
        rc, out, err = _remote_fs._run_ssh(self._cfg, cmd)
        if rc == 255:
            raise _remote_fs._classify_ssh_failure(rc, err, cmd)
        if not out:
            return "(no matches)"
        # Strip the absolute remote prefix so paths are relative.
        prefix = self._cfg["path"].rstrip("/") + "/"
        cleaned = "\n".join(
            line[len(prefix):] if line.startswith(prefix) else line
            for line in out.splitlines()
        )
        return cleaned

    def bash(self, command: str, timeout: int) -> tuple[int, str, str]:
        return _remote_fs.exec(self.slug, command, timeout=timeout)

    def display(self) -> str:
        return f"remote:{self._cfg['host']}:{self._cfg['path']}/"


def make_root(artist_slug: str, local_path: Optional[Path] = None) -> _Root:
    """Build the right Root for an artist. Local path is optional fallback."""
    if _external_artist.is_remote(artist_slug):
        return RemoteRoot(artist_slug)
    if local_path is None:
        local_path = Path(f"artists/{artist_slug}")
    return LocalRoot(local_path.resolve())


# ── Tool implementations (operate on a Root) ──────────────────────────────────

def _tool_read(root: _Root, args: dict) -> str:
    rel = args["file_path"]
    text = root.read(rel)
    lines = text.splitlines()
    offset = args.get("offset", 0)
    limit = args.get("limit")
    if offset:
        lines = lines[offset:]
    if limit is not None:
        lines = lines[:limit]
    base = offset or 0
    return "\n".join(f"{i + 1 + base}\t{ln}" for i, ln in enumerate(lines))


def _tool_write(root: _Root, args: dict) -> dict:
    rel = args["file_path"]
    pre_text = ""
    is_new = not root.exists(rel)
    if not is_new:
        try:
            pre_text = root.read(rel)
        except Exception:
            pre_text = ""
    new_text = args["content"]
    root.write(rel, new_text)
    diff = "".join(difflib.unified_diff(
        pre_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=("(new) " + rel) if is_new else rel,
        tofile=rel, n=2,
    ))
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    label = "Created" if is_new else "Wrote"
    return {
        "text": f"{label} {rel} ({len(new_text)} bytes)",
        "meta": {"diff": diff, "path": rel, "tool": "Write",
                 "added": added, "removed": removed, "is_new": is_new},
    }


def _tool_edit(root: _Root, args: dict) -> dict:
    rel = args["file_path"]
    text = root.read(rel)
    old = args["old_string"]
    new = args["new_string"]
    replace_all = bool(args.get("replace_all", False))
    if old == new:
        raise ValueError("old_string and new_string are identical")
    occurrences = text.count(old)
    if occurrences == 0:
        raise ValueError(f"old_string not found in {rel}")
    if occurrences > 1 and not replace_all:
        raise ValueError(
            f"old_string appears {occurrences} times in {rel}. "
            f"Pass replace_all=true or include more surrounding context."
        )
    new_text = text.replace(old, new)
    root.write(rel, new_text)
    n = occurrences if replace_all else 1
    diff = "".join(difflib.unified_diff(
        text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=rel, tofile=rel, n=2,
    ))
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    return {
        "text": f"Replaced {n} occurrence(s) in {rel}",
        "meta": {"diff": diff, "path": rel, "tool": "Edit",
                 "added": added, "removed": removed},
    }


def _tool_glob(root: _Root, args: dict) -> str:
    pattern = args["pattern"]
    matches = [
        rel for rel in root.list_files()
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(Path(rel).name, pattern)
    ]
    return "\n".join(matches) or "(no matches)"


def _tool_grep(root: _Root, args: dict) -> str:
    return root.grep(args["pattern"], args.get("path", "."))


def _tool_bash(root: _Root, args: dict) -> str:
    command = args["command"]
    timeout = int(args.get("timeout", 60))
    try:
        first = shlex.split(command)[0]
    except (ValueError, IndexError):
        raise ValueError("Could not parse command")
    bin_name = Path(first).name
    if bin_name not in BASH_ALLOWED:
        raise PermissionError(
            f"Command '{bin_name}' is not in the vibe-coder allow-list. "
            f"Tell the user what you wanted to run; they can add it if it's safe."
        )
    rc, stdout, stderr = root.bash(command, timeout)
    out = stdout
    if stderr:
        out += ("\n[stderr]\n" if out else "[stderr]\n") + stderr
    if rc != 0:
        out += f"\n[exit code: {rc}]"
    return out or "(no output)"


def _tool_webfetch(root: _Root, args: dict) -> str:
    url = args["url"]
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    req = urllib.request.Request(url, headers={"User-Agent": "AdzeVibeCoder/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read(200_000)
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL error: {e.reason}"
    text = body.decode("utf-8", errors="replace")
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
    return text[:50_000]


TOOL_IMPLS = {
    "Read": _tool_read,
    "Write": _tool_write,
    "Edit": _tool_edit,
    "Glob": _tool_glob,
    "Grep": _tool_grep,
    "Bash": _tool_bash,
    "WebFetch": _tool_webfetch,
}


# ── Tool specs (LiteLLM/OpenAI-compatible JSON schema) ────────────────────────

def _tool_specs() -> List[dict]:
    return [
        {"type": "function", "function": {
            "name": "Read",
            "description": "Read a file's contents. Path must be inside the artist's directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path relative to the artist's directory."},
                    "offset": {"type": "integer", "description": "Optional starting line (0-indexed)."},
                    "limit": {"type": "integer", "description": "Optional max number of lines to return."},
                },
                "required": ["file_path"],
            },
        }},
        {"type": "function", "function": {
            "name": "Write",
            "description": "Create or overwrite a file. Parent directories created as needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["file_path", "content"],
            },
        }},
        {"type": "function", "function": {
            "name": "Edit",
            "description": (
                "Replace exact strings in an existing file. The old_string must be unique unless "
                "replace_all is true. Prefer Edit over Write for small changes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                    "replace_all": {"type": "boolean", "description": "Replace every occurrence."},
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        }},
        {"type": "function", "function": {
            "name": "Glob",
            "description": "List files in the artist's directory matching a glob pattern (e.g. '**/*.md').",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        }},
        {"type": "function", "function": {
            "name": "Grep",
            "description": "Search for a regex pattern across files in the artist's directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regular expression."},
                    "path": {"type": "string", "description": "File or subdirectory to search. Default: artist root."},
                },
                "required": ["pattern"],
            },
        }},
        {"type": "function", "function": {
            "name": "Bash",
            "description": (
                "Run a shell command in the artist's directory. Limited to a curated allow-list "
                "(no sudo, systemctl, ssh, etc.). Use for: ls, find, image processing (convert/ffmpeg), "
                "git, jq, file manipulation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "description": "Seconds. Default 60, max 300."},
                },
                "required": ["command"],
            },
        }},
        {"type": "function", "function": {
            "name": "WebFetch",
            "description": "Fetch a URL and return the text body (capped at 50kB).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        }},
    ]


# ── Conversation persistence ──────────────────────────────────────────────────

def load_history(sessions_dir: Path, session_id: str) -> List[dict]:
    f = sessions_dir / f"{session_id}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history(sessions_dir: Path, session_id: str, history: List[dict]) -> None:
    sessions_dir.mkdir(parents=True, exist_ok=True)
    f = sessions_dir / f"{session_id}.json"
    f.write_text(json.dumps(history, indent=2), encoding="utf-8")


def clear_session(sessions_dir: Path, session_id: str) -> bool:
    f = sessions_dir / f"{session_id}.json"
    if f.exists():
        f.unlink()
        return True
    return False


# ── Hallucination guard ───────────────────────────────────────────────────────
# Catches the model claiming "I've edited X" without actually calling Edit.
# Triggers a corrective re-iteration in the same turn so the user just sees
# the work happen, not the model's apology.

_HALLUCINATION_PHRASES = (
    "i've edited", "i edited",
    "i've changed", "i changed",
    "i've updated", "i updated",
    "i've added", "i added",
    "i've removed", "i removed",
    "i've replaced", "i replaced",
    "i've fixed", "i fixed",
    "i've corrected", "i corrected",
    "i've modified", "i modified",
    "i've made the change", "i've made the changes",
    "i've now applied", "i've applied",
    "i've performed",
    "the file now", "the change has been", "changes have been applied",
    "the new version reads", "the new code reads",
    "the file has been", "the page has been",
)

_USER_CHANGE_INDICATORS = (
    "change", "edit", "add ", "remove", "fix", "update", "replace",
    "rebuild", "rewrite", "merge", "delete", "swap", "modify",
    "alter", "refactor", "adjust", "tweak",
    "make ", "make it ", "make the ",
    "set the ", "create ", "write ", "build ",
    "convert ", "move ", "rename ",
)


def _detect_hallucinated_edit(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(phrase in lower for phrase in _HALLUCINATION_PHRASES)


def _looks_like_change_request(prompt: str) -> bool:
    if not prompt:
        return False
    lower = prompt.lower()
    return any(ind in lower for ind in _USER_CHANGE_INDICATORS)


# ── The agent loop ────────────────────────────────────────────────────────────

MAX_ITERATIONS = 25  # safety bound on tool-call loop per turn


def run_turn(
    artist_root: Path,
    sessions_dir: Path,
    session_id: str,
    prompt: str,
    system_prompt: str,
    log: Optional[logging.Logger] = None,
    artist_slug: Optional[str] = None,
    root: Optional[_Root] = None,
) -> Iterator[dict]:
    """
    Run one user turn (one prompt -> one final assistant text), looping over
    tool calls as needed. Yields events shaped to match what dashboard.html's
    SSE parser at line 6472+ expects:

        {type: 'assistant', message: {content: [{type:'text',text}|{type:'tool_use',id,name,input}]}}
        {type: 'tool_result', tool_use_id, content, is_error}
        {type: 'result', result, cost_usd?, duration_ms}
        {type: 'system_message', text}
        {type: 'error', error}
        {type: 'stream_end'}

    The session's full conversation history persists in
    `sessions_dir/<session_id>.json` and is mutated by this function.
    """
    log = log or logging.getLogger("vibe")
    slug_tag = f"[{artist_slug}] " if artist_slug else ""

    # Build the filesystem facade. Callers can pass `root` directly (preferred);
    # otherwise we infer from artist_slug (remote-capable) or fall back to the
    # legacy artist_root path.
    if root is None:
        if artist_slug:
            root = make_root(artist_slug, artist_root)
        else:
            root = LocalRoot(artist_root)

    model, prompt = _select_model(prompt)
    if model != DEFAULT_MODEL:
        yield {"type": "system_message", "text": f"Routing this turn through {model.split('/')[-1]}."}

    history = load_history(sessions_dir, session_id)
    # Always refresh the system prompt at history[0]. The docs/*.md files in
    # _shared/docs/ change occasionally; without this, an old session keeps
    # the stale prompt until the user runs /clear (which we don't want — they
    # shouldn't have to know that). Cheap: dropping/setting one message.
    if history and history[0].get("role") == "system":
        history[0]["content"] = system_prompt
    elif not history:
        history.append({"role": "system", "content": system_prompt})
    else:
        # Defensive: history exists but no system message at index 0. Insert.
        history.insert(0, {"role": "system", "content": system_prompt})
    history.append({"role": "user", "content": prompt})

    started = time.time()
    total_cost: float = 0.0
    final_text = ""

    total_tokens = 0  # rolling token usage for the cost-meter context bar

    try:
        for iteration in range(1, MAX_ITERATIONS + 1):
            # Stream the model's output. Text deltas go straight to the wire as
            # content_block_delta events (typewriter effect — dashboard parses at
            # line 6514). Tool calls accumulate across chunks and are emitted in
            # one assistant event after the stream finishes.
            try:
                response_stream = litellm.completion(
                    model=model,
                    messages=history,
                    tools=_tool_specs(),
                    tool_choice="auto",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                    stream=True,
                    stream_options={"include_usage": True},
                )
            except Exception as e:
                log.error(f"{slug_tag}LLM error iteration {iteration}: {e}")
                yield {"type": "error", "error": f"Model call failed: {e}"}
                return

            text = ""
            tool_calls_acc: list[dict] = []
            chunks: list = []

            try:
                for chunk in response_stream:
                    chunks.append(chunk)
                    if not getattr(chunk, "choices", None):
                        continue
                    delta = chunk.choices[0].delta
                    if delta is None:
                        continue
                    content_piece = getattr(delta, "content", None)
                    if content_piece:
                        text += content_piece
                        yield {
                            "type": "content_block_delta",
                            "delta": {"type": "text_delta", "text": content_piece},
                        }
                    for tc in (getattr(delta, "tool_calls", None) or []):
                        idx = getattr(tc, "index", 0) or 0
                        while len(tool_calls_acc) <= idx:
                            tool_calls_acc.append({"id": "", "name": "", "arguments": ""})
                        slot = tool_calls_acc[idx]
                        if getattr(tc, "id", None):
                            slot["id"] = tc.id
                        fn = getattr(tc, "function", None)
                        if fn:
                            if getattr(fn, "name", None):
                                slot["name"] += fn.name
                            if getattr(fn, "arguments", None):
                                slot["arguments"] += fn.arguments
            except Exception as e:
                log.exception(f"{slug_tag}stream error iteration {iteration}")
                yield {"type": "error", "error": f"Stream error: {e}"}
                return

            tool_calls_acc = [tc for tc in tool_calls_acc if tc["name"]]

            # Cost + token usage from the assembled stream
            try:
                built = litellm.stream_chunk_builder(chunks, messages=history)
                turn_cost = float(litellm.completion_cost(built) or 0.0)
                total_cost += turn_cost
                usage = getattr(built, "usage", None)
                if usage is not None:
                    tt = getattr(usage, "total_tokens", 0) or 0
                    if tt:
                        total_tokens = int(tt)
            except Exception:
                turn_cost = 0.0

            # Build content array (text + tool_use blocks)
            content_blocks: list[dict] = []
            if text:
                content_blocks.append({"type": "text", "text": text})
                final_text = text
            for tc in tool_calls_acc:
                try:
                    parsed_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    parsed_args = {"_raw": tc["arguments"]}
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": parsed_args,
                })
                snippet = json.dumps(parsed_args)[:300]
                log.info(f"{slug_tag}TOOL: {tc['name']} → {snippet}")

            yield {"type": "assistant", "message": {"content": content_blocks}}

            history.append({
                "role": "assistant",
                "content": text or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    } for tc in tool_calls_acc
                ] if tool_calls_acc else None,
            })

            # No tool calls → maybe done. Hallucination guard fires if the
            # model claimed an edit in chat but didn't actually call a tool.
            if not tool_calls_acc:
                hallucinated = (
                    _looks_like_change_request(prompt)
                    and _detect_hallucinated_edit(text)
                    and iteration < MAX_ITERATIONS
                )
                if hallucinated:
                    log.warning(
                        f"{slug_tag}HALLUCINATION GUARD fired iteration={iteration}: "
                        f"text claims edit but no tool calls. Pushing back."
                    )
                    yield {
                        "type": "system_message",
                        "text": "Detected claimed edit with no tool call — pushing back.",
                    }
                    history.append({
                        "role": "user",
                        "content": (
                            "Stop. You said you made a change but called no tools "
                            "this turn. The file has not changed. Use the Edit "
                            "(or Write/Bash) tool now to actually make the change "
                            "the user asked for. Do NOT paste the new code in chat "
                            "as proof — execute the tool. After the tool call "
                            "succeeds, briefly confirm what you did."
                        ),
                    })
                    continue  # next iteration retries with the corrective nudge

                if text:
                    log.info(f"{slug_tag}TEXT: {text[:500]}")
                duration_ms = int((time.time() - started) * 1000)
                log.info(
                    f"{slug_tag}── END (ok) cost=${total_cost:.4f} "
                    f"tokens={total_tokens} duration={duration_ms}ms ──"
                )
                yield {
                    "type": "result",
                    "result": final_text,
                    "cost_usd": round(total_cost, 6),
                    "tokens": total_tokens,
                    "duration_ms": duration_ms,
                }
                return

            # Execute each tool call
            for tc in tool_calls_acc:
                name = tc["name"]
                try:
                    args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    args = {}

                impl = TOOL_IMPLS.get(name)
                result_meta: dict = {}
                if impl is None:
                    result_text = f"Unknown tool: {name}"
                    is_error = True
                else:
                    try:
                        raw = impl(root, args)
                        if isinstance(raw, dict):
                            result_text = raw.get("text", "")
                            result_meta = raw.get("meta", {}) or {}
                        else:
                            result_text = raw
                        is_error = False
                    except _remote_fs.RemoteError as e:
                        # Translate SSH-layer failures into chat-friendly notices
                        # so the (often non-technical) external-artist user has
                        # recourse beyond a generic "tool crashed".
                        kind = type(e).__name__
                        friendly = {
                            "RemoteAuthError": "SSH key was rejected. Check that the public key is in the Seed box's authorized_keys.",
                            "RemoteUnreachable": "Cannot reach the Seed box (network, DNS, or refused connection).",
                            "RemoteTimeout": "SSH timed out. The Seed box may be busy or unreachable.",
                            "RemoteCommandFailed": "Remote command failed.",
                            "UnsafePathError": "Refused a path that tried to escape the artist root.",
                        }.get(kind, "Remote operation failed.")
                        yield {"type": "system_message", "text": f"{friendly} ({e})"}
                        log.warning(f"{slug_tag}{kind}: {e}")
                        result_text = f"{kind}: {e}"
                        is_error = True
                    except (PermissionError, FileNotFoundError, IsADirectoryError, ValueError) as e:
                        result_text = f"{type(e).__name__}: {e}"
                        is_error = True
                    except subprocess.TimeoutExpired:
                        result_text = "Bash command timed out"
                        is_error = True
                    except Exception as e:
                        log.exception(f"{slug_tag}Tool {name} crashed")
                        result_text = f"Tool crashed: {type(e).__name__}: {e}"
                        is_error = True

                if len(result_text) > 30_000:
                    result_text = result_text[:30_000] + "\n... (truncated)"

                event: dict = {
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": result_text,
                    "is_error": is_error,
                }
                if result_meta:
                    event["meta"] = result_meta
                yield event

                history.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_text,
                })

        log.warning(f"{slug_tag}Reached MAX_ITERATIONS={MAX_ITERATIONS}")
        yield {
            "type": "error",
            "error": f"Reached the {MAX_ITERATIONS}-step safety limit. Try splitting the request.",
        }
    finally:
        save_history(sessions_dir, session_id, history)
