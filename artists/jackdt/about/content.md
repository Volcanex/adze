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

/* ── Article body ── */
.wrap {
    max-width: 760px;
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
    margin-bottom: 40px;
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
h2 {
    font-family: var(--display);
    font-weight: 400;
    color: var(--ink);
    line-height: 0.9;
    letter-spacing: 0.015em;
    text-transform: uppercase;
    font-size: clamp(28px, 4vw, 46px);
    margin: 56px 0 24px;
}
p {
    font-family: var(--body);
    font-weight: 200;
    font-size: clamp(17px, 1.55vw, 20px);
    line-height: 1.78;
    color: #24272f;
    margin-bottom: 22px;
    max-width: 66ch;
}
p strong { color: var(--ink); font-weight: 700; }
p a { color: var(--blue); font-weight: 700; border-bottom: 2px solid rgba(26,53,255,0.3); }
p a:hover { border-bottom-color: var(--blue); }

/* standfirst — larger serif italic, classic feature opener */
.lede {
    font-family: var(--body);
    font-weight: 200;
    font-style: italic;
    font-size: clamp(21px, 2.2vw, 28px);
    color: var(--ink);
    line-height: 1.5;
    max-width: 60ch;
}
.lede strong { font-style: normal; }

ul.exp {
    list-style: none;
    margin-top: 8px;
}
ul.exp li {
    font-family: var(--body);
    font-weight: 200;
    font-size: clamp(17px, 1.55vw, 20px);
    line-height: 1.5;
    color: #24272f;
    padding: 18px 0;
    border-top: 1px solid rgba(11,13,26,0.12);
}
ul.exp li strong { color: var(--ink); font-weight: 700; }

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
p a,
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
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <nav class="top-nav">
        <a href="../about/" class="active">About</a>
        <a href="../writing/">Writing</a>
    </nav>
</header>

<article class="wrap">
    <div class="eyebrow">About</div>
    <h1>About<br>Jack</h1>

    <p class="lede"><strong>MA Magazine Journalism student at City, University of London</strong>, with a passion for storytelling across music, culture, and current affairs.</p>

    <p>I have hands-on experience at <a href="https://maghrebi.org" target="_blank">maghrebi.org</a>, where I reported on North African current events under award-winning journalist Martin Jay, and through music journalism for The Indiependent and Folk and Honey, where I wrote reviews, features and interviews.</p>

    <p>My work spans news reporting, cultural features, and music journalism — from covering political developments to profiling emerging artists. I'm particularly interested in stories that sit at the intersection of culture, politics, and community.</p>

    <h2>Experience</h2>
    <ul class="exp">
        <li><strong>Contributing Writer</strong> &mdash; Clash Music Group</li>
        <li><strong>Deputy Multimedia Editor</strong> &mdash; GTFO Magazine</li>
        <li><strong>News Intern</strong> &mdash; Campaign UK</li>
        <li><strong>Contributor</strong> &mdash; Maghrebi.org, Folk &amp; Honey, The Indiependent</li>
    </ul>
</article>

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
