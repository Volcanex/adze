# Widgets — Dashboard panels in the artist admin

A widget is a small JS module that mounts a panel in the artist's admin dashboard. It runs inside a sandboxed iframe, talks to the host dashboard via a `ctx` object (postMessage-bridged), and uses the existing admin API for any backend ops (`ctx.apiFetch`, `ctx.getPageContent`, `ctx.savePage`, `ctx.assetList`, …).

## Tiers (the "T-numbers")

| Tier | Name | Location | Who edits | Visibility |
|------|------|----------|-----------|-----------|
| T2 | Platform | `_shared/widgets/<name>/` | Gabriel only (no in-dashboard editor) | All artists who opt in via `config.platform_widgets` |
| T3 | Community | `_shared/widgets/<name>/` with `forked_from=community` | Forked from T4, hideable per-artist | Artists who install from the marketplace |
| T4 | Custom / artist-private | `artists/<slug>/widgets/<name>.js` *or* `artists/<slug>/widgets/<name>/widget.js` | Editable in the dashboard widget editor | Only that one artist |

Promote a T4 widget to T3 via the **Share** action in the widget editor.

`ctx.tier` inside the widget reflects this (`platform`, `community`, `artist`).

## Shape

**T2/T3 (directory form):**
```
_shared/widgets/<name>/
  widget.json     # manifest: name, description, icon, author, version, marketplace, category
  widget.js       # (function(ctx){ ... })(ctx);
  README.md       # embed/setup notes
```

**T4 (single-file or directory form):**
```
artists/<slug>/widgets/<name>.js                # the IIFE
# or
artists/<slug>/widgets/<name>/widget.js + widget.json
```

Reference T2: `_shared/widgets/youtube/widget.js`.
Reference T4: `artists/mariaslaughter/widgets/add-to-gallery.js`,
`artists/rose/widgets/new-work.js`,
`artists/rose/widgets/new-exhibition.js`.

## The `ctx` object

`widget.js` runs as `(function(ctx){...})(ctx)` inside an iframe. The host bridges these through to the real admin API:

- `ctx.container` — DOM node to render into
- `ctx.artistSlug`, `ctx.tier`, `ctx.name`
- `ctx.pages` — list of page descriptors
- `ctx.assetList` — array of `{path, filename, is_image, …}` relative to `artists/<slug>/assets/`
- `ctx.apiFetch(url, opts)` — authenticated fetch (injects `X-Artist-Slug`, `X-Admin-Token`); pass `isFormData: true` for multipart uploads
- `ctx.getPageContent(slug)` → `{content, config}` for any page (uses `_valid_slug`, so single-segment slugs only)
- `ctx.savePage(slug, content, config)` — write a page
- `ctx.toast(msg, type)`, `ctx.escHtml`, `ctx.switchTab`, `ctx.reloadWidgets`

Style with dashboard CSS vars (`var(--text)`, `var(--text2)`, `var(--accent)`, `var(--bg)`, `var(--bg2)`, `var(--surface)`, `var(--border)`, `var(--radius)`, `var(--heading-font)`, `var(--mono)`).

## Backend touchpoints (admin API in `_shared/admin_api.py`)

- `POST /api/adze/upload-file` — multipart upload; auto-routes images → `assets/images/`, fonts → `assets/fonts/`, rest → `assets/`. Returns `{path}` relative to assets/.
- `POST /api/adze/create-page` — flat slug only (`works`, `about`, …).
- `POST /api/adze/create-nested-page` — `{parent_slug, child_slug, title, content, config}` for one-level nesting (e.g. `works/<slug>/`). Used by Rose's New Work / New Exhibition widgets together with `compile.py`'s recursive page discovery.
- `POST /api/adze/edit-page` — overwrite an existing page's content/config.
- `GET /api/adze/list-assets` — re-fetch the asset list after upload.

## Trust model

Widgets run with **admin auth** and may write to artist page files. They are developed by Gabriel (T2) or by the artist via the in-dashboard editor (T4). The vibe coder is sandboxed out of widget creation — see `_shared/docs/00-behaviour.md` lines 31–37.

## Adding a T2 (platform) widget

1. `_shared/widgets/<name>/widget.json` (manifest) + `widget.js` (IIFE)
2. `README.md` with embed syntax / setup notes
3. Test against a real artist via the dashboard widget editor
4. `sudo docker restart adze-flask` to reload (source is bind-mounted, no rebuild)

## Adding a T4 (artist-private) widget

1. Drop `artists/<slug>/widgets/<name>.js` (or the directory form)
2. It appears in that artist's dashboard automatically — `list-widgets` scans `artists/<slug>/widgets/` on every request
3. No restart needed for a new T4 widget; restart only if you touched `_shared/admin_api.py` or `flask_server.py`
