"""
Per-artist git repos for the Auto-Coder tabs/worktrees feature.

Each artist directory (`artists/<slug>/`) is *lazily* initialised as a
standalone git repo on the first Auto-Coder tab open. The repo is
local-only — no remote, no owner — and exists so tabs 2+ have somewhere to
branch from and so we can auto-commit per assistant turn inside a worktree.

Worktree creation used to be opencode's job (`POST /experimental/worktree`).
DeepSeek Harness has no equivalent — it is an agent runtime, not a workspace
manager — so `create_worktree` / `list_worktrees` / `remove_worktree` below
are the local replacement for that part of opencode's API.

The outer `/home/gabriel/adze` repo keeps tracking the artist's files
as before; the inner `.git/` is excluded via the root `.gitignore`. The
two repos share a working tree but record independent history.

Git commands run **in this process**, inside the Flask container, which is
already uid 1000 (`adze`) — the same uid the sandbox containers used — and
ships git. They used to run via `docker exec` into the per-artist sandbox;
that container went away with the opencode backend (see `dsh_agent.py`), and
routing git through a container purely to borrow its uid was never the point.
The uid is what matters, because a root-owned object in `.git/` is exactly
the failure mode described in the root CLAUDE.md for `output/`.

Worktrees live **outside** `artists/`, under `.autocode-worktrees/<slug>/`.
That is deliberate: anything under `artists/<slug>/` is compiled by
`compile.py` and served, so a worktree parked in there would publish an
artist's half-finished branch to their live site.
"""

from __future__ import annotations

import logging
import os
import re
import shlex
import subprocess
import time
from pathlib import Path

_log = logging.getLogger('adze.repos')

WORKTREE_ROOT = Path(os.environ.get('ADZE_WORKTREE_ROOT', '.autocode-worktrees'))

GIT_USER_NAME = 'Adze Auto-Coder'
GIT_USER_EMAIL = 'autocoder@adze.local'

INNER_GITIGNORE = """\
# Inner per-artist repo — worktrees live outside artists/ (see
# WORKTREE_ROOT), so we only need to keep large/regen-able junk out of
# the artist's own history.
.snapshots/
backups/
analytics.json
analytics.json.bak
data.db
data.db-shm
data.db-wal
.aider.chat.history.md
.aider.input.history
.adze-context.md
.env
ssh_key
ssh_key.pub
.adze-remote.cache.json
"""


def artist_root(slug: str) -> Path:
    """Absolute path to the artist's working tree in this container."""
    return (Path.cwd() / 'artists' / slug).resolve()


def worktree_root(slug: str) -> Path:
    base = WORKTREE_ROOT if WORKTREE_ROOT.is_absolute() else (Path.cwd() / WORKTREE_ROOT)
    return (base / slug).resolve()


def _exec(slug: str, cmd: str, check: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a shell command in the artist's working tree.

    Runs in-process (uid 1000, `adze`) rather than via `docker exec`. The
    callers below assume the artist root is the working directory, which is
    why `cwd` defaults to it instead of the process cwd.
    """
    return subprocess.run(
        ['bash', '-lc', cmd],
        cwd=str(cwd or artist_root(slug)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


def is_repo(slug: str) -> bool:
    r = _exec(slug, 'git rev-parse --is-inside-work-tree 2>/dev/null', check=False)
    return r.returncode == 0 and (r.stdout or '').strip() == 'true'


def ensure_repo(slug: str) -> None:
    """Idempotently turn `artists/<slug>/` into a git repo on branch main.

    Safe to call on every tab open. If already initialised, no-ops.
    """
    if is_repo(slug):
        return
    # Write a sensible .gitignore before the first commit so we don't
    # bake the snapshot/backup dirs into history.
    _exec(slug, f'cat > .gitignore <<\'EOF\'\n{INNER_GITIGNORE}EOF')
    script = (
        f'git init -q -b main && '
        f'git config user.name {shlex.quote(GIT_USER_NAME)} && '
        f'git config user.email {shlex.quote(GIT_USER_EMAIL)} && '
        f'git add -A && '
        f'git commit -q --allow-empty -m "adze: init artist repo" && '
        f'git worktree prune 2>/dev/null || true'
    )
    r = _exec(slug, script, check=False)
    if r.returncode != 0:
        raise RuntimeError(
            f'git init failed for {slug}: {(r.stderr or r.stdout).strip()}'
        )
    _log.info(f'[{slug}] artist repo initialised on main')


def commit_worktree(slug: str, worktree_dir: str, message: str) -> dict:
    """Stage and commit everything in a worktree. No-op if tree is clean.

    `worktree_dir` is an absolute path under `worktree_root(slug)`; the
    caller is responsible for having validated it against that root.
    Returns `{committed: bool, sha: str|None, message: str|None}`.
    """
    safe_msg = shlex.quote(message[:200] or 'adze: auto-commit')
    safe_dir = shlex.quote(worktree_dir)
    script = (
        f'cd {safe_dir} && '
        f'git add -A && '
        f'if git diff --cached --quiet; then '
        f'  echo CLEAN; '
        f'else '
        f'  git -c user.name={shlex.quote(GIT_USER_NAME)} '
        f'      -c user.email={shlex.quote(GIT_USER_EMAIL)} '
        f'      commit -q -m {safe_msg} && '
        f'  git rev-parse HEAD; '
        f'fi'
    )
    r = _exec(slug, script, check=False)
    out = (r.stdout or '').strip()
    if r.returncode != 0:
        raise RuntimeError(f'commit failed: {(r.stderr or out).strip()}')
    if out == 'CLEAN':
        return {'committed': False, 'sha': None, 'message': None}
    return {'committed': True, 'sha': out, 'message': message[:200]}


def merge_branch_into_main(slug: str, branch: str) -> dict:
    """Merge `branch` into main inside the artist root (the main worktree).

    On conflict, aborts the merge and returns the conflicting files so
    the caller can surface them. On success, returns the new HEAD sha.
    """
    safe_branch = shlex.quote(branch)
    # `git merge` reports progress ("Fast-forward", a diffstat) on **stdout**,
    # not stderr. Without the redirect those lines land ahead of the sentinel
    # and `lines[0]` is "Fast-forward" rather than "OK", so a merge that
    # actually succeeded gets reported back as a conflict whose "conflicting
    # files" are diffstat fragments. Route its chatter away and let the exit
    # status decide.
    script = (
        f'git checkout -q main && '
        f'if git -c user.name={shlex.quote(GIT_USER_NAME)} '
        f'    -c user.email={shlex.quote(GIT_USER_EMAIL)} '
        f'    merge --no-edit {safe_branch} >/dev/null 2>&1; then '
        f'  echo OK; git rev-parse HEAD; '
        f'else '
        f'  echo CONFLICT; '
        f'  git diff --name-only --diff-filter=U; '
        f'  git merge --abort 2>/dev/null || true; '
        f'fi'
    )
    r = _exec(slug, script, check=False)
    lines = (r.stdout or '').strip().splitlines()
    if not lines:
        raise RuntimeError(f'merge failed: {(r.stderr or "").strip()}')
    head = lines[0]
    if head == 'OK':
        return {'ok': True, 'sha': lines[1] if len(lines) > 1 else None, 'conflicts': []}
    return {'ok': False, 'sha': None, 'conflicts': lines[1:]}


def delete_branch(slug: str, branch: str) -> None:
    """Force-delete a local branch. Used after a successful merge."""
    safe_branch = shlex.quote(branch)
    _exec(slug, f'git branch -D {safe_branch} 2>/dev/null || true', check=False)


# ─── Worktrees (the part opencode used to own) ───────────────────────────

def _safe_name(name: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9_.-]+', '-', name).strip('-').lower()
    if not cleaned or cleaned.startswith('.'):
        raise ValueError(f'unusable worktree name: {name!r}')
    return cleaned[:40]


def create_worktree(slug: str, name: str | None = None) -> dict:
    """Add a worktree on a fresh branch. Returns a tab record.

    The record's keys mirror what the dashboard read off opencode's Workspace
    (`id`, `name`, `branch`, `directory`) so the tab strip needs no changes.
    """
    ensure_repo(slug)
    base = name or f'tab-{int(time.time()):x}'
    wt_name = _safe_name(base)
    root = worktree_root(slug)
    root.mkdir(parents=True, exist_ok=True)
    target = root / wt_name
    branch = f'autocode/{wt_name}'

    if target.exists():
        raise RuntimeError(f'worktree {wt_name} already exists')

    r = _exec(
        slug,
        f'git worktree add -b {shlex.quote(branch)} {shlex.quote(str(target))} main',
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f'worktree add failed: {(r.stderr or r.stdout).strip()}')
    _log.info(f'[{slug}] worktree {wt_name} -> {target} on {branch}')
    return {'id': wt_name, 'name': wt_name, 'branch': branch, 'directory': str(target)}


def list_worktrees(slug: str) -> list[dict]:
    """Every worktree except the artist root itself."""
    if not is_repo(slug):
        return []
    r = _exec(slug, 'git worktree list --porcelain', check=False)
    if r.returncode != 0:
        return []
    out, current = [], {}
    for line in (r.stdout or '').splitlines():
        if line.startswith('worktree '):
            if current:
                out.append(current)
            current = {'directory': line.split(' ', 1)[1]}
        elif line.startswith('branch ') and current:
            current['branch'] = line.split(' ', 1)[1].replace('refs/heads/', '')
    if current:
        out.append(current)

    root = str(artist_root(slug))
    tabs = []
    for w in out:
        if w.get('directory') == root:
            continue
        name = Path(w['directory']).name
        tabs.append({'id': name, 'name': name,
                     'branch': w.get('branch', ''), 'directory': w['directory']})
    return tabs


def resolve_worktree(slug: str, directory: str) -> Path:
    """Validate that `directory` really is one of this artist's worktrees.

    The old proxy checked `directory.startswith('/home/adze/')`, which was a
    prefix test against a container path supplied by the browser. Resolve the
    path and require containment in this artist's worktree root instead, so a
    crafted `directory` cannot walk into another artist's tree.
    """
    p = Path(directory).resolve()
    root = worktree_root(slug)
    if p != root and root not in p.parents:
        raise ValueError('directory is not inside this artist\'s worktree root')
    if not (p / '.git').exists():
        raise ValueError('directory is not a git worktree')
    return p


def remove_worktree(slug: str, name: str) -> None:
    wt_name = _safe_name(name)
    target = worktree_root(slug) / wt_name
    _exec(slug, f'git worktree remove --force {shlex.quote(str(target))}', check=False)
    _exec(slug, 'git worktree prune', check=False)
    delete_branch(slug, f'autocode/{wt_name}')
