"""
Per-artist git repos for the Auto-Coder tabs/worktrees feature.

Each artist directory (`artists/<slug>/`) is *lazily* initialised as a
standalone git repo on the first Auto-Coder tab open. The repo is
local-only — no remote, no owner — and exists purely so that opencode's
`workspace` adapter (`type: "worktree"`) has somewhere to branch from
and so we can auto-commit per assistant turn inside a worktree.

The outer `/home/gabriel/adze` repo keeps tracking the artist's files
as before; the inner `.git/` is excluded via the root `.gitignore`. The
two repos share a working tree but record independent history.

Git commands run **inside the per-artist sandbox container** (uid 1000,
adze user) so file ownership stays consistent with the rest of the
sandbox. Operating from the host as root would leave root-owned objects
behind in `.git/`.
"""

from __future__ import annotations

import logging
import shlex
import subprocess

from sandbox import docker, ensure_terminal_container, terminal_container_name

_log = logging.getLogger('adze.repos')

GIT_USER_NAME = 'Adze Auto-Coder'
GIT_USER_EMAIL = 'autocoder@adze.local'

INNER_GITIGNORE = """\
# Inner per-artist repo — opencode worktrees live elsewhere
# (~/.local/share/opencode/worktree/<projectID>/<name>/), so we only
# need to keep large/regen-able junk out of the artist's own history.
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


def _exec(slug: str, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command inside the artist sandbox container.

    Always runs as uid 1000 (adze) with HOME set so git's per-user
    config and credential lookups work.
    """
    container = terminal_container_name(slug)
    return docker(
        'exec',
        '--user', '1000:1000',
        '--env', 'HOME=/home/adze',
        '--workdir', '/workspace',
        container,
        'bash', '-lc', cmd,
        check=check,
    )


def is_repo(slug: str) -> bool:
    r = _exec(slug, 'git rev-parse --is-inside-work-tree 2>/dev/null', check=False)
    return r.returncode == 0 and (r.stdout or '').strip() == 'true'


def ensure_repo(slug: str) -> None:
    """Idempotently turn `artists/<slug>/` into a git repo on branch main.

    Safe to call on every tab open. If already initialised, no-ops.
    """
    ensure_terminal_container(slug)
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

    `worktree_dir` is the absolute path *inside the sandbox container*
    (e.g. `/home/adze/.local/share/opencode/worktree/<proj>/<name>`).
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
    script = (
        f'cd /workspace && '
        f'git checkout -q main && '
        f'if git -c user.name={shlex.quote(GIT_USER_NAME)} '
        f'    -c user.email={shlex.quote(GIT_USER_EMAIL)} '
        f'    merge --no-edit {safe_branch}; then '
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
    _exec(slug, f'cd /workspace && git branch -D {safe_branch} 2>/dev/null || true', check=False)
