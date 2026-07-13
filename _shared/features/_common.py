"""_common — small shared helpers for the content-driven admin layer.

Slug/path primitives that every custom admin needs, kept in one place so they
can't drift between modules. Deliberately pure (no Flask, no admin_api import),
so content_admin.py and any future feature can build on them without dragging in
the 7k-line admin_api. Auth lives in auth.py; assets in asset_store.py.
"""
import re
from pathlib import Path

# Same shape admin_api enforces (a leading alnum, then alnum/hyphen).
SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def valid_slug(slug):
    return bool(slug) and bool(SLUG_RE.match(slug))


def slugify(text):
    """Lowercase, collapse non-alphanumerics to single hyphens, trim. Always
    returns a valid slug ('item' for empty/garbage input)."""
    s = re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')
    return s or 'item'


def unique_slug(base, existing):
    """`base`, or `base-2`, `base-3`, … until it isn't in `existing`."""
    existing = set(existing or [])
    slug = base
    n = 2
    while slug in existing:
        slug = f'{base}-{n}'
        n += 1
    return slug


def artist_dir(slug):
    return Path('artists') / slug


def get_artist_path(slug):
    """The artist dir, or None if the slug is invalid (traversal guard)."""
    if not valid_slug(slug):
        return None
    return artist_dir(slug)
