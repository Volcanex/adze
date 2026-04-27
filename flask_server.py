#!/usr/bin/env python3
"""
Flask server that automatically registers API endpoints from page modules.
Each page can define its own Flask blueprint in api.py.
Includes WebSocket support for real-time features.
"""

import os
import sys
import importlib.util
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, send_file, request, redirect
from flask_cors import CORS
from flask_socketio import SocketIO
import psutil
import platform
import subprocess
from datetime import datetime
import socket
import threading

sys.path.insert(0, str(Path(__file__).parent / '_shared'))
from db import insert_pageview
import json
import re
import shutil

class BlogFlaskServer:
    def __init__(self, pages_dir=".", static_dir="output", port=5000):
        self.pages_dir = Path(pages_dir)
        self.static_dir = Path(static_dir)
        self.port = port
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB upload limit

        # CORS: allow adze.studio + all artist custom domains
        def _allowed_origins():
            origins = ['https://adze.studio', 'https://www.adze.studio']
            artists_dir = Path('artists')
            if artists_dir.exists():
                for item in artists_dir.iterdir():
                    cfg = item / 'config.json'
                    if item.is_dir() and cfg.exists():
                        try:
                            domain = json.load(open(cfg)).get('domain', '')
                            if domain:
                                origins.append(f'https://{domain}')
                                origins.append(f'https://www.{domain}')
                        except Exception:
                            pass
            return origins

        self._cors_origins = _allowed_origins()
        CORS(self.app, origins=self._cors_origins)

        # Initialize SocketIO with same CORS origins
        self.socketio = SocketIO(self.app, cors_allowed_origins=self._cors_origins)

        # Per-artist locks to prevent concurrent compile.py executions
        self._compile_locks = {}
        self._compile_locks_guard = threading.Lock()

        # GeoIP cache for analytics
        self._geoip_cache = {}

        # Setup analytics logging
        self._setup_analytics_logging()

        # Setup basic routes
        self._setup_basic_routes()

        # Register artist admin API
        self._register_artist_admin_api()

        # Register per-artist feature blueprints
        self._register_artist_features()

        # Auto-register page API endpoints and WebSocket handlers
        self._register_page_apis()

    # ── Analytics Logging ─────────────────────────────────────────────────

    BOT_STRINGS = ['bot', 'crawl', 'spider', 'slurp', 'wget', 'curl', 'fetch',
                   'scrape', 'headless', 'phantom', 'lighthouse', 'pingdom',
                   'uptimerobot', 'semrush', 'ahref', 'mj12', 'dotbot']

    SKIP_EXTENSIONS = {'.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.webp',
                       '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map',
                       '.mp4', '.mp3', '.pdf', '.zip'}

    # Minimal inline script to track session duration and page count for bounce rate.
    # Uses sessionStorage (no cookies, no PII), beacons duration on page unload.
    _TRACKING_SCRIPT = '''<script>(function(){
var sid=sessionStorage.getItem('_azs');
if(!sid){sid=Math.random().toString(36).slice(2);sessionStorage.setItem('_azs',sid)}
var pc=parseInt(sessionStorage.getItem('_azp')||'0',10)+1;
sessionStorage.setItem('_azp',String(pc));
var t0=Date.now();
function send(){
var d=Math.round((Date.now()-t0)/1000);
if(d<1)return;
var slug=location.pathname.split('/')[2]||'';
navigator.sendBeacon('/api/adze/beacon','sid='+sid+'&slug='+slug+'&dur='+d+'&pc='+pc)}
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden')send()});
window.addEventListener('pagehide',send);
})();</script>'''

    def _setup_analytics_logging(self):
        """Register an after_request hook to log page views and inject tracking for artist pages."""

        @self.app.after_request
        def log_analytics(response):
            try:
                self._log_page_view(response)
            except Exception:
                pass  # Never break the response for analytics
            try:
                self._inject_tracking_script(response)
            except Exception:
                pass
            return response

    def _inject_tracking_script(self, response):
        """Inject a tiny session tracking script into artist HTML pages."""
        if response.status_code != 200:
            return
        content_type = response.content_type or ''
        if 'text/html' not in content_type:
            return
        path = request.path
        if not path.startswith('/artists/'):
            return
        if '/api/' in path or '/dashboard' in path:
            return

        data = response.get_data(as_text=True)
        if '</body>' in data:
            data = data.replace('</body>', self._TRACKING_SCRIPT + '</body>', 1)
            response.set_data(data)
            response.headers['Content-Length'] = len(response.get_data())

    def _log_page_view(self, response):
        """Log a page view if it matches an artist page request."""
        path = request.path

        # Only log artist pages: /artists/{slug}/...
        if not path.startswith('/artists/'):
            return
        parts = path.strip('/').split('/')
        if len(parts) < 2:
            return
        artist_slug = parts[1]

        # Skip API calls, dashboard requests, asset files
        if '/api/' in path or '/dashboard' in path:
            return
        if any(path.lower().endswith(ext) for ext in self.SKIP_EXTENSIONS):
            return
        if path.startswith('/assets/'):
            return

        # Only log successful HTML responses
        content_type = response.content_type or ''
        if response.status_code != 200:
            return
        if 'text/html' not in content_type:
            return

        # Skip bots
        ua = (request.headers.get('User-Agent') or '').lower()
        if any(b in ua for b in self.BOT_STRINGS):
            return

        # Extract referrer domain
        ref = ''
        raw_ref = request.headers.get('Referer') or ''
        if raw_ref:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(raw_ref)
                ref = parsed.netloc or ''
                # Strip www. prefix
                if ref.startswith('www.'):
                    ref = ref[4:]
            except Exception:
                ref = ''

        # Get country from IP
        ip = request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or request.remote_addr or ''
        country = self._geoip_lookup(ip)

        # Build the page path relative to the artist (e.g. /home/, /gallery/)
        page_path = '/' + '/'.join(parts[2:]) + '/' if len(parts) > 2 else '/'

        import time
        entry = {
            'path': page_path,
            'ts': int(time.time()),
            'ref': ref,
            'country': country
        }

        # Write to per-artist SQLite database
        insert_pageview(artist_slug, page_path, entry['ts'], ref, country)

    def _geoip_lookup(self, ip):
        """Look up country from IP using ip-api.com with in-memory caching."""
        if not ip or ip in ('127.0.0.1', '::1', 'localhost'):
            return 'Local'

        if ip in self._geoip_cache:
            return self._geoip_cache[ip]

        try:
            import urllib.request
            url = f'http://ip-api.com/json/{ip}?fields=countryCode'
            req = urllib.request.Request(url, headers={'User-Agent': 'AdzeStudio/1.0'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                country = data.get('countryCode', 'Unknown')
        except Exception:
            country = 'Unknown'

        self._geoip_cache[ip] = country
        return country

    def _check_port_open(self, port, host='localhost', timeout=1):
        """Check if a port is open on the local machine"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _get_process_cpu_by_port(self, port):
        """Get CPU usage of process listening on a specific port"""
        try:
            # Use netstat/ss to find the PID listening on the port
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-t'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split('\n')[0])
                # Get CPU usage for this process
                proc = psutil.Process(pid)
                cpu_usage = proc.cpu_percent(interval=0.1)
                return cpu_usage
        except (FileNotFoundError, ValueError, psutil.NoSuchProcess, subprocess.TimeoutExpired):
            pass
        return None

    def _get_compile_lock(self, key='__global__'):
        """Get or create a per-artist (or global) compile lock."""
        with self._compile_locks_guard:
            if key not in self._compile_locks:
                self._compile_locks[key] = threading.Lock()
            return self._compile_locks[key]

    def _trigger_compile(self, artist_slug=None):
        """
        Trigger compile.py to regenerate static files.
        If artist_slug is provided, only that artist is compiled (per-artist lock).
        Otherwise compiles all artists (global lock).
        Returns dict with success status and details.
        """
        lock_key = artist_slug or '__global__'
        lock = self._get_compile_lock(lock_key)

        acquired = lock.acquire(blocking=False)
        if not acquired:
            return {
                'success': False,
                'error': 'Compile already in progress',
                'message': f'Compile already running for {artist_slug or "all artists"}'
            }

        try:
            compile_script = Path.cwd() / 'compile.py'

            if not compile_script.exists():
                return {
                    'success': False,
                    'error': 'compile.py not found',
                    'path': str(compile_script)
                }

            cmd = [sys.executable, str(compile_script)]
            if artist_slug:
                cmd += ['--artist', artist_slug]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd()
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Compile completed for {artist_slug or "all artists"}',
                    'stdout': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Compile failed',
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Compile timed out',
                'message': 'compile.py took longer than 60 seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Compile execution failed',
                'details': str(e)
            }
        finally:
            lock.release()

    def _get_artist_by_domain(self, domain):
        """
        Get artist slug by domain.
        Returns (artist_slug, base_path) or (None, None)
        """
        artists_dir = Path('artists')

        if not artists_dir.exists():
            return None, None

        for item in artists_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                config_file = item / 'config.json'
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            if config.get('domain') == domain:
                                return item.name, f"artists/{item.name}"
                    except (json.JSONDecodeError, IOError):
                        continue

        return None, None

    def _setup_basic_routes(self):
        """Setup basic Flask routes"""

        @self.app.route('/preview/<slug>/', defaults={'subpath': ''})
        @self.app.route('/preview/<slug>/<path:subpath>')
        def serve_preview(slug, subpath):
            """Same-origin preview of an artist site for embedding in iframes
            from other artist sites (e.g. lastplacesite's case-study tiles)."""
            artist_dir = Path('artists') / slug
            if not artist_dir.is_dir() or slug.startswith('_'):
                return jsonify({'error': f'Unknown artist: {slug}'}), 404
            artist_base = self.static_dir / 'artists' / slug

            # Redirect bare /preview/<slug>/ to /preview/<slug>/home/ so the
            # served HTML's relative asset paths (../assets/...) resolve here
            # the same way they do on the artist's real domain.
            if not subpath:
                return redirect(f'/preview/{slug}/home/', code=302)

            file_path = artist_base / subpath
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(artist_base), subpath)

            if '.' not in subpath.rsplit('/', 1)[-1]:
                idx = artist_base / subpath / 'index.html'
                if idx.exists():
                    return send_from_directory(str(artist_base / subpath), 'index.html')

            return jsonify({'error': f'File {subpath} not found for {slug}'}), 404

        @self.app.route('/')
        def serve_homepage():
            """Serve the homepage - supports domain-based routing for artist sites"""
            # Check if request is for an artist domain
            host = request.headers.get('Host', '').split(':')[0]  # Remove port if present
            artist_slug, artist_base = self._get_artist_by_domain(host)

            if artist_slug:
                # Serve artist's homepage (usually their 'home' page)
                try:
                    # Try to serve home/index.html
                    home_path = self.static_dir / artist_base / 'home' / 'index.html'
                    if home_path.exists():
                        return send_from_directory(str(self.static_dir / artist_base / 'home'), 'index.html')

                    # Fallback: try first available page
                    artist_dir = self.static_dir / artist_base
                    if artist_dir.exists():
                        for subdir in artist_dir.iterdir():
                            if subdir.is_dir():
                                index = subdir / 'index.html'
                                if index.exists():
                                    return send_from_directory(str(subdir), 'index.html')

                    return jsonify({'error': f'Artist homepage not found. Create a "home" page for {artist_slug}.'}), 404

                except FileNotFoundError:
                    return jsonify({'error': 'Artist homepage not found. Run compile.py first.'}), 404

            # Default blog homepage
            try:
                return send_from_directory(self.static_dir, 'index.html')
            except FileNotFoundError:
                return jsonify({'error': 'Homepage not found. Run compile.py first.'}), 404
        
        @self.app.route('/<path:filename>')
        def serve_static(filename):
            """Serve static HTML files (assets handled by nginx in production) - supports artist domains"""
            # Skip API routes (they're handled by blueprints)
            if filename.startswith('api/'):
                return jsonify({'error': f'File {filename} not found'}), 404

            # In production, assets are served by nginx directly
            # Only allow Flask to serve assets in development (when nginx not present)
            if filename.startswith('assets/'):
                # Check if we're in production by looking for nginx headers
                is_production = 'X-Real-IP' in request.headers or 'X-Forwarded-For' in request.headers
                if is_production:
                    return jsonify({'error': 'Assets should be served by nginx in production'}), 404
                # Development mode - allow Flask to serve assets for convenience

            # Check if request is for an artist domain
            host = request.headers.get('Host', '').split(':')[0]  # Remove port if present
            artist_slug, artist_base = self._get_artist_by_domain(host)

            if artist_slug:
                # Try to serve from artist's directory
                # First try exact file in artist's base directory
                artist_file_path = self.static_dir / artist_base / filename
                if artist_file_path.exists() and artist_file_path.is_file():
                    return send_from_directory(str(self.static_dir / artist_base), filename)

                # If no extension, try as a page (directory with index.html)
                if '.' not in filename:
                    artist_index_path = self.static_dir / artist_base / filename / "index.html"
                    if artist_index_path.exists():
                        return send_from_directory(str(self.static_dir / artist_base / filename), "index.html")

                return jsonify({'error': f'File {filename} not found for artist {artist_slug}'}), 404

            # Default blog behavior
            # First try the exact filename (must be a file, not directory)
            file_path = self.static_dir / filename
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(self.static_dir), filename)

            # If not found and no extension, try looking for directory/index.html
            if '.' not in filename:
                index_path = self.static_dir / filename / "index.html"
                if index_path.exists():
                    return send_from_directory(str(self.static_dir / filename), "index.html")

            return jsonify({'error': f'File {filename} not found'}), 404

    def _register_artist_admin_api(self):
        """Register the shared artist admin API blueprint"""
        admin_api_path = Path('_shared/admin_api.py')

        if not admin_api_path.exists():
            return

        try:
            # Load the admin API module
            spec = importlib.util.spec_from_file_location(
                "pages.artists._shared.admin_api",
                str(admin_api_path)
            )
            admin_module = importlib.util.module_from_spec(spec)

            # Add current directory to path so imports work
            if str(Path.cwd()) not in sys.path:
                sys.path.insert(0, str(Path.cwd()))

            spec.loader.exec_module(admin_module)

            # Register the blueprint if it exists
            if hasattr(admin_module, 'bp'):
                self.app.register_blueprint(admin_module.bp)
                print(f"Registered artist admin API endpoints")
            else:
                print(f"Warning: admin_api.py doesn't have a 'bp' blueprint")

        except Exception as e:
            print(f"Error loading artist admin API: {e}")

        # Register the aider WebSocket bridge (pty per artist over /aider namespace)
        try:
            import aider_bridge
            aider_bridge.register(self.socketio)
            print("Registered aider WebSocket bridge on /aider")
        except Exception as e:
            print(f"Error registering aider bridge: {e}")

    def _register_artist_features(self):
        """Register per-artist feature blueprints based on config.json features list."""
        artists_dir = Path('artists')
        features_dir = Path('_shared/features')

        if not artists_dir.exists() or not features_dir.exists():
            return

        # Add features dir to path so imports work
        features_parent = str(features_dir.parent)
        if features_parent not in sys.path:
            sys.path.insert(0, features_parent)

        registered = []

        for artist_dir in artists_dir.iterdir():
            if not artist_dir.is_dir() or artist_dir.name.startswith('_'):
                continue

            config_file = artist_dir / 'config.json'
            if not config_file.exists():
                continue

            try:
                with open(config_file) as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            features = config.get('features', [])
            artist_slug = artist_dir.name

            for feature_name in features:
                feature_file = features_dir / f'{feature_name}.py'
                if not feature_file.exists():
                    print(f"Warning: feature '{feature_name}' not found for artist '{artist_slug}'")
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(
                        f"features.{feature_name}",
                        str(feature_file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, 'create_blueprint'):
                        bp = module.create_blueprint(artist_slug)
                        self.app.register_blueprint(bp)
                        registered.append(f"{artist_slug}/{feature_name}")
                        print(f"  Registered feature '{feature_name}' for artist '{artist_slug}' -> {bp.url_prefix}")
                    else:
                        print(f"Warning: feature '{feature_name}' has no create_blueprint()")

                except Exception as e:
                    print(f"Error loading feature '{feature_name}' for artist '{artist_slug}': {e}")

        if registered:
            print(f"Registered {len(registered)} artist features: {', '.join(registered)}")

        @self.app.route('/test-asset')
        def test_asset():
            """Test route to check if routing works"""
            return jsonify({'message': 'Asset routing test successful'})
            
        @self.app.route('/api/artist-admin/dashboard')
        @self.app.route('/api/sandbox/dashboard')
        def old_dashboard_redirect():
            """Redirect old dashboard URLs to new one"""
            from flask import redirect
            return redirect('/api/adze/dashboard', code=301)

        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'pages_loaded': len(self._get_page_directories()),
                'static_dir': str(self.static_dir),
                'pages_dir': str(self.pages_dir)
            })

        @self.app.route('/api/server-details')
        def server_details():
            """Get server hardware and usage details"""
            try:
                # CPU info
                cpu_count = psutil.cpu_count(logical=False)
                cpu_logical = psutil.cpu_count(logical=True)
                cpu_model = platform.processor() or "Unknown"
                cpu_usage = psutil.cpu_percent(interval=0.1)

                # Get per-core CPU usage
                cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

                cpu_info = {
                    'model': cpu_model,
                    'cores': f"{cpu_count} cores / {cpu_logical} threads" if cpu_count else f"{cpu_logical} threads",
                    'usage_percent': round(cpu_usage, 1),
                    'per_core': [round(core, 1) for core in cpu_per_core]
                }

                # RAM info
                ram = psutil.virtual_memory()
                ram_info = {
                    'total_gb': round(ram.total / (1024**3), 1),
                    'usage_percent': round(ram.percent, 1)
                }

                # GPU info - try nvidia-smi
                gpu_info = {
                    'available': False,
                    'model': None,
                    'memory_gb': None,
                    'usage_percent': None
                }

                try:
                    result = subprocess.run(
                        ['nvidia-smi', '--query-gpu=name,memory.total,utilization.gpu', '--format=csv,noheader'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        gpu_line = result.stdout.strip().split('\n')[0]
                        parts = gpu_line.split(',')
                        if len(parts) >= 3:
                            gpu_info = {
                                'available': True,
                                'model': parts[0].strip(),
                                'memory_gb': parts[1].strip(),
                                'usage_percent': round(float(parts[2].strip().rstrip('%')), 1)
                            }
                except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
                    pass

                # OS info
                os_info = platform.platform()

                # Check Minecraft server on port 25565
                minecraft_healthy = self._check_port_open(25565)
                minecraft_cpu = self._get_process_cpu_by_port(25565) if minecraft_healthy else None

                # Get API (Flask) CPU usage - check port we're running on
                api_cpu = self._get_process_cpu_by_port(self.port)

                return jsonify({
                    'cpu': cpu_info,
                    'ram': ram_info,
                    'gpu': gpu_info,
                    'os': os_info,
                    'minecraft_healthy': minecraft_healthy,
                    'minecraft_cpu': minecraft_cpu,
                    'api_cpu': api_cpu,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
            except Exception as e:
                return jsonify({
                    'error': 'Failed to retrieve server details',
                    'details': str(e)
                }), 500

        @self.app.route('/api/pages')
        def list_pages():
            """List all available pages"""
            pages = []
            for page_dir in self._get_page_directories():
                config_file = page_dir / 'config.json'
                if config_file.exists():
                    try:
                        import json
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            # Compute slug from directory path for artist pages
                            config_slug = config.get('slug', page_dir.name)
                            try:
                                rel = page_dir.relative_to(self.pages_dir)
                                parts = rel.parts
                                if len(parts) >= 3 and parts[0] == 'artists' and not config_slug.startswith('artists/'):
                                    config_slug = str(rel)
                            except ValueError:
                                pass
                            pages.append({
                                'slug': config_slug,
                                'title': config.get('title', page_dir.name),
                                'description': config.get('description', ''),
                                'categories': config.get('categories', []),
                                'date': config.get('date', ''),
                                'hidden': config.get('hidden', False),
                                'has_api': (page_dir / 'api.py').exists(),
                                'has_assets': (page_dir / 'assets').exists()
                            })
                    except (json.JSONDecodeError, IOError):
                        continue
            
            # Sort by date (newest first)
            pages.sort(key=lambda x: x.get('date', ''), reverse=True)
            return jsonify({'pages': pages})

        @self.app.route('/api/widgets')
        def list_widgets():
            """List all permanent widgets and blocks from widgets.json"""
            widgets_path = Path(__file__).parent / 'widgets.json'
            if not widgets_path.exists():
                return jsonify({'widgets': [], 'blocks': []})
            try:
                import json
                with open(widgets_path, 'r') as f:
                    data = json.load(f)
                return jsonify(data)
            except (json.JSONDecodeError, IOError):
                return jsonify({'widgets': [], 'blocks': []})

        @self.app.route('/api/layout', methods=['GET'])
        def get_layout():
            """Get the homepage layout order"""
            layout_path = Path(__file__).parent / 'layout.json'
            if not layout_path.exists():
                return jsonify({'order': []})
            try:
                import json
                with open(layout_path, 'r') as f:
                    data = json.load(f)
                return jsonify(data)
            except (json.JSONDecodeError, IOError):
                return jsonify({'order': []})

        @self.app.route('/api/layout', methods=['PUT'])
        def save_layout():
            """Save the homepage layout order"""
            import json
            data = request.get_json()
            if not data or 'order' not in data:
                return jsonify({'error': 'Missing order array'}), 400
            layout_path = Path(__file__).parent / 'layout.json'
            try:
                with open(layout_path, 'w') as f:
                    json.dump({'order': data['order']}, f, indent=2)
                return jsonify({'success': True})
            except IOError as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/posts/create', methods=['POST'])
        def create_post():
            """Create a new blog post"""
            data = request.get_json()

            # Validate required fields
            required_fields = ['slug', 'title', 'content']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            slug = data['slug']

            # Validate slug format (alphanumeric and hyphens only)
            if not re.match(r'^[a-z0-9-]+$', slug):
                return jsonify({'error': 'Slug must contain only lowercase letters, numbers, and hyphens'}), 400

            # Check if post already exists
            post_dir = self.pages_dir / slug
            if post_dir.exists():
                return jsonify({'error': f'Post with slug "{slug}" already exists'}), 409

            try:
                # Create post directory
                post_dir.mkdir(parents=True, exist_ok=False)

                # Create config.json
                config = {
                    'slug': slug,
                    'title': data['title'],
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'description': data.get('description', ''),
                    'categories': data.get('categories', [])
                }

                with open(post_dir / 'config.json', 'w') as f:
                    json.dump(config, f, indent=4)

                # Create content.md
                with open(post_dir / 'content.md', 'w') as f:
                    f.write(data['content'])

                # Trigger compile if requested
                compile_result = None
                if data.get('auto_compile', True):
                    compile_result = self._trigger_compile()

                return jsonify({
                    'success': True,
                    'slug': slug,
                    'path': str(post_dir),
                    'compile_triggered': data.get('auto_compile', True),
                    'compile_result': compile_result
                }), 201

            except Exception as e:
                # Cleanup on failure
                if post_dir.exists():
                    shutil.rmtree(post_dir)
                return jsonify({'error': f'Failed to create post: {str(e)}'}), 500

        @self.app.route('/api/posts/update/<slug>', methods=['PUT'])
        def update_post(slug):
            """Update an existing blog post"""
            # Validate slug format
            if not re.match(r'^[a-z0-9-]+$', slug):
                return jsonify({'error': 'Invalid slug format'}), 400

            post_dir = self.pages_dir / slug
            if not post_dir.exists():
                return jsonify({'error': f'Post "{slug}" not found'}), 404

            data = request.get_json()

            try:
                # Update config.json if metadata provided
                if any(key in data for key in ['title', 'date', 'description', 'categories', 'hidden']):
                    config_file = post_dir / 'config.json'
                    if config_file.exists():
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                    else:
                        config = {'slug': slug}

                    # Update config fields
                    if 'title' in data:
                        config['title'] = data['title']
                    if 'date' in data:
                        config['date'] = data['date']
                    if 'description' in data:
                        config['description'] = data['description']
                    if 'categories' in data:
                        config['categories'] = data['categories']
                    if 'hidden' in data:
                        config['hidden'] = bool(data['hidden'])

                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=4)

                # Update content.md if provided
                if 'content' in data:
                    with open(post_dir / 'content.md', 'w') as f:
                        f.write(data['content'])

                # Trigger compile if requested
                compile_result = None
                if data.get('auto_compile', True):
                    compile_result = self._trigger_compile()

                return jsonify({
                    'success': True,
                    'slug': slug,
                    'updated_fields': list(data.keys()),
                    'compile_triggered': data.get('auto_compile', True),
                    'compile_result': compile_result
                })

            except Exception as e:
                return jsonify({'error': f'Failed to update post: {str(e)}'}), 500

        @self.app.route('/api/posts/delete/<slug>', methods=['DELETE'])
        def delete_post(slug):
            """Delete a blog post"""
            # Validate slug format
            if not re.match(r'^[a-z0-9-]+$', slug):
                return jsonify({'error': 'Invalid slug format'}), 400

            post_dir = self.pages_dir / slug
            if not post_dir.exists():
                return jsonify({'error': f'Post "{slug}" not found'}), 404

            try:
                # Delete the post directory
                shutil.rmtree(post_dir)

                # Trigger compile if requested
                compile_result = None
                auto_compile = request.args.get('auto_compile', 'true').lower() == 'true'
                if auto_compile:
                    compile_result = self._trigger_compile()

                return jsonify({
                    'success': True,
                    'slug': slug,
                    'deleted': True,
                    'compile_triggered': auto_compile,
                    'compile_result': compile_result
                })

            except Exception as e:
                return jsonify({'error': f'Failed to delete post: {str(e)}'}), 500

        @self.app.route('/api/posts/compile', methods=['POST'])
        def trigger_compile():
            """Manually trigger compile.py to regenerate static files.
            Requires auth. Pass {artist_slug} to compile one artist, or omit for all."""
            from auth import get_authenticated_artist, verify_artist_token
            # Require authentication
            artist = get_authenticated_artist()
            if not artist:
                token = request.headers.get('X-Admin-Token', '')
                if not token or token != os.environ.get('DEV_ADMIN_TOKEN', ''):
                    return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json(silent=True) or {}
            artist_slug = data.get('artist_slug') or artist
            result = self._trigger_compile(artist_slug=artist_slug)

            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500

        @self.app.route('/api/manage')
        def site_management_portal():
            """Serve the site management portal"""
            portal_path = Path(__file__).parent / 'pages' / 'artists' / '_shared' / 'portal.html'
            if portal_path.exists():
                return send_file(str(portal_path), mimetype='text/html')
            return 'Portal not found', 404

        @self.app.route('/api/dev/restart-services', methods=['POST'])
        def restart_dev_services():
            """
            Restart geo-butler development services (Firebase emulators and Next.js dev server)
            Requires admin token for security
            """
            # Check for admin authorization token
            auth_token = request.headers.get('X-Admin-Token')
            admin_token = os.environ.get('DEV_ADMIN_TOKEN', 'dev-restart-token')

            if not auth_token or auth_token != admin_token:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Missing or invalid X-Admin-Token header'
                }), 403

            try:
                # Restart the geo-butler-dev systemd service
                result = subprocess.run(
                    ['sudo', '-S', 'systemctl', 'restart', 'geo-butler-dev.service'],
                    input='01022366\n',  # sudo password piped in (string, not bytes)
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    return jsonify({
                        'success': True,
                        'message': 'Development services restarting',
                        'service': 'geo-butler-dev.service',
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'details': 'Firebase emulators and Next.js dev server will restart in ~5-10 seconds'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to restart service',
                        'stderr': result.stderr,
                        'stdout': result.stdout
                    }), 500

            except subprocess.TimeoutExpired:
                return jsonify({
                    'error': 'Restart command timed out',
                    'message': 'Service restart is taking too long'
                }), 500
            except Exception as e:
                return jsonify({
                    'error': 'Failed to restart services',
                    'details': str(e)
                }), 500

        @self.app.route('/api/dev/services-status', methods=['GET'])
        def check_dev_services_status():
            """
            Check status of development services
            Returns port availability for Firebase emulators and Next.js dev server
            """
            ports = {
                'nextjs_dev': 3000,
                'firebase_functions': 5001,
                'firebase_hosting': 5002,
                'firestore_emulator': 8081,
                'auth_emulator': 9099,
                'pubsub_emulator': 8085,
            }

            status = {}
            for service_name, port in ports.items():
                is_open = self._check_port_open(port)
                status[service_name] = {
                    'port': port,
                    'running': is_open,
                    'url': f'http://localhost:{port}' if is_open else None
                }

            all_healthy = all(s['running'] for s in status.values())

            return jsonify({
                'all_healthy': all_healthy,
                'services': status,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

        @self.app.route('/api/dev/port-status', methods=['GET'])
        def check_dev_port_status():
            """
            Check if dev ports are open without requiring authentication
            Returns port availability for BlueMap, Trading, Depopper, WTA
            """
            ports = {
                'bluemap': 8100,
                'trading': 3005,
                'depopper': 5123,
                'wta': 6767,
                'jupyter': 8888,
                'titansar': 8889,
                'xpvnc': 6080,
                'templeos': 6081,
                'geopolmarkets': 8890,
                'geopolweb': 8891
            }

            status = {}
            for service_name, port in ports.items():
                is_open = self._check_port_open(port)
                status[service_name] = {
                    'port': port,
                    'running': is_open
                }

            return jsonify({
                'services': status,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

    def _get_page_directories(self):
        """Get all page directories (including artist subdirectories)"""
        if not self.pages_dir.exists():
            return []

        page_dirs = []
        for item in self.pages_dir.iterdir():
            if item.is_dir() and (item / 'config.json').exists():
                page_dirs.append(item)
            # Also scan artist subdirectories
            if item.is_dir() and item.name == 'artists':
                for artist_dir in item.iterdir():
                    if artist_dir.is_dir() and not artist_dir.name.startswith('_'):
                        # Check for artist-level api.py (central backend per artist)
                        if (artist_dir / 'api.py').exists():
                            page_dirs.append(artist_dir)
                        for sub in artist_dir.iterdir():
                            if sub.is_dir() and (sub / 'config.json').exists():
                                page_dirs.append(sub)

        return page_dirs
    
    def _register_page_apis(self):
        """Auto-register API endpoints and WebSocket handlers from page modules"""
        registered_pages = []
        registered_routes = {}  # Track routes for collision detection
        
        for page_dir in self._get_page_directories():
            api_file = page_dir / 'api.py'
            
            if api_file.exists():
                try:
                    # Load the page's API module
                    spec = importlib.util.spec_from_file_location(
                        f"pages.{page_dir.name}.api", 
                        str(api_file)
                    )
                    api_module = importlib.util.module_from_spec(spec)
                    
                    # Add the shared module to Python path so imports work
                    if str(Path.cwd()) not in sys.path:
                        sys.path.insert(0, str(Path.cwd()))
                    
                    spec.loader.exec_module(api_module)
                    
                    # Register the blueprint if it exists
                    if hasattr(api_module, 'bp'):
                        # Check for route collisions before registering
                        blueprint = api_module.bp
                        page_routes = []
                        
                        # Register first, then check routes from Flask app
                        self.app.register_blueprint(blueprint)
                        
                        # Check for route collisions by examining all registered routes
                        for rule in self.app.url_map.iter_rules():
                            if rule.endpoint.startswith(f"{blueprint.name}."):
                                route_path = rule.rule
                                page_routes.append(route_path)
                                
                                # Check for collisions (excluding the blueprint prefix)
                                base_route = route_path.replace(blueprint.url_prefix or '', '') if blueprint.url_prefix else route_path
                                collision_key = f"{base_route}#{rule.methods}"
                                
                                if collision_key in registered_routes and registered_routes[collision_key] != page_dir.name:
                                    print(f"⚠️  WARNING: Route collision detected!")
                                    print(f"   Route: {route_path} {rule.methods}")
                                    print(f"   Page '{page_dir.name}' conflicts with page '{registered_routes[collision_key]}'")
                                    print(f"   Recommendation: Use page-specific route names")
                                else:
                                    registered_routes[collision_key] = page_dir.name
                        
                        registered_pages.append(page_dir.name)
                        print(f"Registered API endpoints for page: {page_dir.name}")
                        if page_routes:
                            print(f"  Routes: {', '.join(page_routes)}")
                    else:
                        print(f"Warning: {api_file} doesn't have a 'bp' blueprint")
                    
                    # Register WebSocket handlers if they exist
                    if hasattr(api_module, 'register_websocket_handlers'):
                        try:
                            api_module.register_websocket_handlers(self.socketio)
                            print(f"Registered WebSocket handlers for page: {page_dir.name}")
                        except Exception as ws_error:
                            print(f"Error registering WebSocket handlers for {page_dir.name}: {ws_error}")
                
                except Exception as e:
                    print(f"Error loading API for page {page_dir.name}: {e}")
        
        print(f"Successfully registered APIs for {len(registered_pages)} pages")
        if any("⚠️" in line for line in []):  # This will show warnings if any were printed above
            print("\n🔍 Endpoint Collision Check Complete - Review warnings above")
        return registered_pages
    
    def _serve_page_assets(self, page_slug, asset_path):
        """Serve assets for a specific page"""
        page_dir = self.pages_dir / page_slug
        assets_dir = page_dir / 'assets'
        
        if not assets_dir.exists():
            return jsonify({'error': 'Assets directory not found'}), 404
        
        try:
            return send_from_directory(assets_dir, asset_path)
        except FileNotFoundError:
            return jsonify({'error': f'Asset {asset_path} not found'}), 404
    
    def setup_asset_routes(self):
        """Setup routes for serving page assets"""
        @self.app.route('/assets/<page_slug>/<path:asset_path>')
        def serve_page_assets(page_slug, asset_path):
            return self._serve_page_assets(page_slug, asset_path)
    
    def run(self, debug=True):
        """Run the Flask server"""
        # Setup asset routes
        self.setup_asset_routes()
        
        print(f"Starting Flask server with WebSocket support on port {self.port}")
        print(f"Static files served from: {self.static_dir}")
        print(f"Pages directory: {self.pages_dir}")
        print(f"API base URL: http://localhost:{self.port}/api/")
        print(f"WebSocket URL: http://localhost:{self.port}")
        print(f"Assets URL pattern: http://localhost:{self.port}/assets/<page>/<file>")
        
        # Use socketio.run instead of app.run for WebSocket support
        self.socketio.run(
            self.app,
            host='0.0.0.0',
            port=self.port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the blog Flask server")
    parser.add_argument("--port", "-p", type=int, default=5000, 
                       help="Port to run on (default: 5000)")
    parser.add_argument("--pages", default=".",
                       help="Pages directory (default: .)")
    parser.add_argument("--static", default="output", 
                       help="Static files directory (default: output)")
    parser.add_argument("--no-debug", action="store_true", 
                       help="Disable debug mode")
    
    args = parser.parse_args()
    
    server = BlogFlaskServer(
        pages_dir=args.pages,
        static_dir=args.static,
        port=args.port
    )
    
    server.run(debug=not args.no_debug)

if __name__ == "__main__":
    main()