"""
Auto-Code over HTTP+SSE.

The dashboard's chat UI talks to Flask under `/api/adze/autocode/*`; Flask
drives a DeepSeek Harness agent per artist through `dsh_agent`, which runs
the harness runtime as a subprocess of this process.

This used to reverse-proxy a headless `opencode serve` inside a per-artist
`adze-terminal-<slug>` container, reached over the `adze_default` docker
network behind a per-spawn HTTP Basic password. All of that is gone: no
container, no minted password, no readiness poll, no boot-time orphan reaper.
What replaced it is a Python object with a session dict.

**The wire format did not change.** `dashboard.html` speaks opencode's event
schema, so `dsh_agent._translate` maps harness notifications onto it and the
browser is unaware the backend moved. If you change an event shape here, the
dashboard's `dispatch()` is the thing that breaks.

Two capabilities opencode provided that the harness does not, now served
locally: git worktrees for tabs 2+ (`artist_repos.create_worktree`) and
reading a file out of a workspace (`/file/content` below).

Auth surface for incoming dashboard requests mirrors the rest of
admin_api / the old auto_code_bridge: `X-Admin-Token`,
`X-Artist-Slug`, `adze_admin_session` cookie, `adze_session` cookie.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, stream_with_context

import dsh_agent
from artist_repos import (
    artist_root as _artist_dir,
    commit_worktree,
    create_worktree,
    delete_branch,
    ensure_repo,
    list_worktrees,
    merge_branch_into_main,
    remove_worktree,
    resolve_worktree,
    worktree_root,
)

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


# Only these config.json keys are safe to hand the client-facing model. This
# is an allow-list, not a deny-list, so it fails closed: a new config field is
# hidden by default and only surfaces here once someone deliberately adds it.
# Everything omitted is either a credential (`admin_token`, `intake_token`,
# `handover_token`), a login trace (`last_login`, `last_login_ip`), or internal
# ops data the artist must never see (`lead` — our CRM sizing/pricing notes).
# Zee's context is shipped to OpenRouter and persisted to the session JSONL, so
# nothing sensitive may enter it.
_SAFE_CONFIG_KEYS = (
    'name', 'slug', 'domain', 'description', 'contact_email',
    'platform_widgets', 'figma_url',
)


def _build_system_prompt(slug: str) -> str:
    """Same shape Terminal Access uses (terminal_bridge._build_system_prompt):
    numbered `_shared/docs/*.md` files in order, then a redacted view of this
    artist's config.json, then a list of editable pages. Auto-Code prepends
    its own Zee persona block first so Terminal Access (Claude Code) keeps
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
            full = json.loads(cfg.read_text(encoding='utf-8'))
            safe = {k: full[k] for k in _SAFE_CONFIG_KEYS if k in full}
            parts.append(
                '## This artist (config.json)\n\n```json\n'
                + json.dumps(safe, indent=2, ensure_ascii=False) + '\n```'
            )
        except (OSError, ValueError):
            pass

    excluded = {'assets', '.snapshots', '__pycache__', 'backups', 'widgets'}
    pages: list[str] = []
    if artist_root.exists():
        for d in sorted(artist_root.iterdir()):
            if d.is_dir() and d.name not in excluded and not d.name.startswith('.'):
                if (d / 'content.html').exists():
                    pages.append(d.name)
    if pages:
        page_list = '\n'.join(f'- `{p}/content.html` and `{p}/config.json`' for p in pages)
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


# ─── Helpers ─────────────────────────────────────────────────────────────

bp = Blueprint('autocode', __name__, url_prefix='/api/adze/autocode')


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


def _is_external(slug: str) -> bool:
    cfg = _artist_dir(slug) / 'config.json'
    try:
        return bool(cfg.exists() and json.loads(cfg.read_text(encoding='utf-8')).get('remote'))
    except Exception:
        return False


def _session_root(slug: str) -> Path:
    """Where the harness keeps its JSONL session log for this artist.

    Deliberately not inside `artists/<slug>/` — compile.py walks that tree
    and would publish the transcript.
    """
    root = worktree_root(slug).parent / '.sessions' / slug
    root.mkdir(parents=True, exist_ok=True)
    return root


def _workdir_for(slug: str, workspace_id: str | None) -> Path:
    if not workspace_id:
        return _artist_dir(slug)
    for wt in list_worktrees(slug):
        if wt['id'] == workspace_id:
            return Path(wt['directory'])
    raise ValueError(f'unknown workspace {workspace_id}')


def _owned(slug: str, sid: str):
    """Fetch a session, refusing one that belongs to a different artist."""
    s = dsh_agent._mgr.get(sid)
    if s is None or s.slug != slug:
        return None
    return s


# ─── Routes ──────────────────────────────────────────────────────────────

@bp.get('/health')
def health():
    slug, err = _require_slug()
    if err:
        return err
    ok, why = dsh_agent.sdk_available()
    sessions = dsh_agent._mgr.list_for(slug)
    return jsonify({'running': ok and bool(sessions), 'backend': 'deepseek-harness',
                    'model': dsh_agent.DEFAULT_MODEL, 'sessions': len(sessions),
                    'error': '' if ok else why})


@bp.post('/session')
def create_session():
    slug, err = _require_slug()
    if err:
        return err
    ok, why = dsh_agent.sdk_available()
    if not ok:
        return _err(503, 'agent backend unavailable', why)
    body = request.get_json(silent=True) or {}
    try:
        workdir = _workdir_for(slug, (body.get('workspaceID') or '').strip() or None)
    except ValueError as exc:
        return _err(400, str(exc))
    s = dsh_agent._mgr.create(slug, workdir, _session_root(slug))
    return jsonify({'id': s.id, 'title': '', 'directory': str(workdir)})


@bp.get('/session')
def list_sessions():
    slug, err = _require_slug()
    if err:
        return err
    return jsonify(dsh_agent._mgr.list_for(slug))


@bp.get('/session/<sid>')
def get_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    s = _owned(slug, sid)
    if not s:
        return _err(404, 'no such session')
    # Replayed on reconnect so a page refresh does not lose the transcript.
    messages = [{'role': m['role'],
                 'parts': [{'type': 'text', 'text': m['text'], 'id': f'hist-{i}'}]}
                for i, m in enumerate(s.history)]
    return jsonify({**s.summary(), 'messages': messages})


@bp.delete('/session/<sid>')
def delete_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    if not _owned(slug, sid):
        return _err(404, 'no such session')
    dsh_agent._mgr.delete(sid)
    return ('', 204)


@bp.post('/session/<sid>/message')
def post_message(sid):
    """Run one turn. Blocks until it settles; deltas stream over /event.

    Matches opencode's contract: the client awaits this call *and* renders
    from SSE, so the response is the settled message and the stream is the
    live one.
    """
    slug, err = _require_slug()
    if err:
        return err
    s = _owned(slug, sid)
    if not s:
        return _err(404, 'no such session')

    body = request.get_json(silent=True) or {}
    parts = body.get('parts') or []
    text = ''.join(p.get('text', '') for p in parts if p.get('type') == 'text').strip()
    if not text:
        return _err(400, 'empty message')

    model = dsh_agent.MODELS.get((body.get('model') or '').strip(), None) or s.model

    # The persona + docs + page list go in front of the first turn only; the
    # harness keeps its own conversation state after that, so re-sending it
    # every turn would just pay for the same tokens repeatedly.
    if not s.history:
        try:
            text = _build_system_prompt(slug) + '\n\n---\n\n' + text
        except Exception as exc:
            _log.warning(f'[{slug}] system prompt build failed: {exc}')

    result = s.run(text, model=model)
    return jsonify(result)


@bp.post('/session/<sid>/abort')
def abort_session(sid):
    slug, err = _require_slug()
    if err:
        return err
    s = _owned(slug, sid)
    if not s:
        return _err(404, 'no such session')
    # The SDK exposes no mid-turn cancel, so aborting means tearing the
    # runtime down; the next turn respawns it with the session's history
    # replayed from the JSONL log.
    s.close()
    return ('', 204)


@bp.post('/session/<sid>/permissions/<pid>')
def reply_permission(sid, pid):
    slug, err = _require_slug()
    if err:
        return err
    # The composition in dsh_cordis.yml registers no tool that asks for
    # permission (there is no shell), so nothing raises these today. Kept as
    # a 204 so the dashboard's reply path doesn't 404 if one ever appears.
    return ('', 204)


@bp.get('/event')
def event_stream():
    slug, err = _require_slug()
    if err:
        return err
    return Response(
        stream_with_context(dsh_agent.sse_stream(slug)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@bp.get('/file/content')
def file_content():
    """Read one file from the artist tree (or one of its worktrees).

    opencode served this; now it is local. Paths are resolved and then
    required to sit inside the artist's own directory, so `../` cannot walk
    into another artist.
    """
    slug, err = _require_slug()
    if err:
        return err
    rel = (request.args.get('path') or '').strip()
    if not rel:
        return _err(400, 'path required')
    base = _artist_dir(slug)
    wid = (request.args.get('workspaceID') or '').strip()
    if wid:
        try:
            base = _workdir_for(slug, wid)
        except ValueError as exc:
            return _err(400, str(exc))
    try:
        target = (base / rel).resolve()
        if target != base and base not in target.parents:
            return _err(403, 'path escapes the artist directory')
        if not target.is_file():
            return _err(404, 'not found')
        return jsonify({'path': rel, 'content': target.read_text(encoding='utf-8', errors='replace')})
    except OSError as exc:
        return _err(500, 'read failed', str(exc))


# ─── Tabs / workspaces (git worktrees) ───────────────────────────────────
#
# Tab 1 is implicit: the default workspace = artist root on `main`. No
# auto-commit happens there — that branch is co-owned with the dashboard's
# file editor. Tabs 2+ are git worktrees, created here rather than by
# opencode's `/experimental/worktree`. After each assistant turn in a
# worktree tab the client POSTs /tab/<wid>/commit; on close, DELETE removes
# the worktree and its branch.


@bp.post('/tab')
def create_tab():
    slug, err = _require_slug()
    if err:
        return err
    if _is_external(slug):
        return _err(400, 'tabs are not supported on external artists')
    try:
        return jsonify(create_worktree(slug))
    except Exception as exc:
        return _err(500, 'worktree creation failed', str(exc))


@bp.get('/tab')
def list_tabs():
    slug, err = _require_slug()
    if err:
        return err
    try:
        return jsonify(list_worktrees(slug))
    except Exception as exc:
        return _err(500, 'worktree listing failed', str(exc))


@bp.delete('/tab/<wid>')
def close_tab(wid):
    slug, err = _require_slug()
    if err:
        return err
    try:
        remove_worktree(slug, wid)
    except Exception as exc:
        return _err(500, 'worktree removal failed', str(exc))
    return ('', 204)


@bp.post('/tab/<wid>/commit')
def commit_tab(wid):
    """Auto-commit hook called by the client after each assistant turn.

    Body: `{directory: str, message: str}`.
    """
    slug, err = _require_slug()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    directory = (body.get('directory') or '').strip()
    message = (body.get('message') or '').strip() or 'adze: auto-commit'
    if not directory:
        return _err(400, 'directory required')
    try:
        # Containment check, not a string prefix test — see resolve_worktree.
        resolved = resolve_worktree(slug, directory)
    except ValueError as exc:
        return _err(400, str(exc))
    try:
        return jsonify(commit_worktree(slug, str(resolved), message))
    except Exception as exc:
        return _err(500, 'commit failed', str(exc))


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


@bp.get('/session/<sid>/context')
def session_context(sid):
    """Token-window state for the dashboard's usage bar."""
    slug, err = _require_slug()
    if err:
        return err
    s = _owned(slug, sid)
    if not s:
        return _err(404, 'no such session')
    return jsonify({'model': s.model, 'context': dsh_agent.CONTEXT_WINDOW})


@bp.post('/restart')
def restart():
    slug, err = _require_slug()
    if err:
        return err
    for summary in dsh_agent._mgr.list_for(slug):
        dsh_agent._mgr.delete(summary['id'])
    return ('', 204)


@bp.post('/compile')
def compile_artist():
    """Recompile the artist's static site after auto-code edits.

    Called by the dashboard after session.idle when files were edited.
    Runs compile.py --artist <slug> in the Flask working directory.
    External (remote Seed) artists are skipped — their compile lives
    on the remote host.
    """
    import subprocess as _sub

    slug, err = _require_slug()
    if err:
        return err

    if _is_external(slug):
        return jsonify({'ok': True, 'skipped': 'external'})

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
    ok, why = dsh_agent.sdk_available()
    if ok:
        _log.info('auto-code backend: deepseek-harness (%s)', dsh_agent.DEFAULT_MODEL)
    else:
        # Not fatal: the rest of the dashboard must still load. /health and
        # /session report the reason so it surfaces in the UI rather than as
        # a mystery 500 on first message.
        _log.warning('auto-code backend unavailable: %s', why)
