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

:root {
    --primary: #2a2a28;
    --accent: #7a8a6e;
    --accent-hover: #5d7050;
    --bg: #f5f2ed;
    --border: #e5e0d8;
    --text-muted: #6b6860;
    --text-light: #9a958c;
    --text-font: 'Inter', sans-serif;
    --heading-font: 'Cardo', serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--text-font);
    color: var(--primary);
    background: var(--bg);
    line-height: 1.7;
    font-size: 1.05rem;
    font-weight: 400;
    min-height: 100vh;
    display: flex;
    opacity: 0;
    animation: pageIn 1s ease-out forwards;
}

/* Subtle grain overlay */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 256px 256px;
}

@keyframes pageIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes gentleFade {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--heading-font);
    color: var(--primary);
    line-height: 1.4;
}

a {
    color: var(--primary);
    text-decoration: none;
    transition: color 0.4s ease;
}
a:hover { color: var(--accent); }

/* ── Sidebar ── */
.sidebar {
    width: 260px;
    min-width: 260px;
    min-height: 100vh;
    padding: 48px 36px;
    display: flex;
    flex-direction: column;
    gap: 28px;
    animation: slideRight 0.8s ease-out 0.1s both;
}

.site-name {
    font-family: var(--text-font);
    font-weight: 600;
    font-size: 18px;
    color: var(--primary);
    text-decoration: none;
    display: block;
    letter-spacing: 0.2px;
    transition: color 0.4s ease;
}
.site-name:hover { color: var(--accent); }

/* ── Navigation ── */
.nav-section {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.nav-category {
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    padding: 6px 0;
    transition: color 0.4s ease;
    user-select: none;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.nav-category:hover { color: var(--accent); }

.nav-dropdown {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.5s ease-out;
    padding-left: 0;
    list-style: none;
}
.nav-dropdown.open {
    max-height: 500px;
    margin-top: 4px;
    margin-bottom: 10px;
}
.nav-dropdown li {
    margin-bottom: 4px;
    opacity: 0;
    transform: translateX(-6px);
    transition: opacity 0.35s ease, transform 0.35s ease;
}
.nav-dropdown.open li {
    opacity: 1;
    transform: translateX(0);
}
.nav-dropdown.open li:nth-child(1) { transition-delay: 0.05s; }
.nav-dropdown.open li:nth-child(2) { transition-delay: 0.1s; }
.nav-dropdown.open li:nth-child(3) { transition-delay: 0.15s; }
.nav-dropdown.open li:nth-child(4) { transition-delay: 0.2s; }
.nav-dropdown.open li:nth-child(5) { transition-delay: 0.25s; }
.nav-dropdown.open li:nth-child(6) { transition-delay: 0.3s; }

.nav-dropdown a {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 400;
    padding-left: 8px;
    display: block;
    transition: color 0.3s ease, padding-left 0.3s ease;
}
.nav-dropdown a:hover {
    color: var(--accent);
    padding-left: 14px;
}

.nav-links {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.nav-links a {
    font-size: 14px;
    font-weight: 400;
    display: block;
    transition: color 0.3s ease, padding-left 0.3s ease;
    padding-left: 0;
}
.nav-links a:hover {
    color: var(--accent);
    padding-left: 6px;
}

.social-links {
    display: flex;
    gap: 16px;
    margin-top: auto;
}
.social-links a {
    font-size: 12px;
    color: var(--text-light);
    letter-spacing: 0.5px;
    transition: color 0.4s ease;
}
.social-links a:hover { color: var(--accent); }

/* ── Mobile Menu Button ── */
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
.menu-toggle.active span:nth-child(1) {
    top: 50%;
    transform: translateY(-50%) rotate(45deg);
}
.menu-toggle.active span:nth-child(2) {
    bottom: auto;
    top: 50%;
    transform: translateY(-50%) rotate(-45deg);
}

/* ── Mobile Header ── */
.mobile-header {
    display: none;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    body {
        flex-direction: column;
        font-size: 14px;
    }

    .mobile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        position: sticky;
        top: 0;
        background: var(--bg);
        z-index: 1000;
        border-bottom: 1px solid var(--border);
    }
    .mobile-header .site-name { font-size: 16px; animation: none; }

    .menu-toggle { display: block; }

    .sidebar {
        width: 100%;
        min-width: 100%;
        min-height: 0;
        padding: 0 20px;
        gap: 16px;
        overflow: hidden;
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
    }
    .sidebar.open {
        grid-template-rows: 1fr;
        border-bottom: 1px solid var(--border);
    }
    .sidebar > .sidebar-inner {
        overflow: hidden;
    }
    .sidebar .site-name { display: none; }
    .sidebar .nav-section { padding-top: 16px; }
    .sidebar .social-links { padding-bottom: 20px; margin-top: 8px; }

    .nav-category { font-size: 11px; padding: 5px 0; }
    .nav-dropdown.open { margin-bottom: 6px; }
    .nav-dropdown a { font-size: 12px; }
    .nav-links { flex-direction: column; gap: 8px; margin-top: 4px; }
    .nav-links a { font-size: 12px; }
    .social-links a { font-size: 11px; }
}

/* ── Gallery Grid ── */
.gallery-page {
    flex: 1;
    padding: 48px;
    overflow-y: auto;
}

.gallery-page h1 {
    font-size: clamp(1.5rem, 2vw, 2rem);
    font-weight: 400;
    font-style: italic;
    margin-bottom: 36px;
    animation: gentleFade 0.8s ease-out 0.2s both;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.gallery-tile {
    position: relative;
    overflow: hidden;
    cursor: pointer;
    display: block;
    opacity: 0;
    animation: gentleFade 0.8s ease-out both;
}

.gallery-tile:nth-child(1) { animation-delay: 0.2s; }
.gallery-tile:nth-child(2) { animation-delay: 0.3s; }
.gallery-tile:nth-child(3) { animation-delay: 0.4s; }
.gallery-tile:nth-child(4) { animation-delay: 0.45s; }
.gallery-tile:nth-child(5) { animation-delay: 0.5s; }
.gallery-tile:nth-child(6) { animation-delay: 0.55s; }
.gallery-tile:nth-child(7) { animation-delay: 0.6s; }
.gallery-tile:nth-child(8) { animation-delay: 0.65s; }
.gallery-tile:nth-child(9) { animation-delay: 0.7s; }
.gallery-tile:nth-child(10) { animation-delay: 0.75s; }
.gallery-tile:nth-child(11) { animation-delay: 0.8s; }
.gallery-tile:nth-child(12) { animation-delay: 0.85s; }

.gallery-tile img {
    width: 100%;
    height: 340px;
    object-fit: cover;
    display: block;
    transition: opacity 0.5s ease;
}

.gallery-tile:hover img {
    opacity: 0.85;
}

.gallery-tile .tile-label {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 24px;
    background: linear-gradient(transparent, rgba(0,0,0,0.4));
    color: white;
    opacity: 0;
    transition: opacity 0.5s ease;
}

.gallery-tile:hover .tile-label {
    opacity: 1;
}

.tile-label h3 {
    font-size: 14px;
    font-weight: 500;
    color: white;
    font-family: var(--text-font);
}
.tile-label span {
    font-size: 11px;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: var(--text-font);
}

@media (max-width: 768px) {
    .gallery-page { padding: 20px 16px; }
    .gallery-grid { grid-template-columns: 1fr; gap: 12px; }
    .gallery-tile img { height: 250px; }
}
</style>
<html>
<div class="mobile-header">
    <a href="../home/" class="site-name">Leah Mclaine</a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.sidebar').classList.toggle('open');" aria-label="Menu">
        <span></span>
        <span></span>
    </button>
</div>

<div class="sidebar">
    <div class="sidebar-inner">
    <a href="../home/" class="site-name">Leah Mclaine</a>

    <nav class="nav-section">
        <span class="nav-category" onclick="this.nextElementSibling.classList.toggle('open')">Works</span>
        <ul class="nav-dropdown">
            <li><a href="../facing-east/">Facing East, 2025</a></li>
            <li><a href="../jonis-angel/">Joni's Angel, The Morning of, 2025</a></li>
            <li><a href="../np-in-the-wings/">NP in the wings, 2025</a></li>
            <li><a href="../portrait-study/">Untitled (diptych), 2025</a></li>
            <li><a href="../contemplation/">Contemplation, 2025</a></li>
            <li><a href="../still-object/">Still object (after faith), 2025</a></li>
        </ul>
        <span class="nav-category" onclick="this.nextElementSibling.classList.toggle('open')">Having Had Faith</span>
        <ul class="nav-dropdown">
            <li><a href="../having-had-faith/">Having Had Faith</a></li>
            <li><a href="../joy/">Joy, 2024</a></li>
        </ul>
        <span class="nav-category" onclick="this.nextElementSibling.classList.toggle('open')">Exhibition &amp; Press</span>
        <ul class="nav-dropdown">
            <li><a href="../degree-show/">RCA Degree Show, 2025</a></li>
            <li><a href="../proposition-studios/">Proposition Studios, 2026</a></li>
            <li><a href="../darkroom-notes/">Darkroom notes</a></li>
        </ul>
    </nav>

    <ul class="nav-links">
        <li><a href="../about/">About</a></li>
        <li><a href="../bookings/">Bookings</a></li>
    </ul>

    <div class="social-links">
        <a href="https://instagram.com/leahmclaine">Instagram</a>
    </div>
    </div>
</div>

<main class="gallery-page">
    <h1>All Work</h1>
    <div class="gallery-grid">
        <a href="../facing-east/" class="gallery-tile">
            <img src="../assets/images/artultra-1.jpg" alt="Facing East, 2025">
            <div class="tile-label">
                <h3>Facing East, 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../jonis-angel/" class="gallery-tile">
            <img src="../assets/images/artultra-3.jpg" alt="Joni's Angel, The Morning of, 2025">
            <div class="tile-label">
                <h3>Joni's Angel, The Morning of, 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../np-in-the-wings/" class="gallery-tile">
            <img src="../assets/images/artultra-10.jpg" alt="NP in the wings, 2025">
            <div class="tile-label">
                <h3>NP in the wings, 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../portrait-study/" class="gallery-tile">
            <img src="../assets/images/artultra-2.png" alt="Untitled (diptych), 2025">
            <div class="tile-label">
                <h3>Untitled (diptych), 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../contemplation/" class="gallery-tile">
            <img src="../assets/images/artultra-8.png" alt="Contemplation, 2025">
            <div class="tile-label">
                <h3>Contemplation, 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../still-object/" class="gallery-tile">
            <img src="../assets/images/artultra-9.png" alt="Still object (after faith), 2025">
            <div class="tile-label">
                <h3>Still object (after faith), 2025</h3>
                <span>Works</span>
            </div>
        </a>
        <a href="../having-had-faith/" class="gallery-tile">
            <img src="../assets/images/having-had-faith-2.jpg" alt="Having Had Faith">
            <div class="tile-label">
                <h3>Having Had Faith</h3>
                <span>Having Had Faith</span>
            </div>
        </a>
        <a href="../joy/" class="gallery-tile">
            <img src="../assets/images/artultra-4.png" alt="Joy, 2024">
            <div class="tile-label">
                <h3>Joy, 2024</h3>
                <span>Having Had Faith</span>
            </div>
        </a>
        <a href="../degree-show/" class="gallery-tile">
            <img src="../assets/images/exhibition.jpg" alt="RCA Degree Show, 2025">
            <div class="tile-label">
                <h3>RCA Degree Show, 2025</h3>
                <span>Exhibition &amp; Press</span>
            </div>
        </a>
        <a href="../proposition-studios/" class="gallery-tile">
            <img src="../assets/images/having-had-faith-1.jpg" alt="Proposition Studios, 2026">
            <div class="tile-label">
                <h3>Proposition Studios, 2026</h3>
                <span>Exhibition &amp; Press</span>
            </div>
        </a>
        <a href="../darkroom-notes/" class="gallery-tile">
            <img src="../assets/images/shaving-head.jpg" alt="Darkroom notes">
            <div class="tile-label">
                <h3>Darkroom notes</h3>
                <span>Exhibition &amp; Press</span>
            </div>
        </a>
    </div>
</main>
</html>