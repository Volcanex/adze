<style>
@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant[wght].ttf') format('truetype');
    font-weight: 300 700;
    font-style: normal;
    font-display: swap;
}
@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant-Italic[wght].ttf') format('truetype');
    font-weight: 300 700;
    font-style: italic;
    font-display: swap;
}

:root {
    --primary: #000000;
    --bg: #ffffff;
    --accent: #0000ff;
    --paper: oklch(0.97 0.012 80);
    --ink-soft: #000000;
    --accent-wash: color-mix(in oklch, var(--accent) 12%, transparent);
    --hair: 1px;
}

::view-transition-old(root),
::view-transition-new(root) { animation-duration: 0.6s; }

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
    font-family: 'Cormorant', Georgia, serif;
    color: var(--primary);
    background: var(--bg);
    line-height: 0.88;
    font-size: 11pt;
    font-weight: 400;
    text-align: right;
    cursor: none;
    overflow-x: hidden;
}

a {
    color: var(--primary);
    text-decoration: none;
    transition: opacity 0.25s ease;
    cursor: none;
}
a:hover { opacity: 0.55; }

h1, h2, h3 { font-weight: 400; text-wrap: balance; }
p { text-wrap: pretty; }

/* Custom cursor — inherited Erlabrunn move */
.cursor {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--primary);
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
    transition: background-color 1.2s ease, border-radius 3.5s ease, width 0.4s ease, height 0.4s ease;
    mix-blend-mode: difference;
    filter: invert(1);
}
.cursor.clickable { background: var(--accent); border-radius: 0; width: 14px; height: 14px; }

/* --- HEADER --- */
.header {
    padding: 20px 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    color: var(--primary);
    background: transparent;
}
.header a { color: inherit; }
.logo { font-size: 11pt; letter-spacing: normal; color: var(--accent); }
.nav {
    display: flex;
    gap: 28px;
    font-size: 11pt;
    will-change: transform;
}
.nav.hidden { pointer-events: none; }

/* --- HERO --- */
.hero {
    min-height: 100vh;
    padding: 180px 60px 80px;
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    align-items: center;
}
.hero-headline {
    font-family: 'Cormorant', serif;
    font-size: clamp(20px, 3.19vw, 48px);
    line-height: 0.62;
    letter-spacing: normal;
    font-weight: 400;
}
.hero-headline em { color: inherit; font-style: normal; }
.hero-headline .u { color: var(--accent); font-style: italic; }

.lead-row {
    display: flex;
    align-items: stretch;
    gap: 18px;
}
.lead-row p { flex: 1; margin: 0; }

/* Desktop-only: first line of each body paragraph is squeezed to 20vw
   by a floated empty box on the left. Short paragraphs end up ragged,
   long paragraphs get a narrow hanging first line. Mobile is untouched. */
@media (min-width: 841px) {
    .hero-flow p::before,
    .studio-card p::before,
    .studio-outro p::before,
    .contact-body p::before,
    .manifesto p::before {
        content: '';
        float: left;
        width: calc(100% - 20vw);
        height: 1em;
    }
    /* Clive's bio is left-aligned, so flip the first-line squeeze to the right. */
    .studio-card.clive p::before {
        float: right;
    }
}

.lead-mark {
    /* Aspect ratio of the trimmed line-logo asset, so the visible artwork
       matches the paragraph height exactly (no PNG whitespace). */
    aspect-ratio: 1329 / 1723;
    align-self: stretch;
    flex-shrink: 0;
    background: url('../assets/images/logo-line.png') no-repeat center / contain;
}

.hero-flow {
    font-size: 11pt;
    line-height: 0.88;
    width: 72%;
    margin-left: auto;
    text-align: right;
}
/* --- HERO CURSOR-DRIFT --- */
.hero-headline {
    transition: transform 0.6s cubic-bezier(.2,.8,.2,1);
    will-change: transform;
}

/* --- PRETEXT (text reflows around cursor) --- */
.pt-block { position: relative; }
/* Force transparent on the element AND every descendant to defeat accent-color
   rules on <a>/<em>/<strong>/.coda and any inline style="color:...". */
.pt-block .pt-native,
.pt-block.pt-native { color: transparent !important; }
/* Descendants get transparent too — but EXCLUDE the pretext-injected
   .pt-layer (and the .pt-line elements inside it), since those carry
   the visible rendered text. Otherwise the rule would paint pretext's
   own output transparent and you'd see nothing. */
.pt-block .pt-native > *:not(.pt-layer),
.pt-block.pt-native > *:not(.pt-layer),
.pt-block .pt-native > *:not(.pt-layer) *,
.pt-block.pt-native > *:not(.pt-layer) * { color: transparent !important; }
.pt-block .pt-native ::selection,
.pt-block.pt-native ::selection { color: var(--primary); background: var(--accent-wash); }
.pt-layer { position: absolute; inset: 0; pointer-events: none; z-index: 2; }
.pt-line {
    position: absolute; top: 0; left: 0;
    white-space: pre; color: var(--primary); will-change: transform;
}
@media (prefers-reduced-motion: reduce) {
    .pt-block .pt-native { color: inherit; }
    .pt-layer { display: none; }
}

/* --- PAGE-WIDE FLOWER RAIN --- */
.flower-rain {
    position: fixed; inset: 0;
    pointer-events: none;
    z-index: 50;
    overflow: hidden;
}
.flower-rain img {
    position: absolute; top: 0; left: 0;
    will-change: transform;
    opacity: 0.55;
}
@media (prefers-reduced-motion: reduce) {
    .flower-rain { display: none; }
}

/* --- FLOATING BACKGROUND IMAGES --- */
.drift-layer { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.drift-layer img {
    position: absolute;
    opacity: 0;
    mix-blend-mode: multiply;
    transition: opacity 2.2s ease;
    will-change: transform, opacity;
}
.drift-layer img.in { opacity: var(--drift-opacity, 0.16); }

/* --- MANIFESTO --- */
.manifesto {
    padding: 160px 60px;
    position: relative;
    z-index: 2;
}
.manifesto .eyebrow {
    font-size: 11pt;
    letter-spacing: normal;
    color: var(--accent);
    margin-bottom: 32px;
}
.manifesto p {
    font-size: 11pt;
    line-height: 0.88;
    font-weight: 400;
    max-width: 24ch;
    margin-left: auto;
}
.manifesto p + p { margin-top: 28px; color: var(--ink-soft); }

/* --- WORK BAND (scroll-driven) --- */
.work { padding: 120px 0 200px; position: relative; z-index: 2; }
.work-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0 60px 48px;
}
.work-header h2 { font-size: 11pt; font-weight: 400; line-height: 0.88; }
.work-header .meta { font-size: 11pt; color: var(--ink-soft); letter-spacing: normal; }

.work-rail {
    display: flex;
    gap: 40px;
    padding: 0 60px;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
    animation: rail-drift linear;
    animation-timeline: view();
    animation-range: entry 0% cover 100%;
}
.work-rail.reverse {
    animation-name: rail-drift-reverse;
    margin-top: 32px;
}
.work-rail::-webkit-scrollbar { display: none; }

@keyframes rail-drift {
    from { transform: translateX(6%); }
    to   { transform: translateX(-6%); }
}
@keyframes rail-drift-reverse {
    from { transform: translateX(-6%); }
    to   { transform: translateX(6%); }
}

.tile {
    flex: 0 0 520px;
    scroll-snap-align: start;
    display: block;
    content-visibility: auto;
    contain-intrinsic-size: 520px 560px;
}
.tile-frame {
    width: 100%;
    /* JS sets --tile-aspect = RENDER_W / RENDER_H so tile aspect matches the
       full-page iframe (a tall poster ~4:5 on most desktops). */
    aspect-ratio: var(--tile-aspect, 4/5);
    overflow: hidden;
    background: var(--paper);
    position: relative;
}
.tile-frame img {
    width: 100%; height: 100%;
    object-fit: cover;
    transition: transform 1.2s cubic-bezier(.2,.8,.2,1), filter 1.2s ease;
    filter: saturate(0.9) contrast(1.02);
}
.tile:hover .tile-frame img { transform: scale(1.04); filter: saturate(1.1) contrast(1.05); }

/* Imageless tile (placeholder editorial card) */
.tile-frame.placeholder {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 28px 26px;
    background: var(--paper);
    transition: background 0.5s ease;
}
.tile:hover .tile-frame.placeholder { background: color-mix(in oklch, var(--paper) 85%, var(--accent-wash)); }
.tile-frame.placeholder .ph-num {
    font-size: 11pt;
    color: var(--accent);
    letter-spacing: normal;
    font-variant-numeric: tabular-nums;
}
.tile-frame.placeholder .ph-name {
    font-family: 'Cormorant', serif;
    font-size: 11pt;
    line-height: 0.88;
    font-weight: 300;
    margin-top: auto;
}
.tile-frame.placeholder .ph-host {
    font-size: 11pt;
    color: var(--ink-soft);
    letter-spacing: normal;
    margin-top: 10px;
}
.tile-frame.placeholder .ph-cta {
    font-size: 11pt;
    color: var(--accent);
    letter-spacing: normal;
    margin-top: 18px;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 0.4s ease, transform 0.4s ease;
}
.tile:hover .tile-frame.placeholder .ph-cta { opacity: 1; transform: translateY(0); }

/* The carousel slot is just an empty paper rectangle. The live iframe lives
   in a fixed-position container at body level (see below) and is positioned
   to overlay this slot — that way it escapes the carousel's transformed
   ancestor and can morph to fullscreen without being clipped by it. */
.tile-frame.live-slot {
    background: var(--paper);
}

/* --- CASE STUDY: a fixed-position iframe container morphs from the tile slot
       to fullscreen, with the bar dropping in on top. The iframe never moves
       in the DOM, so its document is preserved across the morph. --- */
:root { --case-bar-h: 60px; }

.live-iframe-container {
    position: fixed;
    z-index: 95;            /* above flowers (50), below header (100) */
    overflow: hidden;
    background: var(--paper);
    pointer-events: none;
    will-change: top, left, width, height;
    /* Cursor on the slot in the carousel still says "clickable" — the click
       is captured by the underlying tile <a>, since the container above is
       pointer-events:none in its tracking state. */
}
.live-iframe-container.morphing,
.live-iframe-container.expanded {
    transition: top 0.55s cubic-bezier(.2, .8, .2, 1),
                left 0.55s cubic-bezier(.2, .8, .2, 1),
                width 0.55s cubic-bezier(.2, .8, .2, 1),
                height 0.55s cubic-bezier(.2, .8, .2, 1);
}
/* Lift the morphing/expanded container above all the others (which sit at
   z-index 95 in their tile-tracking state) so it doesn't render under a
   sibling tile during the transition. */
.live-iframe-container.morphing { z-index: 201; }
.live-iframe-container.expanded {
    z-index: 202;            /* above the page, below the bar (203) */
    pointer-events: auto;
    overflow: auto;          /* let user scroll the tall iframe vertically */
    overscroll-behavior: contain;
}
.live-iframe-container > iframe {
    position: absolute; top: 0; left: 0;
    width: var(--render-w, 1920px);
    height: var(--render-h, 1080px);
    border: 0;
    transform-origin: 0 0;
    transform: translate(var(--x-offset, 0px), 0) scale(var(--scale, 0.22));
    background: var(--paper);
}
/* Animate transform (the scale) only during morph or when expanded — NOT
   during tile-tracking, where we need scroll-driven position updates to
   apply instantly without lag. */
.live-iframe-container.morphing > iframe,
.live-iframe-container.expanded > iframe {
    transition: transform 0.55s cubic-bezier(.2, .8, .2, 1);
}

.case-overlay { display: none; }

/* Native cursor while a case panel is open */
body.case-open { cursor: auto; }
body.case-open .cursor { display: none; }
body.case-open a, body.case-open button { cursor: pointer; }
.case-overlay { cursor: auto; }
.case-overlay a, .case-overlay button { cursor: pointer; }

.case-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: var(--case-bar-h);
    z-index: 203;
    padding: 0 28px;
    display: flex;
    align-items: center;
    gap: 24px;
    background: color-mix(in oklch, var(--bg) 85%, transparent);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid color-mix(in oklch, var(--primary) 8%, transparent);
    /* Drops in after the morph completes */
    transform: translateY(-100%);
    opacity: 0;
    transition: transform 0.4s 0.4s cubic-bezier(.2, .8, .2, 1),
                opacity   0.35s 0.45s ease;
}
body.case-open .case-bar { transform: translateY(0); opacity: 1; }
.case-back {
    background: none; border: 0; padding: 6px 0;
    font: inherit; color: var(--primary);
    font-size: 11pt; cursor: none;
}
.case-back:hover { opacity: 0.55; }
.case-meta { flex: 1; min-width: 0; }
.case-name { font-size: 11pt; font-family: 'Cormorant', serif; }
.case-url { font-size: 11pt; color: var(--ink-soft); letter-spacing: normal; }
.case-live {
    color: var(--accent);
    font-size: 11pt;
    border-bottom: 1px solid color-mix(in oklch, var(--accent) 40%, transparent);
    padding-bottom: 2px;
}
.tile-caption {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 14px;
    font-size: 11pt;
}
.tile-caption .n { color: var(--accent); font-variant-numeric: tabular-nums; }
.tile-caption .name { font-size: 11pt; }

/* --- STUDIO --- */
.studio {
    padding: 160px 60px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 100px 100px;
    position: relative;
    z-index: 2;
}
.studio-intro, .studio-outro { grid-column: 1 / -1; }
.studio-intro { margin-bottom: 40px; }
.studio-intro .eyebrow {
    font-size: 11pt;
    letter-spacing: normal;
    color: var(--accent);
    margin-bottom: 24px;
}
.studio-intro p {
    font-size: 11pt;
    line-height: 0.88;
    font-weight: 400;
    max-width: 32ch;
    margin-left: auto;
}
.studio-outro {
    margin-top: 80px;
}
.studio-outro p {
    font-size: 11pt;
    line-height: 0.88;
    color: var(--ink-soft);
    width: 72%;
    margin-left: auto;
    margin-bottom: 1.1em;
    text-align: right;
}
.studio-outro em { font-style: italic; color: var(--primary); }
.studio-outro .coda {
    font-style: italic;
    color: var(--primary);
    font-size: 11pt;
}
.studio-card { position: relative; }
.studio-card.john, .studio-card.clive { margin-top: 0; }
/* Mirror the Gabriel (right) card — image on the right, text right-aligned */
.studio-card.john { text-align: right; }
.studio-card.john .studio-portrait { margin-left: auto; margin-right: 0; }
.studio-card.john h3 .tag { right: auto; left: 0; }
.studio-card.john p { margin-left: auto; }
.studio-card.john .link-line a { border-bottom-color: color-mix(in oklch, var(--accent) 40%, transparent); }
/* Clive's card mirrors to the left edge: text and bio block both left-aligned. */
.studio-card.clive { text-align: left; }
.studio-card.clive p { margin-left: 0; margin-right: auto; text-align: left; }
.studio-card p { font-size: 11pt; line-height: 0.88; width: 72%; margin-left: auto; text-align: right; }
.studio-card p strong { font-weight: 400; color: var(--primary); }
.studio-card .link-line {
    margin-top: 14px;
    font-size: 11pt;
}
.studio-card .link-line a {
    color: var(--accent);
    border-bottom: 1px solid color-mix(in oklch, var(--accent) 40%, transparent);
}
.studio-portrait {
    width: 220px;
    max-width: 45%;
    aspect-ratio: 4/5;
    background: color-mix(in oklch, var(--primary) 12%, #ffffff);
    display: block;
}
img.studio-portrait {
    aspect-ratio: auto;
    height: auto;
    object-fit: fill;
    filter: saturate(0.9) contrast(1.02);
}
.studio-card h3 {
    font-size: 11pt;
    line-height: 0.88;
    margin: 24px 0 6px;
    position: relative;
}
.studio-card h3 .tag {
    position: absolute;
    top: -14px;
    right: 0;
    font-size: 11pt;
    letter-spacing: normal;
    color: var(--accent);
}
.studio-card p { color: var(--ink-soft); }
.studio-card p em { color: var(--primary); font-style: italic; }

/* --- CONTACT --- */
.contact {
    padding: 180px 60px 120px;
    text-align: right;
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 40% 1fr;
    gap: 60px;
    align-items: center;
}
.contact-mark { display: block; }
.contact-mark img { width: 100%; height: auto; display: block; }
.contact-body > * { margin-left: auto; }
.contact h2 {
    font-size: 11pt;
    line-height: 0.88;
    font-weight: 400;
    letter-spacing: normal;
}
.contact h2 em { color: var(--accent); }
.contact a.email {
    display: inline-block;
    margin-top: 40px;
    font-size: 11pt;
    border-bottom: var(--hair) solid var(--primary);
    padding-bottom: 4px;
}

/* --- FOOTER --- */
.footer {
    padding: 28px 60px 48px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    font-size: 11pt;
    color: var(--ink-soft);
    gap: 40px;
    position: relative;
    z-index: 2;
    text-align: left;
}
.footer .clock {
    font-variant-numeric: tabular-nums;
    letter-spacing: normal;
    transform: scaleX(0.92);
    transform-origin: left;
}

/* --- MOBILE --- */
@media (max-width: 840px) {
    body { cursor: auto; font-size: 11pt; }
    .cursor { display: none; }
    a, .tile, button { cursor: pointer; }
    .header { padding: 24px; }
    .nav { gap: 18px; font-size: 11pt; }
    .hero { padding: 120px 24px 60px; grid-template-columns: 1fr; gap: 40px; min-height: auto; }
    .flower.big { width: 160px; } .flower.med { width: 120px; } .flower.small { width: 90px; }
    .manifesto { padding: 80px 24px; }
    .work-header, .work-rail { padding-left: 24px; padding-right: 24px; }
    .tile { flex-basis: 75vw; }
    .studio { padding: 80px 24px; grid-template-columns: 1fr; gap: 60px; }
    .studio-card.john, .studio-card.clive { margin-top: 0; }
    .studio-outro { margin-top: 40px; }
    .contact { padding: 100px 24px 60px; grid-template-columns: 1fr; gap: 32px; }
    .footer { padding: 24px; flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>

<html>
<div class="cursor" id="cursor"></div>
<div class="drift-layer" id="drift"></div>
<div class="flower-rain" id="flower-rain" aria-hidden="true"></div>

<header class="header">
    <a href="./" class="logo">Last Place</a>
    <nav class="nav">
        <a href="#work">Work</a>
        <a href="#studio">About</a>
        <a href="#contact">Contact</a>
    </nav>
</header>

<main>
    <section class="hero">
        <h1 class="hero-headline">
            Websites for <span class="u">artists</span>,<br>
            musicians, and <em>cultural projects</em>.<br>
            Made once, made properly.
        </h1>

        <div class="hero-flow pt-block">
            <div class="lead-row">
                <span class="lead-mark" aria-hidden="true"></span>
                <p>Last Place is a small studio making websites for people whose work deserves more than a template. We do it the old way, one at a time. Each site is designed by hand and checked by hand. Then we hand over the domain and the keys. We keep hosting it, for free, forever (unless you get really famous, at which point we'll have a nice conversation).</p>
            </div>
            <p>You pay once and the code is yours.</p>
        </div>
    </section>

    <section class="manifesto pt-block">
        <div class="eyebrow">Service</div>
        <p>A one-of-one site, designed around your work. Your own domain, to keep. A simple dashboard to tend it, when you want to. One payment. No roof caving in.</p>
    </section>

    <section class="work" id="work">
        <div class="work-header">
            <h2>Recent work</h2>
            <div class="meta">2024 — 2026</div>
        </div>

        <div class="work-rail" id="rail">
            <a href="?case=maria" class="tile" data-slug="maria">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Maria Slaughter</span><span class="n">11 2025</span></div>
            </a>
            <a href="?case=nina" class="tile" data-slug="nina">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Nina Sere</span><span class="n">04 2026</span></div>
            </a>
            <a href="?case=erlabrunn" class="tile" data-slug="erlabrunn">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Erlabrunn</span><span class="n">02 2026</span></div>
            </a>
        </div>

        <div class="work-rail reverse" id="rail-2">
            <a href="?case=keskesay" class="tile" data-slug="keskesay">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Keskesay</span><span class="n">— Jack DT</span></div>
            </a>
            <a href="?case=morty" class="tile" data-slug="morty">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Morty</span><span class="n">— mortaghh.com</span></div>
            </a>
            <a href="?case=harry" class="tile" data-slug="harry">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Harry Hudson</span><span class="n">— harryhudson.com</span></div>
            </a>
            <a href="?case=oli" class="tile" data-slug="oli">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Oli Edgar</span><span class="n">— oliedgar.com</span></div>
            </a>
            <a href="?case=seb" class="tile" data-slug="seb">
                <div class="tile-frame live-slot"></div>
                <div class="tile-caption"><span class="name">Seb Baron</span><span class="n">— sebbaron.com</span></div>
            </a>
        </div>
    </section>

    <section class="studio" id="studio">
        <div class="studio-intro pt-block">
            <div class="eyebrow">About</div>
            <p>Last Place is one designer and one engineer.</p>
        </div>

        <article class="studio-card clive">
            <img class="studio-portrait" src="../assets/images/WhatsApp_Image_2026-04-22_at_13.09.49.jpeg" alt="Clive Burgess">
            <h3>Clive Burgess <span class="tag">The Design</span></h3>
            <p class="pt-block"><strong>Clive Burgess</strong> (b. 2002) is an artist, director and designer working between many mediums. He studied Architecture at The Bartlett School of Architecture, UCL (2021–2024). Alongside Last Place he co-runs <em>Erlabrunn</em>, a young London publishing imprint focussed on exhibitions, books, illustration, artist residencies, platforming emerging writers and handbinding, with his sister Nell. His practice and freelance work spans visual communication, model making, metalworking and drawing. He brings the eye, the hands and the patience.</p>
            <p class="link-line"><a href="https://erlabrunn.org.uk" target="_blank" rel="noopener">erlabrunn.org.uk →</a></p>
        </article>

        <article class="studio-card john">
            <img class="studio-portrait" src="../assets/images/61O_1323-4.jpg" alt="Gabriel Penman">
            <h3>Gabriel Penman <span class="tag">The Build</span></h3>
            <p class="pt-block"><strong>Gabriel Penman</strong> (b. 2002) is a developer and machine learning engineer currently based in Saigon. He's completing an MSc in Artificial Intelligence at the University of Huddersfield, and is Lead Developer at <em>Baseline Labs</em>, an Irish AI startup. He considers his study of AI something like the Dark Arts in Harry Potter — useful, dangerous, faintly embarrassing to admit in polite company — and finds the use of AI for creative outlets pretty abhorrent. Specialising in autonomic infrastructure has its benefits, though, and it means your website runs very cleanly.</p>
            <p class="link-line"><a href="https://gabrielpenman.com" target="_blank" rel="noopener">gabrielpenman.com →</a></p>
        </article>

        <div class="studio-outro">
            <p class="pt-block">We first met at <em>UCL Tree Soc</em> in 2022. A society Clive ran, ostensibly about trees, it's now proof that Gabriel does sometimes go outside. We've been working together one way or another since then.</p>
            <p class="coda pt-block">There will eventually be a Wozniak vs. Jobs moment, but as of now both Steves are getting on well.</p>
        </div>
    </section>

    <section class="contact" id="contact">
        <div class="contact-mark">
            <img src="../assets/images/Artboard_24x.png" alt="Last Place">
        </div>
        <div class="contact-body">
            <h2>Tell us about <em>your site</em>.</h2>
            <p class="pt-block" style="margin-top:28px; color: var(--ink-soft);">Send us a sentence about your practice and a link to your work, we'll get back to you within a week.</p>
            <a class="email" href="mailto:hello@lastplace.co.uk">hello@lastplace.co.uk</a>
        </div>
    </section>

    <footer class="footer">
        <div>Last Place, London</div>
        <div class="clock" id="clock">—</div>
        <div>© <span id="year"></span> Last Place. Made by two humans.</div>
    </footer>
</main>

<div class="case-overlay" id="case" hidden aria-hidden="true"></div>
<header class="case-bar" id="case-bar">
    <button class="case-back" type="button" aria-label="Back to recent work">← back</button>
    <div class="case-meta">
        <div class="case-name"></div>
        <div class="case-url"></div>
    </div>
    <a class="case-live" href="#" target="_blank" rel="noopener">Open live ↗</a>
</header>

<script>
const cursor = document.getElementById('cursor');
document.addEventListener('mousemove', e => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top  = e.clientY + 'px';
});
document.querySelectorAll('a, .tile, button').forEach(el => {
    el.addEventListener('mouseenter', () => cursor.classList.add('clickable'));
    el.addEventListener('mouseleave', () => cursor.classList.remove('clickable'));
});

const drift = document.getElementById('drift');
const pool = [
    '../assets/images/Roots_2_cropped.jpg',
    '../assets/images/Root_Sectionv2.jpeg',
    '../assets/images/hieracium-minus-coloring-page-original.png',
    '../assets/images/betonica-altilis-coloring-page-lg.png',
    '../assets/images/images20.jpg',
    '../assets/images/images7.jpg',
    '../assets/images/images30.jpg',
    '../assets/images/images8.jpg',
    '../assets/images/images10.jpg',
    '../assets/images/botanical/Abies_balsamea_drawing.png',
    '../assets/images/botanical/Abies_fraseri_drawing.png',
    '../assets/images/botanical/Abronia_fragrans_drawing.png',
    '../assets/images/botanical/Abutilon_theophrasti_BB-1913.png',
    '../assets/images/botanical/Abutilon_theophrasti_drawing.png',
    '../assets/images/botanical/Acacia_angustissima_drawing.png',
    '../assets/images/botanical/Acalypha_gracilens_drawing.png',
    '../assets/images/botanical/Acalypha_ostryifolia_drawing.png',
    '../assets/images/botanical/Acalypha_virginica_drawing.png',
    '../assets/images/botanical/Acanthospermum_australe_drawing.png',
    '../assets/images/botanical/Acer_glabrum_BB-1913.png',
    '../assets/images/botanical/Acer_glabrum_drawing.png',
    '../assets/images/botanical/Acer_negundo_drawing.png',
    '../assets/images/botanical/Acer_nigrum_BB-1913.png',
    '../assets/images/botanical/Acer_nigrum_drawing.png',
    '../assets/images/botanical/Acer_pensylvanicum_BB-1913.png',
    '../assets/images/botanical/Acer_pensylvanicum_drawing.png',
    '../assets/images/botanical/Acer_rubrum_drawing.png',
    '../assets/images/botanical/Acer_rubrum_drummondii_drawing.png',
    '../assets/images/botanical/Acer_rubrum_rubrum_drawing.png',
    '../assets/images/botanical/Acer_rubrum_trilobum_drawing.png',
    '../assets/images/botanical/Acer_saccharinum_drawing.png',
    '../assets/images/botanical/Acer_saccharum_drawing.png',
    '../assets/images/botanical/Acer_spicatum_drawing.png',
    '../assets/images/botanical/Achillea_millefolium_borealis_drawing.png',
    '../assets/images/botanical/Achillea_millefolium_drawing.png',
    '../assets/images/botanical/Achillea_millefolium_occidentalis_drawing.png',
    '../assets/images/botanical/Achillea_ptarmica_drawing.png',
    '../assets/images/botanical/Achnatherum_hymenoides_BB-1913.png',
    '../assets/images/botanical/Aconitum_noveboracense_BB-1913.png'
];
const picks = pool.sort(() => 0.5 - Math.random()).slice(0, 7);
// Divide viewport into 7 non-overlapping cells so images don't stack.
// Each cell is a top/left % range; the actual position within is random.
const cells = [
    { top: [4, 16],   left: [4, 16]   },  // top-left
    { top: [6, 18],   left: [78, 88]  },  // top-right
    { top: [30, 42],  left: [2, 12]   },  // middle-left
    { top: [34, 46],  left: [44, 56]  },  // middle-centre
    { top: [28, 40],  left: [82, 92]  },  // middle-right
    { top: [66, 78],  left: [20, 32]  },  // lower-left-mid
    { top: [70, 82],  left: [68, 80]  }   // lower-right-mid
].sort(() => 0.5 - Math.random());
picks.forEach((src, i) => {
    const img = new Image();
    img.src = src;
    const w = 90 + Math.random() * 70; // smaller: 90–160px
    const cell = cells[i];
    img.style.width = w + 'px';
    img.style.top   = (cell.top[0]  + Math.random() * (cell.top[1]  - cell.top[0]))  + '%';
    img.style.left  = (cell.left[0] + Math.random() * (cell.left[1] - cell.left[0])) + '%';
    img.style.transitionDelay = (i * 0.3) + 's';
    // Per-image random target opacity between 0.10 and 0.16.
    img.style.setProperty('--drift-opacity', (0.10 + Math.random() * 0.06).toFixed(3));
    drift.appendChild(img);
    requestAnimationFrame(() => setTimeout(() => img.classList.add('in'), 200 + i * 350));
});

const navEl = document.querySelector('.nav');
let _lastScrollY = window.scrollY;
let _navOffset = 0;            // 0 = at rest position; negative = pushed up
let _navHideAt = 0;            // computed lazily after nav has laid out
const HEADER_HIDE_THRESHOLD = 80;
window.addEventListener('scroll', () => {
    const y = window.scrollY;
    const dy = y - _lastScrollY;
    _lastScrollY = y;
    drift.querySelectorAll('img').forEach((img, i) => {
        const rate = 0.04 + (i % 3) * 0.02;
        img.style.transform = `translateY(${-y * rate}px)`;
    });
    if (navEl) {
        if (!_navHideAt) _navHideAt = navEl.offsetHeight + 40; // clear the header padding
        if (y < HEADER_HIDE_THRESHOLD) {
            // Near top — always pinned visible.
            _navOffset = 0;
        } else {
            // Move 1:1 with scroll. Down → push up; up → pull down.
            _navOffset -= dy;
            if (_navOffset > 0) _navOffset = 0;
            if (_navOffset < -_navHideAt) _navOffset = -_navHideAt;
        }
        navEl.style.transform = `translateY(${_navOffset}px)`;
        navEl.classList.toggle('hidden', _navOffset <= -_navHideAt);
    }
}, { passive: true });

// ---- Live iframe containers (one per case with an embeddable site) ----
// Each container is fixed-positioned at body level. Default: it tracks the
// position of its tile slot in the carousel. On case-open it animates to
// fullscreen and back. The iframe inside never moves in the DOM, so its
// loaded document persists across the morph.
const BAR_H_INIT = 60;
// Fixed 1920×1080 (standard HD). Gives consistent 16:9 widescreen tiles
// regardless of the user's viewport, and the panel renders the embedded
// site at native HD — letterboxes naturally on narrower viewports and
// fits cleanly on 1920+ screens. No portrait-tile surprises.
const RENDER_W = 1920;
const RENDER_H = 1080;
document.documentElement.style.setProperty('--tile-aspect',
    (RENDER_W / RENDER_H).toFixed(4));
const liveContainers = {};

function buildLiveContainer(slug, embedUrl, name) {
    const c = document.createElement('div');
    c.className = 'live-iframe-container';
    c.dataset.slug = slug;
    const f = document.createElement('iframe');
    f.src = embedUrl;
    f.title = name + ' preview';
    f.tabIndex = -1;
    f.setAttribute('aria-hidden', 'true');
    f.style.setProperty('--render-w', RENDER_W + 'px');
    f.style.setProperty('--render-h', RENDER_H + 'px');
    f.addEventListener('load', () => {
        try {
            const doc = f.contentDocument;
            if (!doc) return;
            const s = doc.createElement('style');
            s.textContent = 'html{scrollbar-width:none}html::-webkit-scrollbar{display:none;width:0;height:0}';
            doc.documentElement.appendChild(s);
        } catch {} // cross-origin iframe; nothing we can do from here
    });
    c.appendChild(f);
    document.body.appendChild(c);
    liveContainers[slug] = c;
    return c;
}

function slotFor(slug) {
    return document.querySelector(`.tile[data-slug="${slug}"] .tile-frame.live-slot`);
}

function setRect(el, r, transition = false) {
    if (!transition) el.style.transition = 'none';
    el.style.top    = r.top    + 'px';
    el.style.left   = r.left   + 'px';
    el.style.width  = r.width  + 'px';
    el.style.height = r.height + 'px';
    const iframe = el.querySelector('iframe');
    if (iframe) {
        // Cover-fit: pick the larger axis scale so the iframe always fills the
        // slot. Excess width/height is clipped by the container's overflow:hidden.
        // Centered horizontally; top-aligned (so the site's header stays visible).
        const scale = Math.max(r.width / RENDER_W, r.height / RENDER_H);
        const xOffset = (r.width - RENDER_W * scale) / 2;
        iframe.style.setProperty('--scale', scale.toFixed(4));
        iframe.style.setProperty('--x-offset', xOffset.toFixed(2) + 'px');
    }
    if (!transition) {
        void el.offsetHeight;
        el.style.transition = '';
    }
}

function trackContainersToTiles() {
    for (const slug in liveContainers) {
        const c = liveContainers[slug];
        if (c.classList.contains('morphing') || c.classList.contains('expanded')) continue;
        const slot = slotFor(slug);
        if (!slot) continue;
        const r = slot.getBoundingClientRect();
        if (r.width <= 0) continue;
        setRect(c, r, false);
    }
}

// ---- Case study routing (View Transitions + history) ----
const CASES = {
    maria: {
        name: 'Maria Slaughter',
        live: 'https://mariaslaughter.online/home/',
        embed: 'https://adze.studio/preview/mariaslaughter/home/',
    },
    nina: {
        name: 'Nina Sere',
        live: 'https://ninasere.com',
        embed: 'https://adze.studio/preview/nina/home/',
    },
    erlabrunn: {
        name: 'Erlabrunn',
        live: 'https://erlabrunn.org.uk',
        embed: 'https://adze.studio/preview/cliveburgess/home/',
    },
    keskesay: {
        name: 'Keskesay',
        live: 'https://jackdt.com',
        embed: 'https://adze.studio/preview/jackdt/home/',
    },
    morty: {
        name: 'Morty',
        live: 'https://mortaghh.com',
        embed: 'https://adze.studio/preview/mortaghh/home/',
    },
    harry: {
        name: 'Harry Hudson',
        live: 'https://harryhudson.com',
        embed: 'https://adze.studio/preview/harryhudson/home/',
    },
    oli: {
        name: 'Oli Edgar',
        live: 'https://oliedgar.com',
        embed: 'https://adze.studio/preview/oliedgar/home/',
    },
    seb: {
        name: 'Seb Baron',
        live: 'https://sebbaron.com',
        embed: 'https://adze.studio/preview/sebbaron/home/',
    },
};

// In dashboard preview the document lives in about:srcdoc, where pushState
// throws SecurityError. Detect and skip URL updates in that context.
const CAN_PUSH_STATE = (() => {
    try { history.replaceState(history.state, ''); return true; }
    catch { return false; }
})();
function safePush(state, url)    { if (CAN_PUSH_STATE) try { history.pushState(state, '', url); } catch {} }
function safeReplace(state, url) { if (CAN_PUSH_STATE) try { history.replaceState(state, '', url); } catch {} }

const caseEl   = document.getElementById('case');
const caseBar  = document.getElementById('case-bar');
const caseName = caseBar.querySelector('.case-name');
const caseUrl  = caseBar.querySelector('.case-url');
const caseLive = caseBar.querySelector('.case-live');
const caseBack = caseBar.querySelector('.case-back');

let activeSlug = null;

function paint(slug) {
    const c = CASES[slug];
    caseName.textContent = c.name;
    caseUrl.textContent  = c.live;
    caseLive.href        = c.live;
    caseEl.hidden = false;
    caseEl.setAttribute('aria-hidden', 'false');
}

function hidePanel() {
    caseEl.hidden = true;
    caseEl.setAttribute('aria-hidden', 'true');
}

const BAR_H = 60;

// Build a live container per case that has a real same-origin embed URL.
for (const slug in CASES) {
    const c = CASES[slug];
    if (c.embed && c.embed.includes('/preview/')) buildLiveContainer(slug, c.embed, c.name);
}
trackContainersToTiles();

// Keep containers glued to their tiles as the page / carousel scrolls.
window.addEventListener('scroll',  trackContainersToTiles, { passive: true });
window.addEventListener('resize',  trackContainersToTiles);
document.querySelectorAll('.work-rail').forEach(r =>
    r.addEventListener('scroll', trackContainersToTiles, { passive: true })
);

function morphOpen(slug) {
    const c = liveContainers[slug];
    if (!c) return;
    paint(slug);

    // Snap to current tile rect (no transition), then enable transition and
    // animate to fullscreen-below-bar. ResizeObserver semantics aren't
    // involved — we set --scale explicitly via setRect each step.
    const slot = slotFor(slug);
    if (slot) setRect(c, slot.getBoundingClientRect(), false);

    // Single-step morph: container expands to fill the viewport while the
    // iframe simultaneously scales to fit-content and translates to centered.
    // Both animate over the same 0.55s.
    const fullW = window.innerWidth;
    const panelH = window.innerHeight - BAR_H;
    const fitWidthScale   = Math.min(1, fullW / RENDER_W);
    const fitContentScale = Math.min(fitWidthScale, panelH / RENDER_H);
    const centerOffset    = Math.max(0, (fullW - RENDER_W * fitContentScale) / 2);

    c.classList.add('morphing');
    requestAnimationFrame(() => {
        c.style.top    = BAR_H + 'px';
        c.style.left   = '0px';
        c.style.width  = fullW + 'px';
        c.style.height = panelH + 'px';
        const iframe = c.querySelector('iframe');
        iframe.style.setProperty('--scale', fitContentScale.toFixed(4));
        iframe.style.setProperty('--x-offset', centerOffset.toFixed(2) + 'px');
    });
    const onEnd = (e) => {
        if (e.target !== c || e.propertyName !== 'width') return;
        c.removeEventListener('transitionend', onEnd);
        c.classList.remove('morphing');
        c.classList.add('expanded');
    };
    c.addEventListener('transitionend', onEnd);
}

function morphClose(slug) {
    const c = liveContainers[slug];
    if (!c) { hidePanel(); return; }
    const slot = slotFor(slug);
    if (!slot) { hidePanel(); return; }
    const iframe = c.querySelector('iframe');
    const r = slot.getBoundingClientRect();

    // Single-step reverse: container shrinks to the tile slot while the
    // iframe simultaneously scales/translates back to its tile-tracking state.
    c.classList.remove('expanded');
    c.classList.add('morphing');
    requestAnimationFrame(() => {
        c.style.top    = r.top    + 'px';
        c.style.left   = r.left   + 'px';
        c.style.width  = r.width  + 'px';
        c.style.height = r.height + 'px';
        // Match setRect's cover-fit logic for the tile state.
        const tileScale = Math.max(r.width / RENDER_W, r.height / RENDER_H);
        const tileOffset = (r.width - RENDER_W * tileScale) / 2;
        iframe.style.setProperty('--scale', tileScale.toFixed(4));
        iframe.style.setProperty('--x-offset', tileOffset.toFixed(2) + 'px');
    });
    const onEnd = (e) => {
        if (e.target !== c || e.propertyName !== 'width') return;
        c.removeEventListener('transitionend', onEnd);
        c.classList.remove('morphing');
        trackContainersToTiles();
        hidePanel();
    };
    c.addEventListener('transitionend', onEnd);
}

function openCase(slug, push = true) {
    if (!CASES[slug] || activeSlug === slug) return;
    if (push) safePush({ case: slug }, `?case=${slug}`);
    morphOpen(slug);
    activeSlug = slug;
    document.body.style.overflow = 'hidden';
    document.body.classList.add('case-open');
}

function closeCase(push = true) {
    if (!activeSlug) return;
    const slug = activeSlug;
    activeSlug = null;
    if (push) safePush({}, location.pathname);
    document.body.style.overflow = '';
    document.body.classList.remove('case-open');
    morphClose(slug);
}

document.querySelectorAll('.tile[data-slug]').forEach(t => {
    t.addEventListener('click', e => {
        // Allow modifier-clicks (open in new tab) to behave normally
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
        const slug = t.dataset.slug;
        // Only morph if we have a same-origin embeddable container; otherwise
        // open the live site in a new tab.
        if (!liveContainers[slug]) {
            if (CASES[slug] && CASES[slug].live) {
                window.open(CASES[slug].live, '_blank', 'noopener');
                e.preventDefault();
            }
            return;
        }
        e.preventDefault();
        openCase(slug);
    });
});
caseBack.addEventListener('click', () => CAN_PUSH_STATE ? history.back() : closeCase(false));
window.addEventListener('keydown', e => {
    if (e.key === 'Escape' && activeSlug) {
        if (CAN_PUSH_STATE) history.back(); else closeCase(false);
    }
});
window.addEventListener('popstate', e => {
    const slug = (e.state && e.state.case) ||
                 new URL(location.href).searchParams.get('case');
    if (slug && CASES[slug]) {
        if (slug !== activeSlug) {
            // Open without pushing (we got here via back/forward)
            if (activeSlug) {
                // back/forward jumped between two cases — close the current
                // and open the new one once its morph slot is free
                closeCase(false);
                setTimeout(() => openCase(slug, false), 600);
            } else {
                openCase(slug, false);
            }
        }
    } else if (activeSlug) {
        closeCase(false);
    }
});

// Honour ?case= on initial load (skipped in about:srcdoc, where there's no URL)
if (CAN_PUSH_STATE) {
    const initial = new URL(location.href).searchParams.get('case');
    if (initial && CASES[initial]) {
        safeReplace({ case: initial }, `?case=${initial}`);
        openCase(initial, false);
    }
}

// (flower-rain + hero drift live in the ES module below)

function pad(n){ return String(n).padStart(2,'0'); }
function tick() {
    const d = new Date();
    const updated = new Date(2026, 3, 22);
    const diffMs = d - updated;
    const diffDays = Math.floor(diffMs / 86400000);
    let rel = diffDays < 1 ? 'updated today' :
              diffDays === 1 ? 'updated yesterday' :
              diffDays < 30 ? `updated ${diffDays} days ago` :
              `updated ${Math.floor(diffDays/30.44)} months ago`;
    document.getElementById('clock').textContent =
        `${pad(d.getHours())} : ${pad(d.getMinutes())}  ·  ${rel}`;
}
tick(); setInterval(tick, 30000);
document.getElementById('year').textContent = new Date().getFullYear();
</script>

<script type="module">
import { prepareWithSegments, layoutNextLine } from '../assets/js/pretext.js';

// ---- Flower sprite pipeline (atlas → chroma-keyed PNG blobs) ----
async function loadFlowerSprites() {
    const atlas = await new Promise((res, rej) => {
        const im = new Image();
        im.crossOrigin = 'anonymous';
        im.onload = () => res(im);
        im.onerror = rej;
        im.src = '../assets/images/flowers2.png';
    });
    const COLS = 12, ROWS = 7;
    const off = document.createElement('canvas');
    off.width = atlas.naturalWidth;
    off.height = atlas.naturalHeight;
    const octx = off.getContext('2d');
    octx.drawImage(atlas, 0, 0);
    const img = octx.getImageData(0, 0, off.width, off.height);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
        const r = d[i], g = d[i+1], b = d[i+2];
        const m = Math.min(r, g, b);
        if (m >= 228) d[i+3] = 0;
        else if (m >= 185) d[i+3] = Math.round(d[i+3] * (1 - (m - 185) / 43));
    }
    octx.putImageData(img, 0, 0);
    const cw = Math.floor(off.width / COLS);
    const ch = Math.floor(off.height / ROWS);
    const urls = [];
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const tile = document.createElement('canvas');
            tile.width = cw; tile.height = ch;
            tile.getContext('2d').drawImage(off, c*cw, r*ch, cw, ch, 0, 0, cw, ch);
            const url = await new Promise(res => tile.toBlob(b => res(URL.createObjectURL(b)), 'image/png'));
            urls.push(url);
        }
    }
    return urls;
}

// ---- Shared pointer state (viewport coords) ----
const pointer = { x: -9999, y: -9999, active: false };
window.addEventListener('mousemove', e => {
    pointer.x = e.clientX;
    pointer.y = e.clientY;
    pointer.active = true;
}, { passive: true });
window.addEventListener('mouseleave', () => { pointer.active = false; });

// ---- Page-wide ambient flower rain (fixed overlay, mouse-repelling) ----
// Module-scope so the pretext-wrap loop can read flower positions as text obstacles.
const rainFlowers = [];

function initRain(spriteUrls) {
    const container = document.getElementById('flower-rain');
    if (!container) return;
    const pickSprite = () => spriteUrls[Math.floor(Math.random() * spriteUrls.length)];

    let vw = window.innerWidth, vh = window.innerHeight;
    const N = 6;
    const REPEL_R = 140, REPEL_K = 450; // px radius, accel scale (gentle)
    const flowers = rainFlowers;
    for (let i = 0; i < N; i++) {
        const size = 56 + Math.random() * 38;
        const el = document.createElement('img');
        el.src = pickSprite();
        el.style.width = size + 'px';
        el.style.height = size + 'px';
        container.appendChild(el);
        flowers.push({
            el, size,
            x: Math.random() * vw,
            y: Math.random() * vh - vh,
            baseVy: 14 + Math.random() * 14,
            vx: (Math.random() - 0.5) * 6,
            vy: 14,
            sway: Math.random() * Math.PI * 2,
            swaySpeed: 0.3 + Math.random() * 0.5,
            rot: Math.random() * 360,
            rotSpeed: (Math.random() - 0.5) * 24,
        });
    }

    window.addEventListener('resize', () => {
        vw = window.innerWidth;
        vh = window.innerHeight;
    });

    // Cache the drift-layer image elements; recompute their rects each frame
    // (scroll parallax moves them via transform, so the rect changes too).
    let driftEls = [];
    const refreshDriftEls = () => { driftEls = Array.from(document.querySelectorAll('.drift-layer img')); };
    refreshDriftEls();
    // Also refresh after the fade-in stagger completes, in case images were
    // appended after this initRain call ran.
    setTimeout(refreshDriftEls, 4000);

    let last = performance.now();
    function frame(now) {
        const dt = Math.min((now - last) / 1000, 0.05);
        last = now;

        // Snapshot the drift-image obstacles once per frame.
        const obstacles = [];
        for (const el of driftEls) {
            const r = el.getBoundingClientRect();
            if (r.width <= 0) continue;
            obstacles.push({
                cx: r.left + r.width / 2,
                cy: r.top  + r.height / 2,
                // Effective repel radius = the image's own half-extent + a soft halo.
                radius: Math.max(r.width, r.height) / 2 + REPEL_R * 0.6,
            });
        }

        for (const f of flowers) {
            // Cursor repulsion
            if (pointer.active) {
                const dx = f.x - pointer.x;
                const dy = f.y - pointer.y;
                const dist = Math.hypot(dx, dy);
                if (dist > 0 && dist < REPEL_R) {
                    const force = (1 - dist / REPEL_R) * REPEL_K;
                    f.vx += (dx / dist) * force * dt;
                    f.vy += (dy / dist) * force * dt;
                }
            }
            // Drift-illustration repulsion
            for (const o of obstacles) {
                const dx = f.x - o.cx;
                const dy = f.y - o.cy;
                const dist = Math.hypot(dx, dy);
                if (dist > 0 && dist < o.radius) {
                    const force = (1 - dist / o.radius) * REPEL_K * 0.7;
                    f.vx += (dx / dist) * force * dt;
                    f.vy += (dy / dist) * force * dt;
                }
            }
            // Damping back toward drift
            const damp = Math.pow(0.5, dt * 1.2);
            f.vx *= damp;
            f.vy = f.vy * damp + f.baseVy * (1 - damp);

            f.sway += f.swaySpeed * dt;
            f.x += (f.vx + Math.sin(f.sway) * 5) * dt;
            f.y += f.vy * dt;
            f.rot += f.rotSpeed * dt;

            if (f.y - f.size > vh) {
                f.y = -f.size - Math.random() * 120;
                f.x = Math.random() * vw;
                f.vy = f.baseVy;
            }
            if (f.x < -f.size) f.x = vw + f.size;
            else if (f.x > vw + f.size) f.x = -f.size;

            f.el.style.transform =
                `translate3d(${f.x - f.size/2}px, ${f.y - f.size/2}px, 0) rotate(${f.rot}deg)`;
        }
        requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
}

// ---- Hero text drift (cursor parallax on headline + body) ----
function initHeroDrift() {
    const targets = [].filter(t => t.el);
    if (!targets.length) return;

    let tx = 0, ty = 0;
    const cur = targets.map(() => ({ x: 0, y: 0 }));

    window.addEventListener('mousemove', e => {
        tx = (e.clientX / window.innerWidth)  - 0.5;
        ty = (e.clientY / window.innerHeight) - 0.5;
    }, { passive: true });

    function frame() {
        for (let i = 0; i < targets.length; i++) {
            const t = targets[i], c = cur[i];
            c.x += (tx * t.strength - c.x) * 0.08;
            c.y += (ty * t.strength - c.y) * 0.08;
            t.el.style.transform = `translate3d(${c.x}px, ${c.y}px, 0)`;
        }
        requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
}

// ---- Pretext that wraps around the cursor ----
const MIN_SLOT = 40;
function carveSlots(base, blocked) {
    let slots = [base];
    for (const iv of blocked) {
        const next = [];
        for (const s of slots) {
            if (iv.right <= s.left || iv.left >= s.right) { next.push(s); continue; }
            if (iv.left  > s.left)  next.push({ left: s.left, right: iv.left });
            if (iv.right < s.right) next.push({ left: iv.right, right: s.right });
        }
        slots = next;
    }
    return slots.filter(s => s.right - s.left >= MIN_SLOT);
}
function circleBand(cx, cy, r, top, bottom, hPad) {
    const minDy = cy >= top && cy <= bottom ? 0 : cy < top ? top - cy : cy - bottom;
    if (minDy >= r) return null;
    const dx = Math.sqrt(r*r - minDy*minDy);
    return { left: cx - dx - hPad, right: cx + dx + hPad };
}

function layoutPara(p, obstacles) {
    const lines = [];
    const { prepared, lineHeight, width, xOffset, yOffset, heightCap } = p;
    let cur = { segmentIndex: 0, graphemeIndex: 0 };
    let top = yOffset;
    const base = { left: xOffset, right: xOffset + width };
    let guard = 0;
    while (top + lineHeight <= yOffset + heightCap && guard++ < 400) {
        const blocked = [];
        for (const o of obstacles) {
            const iv = circleBand(o.x, o.y, o.r, top, top + lineHeight, 8);
            if (iv) blocked.push(iv);
        }
        const slots = carveSlots(base, blocked).sort((a, b) => a.left - b.left);
        if (!slots.length) { top += lineHeight; continue; }
        let exhausted = false;
        for (const slot of slots) {
            const line = layoutNextLine(prepared, cur, slot.right - slot.left);
            if (!line) { exhausted = true; break; }
            lines.push({ x: slot.left, y: top, text: line.text });
            cur = line.end;
        }
        if (exhausted) break;
        top += lineHeight;
    }
    return lines;
}

function splitByBr(el) {
    const html = el.innerHTML;
    if (!/<br/i.test(html)) {
        const t = el.textContent.trim();
        return t ? [t] : [];
    }
    return html.split(/<br\s*\/?>/i)
        .map(s => s.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim())
        .filter(Boolean);
}

async function initCursorWrap() {
    await document.fonts.ready;
    const blocks = [];
    for (const block of document.querySelectorAll('.pt-block')) {
        // pt-block can wrap text elements OR be set directly on a single
        // <p>/<h*> (in which case treat that one as the text target).
        const els = block.matches('p, h1, h2, h3, h4')
            ? [block]
            : [...block.querySelectorAll('p, h1, h2, h3')];
        if (!els.length) continue;
        const blockRect = block.getBoundingClientRect();
        const pInfos = [];
        for (const el of els) {
            const cs = getComputedStyle(el);
            const color = cs.color;
            const font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
            const lineHeight = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
            const elRect = el.getBoundingClientRect();
            const xOffset = elRect.left - blockRect.left;
            const yBase   = elRect.top  - blockRect.top;
            const width   = el.clientWidth;

            const lines = splitByBr(el);
            if (!lines.length) continue;
            el.classList.add('pt-native');

            if (lines.length === 1) {
                // Single block of text: let it flow on multiple wrapped lines
                const prepared = prepareWithSegments(lines[0], font);
                const heightCap = Math.max(elRect.height * 1.5, lineHeight * 2);
                pInfos.push({ el, prepared, lineHeight, font, width, xOffset, yOffset: yBase, heightCap, color });
            } else {
                // Author-broken lines (<br>): one pInfo per line, each one-line tall
                for (let i = 0; i < lines.length; i++) {
                    const prepared = prepareWithSegments(lines[i], font);
                    pInfos.push({
                        el, prepared, lineHeight, font, width, xOffset,
                        yOffset: yBase + i * lineHeight,
                        heightCap: lineHeight,
                        color,
                    });
                }
            }
        }
        if (!pInfos.length) continue;
        const layer = document.createElement('div');
        layer.className = 'pt-layer';
        layer.setAttribute('aria-hidden', 'true');
        block.appendChild(layer);
        blocks.push({ block, pInfos, layer, linePool: [] });
    }
    if (!blocks.length) return;

    const FLOWER_R_FACTOR = 0.30; // visible flower covers ~60% of its bbox
    function frame() {
        for (const b of blocks) {
            const rect = b.block.getBoundingClientRect();
            const obstacles = [];
            // Falling flowers (viewport coords → block-local) push text aside.
            for (const f of rainFlowers) {
                const r = f.size * FLOWER_R_FACTOR;
                const fx = f.x - rect.left;
                const fy = f.y - rect.top;
                if (fx > -r && fx < rect.width + r &&
                    fy > -r && fy < rect.height + r) {
                    obstacles.push({ x: fx, y: fy, r });
                }
            }

            const hasObstacle = obstacles.length > 0;
            // Skip relayout if nothing changed: cursor outside this block AND we already
            // painted the rest state.
            if (!hasObstacle && b.atRest) continue;
            b.atRest = !hasObstacle;

            const allLines = [];
            for (const p of b.pInfos) {
                const lines = layoutPara(p, obstacles);
                for (const ln of lines) allLines.push({ ...ln, color: p.color, font: p.font });
            }

            while (b.linePool.length < allLines.length) {
                const el = document.createElement('div');
                el.className = 'pt-line';
                b.layer.appendChild(el);
                b.linePool.push(el);
            }
            for (let i = 0; i < b.linePool.length; i++) {
                const el = b.linePool[i];
                if (i >= allLines.length) { el.style.display = 'none'; continue; }
                const ln = allLines[i];
                if (el.style.display === 'none') el.style.display = '';
                if (el._text !== ln.text) { el.textContent = ln.text; el._text = ln.text; }
                if (el._font !== ln.font) { el.style.font = ln.font; el._font = ln.font; }
                if (el._color !== ln.color) { el.style.color = ln.color; el._color = ln.color; }
                el.style.transform = `translate3d(${ln.x}px, ${ln.y}px, 0)`;
            }
        }
        requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => location.reload(), 300);
    });
}

if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    initHeroDrift();
    loadFlowerSprites()
        .then(initRain)
        .catch(err => console.error('[flowers]', err));
}

// ---- Adaptive justify: justify paragraphs with > 3 lines; the last line
//      preserves the element's original alignment (right → right, left → left).
function adaptiveJustify() {
    document.querySelectorAll('p').forEach(p => {
        // Clear any prior inline alignment so we measure the natural wrapping
        // and read the true cascaded alignment.
        p.style.textAlign = '';
        p.style.textAlignLast = '';
        const cs = getComputedStyle(p);
        const baseAlign = cs.textAlign;
        const fs = parseFloat(cs.fontSize);
        const lhStr = cs.lineHeight;
        let lh;
        if (lhStr === 'normal')        lh = fs * 1.2;
        else if (lhStr.endsWith('px')) lh = parseFloat(lhStr);
        else                           lh = parseFloat(lhStr) * fs; // unitless multiplier
        const lines = Math.round(p.getBoundingClientRect().height / lh);
        if (lines > 3) {
            p.style.textAlign = 'justify';
            // Bottom line follows the element's natural alignment.
            p.style.textAlignLast =
                  (baseAlign === 'right'  || baseAlign === 'end')   ? 'right'
                : (baseAlign === 'center')                          ? 'center'
                :                                                     'left';
        }
    });
}

if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(adaptiveJustify);
} else {
    window.addEventListener('load', adaptiveJustify);
}
let _ajTimer;
window.addEventListener('resize', () => {
    clearTimeout(_ajTimer);
    _ajTimer = setTimeout(adaptiveJustify, 150);
});
</script>
</html>