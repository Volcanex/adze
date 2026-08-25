<style>
/* CSS here */
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
.contact a.whatsapp {
    display: inline-block;
    margin-top: 32px;
    font-family: 'Cormorant', serif;
    font-style: italic;
    font-size: clamp(22px, 3.8vw, 56px);
    line-height: 0.9;
    color: var(--accent);
    border-bottom: 1px solid color-mix(in oklch, var(--accent) 40%, transparent);
    padding-bottom: 6px;
}
.contact a.whatsapp:hover { opacity: 0.7; }

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

/* Contact form improvements */
.contact-form {
    display: flex;
    flex-direction: column;
    gap: 24px; /* Increased gap for a lighter feel */
    margin-top: 40px;
    max-width: 480px;
    margin-left: auto;
    text-align: left;
}

.contact-form label {
    font-size: 10pt;
    color: var(--ink-soft);
    margin-bottom: 4px;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.contact-form input[type="text"],
.contact-form input[type="email"],
.contact-form textarea {
    width: 100%;
    padding: 8px 4px; /* Adjusted padding for underline style */
    border: none; /* Remove all borders */
    border-bottom: 1px solid var(--ink-soft); /* Add underline */
    border-radius: 0; /* Remove rounded corners */
    background-color: transparent; /* No background */
    color: var(--primary);
    font-family: 'Cormorant', Georgia, serif;
    font-size: 11pt;
    line-height: 1.4;
    transition: border-color 0.3s ease;
}

.contact-form input[type="text"]:focus,
.contact-form input[type="email"]:focus,
.contact-form textarea:focus {
    border-bottom-color: var(--primary); /* Darken underline on focus */
    outline: none;
}

.contact-form textarea {
    resize: vertical;
    min-height: 120px;
}

.contact-form button {
    background: none;
    color: var(--primary);
    padding: 10px 0;
    border: none;
    border-bottom: var(--hair) solid var(--primary); /* Use site's hair-line border */
    font-size: 11pt;
    cursor: pointer;
    transition: border-color 0.3s ease, color 0.3s ease, opacity 0.3s ease; /* Subtle transitions */
    align-self: flex-end;
    margin-top: 20px; /* More space above button */
    text-transform: uppercase; /* Match labels */
    letter-spacing: 0.05em; /* Match labels */
    font-family: 'Cormorant', Georgia, serif; /* Ensure consistent font */
}

.contact-form button:hover {
    color: var(--accent); /* Accent color on hover */
    border-color: var(--accent); /* Accent color border on hover */
    opacity: 0.8; /* Slight opacity change */
}

/* Mobile adjustments for contact form */
@media (max-width: 840px) {
    .contact-form {
        max-width: 100%;
        margin-right: auto;
    }
    .contact-form button {
        align-self: stretch;
    }
}
</style>

<html>
<div class="cursor" id="cursor"></div>
<div class="drift-layer" id="drift"></div>
<div class="flower-rain" id="flower-rain" aria-hidden="true"></div>

<header class="header">
    <a href="./" class="logo">Last Place</a>
    <nav class="nav">
        <a href="../home/#work">Work</a>
        <a href="../home/#studio">About</a>
        <a href="./">Contact</a>
    </nav>
</header>

<main>
    <section class="contact" id="contact">
        <div class="contact-mark">
            <img src="../assets/images/Artboard_24x.png" alt="Last Place">
        </div>
        <div class="contact-body">
            <h2>Tell us about <em>your site</em>.</h2>
            <p class="pt-block" style="margin-top:28px; color: var(--ink-soft);">Send us a sentence about your practice and a link to your work, we'll get back to you within a week.</p>
            <a class="whatsapp" href="https://wa.me/447341316804" target="_blank" rel="noopener">WhatsApp&nbsp;&nbsp;+44 7341 316804</a>

            <form class="contact-form" action="/api/adze/contact" method="POST">
                <input type="hidden" name="artist_slug" value="lastplacesite">
                <div>
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div>
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div>
                    <label for="subject">Subject</label>
                    <input type="text" id="subject" name="subject">
                </div>
                <div>
                    <label for="message">Message</label>
                    <textarea id="message" name="message" required></textarea>
                </div>
                <button type="submit">Send Message</button>
            </form>
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
    '../assets/images/botanical/Abronia_fragrans_drawing.png'
];
</script>
</html>