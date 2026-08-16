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
.top-nav a.active { color: var(--blue); }
.top-nav a::after {
    content: '';
    position: absolute;
    right: 0; bottom: -4px;
    width: 0; height: 2px;
    background: var(--blue);
    transition: width 0.25s ease;
}
.top-nav a:hover::after, .top-nav a.active::after { width: 100%; }

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


/* ── Page head ── */
.wrap {
    max-width: 1200px;
    margin: 0 auto;
    padding: clamp(120px, 18vh, 200px) 32px 120px;
}
.eyebrow {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 22px;
}
h1 {
    font-family: var(--display);
    font-weight: 400;
    color: var(--blue);
    line-height: 0.84;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    font-size: clamp(58px, 12vw, 150px);
    margin-bottom: 48px;
    /* blue text with a faint texture overlay clipped to the glyphs */
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


/* ── Tag filters ──
   Same idea as lydialott's works browser: a plain row of text, no pills or
   boxes, active one in the accent. Set here in Bebas (--display) rather than
   the body face — it is the only nav on the page and it should read as Jack's
   own type. Horizontally scrollable rather than wrapping, so the row never
   becomes two lines on a phone. */
.filters {
    display: flex;
    gap: 22px;
    align-items: baseline;
    margin-bottom: 34px;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    padding-bottom: 2px;
}
.filters::-webkit-scrollbar { display: none; }
.filter {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(19px, 1.8vw, 27px);
    line-height: 1;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--ink);
    background: none;
    border: 0;
    padding: 0 0 3px;
    cursor: pointer;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    transition: color var(--t-hover);
}
.filter:hover { color: var(--blue); }
.filter.is-active { color: var(--blue); border-bottom-color: var(--blue); }
.filter .n {
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.1em;
    vertical-align: super;
    margin-left: 3px;
    opacity: 0.55;
}

/* Lazy reveal: everything renders server-side (so the page works with no JS and
   is fully crawlable), then the script hides all but the first chunk and hands
   them back a chunk at a time as the sentinel comes into view. The images are
   loading="lazy", so a hidden plate never costs a request. */
.entry[hidden] { display: none; }
.sentinel { height: 1px; }
.empty-note {
    font-family: var(--body);
    font-weight: 200;
    font-style: italic;
    font-size: 16px;
    color: var(--muted);
}

/* ── Article plates — four across, square, in colour ──
   Same rendering as the home page's latest-four block. These used to be
   full-width rows with a greyscale thumbnail and a 2px rule; the plates read
   better and the covers are the point, so they run as shot. */
.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: clamp(18px, 2vw, 30px) clamp(14px, 1.6vw, 26px);
}
.entry { display: block; }
.entry .thumb {
    aspect-ratio: 1;
    overflow: hidden;
    background: var(--paper);
}
.entry .thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform var(--t-image, 0.4s ease);
}
.entry:hover .thumb img { transform: scale(1.04); }
/* the only plate that keeps a frame — a missing image still reads as a slot */
.entry .thumb.empty { border: 2px dashed var(--ink); opacity: 0.5; }

.entry .meta {
    margin-top: 10px;
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.entry .title {
    margin-top: 4px;
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(17px, 1.35vw, 24px);
    line-height: 0.98;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.entry:hover .title { color: var(--blue); }

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
   nav, eyebrow and inline links stay flat --blue. .social links are excluded
   too: background-clip would paint a visible box behind the SVGs. */
.brand {
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
    .wrap { padding: 110px 22px 80px; }
    /* stack the card: thumb on top, text under */
    .grid { grid-template-columns: 1fr 1fr; }
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

@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <input type="checkbox" id="nav-open" class="nav-check" hidden>
    <label for="nav-open" class="nav-toggle" aria-label="Menu">Menu</label>
    <nav class="top-nav">
        <a href="../about/">About</a>
        <a href="../writing/" class="active">Writing</a>
        <a href="../photography/">Photography</a>
        <a href="../music/">Music</a>
        <a href="../video/">Video</a>
        <a href="../multimedia/">Multimedia</a>
    </nav>
</header>

<section class="wrap">
    <div class="eyebrow">Selected Work</div>
    <h1>Writing</h1>



    <nav class="filters" id="filters" aria-label="Filter writing by subject">
        <button type="button" class="filter is-active" data-tag="all">Latest<span class="n">191</span></button>
        <button type="button" class="filter" data-tag="music">Music<span class="n">25</span></button>
        <button type="button" class="filter" data-tag="culture">Culture<span class="n">12</span></button>
        <button type="button" class="filter" data-tag="politics">Politics<span class="n">133</span></button>
        <button type="button" class="filter" data-tag="economy">Economy<span class="n">46</span></button>
        <button type="button" class="filter" data-tag="society">Society<span class="n">44</span></button>
    </nav>

    <div class="grid" id="grid">
        <a class="entry" href="https://www.clashmusic.com/live/live-report-phillgood-festival-2026/" target="_blank" rel="noopener" data-tags="music Culture">
            <div class="thumb"><img src="../assets/posts/draft-663d0b90/VeePandey_Phillgood_163A2953.display.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash</div>
            <div class="title">Live Report: PHILLGOOD Festival 2026</div>
        </a>
        <a class="entry" href="https://thecoldmagazine.co.uk/yaya-bey-only-white-people-are-allowed-to-love-and-mourn/?v=01c054100e77" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/posts/draft-28073e06/d1b1e21c-7981-4874-a0e6-898cd293b3c3.jpeg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">The Cold Magazine</div>
            <div class="title">Yaya Bey: ‘Only White People Are Allowed to Love and Mourn’</div>
        </a>
        <a class="entry" href="https://www.huckmag.com/article/nan-goldin-exhibition-london-hayward-gallery-you-never-did-anything-wrong" target="_blank" rel="noopener" data-tags="culture art">
            <div class="thumb"><img src="../assets/posts/draft-c43aa067/Diana-in-the-bath-2024.display.webp" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Huck</div>
            <div class="title">A major Nan Goldin exhibition is coming to London</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/live/live-report-the-black-lights/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-live-report-the-black-lights.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Live · Jul 2026</div>
            <div class="title">Live Report: The Black Lights</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/live/five-acts-to-watch-out-for-at-phillgood-festival-2026/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-five-acts-to-watch-out-for-at-phillgood-festival-2026.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Live · Jun 2026</div>
            <div class="title">Five Acts To Watch Out For At PHILLGOOD Festival 2026</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/live/the-cure-gorillaz-wolf-alice-for-phillgood-festival-2026/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-the-cure-gorillaz-wolf-alice-for-phillgood-festival-2026.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Live · Jun 2026</div>
            <div class="title">The Cure, Gorillaz, Wolf Alice For PHILLGOOD Festival 2026</div>
        </a>
        <a class="entry" href="https://thecoldmagazine.co.uk/khakikid-is-making-irish-rap-as-an-excuse-to-hang-out/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-khakikid-is-making-irish-rap-as-an-excuse-to-hang-out.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">KhakiKid Is Making Irish Rap ‘as an Excuse to Hang Out’</div>
        </a>
        <a class="entry" href="https://thecoldmagazine.co.uk/geese-psyop/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-the-geese-psyop-marks-the-death-of-indie.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">The Geese ‘Psyop’ Marks the Death of Indie</div>
        </a>
        <a class="entry" href="https://thecoldmagazine.co.uk/ruby-roberts/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-ruby-roberts-is-an-artist-of-dreamlike-spontaneity.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">Ruby Roberts Is an Artist of Dreamlike Spontaneity</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/next-wave/next-wave-1179-pollyfromthedirt/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-next-wave-1179-pollyfromthedirt.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Next Wave</div>
            <div class="title">Next Wave #1179: Pollyfromthedirt</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/next-wave/next-wave-1174-kidwild/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-next-wave-1175-kidwild.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Next Wave · Mar 2026</div>
            <div class="title">Next Wave #1175: Kidwild</div>
        </a>
        <a class="entry" href="https://jackdennisonthompson.substack.com/p/jason-williamson-the-working-class" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-jason-williamson-the-working-class-hero-who-made-his-own-cage.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Substack · Mar 2026</div>
            <div class="title">Jason Williamson: The Working-Class Hero Who Made His Own Cage</div>
        </a>
        <a class="entry" href="https://jackdennisonthompson.substack.com/p/paris-in-spring-alex-taylor-album" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-paris-in-spring-alex-taylor-album-review.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Substack · Mar 2026</div>
            <div class="title">Paris In Spring // Alex Taylor // Album Review</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/live/thundercat-transforms-o2-academy-brixton-into-a-south-london-space-station/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-thundercat-transforms-o2-academy-brixton-into-a-south-london-space-station.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Live · Mar 2026</div>
            <div class="title">Thundercat Transforms O2 Academy Brixton Into a South London Space Station</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/reviews/ms-banks-south-ldn-lover-girl/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-ms-banks-south-ldn-lover-girl.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Review · Mar 2026</div>
            <div class="title">Ms Banks — SOUTH LDN LOVER GIRL</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/parisi-link-with-fred-again-on-this-is-real/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-parisi-link-with-fred-again-on-this-is-real.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Jun 2026</div>
            <div class="title">PARISI Link With Fred again.. On ‘This Is Real (Disappear)’</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/marlon-craft-shares-soulful-cut-analog-man/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-marlon-craft-shares-soulful-cut-analog-man.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Feb 2026</div>
            <div class="title">Marlon Craft Shares Soulful Cut ‘Analog Man’</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/the-temper-trap-find-their-spark-on-new-single-into-the-wild/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-the-temper-trap-find-their-spark-on-new-single-into-the-wild.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Feb 2026</div>
            <div class="title">The Temper Trap Find Their Spark On New Single ‘Into The Wild’</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/reviews/moby-future-quiet/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-moby-future-quiet.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Review · Feb 2026</div>
            <div class="title">Moby — Future Quiet</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/brit-awards-2026-citywide-cultural-programme-confirmed/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-brit-awards-2026-citywide-cultural-programme-confirmed.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Feb 2026</div>
            <div class="title">BRIT Awards 2026: Citywide Cultural Programme Confirmed</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/villanelle-unleash-distorted-new-single-placebo/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-villanelle-unleash-distorted-new-single-placebo.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Feb 2026</div>
            <div class="title">Villanelle Unleash Distorted New Single ‘Placebo’</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/live/brick-lane-jazz-festival-adds-names-to-conference-program/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-brick-lane-jazz-festival-adds-names-to-conference-program.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Live · Feb 2026</div>
            <div class="title">Brick Lane Jazz Festival Adds Names To Conference Program</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/features/remember-me-chet-faker-interviewed/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-remember-me-chet-faker-interviewed.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Feature</div>
            <div class="title">Remember Me: Chet Faker Interviewed</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/features/audio-inception-26-artists-who-could-define-2026/" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-audio-inception-26-artists-who-could-define-2026.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · Feature · Feb 2026</div>
            <div class="title">Audio Inception: 26 Artists Who Could Define 2026</div>
        </a>
        <a class="entry" href="https://www.clashmusic.com/news/adult-dvd-release-new-single-real-tree-lee/" target="_blank" rel="noopener" data-tags="music">
            <div class="thumb"><img src="../assets/thumb-adult-dvd-release-new-single-real-tree-lee.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Clash Music · News · Jan 2026</div>
            <div class="title">Adult DVD Release New Single ‘Real Tree Lee’</div>
        </a>
        <a class="entry" href="https://jackdennisonthompson.substack.com/p/finding-community-on-eight-wheels" target="_blank" rel="noopener" data-tags="music culture">
            <div class="thumb"><img src="../assets/thumb-finding-community-on-eight-wheels.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Substack · Dec 2025</div>
            <div class="title">Finding Community on Eight Wheels</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/18/eu-pushes-libya-towards-economic-reforms/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-eu-pushes-libya-towards-economic-reforms.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">EU pushes Libya towards economic reforms</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/18/60-refugees-gone-missing-off-coast-libya/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-60-refugees-gone-missing-off-coast-libya.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">60 refugees gone missing off coast Libya</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/17/wounded-libyan-soldiers-sent-to-russia-for-medical-care/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-wounded-libyan-soldiers-sent-to-russia-for-medical-care.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Wounded Libyan soldiers sent to Russia for medical care</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/17/libyas-reconstruction-plan-takes-shape/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-libyas-reconstruction-plan-takes-shape.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Libya’s reconstruction plan takes shape</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/16/us-ramps-up-mediterranean-surveillance-missions/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-ramps-up-mediterranean-surveillance-missions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">US ramps up Mediterranean surveillance missions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/12/libya-reconsiders-turkey-maritime-deal/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-libya-reconsiders-turkey-maritime-deal.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Libya reconsiders Turkey maritime deal</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/12/libya-emerges-as-dangerous-crossroads-for-sudanese-refugees/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-libya-emerges-as-dangerous-crossroads-for-sudanese-refugees.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Libya emerges as dangerous crossroads for Sudanese refugees</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/11/russia-emerges-as-key-wheat-supplier-to-libya/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-russia-emerges-as-key-wheat-supplier-to-libya.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Russia emerges as key wheat supplier to Libya</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/10/three-women-killed-in-fatal-traffic-accident-near-tripoli/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-three-women-killed-in-fatal-traffic-accident-near-tripoli.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Three women killed in fatal traffic accident near Tripoli</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/10/libyan-attorney-general-launches-investigation-into-security-abuses/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-libyan-attorney-general-launches-investigation-into-security-abuses.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Libyan Attorney General launches investigation into security abuses</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/09/violent-clashes-at-jabal-al-oweinat-sudan-libya-border-erupts/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-violent-clashes-at-jabal-al-oweinat-sudan-libya-border-erupts.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Violent clashes at Jabal al-Oweinat: Sudan-Libya border erupts</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/09/trumps-travel-ban-on-libya-takes-effect/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-trumps-travel-ban-on-libya-takes-effect.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Trump’s Travel ban on Libya takes effect</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/09/libya-forms-committees-to-address-violent-clashes/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-libya-forms-committees-to-address-violent-clashes.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Libya forms committees to address violent clashes</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/07/neither-war-nor-peace-morocco-and-algerias-delicate-standoff/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-neither-war-nor-peace-morocco-and-algerias-delicate-standoff.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Neither war nor peace: Morocco and Algeria’s delicate standoff</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/06/greece-seeks-egypts-help-to-block-turkey-libya-maritime-deal/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-greece-seeks-egypts-help-to-block-turkey-libya-maritime-deal.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Greece seeks Egypt’s help to block Turkey-Libya maritime deal</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/05/turkish-authorities-continue-crackdown-on-the-countrys-opposition/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-turkish-authorities-continue-crackdown-on-the-countrys-opposition.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Turkish authorities continue crackdown on the country’s opposition</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/05/syria-shuts-down-captagon-production-facilities/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-syria-shuts-down-captagon-production-facilities.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Syria shuts down Captagon production facilities</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/04/uranium-enrichment-halts-iran-us-nuclear-talks/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-uranium-enrichment-halts-iran-us-nuclear-talks.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Uranium enrichment halts Iran-US nuclear talks</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/04/un-aid-convoy-attacked-in-sudan-five-killed/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-un-aid-convoy-attacked-in-sudan-five-killed.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">UN aid convoy attacked in Sudan, five killed</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/04/uk-backs-moroccos-western-sahara-plan-algeria-protests/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-uk-backs-moroccos-western-sahara-plan-algeria-protests.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">UK backs Morocco’s Western Sahara plan, Algeria protests</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/04/trumps-tariff-twist-for-british-steel/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-trumps-tariff-twist-for-british-steel.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">Trump’s tariff twist for British steel</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/06/03/us-brokers-syria-talks-sdf-negotiates-military-integration/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-brokers-syria-talks-sdf-negotiates-military-integration.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Jun 2025</div>
            <div class="title">US brokers Syria talks: SDF negotiates military integration</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/31/terrorist-group-strikes-syrian-army-in-sweida-province/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-terrorist-group-strikes-syrian-army-in-sweida-province.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Terrorist group strikes Syrian Army in Sweida province</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/30/morocco-urged-to-reform-migration-law/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-morocco-urged-to-reform-migration-law.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Morocco urged to reform migration law</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/29/us-envoy-returns-to-damascus-as-us-syria-relationship-grows/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-envoy-returns-to-damascus-as-us-syria-relationship-grows.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">US envoy returns to Damascus as US-Syria relationship grows</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/29/elon-musk-concludes-special-government-employee-stint/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-elon-musk-concludes-special-government-employee-stint.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Elon Musk concludes special government employee stint</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/29/egypt-and-mauritania-reactivate-strategic-alliance/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-egypt-and-mauritania-reactivate-strategic-alliance.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Egypt and Mauritania reactivate strategic alliance</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/28/syria-backs-moroccos-western-sahara-plan/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-syria-backs-moroccos-western-sahara-plan.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Syria backs Morocco’s Western Sahara plan</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/28/syria-and-israel-engage-in-direct-talks-to-ease-tensions/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-syria-and-israel-engage-in-direct-talks-to-ease-tensions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Syria and Israel engage in direct talks to ease tensions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/27/mediterranean-migrant-boat-disaster-greek-coastguards-charged/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-mediterranean-migrant-boat-disaster-greek-coastguards-charged.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Mediterranean migrant boat disaster: Greek coastguards charged</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/27/british-far-right-activist-tommy-robinson-walks-free-from-court/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-british-far-right-activist-tommy-robinson-walks-free-from-court.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">British Far-right activist Tommy Robinson walks free from court</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/26/kenya-backs-moroccos-autonomy-plan-for-sahara-dispute/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-kenya-backs-moroccos-autonomy-plan-for-sahara-dispute.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Kenya backs Morocco’s autonomy plan for Sahara dispute</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/26/jack-dennison-thompson-syrias-al-sharaa-the-wests-dangerous-gamble/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-jack-dennison-thompson-syrias-al-sharaa-the-wests-dangerous-gamble.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Jack Dennison-Thompson: Syria’s al-Sharaa, the West’s Dangerous Gamble</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/26/europe-escalates-pressure-on-israel-at-madrid-summit-over-gaza/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-europe-escalates-pressure-on-israel-at-madrid-summit-over-gaza.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Europe escalates pressure on Israel at Madrid summit over Gaza</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/26/algerian-union-bank-expands-in-mauritania/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-algerian-union-bank-expands-in-mauritania.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algerian Union Bank expands in Mauritania</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/25/spain-sees-sharp-rise-in-migrant-sea-arrivals/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-spain-sees-sharp-rise-in-migrant-sea-arrivals.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Spain sees sharp rise in migrant sea arrivals</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/23/kashmir-dogfight-grounds-frances-8-billion-rafale-export-dreams/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-kashmir-dogfight-grounds-frances-8-billion-rafale-export-dreams.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Kashmir dogfight grounds France’s $8 billion Rafale export dreams</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/23/algeria-shakes-up-intelligence-leadership-amid-regional-crises/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algeria-shakes-up-intelligence-leadership-amid-regional-crises.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algeria shakes up intelligence leadership amid regional crises</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/23/algeria-conducts-military-exercise-near-morocco-border/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algeria-conducts-military-exercise-near-morocco-border.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algeria conducts military exercise near Morocco border</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/22/eu-and-au-pledge-stronger-cooperation/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-eu-and-au-pledge-stronger-cooperation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">EU and AU pledge stronger cooperation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/20/uk-says-gulf-trade-deal-next-after-sealing-eu-pact/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-uk-says-gulf-trade-deal-next-after-sealing-eu-pact.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">UK says Gulf trade deal next after sealing EU pact</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/20/following-us-move-eu-prepares-to-lift-syria-sanctions/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-following-us-move-eu-prepares-to-lift-syria-sanctions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Following US move, EU prepares to lift Syria sanctions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/20/algeria-france-relations-spiral-as-passport-deal-breached/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-algeria-france-relations-spiral-as-passport-deal-breached.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algeria-France relations spiral as passport deal breached</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/19/children-trafficked-and-abused-in-south-african-illegal-mines/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-children-trafficked-and-abused-in-south-african-illegal-mines.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Children trafficked and abused in South African illegal mines</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/16/press-freedom-crumbles-in-north-africa/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-press-freedom-crumbles-in-north-africa.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Press freedom crumbles in North Africa</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/15/tunisias-democracy-faces-breaking-point/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-tunisias-democracy-faces-breaking-point.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Tunisia’s democracy faces breaking point</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/14/trump-meets-syrian-president-as-us-removes-sanctions/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-trump-meets-syrian-president-as-us-removes-sanctions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Trump meets Syrian president as US removes sanctions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/14/algeria-france-relations-reach-totally-blocked-state/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algeria-france-relations-reach-totally-blocked-state.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algeria-France relations reach “totally blocked” state</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/13/us-approves-1-4-billion-weapons-sale-to-uae/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-approves-1-4-billion-weapons-sale-to-uae.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">US approves $1.4 Billion weapons sale to UAE</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/13/trump-offers-syria-olive-branch-that-could-end-economic-isolation/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-trump-offers-syria-olive-branch-that-could-end-economic-isolation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Trump offers Syria olive branch that could end economic isolation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/12/three-children-dead-as-libya-remains-key-crossing-for-migrants/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-three-children-dead-as-libya-remains-key-crossing-for-migrants.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Three children dead as Libya remains key crossing for migrants</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/12/france-backs-moroccos-south-with-major-e150m-investment/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-france-backs-moroccos-south-with-major-150m-investment.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">France backs Morocco’s south with major €150M investment</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/08/uk-us-full-and-comprehensive-trade-deal-announced-by-trump/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-uk-us-full-and-comprehensive-trade-deal-announced-by-trump.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">UK-US “full and comprehensive” trade deal announced by Trump</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/08/emergency-supply-platform-launched-by-king-mohammed-vi/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-emergency-supply-platform-launched-by-king-mohammed-vi.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Emergency supply platform launched by King Mohammed VI</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/07/morocco-seeks-to-expand-casablanca-airport-for-world-cup/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-seeks-to-expand-casablanca-airport-for-world-cup.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Morocco seeks to expand Casablanca airport for World Cup</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/07/france-first-stop-for-syrian-president-in-europe/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-france-first-stop-for-syrian-president-in-europe.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">France first stop for Syrian president in Europe</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/05/rwanda-us-begin-deportation-talks/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-rwanda-us-begin-deportation-talks.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Rwanda-US begin deportation talks</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/05/indra-group-showcases-defense-tech-at-feindef-25/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-indra-group-showcases-defense-tech-at-feindef-25.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Indra group showcases defense tech at FEINDEF 25</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/05/algeria-jails-historian-over-amazigh-identity-comments/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-algeria-jails-historian-over-amazigh-identity-comments.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Algeria jails historian over Amazigh identity comments</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/02/trumps-national-security-adviser-mike-waltz-ousted/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-trumps-national-security-adviser-mike-waltz-ousted.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Trump’s national security adviser Mike Waltz ousted</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/02/opposition-to-tunisias-president-takes-to-the-streets/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-opposition-to-tunisias-president-takes-to-the-streets.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Opposition to Tunisia’s president takes to the streets</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/02/morocco-boosts-public-sector-pay-to-1000-monthly-by-2026/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-boosts-public-sector-pay-to-1-000-monthly-by-2026.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Morocco boosts public sector pay to $1,000 monthly by 2026</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/01/morocco-crowned-african-womens-futsal-champions/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-morocco-crowned-african-womens-futsal-champions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Morocco crowned African women’s futsal champions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/05/01/britain-enters-discussions-on-palestinian-state-recognition/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-britain-enters-discussions-on-palestinian-state-recognition.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · May 2025</div>
            <div class="title">Britain enters discussions on Palestinian state recognition</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/30/morocco-opens-africas-largest-shipyard/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-opens-africas-largest-shipyard.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Morocco opens Africa’s largest shipyard</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/30/france-condemns-israels-unacceptable-travel-ban/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-france-condemns-israels-unacceptable-travel-ban.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">France condemns Israel’s “unacceptable” travel ban</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/29/tunisia-rejects-foreign-criticism-of-opposition-trial/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-tunisia-rejects-foreign-criticism-of-opposition-trial.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Tunisia rejects foreign criticism of opposition trial</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/29/syrias-new-leadership-struggles-as-violence-persists/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-syrias-new-leadership-struggles-as-violence-persists.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Syria’s new leadership struggles as violence persists</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/29/short-term-ceasefire-declared-in-ukraine-war/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-short-term-ceasefire-declared-in-ukraine-war.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Short-term ceasefire declared in Ukraine War</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/29/morocco-partners-with-huawei-to-boost-digital-skills/" target="_blank" rel="noopener" data-tags="economy society">
            <div class="thumb"><img src="../assets/thumb-morocco-partners-with-huawei-to-boost-digital-skills.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Morocco partners with Huawei to boost digital skills</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/29/deepfake-video-sparks-deadly-attack-on-syrian-druze-community/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-deepfake-video-sparks-deadly-attack-on-syrian-druze-community.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Deepfake video sparks deadly attack on Syrian Druze community</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/28/global-military-spending-hits-steepest-rise-since-cold-war/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-global-military-spending-hits-steepest-rise-since-cold-war.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Global military spending hits steepest rise since Cold War</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/28/britain-to-host-palestinian-pm-as-diplomatic-winds-shift-on-gaza/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-britain-to-host-palestinian-pm-as-diplomatic-winds-shift-on-gaza.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Britain to host Palestinian PM as diplomatic winds shift on Gaza</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/25/trump-to-announce-extensive-saudi-arms-package/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-trump-to-announce-extensive-saudi-arms-package.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Trump to announce extensive Saudi arms package</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/25/gallipoli-landings-commemorated-on-110th-anniversary/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-gallipoli-landings-commemorated-on-110th-anniversary.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Gallipoli landings commemorated on 110th anniversary</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/24/terror-past-vs-stability-the-syria-question/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-terror-past-vs-stability-the-syria-question.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Terror past vs. stability: the Syria question</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/24/narcotics-and-alcohol-seized-in-moroccan-security-force-raids/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-narcotics-and-alcohol-seized-in-moroccan-security-force-raids.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Narcotics and alcohol seized in Moroccan security force raids</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/24/moscow-algiers-alliance-forms-amid-diplomatic-tensions/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-moscow-algiers-alliance-forms-amid-diplomatic-tensions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Moscow-Algiers alliance forms amid diplomatic tensions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/24/morocco-and-spain-strengthen-security-cooperation/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-morocco-and-spain-strengthen-security-cooperation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Morocco and Spain strengthen security cooperation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/23/top-eu-official-visits-algeria-to-boost-cooperation/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-top-eu-official-visits-algeria-to-boost-cooperation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Top EU official visits Algeria to boost cooperation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/22/spy-chief-disputes-netanyahu-dismissal/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-spy-chief-disputes-netanyahu-dismissal.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Spy Chief Disputes Netanyahu Dismissal</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/21/iraq-mps-unite-against-former-militants-arab-league-visit/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-iraq-mps-unite-against-former-militants-arab-league-visit.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Iraq MPS unite against former militants’ Arab League visit</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/21/caf-royal-air-maroc-deal-may-force-algeria-to-open-airspace/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-caf-royal-air-maroc-deal-may-force-algeria-to-open-airspace.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">CAF-Royal Air Maroc deal may force Algeria to open airspace</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/21/algeria-makes-strides-in-economic-diversification/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-algeria-makes-strides-in-economic-diversification.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Algeria makes strides in economic diversification</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/17/usda-exempts-morocco-as-new-sugar-tariffs-take-effect/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-usda-exempts-morocco-as-new-sugar-tariffs-take-effect.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">USDA exempts Morocco as new sugar tariffs take effect</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/17/us-approves-825-million-missile-deal-to-strategic-ally-morocco/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-approves-825-million-missile-deal-to-strategic-ally-morocco.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">US approves $825 million missile deal to strategic ally Morocco</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/16/tensions-rise-as-lammy-meets-in-secret-with-israels-foreign-minister/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-tensions-rise-as-lammy-meets-in-secret-with-israels-foreign-minister.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Tensions rise as Lammy meets in secret with Israel’s Foreign Minister</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/16/secret-meeting-between-uk-and-isreal-foreign-ministers/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-secret-meeting-between-uk-and-isreal-foreign-ministers.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Secret meeting between UK and Isreal Foreign Ministers</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/16/netanyahu-shin-bet-feud-deepens-amid-security-crisis/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-netanyahu-shin-bet-feud-deepens-amid-security-crisis.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Netanyahu-Shin Bet feud deepens amid security crisis</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/16/france-hits-back-at-algeria-with-expulsion-of-12-diplomats/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-france-hits-back-at-algeria-with-expulsion-of-12-diplomats.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">France hits back at Algeria with expulsion of 12 diplomats</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/15/african-unions-peace-and-security-council-win-for-algeria/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-african-unions-peace-and-security-council-win-for-algeria.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">African Union’s peace and security council win for Algeria</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/14/morocco-gains-omans-support-in-western-sahara-dispute/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-morocco-gains-omans-support-in-western-sahara-dispute.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Morocco gains Oman’s support in Western Sahara dispute</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/14/macrons-palestine-stance-can-force-the-uks-hand-on-recognition/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-macrons-palestine-stance-can-force-the-uks-hand-on-recognition.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Macron’s Palestine stance can force the UK’s hand on recognition</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/14/algeria-france-tensions-escalate-over-kidnapping-indictments/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algeria-france-tensions-escalate-over-kidnapping-indictments.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Algeria-France tensions escalate over kidnapping indictments</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/14/algeria-and-tunisia-sign-educational-partnership-deal/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-algeria-and-tunisia-sign-educational-partnership-deal.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Algeria and Tunisia sign educational partnership deal</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/11/us-protest-crackdown-signals-wider-threat-to-western-activism/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-us-protest-crackdown-signals-a-wider-threat-to-western-activism.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">US protest crackdown signals a wider threat to Western activism</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/11/the-eu-and-uae-are-set-to-open-talks-over-a-free-trade-agreement/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-the-eu-and-uae-are-set-to-open-talks-over-a-free-trade-agreement.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">The EU and UAE are set to open talks over a free trade agreement</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/11/syria-and-south-korea-begin-bilateral-relationship/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-syria-and-south-korea-begin-bilateral-relationship.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Syria and South Korea begin bilateral relationship</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/10/nato-and-morocco-strengthen-key-ally-partnership-in-north-africa/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-nato-and-morocco-strengthen-key-ally-partnership-in-north-africa.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">NATO and Morocco strengthen key ally partnership in North Africa</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/10/gazas-hidden-war-womens-health-under-siege/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-gazas-hidden-war-womens-health-under-siege.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Gaza’s hidden war: women’s health under siege</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/09/marco-rubio-confirms-us-support-of-morocco-in-western-sahara/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-marco-rubio-confirms-us-support-of-morocco-in-western-sahara.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Marco Rubio confirms US support of Morocco in Western Sahara</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/08/sarkozy-faces-prison-over-alleged-libyan-cash/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-sarkozy-faces-prison-over-alleged-libyan-cash.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Sarkozy faces prison over alleged Libyan cash</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/08/moroccan-national-fired-for-confronting-microsofts-ties-to-israel/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-moroccan-national-fired-for-confronting-microsofts-ties-to-israel.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Moroccan national fired for confronting Microsoft’s ties to Israel</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/08/algerian-cabinet-meeting-sets-key-directives-for-the-end-of-2025/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-algerian-cabinet-meeting-sets-key-directives-for-the-end-of-2025.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Algerian cabinet meeting sets key directives for the end of 2025</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/07/new-lockerbie-documents-point-the-finger-back-at-libya/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-new-lockerbie-documents-point-the-finger-back-at-libya.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">New Lockerbie documents point the finger back at Libya</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/07/libya-orders-aid-groups-to-close-amid-migration-concerns/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-libya-orders-aid-groups-to-close-amid-migration-concerns.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Libya orders aid groups to close amid migration concerns</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/07/france-and-egypt-sign-strategic-partnership-to-boost-stability/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-france-and-egypt-sign-strategic-partnership-to-boost-stability.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">France and Egypt sign strategic partnership to boost stability</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/03/syrian-government-reaches-deal-in-prisoner-exchange/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-syrian-government-reaches-deal-in-prisoner-exchange.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Syrian government reaches deal in prisoner exchange</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/03/germany-orders-deportaton-of-palestine-activists/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-germany-orders-deportation-of-palestine-activists.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Germany orders deportation of Palestine activists</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/02/netanyahu-sparks-crisis-with-shin-bet-chief-appointment/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-netanyahu-sparks-crisis-with-shin-bet-chief-appointment.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Netanyahu sparks crisis with Shin Bet Chief appointment</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/02/morocco-advances-african-stability/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-morocco-advances-african-stability.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Morocco advances African stability</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/02/egypt-syria-relations-remain-cautious-in-the-post-assad-era/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-egypt-syria-relations-remain-cautious-in-the-post-assad-era.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Egypt-Syria relations remain cautious in the post-Assad era</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/01/russias-economy-growth-claims-vs-european-reality/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-russias-economy-growth-claims-vs-european-reality.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Russia’s economy: growth claims vs. European reality</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/04/01/cairos-caution-egypt-keeps-syrias-new-regime-at-arms-length/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-cairos-caution-egypt-keeps-syrias-new-regime-at-arms-length.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Apr 2025</div>
            <div class="title">Cairo’s caution: Egypt keeps Syria’s new regime at arm’s length</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/31/moroccos-economic-growth-slows-to-3-7-in-q4-2024/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-moroccos-economic-growth-slows-to-3-7-in-q4-2024.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco’s economic growth slows to 3.7% in Q4 2024</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/31/morocco-tightens-digital-laws-with-prison-sentences-for-critics/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-morocco-tightens-digital-laws-with-prison-sentences-for-critics.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco tightens digital laws with prison sentences for critics</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/28/uk-business-freedom-in-western-sahara-affirmed/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-uk-business-freedom-in-western-sahara-affirmed.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">UK business freedom in Western Sahara affirmed</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/28/americas-relief-wont-save-russias-economy-without-europe/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-americas-relief-wont-save-russias-economy-without-europe.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">America’s relief won’t save Russia’s economy without Europe</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/27/rome-backs-syrias-transition-with-e68m-in-aid/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-rome-backs-syrias-transition-with-68m-in-aid.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Rome backs Syria’s transition with €68M in aid</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/27/italy-backs-syrias-transition-with-e68m-package/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-italy-backs-syrias-transition-with-68m-package.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Italy backs Syria’s transition with €68M package</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/26/tunisias-saied-appoints-zenzri-as-pm-amid-economic-crisis/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-tunisias-saied-appoints-zenzri-as-pm-amid-economic-crisis.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Tunisia’s Saied appoints Zenzri as PM amid economic crisis</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/26/moroccos-solar-power-to-soar-13-fold-by-2028/" target="_blank" rel="noopener" data-tags="economy society">
            <div class="thumb"><img src="../assets/thumb-moroccos-solar-power-to-soar-13-fold-by-2028.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco’s solar power to soar 13-Fold by 2028</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/26/morocco-eu-tensions-rise-over-aluminium-wheel-duties/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-eu-tensions-rise-over-aluminium-wheel-duties.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco-EU tensions rise over aluminium wheel duties</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/26/morocco-eu-aluminium-duties-dispute/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-eu-aluminium-duties-dispute.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco-EU aluminium duties dispute</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/26/morocco-genuine-hub-between-europe-and-africa-says-italy/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-morocco-genuine-hub-between-europe-and-africa-says-italy.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco “genuine hub” between Europe and Africa, says Italy</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/25/tunisia-president-saied-appoints-zenzri-as-new-prime-minister/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-tunisia-president-saied-appoints-zenzri-as-new-prime-minister.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Tunisia: president Saied appoints Zenzri as new Prime Minister</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/22/emily-thornberry-netanyahu-broke-gaza-truce-to-avoid-trial/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-uk-official-netanyahu-broke-gaza-truce-to-avoid-trial.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">UK official: Netanyahu broke Gaza truce to avoid trial</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/22/thornberry-netanyahu-broke-gaza-truce-to-avoid-corruption-trial/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-thornberry-netanyahu-broke-gaza-truce-to-avoid-corruption-trial.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Thornberry: Netanyahu broke Gaza truce to avoid corruption trial</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/20/tunisian-opposition-calls-for-political-prisoners-release/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-tunisian-opposition-calls-for-political-prisoners-release.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Tunisian opposition calls for political prisoners’ release</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/20/morocco-spain-trade-relations-reach-record-e22-7-billion/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-morocco-spain-trade-relations-reach-record-22-7-billion.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco-Spain trade relations reach record €22.7 billion</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/20/morocco-spain-trade-hits-record-high/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-spain-trade-hits-record-high.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco-Spain trade hits record high</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/19/morocco-au-talks-address-suspended-nations-transitions/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-morocco-au-talks-address-suspended-nations-transitions.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco AU talks address suspended nations’ transitions</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/19/david-lammy-backtracks-on-israel-international-law-claims/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-david-lammy-backtracks-on-israel-international-law-claims.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">David Lammy backtracks on Israel international law claims</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/19/algeria-tunisia-libya-advance-electrical-interconnection-project/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-algeria-tunisia-libya-advance-electrical-interconnection-project.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Algeria, Tunisia, Libya advance electrical interconnection project</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/18/uk-pushes-for-truce-in-gaza-after-israeli-airstrikes-kill-over-400/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-uk-pushes-for-truce-in-gaza-after-israeli-airstrikes-kill-over-400.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">UK pushes for truce in Gaza after Israeli airstrikes kill over 400</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/15/violence-in-syria-un-condemns-attacks-after-1000-killed/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-violence-in-syria-un-condemns-attacks-after-1-000-killed.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Violence in Syria: UN condemns attacks after 1,000 killed</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/15/egypt-train-incident-eight-killed-as-minibus-hit-at-crossing/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-egypt-train-incident-eight-killed-as-minibus-hit-at-crossing.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Egypt train incident: Eight killed as minibus hit at crossing</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/14/syrian-government-secures-kurdish-alliance/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-syrian-government-secures-kurdish-alliance.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Syrian government secures Kurdish alliance</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/14/moroccos-north-south-railway-expansion-plan-unveiled/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-moroccos-north-south-railway-expansion-plan-unveiled.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco’s North-South railway expansion plan unveiled</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/13/usafricom-confronts-libya-crisis/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-us-africa-command-confronts-libya-crisis.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">US Africa Command confronts Libya crisis</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/13/morocco-faces-measles-outbreak-due-to-antivax-misinformation/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-morocco-faces-measles-outbreak-due-to-antivax-misinformation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco faces measles outbreak due to antivax misinformation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/12/two-faces-of-syria-druze-integration-amid-northern-violence/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-two-faces-of-syria-druze-integration-amid-northern-violence.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Two faces of Syria: Druze integration amid northern violence</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/12/global-x-outages-blamed-on-sophisticated-cyberattack/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-global-x-outages-blamed-on-sophisticated-cyberattack.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Global X outages blamed on sophisticated cyberattack</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/11/divided-libya-parliament-official-criticises-uns-role-in-political-split/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-divided-libya-parliament-official-criticises-uns-role-in-split.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Divided Libya: Parliament official criticises UN’s role in split</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/10/carney-takes-helm-as-canadian-pm-amid-trade-tensions-with-us/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-carney-takes-helm-as-canadian-pm-amid-trade-tensions-with-us.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Carney takes helm as Canadian PM amid trade tensions with US</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/10/algeria-investigation-ex-interior-minister-faces-corruption-charges/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-algeria-investigation-ex-interior-minister-faces-corruption-charges.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Algeria investigation: ex-interior minister faces corruption charges</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/09/syrian-sanctions-lifted-by-the-uk-offering-economic-lifeline/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-syrian-sanctions-lifted-by-the-uk-offering-economic-lifeline.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Syrian sanctions lifted by the UK, offering economic lifeline</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/08/trump-signals-final-moments-in-iran-nuclear-negotiations/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-trump-signals-final-moments-in-iran-nuclear-negotiations.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Trump signals ‘final moments’ in Iran nuclear negotiations</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/08/syrian-civilians-caught-in-crossfire-as-world-stays-silent/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-syrian-civilians-caught-in-crossfire-as-world-stays-silent.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Syrian civilians caught in crossfire as world stays silent</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/06/south-sudan-peace-agreement-at-risk-as-machar-allies-detained/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-south-sudan-peace-agreement-at-risk-as-machar-allies-detained.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">South Sudan Peace Agreement at Risk as Machar Allies Detained</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/06/musk-slams-european-leaders-over-forever-war-in-ukraine/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-musk-slams-european-leaders-over-forever-war-in-ukraine.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Musk slams European leaders over ‘forever war’ in Ukraine</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/06/morocco-surpasses-france-as-spains-as-main-gas-customer/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-morocco-surpasses-france-as-spains-as-main-gas-customer.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco surpasses France as Spain’s as main gas customer</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/06/as-syria-falls-russia-sets-sights-on-libya-strategic-prize/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-as-syria-falls-russia-sets-sights-on-libyas-strategic-prize.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">As Syria falls, Russia sets sights on Libya’s strategic prize</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/06/algeria-rebuffs-un-criticism-on-human-rights-defenders/" target="_blank" rel="noopener" data-tags="society">
            <div class="thumb"><img src="../assets/thumb-algeria-rebuffs-un-criticism-on-human-rights-defenders.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Algeria rebuffs UN criticism on human rights defenders</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/05/morocco-leads-next-chapter-in-african-water-council-amcow/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-morocco-leads-next-chapter-in-the-african-water-council.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Morocco leads next chapter in the African Water Council</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/05/eu-unveils-e800-billion-rearm-europe-plan-amid-ukraine-crisis/" target="_blank" rel="noopener" data-tags="economy politics">
            <div class="thumb"><img src="../assets/thumb-eu-unveils-800-billion-rearm-europe-plan-amid-ukraine-crisis.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">EU unveils €800 billion ReArm Europe plan amid Ukraine crisis</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/05/bds-launches-ramadan-boycott-of-israeli-medjool-dates/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-bds-launches-ramadan-boycott-of-israeli-medjool-dates.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">BDS launches Ramadan boycott of Israeli medjool Dates</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/04/demand-for-public-trial-in-tunisian-conspiracy-case/" target="_blank" rel="noopener" data-tags="politics society">
            <div class="thumb"><img src="../assets/thumb-demand-for-public-trial-in-tunisian-conspiracy-case.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Demand for Public Trial in Tunisian ‘Conspiracy Case’</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/03/03/tunisia-reacts-to-citizens-involvement-in-israel-hamas-war/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-tunisia-reacts-to-citizens-involvement-in-israel-hamas-war.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Mar 2025</div>
            <div class="title">Tunisia Reacts to Citizen’s involvement in Israel-Hamas war</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/28/life-imprisonment-for-tunisian-behind-nice-basilica-attack/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-life-imprisonment-for-tunisian-behind-nice-basilica-attack.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Life imprisonment for Tunisian behind Nice basilica attack</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/28/benghazi-proposed-as-arab-parliament-host/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-benghazi-proposed-as-arab-parliament-host.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Benghazi proposed as Arab Parliament host</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/28/algerian-ambassador-in-uruguay-for-presidents-inauguration/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algerian-ambassador-in-uruguay-for-presidents-inauguration.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Algerian Ambassador in Uruguay for President’s Inauguration</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/28/algeria-faces-criticism-over-cultural-appropriation/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-algeria-faces-criticism-over-cultural-appropriation.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Algeria faces criticism over cultural appropriation</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/27/paris-agricultural-show-cements-morocco-france-farming-alliance/" target="_blank" rel="noopener" data-tags="economy">
            <div class="thumb"><img src="../assets/thumb-paris-agricultural-show-cements-morocco-france-farming-alliance.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Paris agricultural show cements Morocco-France farming alliance</div>
        </a>
        <a class="entry" href="https://maghrebi.org/2025/02/27/algeria-signs-landmark-global-social-justice-agreement/" target="_blank" rel="noopener" data-tags="politics">
            <div class="thumb"><img src="../assets/thumb-algeria-signs-landmark-global-social-justice-agreement.jpg" alt="" loading="lazy" decoding="async"></div>
            <div class="meta">Maghrebi.org · Feb 2025</div>
            <div class="title">Algeria signs landmark global social justice agreement</div>
        </a>
    </div>
    <div class="sentinel" id="sentinel"></div>
    <p class="empty-note" id="none" hidden>Nothing filed under that yet.</p>
</section>

<footer class="foot">
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

/* Filter + lazy reveal for the writing index. The plates are all in the HTML
   already; this only decides which of them are shown, a chunk at a time.
   With JS off every plate is visible and the page still reads correctly. */
(function () {
    var grid = document.getElementById('grid');
    if (!grid) return;
    var entries  = Array.prototype.slice.call(grid.querySelectorAll('.entry'));
    var bar      = document.getElementById('filters');
    var sentinel = document.getElementById('sentinel');
    var none     = document.getElementById('none');
    /* Half a chunk on a phone: the plates are two-across there, so 24 is four
       screens of images to download before the first scroll. */
    var CHUNK    = window.innerWidth < 640 ? 12 : 24;
    var active   = 'all';
    var shown    = 0;

    function matches(el) {
        return active === 'all' || (' ' + el.dataset.tags + ' ').indexOf(' ' + active + ' ') >= 0;
    }
    /* Hand back the next CHUNK of matching plates. Returns how many are still
       held back, so the sentinel knows whether there is more to come. */
    function reveal() {
        var left = 0, given = 0;
        for (var i = 0; i < entries.length; i++) {
            var e = entries[i];
            if (!matches(e)) continue;
            if (e.hidden) {
                if (given < CHUNK) { e.hidden = false; given++; shown++; }
                else left++;
            }
        }
        return left;
    }
    function setTag(tag) {
        active = tag;
        shown = 0;
        entries.forEach(function (e) { e.hidden = true; });
        var left = reveal();
        none.hidden = shown > 0;
        sentinel.style.display = left ? '' : 'none';
        if (history.replaceState) {
            history.replaceState(null, '', tag === 'all' ? location.pathname : '#' + tag);
        }
        Array.prototype.forEach.call(bar.querySelectorAll('.filter'), function (b) {
            b.classList.toggle('is-active', b.dataset.tag === tag);
        });
    }

    bar.addEventListener('click', function (ev) {
        var b = ev.target.closest ? ev.target.closest('.filter') : null;
        if (b) setTag(b.dataset.tag);
    });

    if (window.IntersectionObserver) {
        new IntersectionObserver(function (es) {
            if (!es[0].isIntersecting) return;
            var left = reveal();
            if (!left) sentinel.style.display = 'none';
        }, { rootMargin: '600px' }).observe(sentinel);
    } else {
        /* No observer: show everything rather than stranding the archive. */
        CHUNK = entries.length;
    }

    function fromHash() {
        var h = (location.hash || '').replace('#', '');
        return bar.querySelector('.filter[data-tag="' + h + '"]') ? h : 'all';
    }
    /* A hash change on an already-loaded page (an external #music link landing
       here, someone editing the address bar) has to re-filter — the initial
       read alone only covers a cold load. */
    window.addEventListener('hashchange', function () {
        var t = fromHash();
        if (t !== active) setTag(t);
    });
    setTag(fromHash());
})();
</script>
</html>