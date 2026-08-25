# Lydia Lott (lydialott) — lydialott.co.uk

**`content.json` is the source of truth** (single type: `works`), edited through
the generic `content_admin` admin. On publish it is written out to
**`assets/data/works.json`** with drafts filtered — that published feed is the
only thing the site reads. The two files legitimately differ by any draft item;
that is not drift.

## The whole site is one script

`home/` and `works/` contain no content. Each is an empty
`<div id="ll-root">` plus `assets/works-grid.js`, which fetches
`assets/data/works.json` and builds everything client-side —
`data-mode="landing"` (home, selected works) vs `data-mode="browser"` (works,
all works + tag filters). `about/` and `singleview/` are ordinary pages.

**Consequence: any JS throw blanks the entire site**, and it fails *silently* in
a misleading way. `render()` runs inside the `fetch(...).then()` chain, so a
throw there is caught by the `.catch` that was written for network failures and
the page is replaced with `Could not load works.json: <error>`. That message has
nothing to do with the fetch — the JSON loaded fine. Read the error after the
colon, not the sentence in front of it. Nothing appears in the server logs
because nothing failed on the server.

## Two orientations, and why the layout maths differ

The grid has two modes, toggled in the header (`ROWS`/`VERT_COLS` in
`assets/works-grid.js`):

- **Horizontal** — desktop default. `ROWS = 2` fixed rows scrolling sideways;
  tile size is derived from *viewport height ÷ ROWS* so two rows exactly fill
  the screen. Clicking a work opens `.ll-iso2` beside the tile, taking the two
  columns to its right.
- **Vertical** — mobile always, plus the desktop toggle. Columns scrolling
  down; tile size is derived from *available width ÷ column count*
  (`vertCols()`: 3 wide, 2 under 1000px, 2 on mobile), capped at
  `VERT_TW_MAX` so a wide monitor centres the grid instead of stretching it.
  Clicking a work expands the **row**: `.ll-band` opens full-width beneath it
  and the rows below slide down by `bandH`.

**The two sizing rules are not interchangeable.** Vertical briefly used the
horizontal rule (height ÷ ROWS), which left the grid's width unrelated to the
viewport's: a ~250–400px dead gutter on wide screens, and below ~1200px a grid
*wider* than its own `overflow-x: hidden` container, silently clipping the last
column off the page with no way to scroll to it. If you touch `fitTiles()`,
keep the branches separate.

`.ll-band` replaced an earlier fixed bottom sheet (`position: fixed; bottom: 0`)
that covered up to 50vh of the grid and detached the text from the work it
described. Don't reintroduce it — the reason the side panel can't simply be
reused in vertical is that a rightmost-column tile pushes it off the grid, and
expanding the row is what solves that at any column.

`bandH` feeds `sizeGrid()` and `snapAll()`; the band is re-measured on
`bandImg` load because until the full-size image decodes it is only as tall as
its text. That re-measure must not re-scroll (`positionBand(..., false)`).

## ⚠ `image` has two shapes — never assume string

Per work, `image` is **either**:

- a bare path string (`images/weather-ii.jpeg`) — hand-authored entries, whose
  grid thumbnail is a sibling at `images/thumbs/<stem>.webp`; **or**
- the tiered object `content_admin` writes for anything uploaded through the
  dashboard — `{src: display tier, full, card, ar, aspect}` (see
  `_shared/asset_store.py:store_image`) — stored under
  `assets/works/<item-id>/` with **no `thumbs/` sibling**.

`works-grid.js` funnels both through **`imagePaths(w)` → `{thumb, full}`**; the
grid uses `thumb` (the `card` tier for objects), the enlarge overlay uses `full`
(the `display` tier — `full` proper is the multi-MB master). Use that helper for
any new image read. Doing string ops on `w.image` directly is what broke the
site on 2026-07-27: Lydia uploaded a work through the dashboard, it published as
an object, `w.image.replace(...)` threw `TypeError: w.image.replace is not a
function` on the second item, and **every page rendered empty for ten days**.
Fixed 2026-08-06.

This is a standing hazard, not a one-off — every dashboard upload produces the
object shape, so a string assumption anywhere here is a live time bomb rather
than a latent one.

## Gotcha: uploaded images 404 in the dashboard preview

Dashboard uploads land in `assets/works/<item-id>/…`, and Flask registers
`/assets/<page_slug>/<path>` — so `/assets/works/…` is read as "page assets for
the page `works`", which this artist has, and 404s. Production is unaffected
(nginx `location /assets/` aliases the directory), so this only bites the
preview iframe. Platform-level, documented in the repo root; don't work around
it here.

## Compile

`sudo docker exec -w /app adze-flask python3 compile.py --artist lydialott` —
in-container or as `gabriel`, **never as host root** (root-owned files under
`output/artists/lydialott/` become unwritable by the container, uid 1000).
`assets/` is not tracked by this artist's git repo.
