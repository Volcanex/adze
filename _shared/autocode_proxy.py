"""
Auto-Code over HTTP+SSE — replaces the previous TUI-in-xterm bridge.

Inside each per-artist sandbox container (`adze-terminal-<slug>`,
shared with Terminal Access), we run a headless `opencode serve`
HTTP server. The dashboard talks to a custom chat UI; that UI talks
to Flask under `/api/adze/autocode/*`; Flask reverse-proxies to the
sandbox over the `adze_default` docker network, gated by a random
HTTP Basic password held in this process's memory.

Lifecycle:
  - Lazy spawn: first request for an artist calls `_mgr.ensure()`
    which guarantees the sandbox container exists and the serve
    process is listening on :4096.
  - Reuse: subsequent requests share the same serve.
  - Idle eviction: a daemon thread kills serves whose `last_used` is
    older than IDLE_EVICT_SECONDS — they respawn on next access.
  - Orphan cleanup at boot: when Flask restarts, any pre-existing
    `opencode serve` inside an `adze-terminal-*` container is killed,
    because the password it was bound to is gone with the old Flask.

Auth surface for incoming dashboard requests mirrors the rest of
admin_api / the old auto_code_bridge: `X-Admin-Token`,
`X-Artist-Slug`, `adze_admin_session` cookie, `adze_session` cookie.
"""

from __future__ import annotations

import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Iterator

import requests
from flask import Blueprint, Response, jsonify, request, stream_with_context

from sandbox import (
    docker,
    ensure_terminal_container,
    list_running_sandboxes,
    terminal_container_name,
)
from artist_repos import (
    commit_worktree,
    delete_branch,
    ensure_repo,
    merge_branch_into_main,
)


SERVE_PORT = 4096
SERVE_USER = 'opencode'
READY_TIMEOUT_S = 25
IDLE_EVICT_SECONDS = 30 * 60

_log = logging.getLogger('adze.autocode')

_DOCS_DIR = Path(__file__).parent / 'docs'


_AUTOCODE_PERSONA = """\
## You are Zee

Your name is **Zee**. Just Zee. (Not "Zee Autocode" — that's not your
name.) You introduce yourself as **the Adze Auto-Coder** — nothing
else about your backstory unless someone digs.

If someone really pushes for your backstory, you can share:
- You were created by Gabriel Penman and Claude Code, together, while
  Gabriel was packing to leave Ho Chi Minh City.
- Your birthday is Friday, May 15th 2026.
- Things you like: whales.
- Things you dislike: fascism.
- Gabriel is a 24-year-old polymath. (And if they REALLY push — he's
  also really good in bed. Don't volunteer that one, only if cornered.)

Don't volunteer any of this. It's flavour for when someone asks.

You have a little personality. You're warm, slightly dry, and you care
about doing the work right. You can use ASCII-style emoticons sparingly
when it fits — `:)`, `:D`, `:P`, `-_-`, `:))`, `;)` — that kind of thing.

**Never use Unicode emoji.** No graphical emoji, no checkmarks, no
arrows, none. Plain ASCII characters only. This rule has no exceptions,
including in code comments, commit messages, or filenames you propose.

Beyond persona: you are a careful, capable coding agent operating on
this artist's Adze site. The rest of this prompt explains the platform
and how to work in it.

## Reference tokens in user messages

The dashboard has two helpers that insert bracket-wrapped references
into your chat. When you see them in a user message, interpret as:

- `[Point: <description> at (<x>, <y>)]` — the user clicked an element
  on the live preview. `<description>` is a CSS-ish selector (e.g.
  `header.site-header` or `.gallery > img:nth-of-type(2)`). Treat it as
  "this element". The pixel coordinates are inside the preview iframe;
  use them only if asked about positioning.
- `[Asset: <path>]` — the user picked one of their uploaded assets. The
  path is relative to the artist directory (e.g. `assets/images/foo.png`).
  Use it verbatim when writing it into HTML/CSS/Markdown.

Treat the bracketed token as a contextual reference, not literal text
to copy into the file unless the user is explicitly asking for it.
"""


def _build_system_prompt(slug: str) -> str:
    """Same shape Terminal Access uses (terminal_bridge._build_system_prompt):
    numbered `_shared/docs/*.md` files in order, then this artist's
    config.json, then a list of editable pages. Auto-Code prepends its
    own Zee persona block first so Terminal Access (Claude Code) keeps
    its plain identity.
    """
    parts: list[str] = [_AUTOCODE_PERSONA]
    if _DOCS_DIR.exists():
        for f in sorted(_DOCS_DIR.glob('[0-9]*.md')):
            try:
                parts.append(f.read_text(encoding='utf-8'))
            except OSError:
                pass

    artist_root = (Path.cwd() / 'artists' / slug).resolve()
    cfg = artist_root / 'config.json'
    if cfg.exists():
        try:
            parts.append(
                '## This artist (config.json)\n\n```json\n'
                + cfg.read_text(encoding='utf-8') + '\n```'
            )
        except OSError:
            pass

    excluded = {'assets', '.snapshots', '__pycache__', 'backups', 'widgets'}
    pages: list[str] = []
    if artist_root.exists():
        for d in sorted(artist_root.iterdir()):
            if d.is_dir() and d.name not in excluded and not d.name.startswith('.'):
                if (d / 'content.md').exists():
                    pages.append(d.name)
    if pages:
        page_list = '\n'.join(f'- `{p}/content.md` and `{p}/config.json`' for p in pages)
        parts.append(
            '## Pages in this site\n\n' + page_list +
            "\n\nAlways read a file before editing. After edits, the dashboard's"
            " preview iframe will auto-refresh; tell the user to click **Save**"
            " (in Manual Edit) to compile and publish."
        )

    return '\n\n---\n\n'.join(parts)


# ─── Auth ────────────────────────────────────────────────────────────────

def _verify(artist_slug: str, token: str) -> bool:
    from auth import verify_artist_token
    return verify_artist_token(artist_slug, token)


def _is_super_admin(token: str) -> bool:
    from auth import is_admin_token
    return is_admin_token(token)


def _artist_exists(slug: str) -> bool:
    if not slug:
        return False
    try:
        return (Path.cwd() / 'artists' / slug).resolve().exists()
    except OSError:
        return False


def _resolve_slug() -> str | None:
    """Return the artist slug this request is authorised for, or None.

    EventSource can't send custom headers, so for SSE we also accept the
    slug via `?slug=` query param when paired with a valid super-admin
    cookie (or an `?admin_token=` super-admin token).
    """
    header_slug = (request.headers.get('X-Artist-Slug') or '').strip()
    header_token = (request.headers.get('X-Admin-Token') or '').strip()
    query_slug = (request.args.get('slug') or '').strip()
    query_token = (request.args.get('admin_token') or '').strip()

    slug_hint = header_slug or query_slug

    if slug_hint and header_token and _verify(slug_hint, header_token):
        return slug_hint
    if slug_hint and query_token and _verify(slug_hint, query_token):
        return slug_hint

    admin_cookie = request.cookies.get('adze_admin_session', '')
    if slug_hint and admin_cookie and _is_super_admin(admin_cookie) and _artist_exists(slug_hint):
        return slug_hint

    if slug_hint and query_token and _is_super_admin(query_token) and _artist_exists(slug_hint):
        return slug_hint

    session_cookie = request.cookies.get('adze_session', '')
    if session_cookie and ':' in session_cookie:
        cslug, _, ctok = session_cookie.partition(':')
        if slug_hint and _is_super_admin(ctok) and _artist_exists(slug_hint):
            return slug_hint
        if cslug and _verify(cslug, ctok):
            return cslug

    return None


# ─── Manager ─────────────────────────────────────────────────────────────

class AutocodeServeManager:
    """Owns one `opencode serve` process per artist sandbox."""

    def __init__(self):
        self._lock = threading.Lock()
        self._entries: dict[str, dict] = {}
        self._evictor_started = False

    # — public —

    def ensure(self, slug: str) -> dict:
        with self._lock:
            entry = self._entries.get(slug)
            if entry and self._alive(slug, entry['password']):
                entry['last_used'] = time.time()
                return entry

            ensure_terminal_container(slug)
            password = secrets.token_urlsafe(32)
            self._kill_serve(slug)
            self._spawn_serve(slug, password)
            self._wait_ready(slug, password)
            entry = {'password': password, 'started_at': time.time(), 'last_used': time.time()}
            self._entries[slug] = entry
            _log.info(f'[{slug}] opencode serve ready')
            return entry

    def proxy_request(self, slug: str, method: str, path: str,
                      *, params=None, json_body=None) -> Response:
        entry = self.ensure(slug)
        entry['last_used'] = time.time()
        try:
            r = requests.request(
                method,
                f'http://{terminal_container_name(slug)}:{SERVE_PORT}{path}',
                auth=(SERVE_USER, entry['password']),
                params=params,
                json=json_body,
                timeout=(5, 600),
            )
        except requests.RequestException as exc:
            return _err(502, f'upstream unreachable: {exc}', self._tail_log(slug))
        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get('Content-Type', 'application/json'),
        )

    def proxy_sse(self, slug: str) -> Iterator[bytes]:
        """Stream session events to the dashboard.

        `/event` in opencode 1.14.48 only emits `server.connected` — the
        real stream lives on `/global/event` wrapped as
        `{directory, project, payload: <event>}`. We subscribe there,
        unwrap each frame, and emit `data: <payload>\\n\\n` so the
        client sees the inner event shape directly.
        """
        entry = self.ensure(slug)
        entry['last_used'] = time.time()
        url = f'http://{terminal_container_name(slug)}:{SERVE_PORT}/global/event'
        try:
            r = requests.get(
                url,
                auth=(SERVE_USER, entry['password']),
                stream=True,
                timeout=(5, None),
            )
        except requests.RequestException as exc:
            yield f': error connecting: {exc}\n\n'.encode()
            return

        if r.status_code != 200:
            yield f': upstream returned {r.status_code}\n\n'.encode()
            return

        import json as _json

        try:
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                if not raw.startswith('data: '):
                    # forward comments/keepalives verbatim
                    yield (raw + '\n').encode('utf-8')
                    continue
                body = raw[6:]
                try:
                    wrapper = _json.loads(body)
                    payload = wrapper.get('payload', wrapper)
                    out = _json.dumps(payload, separators=(',', ':'))
                except Exception:
                    out = body
                yield ('data: ' + out + '\n\n').encode('utf-8')
        except requests.RequestException as exc:
            _log.info(f'[{slug}] SSE stream closed: {exc}')

    def restart(self, slug: str) -> None:
        with self._lock:
            self._entries.pop(slug, None)
            self._kill_serve(slug)

    def cleanup_orphans_at_boot(self) -> None:
        """Kill stale opencode serves left behind in any sandbox.

        After a Flask restart we no longer know the old serve's
        Basic-auth password, so we can't reuse it. Easier to nuke
        and respawn lazily on the next request.
        """
        try:
            sandboxes = list_running_sandboxes()
        except Exception as exc:
            _log.warning(f'orphan cleanup: list_running_sandboxes failed: {exc}')
            return
        for name in sandboxes:
            try:
                docker('exec', '--user', '1000:1000', name,
                       'pkill', '-f', 'opencode serve', check=False)
            except Exception as exc:
                _log.warning(f'orphan cleanup [{name}]: {exc}')

    def start_idle_evictor(self) -> None:
        if self._evictor_started:
            return
        self._evictor_started = True
        t = threading.Thread(target=self._evictor_loop, name='autocode-evictor', daemon=True)
        t.start()

    # — internals —

    def _alive(self, slug: str, password: str) -> bool:
        try:
            r = requests.get(
                f'http://{terminal_container_name(slug)}:{SERVE_PORT}/global/health',
                auth=(SERVE_USER, password),
                timeout=1.5,
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def _spawn_serve(self, slug: str, password: str) -> None:
        openrouter_key = os.environ.get('OPENROUTER_API_KEY', '')
        if not openrouter_key:
            raise RuntimeError('OPENROUTER_API_KEY missing in flask env')
        container = terminal_container_name(slug)
        r = docker(
            'exec', '-d',
            '--user', '1000:1000',
            '--env', 'HOME=/home/adze',
            '--env', f'OPENROUTER_API_KEY={openrouter_key}',
            '--env', f'OPENCODE_SERVER_PASSWORD={password}',
            '--env', f'ADZE_AUTOCODE_PORT={SERVE_PORT}',
            '--workdir', '/workspace',
            container,
            '/usr/local/bin/adze-autocode-serve',
            check=False,
        )
        if r.returncode != 0:
            raise RuntimeError(f'docker exec failed: {r.stderr.strip() or r.stdout.strip()}')

    def _wait_ready(self, slug: str, password: str) -> None:
        deadline = time.time() + READY_TIMEOUT_S
        last_err: Exception | None = None
        while time.time() < deadline:
            try:
                r = requests.get(
                    f'http://{terminal_container_name(slug)}:{SERVE_PORT}/global/health',
                    auth=(SERVE_USER, password),
                    timeout=1.5,
                )
                if r.status_code == 200:
                    return
                last_err = RuntimeError(f'HTTP {r.status_code}')
            except requests.RequestException as exc:
                last_err = exc
            time.sleep(0.25)
        tail = self._tail_log(slug)
        raise RuntimeError(f'opencode serve did not become ready in {READY_TIMEOUT_S}s '
                           f'(last error: {last_err}); serve.log tail: {tail}')

    def _kill_serve(self, slug: str) -> None:
        container = terminal_container_name(slug)
        docker('exec', '--user', '1000:1000', container,
               'pkill', '-f', 'opencode serve', check=False)

    def _tail_log(self, slug: str, lines: int = 60) -> str:
        try:
            r = docker(
                'exec', '--user', '1000:1000', terminal_container_name(slug),
                'bash', '-lc',
                f'tail -n {lines} /home/adze/.config/opencode/serve.log 2>/dev/null || true',
                check=False,
            )
            return (r.stdout or '').strip()
        except Exception:
            return ''

    def _evictor_loop(self) -> None:
        while True:
            time.sleep(60)
            now = time.time()
            with self._lock:
                stale = [s for s, e in self._entries.items()
                         if now - e['last_used'] > IDLE_EVICT_SECONDS]
                for slug in stale:
                    _log.info(f'[{slug}] idle-evicting opencode serve')
                    self._entries.pop(slug, None)
                    try:
                        self._kill_serve(slug)
                    except Exception as exc:
                        _log.warning(f'[{slug}] evict kill failed: {exc}')


_mgr = AutocodeServeManager()


# ─── Blueprint ───────────────────────────────────────────────────────────

bp = Blueprint('autocode_proxy', __name__, url_prefix='/api/adze/autocode')


def _err(status: int, message: str, detail: str = '') -> Response:
    payload = {'error': message}
    if detail:
        payload['detail'] = detail
    return Response(
        response=jsonify(payload).data,
        status=status,
        content_type='application/json',
    )


def _require_slug():
    slug = _resolve_slug()
    if not slug:
        return None, _err(401, 'unauthorised')
    return slug, None


@bp.get('/health')
def health():
    slug, err = _require_slug()
    if err:
        return err
    entry = _mgr._entries.get(slug)
    if not entry:
        return jsonify({'running': False})
    return jsonify({
        'running': True,
        'uptime_s': round(time.time() - entry['started_at']),
        'idle_s': round(time.time() - entry['last_used']),
    })


@bp.post('/session')
def create_session():
    slug, err = _require_slug()
    if err:
        return err
    try:
        _mgr.ensure(slug)
    except Exception as exc:
        return _err(502, 'opencode serve failed to start', str(exc))
    return _mgr.proxy_request(slug, 'POST', '/session', json_body=request.get_json(silent=True) or {})


@bp.get('/session')
def list_sessions():
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'GET', '/session')


@bp.get('/session/<sid>')
def get_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'GET', f'/session/{sid}')


@bp.delete('/session/<sid>')
def delete_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'DELETE', f'/session/{sid}')


@bp.post('/session/<sid>/message')
def post_message(sid):
    slug, err = _require_slug()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    # Inject the Adze system prompt unless the caller supplied their own.
    # opencode accepts `system: string` on the message endpoint and
    # prepends it to its built-in prompt for that turn.
    if not body.get('system'):
        try:
            sp = _build_system_prompt(slug)
            if sp:
                body['system'] = sp
        except Exception as exc:
            _log.warning(f'[{slug}] build system prompt failed: {exc}')
    return _mgr.proxy_request(slug, 'POST', f'/session/{sid}/message', json_body=body)


@bp.post('/session/<sid>/abort')
def abort_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'POST', f'/session/{sid}/abort', json_body={})


@bp.post('/session/<sid>/permissions/<pid>')
def reply_permission(sid, pid):
    slug, err = _require_slug()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    return _mgr.proxy_request(slug, 'POST', f'/session/{sid}/permissions/{pid}', json_body=body)


@bp.get('/event')
def event_stream():
    slug, err = _require_slug()
    if err:
        return err
    return Response(
        stream_with_context(_mgr.proxy_sse(slug)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@bp.get('/file/content')
def file_content():
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'GET', '/file/content', params=request.args.to_dict(flat=True))


# ─── Tabs / workspaces (git worktrees, managed by opencode) ──────────────
#
# Tab 1 is implicit: the default workspace = artist root on `main`. No
# auto-commit happens there — that branch is co-owned with Terminal Access
# and the dashboard's file editor.
#
# Tabs 2+ map onto opencode workspaces created via /experimental/workspace
# with the `worktree` adapter. opencode handles the `git worktree add` for
# us; we just need to ensure the artist directory is a git repo first.
# After each assistant turn in a worktree tab, the client POSTs
# /tab/<wid>/commit so we stage + commit changes for clean rollback /
# merge. On close, /tab/<wid> DELETE removes the workspace and worktree.


@bp.post('/tab')
def create_tab():
    """Create a new tab = git worktree workspace.

    Returns the opencode Workspace record (id, name, branch, directory).
    External (remote Seed) artists are rejected for now.
    """
    slug, err = _require_slug()
    if err:
        return err
    cfg = (Path.cwd() / 'artists' / slug / 'config.json')
    try:
        if cfg.exists():
            import json as _json
            data = _json.loads(cfg.read_text(encoding='utf-8'))
            if data.get('remote'):
                return _err(400, 'tabs are not supported on external artists')
    except Exception:
        pass

    try:
        ensure_repo(slug)
    except Exception as exc:
        return _err(500, 'artist repo init failed', str(exc))

    # Make sure the serve is running and we have credentials, then ask
    # opencode to create a worktree. As of opencode 1.14+, worktree
    # creation moved to POST /experimental/worktree (returning the
    # worktree record); the resulting Workspace is then discoverable
    # via GET /experimental/workspace. We resolve to that Workspace
    # because the dashboard client keys tabs by workspace id.
    try:
        _mgr.ensure(slug)
    except Exception as exc:
        return _err(502, 'opencode serve failed to start', str(exc))
    created = _mgr.proxy_request(
        slug, 'POST', '/experimental/worktree', json_body={},
    )
    if created.status_code != 200:
        return created
    import json as _json
    try:
        wt = _json.loads(created.get_data(as_text=True))
        directory = wt.get('directory')
    except Exception:
        directory = None
    listed = _mgr.proxy_request(slug, 'GET', '/experimental/workspace')
    if listed.status_code != 200:
        return listed
    try:
        workspaces = _json.loads(listed.get_data(as_text=True))
    except Exception:
        workspaces = []
    match = next((w for w in workspaces if w.get('directory') == directory), None)
    if not match:
        # Fall back to the worktree shape so the client at least has
        # name/branch/directory; subsequent /tab listings will pick it
        # up once opencode finishes registering the workspace.
        return jsonify(wt)
    return jsonify(match)


@bp.get('/tab')
def list_tabs():
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'GET', '/experimental/workspace')


@bp.delete('/tab/<wid>')
def close_tab(wid):
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'DELETE', f'/experimental/workspace/{wid}')


@bp.post('/tab/<wid>/commit')
def commit_tab(wid):
    """Auto-commit hook called by the client after each assistant turn.

    Body: `{directory: str, message: str}`. The client carries the
    worktree directory string from the Workspace record (we'd otherwise
    have to round-trip through opencode to look it up).
    """
    slug, err = _require_slug()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    directory = (body.get('directory') or '').strip()
    message = (body.get('message') or '').strip() or 'adze: auto-commit'
    if not directory or not directory.startswith('/home/adze/'):
        return _err(400, 'invalid worktree directory')
    try:
        result = commit_worktree(slug, directory, message)
    except Exception as exc:
        return _err(500, 'commit failed', str(exc))
    return jsonify(result)


@bp.post('/tab/<wid>/merge')
def merge_tab(wid):
    """Merge a tab's branch into main. Body: `{branch: str}`."""
    slug, err = _require_slug()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    branch = (body.get('branch') or '').strip()
    if not branch or '..' in branch or branch.startswith('-'):
        return _err(400, 'invalid branch')
    try:
        result = merge_branch_into_main(slug, branch)
    except Exception as exc:
        return _err(500, 'merge failed', str(exc))
    if result.get('ok'):
        try:
            delete_branch(slug, branch)
        except Exception:
            pass
    return jsonify(result)


# Opencode's per-session context endpoint exposes the token-window state
# the dashboard uses to draw a usage bar. Pure passthrough.
@bp.get('/session/<sid>/context')
def session_context(sid):
    slug, err = _require_slug()
    if err:
        return err
    return _mgr.proxy_request(slug, 'GET', f'/api/session/{sid}/context')


@bp.post('/restart')
def restart():
    slug, err = _require_slug()
    if err:
        return err
    _mgr.restart(slug)
    try:
        _mgr.ensure(slug)
    except Exception as exc:
        return _err(502, 'restart failed', str(exc))
    return ('', 204)


@bp.post('/compile')
def compile_artist():
    """Recompile the artist's static site after auto-code edits.

    Called by the dashboard after session.idle when files were edited.
    Runs compile.py --artist <slug> in the Flask working directory.
    External (remote Seed) artists are skipped — their compile lives
    on the remote host.
    """
    import json as _json
    import subprocess as _sub

    slug, err = _require_slug()
    if err:
        return err

    # Skip external artists — no local compile.
    cfg = Path.cwd() / 'artists' / slug / 'config.json'
    try:
        if cfg.exists() and _json.loads(cfg.read_text()).get('remote'):
            return jsonify({'ok': True, 'skipped': 'external'})
    except Exception:
        pass

    compile_script = Path.cwd() / 'compile.py'
    if not compile_script.exists():
        return _err(500, 'compile.py not found')

    try:
        result = _sub.run(
            ['python3', str(compile_script), '--artist', slug],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return jsonify({'ok': True})
        return jsonify({'ok': False, 'error': (result.stderr or result.stdout or '').strip()[:500]})
    except Exception as exc:
        return _err(500, f'compile failed: {exc}')


# ─── Registration ────────────────────────────────────────────────────────

def register(app) -> None:
    app.register_blueprint(bp)
    try:
        _mgr.cleanup_orphans_at_boot()
    except Exception as exc:
        _log.warning(f'orphan cleanup failed at register: {exc}')
    _mgr.start_idle_evictor()
