# Artist Site System — Developer Guide

This document explains how artist sites work within the blog-new platform, how to create
new artist sites, set up custom domains, and build widgets. Written for future developers/AI.

## Overview

Artist sites live under `pages/artists/{slug}/`. Each artist gets:
- A set of pages (each a folder with `config.json` + `content.md`)
- Shared assets in `assets/`
- Optional custom widgets in `widgets/`
- An admin dashboard at `/api/sandbox/dashboard`
- Preview routes at `/artists/{slug}/` (no domain needed)
- Optional custom domain support via nginx reverse proxy

## Directory Structure

```
pages/artists/
├── _shared/                        # Shared system files (DO NOT put artist sites here)
│   ├── admin_api.py                # Flask Blueprint — all admin API endpoints
│   ├── auth.py                     # Token-based auth (per-artist + DEV_ADMIN_TOKEN fallback)
│   ├── dashboard.html              # Universal admin dashboard (served to all artists)
│   └── ARTIST-SYSTEM.md            # This file
│
├── {artist-slug}/                  # One directory per artist
│   ├── config.json                 # Artist config (name, domain, token, etc.)
│   ├── assets/                     # Shared assets (images, fonts, gifs, etc.)
│   │   ├── images/
│   │   ├── fonts/
│   │   └── gifs/
│   ├── widgets/                    # Custom dashboard widgets (optional)
│   │   └── my-widget.js
│   ├── home/                       # Pages — each is a folder
│   │   ├── config.json
│   │   └── content.md
│   ├── gallery/
│   │   ├── config.json
│   │   └── content.md
│   └── ...more pages
```

## Creating a New Artist Site

### 1. Create the directory structure

```bash
mkdir -p pages/artists/{slug}/assets
mkdir -p pages/artists/{slug}/home
```

### 2. Create artist config.json

`pages/artists/{slug}/config.json`:
```json
{
    "name": "Artist Display Name",
    "slug": "artist-slug",
    "domain": "optional-custom-domain.com",
    "admin_token": "their-secret-login-token",
    "description": "Short description",
    "contact_email": "artist@email.com"
}
```

- `slug` must match the directory name
- `admin_token` is what the artist uses to log into the dashboard
- `domain` is optional — only needed when setting up a custom domain

### 3. Create a home page

`pages/artists/{slug}/home/config.json`:
```json
{
    "title": "Home - Artist Name",
    "slug": "artists/{slug}/home",
    "description": "Homepage",
    "categories": []
}
```

`pages/artists/{slug}/home/content.md`:
```
<style>
/* CSS goes here */
body { background: #1a1a2e; color: white; font-family: sans-serif; }
</style>
<html>
<!-- HTML body goes here -->
<h1>Welcome</h1>
<p>Artist homepage</p>
</html>
```

The content.md format is: `<style>...</style>` followed by `<html>...</html>`. The compiler
splits these and wraps them in a full HTML document.

### 4. Compile and restart

```bash
python3 compile.py
sudo systemctl restart blog-server
```

The site is now live at `https://yourdomain.com/artists/{slug}/`

## Asset Paths

All asset references in content.md should use relative paths:
```
../assets/images/photo.jpg
../assets/fonts/MyFont.ttf
../assets/gifs/animation.gif
```

This works because pages are served at `/artists/{slug}/{page}/`, so `../assets/` resolves
to `/artists/{slug}/assets/`.

When a custom domain is set up, pages serve at `/{page}/`, so `../assets/` still resolves
to `/assets/` — the same relative path works in both modes.

## Preview Routes

The compiler generates:
- `output/artists/{slug}/{page}/index.html` — each page
- `output/artists/{slug}/index.html` — redirect to `home/`
- `output/artists/{slug}/assets/` — copied from source assets

These are served by nginx as static files. No domain config needed to preview.

## Admin Dashboard

Artists access the dashboard at `/api/sandbox/dashboard`. They log in with:
- **Artist slug** — their directory name
- **Admin token** — from their config.json

The dev fallback token (in auth.py) is for development only.

### Dashboard features:
- **AI Edit** — Gemini 2.5 Flash powered chat that can edit CSS/HTML via function calling
- **Manual Edit** — Split CSS/HTML editors with live preview
- **Config** — Page config form + raw JSON editor
- **Assets** — Upload, browse, copy paths
- **History** — Local snapshots (localStorage)
- **Custom widget tabs** — Per-artist JS widgets (see below)

## Widget System

Each artist can have custom dashboard widgets. These are `.js` files in `widgets/`.

### How widgets work:

1. On login, the dashboard calls `/api/sandbox/list-widgets`
2. For each `.js` file found, it creates a tab and panel in the dashboard
3. The JS is executed with a `ctx` object providing dashboard APIs

### Widget template:

`pages/artists/{slug}/widgets/my-feature.js`:
```javascript
(function(ctx) {
    // ctx.container — the DOM element to render into
    // ctx.artistSlug — current artist slug
    // ctx.assetList — array of {filename, path, url, is_image, size}
    // ctx.pages — array of {slug, title, config}
    // ctx.currentPage() — returns the currently selected page
    // ctx.toast(msg, type) — show a notification ('success'|'error'|'info')
    // ctx.apiFetch(url, opts) — fetch with auth headers pre-set
    // ctx.getPageContent(slug) — fetch a page's content + config
    // ctx.savePage(slug, content, config) — save a page
    // ctx.getCss() / ctx.setCss(val) — read/write CSS editor
    // ctx.getHtml() / ctx.setHtml(val) — read/write HTML editor
    // ctx.parseContent(raw) — split raw content.md into {css, html}
    // ctx.loadAssets() — refresh the asset list

    ctx.container.innerHTML = `
        <h3>My Widget</h3>
        <p>Widget UI goes here</p>
        <button class="widget-btn widget-btn-primary" id="myBtn">Do Something</button>
    `;

    document.getElementById('myBtn').addEventListener('click', async () => {
        // Example: read gallery page
        const page = await ctx.getPageContent('gallery');
        // Modify content...
        const ok = await ctx.savePage('gallery', newContent);
        if (ok) ctx.toast('Done!');
    });
})(ctx);
```

### Widget naming:
- Filename becomes the tab name: `add-to-gallery.js` → "Add To Gallery"
- Hyphens and underscores are converted to spaces, words are capitalized

### Available CSS classes for widget UI:
- `.widget-btn` / `.widget-btn-primary` — buttons
- `.widget-grid` — auto-fill grid for cards
- `.widget-card` / `.widget-card.selected` — selectable cards with hover/selected states
- `.widget-card img` + `.wc-label` — card with image + label
- `.widget-status.success` / `.widget-status.error` — status messages
- `.widget-section` — spacing between sections

## Custom Domain Setup

When an artist wants their own domain (e.g., whitethornapple.com):

### 1. DNS

Point the domain to the server IP:
```
A    @    → {server-ip}
A    www  → {server-ip}
```

### 2. Nginx config

Add a new server block in `/etc/nginx/sites-available/blog` (or a new file):

```nginx
server {
    listen 80;
    server_name whitethornapple.com www.whitethornapple.com;

    root /home/gabriel/blog-new/output;

    # Artist pages served from their subdirectory
    # Rewrite / to the artist's home page
    location = / {
        rewrite ^ /artists/whitethornapple/home/ last;
    }

    # Rewrite /{page}/ to /artists/whitethornapple/{page}/
    location / {
        # Try the artist's pages first
        try_files /artists/whitethornapple$uri /artists/whitethornapple$uri/ @api;
    }

    # Assets — map /assets/ to the artist's assets
    location /assets/ {
        alias /home/gabriel/blog-new/output/artists/whitethornapple/assets/;
        expires 24h;
    }

    # API fallback (for dashboard, admin endpoints)
    location @api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d whitethornapple.com -d www.whitethornapple.com
```

### 4. Flask domain routing

The Flask server (`flask_server.py`) already has `_get_artist_by_domain()` which checks
the `Host` header against each artist's `config.json` `domain` field. This handles
API requests and any dynamic routes.

### 5. Verify

```bash
sudo nginx -t && sudo systemctl reload nginx
```

The artist site is now accessible at both:
- `https://whitethornapple.com/` (custom domain)
- `https://gabrielpenman.com/artists/whitethornapple/` (preview route)

Relative asset paths (`../assets/`) work in both modes because the page structure
maintains the same depth.

## Key Files Reference

| File | Purpose |
|------|---------|
| `pages/artists/_shared/admin_api.py` | Flask Blueprint — CRUD APIs, dashboard serving, widget endpoints |
| `pages/artists/_shared/auth.py` | Token auth — `get_authenticated_artist()`, DEV_ADMIN_TOKEN |
| `pages/artists/_shared/dashboard.html` | Universal admin dashboard — all tabs, AI chat, widget loader |
| `compile.py` | Static site compiler — `copy_artist_assets()`, `generate_artist_root_indexes()` |
| `flask_server.py` | Flask app — domain routing, static file serving, blueprint registration |
| `/etc/nginx/sites-available/blog` | Nginx config — static files, API proxy, caching |

## Compilation

`compile.py` handles artist sites in `compile_all()`:
1. `copy_artist_assets()` — copies `pages/artists/{slug}/assets/` → `output/artists/{slug}/assets/`
2. `generate_artist_root_indexes()` — creates redirect `index.html` at each artist root → `home/`
3. Normal page compilation handles each page's `content.md` → `output/artists/{slug}/{page}/index.html`

## Systemd Service

The Flask server runs as `blog-server`:
```bash
sudo systemctl restart blog-server   # restart after code changes
sudo systemctl status blog-server    # check status
journalctl -u blog-server -f         # view logs
```
