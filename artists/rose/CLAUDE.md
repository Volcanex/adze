# Rose Jones — rosefpjones.com

**`content.json` is the source of truth** (types: `works`, `exhibitions`).
Rose's admin is the generic `content_admin` feature (`/admin` on rosefpjones.com),
driven by the `content_types` + `admin_theme` blocks in `config.json`. Page
`content.md` files are **generated** from `content.json` via the Jinja templates
in `templates/` — not hand-authored.

## ⚠ Do NOT hand-edit the generated pages
Overwritten on every publish (they're listed in `.generated.json`, so `/edit-page`
and Auto-Code refuse direct edits):
- `works/<slug>/content.md` + `works/content.md` (index)
- `exhibitions/<slug>/content.md` + `exhibitions/content.md` (index)

To change them, edit **`content.json`** (data) or the **templates** (layout/CSS).
`home/`, `about/`, `contact/` are ordinary hand-authored pages — edit directly.
(`about/` is deliberately NOT a content type.)

**Except the about-page CV.** `about/content.md` carries a bare
`<!-- EXHIBITIONS_BLOCK -->` marker; compile.py's `_inject_data_placeholders`
fills it from **`assets/data/exhibitions.json`** — the published feed the content
admin writes on every rebuild — newest year first, each entry rendered
`{year} {title}, {type lowercased}, {location}` and linked to
`/exhibitions/<id>/`, joined by `/`. So a show is added to the CV by adding it to
**`content.json`** like any other, which is what guarantees every CV line has a
page behind it. Don't type exhibitions into the page.

`information.json` is a provenance ledger (where each image came from, which
works are real but unphotographed), not a feed — compile.py does not read it.
Keep its exhibitions list in step with `content.json` when a show is added.

## Templates (`templates/`)
`work.html`, `exhibition.html`, `works_index.html`, `exhibitions_index.html` —
full pages with the shared chrome (header, hamburger menu, loading veil, footer),
carrying Jinja logic that reproduces the previous generator exactly (meta spans
only for present fields, missing-image placeholder, works grouped by year desc,
exhibitions-index hero = first item with images). A site-wide chrome change is an
edit to these four files. (`_templates/` is the pre-migration copy, now unused —
`templates/` is live.)

## Image tiers (per image `<stem>`, e.g. `work-bed`)
- `<stem>-full.jpg` — full-res master, source of truth. **Unserved.** Kept in `assets/`.
- `<stem>-good.jpg` — 2560px / q88 display tier. What pages reference.

Existing `content.json` image entries point `src` at the `-good` tier and `full`
at `-full`, with an `aspect` (W/H) for the figure placeholder. New uploads through
the admin route via `asset_store.store_image` (which writes `{full, display, ar}`
and a display derivative) — the shell stores `src`=display, `full`=full, plus
`ar`/`aspect`. A work/exhibition with no resolvable image renders **no figure at
all** — the templates loop `{% for img in item.images or [] %}{% if img.src %}`,
so a missing `images` list *and* an entry with an empty `src` both render nothing
rather than a stand-in box. The exhibitions index picks its hero from the first
item whose `images[0].src` is set, and drops the hero figure entirely if none is.
Keep it that way: a half-filled work should read as text, not as a broken image.

## Menu = title (2x2 conveyor)
The hamburger menu is a 2x2 grid: Works / About top, Exhibitions / Contact below.
There is **no separate `<h1>`** — the current page's menu link carries `is-current`
and stays as the always-visible page title; the others slide in front (z-index).
`.page` reserves the zone with `padding-top` (140px mobile / 190px desktop). To
retitle a page, change which link has `is-current`. This chrome lives in the four
`templates/` files **and** hand-authored `about/`/`contact/content.md` — keep them
in sync. `home/content.md` has no menu, left as-is.

## Bespoke extras (removed with the old admin — see repo root discussion)
The old `rose_admin.py` had a QR-code / business-card generator and an admin-font
route. These were panel utilities, not content, and came out when the bespoke
module was deleted (recoverable from git). If wanted, re-home QR as a shared shell
feature rather than per-artist code.

## Gotcha: compile as uid 1000, never host root
Host-root compiles leave root-owned files in `output/artists/rose/` the container
(uid 1000) can't overwrite → publish 500s. Compile in-container
(`sudo docker exec adze-flask python3 compile.py --artist rose`) or fix with
`sudo chown -R 1000:1000 output/artists/rose`.
