"""
Shared admin API endpoints for all artist sites.
These endpoints handle common functionality like file uploads, page editing, etc.
"""

import os
import re
import json
import shutil
import socket
import subprocess
import time as _time
import threading as _threading
import logging
import mimetypes
from pathlib import Path
from flask import Blueprint, jsonify, request, abort, send_file, Response, stream_with_context, make_response
from werkzeug.utils import secure_filename
from brands import brand_json, brand_asset_path, brand_link_base
import sys


# ── Logging ──────────────────────────────────────────────────────────────────────

_LOGS_DIR = Path(__file__).parent.parent / 'logs'
_LOGS_DIR.mkdir(exist_ok=True)

def _setup_logger(name, filename, fmt='%(asctime)s %(message)s', max_bytes=10*1024*1024, backup_count=5):
    """Create a logger with rotating file handler (10MB per file, 5 backups = 60MB max)."""
    from logging.handlers import RotatingFileHandler
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(
            _LOGS_DIR / filename, maxBytes=max_bytes,
            backupCount=backup_count, encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

_api_log = _setup_logger('adze.api', 'api.log')
_vibe_log = _setup_logger('adze.vibe', 'vibe.log')


# ── Simple in-memory rate limiter ─────────────────────────────────────────────
class _RateLimiter:
    """Per-IP sliding window rate limiter. No external dependencies."""
    def __init__(self):
        self._buckets = {}       # key -> list of timestamps
        self._lock = _threading.Lock()

    def check(self, key, max_requests, window_seconds):
        """Return True if request is allowed, False if rate-limited."""
        now = _time.time()
        cutoff = now - window_seconds
        with self._lock:
            hits = self._buckets.get(key, [])
            hits = [t for t in hits if t > cutoff]
            if len(hits) >= max_requests:
                self._buckets[key] = hits
                return False
            hits.append(now)
            self._buckets[key] = hits
            return True

_limiter = _RateLimiter()


def _rate_limit(scope, max_requests, window_seconds):
    """Check rate limit for current request IP + scope. Aborts 429 if exceeded."""
    ip = request.headers.get('X-Real-IP') or request.remote_addr or 'unknown'
    key = f'{scope}:{ip}'
    if not _limiter.check(key, max_requests, window_seconds):
        abort(429, description='Too many requests. Please try again later.')

# Add parent directory to path to import auth
sys.path.insert(0, str(Path(__file__).parent))
from auth import require_artist_auth, get_authenticated_artist, get_all_artists
import asset_meta
import asset_store
from db import insert_pageview, query_analytics, upsert_session, query_sessions, migrate_json_to_sqlite

bp = Blueprint('artist_admin', __name__, url_prefix='/api/adze')


# Fish images for the admin pipeline grid. Sourced from artists/sandbox/assets/images/
# (Gabriel's own uploads). Public — no auth — they're just decorative PNGs.
@bp.route('/admin-fish/<name>')
def _admin_fish(name):
    safe = secure_filename(name)
    if not safe or not safe.lower().endswith('.png'):
        abort(404)
    p = Path('artists/sandbox/assets/images') / safe
    if not p.exists():
        abort(404)
    return send_file(str(p), mimetype='image/png', max_age=3600)


@bp.after_request
def _log_api_request(response):
    """Log every API request to api.log."""
    try:
        artist = request.headers.get('X-Artist-Slug', '')
        if not artist:
            cookie = request.cookies.get('adze_session', '')
            if cookie and ':' in cookie:
                artist = cookie.partition(':')[0]
        method = request.method
        path = request.path
        status = response.status_code
        # Skip noisy polling endpoints
        if path.endswith(('/list-snapshots', '/whoami')) and status == 200:
            return response
        _api_log.info(f'[{artist or "-"}] {method} {path} → {status}')
    except Exception:
        pass
    return response


def _require_super_admin():
    """Abort 401 unless the request carries a valid super-admin token (cookie or header)."""
    from auth import is_admin_token
    token = request.headers.get('X-Admin-Token', '')
    if is_admin_token(token):
        return
    cookie = request.cookies.get('adze_admin_session', '')
    if is_admin_token(cookie):
        return
    artist_cookie = request.cookies.get('adze_session', '')
    if artist_cookie and ':' in artist_cookie:
        _, _, artist_token = artist_cookie.partition(':')
        if is_admin_token(artist_token):
            return
    abort(401, description='Super-admin auth required')


def _current_workspaces():
    """List of workspaces the current admin can see. Falls back to [lastplace]
    if no identity resolved (shouldn't happen post-auth, but safe)."""
    from auth import current_admin_identity, DEFAULT_WORKSPACE
    ident = current_admin_identity()
    if ident:
        return ident['workspaces']
    return [DEFAULT_WORKSPACE]


def _is_super():
    """True if the current admin identity has the super flag."""
    from auth import current_admin_identity
    ident = current_admin_identity()
    return bool(ident and ident.get('super'))


def _artist_workspace(cfg):
    """Resolve an artist config's workspace tag. Defaults to lastplace."""
    from auth import DEFAULT_WORKSPACE
    return (cfg.get('workspace') or DEFAULT_WORKSPACE).strip().lower()


# ── Storage cache (avoid hammering du for every request) ──────────────────────
_storage_cache = {}  # {slug: (timestamp, size_str)}
_STORAGE_CACHE_TTL = 60  # seconds


def _get_artist_storage(slug):
    """Get storage size in bytes for an artist, cached for 60s."""
    now = _time.time()
    cached = _storage_cache.get(slug)
    if cached and (now - cached[0]) < _STORAGE_CACHE_TTL:
        return cached[1]
    try:
        result = subprocess.run(
            ['du', '-sb', f'artists/{slug}/'],
            capture_output=True, timeout=5, text=True
        )
        size_bytes = int(result.stdout.split('\t')[0]) if result.returncode == 0 else 0
    except Exception:
        size_bytes = 0
    _storage_cache[slug] = (now, size_bytes)
    return size_bytes


ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

# Only block files that could be dangerous on a server
BLOCKED_EXTENSIONS = {'exe', 'bat', 'cmd', 'sh', 'php', 'py', 'rb', 'pl', 'cgi', 'jsp', 'asp', 'aspx', 'htaccess'}

_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def _valid_slug(slug):
    """Return True if slug is a safe directory name (lowercase alphanum + hyphens)."""
    return bool(slug) and bool(_SLUG_RE.match(slug))


def allowed_file(filename, allowed_extensions=None):
    """Check file is not a blocked type. All other extensions are allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext not in BLOCKED_EXTENSIONS


def get_artist_path(artist_slug):
    """Get the path to an artist's directory. Validates slug format."""
    if not _valid_slug(artist_slug):
        abort(400, description='Invalid artist slug')
    return Path(f'artists/{artist_slug}')


def get_page_path(artist_slug, page_slug):
    """Get the path to a specific page within an artist's directory. Validates both slugs."""
    if not _valid_slug(page_slug):
        abort(400, description='Invalid page slug')
    return get_artist_path(artist_slug) / page_slug


def scan_for_leaked_secrets(artist_slug, content):
    """Scan content for leaked .env secret values. Returns list of leaked key names."""
    env_path = get_artist_path(artist_slug) / '.env'
    if not env_path.exists():
        return []

    leaked = []
    try:
        env_text = env_path.read_text()
        for line in env_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Only check values that are long enough to be meaningful (avoid false positives)
            if len(value) >= 8 and value in content:
                leaked.append(key)
    except IOError:
        pass
    return leaked


def _scaffold_new_artist(slug):
    """If an artist directory has no pages yet, copy starter pages from _template."""
    artist_dir = Path(f'artists/{slug}')
    template_dir = Path('artists/_template')
    if not artist_dir.exists() or not template_dir.exists():
        return
    # Check if artist already has at least one page (dir with content.md)
    has_pages = any(
        (d / 'content.md').exists()
        for d in artist_dir.iterdir()
        if d.is_dir() and d.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups')
    )
    if has_pages:
        return
    # Load artist config for name substitution
    config = {}
    cfg_file = artist_dir / 'config.json'
    if cfg_file.exists():
        try:
            config = json.loads(cfg_file.read_text())
        except Exception:
            pass
    display_name = config.get('display_name') or config.get('name') or slug.title()
    # Copy each template directory, replacing placeholders
    for item in template_dir.iterdir():
        if not item.is_dir() or item.name in ('assets', 'widgets'):
            continue
        dest = artist_dir / item.name
        if dest.exists():
            continue
        shutil.copytree(item, dest)
        # Replace placeholders in copied files
        for f in dest.rglob('*'):
            if f.is_file() and f.suffix in ('.json', '.md', '.html'):
                text = f.read_text(encoding='utf-8')
                text = text.replace('{{ARTIST_NAME}}', display_name)
                text = text.replace('{{SLUG}}', slug)
                text = text.replace('{{DOMAIN}}', config.get('domain', ''))
                text = text.replace('{{TOKEN}}', '')
                f.write_text(text, encoding='utf-8')
    # Copy template assets if artist has none
    template_assets = template_dir / 'assets'
    artist_assets = artist_dir / 'assets'
    if template_assets.exists() and not artist_assets.exists():
        shutil.copytree(template_assets, artist_assets)
    # Copy default-styles.css if template has one and artist doesn't
    template_styles = template_dir / 'default-styles.css'
    artist_styles = artist_dir / 'default-styles.css'
    if template_styles.exists() and not artist_styles.exists():
        shutil.copy2(template_styles, artist_styles)


# ── Analytics ─────────────────────────────────────────────────────────────

@bp.route('/analytics')
def analytics():
    """Return aggregated analytics for the authenticated artist."""
    from datetime import datetime, timedelta
    import time

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    # Migrate legacy JSON files on first access (no-op if already done)
    migrate_json_to_sqlite(artist_slug)

    now = int(time.time())
    today_start      = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    week_start       = int((datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    month_start      = int((datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    prev_month_start = int((datetime.now() - timedelta(days=60)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    pv = query_analytics(artist_slug, month_start, prev_month_start, today_start, week_start)
    sess = query_sessions(artist_slug, month_start)

    month_count      = pv['month_count']
    prev_month_count = pv['prev_month_count']

    if prev_month_count == 0:
        trend = 'up' if month_count > 0 else 'flat'
    elif month_count > prev_month_count:
        trend = 'up'
    elif month_count < prev_month_count:
        trend = 'down'
    else:
        trend = 'flat'

    return jsonify({
        'today':          pv['today_count'],
        'week':           pv['week_count'],
        'month':          month_count,
        'trend':          trend,
        'top_pages':      pv['top_pages'],
        'sources':        pv['sources'],
        'countries':      pv['countries'],
        'daily':          pv['daily'],
        'bounce_rate':    sess['bounce_rate'],
        'avg_duration':   sess['avg_duration'],
        'total_sessions': sess['total_sessions'],
        'hourly':         pv['hourly_counts'],
    })


@bp.route('/beacon', methods=['POST'])
def beacon():
    """Receive session duration beacons from the tracking script (no auth required)."""
    import time

    try:
        data = request.get_data(as_text=True)
        params = {}
        for pair in data.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v

        sid = params.get('sid', '')
        slug = params.get('slug', '')
        dur = int(params.get('dur', '0'))
        pc = int(params.get('pc', '1'))

        if not sid or not slug or dur < 1:
            return '', 204

        # Validate slug format
        if not _valid_slug(slug):
            return '', 204

        artist_path = Path(f'artists/{slug}')
        if not artist_path.exists():
            return '', 204

        upsert_session(slug, sid, dur, pc, int(time.time()))

    except Exception:
        pass

    return '', 204


# ── Dashboard ──────────────────────────────────────────────────────────────

def _hosted_site_count():
    """Count real artist sites (same filter the dashboard uses): a directory
    under artists/ with a config.json, excluding _-prefixed dirs, the example,
    and lead-only stubs."""
    count = 0
    artists_dir = Path('artists')
    if not artists_dir.exists():
        return 0
    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_') or item.name == 'example-artist':
            continue
        cfg_path = item / 'config.json'
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            continue
        if cfg.get('is_stub'):
            continue
        count += 1
    return count


@bp.route('/home')
def serve_home():
    """Serve the Adze landing page."""
    home_path = Path(__file__).parent / 'home.html'
    if not home_path.exists():
        return 'Home not found', 404
    html = home_path.read_text(encoding='utf-8')
    html = html.replace('__SITE_COUNT__', str(_hosted_site_count()))
    return html, 200, {
        'Content-Type': 'text/html',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
    }


@bp.route('/dashboard')
def dashboard():
    """Serve the admin dashboard HTML, injecting server-side secrets."""
    dashboard_path = Path(__file__).parent / 'dashboard.html'

    if not dashboard_path.exists():
        return jsonify({'error': 'Dashboard template not found'}), 404

    html = dashboard_path.read_text(encoding='utf-8')

    response = Response(html, mimetype='text/html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@bp.route('/verify-admin', methods=['POST'])
def verify_admin():
    """Verify the super-admin token (for portal auth). No session created."""
    _rate_limit('login', 10, 60)
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    from auth import is_admin_token
    if not is_admin_token(token):
        return jsonify({'error': 'Invalid token'}), 401
    return jsonify({'ok': True})


@bp.route('/create-artist', methods=['POST'])
def create_artist():
    """
    Create a new artist site. Super-admin only.
    JSON body: {admin_token, name, slug?, description?}
    Returns: {ok, slug, token, dashboard_url}
    """
    _rate_limit('login', 10, 60)
    data = request.get_json() or {}

    # Super-admin auth
    from auth import is_admin_token
    admin_token = data.get('admin_token', '').strip()
    if not is_admin_token(admin_token):
        return jsonify({'error': 'Invalid admin token'}), 401

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    # Generate slug from name if not provided
    slug = data.get('slug', '').strip()
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '', name.lower())
    slug = slug.lower()

    if not slug or not re.match(r'^[a-z][a-z0-9]*$', slug):
        return jsonify({'error': 'Invalid slug — lowercase letters and numbers only, must start with a letter'}), 400

    artist_dir = Path(f'artists/{slug}')
    if artist_dir.exists():
        return jsonify({'error': f'Artist "{slug}" already exists'}), 409

    # Generate a human-friendly two-word token
    import random
    _nouns = [
        'hat', 'egg', 'car', 'fox', 'owl', 'bee', 'cat', 'dog', 'bat', 'pig',
        'cup', 'sun', 'moon', 'star', 'fish', 'frog', 'bear', 'wolf', 'lamp',
        'boat', 'cake', 'tree', 'door', 'bell', 'drum', 'coin', 'kite', 'ring',
        'sock', 'toad', 'crab', 'dove', 'leaf', 'plum', 'pear', 'lime', 'rose',
        'seed', 'vine', 'rock', 'fern', 'moth', 'wren', 'crow', 'snail', 'elk',
        'yak', 'ram', 'eel', 'ant', 'jay', 'gem', 'orb', 'arch', 'bolt', 'cape',
        'dune', 'fort', 'glen', 'hive', 'isle', 'knot', 'loft', 'nest', 'pond',
    ]
    _adjs = [
        'red', 'big', 'old', 'hot', 'icy', 'dry', 'wet', 'dim', 'tan', 'odd',
        'calm', 'bold', 'cold', 'dark', 'deep', 'fair', 'fast', 'flat', 'glad',
        'gold', 'gray', 'keen', 'kind', 'last', 'lean', 'long', 'loud', 'mild',
        'neat', 'pale', 'pink', 'pure', 'rare', 'rich', 'safe', 'slim', 'slow',
        'soft', 'tall', 'thin', 'tiny', 'warm', 'wide', 'wild', 'wise', 'cool',
        'blue', 'green', 'swift', 'brave', 'crisp', 'fresh', 'grand', 'lucky',
        'proud', 'quiet', 'sharp', 'vivid', 'amber', 'coral', 'dusty', 'foggy',
    ]
    artist_token = random.choice(_adjs) + random.choice(_nouns)

    # Create directory structure
    artist_dir.mkdir(parents=True)
    (artist_dir / 'assets' / 'fonts').mkdir(parents=True)
    (artist_dir / 'assets' / 'images').mkdir(parents=True)

    # Workspace tag — defaults to lastplace; clamped to the caller's
    # visible workspaces so Clive can't accidentally create a personal artist.
    from auth import DEFAULT_WORKSPACE, ALL_WORKSPACES
    ws = (data.get('workspace') or DEFAULT_WORKSPACE).strip().lower()
    if ws not in ALL_WORKSPACES:
        ws = DEFAULT_WORKSPACE
    if ws not in _current_workspaces():
        ws = DEFAULT_WORKSPACE

    # Write config.json
    config = {
        'name': name,
        'slug': slug,
        'domain': '',
        'admin_token': artist_token,
        'description': data.get('description', ''),
        'contact_email': data.get('contact_email', ''),
        'workspace': ws,
    }
    (artist_dir / 'config.json').write_text(
        json.dumps(config, indent=4) + '\n', encoding='utf-8'
    )

    # Copy default fonts from template
    template_fonts = Path('artists/_template/assets/fonts')
    if template_fonts.exists():
        for font_file in template_fonts.iterdir():
            if font_file.is_file():
                shutil.copy2(font_file, artist_dir / 'assets' / 'fonts' / font_file.name)

    # Scaffold pages from template
    _scaffold_new_artist(slug)

    # Compile the new artist
    try:
        subprocess.run(
            ['python3', 'compile.py', '--artist', slug],
            capture_output=True, timeout=30
        )
    except Exception:
        pass  # Non-fatal — user can click Save later

    # Slack: fire-and-forget. Provisions a channel + pinned message if the
    # artist's workspace has Slack configured. Never blocks creation.
    try:
        from integrations.slack import ensure_artist_channel
        ensure_artist_channel(slug)
    except Exception as e:
        _api_log.warning(f'slack provisioning failed for {slug}: {e}')

    return jsonify({
        'ok': True,
        'slug': slug,
        'name': name,
        'token': artist_token,
        'dashboard_url': f'/api/adze/dashboard?slug={slug}',
        'site_url': f'/artists/{slug}/home/',
    })


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate an artist and set a persistent session cookie.
    JSON body: {slug, token}
    Returns: {ok, slug, name} and sets adze_session httpOnly cookie.
    """
    _rate_limit('login', 10, 60)  # 10 attempts per minute per IP
    data = request.get_json() or {}
    slug = data.get('slug', '').strip()
    token = data.get('token', '').strip()
    if not slug or not token:
        return jsonify({'error': 'slug and token required'}), 400
    from auth import verify_artist_token, get_artist_config, is_admin_token
    if not verify_artist_token(slug, token):
        return jsonify({'error': 'Invalid credentials'}), 401
    # Scaffold from template if artist has no pages yet
    _scaffold_new_artist(slug)
    # Track last login
    try:
        cfg_path = Path(f'artists/{slug}/config.json')
        cfg = json.loads(cfg_path.read_text())
        cfg['last_login'] = int(_time.time())
        cfg['last_login_ip'] = request.headers.get('X-Real-IP') or request.remote_addr or ''
        cfg_path.write_text(json.dumps(cfg, indent=4) + '\n')
    except Exception:
        pass
    config = get_artist_config(slug) or {}
    resp = make_response(jsonify({
        'ok': True,
        'slug': slug,
        'name': config.get('display_name') or config.get('name') or slug,
        'is_admin': is_admin_token(token),
        'config': {k: v for k, v in config.items() if k != 'admin_token'}
    }))
    # httpOnly — not accessible via JS (XSS protection)
    # SameSite=Lax — safe for normal navigation, blocks CSRF from cross-site POSTs
    # secure — True when behind TLS (nginx sets X-Forwarded-Proto)
    is_https = request.headers.get('X-Forwarded-Proto') == 'https'
    resp.set_cookie('adze_session', f'{slug}:{token}',
                    httponly=True, samesite='Lax', secure=is_https,
                    max_age=30 * 24 * 3600, path='/')
    return resp


@bp.route('/logout', methods=['POST'])
def logout():
    """Clear the session cookie."""
    resp = make_response(jsonify({'ok': True}))
    resp.delete_cookie('adze_session', path='/')
    return resp


@bp.route('/whoami')
def whoami():
    """
    Return the authenticated artist info based on session cookie or headers.
    Used by the dashboard on page load to restore a persistent session.
    """
    slug = get_authenticated_artist()
    if not slug:
        return jsonify({'ok': False}), 401
    from auth import get_artist_config, is_admin_token
    config = get_artist_config(slug) or {}
    header_token = request.headers.get('X-Admin-Token', '')
    admin_cookie = request.cookies.get('adze_admin_session', '')
    session_cookie = request.cookies.get('adze_session', '')
    session_token = session_cookie.partition(':')[2] if ':' in session_cookie else ''
    return jsonify({
        'ok': True,
        'slug': slug,
        'name': config.get('display_name') or config.get('name') or slug,
        'is_admin': is_admin_token(header_token) or is_admin_token(admin_cookie) or is_admin_token(session_token),
        'config': {k: v for k, v in config.items() if k != 'admin_token'}
    })


# ── Default Styles ────────────────────────────────────────────────────────────

@bp.route('/default-styles')
def get_default_styles():
    """Read the artist's default-styles.css. Falls back to extracting :root from home page."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    artist_path = get_artist_path(artist_slug)
    styles_file = artist_path / 'default-styles.css'

    if styles_file.exists():
        return jsonify({'css': styles_file.read_text(encoding='utf-8'), 'exists': True})

    # Fallback: extract :root {} from home page
    home_content = artist_path / 'home' / 'content.md'
    if home_content.exists():
        import re as _re
        raw = home_content.read_text(encoding='utf-8')
        style_match = _re.search(r'<style>(.*?)</style>', raw, _re.DOTALL)
        if style_match:
            css_text = style_match.group(1)
            root_match = _re.search(r':root\s*\{[^}]+\}', css_text)
            if root_match:
                return jsonify({'css': root_match.group(0) + '\n', 'exists': False})

    return jsonify({'css': '', 'exists': False})


@bp.route('/default-styles', methods=['POST'])
def save_default_styles():
    """Save the artist's default-styles.css."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json() or {}
    css = data.get('css', '').strip()
    if not css:
        return jsonify({'error': 'css is required'}), 400

    artist_path = get_artist_path(artist_slug)
    styles_file = artist_path / 'default-styles.css'
    styles_file.write_text(css + '\n', encoding='utf-8')
    return jsonify({'ok': True})


# ── Dashboard Theme Override ──────────────────────────────────────────────────

@bp.route('/dashboard-theme')
def get_dashboard_theme():
    """
    Return the admin-selected dashboard theme CSS for the authenticated artist.
    Themes live in _shared/dashboard-themes/{name}/theme.css.
    Returns 204 if no theme is configured or the theme file is missing.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    from auth import get_artist_config
    cfg = get_artist_config(artist_slug) or {}
    theme_name = (cfg.get('dashboard') or {}).get('theme_override')
    if not theme_name:
        return ('', 204)
    theme_file = Path(__file__).parent / 'dashboard-themes' / theme_name / 'theme.css'
    if not theme_file.exists():
        return ('', 204)
    return jsonify({'name': theme_name, 'css': theme_file.read_text(encoding='utf-8')})


# ── Super-Admin Dashboard ─────────────────────────────────────────────────────

@bp.route('/admin')
@bp.route('/admin/artist/<slug>')
@bp.route('/admin/artist')
def serve_admin(slug=None):
    """Serve the super-admin dashboard HTML.

    The same SPA shell is returned for /admin, /admin/artist, and
    /admin/artist/<slug> so the client-side router can resolve the URL on
    refresh / direct link. Slug is read by JS from window.location.pathname.
    """
    admin_path = Path(__file__).parent / 'admin.html'
    if not admin_path.exists():
        return 'Admin dashboard not found', 404
    return admin_path.read_text(encoding='utf-8'), 200, {
        'Content-Type': 'text/html',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
    }


@bp.route('/asset-tree.js')
def asset_tree_js():
    """Serve the shared asset-tree helper used by both the admin dashboard and
    the intake portal. Served under /api/adze/ so it is always same-origin with
    whichever page loads it."""
    js_path = Path(__file__).parent / 'asset_tree.js'
    if not js_path.exists():
        return 'not found', 404
    return js_path.read_text(encoding='utf-8'), 200, {
        'Content-Type': 'application/javascript; charset=utf-8',
        'Cache-Control': 'no-cache',
    }


@bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Validate admin credentials and set persistent cookie.

    Accepts {username, password} (preferred) or legacy {token}.
    The cookie value is the identity's password — get_identity_by_token()
    resolves it back to the identity on subsequent requests.
    """
    _rate_limit('login', 10, 60)
    data = request.get_json() or {}
    from auth import verify_admin_credentials, get_identity_by_token

    username = (data.get('username') or '').strip()
    password = (data.get('password') or data.get('token') or '').strip()

    ident = None
    if username:
        ident = verify_admin_credentials(username, password)
    if not ident:
        # Legacy: token-only login. Password alone must uniquely match.
        ident = get_identity_by_token(password)

    if not ident:
        return jsonify({'error': 'Invalid credentials'}), 401

    is_https = request.headers.get('X-Forwarded-Proto') == 'https'
    resp = make_response(jsonify({
        'ok': True,
        'name': ident['name'],
        'username': ident['username'],
        'workspaces': ident['workspaces'],
        'super': ident.get('super', False),
    }))
    resp.set_cookie('adze_admin_session', ident['password'],
                    httponly=True, samesite='Lax', secure=is_https,
                    max_age=7 * 24 * 3600, path='/')
    return resp


@bp.route('/admin/integrations/slack/provision/<slug>', methods=['POST'])
def admin_slack_provision(slug):
    """Provision (or refresh) a single artist's Slack channel + pin."""
    _require_super_admin()
    if not _valid_slug(slug):
        return jsonify({'error': 'invalid slug'}), 400
    cfg_path = Path('artists') / slug / 'config.json'
    if not cfg_path.exists():
        return jsonify({'error': 'artist not found'}), 404
    cfg = json.loads(cfg_path.read_text())
    if _artist_workspace(cfg) not in _current_workspaces():
        return jsonify({'error': 'not visible'}), 404
    from integrations.slack import ensure_artist_channel
    return jsonify(ensure_artist_channel(slug))


@bp.route('/admin/integrations/slack/backfill', methods=['POST'])
def admin_slack_backfill():
    """Walk every visible artist whose workspace has Slack and provision
    a channel for them. Idempotent — artists with an existing channel just
    get their pinned message refreshed."""
    _require_super_admin()
    from integrations.slack import ensure_artist_channel
    visible_ws = set(_current_workspaces())
    results = []
    artists_dir = Path('artists')
    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_') or item.name == 'example-artist':
            continue
        cfg_path = item / 'config.json'
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            continue
        if _artist_workspace(cfg) not in visible_ws:
            continue
        if cfg.get('is_stub'):
            continue  # lead-only entries don't get a channel
        res = ensure_artist_channel(item.name)
        results.append({'slug': item.name, **res})
    ok = sum(1 for r in results if r.get('ok'))
    return jsonify({'ok': True, 'provisioned': ok, 'total': len(results), 'results': results})


@bp.route('/admin/nav')
def admin_nav():
    """Return tab + widget nav entries the current identity can see.
    Front-end uses this to hide/show tabs and render the Integrations list."""
    _require_super_admin()
    from widgets._registry import visible_tabs, visible_widgets
    ws = _current_workspaces()
    return jsonify({
        'tabs': visible_tabs(ws),
        'widgets': visible_widgets(ws),
    })


@bp.route('/admin/whoami')
def admin_whoami():
    """Return the current admin identity (name, workspaces, super)."""
    from auth import current_admin_identity
    ident = current_admin_identity()
    if not ident:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'name': ident['name'],
        'username': ident['username'],
        'workspaces': ident['workspaces'],
        'super': ident.get('super', False),
    })


@bp.route('/admin/artists')
def admin_artists():
    """List all artists with metadata."""
    _require_super_admin()
    visible_ws = set(_current_workspaces())
    artists_dir = Path('artists')
    result = []
    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_') or item.name == 'example-artist':
            continue
        cfg_path = item / 'config.json'
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            cfg = {}
        if _artist_workspace(cfg) not in visible_ws:
            continue
        if cfg.get('is_stub'):
            # Lead-only entries don't represent a hosted site; skip them here so
            # the Artists table stays focused on actual hosted artists. They're
            # still visible in the pipeline grid.
            continue
        # Count pages
        pages = [d.name for d in item.iterdir()
                 if d.is_dir() and (d / 'content.md').exists()
                 and d.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups')]
        # 30d pageviews
        views_30d = 0
        try:
            db_path = item / 'data.db'
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(str(db_path), timeout=2)
                cutoff = int(_time.time()) - 30 * 86400
                row = conn.execute('SELECT COUNT(*) FROM pageviews WHERE ts > ?', (cutoff,)).fetchone()
                views_30d = row[0] if row else 0
                conn.close()
        except Exception:
            pass
        # Storage
        storage = _get_artist_storage(item.name)
        # Hosted-domain liveness: a per-domain nginx config exists in the
        # repo's nginx/sites-available/ (bind-mounted into the container).
        # Not checking SSL cert path — SAN/wildcard certs may live under a
        # different domain's letsencrypt dir (e.g. ninasere.com uses the
        # adze.studio cert), and /etc/nginx isn't visible inside the container.
        domain = cfg.get('domain', '')
        domain_live = bool(domain) and Path(f'nginx/sites-available/{domain}').exists()
        result.append({
            'slug': item.name,
            'name': cfg.get('name', item.name),
            'domain': domain,
            'domain_live': domain_live,
            'contact_email': cfg.get('contact_email', ''),
            'pages': pages,
            'page_count': len(pages),
            'storage_bytes': storage,
            'views_30d': views_30d,
            'last_login': cfg.get('last_login'),
            'last_login_ip': cfg.get('last_login_ip', ''),
            'admin_token': cfg.get('admin_token', ''),
            'workspace': _artist_workspace(cfg),
        })
    return jsonify({'artists': result})


@bp.route('/admin/dashboard-themes')
def admin_dashboard_themes():
    """List available dashboard themes from _shared/dashboard-themes/."""
    _require_super_admin()
    themes_dir = Path(__file__).parent / 'dashboard-themes'
    themes = []
    if themes_dir.exists():
        for item in sorted(themes_dir.iterdir()):
            if not item.is_dir() or item.name.startswith('_'):
                continue
            if (item / 'theme.css').exists():
                themes.append({'name': item.name})
    return jsonify({'themes': themes})


@bp.route('/admin/artists/<slug>/widgets')
def admin_artist_widgets(slug):
    """
    List every widget visible to the artist (across tiers) plus the hardcoded T1
    dashboard tab IDs, so the super-admin UI can offer them as hide targets.
    T4 artist-custom widgets are excluded — those are always on.
    """
    _require_super_admin()
    artist_path = Path('artists') / slug
    if not artist_path.exists():
        abort(404)

    # T2 platform widgets (all, regardless of whether artist has opted in)
    platform_dir = Path(__file__).parent / 'widgets'
    platform = [{'name': w['name'], 'tier': 'platform'}
                for w in _scan_widgets(platform_dir, 'platform')]

    # T1 hardcoded dashboard tabs — IDs match data-tab in dashboard.html
    core = [{'name': n, 'tier': 'core'} for n in [
        'edit', 'claude', 'styles', 'assets', 'snapshots', 'domain', 'api',
        'fonts', 'export', 'share', 'analytics', 'extensions', 'about',
    ]]

    return jsonify({'widgets': core + platform})


@bp.route('/admin/artists/<slug>/dashboard-config', methods=['GET'])
def admin_get_dashboard_config(slug):
    """Return the artist's dashboard section from config.json."""
    _require_super_admin()
    cfg_path = Path('artists') / slug / 'config.json'
    if not cfg_path.exists():
        abort(404)
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        cfg = {}
    dashboard = cfg.get('dashboard') or {}
    return jsonify({
        'hidden_widgets': dashboard.get('hidden_widgets', []),
        'theme_override': dashboard.get('theme_override'),
    })


@bp.route('/admin/artists/<slug>/dashboard-config', methods=['POST'])
def admin_set_dashboard_config(slug):
    """Update the artist's dashboard.{hidden_widgets,theme_override} config."""
    _require_super_admin()
    cfg_path = Path('artists') / slug / 'config.json'
    if not cfg_path.exists():
        abort(404)
    data = request.get_json() or {}
    hidden = data.get('hidden_widgets', [])
    theme = data.get('theme_override')
    if not isinstance(hidden, list) or not all(isinstance(x, str) for x in hidden):
        return jsonify({'error': 'hidden_widgets must be an array of strings'}), 400
    if theme is not None and not isinstance(theme, str):
        return jsonify({'error': 'theme_override must be a string or null'}), 400
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        cfg = {}
    cfg.setdefault('dashboard', {})
    cfg['dashboard']['hidden_widgets'] = hidden
    cfg['dashboard']['theme_override'] = theme or None
    cfg_path.write_text(json.dumps(cfg, indent=4) + '\n', encoding='utf-8')
    return jsonify({'ok': True})


@bp.route('/admin/artists/<slug>', methods=['DELETE'])
def admin_delete_artist(slug):
    """
    Permanently delete an artist's site (source + compiled output).
    Super-admin only. Confirmation is enforced in the UI.
    """
    _require_super_admin()
    if not _valid_slug(slug):
        return jsonify({'error': 'Invalid slug'}), 400
    artist_path = Path('artists') / slug
    output_path = Path('output/artists') / slug
    if not artist_path.exists() and not output_path.exists():
        return jsonify({'error': 'Artist not found'}), 404
    try:
        if artist_path.exists():
            shutil.rmtree(str(artist_path))
        if output_path.exists():
            shutil.rmtree(str(output_path))
        return jsonify({'ok': True, 'slug': slug})
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


@bp.route('/admin/traffic')
def admin_traffic():
    """Aggregate traffic across all artists."""
    _require_super_admin()
    import sqlite3
    artists_dir = Path('artists')
    now = int(_time.time())
    today_start = now - (now % 86400)
    week_start = now - 7 * 86400
    month_start = now - 30 * 86400

    total_today = 0
    total_week = 0
    total_month = 0
    per_artist = []
    daily_agg = {}  # date_str -> count

    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_'):
            continue
        db_path = item / 'data.db'
        if not db_path.exists():
            continue
        try:
            conn = sqlite3.connect(str(db_path), timeout=2)
            today = conn.execute('SELECT COUNT(*) FROM pageviews WHERE ts >= ?', (today_start,)).fetchone()[0]
            week = conn.execute('SELECT COUNT(*) FROM pageviews WHERE ts >= ?', (week_start,)).fetchone()[0]
            month = conn.execute('SELECT COUNT(*) FROM pageviews WHERE ts >= ?', (month_start,)).fetchone()[0]
            total_today += today
            total_week += week
            total_month += month
            per_artist.append({'slug': item.name, 'today': today, 'week': week, 'month': month})
            # Daily breakdown for chart
            rows = conn.execute(
                "SELECT date(ts, 'unixepoch') as d, COUNT(*) FROM pageviews WHERE ts >= ? GROUP BY d ORDER BY d",
                (month_start,)
            ).fetchall()
            for date_str, count in rows:
                daily_agg[date_str] = daily_agg.get(date_str, 0) + count
            conn.close()
        except Exception:
            continue

    daily = [{'date': d, 'views': v} for d, v in sorted(daily_agg.items())]
    per_artist.sort(key=lambda x: x['month'], reverse=True)
    return jsonify({
        'total_today': total_today,
        'total_week': total_week,
        'total_month': total_month,
        'daily': daily,
        'per_artist': per_artist,
    })


@bp.route('/admin/logs')
def admin_logs():
    """Tail a log file. Query params: file=api|vibe, lines=200, filter=text."""
    _require_super_admin()
    from collections import deque
    log_file = request.args.get('file', 'api')
    if log_file not in ('api', 'vibe'):
        return jsonify({'error': 'file must be api or vibe'}), 400
    max_lines = min(int(request.args.get('lines', 200)), 1000)
    text_filter = request.args.get('filter', '').strip().lower()

    log_path = _LOGS_DIR / f'{log_file}.log'
    if not log_path.exists():
        return jsonify({'lines': [], 'total_lines': 0})
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = deque(f, maxlen=max_lines * 3 if text_filter else max_lines)
        lines = [l.rstrip('\n') for l in all_lines]
        if text_filter:
            lines = [l for l in lines if text_filter in l.lower()][-max_lines:]
        return jsonify({'lines': lines, 'total_lines': len(lines)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/usage')
def admin_usage():
    """Per-artist resource usage: storage, vibe sessions, duration."""
    _require_super_admin()
    artists_dir = Path('artists')
    vibe_log = _LOGS_DIR / 'vibe.log'

    # Parse vibe log for per-artist stats
    vibe_stats = {}  # slug -> {sessions: int, total_duration_ms: int}
    if vibe_log.exists():
        try:
            with open(vibe_log, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    m = re.search(r'\[(\w+)\] ── PROMPT ──', line)
                    if m:
                        slug = m.group(1)
                        if slug not in vibe_stats:
                            vibe_stats[slug] = {'sessions': 0, 'total_duration_ms': 0}
                        vibe_stats[slug]['sessions'] += 1
                    m = re.search(r'\[(\w+)\] RESULT: cost=\S+ duration=(\d+)ms', line)
                    if m:
                        slug = m.group(1)
                        dur = int(m.group(2))
                        if slug not in vibe_stats:
                            vibe_stats[slug] = {'sessions': 0, 'total_duration_ms': 0}
                        vibe_stats[slug]['total_duration_ms'] += dur
        except Exception:
            pass

    result = []
    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_'):
            continue
        if not (item / 'config.json').exists():
            continue
        slug = item.name
        storage = _get_artist_storage(slug)
        vs = vibe_stats.get(slug, {'sessions': 0, 'total_duration_ms': 0})
        try:
            has_active = slug in _claude_sessions
        except NameError:
            has_active = False
        result.append({
            'slug': slug,
            'storage_bytes': storage,
            'vibe_sessions': vs['sessions'],
            'vibe_duration_ms': vs['total_duration_ms'],
            'has_active_session': has_active,
        })
    result.sort(key=lambda x: x['vibe_sessions'], reverse=True)
    return jsonify({'artists': result})


@bp.route('/admin/status')
def admin_status():
    """System status: Docker, backups, disk. Read from status.json (updated by host cron)."""
    _require_super_admin()

    # Read status.json written by status-update.sh on the host
    status_path = Path(__file__).parent.parent / 'logs' / 'status.json'
    status = {}
    try:
        if status_path.exists():
            status = json.loads(status_path.read_text())
    except Exception:
        pass

    # Add live data from inside the container
    try:
        status['claude'] = {'active_sessions': len(_claude_sessions)}
    except Exception:
        status['claude'] = {'active_sessions': 0}

    return jsonify(status)


# ── Studio data (hours log + leads CRM) ──────────────────────────────────────

_STUDIO_DATA_DIR = Path(__file__).parent.parent / 'data'
_STUDIO_DATA_DIR.mkdir(exist_ok=True)
_HOURS_FILE = _STUDIO_DATA_DIR / 'hours.json'
_LEADS_FILE = _STUDIO_DATA_DIR / 'leads.json'  # legacy; preserved for the table sub-view
_PINNED_ORDER_FILE = _STUDIO_DATA_DIR / 'pinned_order.json'
_TODOS_FILE = _STUDIO_DATA_DIR / 'todos.json'


def _read_studio_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    return []


def _write_studio_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


@bp.route('/admin/hours')
def admin_hours_list():
    _require_super_admin()
    return jsonify({'entries': _read_studio_json(_HOURS_FILE)})


@bp.route('/admin/hours', methods=['POST'])
def admin_hours_create():
    _require_super_admin()
    import uuid
    data = request.get_json() or {}
    entry = {
        'id': str(uuid.uuid4()),
        'date': data.get('date', ''),
        'person': data.get('person', ''),
        'scope': data.get('scope', ''),
        'description': data.get('description', ''),
        'hours': float(data.get('hours', 0)),
        'created_at': int(_time.time()),
    }
    entries = _read_studio_json(_HOURS_FILE)
    entries.append(entry)
    _write_studio_json(_HOURS_FILE, entries)
    return jsonify({'entry': entry}), 201


@bp.route('/admin/hours/<entry_id>', methods=['PUT', 'PATCH'])
def admin_hours_update(entry_id):
    _require_super_admin()
    data = request.get_json() or {}
    entries = _read_studio_json(_HOURS_FILE)
    updated = None
    for e in entries:
        if e.get('id') == entry_id:
            # id and created_at are immutable; everything else is editable.
            for field in ('date', 'person', 'scope', 'description'):
                if field in data:
                    e[field] = data[field]
            if 'hours' in data:
                e['hours'] = float(data['hours'] or 0)
            e['updated_at'] = int(_time.time())
            updated = e
            break
    if updated is None:
        return jsonify({'error': 'Entry not found'}), 404
    _write_studio_json(_HOURS_FILE, entries)
    return jsonify({'entry': updated})


@bp.route('/admin/hours/<entry_id>', methods=['DELETE'])
def admin_hours_delete(entry_id):
    _require_super_admin()
    entries = _read_studio_json(_HOURS_FILE)
    entries = [e for e in entries if e.get('id') != entry_id]
    _write_studio_json(_HOURS_FILE, entries)
    return jsonify({'ok': True})


# ── To-dos ──────────────────────────────────────────────────────────────────
# Studio-wide quick to-do list. Each item may optionally reference an artist by
# slug. Persisted to data/todos.json alongside hours/leads. Super-admin only.

def _todo_artist_valid(slug):
    """An artist reference is valid only if that artist dir exists; '' = none."""
    if not slug:
        return True
    return _valid_slug(slug) and (Path('artists') / slug / 'config.json').exists()


@bp.route('/admin/todos')
def admin_todos_list():
    _require_super_admin()
    return jsonify({'todos': _read_studio_json(_TODOS_FILE)})


@bp.route('/admin/todos', methods=['POST'])
def admin_todos_create():
    _require_super_admin()
    import uuid
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'text is required'}), 400
    artist = (data.get('artist') or '').strip()
    if not _todo_artist_valid(artist):
        artist = ''
    now = int(_time.time())
    todo = {
        'id': str(uuid.uuid4()),
        'text': text,
        'artist': artist,
        'due': (data.get('due') or '').strip(),
        'done': bool(data.get('done', False)),
        'created_at': now,
        'updated_at': now,
        'done_at': now if data.get('done') else None,
    }
    todos = _read_studio_json(_TODOS_FILE)
    todos.insert(0, todo)
    _write_studio_json(_TODOS_FILE, todos)
    return jsonify({'todo': todo}), 201


@bp.route('/admin/todos/<todo_id>', methods=['PUT', 'PATCH'])
def admin_todos_update(todo_id):
    _require_super_admin()
    data = request.get_json() or {}
    todos = _read_studio_json(_TODOS_FILE)
    updated = None
    for t in todos:
        if t.get('id') != todo_id:
            continue
        if 'text' in data:
            text = (data.get('text') or '').strip()
            if text:
                t['text'] = text
        if 'artist' in data:
            artist = (data.get('artist') or '').strip()
            t['artist'] = artist if _todo_artist_valid(artist) else ''
        if 'due' in data:
            t['due'] = (data.get('due') or '').strip()
        if 'done' in data:
            done = bool(data['done'])
            # Only stamp done_at on a transition into done.
            if done and not t.get('done'):
                t['done_at'] = int(_time.time())
            elif not done:
                t['done_at'] = None
            t['done'] = done
        t['updated_at'] = int(_time.time())
        updated = t
        break
    if updated is None:
        return jsonify({'error': 'Todo not found'}), 404
    _write_studio_json(_TODOS_FILE, todos)
    return jsonify({'todo': updated})


@bp.route('/admin/todos/<todo_id>', methods=['DELETE'])
def admin_todos_delete(todo_id):
    _require_super_admin()
    todos = _read_studio_json(_TODOS_FILE)
    todos = [t for t in todos if t.get('id') != todo_id]
    _write_studio_json(_TODOS_FILE, todos)
    return jsonify({'ok': True})


@bp.route('/admin/leads')
def admin_leads_list():
    _require_super_admin()
    from auth import DEFAULT_WORKSPACE
    visible_ws = set(_current_workspaces())
    leads = _read_studio_json(_LEADS_FILE)
    filtered = [l for l in leads
                if (l.get('workspace') or DEFAULT_WORKSPACE) in visible_ws]
    return jsonify({'leads': filtered})


@bp.route('/admin/leads', methods=['POST'])
def admin_leads_create():
    _require_super_admin()
    from auth import DEFAULT_WORKSPACE, ALL_WORKSPACES
    import uuid
    data = request.get_json() or {}
    now = int(_time.time())
    ws = (data.get('workspace') or DEFAULT_WORKSPACE).strip().lower()
    if ws not in ALL_WORKSPACES:
        ws = DEFAULT_WORKSPACE
    # Non-super users can only create within their own visible workspaces.
    if ws not in _current_workspaces():
        ws = DEFAULT_WORKSPACE
    lead = {
        'id': str(uuid.uuid4()),
        'client': data.get('client', ''),
        'active': bool(data.get('active', True)),
        'contact': data.get('contact', ''),
        'stage': data.get('stage'),
        'contacted': bool(data.get('contacted', False)),
        'fish_size': data.get('fish_size'),
        'instagram': data.get('instagram', ''),
        'work': data.get('work', ''),
        'clive_hours': float(data.get('clive_hours', 0)),
        'gabe_hours': float(data.get('gabe_hours', 0)),
        'discount': data.get('discount', ''),
        'notes': data.get('notes', ''),
        'workspace': ws,
        'created_at': now,
        'updated_at': now,
    }
    leads = _read_studio_json(_LEADS_FILE)
    leads.append(lead)
    _write_studio_json(_LEADS_FILE, leads)
    return jsonify({'lead': lead}), 201


@bp.route('/admin/leads/<lead_id>', methods=['PUT'])
def admin_leads_update(lead_id):
    _require_super_admin()
    from auth import DEFAULT_WORKSPACE, ALL_WORKSPACES
    data = request.get_json() or {}
    leads = _read_studio_json(_LEADS_FILE)
    visible_ws = _current_workspaces()
    for lead in leads:
        if lead.get('id') == lead_id:
            current_ws = lead.get('workspace') or DEFAULT_WORKSPACE
            if current_ws not in visible_ws:
                return jsonify({'error': 'Not found'}), 404
            # Re-scoping: only super admins can change a lead's workspace.
            if 'workspace' in data and _is_super():
                new_ws = (data['workspace'] or DEFAULT_WORKSPACE).strip().lower()
                if new_ws in ALL_WORKSPACES:
                    lead['workspace'] = new_ws
            lead['client']      = data.get('client', lead.get('client', ''))
            lead['active']      = bool(data.get('active', lead.get('active', True)))
            lead['contact']     = data.get('contact', lead.get('contact', ''))
            lead['stage']       = data.get('stage', lead.get('stage'))
            lead['contacted']   = bool(data.get('contacted', lead.get('contacted', False)))
            lead['fish_size']   = data.get('fish_size', lead.get('fish_size'))
            lead['instagram']   = data.get('instagram', lead.get('instagram', ''))
            lead['work']        = data.get('work', lead.get('work', ''))
            lead['clive_hours'] = float(data.get('clive_hours', lead.get('clive_hours', 0)))
            lead['gabe_hours']  = float(data.get('gabe_hours', lead.get('gabe_hours', 0)))
            lead['discount']    = data.get('discount', lead.get('discount', ''))
            lead['notes']       = data.get('notes', lead.get('notes', ''))
            lead['updated_at']  = int(_time.time())
            _write_studio_json(_LEADS_FILE, leads)
            return jsonify({'lead': lead})
    return jsonify({'error': 'Lead not found'}), 404


@bp.route('/admin/leads/<lead_id>', methods=['DELETE'])
def admin_leads_delete(lead_id):
    _require_super_admin()
    leads = _read_studio_json(_LEADS_FILE)
    leads = [l for l in leads if l.get('id') != lead_id]
    _write_studio_json(_LEADS_FILE, leads)
    return jsonify({'ok': True})


# ── Pipeline (merged artists + leads) ────────────────────────────────────────
# Cards represent artists. An artist with no `lead` block in config.json is
# implicitly XS — Minnow. Hours roll up by matching scope=lead:<original_id> or
# scope=artist:<slug> in hours.json.

def _hours_rollup_by_scope():
    """Return {scope_key: total_hours} so the pipeline endpoint can attach
    hours-this-month to each artist card."""
    entries = _read_studio_json(_HOURS_FILE)
    rollup = {}
    month_start = _time.strftime('%Y-%m-01', _time.gmtime())
    for e in entries:
        if (e.get('date') or '') < month_start:
            continue
        scope = e.get('scope') or ''
        rollup[scope] = rollup.get(scope, 0) + float(e.get('hours') or 0)
    return rollup


@bp.route('/admin/pipeline')
def admin_pipeline():
    """Unified Artists & Leads view. One card per artist; lead block embedded
    alongside the same rollups the Artists table shows (pages, storage, 30d
    views, last login, hours)."""
    _require_super_admin()
    visible_ws = set(_current_workspaces())
    artists_dir = Path('artists')
    hours_by_scope = _hours_rollup_by_scope()
    cards = []
    for item in sorted(artists_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_') or item.name == 'example-artist':
            continue
        cfg_path = item / 'config.json'
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            continue
        if _artist_workspace(cfg) not in visible_ws:
            continue
        slug = item.name
        lead = cfg.get('lead') or {}
        # Hours: try lead's original_lead_id first (legacy hours rows reference
        # lead:<uuid>), then artist:<slug>.
        hrs = 0.0
        if lead.get('original_lead_id'):
            hrs += hours_by_scope.get(f"lead:{lead['original_lead_id']}", 0)
        hrs += hours_by_scope.get(f"artist:{slug}", 0)
        # Pages, storage, views, last login — same as /admin/artists.
        pages = [d.name for d in item.iterdir()
                 if d.is_dir() and (d / 'content.md').exists()
                 and d.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups')]
        views_30d = 0
        views_series = []  # daily counts for last 30 days, oldest → newest
        try:
            db_path = item / 'data.db'
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(str(db_path), timeout=2)
                now = int(_time.time())
                cutoff = now - 30 * 86400
                row = conn.execute('SELECT COUNT(*) FROM pageviews WHERE ts > ?', (cutoff,)).fetchone()
                views_30d = row[0] if row else 0
                # Bucket by day for a sparkline.
                rows = conn.execute(
                    "SELECT CAST((? - ts) / 86400 AS INT) AS d_ago, COUNT(*) "
                    "FROM pageviews WHERE ts > ? GROUP BY d_ago",
                    (now, cutoff),
                ).fetchall()
                buckets = [0] * 30
                for d_ago, count in rows:
                    if 0 <= d_ago < 30:
                        buckets[29 - d_ago] = count
                views_series = buckets
                conn.close()
        except Exception:
            pass
        domain = cfg.get('domain', '')
        domain_live = bool(domain) and Path(f'nginx/sites-available/{domain}').exists()
        cards.append({
            'slug': slug,
            'name': cfg.get('name') or slug,
            'domain': domain,
            'domain_live': domain_live,
            'description': cfg.get('description', ''),
            'contact_email': cfg.get('contact_email', ''),
            'admin_token': cfg.get('admin_token', ''),
            'is_stub': bool(cfg.get('is_stub')),  # lead-only; no real hosted site
            'page_count': len(pages),
            'storage_bytes': _get_artist_storage(slug),
            'views_30d': views_30d,
            'views_series': views_series,
            'last_login': cfg.get('last_login'),
            'has_lead': bool(lead),
            'lead': lead or None,
            'fish_size': (lead.get('fish_size') if lead else None) or 'xs',
            'stage': (lead.get('stage') if lead else None),
            'active': bool(lead.get('active')) if lead else False,
            'hours_this_month': round(hrs, 2),
            'updated_at': lead.get('updated_at') if lead else None,
            'workspace': _artist_workspace(cfg),
            'figma_url': cfg.get('figma_url', ''),
            'slack_channel_id': cfg.get('slack_channel_id', ''),
        })
    return jsonify({
        'cards': cards,
        'pinned_order': _read_studio_json(_PINNED_ORDER_FILE) or [],
    })


@bp.route('/admin/artists/<slug>', methods=['PATCH'])
def admin_artist_patch(slug):
    """Update an artist's core fields (name, domain, description, contact_email).
    Lead block is updated separately via /admin/artists/<slug>/lead."""
    _require_super_admin()
    if not _valid_slug(slug):
        return jsonify({'error': 'invalid slug'}), 400
    cfg_path = Path('artists') / slug / 'config.json'
    if not cfg_path.exists():
        return jsonify({'error': 'artist not found'}), 404
    cfg = json.loads(cfg_path.read_text())
    data = request.get_json() or {}
    # Workspace gate: caller must currently see this artist.
    if _artist_workspace(cfg) not in _current_workspaces():
        return jsonify({'error': 'artist not found'}), 404
    # Snapshot fields whose changes trigger noisy Slack updates.
    _before = {f: cfg.get(f, '') for f in ('domain', 'figma_url')}
    for field in ('name', 'domain', 'description', 'contact_email', 'figma_url'):
        if field in data:
            cfg[field] = (data[field] or '').strip()
    # Re-scoping: only super admins may move an artist between workspaces.
    if 'workspace' in data and _is_super():
        from auth import ALL_WORKSPACES, DEFAULT_WORKSPACE
        new_ws = (data['workspace'] or DEFAULT_WORKSPACE).strip().lower()
        if new_ws in ALL_WORKSPACES:
            cfg['workspace'] = new_ws
    if 'is_stub' in data:
        if data['is_stub']:
            cfg['is_stub'] = True
        else:
            cfg.pop('is_stub', None)
    cfg_path.write_text(json.dumps(cfg, indent=4) + '\n')
    # If this artist has a Slack channel, refresh the pinned message and
    # post noisy bare-URL announcements for any tracked field that changed
    # (Figma/domain unfurl with previews). Fire-and-forget.
    if cfg.get('slack_channel_id'):
        try:
            from integrations.slack import refresh_pinned, post_field_update
            refresh_pinned(slug)
            for f, before in _before.items():
                after = cfg.get(f, '')
                if after and after != before:
                    post_field_update(slug, f, after)
        except Exception as e:
            _api_log.warning(f'slack pin refresh failed for {slug}: {e}')
    return jsonify({'artist': {k: cfg.get(k, '') for k in ('name', 'slug', 'domain', 'description', 'contact_email', 'figma_url')}})


@bp.route('/admin/artists/<slug>/lead', methods=['PUT', 'DELETE'])
def admin_artist_lead_update(slug):
    """Write or clear the lead block on an artist's config.json."""
    _require_super_admin()
    if not _valid_slug(slug):
        return jsonify({'error': 'invalid slug'}), 400
    cfg_path = Path('artists') / slug / 'config.json'
    if not cfg_path.exists():
        return jsonify({'error': 'artist not found'}), 404
    cfg = json.loads(cfg_path.read_text())
    if request.method == 'DELETE':
        cfg.pop('lead', None)
        cfg_path.write_text(json.dumps(cfg, indent=4) + '\n')
        return jsonify({'ok': True})
    data = request.get_json() or {}
    existing = cfg.get('lead') or {}
    block = {
        'active': bool(data.get('active', existing.get('active', True))),
        'contact': data.get('contact', existing.get('contact', '')) or '',
        'stage': data.get('stage', existing.get('stage')) or None,
        'fish_size': data.get('fish_size', existing.get('fish_size')) or None,
        'instagram': data.get('instagram', existing.get('instagram', '')) or '',
        'work': data.get('work', existing.get('work', '')) or '',
        'discount': data.get('discount', existing.get('discount', '')) or '',
        'notes': data.get('notes', existing.get('notes', '')) or '',
        'clive_hours': float(data.get('clive_hours', existing.get('clive_hours', 0)) or 0),
        'gabe_hours': float(data.get('gabe_hours', existing.get('gabe_hours', 0)) or 0),
        'contacted': bool(data.get('contacted', existing.get('contacted', False))),
        'original_lead_id': existing.get('original_lead_id'),
        'created_at': existing.get('created_at') or int(_time.time()),
        'updated_at': int(_time.time()),
    }
    cfg['lead'] = block
    cfg_path.write_text(json.dumps(cfg, indent=4) + '\n')
    return jsonify({'lead': block})


@bp.route('/admin/pipeline/order', methods=['GET', 'PUT'])
def admin_pipeline_order():
    """Persist the user's manual card ordering. Body: {order: [slug, ...]}."""
    _require_super_admin()
    if request.method == 'GET':
        return jsonify({'order': _read_studio_json(_PINNED_ORDER_FILE) or []})
    data = request.get_json() or {}
    order = data.get('order', [])
    if not isinstance(order, list):
        return jsonify({'error': 'order must be a list'}), 400
    _write_studio_json(_PINNED_ORDER_FILE, [str(s) for s in order])
    return jsonify({'ok': True, 'order': order})


# ── Docs ──────────────────────────────────────────────────────────────────────

@bp.route('/docs')
@bp.route('/docs/<path:doc_path>')
def serve_docs(doc_path=None):
    """
    Render the _shared/docs/ markdown files as a simple HTML page.
    Requires login (artist or super-admin).
    """
    # Auth gate: require either super-admin or artist session
    from auth import is_admin_token, verify_artist_token
    admin_cookie = request.cookies.get('adze_admin_session', '')
    artist_cookie = request.cookies.get('adze_session', '')
    has_admin = is_admin_token(admin_cookie)
    has_artist = False
    if artist_cookie and ':' in artist_cookie:
        s, _, t = artist_cookie.partition(':')
        has_artist = verify_artist_token(s, t)
    if not has_admin and not has_artist:
        return '''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Adze Docs — Login</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Cardo:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>body{font-family:'Inter',-apple-system,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f5f2ed;margin:0}
.box{background:#fff;padding:2.5rem;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.08);text-align:center;max-width:340px;width:100%}
h2{margin:0 0 0.5rem;font-family:'Cardo',Georgia,serif;font-weight:400;font-style:italic;font-size:1.3rem;color:#2a2a28}
p{color:#6b6860;font-size:13px;margin:0 0 1.5rem}
input{width:100%;padding:10px 12px;border:1px solid #ddd8cf;border-radius:4px;font-size:14px;box-sizing:border-box;background:#f5f2ed}
button{margin-top:12px;padding:10px 28px;background:#1C4F82;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:14px}
button:hover{background:#163f68}.err{color:#c0392b;font-size:13px;margin-top:8px;display:none}</style></head>
<body><div class="box"><img src="/api/adze/logo.png" alt="" style="height:32px;margin-bottom:12px;opacity:0.85">
<h2>Adze Studio</h2><p>Login to view docs</p>
<input type="password" id="pw" placeholder="Password" onkeydown="if(event.key==='Enter')go()">
<button onclick="go()">Login</button><div class="err" id="err">Invalid password</div>
<script>async function go(){const r=await fetch('/api/adze/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({token:document.getElementById('pw').value})});if(r.ok){location.reload()}else{document.getElementById('err').style.display='block'}}</script>
</div></body></html>''', 200, {'Content-Type': 'text/html'}
    import re as _re
    docs_dir = Path(__file__).parent / 'docs'
    doc_files = sorted(docs_dir.glob('[0-9]*.md'))

    # Build nav + content
    nav_items = []
    sections = []
    for f in doc_files:
        name = f.stem.lstrip('0123456789-')
        title = name.replace('-', ' ').title()
        text = f.read_text(encoding='utf-8')
        # First h1 overrides the title
        m = _re.match(r'^#\s+(.+)', text.strip())
        if m:
            title = m.group(1)
        anchor = f.stem
        nav_items.append(f'<a href="#doc-{anchor}">{title}</a>')
        # Minimal markdown → HTML
        html = text
        # 1. Extract code blocks FIRST (before any other processing)
        _code_blocks = []
        def _stash_code(m2):
            escaped = m2.group(2).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            _code_blocks.append(f'<pre><code class="lang-{m2.group(1)}">{escaped}</code></pre>')
            return f'\x00CODEBLOCK{len(_code_blocks)-1}\x00'
        html = _re.sub(r'```(\w*)\n(.*?)```', _stash_code, html, flags=_re.S)
        # 2. Now process headers, inline code, bold (safe — code blocks are stashed)
        html = _re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=_re.M)
        html = _re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=_re.M)
        html = _re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=_re.M)
        html = _re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=_re.M)
        html = _re.sub(r'`([^`]+)`', lambda m3: f'<code>{m3.group(1).replace("<","&lt;").replace(">","&gt;")}</code>', html)
        html = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        # 3. Restore code blocks
        for i, block in enumerate(_code_blocks):
            html = html.replace(f'\x00CODEBLOCK{i}\x00', block)
        # Tables
        def render_table(m2):
            rows = [r.strip() for r in m2.group(0).strip().split('\n') if r.strip() and not _re.match(r'^[\|\s\-:]+$', r)]
            if not rows: return m2.group(0)
            out = ['<table>']
            for i, row in enumerate(rows):
                cells = [c.strip() for c in row.strip('|').split('|')]
                tag = 'th' if i == 0 else 'td'
                out.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            out.append('</table>')
            return '\n'.join(out)
        html = _re.sub(r'(\|.+\|\n)+', render_table, html)
        # Paragraphs
        paras = _re.split(r'\n{2,}', html)
        out_parts = []
        for p in paras:
            p = p.strip()
            if not p: continue
            if p.startswith('<h') or p.startswith('<pre') or p.startswith('<table') or p.startswith('<ul') or p.startswith('<ol'):
                out_parts.append(p)
            else:
                lines = p.split('\n')
                if all(l.strip().startswith('- ') or l.strip().startswith('* ') for l in lines if l.strip()):
                    items = ''.join(f'<li>{l.strip().lstrip("-* ").strip()}</li>' for l in lines if l.strip())
                    out_parts.append(f'<ul>{items}</ul>')
                elif all(_re.match(r'^\d+\.', l.strip()) for l in lines if l.strip()):
                    items = ''.join('<li>' + _re.sub(r'^\d+\.\s*', '', l.strip()) + '</li>' for l in lines if l.strip())
                    out_parts.append(f'<ol>{items}</ol>')
                else:
                    out_parts.append(f'<p>{p}</p>')
        sections.append(f'<section id="doc-{anchor}">\n{"".join(out_parts)}\n</section>')

    nav_html = '\n'.join(nav_items)
    body_html = '\n<hr>\n'.join(sections)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Adze Studio — Docs</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Cardo:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  :root {{ --bg:#f5f2ed; --surface:#fff; --surface2:#f0ede7; --border:#ddd8cf; --text:#2a2a28; --text2:#6b6860; --accent:#1C4F82; --accent-hover:#163f68; --radius:8px; --mono:'Monaco','Menlo','Courier New',monospace; --heading-font:'Cardo',Georgia,serif; --body-font:'Inter',-apple-system,sans-serif; --shadow-sm:0 1px 3px rgba(0,0,0,0.06); }}
  @media(prefers-color-scheme:dark) {{ :root {{ --bg:#1a1a1e; --surface:#2c2c30; --surface2:#343438; --border:#3e3e44; --text:#e8e6e0; --text2:#9a978e; --accent:#99cdff; --shadow-sm:0 1px 3px rgba(0,0,0,0.2); }} }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; scroll-padding-top:72px; }}
  body {{ font-family:var(--body-font); background:var(--bg); color:var(--text); font-size:14px; line-height:1.7; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .docs-header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:14px 32px; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:100; box-shadow:var(--shadow-sm); }}
  .docs-header-left {{ display:flex; align-items:center; gap:16px; }}
  .docs-header-left h1 {{ font-family:var(--heading-font); font-weight:400; font-style:italic; font-size:20px; }}
  .docs-header-left h1 span {{ font-style:normal; font-weight:300; color:var(--text2); font-size:14px; font-family:var(--body-font); margin-left:4px; }}
  .docs-header-right {{ display:flex; gap:8px; }}
  .docs-header-right a {{ background:none; border:1px solid var(--border); padding:6px 14px; border-radius:4px; font-size:12px; color:var(--text2); text-decoration:none; }}
  .docs-header-right a:hover {{ background:var(--surface2); text-decoration:none; }}
  .docs-wrap {{ display:flex; }}
  .docs-nav {{ width:220px; min-width:220px; background:var(--surface); border-right:1px solid var(--border); padding:24px 16px; position:fixed; top:56px; bottom:0; overflow-y:auto; }}
  .docs-nav h2 {{ font-size:11px; font-weight:600; letter-spacing:.5px; color:var(--text2); text-transform:uppercase; margin-bottom:12px; }}
  .docs-nav a {{ display:block; padding:5px 8px; border-radius:var(--radius); font-size:12px; color:var(--text2); margin-bottom:2px; }}
  .docs-nav a:hover {{ background:var(--bg); color:var(--text); text-decoration:none; }}
  .docs-main {{ flex:1; padding:48px; max-width:860px; margin-left:220px; }}
  h1 {{ font-family:var(--heading-font); font-size:24px; font-weight:400; margin:0 0 8px; }}
  h2 {{ font-size:18px; font-weight:600; margin:32px 0 10px; padding-top:8px; border-top:1px solid var(--border); }}
  h3 {{ font-size:14px; font-weight:600; margin:24px 0 8px; }}
  h4 {{ font-size:13px; font-weight:600; margin:16px 0 6px; color:var(--text2); }}
  p {{ margin:0 0 14px; }}
  ul,ol {{ margin:0 0 14px 20px; }}
  li {{ margin-bottom:4px; }}
  pre {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px; overflow-x:auto; margin:0 0 16px; }}
  code {{ font-family:var(--mono); font-size:12px; }}
  p code, li code, td code {{ background:var(--surface2); border:1px solid var(--border); border-radius:3px; padding:1px 5px; font-size:11px; }}
  table {{ border-collapse:collapse; width:100%; margin:0 0 16px; font-size:12px; }}
  th,td {{ border:1px solid var(--border); padding:7px 10px; text-align:left; }}
  th {{ background:var(--surface2); font-weight:600; }}
  hr {{ border:none; border-top:1px solid var(--border); margin:40px 0; }}
  section {{ margin-bottom:8px; }}
  @media(max-width:700px) {{ .docs-nav {{ display:none; }} .docs-main {{ padding:24px; }} }}
</style>
</head>
<body>
<div class="docs-header">
  <div class="docs-header-left">
    <img src="/api/adze/logo.png" alt="" style="height:26px;opacity:0.85">
    <h1>Adze Studio <span>Docs</span></h1>
  </div>
  <div class="docs-header-right">
    <a href="/admin">Admin</a>
    <a href="/dashboard">Dashboard</a>
  </div>
</div>
<div class="docs-wrap">
<div class="docs-nav">
  <h2>Contents</h2>
  {nav_html}
</div>
<div class="docs-main">
{body_html}
</div>
</div>
<script>
// Handle nav clicks — scroll the target into view manually
document.querySelectorAll('.docs-nav a[href^="#"]').forEach(a => {{
    a.addEventListener('click', e => {{
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {{
            target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            history.replaceState(null, '', a.getAttribute('href'));
        }}
    }});
}});
</script>
</body>
</html>"""
    return page, 200, {'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache'}


@bp.route('/world-map.svg')
def serve_world_map():
    """Serve the world map SVG for analytics, stripped of XML preamble for safe DOMParser use."""
    svg_path = Path(__file__).parent / 'world-map.svg'
    if not svg_path.exists():
        abort(404)
    content = svg_path.read_text(encoding='utf-8')
    # Strip XML declaration and DOCTYPE — DOMParser chokes on external DTD references
    import re as _re
    content = _re.sub(r'<\?xml[^?]*\?>', '', content)
    content = _re.sub(r'<!DOCTYPE[^>]*>', '', content)
    content = content.strip()
    from flask import make_response
    response = make_response(content)
    response.headers['Content-Type'] = 'image/svg+xml; charset=utf-8'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


@bp.route('/logo.png')
def serve_logo():
    """Serve the Adze Studio logo"""
    logo_path = Path(__file__).parent / 'adze-logo.png'
    if not logo_path.exists():
        abort(404)
    return send_file(logo_path, mimetype='image/png')

@bp.route('/favicon.png')
def serve_favicon():
    """Serve the Adze Studio favicon (square PNG — Google requires 1:1)."""
    fav_path = Path(__file__).parent / 'adze-favicon.png'
    if not fav_path.exists():
        abort(404)
    return send_file(fav_path, mimetype='image/png')

@bp.route('/favicon.ico')
def serve_favicon_ico():
    """Multi-size .ico for the default /favicon.ico crawlers/browsers request.
    nginx maps the site-root /favicon.ico here (see nginx/sites-available)."""
    ico_path = Path(__file__).parent / 'adze-favicon.ico'
    if not ico_path.exists():
        abort(404)
    return send_file(ico_path, mimetype='image/x-icon')


@bp.route('/brand/<workspace>/<path:filename>')
def serve_brand_asset(workspace, filename):
    """Serve a brand pack asset (brand.css or assets/<filename>). No auth — UI chrome."""
    asset_path = brand_asset_path(workspace, filename)
    if asset_path is None:
        abort(404)
    mimetype, _ = mimetypes.guess_type(str(asset_path))
    if not mimetype:
        mimetype = 'application/octet-stream'
    response = send_file(str(asset_path), mimetype=mimetype)
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


@bp.route('/brand-info')
def brand_info():
    """Return brand pack metadata for the current workspace. No pack → {}."""
    from auth import current_admin_identity
    ws = None
    # Try artist auth first
    artist_slug = get_authenticated_artist()
    if artist_slug:
        try:
            _, cfg = _read_artist_config(artist_slug)
            ws = _artist_workspace(cfg)
        except Exception:
            ws = None
    # Fall back to admin identity
    if not ws:
        ident = current_admin_identity()
        if ident and ident.get('workspaces'):
            ws = ident['workspaces'][0]
    if not ws:
        return jsonify({})
    brand = brand_json(ws)
    if not brand:
        return jsonify({})
    return jsonify({**brand, 'workspace': ws, 'asset_base_url': f'/api/adze/brand/{ws}/'})


@bp.route('/robots.txt')
def serve_robots():
    """adze.studio robots.txt. nginx maps the site-root /robots.txt here.
    Keeps /api/ crawlable so Googlebot can fetch the favicon; only the
    login surfaces are disallowed."""
    body = ("User-agent: *\n"
            "Disallow: /admin\n"
            "Disallow: /dashboard\n"
            "Sitemap: https://adze.studio/sitemap.xml\n")
    return body, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@bp.route('/sitemap.xml')
def serve_sitemap():
    """adze.studio sitemap — just the public landing page. nginx maps the
    site-root /sitemap.xml here."""
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url><loc>https://adze.studio/</loc></url>\n'
            '</urlset>\n')
    return body, 200, {'Content-Type': 'application/xml; charset=utf-8'}


# ── List Pages ─────────────────────────────────────────────────────────────

# ── External manifest ─────────────────────────────────────────────────────
# Lets the dashboard discover whether it's looking at a remote (Seed) artist
# and adjust the preview iframe + tab visibility accordingly.

@bp.route('/external-manifest', methods=['GET'])
def external_manifest():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    import external_artist as _ext
    import remote_fs as _rfs
    if not _ext.is_remote(artist_slug):
        return jsonify({'remote': False})
    try:
        manifest = _rfs.fetch_manifest(artist_slug)
    except _rfs.RemoteError as exc:
        cached = _ext.cached_manifest(artist_slug) or _ext.manifest_defaults(artist_slug)
        return jsonify({'remote': True, 'manifest': cached, 'fetch_error': str(exc)})
    return jsonify({'remote': True, 'manifest': manifest})


@bp.route('/list-pages', methods=['GET'])
def list_pages():
    """
    List all pages for an artist.
    Requires X-Artist-Slug and X-Admin-Token headers.

    For external (remote Seed) artists, enumerates `pages/<slug>/` on the
    remote box — Seed's convention — instead of the local artist dir.
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    import external_artist as _ext
    import remote_fs as _rfs

    if _ext.is_remote(artist_slug):
        try:
            entries = _rfs.list(artist_slug, 'pages')
        except _rfs.RemoteError as exc:
            return jsonify({'error': f'remote: {exc}'}), 502
        pages = []
        for name in entries:
            try:
                cfg_text = _rfs.read(artist_slug, f'pages/{name}/config.json')
            except _rfs.RemoteError:
                continue
            except FileNotFoundError:
                continue
            try:
                config = json.loads(cfg_text)
            except json.JSONDecodeError:
                continue
            pages.append({
                'slug': name,
                'title': config.get('title', name),
                'path': f'pages/{name}',
                'config': config,
            })
        return jsonify({'artist': artist_slug, 'pages': pages, 'remote': True})

    artist_path = get_artist_path(artist_slug)

    if not artist_path.exists():
        return jsonify({'error': 'Artist not found'}), 404

    pages = []

    for item in artist_path.iterdir():
        if item.is_dir():
            config_file = item / 'config.json'
            content_file = item / 'content.md'

            if config_file.exists() and content_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                    pages.append({
                        'slug': item.name,
                        'title': config.get('title', item.name),
                        'path': str(item.relative_to('.')),
                        'config': config
                    })
                except (json.JSONDecodeError, IOError):
                    continue

    return jsonify({
        'artist': artist_slug,
        'pages': pages
    })


# ── Get Page Content ───────────────────────────────────────────────────────

@bp.route('/get-page-content', methods=['GET'])
def get_page_content():
    """
    Get the content of a specific page.
    Query params: page_slug
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    page_slug = request.args.get('page_slug')

    if not page_slug:
        return jsonify({'error': 'page_slug parameter required'}), 400

    import external_artist as _ext
    import remote_fs as _rfs

    if _ext.is_remote(artist_slug):
        # Seed shape: pages/<slug>/{config.json, content.html}
        try:
            cfg_text = _rfs.read(artist_slug, f'pages/{page_slug}/config.json')
            content = _rfs.read(artist_slug, f'pages/{page_slug}/content.html')
        except FileNotFoundError:
            return jsonify({'error': 'Page not found'}), 404
        except _rfs.RemoteError as exc:
            return jsonify({'error': f'remote: {exc}'}), 502
        try:
            config = json.loads(cfg_text)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Bad config.json: {e}'}), 500
        return jsonify({
            'slug': page_slug,
            'config': config,
            'content': content,
            'content_filename': 'content.html',
            'remote': True,
        })

    page_path = get_page_path(artist_slug, page_slug)
    config_file = page_path / 'config.json'
    content_file = page_path / 'content.md'

    if not config_file.exists() or not content_file.exists():
        return jsonify({'error': 'Page not found'}), 404

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'slug': page_slug,
            'config': config,
            'content': content
        })

    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': f'Error reading page: {str(e)}'}), 500


# ── Edit Page ──────────────────────────────────────────────────────────────

@bp.route('/edit-page', methods=['POST'])
def edit_page():
    """
    Edit a page's content and/or config. (External artists: writes to
    pages/<slug>/{content.html,config.json} on the remote Seed repo via
    remote_fs; no local compile is triggered.)
    JSON body: {page_slug, content?, config?}
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()

    if not data or 'page_slug' not in data:
        return jsonify({'error': 'page_slug required'}), 400

    page_slug = data['page_slug']

    import external_artist as _ext
    import remote_fs as _rfs

    if _ext.is_remote(artist_slug):
        try:
            if 'content' in data:
                _rfs.write(artist_slug, f'pages/{page_slug}/content.html', data['content'])
            if 'config' in data:
                _rfs.write(
                    artist_slug,
                    f'pages/{page_slug}/config.json',
                    json.dumps(data['config'], indent=2, ensure_ascii=False),
                )
        except _rfs.RemoteError as exc:
            return jsonify({'error': f'remote: {exc}'}), 502
        return jsonify({
            'success': True,
            'message': 'Page updated (remote). Build separately.',
            'page_slug': page_slug,
            'remote': True,
        })

    # Refuse edits to dashboard-generated pages — they're derived from the
    # artist's dashboard data file (source of truth) and the next rebuild would
    # silently overwrite a direct edit here.
    try:
        from features.artist_admin import generated_pages
    except ImportError:
        from artist_admin import generated_pages
    if page_slug in generated_pages(artist_slug):
        return jsonify({
            'error': f"'{page_slug}' is generated from this artist's dashboard data "
                     f"and can't be edited directly — change it in the dashboard instead.",
            'generated': True,
        }), 409

    page_path = get_page_path(artist_slug, page_slug)

    if not page_path.exists():
        return jsonify({'error': 'Page not found'}), 404

    try:
        # Update content.md if provided
        if 'content' in data:
            # Scan for leaked secrets before saving
            leaked = scan_for_leaked_secrets(artist_slug, data['content'])
            if leaked:
                return jsonify({
                    'error': f'BLOCKED: Secret values detected in page content for keys: {", ".join(leaked)}. '
                             f'Secrets must stay in .env and api.py — never in frontend code.',
                    'leaked_keys': leaked
                }), 400

            content_file = page_path / 'content.md'
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(data['content'])
            # Flask runs as root; Auto-Code/Terminal sandboxes run as uid 1000.
            # Match host uid 1000 so the sandbox can rewrite this file later.
            try: os.chown(content_file, 1000, 1000)
            except OSError: pass

        # Update config.json if provided
        if 'config' in data:
            config_file = page_path / 'config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data['config'], f, indent=4, ensure_ascii=False)
            try: os.chown(config_file, 1000, 1000)
            except OSError: pass

        # Trigger compile to regenerate static files
        compile_ok = True
        compile_error = None
        compile_script = Path.cwd() / 'compile.py'
        if compile_script.exists():
            import subprocess
            result = subprocess.run(
                ['python3', str(compile_script), '--artist', artist_slug],
                capture_output=True, text=True
            )
            compile_ok = result.returncode == 0
            if not compile_ok:
                compile_error = (result.stderr or result.stdout or 'Unknown compile error').strip()

        return jsonify({
            'success': True,
            'message': 'Page updated successfully',
            'page_slug': page_slug,
            'compile_ok': compile_ok,
            'compile_error': compile_error
        })

    except IOError as e:
        return jsonify({'error': f'Error writing page: {str(e)}'}), 500


# ── Raw File Browser ───────────────────────────────────────────────────────
# Backs the Manual Edit tab's file tree. Walks the artist's working dir and
# exposes a constrained read/write surface for power users who want to edit
# raw files without going through the curated tabs (Settings / Styles /
# Backend / etc.). Same compile + autosave path as edit-page.

# Folders that are either too heavy to surface here or already managed by a
# dedicated tab (Assets, Snapshots, Widgets).
FILES_TREE_HIDDEN_DIRS = {'assets', 'widgets', '.snapshots', '__pycache__', 'backups', '.git'}
FILES_HIDDEN_NAMES = {'.DS_Store'}

# Extensions the Manual Edit panel knows how to render.
FILES_TEXT_EXTENSIONS = {
    '.md', '.html', '.htm', '.css', '.js', '.json', '.py', '.txt', '.env',
    '.yml', '.yaml', '.toml', '.ini', '.conf', '.svg', '.xml', '.sh',
}
FILES_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.avif'}
FILES_MAX_TEXT_BYTES = 512 * 1024  # 512 KB cap on read/write to keep textareas usable


def _file_kind(path):
    """Classify a file for the dashboard so it can pick the right editor."""
    suffix = path.suffix.lower()
    if path.name == '.env' or suffix == '.env':
        return 'env'
    if suffix == '.md':
        return 'markdown'
    if suffix in FILES_IMAGE_EXTENSIONS:
        return 'image'
    if suffix in FILES_TEXT_EXTENSIONS:
        return 'text'
    return 'binary'


def _resolve_artist_file(artist_slug, rel_path):
    """
    Resolve `rel_path` inside the artist dir, rejecting any escape attempt.
    Returns (artist_path, file_path) — never raises; returns (None, None)
    on rejection. Symlinks, '..', absolute paths, and hidden-dir traversal
    are all blocked.
    """
    if not rel_path or '\x00' in rel_path:
        return None, None
    rel_path = rel_path.lstrip('/').replace('\\', '/')
    if '..' in rel_path.split('/'):
        return None, None
    artist_path = get_artist_path(artist_slug)
    artist_root = artist_path.resolve()
    target = (artist_path / rel_path).resolve()
    try:
        target.relative_to(artist_root)
    except ValueError:
        return None, None
    if target.is_symlink():
        return None, None
    # Refuse to touch anything under a hidden/managed folder.
    parts = target.relative_to(artist_root).parts
    if any(p in FILES_TREE_HIDDEN_DIRS for p in parts):
        return None, None
    return artist_path, target


@bp.route('/list-artist-files', methods=['GET'])
def list_artist_files():
    """Return every editable file in the artist dir, with kind hints for the UI."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    artist_path = get_artist_path(artist_slug)
    if not artist_path.exists():
        return jsonify({'files': []})

    files = []
    for p in sorted(artist_path.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        if p.name in FILES_HIDDEN_NAMES:
            continue
        rel = p.relative_to(artist_path)
        if any(part in FILES_TREE_HIDDEN_DIRS for part in rel.parts):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        files.append({
            'path': str(rel),
            'kind': _file_kind(p),
            'size': size,
        })
        if len(files) >= 1000:
            break
    return jsonify({'files': files})


@bp.route('/read-artist-file', methods=['GET'])
def read_artist_file():
    """Read a text file's contents. Binary files are refused."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    rel = request.args.get('path', '')
    artist_path, target = _resolve_artist_file(artist_slug, rel)
    if target is None:
        return jsonify({'error': 'Invalid path'}), 400
    if not target.exists() or not target.is_file():
        return jsonify({'error': 'Not found'}), 404
    kind = _file_kind(target)
    if kind == 'binary' or kind == 'image':
        return jsonify({'error': 'Binary file — open in a dedicated tab', 'kind': kind, 'size': target.stat().st_size}), 415
    size = target.stat().st_size
    if size > FILES_MAX_TEXT_BYTES:
        return jsonify({'error': f'File too large for inline editing ({size} bytes)', 'kind': kind, 'size': size}), 413
    try:
        content = target.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return jsonify({'error': 'File is not valid UTF-8 text', 'kind': 'binary'}), 415
    return jsonify({'path': rel, 'kind': kind, 'size': size, 'content': content})


@bp.route('/write-artist-file', methods=['POST'])
def write_artist_file():
    """
    Overwrite a text file inside the artist dir, then trigger compile.
    Body: { "path": "home/content.md", "content": "..." }
    Refuses paths outside the dir, paths in hidden folders, binary files,
    and content that leaks .env secrets into frontend files.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json() or {}
    rel = data.get('path', '')
    content = data.get('content', '')
    if not isinstance(content, str):
        return jsonify({'error': 'content must be a string'}), 400
    if len(content.encode('utf-8')) > FILES_MAX_TEXT_BYTES:
        return jsonify({'error': f'File too large (>{FILES_MAX_TEXT_BYTES} bytes)'}), 413

    artist_path, target = _resolve_artist_file(artist_slug, rel)
    if target is None:
        return jsonify({'error': 'Invalid path'}), 400

    kind = _file_kind(target) if target.exists() else _file_kind(Path(rel))
    if kind in ('binary', 'image'):
        return jsonify({'error': 'Cannot write binary files through this endpoint'}), 415

    # Frontend files never need real secret values — block obvious leaks.
    suffix = target.suffix.lower()
    if suffix in {'.md', '.html', '.htm'}:
        leaked = scan_for_leaked_secrets(artist_slug, content)
        if leaked:
            return jsonify({
                'error': f'BLOCKED: Secret values detected for keys: {", ".join(leaked)}. '
                         f'Secrets must stay in .env / api.py.',
                'leaked_keys': leaked,
            }), 400

    # JSON files: validate before persisting so we never leave broken config on disk.
    if suffix == '.json' and content.strip():
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON: {e.msg} (line {e.lineno}, col {e.colno})'}), 400

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    except OSError as e:
        return jsonify({'error': f'Write failed: {e}'}), 500

    # Recompile so changes show up in published output. Cheap per-artist.
    compile_ok = True
    compile_error = None
    compile_script = Path.cwd() / 'compile.py'
    if compile_script.exists():
        import subprocess
        result = subprocess.run(
            ['python3', str(compile_script), '--artist', artist_slug],
            capture_output=True, text=True,
        )
        compile_ok = result.returncode == 0
        if not compile_ok:
            compile_error = (result.stderr or result.stdout or 'Unknown compile error').strip()

    return jsonify({
        'ok': True,
        'path': rel,
        'kind': kind,
        'size': target.stat().st_size,
        'compile_ok': compile_ok,
        'compile_error': compile_error,
    })


# ── Create Page ────────────────────────────────────────────────────────────

@bp.route('/create-page', methods=['POST'])
def create_page():
    """
    Create a new page for an artist.
    JSON body: {page_slug, title, content?, config?}
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()

    if not data or 'page_slug' not in data or 'title' not in data:
        return jsonify({'error': 'page_slug and title required'}), 400

    page_slug = secure_filename(data['page_slug'])
    page_path = get_page_path(artist_slug, page_slug)

    if page_path.exists():
        return jsonify({'error': 'Page already exists'}), 400

    try:
        # Create page directory
        page_path.mkdir(parents=True, exist_ok=True)

        # Create config.json
        default_config = {
            'title': data['title'],
            'slug': page_slug,
            'description': data.get('description', ''),
            'categories': data.get('categories', [])
        }

        # Merge with provided config
        if 'config' in data:
            default_config.update(data['config'])

        config_file = page_path / 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)

        # Create content.md
        default_content = data.get('content', '<html>\n<h1>New Page</h1>\n<p>Start editing...</p>\n</html>')
        content_file = page_path / 'content.md'
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(default_content)

        # Trigger compile
        compile_script = Path.cwd() / 'compile.py'
        if compile_script.exists():
            import subprocess
            subprocess.run(['python3', str(compile_script), '--artist', artist_slug], check=False)

        return jsonify({
            'success': True,
            'message': 'Page created successfully',
            'page_slug': page_slug,
            'path': str(page_path.relative_to('.'))
        })

    except IOError as e:
        return jsonify({'error': f'Error creating page: {str(e)}'}), 500


@bp.route('/create-nested-page', methods=['POST'])
def create_nested_page():
    """
    Create a new page nested under a parent page directory (e.g. works/wondering-women).
    Body: {parent_slug, child_slug, title, content?, config?, description?}
    Each segment is validated separately so the existing _valid_slug rule still applies.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    parent_slug = data.get('parent_slug', '')
    child_slug = data.get('child_slug', '')
    title = data.get('title', '')

    if not (parent_slug and child_slug and title):
        return jsonify({'error': 'parent_slug, child_slug and title required'}), 400
    if not _valid_slug(parent_slug) or not _valid_slug(child_slug):
        return jsonify({'error': 'Invalid slug'}), 400

    artist_dir = get_artist_path(artist_slug)
    parent_path = artist_dir / parent_slug
    if not parent_path.is_dir():
        return jsonify({'error': f'Parent page "{parent_slug}" not found'}), 404

    page_path = parent_path / child_slug
    if page_path.exists():
        return jsonify({'error': 'Page already exists'}), 400

    try:
        page_path.mkdir(parents=True, exist_ok=True)

        default_config = {
            'title': title,
            'slug': f'artists/{artist_slug}/{parent_slug}/{child_slug}',
            'description': data.get('description', ''),
            'categories': data.get('categories', []),
        }
        if 'config' in data and isinstance(data['config'], dict):
            default_config.update(data['config'])

        (page_path / 'config.json').write_text(
            json.dumps(default_config, indent=4, ensure_ascii=False), encoding='utf-8')

        content = data.get('content', '<html>\n<h1>New Page</h1>\n</html>')
        (page_path / 'content.md').write_text(content, encoding='utf-8')

        compile_script = Path.cwd() / 'compile.py'
        if compile_script.exists():
            import subprocess
            subprocess.run(['python3', str(compile_script), '--artist', artist_slug], check=False)

        return jsonify({
            'success': True,
            'page_slug': f'{parent_slug}/{child_slug}',
            'path': str(page_path.relative_to('.')),
        })
    except IOError as e:
        return jsonify({'error': f'Error creating page: {str(e)}'}), 500


# ── Upload File ────────────────────────────────────────────────────────────

@bp.route('/upload-file', methods=['POST'])
def upload_file():
    """
    Upload a file to an artist's assets directory.
    Form data:
        file       — the upload (required)
        page_slug  — optional; targets pages/<slug>/<page>/assets/ instead
        rel_path   — optional; preserve a folder path under assets/ (e.g. from
                     a folder picker's webkitRelativePath). Disables type-based
                     auto-routing — the file lands exactly where rel_path says.
        extract    — optional; if truthy and the upload is a .zip, unpack it
                     preserving its internal folder tree (into rel_path's dir,
                     or assets root). The archive itself is not kept.
        tags       — optional comma-separated labels (single-file path only).
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    page_slug = request.form.get('page_slug')
    rel_path = request.form.get('rel_path')
    want_extract = request.form.get('extract') in ('1', 'true', 'on', 'yes')
    is_zip = file.filename.lower().endswith('.zip')

    try:
        # ── Zip upload → extract preserving folder tree ──────────────────────
        # Only for the default assets dir (not page-scoped uploads). Members are
        # vetted against the same denylist as direct uploads.
        if is_zip and want_extract and not page_slug:
            dest_prefix = asset_store.safe_rel(rel_path) or ''
            tmp = asset_store.save_temp_upload(file)
            try:
                summary = asset_store.extract_zip(
                    artist_slug, tmp,
                    dest_prefix=dest_prefix,
                    is_allowed=lambda ext: ext not in BLOCKED_EXTENSIONS,
                    uploaded_by='admin',
                )
            except Exception as e:  # noqa: BLE001 — never bare-500 on a bad upload
                logging.exception('zip extract failed')
                return jsonify({'error': f'Could not read that zip: {e}'}), 400
            finally:
                Path(tmp).unlink(missing_ok=True)
            if summary.get('error'):
                return jsonify({'error': summary['error']}), 400
            return jsonify({
                'success': True,
                'extracted': len(summary['stored']),
                'skipped': len(summary['skipped']),
                'truncated': summary['truncated'],
                'paths': summary['stored'],
            })

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        # ── Folder upload (rel_path given) → preserve structure, no routing ──
        if rel_path and not page_slug:
            clean = asset_store.store_fileobj(artist_slug, rel_path, file,
                                              uploaded_by='admin')
            if not clean:
                return jsonify({'error': 'Invalid path'}), 400
            return jsonify({
                'success': True,
                'filename': clean.rsplit('/', 1)[-1],
                'path': clean,
                'url': f'../assets/{clean}',
            })

        # ── Single file → existing type-based auto-routing ───────────────────
        if page_slug:
            upload_dir = get_page_path(artist_slug, page_slug) / 'assets'
        else:
            base_assets = get_artist_path(artist_slug) / 'assets'
            # Route images into assets/images/, fonts into assets/fonts/, rest into assets/
            if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico', 'bmp', 'tiff'):
                upload_dir = base_assets / 'images'
            elif ext in ('woff', 'woff2', 'ttf', 'otf', 'eot'):
                upload_dir = base_assets / 'fonts'
            else:
                upload_dir = base_assets

        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / filename
        file.save(str(file_path))

        # Also copy to output directory so nginx can serve it immediately.
        # Best-effort: some artists' output/ tree is host-owned (compiled on the
        # host) and unwritable from the container — the canonical copy under
        # artists/<slug>/assets still stands, so don't 500 on a mirror failure.
        rel_path = str(file_path.relative_to(get_artist_path(artist_slug) / 'assets')).replace('\\', '/')
        try:
            output_path = Path('output/artists') / artist_slug / 'assets' / rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(file_path), str(output_path))
        except (OSError, PermissionError) as err:
            logging.warning('upload output mirror failed for %s: %s', rel_path, err)

        # Record metadata (optional `tags` form field, comma-separated).
        raw_tags = request.form.get('tags', '')
        tags = [t.strip() for t in raw_tags.split(',') if t.strip()][:32] if raw_tags else []
        asset_meta.update_for(artist_slug, rel_path,
                              tags=tags or None,
                              uploaded_by='admin',
                              uploaded_at=int(_time.time()))

        return jsonify({
            'success': True,
            'filename': filename,
            'path': str(file_path.relative_to('.')),
            'url': f'../assets/{rel_path}'
        })

    except IOError as e:
        return jsonify({'error': f'Error uploading file: {str(e)}'}), 500


@bp.route('/add-link', methods=['POST'])
def add_link_asset():
    """Save a link as an asset (metadata-only, no file on disk).
    Body: {url, notes?}. Title auto-fetched best-effort.
    Headers: X-Artist-Slug, X-Admin-Token."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')
    data = request.get_json() or {}
    url = _normalize_url(data.get('url'))
    if not url:
        return jsonify({'error': 'A URL is required'}), 400
    notes = (data.get('notes') or '')[:2000]
    title = _fetch_link_title(url)
    entry = asset_meta.add_link(artist_slug, url, title=title,
                                notes=notes or None, uploaded_by='admin')
    return jsonify({'success': True, 'item': entry})


# ── Delete Page ────────────────────────────────────────────────────────────

@bp.route('/delete-page', methods=['POST'])
def delete_page():
    """
    Delete a page.
    JSON body: {page_slug}
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()

    if not data or 'page_slug' not in data:
        return jsonify({'error': 'page_slug required'}), 400

    page_slug = data['page_slug']
    page_path = get_page_path(artist_slug, page_slug)

    if not page_path.exists():
        return jsonify({'error': 'Page not found'}), 404

    try:
        shutil.rmtree(page_path)

        # Trigger compile
        compile_script = Path.cwd() / 'compile.py'
        if compile_script.exists():
            import subprocess
            subprocess.run(['python3', str(compile_script), '--artist', artist_slug], check=False)

        return jsonify({
            'success': True,
            'message': 'Page deleted successfully',
            'page_slug': page_slug
        })

    except IOError as e:
        return jsonify({'error': f'Error deleting page: {str(e)}'}), 500


# ── List Assets ────────────────────────────────────────────────────────────

@bp.route('/list-assets', methods=['GET'])
def list_assets():
    """
    List all assets for an artist.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    assets_dir = artist_path / 'assets'

    if not assets_dir.exists():
        return jsonify({'artist': artist_slug, 'assets': []})

    meta_files = asset_meta.load_meta(artist_slug).get('files', {})
    assets = []
    for asset_file in assets_dir.rglob('*'):
        if not asset_file.is_file() or asset_file.name == 'assets.meta.json':
            continue
        relative = asset_file.relative_to(assets_dir)
        if any(part.startswith('.') for part in relative.parts):
            continue
        rel_str = str(relative).replace('\\', '/')
        ext = asset_file.suffix.lower()
        is_image = ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')
        entry = meta_files.get(rel_str, {})
        labels = entry.get('labels') or entry.get('tags') or []
        assets.append({
            'filename': asset_file.name,
            'path': rel_str,
            'url': f'../assets/{rel_str}',
            'size': asset_file.stat().st_size,
            'is_image': is_image,
            'labels': labels,
            'tags': labels,  # back-compat
            'uploaded_by': entry.get('uploaded_by'),
            'uploaded_at': entry.get('uploaded_at'),
            'notes': entry.get('notes', ''),
        })

    assets.sort(key=lambda a: a['filename'])

    # Link assets — metadata-only, no file on disk.
    links = []
    for ln in asset_meta.links_for(artist_slug):
        links.append({
            'filename': ln.get('title') or ln.get('url'),
            'path': ln['path'],
            'kind': 'link',
            'url': ln.get('url'),
            'size': 0,
            'is_image': False,
            'labels': ln.get('labels') or [],
            'tags': ln.get('labels') or [],  # back-compat
            'uploaded_by': ln.get('uploaded_by'),
            'uploaded_at': ln.get('uploaded_at'),
            'notes': ln.get('notes', ''),
        })

    return jsonify({
        'artist': artist_slug,
        'assets': links + assets,
        'labels': asset_meta.all_labels(artist_slug),
        'known_tags': asset_meta.all_tags(artist_slug),  # back-compat
    })


# ── Asset metadata (admin) ─────────────────────────────────────────────────

# ── Intake token (magic-link upload portal) ────────────────────────────────

def _read_artist_config(slug):
    cfg_path = get_artist_path(slug) / 'config.json'
    if not cfg_path.exists():
        abort(404, description='Artist not found')
    return cfg_path, json.loads(cfg_path.read_text())


def _write_artist_config(cfg_path, cfg):
    cfg_path.write_text(json.dumps(cfg, indent=4) + '\n')


@bp.route('/admin/artists/<slug>/intake-token', methods=['GET', 'POST', 'DELETE'])
def admin_intake_token(slug):
    """GET: return the current token (mint one lazily if missing).
    POST: rotate (mint a new one, invalidating any link with the old).
    DELETE: clear the token so the link stops working."""
    from auth import is_admin_token
    import secrets
    token = request.headers.get('X-Admin-Token', '')
    if not is_admin_token(token):
        abort(403)
    cfg_path, cfg = _read_artist_config(slug)
    changed = False
    if request.method == 'DELETE':
        if cfg.pop('intake_token', None) is not None:
            changed = True
        _write_artist_config(cfg_path, cfg)
    else:
        if request.method == 'POST' or not cfg.get('intake_token'):
            cfg['intake_token'] = secrets.token_urlsafe(24)
            _write_artist_config(cfg_path, cfg)
            changed = True
    # Keep the artist's pinned Slack message in sync — the intake link is one
    # of the standard fields it surfaces.
    if changed and cfg.get('slack_channel_id'):
        try:
            from integrations.slack import refresh_pinned
            refresh_pinned(slug)
        except Exception:
            logging.getLogger(__name__).warning(
                'slack refresh_pinned failed for %s', slug, exc_info=True)
    if request.method == 'DELETE':
        return jsonify({'success': True, 'token': None})
    return jsonify({
        'success': True,
        'token': cfg['intake_token'],
        'url': brand_link_base(_artist_workspace(cfg)) + f'/intake/{slug}/{cfg["intake_token"]}',
    })


def _intake_validate(slug, token):
    """Constant-time compare token against the artist's stored intake_token.
    Returns (cfg, artist_dir) or aborts."""
    import hmac
    cfg_path, cfg = _read_artist_config(slug)
    stored = cfg.get('intake_token') or ''
    if not stored or not hmac.compare_digest(stored, token):
        abort(403, description='Invalid intake link')
    return cfg, get_artist_path(slug)


def _brand_substitutions(cfg):
    """Return a dict of {{BRAND_*}} placeholder → value for a given artist config.
    Reused by intake_portal and handover routes."""
    ws = _artist_workspace(cfg)
    brand = brand_json(ws)
    asset_base = f'/api/adze/brand/{ws}/'

    if brand.get('logo_asset'):
        logo_url = f'{asset_base}{brand["logo_asset"]}'
    else:
        logo_url = '/static/ADZE.png'

    if brand.get('favicon_asset'):
        favicon_url = f'{asset_base}{brand["favicon_asset"]}'
    else:
        favicon_url = '/api/adze/favicon.png'

    if brand:
        css_link = f'<link rel="stylesheet" href="{asset_base}brand.css">'
    else:
        css_link = ''

    if brand.get('link_domain'):
        site_url = f'https://{brand["link_domain"]}'
    else:
        site_url = 'https://adze.studio/'

    subs = {
        '{{BRAND_NAME}}': brand.get('name') or 'Adze',
        '{{BRAND_LOGO_URL}}': logo_url,
        '{{BRAND_FAVICON_URL}}': favicon_url,
        '{{BRAND_SUBTITLE}}': (brand.get('intake_subtitle') or brand.get('tagline')
                               or 'Adze · Artist intake portal'),
        '{{BRAND_INTAKE_HEADING}}': (brand.get('intake_heading')
                                     or 'Send your work to {{ARTIST_NAME}}'),
        '{{BRAND_FOOTER}}': 'This link is private to you.',
        '{{BRAND_SITE_URL}}': site_url,
        '{{BRAND_WELCOME_HEADING}}': brand.get('welcome_heading') or 'Welcome to the Adze Studio',
        '{{BRAND_WELCOME_COPY}}': (brand.get('welcome_copy') or
            'Built by Gabriel for friends and the clients of <strong>LastPlace</strong>. '
            'This portal is your way in — drop work above, or sign into the editor to '
            'shape your site directly.'),
        '{{BRAND_CSS_LINK}}': css_link,
    }
    # Brand copy may personalise with {{ARTIST_NAME}} ("Hey Curated London") —
    # resolve it here, since the portal routes replace artist placeholders
    # before brand values are inserted.
    artist_name = cfg.get('name') or cfg.get('slug') or ''
    return {k: v.replace('{{ARTIST_NAME}}', artist_name) for k, v in subs.items()}


# Public portal HTML — token-gated, no admin auth.
@bp.route('/intake/<slug>/<token>')
def intake_portal(slug, token):
    cfg, _ = _intake_validate(slug, token)
    portal_path = Path(__file__).parent / 'intake.html'
    if not portal_path.exists():
        return 'Portal not found', 404
    html = portal_path.read_text(encoding='utf-8')
    subs = {
        '{{ARTIST_NAME}}': cfg.get('name') or slug,
        '{{ARTIST_SLUG}}': slug,
        '{{INTAKE_TOKEN}}': token,
        '{{ADMIN_TOKEN}}': '',
        **_brand_substitutions(cfg),
    }
    for placeholder, value in subs.items():
        html = html.replace(placeholder, value)
    return html, 200, {'Content-Type': 'text/html', 'Cache-Control': 'no-cache'}


def _handover_validate(slug, token):
    """Constant-time compare token against the artist's stored handover_token.
    Returns (cfg, artist_dir) or aborts."""
    import hmac
    cfg_path, cfg = _read_artist_config(slug)
    stored = cfg.get('handover_token') or ''
    if not stored or not hmac.compare_digest(stored, token):
        abort(403, description='Invalid handover link')
    return cfg, get_artist_path(slug)


def _handover_flags(cfg):
    """Return control flags governing what the handover page shows."""
    features = cfg.get('features') or []
    domain = cfg.get('domain') or ''
    has_custom_dashboard = any(f.endswith('_admin') for f in features) and bool(domain)
    handover_cfg = cfg.get('handover') or {}
    return {
        'has_custom_dashboard': has_custom_dashboard,
        'include_adze_login': handover_cfg.get('include_adze_login', True),
        'include_custom_dashboard': handover_cfg.get('include_custom_dashboard', True),
    }


def _strip_domain_scheme(domain):
    """Normalise a domain value that may carry a scheme (e.g. 'https://alfiebruce.com')."""
    d = (domain or '').strip()
    for prefix in ('https://', 'http://', 'www.'):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.rstrip('/')


# Fallback for a custom dashboard whose feature module doesn't describe itself.
DEFAULT_DASHBOARD_INFO = {
    'name': 'Your dashboard',
    'blurb': 'Your day-to-day dashboard for updating your site.',
    'can': [],
}


def _dashboard_info(cfg):
    """A custom dashboard's self-description, for the handover page.

    Any `*_admin` feature module may export `DASHBOARD_INFO = {name, blurb,
    can: [...]}`. The handover route reads it here, so the moment an agent
    builds a new custom dash and gives it a DASHBOARD_INFO, the handover page
    explains it automatically — no per-artist config. Missing fields fall back
    to DEFAULT_DASHBOARD_INFO. Returns None when there is no custom dashboard."""
    import importlib
    features = cfg.get('features') or []
    name = next((f for f in features if f.endswith('_admin')), None)
    if not name:
        return None
    info = dict(DEFAULT_DASHBOARD_INFO)
    try:
        mod = importlib.import_module(f'features.{name}')
        custom = getattr(mod, 'DASHBOARD_INFO', None)
        if isinstance(custom, dict):
            info.update({k: v for k, v in custom.items() if k in info})
    except Exception:
        pass
    return info


@bp.route('/handover/<slug>/<token>')
def handover_portal(slug, token):
    """Public handover page — carries editor credentials + intake link."""
    cfg, _ = _handover_validate(slug, token)
    handover_path = Path(__file__).parent / 'handover.html'
    if not handover_path.exists():
        return 'Handover page not found', 404
    html = handover_path.read_text(encoding='utf-8')
    ws = _artist_workspace(cfg)
    brand = brand_json(ws)
    intake_url = (f'/intake/{slug}/{cfg["intake_token"]}'
                  if cfg.get('intake_token') else '')
    flags = _handover_flags(cfg)
    if flags['has_custom_dashboard'] and flags['include_custom_dashboard']:
        show_custom_dash = 'true'
    else:
        show_custom_dash = 'false'
    if flags['has_custom_dashboard']:
        custom_dash_url = f'https://{_strip_domain_scheme(cfg.get("domain"))}/admin'
        dash_info = _dashboard_info(cfg)
    else:
        custom_dash_url = ''
        dash_info = None
    subs = {
        '{{ARTIST_NAME}}': cfg.get('name') or slug,
        '{{ARTIST_SLUG}}': slug,
        '{{ADMIN_TOKEN}}': cfg.get('admin_token') or '',
        '{{DOMAIN}}': cfg.get('domain') or '',
        '{{INTAKE_URL}}': intake_url,
        '{{CONTACT_EMAIL}}': brand.get('contact_email') or 'hello@adze.studio',
        '{{HOW_IT_WORKS}}': (brand.get('how_it_works') or
            'Your site is built and managed by Adze. '
            'Use the details below to sign into your editor.'),
        '{{SHOW_CUSTOM_DASH}}': show_custom_dash,
        '{{SHOW_ADZE_LOGIN}}': 'true' if flags['include_adze_login'] else 'false',
        '{{CUSTOM_DASH_URL}}': custom_dash_url,
        '{{DASH_INFO_JSON}}': json.dumps(dash_info),
        '{{PASSWORD_CHANGED}}': 'true' if cfg.get('password_changed') else 'false',
        '{{HANDOVER_PW_URL}}': f'/api/adze/handover/{slug}/{token}/password',
        **_brand_substitutions(cfg),
    }
    for placeholder, value in subs.items():
        html = html.replace(placeholder, value)
    return html, 200, {'Content-Type': 'text/html', 'Cache-Control': 'no-cache'}


HANDOVER_MIN_PASSWORD_LEN = 6


@bp.route('/handover/<slug>/<token>/password', methods=['POST'])
def handover_set_password(slug, token):
    """One-time password change from the handover page, for any artist.

    Authed by possession of the handover link (same token as the page itself).
    Replaces `admin_token` — the single credential for both the custom dashboard
    and the Adze editor — and locks via a `password_changed` flag so it's a
    deliberate one-time action. A super-admin can clear the flag to allow
    another change."""
    cfg, _ = _handover_validate(slug, token)
    if cfg.get('password_changed'):
        return jsonify({'error': 'Your password has already been changed.'}), 409
    body = request.get_json(silent=True) or {}
    new = (body.get('new_password') or '').strip()
    confirm = (body.get('confirm') or '').strip()
    if len(new) < HANDOVER_MIN_PASSWORD_LEN:
        return jsonify({'error': f'Password must be at least {HANDOVER_MIN_PASSWORD_LEN} characters.'}), 400
    if new != confirm:
        return jsonify({'error': 'The two passwords do not match.'}), 400
    cfg_path = get_artist_path(slug) / 'config.json'
    cfg['admin_token'] = new
    cfg['password_changed'] = True
    _write_artist_config(cfg_path, cfg)
    return jsonify({'ok': True, 'password': new})


@bp.route('/admin/artists/<slug>/handover-token', methods=['GET', 'POST', 'DELETE'])
def admin_handover_token(slug):
    """GET: return the current token (mint one lazily if missing).
    POST: rotate (mint a new one, invalidating any link with the old).
    DELETE: clear the token so the link stops working."""
    import secrets
    # Header-or-cookie auth so cookie-only sessions (workspace subdomains) work.
    _require_super_admin()
    cfg_path, cfg = _read_artist_config(slug)
    if request.method == 'DELETE':
        cfg.pop('handover_token', None)
        _write_artist_config(cfg_path, cfg)
        return jsonify({'success': True, 'token': None})
    if request.method == 'POST' or not cfg.get('handover_token'):
        cfg['handover_token'] = secrets.token_urlsafe(24)
        _write_artist_config(cfg_path, cfg)
    flags = _handover_flags(cfg)
    return jsonify({
        'success': True,
        'token': cfg['handover_token'],
        'url': brand_link_base(_artist_workspace(cfg)) + f'/handover/{slug}/{cfg["handover_token"]}',
        'config': {
            'include_adze_login': flags['include_adze_login'],
            'include_custom_dashboard': flags['include_custom_dashboard'],
        },
        'has_custom_dashboard': flags['has_custom_dashboard'],
    })


@bp.route('/admin/artists/<slug>/handover-config', methods=['POST'])
def admin_handover_config(slug):
    """Persist optional booleans controlling what the handover page shows."""
    from auth import is_admin_token
    token = request.headers.get('X-Admin-Token', '')
    if not is_admin_token(token):
        abort(403)
    cfg_path, cfg = _read_artist_config(slug)
    body = request.get_json(silent=True) or {}
    handover = cfg.get('handover') or {}
    for key in ('include_adze_login', 'include_custom_dashboard'):
        if key in body and isinstance(body[key], bool):
            handover[key] = body[key]
    cfg['handover'] = handover
    _write_artist_config(cfg_path, cfg)
    flags = _handover_flags(cfg)
    return jsonify({
        'success': True,
        'config': {
            'include_adze_login': flags['include_adze_login'],
            'include_custom_dashboard': flags['include_custom_dashboard'],
        },
    })


# Allowed intake MIME types — narrower than the admin's allowlist; artists
# send finished work, not source code.
_INTAKE_ALLOWED_EXT = {
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'heic', 'tiff', 'bmp',
    'mp4', 'mov', 'webm',
    'mp3', 'wav', 'm4a', 'aac', 'flac',
    'pdf',
}
_INTAKE_MAX_BYTES = 1024 * 1024 * 1024   # 1 GB per file (zips/folders can be large)
_INTAKE_MAX_TOTAL = 20 * 1024 * 1024 * 1024  # 20 GB per artist via intake


def _normalize_url(raw):
    """Trim and ensure a scheme. Bare 'example.com/x' becomes https://….
    Returns '' if there's nothing usable."""
    url = (raw or '').strip()
    if not url:
        return ''
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.\-]*://', url):
        url = 'https://' + url
    return url[:2000]


def _url_is_public(url):
    """SSRF guard for the optional title-fetch: http(s) only, and every
    resolved address must be public. We still *store* any URL — this only
    gates whether the server makes an outbound request to it."""
    from urllib.parse import urlparse
    import ipaddress
    try:
        p = urlparse(url)
    except ValueError:
        return False
    if p.scheme not in ('http', 'https') or not p.hostname:
        return False
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False
    return True


def _fetch_link_title(url):
    """Best-effort fetch of a page's <title>. Returns None on any failure
    (timeout, non-HTML, private address, parse miss). Never raises."""
    if not _url_is_public(url):
        return None
    try:
        import urllib.request
        import html as _html
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AdzeIntake/1.0)'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            ctype = (resp.headers.get('Content-Type') or '').lower()
            if ctype and 'html' not in ctype:
                return None
            raw = resp.read(200_000).decode('utf-8', 'ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.IGNORECASE | re.DOTALL)
        if m:
            title = _html.unescape(m.group(1)).strip()
            return title[:300] or None
    except Exception:
        return None
    return None


def _intake_total_bytes(artist_dir):
    intake_root = artist_dir / 'assets' / 'intake'
    if not intake_root.exists():
        return 0
    return sum(f.stat().st_size for f in intake_root.rglob('*') if f.is_file())


@bp.route('/intake/<slug>/<token>/assets', methods=['GET'])
def intake_list_assets(slug, token):
    """List what's been uploaded via this token. Public, but token-gated."""
    cfg, artist_dir = _intake_validate(slug, token)
    meta_files = asset_meta.load_meta(slug).get('files', {})
    intake_dir = artist_dir / 'assets' / 'intake'
    items = []
    if intake_dir.exists():
        for p in intake_dir.rglob('*'):
            if p.is_file():
                rel = str(p.relative_to(artist_dir / 'assets')).replace('\\', '/')
                ext = p.suffix.lower()
                is_image = ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.heic')
                entry = meta_files.get(rel, {})
                labels = entry.get('labels') or entry.get('tags') or []
                items.append({
                    'filename': p.name,
                    'path': rel,
                    'url': f'/intake/{slug}/{token}/file/{rel}',
                    'size': p.stat().st_size,
                    'is_image': is_image,
                    'labels': labels,
                    'tags': labels,  # back-compat
                    'notes': entry.get('notes', ''),
                    'uploaded_at': entry.get('uploaded_at'),
                })
    # Link assets — metadata-only entries, no file on disk.
    for ln in asset_meta.links_for(slug):
        items.append({
            'filename': ln.get('title') or ln.get('url'),
            'path': ln['path'],
            'kind': 'link',
            'url': ln.get('url'),
            'size': 0,
            'is_image': False,
            'labels': ln.get('labels') or [],
            'tags': ln.get('labels') or [],  # back-compat
            'notes': ln.get('notes', ''),
            'uploaded_at': ln.get('uploaded_at'),
        })
    items.sort(key=lambda a: -(a.get('uploaded_at') or 0))
    return jsonify({
        'artist_name': cfg.get('name') or slug,
        'artist_slug': slug,
        'items': items,
        'labels': asset_meta.all_labels(slug),
        'known_tags': asset_meta.all_tags(slug),  # back-compat
    })


@bp.route('/intake/<slug>/<token>/file/<path:rel>')
def intake_serve_file(slug, token, rel):
    """Serve a file the artist uploaded so they can preview it back."""
    _, artist_dir = _intake_validate(slug, token)
    target = (artist_dir / 'assets' / rel).resolve()
    assets_root = (artist_dir / 'assets').resolve()
    if not str(target).startswith(str(assets_root)) or not target.is_file():
        abort(404)
    return send_file(str(target))


@bp.route('/intake/<slug>/<token>/upload', methods=['POST'])
def intake_upload(slug, token):
    """Accept a file from the artist's intake portal.

    Beyond single files, supports:
      - `rel_path` form field — preserve a folder path (from a folder picker);
        the file lands under `intake/<rel_path>` keeping the structure.
      - a `.zip` upload — unpacked under `intake/<zip-name>/` preserving its
        internal folder tree. Members are vetted against the same intake
        allowlist; the archive itself is discarded.
    Everything stays under `intake/` so the portal's delete/label boundary
    (which only touches `intake/` paths) still holds.
    """
    cfg, artist_dir = _intake_validate(slug, token)
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'No file selected'}), 400
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    is_zip = ext == 'zip'
    if not is_zip and ext not in _INTAKE_ALLOWED_EXT:
        return jsonify({'error': f'File type .{ext} not accepted via intake'}), 400

    # Check size after save (Werkzeug doesn't reliably expose content length
    # for multipart parts until consumed).
    used = _intake_total_bytes(artist_dir)
    if used >= _INTAKE_MAX_TOTAL:
        return jsonify({'error': 'Intake storage cap reached. Contact your admin.'}), 413

    intake_dir = artist_dir / 'assets' / 'intake'
    intake_dir.mkdir(parents=True, exist_ok=True)
    rel_path_field = request.form.get('rel_path')

    # ── Zip upload → extract under intake/<zip-name>/ preserving the tree ────
    if is_zip:
        stem = secure_filename(f.filename.rsplit('.', 1)[0]) or 'archive'
        sub = asset_store.safe_rel(rel_path_field) if rel_path_field else stem
        dest_prefix = f'intake/{sub or stem}'
        tmp = asset_store.save_temp_upload(f)
        try:
            summary = asset_store.extract_zip(
                slug, tmp,
                dest_prefix=dest_prefix,
                is_allowed=lambda e: e in _INTAKE_ALLOWED_EXT,
                uploaded_by=f'intake:{slug}',
                max_total_bytes=_INTAKE_MAX_TOTAL - used,
            )
        except Exception as e:  # noqa: BLE001 — bad upload is a 400, not a 500
            logging.exception('intake zip extract failed')
            return jsonify({'error': f'Could not read that zip: {e}'}), 400
        finally:
            Path(tmp).unlink(missing_ok=True)
        if summary.get('error'):
            return jsonify({'error': summary['error']}), 400
        if not summary['stored']:
            return jsonify({'error': 'Nothing usable in that zip (only allowed '
                                     'media types are kept).'}), 400
        return jsonify({
            'success': True,
            'extracted': len(summary['stored']),
            'skipped': len(summary['skipped']),
            'truncated': summary['truncated'],
            'paths': summary['stored'],
        })

    # ── Folder upload (rel_path given) → preserve structure under intake/ ────
    if rel_path_field:
        clean = asset_store.store_fileobj(
            slug, f'intake/{rel_path_field}', f,
            uploaded_by=f'intake:{slug}')
        if not clean:
            return jsonify({'error': 'Invalid path'}), 400
        target = artist_dir / 'assets' / clean
        if target.stat().st_size > _INTAKE_MAX_BYTES:
            target.unlink(missing_ok=True)
            asset_meta.delete_for(slug, clean)
            return jsonify({'error': f'File exceeds {_INTAKE_MAX_BYTES // (1024*1024)} MB limit'}), 413
        return jsonify({'success': True, 'filename': clean.rsplit('/', 1)[-1],
                        'path': clean, 'size': target.stat().st_size})

    # UUID-prefixed filename to prevent collisions and to make filenames opaque.
    import secrets as _sec
    safe_base = secure_filename(f.filename) or f'upload.{ext}'
    final_name = f'{_sec.token_hex(4)}_{safe_base}'
    target = intake_dir / final_name
    f.save(str(target))

    if target.stat().st_size > _INTAKE_MAX_BYTES:
        target.unlink(missing_ok=True)
        return jsonify({'error': f'File exceeds {_INTAKE_MAX_BYTES // (1024*1024)} MB limit'}), 413

    rel_path = f'intake/{final_name}'
    # Mirror to output so nginx can serve the file as part of the live site.
    # This is best-effort: if the output dir is unwritable from the container
    # (host-owned), we still keep the canonical copy under artists/<slug>/assets.
    try:
        out = Path('output/artists') / slug / 'assets' / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(target), str(out))
    except (OSError, PermissionError) as err:
        logging.warning('Intake output mirror failed for %s: %s', rel_path, err)

    raw_tags = request.form.get('tags', '')
    tags = [t.strip() for t in raw_tags.split(',') if t.strip()][:32] if raw_tags else []
    notes = (request.form.get('notes') or '')[:2000]
    asset_meta.update_for(slug, rel_path,
                          tags=tags or None,
                          uploaded_by=f'intake:{slug}',
                          uploaded_at=int(_time.time()),
                          notes=notes or None)

    return jsonify({
        'success': True,
        'filename': final_name,
        'path': rel_path,
        'size': target.stat().st_size,
    })


@bp.route('/intake/<slug>/<token>/link', methods=['POST'])
def intake_add_link(slug, token):
    """Save a link as an asset from the intake portal. Body: {url, notes?}.
    Title is auto-fetched best-effort; the artist can relabel/rename later."""
    _intake_validate(slug, token)
    data = request.get_json() or {}
    url = _normalize_url(data.get('url'))
    if not url:
        return jsonify({'error': 'A URL is required'}), 400
    notes = (data.get('notes') or '')[:2000]
    title = _fetch_link_title(url)
    entry = asset_meta.add_link(slug, url, title=title, notes=notes or None,
                                uploaded_by=f'intake:{slug}')
    return jsonify({'success': True, 'item': entry})


@bp.route('/intake/<slug>/<token>/file/<path:rel>', methods=['DELETE'])
def intake_delete_file(slug, token, rel):
    """Remove a file the artist uploaded via the intake portal. Restricted to
    files under `assets/intake/` (or `link:` metadata-only entries) — the
    portal can't touch anything else."""
    _, artist_dir = _intake_validate(slug, token)
    if asset_meta.is_link_key(rel):
        asset_meta.delete_for(slug, rel)
        return jsonify({'success': True})
    if not rel.startswith('intake/'):
        return jsonify({'error': 'Only intake/ files can be removed via this endpoint'}), 400
    base = (artist_dir / 'assets').resolve()
    target = (base / rel).resolve()
    if not str(target).startswith(str(base)) or not target.is_file():
        return jsonify({'error': 'File not found'}), 404
    target.unlink()
    # Also remove the mirror in output/ if present (best-effort).
    out = Path('output/artists') / slug / 'assets' / rel
    try:
        if out.is_file():
            out.unlink()
    except OSError:
        pass
    asset_meta.delete_for(slug, rel)
    return jsonify({'success': True})


@bp.route('/intake/<slug>/<token>/labels', methods=['GET', 'POST'])
def intake_labels(slug, token):
    """GET: list labels with colors + counts.
    POST: create or upsert a label {name, color?}."""
    _intake_validate(slug, token)
    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            lbl = asset_meta.create_label(slug, data.get('name'), data.get('color'))
        except ValueError as err:
            return jsonify({'error': str(err)}), 400
        return jsonify({'success': True, 'label': lbl})
    return jsonify({'labels': asset_meta.all_labels(slug)})


@bp.route('/intake/<slug>/<token>/labels/<name>', methods=['DELETE'])
def intake_delete_label(slug, token, name):
    _intake_validate(slug, token)
    asset_meta.delete_label(slug, name)
    return jsonify({'success': True})


@bp.route('/intake/<slug>/<token>/apply-labels', methods=['POST'])
def intake_apply_labels(slug, token):
    """Bulk add/remove a label on many files. Body:
        {paths: [...], label: "Sculpture", on: true|false (default true)}.
    Files must be under intake/ for safety."""
    _intake_validate(slug, token)
    data = request.get_json() or {}
    label = (data.get('label') or '').strip()
    paths = [p for p in (data.get('paths') or [])
             if str(p).startswith('intake/') or asset_meta.is_link_key(p)]
    on = data.get('on', True)
    if not label or not paths:
        return jsonify({'error': 'label and at least one intake/ path required'}), 400
    asset_meta.toggle_labels(slug, paths, label, on=on)
    return jsonify({'success': True, 'count': len(paths)})


@bp.route('/intake/<slug>/<token>/meta', methods=['PATCH'])
def intake_update_meta(slug, token):
    """Update tags/notes on an existing intake upload. Only files under
    `assets/intake/` are touchable via this endpoint."""
    _intake_validate(slug, token)
    data = request.get_json() or {}
    rel = (data.get('path') or '').strip()
    if not rel.startswith('intake/') and not asset_meta.is_link_key(rel):
        return jsonify({'error': 'Can only update intake uploads'}), 400
    fields = {}
    if 'tags' in data:
        tags = data.get('tags') or []
        fields['tags'] = [str(t).strip() for t in tags if str(t).strip()][:32]
    if 'notes' in data:
        fields['notes'] = (data.get('notes') or '')[:2000]
    asset_meta.update_for(slug, rel, **fields)
    return jsonify({'success': True})


def _check_label_access(slug):
    """Either super-admin or the artist's own per-artist token.
    Returns True or aborts 403."""
    from auth import is_admin_token, get_artist_config
    token = request.headers.get('X-Admin-Token', '')
    if is_admin_token(token):
        return True
    cfg = get_artist_config(slug) if slug else None
    if cfg and cfg.get('admin_token') == token:
        return True
    abort(403)


@bp.route('/admin/artists/<slug>/labels', methods=['GET', 'POST'])
def admin_labels(slug):
    """GET: list labels with colors + counts. POST: create/upsert {name, color?}.
    Allows either super-admin or the artist's own token, so the artist
    dashboard and admin both call this."""
    _check_label_access(slug)
    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            lbl = asset_meta.create_label(slug, data.get('name'), data.get('color'))
        except ValueError as err:
            return jsonify({'error': str(err)}), 400
        return jsonify({'success': True, 'label': lbl})
    return jsonify({'labels': asset_meta.all_labels(slug)})


@bp.route('/admin/artists/<slug>/labels/<name>', methods=['DELETE'])
def admin_delete_label(slug, name):
    _check_label_access(slug)
    asset_meta.delete_label(slug, name)
    return jsonify({'success': True})


@bp.route('/admin/artists/<slug>/apply-labels', methods=['POST'])
def admin_apply_labels(slug):
    """Bulk add/remove a label on many files. Body:
        {paths: [...], label: "Name", on: true|false}.
    Unlike the intake variant, admin can label any file under the artist's
    assets dir, not just intake/."""
    _check_label_access(slug)
    data = request.get_json() or {}
    label = (data.get('label') or '').strip()
    paths = list(data.get('paths') or [])
    on = data.get('on', True)
    if not label or not paths:
        return jsonify({'error': 'label and at least one path required'}), 400
    asset_meta.toggle_labels(slug, paths, label, on=on)
    return jsonify({'success': True, 'count': len(paths)})


@bp.route('/asset-thumb/<slug>/<path:rel>')
def admin_asset_thumb(slug, rel):
    """Serve a raw asset file to the admin/dashboard UI.

    Auth: admin token (header X-Admin-Token, query ?t=, or adze_admin_session
    cookie), OR the artist's own session (adze_session cookie or
    X-Artist-Slug + X-Admin-Token with the artist's token).  The URL slug
    must match the authenticated artist."""
    from auth import is_admin_token, get_authenticated_artist
    # Admin path: explicit token in header / query / old admin_session cookie.
    token = (request.headers.get('X-Admin-Token', '')
             or request.cookies.get('admin_session', '')
             or request.cookies.get('adze_admin_session', '')
             or request.args.get('t', ''))
    authed = is_admin_token(token)
    if not authed:
        # Artist path: the authenticated artist must own this slug.
        authed_slug = get_authenticated_artist()
        authed = (authed_slug == slug)
    if not authed:
        abort(403)
    base = get_artist_path(slug) / 'assets'
    target = (base / rel).resolve()
    if not str(target).startswith(str(base.resolve())) or not target.is_file():
        abort(404)
    return send_file(str(target), max_age=300)


@bp.route('/admin/artists/<slug>/asset-meta', methods=['PATCH'])
def admin_set_asset_meta(slug):
    """Update metadata for a single asset. Body: {path, tags?, notes?}."""
    from auth import is_admin_token
    token = request.headers.get('X-Admin-Token', '')
    if not is_admin_token(token):
        abort(403)
    data = request.get_json() or {}
    rel = (data.get('path') or '').strip()
    if not rel:
        return jsonify({'error': 'path required'}), 400
    fields = {}
    if 'tags' in data:
        tags = data.get('tags') or []
        if not isinstance(tags, list):
            return jsonify({'error': 'tags must be a list'}), 400
        fields['tags'] = [str(t).strip() for t in tags if str(t).strip()][:32]
    if 'notes' in data:
        fields['notes'] = (data.get('notes') or '')[:2000]
    asset_meta.update_for(slug, rel, **fields)
    return jsonify({'success': True})


@bp.route('/download-assets', methods=['POST'])
def download_assets():
    """Stream a zip of the requested asset paths. Body: {paths:[...]}.
    Single file → served as-is; multiple files → zipped in memory."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    paths = data.get('paths', [])
    if not paths:
        return jsonify({'error': 'No paths provided'}), 400

    artist_path = get_artist_path(artist_slug)
    assets_dir = artist_path / 'assets'
    assets_root = assets_dir.resolve()

    # Resolve + safety-check every path before opening the response.
    files = []
    for p in paths:
        try:
            target = (assets_dir / p).resolve()
            target.relative_to(assets_root)
        except (ValueError, Exception):
            continue
        if target.is_file():
            files.append((p, target))

    if not files:
        return jsonify({'error': 'No valid files found'}), 404

    # Single file → direct download, original filename.
    if len(files) == 1:
        p, target = files[0]
        return send_file(str(target), as_attachment=True, download_name=target.name)

    # Multiple → in-memory zip.
    import io, zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel, target in files:
            zf.write(str(target), arcname=rel)
    buf.seek(0)
    ts = _time.strftime('%Y%m%d-%H%M%S')
    return send_file(
        buf, mimetype='application/zip', as_attachment=True,
        download_name=f'{artist_slug}-assets-{ts}.zip',
    )


@bp.route('/rename-asset', methods=['POST'])
def rename_asset():
    """
    Rename a single asset within its current directory.
    Body: { "path": "subdir/old.jpg", "new_name": "new.jpg" }
    new_name is a basename only — directory is preserved.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    path = (data.get('path') or '').strip()
    new_name = (data.get('new_name') or '').strip()
    if not path or not new_name:
        return jsonify({'error': 'path and new_name required'}), 400
    if '/' in new_name or '\\' in new_name or new_name in ('.', '..'):
        return jsonify({'error': 'new_name must be a bare filename'}), 400

    artist_path = get_artist_path(artist_slug)
    assets_root = (artist_path / 'assets').resolve()

    try:
        src = (assets_root / path).resolve()
        src.relative_to(assets_root)
    except (ValueError, Exception):
        return jsonify({'error': 'invalid path'}), 400
    if not src.is_file():
        return jsonify({'error': 'not found'}), 404

    dst = src.parent / new_name
    if dst.exists():
        return jsonify({'error': 'a file with that name already exists'}), 409

    src.rename(dst)
    new_rel = str(dst.relative_to(assets_root))

    # Move the output mirror too, so nginx serves the renamed file.
    try:
        out_dir = Path('output/artists') / artist_slug / 'assets'
        out_src = out_dir / path
        out_dst = out_dir / new_rel
        if out_src.is_file():
            out_dst.parent.mkdir(parents=True, exist_ok=True)
            out_src.rename(out_dst)
    except OSError:
        pass

    asset_meta.rename_for(artist_slug, path, new_rel)
    return jsonify({'old_path': path, 'new_path': new_rel, 'filename': new_name})


@bp.route('/delete-assets', methods=['POST'])
def delete_assets():
    """
    Delete one or more assets.
    Body: { "paths": ["image.jpg", "subdir/file.pdf"] }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()
    paths = data.get('paths', [])
    if not paths:
        return jsonify({'error': 'No paths provided'}), 400

    artist_path = get_artist_path(artist_slug)
    assets_dir = artist_path / 'assets'
    deleted, errors = [], []

    for p in paths:
        # Link assets are metadata-only — no file to unlink.
        if asset_meta.is_link_key(p):
            asset_meta.delete_for(artist_slug, p)
            deleted.append(p)
            continue
        # Prevent path traversal
        try:
            target = (assets_dir / p).resolve()
            target.relative_to(assets_dir.resolve())
        except (ValueError, Exception):
            errors.append(f'{p}: invalid path')
            continue
        if target.exists() and target.is_file():
            target.unlink()
            # Best-effort: also remove the output mirror so nginx stops serving it.
            try:
                out = Path('output/artists') / artist_slug / 'assets' / p
                if out.is_file():
                    out.unlink()
            except OSError:
                pass
            asset_meta.delete_for(artist_slug, p)
            deleted.append(p)
        else:
            errors.append(f'{p}: not found')

    return jsonify({'deleted': deleted, 'errors': errors})


# ── Inbox (contact form submissions) ──────────────────────────────────────

@bp.route('/contact', methods=['POST'])
def public_contact():
    """
    Public endpoint — no auth. Accept a contact form submission and store it.
    Body: { artist_slug, name, email, subject?, message }
    """
    _rate_limit('contact', 20, 60)  # 20 submissions per minute per IP
    import time, uuid
    data = request.get_json(silent=True) or {}
    slug    = data.get('artist_slug', '').strip()
    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not slug or not message or not email:
        return jsonify({'error': 'artist_slug, email and message are required'}), 400

    artist_path = get_artist_path(slug)
    if not artist_path.exists():
        return jsonify({'error': 'Artist not found'}), 404

    submission = {
        'id':      str(uuid.uuid4()),
        'name':    name,
        'email':   email,
        'subject': subject,
        'message': message,
        'read':    False,
        'ts':      int(time.time()),
    }

    sub_file = artist_path / 'submissions.json'
    submissions = []
    if sub_file.exists():
        try:
            submissions = json.loads(sub_file.read_text())
        except Exception:
            submissions = []
    submissions.insert(0, submission)
    sub_file.write_text(json.dumps(submissions, indent=2))
    return jsonify({'success': True}), 201


@bp.route('/list-submissions', methods=['GET'])
def list_submissions():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    sub_file = get_artist_path(artist_slug) / 'submissions.json'
    submissions = []
    if sub_file.exists():
        try:
            submissions = json.loads(sub_file.read_text())
        except Exception:
            pass
    return jsonify({'submissions': submissions})


@bp.route('/delete-submission', methods=['POST'])
def delete_submission():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json(silent=True) or {}
    sid = data.get('id', '')
    sub_file = get_artist_path(artist_slug) / 'submissions.json'
    if sub_file.exists():
        try:
            submissions = json.loads(sub_file.read_text())
            submissions = [s for s in submissions if s.get('id') != sid]
            sub_file.write_text(json.dumps(submissions, indent=2))
        except Exception:
            pass
    return jsonify({'success': True})


@bp.route('/mark-submission-read', methods=['POST'])
def mark_submission_read():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json(silent=True) or {}
    sid  = data.get('id', '')
    read = data.get('read', True)
    sub_file = get_artist_path(artist_slug) / 'submissions.json'
    if sub_file.exists():
        try:
            submissions = json.loads(sub_file.read_text())
            for s in submissions:
                if s.get('id') == sid:
                    s['read'] = read
            sub_file.write_text(json.dumps(submissions, indent=2))
        except Exception:
            pass
    return jsonify({'success': True})


# ── Subscribers (mailing list) ─────────────────────────────────────────────

@bp.route('/subscribe', methods=['POST'])
def public_subscribe():
    """
    Public endpoint — no auth. Add an email to the artist's subscriber list.
    Body: { artist_slug, email, name? }
    """
    _rate_limit('subscribe', 20, 60)  # 20 signups per minute per IP
    import time
    data  = request.get_json(silent=True) or {}
    slug  = data.get('artist_slug', '').strip()
    email = data.get('email', '').strip().lower()
    name  = data.get('name', '').strip()

    if not slug or not email or '@' not in email:
        return jsonify({'error': 'Valid artist_slug and email are required'}), 400

    artist_path = get_artist_path(slug)
    if not artist_path.exists():
        return jsonify({'error': 'Artist not found'}), 404

    sub_file = artist_path / 'subscribers.json'
    subscribers = []
    if sub_file.exists():
        try:
            subscribers = json.loads(sub_file.read_text())
        except Exception:
            pass

    # Prevent duplicates
    if any(s.get('email', '').lower() == email for s in subscribers):
        return jsonify({'success': True, 'already_subscribed': True})

    subscribers.append({'email': email, 'name': name, 'ts': int(time.time())})
    sub_file.write_text(json.dumps(subscribers, indent=2))
    return jsonify({'success': True}), 201


@bp.route('/list-subscribers', methods=['GET'])
def list_subscribers():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    sub_file = get_artist_path(artist_slug) / 'subscribers.json'
    subscribers = []
    if sub_file.exists():
        try:
            subscribers = json.loads(sub_file.read_text())
        except Exception:
            pass
    return jsonify({'subscribers': subscribers, 'count': len(subscribers)})


@bp.route('/delete-subscriber', methods=['POST'])
def delete_subscriber():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').lower()
    sub_file = get_artist_path(artist_slug) / 'subscribers.json'
    if sub_file.exists():
        try:
            subscribers = json.loads(sub_file.read_text())
            subscribers = [s for s in subscribers if s.get('email', '').lower() != email]
            sub_file.write_text(json.dumps(subscribers, indent=2))
        except Exception:
            pass
    return jsonify({'success': True})


@bp.route('/export-subscribers', methods=['GET'])
def export_subscribers():
    """Export subscriber list as CSV."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    import io, csv as csv_mod
    from flask import Response
    sub_file = get_artist_path(artist_slug) / 'subscribers.json'
    subscribers = []
    if sub_file.exists():
        try:
            subscribers = json.loads(sub_file.read_text())
        except Exception:
            pass
    output = io.StringIO()
    writer = csv_mod.writer(output)
    writer.writerow(['email', 'name', 'subscribed'])
    for s in subscribers:
        from datetime import datetime
        ts = datetime.fromtimestamp(s.get('ts', 0)).strftime('%Y-%m-%d') if s.get('ts') else ''
        writer.writerow([s.get('email', ''), s.get('name', ''), ts])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={artist_slug}-subscribers.csv'}
    )


# ── Artist Info ────────────────────────────────────────────────────────────

@bp.route('/artist-info', methods=['GET'])
def artist_info():
    """
    Get info about the authenticated artist.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()

    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    config_file = artist_path / 'config.json'

    if not config_file.exists():
        return jsonify({'error': 'Artist config not found'}), 404

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Don't expose the admin token
        config.pop('admin_token', None)

        return jsonify({
            'slug': artist_slug,
            'config': config
        })

    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': f'Error reading config: {str(e)}'}), 500


# ── Update Domain ─────────────────────────────────────────────────────────

@bp.route('/update-domain', methods=['POST'])
def update_domain():
    """
    Update the domain field in an artist's config.json.
    Body: { "domain": "example.com" }
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()
    domain = (data.get('domain') or '').strip().lower()

    artist_path = get_artist_path(artist_slug)
    config_file = artist_path / 'config.json'

    if not config_file.exists():
        return jsonify({'error': 'Artist config not found'}), 404

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config['domain'] = domain

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        return jsonify({'success': True, 'domain': domain})
    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': f'Error updating config: {str(e)}'}), 500


# ── Activate Domain (nginx config + SSL) ──────────────────────────────────

NGINX_TEMPLATE = """server {{
    server_name {domain} www.{domain};

    root /home/gabriel/adze/output/artists/{slug};

    location /assets/ {{
        alias /home/gabriel/adze/output/artists/{slug}/assets/;
        expires 24h;
        add_header Cache-Control "public, max-age=86400";
    }}

    location /api/ {{
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        client_max_body_size 50M;
    }}

    location / {{
        try_files $uri $uri/ @api;
    }}

    location @api {{
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    listen 80;
    listen [::]:80;
}}"""


@bp.route('/activate-domain', methods=['POST'])
def activate_domain():
    """
    Write nginx config for an artist's custom domain and activate SSL.
    Body: { "domain": "example.com" }

    Flask runs in Docker so it can't call systemctl or certbot directly.
    This endpoint writes the nginx config to the repo (accessible on the host)
    and returns the commands to run on the server to complete setup.
    """
    import re as _re

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()
    domain = (data.get('domain') or '').strip().lower()

    if not domain:
        return jsonify({'error': 'Domain is required'}), 400

    if not _re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$', domain):
        return jsonify({'error': 'Invalid domain format'}), 400

    if '..' in domain or '/' in domain:
        return jsonify({'error': 'Invalid domain'}), 400

    email = os.environ.get('CERTBOT_EMAIL', 'gabrielpenman@gmail.com')

    try:
        # Write nginx config to the repo — readable from the host
        conf_dir = Path(__file__).parent.parent / 'nginx' / 'sites-available'
        conf_dir.mkdir(parents=True, exist_ok=True)
        conf_path = conf_dir / domain
        conf_path.write_text(NGINX_TEMPLATE.format(domain=domain, slug=artist_slug))

        # Update config.json
        artist_path = get_artist_path(artist_slug)
        config_file = artist_path / 'config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['domain'] = domain
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

        # Return the commands needed on the host to activate nginx + SSL
        host_conf = f'/etc/nginx/sites-available/{domain}'
        repo_conf = f'/home/gabriel/adze/nginx/sites-available/{domain}'
        commands = (
            f'sudo cp {repo_conf} {host_conf} && '
            f'sudo ln -sf {host_conf} /etc/nginx/sites-enabled/{domain} && '
            f'sudo nginx -t && sudo systemctl reload nginx && '
            f'sudo certbot --nginx -d {domain} -d www.{domain} '
            f'--non-interactive --agree-tos -m {email} --redirect'
        )

        return jsonify({
            'success': True,
            'config_written': str(conf_path),
            'next_step': 'Run the following on the server to activate nginx and SSL:',
            'commands': commands
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'steps': steps}), 500


# ── Update Site Config ────────────────────────────────────────────────────

@bp.route('/update-site-config', methods=['POST'])
def update_site_config():
    """
    Update an artist's config.json (safe fields only).
    Body: { "config": { "name": "...", "favicon": "images/icon.png", ... } }
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()
    new_config = data.get('config', {})

    artist_path = get_artist_path(artist_slug)
    config_file = artist_path / 'config.json'

    if not config_file.exists():
        return jsonify({'error': 'Artist config not found'}), 404

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Only allow safe fields to be updated
        allowed = ['name', 'description', 'contact_email', 'domain', 'favicon', 'favicon_color', 'schema', 'seo', 'robots']
        for key in allowed:
            if key in new_config:
                config[key] = new_config[key]

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        return jsonify({'success': True})
    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': f'Error updating config: {str(e)}'}), 500


# ── Feature config ────────────────────────────────────────────────────────

@bp.route('/save-feature', methods=['POST'])
def save_feature():
    """
    Save per-artist feature config and trigger a recompile.
    Body: { "feature": "image_pipeline", "config": {...} | null }
    Passing null disables the feature.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data        = request.get_json() or {}
    feature     = (data.get('feature') or '').strip().replace('-', '_')
    feature_cfg = data.get('config')   # None = disable

    if not feature:
        return jsonify({'error': 'feature name required'}), 400

    config_file = get_artist_path(artist_slug) / 'config.json'
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        features = config.setdefault('features', {})
        if feature_cfg is None:
            features.pop(feature, None)
        else:
            features[feature] = feature_cfg
        if not features:
            config.pop('features', None)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': str(e)}), 500

    # Recompile so the injected script + data-thumb attrs take effect
    compile_ok, compile_error = True, None
    compile_script = Path.cwd() / 'compile.py'
    if compile_script.exists():
        result = subprocess.run(
            ['python3', str(compile_script), '--artist', artist_slug],
            capture_output=True, text=True, timeout=120
        )
        compile_ok    = result.returncode == 0
        compile_error = (result.stderr or result.stdout or '').strip() if not compile_ok else None

    return jsonify({'ok': True, 'compile_ok': compile_ok, 'compile_error': compile_error})


@bp.route('/loom-presets', methods=['GET'])
def loom_presets():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')
    looms_dir = get_artist_path(artist_slug) / 'looms'
    presets = []
    if looms_dir.exists():
        for f in sorted(looms_dir.glob('*.json')):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    trace = json.load(fp)
                presets.append({'name': f.stem, 'trace': trace})
            except (json.JSONDecodeError, IOError):
                pass
    return jsonify({'presets': presets})


@bp.route('/loom-preset', methods=['POST'])
def save_loom_preset():
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')
    data  = request.get_json() or {}
    name  = (data.get('name') or '').strip()
    trace = data.get('trace')
    if not name or not trace:
        return jsonify({'error': 'name and trace required'}), 400
    import re as _re
    name = _re.sub(r'[^a-zA-Z0-9_\- ]', '', name).strip()[:64]
    if not name:
        return jsonify({'error': 'invalid name'}), 400
    looms_dir = get_artist_path(artist_slug) / 'looms'
    looms_dir.mkdir(exist_ok=True)
    with open(looms_dir / f'{name}.json', 'w', encoding='utf-8') as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    return jsonify({'ok': True, 'name': name})


@bp.route('/loom-preset/<name>', methods=['DELETE'])
def delete_loom_preset(name):
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')
    import re as _re
    name = _re.sub(r'[^a-zA-Z0-9_\- ]', '', name).strip()
    looms_dir = get_artist_path(artist_slug) / 'looms'
    preset_file = looms_dir / f'{name}.json'
    if preset_file.exists():
        preset_file.unlink()
    return jsonify({'ok': True})


@bp.route('/generate-thumbs', methods=['POST'])
def generate_thumbs():
    """Backfill .thumbs/ for all images already in this artist's assets/."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    from asset_store import _generate_thumb, assets_dir, _THUMB_IMAGE_EXTS
    root = assets_dir(artist_slug)
    if not root.exists():
        return jsonify({'ok': True, 'generated': 0})

    generated, skipped = 0, 0
    for f in root.rglob('*'):
        if not f.is_file():
            continue
        if any(part.startswith('.') for part in f.relative_to(root).parts):
            continue
        if f.suffix.lower().lstrip('.') in _THUMB_IMAGE_EXTS:
            try:
                _generate_thumb(f, root)
                generated += 1
            except Exception:
                skipped += 1
    return jsonify({'ok': True, 'generated': generated, 'skipped': skipped})


# ── Google Fonts ──────────────────────────────────────────────────────────

@bp.route('/install-google-font', methods=['POST'])
def install_google_font():
    """
    Download a Google Font to the artist's assets/fonts/ directory.
    Body: { "family": "Roboto" }
    Downloads the TTF files for all available weights.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json()
    family = data.get('family', '').strip()
    if not family:
        return jsonify({'error': 'Font family required'}), 400

    artist_path = get_artist_path(artist_slug)
    fonts_dir = artist_path / 'assets' / 'fonts'
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # Also ensure output directory exists
    output_fonts_dir = Path('output') / 'artists' / artist_slug / 'assets' / 'fonts'
    output_fonts_dir.mkdir(parents=True, exist_ok=True)

    import urllib.request
    import re

    try:
        # Fetch the CSS from Google Fonts with a user-agent that returns TTF
        # Request common weights + italic variants
        encoded = family.replace(' ', '+')
        css_url = f"https://fonts.googleapis.com/css2?family={encoded}:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900"
        req = urllib.request.Request(css_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            css_text = resp.read().decode('utf-8')

        # Parse out the font URLs and weights from the CSS
        # Pattern: font-weight: 400; ... src: url(https://...) format('truetype')
        blocks = re.split(r'@font-face\s*\{', css_text)
        downloaded = []

        for block in blocks[1:]:  # Skip first empty split
            weight_match = re.search(r'font-weight:\s*(\d+)', block)
            style_match = re.search(r'font-style:\s*(\w+)', block)
            url_match = re.search(r'src:\s*url\(([^)]+)\)', block)

            if not url_match:
                continue

            font_url = url_match.group(1)
            weight = weight_match.group(1) if weight_match else '400'
            style = style_match.group(1) if style_match else 'normal'

            # Determine file extension from URL
            ext = 'ttf'
            if '.woff2' in font_url:
                ext = 'woff2'
            elif '.woff' in font_url:
                ext = 'woff'

            # Sanitize family name for filename
            safe_family = re.sub(r'[^a-zA-Z0-9]', '-', family).lower().strip('-')
            style_suffix = f'-{style}' if style != 'normal' else ''
            filename = f'{safe_family}-{weight}{style_suffix}.{ext}'

            # Download the font file
            font_req = urllib.request.Request(font_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(font_req, timeout=30) as font_resp:
                font_data = font_resp.read()

            # Save to both source and output
            (fonts_dir / filename).write_bytes(font_data)
            (output_fonts_dir / filename).write_bytes(font_data)

            downloaded.append({
                'filename': filename,
                'weight': weight,
                'style': style,
                'size': len(font_data)
            })

        if not downloaded:
            return jsonify({'error': f'Could not download any font files for "{family}"'}), 400

        return jsonify({
            'success': True,
            'family': family,
            'files': downloaded,
            'css_hint': f"@font-face {{ font-family: '{family}'; src: url('../assets/fonts/{downloaded[0]['filename']}'); }}"
        })

    except urllib.error.URLError as e:
        return jsonify({'error': f'Failed to fetch font: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error installing font: {str(e)}'}), 500


@bp.route('/google-fonts-list', methods=['GET'])
def google_fonts_list():
    """Proxy Google Fonts metadata for the font browser (fallback if direct CORS fails)."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    import urllib.request

    try:
        req = urllib.request.Request('https://fonts.google.com/metadata/fonts', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        fonts = [{'family': f['family'], 'category': f.get('category', ''), 'fonts': f.get('fonts', {})} for f in data.get('familyMetadataList', [])[:1500]]
        return jsonify({'fonts': fonts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Environment Variables / Secrets ────────────────────────────────────────

def _read_env_file(env_path):
    """Parse a .env file into an ordered list of (key, value) tuples."""
    entries = []
    if not env_path.exists():
        return entries
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            entries.append((key.strip(), value.strip()))
    return entries


def _write_env_file(env_path, entries):
    """Write a list of (key, value) tuples to a .env file."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'{k}={v}' for k, v in entries]
    env_path.write_text('\n'.join(lines) + ('\n' if lines else ''))


def _mask_value(value):
    """Show first 4 chars + '...' for masking."""
    if len(value) <= 4:
        return value[:1] + '...' if value else ''
    return value[:4] + '...'


@bp.route('/list-env', methods=['GET'])
def list_env():
    """List environment variables with masked values."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    artist_path = get_artist_path(artist_slug)
    env_path = artist_path / '.env'
    entries = _read_env_file(env_path)
    vars_list = [
        {'key': k, 'value_preview': _mask_value(v), 'has_value': bool(v)}
        for k, v in entries
    ]
    return jsonify({'vars': vars_list})


@bp.route('/get-env-value', methods=['GET'])
def get_env_value():
    """Get the full unmasked value for a single env key."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    key = request.args.get('key', '').strip()
    if not key:
        return jsonify({'error': 'Missing key parameter'}), 400
    artist_path = get_artist_path(artist_slug)
    env_path = artist_path / '.env'
    entries = _read_env_file(env_path)
    for k, v in entries:
        if k == key:
            return jsonify({'key': k, 'value': v})
    return jsonify({'error': 'Key not found'}), 404


@bp.route('/update-env', methods=['POST'])
def update_env():
    """Create or update an environment variable. Empty value deletes the key."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json() or {}
    key = data.get('key', '').strip()
    value = data.get('value', '')
    if not key:
        return jsonify({'error': 'Missing key'}), 400
    artist_path = get_artist_path(artist_slug)
    env_path = artist_path / '.env'
    entries = _read_env_file(env_path)
    # If value is empty, delete the key
    if value == '':
        entries = [(k, v) for k, v in entries if k != key]
    else:
        # Update existing or append
        found = False
        new_entries = []
        for k, v in entries:
            if k == key:
                new_entries.append((key, value))
                found = True
            else:
                new_entries.append((k, v))
        if not found:
            new_entries.append((key, value))
        entries = new_entries
    _write_env_file(env_path, entries)
    return jsonify({'ok': True})


@bp.route('/delete-env', methods=['POST'])
def delete_env():
    """Delete an environment variable."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json() or {}
    key = data.get('key', '').strip()
    if not key:
        return jsonify({'error': 'Missing key'}), 400
    artist_path = get_artist_path(artist_slug)
    env_path = artist_path / '.env'
    entries = _read_env_file(env_path)
    entries = [(k, v) for k, v in entries if k != key]
    _write_env_file(env_path, entries)
    return jsonify({'ok': True})


# ── Secret Leak Scanner ────────────────────────────────────────────────────

@bp.route('/scan-secrets', methods=['POST'])
def scan_secrets():
    """Scan all pages for leaked .env values. Returns any findings."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    env_path = artist_path / '.env'

    if not env_path.exists():
        return jsonify({'status': 'ok', 'message': 'No .env file found — nothing to scan for', 'findings': []})

    findings = []
    for page_dir in sorted(artist_path.iterdir()):
        if not page_dir.is_dir() or page_dir.name in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups'):
            continue
        content_file = page_dir / 'content.md'
        if content_file.exists():
            try:
                content = content_file.read_text()
                leaked = scan_for_leaked_secrets(artist_slug, content)
                if leaked:
                    findings.append({'page': page_dir.name, 'leaked_keys': leaked})
            except IOError:
                pass

    # Also scan api.py output templates (but not the os.getenv calls themselves)
    api_file = artist_path / 'api.py'
    if api_file.exists():
        try:
            api_content = api_file.read_text()
            leaked = scan_for_leaked_secrets(artist_slug, api_content)
            # Filter out false positives from os.getenv('KEY') patterns
            if leaked:
                findings.append({'page': 'api.py', 'leaked_keys': leaked, 'note': 'Check these are not hardcoded values'})
        except IOError:
            pass

    return jsonify({
        'status': 'clean' if not findings else 'leaked',
        'findings': findings
    })


# ── Raw Env File ──────────────────────────────────────────────────────────

@bp.route('/get-env-raw', methods=['GET'])
def get_env_raw():
    """Return the raw .env file content."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    env_path = get_artist_path(artist_slug) / '.env'
    content = ''
    if env_path.exists():
        try:
            content = env_path.read_text()
        except IOError:
            pass
    return jsonify({'content': content})


@bp.route('/set-env-raw', methods=['POST'])
def set_env_raw():
    """Write the raw .env file content."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    data = request.get_json()
    content = data.get('content', '')
    env_path = get_artist_path(artist_slug) / '.env'
    try:
        env_path.write_text(content)
        return jsonify({'success': True})
    except IOError as e:
        return jsonify({'error': str(e)}), 500


# ── List Widgets ──────────────────────────────────────────────────────────

def _read_widget_manifest(widget_dir, name):
    """
    Read manifest for a widget. Checks (in order):
      1. widget_dir/name/widget.json  (directory-format widget)
      2. widget_dir/name.manifest.json  (sidecar for simple .js widgets)
    Falls back to safe defaults.
    """
    manifest = {}
    for candidate in [
        widget_dir / name / 'widget.json',
        widget_dir / (name + '.manifest.json'),
    ]:
        if candidate.exists():
            try:
                with open(candidate, 'r') as f:
                    manifest = json.load(f)
                break
            except (json.JSONDecodeError, IOError):
                pass
    return {
        'name':        manifest.get('name', name),
        'description': manifest.get('description', ''),
        'icon':        manifest.get('icon', ''),
        'author':      manifest.get('author', ''),
        'version':     manifest.get('version', '1.0'),
        'marketplace': manifest.get('marketplace', False),
        'category':    manifest.get('category', 'general'),
        'forked_from': manifest.get('forked_from', ''),
    }


def _scan_widgets(directory, tier):
    """Scan a directory for widgets. Supports both name.js and name/widget.js formats."""
    widgets = []
    if not directory.exists():
        return widgets

    for f in sorted(directory.iterdir()):
        if f.is_file() and f.suffix == '.js':
            # Simple format: widget-name.js
            meta = _read_widget_manifest(directory, f.stem)
            widgets.append({
                'name': f.stem,
                'filename': f.name,
                'tier': tier,
                **meta
            })
        elif f.is_dir():
            # Directory format: widget-name/widget.js
            js_file = f / 'widget.js'
            if js_file.exists():
                meta = _read_widget_manifest(directory, f.name)
                widgets.append({
                    'name': f.name,
                    'filename': f.name + '/widget.js',
                    'tier': tier,
                    **meta
                })
    return widgets


@bp.route('/list-widgets', methods=['GET'])
def list_widgets():
    """
    List all widgets for an artist across tiers.
    Tier 2 (platform): from _shared/widgets/, filtered by artist config platform_widgets list.
    Tier 4 (artist/custom): from artists/{slug}/widgets/ — forked or custom-built.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    # Read artist config for platform_widgets opt-in
    config_file = get_artist_path(artist_slug) / 'config.json'
    enabled_platform = []
    hidden_widgets = []
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            enabled_platform = config.get('platform_widgets', [])
            hidden_widgets = (config.get('dashboard') or {}).get('hidden_widgets', [])
        except (json.JSONDecodeError, IOError):
            pass

    # Tier 2: Adze official widgets — flagship widgets are core (always on); others are opt-in per artist
    platform_dir = Path(__file__).parent / 'widgets'
    all_platform = _scan_widgets(platform_dir, 'platform')
    platform_widgets = [w for w in all_platform
                        if (w.get('flagship') or w['name'] in enabled_platform)
                        and w['name'] not in hidden_widgets]

    # Tier 4: artist custom/forked widgets
    artist_dir = get_artist_path(artist_slug) / 'widgets'
    artist_widgets = _scan_widgets(artist_dir, 'artist')

    # Available = opt-in widgets not yet installed (exclude flagship — they're always on)
    available_platform = [w for w in all_platform
                          if not w.get('flagship') and w['name'] not in enabled_platform]

    return jsonify({
        'artist': artist_slug,
        'widgets': platform_widgets + artist_widgets,
        'available_platform': available_platform
    })


@bp.route('/list-extensions', methods=['GET'])
def list_extensions():
    """List all T2 platform widgets, marking which are installed for this artist."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    config_file = get_artist_path(artist_slug) / 'config.json'
    enabled_platform = []
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            enabled_platform = config.get('platform_widgets', [])
        except (json.JSONDecodeError, IOError):
            pass

    platform_dir = Path(__file__).parent / 'widgets'
    platform_widgets = _scan_widgets(platform_dir, 'platform')
    for w in platform_widgets:
        w['installed'] = w.get('flagship') or w['name'] in enabled_platform
    # Core/flagship widgets are always installed — exclude from the extensions marketplace
    platform_widgets = [w for w in platform_widgets if not w.get('flagship')]

    return jsonify({'platform': platform_widgets})


@bp.route('/install-widget', methods=['POST'])
def install_widget():
    """
    Install a T2 platform widget — adds it to the artist's config platform_widgets list.
    Body: { "name": "widget-name", "tier": "platform" }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Widget name required'}), 400

    platform_dir = Path(__file__).parent / 'widgets'
    found = any(
        (f.is_file() and f.suffix == '.js' and f.stem == name) or
        (f.is_dir() and f.name == name and (f / 'widget.js').exists())
        for f in platform_dir.iterdir()
    )
    if not found:
        return jsonify({'error': 'Platform widget not found'}), 404

    config_file = get_artist_path(artist_slug) / 'config.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        pw = config.get('platform_widgets', [])
        if name not in pw:
            pw.append(name)
            config['platform_widgets'] = pw
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
        return jsonify({'ok': True, 'action': 'enabled'})
    except (json.JSONDecodeError, IOError) as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/uninstall-widget', methods=['POST'])
def uninstall_widget():
    """
    Uninstall a widget. Platform: removes from config. Artist: deletes file.
    Body: { "name": "widget-name", "tier": "platform"|"artist" }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    tier = data.get('tier', '')

    if not name:
        return jsonify({'error': 'Widget name required'}), 400

    if tier == 'platform':
        config_file = get_artist_path(artist_slug) / 'config.json'
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            pw = config.get('platform_widgets', [])
            if name in pw:
                pw.remove(name)
                config['platform_widgets'] = pw
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=4)
            return jsonify({'ok': True})
        except (json.JSONDecodeError, IOError) as e:
            return jsonify({'error': str(e)}), 500

    elif tier == 'artist':
        widgets_dir = get_artist_path(artist_slug) / 'widgets'
        # Try file first, then directory
        js_file = widgets_dir / (name + '.js')
        dir_path = widgets_dir / name
        if js_file.exists():
            js_file.unlink()
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
        return jsonify({'ok': True})

    return jsonify({'error': 'Invalid tier'}), 400


@bp.route('/save-widget', methods=['POST'])
def save_widget():
    """
    Save (create or update) a Tier 4 (custom/forked) widget's JS source.
    Body: { "name": "widget-name", "code": "...js..." }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    name = (data.get('name', '') or '').strip()
    code = data.get('code', '')

    name = secure_filename(name if name.endswith('.js') else name + '.js')
    if not name or name == '.js':
        return jsonify({'error': 'Widget name required'}), 400

    widgets_dir = get_artist_path(artist_slug) / 'widgets'
    widgets_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(widgets_dir / name, 'w', encoding='utf-8') as f:
            f.write(code)
        return jsonify({'ok': True, 'filename': name})
    except IOError as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/new-widget', methods=['POST'])
def new_widget():
    """
    Create a blank new Tier 4 (custom) widget.
    Body: { "name": "My Widget", "description": "..." }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    raw_name = (data.get('name', '') or '').strip()
    description = (data.get('description', '') or '').strip()

    if not raw_name:
        return jsonify({'error': 'Widget name required'}), 400

    import re as _re
    slug_name = _re.sub(r'[^a-z0-9]+', '-', raw_name.lower()).strip('-')
    if not slug_name:
        return jsonify({'error': 'Invalid widget name'}), 400

    widgets_dir = get_artist_path(artist_slug) / 'widgets'
    widgets_dir.mkdir(parents=True, exist_ok=True)

    js_path = widgets_dir / (slug_name + '.js')
    if js_path.exists():
        return jsonify({'error': f'Widget "{slug_name}" already exists'}), 409

    display_name = raw_name.replace('-', ' ').replace('_', ' ').title()
    blank_js = (
        f'// Widget: {display_name}\n'
        f'// {description or "Custom widget"}\n\n'
        f'(function(ctx) {{\n'
        f'    const c = ctx.container;\n'
        f'    c.style.cssText = "display:flex;flex-direction:column;flex:1;padding:24px;overflow:auto;";\n'
        f'    c.innerHTML = `\n'
        f'        <h3 style="margin:0 0 8px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">{display_name}</h3>\n'
        f'        <p style="color:var(--text2);font-size:11px;">Start building here. Use <code>ctx.apiFetch()</code> to call APIs.</p>\n'
        f'    `;\n'
        f'}})(ctx);\n'
    )

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(blank_js)

    manifest = {'name': slug_name, 'description': description or display_name,
                 'author': artist_slug, 'version': '1.0', 'marketplace': False, 'category': 'custom'}
    with open(widgets_dir / (slug_name + '.manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    return jsonify({'ok': True, 'name': slug_name, 'filename': slug_name + '.js'})



@bp.route('/fork-widget', methods=['POST'])
def fork_widget():
    """
    Fork a Tier 2 or Tier 3 widget into the artist's Tier 4 (custom) widgets directory.
    Creates an editable copy that no longer auto-updates from the source.
    Body: { "name": "platform-widget-name" }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'Widget name required'}), 400

    platform_dir = Path(__file__).parent / 'widgets'
    dest_dir = get_artist_path(artist_slug) / 'widgets'
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Don't clobber an existing artist widget
    dest_stem = name
    if (dest_dir / (dest_stem + '.js')).exists():
        dest_stem = name + '-fork'

    src_dir = platform_dir / name
    src_js  = platform_dir / (name + '.js')

    if src_dir.exists() and (src_dir / 'widget.js').exists():
        src_code = (src_dir / 'widget.js').read_text(encoding='utf-8')
        src_meta_path = src_dir / 'widget.json'
    elif src_js.exists():
        src_code = src_js.read_text(encoding='utf-8')
        src_meta_path = platform_dir / (name + '.json')
    else:
        return jsonify({'error': 'Platform widget not found'}), 404

    src_meta = {}
    if src_meta_path.exists():
        try:
            with open(src_meta_path) as f:
                src_meta = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    fork_header = f'// Forked from Adze platform widget: {name}\n// This copy is yours — edit freely.\n\n'
    with open(dest_dir / (dest_stem + '.js'), 'w', encoding='utf-8') as f:
        f.write(fork_header + src_code)

    fork_manifest = {
        'name': dest_stem,
        'description': (src_meta.get('description') or '') + ' (forked)',
        'author': artist_slug, 'version': '1.0',
        'marketplace': False,
        'category': src_meta.get('category', 'custom'),
        'forked_from': name
    }
    with open(dest_dir / (dest_stem + '.manifest.json'), 'w') as f:
        json.dump(fork_manifest, f, indent=2)

    return jsonify({'ok': True, 'name': dest_stem, 'filename': dest_stem + '.js'})


@bp.route('/update-widget', methods=['POST'])
def update_widget():
    """
    Update an installed widget to the latest platform version.

    For platform widgets (tier=platform): no file action needed — they always
    load fresh from _shared/widgets/. Returns ok so the frontend can reload.

    For forked artist widgets (tier=artist, has forked_from in manifest):
    overwrites the artist's widget.js with the current platform source,
    preserving the fork header comment.

    Body: { "name": "widget-name", "tier": "platform"|"artist" }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    data = request.get_json() or {}
    name = (data.get('name', '') or '').strip()
    tier = data.get('tier', '')

    if not name:
        return jsonify({'error': 'Widget name required'}), 400

    platform_dir = Path(__file__).parent / 'widgets'

    if tier == 'platform':
        # Platform widgets load directly from _shared/widgets/ — always current.
        # Nothing to copy; just confirm it exists.
        src_dir = platform_dir / name
        if not (src_dir / 'widget.js').exists():
            return jsonify({'error': 'Platform widget source not found'}), 404
        return jsonify({'ok': True, 'message': 'Platform widget is always up to date'})

    elif tier == 'artist':
        # Find the manifest to discover forked_from
        widgets_dir = get_artist_path(artist_slug) / 'widgets'
        manifest_path = widgets_dir / (name + '.manifest.json')
        if not manifest_path.exists():
            return jsonify({'error': 'No manifest found — widget was not forked from a platform widget'}), 400

        try:
            manifest = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, IOError) as e:
            return jsonify({'error': f'Could not read manifest: {e}'}), 500

        source = manifest.get('forked_from')
        if not source:
            return jsonify({'error': 'Widget was not forked from a platform widget'}), 400

        src_js_path = platform_dir / source / 'widget.js'
        if not src_js_path.exists():
            src_js_path = platform_dir / (source + '.js')
        if not src_js_path.exists():
            return jsonify({'error': f'Platform source "{source}" not found'}), 404

        new_code = src_js_path.read_text(encoding='utf-8')
        dest_js = widgets_dir / (name + '.js')

        fork_header = f'// Forked from Adze platform widget: {source}\n// This copy is yours — edit freely.\n// Updated from platform source.\n\n'
        dest_js.write_text(fork_header + new_code, encoding='utf-8')

        return jsonify({'ok': True, 'message': f'Updated from platform widget "{source}"'})

    return jsonify({'error': 'Invalid tier'}), 400


@bp.route('/get-widget', methods=['GET'])
def get_widget():
    """
    Get the JS content of a widget file.
    Query params: filename, tier (platform|artist, default: artist)
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    filename = request.args.get('filename')
    tier = request.args.get('tier', 'artist')

    if not filename:
        return jsonify({'error': 'filename parameter required'}), 400

    # Widgets come in two shapes: "name.js" or "name/widget.js" (directory format).
    # secure_filename collapses slashes, so we sanitise each component separately
    # and only allow the specific subpath patterns we generate ourselves.
    parts = filename.replace('\\', '/').split('/')
    parts = [secure_filename(p) for p in parts if p and p != '..']

    if len(parts) == 1:
        # Simple: name.js
        safe_filename = parts[0]
    elif len(parts) == 2 and parts[1] in ('widget.js', 'engine.js'):
        # Directory format: name/widget.js — plus name/engine.js for widgets
        # (e.g. Loom) whose editor and live runtime share one engine file.
        safe_filename = parts[0] + '/' + parts[1]
    else:
        return jsonify({'error': 'Invalid widget filename'}), 400

    if tier == 'platform':
        widget_path = (Path(__file__).parent / 'widgets' / safe_filename).resolve()
        root = (Path(__file__).parent / 'widgets').resolve()
    else:
        widget_path = (get_artist_path(artist_slug) / 'widgets' / safe_filename).resolve()
        root = (get_artist_path(artist_slug) / 'widgets').resolve()

    # Final path traversal guard — resolved path must stay inside the widgets root
    if not str(widget_path).startswith(str(root)):
        abort(403)

    if not widget_path.exists():
        return jsonify({'error': 'Widget not found'}), 404

    return send_file(widget_path, mimetype='application/javascript')


# ── Domain Check ──────────────────────────────────────────────────────────

SERVER_IPV4 = '178.104.233.5'  # adze.studio A record — the host artists must point their A record at
SERVER_IPV6 = '2a01:4f8:1c18:33e9::1'  # host IPv6 (adze.studio publishes no AAAA; kept for match-only)

@bp.route('/check-domain', methods=['GET'])
def check_domain():
    """
    Check if an artist's configured domain has correct DNS and SSL.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    config_file = artist_path / 'config.json'

    if not config_file.exists():
        return jsonify({'error': 'Artist config not found'}), 404

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    domain = config.get('domain', '').strip()
    if not domain:
        return jsonify({
            'domain': '',
            'status': 'not_configured',
            'message': 'No domain configured. Set one in the Config tab.'
        })

    result = {
        'domain': domain,
        'dns_a': None,
        'dns_aaaa': None,
        'dns_ok': False,
        'nginx_ok': False,
        'ssl_ok': False,
        'status': 'unknown',
        'message': ''
    }

    # Check DNS A record
    try:
        a_records = socket.getaddrinfo(domain, None, socket.AF_INET)
        result['dns_a'] = list(set(addr[4][0] for addr in a_records))
    except socket.gaierror:
        result['dns_a'] = []

    # Check DNS AAAA record
    try:
        aaaa_records = socket.getaddrinfo(domain, None, socket.AF_INET6)
        result['dns_aaaa'] = list(set(addr[4][0] for addr in aaaa_records))
    except socket.gaierror:
        result['dns_aaaa'] = []

    # Check if DNS points to this server
    a_match = SERVER_IPV4 in (result['dns_a'] or [])
    aaaa_match = any(SERVER_IPV6 in addr for addr in (result['dns_aaaa'] or []))
    result['dns_ok'] = a_match or aaaa_match

    # Check nginx config
    nginx_conf = Path(f'/etc/nginx/sites-available/{domain}')
    nginx_enabled = Path(f'/etc/nginx/sites-enabled/{domain}')
    # Also check if domain appears in the main blog config
    main_conf = Path('/etc/nginx/sites-available/blog')
    nginx_in_main = False
    if main_conf.exists():
        try:
            nginx_in_main = domain in main_conf.read_text()
        except:
            pass
    result['nginx_ok'] = nginx_conf.exists() or nginx_enabled.exists() or nginx_in_main

    # Check SSL certificate (needs root, so handle permission errors)
    try:
        cert_path = Path(f'/etc/letsencrypt/live/{domain}/fullchain.pem')
        result['ssl_ok'] = cert_path.exists()
    except (PermissionError, OSError):
        # Can't read letsencrypt dir without root — check via subprocess instead
        try:
            r = subprocess.run(['sudo', 'test', '-f', f'/etc/letsencrypt/live/{domain}/fullchain.pem'],
                               capture_output=True, timeout=3)
            result['ssl_ok'] = r.returncode == 0
        except:
            result['ssl_ok'] = False

    # Determine overall status
    if not result['dns_ok']:
        result['status'] = 'dns_pending'
        result['message'] = f'DNS not pointing to this server. Add an A record for {domain} pointing to {SERVER_IPV4}'
    elif not result['nginx_ok']:
        result['status'] = 'nginx_needed'
        result['message'] = 'DNS is correct. Nginx config needed.'
    elif not result['ssl_ok']:
        result['status'] = 'ssl_needed'
        result['message'] = 'DNS and Nginx configured. SSL certificate needed.'
    else:
        result['status'] = 'live'
        result['message'] = f'{domain} is fully configured and live.'

    # Generate setup commands
    result['server_ipv4'] = SERVER_IPV4
    result['server_ipv6'] = SERVER_IPV6
    result['slug'] = artist_slug

    return jsonify(result)


# ── Export Site ────────────────────────────────────────────────────────────

@bp.route('/export-site', methods=['GET'])
def export_site():
    """
    Export the artist's site as a downloadable .zip.
    Includes: compiled HTML, assets, api.py source, and a README.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    import zipfile
    import io
    import time

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    output_path = Path('output/artists') / artist_slug

    if not output_path.exists():
        return jsonify({'error': 'No compiled site found. Save a page first.'}), 404

    # Build zip in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Compiled HTML + assets from output/
        for file_path in sorted(output_path.rglob('*')):
            if file_path.is_file():
                arcname = str(file_path.relative_to(output_path))
                zf.write(file_path, f'site/{arcname}')

        # 2. api.py source if it exists
        api_file = artist_path / 'api.py'
        if api_file.exists():
            zf.write(api_file, 'api/api.py')

        # 3. Feature config
        config_file = artist_path / 'config.json'
        if config_file.exists():
            zf.write(config_file, 'api/config.json')

        # 4. Source content.md files (for re-editing elsewhere)
        for page_dir in sorted(artist_path.iterdir()):
            if page_dir.is_dir() and page_dir.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups'):
                content_file = page_dir / 'content.md'
                config_json = page_dir / 'config.json'
                if content_file.exists():
                    zf.write(content_file, f'source/{page_dir.name}/content.md')
                if config_json.exists():
                    zf.write(config_json, f'source/{page_dir.name}/config.json')

        # 5. README
        readme = f"""# {artist_slug} — Site Export
Exported: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}

## What's in this zip

### site/
Your complete, ready-to-host website. Every page is a folder with an
index.html file. Assets (images, fonts) are in site/assets/.

To host this anywhere: upload the contents of site/ to any static
hosting provider (Netlify, Vercel, GitHub Pages, any web server).
The site is fully self-contained with relative paths — no server needed.

### source/
The raw content.md and config.json files for each page. These are the
editable source files used by the dashboard. Format:
  <style>CSS here</style>
  <html>HTML here</html>

### api/ (if present)
Your custom backend code (api.py) and artist config. This is a Flask
Blueprint — to run it elsewhere you'll need Python + Flask:
  pip install flask
  # See api.py for the Blueprint definition
  # You'll need to adapt it to your hosting setup

Note: features like bookings are pre-built modules that aren't included
in this export. The api.py file contains only your custom endpoints.
"""
        zf.writestr('README.md', readme)

    buf.seek(0)
    timestamp = time.strftime('%Y%m%d', time.gmtime())
    filename = f'{artist_slug}-export-{timestamp}.zip'

    return send_file(
        buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )


# ── Delete Site ────────────────────────────────────────────────────────────

@bp.route('/delete-site', methods=['POST'])
def delete_site():
    """
    Permanently delete an artist's entire site.
    Removes source files, compiled output, and data.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    artist_path = get_artist_path(artist_slug)
    output_path = Path('output/artists') / artist_slug

    if not artist_path.exists():
        return jsonify({'error': 'Artist directory not found'}), 404

    try:
        # Remove source
        if artist_path.exists():
            shutil.rmtree(str(artist_path))
        # Remove compiled output
        if output_path.exists():
            shutil.rmtree(str(output_path))
        return jsonify({'ok': True, 'message': 'Site deleted permanently.'})
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


# ── Snapshots ──────────────────────────────────────────────────────────────
# Two flavours of snapshot live in the same .snapshots/ dir:
#   - User snapshots: timestamped, capped at SNAPSHOT_KEEP, shown in History.
#   - Autosave: single rolling slot (AUTOSAVE_FILENAME) overwritten by every
#     Save. Excluded from the cap and surfaced separately.

AUTOSAVE_FILENAME = '_autosave.tar.gz'
SNAPSHOT_KEEP = 10
SNAPSHOT_EXCLUDE_DIRS = {'assets', 'widgets', '.snapshots', '__pycache__', 'backups'}
SNAPSHOT_EXCLUDE_FILES = {'.env'}


def _write_artist_tarball(artist_path, snap_path):
    """Tar+gzip the artist dir into snap_path, skipping heavy/secret items."""
    import tarfile
    snap_path.parent.mkdir(exist_ok=True)
    with tarfile.open(str(snap_path), 'w:gz') as tar:
        for item in sorted(artist_path.iterdir()):
            if item.name in SNAPSHOT_EXCLUDE_DIRS or item.name in SNAPSHOT_EXCLUDE_FILES:
                continue
            tar.add(str(item), arcname=item.name)


def _parse_snapshot_filename(f):
    """Turn a timestamped snapshot file into a UI-ready dict."""
    stem = f.stem.replace('.tar', '')
    parts = stem.split('_', 1)
    timestamp = parts[0] if parts else stem
    name = parts[1].replace('-', ' ') if len(parts) > 1 else 'Unnamed'
    return {
        'filename': f.name,
        'name': name,
        'timestamp': timestamp,
        'size': f.stat().st_size,
    }


@bp.route('/list-snapshots', methods=['GET'])
def list_snapshots():
    """
    List all snapshots for an artist.
    Headers: X-Artist-Slug, X-Admin-Token
    Returns: { "snapshots": [...], "autosave": {...} | null }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    snap_dir = get_artist_path(artist_slug) / '.snapshots'
    if not snap_dir.exists():
        return jsonify({'snapshots': [], 'autosave': None})

    snapshots = []
    autosave = None
    for f in sorted(snap_dir.glob('*.tar.gz'), reverse=True):
        if f.name == AUTOSAVE_FILENAME:
            autosave = {
                'filename': f.name,
                'name': 'Autosave (latest Save)',
                'timestamp': _time.strftime('%Y-%m-%dT%H-%M-%S', _time.gmtime(f.stat().st_mtime)),
                'size': f.stat().st_size,
                'autosave': True,
            }
            continue
        snapshots.append(_parse_snapshot_filename(f))

    return jsonify({'snapshots': snapshots, 'autosave': autosave})


@bp.route('/create-snapshot', methods=['POST'])
def create_snapshot():
    """
    Create a user-named snapshot of the artist's site.
    Headers: X-Artist-Slug, X-Admin-Token
    Body: { "name": "optional snapshot name" }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data = request.get_json() or {}
    name = data.get('name', 'manual').strip()
    safe_name = name.lower().replace(' ', '-')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '-')[:40] or 'manual'

    artist_path = get_artist_path(artist_slug)
    snap_dir = artist_path / '.snapshots'

    timestamp = _time.strftime('%Y-%m-%dT%H-%M-%S', _time.gmtime())
    filename = f'{timestamp}_{safe_name}.tar.gz'
    snap_path = snap_dir / filename

    try:
        _write_artist_tarball(artist_path, snap_path)

        # Prune user snapshots — keep max SNAPSHOT_KEEP, never touching the autosave slot.
        user_snaps = sorted(
            (s for s in snap_dir.glob('*.tar.gz') if s.name != AUTOSAVE_FILENAME),
            reverse=True,
        )
        for old in user_snaps[SNAPSHOT_KEEP:]:
            old.unlink()

        return jsonify({
            'ok': True,
            'filename': filename,
            'size': snap_path.stat().st_size,
        })

    except Exception as e:
        return jsonify({'error': f'Snapshot failed: {str(e)}'}), 500


@bp.route('/autosave-snapshot', methods=['POST'])
def autosave_snapshot():
    """
    Overwrite the rolling autosave slot. Called fire-and-forget by the
    dashboard after every Save so the user always has one-step undo
    without growing the snapshot pile.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    artist_path = get_artist_path(artist_slug)
    snap_path = artist_path / '.snapshots' / AUTOSAVE_FILENAME

    try:
        _write_artist_tarball(artist_path, snap_path)
        return jsonify({'ok': True, 'filename': AUTOSAVE_FILENAME, 'size': snap_path.stat().st_size})
    except Exception as e:
        return jsonify({'error': f'Autosave failed: {str(e)}'}), 500


@bp.route('/restore-snapshot', methods=['POST'])
def restore_snapshot():
    """
    Restore a snapshot. Extracts the tarball over the artist directory
    (replacing pages, config, api.py — but NOT assets/ or widgets/).
    Headers: X-Artist-Slug, X-Admin-Token
    Body: { "filename": "2026-03-27T08-15-30_name.tar.gz" }
    """
    import tarfile

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data = request.get_json() or {}
    filename = data.get('filename', '')
    if not filename or '..' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    artist_path = get_artist_path(artist_slug)
    snap_path = artist_path / '.snapshots' / filename

    if not snap_path.exists():
        return jsonify({'error': 'Snapshot not found'}), 404

    PRESERVE_DIRS = {'assets', 'widgets', '.snapshots', '__pycache__', 'backups'}

    try:
        # Remove current files (except preserved dirs)
        for item in artist_path.iterdir():
            if item.name in PRESERVE_DIRS:
                continue
            if item.is_dir():
                shutil.rmtree(str(item))
            else:
                item.unlink()

        # Extract snapshot
        with tarfile.open(str(snap_path), 'r:gz') as tar:
            tar.extractall(str(artist_path))

        return jsonify({'ok': True, 'message': 'Snapshot restored. Click Save to recompile.'})

    except Exception as e:
        return jsonify({'error': f'Restore failed: {str(e)}'}), 500


@bp.route('/delete-snapshot', methods=['POST'])
def delete_snapshot():
    """
    Delete a snapshot file.
    Headers: X-Artist-Slug, X-Admin-Token
    Body: { "filename": "..." }
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data = request.get_json() or {}
    filename = data.get('filename', '')
    if not filename or '..' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    snap_path = get_artist_path(artist_slug) / '.snapshots' / filename
    if not snap_path.exists():
        return jsonify({'error': 'Snapshot not found'}), 404

    try:
        snap_path.unlink()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


# ── Integration helpers ───────────────────────────────────────────────────

def _read_env(artist_slug):
    """Return dict of .env key/value pairs for an artist."""
    env_path = get_artist_path(artist_slug) / '.env'
    env = {}
    if env_path.exists():
        for line in env_path.read_text().strip().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ── YouTube Integration ───────────────────────────────────────────────────

@bp.route('/youtube-stats', methods=['GET'])
def youtube_stats():
    """
    Proxy YouTube Data API v3 — reads YOUTUBE_API_KEY + YOUTUBE_CHANNEL_ID from artist .env.
    Returns channel stats + recent videos (uses uploads playlist, minimal quota).
    """
    import urllib.request, urllib.parse

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    env = _read_env(artist_slug)
    api_key    = env.get('YOUTUBE_API_KEY', '')
    channel_id = env.get('YOUTUBE_CHANNEL_ID', '')

    if not api_key or not channel_id:
        return jsonify({'configured': False})

    def yt_get(endpoint, params):
        params['key'] = api_key
        url = f'https://www.googleapis.com/youtube/v3/{endpoint}?' + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=8) as r:
                return json.loads(r.read())
        except Exception as e:
            return {'error': str(e)}

    # 1. Channel stats + uploads playlist ID
    ch = yt_get('channels', {
        'part': 'statistics,snippet,contentDetails',
        'id': channel_id
    })
    if 'error' in ch or not ch.get('items'):
        return jsonify({'configured': True, 'error': ch.get('error', {}).get('message', 'Channel not found')})

    channel    = ch['items'][0]
    stats      = channel['statistics']
    snippet    = channel['snippet']
    uploads_pl = channel['contentDetails']['relatedPlaylists']['uploads']

    # 2. Recent uploads (1 quota unit vs 100 for search)
    pl = yt_get('playlistItems', {
        'part': 'snippet',
        'playlistId': uploads_pl,
        'maxResults': 8
    })
    video_ids = [item['snippet']['resourceId']['videoId'] for item in pl.get('items', [])]

    # 3. Video statistics
    videos = []
    if video_ids:
        vr = yt_get('videos', {
            'part': 'statistics,snippet',
            'id': ','.join(video_ids)
        })
        for v in vr.get('items', []):
            vs  = v.get('statistics', {})
            vsn = v.get('snippet', {})
            thumb = (vsn.get('thumbnails', {}).get('medium') or
                     vsn.get('thumbnails', {}).get('default') or {}).get('url', '')
            videos.append({
                'id':          v['id'],
                'title':       vsn.get('title', ''),
                'published':   vsn.get('publishedAt', ''),
                'thumbnail':   thumb,
                'views':       int(vs.get('viewCount', 0)),
                'likes':       int(vs.get('likeCount', 0)),
                'comments':    int(vs.get('commentCount', 0)),
            })

    return jsonify({
        'configured':    True,
        'channel_id':    channel_id,
        'name':          snippet.get('title', ''),
        'description':   snippet.get('description', ''),
        'thumbnail':     (snippet.get('thumbnails', {}).get('default') or {}).get('url', ''),
        'subscribers':   int(stats.get('subscriberCount', 0)),
        'total_views':   int(stats.get('viewCount', 0)),
        'video_count':   int(stats.get('videoCount', 0)),
        'videos':        videos,
    })


@bp.route('/youtube-verify', methods=['POST'])
def youtube_verify():
    """Verify a YouTube API key + channel ID and save them to .env."""
    import urllib.request, urllib.parse

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data       = request.get_json(silent=True) or {}
    api_key    = data.get('api_key', '').strip()
    channel_id = data.get('channel_id', '').strip()

    if not api_key or not channel_id:
        return jsonify({'error': 'api_key and channel_id are required'}), 400

    # Verify the key + channel work
    params = {'part': 'snippet', 'id': channel_id, 'key': api_key}
    url    = 'https://www.googleapis.com/youtube/v3/channels?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            result = json.loads(r.read())
    except Exception as e:
        return jsonify({'error': f'Could not reach YouTube: {e}'}), 502

    if result.get('error'):
        msg = result['error'].get('message', 'Invalid API key')
        return jsonify({'error': msg}), 400
    if not result.get('items'):
        return jsonify({'error': 'Channel not found. Check your Channel ID.'}), 400

    channel_name = result['items'][0]['snippet']['title']

    # Save to .env
    env_path = get_artist_path(artist_slug) / '.env'
    lines    = env_path.read_text().splitlines() if env_path.exists() else []
    for key, val in [('YOUTUBE_API_KEY', api_key), ('YOUTUBE_CHANNEL_ID', channel_id)]:
        replaced = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={val}'
                replaced = True
                break
        if not replaced:
            lines.append(f'{key}={val}')
    env_path.write_text('\n'.join(lines) + '\n')

    return jsonify({'success': True, 'channel_name': channel_name})


# ── Vimeo Integration ─────────────────────────────────────────────────────

@bp.route('/vimeo-stats', methods=['GET'])
def vimeo_stats():
    """Proxy Vimeo API — reads VIMEO_ACCESS_TOKEN from artist .env."""
    import urllib.request

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    env   = _read_env(artist_slug)
    token = env.get('VIMEO_ACCESS_TOKEN', '')

    if not token:
        return jsonify({'configured': False})

    def vimeo_get(path, params=''):
        url = f'https://api.vimeo.com{path}{"?" + params if params else ""}'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.vimeo.*+json;version=3.4'
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            return None, f'HTTP {e.code}'
        except Exception as e:
            return None, str(e)

    # User profile + stats
    me, err = vimeo_get('/me')
    if err:
        return jsonify({'configured': True, 'error': err})

    # Recent videos (up to 9 for a 3-column grid)
    vids, _ = vimeo_get('/me/videos', 'per_page=9&fields=uri,name,description,created_time,stats,pictures,link,duration')

    videos = []
    for v in (vids or {}).get('data', []):
        thumb = ''
        for size in (v.get('pictures', {}).get('sizes') or []):
            if size.get('width', 0) >= 295:
                thumb = size['link']
                break
        if not thumb:
            sizes = v.get('pictures', {}).get('sizes') or []
            if sizes:
                thumb = sizes[-1].get('link', '')
        dur = v.get('duration', 0)
        videos.append({
            'uri':         v.get('uri', ''),
            'name':        v.get('name', ''),
            'link':        v.get('link', ''),
            'created':     v.get('created_time', ''),
            'plays':       v.get('stats', {}).get('plays', 0) or 0,
            'thumbnail':   thumb,
            'duration':    f'{dur // 60}:{dur % 60:02d}' if dur else '',
        })

    stats = me.get('metadata', {}).get('connections', {})
    return jsonify({
        'configured':    True,
        'name':          me.get('name', ''),
        'bio':           me.get('bio', ''),
        'link':          me.get('link', ''),
        'thumbnail':     (me.get('pictures', {}).get('sizes') or [{}])[-1].get('link', ''),
        'followers':     me.get('metadata', {}).get('connections', {}).get('followers', {}).get('total', 0),
        'total_videos':  me.get('metadata', {}).get('connections', {}).get('videos', {}).get('total', 0),
        'videos':        videos,
    })


@bp.route('/vimeo-verify', methods=['POST'])
def vimeo_verify():
    """Verify a Vimeo personal access token and save to .env."""
    import urllib.request

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data  = request.get_json(silent=True) or {}
    token = data.get('access_token', '').strip()

    if not token:
        return jsonify({'error': 'access_token is required'}), 400

    req = urllib.request.Request(
        'https://api.vimeo.com/me',
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.vimeo.*+json;version=3.4'}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            me = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return jsonify({'error': 'Invalid access token'}), 400
        return jsonify({'error': f'Vimeo error: HTTP {e.code}'}), 400
    except Exception as e:
        return jsonify({'error': f'Could not reach Vimeo: {e}'}), 502

    name = me.get('name', 'Your Vimeo account')

    env_path = get_artist_path(artist_slug) / '.env'
    lines    = env_path.read_text().splitlines() if env_path.exists() else []
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith('VIMEO_ACCESS_TOKEN='):
            lines[i] = f'VIMEO_ACCESS_TOKEN={token}'
            replaced = True
            break
    if not replaced:
        lines.append(f'VIMEO_ACCESS_TOKEN={token}')
    env_path.write_text('\n'.join(lines) + '\n')

    return jsonify({'success': True, 'name': name})


# ── Calendly Integration ──────────────────────────────────────────────────

@bp.route('/calendly-stats', methods=['GET'])
def calendly_stats():
    """Proxy Calendly API v2 — reads CALENDLY_ACCESS_TOKEN from artist .env."""
    import urllib.request, urllib.parse
    from datetime import datetime, timezone, timedelta

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    env   = _read_env(artist_slug)
    token = env.get('CALENDLY_ACCESS_TOKEN', '')

    if not token:
        return jsonify({'configured': False})

    def cal_get(path, params=None):
        url = f'https://api.calendly.com{path}'
        if params:
            url += '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read())
                return None, body.get('message', f'HTTP {e.code}')
            except Exception:
                return None, f'HTTP {e.code}'
        except Exception as e:
            return None, str(e)

    # Get current user
    me, err = cal_get('/users/me')
    if err:
        return jsonify({'configured': True, 'error': err})

    user_uri  = me['resource']['uri']
    user_name = me['resource']['name']
    slug      = me['resource']['slug']
    tz        = me['resource'].get('timezone', 'UTC')

    # Event types
    et, _ = cal_get('/event_types', {'user': user_uri, 'active': 'true'})
    event_types = []
    for e in (et or {}).get('collection', []):
        event_types.append({
            'name':               e.get('name', ''),
            'duration':           e.get('duration', 0),
            'scheduling_url':     e.get('scheduling_url', ''),
            'color':              e.get('color', '#0069ff'),
            'kind':               e.get('kind', 'solo'),
        })

    # Upcoming events (next 7 days)
    now      = datetime.now(timezone.utc)
    in7days  = now + timedelta(days=7)
    upcoming, _ = cal_get('/scheduled_events', {
        'user':            user_uri,
        'status':          'active',
        'min_start_time':  now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'max_start_time':  in7days.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sort':            'start_time:asc',
        'count':           10,
    })

    events = []
    for ev in (upcoming or {}).get('collection', []):
        invitees_uri = ev.get('uri', '').split('/')[-1]
        events.append({
            'name':       ev.get('name', ''),
            'start_time': ev.get('start_time', ''),
            'end_time':   ev.get('end_time', ''),
            'status':     ev.get('status', ''),
            'uri':        ev.get('uri', ''),
            'invitees_count': ev.get('invitees_counter', {}).get('active', 0),
        })

    # Past 30 days count
    past30, _ = cal_get('/scheduled_events', {
        'user':            user_uri,
        'status':          'active',
        'min_start_time':  (now - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'max_start_time':  now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'count':           100,
    })
    past_count = len((past30 or {}).get('collection', []))

    return jsonify({
        'configured':    True,
        'name':          user_name,
        'slug':          slug,
        'timezone':      tz,
        'scheduling_url': f'https://calendly.com/{slug}',
        'event_types':   event_types,
        'upcoming':      events,
        'past_30_days':  past_count,
    })


@bp.route('/calendly-verify', methods=['POST'])
def calendly_verify():
    """Verify a Calendly personal access token and save to .env."""
    import urllib.request

    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    data  = request.get_json(silent=True) or {}
    token = data.get('access_token', '').strip()

    if not token:
        return jsonify({'error': 'access_token is required'}), 400

    req = urllib.request.Request(
        'https://api.calendly.com/users/me',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return jsonify({'error': 'Invalid access token — check it was copied correctly'}), 400
        return jsonify({'error': f'Calendly error: HTTP {e.code}'}), 400
    except Exception as e:
        return jsonify({'error': f'Could not reach Calendly: {e}'}), 502

    name = result.get('resource', {}).get('name', 'Your Calendly account')

    env_path = get_artist_path(artist_slug) / '.env'
    lines    = env_path.read_text().splitlines() if env_path.exists() else []
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith('CALENDLY_ACCESS_TOKEN='):
            lines[i] = f'CALENDLY_ACCESS_TOKEN={token}'
            replaced = True
            break
    if not replaced:
        lines.append(f'CALENDLY_ACCESS_TOKEN={token}')
    env_path.write_text('\n'.join(lines) + '\n')

    return jsonify({'success': True, 'name': name})


# ── Stripe Integration ────────────────────────────────────────────────────

def _get_stripe_client(artist_slug):
    """Get a Stripe client using the artist's API key from .env"""
    env_path = get_artist_path(artist_slug) / '.env'
    if not env_path.exists():
        return None
    env_text = env_path.read_text()
    keys = {}
    for line in env_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, _, v = line.partition('=')
        keys[k.strip()] = v.strip().strip('"').strip("'")
    secret_key = keys.get('STRIPE_SECRET_KEY')
    if not secret_key:
        return None
    try:
        import stripe
        stripe.api_key = secret_key
        return stripe
    except ImportError:
        return None


@bp.route('/stripe-status', methods=['GET'])
def stripe_status():
    """Check if Stripe is configured for this artist."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    stripe_client = _get_stripe_client(artist_slug)
    if not stripe_client:
        return jsonify({'configured': False})
    # Test the key by fetching account info
    try:
        account = stripe_client.Account.retrieve()
        # Extract account name safely — Stripe objects use attribute access
        account_name = ''
        try:
            bp = account.business_profile
            if bp and bp.name:
                account_name = bp.name
        except:
            pass
        if not account_name:
            try:
                account_name = account.settings.dashboard.display_name or ''
            except:
                pass
        return jsonify({
            'configured': True,
            'account_name': account_name or account.id,
            'account_id': account.id
        })
    except Exception as e:
        return jsonify({'configured': False, 'error': str(e)})


@bp.route('/stripe-products', methods=['GET'])
def stripe_list_products():
    """List products from the artist's Stripe account."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    stripe_client = _get_stripe_client(artist_slug)
    if not stripe_client:
        return jsonify({'error': 'Stripe not configured'}), 400
    try:
        products = stripe_client.Product.list(limit=100, active=True, expand=['data.default_price'])
        result = []
        for p in products.data:
            price_info = None
            if p.default_price:
                dp = p.default_price
                price_info = {
                    'id': dp.id,
                    'amount': dp.unit_amount,
                    'currency': dp.currency,
                    'formatted': f"{dp.unit_amount / 100:.2f} {dp.currency.upper()}"
                }
            result.append({
                'id': p.id,
                'name': p.name,
                'description': p.description or '',
                'images': p.images or [],
                'active': p.active,
                'default_price': price_info,
                'metadata': dict(p.metadata) if p.metadata else {}
            })
        return jsonify({'products': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stripe-create-product', methods=['POST'])
def stripe_create_product():
    """Create a product with a price in the artist's Stripe account."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    stripe_client = _get_stripe_client(artist_slug)
    if not stripe_client:
        return jsonify({'error': 'Stripe not configured'}), 400

    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    price_cents = data.get('price_cents', 0)
    currency = data.get('currency', 'gbp').lower()
    image_url = data.get('image_url', '')

    if not name or not price_cents:
        return jsonify({'error': 'Name and price are required'}), 400

    try:
        create_args = {
            'name': name,
            'default_price_data': {
                'currency': currency,
                'unit_amount': int(price_cents),
            },
            'metadata': {'artist': artist_slug}
        }
        if description:
            create_args['description'] = description
        if image_url:
            create_args['images'] = [image_url]

        product = stripe_client.Product.create(**create_args)
        return jsonify({
            'success': True,
            'product_id': product.id,
            'price_id': product.default_price
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stripe-update-product', methods=['POST'])
def stripe_update_product():
    """Update a product in the artist's Stripe account."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    stripe_client = _get_stripe_client(artist_slug)
    if not stripe_client:
        return jsonify({'error': 'Stripe not configured'}), 400

    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400

    try:
        update_args = {}
        if 'name' in data:
            update_args['name'] = data['name']
        if 'description' in data:
            update_args['description'] = data['description']
        if 'active' in data:
            update_args['active'] = data['active']
        if 'image_url' in data:
            update_args['images'] = [data['image_url']] if data['image_url'] else []

        product = stripe_client.Product.modify(product_id, **update_args)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stripe-delete-product', methods=['POST'])
def stripe_delete_product():
    """Archive (deactivate) a product."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    stripe_client = _get_stripe_client(artist_slug)
    if not stripe_client:
        return jsonify({'error': 'Stripe not configured'}), 400

    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400

    try:
        stripe_client.Product.modify(product_id, active=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stripe-scaffold', methods=['POST'])
def stripe_scaffold():
    """Scaffold default Stripe checkout + webhook routes into the artist's api.py."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    artist_path = get_artist_path(artist_slug)
    api_file = artist_path / 'api.py'

    # Check if stripe routes already exist
    if api_file.exists():
        existing = api_file.read_text()
        if 'stripe' in existing.lower() and 'checkout' in existing.lower():
            return jsonify({'success': True, 'message': 'Stripe routes already exist in api.py'})

    # Get the artist's domain for success/cancel URLs
    config_file = artist_path / 'config.json'
    domain = ''
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            domain = config.get('domain', '')
        except:
            pass

    base_url = f'https://{domain}' if domain else f'https://adze.studio/artists/{artist_slug}'

    template = f'''import os
import json
from flask import Blueprint, jsonify, request
from pathlib import Path

bp = Blueprint('artist_{artist_slug}', __name__, url_prefix='/api/artists/{artist_slug}')

# Load .env
_env = {{}}
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for line in _env_path.read_text().strip().split('\\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            _env[k.strip()] = v.strip().strip('"').strip("'")


# ── Stripe Checkout ──────────────────────────────────────────────────────

@bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe Checkout Session and return the URL."""
    import stripe
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    if not stripe.api_key:
        return jsonify({{'error': 'Stripe not configured'}}), 400

    data = request.get_json()
    price_id = data.get('price_id')
    if not price_id:
        return jsonify({{'error': 'price_id required'}}), 400

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{{'price': price_id, 'quantity': 1}}],
            success_url='{base_url}/shop-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='{base_url}/shop',
            shipping_address_collection={{'allowed_countries': ['GB', 'US', 'CA', 'AU', 'DE', 'FR', 'NL', 'IE']}},
            metadata={{'artist': '{artist_slug}'}},
        )
        return jsonify({{'url': session.url}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400


@bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events (payment confirmations, etc.)."""
    import stripe
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    endpoint_secret = _env.get('STRIPE_ENDPOINT_SECRET', '')

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')

    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return 'Invalid payload', 400
        except stripe.error.SignatureVerificationError:
            return 'Invalid signature', 400
    else:
        # No webhook secret configured — parse but don't verify (dev mode)
        event = json.loads(payload)

    event_type = event.get('type', '')

    if event_type == 'checkout.session.completed':
        session_data = event['data']['object']
        # Store the order
        orders_file = Path(__file__).parent / 'orders.json'
        orders = []
        if orders_file.exists():
            try:
                orders = json.loads(orders_file.read_text())
            except:
                pass
        orders.append({{
            'session_id': session_data.get('id'),
            'customer_email': session_data.get('customer_details', {{}}).get('email', ''),
            'amount_total': session_data.get('amount_total'),
            'currency': session_data.get('currency'),
            'status': session_data.get('payment_status'),
            'created': session_data.get('created'),
            'shipping': session_data.get('shipping_details'),
        }})
        orders_file.write_text(json.dumps(orders, indent=2))

    return 'OK', 200


@bp.route('/orders', methods=['GET'])
def list_orders():
    """List orders (for dashboard use — requires auth header check in production)."""
    orders_file = Path(__file__).parent / 'orders.json'
    if not orders_file.exists():
        return jsonify({{'orders': []}})
    try:
        orders = json.loads(orders_file.read_text())
        return jsonify({{'orders': orders}})
    except:
        return jsonify({{'orders': []}})
'''

    try:
        if api_file.exists():
            # Append to existing api.py
            existing = api_file.read_text()
            # Add imports and routes after the existing blueprint
            stripe_section = f'''

# ── Stripe Checkout (auto-scaffolded by Adze Studio) ─────────────────────
# Customise this! The Terminal Access can modify the webhook handler,
# add email notifications, inventory tracking, etc.

@bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe Checkout Session and return the URL."""
    import stripe
    _env_path = Path(__file__).parent / '.env'
    _env = {{}}
    if _env_path.exists():
        for line in _env_path.read_text().strip().split('\\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                _env[k.strip()] = v.strip().strip('"').strip("'")
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    if not stripe.api_key:
        return jsonify({{'error': 'Stripe not configured'}}), 400

    data = request.get_json()
    price_id = data.get('price_id')
    if not price_id:
        return jsonify({{'error': 'price_id required'}}), 400

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{{'price': price_id, 'quantity': 1}}],
            success_url='{base_url}/shop-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='{base_url}/shop',
            shipping_address_collection={{'allowed_countries': ['GB', 'US', 'CA', 'AU', 'DE', 'FR', 'NL', 'IE']}},
            metadata={{'artist': '{artist_slug}'}},
        )
        return jsonify({{'url': session.url}})
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400


@bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    import stripe
    _env_path = Path(__file__).parent / '.env'
    _env = {{}}
    if _env_path.exists():
        for line in _env_path.read_text().strip().split('\\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                _env[k.strip()] = v.strip().strip('"').strip("'")
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    endpoint_secret = _env.get('STRIPE_ENDPOINT_SECRET', '')

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')

    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError):
            return 'Invalid', 400
    else:
        event = json.loads(payload)

    if event.get('type') == 'checkout.session.completed':
        session_data = event['data']['object']
        orders_file = Path(__file__).parent / 'orders.json'
        orders = []
        if orders_file.exists():
            try: orders = json.loads(orders_file.read_text())
            except: pass
        orders.append({{
            'session_id': session_data.get('id'),
            'customer_email': session_data.get('customer_details', {{}}).get('email', ''),
            'amount_total': session_data.get('amount_total'),
            'currency': session_data.get('currency'),
            'status': session_data.get('payment_status'),
            'created': session_data.get('created'),
            'shipping': session_data.get('shipping_details'),
        }})
        orders_file.write_text(json.dumps(orders, indent=2))

    return 'OK', 200


@bp.route('/orders', methods=['GET'])
def list_orders():
    """List orders."""
    orders_file = Path(__file__).parent / 'orders.json'
    if not orders_file.exists():
        return jsonify({{'orders': []}})
    try:
        return jsonify({{'orders': json.loads(orders_file.read_text())}})
    except:
        return jsonify({{'orders': []}})
'''
            with open(api_file, 'a') as f:
                f.write(stripe_section)
        else:
            # Write fresh api.py
            with open(api_file, 'w') as f:
                f.write(template)

        # Auto-restart the server so the new routes are picked up
        try:
            deploy_script = Path.cwd() / 'deploy.sh'
            if deploy_script.exists():
                subprocess.Popen(['bash', str(deploy_script)],
                                 cwd=str(Path.cwd()),
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        except Exception:
            pass  # Non-critical — user can restart manually

        return jsonify({
            'success': True,
            'message': 'Stripe routes scaffolded and server restarting',
            'webhook_url': f'{base_url.rstrip("/")}/api/artists/{artist_slug}/stripe-webhook',
            'checkout_url': f'/api/artists/{artist_slug}/create-checkout'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Claude Code Terminal ──────────────────────────────────────────────────

# Track active Claude sessions per artist: { artist_slug: session_id }
# Persisted to disk so sessions survive server restarts
import threading
import uuid
import time

_CLAUDE_SESSIONS_FILE = Path(__file__).parent.parent / '_claude_sessions.json'
_VIBE_SESSIONS_DIR = Path(__file__).parent.parent / '_vibe_sessions'

def _load_claude_sessions():
    try:
        if _CLAUDE_SESSIONS_FILE.exists():
            return json.loads(_CLAUDE_SESSIONS_FILE.read_text())
    except:
        pass
    return {}

def _save_claude_sessions(sessions):
    try:
        _CLAUDE_SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))
    except:
        pass

_claude_sessions = _load_claude_sessions()

# Track active Claude CLI processes per artist for halt functionality
_claude_processes = {}  # artist_slug -> subprocess.Popen
# Per-artist streaming lock: prevents two users from running Claude simultaneously
_claude_streaming = {}  # artist_slug -> { 'since': timestamp, 'prompt': str }

# Per-artist Terminal Access tab presence. Tabs heartbeat; a "take over"
# marks the caller as the primary tab but does not kick other tabs because
# Terminal Access is a shared tmux session.
# SSH / direct filesystem edits are invisible here by design.
_vibe_presence = {}       # artist_slug -> {'epoch': int, 'tabs': {tab_id: last_seen_ts}, 'kicked': {tab_id: kicked_at_ts}}
_vibe_presence_lock = _threading.Lock()
_VIBE_PRESENCE_STALE_S = 15   # live tabs idle longer than this are pruned
_VIBE_KICKED_TTL_S = 60 * 30  # forget kicked tab ids after this (bounded memory)


def _vibe_prune_locked(slot):
    """Drop stale live tabs and expired kicked entries. Caller holds the lock."""
    now = _time.time()
    slot['tabs'] = {tid: ts for tid, ts in slot['tabs'].items() if now - ts < _VIBE_PRESENCE_STALE_S}
    slot['kicked'] = {tid: ts for tid, ts in slot['kicked'].items() if now - ts < _VIBE_KICKED_TTL_S}


def _vibe_slot_locked(artist_slug):
    return _vibe_presence.setdefault(artist_slug, {'epoch': 0, 'tabs': {}, 'kicked': {}})


@bp.route('/vibe-presence/heartbeat', methods=['POST'])
def vibe_presence_heartbeat():
    """
    Heartbeat for a Terminal Access browser tab.
    Body: {tab_id}
    Returns: {ok, epoch, kicked, others: [{idle_s}]}
    `kicked` is kept for old clients but is always false.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json(silent=True) or {}
    tab_id = (data.get('tab_id') or '').strip()
    if not tab_id or len(tab_id) > 64:
        return jsonify({'error': 'tab_id required'}), 400
    now = _time.time()
    with _vibe_presence_lock:
        slot = _vibe_slot_locked(artist_slug)
        _vibe_prune_locked(slot)
        slot['kicked'].pop(tab_id, None)
        slot['tabs'][tab_id] = now
        others = [
            {'idle_s': round(now - ts, 1)}
            for tid, ts in slot['tabs'].items()
            if tid != tab_id
        ]
        return jsonify({
            'ok': True,
            'epoch': slot['epoch'],
            'kicked': False,
            'others': others,
        })


@bp.route('/vibe-presence/takeover', methods=['POST'])
def vibe_presence_takeover():
    """
    Bump the epoch and mark the caller as the primary live tab. Other tabs
    are left connected; they can continue watching or typing into the same
    tmux session.
    Body: {tab_id}
    Returns: {ok, epoch}
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json(silent=True) or {}
    tab_id = (data.get('tab_id') or '').strip()
    if not tab_id or len(tab_id) > 64:
        return jsonify({'error': 'tab_id required'}), 400
    now = _time.time()
    with _vibe_presence_lock:
        slot = _vibe_slot_locked(artist_slug)
        _vibe_prune_locked(slot)
        slot['epoch'] += 1
        slot['tabs'] = {tab_id: now}
        # If the caller was previously kicked (shouldn't normally happen but be safe), clear it.
        slot['kicked'].pop(tab_id, None)
        return jsonify({'ok': True, 'epoch': slot['epoch']})


def _load_docs() -> str:
    """Read all *.md files from _shared/docs/ in filename order and concatenate them."""
    docs_dir = Path(__file__).parent / 'docs'
    if not docs_dir.exists():
        return ''
    parts = []
    for f in sorted(docs_dir.glob('[0-9]*.md')):
        try:
            parts.append(f.read_text(encoding='utf-8'))
        except Exception:
            pass
    return '\n\n---\n\n'.join(parts)


def _build_external_system_prompt(artist_slug):
    """
    System prompt for an external (remote Seed) artist. Dramatically shorter
    than the local prompt — Seed's own CLAUDE.md does the orientation work.
    Three short paragraphs: where you are, who you're talking to, how to
    build. Then the remote CLAUDE.md inlined.
    """
    import external_artist as _ext
    import remote_fs as _rfs

    try:
        manifest = _rfs.fetch_manifest(artist_slug)
    except _rfs.RemoteError as exc:
        manifest = _ext.cached_manifest(artist_slug) or _ext.manifest_defaults(artist_slug)
        _vibe_log.warning(f'[{artist_slug}] manifest fetch failed: {exc}; using cache/defaults')

    cfg = _ext.load_remote_config(artist_slug) or {}
    host = cfg.get('host', '?')
    path = cfg.get('path', '?')

    readme_text = ''
    readme_path = manifest.get('readme_path') or 'CLAUDE.md'
    try:
        readme_text = _rfs.read(artist_slug, readme_path)
    except (_rfs.RemoteError, FileNotFoundError) as exc:
        readme_text = f'(could not read {readme_path}: {exc})'

    client_brief = manifest.get('client_brief') or ''
    client_block = f'\nAbout the user: {client_brief}\n' if client_brief else '\n'

    return f"""You are the Terminal Access for an external Seed deployment.

Repo location: {host}:{path}. Treat it as your working directory; all
filesystem and shell tools are scoped to it transparently.

Build: when you change source files, run `{manifest.get('build_command', 'python3 compile.py')}`.
This deployment uses `build_on: agent` — the build does not run automatically.
Preview lives at {manifest.get('preview_url') or '(not set)'}.
{client_block}You are talking to a non-technical client. Prefer small, reversible edits;
ask before destructive operations; explain in plain language what you're
about to do, then do it. Do not produce large rewrites without confirming.

Project conventions live in the file below — it is the authoritative
orientation. Read sub-directory CLAUDE.md files (via Read) when working
in those areas.

---

{readme_text}
"""


def _get_artist_system_prompt(artist_slug):
    """
    Build the system prompt for the Terminal Access.
    Static foundation = docs/*.md files (single source of truth).
    Runtime context = artist-specific data appended at the end.

    For external (remote Seed) artists, returns a much shorter prompt that
    defers to Seed's own CLAUDE.md — see _build_external_system_prompt.
    """
    import external_artist as _ext
    if _ext.is_remote(artist_slug):
        return _build_external_system_prompt(artist_slug)

    artist_path = get_artist_path(artist_slug)
    config_path = artist_path / 'config.json'
    abs_artist_path = str(Path.cwd() / artist_path)

    artist_config = {}
    if config_path.exists():
        try:
            artist_config = json.loads(config_path.read_text())
        except Exception:
            pass

    artist_name  = artist_config.get('name', artist_slug)
    description  = artist_config.get('description', '')
    features     = artist_config.get('features', [])

    pages = []
    for d in sorted(artist_path.iterdir()):
        if d.is_dir() and d.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups'):
            if (d / 'content.md').exists():
                pages.append(d.name)
    pages_str = ', '.join(pages) if pages else 'none yet'

    has_api = (artist_path / 'api.py').exists()

    # Build installed widget manifest — inline README content so Claude can access it
    # regardless of sandbox restrictions (acceptEdits mode limits file reads to artist dir)
    platform_widgets_dir = Path(__file__).parent / 'widgets'
    enabled_platform = artist_config.get('platform_widgets', [])
    widget_blocks = []

    def _read_readme(path):
        try:
            return path.read_text(encoding='utf-8').strip()
        except Exception:
            return None

    # T2: platform widgets the artist has enabled
    for name in enabled_platform:
        readme_content = _read_readme(platform_widgets_dir / name / 'README.md')
        if readme_content:
            widget_blocks.append(readme_content)
        else:
            meta_path = platform_widgets_dir / name / 'widget.json'
            desc = ''
            try:
                desc = json.loads(meta_path.read_text()).get('description', '')
            except Exception:
                pass
            widget_blocks.append(f'### {name} (T2 platform)\n{desc}')

    # T4: artist's own widgets directory
    artist_widgets_dir = artist_path / 'widgets'
    if artist_widgets_dir.exists():
        for item in sorted(artist_widgets_dir.iterdir()):
            if item.is_file() and item.suffix == '.js':
                wname = item.stem
                readme_path = artist_widgets_dir / f'{wname}' / 'README.md'
                meta_path = artist_widgets_dir / f'{wname}.json'
            elif item.is_dir() and (item / 'widget.js').exists():
                wname = item.name
                readme_path = item / 'README.md'
                meta_path = item / 'widget.json'
            else:
                continue
            readme_content = _read_readme(readme_path)
            if readme_content:
                widget_blocks.append(readme_content)
            else:
                desc = ''
                tier = 'T4 custom'
                try:
                    m = json.loads(meta_path.read_text())
                    desc = m.get('description', '')
                    if m.get('forked_from'):
                        tier = 'T4 forked'
                except Exception:
                    pass
                widget_blocks.append(f'### {wname} ({tier})\n{desc}')

    widgets_section = ''
    if widget_blocks:
        widgets_section = '\n\n## Installed widgets\n\n' + '\n\n---\n\n'.join(widget_blocks)
    else:
        widgets_section = '\n\n## Installed widgets\n\nNone installed yet.'

    runtime_context = f"""---

## Runtime context (this session)

- Artist: {artist_name}
- Slug: {artist_slug}
- Description: {description}
- Working directory: {abs_artist_path}
- Current pages: {pages_str}
- Custom api.py: {'yes — read it before making backend changes' if has_api else 'no — create one if needed'}
- Active features: {', '.join(features) if features else 'none'}
{widgets_section}

You are STRICTLY sandboxed to {abs_artist_path}. All file operations must be within it.
Page slugs must always start with "artists/{artist_slug}/" — never bare slugs."""

    return _load_docs() + '\n\n' + runtime_context


@bp.route('/claude-stream', methods=['POST'])
def claude_stream():
    """Retired API-credit Terminal Access endpoint.

    Terminal Access now runs Claude Code directly through the Socket.IO pty
    bridge, so this endpoint intentionally refuses requests instead of burning
    OpenRouter/API credits.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    return jsonify({
        'error': 'The API-credit Terminal Access has been retired. Use Terminal Access.',
        'terminal_access': True,
    }), 410


@bp.route('/list-vibe-files', methods=['GET'])
def list_vibe_files():
    """List artist files for the @-mention picker. Excludes large/binary subtrees."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    artist_path = get_artist_path(artist_slug)
    if not artist_path.exists():
        return jsonify({'files': []})
    excluded_dirs = {'assets', '.snapshots', '__pycache__', 'backups', 'widgets'}
    files = []
    for p in sorted(artist_path.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(artist_path)
        parts = set(rel.parts)
        if parts & excluded_dirs:
            continue
        if p.name.startswith('.') or p.name.endswith(('.pyc', '.db', '.db-shm', '.db-wal', '.bak')):
            continue
        files.append(str(rel))
        if len(files) >= 500:
            break
    return jsonify({'files': files})


@bp.route('/vibe/reset', methods=['POST'])
def vibe_reset():
    """Retired Terminal Access reset endpoint kept for old clients."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    return jsonify({
        'ok': True,
        'message': 'Terminal Access uses the live Claude Code terminal. Use /clear there if needed.',
    })


@bp.route('/claude-stream-legacy', methods=['POST'])
def claude_stream_legacy():
    """Retired prompt-mode Claude subprocess endpoint."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)
    return jsonify({
        'error': 'Prompt-mode Claude streaming has been retired. Use Terminal Access.',
        'terminal_access': True,
    }), 410

    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400

    _vibe_log.info(f'[{artist_slug}] ── PROMPT ── {prompt}')

    # Per-artist mutex — only one Claude stream at a time
    active = _claude_streaming.get(artist_slug)
    if active:
        # Check if the process is actually still running
        proc = _claude_processes.get(artist_slug)
        if proc and proc.poll() is None:
            return jsonify({
                'error': 'Terminal Access is busy',
                'busy': True,
                'since': active['since'],
            }), 409
        else:
            # Process finished but wasn't cleaned up
            _claude_streaming.pop(artist_slug, None)

    _claude_streaming[artist_slug] = {'since': time.time(), 'prompt': prompt[:100]}

    artist_path = get_artist_path(artist_slug)
    abs_artist_path = str(Path.cwd() / artist_path)

    # Get or create session ID for this artist
    session_id = _claude_sessions.get(artist_slug)
    session_exists = session_id is not None

    if not session_exists:
        session_id = str(uuid.uuid4())
        _claude_sessions[artist_slug] = session_id
        _save_claude_sessions(_claude_sessions)

        # Auto-snapshot before new Terminal Access session
        try:
            import tarfile, time as _time
            snap_dir = artist_path / '.snapshots'
            snap_dir.mkdir(exist_ok=True)
            ts = _time.strftime('%Y-%m-%dT%H-%M-%S', _time.gmtime())
            snap_path = snap_dir / f'{ts}_auto-before-vibe-coder.tar.gz'
            _excl = {'assets', 'widgets', '.snapshots', '__pycache__', 'backups', '.env'}
            with tarfile.open(str(snap_path), 'w:gz') as tar:
                for item in sorted(artist_path.iterdir()):
                    if item.name not in _excl:
                        tar.add(str(item), arcname=item.name)
            # Prune to 30
            for old in sorted(snap_dir.glob('*.tar.gz'), reverse=True)[30:]:
                old.unlink()
        except Exception:
            pass  # Don't block the session if snapshot fails

    system_prompt = _get_artist_system_prompt(artist_slug)

    # Find claude binary path
    claude_bin = shutil.which('claude') or '/usr/local/bin/claude'

    # Build claude CLI args
    args = [
        claude_bin,
        '-p', prompt,
        '--output-format', 'stream-json',
        '--verbose',
    ]

    if session_exists:
        args.extend(['--resume', session_id])
    else:
        args.extend(['--session-id', session_id])
        args.extend(['--system-prompt', system_prompt])

    # acceptEdits mode: auto-approves file operations within cwd (the artist dir)
    # but BLOCKS access to files outside cwd (other artists, system files, _shared)
    # This is enforced by Claude CLI at the permission level — not just prompt-based
    args.extend(['--permission-mode', 'acceptEdits'])

    # Pre-approve a wide set of Bash commands so they don't need interactive approval.
    # acceptEdits already sandboxes file tools to the artist dir.
    # If a command isn't listed here, it fails gracefully (Claude says it can't do it).
    # Deliberately excluded: sudo, su, systemctl, apt, dpkg, mount, chroot, iptables,
    #                        ssh, scp, rsync (to remote), passwd, useradd, userdel,
    #                        shutdown, reboot, kill, killall, pkill, dd, mkfs, fdisk
    allowed_tools = [
        'Read', 'Write', 'Edit', 'Glob', 'Grep',
        # File operations
        'Bash(ls:*)', 'Bash(mkdir:*)', 'Bash(cp:*)', 'Bash(mv:*)', 'Bash(rm:*)',
        'Bash(touch:*)', 'Bash(chmod:*)', 'Bash(chown:*)', 'Bash(ln:*)',
        'Bash(basename:*)', 'Bash(dirname:*)', 'Bash(realpath:*)', 'Bash(readlink:*)',
        'Bash(find:*)', 'Bash(tree:*)', 'Bash(pwd:*)', 'Bash(cd:*)',
        'Bash(stat:*)', 'Bash(file:*)', 'Bash(du:*)', 'Bash(df:*)',
        # Text processing
        'Bash(cat:*)', 'Bash(head:*)', 'Bash(tail:*)', 'Bash(wc:*)',
        'Bash(sort:*)', 'Bash(uniq:*)', 'Bash(diff:*)', 'Bash(comm:*)',
        'Bash(sed:*)', 'Bash(awk:*)', 'Bash(tr:*)', 'Bash(cut:*)', 'Bash(paste:*)',
        'Bash(grep:*)', 'Bash(egrep:*)', 'Bash(fgrep:*)', 'Bash(rg:*)',
        'Bash(xargs:*)', 'Bash(tee:*)', 'Bash(rev:*)', 'Bash(fold:*)',
        # Output
        'Bash(echo:*)', 'Bash(printf:*)', 'Bash(yes:*)',
        # Scripting / languages
        'Bash(python3:*)', 'Bash(python:*)', 'Bash(node:*)', 'Bash(npx:*)',
        'Bash(ruby:*)', 'Bash(perl:*)', 'Bash(php:*)', 'Bash(bash:*)', 'Bash(sh:*)',
        # Package / dependency management (within project)
        'Bash(pip:*)', 'Bash(pip3:*)', 'Bash(npm:*)', 'Bash(yarn:*)', 'Bash(pnpm:*)',
        # Network / HTTP
        'Bash(curl:*)', 'Bash(wget:*)', 'Bash(http:*)',
        # Archives
        'Bash(tar:*)', 'Bash(gzip:*)', 'Bash(gunzip:*)', 'Bash(bzip2:*)',
        'Bash(zip:*)', 'Bash(unzip:*)', 'Bash(7z:*)', 'Bash(xz:*)',
        # Image / audio / video processing
        'Bash(convert:*)', 'Bash(identify:*)', 'Bash(mogrify:*)', 'Bash(composite:*)',
        'Bash(ffmpeg:*)', 'Bash(ffprobe:*)', 'Bash(sox:*)', 'Bash(soxi:*)',
        'Bash(aplay:*)', 'Bash(arecord:*)', 'Bash(lame:*)', 'Bash(oggenc:*)',
        'Bash(magick:*)', 'Bash(gifsicle:*)', 'Bash(optipng:*)', 'Bash(pngquant:*)',
        # Data / encoding
        'Bash(jq:*)', 'Bash(base64:*)', 'Bash(md5sum:*)', 'Bash(sha256sum:*)',
        'Bash(openssl:*)', 'Bash(xxd:*)', 'Bash(od:*)',
        # System info (read-only)
        'Bash(date:*)', 'Bash(env:*)', 'Bash(which:*)', 'Bash(whoami:*)',
        'Bash(hostname:*)', 'Bash(uname:*)', 'Bash(id:*)', 'Bash(test:*)',
        'Bash(true:*)', 'Bash(false:*)', 'Bash(sleep:*)',
        # Git (read-only operations mostly, but allow all)
        'Bash(git:*)',
        # Web tools
        'WebFetch', 'WebSearch',
    ]
    args.extend(['--allowedTools'] + allowed_tools)

    def _stream_proc(run_args):
        """Run claude CLI and yield SSE lines. Returns stderr string on exit."""
        env = os.environ.copy()
        env.pop('CLAUDECODE', None)
        _vibe_log.info(f'[{artist_slug}] ── START (session={session_id}) ──')
        proc = subprocess.Popen(
            run_args,
            cwd=abs_artist_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=1,
        )
        _claude_processes[artist_slug] = proc
        buffer = ''
        for chunk in iter(lambda: proc.stdout.read(4096), b''):
            buffer += chunk.decode('utf-8', errors='replace')
            lines = buffer.split('\n')
            buffer = lines[-1]
            for line in lines[:-1]:
                line = line.strip()
                if line:
                    # Log meaningful events (text, tool use, errors) but skip raw deltas
                    try:
                        evt = json.loads(line)
                        etype = evt.get('type', '')
                        if etype == 'assistant' and evt.get('message', {}).get('content'):
                            for block in evt['message']['content']:
                                btype = block.get('type', '')
                                if btype == 'text':
                                    _vibe_log.info(f'[{artist_slug}] TEXT: {block["text"][:500]}')
                                elif btype == 'tool_use':
                                    inp = json.dumps(block.get('input', ''))
                                    if len(inp) > 300:
                                        inp = inp[:300] + '…'
                                    _vibe_log.info(f'[{artist_slug}] TOOL: {block.get("name")} → {inp}')
                        elif etype == 'result' and evt.get('result'):
                            _vibe_log.info(f'[{artist_slug}] RESULT: cost=${evt.get("cost_usd", "?")} duration={evt.get("duration_ms", "?")}ms')
                    except (json.JSONDecodeError, KeyError):
                        pass
                    yield ('data', line)
        if buffer.strip():
            yield ('data', buffer.strip())
        proc.wait()
        stderr_out = proc.stderr.read().decode('utf-8', errors='replace').strip()
        rc = proc.returncode
        if rc == 0:
            _vibe_log.info(f'[{artist_slug}] ── END (ok) ──')
        else:
            _vibe_log.info(f'[{artist_slug}] ── END (exit={rc}) ── {stderr_out[:500]}')
        yield ('done', str(rc) + '|' + stderr_out)

    def generate():
        try:
            had_session_reset = False
            current_args = args[:]

            for event_type, payload in _stream_proc(current_args):
                if event_type == 'data':
                    yield f"data: {payload}\n\n"
                elif event_type == 'done':
                    returncode, stderr_out = payload.split('|', 1)
                    returncode = int(returncode)

                    if returncode != 0:
                        is_session_error = (
                            'no conversation found' in stderr_out.lower() or
                            ('session' in stderr_out.lower() and 'not found' in stderr_out.lower()) or
                            'invalid session' in stderr_out.lower()
                        )

                        if is_session_error and not had_session_reset:
                            # Clear stale session and retry with a fresh one
                            _claude_sessions.pop(artist_slug, None)
                            _save_claude_sessions(_claude_sessions)

                            new_session_id = str(uuid.uuid4())
                            _claude_sessions[artist_slug] = new_session_id
                            _save_claude_sessions(_claude_sessions)

                            notice = json.dumps({'type': 'system_message', 'text': 'Starting new session...'})
                            yield f"data: {notice}\n\n"

                            # Rebuild args without --resume, with new session ID + system prompt
                            retry_args = [a for a in current_args if a not in ['--resume']]
                            # Remove old session id value (the UUID after --resume or --session-id)
                            clean_args = []
                            skip_next = False
                            for a in retry_args:
                                if skip_next:
                                    skip_next = False
                                    continue
                                if a in ('--resume', '--session-id'):
                                    skip_next = True
                                    continue
                                clean_args.append(a)

                            clean_args.extend(['--session-id', new_session_id])
                            clean_args.extend(['--system-prompt', _get_artist_system_prompt(artist_slug)])
                            had_session_reset = True

                            for event_type2, payload2 in _stream_proc(clean_args):
                                if event_type2 == 'data':
                                    yield f"data: {payload2}\n\n"
                                elif event_type2 == 'done':
                                    rc2, err2 = payload2.split('|', 1)
                                    if int(rc2) != 0 and err2:
                                        yield f"data: {json.dumps({'type': 'error', 'error': err2, 'exit_code': int(rc2)})}\n\n"
                        else:
                            if stderr_out:
                                yield f"data: {json.dumps({'type': 'error', 'error': stderr_out, 'exit_code': returncode})}\n\n"

            yield "data: {\"type\": \"stream_end\"}\n\n"

        except FileNotFoundError:
            error_data = json.dumps({
                'type': 'error',
                'error': 'Claude CLI not found. Is it installed?'
            })
            yield f"data: {error_data}\n\n"
        except Exception as e:
            error_data = json.dumps({
                'type': 'error',
                'error': str(e)
            })
            yield f"data: {error_data}\n\n"
        finally:
            _claude_streaming.pop(artist_slug, None)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
        }
    )


@bp.route('/list-endpoints', methods=['GET'])
def list_endpoints():
    """
    List all API endpoints relevant to this artist.
    Returns shared admin endpoints + any custom artist api.py endpoints.
    Headers: X-Artist-Slug, X-Admin-Token
    """
    from flask import current_app
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401, description='Authentication required')

    # Friendly descriptions for known shared endpoints
    SHARED_DESCRIPTIONS = {
        'list-pages': {'summary': 'List all your pages', 'detail': 'Returns a list of every page on your site with its title and slug.'},
        'get-page-content': {'summary': 'Get a page\'s content', 'detail': 'Fetches the HTML and CSS content for a specific page.'},
        'edit-page': {'summary': 'Update a page', 'detail': 'Save new content or config for one of your pages.'},
        'create-page': {'summary': 'Create a new page', 'detail': 'Add a brand new page to your site.'},
        'delete-page': {'summary': 'Delete a page', 'detail': 'Permanently remove a page from your site.'},
        'upload-file': {'summary': 'Upload a file', 'detail': 'Upload images, fonts, or other files to your assets.'},
        'list-assets': {'summary': 'List your files', 'detail': 'See all uploaded images, fonts, and other files.'},
        'artist-info': {'summary': 'Your site info', 'detail': 'Get your site name, description, and settings.'},
        'list-widgets': {'summary': 'List dashboard widgets', 'detail': 'See what custom tools are available in your dashboard.'},
        'check-domain': {'summary': 'Check domain status', 'detail': 'See if your custom domain is set up correctly (DNS, SSL, etc).'},
        'list-endpoints': {'summary': 'List API endpoints', 'detail': 'Returns this list of all available API endpoints (you\'re looking at it!).'},
        'export-site': {'summary': 'Export your site', 'detail': 'Downloads a .zip of your complete site — compiled HTML, assets, source files, and API code.'},
    }

    # Load feature descriptions dynamically
    feature_descriptions = {}
    try:
        from features import bookings as bookings_feature
        if hasattr(bookings_feature, 'ENDPOINT_DESCRIPTIONS'):
            feature_descriptions['bookings'] = bookings_feature.ENDPOINT_DESCRIPTIONS
    except ImportError:
        pass

    endpoints = []

    # Collect all routes from the Flask app
    for rule in current_app.url_map.iter_rules():
        route = rule.rule
        methods = sorted(rule.methods - {'HEAD', 'OPTIONS'})
        if not methods:
            continue

        # Shared admin endpoints (skip dashboard/streaming/internal)
        if route.startswith('/api/adze/'):
            short = route.replace('/api/adze/', '')
            if short in ('dashboard', 'get-widget', 'claude-stream', 'claude-reset'):
                continue
            desc = SHARED_DESCRIPTIONS.get(short, {})
            endpoints.append({
                'url': route,
                'methods': methods,
                'source': 'shared',
                'name': short,
                'summary': desc.get('summary', short.replace('-', ' ').title()),
                'detail': desc.get('detail', ''),
                'auth': True,
            })

        # Artist-scoped endpoints (features + custom api.py)
        elif f'/api/artists/{artist_slug}' in route:
            tail = route.split(f'/api/artists/{artist_slug}/')[-1] if f'/api/artists/{artist_slug}/' in route else route.split('/')[-1]
            parts = tail.split('/')

            # Check if this is a known feature (e.g. bookings/submit)
            feature_name = parts[0] if parts else ''
            endpoint_name = parts[1] if len(parts) > 1 else ''
            feat_descs = feature_descriptions.get(feature_name, {})
            ep_desc = feat_descs.get(endpoint_name, {})

            if ep_desc:
                # Known feature endpoint — use its descriptions
                endpoints.append({
                    'url': route,
                    'methods': methods,
                    'source': 'feature',
                    'feature': feature_name,
                    'name': tail,
                    'summary': ep_desc.get('summary', tail.replace('/', ' ').title()),
                    'detail': ep_desc.get('detail', ''),
                    'auth': ep_desc.get('auth', True),
                })
            else:
                # Custom api.py endpoint
                endpoints.append({
                    'url': route,
                    'methods': methods,
                    'source': 'custom',
                    'name': tail or 'root',
                    'summary': tail.replace('-', ' ').replace('_', ' ').replace('/', ' ').title() if tail else 'Custom Endpoint',
                    'detail': 'Custom endpoint defined in your api.py',
                    'auth': False,
                })

    # Sort: features first, then custom, then shared
    source_order = {'feature': 0, 'custom': 1, 'shared': 2}
    endpoints.sort(key=lambda e: (source_order.get(e['source'], 1), e['name']))

    # Check if artist has an api.py
    artist_path = get_artist_path(artist_slug)
    has_custom_api = (artist_path / 'api.py').exists()

    # Scan widgets for endpoint usage
    widget_files = {}  # name -> content
    shared_widgets_dir = Path(__file__).parent / 'widgets'
    for wf in shared_widgets_dir.glob('*/widget.js'):
        widget_files[wf.parent.name] = wf.read_text(encoding='utf-8', errors='ignore')
    artist_widgets_dir = artist_path / 'widgets'
    if artist_widgets_dir.exists():
        for wf in artist_widgets_dir.glob('*.js'):
            widget_files[wf.stem] = wf.read_text(encoding='utf-8', errors='ignore')

    # Extract URLs actually passed to fetch()/apiFetch() calls — avoids false positives from comments/strings
    _CALL_RE = re.compile(r"""(?:apiFetch|fetch)\s*\(\s*[`'"]((?:[^`'"\\]|\\.)+)[`'"]""")
    widget_called_urls = {
        name: set(_CALL_RE.findall(content))
        for name, content in widget_files.items()
    }

    for ep in endpoints:
        ep_url = ep['url']
        # Extract the trailing path segment for matching template-literal URLs
        # e.g. /api/artists/${ctx.artistSlug}/orders → match on 'orders'
        ep_tail = ep_url.rstrip('/').split('/')[-1]
        ep['used_by'] = [
            name for name, called in widget_called_urls.items()
            if any(
                ep_url in u                        # exact URL match
                or u in ep_url                     # URL is suffix of endpoint
                or (ep_tail and ep_tail in u.split('/')[-1])  # tail segment matches (handles ${slug} templates)
                for u in called
            )
        ]

    return jsonify({
        'endpoints': endpoints,
        'has_custom_api': has_custom_api,
        'custom_api_prefix': f'/api/artists/{artist_slug}',
    })


@bp.route('/claude-reset', methods=['POST'])
def claude_reset():
    """Reset retired prompt-mode state for the artist. Requires auth."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    # Refuse mid-stream — clearing during a turn would corrupt the conversation file
    active = _claude_streaming.get(artist_slug)
    if active and time.time() - active.get('since', 0) < 600:
        return jsonify({'error': 'Cannot reset while a turn is in flight', 'busy': True}), 409

    legacy_cleared = artist_slug in _claude_sessions
    _claude_sessions.pop(artist_slug, None)
    _save_claude_sessions(_claude_sessions)

    _vibe_log.info(f'[{artist_slug}] ── RESET (legacy={legacy_cleared}) ──')
    return jsonify({
        'ok': True,
        'message': 'Old prompt-mode session reset. Terminal Access uses the live Claude Code terminal.',
    })


@bp.route('/openrouter-usage', methods=['GET'])
def openrouter_usage():
    """Report OpenRouter total spend (USD) for the configured API key.

    Used by the Auto-Code cost meter — the dashboard snapshots `usage`
    when a session connects and shows the delta since.
    """
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    key = os.environ.get('OPENROUTER_API_KEY', '')
    if not key:
        return jsonify({'error': 'OPENROUTER_API_KEY not configured'}), 503

    try:
        import urllib.request
        req = urllib.request.Request(
            'https://openrouter.ai/api/v1/auth/key',
            headers={'Authorization': f'Bearer {key}'},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        data = payload.get('data', {}) if isinstance(payload, dict) else {}
        return jsonify({
            'usage': float(data.get('usage') or 0.0),
            'limit': data.get('limit'),
            'label': data.get('label'),
        })
    except Exception as exc:
        return jsonify({'error': f'OpenRouter lookup failed: {exc}'}), 502


@bp.route('/claude-halt', methods=['POST'])
def claude_halt():
    """Halt the running Claude process for the artist. Requires auth."""
    artist_slug = get_authenticated_artist()
    if not artist_slug:
        abort(401)

    proc = _claude_processes.get(artist_slug)
    if proc and proc.poll() is None:
        import signal
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        _claude_processes.pop(artist_slug, None)
        _claude_streaming.pop(artist_slug, None)
        return jsonify({'ok': True, 'message': 'Terminal Access stopped.'})
    else:
        _claude_processes.pop(artist_slug, None)
        _claude_streaming.pop(artist_slug, None)
        return jsonify({'ok': False, 'message': 'No active process to stop.'})
