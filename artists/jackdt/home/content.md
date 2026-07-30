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

:root {
    --blue: #1a35ff;
    --blue-deep: #0a1ea8;
    --ink: #0b0d1a;
    --bg: #f4f3ee;
    --paper: #fbfaf6;
    --muted: #4a4d5c;
    --display: 'Bebas Neue', 'Barlow', sans-serif;
    --body: 'Barlow', sans-serif;
    --serif: 'Cardo', Georgia, 'Times New Roman', serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: var(--body);
    color: var(--ink);
    background-color: var(--bg);
    background-image: url('../assets/images/paper-texture.jpg');
    background-size: 620px auto;
    background-repeat: repeat;
    line-height: 1.5;
    font-weight: 400;
    overflow-x: hidden;
    opacity: 0;
    animation: pageIn 0.6s ease-out forwards;
}
@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

a { color: inherit; text-decoration: none; }

/* ── Slim masthead (top-left name + right-side vertical nav) ── */
.masthead {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 18px 32px;
    mix-blend-mode: difference;
    pointer-events: none;
}
.masthead a { pointer-events: auto; }

.brand {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(20px, 2.4vw, 32px);
    letter-spacing: 0.06em;
    line-height: 0.9;
    color: #fff;            /* difference blend turns it blue over paper */
    text-transform: uppercase;
    white-space: nowrap;
}

.top-nav {
    display: flex;
    flex-direction: column;
    gap: 18px;
    align-items: flex-end;
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #fff;
}
.top-nav a { position: relative; }
.top-nav a::after {
    content: '';
    position: absolute;
    right: 0; bottom: -4px;
    width: 0; height: 2px;
    background: currentColor;
    transition: width 0.25s ease;
}
.top-nav a:hover::after { width: 100%; }

/* ── Parallax stage ── */
.stage {
    position: relative;
    height: 100vh;
    overflow: hidden;
    background: var(--paper);
    display: flex;
    align-items: center;
    justify-content: flex-start;
}

/* photo background — TOP HALF of the source image (1071x2204 → show 0–50%) */
.stage-bg {
    position: absolute;
    top: -15%; left: 0; right: 0;   /* extra height centred so the drift never exposes an edge */
    height: 130%;               /* taller than viewport so parallax has room to drift */
    background-image: url('../assets/images/jack-hero-src.jpg');
    background-repeat: no-repeat;
    background-position: center top;   /* anchor to the top of the image */
    background-size: cover;
    will-change: transform;
}

/* white paper texture overlaid on the photo so it reads as printed-on-paper */
.stage-paper {
    position: absolute;
    inset: 0;
    background-color: rgba(244, 243, 238, 0.30);
    background-image: url('../assets/images/paper-texture.jpg');
    background-size: 620px auto;
    background-repeat: repeat;
    mix-blend-mode: screen;
    opacity: 0.78;
    pointer-events: none;
}

/* left-side legibility veil so the blue headline pops over the photo */
.stage-veil {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        rgba(244,243,238,0.85) 0%,
        rgba(244,243,238,0.55) 38%,
        rgba(244,243,238,0.10) 70%,
        rgba(244,243,238,0.0) 100%);
    pointer-events: none;
}

/* big blue magazine headline — left aligned */
.hero {
    position: relative;
    z-index: 2;
    text-align: left;
    will-change: transform;
    padding: 0 clamp(24px, 8vw, 120px);
    max-width: 1100px;
    margin-top: -180px;
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
.hero h1 .nm { display: block; }

/* textured blue glyphs — shared by the static "Jack" and the marquee name */
.hero h1 .nm,
.hero h1 .unit {
    color: var(--blue);
    background-image:
        linear-gradient(rgba(26, 53, 255, 0.65), rgba(26, 53, 255, 0.65)),
        url('../assets/intake/91aafc78_5.jpeg');
    background-size: cover, 80px auto;
    background-position: center;
    background-repeat: no-repeat, repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* marquee: DENNISON THOMPSON runs off the right and re-enters from the left.
   Breaks out of the hero's padding to span the full page width. */
.hero h1 .marquee {
    display: flex;
    align-items: center;       /* centre the stretched track in the taller box */
    height: 1.7em;             /* room for the doubled-height letters */
    width: 100vw;
    margin-left: calc(-1 * clamp(24px, 8vw, 120px));
    overflow: hidden;
}
.hero h1 .marquee__track {
    flex: none;                /* don't let flex shrink the overflowing track */
    display: inline-flex;
    align-items: baseline;
    width: max-content;
    white-space: nowrap;
    will-change: transform;
    transform-origin: center;
    transform: scaleY(1.7);      /* base so the doubled height holds if the animation is off */
    animation: nameMarquee 22s linear infinite;
}
.hero h1 .unit { padding-right: 0.34em; }
.hero h1 .sep {
    color: var(--blue);
    -webkit-text-fill-color: var(--blue);
    align-self: center;
    opacity: 0.6;
    padding-right: 0.34em;   /* unit's 0.34em on the left + this on the right = even spacing */
}
/* -50% == one identical half of the track → seamless loop.
   from -50% to 0 moves content rightward (out right, in from left). */
@keyframes nameMarquee {
    from { transform: translateX(-50%) scaleY(1.7); }   /* scaleY(1.7) = double height, held constant */
    to   { transform: translateX(0) scaleY(1.7); }
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

/* ── Editorial content ── */
.sheet {
    position: relative;
    z-index: 4;
    background: var(--bg);
    padding: clamp(70px, 12vh, 160px) 32px;
}
.col {
    max-width: 760px;
    margin: 0 auto;
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
.col p {
    font-family: var(--body);
    font-weight: 200;
    font-size: clamp(17px, 1.55vw, 20px);
    line-height: 1.72;
    color: #24272f;
    margin-bottom: 22px;
    max-width: 64ch;
}
.col p strong { color: var(--ink); font-weight: 700; }

.bylines {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 14px;
    margin-top: 40px;
}
.bylines span {
    font-family: var(--body);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--blue);
    border: 2px solid var(--blue);
    padding: 7px 14px;
    border-radius: 100px;
}

.cta {
    display: flex;
    gap: 18px;
    flex-wrap: wrap;
    margin-top: 48px;
}
.cta a {
    font-family: var(--body);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 16px 30px;
    border: 2px solid var(--blue);
    color: var(--blue);
    transition: background 0.2s ease, color 0.2s ease;
}
.cta a.solid { background: var(--blue); color: #fff; }
.cta a:hover { background: var(--blue-deep); border-color: var(--blue-deep); color: #fff; }

.foot {
    text-align: center;
    padding: 60px 32px;
    background: var(--ink);
    background-image: url('../assets/images/IMG_3062.jpeg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-blend-mode: multiply;
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
    background-image:
        linear-gradient(rgba(26, 53, 255, 0.65), rgba(26, 53, 255, 0.65)),
        url('../assets/intake/91aafc78_5.jpeg');
    background-size: cover, 200px auto;
    background-position: center;
    background-repeat: no-repeat, repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.foot .foot-mail:hover { color: #fff; }

/* ── Social marks (inline SVG — no CDN, no icon font) ── */
.social {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 30px;
}
.social a {
    display: inline-flex;
    width: 26px;
    height: 26px;
    color: rgba(255, 255, 255, 0.55);
    transition: color 0.2s ease, transform 0.2s ease;
}
.social a:hover { color: var(--blue); transform: translateY(-2px); }
.social svg { width: 100%; height: 100%; display: block; }

/* texture on the remaining (smaller) blue text — same treatment, clipped to glyphs.
   .social links are excluded: background-clip would paint a box behind the SVGs. */
.col .label,
.col .lede em,
.bylines span,
.cta a:not(.solid),
.foot .foot-mail {
    background-image:
        linear-gradient(rgba(26, 53, 255, 0.65), rgba(26, 53, 255, 0.65)),
        url('../assets/intake/91aafc78_5.jpeg');
    background-size: cover, 200px auto;
    background-position: center;
    background-repeat: no-repeat, repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
/* restore solid fill where blue text flips to white on hover */
.cta a:not(.solid):hover, .foot .foot-mail:hover { -webkit-text-fill-color: #fff; }

@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .top-nav { gap: 14px; font-size: 10px; letter-spacing: 0.12em; }
    .backdrop span { font-size: 90vw; }
    .sheet { padding: 70px 22px; }
}

@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .scroll-cue { animation: none; }
}
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <nav class="top-nav">
        <a href="../about/">About</a>
        <a href="../writing/">Writing</a>
    </nav>
</header>

<section class="stage">
    <div class="stage-bg" data-parallax="0.12"></div>
    <div class="stage-paper"></div>
    <div class="stage-veil"></div>
    <div class="hero" data-parallax="-0.12">
         <h1>
        <span class="nm">Jack</span>
        <span class="marquee" aria-label="Dennison Thompson">
            <span class="marquee__track" aria-hidden="true">
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
                <span class="unit">Dennison&nbsp;Thompson</span><span class="sep">&#8202;-&#8202;</span>
            </span>
        </span>
    </h1>
    </div>
</section>

<div class="sheet">
    <div class="col">
        <div class="label">The Byline</div>
        <div class="lede">Journalist &amp; <em>Culture</em> writer based in London.</div>
        <p><strong>Jack Dennison Thompson</strong> reports on music, politics, and the stories that sit between. An MA Magazine Journalism student at City, University of London, he writes features, reviews and interviews that put the people at the centre of the page.</p>
        <p>Currently a contributing writer at <strong>Clash Music Group</strong> and deputy multimedia editor at <strong>GTFO Magazine</strong>, with reported work for Maghrebi, Folk &amp; Honey, The Indiependent and Campaign UK.</p>

        <div class="bylines">
            <span>Clash Music</span>
            <span>GTFO Magazine</span>
            <span>Maghrebi</span>
            <span>Folk &amp; Honey</span>
            <span>The Indiependent</span>
            <span>Campaign UK</span>
        </div>

        <div class="cta" id="contact">
            <a href="../writing/" class="solid">Read the Writing</a>
            <a href="../about/">More About Jack</a>
        </div>
    </div>
</div>

<footer class="foot">
    <div class="big">Get in touch</div>
    <a class="foot-mail" href="mailto:jackdt26@outlook.com">Email Jack &rarr;</a>

    <div class="social">
        <a href="https://soundcloud.com/user-216694930" target="_blank" rel="noopener" aria-label="SoundCloud">
            <svg viewBox="0 0 256 256" fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <line x1="28" y1="150" x2="28" y2="182"/>
                <line x1="62" y1="128" x2="62" y2="182"/>
                <line x1="96" y1="112" x2="96" y2="182"/>
                <path d="M130 182V104a54 54 0 0 1 103 -16 42 42 0 0 1 -9 94 Z"/>
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
    </div>
</footer>

<script>
(function () {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var layers = [].slice.call(document.querySelectorAll('[data-parallax]'));
    if (reduce || !layers.length) return;

    var ticking = false;
    function update() {
        var y = window.pageYOffset || document.documentElement.scrollTop;
        for (var i = 0; i < layers.length; i++) {
            var speed = parseFloat(layers[i].getAttribute('data-parallax')) || 0;
            layers[i].style.transform = 'translate3d(0,' + (y * speed) + 'px,0)';
        }
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