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
    background: var(--bg);
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
    flex-direction: column;
    gap: 14px;
    align-items: flex-end;
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

/* ── Page head ── */
.wrap {
    max-width: 940px;
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

/* ── Article cards — thumbnail left, title/meta right ── */
.grid { display: grid; gap: 0; }
.entry {
    display: grid;
    grid-template-columns: 200px 1fr;
    align-items: center;
    gap: 28px;
    padding: 28px 0;
    border-top: 2px solid var(--ink);
    transition: padding-left 0.2s ease;
}
.entry:last-of-type { border-bottom: 2px solid var(--ink); }
.entry:hover { padding-left: 12px; }

/* thumb keeps a fixed frame so ragged source aspect ratios still line up */
.entry .thumb {
    position: relative;
    aspect-ratio: 3 / 2;
    overflow: hidden;
    background: var(--paper);
    border: 2px solid var(--ink);
}
.entry .thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: grayscale(1) contrast(1.05);
    transition: filter 0.3s ease, transform 0.4s ease;
}
.entry:hover .thumb img { filter: grayscale(0); transform: scale(1.04); }
/* placeholder when a post has no image yet */
.entry .thumb.empty { border-style: dashed; opacity: 0.5; }

.entry .body { display: flex; flex-direction: column; gap: 8px; }
.entry .meta {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.entry .title {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(28px, 3.6vw, 46px);
    line-height: 0.94;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.entry:hover .title { color: var(--blue); }
.entry .more {
    margin-top: 2px;
    font-family: var(--body);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--blue);
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
.foot .foot-mail { color: var(--blue); }
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

/* texture on the remaining blue text — same treatment, clipped to glyphs.
   .social links are excluded: background-clip would paint a box behind the SVGs. */
.brand,
.top-nav a.active,
.eyebrow,
.entry .meta,
.entry .more,
.entry:hover .title,
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
.foot .foot-mail:hover { -webkit-text-fill-color: #fff; }

@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .top-nav { gap: 14px; font-size: 10px; letter-spacing: 0.12em; }
    .wrap { padding: 110px 22px 80px; }
    /* stack the card: thumb on top, text under */
    .entry { grid-template-columns: 1fr; gap: 16px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <nav class="top-nav">
        <a href="../about/">About</a>
        <a href="../writing/" class="active">Writing</a>
    </nav>
</header>

<section class="wrap">
    <div class="eyebrow">Selected Work</div>
    <h1>Writing</h1>

    <div class="grid">
        <a class="entry" href="https://www.clashmusic.com/live/live-report-the-black-lights/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-live-report-the-black-lights.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Live · Jul 2026</div>
                <div class="title">Live Report: The Black Lights</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/news/parisi-link-with-fred-again-on-this-is-real/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-parisi-link-with-fred-again-on-this-is-real.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · News · Jun 2026</div>
                <div class="title">PARISI Link With Fred again.. On ‘This Is Real (Disappear)’</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/live/the-cure-gorillaz-wolf-alice-for-phillgood-festival-2026/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-the-cure-gorillaz-wolf-alice-for-phillgood-festival-2026.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Live · Jun 2026</div>
                <div class="title">The Cure, Gorillaz, Wolf Alice For PHILLGOOD Festival 2026</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://thecoldmagazine.co.uk/khakikid-is-making-irish-rap-as-an-excuse-to-hang-out/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-khakikid-is-making-irish-rap-as-an-excuse-to-hang-out.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">The Cold Magazine · May 2026</div>
                <div class="title">KhakiKid Is Making Irish Rap ‘as an Excuse to Hang Out’</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://thecoldmagazine.co.uk/geese-psyop/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-the-geese-psyop-marks-the-death-of-indie.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">The Cold Magazine · May 2026</div>
                <div class="title">The Geese ‘Psyop’ Marks the Death of Indie</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://thecoldmagazine.co.uk/ruby-roberts/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-ruby-roberts-is-an-artist-of-dreamlike-spontaneity.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">The Cold Magazine · May 2026</div>
                <div class="title">Ruby Roberts Is an Artist of Dreamlike Spontaneity</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/live/thundercat-transforms-o2-academy-brixton-into-a-south-london-space-station/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-thundercat-transforms-o2-academy-brixton-into-a-south-london-space-station.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Live · Mar 2026</div>
                <div class="title">Thundercat Transforms O2 Academy Brixton Into a South London Space Station</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/reviews/ms-banks-south-ldn-lover-girl/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-ms-banks-south-ldn-lover-girl.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Review · Mar 2026</div>
                <div class="title">Ms Banks — SOUTH LDN LOVER GIRL</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://jackdennisonthompson.substack.com/p/jason-williamson-the-working-class" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-jason-williamson-the-working-class-hero-who-made-his-own-cage.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Substack · Mar 2026</div>
                <div class="title">Jason Williamson: The Working-Class Hero Who Made His Own Cage</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/reviews/moby-future-quiet/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-moby-future-quiet.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Review · Feb 2026</div>
                <div class="title">Moby — Future Quiet</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/features/audio-inception-26-artists-who-could-define-2026/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-audio-inception-26-artists-who-could-define-2026.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Feature · Feb 2026</div>
                <div class="title">Audio Inception: 26 Artists Who Could Define 2026</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/news/marlon-craft-shares-soulful-cut-analog-man/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-marlon-craft-shares-soulful-cut-analog-man.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · News · Feb 2026</div>
                <div class="title">Marlon Craft Shares Soulful Cut ‘Analog Man’</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/features/remember-me-chet-faker-interviewed/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-remember-me-chet-faker-interviewed.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Feature</div>
                <div class="title">Remember Me: Chet Faker Interviewed</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/next-wave/next-wave-1179-pollyfromthedirt/" target="_blank" rel="noopener">
            <div class="thumb"><img src="../assets/thumb-next-wave-1179-pollyfromthedirt.jpg" alt="" loading="lazy"></div>
            <div class="body">
                <div class="meta">Clash Music · Next Wave</div>
                <div class="title">Next Wave #1179: Pollyfromthedirt</div>
                <div class="more">Read Article &rarr;</div>
            </div>
        </a>
    </div>
</section>

<footer class="foot">
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
</html>