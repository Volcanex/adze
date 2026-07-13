# Features — Site-wide capability modules

Each `.py` file here is a feature that can be enabled for an artist site
by adding its name to `features` in the artist's `config.json`.
`flask_server._register_artist_features()` auto-discovers and loads them.

## Adding a feature

1. Create `_shared/features/<name>.py`.
2. Implement `create_blueprint(artist_slug) -> Blueprint`. The function
   receives the artist slug, must set `bp.url_prefix = ''`, and return
   the blueprint.
3. Add the feature name to the artist's `config.json` features array.
4. No changes to `flask_server.py` are needed.

## Custom artist admins — `content_admin` (config-driven, ONE module)

A custom admin is a per-artist `/admin` SPA on the artist's own domain. There is
**no per-artist Python** — every artist uses the single generic feature
`content_admin.py`, driven entirely by a `content_types` block in their
`config.json`. (This replaced the old hand-written `maria_admin.py` /
`rose_admin.py` / … modules, which duplicated auth + chrome + image handling
per artist and drifted independently.)

To give an artist a custom admin:

1. Add `"content_admin"` to `features` in their `config.json`.
2. Declare their content under `content_types` (see the example in
   `content_admin.py`'s module docstring). Each type has an `item` field schema
   and a `page` block:
   - **field types** (→ editors in the shared shell's `field-editors.js`
     registry): `text`, `textarea`, `number`, `date`, `boolean`, `select`
     (+`options`), `tags`, `image` (+`multiple`), `markdown` (EasyMDE),
     `richtext` (Quill). Field opts: `required`, `slug_source` (which field
     becomes the item `id`), `format:"url"`, `label`.
   - **page.mode**: `single` (one page lists all items), `per_item` (a page per
     item + an optional index via `index_template`), `none` (no page — items are
     published to `assets/data/<type>.json` for a client-side grid to `fetch`).
   - `page.parent` is the URL dir; `"."` = the artist root (siblings of static
     pages like `home/`).
3. Add an `admin_theme` block (CSS vars: `bg`, `surface`, `text`, `accent`,
   `accentText`, `border`, `font`) to brand the admin.
4. Write the per-artist Jinja templates named in `page.template` /
   `index_template`, under `artists/<slug>/templates/`. These hold the design;
   the engine fills them with data. Template output **is** the page `content.md`
   (a `<style>…</style>` + `<html>…</html>` blob). Autoescape is on; use
   `{{ x|safe }}` for pre-sanitised richtext. Relative asset URLs must match page
   depth (`../assets/…` at `<parent>/`, `../../assets/…` at `<parent>/<id>/`).

Data lives in `artists/<slug>/content.json` keyed by type; each item is a dict
with an `id`. The JSON is the source of truth; pages are always derived.

What the engine (via the underlying `ArtistAdmin` framework) still owns and you
never re-implement: **auth** (domain guard + `admin_token` from `config.json`),
the **rebuild transaction** (`render()` → `.generated.json` → `compile.py`), and
the **generated-page manifest** (those pages are read-only to `/edit-page` and
the control-panel editor).

**Safe pruning (important):** on rebuild, `_prune_stale` removes only page dirs
that were in the *previous* `.generated.json` and are no longer generated. A
hand-authored sibling the engine never created (static `home/`, `videography/`)
is never touched — even at `parent:"."`. Publish can't destroy a page it didn't
make.

**Images**: `content_admin` uploads route through `asset_store.store_image`
(tiered `full`/`display` + 64px thumb + `output/` mirror + `asset_meta`), storing
`{src, full, ar}` per image. Paths are relative to the artist's `assets/` dir;
the shell renders admin thumbnails from `/assets/<src>` (served by the artist
domain's nginx). No per-artist upload code.

**Control-panel handoff**: the shell's "Advanced editing →" link hits
`{prefix}/handoff`, which (once the artist is logged in) mints the `adze_session`
cookie and redirects to `/api/adze/dashboard?slug=<slug>` — same-origin on the
artist's own domain, no re-auth, no token in the URL.

**`output/` ownership gotcha (general):** a host-side **root** `compile.py` run
leaves `output/artists/<slug>/` owned by uid 0, after which the container (`adze`,
uid 1000) can't overwrite them and Publish 500s with `PermissionError`. Fix:
`sudo chown -R 1000:1000 output/artists/<slug>`. Always compile as uid 1000.

### Describe the admin for the handover page

The handover page auto-detects a `content_admin` feature + domain and shows a
"Your dashboard" card. `admin_api._dashboard_info()` supplies the copy; the old
per-module `DASHBOARD_INFO` export is gone with the bespoke modules.

## Feature vs widget

- **Widget**: embeddable content in one spot on a page. Small surface.
- **Feature**: a system spanning multiple pages or long-running state.

If you're unsure which, start with a widget.
