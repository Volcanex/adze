"""
Authentication utilities for artist admin dashboards.
Each artist has a token stored in their config.json.
"""

import os
from pathlib import Path
from flask import request, abort
import json

# ── Admin identities & workspaces ─────────────────────────────────────────────
# An admin identity has a username, a password, a display name, and a list of
# workspaces it can see. "Workspace" tags artists/leads (default 'lastplace').
# Gabriel is hard-coded as the super-master: access to every workspace and the
# only identity allowed to re-scope artists between workspaces.

ALL_WORKSPACES = ['personal', 'lastplace']
DEFAULT_WORKSPACE = 'lastplace'

# Hard-coded super identity. Password sourced from env so it isn't in the repo.
_GABRIEL_PASSWORD = os.environ.get('GABRIEL_PASSWORD', '') or os.environ.get('DEV_ADMIN_TOKEN', '')

# username -> {password, name, workspaces, super}
ADMIN_IDENTITIES = {}
if _GABRIEL_PASSWORD:
    ADMIN_IDENTITIES['gabriel'] = {
        'username': 'gabriel',
        'password': _GABRIEL_PASSWORD,
        'name': 'Gabriel',
        'workspaces': list(ALL_WORKSPACES),
        'super': True,
    }

# Additional identities loaded from ADMIN_IDENTITIES_JSON:
# [{"username":"clive","password":"...","name":"Clive","workspaces":["lastplace"]}]
_identities_json = os.environ.get('ADMIN_IDENTITIES_JSON', '').strip()
if _identities_json:
    try:
        for entry in json.loads(_identities_json):
            uname = (entry.get('username') or '').strip().lower()
            pw = entry.get('password') or ''
            if not uname or not pw or uname == 'gabriel':
                continue
            ADMIN_IDENTITIES[uname] = {
                'username': uname,
                'password': pw,
                'name': entry.get('name') or uname.title(),
                'workspaces': entry.get('workspaces') or [DEFAULT_WORKSPACE],
                'super': bool(entry.get('super')),
            }
    except (json.JSONDecodeError, TypeError):
        pass

# Legacy back-compat: DEV_ADMIN_TOKENS_EXTRA still accepted as raw passwords
# that map to a generic "lastplace-only" identity (so existing Clive token
# keeps working until ADMIN_IDENTITIES_JSON is wired up in .env).
_EXTRA_ADMIN_TOKENS = {t.strip() for t in os.environ.get('DEV_ADMIN_TOKENS_EXTRA', '').split(',') if t.strip()}
for _idx, _tok in enumerate(sorted(_EXTRA_ADMIN_TOKENS)):
    if any(i['password'] == _tok for i in ADMIN_IDENTITIES.values()):
        continue
    _uname = f'legacy{_idx}'
    ADMIN_IDENTITIES[_uname] = {
        'username': _uname,
        'password': _tok,
        'name': 'Designer',
        'workspaces': [DEFAULT_WORKSPACE],
        'super': False,
    }

# Legacy flat token set — used by is_admin_token() so existing call sites
# (cookies, headers) keep working without knowing about identities.
DEFAULT_ADMIN_TOKEN = _GABRIEL_PASSWORD
ADMIN_TOKENS = {i['password'] for i in ADMIN_IDENTITIES.values()}
# Back-compat: keep the legacy DEV_ADMIN_TOKEN valid so existing admin
# session cookies / saved master passwords keep working after the identity
# refactor (resolves to the gabriel super-identity via get_identity_by_token).
_legacy_admin = os.environ.get('DEV_ADMIN_TOKEN', '').strip()
if _legacy_admin:
    ADMIN_TOKENS.add(_legacy_admin)
    if 'gabriel' in ADMIN_IDENTITIES:
        ADMIN_IDENTITIES.setdefault('gabriel-legacy', {
            'username': 'gabriel',
            'password': _legacy_admin,
            'name': 'Gabriel',
            'workspaces': list(ALL_WORKSPACES),
            'super': True,
        })

def is_admin_token(token):
    """True if `token` matches any admin identity's password."""
    return bool(token) and token in ADMIN_TOKENS

def verify_admin_credentials(username, password):
    """Return identity dict for valid (username, password), else None.
    Username match is case-insensitive."""
    if not username or not password:
        return None
    ident = ADMIN_IDENTITIES.get(username.strip().lower())
    if ident and ident['password'] == password:
        return ident
    return None

def get_identity_by_token(token):
    """Return identity dict whose password matches `token`, else None.
    Used to resolve the adze_admin_session cookie back to an identity."""
    if not token:
        return None
    for ident in ADMIN_IDENTITIES.values():
        if ident['password'] == token:
            return ident
    return None

def current_admin_identity():
    """Resolve the current request's admin identity from cookie/header.
    Returns identity dict or None."""
    token = request.headers.get('X-Admin-Token', '')
    ident = get_identity_by_token(token)
    if ident:
        return ident
    cookie = request.cookies.get('adze_admin_session', '')
    ident = get_identity_by_token(cookie)
    if ident:
        return ident
    artist_cookie = request.cookies.get('adze_session', '')
    if artist_cookie and ':' in artist_cookie:
        _, _, tok = artist_cookie.partition(':')
        ident = get_identity_by_token(tok)
        if ident:
            return ident
    return None

def get_artist_config(artist_slug):
    """
    Load artist's config.json to get their auth token and settings.

    Args:
        artist_slug: The artist's slug (e.g., 'artist-one')

    Returns:
        dict: Artist config or None if not found
    """
    config_path = Path(f'artists/{artist_slug}/config.json')

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def get_all_artists():
    """
    Get list of all artist slugs and their domains.

    Returns:
        dict: {artist_slug: domain} mapping
    """
    artists_dir = Path('pages/artists')
    artist_map = {}

    if not artists_dir.exists():
        return artist_map

    for item in artists_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            config = get_artist_config(item.name)
            if config and 'domain' in config:
                artist_map[item.name] = config['domain']

    return artist_map

def get_artist_by_domain(domain):
    """
    Find artist slug by their domain.

    Args:
        domain: The domain to lookup (e.g., 'artist1.com')

    Returns:
        str: Artist slug or None
    """
    artists = get_all_artists()
    for slug, artist_domain in artists.items():
        if artist_domain == domain:
            return slug
    return None

def verify_artist_token(artist_slug, token):
    """
    Verify if the provided token matches the artist's token.

    Args:
        artist_slug: The artist's slug
        token: Token to verify

    Returns:
        bool: True if token is valid
    """
    config = get_artist_config(artist_slug)

    if not config:
        return False

    # Check artist's specific token first
    if 'admin_token' in config and config['admin_token'] == token:
        return True

    # Fallback to default admin token (for super admin)
    if is_admin_token(token):
        return True

    return False

def require_artist_auth(artist_slug):
    """
    Decorator/helper to require authentication for an artist.
    Call this at the start of endpoints that need auth.

    Args:
        artist_slug: The artist slug to verify against

    Raises:
        401 if auth fails
    """
    token = request.headers.get('X-Admin-Token', '')
    if verify_artist_token(artist_slug, token):
        return

    # Cookie fallback
    session_cookie = request.cookies.get('adze_session', '')
    if session_cookie and ':' in session_cookie:
        slug, _, tok = session_cookie.partition(':')
        if slug == artist_slug and verify_artist_token(slug, tok):
            return

    abort(401, description='Invalid or missing admin token')

def get_authenticated_artist():
    """
    Get the authenticated artist slug from the request.
    Checks X-Artist-Slug/X-Admin-Token headers first, then falls back to
    the adze_session cookie set by POST /api/adze/login.

    Returns:
        str: Artist slug if authenticated, None otherwise
    """
    # Headers take priority (programmatic/API access, in-memory session)
    artist_slug = request.headers.get('X-Artist-Slug', '')
    token = request.headers.get('X-Admin-Token', '')
    if artist_slug and verify_artist_token(artist_slug, token):
        return artist_slug

    # Super-admin browser session: allow the dashboard to choose an artist
    # with X-Artist-Slug while authenticating via the httpOnly admin cookie.
    admin_cookie = request.cookies.get('adze_admin_session', '')
    if artist_slug and is_admin_token(admin_cookie):
        if get_artist_config(artist_slug):
            return artist_slug
    session_cookie = request.cookies.get('adze_session', '')
    if artist_slug and ':' in session_cookie:
        _, _, session_token = session_cookie.partition(':')
        if is_admin_token(session_token) and get_artist_config(artist_slug):
            return artist_slug

    # Cookie fallback (persistent browser sessions)
    if session_cookie and ':' in session_cookie:
        slug, _, tok = session_cookie.partition(':')
        if slug and verify_artist_token(slug, tok):
            return slug

    return None
