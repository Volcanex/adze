# Jack Dennison-Thompson (jackdt) — jackdt.com

Music & culture journalist. Portfolio site: home / about / writing /
photography / video / multimedia.

The last three were added 2026-08-05 (Jack asked for "one for videos, then
another called multimedia", plus photography). They are all `content_admin`
types with their own template, and they all reuse `/writing`'s tag-filter row —
see *The three media sections* below.

## Design language
This site has **its own** design language, published as the claude.ai/design
project **"JackDT — Design Language"** (tokens, component previews, guidelines).
It is deliberately *not* the Adze design language — Adze's React component
library serves the dashboard; Jack's site is bespoke static HTML and shares
none of it. Don't "harmonise" the two.

The design project ships its own copy of the four fonts, because jackdt.com
serves no `Access-Control-Allow-Origin` header and cross-origin webfont loads
therefore fail in the design pane. Images are fine cross-origin (only fonts need
CORS). If you re-sync it, keep the fonts local to that project.

### The pages pull their values from it
The three page `<style>` blocks (`home/content.html`, `about/content.html`,
`templates/writing.html`) carry a `:root` that names the design project as its
source and mirrors its tokens: `--blue: #2b3ecd` / `--blue-deep: #1a2792`
(colors.css), the `'Barlow Fallback'` metric-matched local face and the font
stacks (typography.css), `--blue-fill` for photographic blue ink clipped into
display glyphs (print.css), and `--t-hover` / `--t-marquee` (motion.css).
**Change a value in the design project first, then copy it into all three
files** — there is no build step that does this, and the three copies are
deliberately independent.

The old electric `#1a35ff` is gone. Nothing should hardcode `rgba(26,53,255,…)`
any more; the ink-fill gradient is `var(--blue-fill)`.

### `pages/home.html` in the design project is a MIRROR of the home page
Pushed 2026-07-30 so the home page can be designed in the Claude Design pane.
It is a copy — editing it there does **not** touch the site. To land a change:
copy it back into `home/content.html`, swapping the absolute
`https://jackdt.com/assets/…` URLs back to `../assets/…`, restoring the local
`@font-face` block (site fonts live in `assets/fonts/`, the card's in the
design project's `fonts/`), and re-wrapping the body in adze's bare `<html>`
tag. Then republish. Those four rewrites are the whole difference between the
two files — script them rather than hand-editing both copies.

### No backing photographs, no framed photographs (2026-07-30)
Two rules that came out of the same pass and are easy to undo by accident:

- **Nothing decorative sits behind the type.** The home page's `.stage-bg` /
  `.stage-paper` / `.stage-veil` trio is gone. `assets/images/jack-hero-src.jpg`
  was never a photograph — it is a white-to-black gradient, and the CSS showed
  its white top half under a screen-blended paper layer, so the hero was blank
  by construction. The footer's `IMG_3062.jpeg` multiply went with it. The hero
  is type on the ink ground now, and the parallax script (its only two targets
  removed) went too. `jack-hero-src.jpg` and `paper-texture.jpg` are still in
  `assets/` but nothing references them.
- **Photographs are unframed.** No `border` on `.portrait` (about) or
  `.entry .thumb` (writing). The 2px rules belong to the row and the marquee
  band, not to the image. The one exception is `.entry .thumb.empty`, which
  keeps a dashed 2px frame so a missing thumbnail still reads as a slot.

Both are written into the design project (`readme.md`, `components/article-card.html`).

### Square measures — `.columns` on home and about
Both pages set their body copy in `<section>`s inside a `.columns` grid, with
`text-align: justify` + `hyphens: auto`. The square edges are the point — don't
"fix" the justification back to ragged.

The two pages deliberately differ: **/about** runs 2-up side by side; **home**
stacks its six sections one per row inside a left-aligned `.col` (`margin: 0`,
max-width 1600px, sharing the hero's `clamp(24px, 8vw, 120px)` left edge)
because the sections are too uneven to sit side by side without a hole under
the shorter one. Each row is `1fr 1fr` with `align-items: center`, so the
section word is centred in its half against the block it belongs to. The
reading measure is held **separately** on `.columns .text` (max-width 600px) —
widening `.col` must not widen the lines. The paragraphs need that `.text`
wrapper: without it each `<p>` becomes its own grid item and the row collapses.
Under 640px the row stacks and the word goes back to the left.

**The word rail is on the LEFT above 640px (2026-08-18).** Every row is
`[word][copy]`, and the halves are unequal — `0.85fr 1.15fr`, so the copy gets
the wider one. `order` does the swap in a `@media (min-width: 641px)` block
rather than in the base rule, deliberately: the ≤640px phone layout keeps its
own stacking (copy, then its word underneath).

0.85 is about the limit on the word side. PHOTOGRAPHY is the longest of the six
and sets ~375px at its 81px cap; at the 641px floor the left column has to still
clear it. If a longer section name is ever added, check that column before
anything else.

Three arrangements have now been live, all on 2026-08-18, and the losers are
recorded in `home/content.html` so they don't get re-proposed: copy-left with one
straight rail of words down the right (the original — **the note above
`.columns` still argues for it, don't read that as live**), a zigzag alternating
the two, and this one.

**Body copy is 400 weight at `clamp(16px, 1.35vw, 20px)` across a 700px measure
(2026-08-18)**, from 200 at 16.5px/600px. Wider, smaller, heavier, in that order
of importance — it overshot first at 24px/300 and came back, because at a real
text weight that size was too loud beside the words. Two things go with it:
- **Barlow 300 had to be declared** in the same pass. `barlow-300.ttf` was
  already in `assets/fonts/` but had no `@font-face`, so `font-weight: 300`
  silently snapped to the 400 face. 200/300/400/700 normal (and 200 italic) are
  the declared faces now; anything else still needs adding first.
- **One size for all six, deliberately.** Sized to match its own word, each
  section would want a different value — PHOTOGRAPHY's short blurb more,
  MUSIC's long one less. The cap protects the measure: 20px across 700px is
  ~70 characters, which is longer than the ~55 this block was first tuned to
  and is the intended trade.

### Article plates — the one card, used twice
Square photo, publication line, title. **In colour, unframed, as shot** — the
writing index used to grey its thumbnails and sit them in full-width rows behind
a 2px rule; both are gone (2026-07-30). Four across on desktop, two under 640px.

- **/writing** renders every post as plates in a 4-column grid
  (`templates/writing.html`), tag-filtered and revealed a chunk at a time —
  see *One index, tagged*.
- **The home page** carries the same plates as a **carousel** under the hero:
  four in view, the rest drifting in. No buttons and no label above it — the row
  creeps sideways **on its own clock**, and it is still a real scroller so a
  swipe, drag or wheel takes over (the drift backs off while a pointer is down
  and resumes from wherever the hand left it). It runs **the opposite way to the
  hero marquee**: the marquee animates -50% → 0 so its letters drift right, and
  `scrollLeft` increasing carries the plates left. Keep those opposed.

  **The drift is not coupled to scroll.** It was, until 2026-07-30 — driven by
  progress down the page, which made it a second parallax layer and meant one
  flick of the wheel threw the plates across the block far too fast to read. Do
  not reattach it to scroll; the ground is the only thing scroll moves (see
  *Parallax — the ground only*).

  Speed is `SPEED` in the home page's carousel script, in **pixels per second**,
  currently **12** (about half a minute per plate). Same call as
  `--t-marquee: 150s`: slow enough to read as drifting, not as animation. The
  plates are appended **twice**, and the drift wraps by one set's width so the
  loop is seamless; the second set is `aria-hidden` and untabbable.

The home block is **not hand-written**: it starts `hidden` and a script fetches
`assets/data/posts.json`, builds a plate for the newest 12 items that have both
a `url` and an `image.src`, then unhides. So it tracks whatever Jack publishes through `/admin`
with no second copy to keep in sync.

That data file is published by `content_admin`'s `render()` **for every content
type**, not just `mode: none` — a shared change made for this (see
`_shared/features/CLAUDE.md`). Two consequences worth knowing:
- Every artist using `content_admin` now gets an `assets/data/<type>.json`. It
  is the same items their generated page already shows publicly.
- `/assets/data/posts.json` resolves through nginx in production but **404s in
  the dashboard's preview iframe** (the flat-asset-URL gotcha). That is why the
  block fails silently — in preview it simply isn't there. Don't "fix" that by
  making it render an empty state.

### Parallax — the ground only
The ink wash drifts at half the scroll rate; **nothing in the content moves.**
One line: the scroll handler sets `body.style.backgroundPosition`. Off under
`prefers-reduced-motion`.

An earlier pass drifted the hero, the latest block and each plate individually
(a `data-parallax` attribute per layer). It was rejected — the plates have to
hold their line. Don't reintroduce per-element transforms here; if more movement
is wanted, it belongs in the background.

### The ink ground must be able to show through
`body` carries the one ink wash (`ink-texture.jpg`, 4.5% baked in, tiled at
900px) on all three pages. On the home page that means `.stage` and `.sheet`
must stay **unfilled** — the moment either gets a `background`, the texture
disappears behind it and the page looks flat for no visible reason.

### Glyph texture — one plate, `cover`, everywhere (2026-08-15)
`--blue-fill` fills every display glyph on the site from
**`assets/images/ink-wash-plate.jpg`**: the middle 80% of a cyanotype wash
Gabriel supplied, cropped on all four sides to drop the deckle edge and the
dark frame (819×604 from a 1024×755 original; raw kept at
`intake/blue-wash-source.jpg`). Consumers are `.brand` on all seven pages, the
hero's `.nm`/`.unit`, `.col .lede em`, `.foot .big`, each generated page's `h1`,
and the `.cta` rail.

**Two things changed with it, and both matter more than the file swap:**

- **`--fill-tile: 720px` is now `--fill-size: cover`.** The token was renamed
  because it no longer names a tile — an 80% crop of a real sheet has no
  seamless edges, so it **cannot repeat**, and every consumer's
  `background-repeat` is `no-repeat, no-repeat`. `cover` is the only single
  value that fills the whole range of consumers (a 302×29 wordmark up to a
  1550×177 marquee unit) without per-element tuning.
- **The tint dropped from 0.65 to 0.30.** This plate is a duller, greener blue
  than `--blue`; at 0.65 the overlay flattened it straight back into a swatch.
  The display type therefore now reads slightly deeper and less indigo than
  `--blue` itself, which is intended — flat `--blue` is still what the nav,
  eyebrows and inline links use, so the two are meant to differ.

**Upscaling is fine here in a way it was not before, and that is the whole
reason `cover` works.** The previous plate (`ink-grain-tile.jpg`, still on disk,
now unreferenced) was a *grain* tile — generated by cropping the flattest 520px
window of `intake/91aafc78_5.jpeg`, partially high-passing out its tonal drift
and mirroring it 2×2 for seamlessness — and grain is exactly what dies when you
enlarge it past its source resolution. That is why it had to tile. This plate
carries broad tonal drift and nothing fine, and drift survives being enlarged,
so a 1.9× upscale on the marquee costs nothing visible. **If a future plate is
grainy rather than washy, this `cover` approach will go soft and you will need
the mirrored-tile recipe back** — it is recorded above for that reason.

The old "don't go back to fixed-pixel tiles" rule (2026-07-30) is now moot
either way: nothing tiles.

### Hero marquee speed
`--t-marquee: 150s` (was 75s, halved 2026-07-30 — at 75s it still read as an
animation rather than as drifting texture). It lives in the home page's `:root`
and in the design project's `tokens/motion.css`; keep them equal.

## Mobile smoothness — the three things that cost frames
This site is one long scroll over a tiled ground with a fixed bar on top, which
is exactly the shape that goes choppy on a phone. Three rules, all added
2026-07-31 after the home page was measurably janky on touch:

1. **No backdrop blur on touch.** `.masthead`'s `backdrop-filter` is recomputed
   every scroll frame and was the most expensive thing on the page. A
   `@media (hover: none)` block swaps it for a 0.97-opacity bar on all four
   pages. Keyed on `hover: none`, not a width — the cost is the GPU, not the
   viewport.
2. **No background parallax on touch.** Moving `body`'s `background-position`
   repaints the whole tiled ground per frame. The home page's parallax script
   returns early under `(hover: none)`.
3. **Thumbnails are capped at 720px on the long edge.** They are displayed in a
   ~340px square, and the home carousel holds **two** copies of every plate, so
   full-resolution art is paid for twice in decode and memory. A batch of
   `og:image` scrapes once shipped 2048px files and 3.0MB of thumbnails; the
   same set is 1.26MB at 720/q82 and looks identical. **Anything added to
   `assets/thumb-*.jpg` by hand must be resized first** — the admin's upload
   route does this for you, a scraper does not.

The carousel also stops writing `scrollLeft` when its block is off screen
(IntersectionObserver), so the per-frame layout isn't paid for while reading the
rest of the page.

Measured after: mobile home is ~1.1MB over 20 requests, no backdrop filter, no
parallax repaint; desktop keeps both and still drifts at 12.0 px/s.

## One index, tagged — /writing
Everything Jack has published lives in **one** `posts` list and one page. There
was briefly a separate `/news` section for the Maghrebi reporting (2026-07-30 →
31); it was folded back in on request. **`/news` is gone and now 404s** — don't
resurrect it, and if an inbound link ever matters, redirect it to
`/writing#politics` rather than rebuilding the page.

Each post carries `tags`, and the filter row across the top of `/writing` is
built from them:

| tag | what it is | n |
|----|----|----|
| *(none — "Latest")* | everything, newest first — the default view | 188 |
| `music` | Clash, The Cold Magazine, Substack | 23 |
| `culture` | the long-form subset — features, Next Wave, interviews, essays. **Also tagged `music`**, so a piece shows under both | 10 |
| `politics` | Maghrebi geopolitics, conflict, defence, world, Western Sahara | 133 |
| `economy` | Maghrebi economy, banking, industry, energy, tech | 46 |
| `society` | Maghrebi human rights, migration, crime, health, press freedom | 44 |

The labels are just an array at the top of `templates/writing.html` (`TAGS`)
plus the `tags` values in `content.json` — renaming or re-cutting them is a
data edit, not a code one. Counts render from the data, so they can't drift.
The Maghrebi tags were derived from that site's own WordPress categories at
scrape time; new items need tagging by hand in the admin.

The filter row is deliberately **Bebas (`--display`), not the body face** —
same pattern as `lydialott`'s works browser (plain text, no pills, active in
the accent), but in Jack's own type. It is the only nav on the page.

### /writing renders all 188 and reveals 24 at a time
Every plate is in the HTML server-side — the page works with JS off and is
fully crawlable. The script then hides all but the first chunk and hands back
more as a sentinel enters view (`rootMargin: 600px`). Images are
`loading="lazy"`, so a hidden plate costs **no request**. Chunk is 24, or
**12 under 640px** where the plates run two-across.

Consequences worth knowing:
- Filtering is show/hide over nodes already present — no refetch, no rebuild.
- The active tag is mirrored to the URL hash, and `#music` etc. deep-links.
- Without `IntersectionObserver` the chunking is switched off entirely rather
  than stranding the archive behind a sentinel that never fires.

### The home block — Jack picks it, and it is different on mobile
**Which articles: the `featured` checkbox on a post** ("Show on home page" in
the admin). The script takes the featured ones, newest first. If **nothing** is
flagged it falls back to the newest twelve rather than rendering an empty
block — so the page can never go blank, but a silent fallback also means "the
home page ignored my choice" usually means nothing is ticked.

It builds from `assets/data/posts.json`, which is the **whole** archive (188 and
growing), and it duplicates its set for the seamless loop — so this list must
never go unfiltered: that is ~380 plates on the home page.

- **Desktop** — up to 12 featured, drifting, set duplicated → 24 plates.
- **Under 640px** — exactly **4**, in a static 2×2 square. No duplicate set, no
  drift, no `requestAnimationFrame` at all. Four across at 390px gave ~85px
  plates nobody could read, and a row creeping sideways under a thumb trying to
  scroll down is a fight. `MOBILE` in the script and the `.latest .track` rule
  in the 640px media query are two halves of the same decision — change both.

## The three media sections (2026-08-05)

`photos` → `/photography/`, `videos` → `/video/`, `multimedia` →
`/multimedia/`. All three are `mode: single` content types rendered by their own
template in `templates/`, and all three build their **filter row from the data**
rather than from a hardcoded list like `/writing`'s `TAGS` — nobody has fixed
what Jack's photo or video subjects are, and a filter row that can only show
labels someone remembered to add to a template goes stale silently.

### /photography — one item is a SET, not a photograph
The unit Jack edits is a shoot ("Tangier, March") holding many images; the wall
is every image across every set, and **each tile inherits its set's tags**. This
is the whole reason the section is usable: he drags 30 frames in at once and
tags them once. One-item-per-photograph was considered and rejected — adding 40
photographs would have meant 40 forms.

- **Photographs are not cropped.** The writing plates are squares because a
  masthead crop is a thumbnail; a photograph is the work. Portrait and landscape
  keep their own shape and the column takes the height.
- **CSS columns, not a JS masonry** (`column-count: 3 / 2 / 2`). The layout then
  survives with JS off, and every tile gets `aspect-ratio` from the stored `ar`,
  so nothing reflows as images decode.
- **Deliberately NOT chunk-revealed** the way `/writing` is. Images are
  `loading="lazy"`, so a tile below the fold costs no request either way, and
  revealing a chunk into balanced columns makes every tile jump sideways. If the
  wall ever grows into the hundreds, revisit — but don't copy the writing
  chunker in reflexively.
- `srcset` offers the 480px card and the 2000px display tier, with
  `sizes="(max-width: 1000px) 50vw, 33vw"`. That `sizes` value is why the wall
  stays **two columns on a phone rather than one**: at 50vw a 390px phone picks
  the card tier, and going full-width would pull 2000px files onto mobile —
  exactly what the thumbnail rule below exists to prevent. Two candidates are
  only emitted when `card` and `src` are genuinely different files.
- Clicking a tile opens a lightbox that steps through the **currently visible**
  tiles, not all of them — arrowing into photographs you just filtered away
  reads as a bug. With JS off each tile is a plain link to the image.

### /video — a link or a file, and the frame is a facade
A video is **either** a `url` (YouTube/Vimeo) **or** an uploaded `video` file
(the `file` field type). The embed id is parsed in the template from whatever
Jack pastes — `watch?v=`, `youtu.be/`, `/shorts/` and Vimeo all work — rather
than stored in a second field he'd have to fill in correctly.

**The plates are facades: a poster image plus a play mark, with the real player
swapped in on click.** Sixteen live YouTube iframes on one page is several
megabytes of third-party script before anyone has asked to watch anything,
which is precisely what the mobile-smoothness rules below exist to stop. Don't
"simplify" this into plain iframes.

Poster resolution: the uploaded `poster` image, else `i.ytimg.com/vi/<id>/
hqdefault.jpg`. That ytimg URL is **the only third-party asset on the site** and
is only ever a fallback for a link Jack has just pasted — the backfilled videos
have local 720px thumbnails under `assets/videos/<id>/`.

**The 17 items were backfilled from his channel on 2026-08-05** (`Keskesay`,
`UC8wJrBxVPJrZTqmJ7fRLSlQ` — literature/philosophy essays, 2020–2025, plus one
Short). No API key was needed and none is configured. If you ever re-run this,
four things cost the first attempt real time:

- **It is 17, not 16.** The `/videos` tab's `ytInitialData` holds exactly 16
  (`richGridRenderer`, no continuation). The Short (`PlkuBXOn4YM`) lives only on
  the `/shorts` tab as a `shortsLockupViewModel` and never appears in the
  `/videos` payload. Count from both or you will silently lose it.
- **The Atom feed** (`youtube.com/feeds/videos.xml?channel_id=…`) is the best
  source for dates and descriptions but **caps at 15 entries**, so it had already
  aged out the two oldest videos.
- **`/watch` and the innertube `/youtubei/v1/player` endpoint hard-block this
  host** — "Sign in to confirm you're not a bot", because it is a datacenter IP.
  Header and client spoofing do not get round it. Don't burn an hour there.
- **The two oldest dates came from the Wayback Machine** (`web.archive.org/cdx`
  → an `id_` capture of the watch page), which is still plain `curl` and no API
  key. Independently re-verified 2026-08-05: `Ya8iWqOmbNE` → `uploadDate`
  2020-11-05 and `r9SCFlAateQ` → 2020-10-28, both also matching the page's own
  `dateText`. Note the `archive.org/wayback/available` helper API returns
  "no snapshot" for these even though captures exist — use the CDX endpoint.

Durations come only from `ytInitialData` (`lengthText`); the Short has none.
Posters were resized to 720px long edge (16 from `maxresdefault`, one that only
had `hqdefault`, so it is 480×360 and gets cropped into the 16:9 plate — replace
it by uploading a poster if it ever matters). Tag vocabulary is deliberately
four words: `books`, `philosophy`, `film`, `shorts`. **There is deliberately no
`music` tag here**, which looks like an oversight on a music journalist's site
and isn't: nothing on the channel is actually about music (the "27 club" video
is about mental health and creativity, not the music), so the tag would render
a filter with a count of zero. `philosophy` earns its place because 8 of the 17
titles literally begin "The philosophy of" — it is the channel's own format,
not an imposed category. The Short is double-tagged `books` as well as `shorts`
so filtering by `books` doesn't lose it. Item **ids encode the
original titles and the poster paths are keyed to them** — two titles had their
trailing YouTube hashtag runs stripped afterwards, so a few ids are longer than
their title now. That is harmless (no per-item pages exist) but don't "fix" an
id without moving its `assets/videos/<id>/` directory.

**Upload ceiling: 200MB, and it is set in two places that must agree.** The
field's `max_mb` in `config.json` refuses the file client-side; the real limit
is `client_max_body_size 220M` in `nginx/sites-available/jackdt.com` (raised
from 50M for this). Over the nginx limit the artist gets nginx's own 413 page,
which the admin can only report as a bare failure — after the whole upload has
transferred. Assets are stored twice (canonical + `output/` mirror), so a 200MB
video costs 400MB on a box that had 33G free.

### /multimedia — the catch-all, dispatching on `kind`
Mixed files (`image`/`video`/`audio`/`doc`) plus an optional `embed` URL
(YouTube, Vimeo, SoundCloud, Spotify). Unlike the other two it can't assume one
shape per item, so each piece is a block in one column and the media inside lays
itself out: several pictures share a row, one picture takes the width, audio and
video get real players, a PDF becomes a named card.

**The template switches on the stored `kind`, never on the file extension.** The
extension table lives once, in `_FILE_KINDS` in `_shared/features/content_admin.py`.

### /music — self-hosted, not a SoundCloud embed (2026-08-05)

**This overturns the "Music page — REMOVED, don't reinstate" rule below.** That
rule was written when the section was one SoundCloud embed for a journalist who
doesn't release records. What exists now is different: 20 of his own tracks,
downloaded and served from this box. Gabriel asked for it explicitly on
2026-08-05 — SoundCloud's embed player was the thing he wanted rid of.

- Fetched with `yt-dlp` (in a scratch venv, not installed system-wide).
  **Do not force an audio container**: SoundCloud serves AAC for some of these
  tracks and MP3 for others, and remuxing MP3 into `.m4a` fails outright with
  "Error opening output files: Invalid argument". Take `bestaudio` and keep
  whatever arrives — 5 are `.m4a` (160k AAC), 7 are `.mp3` (128k). Transcoding
  to a single format would be both larger and lossier; `<audio>` plays both.
  43.6MB total, and remember `output/` doubles it.
- **Two SoundCloud accounts, ONE artist.** The tracks were pulled from
  `soundcloud.com/bodaciousfm` (12) and `soundcloud.com/user-216694930` (8),
  but **Bodacious and Keskesay are the same person and the site must not split
  them** — he goes by **Keskesay** (2026-08-05, Gabriel, explicitly). They were
  briefly tagged by account and filtered into two projects; that was wrong and
  is gone. The tracks now carry **no tags**, the page names Keskesay once in
  the eyebrow, and the row meta is date · format only — repeating one artist
  name down 20 rows is noise, not information.
- **Tags were cleared rather than set to `keskesay` for all 20.** A tag every
  item carries groups nothing; leaving the field empty keeps it free for tags
  that would mean something later (genre, mood). The filter row is still in the
  template and renders **only when more than one tag exists**, so it lights up
  by itself the moment he tags anything, with no code change.
- **Grouped by year**, newest first, derived from the data — a year leaves the
  page when its last track does.
- **Layout is a catalogue row, not a card**: sleeve left, then title, length,
  project · date · format, and the waveform. It suits 20 unreleased experiments
  better than a grid of identical squares (which is what it was for an hour
  before it became this).
- **One `<audio>` for the whole page**, with a sticky player bar. Twenty
  separate players would let two ambient tracks run over each other, which is
  confusing rather than merely untidy. Each row is still a real link to its
  file, so the tracks play with JS off.

### The player bar — three things that look like mistakes and aren't

Restyled 2026-08-05 (Gabriel: "darker, sleeker, match the style of his site").
It was `--ink` with a blue border, a round cream button and a **raw
`input[type=range]`** — a white pill with a blue thumb, the one piece of
browser chrome on the site. The bar now runs **sleeve · transport · seek ·
elapsed · title**, all squared off, and the seek block is doing the same job
for the playing track that the waveforms do for the rows.

That order was arrived at, not designed: the title sat between the sleeve and
the transport for one pass, which pushed the buttons 300px in from the left
edge and was rejected on sight. **The controls own the left, the track's name
owns the right.** Anything put in front of `.pnav` moves the transport.

- **The seek is a solid two-tone blue block, and it is still the native
  range.** It sits inline, immediately right of the transport (Gabriel,
  explicitly — it was briefly the bar's top edge instead, and that was
  rejected). Every default part is replaced: the track is a block set to the
  height of the title beside it, the played portion is full-strength
  `--blue` and the rest `--pblue`, square ends, with a 3px cream tick for the
  playhead. Keeping the real `<input type=range>` is what buys dragging,
  tabbing and arrow-key seeking for free — **there is no custom pointer maths
  anywhere in this player**, and rebuilding the slider out of divs would mean
  writing all of it.
- **The fill is a gradient stop, not an element.** The script sets `--p` on
  the input; both `::-webkit-slider-runnable-track` and `::-moz-range-track`
  read it. Firefox's `::-moz-range-progress` would do the same job by itself,
  but one gradient covers both engines, so there is one thing to keep true
  rather than two. `setFill()` is called from `timeupdate` **and** from the
  range's own `input` handler, so the block follows a drag as well as
  playback — and `timeupdate` skips it while `seeking`, or the drag fights
  the playhead.
- **`--pblue: #7783d9` is not a stray colour.** `--blue` is 2.2:1 on the bar's
  ground — a hairline in it barely shows. This is the same hue lifted 62/38
  towards `--bg` for the dark surface only. The exception is the seek block,
  which uses full-strength `--blue` for the played portion **because there the
  contrast that matters is block against block**, not a line against
  near-black. The bar's four colours (`--pbg`, `--prule`, `--pdim`, `--pblue`)
  are declared **on `.player` itself, not in `:root`** — they are local to this
  one surface and are deliberately *not* claiming to be design tokens. If a
  second dark surface ever needs them, promote them to the design project
  first (per the token rule above), then hoist them.
- **The title is a fixed slot** (`flex: 0 0 clamp(160px, 21vw, 300px)`,
  right-aligned), not a flexible one. Sized to its text it would change width
  on every track change, and the seek — which absorbs all the slack — would
  jump with it. Long titles ellipsise instead. Under 640px it goes flexible
  and left-aligned again, because there the sleeve is hidden and the seek has
  wrapped to its own row.
- **Under 640px the bar is two rows** (`flex-wrap`): transport, title and time
  on the first, the seek full-width beneath. Four things on one line at 390px
  left the seek ~80px and the title ellipsised to nothing. `order` on
  `.ptitle`, `.ptime` and `.seek` is what does it — that and `row-gap` are the
  whole mechanism.

## Home page — the six CTAs are type, not buttons (2026-08-15)

**This replaces the old uniform blue slabs** (`210x64` desktop / `164x48`
mobile, one size for all six so the rail couldn't go ragged). Gabriel asked
for the section names to be set like the hero instead — Bebas, uppercase, the
same `--blue-fill` ink. The uniform-width rule went with the boxes: with no
box there is no edge to line up, so the six are simply centred on one axis in
the right-hand column (left-aligned under 640px, where they sit in the copy's
own margin). `.cta` exists only in `home/content.html` — no other page carries it.

Size is `clamp(54px, 6.3vw, 81px)`, 51px flat under 640px — sized up 50% from
the first pass on request. **The rail is now bigger than `.col .lede`**
(`clamp(30px, 5vw, 62px)`), so it, not the opening line, is the loudest thing
in the sheet. That is deliberate; it was the other way round for one pass.

The limit is PHOTOGRAPHY, the longest label: 370px inside a 577px column at
1440, and 233px against a 346px measure on a 390px phone. Both have room, but
there is not room for another 50% — check that word, not MULTIMEDIA, before
sizing up again. Both sizes are far over the ~28px floor below which the
photographic fill turns to mud.

### The rail takes six different cuts of the shared plate
The CTAs use `var(--blue-fill)` like everything else, but they are **the one
place that overrides `--fill-size`**, with a fixed `440px` instead of `cover`.

`cover` would fit the plate to each word individually, so six words of
different lengths would show the same patch at six different zooms — the
opposite of the effect. A fixed size pins all six to one sheet, and `--cut` on
`.columns section:nth-child(n) .cta a` then chooses **which patch** each takes.
The rail reads as six pieces torn from one sheet rather than six prints of one
patch.

Two things bound that number, both learned the hard way:

- **440px is a floor, and the failure is silent.** The plate must stay wider
  than the widest word (PHOTOGRAPHY, 370px). Under that, `no-repeat` leaves
  part of the glyph with no background at all, and because the fill is
  `-webkit-text-fill-color: transparent` those letters go *invisible* — they do
  not fall back to `color`.
- **There is a soft ceiling too.** At 760px each word sampled so small a patch
  of a very smooth wash that all six came out the same near-solid blue. Between
  the two, most usable variation is vertical (243px of slack against 70px
  horizontally), which is why the `--cut` values move more in Y than in X.

`--cut` values are **fixed, not generated.** This is a static page — a
per-load random offset would re-roll the wash on every refresh. They are also
hand-kept off the plate's two surviving blemishes (brown along the top, a dark
run bottom-right), so the vertical values sit in a 20–70% band. Re-pick them if
the plate is ever replaced.

### The raise is a `filter`, and it cannot be a `text-shadow`
Resting state is one **hard, unblurred** shadow at **`1.7px 1.7px`, alpha
0.21** — 45 degrees, down and right. On hover the word travels that same
diagonal onto the shadow while the ink darkens, so it presses into the paper
rather than lighting up. **The travel and the offset are the same number**;
that is what makes the word land exactly where its shadow was. Change one and
you must change the other or the press stops reading.

A 45° offset this low is the design language's own `--press`
(`2px 2px 0 rgba(11,13,26,.055)` in `components/buttons.html`) — "an impression
in the sheet, not a raised card". It was `0 4px` at 0.55 for one pass and
Gabriel rejected it on sight: directly underneath and that tall, the word reads
as hovering above the page rather than sitting on it. Keep any future
adjustment on the diagonal and keep it low. Note the shadow did **not** scale
with the 50% type increase — it was taken 15% closer and 25% lighter at the
same time, because a bigger word wants a *tighter* press, not a longer one.

- **`text-shadow` does not work here.** Under `background-clip: text` the
  background paints in the *background* layer, which is below the text-shadow
  layer — so the shadow lands on top of the ink grain and hides the texture
  that is the whole point. `filter: drop-shadow()` runs on the composited
  element and falls behind it correctly. Same trap applies anywhere else on
  this site that combines the ink fill with a shadow.
- **`brightness(1)` in the resting filter is not a no-op.** A filter list
  interpolates function-for-function; if the resting state doesn't name every
  function the hover state uses, the transition goes discrete and the darken
  snaps instead of easing. `brightness(0.66)` is `--blue` → roughly
  `--blue-deep`, applied to the grain as well as the colour.
- The travel is 4px, twice. It was 3px for one pass and the sink barely read
  at 54px.
- **`--pbg: #05060d` is below `--ink`**, which is the footer's black. When the
  bar sits over the footer the two tones differ slightly. That is the point —
  the player is a surface laid over the page, not part of it.

The glyphs are CSS borders (same construction as `.cplay` on the rows), not
`&#9654;`/`&#10074;` entities — the entities picked up whatever fallback face
had them and sat off their own centre. Play/pause is a `.playing` class on the
bar, not `innerHTML`.

**Next disables at the end of the visible list; previous never disables.**
`syncNav()` runs on load and after a filter change. Next deliberately does not
wrap, because the `ended` handler doesn't either — a wrapping button and
non-wrapping autoplay would disagree about where the list stops. Previous
restarts the current track past 3s or on the first track, which is what every
hardware transport does and means it has no dead state to show.

### The waveforms are precomputed — do not add a library for this
Each track carries a `peaks` string in `content.json`: **240 buckets, one
base36 char each** (`parseInt(c, 36) / 35`), computed at build time from
`ffmpeg -ac 1 -ar 8000 -f s16le` and RMS-averaged per bucket. The page decodes
a short string and fills a `<canvas>`; nothing is decoded, fetched or analysed
in the browser, and there is no dependency. Clicking a waveform on the playing
track seeks.

RMS, not absolute peak — peak-per-bucket saturates into a flat block on
anything compressed, which is most of these. All 20 came to ~6KB of peaks
(`content.json` 147KB → 160KB).

**Regenerate `peaks` whenever a track's audio file changes**, or the waveform
will describe the previous recording. `_clean_item` only overwrites *declared*
schema fields, so `peaks` survives ordinary admin edits — but nothing
recomputes it automatically, and there is no `peaks` field in the schema by
design (it is derived data, not something Jack should ever type).

**`gr-webspectrum` was considered and rejected** (suggested 2026-08-05): it is a
GNU Radio out-of-tree module for displaying live RF spectrum from an SDR
flowgraph, needs GNU Radio plus a persistent server process, and cannot render
an audio file's waveform at all. It shares only the word "spectrum". If a live
frequency display is ever wanted *while playing*, the tool is the Web Audio
API's `AnalyserNode` on the existing `<audio>` — still no dependency.
- Track titles had `.aif` stripped (leftovers of his own filenames). **Item ids
  are keyed to the asset directories** (`assets/music/<id>/track.{m4a,mp3}`), so
  renaming a title is safe but renaming an id means moving its directory.

## Selection is a highlighter — `::selection`, in all seven style blocks

`background: #ffef5a` with ink text, site-wide (2026-08-15, Gabriel: "yellow
like a highlighter pen"). It replaces Chrome's default blue, which is the wrong
register for a reading surface.

- **It carries `-webkit-text-fill-color: var(--ink)` and that is load-bearing.**
  The selection background paints below the text but *above* the element
  background, so on every display glyph on this site — hero, `.lede`, the CTA
  rail, the footer's `.big`, all painted through `background-clip: text` with a
  transparent fill — it covers the ink grain and leaves a yellow block with
  invisible letters. Repainting the fill in ink for the selected state is the
  whole fix. Verified against body copy, `.col .lede` and the footer over
  `--ink`.
- **The colour is declared inline in the rule, not as a `:root` token.** Same
  call as `.player`'s four locals: it is one effect's colour and is not
  claiming to be a design token. If something else ever needs it, it goes into
  the design project's `tokens/colors.css` first, then gets hoisted here.
- It is duplicated across **seven** files — `home/`, `about/` and the five
  templates — inserted after each block's `a { color: inherit; … }`. That is
  this site's existing pattern (every page carries its own full `<style>`), and
  it is the same seven-way edit the nav already needs. See the masthead section
  below: this is another vote for building an include mechanism in `compile.py`.

## Copy slots on the generated pages — mark the TEMPLATE

Every page's standing prose is editable from the admin's **Text** section,
including the four generated ones. The attribute goes in the **Jinja template**,
never in the generated `content.html` — see the corrected rule in
[../CLAUDE.md](../CLAUDE.md). Current slots: `home` and `about` (many),
`music` (`eyebrow`, `lede`), and `eyebrow` on photography/video/multimedia.

**If you add a section here, mark its prose in the same commit.** An admin that
covers every page except the newest one is worse than useless, because the new
page is the one the artist wants to change. Verified 2026-08-05 that an override
on `music/lede` reaches the live page and survives repeated publishes.

## The masthead: flat row on desktop, full-screen menu under 900px

Five sections don't fit beside the name. The control is a **`<label>` over a
hidden checkbox, not a button**, so the menu opens with no JavaScript at all — a
nav that needs a script to be reachable is a nav that can disappear. The script
on each page only adds Escape-to-close.

**The gotcha that cost a rebuild:** the overlay is `position: fixed; inset: 0`,
and `.masthead` carried `backdrop-filter`. **A backdrop-filter makes an element
the containing block for its fixed-position descendants**, so `inset: 0`
resolved to the masthead's own ~50px box — the menu rendered clipped and
see-through inside the header. The `@media (max-width: 900px)` block therefore
sets `backdrop-filter: none` on `.masthead` and gives it an opaque background.
That agrees with rule 1 of the mobile-smoothness notes below rather than
fighting it. **If you ever put the blur back at mobile widths, the menu breaks
again** — and it breaks visually, not in any DOM assertion, so it will pass a
scripted check.

The nav is duplicated across **six** files now (`home/content.html`,
`about/content.html` and the four templates). That is this site's existing pattern
— every page carries its own full `<style>` — but six copies is the point at
which adding a seventh section means six edits. There is no include mechanism in
`compile.py`; if this grows again, that's the thing to build.

## Generated pages — do not hand-edit
**Four** pages are now generated — `writing/`, `photography/`, `video/` and
`multimedia/content.html` — rebuilt from **`content.json`** (types `posts`,
`photos`, `videos`, `multimedia`, the source of truth) by the generic
`content_admin` feature via the matching template in `templates/` (all page mode
`single`). All four are listed in `.generated.json`, so `/edit-page` and
Auto-Code refuse direct edits and the next publish overwrites hand edits. To
change content, edit `content.json` or use the admin.

`home/` and `about/` are **not** generated and are safe to edit directly —
which is why the nav change had to be applied to them by hand.

(A `news/content.html` and `templates/news.html` are described in older notes;
that section was folded back into `/writing` on 2026-07-31 and the template is
gone. Ignore any remaining reference to it.)

**`compile.py` alone will not create these pages.** It compiles whatever
`content.html` already exists; the render step that writes them belongs to
`content_admin` and normally runs on Publish. To force it from the host after
editing `content.json` or a template by hand:

```
docker exec -u 1000 -w /app adze-flask python3 -c "
import sys, json
for p in ('/app','/app/_shared','/app/_shared/features'): sys.path.insert(0,p)
import content_admin as ca
print(ca.make_render('jackdt', json.load(open('/app/artists/jackdt/config.json')))())"
```
then `python3 compile.py --artist jackdt` and
`chown -R 1000:1000 output/artists/jackdt` (root compiles break Publish — see
the features doc). All three module paths are needed; `content_admin` imports
`artist_admin` and `asset_store` as top-level names.

⚠ **That snippet is a HALF publish, and the missing half bites quietly.**
`make_render(...)()` writes the pages and returns the generated slugs, but
**`.generated.json` is written by `ArtistAdmin.rebuild()`, not by `render()`**.
Run only the snippet and the manifest keeps whatever it said before — so a page
you just started generating is still considered hand-authored, `/edit-page` and
Auto-Code will happily let someone edit it, and the next real Publish silently
overwrites their work. It also leaves `schema.unpublished` stuck true, because
that compares `content.json`'s mtime against `.generated.json`'s. This was live
for the three new sections for about half an hour on 2026-08-05.

**Prefer the artist's own Publish path**, which does render → manifest →
compile in one transaction, as the button does:

```
curl -c jar -X POST https://jackdt.com/api/content-admin/jackdt/login \
     -H 'Content-Type: application/json' -d '{"token":"<admin_token>"}'
curl -b jar -X POST https://jackdt.com/api/content-admin/jackdt/compile
```

Use the raw `make_render` snippet only to *test* that a template renders at all;
finish with the publish route (or the button) so the manifest catches up.

Each post: `{id, title, meta, image, url}` — `meta` is the small-caps
"Publication · Section · Date" line; store real unicode (“ ” · —), the renderer
escapes.

**No excerpts.** Cards are thumbnail + publication + title only (dropped
2026-07-30 in favour of the thumbnails). There is no `excerpt` field in the
`content_types` schema any more — re-add it to `config.json` *and* the template
together if it ever comes back.

### Article thumbnails
`image` is a `content_admin` `image` field: `{src, full, ar}`, paths **relative
to `assets/`**. The admin's upload route owns it — `_clean_item` strips image
fields from the JSON body, so a hand-written `image` value survives an ordinary
admin text edit.

**Filenames must be flat: `assets/thumb-<post-id>.jpg`, never `assets/thumbs/…`.**
Flask registers `/assets/<page_slug>/<path>`, so any `assets/<subdir>/file` URL
is read as "page asset for page `<subdir>`" and 404s in the dashboard preview
iframe (nginx serves it fine in prod, so this breaks *only* in preview — easy to
miss). See the root `CLAUDE.md` "Asset URLs must be flat" gotcha.

The current thumbnails were scraped from each article's `og:image`.
**clashmusic.com is behind Cloudflare and 403s plain `curl`/WebFetch** — a real
browser (Playwright/Chrome) is needed to re-scrape. thecoldmagazine.co.uk and
Substack respond to ordinary `curl`.

The page *chrome* (fonts, masthead, footer) lives in `templates/writing.html`,
not in `content.html`. Design changes go there, then re-publish. `compile.py`
alone is **not** enough — it compiles the already-rendered `content.html`, so a
template edit is invisible until `render()` runs. Headless equivalent of the
admin's Publish (the sys.path prefixes are the fiddly part):

```
docker exec adze-flask python3 -c "
import sys; sys.path[:0]=['/app','/app/_shared','/app/_shared/features']
import content_admin as ca
ca.make_render('jackdt', ca._load_config('jackdt'))()"
docker exec adze-flask python3 compile.py --artist jackdt
```

## Custom admin at /admin
The shared `content_admin` feature (enabled via `features` + `content_types` in
`config.json`) gives a posts editor at **jackdt.com/admin**, auth = `admin_token`.
Add/edit/delete posts, then Publish runs the framework rebuild (`render()` →
`compile.py --artist jackdt`). See `_shared/features/CLAUDE.md`. The "Advanced
editing →" link hands off to the full Adze control panel.

home / about are ordinary hand-authored `content.html` (not generated).

## Music page — removed 2026-07-30, REINSTATED 2026-08-05

**Superseded — see "/music — self-hosted" above.** The history below is why it
was removed the first time; it no longer describes the site.

### Original note
There used to be a `music/` page embedding his SoundCloud. It's gone: he's a
journalist, not a release artist, and a whole page for one embed didn't earn its
place. Replaced by the footer social row (below). The stale `assets/test-track-*.mp3`
/ `frequency-sweep.mp3` / `volume-variation.mp3` fixtures went with it.
Don't reinstate a music page.

## Footer social row
Home, About and `templates/writing.html` each carry the same `.social` block —
SoundCloud (`soundcloud.com/user-216694930`, his handle is **Keskesay**),
Instagram (`jack.dennison.thompson`) and Substack (`@jackdennisonthompson`).

Icons are **inline SVG**, deliberately: artist sites are self-contained and must
not pull the Phosphor CDN (it's only used in `design-language/` guideline pages),
and Substack has no Phosphor glyph anyway.

Gotcha: this site paints blue text with `background-image` + `background-clip:
text`. That rule must **never** match a `.social a` — it paints a visible box
behind the SVG. The selector lists say `.foot .foot-mail`, not `.foot a`, for
exactly this reason. Keep it that way if you touch the footer CSS.

The block is duplicated across the three files rather than shared. That's the
existing pattern here (every page carries its own full `<style>`), and the copies
are independent — no drift risk worth coupling them for. Edit all three together.

## Gotcha: never run compile.py as root on the host for this artist
Host-root compiles leave root-owned files in `output/artists/jackdt/` the
container (uid 1000) can't overwrite on the next publish (PermissionError).
Publish via the admin, or compile in-container
(`sudo docker exec adze-flask python3 compile.py --artist jackdt`). If broken:
`sudo chown -R 1000:1000 output/artists/jackdt`.
