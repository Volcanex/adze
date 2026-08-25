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

/* ── Slim masthead (top-left name + right-side nav) ── */
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
   that can disappear. The script below only adds Escape-to-close on top. */
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

    .nav-toggle { display: block; }
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
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s;
    }
    .nav-check:checked ~ .top-nav { opacity: 1; visibility: visible; }
    .top-nav a::after { display: none; }
    .top-nav a:hover, .top-nav a.active { color: var(--blue); }
    .nav-toggle { position: relative; z-index: 101; }
    .nav-check:checked ~ .nav-toggle::after { content: ' ×'; }
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
    background-image: var(--blue-fill);
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Tag filters — the same row as /writing, labels derived from the data ── */
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

/* ── Video plates ──
   16:9 rather than the writing page's square: a video frame has a shape and
   cropping it to a square throws away the composition. Three across on
   desktop, one on a phone — a 16:9 plate two-across at 390px is 185px wide,
   which is not a video, it is a stamp. */
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: clamp(26px, 3vw, 44px) clamp(14px, 1.6vw, 26px);
}
.item { display: block; }
.item[hidden] { display: none; }

/* The frame is a FACADE until it is clicked: a poster image and a play mark,
   with the real player swapped in on demand. Sixteen YouTube iframes on one
   page is several megabytes of third-party script and sixteen live players
   before anybody has asked to watch anything — the thing the mobile-smoothness
   rules in this site's CLAUDE.md exist to prevent. */
.frame {
    position: relative;
    aspect-ratio: 16 / 9;
    overflow: hidden;
    background: var(--ink);
    cursor: pointer;
}
.frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform var(--t-image, 0.4s ease), opacity var(--t-hover);
}
.item:hover .frame img { transform: scale(1.04); opacity: 0.9; }
.frame iframe, .frame video {
    width: 100%;
    height: 100%;
    display: block;
    border: 0;
    background: #000;
}
.frame.empty { border: 2px dashed var(--ink); opacity: 0.5; background: none; }

/* Hover preview for videos Jack has uploaded himself (never for a YouTube
   link — that would mean loading a third-party player on hover, which is the
   thing the facade above exists to avoid). Muted, looping, and it only starts
   fetching when the pointer arrives. pointer-events:none so the click still
   lands on .frame and opens the real player. */
.frame .preview {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
    pointer-events: none;
}
.play { z-index: 2; }

/* Play mark — a triangle in the blue, no icon font, no CDN. */
.play {
    position: absolute;
    left: 50%; top: 50%;
    transform: translate(-50%, -50%);
    width: 62px; height: 62px;
    border-radius: 50%;
    background: rgba(244, 243, 238, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background var(--t-hover), transform var(--t-hover);
    pointer-events: none;
}
.play::after {
    content: '';
    margin-left: 5px;
    border-style: solid;
    border-width: 11px 0 11px 19px;
    border-color: transparent transparent transparent var(--blue);
}
.item:hover .play { background: #fff; transform: translate(-50%, -50%) scale(1.06); }

/* A duration badge only exists when Jack has filled one in. */
.dur {
    position: absolute;
    right: 8px; bottom: 8px;
    padding: 2px 6px;
    background: rgba(11, 13, 26, 0.8);
    color: #fff;
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.1em;
}

.item .meta {
    margin-top: 10px;
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.item .title {
    margin-top: 4px;
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(17px, 1.35vw, 24px);
    line-height: 0.98;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.item:hover .title { color: var(--blue); }
.item .blurb {
    margin-top: 6px;
    font-family: var(--body);
    font-weight: 200;
    font-size: 14px;
    line-height: 1.45;
    color: var(--muted);
}

.empty-note {
    font-family: var(--body);
    font-weight: 200;
    font-style: italic;
    font-size: 16px;
    color: var(--muted);
}

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
    background-size: cover, var(--fill-size);
    background-position: center;
    background-repeat: no-repeat, no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

@media (max-width: 1000px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .wrap { padding: 110px 22px 80px; }
    .grid { grid-template-columns: 1fr; }
    .play { width: 52px; height: 52px; }
}
/* Touch devices: the masthead's backdrop blur is recomputed on every scroll
   frame and it is the single most expensive thing on the page on a phone. */
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
        <a href="../writing/">Writing</a>
        <a href="../photography/">Photography</a>
        <a href="../music/">Music</a>
        <a href="../video/" class="active">Video</a>
        <a href="../multimedia/">Multimedia</a>
    </nav>
</header>



<section class="wrap">
    <div class="eyebrow" data-copy="eyebrow">Selected Work</div>
    <h1>Video</h1>

    <nav class="filters" id="filters" aria-label="Filter video by subject">
        <button type="button" class="filter is-active" data-tag="all">All<span class="n">17</span></button>
        <button type="button" class="filter" data-tag="books">books<span class="n">8</span></button>
        <button type="button" class="filter" data-tag="film">film<span class="n">2</span></button>
        <button type="button" class="filter" data-tag="philosophy">philosophy<span class="n">7</span></button>
        <button type="button" class="filter" data-tag="shorts">shorts<span class="n">1</span></button>
    </nav>


    <div class="grid" id="grid">
<article class="item" data-tags="books shorts">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/PlkuBXOn4YM?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Norwegian Wood - Love, Loss, and Loneliness">

                <img src="../assets/videos/norwegian-wood-love-loss-and-loneliness/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
            </div>
            <div class="meta">Keskesay · January 2025</div>
            <h2 class="title"><a href="https://www.youtube.com/shorts/PlkuBXOn4YM" target="_blank" rel="noopener">Norwegian Wood - Love, Loss, and Loneliness</a></h2>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/eit3NeWzz5s?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Decoding Norwegian Wood: Murakami&#39;s Masterpiece Explored">

                <img src="../assets/videos/decoding-norwegian-wood-murakamis-masterpiece-explored/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">6:36</span>
            </div>
            <div class="meta">Keskesay · January 2025</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=eit3NeWzz5s" target="_blank" rel="noopener">Decoding Norwegian Wood: Murakami&#39;s Masterpiece Explored</a></h2>
            <p class="blurb">In 1979, a young jazz bar owner named Haruki Murakami had a moment of inspiration at a baseball game that would change literature forever. Today, we&#39;re diving deep into his breakthrough masterpiece, Norwegian Wood — a novel that blends Eastern and Western influences to create something uniquely powerful.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/UoettzQlAvA?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Why you should write according to George Orwell">

                <img src="../assets/videos/why-you-should-write-according-to-george-orwell/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">8:52</span>
            </div>
            <div class="meta">Keskesay · February 2022</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=UoettzQlAvA" target="_blank" rel="noopener">Why you should write according to George Orwell</a></h2>
            <p class="blurb">In this video I will be looking at the four motivations which George Orwell believed inspired each writer to write, according to his essay &#39;Why I Write&#39;.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/nBgO9Y3IEWw?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Leonardo Da Vinci the philosophy of a creator">

                <img src="../assets/videos/leonardo-da-vinci-the-philosophy-of-a-creator/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">7:26</span>
            </div>
            <div class="meta">Keskesay · November 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=nBgO9Y3IEWw" target="_blank" rel="noopener">Leonardo Da Vinci the philosophy of a creator</a></h2>
            <p class="blurb">In this video, I am exploring the life of Leonardo Da Vinci and the philosophy that we can take away from his life.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/9t-PuyahHc0?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The philosophy of Thomas Sankara ?">

                <img src="../assets/videos/the-philosophy-of-thomas-sankara/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">8:24</span>
            </div>
            <div class="meta">Keskesay · July 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=9t-PuyahHc0" target="_blank" rel="noopener">The philosophy of Thomas Sankara ?</a></h2>
            <p class="blurb">Thomas Sankara was a revolutionary who would become the president of Burkina Faso and is one of the most unrecognised historical figures in the western world, but one which deserves to be told.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/Fm-yrZYmKfw?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The philosophy of Franz Kafka">

                <img src="../assets/videos/the-philosophy-of-franz-kafka/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">8:17</span>
            </div>
            <div class="meta">Keskesay · June 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=Fm-yrZYmKfw" target="_blank" rel="noopener">The philosophy of Franz Kafka</a></h2>
            <p class="blurb">In this video I am breaking down the philosophy of Franz Kafka by looking at the history of his life alongside my own views from my reading of his work.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/Tr8PmQLQWEQ?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The philosophy of Michael Jordan">

                <img src="../assets/videos/the-philosophy-of-michael-jordan/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">9:32</span>
            </div>
            <div class="meta">Keskesay · May 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=Tr8PmQLQWEQ" target="_blank" rel="noopener">The philosophy of Michael Jordan</a></h2>
            <p class="blurb">In this video I am exploring the mentality of Michael Jordan and the philosophy of how hard work can pay off.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/3zXytwPIECQ?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The philosophy of Martin Luther King; turn the other cheek">

                <img src="../assets/videos/the-philosophy-of-martin-luther-king-turn-the-other-cheek/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">5:12</span>
            </div>
            <div class="meta">Keskesay · May 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=3zXytwPIECQ" target="_blank" rel="noopener">The philosophy of Martin Luther King; turn the other cheek</a></h2>
            <p class="blurb">In this video I am exploring the parable of ‘turn the other cheek’ through how Martin Luther King acted, completely embodying that philosophy in the civil rights movement of the 1960s.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/tCYxwGOLSuI?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Ernest Hemingway journalism in fiction (Ernest Hemingway writing style)">

                <img src="../assets/videos/ernest-hemingway-journalism-in-fiction/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">11:13</span>
            </div>
            <div class="meta">Keskesay · April 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=tCYxwGOLSuI" target="_blank" rel="noopener">Ernest Hemingway journalism in fiction (Ernest Hemingway writing style)</a></h2>
            <p class="blurb">In this video I am exploring Ernest Hemingway’s writing style and how he brought the style dominated by his early journalism years to fiction.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/46MVHFXCLfg?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Abstract expressionism the art movement which changed the world">

                <img src="../assets/videos/abstract-expressionism-the-art-movement-which-changed-the-world/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">11:05</span>
            </div>
            <div class="meta">Keskesay · March 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=46MVHFXCLfg" target="_blank" rel="noopener">Abstract expressionism the art movement which changed the world</a></h2>
            <p class="blurb">In this video essay I am exploring how the art movement &#39;abstract expressionism&#39; changed the way people approach art and the world, breaking down the philosophy and history behind the movement and the artists who made it.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/ge5o1y-CqSY?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Hunter S. Thompson and the philosophy of gonzo journalism">

                <img src="../assets/videos/hunter-s-thompson-and-the-philosophy-of-gonzo-journalism/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">11:13</span>
            </div>
            <div class="meta">Keskesay · March 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=ge5o1y-CqSY" target="_blank" rel="noopener">Hunter S. Thompson and the philosophy of gonzo journalism</a></h2>
            <p class="blurb">In this video I am looking at Hunter S. Thompson&#39;s life and how he developed the gonzo style of writing, specifically in journalism, alongside the philosophy of gonzo journalism itself.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/YU4tr05FKMk?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The 27 club and the philosophy of a tortured artist">

                <img src="../assets/videos/the-27-club-and-the-philosophy-of-a-tortured-artist/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">5:35</span>
            </div>
            <div class="meta">Keskesay · February 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=YU4tr05FKMk" target="_blank" rel="noopener">The 27 club and the philosophy of a tortured artist</a></h2>
            <p class="blurb">In this video I am exploring the misunderstanding that to be a true artist or creator you have to have some kind of emotional conflict or mental problem which inspires your work, through the perspective of the 27 club and its romanticisation.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/InT9ufIzChc?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Charles Bukowski; The beauty of pessimism.">

                <img src="../assets/videos/charles-bukowski-the-beauty-of-pessimism/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">5:16</span>
            </div>
            <div class="meta">Keskesay · January 2021</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=InT9ufIzChc" target="_blank" rel="noopener">Charles Bukowski; The beauty of pessimism.</a></h2>
            <p class="blurb">In this video essay I am exploring the prolific writer that is Henry Charles Bukowski, delving into the philosophy of his work and life, or at least how I see it to be.</p>
        </article>
<article class="item" data-tags="books">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/kuFWdZNEVf8?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play The Philosophy of the Beat Generation.">

                <img src="../assets/videos/the-philosophy-of-the-beat-generation/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">9:51</span>
            </div>
            <div class="meta">Keskesay · December 2020</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=kuFWdZNEVf8" target="_blank" rel="noopener">The Philosophy of the Beat Generation.</a></h2>
            <p class="blurb">The Beat Generation is a literary movement which came to prominence in the 1950s with books such as &#39;Naked Lunch&#39; by William Burroughs and &#39;On The Road&#39; by Jack Kerouac becoming classics of American literature.</p>
        </article>
<article class="item" data-tags="film">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/p1PzXAPOyT8?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Midnight In Paris; A Philosophy Of A Generation">

                <img src="../assets/videos/midnight-in-paris-a-philosophy-of-a-generation/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">6:48</span>
            </div>
            <div class="meta">Keskesay · November 2020</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=p1PzXAPOyT8" target="_blank" rel="noopener">Midnight In Paris; A Philosophy Of A Generation</a></h2>
            <p class="blurb">In this video I&#39;m looking at how Woody Allen&#39;s Midnight in Paris showcases a philosophy of how to look on our generation and the ones of the past.</p>
        </article>
<article class="item" data-tags="film">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/Ya8iWqOmbNE?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Tenet A Lost Nolan.">

                <img src="../assets/videos/tenet-a-lost-nolan/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">5:48</span>
            </div>
            <div class="meta">Keskesay · November 2020</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=Ya8iWqOmbNE" target="_blank" rel="noopener">Tenet A Lost Nolan.</a></h2>
            <p class="blurb">In this video I am exploring Christopher Nolan&#39;s most recent movie Tenet and how I feel it compares to Stanley Kubrick&#39;s 2001: A Space Odyssey.</p>
        </article>
<article class="item" data-tags="philosophy">
            <div class="frame" data-embed="https://www.youtube-nocookie.com/embed/r9SCFlAateQ?autoplay=1&amp;rel=0" role="button" tabindex="0" aria-label="Play Robert Nozick&#39;s &#39;Experience Machine&#39;, Hedonism and its prevalence in modern society.">

                <img src="../assets/videos/robert-nozicks-experience-machine-hedonism-and-its-prevalence-in-modern-society/poster.jpg" alt="" loading="lazy" decoding="async">
                <span class="play"></span>
                <span class="dur">3:51</span>
            </div>
            <div class="meta">Keskesay · October 2020</div>
            <h2 class="title"><a href="https://www.youtube.com/watch?v=r9SCFlAateQ" target="_blank" rel="noopener">Robert Nozick&#39;s &#39;Experience Machine&#39;, Hedonism and its prevalence in modern society.</a></h2>
            <p class="blurb">In this essay I am looking into the links between modern societal advances in technology and their advancement into humanity&#39;s cognitive thought, and the link to the ethical thought of hedonism through the thought experiment of the experience machine.</p>
        </article>
    </div>
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
        <a href="https://www.youtube.com/channel/UC8wJrBxVPJrZTqmJ7fRLSlQ" target="_blank" rel="noopener" aria-label="YouTube">
            <svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
                <path d="M234 74a26 26 0 0 0 -18-18C199 51 128 51 128 51s-71 0-88 5a26 26 0 0 0 -18 18c-5 18-5 54-5 54s0 36 5 54a26 26 0 0 0 18 18c17 5 88 5 88 5s71 0 88-5a26 26 0 0 0 18-18c5-18 5-54 5-54s0-36-5-54Zm-129 87V95l56 33Z"/>
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

/* Filters + the facade swap. With JS off every plate still shows its poster
   and its title still links out to YouTube, so the page is a working index —
   it just doesn't play inline. */
(function () {
    var grid = document.getElementById('grid');
    if (!grid) return;
    var items = Array.prototype.slice.call(grid.querySelectorAll('.item'));
    var bar   = document.getElementById('filters');
    var none  = document.getElementById('none');
    var active = 'all';

    function matches(el) {
        return active === 'all' || (' ' + el.dataset.tags + ' ').indexOf(' ' + active + ' ') >= 0;
    }
    function setTag(tag) {
        active = tag;
        var shown = 0;
        items.forEach(function (it) {
            var ok = matches(it);
            it.hidden = !ok;
            if (ok) shown++;
        });
        if (none) none.hidden = shown > 0;
        if (history.replaceState) {
            history.replaceState(null, '', tag === 'all' ? location.pathname : '#' + tag);
        }
        if (bar) {
            Array.prototype.forEach.call(bar.querySelectorAll('.filter'), function (b) {
                b.classList.toggle('is-active', b.dataset.tag === tag);
            });
        }
    }

    if (bar) {
        bar.addEventListener('click', function (ev) {
            var b = ev.target.closest ? ev.target.closest('.filter') : null;
            if (b) setTag(b.dataset.tag);
        });
        function fromHash() {
            var h = (location.hash || '').replace('#', '');
            return bar.querySelector('.filter[data-tag="' + h + '"]') ? h : 'all';
        }
        window.addEventListener('hashchange', function () {
            var t = fromHash();
            if (t !== active) setTag(t);
        });
        setTag(fromHash());
    }

    /* Swap the poster for a real player, once, on demand. A frame that has
       already been swapped has no data-embed/data-file left, so a second
       click lands on the player itself and is left alone. */
    function play(frame) {
        var embed = frame.dataset.embed, file = frame.dataset.file;
        var node;
        if (embed) {
            node = document.createElement('iframe');
            node.src = embed;
            node.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            node.allowFullscreen = true;
            node.title = frame.getAttribute('aria-label') || 'Video';
        } else if (file) {
            node = document.createElement('video');
            node.src = file;
            node.controls = true;
            node.autoplay = true;
            node.playsInline = true;
            node.preload = 'metadata';
        } else {
            return;
        }
        delete frame.dataset.embed;
        delete frame.dataset.file;
        frame.innerHTML = '';
        frame.style.cursor = 'default';
        frame.removeAttribute('role');
        frame.removeAttribute('tabindex');
        frame.appendChild(node);
    }

    /* Silent hover preview, uploaded files only.
       Gated on (hover: hover) so a phone never starts fetching video because a
       thumb brushed a tile, and on reduced-motion because a looping clip is
       motion whatever its volume. Nothing is requested until the pointer
       actually arrives, so the page still costs one poster per plate. */
    var canHover = window.matchMedia &&
                   window.matchMedia('(hover: hover)').matches &&
                   !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (canHover) {
        Array.prototype.forEach.call(grid.querySelectorAll('.frame[data-file]'), function (f) {
            var prev = null;
            f.addEventListener('mouseenter', function () {
                if (!f.dataset.file) return;   // already swapped for the real player
                if (!prev) {
                    prev = document.createElement('video');
                    prev.src = f.dataset.file;
                    prev.muted = true; prev.loop = true;
                    prev.playsInline = true; prev.preload = 'metadata';
                    prev.className = 'preview';
                    f.appendChild(prev);
                }
                prev.play().catch(function () { /* refused — the poster stands */ });
            });
            f.addEventListener('mouseleave', function () {
                if (!prev) return;
                prev.pause();
                prev.currentTime = 0;          // next hover restarts, not resumes
            });
        });
    }

    grid.addEventListener('click', function (ev) {
        var f = ev.target.closest ? ev.target.closest('.frame') : null;
        if (f && (f.dataset.embed || f.dataset.file)) play(f);
    });
    grid.addEventListener('keydown', function (ev) {
        if (ev.key !== 'Enter' && ev.key !== ' ') return;
        var f = ev.target.closest ? ev.target.closest('.frame') : null;
        if (f && (f.dataset.embed || f.dataset.file)) { ev.preventDefault(); play(f); }
    });
})();
</script>
</html>