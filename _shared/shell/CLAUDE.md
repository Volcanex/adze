# shell/ — the shared artist-admin front-end

The single UI behind every artist's custom admin (`content_admin`). No per-artist
markup, no build step, plain vanilla JS/CSS — served same-origin under each
artist's own admin prefix by `content_admin`'s `{prefix}/asset/<name>` route (it
reads these files fresh from disk; single source, per-artist route), mirroring the
`asset_tree.js` pattern.

- `admin-shell.js` — `window.AdminShell.init({prefix})`. Fetches `{prefix}/schema`,
  renders the login screen, a nav of the artist's content types, list/edit views
  (fields built from the registry), a Publish button, and the "Advanced editing →"
  handoff link to the Adze control panel. Applies `admin_theme` CSS vars.
- `field-editors.js` — `window.AdzeFields`, the pluggable field-type registry:
  `{type → fn(fieldName, fieldDef, value, ctx) → {el, value()}}`. Adding a new
  field type = one `register()` call; no shell/schema changes. `text/textarea/
  number/date/boolean/select/tags/image` are native; `markdown` → EasyMDE,
  `richtext` → Quill (the reference WYSIWYG, "ready to wire in" — no migrated
  artist uses them yet, but a schema `"type":"richtext"` field lights them up).
  Image thumbnails resolve from `/assets/<src>` (the artist domain's nginx).
- `admin-shell.css` — layout and component shape only, on the **Adze design
  language** (adopted 2026-07-30). Every colour, size, radius and duration is a
  token; a literal hex in this file is a bug. Per-artist palette via the six
  `--adze-artist-*` vars that `applyTheme()` sets from `config.admin_theme`.

## Tokens are served live, not copied

`content_admin.py` serves `design-language/adze/tokens/*.css` under
`{prefix}/asset/tokens/<name>` (`TOKEN_FILES`, cascade order matters) and links
them ahead of `admin-shell.css`. There is no second copy to drift — editing the
design language restyles every artist admin on the next load. This needs
`./design-language:/app/design-language:ro` in `docker-compose.yml`; without it
the container serves a stale copy baked in at image-build time and the token
requests 404.

`fonts.css` is deliberately **not** served: it `@import`s Google Fonts, which is
render-blocking and serial inside a linked sheet. The bootstrap `<head>` uses a
`<link>` plus preconnects instead. Self-hosting Inter and JetBrains Mono under
`../vendor/fonts/` is the outstanding win — it would remove the last external
origin from the artist admin.

## Feedback helpers

`admin-shell.js` exposes the design language's feedback components as plain DOM:
`skeletonRows(n)`, `spinner(size, tone)`, `progressBar(label)`,
`emptyState(title, body, action)` and `withBusy(btn, fn)`. Use these rather than
inventing loading states.

`withBusy` is required on any async submit. It adds `is-busy`, which sets
`pointer-events: none` **synchronously** — that, not `disabled`, is what stops a
double-publish, because `disabled` set after an `await` leaves a window open.
Omit the `tone` argument for a spinner inside a filled button, so it inherits
`currentColor`; an `--adze-accent` spinner is invisible on an accent background.

## The class-name contract

`as-*` (shell chrome) and `af-*` (field editors) are built as literal strings in
`admin-shell.js` and `field-editors.js`. Renaming one in the CSS silently
unstyles it — change all three files or none.

Vendored libraries live in `../vendor/` (Quill, EasyMDE — JS + CSS), served via
the same `{prefix}/asset/vendor/<lib>` route. **Vendored, not CDN** — no external
hosts, works offline, reproducible. To update a lib, replace the file in
`../vendor/` (keep the filename the vendor map in `content_admin.create_blueprint`
expects).

Trust model: these are Gabriel-authored platform components, mounted **unsandboxed**
in the panel document (like the live-widget path, not the iframe preview sandbox) —
so editors get direct DOM/selection access. Don't route them through postMessage.
