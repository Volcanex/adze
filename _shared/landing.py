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

Five sections: Overview, Files, History, Export, Account. The last four are
served by the routes below, and every one of them reads through an admin_api
payload function rather than walking the artist directory here — admin_api
owns path safety and the definition of what an export or a snapshot is.
Nothing on this page writes a file; the single mutating route (restore) calls
the control panel's own function and then rebuilds, because restoring without
republishing leaves the source and the live site disagreeing.

Registered from flask_server after _register_artist_features(), which hands
over its domain -> content-panel map so the button knows where to point.
"""

import json
import time
import uuid
from pathlib import Path

from flask import jsonify, make_response, request, send_file

from features.artist_admin import ArtistAdmin
import shell_assets

ARTISTS = Path('artists')
OUTPUT = Path('output/artists')

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


_TITLE_SEPS = (' — ', ' – ', ' | ', ' - ', ' · ')


def _repeated_tail(titles):
    """The "— Rose Jones" that every page title carries, discovered from the
    titles themselves rather than taken from config.

    config's `name` is not reliable for this: it is the artist ("Rose") while
    the tab is the site ("Rose Jones"), and the tab is what ends up in this
    list. Two pages sharing a tail is a house style; one page is a title that
    happens to contain a dash, so a single hit is ignored.
    """
    counts = {}
    for t in titles:
        for sep in _TITLE_SEPS:
            i = t.rfind(sep)
            if i > 0:
                counts[t[i:]] = counts.get(t[i:], 0) + 1
    if not counts:
        return None
    tail, n = max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))
    return tail if n >= 2 else None


def _clean_title(title, tails, rel):
    """Page titles are written for the browser tab, so a list of them repeats
    the site's own name down every row and buries the one word that differs.
    Strip that tail, and give a folder-derived title a capital so "sparrow"
    doesn't sit next to "Bed". Titles the artist typed in caps ("GOOD GRIEF")
    are left exactly as typed.
    """
    t = (title or '').strip()
    low = t.lower()
    for tail in tails:
        # Case-insensitive because half these tails are the slug as typed
        # ("About — chris"), and `>` not `>=` because the home page's title IS
        # the site name — trimming that leaves an empty chip.
        if tail and low.endswith(tail.lower()) and len(t) > len(tail):
            t = t[:-len(tail)].strip()
            break
    if not t:
        t = rel.split('/')[-1].replace('-', ' ').replace('_', ' ')
    if t[:1].islower():
        t = t[0].upper() + t[1:]
    return t


def _site_payload(slug, cfg):
    """The artist's site as it actually stands, read from compiled output
    rather than from the source tree: a page an artist can't reach isn't a
    page, and the whole point of this block is links they can click.

    URL shape follows flask_server's artist routing — `home` is the site root,
    every other page is `/<page>/`. Nested pages keep their full path.
    """
    domain = _strip_domain(cfg.get('domain'))
    base = f'https://{domain}' if domain else f'/preview/{slug}'
    out_root = OUTPUT / slug

    pages = []
    published = None
    if out_root.is_dir():
        for idx in sorted(out_root.rglob('index.html')):
            rel = idx.parent.relative_to(out_root).as_posix()
            if rel == '.':
                continue          # the root redirect stub, not a page
            title = None
            try:
                page_cfg = json.loads((ARTISTS / slug / rel / 'config.json').read_text())
                title = page_cfg.get('title')
            except (OSError, json.JSONDecodeError):
                pass
            pages.append({
                'path': rel,
                'title': title,
                'url': base + ('/' if rel == 'home' else f'/{rel}/'),
                'home': rel == 'home',
            })
            try:
                mtime = int(idx.stat().st_mtime)
                published = mtime if published is None else max(published, mtime)
            except OSError:
                pass

    # The discovered tail first, then the two names we know for certain — the
    # artist's display name and the slug, both of which turn up as a tail on
    # sites too small for _repeated_tail to see a pattern in.
    tails = [_repeated_tail([p['title'] for p in pages if p['title']])]
    for name in (cfg.get('name'), slug):
        if name:
            tails += [sep + name for sep in _TITLE_SEPS]
    for p in pages:
        p['title'] = _clean_title(p['title'], tails, p['path'])

    pages.sort(key=lambda p: (not p['home'], p['path']))
    return {'domain': domain, 'url': base, 'pages': pages, 'published': published}


def _export_info(slug):
    """Size of what an export would contain, without building the zip twice.
    Uncompressed bytes on disk — honest, and cheap enough to read on load."""
    out_root = OUTPUT / slug
    files = 0
    total = 0
    if out_root.is_dir():
        for p in out_root.rglob('*'):
            if p.is_file():
                files += 1
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    return {'files': files, 'bytes': total, 'ready': files > 0}


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
        token_links=shell_assets.token_links(prefix),
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

    _ASSETS = shell_assets.shell_assets('admin-landing.js', 'file-viewer.js')
    _ASSETS.update(shell_assets.token_assets())
    # Vendored, never CDN — same rule as the content admin's editors. Served
    # under `vendor/` so the two surfaces address them identically.
    _ASSETS.update({
        f'vendor/{k}': v
        for k, v in shell_assets.vendor_assets('highlight.js', 'qrcode.js').items()
    })

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

    # ── the artist's own site: links, files, export, history ─────────────────
    #
    # Every route below reads through admin_api's payload functions rather than
    # re-walking the artist directory here. admin_api owns the path-safety
    # rules (_resolve_artist_file) and the definition of what an export or a
    # snapshot IS; a second copy in this file would be a second thing to get
    # wrong. Nothing here writes a file — the one mutating route (restore)
    # calls a function the control panel already uses.

    @admin.bp.route(f'{prefix}/site', endpoint=f'{slug}_landing_site')
    @admin.auth_required
    def site():
        return jsonify(_site_payload(slug, cfg_now(slug)))

    @admin.bp.route(f'{prefix}/files', endpoint=f'{slug}_landing_files')
    @admin.auth_required
    def files():
        from admin_api import artist_files_payload
        return jsonify(artist_files_payload(slug, include_assets=True))

    @admin.bp.route(f'{prefix}/file', endpoint=f'{slug}_landing_file')
    @admin.auth_required
    def file_read():
        from admin_api import read_artist_file_payload
        payload, code = read_artist_file_payload(
            slug, request.args.get('path', ''), include_assets=True)
        return jsonify(payload), code

    @admin.bp.route(f'{prefix}/file-raw', endpoint=f'{slug}_landing_file_raw')
    @admin.auth_required
    def file_raw():
        """Bytes — images inline, anything with ?download=1 as an attachment."""
        from admin_api import _resolve_artist_file
        _, target = _resolve_artist_file(
            slug, request.args.get('path', ''), include_assets=True)
        if target is None or not target.is_file():
            return jsonify({'error': 'Not found'}), 404
        return send_file(str(target), max_age=0,
                         as_attachment=request.args.get('download') == '1',
                         download_name=target.name)

    @admin.bp.route(f'{prefix}/export-info', endpoint=f'{slug}_landing_export_info')
    @admin.auth_required
    def export_info():
        return jsonify(_export_info(slug))

    @admin.bp.route(f'{prefix}/export', endpoint=f'{slug}_landing_export')
    @admin.auth_required
    def export():
        from admin_api import export_site_zip
        buf, filename = export_site_zip(slug)
        if buf is None:
            return jsonify({'error': 'Nothing has been published yet, so there '
                                     'is nothing to export.'}), 404
        return send_file(buf, mimetype='application/zip',
                         as_attachment=True, download_name=filename)

    @admin.bp.route(f'{prefix}/history', endpoint=f'{slug}_landing_history')
    @admin.auth_required
    def history():
        from admin_api import snapshots_payload
        return jsonify(snapshots_payload(slug))

    @admin.bp.route(f'{prefix}/history/restore', methods=['POST'],
                    endpoint=f'{slug}_landing_history_restore')
    @admin.auth_required
    def history_restore():
        """Restore, then rebuild here rather than telling the artist to go and
        press Save somewhere else. Restoring and not republishing leaves the
        source and the live site disagreeing, which is the one state nobody on
        this page could diagnose."""
        from admin_api import restore_snapshot_for
        data = request.get_json(silent=True) or {}
        payload, code = restore_snapshot_for(slug, data.get('filename', ''))
        if code != 200:
            return jsonify(payload), code
        ok, err = admin.rebuild()
        if not ok:
            return jsonify({
                'ok': False,
                'restored': True,
                'error': f'Restored your files, but rebuilding the site failed: {err}',
            }), 500
        return jsonify({'ok': True, 'restored': True,
                        'message': 'Restored and republished.'})

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

    @admin.bp.route(f'{prefix}/enter', endpoint=f'{slug}_landing_enter')
    def enter():
        """Cross-origin bridge from the intake portal. Consume a one-time nonce
        minted on adze.studio and set a first-party {slug}_admin cookie on THIS
        domain, then bounce to the clean panel URL with the nonce stripped. A
        spent or expired nonce just lands on the panel's own login — no error."""
        from flask import redirect
        admin.domain_guard()
        cookie_value = None
        try:
            import accounts
            acct_id = accounts.consume_handoff(request.args.get('h', ''), slug)
            if acct_id is not None:
                cookie_value = accounts.create_session(
                    acct_id, slug,
                    ip=request.headers.get('X-Real-IP') or request.remote_addr,
                    ua=request.headers.get('User-Agent'))
        except Exception:
            pass
        resp = redirect(admin.panel_url, code=302)
        # The nonce rode in the URL; keep it out of any Referer the panel's
        # third-party assets (fonts) would otherwise leak it through.
        resp.headers['Referrer-Policy'] = 'no-referrer'
        if cookie_value:
            resp.set_cookie(admin.cookie, cookie_value, httponly=True,
                            samesite='Strict',
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
{token_links}
<link rel="stylesheet" href="{prefix}/asset/admin-shell.css">
</head>
<body>
<div id="adze-admin-root"></div>
<script>window.ADZE_LANDING = {boot};</script>
<script src="{prefix}/asset/vendor/highlight.js"></script>
<script src="{prefix}/asset/vendor/qrcode.js"></script>
<script src="{prefix}/asset/adze-ui.js"></script>
<script src="{prefix}/asset/file-viewer.js"></script>
<script src="{prefix}/asset/admin-landing.js"></script>
</body>
</html>
"""
