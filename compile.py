#!/usr/bin/env python3
"""
Adze Studio — Artist site compiler.
Compiles artist pages from content.md + config.json into static HTML.
Supports per-artist compilation for fast, isolated rebuilds.
"""

import os
import sys
import json
import re
import shutil
import base64
import hashlib
import html
from urllib.parse import quote
from pathlib import Path
from datetime import datetime


class AdzeCompiler:
    def __init__(self, artists_dir="artists", shared_dir="_shared", output_dir="output"):
        self.artists_dir = Path(artists_dir)
        self.shared_dir = Path(shared_dir)
        self.output_dir = Path(output_dir)

    def get_artist_dirs(self):
        """List all artist directories (skip _shared, _template, hidden)."""
        if not self.artists_dir.exists():
            return []
        return [
            d for d in sorted(self.artists_dir.iterdir())
            if d.is_dir() and not d.name.startswith('_') and d.name != 'example-artist'
        ]

    def get_page_dirs(self, artist_dir):
        """Get all page directories for an artist (dirs with content.md + config.json).
        Recurses into subdirectories so works/<slug>/ and exhibitions/<slug>/ detail
        pages compile alongside their parent listing pages."""
        skip = {'assets', 'widgets', '__pycache__', '.snapshots', 'backups'}
        pages = []

        def walk(d):
            for child in sorted(d.iterdir()):
                if not child.is_dir() or child.name in skip:
                    continue
                if (child / 'content.md').exists() and (child / 'config.json').exists():
                    pages.append(child)
                walk(child)

        walk(artist_dir)
        return pages

    def parse_content(self, page_dir):
        """Parse content.md into HTML, CSS, and meta tags."""
        content_file = page_dir / 'content.md'
        raw = content_file.read_text(encoding='utf-8')

        # Extract CSS
        css_match = re.search(r'<style>(.*?)</style>', raw, re.DOTALL)
        page_css = css_match.group(1) if css_match else ""

        # Prepend default-styles.css if it exists (site-wide CSS vars)
        artist_dir = page_dir.parent
        default_styles_file = artist_dir / 'default-styles.css'
        if default_styles_file.exists():
            default_css = default_styles_file.read_text(encoding='utf-8')
            page_css = default_css + '\n' + page_css

        css = f"<style>{page_css}</style>" if page_css else ""

        # Extract HTML
        html_match = re.search(r'<html>(.*?)</html>', raw, re.DOTALL)
        html = html_match.group(1).strip() if html_match else ""

        # Extract meta tags (before <style> or <html>)
        before = raw[:raw.find('<style>')] if '<style>' in raw else raw[:raw.find('<html>')] if '<html>' in raw else ''
        meta_tags = '\n    '.join(re.findall(r'<meta[^>]+>', before, re.IGNORECASE))

        return html, css, meta_tags

    def copy_artist_assets(self, artist_slug):
        """Copy artist assets/ to output/{slug}/assets/."""
        src = self.artists_dir / artist_slug / 'assets'
        dst = self.output_dir / 'artists' / artist_slug / 'assets'

        if not src.exists():
            return 0

        if dst.exists():
            try:
                shutil.rmtree(dst)
            except (PermissionError, OSError):
                pass  # output/ may be host-owned; overwrite in place instead
        dst.mkdir(parents=True, exist_ok=True)

        # Files that live in assets/ but are never served
        _SKIP_NAMES = {'assets.meta.json'}

        count = 0
        for f in src.rglob('*'):
            if not f.is_file():
                continue
            rel = f.relative_to(src)
            # Skip hidden dirs (.thumbs etc) and internal metadata files
            if any(part.startswith('.') for part in rel.parts):
                continue
            if f.name in _SKIP_NAMES:
                continue
            out = dst / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copyfile(f, out)
            except (PermissionError, OSError):
                try:
                    out.write_bytes(f.read_bytes())
                except (PermissionError, OSError):
                    pass  # file exists in output and is host-owned; already served, skip
            count += 1
        return count

    def _build_schema_blocks(self, artist_config, page_config):
        """Collect JSON-LD blocks from artist + page config and serialize to <script> tags."""
        items = []
        for src in (artist_config.get('schema'), page_config.get('schema')):
            if not src:
                continue
            if isinstance(src, list):
                items.extend(x for x in src if isinstance(x, (dict, list)))
            elif isinstance(src, dict):
                items.append(src)
        if not items:
            return ''
        out = []
        for item in items:
            try:
                payload = json.dumps(item, ensure_ascii=False, separators=(',', ':'))
            except (TypeError, ValueError):
                continue
            payload = payload.replace('</', '<\\/')
            out.append(f'\n    <script type="application/ld+json">{payload}</script>')
        return ''.join(out)

    def _build_seo_head(self, artist_slug, artist_config, page_config, page_rel):
        """Generate meta description, canonical, Open Graph/Twitter tags, and a
        typed JSON-LD entity from the artist's `seo` block + page config.

        Baseline meta/OG is emitted for every page from the best-available
        name/description/image. The typed Schema.org entity (Person / MusicGroup
        / Organization) is emitted only once the artist fills in `seo` (so we
        never assert a wrong @type). Raw `schema` blocks are handled separately."""
        seo = artist_config.get('seo') or {}

        # Absolute site base — custom domain if set, else the adze.studio path.
        domain = (artist_config.get('domain') or '').strip()
        base = f"https://{domain}" if domain else f"https://adze.studio/artists/{artist_slug}"
        page_path = page_rel.as_posix() if hasattr(page_rel, 'as_posix') else str(page_rel)
        page_url = f"{base}/{page_path}/" if page_path and page_path != '.' else f"{base}/"

        name = (seo.get('name') or artist_config.get('name') or artist_slug).strip()
        # Page-specific description drives this page's meta/OG; the site-level
        # description (about the artist, identical on every page) drives the
        # JSON-LD entity so its description doesn't change page to page.
        site_desc = (seo.get('description') or artist_config.get('description') or '').strip()
        description = (page_config.get('description') or site_desc).strip()
        title = (page_config.get('title') or name).strip()

        # Resolve an absolute image URL (page og_image wins, else seo.image).
        img = (page_config.get('og_image') or seo.get('image') or '').strip()
        if img.startswith(('http://', 'https://')):
            image_abs = img
        elif img:
            image_abs = f"{base}/assets/{img.lstrip('/')}"
        else:
            image_abs = ''

        e = html.escape
        out = []
        if description:
            out.append(f'<meta name="description" content="{e(description)}">')
        out.append(f'<link rel="canonical" href="{e(page_url)}">')
        out.append('<meta property="og:type" content="website">')
        out.append(f'<meta property="og:site_name" content="{e(name)}">')
        out.append(f'<meta property="og:title" content="{e(title)}">')
        if description:
            out.append(f'<meta property="og:description" content="{e(description)}">')
        out.append(f'<meta property="og:url" content="{e(page_url)}">')
        if image_abs:
            out.append(f'<meta property="og:image" content="{e(image_abs)}">')
        out.append(f'<meta name="twitter:card" content="{"summary_large_image" if image_abs else "summary"}">')
        out.append(f'<meta name="twitter:title" content="{e(title)}">')
        if description:
            out.append(f'<meta name="twitter:description" content="{e(description)}">')
        if image_abs:
            out.append(f'<meta name="twitter:image" content="{e(image_abs)}">')

        if seo.get('type'):
            entity = {
                '@context': 'https://schema.org',
                '@type': seo['type'],
                'name': name,
                'url': f"{base}/",
            }
            if site_desc:
                entity['description'] = site_desc
            if image_abs:
                entity['image'] = image_abs
            same = [s for s in (seo.get('sameAs') or []) if s]
            if same:
                entity['sameAs'] = same
            if seo['type'] == 'Person' and seo.get('role'):
                entity['jobTitle'] = seo['role']
            if seo['type'] == 'MusicGroup' and seo.get('genre'):
                entity['genre'] = seo['genre']
            payload = json.dumps(entity, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
            out.append(f'<script type="application/ld+json">{payload}</script>')

        return ('\n    ' + '\n    '.join(out)) if out else ''

    def _inject_image_pipeline(self, html, artist_slug, artist_config, up_prefix):
        """Rewrite <img> tags with data-thumb and inject pipeline script. No-op if feature not configured."""
        # `features` may be a dict (per-feature config) or a list of enabled
        # feature names (e.g. ["bookings"]) — only the dict form carries an
        # image_pipeline config block.
        _feats = artist_config.get('features')
        pipeline_cfg = _feats.get('image_pipeline') if isinstance(_feats, dict) else None
        if not pipeline_cfg:
            return html

        thumbs_base = self.artists_dir / artist_slug / 'assets' / '.thumbs'
        assets_prefix = up_prefix + 'assets/'

        mode = pipeline_cfg.get('mode', 'halftone')
        is_dither = (mode == 'dither')

        def _make_data_uri(thumb_path):
            """Read thumb, optionally quantise to indexed PNG for dither mode, return data URI."""
            if is_dither:
                try:
                    from PIL import Image
                    import io as _io
                    depth      = int(pipeline_cfg.get('colorDepth', 4))
                    n_colors   = 2 ** depth
                    grayscale  = pipeline_cfg.get('paletteType') == 'grayscale'
                    use_dither = pipeline_cfg.get('ditherAlgo', 'floyd-steinberg') != 'none'
                    dither_val = 1 if use_dither else 0  # PIL: 1=Floydsteinberg, 0=none
                    with Image.open(thumb_path) as img:
                        if grayscale:
                            img = img.convert('L').convert('RGB')
                        else:
                            img = img.convert('RGB')
                        quantised = img.quantize(colors=n_colors, dither=dither_val)
                    buf = _io.BytesIO()
                    quantised.save(buf, 'PNG', optimize=True)
                    b64 = base64.b64encode(buf.getvalue()).decode()
                    return 'data:image/png;base64,' + b64
                except Exception:
                    pass  # fall through to raw WebP
            b64 = base64.b64encode(thumb_path.read_bytes()).decode()
            return 'data:image/webp;base64,' + b64

        def _add_thumb(m):
            tag = m.group(0)
            if 'data-thumb' in tag:
                return tag
            src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
            if not src_m:
                return tag
            src = src_m.group(1)
            if not src.startswith(assets_prefix):
                return tag
            rel = src[len(assets_prefix):]
            for candidate in [
                thumbs_base / (rel + '.webp'),
                thumbs_base / (Path(rel).with_suffix('.webp')),
            ]:
                if candidate.exists():
                    try:
                        data_uri = _make_data_uri(candidate)
                        close = '/>' if tag.endswith('/>') else '>'
                        return tag[:-len(close)] + ' data-thumb="' + data_uri + '"' + close
                    except Exception:
                        pass
            return tag

        html = re.sub(r'<img\b[^>]*>', _add_thumb, html)

        pipeline_js_path = self.shared_dir / 'features' / 'image-pipeline.js'
        if not pipeline_js_path.exists():
            return html

        # Build a thumbMap covering ALL asset images so dynamically created
        # <img> elements (galleries, lightboxes) can also get the pipeline effect.
        # Keys are asset-relative stem without extension, e.g. 'images/foo'
        # so they match regardless of what extension the JS uses in img.src.
        thumb_map = {}
        if thumbs_base.exists():
            for tf in sorted(thumbs_base.rglob('*.webp')):
                stem = str(tf.relative_to(thumbs_base).with_suffix(''))
                try:
                    thumb_map[stem] = _make_data_uri(tf)
                except Exception:
                    pass

        inject_cfg = dict(pipeline_cfg)
        if thumb_map:
            inject_cfg['thumbMap'] = thumb_map

        pipeline_js  = pipeline_js_path.read_text(encoding='utf-8')
        config_json  = json.dumps(inject_cfg, ensure_ascii=False, separators=(',', ':'))
        script_block = (
            '<script>window.__imagePipeline=' + config_json + ';</script>\n'
            '<script>' + pipeline_js + '</script>\n'
        )
        html = html.replace('</body>', script_block + '</body>')
        return html

    def _inject_data_placeholders(self, html_content, artist_slug):
        """Replace data placeholders in HTML with content derived from information.json.

        <!-- EXHIBITIONS_BLOCK --> → <p> lines for each exhibition, newest first.
        No-op if information.json is absent or the placeholder isn't present.
        """
        if '<!-- EXHIBITIONS_BLOCK -->' not in html_content:
            return html_content

        info_path = self.artists_dir / artist_slug / 'information.json'
        if not info_path.exists():
            return html_content

        try:
            info = json.loads(info_path.read_text(encoding='utf-8'))
        except Exception:
            return html_content

        exhibitions = info.get('exhibitions', [])
        # Sort newest first, stable on title
        exhibitions = sorted(exhibitions, key=lambda e: -e.get('year', 0))

        lines = []
        for e in exhibitions:
            year = str(e.get('year', ''))
            title = e.get('title', '')
            etype = (e.get('type') or '').lower()
            location = e.get('location', '')
            suffix = ', '.join(p for p in [etype, location] if p)
            text = f"{year} — {title}, {suffix}" if suffix else f"{year} — {title}"
            lines.append(f'        <p>{html.escape(text)}</p>')

        block = '\n'.join(lines)
        return html_content.replace('<!-- EXHIBITIONS_BLOCK -->', block)

    def _inject_loom(self, html, artist_config):
        """Inject the Loom visual-synth runtime if features.loom holds a trace.

        Loads the shared engine (_shared/widgets/loom/engine.js) + the live
        runtime (_shared/features/loom.js) + the trace as window.__loom. The
        trace is the source of truth; this is just the 'live' renderer. No-op
        if the feature is not configured.
        """
        _feats = artist_config.get('features')
        trace = _feats.get('loom') if isinstance(_feats, dict) else None
        if not trace:
            return html

        engine_path = self.shared_dir / 'widgets' / 'loom' / 'engine.js'
        runtime_path = self.shared_dir / 'features' / 'loom.js'
        if not engine_path.exists() or not runtime_path.exists():
            return html

        engine_js  = engine_path.read_text(encoding='utf-8')
        runtime_js = runtime_path.read_text(encoding='utf-8')
        trace_json = json.dumps(trace, ensure_ascii=False, separators=(',', ':'))
        script_block = (
            '<script>' + engine_js + '</script>\n'
            '<script>window.__loom=' + trace_json + ';</script>\n'
            '<script>' + runtime_js + '</script>\n'
        )
        return html.replace('</body>', script_block + '</body>')

    @staticmethod
    def _hsl_hex(h, s, l):
        """HSL (h 0-360, s/l 0-100) -> #RRGGBB. Mirrors the dashboard's JS
        implementation so the live favicon matches the dashboard preview."""
        s /= 100.0
        l /= 100.0
        a = s * min(l, 1 - l)
        def f(n):
            k = (n + h / 30.0) % 12
            return l - a * max(-1, min(k - 3, min(9 - k, 1)))
        def to_hex(x):
            return format(round(255 * x), '02x')
        return '#' + to_hex(f(0)) + to_hex(f(8)) + to_hex(f(4))

    def _favicon_dot_color(self, slug, explicit=None):
        """Return the dot colour: an explicit dashboard-set value, or a stable
        colour derived from the slug (djb2 hash -> hue). Must stay in sync with
        dotColorForSlug() in dashboard.html."""
        if explicit:
            return explicit
        h = 5381
        for ch in slug:
            h = (h * 33 + ord(ch)) & 0xFFFFFFFF
        return self._hsl_hex(h % 360, 65, 60)

    @staticmethod
    def _favicon_dot_link(color):
        """A filled-circle SVG favicon as an inline data URI (no asset needed)."""
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
            f"<circle cx='16' cy='16' r='12' fill='{color}'/></svg>"
        )
        return ('<link rel="icon" type="image/svg+xml" '
                f'href="data:image/svg+xml,{quote(svg, safe="")}">')

    def compile_page(self, artist_slug, page_dir):
        """Compile a single page into output/{slug}/{page}/index.html."""
        config = json.loads((page_dir / 'config.json').read_text(encoding='utf-8'))
        html_content, css_content, meta_tags = self.parse_content(page_dir)
        html_content = self._inject_data_placeholders(html_content, artist_slug)
        artist_root = self.artists_dir / artist_slug
        page_rel = page_dir.relative_to(artist_root)
        page_name = str(page_rel)
        depth = len(page_rel.parts)
        up_prefix = '../' * depth

        meta_section = f"\n    {meta_tags}" if meta_tags else ""

        # Favicon resolution:
        #   1. explicit image asset (`favicon` in config) — depth-aware path
        #   2. otherwise a coloured-dot SVG so the tab icon is never empty.
        #      Colour comes from `favicon_color` (set via the dashboard) or,
        #      failing that, a stable colour derived from the artist slug.
        artist_config = {}
        artist_config_file = self.artists_dir / artist_slug / 'config.json'
        if artist_config_file.exists():
            try:
                artist_config = json.loads(artist_config_file.read_text(encoding='utf-8'))
            except:
                pass
        if artist_config.get('favicon'):
            favicon_link = f'<link rel="icon" href="{up_prefix}assets/{artist_config["favicon"]}">'
        else:
            color = self._favicon_dot_color(artist_slug, artist_config.get('favicon_color'))
            favicon_link = self._favicon_dot_link(color)

        schema_blocks = self._build_schema_blocks(artist_config, config)
        seo_head = self._build_seo_head(artist_slug, artist_config, config, page_rel)

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">{meta_section}
    <title>{config.get('title', 'Untitled')}</title>{seo_head}
    {favicon_link}{schema_blocks}
    {css_content}
</head>
<body>
    {html_content}
</body>
</html>"""

        # Feature injection (opt-in, no-op if not configured)
        full_html = self._inject_image_pipeline(full_html, artist_slug, artist_config, up_prefix)
        full_html = self._inject_loom(full_html, artist_config)

        # Write to output/artists/{slug}/{page}/index.html (matches URL structure)
        out_dir = self.output_dir / 'artists' / artist_slug / page_rel
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(full_html, encoding='utf-8')

        return config

    def _artist_base_url(self, artist_slug, artist_config):
        """Canonical site origin — custom domain if set, else the adze.studio path."""
        domain = (artist_config.get('domain') or '').strip()
        return f"https://{domain}" if domain else f"https://adze.studio/artists/{artist_slug}"

    def _write_artist_seo_files(self, artist_slug, artist_config, pages, artist_output):
        """Emit sitemap.xml (built from the compiled pages) and robots.txt (the
        artist's override, or a sensible allow-all default) at the site root so
        search engines can discover the site. Served at <domain>/sitemap.xml and
        <domain>/robots.txt via the artist's nginx `try_files $uri`."""
        base = self._artist_base_url(artist_slug, artist_config)

        locs = [f"{base}/{p}/" for p in pages] or [f"{base}/"]
        urls = '\n'.join(f'  <url><loc>{html.escape(u)}</loc></url>' for u in locs)
        sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                   f'{urls}\n</urlset>\n')
        (artist_output / 'sitemap.xml').write_text(sitemap, encoding='utf-8')

        custom = (artist_config.get('robots') or '').strip()
        if custom:
            robots = custom if custom.endswith('\n') else custom + '\n'
            if 'sitemap:' not in robots.lower():
                robots += f"Sitemap: {base}/sitemap.xml\n"
        else:
            robots = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
        (artist_output / 'robots.txt').write_text(robots, encoding='utf-8')

    def prune_orphaned_output(self, artist_slug, source_page_rels):
        """Remove compiled page dirs whose source page no longer exists, so a
        deleted page stops being served. Scoped strictly to this artist's
        output tree; never touches assets/ or the site-root files. Keyed on
        *source presence* (not compile success) so a transient compile error
        never deletes a still-valid page."""
        artist_output = self.output_dir / 'artists' / artist_slug
        if not artist_output.exists():
            return 0
        keep = set(source_page_rels)
        removed = 0
        for index_file in sorted(artist_output.rglob('index.html'), reverse=True):
            page_dir = index_file.parent
            rel = page_dir.relative_to(artist_output)
            if rel == Path('.') or 'assets' in rel.parts:
                continue  # root redirect + asset tree are not pages
            if rel.as_posix() in keep or not page_dir.exists():
                continue
            try:
                shutil.rmtree(page_dir)
                removed += 1
            except OSError:
                pass
        return removed

    def compile_artist(self, artist_slug):
        """Compile all pages for a single artist."""
        artist_dir = self.artists_dir / artist_slug
        if not artist_dir.exists():
            print(f"Error: Artist '{artist_slug}' not found")
            return False

        print(f"=== Compiling: {artist_slug} ===")

        # Copy assets
        asset_count = self.copy_artist_assets(artist_slug)
        if asset_count:
            print(f"  Copied {asset_count} assets")

        # Compile pages
        compiled = 0
        compiled_pages = []
        source_page_rels = [p.relative_to(artist_dir).as_posix()
                            for p in self.get_page_dirs(artist_dir)]
        for page_dir in self.get_page_dirs(artist_dir):
            try:
                self.compile_page(artist_slug, page_dir)
                compiled_pages.append(page_dir.relative_to(artist_dir).as_posix())
                print(f"  Compiled: {page_dir.name}")
                compiled += 1
            except Exception as e:
                print(f"  Error compiling {page_dir.name}: {e}")

        # Drop compiled output for pages deleted from source
        pruned = self.prune_orphaned_output(artist_slug, source_page_rels)
        if pruned:
            print(f"  Pruned {pruned} orphaned page(s)")

        # Generate root index redirect to home/
        artist_output = self.output_dir / 'artists' / artist_slug
        artist_output.mkdir(parents=True, exist_ok=True)
        home_index = artist_output / 'home' / 'index.html'
        if home_index.exists():
            redirect = '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=home/"></head></html>'
            (artist_output / 'index.html').write_text(redirect)

        # robots.txt + sitemap.xml for search engines (served at the site root)
        artist_config = {}
        cfg_file = artist_dir / 'config.json'
        if cfg_file.exists():
            try:
                artist_config = json.loads(cfg_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        self._write_artist_seo_files(artist_slug, artist_config, compiled_pages, artist_output)

        print(f"=== Done: {compiled} pages ===")
        return True

    def compile_all(self):
        """Compile all artists."""
        print("=== Adze Studio — Full Compile ===")

        # Ensure output dir exists (don't nuke it — per-artist compile may have put things there)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for artist_dir in self.get_artist_dirs():
            self.compile_artist(artist_dir.name)

        print("\n=== All artists compiled ===")


if __name__ == "__main__":
    compiler = AdzeCompiler()

    if len(sys.argv) > 1 and sys.argv[1] == '--artist' and len(sys.argv) > 2:
        compiler.compile_artist(sys.argv[2])
    else:
        compiler.compile_all()
