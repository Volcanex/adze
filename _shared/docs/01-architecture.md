# Architecture

Adze Studio is a multi-tenant portfolio platform. Each artist has their own directory, compiled static site, and isolated admin API session.

## Directory structure

```
adze/
  flask_server.py        ← main server: routing, analytics tracking, feature auto-discovery
  compile.py             ← static site compiler: content.md → output HTML
  _shared/
    admin_api.py         ← all /api/adze/* endpoints (auth, pages, analytics, widgets, etc.)
    auth.py              ← per-artist token auth + session cookie
    db.py                ← per-artist SQLite (analytics + sessions only)
    dashboard.html       ← the entire admin dashboard UI (single HTML file)
    docs/                ← this directory — source of truth for AI + human docs
    widgets/             ← Tier 2 (Adze) widget definitions
    features/            ← opt-in per-artist feature blueprints (bookings, etc.)
  artists/
    {slug}/
      config.json        ← artist metadata: name, domain, admin_token, features
      {page}/
        content.md       ← page source: <style>...</style><html>...</html>
        config.json      ← page metadata: title, slug, description
      assets/
        images/
        fonts/
      data.db            ← SQLite: pageviews + sessions (auto-created)
      subscribers.json   ← mailing list
      submissions.json   ← contact form submissions
  output/
    artists/{slug}/{page}/index.html  ← compiled static HTML (served by nginx)
```

## Request flow

```
Browser → nginx
  ├── /dashboard          → proxy to Flask → serves dashboard.html
  ├── /api/*              → proxy to Flask blueprints
  └── /artists/{slug}/**  → try static file in output/ first
                            → fallback to Flask if not found
```

## Compile flow

```
Artist edits content.md in dashboard
→ POST /api/adze/edit-page
→ compile.py --artist {slug} runs
→ reads artists/{slug}/{page}/content.md
→ wraps in base HTML template
→ writes output/artists/{slug}/{page}/index.html
→ nginx serves the static file on next request
```

## Analytics flow

```
Visitor loads artist page
→ nginx serves static HTML
→ tracking script injected (sessionStorage-based, no cookies)
→ on page hide: POST /api/adze/beacon (session duration, page count)
→ stored in artists/{slug}/data.db (pageviews + sessions tables)
→ dashboard /api/adze/analytics aggregates from SQLite
```

## Auth

- Per-artist token stored in `artists/{slug}/config.json` → `admin_token`
- Fallback super-admin token from env var `DEV_ADMIN_TOKEN`
- Dashboard sends `X-Artist-Slug` + `X-Admin-Token` headers on every request
- `POST /api/adze/login` sets a 30-day httpOnly `adze_session` cookie
- `GET /api/adze/whoami` restores session from cookie on page load
- Cookie is `slug:token` — verified server-side on every request

## Domain activation

Single endpoint `/api/adze/activate-domain`:
1. Writes nginx config to `/etc/nginx/sites-available/{domain}`
2. Symlinks to `sites-enabled/`
3. Tests nginx config
4. Reloads nginx
5. Runs certbot for SSL
6. Updates `config.json` with domain

## Feature system

Opt-in per-artist features that add API endpoints:
```json
// artists/{slug}/config.json
{ "features": ["bookings"] }
```
Flask auto-discovers `_shared/features/bookings.py` and registers its blueprint at `/api/artists/{slug}/bookings/`.

## Server environment

Flask runs in a Docker container (`adze-flask`) on port 5001. Host nginx proxies adze.studio (and all artist custom domains) to `127.0.0.1:5001`. Host certbot manages SSL. See `_shared/docs/05-deployment.md` for setup and new-server instructions.

- Compiled output lives at `/home/gabriel/adze/output/` on the host (mounted into the container at `/app/output/`)
- Artist data lives at `/home/gabriel/adze/artists/` on the host (mounted at `/app/artists/`)
- Claude CLI is installed inside the container; auth persists in the `claude_auth` Docker volume
- Google Cloud SDK (`gcloud`) is available at `/usr/bin/gcloud`, authenticated as `gabrielpenman@gmail.com`, project `geo-butler`

## Key design decisions

- **No database for content** — pages, config, subscribers, submissions are JSON files. Simple, version-controllable, zero setup.
- **SQLite for time-series** — analytics and sessions are append-heavy with aggregation needs. Per-artist `data.db`, WAL mode.
- **Static-first** — compiled pages are served directly by nginx (no server-side rendering at request time). Flask only handles API and dynamic content.
- **No cap** — SQLite removes the old 10k pageview cap.
