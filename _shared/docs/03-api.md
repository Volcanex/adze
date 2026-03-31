# API Reference

All endpoints are under `/api/adze/`. Authenticated endpoints require `X-Artist-Slug` and `X-Admin-Token` headers, or a valid `adze_session` cookie.

## Auth

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/login` | No | Validate credentials, set session cookie. Body: `{slug, token}` |
| POST | `/logout` | No | Clear session cookie |
| GET | `/whoami` | Cookie | Return authenticated artist info |

## Dashboard

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/dashboard` | No | Serve dashboard.html |

## Pages

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/list-pages` | Yes | List artist's pages |
| GET | `/get-page-content` | Yes | Get page `content.md` + `config.json`. Query: `?page_slug=home` |
| POST | `/edit-page` | Yes | Update page. Body: `{page_slug, content?, config?}`. Returns `{compile_ok, compile_error}` |
| POST | `/create-page` | Yes | Create new page. Body: `{page_slug, title, content?, config?}` |
| POST | `/delete-page` | Yes | Delete a page. Body: `{page_slug}` |

## Assets

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/list-assets` | Yes | List all assets for artist |
| POST | `/upload-file` | Yes | Upload file to `assets/`. Multipart form. Blocked extensions: exe, bat, sh, php, py, etc. |

## Analytics

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/analytics` | Yes | Aggregated analytics (today/week/month views, daily chart, countries, sources, bounce rate, etc.) |
| POST | `/beacon` | No | Session duration heartbeat from tracking script. Body: `sid={}&slug={}&dur={}&pc={}` |

## Contact / Inbox

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/contact` | No | Public contact form. Body: `{artist_slug, name, email, subject, message}` |
| GET | `/list-submissions` | Yes | List contact form submissions |
| POST | `/delete-submission` | Yes | Delete submission. Body: `{id}` |
| POST | `/mark-submission-read` | Yes | Mark read/unread. Body: `{id, read}` |

## Subscribers

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/subscribe` | No | Public subscribe. Body: `{artist_slug, email, name?}` |
| GET | `/list-subscribers` | Yes | List subscribers |
| POST | `/delete-subscriber` | Yes | Delete subscriber. Body: `{email}` |
| GET | `/export-subscribers` | Yes | Export as CSV |

## Site config

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/artist-info` | Yes | Get artist config (minus token) |
| POST | `/update-site-config` | Yes | Update safe config fields (name, description, favicon, etc.) |
| POST | `/update-domain` | Yes | Update domain field |
| POST | `/activate-domain` | Yes | Auto-configure nginx + certbot SSL |
| POST | `/install-google-font` | Yes | Download Google Font TTF files to `assets/fonts/` |

## Widgets

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/list-widgets` | Yes | List available widgets (T2 + T4) |
| GET | `/get-widget` | Yes | Get widget source. Query: `?name=youtube` |
| POST | `/save-widget` | Yes | Save T4 widget source |
| POST | `/new-widget` | Yes | Create new T4 widget |
| POST | `/delete-widget` | Yes | Delete T4 widget |
| POST | `/fork-widget` | Yes | Fork T2/T3 widget to T4 |
| POST | `/share-widget` | Yes | Publish T4 widget to T3 community marketplace |

## Vibe Coder (Claude)

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/claude-stream` | Yes | Stream Claude CLI response (SSE). Body: `{prompt}` |
| POST | `/claude-reset` | Yes | Reset Claude session for artist |
