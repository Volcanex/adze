<style>
@font-face {
    font-family: 'Bebas Neue';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/bebas-neue-400.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/barlow-400.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/barlow-700.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: italic;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200-italic.ttf') format('truetype');
}

@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Bold.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: italic;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}

/* Metric-matched local fallback so the Barlow swap settles rather than jumps.
   Source: JackDT — Design Language, tokens/typography.css */
@font-face {
    font-family: 'Barlow Fallback';
    src: local('Helvetica Neue'), local('Helvetica'), local('Arial');
    size-adjust: 97%;
    ascent-override: 96%;
    descent-override: 24%;
}

:root {
    /* Values below are pulled from the claude.ai/design project
       "JackDT — Design Language" (tokens/colors.css, typography.css,
       motion.css, print.css). Change them there first, then here. */
    --blue: #2b3ecd;
    --blue-deep: #1a2792;
    --ink: #0b0d1a;
    --bg: #f4f3ee;
    --paper: #fbfaf6;
    --muted: #4a4d5c;
    --display: 'Bebas Neue', 'Barlow', 'Barlow Fallback', sans-serif;
    --body: 'Barlow', 'Barlow Fallback', sans-serif;
    --serif: 'Cardo', Georgia, 'Times New Roman', serif;
    /* photographic blue ink, clipped into display glyphs — never a flat swatch.
       The plate is the middle 80% of a cyanotype wash; raw at
       assets/intake/blue-wash-source.jpg. The 0.30 tint is low because this
       plate is a duller, greener blue than --blue and the old 0.65 flattened
       it back into a swatch. */
    --blue-fill:
        linear-gradient(rgba(43, 62, 205, 0.30), rgba(43, 62, 205, 0.30)),
        url('../assets/images/ink-wash-plate.jpg');
    /* cover, not a tile size. An 80% crop of a real sheet has no seamless
       edges, so it cannot repeat; cover is the only value that fills every
       consumer from a 302x29 wordmark to a 1550x177 marquee unit without
       per-element tuning. .cta overrides it with an explicit size. */
    --fill-size: cover;
    /* motion is either a 0.2s hover acknowledgement or very slow ambient drift */
    --t-hover: 0.2s ease;
    --t-marquee: 150s;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: var(--body);
    color: var(--ink);
    background: var(--bg);
    /* the one ink wash, 4.5% baked into the JPEG and tiled at 900px — same
       ground as /about and /writing (design language, guidelines/texture) */
    background-image: url('../assets/ink-texture.jpg');
    background-size: 900px auto;
    background-repeat: repeat;
    line-height: 1.5;
    font-weight: 400;
    overflow-x: hidden;
    opacity: 0;
    animation: pageIn 0.6s ease-out forwards;
}
@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

a { color: inherit; text-decoration: none; }

/* ── Selection is a highlighter, not the browser's blue ──
   The site is a reading surface; a marker line belongs on it and Chrome's
   default blue does not. Declared inline rather than as a :root token — it is
   one surface's colour, the same call as .player's four locals on /music. If
   anything else ever needs it, promote it to the design project's
   tokens/colors.css first, then hoist it here.

   `-webkit-text-fill-color` is the part that matters. The selection background
   paints immediately BELOW the text but ABOVE the element background, so on
   the display glyphs — which are painted through background-clip: text with a
   transparent fill — it covers the ink grain and leaves a yellow block with
   invisible letters. Repainting the fill in ink for the selected state is what
   keeps a selected headline readable. */
::selection {
    background: #ffef5a;
    color: var(--ink);
    -webkit-text-fill-color: var(--ink);
}

/* ── Slim masthead (top-left name + right-side vertical nav) ── */
.masthead {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 32px;
    /* was mix-blend-mode:difference over the hero photo; with the photo gone it
       bleached the wordmark out. Same paper bar as /about and /writing now. */
    background: rgba(244, 243, 238, 0.82);
    backdrop-filter: saturate(140%) blur(8px);
    -webkit-backdrop-filter: saturate(140%) blur(8px);
    border-bottom: 1px solid rgba(11, 13, 26, 0.08);
}

.brand {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(20px, 2.4vw, 32px);
    letter-spacing: 0.06em;
    line-height: 0.9;
    color: var(--blue);
    text-transform: uppercase;
    white-space: nowrap;
    background-image: var(--blue-fill);
    /* cover: the plate is scaled to fill the box, so which patch lands in the
       glyphs follows the element's aspect ratio. Upscaling on the big elements
       is fine here in a way it never was for the old grain tile — this plate
       carries broad tonal drift, not fine grain, and drift survives being
       enlarged. */
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.top-nav {
    display: flex;
    flex-direction: row;
    gap: 26px;
    align-items: center;
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink);
}
.top-nav a { position: relative; }
.top-nav a::after {
    content: '';
    position: absolute;
    right: 0; bottom: -4px;
    width: 0; height: 2px;
    background: var(--blue);
    transition: width 0.25s ease;
}
.top-nav a:hover::after { width: 100%; }

/* ── Menu, under 900px ──
   Five sections do not fit beside the name on a phone. The control is a
   LABEL over a hidden checkbox rather than a button, so the menu opens with
   no JavaScript at all — a nav that needs a script to be reachable is a nav
   that can disappear. The script at the foot only adds Escape-to-close. */
.nav-check { position: absolute; opacity: 0; pointer-events: none; }
.nav-toggle {
    display: none;
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink);
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
}
.nav-toggle:hover { color: var(--blue); }
.nav-check:focus-visible ~ .nav-toggle { outline: 2px solid var(--blue); outline-offset: 4px; }

@media (max-width: 900px) {
    /* The overlay is position:fixed, but a backdrop-filter on an ancestor makes
       that ancestor the containing block for its fixed descendants — so
       `inset: 0` resolved to the masthead's own 50px-tall box and the menu
       rendered clipped and see-through inside the header. Dropping the filter
       at this width hands the viewport back. It is also what the touch rule
       further down wants anyway (rule 1 of the mobile-smoothness notes: no
       backdrop blur on touch), so the two agree rather than fight. */
    .masthead {
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        background: rgba(244, 243, 238, 0.97);
    }

    .nav-toggle { display: block; position: relative; z-index: 101; }
    .top-nav {
        position: fixed;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        gap: clamp(10px, 3vh, 26px);
        padding: 0 clamp(24px, 8vw, 120px);
        background: var(--bg);
        background-image: url('../assets/ink-texture.jpg');
        background-size: 900px auto;
        font-family: var(--display);
        font-weight: 400;
        font-size: clamp(38px, 11vw, 74px);
        line-height: 0.9;
        letter-spacing: 0.02em;
        /* visibility, not display:none — the links keep their place in the
           accessibility tree and the fade has something to animate */
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s;
    }
    .nav-check:checked ~ .top-nav { opacity: 1; visibility: visible; }
    .top-nav a::after { display: none; }
    .top-nav a:hover, .top-nav a.active { color: var(--blue); }
    .nav-check:checked ~ .nav-toggle::after { content: ' \00d7'; }
}


/* ── Hero stage ──
   No backing photograph. The three layers that used to live here (.stage-bg,
   .stage-paper, .stage-veil) existed to hold a hero image that was only ever a
   white-to-black gradient JPEG, and the paper layer screen-blended over it —
   which the design language forbids. Removed 2026-07-30: the hero now sits
   straight on the ink ground, like every other page. */
.stage {
    position: relative;
    height: 70vh;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding-bottom: 9vh;   /* sits the name above dead centre */
}

/* big blue magazine headline — left aligned */
.hero {
    position: relative;
    z-index: 2;
    text-align: left;
    width: 100%;
    will-change: transform;
    padding: 0 clamp(24px, 8vw, 120px);
}
.hero .kicker {
    font-family: var(--body);
    font-weight: 700;
    font-size: clamp(11px, 1.1vw, 14px);
    letter-spacing: 0.42em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 18px;
}
.hero h1 {
    font-family: var(--display);
    font-weight: 400;
    color: var(--blue);                 /* fallback for no background-clip support */
    line-height: 0.82;
    letter-spacing: 0.005em;
    text-transform: uppercase;
    font-size: clamp(64px, 15vw, 240px);
}
.hero h1 .nm { display: block; margin-bottom: 0.12em; }

/* textured blue glyphs — shared by the static "Jack" and the marquee name */
.hero h1 .nm,
.hero h1 .unit {
    color: var(--blue);
    background-image: var(--blue-fill);
    /* cover: the plate is scaled to fill the box, so which patch lands in the
       glyphs follows the element's aspect ratio. Upscaling on the big elements
       is fine here in a way it never was for the old grain tile — this plate
       carries broad tonal drift, not fine grain, and drift survives being
       enlarged. */
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* marquee: DENNISON THOMPSON runs off the right and re-enters from the left.
   Breaks out of the hero's padding to span the full page width. */
.hero h1 .marquee {
    display: flex;
    align-items: center;
    height: 0.88em;            /* the cap height of the display face, nothing more */
    width: 100vw;
    margin-left: calc(-1 * clamp(24px, 8vw, 120px));
    overflow: hidden;
}
.hero h1 .marquee__track {
    flex: none;                /* don't let flex shrink the overflowing track */
    display: inline-flex;
    align-items: center;
    width: max-content;
    white-space: nowrap;
    will-change: transform;
    animation: nameMarquee var(--t-marquee) linear infinite;
}
.hero h1 .unit { padding-right: 0.62em; }   /* the only gap between repeats now */
/* -50% == one identical half of the track → seamless loop.
   from -50% to 0 moves content rightward (out right, in from left). */
@keyframes nameMarquee {
    from { transform: translateX(-50%); }
    to   { transform: translateX(0); }
}
/* Touch devices: the masthead's backdrop blur is recomputed on every scroll
   frame and it is the single most expensive thing on the page on a phone.
   Trade it for an almost-opaque bar — visually near-identical, no per-frame
   filter. Keyed on (hover: none) rather than a width so a large tablet gets it
   too; the cost is the GPU, not the viewport. */
@media (hover: none) {
    .masthead {
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        background: rgba(244, 243, 238, 0.97);
    }
}

@media (prefers-reduced-motion: reduce) {
    .hero h1 .marquee__track { animation: none; }
}
.hero .tagline {
    margin-top: 26px;
    font-family: var(--body);
    font-weight: 200;
    font-style: italic;
    font-weight: 400;
    font-size: clamp(17px, 1.9vw, 23px);
    color: var(--ink);
    letter-spacing: 0;
    line-height: 1.4;
    max-width: 30ch;
}

.scroll-cue {
    position: absolute;
    bottom: 28px; left: 50%;
    transform: translateX(-50%);
    z-index: 3;
    font-family: var(--body);
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    animation: bob 2s ease-in-out infinite;
}
@keyframes bob { 0%,100%{ transform: translate(-50%,0);} 50%{ transform: translate(-50%,8px);} }

/* ── Latest four, in colour ──
   A square block of four square plates under the hero. These run in FULL COLOUR
   — the writing index deliberately greys its thumbnails so a dozen competing
   magazine covers don't fight; four of them, at size, are the point here.
   Items come from assets/data/posts.json (published by content_admin on every
   rebuild) so this never needs hand-editing when Jack publishes. */
.latest {
    position: relative;
    z-index: 3;
    padding: 0 clamp(24px, 8vw, 120px);   /* the sheet below supplies the gap */
}
.latest[hidden] { display: none; }
/* carousel: four plates in view, the rest drifting in from the right on their
   own clock. No buttons — the track is a real scroller (arrow keys, trackpad
   swipe all work) and a hand on it takes over from the drift. */
.latest .frame { display: block; }
.latest .track {
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: calc((100% - 3 * var(--plate-gap)) / 4);
    gap: var(--plate-gap);
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.latest .track::-webkit-scrollbar { display: none; }
.latest {
    --plate-gap: clamp(14px, 1.6vw, 26px);
}
.latest a {
    display: block;
}
.latest .shot {
    aspect-ratio: 1;
    overflow: hidden;
    background: var(--paper);
}
.latest .shot img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform var(--t-image, 0.4s ease);
}
.latest a:hover .shot img { transform: scale(1.04); }
.latest .meta {
    margin-top: 10px;
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.latest .title {
    margin-top: 4px;
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(17px, 1.35vw, 24px);
    line-height: 0.98;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.latest a:hover .title { color: var(--blue); }

/* ── Editorial content ── */
.sheet {
    position: relative;
    z-index: 4;
    /* no fill — the body's ink ground runs through the editorial section too */
    padding: clamp(70px, 12vh, 160px) clamp(24px, 8vw, 120px);
}
/* left-aligned block, sharing the hero's left edge — not centred. It holds the
   2x3 section grid; each cell's column comes out ~450px, which is the reading
   measure the copy was tuned for. */
.col {
    /* Fills the sheet rather than stopping short of it: at 980px this block
       used about two thirds of a 1440 screen and left a band of dead space
       down the right. The cap is only there so the row doesn't become absurd
       on a very wide monitor. The reading measure is held separately, on
       .columns .text — widening this must not widen the lines. */
    max-width: 1600px;
    margin: 0;
}
.col .label {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 28px;
}
.col .lede {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(30px, 5vw, 62px);
    line-height: 0.96;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    color: var(--ink);
    margin-bottom: 36px;
}
.col .lede em { color: var(--blue); font-style: normal; }
.col .lede { max-width: 620px; }
.col p {
    font-family: var(--body);
    font-weight: 200;
    /* Newspaper measure: ~55 characters a line. This was 18px/1.7 across a
       620px column, which is ~80 characters — past the point where the eye
       reliably finds the next line, and it read as a slab. Tightening the
       leading with it keeps the column dense rather than airy. */
    font-size: clamp(15px, 1.2vw, 16.5px);
    line-height: 1.55;
    color: #24272f;
    margin-bottom: 20px;
    /* set square: justified with hyphenation so both edges are flush and the
       two columns read as newspaper measures rather than ragged blocks */
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
}
.col p strong { color: var(--ink); font-weight: 700; }

/* ── The six sections ──
   Prose on the left, its button on the right, 50/50. The button is centred
   both ways inside its half — vertically against the block it belongs to, and
   horizontally in the column, so the whole right-hand side reads as one rail
   of identical buttons rather than a ragged edge.

   Tried and rejected on 2026-08-05, in order: a zigzag (buttons alternating
   sides), and a 2x3 grid of titled cells with feed-driven pictures. The grid
   read as a set of cards rather than as a bio with places to go next, which is
   what this page is. Don't re-add section titles or images here. */
.columns {
    display: grid;
    grid-template-columns: 1fr;
    gap: 44px;
}
.columns section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: clamp(28px, 4vw, 56px);
}
.columns .text > :last-child { margin-bottom: 0; }
/* The measure is capped independently of the column. The grid stays a true
   50/50, but past ~1200px the copy stops stretching with it and the extra
   width becomes margin instead of longer lines. */
.columns .text { max-width: 600px; }

/* The six are set in the hero's face and the same photographic blue ink, not
   in blue slabs (2026-08-15). They run LARGER than .col .lede — the rail is
   the loudest thing in the sheet on purpose, sized up 50% on request once the
   type was in.

   Raised, then sunk: one hard unblurred shadow at 45 degrees stands each word
   just off the paper, and on hover it travels down that diagonal onto the
   shadow while the ink darkens — the word presses in rather than lighting up.
   2px, matching the design language's own `--press` offset: an impression in
   the sheet, not a card floating over it. The shadow is a `filter`, NOT a
   `text-shadow`: under `background-clip: text` the background paints in the
   background layer, *below* the text-shadow, so a text-shadow would cover the
   ink grain instead of falling behind the glyph. A filter runs on the
   composited element and keeps the texture. */
.cta { display: flex; justify-content: center; align-items: center; }
.cta a {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(54px, 6.3vw, 81px);
    line-height: 0.9;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    text-align: center;
    color: var(--blue);                 /* fallback for no background-clip support */
    background-image: var(--blue-fill);
    /* The one place that overrides --fill-size. `cover` would fit the plate to
       each word individually, and six words of different lengths would then
       show the same patch at six different zooms — the opposite of the effect.
       A fixed 440px pins all six to one sheet, so --cut below chooses WHICH
       patch of it each one takes.

       440px is a floor, not a preference. Under it the plate (440x324 at this
       size) stops covering PHOTOGRAPHY at 370px, and the uncovered glyphs go
       transparent — invisible letters, not a fallback colour. Over it the wash
       flattens: at 760px each word sampled so small a patch that all six came
       out the same near-solid blue, which defeats the point of cutting them
       differently. Most of the visible variation is therefore vertical, where
       there are 243px of slack against 70px horizontally. */
    background-size: cover, 440px;
    background-position: center, var(--cut, 50% 50%);
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    /* brightness(1) is not a no-op: a filter list only interpolates
       function-for-function, so the resting state has to name every function
       the hover state uses or the whole transition goes discrete and snaps. */
    filter: brightness(1) drop-shadow(1.7px 1.7px 0 rgba(26, 39, 146, 0.21));
    transition: transform var(--t-hover), filter var(--t-hover);
}
.cta a:hover {
    transform: translate(1.7px, 1.7px);
    filter: brightness(0.66) drop-shadow(0 0 0 rgba(26, 39, 146, 0.21));
}
.cta a:focus-visible { outline: 2px solid var(--ink); outline-offset: 6px; }

/* Six different cuts of the one plate, so the rail reads as six pieces torn
   from the same sheet rather than six prints of one patch. Fixed values, not
   generated: this is a static page and a per-load random offset would flicker
   the wash on every refresh for no gain. They are hand-spread across the plate
   and kept off its two remaining blemishes — the brown along the top edge and
   the dark run bottom-right — which is why the vertical values sit in the
   20-70% band rather than the full range. Re-pick them if the plate changes. */
.columns section:nth-child(1) .cta a { --cut:  8% 40%; }   /* Writing */
.columns section:nth-child(2) .cta a { --cut: 62% 28%; }   /* About */
.columns section:nth-child(3) .cta a { --cut: 26% 62%; }   /* Photography */
.columns section:nth-child(4) .cta a { --cut: 90% 48%; }   /* Music */
.columns section:nth-child(5) .cta a { --cut: 40% 20%; }   /* Video */
.columns section:nth-child(6) .cta a { --cut: 70% 66%; }   /* Multimedia */

.foot {
    text-align: center;
    padding: 60px 32px;
    background: var(--ink);
    color: rgba(255,255,255,0.6);
    font-family: var(--body);
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.foot .big {
    font-family: var(--display);
    font-size: clamp(40px, 8vw, 110px);
    color: var(--blue);
    line-height: 0.85;
    letter-spacing: 0.02em;
    margin-bottom: 28px;
    background-image: var(--blue-fill);
    /* cover: the plate is scaled to fill the box, so which patch lands in the
       glyphs follows the element's aspect ratio. Upscaling on the big elements
       is fine here in a way it never was for the old grain tile — this plate
       carries broad tonal drift, not fine grain, and drift survives being
       enlarged. */
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Social marks (inline SVG — no CDN, no icon font) ── */
.social {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 34px;
}
.social a {
    display: inline-flex;
    width: 34px;
    height: 34px;
    color: rgba(255, 255, 255, 0.55);
    transition: color 0.2s ease, transform 0.2s ease;
}
.social a:hover { color: var(--blue); transform: translateY(-2px); }
.social svg { width: 100%; height: 100%; display: block; }

/* Photographic fill is display sizes only — below ~28px it turns to mud, so the
   buttons stay flat --blue. .social links are excluded too: background-clip
   would paint a visible box behind the SVGs. */
.col .lede em {
    background-image: var(--blue-fill);
    /* cover: the plate is scaled to fill the box, so which patch lands in the
       glyphs follows the element's aspect ratio. Upscaling on the big elements
       is fine here in a way it never was for the old grain tile — this plate
       carries broad tonal drift, not fine grain, and drift survives being
       enlarged. */
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .backdrop span { font-size: 90vw; }
    .sheet { padding: 70px 22px; }
    .latest { padding: 0 22px; }
    /* On a phone the carousel becomes a static 2x2 square. A four-across
       scroller at 390px gives ~85px plates that can't be read, and a row that
       creeps sideways under a thumb that is trying to scroll down is a fight.
       The script matches this: on mobile it renders four plates, doesn't
       duplicate the set, and never starts the drift. */
    .latest .track {
        grid-auto-flow: row;
        grid-template-columns: 1fr 1fr;
        grid-auto-columns: auto;
        overflow-x: visible;
    }
    .columns section { grid-template-columns: 1fr; gap: 20px; }
    /* Left edge, not centred: on a phone the word sits under its own paragraph
       and the six read down the same margin as the copy. One step smaller so
       PHOTOGRAPHY still clears a 390px screen with the sheet's 22px padding. */
    .cta { justify-content: flex-start; }
    .cta a { font-size: 51px; }
}

@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .scroll-cue { animation: none; }
}
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <input type="checkbox" id="nav-open" class="nav-check" hidden>
    <label for="nav-open" class="nav-toggle" aria-label="Menu">Menu</label>
    <nav class="top-nav">
        <a href="../about/">About</a>
        <a href="../writing/">Writing</a>
        <a href="../photography/">Photography</a>
        <a href="../music/">Music</a>
        <a href="../video/">Video</a>
        <a href="../multimedia/">Multimedia</a>
    </nav>
</header>

<section class="stage">
    <div class="hero">
        <h1>
        <span class="nm">Jack</span>
        <span class="marquee" aria-label="Dennison Thompson">
            <span class="marquee__track" aria-hidden="true">
                <span class="unit">Dennison&nbsp;Thompson</span>
                <span class="unit">Dennison&nbsp;Thompson</span>
                <span class="unit">Dennison&nbsp;Thompson</span>
                <span class="unit">Dennison&nbsp;Thompson</span>
                <span class="unit">Dennison&nbsp;Thompson</span>
                <span class="unit">Dennison&nbsp;Thompson</span>
            </span>
        </span>
    </h1>
    </div>
</section>

<section class="latest" id="latest" hidden>
    <div class="frame">
        <div class="track"></div>
    </div>
</section>

<div class="sheet">
    <div class="col">
        <div class="lede" data-copy-rich="tagline"><em>Music</em> &amp; <em>culture</em> journalist, Clapton, London</div>

        <div class="columns" id="contact">
            <section>
                <div class="text">
                    <p data-copy-rich="intro"><strong>Jack Dennison Thompson</strong> writes features, reviews and interviews across music, culture and current affairs. Originally from Newcastle, he is studying for an MA in Magazine Journalism at City, University of London.</p>
                </div>
                <div class="cta"><a href="../writing/">Writing</a></div>
            </section>
            <section>
                <div class="text">
                    <p data-copy-rich="bio-bylines">He is a contributing writer at <strong>Clash Music Group</strong> and deputy multimedia editor at <strong>GTFO Magazine</strong>, and has written for Maghrebi, Folk &amp; Honey, The Indiependent and Campaign UK.</p>
                    <p data-copy="bio-beyond-writing">Beyond writing he produces his own YouTube channel and radio show, and works in Adobe Creative Suite, Ableton and WordPress.</p>
                </div>
                <div class="cta"><a href="../about/">About</a></div>
            </section>
            <section>
                <div class="text">
                    <p data-copy-rich="blurb-photography">Photographs made alongside the reporting, on assignment and off it.</p>
                </div>
                <div class="cta"><a href="../photography/">Photography</a></div>
            </section>
            <section>
                <div class="text">
                    <p data-copy-rich="blurb-music">Jack has been making music since 2020, for personal satisfaction rather than release. Syncopated rhythms sit atop lucid ambient chords and fall-to-the-floor kick drums. Influenced by <strong>Vegyn</strong>, <strong>Aphex Twin</strong> and <strong>Mall Grab</strong> &mdash; though it sits between those influences rather than mirroring them.</p>
                </div>
                <div class="cta"><a href="../music/">Music</a></div>
            </section>
            <section>
                <div class="text">
                    <p data-copy-rich="blurb-video">Video essays on literature and philosophy, published as <strong>Keskesay</strong> &mdash; Murakami, Kafka, Hemingway, Hunter S. Thompson and the writers he keeps coming back to.</p>
                </div>
                <div class="cta"><a href="../video/">Video</a></div>
            </section>
            <section>
                <div class="text">
                    <p data-copy-rich="blurb-multimedia">Work that refuses to sit in one format &mdash; picture, sound, video and document held together in a single piece.</p>
                </div>
                <div class="cta"><a href="../multimedia/">Multimedia</a></div>
            </section>
        </div>
    </div>
</div>

<footer class="foot">
    <div class="big" data-copy="contact-heading">Get in touch</div>
    <div class="social">
        <a href="mailto:jackdt26@outlook.com" aria-label="Email Jack">
            <svg viewBox="0 0 256 256" fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="32" y="48" width="192" height="160" rx="10"/>
                <path d="M224 56 128 144 32 56"/>
            </svg>
        </a>
        <a href="https://soundcloud.com/user-216694930" target="_blank" rel="noopener" aria-label="SoundCloud">
            <svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                <rect x="16" y="140" width="15" height="62" rx="7.5"/>
                <rect x="50" y="118" width="15" height="84" rx="7.5"/>
                <rect x="84" y="100" width="15" height="102" rx="7.5"/>
                <path d="M126 202a8 8 0 0 1 -8 -8V86a8 8 0 0 1 5.6 -7.6 62 62 0 0 1 79.4 52.2 44 44 0 0 1 -8 71.4Z"/>
            </svg>
        </a>
        <a href="https://www.instagram.com/jack.dennison.thompson/" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 256 256" fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="36" y="36" width="184" height="184" rx="48"/>
                <circle cx="128" cy="128" r="40"/>
                <circle cx="180" cy="76" r="10" fill="currentColor" stroke="none"/>
            </svg>
        </a>
        <a href="https://substack.com/@jackdennisonthompson" target="_blank" rel="noopener" aria-label="Substack">
            <svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                <path d="M56 40h144v26H56z"/>
                <path d="M56 90h144v26H56z"/>
                <path d="M56 140v76l72-40 72 40v-76z"/>
            </svg>
        </a>
        <a href="https://www.linkedin.com/in/jack-dennison-thompson-a4668126a" target="_blank" rel="noopener" aria-label="LinkedIn">
            <svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                <path d="M212 28H44a16 16 0 0 0 -16 16v168a16 16 0 0 0 16 16h168a16 16 0 0 0 16 -16V44a16 16 0 0 0 -16 -16ZM96 184a8 8 0 0 1 -16 0v-72a8 8 0 0 1 16 0Zm-8-88a12 12 0 1 1 12-12 12 12 0 0 1 -12 12Zm96 88a8 8 0 0 1 -16 0v-40a20 20 0 0 0 -40 0v40a8 8 0 0 1 -16 0v-72a8 8 0 0 1 15.8 -1.8A36 36 0 0 1 184 144Z"/>
            </svg>
        </a>
    </div>
</footer>

<script>

/* Menu: the checkbox does the opening, so this only adds Escape. */
(function () {
    var check = document.getElementById('nav-open');
    if (!check) return;
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && check.checked) check.checked = false;
    });
})();

/* Latest articles, fetched from the same data the writing index is generated
   from, as a carousel: four in view, the buttons page the rest in. Fails
   silently — the block starts [hidden] and only reveals once it has something
   to show, so a 404 leaves no hole in the page. */
(function () {
    var wrap = document.getElementById('latest');
    if (!wrap) return;
    var track = wrap.querySelector('.track');
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    /* Matches the 640px breakpoint in the stylesheet, where .track becomes a
       2x2 grid. Read once at build time — a phone does not change width. */
    var MOBILE = window.matchMedia && window.matchMedia('(max-width: 640px)').matches;

    /* No buttons: the row drifts on its own clock, not off the scrollbar. It
       used to be driven by page-scroll progress, which made it a second
       parallax layer — a flick of the wheel threw the plates across the block,
       far too fast to read and fighting the ground behind them. It is its own
       thing now: a slow constant creep, like the hero marquee. It runs the
       OPPOSITE WAY to that marquee — the marquee's track animates from -50% to
       0, so its letters drift rightward; scrollLeft increasing here carries the
       plates leftward. Keep those two opposed. The track is still a real
       scroller, so a swipe, drag or wheel takes over and the drift picks up
       from wherever the hand left it. */

    /* The only knob: pixels per second. 12px/s walks one plate past in about
       half a minute — slow enough to read as drifting rather than animating,
       which is the same call as --t-marquee: 150s. */
    var SPEED = 12;

    var dragging = false;
    var pos = 0;      /* our own float position; scrollLeft rounds when read back */
    var period = 0;   /* width of one full set of plates, incl. its trailing gap */

    track.addEventListener('pointerdown', function () { dragging = true; });
    window.addEventListener('pointerup', function () { dragging = false; sync(); });
    track.addEventListener('wheel', sync, { passive: true });
    track.addEventListener('keydown', sync);

    function sync() { pos = track.scrollLeft; }

    /* The plates are appended twice, so the second set is under the cursor by
       the time the first has walked off — wrapping back by exactly one period
       is then invisible. Without the copy the row would just run out. */
    function measure() {
        var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
        period = (track.scrollWidth + gap) / 2;
    }

    /* Writing scrollLeft every frame costs a layout on the scroller, so don't
       pay it while the block is off screen — which on a phone is most of the
       page. The row picks up where it left off when it comes back into view. */
    var visible = true;
    if (window.IntersectionObserver) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; },
                                 { rootMargin: '100px' }).observe(wrap);
    }

    var last = null;
    function tick(now) {
        if (last === null) last = now;
        var dt = (now - last) / 1000;
        last = now;
        /* A backgrounded tab hands back one huge dt on return; ignore it
           rather than teleporting the row. */
        if (dt > 0.5) dt = 0;
        if (!visible) dt = 0;
        if (!dragging && period > 0) {
            pos += SPEED * dt;
            if (pos >= period) pos -= period;
            track.scrollLeft = pos;
        }
        window.requestAnimationFrame(tick);
    }

    fetch('../assets/data/posts.json', { cache: 'no-cache' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (items) {
            if (!Array.isArray(items)) return;
            /* WHICH articles is Jack's call, from /admin: the `featured`
               checkbox on a post puts it here. posts.json is the whole archive
               (188 and growing) and the row is built twice for the loop, so
               this must never be the unfiltered list — it would put ~380
               plates on the home page. If nothing is flagged we fall back to
               the newest twelve rather than showing an empty block. */
            var usable = items.filter(function (it) {
                return it && it.url && it.image && it.image.src;
            }).sort(function (a, b) {
                return (b.date || '').localeCompare(a.date || '');
            });
            var picked = usable.filter(function (it) { return it.featured; });
            var shown = (picked.length ? picked : usable).slice(0, MOBILE ? 4 : 12);
            if (!shown.length) return;

            function plate(it, clone) {
                var a = document.createElement('a');
                a.href = it.url;
                a.target = '_blank';
                a.rel = 'noopener';
                /* The second set is the same articles again — hide it from
                   assistive tech and from tabbing so the list reads once. */
                if (clone) {
                    a.setAttribute('aria-hidden', 'true');
                    a.tabIndex = -1;
                }

                var shot = document.createElement('div');
                shot.className = 'shot';
                var img = document.createElement('img');
                img.src = '../assets/' + it.image.src;
                img.alt = '';
                img.loading = 'lazy';
                img.decoding = 'async';
                shot.appendChild(img);

                var meta = document.createElement('div');
                meta.className = 'meta';
                meta.textContent = it.meta || '';

                var title = document.createElement('div');
                title.className = 'title';
                title.textContent = it.title || '';

                a.appendChild(shot);
                a.appendChild(meta);
                a.appendChild(title);
                return a;
            }

            shown.forEach(function (it) { track.appendChild(plate(it, false)); });
            /* The duplicate set exists only to make the drift loop seamless.
               On mobile there is no drift, so there is no second set — four
               plates, 2x2, and none of the per-frame work. */
            if (!MOBILE) shown.forEach(function (it) { track.appendChild(plate(it, true)); });
            wrap.hidden = false;
            if (MOBILE) return;
            measure();
            if (!reduce) window.requestAnimationFrame(tick);
        })
        .catch(function () { /* leave the block hidden */ });

    window.addEventListener('resize', function () { measure(); sync(); }, { passive: true });
})();

/* Parallax — the ink ground only. The paper drifts at half the scroll rate
   behind the page; nothing in the content moves out of line. Off under
   prefers-reduced-motion. */
(function () {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return;
    /* Off on touch devices. Moving the background-position repaints the whole
       tiled ground on every scroll frame — on desktop that is free, on a phone
       it is the difference between a smooth scroll and a choppy one, and the
       drift is barely legible on a 390px screen anyway. */
    if (window.matchMedia && window.matchMedia('(hover: none)').matches) return;

    var ticking = false;
    function update() {
        var y = window.pageYOffset || document.documentElement.scrollTop;
        document.body.style.backgroundPosition = '0 ' + (y * 0.5).toFixed(1) + 'px';
        ticking = false;
    }
    function onScroll() {
        if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    update();
})();
</script>
</html>
