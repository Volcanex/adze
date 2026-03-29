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
        padding: 16px 20px;
        position: sticky;
        top: 0;
        background: var(--bg);
        z-index: 1000;
        border-bottom: 1px solid #000;
        box-shadow: 0 4px 8px var(--shadow-dark);
    }
    .mobile-header .site-name { font-size: 16px; animation: none; }
    .menu-toggle { display: block; }

    .sidebar {
        width: 100%; min-width: 100%; min-height: 0;
        padding: 0 20px; gap: 16px; overflow: hidden;
        display: grid; grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
        border: none;
        box-shadow: none;
    }
    .sidebar.open { grid-template-rows: 1fr; border-bottom: 1px solid #000; }
    .sidebar > .sidebar-inner { overflow: hidden; }
    .sidebar .site-name { display: none; }
    .sidebar .nav-links { padding-top: 16px; flex-direction: column; gap: 8px; }
    .sidebar .nav-links a { font-size: 12px; }
    .sidebar .social-links { padding-bottom: 20px; margin-top: 8px; }
    .social-links a { font-size: 11px; }
}

/* ── Main Content ── */
.main-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    min-height: 100vh;
    animation: gentleFade 1s ease-out 0.3s both;
    margin-left: -130px; /* Offset sidebar width to center content */
}

.hero-text {
    text-align: center;
    position: relative;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
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
    transition: letter-spacing 0.3s ease;
}
.hero-text h1:hover {
    letter-spacing: 0px;
}

/* Center */
.layer-black-center {
    color: #000;
    z-index: 11;
    top: 50%;
    left: calc(50% + 7px);
    transform: translate(-50%, -50%);
}

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
    left: calc(50% - 12px);
    transform: translate(-50%, -50%);
}

.layer-blue-top {
    color: var(--blue);
    z-index: 9;
    top: calc(50% - 12rem);
    left: calc(50% + 5px);
    transform: translate(-50%, -50%);
}

.layer-black-top {
    color: #000;
    z-index: 8;
    top: calc(50% - 18rem);
    left: calc(50% - 8px);
    transform: translate(-50%, -50%);
}

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
    left: calc(50% + 14px);
    transform: translate(-50%, -50%);
}

.layer-blue-top-2 {
    color: var(--blue);
    z-index: 6;
    top: calc(50% - 30rem);
    left: calc(50% - 6px);
    transform: translate(-50%, -50%);
}

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
    left: calc(50% + 11px);
    transform: translate(-50%, -50%);
}

.layer-blue-bottom {
    color: var(--blue);
    z-index: 4;
    top: calc(50% + 12rem);
    left: calc(50% - 9px);
    transform: translate(-50%, -50%);
}

.layer-black-bottom {
    color: #000;
    z-index: 3;
    top: calc(50% + 18rem);
    left: calc(50% + 13px);
    transform: translate(-50%, -50%);
}

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
    left: calc(50% - 15px);
    transform: translate(-50%, -50%);
}

.layer-blue-bottom-2 {
    color: var(--blue);
    z-index: 1;
    top: calc(50% + 30rem);
    left: calc(50% + 10px);
    transform: translate(-50%, -50%);
}

@media (max-width: 768px) {
    .main-content { min-height: 60vh; padding: 16px; margin-left: 0; }
    .hero-text { height: 60vh; }
    .hero-text h1 { font-size: 2.5rem; }

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
        <h1 class="layer-blue-top-2" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-pink-top-2" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-black-top" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-blue-top" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-pink-top" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-black-center">KESKESAY</h1>
        <h1 class="layer-pink-bottom" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-blue-bottom" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-black-bottom" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-pink-bottom-2" aria-hidden="true">KESKESAY</h1>
        <h1 class="layer-blue-bottom-2" aria-hidden="true">KESKESAY</h1>
    </div>
</main>
</html>