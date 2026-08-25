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
     (+`options`), `tags`, `image` (+`multiple`), `file` (+`multiple`,
     `accept`, `max_mb` — see below), `markdown` (EasyMDE),
     `richtext` (Quill). Field opts: `required`, `slug_source` (which field
     becomes the item `id`), `format:"url"`, `label`.
   - **page.mode**: `single` (one page lists all items), `per_item` (a page per
     item + an optional index via `index_template`), `none` (no page at all).
   - **Every mode publishes `assets/data/<type>.json`** on rebuild, not just
     `none`. A hand-authored page can `fetch` it for a teaser grid instead of
     carrying a hand-copied duplicate that goes stale the next time the artist
     publishes (jackdt's homepage does this for its latest-four block). Note the
     root `CLAUDE.md` "asset URLs must be flat" gotcha: `/assets/data/x.json`
     resolves fine through nginx in production but 404s in the dashboard's
     preview iframe, so any consumer must degrade quietly.
   - `page.parent` is the URL dir; `"."` = the artist root (siblings of static
     pages like `home/`).
   - `page.config` (optional dict) is merged verbatim into the generated page's
     `config.json` — carry keys the compiler cares about that aren't
     title/description, e.g. `{"hidden": true, "categories": ["portfolio"]}`. This
     is what lets a hand-authored page keep its config when it becomes editable.
3. Add an `admin_theme` block to brand the admin. **Exactly six keys**: `bg`,
   `surface`, `text`, `accent`, `accentText`, `border`. Opaque colours only —
   an `rgba()` value poisons every `color-mix()` derivation downstream. There
   is deliberately **no `font` key**: type belongs to the Adze design language,
   colour belongs to the artist. See `/adze-content-admin` (the skill) and
   `design-language/adze/CLAUDE.md` for the full contract.
4. Write the per-artist Jinja templates named in `page.template` /
   `index_template`, under `artists/<slug>/templates/`. These hold the design;
   the engine fills them with data. Template output **is** the page `content.html`
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

### The `file` field type — video, audio, PDFs (added 2026-08-05, for jackdt)

`image` promises a raster the page can crop and size: it has display/card tiers
and an aspect ratio. `file` is for everything else a page can render. They are
**deliberately separate types with separate routes**
(`{prefix}/<ctype>/<iid>/file`, mirroring the image pair) — folding them
together would mean every existing consumer of an image field having to cope
with an entry that turns out to be an mp3.

- `accept` lists **kinds**, not extensions: `["video"]`, `["image","video",
  "audio","doc"]`. The extension table lives in `_FILE_KINDS` in
  `content_admin.py` and nowhere else, so an artist config says what a field is
  *for* and this module owns what containers that means today.
- Each stored entry carries `{src, full, kind, name, size}`, plus `card`/`ar`
  when the upload was an image (an image dropped into a mixed field still goes
  through `store_image`, so it keeps its tiers). **Templates dispatch on
  `kind`** and must never re-parse the extension — that would be a second copy
  of the table.
- `max_mb` is the client-side guard, and it exists because the **real** limit is
  `client_max_body_size` on the artist's nginx vhost. Over that, nginx returns
  its own 413 HTML page, which the admin's `fetch` can only report as a bare
  failure — after the artist has waited out the whole upload. Set `max_mb` just
  under the vhost value and **change the two together**. jackdt: 200MB field /
  220M vhost. Remember assets are stored twice (canonical + `output/` mirror),
  so a 200MB file costs 400MB of disk.

**Both media types are server-owned.** `_managed_fields()` covers `image` *and*
`file`, so `_clean_item` strips them from any JSON body: a save that happened to
carry a stale array cannot revert an upload. The shell has the matching
`SERVER_OWNED` list. If a third media type is ever added, those two lists are
what it has to join — verified by trying to PUT `{"video": "HIJACKED"}`, which
is discarded.

**Control-panel handoff**: the shell's "Advanced editing →" link hits
`{prefix}/handoff`, which (once the artist is logged in) mints the `adze_session`
cookie and redirects to `/api/adze/dashboard?slug=<slug>` — same-origin on the
artist's own domain, no re-auth, no token in the URL.

**`output/` ownership gotcha (general):** a host-side **root** `compile.py` run
leaves `output/artists/<slug>/` owned by uid 0, after which the container (`adze`,
uid 1000) can't overwrite them and Publish 500s with `PermissionError`. Fix:
`sudo chown -R 1000:1000 output/artists/<slug>`. Always compile as uid 1000.

### Editable copy on a hand-authored page (the singleton "copy" pattern)

A common need: let an artist edit the **prose** on a bespoke, hand-designed page
(a home page, an about page) without touching the layout. This reuses the same
machinery — no new engine code — as a **singleton** content type:

1. Declare a content type (e.g. `"copy"`) whose `item` fields are the editable
   text blocks (`text` for one-liners, `textarea` for multi-line). `page.mode:
   "single"`, `page.parent` = the page's dir (e.g. `"home"`).
2. Convert that page's hand-authored `content.html` into the type's
   `page.template`. Keep **all** the markup and `<style>` verbatim; replace only
   the copy with `{{ copy.<field> }}`, where `{% set copy = items[0] if items
   else {} %}` treats the single item as the record.
3. Seed `content.json` with one item holding the current copy, so the first
   publish reproduces the page unchanged. Use `page.config` (above) to preserve
   flags like `hidden`.
4. **Multi-line → `<br>`**: don't `replace('\n','<br>')|safe` — Jinja's `Markup`
   re-escapes the inserted tag (`&lt;br&gt;`). Split and let each line autoescape:
   `{% for line in (copy.body or '').split('\n') %}{{ line }}{% if not loop.last %}<br>{% endif %}{% endfor %}`.

By convention this type holds exactly one item; the shell's list view still shows
an "Add", so label it clearly (e.g. `"Home text"`) and seed the one row.
`artists/mariaslaughter/` uses this for its home page alongside `gallery`/`music`
photo editors — a worked reference.

### Self-service password change

Artists change their own password from the shell's **Account** button →
`POST {prefix}/password` (`{current, new}`), handled in `artist_admin.py`'s
`register_core`. It verifies the current token, writes the new `admin_token` to
`config.json` via `ArtistAdmin.set_token`, and re-mints the session cookie. Unlike
the one-time handover-page change (`admin_api.handover_set_password`, which sets
`password_changed` to lock itself), this path is **repeatable**.

### Describe the admin for the handover page

The handover page auto-detects a `content_admin` feature + domain and shows a
"Your dashboard" card. `admin_api._dashboard_info()` supplies the copy; the old
per-module `DASHBOARD_INFO` export is gone with the bespoke modules.

## Feature vs widget

- **Widget**: embeddable content in one spot on a page. Small surface.
- **Feature**: a system spanning multiple pages or long-running state.

If you're unsure which, start with a widget.

## content_admin: drafts and the copy routes (2026-07-31)

**Items are created as drafts.** `POST {prefix}/{ctype}/draft` creates an empty
item immediately and returns it with `_draft: true` and `_draft_at`, so image
uploads (which need `{ctype}/{id}/image`) have an id from the first second.
`PUT` clears both flags on save. `GET {prefix}/{ctype}` returns drafts *and*
sweeps any older than 24h — no cron.

**THE draft gate is one line**: `items = _live(items)` at the top of
`make_render`'s per-type loop. The data feed, the listing page, the per-item
index and every per-item page all come off that filtered list, so there is no
way to add a published artefact that bypasses it. `compile.py`'s
`_copy_live_items` is a second layer when mirroring feeds to `output/`. A draft
reaching a live domain is the worst failure this feature could have; keep the
single choke point rather than filtering at N call sites.

**The copy routes are `{prefix}/_copy`, not `{prefix}/copy`** — mariaslaughter
has a content type literally named `copy`, so the bare path collides with the
generic `{prefix}/{ctype}` route and would shadow her real content. `GET`
returns `{pages:[{page,label,slots:[{id,rich,default,value}]}], orphans:[]}`;
`PUT` merges. `GET {prefix}/schema` carries a boolean `copy`, which is how the
front-end decides whether the Text section exists at all — so rollout is
per-artist by construction, with no feature flag.

`put_copy` **re-derives which slots are rich from the artist's markup** and never
trusts the client, so a plain-value-into-a-rich-slot mismatch is not expressible.
Orphans (overrides whose slot no longer exists in source) are surfaced, never
silently dropped.

## `schema.unpublished` — saved is no longer the same as live (2026-07-31)

The admin autosaves (see `shell/CLAUDE.md`), so a write no longer implies the
artist meant to ship. `_unpublished(slug)` answers whether the compiled site is
behind what has been saved, and the schema carries it so the footer can say so on
first paint rather than only after the artist types something.

It is **derived from mtimes, never stored**: `content.json` and `copy.json`
against `.generated.json`. A stored flag would be a second source of truth for
something the filesystem already knows, and it is the copy that goes stale — a
publish that died inside `compile.py` would clear the flag while leaving the old
built site in place. `.generated.json` is written by `ArtistAdmin.rebuild()` as
part of the same transaction, so it only moves when a publish actually got that
far.

Unknown counts as unpublished. An artist told "everything is live" about a site
that isn't has no reason to press the button, which is the failure that matters.

Write paths that bypass these two files (a route that edits config, say) will not
show up here. If one is added and should count, extend the tuple in
`_unpublished` rather than introducing a flag.
