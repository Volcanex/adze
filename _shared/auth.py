"""
Authentication utilities for artist admin dashboards.
Each artist has a token stored in their config.json.
"""

import os
from pathlib import Path
from flask import request, abort
import json

# Admin token from environment — no hardcoded fallback
DEFAULT_ADMIN_TOKEN = os.environ.get('DEV_ADMIN_TOKEN', '')

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
    if DEFAULT_ADMIN_TOKEN and token == DEFAULT_ADMIN_TOKEN:
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

    # Cookie fallback (persistent browser sessions)
    session_cookie = request.cookies.get('adze_session', '')
    if session_cookie and ':' in session_cookie:
        slug, _, tok = session_cookie.partition(':')
        if slug and verify_artist_token(slug, tok):
            return slug

    return None
