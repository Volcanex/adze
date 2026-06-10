# Rose Jones — generated from information.json

**`information.json` is the source of truth for this site.** Rose's admin
(`/admin` on rosefpjones.com, served by `_shared/features/rose_admin.py`)
reads/writes it and uploads images. The page `content.md` files are
**generated**, not hand-authored.

## ⚠ Do NOT hand-edit the generated pages
These are overwritten on every compile — edits are lost:
- `works/<slug>/content.md`, `works/content.md` (index)
- `exhibitions/<slug>/content.md`, `exhibitions/content.md` (index)
- `about/content.md`

To change them, edit either **`information.json`** (data: titles, years,
medium, dimensions, status, images) or the **templates in `_templates/`**
(layout/CSS). `home/` and `contact/` are NOT generated — edit those directly.

## Pipeline
`POST /api/rose-admin/compile` (or the admin "compile" action) runs:
1. `rose_pages.regenerate(info)` — writes all generated `content.md` + ensures
   image tiers exist, from `information.json`.
2. `compile.py --artist rose` — the normal content.md → HTML step (also fills
   the `<!-- EXHIBITIONS_BLOCK -->` placeholder on the About page).

Regenerate by hand from the repo root: `python3 _shared/features/rose_pages.py`.
The generator (`_shared/features/rose_pages.py`) and admin (`rose_admin.py`)
are Rose-scoped; they do **not** touch shared `compile.py`.

## Image tiers (per image `<stem>`, e.g. `work-bed`)
- `<stem>-full.jpg` — full-res master, the source of truth. **Unserved** — never
  referenced by a page. Kept in `assets/`.
- `<stem>-good.jpg` — 2560px / q88 display tier. The only image pages reference.

Admin uploads call `rose_pages.save_master(stem, file)` which writes the master
**and** derives the display tier. Stored image ids in `information.json` are
logical (`work-bed.jpg`); the generator derives `-full`/`-good` from the stem,
and `serve_asset` resolves logical ids to the display tier for admin previews.
There is no blur/`-fast` tier — the loading veil (in the templates) covers the
load gap instead. A work/exhibition with `status: "missing"` (or no resolvable
image) renders a "(Work file missing)" placeholder box.

## Templates (`_templates/`)
`work.html`, `exhibition.html`, `works-index.html`, `exhibitions-index.html`,
`about.html` — full pages with `{{TOKEN}}` slots the generator fills. They carry
the shared chrome (header, hamburger menu, loading veil, footer, scripts), so a
site-wide chrome change is an edit to these five files, not 40 pages.
