# Beth Darroch (beth) — beth.adze.studio

Freelance fashion and culture journalist, London. Built 2026-09-08.
Editorial black-on-white layout. The writing is her real published work —
see "Content" below for provenance and for what is still placeholder.

## Shape

Four pages: `home` (index), `writing`, `about`, `contact`. Navigation is a
sticky **masthead**, not a sidebar (an earlier dark build used a sidebar;
any doc or CSS still referring to `.sidebar` is stale).

## Where the CSS lives — read this before editing a page

**All shared styling is in `default-styles.css`, not in the page files.**
`compile.py` prepends that file to every page's `<style>`, so it is the one
place site-wide rules belong — including the `@font-face` blocks, which are
declared there exactly once. A page's own `<style>` holds only what is
genuinely specific to it (`.hero` on home, `.about-grid` on about).

The adze template this started from repeated the full `@font-face` +
body/nav CSS in every `content.html`. That is the thing to avoid: five
copies that drift apart. If you are pasting a rule into a second page, it
belongs in `default-styles.css`.

Same rule for markup that repeats on every page (`.progress`, `.masthead`,
`.draft-bar`): the markup has to repeat because adze has no partials, but
its CSS and its behaviour must not.

## Design language

Black on white, editorial. **One ink: no grey text and no grey rules**
(Gabriel, 23 Sep) — hierarchy comes from size, face and weight. Rules are
`--rule: 1.5px`, matched to the weight of the type; don't go back to 1px.

Three faces, all vendored in `assets/`:

- **Archivo** — display headings and the wordmark, uppercase, 700-800,
  heavy negative tracking.
- **Crimson Pro** (OFL, from Google Fonts) — the *writing*: card headlines,
  page intros, the About standfirst. It is the secondary voice Gabriel asked
  for, modelled on to Be Magazine's Sabon. **Do not lift to Be's own font
  files** (their bespoke "To Be" family and a licensed Sabon): unlicensed,
  and it would make her portfolio look like their site. An earlier Cardo
  build was dropped for its calligraphic italic; keep Crimson upright.
- **Inter** for body, a system mono stack for every label, meta line, date.

**The grid.** One column system for every page: `--cols` (6 / 5 / 4 / 3 /
2 / 1 at 1800 / default / 1360 / 1080 / 860 / 560px) and `--gutter`, in
`default-styles.css`. The banner, hero, sheet, About's text/portrait split
and the timeline all use `repeat(var(--cols), ...)`, so edges line up
across sections. Every page is full width to the masthead's edges; prose
keeps a measure with `ch` max-widths on the text, never by capping the page.

**Film grain.** `body::after`, a moving `feTurbulence` tile at `opacity: .16`.
It was .34 and read as grey dirt on the page.

**`.plate`** wraps every article image, full colour, **no filter at rest**
(hover must never read as desaturate-then-resaturate). The halftone dot
screen was removed on 23 Sep ("I don't like the grey dotted stuff"). Hover
is the only motion on the site and never moves the plate box: inside its
clip the image gains `saturate(1.1)` and a soft 3% zoom, easing in and
out over .8s. A bloom glow and a stepped tremor were both tried and
rejected on 23 Sep; keep it to the zoom.

**`.banner`** (home only) is the black strip under the masthead that
replaced the hero's kicker and standfirst.

## The contact sheet

`writing/` and `home/` list articles as a `.sheet` of `.card`s on the site
grid. One card is a `.plate` image, a two-line mono `.meta`, and the
headline in Crimson Pro. Nothing else.

Decisions worth not undoing:

- **No section headings on these pages.** The images carry the page.
- **Publication lives in the meta**, since there are no headings to carry it.
- **`.card .meta` is a fixed two-line flex column** — publication, then kind
  and date. As one line it wrapped on the longest entry and knocked that
  card's headline out of alignment across the row.
- **Home leads with the latest piece** in `.hero` (name spans all columns
  but the last two, the featured card takes those two) and drops it from
  the grid below.

`writing/` is one merged grid in strict reverse-chronological order — **if
you add a piece, keep that order.**

## Behaviour — `assets/site.js`

Shared by every page: nav current-page marking, mobile menu, scroll
progress bar. Loaded as `site.js?v=YYYYMMDDx` — **bump that stamp in all
four `content.html` files on every JS change**: nginx serves assets with a
24h cache while the HTML (with CSS inlined) is `no-cache`, so a stale script
against fresh CSS is the failure mode.

`assets/motion.js` is **motion@11.11.13**, vendored from jsDelivr's `+esm`
build. v12's `+esm` is a one-line re-export from the CDN — don't
"upgrade" to it without re-bundling. Only the progress bar uses it now.

**No scroll reveals.** They were removed on 23 Sep. `.mask` keeps
`overflow: hidden` so anything that does animate cannot spill.

**Mobile menu.** `site.js` clones `.nav-links` into a `<nav
class="menu-overlay">` appended to `<body>`. It must not live inside the
masthead: a `position: fixed` child of the sticky (once backdrop-filtered)
masthead resolved against the wrong box and covered its own close button.
The overlay sits at z 39 under the masthead's 40, so the X is always on
top. Scroll lock is on `<html>` only — locking `<body>` too made the sticky
masthead jump off screen when opened mid-page.

## Assets must be flat

Files sit directly in `assets/` (`motion.js`, `site.js`, the
`.woff2` fonts) — **not** in subfolders. Flask's preview route reads
`/assets/<subdir>/file` as "page asset for page `<subdir>`" and 404s, so a
subfolder works in prod and breaks the dashboard preview iframe.
`assets/fonts/` still exists from the template; the fonts were copied up to
the root and those copies are what the CSS references.

## Content — real, and where it came from

**The 19 pieces on `writing/` are Beth's actual published work**, not
placeholder. They were found by open-web search (her LinkedIn has zero
posts and was useless for this) and each one was verified by fetching the
live page and confirming the byline and `article:published_time`:

- **10 Magazine** — 12 pieces, 20 Mar – 14 May 2024, her internship period.
  Author archive: <https://10magazine.com/author/bethdarroch/>
- **Shift London** — 7 pieces, 18 May 2023 – 18 Jan 2024, the UAL/LCF
  student title, pre-internship.
  Author archive: <https://www.shiftlondon.org/author/beth-darroch/>

Both archives are unpaginated, so those two lists are complete as of
2026-09-08. If you add pieces, re-check the archives first — she may have
published since.

The one-line standfirsts under each headline were written here from the
article, not lifted. Headlines, dates, sections and URLs are verbatim.

An earlier build of this page carried six *invented* placeholder articles
and a `.draft-bar` warning banner. Both are gone now that the real bylines
landed. **If you ever put placeholder journalism back on this site, put the
banner back with it** — invented headlines under a working journalist's
name read as her actual bylines, and that is the one genuinely harmful
failure mode this site has.

### Article images

`assets/art-NN-<slug>.webp` — 19 images, one per piece, numbered to match
the order in `gen_beth.py`. Each was taken from its article's `og:image`,
centre-cropped to 3:2, resized to 900x600 and saved as WebP q78. Total
~915KB for all 19.

Sanity check worth knowing about: 10 Magazine's CMS filenames do **not**
match their articles (the Church's loafer piece serves `fila-feature.jpg`).
That was verified as a publisher-side naming quirk, not a scraping error —
`og:title` and `og:image` pair correctly on every page. Don't "fix" a
mapping by matching filenames to headlines; go by the page.

**These images are the publications' and photographers' copyright, not
Beth's.** Reproducing an article thumbnail alongside a link to the piece is
normal practice for a byline portfolio, but it is her call and a risk she
should know about. If anyone objects, the `.plate` markup degrades to the
`.wf` placeholder block cleanly.

### Still placeholder

- **No portrait.** `about/` carries a `.wf` block where it goes. It is the
  only image on the site that is not scraped.
- **No email address.** The contact page's Email button points at `#` and
  says so in a `.note`. Same for any social link.
- The `about/` bio was drafted from the published work and is marked with a
  `.note` asking Beth to rewrite it in her own voice.
- No Instagram, Substack, Muck Rack or portfolio account could be found for
  her anywhere, so there is nothing else to link.

## Copy slots

Editable text is marked `data-copy` / `data-copy-rich` for the admin Text
tab. `content.html` stays the default and the source of truth; `copy.json`
is an override layer. See [../CLAUDE.md](../CLAUDE.md).
