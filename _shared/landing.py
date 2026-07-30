"""
The artist landing page — theirdomain.com/admin

A system module, not a feature. Features are opt-in per artist via
config.json; this has to be universal, because the artists who most need a
front door are exactly the 26 who don't have a content admin and who got a
bare 404 here before.

It reuses ArtistAdmin wholesale (domain_guard, auth_required, login, logout,
password) so there is no second copy of the auth code, and it deliberately
sets the SAME `{slug}_admin` cookie the content admin uses. That is the whole
trick: one login covers both surfaces, so the big button is a plain link that
lands already authenticated rather than a second sign-in.

Registered from flask_server after _register_artist_features(), which hands
over its domain -> content-panel map so the button knows where to point.
"""

import json
import time
import uuid
from pathlib import Path

from flask import jsonify, make_response, request

from features.artist_admin import ArtistAdmin

ARTISTS = Path('artists')
SHELL_DIR = Path('_shared/shell')
TOKENS_DIR = Path('design-language/adze/tokens')
TOKEN_FILES = ['colors.css', 'typography.css', 'spacing.css', 'motion.css', 'base.css']

# One pool for the whole studio, not per-artist — the point is a single place
# to read everyone's problems. JSONL because the /contact precedent rewrites
# the entire file per submission, which is O(n), racy, and loses the lot on a
# partial write. Append-only never loses anything.
FEEDBACK_PATH = Path('data/feedback.jsonl')
STATUS_NOTE_PATH = Path('data/status_note.json')
STATUS_JSON = Path('logs/status.json')
STATUS_STALE_AFTER = 20 * 60      # cron writes every 5 min


def _strip_domain(d):
    d = (d or '').strip().lower()
    for p in ('https://', 'http://', 'www.'):
        if d.startswith(p):
            d = d[len(p):]
    return d.rstrip('/')


def _live_artists():
    """slug -> config, for artists with a real domain. Skips the template
    (its domain is a literal {{DOMAIN}}) and the example scaffold."""
    out = {}
    if not ARTISTS.exists():
        return out
    for d in sorted(ARTISTS.iterdir()):
        if not d.is_dir() or d.name.startswith('_') or d.name == 'example-artist':
            continue
        p = d / 'config.json'
        if not p.exists():
            continue
        try:
            cfg = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            print(f"  !! landing: {d.name}/config.json is unparseable — skipped")
            continue
        dom = _strip_domain(cfg.get('domain'))
        if not dom or '{{' in dom or cfg.get('is_stub'):
            continue
        out[d.name] = cfg
    return out


def _status_payload(slug):
    """Deliberately reduced from the super-admin status: an artist can't act on
    CPU or backup age, and shouldn't see another tenant's numbers."""
    now = int(time.time())
    note = None
    try:
        st = json.loads(STATUS_JSON.read_text())
        age = now - int(st.get('ts') or 0)
        if age > STATUS_STALE_AFTER:
            editor = 'degraded'
        elif (st.get('docker') or {}).get('status') not in (None, 'running'):
            editor = 'degraded'
        else:
            editor = 'ok'
    except (OSError, json.JSONDecodeError, ValueError):
        # No status file at all (the usual case — nothing writes one yet).
        # This is 'unknown', NOT 'degraded': the artist is reading this page,
        # which is served by the very process the status would describe, so
        # claiming trouble would be crying wolf permanently. The page renders
        # nothing for 'unknown' unless Gabriel has left a note.
        editor = 'unknown'
    try:
        note = (json.loads(STATUS_NOTE_PATH.read_text()) or {}).get('note') or None
    except (OSError, json.JSONDecodeError):
        pass
    site = 'ok' if (Path('output/artists') / slug / 'index.html').exists() else 'unknown'
    return {'editor': editor, 'site': site, 'checked': now, 'note': note}


def _append_feedback(rec):
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_PATH, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + '\n')


def register(app, content_panels=None):
    """Mount /admin and a landing blueprint per artist.

    `content_panels` is the domain -> content-admin PANEL_URL map built by
    _register_artist_features, passed in rather than recomputed so the two can
    never disagree about who has a content admin.
    """
    content_panels = content_panels or {}
    by_domain = {}
    artists = _live_artists()

    for slug, cfg in artists.items():
        domain = _strip_domain(cfg.get('domain'))
        by_domain[domain] = slug
        panel_url = f'/api/landing/{slug}/panel'
        admin = ArtistAdmin(slug, cookie=f'{slug}_admin', panel_url=panel_url,
                            blueprint_name=f'{slug}_landing')
        _register_one(app, admin, cfg, content_panels.get(domain))

    @app.route('/admin')
    @app.route('/admin/')
    def admin_landing_dispatch():
        from flask import redirect, abort
        host = request.headers.get('Host', '').split(':')[0].removeprefix('www.')
        slug = by_domain.get(host)
        if not slug:
            abort(404)
        return redirect(f'/api/landing/{slug}/panel', code=302)

    print(f"  Landing page mounted for {len(by_domain)} artists "
          f"({len(content_panels)} with a content admin)")
    return by_domain


def _register_one(app, admin, cfg, content_url):
    slug = admin.slug
    prefix = admin.prefix

    theme = cfg.get('admin_theme') or {}
    bootstrap = _BOOTSTRAP.format(
        prefix=prefix,
        title=(cfg.get('name') or slug),
        boot=json.dumps({
            'prefix': prefix,
            'slug': slug,
            'name': cfg.get('name') or slug,
            'domain': _strip_domain(cfg.get('domain')),
            'theme': theme,
            # None when the artist has no content admin — the page swaps the
            # primary button for the advanced editor rather than showing a
            # button that goes nowhere.
            'contentUrl': content_url,
        }),
    )
    admin.register_core(bootstrap)

    _ASSETS = {
        'adze-ui.js':       (SHELL_DIR / 'adze-ui.js', 'application/javascript'),
        'admin-shell.css':  (SHELL_DIR / 'admin-shell.css', 'text/css'),
        'admin-landing.js': (SHELL_DIR / 'admin-landing.js', 'application/javascript'),
    }
    _ASSETS.update({f'tokens/{n}': (TOKENS_DIR / n, 'text/css') for n in TOKEN_FILES})

    @admin.bp.route(f'{prefix}/asset/<path:name>', endpoint=f'{slug}_landing_asset')
    def asset(name):
        entry = _ASSETS.get(name)
        if not entry:
            return jsonify({'error': 'not found'}), 404
        path, mime = entry
        try:
            return make_response(path.read_bytes(), 200, {
                'Content-Type': mime, 'Cache-Control': 'no-cache'})
        except OSError:
            return jsonify({'error': 'not found'}), 404

    @admin.bp.route(f'{prefix}/analytics', endpoint=f'{slug}_landing_analytics')
    @admin.auth_required
    def analytics():
        from admin_api import analytics_payload
        data = analytics_payload(slug)
        # When measurement started, so the page can tell "nobody came" apart
        # from "we weren't counting" — see the empty states in admin-landing.js.
        # Sidecar rather than config.json; compile.py writes it (see there for
        # why it stays out of the hand-authored config).
        since = None
        try:
            since = json.loads((ARTISTS / slug / '.analytics.json').read_text()).get('since')
        except (OSError, json.JSONDecodeError):
            pass
        data['analytics_since'] = since
        return jsonify(data)

    @admin.bp.route(f'{prefix}/status', endpoint=f'{slug}_landing_status')
    @admin.auth_required
    def status():
        return jsonify(_status_payload(slug))

    @admin.bp.route(f'{prefix}/handoff', endpoint=f'{slug}_landing_handoff')
    @admin.auth_required
    def handoff():
        """Into the control panel without a second login. Mints adze_session
        same-origin on the artist's own domain, so no token rides in the URL."""
        from flask import redirect
        cookie_value = f'{slug}:{admin.token()}'
        try:
            import accounts
            acct = accounts.account_for_slug(slug)
            if acct is not None:
                cookie_value = f'{slug}:' + accounts.create_session(
                    acct['id'], slug,
                    ip=request.headers.get('X-Real-IP') or request.remote_addr,
                    ua=request.headers.get('User-Agent'))
        except Exception:
            pass
        resp = redirect(f'/api/adze/dashboard?slug={slug}', code=302)
        resp.set_cookie('adze_session', cookie_value, httponly=True, samesite='Lax',
                        secure=request.headers.get('X-Forwarded-Proto') == 'https',
                        max_age=30 * 24 * 3600, path='/')
        return resp

    @admin.bp.route(f'{prefix}/feedback', methods=['POST'], endpoint=f'{slug}_landing_feedback')
    @admin.auth_required
    def feedback():
        try:
            from admin_api import _rate_limit
            _rate_limit(f'feedback:{slug}', 5, 300)
        except ImportError:
            pass
        data = request.get_json(silent=True) or {}
        msg = (data.get('message') or '').strip()
        if len(msg) < 4:
            return jsonify({'error': 'Tell us a little more than that.'}), 400
        if len(msg) > 4000:
            return jsonify({'error': 'That is too long — 4000 characters max.'}), 400
        cfg = cfg_now(slug)
        rec = {
            'id': str(uuid.uuid4()),
            'ts': int(time.time()),
            'slug': slug,
            'domain': _strip_domain(cfg.get('domain')),
            'name': cfg.get('name') or slug,
            'kind': (data.get('kind') or 'other')[:32],
            'message': msg,
            'reply_to': (data.get('reply_to') or '')[:200],
            'status': 'new',
            'seen': False,
            'ua': (request.headers.get('User-Agent') or '')[:300],
        }
        _append_feedback(rec)

        # The file write is the source of truth; the email is a notification.
        # A dead SMTP box must never make an artist's message disappear.
        try:
            import mailer
            mailer.send_async(
                subject=f'[Adze] {rec["kind"]} from {rec["name"]}',
                text_body=(f'{rec["name"]} ({rec["domain"]}) wrote:\n\n{msg}\n\n'
                           f'Reply-to: {rec["reply_to"] or "(not given)"}\n'
                           f'Artist slug: {slug}\n'),
                reply_to=rec['reply_to'] or None)
        except Exception:
            pass
        return jsonify({'ok': True})

    # Must be the LAST thing in this function: Flask refuses any @bp.route
    # added after the blueprint is registered, and fails at import time rather
    # than silently dropping the route.
    admin.bp.url_prefix = ''
    app.register_blueprint(admin.bp)


def cfg_now(slug):
    """Re-read config rather than closing over it — publishes rewrite it."""
    try:
        return json.loads((ARTISTS / slug / 'config.json').read_text())
    except (OSError, json.JSONDecodeError):
        return {}


# fonts.css is deliberately not linked: it @imports Google Fonts, which is
# render-blocking and serial inside a linked sheet. Preconnect + <link> instead.
_BOOTSTRAP = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{prefix}/asset/tokens/colors.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/typography.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/spacing.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/motion.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/base.css">
<link rel="stylesheet" href="{prefix}/asset/admin-shell.css">
</head>
<body>
<div id="adze-admin-root"></div>
<script>window.ADZE_LANDING = {boot};</script>
<script src="{prefix}/asset/adze-ui.js"></script>
<script src="{prefix}/asset/admin-landing.js"></script>
</body>
</html>
"""
