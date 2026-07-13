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

/* ── Article cards ── */
.grid { display: grid; gap: 0; }
.entry {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 36px 0;
    border-top: 2px solid var(--ink);
    transition: padding-left 0.2s ease;
}
.entry:last-of-type { border-bottom: 2px solid var(--ink); }
.entry:hover { padding-left: 12px; }
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
    font-size: clamp(30px, 5vw, 58px);
    line-height: 0.92;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.entry:hover .title { color: var(--blue); }
.entry .excerpt {
    font-family: var(--body);
    font-weight: 200;
    font-size: clamp(16px, 1.45vw, 19px);
    line-height: 1.7;
    color: #24272f;
    max-width: 64ch;
    margin-top: 6px;
}
.entry .more {
    margin-top: 6px;
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
.foot a { color: var(--blue); }
.foot a:hover { color: #fff; }

/* texture on the remaining blue text — same treatment, clipped to glyphs */
.brand,
.top-nav a.active,
.eyebrow,
.entry .meta,
.entry .more,
.entry:hover .title,
.foot a {
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
.foot a:hover { -webkit-text-fill-color: #fff; }

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
        <a href="../about/">About</a>
        <a href="../writing/" class="active">Writing</a>
        <a href="../music/">Music</a>
    </nav>
</header>

<section class="wrap">
    <div class="eyebrow">Selected Work</div>
    <h1>Writing</h1>

    <div class="grid">
        <a class="entry" href="https://thecoldmagazine.co.uk/khakikid-is-making-irish-rap-as-an-excuse-to-hang-out/" target="_blank" rel="noopener">
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">KhakiKid Is Making Irish Rap ‘as an Excuse to Hang Out’</div>
            <p class="excerpt">The Irish-Libyan rapper treats music as an excuse to hang out — prizing collaboration and creative freedom over the commercial machine.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://thecoldmagazine.co.uk/geese-psyop/" target="_blank" rel="noopener">
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">The Geese ‘Psyop’ Marks the Death of Indie</div>
            <p class="excerpt">The outrage over Geese’s manufactured rise lays bare a deeper anxiety: indie authenticity dying in the streaming era’s algorithm-driven industry.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://thecoldmagazine.co.uk/ruby-roberts/" target="_blank" rel="noopener">
            <div class="meta">The Cold Magazine · May 2026</div>
            <div class="title">Ruby Roberts Is an Artist of Dreamlike Spontaneity</div>
            <p class="excerpt">The Somerset alt-pop singer builds fluid, genre-defying songs out of spontaneous late-night jam sessions and an ever-shifting sense of self.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/live/thundercat-transforms-o2-academy-brixton-into-a-south-london-space-station/" target="_blank" rel="noopener">
            <div class="meta">Clash Music · Live · Mar 2026</div>
            <div class="title">Thundercat Transforms O2 Academy Brixton Into a South London Space Station</div>
            <p class="excerpt">A futuristic, avant-garde Thundercat turns Brixton into an interstellar nightclub — funkadelic, six-string bass in hand, too unearthly for any normal stage.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/reviews/ms-banks-south-ldn-lover-girl/" target="_blank" rel="noopener">
            <div class="meta">Clash Music · Review · Mar 2026</div>
            <div class="title">Ms Banks — SOUTH LDN LOVER GIRL</div>
            <p class="excerpt">The debut balances feel-good anthems with a bracing origin story — Afrobeats, rap and R&amp;B from a true voice of the streets.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://jackdennisonthompson.substack.com/p/jason-williamson-the-working-class" target="_blank" rel="noopener">
            <div class="meta">Substack · Mar 2026</div>
            <div class="title">Jason Williamson: The Working-Class Hero Who Made His Own Cage</div>
            <p class="excerpt">The sober Sleaford Mods frontman on how his working-class roots shaped his music — and his reluctant, controversial political identity.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/reviews/moby-future-quiet/" target="_blank" rel="noopener">
            <div class="meta">Clash Music · Review · Feb 2026</div>
            <div class="title">Moby — Future Quiet</div>
            <p class="excerpt">An album of ambient-piano therapy — a rescue from insomnia and anxiety, offered to the world by one of electronic music’s great producers.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/features/remember-me-chet-faker-interviewed/" target="_blank" rel="noopener">
            <div class="meta">Clash Music · Feature</div>
            <div class="title">Remember Me: Chet Faker Interviewed</div>
            <p class="excerpt">Five years on from ‘Hotel Surrender’, Chet Faker confronts loss, heartache and industry disenchantment on an album grounded in communal warmth.</p>
            <div class="more">Read Article &rarr;</div>
        </a>

        <a class="entry" href="https://www.clashmusic.com/next-wave/next-wave-1179-pollyfromthedirt/" target="_blank" rel="noopener">
            <div class="meta">Clash Music · Next Wave</div>
            <div class="title">Next Wave #1179: Pollyfromthedirt</div>
            <p class="excerpt">Darlington’s masked, anti-industry talent honours his Northern roots on instinct alone — never chasing trends, just figuring out who he is in real time.</p>
            <div class="more">Read Article &rarr;</div>
        </a>
    </div>
</section>

<footer class="foot">
    <a href="mailto:jackdt26@outlook.com">Email Jack &rarr;</a>
</footer>
</html>