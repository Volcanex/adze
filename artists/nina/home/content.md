<style>
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300 900;
    font-display: swap;
    src: url('../assets/fonts/Inter-Variable.woff2') format('woff2');
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
    font-style: italic;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Bold.woff2') format('woff2');
}

:root {
    --bg: #f5f3ee;
    --ink: #111;
    --muted: #6a6660;
    --accent: #b84a39;
    --paper: #ece8df;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { min-height: 100%; }

body {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
    background: var(--bg);
    line-height: 1.5;
    font-size: 14px;
    overflow-x: hidden;
}
body.lightbox-open { overflow: hidden; }

/* ── Loader (covers initial font + image loading) ── */
#loader {
    position: fixed;
    inset: 0;
    background: var(--bg);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity .7s ease;
    pointer-events: auto;
}
.spinner {
    width: 26px;
    height: 26px;
    border: 1.5px solid rgba(17, 17, 17, 0.1);
    border-top-color: rgba(17, 17, 17, 0.75);
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

body > *:not(#loader) {
    opacity: 0;
    transition: opacity 0.9s ease;
}
body.ready > *:not(#loader) { opacity: 1; }
body.ready #loader {
    opacity: 0;
    pointer-events: none;
}

body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
}

#bg-flowers {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
    display: block;
}
.hero, .flurry, .foot { position: relative; z-index: 1; }

.topbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 50;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 32px;
    pointer-events: none;
    mix-blend-mode: difference;
    color: #f5f3ee;
}
.topbar > * { pointer-events: auto; }
.brand {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 15px;
    letter-spacing: 0.02em;
    text-decoration: none;
    color: inherit;
}
.topbar nav a {
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: inherit;
    text-decoration: none;
    margin-left: 20px;
    opacity: 0.85;
    transition: opacity .3s;
}
.topbar nav a:hover { opacity: 1; }

/* ── Hero ── */
.hero {
    min-height: 100vh;
    padding: 40px 32px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-name-wrap {
    position: relative;
    z-index: 5;
    mix-blend-mode: multiply;
}
.hero .name {
    font-family: 'Cardo', serif;
    font-weight: 400;
    font-size: clamp(2.8rem, 11vw, 10rem);
    line-height: 0.92;
    letter-spacing: -0.025em;
    animation: heroIn 1.1s cubic-bezier(.2,.8,.2,1) .1s both;
    position: relative;
}

/* ── Scattered hero photos ── */
.scatter {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 1;
}
.scatter .sp {
    position: absolute;
    overflow: hidden;
    border-radius: 2px;
    background: var(--paper);
    box-shadow: 0 14px 40px rgba(0,0,0,0.18);
    pointer-events: auto;
    cursor: pointer;
    opacity: 0;
    transform: translateY(12px) rotate(var(--r, 0deg)) scale(0.96);
    transition: transform .8s cubic-bezier(.2,.8,.2,1), box-shadow .4s ease, opacity .9s ease;
    will-change: transform;
    animation: spIn 1.4s cubic-bezier(.2,.8,.2,1) forwards, spFloat 9s ease-in-out infinite;
    animation-delay: var(--d, 0s), calc(var(--d, 0s) + 1.4s);
}
.scatter .sp img {
    width: 100%;
    height: auto;
    display: block;
}
.scatter .sp:hover {
    z-index: 6;
    box-shadow: 0 22px 60px rgba(0,0,0,0.28);
    transform: translateY(-6px) rotate(var(--r, 0deg));
}

@keyframes spIn {
    from { opacity: 0; transform: translateY(14px) rotate(var(--r, 0deg)) scale(0.94); }
    to   { opacity: 1; transform: translateY(0) rotate(var(--r, 0deg)) scale(1); }
}
@keyframes spFloat {
    0%, 100% { transform: translateY(0) rotate(var(--r, 0deg)) scale(1); }
    50%      { transform: translateY(var(--fy, -6px)) rotate(calc(var(--r, 0deg) + var(--rf, 0.4deg))) scale(1); }
}

@media (max-width: 680px) {
    .scatter .sp { box-shadow: 0 8px 22px rgba(0,0,0,0.15); }
}
.hero .name .first { display: block; font-style: italic; }
.hero .name .last {
    display: block;
    font-size: clamp(2.2rem, 9vw, 8rem);
    margin-top: -0.04em;
}
.hero .tag {
    margin-top: 28px;
    font-size: 11px;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    color: var(--muted);
    animation: heroIn 1.1s cubic-bezier(.2,.8,.2,1) .45s both;
}
.hero .tag .dot {
    display: inline-block; width: 4px; height: 4px;
    border-radius: 50%; background: var(--accent);
    margin: 0 10px; vertical-align: middle;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .5; transform: scale(1.4); } }
@keyframes heroIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }

.hero .scroll-hint {
    position: absolute;
    bottom: 36px; left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--muted);
    opacity: 0;
    animation: fadeInUp 1s ease-out 1.5s forwards, bob 2.4s ease-in-out 2.5s infinite;
}
@keyframes fadeInUp { from { opacity: 0; transform: translate(-50%, 10px); } to { opacity: .7; transform: translate(-50%, 0); } }
@keyframes bob { 0%,100% { transform: translate(-50%, 0); } 50% { transform: translate(-50%, 6px); } }

/* ── Flurry / masonry gallery ── */
.flurry {
    column-count: 5;
    column-gap: 18px;
    padding: 20px 32px 120px;
    max-width: 1720px;
    margin: 0 auto;
}
@media (max-width: 1400px) { .flurry { column-count: 4; } }
@media (max-width: 1000px) { .flurry { column-count: 3; column-gap: 14px; padding: 20px 20px 80px; } }
@media (max-width: 680px)  { .flurry { column-count: 2; column-gap: 10px; padding: 16px 14px 60px; } }
@media (max-width: 420px)  { .flurry { column-count: 2; column-gap: 8px; } }

.photo {
    position: relative;
    display: block;
    margin: 0 0 18px;
    break-inside: avoid;
    overflow: hidden;
    cursor: pointer;
    background: var(--paper);
    border-radius: 2px;
    opacity: 0;
    transform: translateY(22px) rotate(var(--rot, 0deg));
    transition: opacity .9s ease, transform .9s cubic-bezier(.2,.8,.2,1), box-shadow .4s ease;
    will-change: transform, opacity;
    box-shadow: 0 2px 8px rgba(0,0,0,0);
}
.photo.in {
    opacity: 1;
    transform: translateY(0) rotate(var(--rot, 0deg));
}
.photo:hover {
    z-index: 5;
    box-shadow: 0 16px 40px rgba(0,0,0,0.22);
    transform: translateY(-4px) rotate(var(--rot, 0deg)) scale(1.015);
}
.photo img {
    width: 100%;
    height: auto;
    display: block;
    transition: filter .6s;
}
.photo:hover img { filter: brightness(1.04); }
.photo::after {
    content: '↗';
    position: absolute;
    top: 10px; right: 12px;
    font-size: 16px;
    color: #fff;
    mix-blend-mode: difference;
    opacity: 0;
    transition: opacity .35s, transform .35s;
    transform: translate(-4px, 4px);
}
.photo:hover::after { opacity: 1; transform: translate(0, 0); }

/* Width-only sizing — heights follow each image's natural aspect ratio so nothing gets cropped. */
.photo.small  { width: 72%; }
.photo.medium { width: 88%; }
.photo.large  { width: 100%; }

/* ── Footer ── */
.foot {
    text-align: center;
    padding: 40px 24px 80px;
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
}
.foot a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--muted); padding-bottom: 2px; }
.foot a:hover { color: var(--accent); border-color: var(--accent); }

/* ── Lightbox ── */
.lightbox {
    position: fixed;
    inset: 0;
    background: rgba(10, 9, 8, 0.96);
    z-index: 1000;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 40px;
    opacity: 0;
    transition: opacity .4s ease;
}
.lightbox.open { display: flex; opacity: 1; }
.lightbox .lb-stage {
    position: relative;
    max-width: 100%;
    max-height: 100%;
}
.lightbox img {
    max-width: 92vw;
    max-height: 82vh;
    object-fit: contain;
    border-radius: 2px;
    box-shadow: 0 30px 80px rgba(0,0,0,0.5);
    transform: scale(0.98);
    transition: transform .5s cubic-bezier(.2,.8,.2,1);
}
.lightbox.open img { transform: scale(1); }

.lb-meta {
    position: absolute;
    left: 50%;
    bottom: 24px;
    transform: translateX(-50%);
    color: #f5f3ee;
    text-align: center;
    font-family: 'Cardo', serif;
    pointer-events: none;
}
.lb-meta .loc { font-style: italic; font-size: 22px; letter-spacing: 0.02em; }
.lb-meta .sub { font-family: 'Inter'; font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase; color: #d7d0c4; margin-top: 8px; opacity: 0.85; }

.lb-close, .lb-prev, .lb-next {
    position: absolute;
    background: none;
    border: none;
    color: #f5f3ee;
    font-family: 'Cardo', serif;
    font-size: 28px;
    cursor: pointer;
    padding: 16px;
    opacity: 0.6;
    transition: opacity .2s, transform .2s;
}
.lb-close:hover, .lb-prev:hover, .lb-next:hover { opacity: 1; }
.lb-close { top: 20px; right: 20px; font-size: 12px; letter-spacing: 0.2em; font-family: 'Inter'; text-transform: uppercase; }
.lb-prev { left: 20px; top: 50%; transform: translateY(-50%); }
.lb-next { right: 20px; top: 50%; transform: translateY(-50%); }
.lb-prev:hover { transform: translateY(-50%) translateX(-4px); }
.lb-next:hover { transform: translateY(-50%) translateX(4px); }

.lb-counter {
    position: absolute;
    top: 28px;
    left: 50%;
    transform: translateX(-50%);
    color: #d7d0c4;
    font-size: 10px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    font-family: 'Inter';
}

@media (max-width: 680px) {
    .topbar { padding: 16px 18px; }
    .topbar nav a { margin-left: 12px; }
    .hero .scroll-hint { bottom: 24px; }
    .lb-meta .loc { font-size: 16px; }
}
</style>
<html>
<div id="loader" aria-hidden="true"><div class="spinner"></div></div>
<canvas id="bg-flowers" aria-hidden="true"></canvas>

<div class="topbar">
    <span></span>
    <nav>
        <a href="../about/">About</a>
    </nav>
</div>

<section class="hero">
    <div class="scatter" id="scatter" aria-hidden="true"></div>
    <div class="hero-name-wrap">
        <div class="name">
            <span class="first">Nina</span>
            <span class="last">Serebrennikova</span>
        </div>
        <div class="tag">International Model</div>
    </div>
    <div class="scroll-hint">Scroll</div>
</section>

<section class="flurry" id="flurry"></section>

<footer class="foot">
    <a href="../about/">About Nina</a>
</footer>

<div class="lightbox" id="lightbox" aria-hidden="true">
    <button class="lb-close" aria-label="Close">Close</button>
    <button class="lb-prev" aria-label="Previous">←</button>
    <button class="lb-next" aria-label="Next">→</button>
    <div class="lb-counter" id="lb-counter"></div>
    <div class="lb-stage"><img id="lb-img" alt=""></div>
    <div class="lb-meta">
        <div class="loc" id="lb-loc"></div>
        <div class="sub" id="lb-sub"></div>
    </div>
</div>

<script type="application/json" id="photo-data">
[{"src":"photos/0-12.jpeg","location":"Saigon, Vietnam","year":2024,"caption":"","w":750,"h":1125},{"src":"photos/81c1b8e6-5fb1-4d7f-ba48-112395977e07.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/aandb-2023-05-02-at-1-21-41-pm.jpg","location":"Seoul, South Korea","year":2023,"caption":"A&B","w":750,"h":1130},{"src":"photos/adaul-2023-04-28-at-2-41-08-pm.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Adaul","w":1280,"h":1856},{"src":"photos/adaul-2023-04-28-at-2-51-08-pm.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Adaul","w":1268,"h":1870},{"src":"photos/adaul-2023-04-28-at-2-51-19-pm.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Adaul","w":1266,"h":1854},{"src":"photos/adaul-2023-04-28-at-2-52-01-pm.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Adaul","w":1294,"h":1882},{"src":"photos/beldencarlson1656.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1657.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1658.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1661.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":4898,"h":3265},{"src":"photos/beldencarlson1664.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3229,"h":4954},{"src":"photos/beldencarlson1674.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3068,"h":4602},{"src":"photos/beldencarlson1681.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1683.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3232,"h":4949},{"src":"photos/beldencarlson1684.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1691.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1696.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3306,"h":4840},{"src":"photos/beldencarlson1698.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/beldencarlson1718.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3266,"h":4898},{"src":"photos/beldencarlson1731.jpg","location":"San Francisco, USA","year":2022,"caption":"Belden Carlson","w":3265,"h":4898},{"src":"photos/daughter-2663-large.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":750,"h":1125},{"src":"photos/daughter-3377-large.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":750,"h":1125},{"src":"photos/daughter-korea-24.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":1000,"h":1500},{"src":"photos/daughter-korea-25.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":1000,"h":1500},{"src":"photos/daughter-korea-27.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":992,"h":1494},{"src":"photos/daughter-korea11.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":1000,"h":1500},{"src":"photos/daughter-korea5.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Daughter","w":983,"h":1448},{"src":"photos/dsc02463-2-edit-copy.jpg","location":"Tokyo, Japan","year":2022,"caption":"","w":3265,"h":4898},{"src":"photos/dsc02504-edit-copy.jpg","location":"Tokyo, Japan","year":2022,"caption":"","w":3142,"h":5092},{"src":"photos/fx.jpg","location":"Paris, France","year":2023,"caption":"","w":5003,"h":3197},{"src":"photos/img-20210910-052055-363.jpg","location":"Moscow, Russia","year":2021,"caption":"","w":4781,"h":3182},{"src":"photos/img-20210910-052100-850.jpg","location":"Moscow, Russia","year":2021,"caption":"","w":4969,"h":3307},{"src":"photos/img-20210910-052127-775.jpg","location":"Moscow, Russia","year":2021,"caption":"","w":4808,"h":3200},{"src":"photos/img-3383.jpg","location":"Tokyo, Japan","year":2022,"caption":"","w":4955,"h":3229},{"src":"photos/img-4555.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-4691.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-4772.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3234,"h":4946},{"src":"photos/img-4787.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-4847.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-4876.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-4932.jpg","location":"Saigon, Vietnam","year":2024,"caption":"","w":3265,"h":4898},{"src":"photos/img-5039.jpg","location":"London, UK","year":2022,"caption":"","w":3265,"h":4898},{"src":"photos/img-5063.jpg","location":"London, UK","year":2022,"caption":"","w":4898,"h":3265},{"src":"photos/img-5066.jpg","location":"London, UK","year":2022,"caption":"","w":4898,"h":3265},{"src":"photos/img-5076bw.jpg","location":"London, UK","year":2022,"caption":"","w":4898,"h":3265},{"src":"photos/img-5089.jpg","location":"London, UK","year":2022,"caption":"","w":4898,"h":3265},{"src":"photos/img-5125.jpg","location":"London, UK","year":2022,"caption":"","w":3265,"h":4898},{"src":"photos/img-5161bw.jpg","location":"London, UK","year":2022,"caption":"","w":3265,"h":4898},{"src":"photos/img-5553cropv2.jpg","location":"London, UK","year":2022,"caption":"","w":2609,"h":1825},{"src":"photos/img-7478.jpg","location":"New York, USA","year":2023,"caption":"","w":4898,"h":3265},{"src":"photos/img-7486.jpg","location":"New York, USA","year":2023,"caption":"","w":3265,"h":4898},{"src":"photos/img-7506.jpg","location":"New York, USA","year":2023,"caption":"","w":3265,"h":4898},{"src":"photos/kirsh10.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":1670,"h":1181},{"src":"photos/kirsh14.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":1670,"h":1181},{"src":"photos/kirsh20.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":1670,"h":1181},{"src":"photos/kirsh26.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":900,"h":900},{"src":"photos/kirsh32.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":800,"h":1189},{"src":"photos/kirsh4.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":1670,"h":1181},{"src":"photos/kirsh45.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":800,"h":1191},{"src":"photos/kirsh6.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Kirsh","w":1670,"h":1181},{"src":"photos/parisss.jpeg","location":"Paris, France","year":2023,"caption":"","w":1399,"h":1000},{"src":"photos/parisss1.jpeg","location":"Paris, France","year":2023,"caption":"","w":1200,"h":1500},{"src":"photos/parisss2.jpeg","location":"Paris, France","year":2023,"caption":"","w":1200,"h":1500},{"src":"photos/parisss3.jpeg","location":"Paris, France","year":2023,"caption":"","w":1200,"h":1500},{"src":"photos/parisss4.jpeg","location":"Paris, France","year":2023,"caption":"","w":1200,"h":1500},{"src":"photos/peachy1.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Peachy","w":617,"h":765},{"src":"photos/peachy24.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Peachy","w":960,"h":1436},{"src":"photos/peachy5.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Peachy","w":960,"h":1437},{"src":"photos/somewhere1.png","location":"Tokyo, Japan","year":2022,"caption":"","w":270,"h":404},{"src":"photos/somewhere14.jpeg","location":"Tokyo, Japan","year":2022,"caption":"","w":900,"h":1343},{"src":"photos/soonsu12.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu18.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu19.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu2.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu27.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu28.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/soonsu3.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Soonsu","w":1200,"h":1800},{"src":"photos/verte-kor-5.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Verte","w":1000,"h":1261},{"src":"photos/verte-kor.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Verte","w":1000,"h":1156},{"src":"photos/verte-korea-15-copy.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Verte","w":989,"h":1479},{"src":"photos/verte-korea1.jpeg","location":"Seoul, South Korea","year":2023,"caption":"Verte","w":1046,"h":800}]
</script>

<script>
// ── Loader gate: fade page in only when fonts + scatter photos + atlas ready ──
(function() {
    const MIN_VISIBLE = 700; // ms — show the spinner briefly even on cached loads
    const HARD_TIMEOUT = 6000; // ms — don't let a slow asset hold the page forever
    const start = performance.now();

    function imgDone(img) {
        if (img.complete && img.naturalWidth > 0) return Promise.resolve();
        return new Promise(res => {
            img.addEventListener('load', res, { once: true });
            img.addEventListener('error', res, { once: true });
        });
    }

    function ready() {
        const held = performance.now() - start;
        const wait = Math.max(0, MIN_VISIBLE - held);
        setTimeout(() => document.body.classList.add('ready'), wait);
    }

    window.addEventListener('DOMContentLoaded', () => {
        // Scatter images are built by the next IIFE — wait a tick for them to attach.
        Promise.resolve().then(() => {
            const scatterImgs = Array.from(document.querySelectorAll('.scatter img'));
            const fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
            const imgs = Promise.all(scatterImgs.map(imgDone));
            Promise.race([
                Promise.all([fontsReady, imgs]),
                new Promise(r => setTimeout(r, HARD_TIMEOUT))
            ]).then(ready);
        });
    });
})();

// ── Flower background: sprites sliced from flowers.png atlas ──
(function() {
    const canvas = document.getElementById('bg-flowers');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0, dpr = 1;

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        canvas.style.width = W + 'px';
        canvas.style.height = H + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    // Atlas: uniform 12 × 7 grid, no gap, no shave.
    const COLS = 12, ROWS = 7;
    const atlas = new Image();
    atlas.src = '../assets/images/flowers2.png';
    let atlasCanvas = null;
    const TILES = [];
    let atlasReady = false;

    atlas.addEventListener('load', () => {
        const off = document.createElement('canvas');
        off.width = atlas.naturalWidth;
        off.height = atlas.naturalHeight;
        const octx = off.getContext('2d');
        octx.drawImage(atlas, 0, 0);
        // Chroma-key: drop near-white pixels with a soft anti-aliased edge.
        const img = octx.getImageData(0, 0, off.width, off.height);
        const d = img.data;
        for (let i = 0; i < d.length; i += 4) {
            const r = d[i], g = d[i+1], b = d[i+2];
            const m = Math.min(r, g, b);
            if (m >= 228) {
                d[i+3] = 0;
            } else if (m >= 185) {
                const t = (m - 185) / 43;
                d[i+3] = Math.round(d[i+3] * (1 - t));
            }
        }
        octx.putImageData(img, 0, 0);
        atlasCanvas = off;

        const cw = atlas.naturalWidth / COLS;
        const ch = atlas.naturalHeight / ROWS;
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                TILES.push({ sx: c * cw, sy: r * ch, sw: cw, sh: ch });
            }
        }
        atlasReady = true;
    });

    const rand = (a, b) => a + Math.random() * (b - a);
    const pickTile = () => TILES[Math.floor(Math.random() * TILES.length)];
    function easeOutBack(t) { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); }

    // ── Petal: sprite falling with sway + rotation, with gentle repulsion from each other & the mouse ──
    class Petal {
        constructor(y) {
            this.x = rand(-20, W + 20);
            this.y = y !== undefined ? y : rand(-160, -40);
            this.size = rand(70, 150);
            this.tile = pickTile();
            this.vx = rand(-0.25, 0.25);
            this.vy = rand(0.35, 0.85);
            this.rotation = rand(0, Math.PI * 2);
            this.rotSpeed = rand(-0.01, 0.01);
            this.swayPhase = rand(0, Math.PI * 2);
            this.swayAmp = rand(0.3, 0.9);
            this.swayFreq = rand(0.0008, 0.0016);
            this.ox = 0; this.oy = 0; // repulsion offset — accumulates, decays
            this.life = 0;
        }
        update(dt) {
            this.life += dt;
            // Decay repulsion offset toward zero
            this.ox *= 0.92;
            this.oy *= 0.92;
            this.y += this.vy * (dt / 16) + this.oy * (dt / 16) * 0.4;
            this.x += (this.vx + Math.sin(this.life * this.swayFreq + this.swayPhase) * this.swayAmp) * (dt / 16) + this.ox * (dt / 16) * 0.4;
            this.rotation += this.rotSpeed * (dt / 16);
            this.done = this.y > H + 120 || this.x < -160 || this.x > W + 160;
        }
        draw(ctx) {
            if (!this.tile || !atlasCanvas) return;
            const aspect = this.tile.sh / this.tile.sw;
            const w = this.size, h = w * aspect;
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.rotation);
            ctx.drawImage(atlasCanvas, this.tile.sx, this.tile.sy, this.tile.sw, this.tile.sh, -w/2, -h/2, w, h);
            ctx.restore();
        }
    }

    const petals = [];
    const MAX_PETALS = 16;
    let lastSpawn = 0, lastTime = performance.now();
    let visible = !document.hidden;
    let mouseX = -1e6, mouseY = -1e6;

    document.addEventListener('visibilitychange', () => { visible = !document.hidden; lastTime = performance.now(); });
    window.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; }, { passive: true });
    window.addEventListener('mouseleave', () => { mouseX = -1e6; mouseY = -1e6; });

    atlas.addEventListener('load', () => {
        for (let i = 0; i < 6; i++) petals.push(new Petal(rand(-H * 0.3, H)));
    });

    // Apply pairwise repulsion + mouse repulsion. O(n^2) is fine for ~16 petals.
    function applyRepulsion() {
        const MIN_DIST = 120;            // petals push away when centers are closer than this
        const MOUSE_RADIUS = 180;         // mouse influence radius
        const MOUSE_STRENGTH = 2.2;
        for (let i = 0; i < petals.length; i++) {
            const a = petals[i];
            // Mouse
            if (mouseX > -1e5) {
                const dx = a.x - mouseX, dy = a.y - mouseY;
                const d2 = dx * dx + dy * dy;
                if (d2 < MOUSE_RADIUS * MOUSE_RADIUS && d2 > 1) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d / MOUSE_RADIUS) * MOUSE_STRENGTH;
                    a.ox += (dx / d) * f;
                    a.oy += (dy / d) * f;
                }
            }
            // Petal pairs
            for (let j = i + 1; j < petals.length; j++) {
                const b = petals[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const d2 = dx * dx + dy * dy;
                if (d2 < MIN_DIST * MIN_DIST && d2 > 1) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d / MIN_DIST) * 0.35;
                    const fx = (dx / d) * f, fy = (dy / d) * f;
                    a.ox += fx; a.oy += fy;
                    b.ox -= fx; b.oy -= fy;
                }
            }
        }
    }

    function loop(now) {
        requestAnimationFrame(loop);
        if (!visible || !atlasReady) { lastTime = now; return; }
        const dt = Math.min(60, now - lastTime); lastTime = now;
        if (now - lastSpawn > rand(900, 1800) && petals.length < MAX_PETALS) {
            petals.push(new Petal()); lastSpawn = now;
        }
        applyRepulsion();
        ctx.clearRect(0, 0, W, H);
        for (let i = petals.length - 1; i >= 0; i--) {
            petals[i].update(dt); petals[i].draw(ctx);
            if (petals[i].done) petals.splice(i, 1);
        }
    }
    requestAnimationFrame((t) => { lastTime = t; loop(t); });
})();

(function() {
    const data = JSON.parse(document.getElementById('photo-data').textContent);

    // Deterministic shuffle from a seed so rebuilds are stable but feel random.
    function mulberry32(a) {
        return function() {
            let t = a += 0x6D2B79F5;
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }
    const rand = mulberry32(42);
    const photos = data.slice();
    for (let i = photos.length - 1; i > 0; i--) {
        const j = Math.floor(rand() * (i + 1));
        [photos[i], photos[j]] = [photos[j], photos[i]];
    }

    // ── Scattered hero photos ──
    // Preset positions (%), sizes (vmin), rotations — gives a composed-but-organic look.
    // Name sits centered; these orbit it. Tweak freely.
    // Height is driven by the image's natural aspect ratio (no cropping); only width is set.
    const SCATTER = [
        { top: '5%',   left: '2%',   w: '22vmin', r: -5, d: 0.0,  fy: -8 },
        { top: '3%',   left: '28%',  w: '15vmin', r: 3,  d: 0.18, fy: -5 },
        { top: '6%',   right: '3%',  w: '23vmin', r: 4,  d: 0.08, fy: -7 },
        { top: '42%',  left: '1%',   w: '18vmin', r: -3, d: 0.26, fy: 6  },
        { top: '44%',  right: '2%',  w: '19vmin', r: 5,  d: 0.14, fy: -6 },
        { bottom: '3%', left: '4%',  w: '24vmin', r: -4, d: 0.32, fy: 5  },
        { bottom: '6%', left: '33%', w: '15vmin', r: 6,  d: 0.22, fy: 7  },
        { bottom: '5%', right: '24%', w: '17vmin', r: -2, d: 0.28, fy: 6 },
        { bottom: '3%', right: '2%',  w: '22vmin', r: 4,  d: 0.36, fy: -5 },
    ];

    const scatter = document.getElementById('scatter');
    // Pick the first N from the shuffled deck so it feels fresh each session;
    // shuffled order itself is deterministic (seeded) so refreshes look stable.
    const scatterPicks = data.slice(); // use unshuffled data for scatter
    // Use a different rand seed so scatter != flurry ordering
    const rand2 = mulberry32(88);
    for (let i = scatterPicks.length - 1; i > 0; i--) {
        const j = Math.floor(rand2() * (i + 1));
        [scatterPicks[i], scatterPicks[j]] = [scatterPicks[j], scatterPicks[i]];
    }
    SCATTER.forEach((slot, i) => {
        const p = scatterPicks[i % scatterPicks.length];
        if (!p) return;
        const tile = document.createElement('div');
        tile.className = 'sp';
        tile.style.width = slot.w;
        if (p.w && p.h) tile.style.aspectRatio = `${p.w} / ${p.h}`;
        tile.style.setProperty('--r', slot.r + 'deg');
        tile.style.setProperty('--d', slot.d + 's');
        tile.style.setProperty('--fy', slot.fy + 'px');
        tile.style.setProperty('--rf', ((i % 2 ? 0.6 : -0.6)).toFixed(2) + 'deg');
        if (slot.top)    tile.style.top = slot.top;
        if (slot.left)   tile.style.left = slot.left;
        if (slot.right)  tile.style.right = slot.right;
        if (slot.bottom) tile.style.bottom = slot.bottom;
        const url = '../assets/' + p.src.split('/').map(encodeURIComponent).join('/');
        const ws = p.w || '', hs = p.h || '';
        tile.innerHTML = `<img ${ws?`width="${ws}" `:''}${hs?`height="${hs}" `:''}src="${url}" alt="${p.location || ''}">`;
        tile.addEventListener('click', () => {
            const idx = photos.findIndex(q => q.src === p.src);
            if (idx >= 0) openLightbox(idx);
        });
        scatter.appendChild(tile);
    });

    const flurry = document.getElementById('flurry');
    const sizes = ['large', 'medium', 'large', 'small', 'large', 'medium', 'large', 'medium', 'large', 'small'];

    photos.forEach((p, i) => {
        const tile = document.createElement('div');
        const size = sizes[i % sizes.length];
        tile.className = 'photo ' + size;
        tile.dataset.idx = String(i);
        // Micro-random rotation for that hand-placed collage feel
        const rot = (rand() * 2 - 1) * 1.2; // ±1.2deg
        tile.style.setProperty('--rot', rot.toFixed(2) + 'deg');
        // Reserve space based on natural aspect ratio so images don't knock neighbours around as they load.
        if (p.w && p.h) tile.style.aspectRatio = `${p.w} / ${p.h}`;
        const url = '../assets/' + p.src.split('/').map(encodeURIComponent).join('/');
        const w = p.w || '', h = p.h || '';
        tile.innerHTML = `<img loading="lazy" ${w?`width="${w}" `:''}${h?`height="${h}" `:''}src="${url}" alt="${p.location || ''}">`;
        tile.addEventListener('click', () => openLightbox(i));
        flurry.appendChild(tile);
    });

    // Stagger the entrance as tiles scroll into view
    const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                const idx = parseInt(e.target.dataset.idx, 10) || 0;
                // Small per-tile delay for the "flurry" reveal
                e.target.style.transitionDelay = ((idx % 6) * 60) + 'ms';
                e.target.classList.add('in');
                io.unobserve(e.target);
            }
        });
    }, { rootMargin: '0px 0px -60px 0px', threshold: 0.05 });
    flurry.querySelectorAll('.photo').forEach(el => io.observe(el));

    // ── Lightbox ──
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lb-img');
    const lbLoc = document.getElementById('lb-loc');
    const lbSub = document.getElementById('lb-sub');
    const lbCounter = document.getElementById('lb-counter');
    let lbIdx = 0;

    function openLightbox(i) {
        lbIdx = i;
        showLightbox();
        lb.classList.add('open');
        lb.setAttribute('aria-hidden', 'false');
        document.body.classList.add('lightbox-open');
    }
    function showLightbox() {
        const p = photos[lbIdx];
        if (!p) return;
        lbImg.src = '../assets/' + p.src.split('/').map(encodeURIComponent).join('/');
        lbImg.alt = p.location;
        lbLoc.textContent = p.location || '';
        const subParts = [];
        if (p.year) subParts.push(p.year);
        if (p.caption) subParts.push(p.caption);
        lbSub.textContent = subParts.join('  ·  ');
        lbCounter.textContent = `${lbIdx + 1} / ${photos.length}`;
    }
    function closeLightbox() {
        lb.classList.remove('open');
        lb.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('lightbox-open');
    }
    function next() { lbIdx = (lbIdx + 1) % photos.length; showLightbox(); }
    function prev() { lbIdx = (lbIdx - 1 + photos.length) % photos.length; showLightbox(); }

    lb.querySelector('.lb-close').addEventListener('click', closeLightbox);
    lb.querySelector('.lb-next').addEventListener('click', next);
    lb.querySelector('.lb-prev').addEventListener('click', prev);
    lb.addEventListener('click', (e) => { if (e.target === lb) closeLightbox(); });

    document.addEventListener('keydown', (e) => {
        if (!lb.classList.contains('open')) return;
        if (e.key === 'Escape') closeLightbox();
        else if (e.key === 'ArrowRight') next();
        else if (e.key === 'ArrowLeft') prev();
    });
})();
</script>
</html>
