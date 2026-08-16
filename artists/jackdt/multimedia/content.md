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
    max-width: 1000px;
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

/* ── Pieces ──
   This section is the catch-all, so unlike the photo wall and the video grid
   it cannot assume one shape per item: a piece might be three photographs, or
   one audio file, or a PDF, or a Spotify embed. So each piece is a block in a
   single column and the media inside it lays itself out — a row of images if
   there are several, full width if there is one. The 2px rule above each
   piece is the same device the writing index used to use for its rows. */
.piece {
    padding-top: 34px;
    margin-top: 34px;
    border-top: 2px solid var(--ink);
}
.piece:first-child { border-top: 0; margin-top: 0; padding-top: 0; }
.piece[hidden] { display: none; }

.piece .when {
    font-family: var(--body);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.piece h2 {
    margin-top: 6px;
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(28px, 4vw, 54px);
    line-height: 0.92;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.piece .body {
    margin-top: 12px;
    max-width: 620px;
    font-family: var(--body);
    font-weight: 200;
    font-size: 16px;
    line-height: 1.6;
    color: var(--muted);
    text-align: justify;
    hyphens: auto;
}

.media { margin-top: 22px; display: flex; flex-direction: column; gap: 16px; }

/* Several pictures sit side by side and share the width; one picture takes it
   all. `flex-basis: 0` with grow means the row divides evenly regardless of
   how differently shaped the frames are. */
.shots { display: flex; flex-wrap: wrap; gap: 12px; }
.shots a { flex: 1 1 0; min-width: 220px; display: block; }
.shots img { width: 100%; height: auto; display: block; background: var(--paper); }
.shots a:hover img { opacity: 0.88; }

.media video {
    width: 100%;
    display: block;
    background: #000;
    aspect-ratio: 16 / 9;
}
.media audio { width: 100%; display: block; }

/* A PDF or anything else that has no player: a named row that reads as a
   deliberate object rather than a bare blue link. */
.filecard {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border: 2px solid var(--ink);
    background: var(--paper);
    transition: background var(--t-hover), color var(--t-hover);
}
.filecard:hover { background: var(--ink); color: var(--bg); }
.filecard .kind {
    font-family: var(--display);
    font-size: 22px;
    line-height: 1;
    letter-spacing: 0.06em;
    color: var(--blue);
}
.filecard:hover .kind { color: var(--bg); }
.filecard .fname {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Embeds keep their own aspect: 16:9 for video hosts, a short bar for audio
   hosts, because a SoundCloud player in a 16:9 box is mostly empty space. */
.embed { width: 100%; border: 0; display: block; }
.embed.video { aspect-ratio: 16 / 9; }
.embed.audio { height: 166px; }

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

@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .wrap { padding: 110px 22px 80px; }
    .shots a { min-width: 100%; }
    .piece .body { text-align: left; }
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
        <a href="../video/">Video</a>
        <a href="../multimedia/" class="active">Multimedia</a>
    </nav>
</header>



<section class="wrap">
    <div class="eyebrow" data-copy="eyebrow">Selected Work</div>
    <h1>Multimedia</h1>

    <nav class="filters" id="filters" aria-label="Filter multimedia by subject">
        <button type="button" class="filter is-active" data-tag="all">All<span class="n">1</span></button>
        <button type="button" class="filter" data-tag="art">art<span class="n">1</span></button>
        <button type="button" class="filter" data-tag="design">design<span class="n">1</span></button>
    </nav>


    <div id="pieces">
<article class="piece" data-tags="art design">
            <h2>Digital Painting</h2>

            <div class="media">
                <div class="shots">
                    <a href="../assets/multimedia/draft-bf783d1f/IMG_0923.PNG" target="_blank" rel="noopener"><img src="../assets/multimedia/draft-bf783d1f/IMG_0923.display.PNG" style="aspect-ratio: 1.0" alt="IMG_0923.PNG" loading="lazy" decoding="async"></a>
                </div>

            </div>
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

/* Filters only. Every piece and every player is in the HTML server-side, so
   with JS off the page is complete — this just hides the ones that don't
   match the chosen tag. */
(function () {
    var host = document.getElementById('pieces');
    if (!host) return;
    var pieces = Array.prototype.slice.call(host.querySelectorAll('.piece'));
    var bar    = document.getElementById('filters');
    var none   = document.getElementById('none');
    var active = 'all';

    function matches(el) {
        return active === 'all' || (' ' + el.dataset.tags + ' ').indexOf(' ' + active + ' ') >= 0;
    }
    function setTag(tag) {
        active = tag;
        var shown = 0;
        pieces.forEach(function (p) {
            var ok = matches(p);
            p.hidden = !ok;
            if (ok) shown++;
        });
        if (none) none.hidden = shown > 0;
        if (history.replaceState) {
            history.replaceState(null, '', tag === 'all' ? location.pathname : '#' + tag);
        }
        Array.prototype.forEach.call(bar.querySelectorAll('.filter'), function (b) {
            b.classList.toggle('is-active', b.dataset.tag === tag);
        });
    }
    if (!bar) return;
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
})();
</script>
</html>