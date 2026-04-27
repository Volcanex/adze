<style>
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/barlow-700.ttf') format('truetype');
}

:root {
    --primary: #000000;
    --accent: #6495ED;
    --accent-hover: #FFB6C1;
    --bg: #ffffff;
    --bg-alt: #f0f0f0;
    --border: #000000;
    --text-muted: #333333;
    --pink: #FFB6C1;
    --blue: #6495ED;
    --text-font: 'Barlow', sans-serif;
    --heading-font: 'Barlow', sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--text-font);
    color: var(--primary);
    background: var(--bg);
    line-height: 1.5;
    font-size: 1rem;
    font-weight: 400;
    min-height: 100vh;
    display: flex;
    opacity: 0;
    animation: pageIn 0.3s ease-out forwards;
    position: relative;
}

body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 200px;
    width: 4px;
    height: 100vh;
    background: #000;
    z-index: 100;
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

h1, h2, h3, h4, h5, h6 {
    font-family: var(--heading-font);
    color: var(--primary);
    line-height: 1.4;
}

a { color: var(--primary); text-decoration: none; transition: color 0.4s ease; }
a:hover { color: var(--accent); }

/* ── Sidebar ── */
.sidebar {
    width: 200px;
    min-width: 200px;
    min-height: 100vh;
    padding: 40px 30px;
    display: flex;
    flex-direction: column;
    gap: 40px;
    background: #000;
    color: #fff;
    border-right: 4px solid #000;
    position: relative;
    z-index: 10;
}

.site-name {
    font-family: var(--heading-font);
    font-weight: 900;
    font-size: 24px;
    color: #fff;
    text-decoration: none;
    display: block;
    letter-spacing: -1px;
    text-transform: uppercase;
    transition: all 0.1s ease;
    border: 3px solid #fff;
    padding: 10px;
    text-align: center;
}
.site-name:hover {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
}

/* ── Navigation ── */
.nav-links {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
}
.nav-links a {
    font-size: 16px;
    font-weight: 700;
    display: block;
    transition: all 0.1s ease;
    padding: 12px 0;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: -0.5px;
    border-bottom: 2px solid #333;
}
.nav-links a:hover {
    background: var(--accent);
    color: #000;
    padding-left: 10px;
    border-bottom-color: var(--accent);
}

.social-links {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: auto;
}
.social-links a {
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.5px;
    transition: all 0.1s ease;
    text-transform: uppercase;
    padding: 12px 0;
    border-bottom: 2px solid #333;
}
.social-links a:hover {
    background: var(--pink);
    color: #000;
    padding-left: 10px;
}

/* ── Mobile ── */
.menu-toggle {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    width: 28px;
    height: 20px;
    position: relative;
    z-index: 1001;
}
.menu-toggle span {
    display: block;
    width: 100%;
    height: 1.5px;
    background: var(--primary);
    position: absolute;
    left: 0;
    transition: transform 0.35s ease, opacity 0.25s ease;
}
.menu-toggle span:nth-child(1) { top: 4px; }
.menu-toggle span:nth-child(2) { bottom: 4px; }
.menu-toggle.active span:nth-child(1) { top: 50%; transform: translateY(-50%) rotate(45deg); }
.menu-toggle.active span:nth-child(2) { bottom: auto; top: 50%; transform: translateY(-50%) rotate(-45deg); }

.mobile-header { display: none; }

@media (max-width: 768px) {
    body { flex-direction: column; font-size: 14px; }
    body::after { display: none; }

    .mobile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 16px;
        position: sticky;
        top: 0;
        background: #000;
        z-index: 1000;
        border-bottom: 1px solid #000;
    }
    .mobile-header .site-name {
        font-size: 13px;
        line-height: 1;
        animation: none;
        padding: 5px 8px;
        border-width: 2px;
    }
    .menu-toggle { display: block; height: 14px; width: 22px; align-self: center; }
    .menu-toggle span { background: #fff; }
    .menu-toggle span:nth-child(1) { top: 2px; }
    .menu-toggle span:nth-child(2) { bottom: 2px; }

    .sidebar {
        width: 100%; min-width: 100%; min-height: 0;
        padding: 0 20px;
        gap: 0;
        overflow: hidden;
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
        border: none;
        box-shadow: none;
    }
    .sidebar.open { grid-template-rows: 1fr; }
    .sidebar > .sidebar-inner { overflow: hidden; padding: 10px 0; }
    .sidebar .site-name { display: none; }
    .sidebar .nav-links { flex-direction: column; gap: 0; }
    .sidebar .nav-links a {
        font-size: 13px;
        padding: 8px 0;
        border-bottom-width: 1px;
    }
    .sidebar .social-links { margin-top: 0; padding-bottom: 4px; }
    .sidebar .social-links a {
        font-size: 13px;
        padding: 8px 0;
        border-bottom-width: 1px;
        letter-spacing: -0.5px;
    }
    .sidebar .social-links a:hover {
        background: var(--accent);
        border-bottom-color: var(--accent);
    }
}

/* ── Main Content ── */
.main-content {
    flex: 1;
    padding: 0;
    min-height: 100vh;
    animation: gentleFade 1s ease-out 0.3s both;
    position: relative;
    overflow: hidden;
}

.hero-text {
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
}
.hero-text h1 {
    font-style: normal;
    font-weight: 900;
    font-size: 6rem;
    margin: 0;
    letter-spacing: -4px;
    text-transform: uppercase;
    line-height: 0.9;
    position: absolute;
    left: 0;
    right: 0;
    white-space: nowrap;
    overflow: hidden;
    transform: translateY(-50%);
}
.hero-text h1 .scroll-track {
    display: inline-block;
    animation: scrollLeft 50s linear infinite;
    will-change: transform;
}
.hero-text h1.reverse .scroll-track {
    animation-name: scrollRight;
}
@keyframes scrollLeft {
    from { transform: translate3d(0, 0, 0); }
    to { transform: translate3d(-50%, 0, 0); }
}
@keyframes scrollRight {
    from { transform: translate3d(-50%, 0, 0); }
    to { transform: translate3d(0, 0, 0); }
}

/* Center */
.layer-black-center { color: #000; z-index: 11; top: 50%; }

/* Going up from center: Black → Pink → Blue → Black → Pink → Blue */
.layer-pink-top {
    background-image: url('../assets/images/back.png');
    background-size: 200px 200px;
    background-repeat: repeat;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    z-index: 10;
    top: calc(50% - 6rem);
}

.layer-blue-top { color: var(--blue); z-index: 9; top: calc(50% - 12rem); }
.layer-black-top { color: #000; z-index: 8; top: calc(50% - 18rem); }

.layer-pink-top-2 {
    background-image: url('../assets/images/back.png');
    background-size: 200px 200px;
    background-repeat: repeat;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    z-index: 7;
    top: calc(50% - 24rem);
}

.layer-blue-top-2 { color: var(--blue); z-index: 6; top: calc(50% - 30rem); }

/* Going down from center: Black → Pink → Blue → Black → Pink → Blue */
.layer-pink-bottom {
    background-image: url('../assets/images/back.png');
    background-size: 200px 200px;
    background-repeat: repeat;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    z-index: 5;
    top: calc(50% + 6rem);
}

.layer-blue-bottom { color: var(--blue); z-index: 4; top: calc(50% + 12rem); }
.layer-black-bottom { color: #000; z-index: 3; top: calc(50% + 18rem); }

.layer-pink-bottom-2 {
    background-image: url('../assets/images/back.png');
    background-size: 200px 200px;
    background-repeat: repeat;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    z-index: 2;
    top: calc(50% + 24rem);
}

.layer-blue-bottom-2 { color: var(--blue); z-index: 1; top: calc(50% + 30rem); }

@media (max-width: 768px) {
    .main-content { min-height: 60vh; padding: 0; }
    .hero-text { height: 60vh; }
    .hero-text h1 { font-size: 2.5rem; letter-spacing: -2px; }
    .hero-text h1 .scroll-track { animation-duration: 30s; }

    .layer-pink-top { top: calc(50% - 3rem); }
    .layer-blue-top { top: calc(50% - 6rem); }
    .layer-black-top { top: calc(50% - 9rem); }
    .layer-pink-top-2 { top: calc(50% - 12rem); }
    .layer-blue-top-2 { top: calc(50% - 15rem); }

    .layer-pink-bottom { top: calc(50% + 3rem); }
    .layer-blue-bottom { top: calc(50% + 6rem); }
    .layer-black-bottom { top: calc(50% + 9rem); }
    .layer-pink-bottom-2 { top: calc(50% + 12rem); }
    .layer-blue-bottom-2 { top: calc(50% + 15rem); }
}
</style>

<html>
<div class="mobile-header">
    <a href="../home/" class="site-name">KESKESAY</a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.sidebar').classList.toggle('open');" aria-label="Menu">
        <span></span>
        <span></span>
    </button>
</div>

<div class="sidebar">
    <div class="sidebar-inner">
    <a href="../home/" class="site-name">KESKESAY</a>

    <ul class="nav-links">
        <li><a href="../about/">About</a></li>
        <li><a href="../music/">Music</a></li>
        <li><a href="../writing/">Writing</a></li>
    </ul>

    <div class="social-links">
        <a href="#">Instagram</a>
    </div>
    </div>
</div>

<main class="main-content">
    <div class="hero-text">
        <h1 class="layer-blue-top-2" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-pink-top-2 reverse" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-black-top" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-blue-top reverse" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-pink-top" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-black-center reverse"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-pink-bottom" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-blue-bottom reverse" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-black-bottom" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-pink-bottom-2 reverse" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
        <h1 class="layer-blue-bottom-2" aria-hidden="true"><span class="scroll-track">KESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAYKESKESAY</span></h1>
    </div>
</main>
</html>