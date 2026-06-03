<style>
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300 900;
    font-display: fallback;
    src: url('../assets/fonts/Inter-Variable.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: italic;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Bold.woff2') format('woff2');
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--text-font);
    color: var(--primary);
    background: #0c0a08;
    line-height: var(--body-line-height);
    font-size: var(--body-size);
    font-weight: var(--body-weight);
    min-height: 100vh;
    display: flex;
    overflow: hidden;
    opacity: 0;
    animation: pageIn 1.2s ease-out forwards;
}

body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: 0.08;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 256px 256px;
    mix-blend-mode: overlay;
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideRight { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
@keyframes floatA { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(40px,-30px) scale(1.08); } }
@keyframes floatB { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-50px,40px) scale(1.12); } }
@keyframes floatC { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px,50px) scale(0.95); } }
@keyframes driftIn { from { opacity: 0; transform: translateY(20px) scale(0.96); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes nameRoll { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes tickerScroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }

a { color: inherit; text-decoration: none; transition: color 0.4s ease, opacity 0.4s ease; }

/* ── Sidebar ── */
.sidebar {
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    min-height: 100vh;
    padding: var(--page-padding) 36px;
    display: flex;
    flex-direction: column;
    gap: var(--section-gap);
    position: relative;
    z-index: 5;
    color: #f3ece1;
    mix-blend-mode: difference;
    animation: slideRight 0.8s ease-out 0.1s both;
}

.site-name {
    font-family: var(--heading-font);
    font-weight: var(--site-name-weight);
    font-size: var(--site-name-size);
    color: #f3ece1;
    display: block;
    letter-spacing: 0.2px;
}
.site-name:hover { color: #ff7a2c; }

.nav-links { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.nav-links a {
    font-size: var(--nav-size);
    font-weight: var(--nav-weight);
    color: #f3ece1;
    transition: color 0.3s ease, padding-left 0.3s ease;
}
.nav-links a:hover { color: #ff7a2c; padding-left: 6px; }

.social-links { display: flex; gap: 16px; margin-top: auto; }
.social-links a { font-size: 12px; color: #c8bfb1; letter-spacing: 0.5px; }
.social-links a:hover { color: #ff7a2c; }

.menu-toggle { display: none; background: none; border: none; cursor: pointer; width: 28px; height: 20px; position: relative; z-index: 1001; }
.menu-toggle span { display: block; width: 100%; height: 1.5px; background: #f3ece1; position: absolute; left: 0; transition: transform 0.35s ease, opacity 0.25s ease; }
.menu-toggle span:nth-child(1) { top: 4px; }
.menu-toggle span:nth-child(2) { bottom: 4px; }
.menu-toggle.active span:nth-child(1) { top: 50%; transform: translateY(-50%) rotate(45deg); }
.menu-toggle.active span:nth-child(2) { bottom: auto; top: 50%; transform: translateY(-50%) rotate(-45deg); }

.mobile-header { display: none; }

/* ── Stage ── */
.stage {
    flex: 1;
    position: relative;
    min-height: 100vh;
    overflow: hidden;
}

.blur {
    position: absolute;
    border-radius: 50%;
    filter: blur(110px);
    opacity: 0.75;
    pointer-events: none;
    mix-blend-mode: screen;
}
.blur.b1 { width: 55vw; height: 55vw; left: -10vw; top: -15vw; background: #ff4a1c; animation: floatA 22s ease-in-out infinite; }
.blur.b2 { width: 45vw; height: 45vw; right: -8vw; top: 10vw; background: #ffd24a; animation: floatB 26s ease-in-out infinite; }
.blur.b3 { width: 40vw; height: 40vw; left: 25vw; bottom: -12vw; background: #6a3cff; animation: floatC 30s ease-in-out infinite; }
.blur.b4 { width: 30vw; height: 30vw; right: 18vw; bottom: 8vw; background: #19c2a0; animation: floatA 28s ease-in-out infinite reverse; }

.photo {
    position: absolute;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 30px 60px rgba(0,0,0,0.55), 0 6px 14px rgba(0,0,0,0.35);
    transition: transform 0.6s cubic-bezier(.2,.8,.2,1), box-shadow 0.6s ease, filter 0.6s ease;
    will-change: transform;
    opacity: 0;
    animation: driftIn 1s ease-out both;
}
.photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photo .cap {
    position: absolute;
    left: 8px; bottom: 6px;
    font-family: var(--heading-font);
    font-style: italic;
    font-size: 12px;
    color: #fff;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 4px rgba(0,0,0,0.7);
    opacity: 0.85;
}
.photo:hover { transform: rotate(0deg) scale(1.04) !important; box-shadow: 0 40px 80px rgba(0,0,0,0.7); filter: saturate(1.15); }

.p1 { width: 28vw; height: 36vh; left: 6vw;  top: 12vh; transform: rotate(-4deg); animation-delay: 0.5s; }
.p2 { width: 22vw; height: 30vh; right: 8vw; top: 8vh;  transform: rotate(3deg);  animation-delay: 0.7s; }
.p3 { width: 24vw; height: 28vh; left: 18vw; bottom: 6vh; transform: rotate(2deg); animation-delay: 0.9s; }
.p4 { width: 18vw; height: 24vh; right: 14vw; bottom: 10vh; transform: rotate(-3deg); animation-delay: 1.1s; }
.p5 { width: 20vw; height: 22vh; left: 38vw; top: 38vh; transform: rotate(-1deg); animation-delay: 1.3s; }

.title-wrap {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    z-index: 3;
    text-align: center;
    padding: 0 20px;
}
.title-wrap h1 {
    font-family: var(--heading-font);
    font-style: italic;
    font-weight: 700;
    font-size: clamp(56px, 11vw, 180px);
    line-height: 0.95;
    color: #fff8ee;
    letter-spacing: -2px;
    mix-blend-mode: difference;
    text-shadow: 0 4px 24px rgba(0,0,0,0.4);
    animation: nameRoll 1.2s ease-out 0.4s both;
}
.title-wrap .sub {
    margin-top: 10px;
    font-size: 13px;
    color: #f3ece1;
    letter-spacing: 4px;
    text-transform: uppercase;
    opacity: 0.85;
    mix-blend-mode: difference;
    animation: nameRoll 1.2s ease-out 0.8s both;
}

.ticker {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    overflow: hidden;
    padding: 14px 0;
    z-index: 4;
    background: linear-gradient(to top, rgba(0,0,0,0.55), transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
            mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
    white-space: nowrap;
}
.ticker-track {
    display: inline-block;
    white-space: nowrap;
    animation: tickerScroll 38s linear infinite;
    font-family: var(--heading-font);
    font-style: italic;
    font-size: 16px;
    color: #f3ece1;
    letter-spacing: 0.5px;
}
.ticker-track span { opacity: 0.8; padding-right: 36px; }
.ticker-track span::after { content: '·'; color: #ff7a2c; opacity: 0.7; padding-left: 36px; }

@media (max-width: 768px) {
    body { flex-direction: column; font-size: 14px; overflow-x: hidden; }

    .mobile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        position: sticky; top: 0; z-index: 1000;
        background: rgba(12,10,8,0.85);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #f3ece1;
    }
    .mobile-header .site-name { font-size: 16px; color: #f3ece1; }

    .sidebar {
        width: 100%; min-width: 100%; min-height: 0;
        padding: 0 20px; gap: 16px; overflow: hidden;
        display: grid; grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
        mix-blend-mode: normal;
    }
    .sidebar.open { grid-template-rows: 1fr; border-bottom: 1px solid rgba(255,255,255,0.08); }
    .sidebar > .sidebar-inner { overflow: hidden; padding-bottom: 16px; }
    .sidebar .site-name { display: none; }
    .sidebar .nav-links { padding-top: 16px; gap: 8px; }

    .stage { min-height: 80vh; }
    .p1 { width: 60vw; height: 28vh; left: 4vw; top: 8vh; }
    .p2 { width: 50vw; height: 24vh; right: 4vw; top: 6vh; }
    .p3 { width: 55vw; height: 22vh; left: 8vw; bottom: 18vh; }
    .p4 { width: 40vw; height: 18vh; right: 6vw; bottom: 22vh; }
    .p5 { display: none; }
    .title-wrap h1 { font-size: clamp(44px, 14vw, 90px); }
    .ticker-track { font-size: 13px; }
}
</style>
<html>
<div class="mobile-header">
    <a href="../home/" class="site-name">bodaciousfm</a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.sidebar').classList.toggle('open');" aria-label="Menu">
        <span></span>
        <span></span>
    </button>
</div>

<div class="sidebar">
    <div class="sidebar-inner">
    <a href="../home/" class="site-name">bodaciousfm</a>

    <ul class="nav-links">
        <li><a href="../about/">About</a></li>
    </ul>

    <div class="social-links">
        <a href="#">Instagram</a>
    </div>
    </div>
</div>

<main class="stage">
    <div class="blur b1"></div>
    <div class="blur b2"></div>
    <div class="blur b3"></div>
    <div class="blur b4"></div>

    <div class="photo p1"><img src="../assets/images/BINS.jpeg" alt=""><span class="cap">bins</span></div>
    <div class="photo p2"><img src="../assets/images/FOOT.jpeg" alt=""><span class="cap">foot</span></div>
    <div class="photo p3"><img src="../assets/images/mushroom.jpeg" alt=""><span class="cap">mushroom</span></div>
    <div class="photo p4"><img src="../assets/images/drawing.png" alt=""><span class="cap">drawing</span></div>
    <div class="photo p5"><img src="../assets/images/IMG_2966.jpeg" alt=""><span class="cap">2966</span></div>

    <div class="title-wrap">
        <h1>bodaciousfm</h1>
        <div class="sub">chariot · cutlass · cerberus</div>
    </div>

    <div class="ticker">
        <div class="ticker-track">
            <span>chariot</span><span>cutlass</span><span>mancherum</span><span>naysayer</span><span>blimey</span><span>parlortalk</span><span>braggot</span><span>abandon ship</span><span>sojourn</span><span>cerberus</span><span>chariot</span><span>cutlass</span><span>mancherum</span><span>naysayer</span><span>blimey</span><span>parlortalk</span><span>braggot</span><span>abandon ship</span><span>sojourn</span><span>cerberus</span>
        </div>
    </div>
</main>
</html>
