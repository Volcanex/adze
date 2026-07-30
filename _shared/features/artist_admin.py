"""
artist_admin — shared framework for per-artist /admin dashboards.

A custom dashboard is a feature module that gives one artist a bespoke admin
SPA at /admin on their own domain. Before this framework, each one
(alfie_admin, rose_admin, …) hand-rolled the *same* auth, the *same* core
routes, and the *same* compile trigger — copy-pasted and free to drift. This
module owns those shared parts so a new dashboard only supplies what is
genuinely bespoke: its data model, its render function, and its HTML.

What the framework owns (must never drift between dashboards):
  - Auth — domain guard + token, both read from the artist's config.json.
  - Core routes — panel, login, logout.
  - The rebuild transaction — render() -> compile.py --artist -> mark the
    generated pages. One guaranteed code path, so the data source of truth
    and the compiled site can't fall out of sync.

What a dashboard supplies:
  - slug, cookie name, panel_url
  - panel_html — the SPA
  - render (optional) — a callable that rewrites the artist's data-driven
    content.md pages from the dashboard's source-of-truth data file, and
    returns the list of generated page paths (rel to the artist dir, posix)
    so /edit-page knows not to let a human edit a generated file.

See _shared/features/CLAUDE.md → "Custom artist admins" for the author guide.
"""

import sys
import json
import subprocess
from pathlib import Path
from functools import wraps
from flask import Blueprint, request, jsonify, make_response, abort


# Marker file written into each dashboard-managed artist dir, listing the
# pages the dashboard generates. Read by admin_api.edit_page() to refuse direct
# edits to derived files (which the next rebuild would silently overwrite).
GENERATED_MANIFEST = '.generated.json'


def _strip_scheme(domain):
    d = (domain or '').strip()
    for p in ('https://', 'http://', 'www.'):
        if d.startswith(p):
            d = d[len(p):]
    return d.rstrip('/')


def generated_pages(artist_slug):
    """The page slugs a dashboard generates for this artist (or [] if none).
    A page slug is the page dir path relative to the artist dir, posix-style,
    e.g. 'works/cormorant'."""
    mf = Path('artists') / artist_slug / GENERATED_MANIFEST
    try:
        data = json.loads(mf.read_text(encoding='utf-8'))
        return data.get('pages', []) if isinstance(data, dict) else []
    except (OSError, json.JSONDecodeError):
        return []


class ArtistAdmin:
    """Plumbing for one artist's custom dashboard. Construct it, register the
    core routes with the panel HTML, hang bespoke routes off `.bp` guarded by
    `.auth_required`, and call `.rebuild()` to republish."""

    def __init__(self, slug, cookie, panel_url, render=None, blueprint_name=None):
        self.slug = slug
        self.cookie = cookie
        self.panel_url = panel_url
        # Route prefix is whatever sits above /panel, so login/logout/compile
        # share it — covers the case where the admin name != the artist slug
        # (alfie's slug is 'alfiebruce' but its prefix is '/api/alfie-admin').
        self.prefix = panel_url.rsplit('/', 1)[0]
        self.render = render
        self.artist_dir = Path('artists') / slug
        self.bp = Blueprint(blueprint_name or f'{slug}_admin', __name__)

    # ── config-derived identity ──────────────────────────────────────────────
    def _config(self):
        try:
            return json.loads((self.artist_dir / 'config.json').read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return {}

    def token(self):
        return self._config().get('admin_token', '')

    def set_token(self, new_token):
        """Persist a new admin_token to config.json, preserving everything else.
        Returns True on success. Used by the self-service password change."""
        cfg_path = self.artist_dir / 'config.json'
        cfg = self._config()
        if not cfg:
            return False
        cfg['admin_token'] = new_token
        try:
            cfg_path.write_text(
                json.dumps(cfg, indent=4, ensure_ascii=False), encoding='utf-8')
            return True
        except OSError:
            return False

    def domain(self):
        return _strip_scheme(self._config().get('domain'))

    # ── auth ─────────────────────────────────────────────────────────────────
    def domain_guard(self):
        host = request.headers.get('Host', '').split(':')[0]
        if host.startswith('www.'):
            host = host[4:]
        if host != self.domain():
            abort(404)

    def auth_required(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.domain_guard()
            token = request.cookies.get(self.cookie, '')
            if not token:
                abort(401)
            # The legacy compare stays first and stays permanently: for the
            # artists whose only door is their own /admin, it is the thing that
            # guarantees this change can never lock them out.
            if token == self.token():
                return f(*args, **kwargs)
            if token.startswith('as1_'):
                try:
                    import accounts
                    if accounts.session_grants(token, self.slug):
                        return f(*args, **kwargs)
                except ImportError:
                    pass
            abort(401)
        return wrapper

    # ── the rebuild transaction ──────────────────────────────────────────────
    def _write_manifest(self, pages):
        try:
            (self.artist_dir / GENERATED_MANIFEST).write_text(
                json.dumps({'pages': sorted(pages)}, indent=2), encoding='utf-8')
        except OSError:
            pass

    def rebuild(self, timeout=120):
        """Source of truth -> live site, atomically. Runs render() (if any),
        records the generated pages, then compiles the artist. Returns
        (ok: bool, error: str|None) so the caller can surface failures."""
        if self.render is not None:
            try:
                generated = self.render()
            except Exception as e:
                return False, f'page generation failed: {e}'
            if isinstance(generated, (list, tuple, set)):
                self._write_manifest(list(generated))

        compile_script = Path.cwd() / 'compile.py'
        if not compile_script.exists():
            return False, 'compile.py not found'
        result = subprocess.run(
            [sys.executable, str(compile_script), '--artist', self.slug],
            capture_output=True, text=True, timeout=timeout, cwd=Path.cwd(),
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout or 'compile failed')[-500:]
        return True, None

    # ── core routes ──────────────────────────────────────────────────────────
    def register_core(self, panel_html):
        """Wire panel, login, logout, and a /compile route that runs rebuild().
        Call once; hang the dashboard's bespoke routes off `.bp` separately."""
        admin = self

        @admin.bp.route(admin.panel_url)
        @admin.bp.route(admin.panel_url + '/')
        def admin_page():
            admin.domain_guard()
            return make_response(panel_html, 200, {'Content-Type': 'text/html; charset=utf-8'})

        @admin.bp.route(f'{admin.prefix}/login', methods=['POST'])
        def login():
            admin.domain_guard()
            # This route had no rate limit at all while comparing against the
            # artist's live API key.
            try:
                from admin_api import _rate_limit
                _rate_limit(f'artistlogin:{admin.slug}', 10, 60)
            except ImportError:
                pass
            data = request.get_json(silent=True) or {}

            def _ok(cookie_value):
                resp = jsonify({'ok': True})
                resp.set_cookie(admin.cookie, cookie_value, httponly=True,
                                samesite='Strict', max_age=60 * 60 * 24 * 30)
                return resp

            # Password-only: the domain already says which artist this is, so
            # the identifier is optional here. Try the account first so the
            # cookie becomes an opaque session, then fall back to the raw token.
            password = (data.get('password') or data.get('token') or '').strip()
            identifier = (data.get('identifier') or '').strip()
            if password:
                try:
                    import accounts
                    acct = (accounts.resolve(identifier) if identifier
                            else accounts.account_for_slug(admin.slug))
                    if acct and accounts.verify_password(acct, password) \
                            and (acct['is_owner'] or admin.slug in accounts.sites_for(acct['id'])):
                        sid = accounts.create_session(
                            acct['id'], admin.slug,
                            ip=request.headers.get('X-Real-IP') or request.remote_addr,
                            ua=request.headers.get('User-Agent'))
                        accounts.record_login(
                            acct['id'], request.headers.get('X-Real-IP') or request.remote_addr)
                        return _ok(sid)
                except ImportError:
                    pass

            if password and password == admin.token():
                return _ok(admin.token())
            return jsonify({'ok': False, 'error': 'Invalid token'}), 401

        @admin.bp.route(f'{admin.prefix}/logout', methods=['POST'])
        def logout():
            admin.domain_guard()
            resp = jsonify({'ok': True})
            resp.delete_cookie(admin.cookie)
            return resp

        @admin.bp.route(f'{admin.prefix}/password', methods=['POST'])
        @admin.auth_required
        def change_password():
            # Repeatable, self-service. Unlike the one-time handover change, this
            # never sets `password_changed` — the artist can rotate it any time.
            data = request.get_json(silent=True) or {}
            current = (data.get('current') or '').strip()
            new = (data.get('new') or '').strip()
            acct = None
            try:
                import accounts
                acct = accounts.account_for_slug(admin.slug)
            except ImportError:
                accounts = None

            current_ok = (current == admin.token())
            if not current_ok and acct is not None:
                current_ok = accounts.verify_password(acct, current)
            if not current_ok:
                return jsonify({'error': 'Current password is incorrect.'}), 400
            if len(new) < 6:
                return jsonify({'error': 'New password must be at least 6 characters.'}), 400

            # DUAL-WRITE, and it is not optional. admin_token is still the
            # editor's API key (~35 X-Admin-Token call sites in admin.html), so
            # writing only the hash would silently desync the artist's password
            # from their API key and break the editor for them alone. This is
            # the tax of keeping the editor out of scope; it goes away when the
            # editor moves to a separate api_key.
            if not admin.set_token(new):
                return jsonify({'error': 'Could not save the new password.'}), 500
            cookie_value = new
            if acct is not None:
                try:
                    accounts.set_password(acct['id'], new)
                    sid = accounts.create_session(
                        acct['id'], admin.slug,
                        ip=request.headers.get('X-Real-IP') or request.remote_addr,
                        ua=request.headers.get('User-Agent'))
                    accounts.revoke_all_for_account(acct['id'], except_sid=sid)
                    cookie_value = sid
                except Exception:
                    pass          # config.json is written; don't fail the change

            resp = jsonify({'ok': True})
            resp.set_cookie(admin.cookie, cookie_value, httponly=True,
                            samesite='Strict', max_age=60 * 60 * 24 * 30)
            return resp

        @admin.bp.route(f'{admin.prefix}/compile', methods=['POST'])
        @admin.auth_required
        def compile_site():
            ok, error = admin.rebuild()
            if ok:
                return jsonify({'ok': True})
            return jsonify({'error': error}), 500
