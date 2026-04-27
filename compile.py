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
        """Get all page directories for an artist (dirs with content.md + config.json)."""
        pages = []
        for d in sorted(artist_dir.iterdir()):
            if d.is_dir() and d.name not in ('assets', 'widgets', '__pycache__', '.snapshots', 'backups'):
                if (d / 'content.md').exists() and (d / 'config.json').exists():
                    pages.append(d)
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
            shutil.rmtree(dst)
        dst.mkdir(parents=True, exist_ok=True)

        count = 0
        for f in src.rglob('*'):
            if f.is_file():
                rel = f.relative_to(src)
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)
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

    def compile_page(self, artist_slug, page_dir):
        """Compile a single page into output/{slug}/{page}/index.html."""
        config = json.loads((page_dir / 'config.json').read_text(encoding='utf-8'))
        html_content, css_content, meta_tags = self.parse_content(page_dir)
        page_name = page_dir.name

        meta_section = f"\n    {meta_tags}" if meta_tags else ""

        # Check for artist-specific favicon
        favicon_link = '<link rel="icon" href="../assets/favicon.png">'
        artist_config = {}
        artist_config_file = self.artists_dir / artist_slug / 'config.json'
        if artist_config_file.exists():
            try:
                artist_config = json.loads(artist_config_file.read_text(encoding='utf-8'))
                if artist_config.get('favicon'):
                    favicon_link = f'<link rel="icon" href="../assets/{artist_config["favicon"]}">'
            except:
                pass

        schema_blocks = self._build_schema_blocks(artist_config, config)

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">{meta_section}
    <title>{config.get('title', 'Untitled')}</title>
    {favicon_link}{schema_blocks}
    {css_content}
</head>
<body>
    {html_content}
</body>
</html>"""

        # Write to output/artists/{slug}/{page}/index.html (matches URL structure)
        out_dir = self.output_dir / 'artists' / artist_slug / page_name
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'index.html').write_text(full_html, encoding='utf-8')

        return config

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
        for page_dir in self.get_page_dirs(artist_dir):
            try:
                self.compile_page(artist_slug, page_dir)
                print(f"  Compiled: {page_dir.name}")
                compiled += 1
            except Exception as e:
                print(f"  Error compiling {page_dir.name}: {e}")

        # Generate root index redirect to home/
        artist_output = self.output_dir / 'artists' / artist_slug
        artist_output.mkdir(parents=True, exist_ok=True)
        home_index = artist_output / 'home' / 'index.html'
        if home_index.exists():
            redirect = '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=home/"></head></html>'
            (artist_output / 'index.html').write_text(redirect)

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
