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
- `admin-shell.css` — one theme; per-artist palette via CSS vars set by
  `applyTheme()` from `config.admin_theme`.

Vendored libraries live in `../vendor/` (Quill, EasyMDE — JS + CSS), served via
the same `{prefix}/asset/vendor/<lib>` route. **Vendored, not CDN** — no external
hosts, works offline, reproducible. To update a lib, replace the file in
`../vendor/` (keep the filename the vendor map in `content_admin.create_blueprint`
expects).

Trust model: these are Gabriel-authored platform components, mounted **unsandboxed**
in the panel document (like the live-widget path, not the iframe preview sandbox) —
so editors get direct DOM/selection access. Don't route them through postMessage.
