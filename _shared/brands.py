"""Brand pack resolution. A workspace may have a pack under
_shared/brands/<workspace>/ (brand.json + brand.css + assets/). No pack means
default Adze branding. Pure helpers, no Flask dependencies."""
import json
from pathlib import Path

BRANDS_DIR = Path(__file__).parent / 'brands'


def get_brand(workspace):
    """Load brand.json for a workspace. Returns dict or None if no pack."""
    if not workspace:
        return None
    path = BRANDS_DIR / workspace / 'brand.json'
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def brand_json(workspace):
    """Like get_brand but always returns a dict (empty = Adze defaults)."""
    return get_brand(workspace) or {}


def brand_asset_path(workspace, filename):
    """Resolve a brand asset (assets/<filename>, or brand.css at the pack
    root) to an absolute path. Returns None on miss or path traversal."""
    if not workspace or not filename:
        return None
    pack = (BRANDS_DIR / workspace).resolve()
    if not str(pack).startswith(str(BRANDS_DIR.resolve())) or not pack.is_dir():
        return None
    if filename == 'brand.css':
        target = pack / 'brand.css'
    else:
        target = (pack / 'assets' / filename).resolve()
        if not str(target).startswith(str(pack / 'assets')):
            return None
    return target if target.is_file() else None
