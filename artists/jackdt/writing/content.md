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
    padding: 80px 60px;
    max-width: 900px;
    animation: pageIn 1s ease-out 0.3s both;
}

.main-content h1 {
    font-style: normal;
    font-weight: 900;
    font-size: 3rem;
    margin-bottom: 32px;
    letter-spacing: -2px;
    text-transform: uppercase;
}

.main-content h2 {
    font-style: normal;
    font-weight: 900;
    font-size: 2rem;
    margin-top: 48px;
    margin-bottom: 20px;
    letter-spacing: -1px;
    text-transform: uppercase;
}

.main-content p {
    color: var(--text-muted);
    margin-bottom: 24px;
    font-size: 16px;
    line-height: 1.7;
}

.article-grid {
    display: grid;
    gap: 24px;
    margin-top: 40px;
}

.article-card {
    padding: 28px;
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
    transition: all 0.1s ease;
    cursor: pointer;
}

.article-card:hover {
    border-color: var(--accent);
    transform: translateX(3px);
}

.article-meta {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: -0.3px;
    margin-bottom: 12px;
}

.article-title {
    font-family: var(--heading-font);
    font-size: 24px;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 12px;
    letter-spacing: -1px;
    text-transform: uppercase;
    line-height: 1.2;
}

.article-excerpt {
    color: var(--text-muted);
    font-size: 15px;
    line-height: 1.6;
    margin-bottom: 16px;
}

.article-link {
    font-size: 14px;
    font-weight: 700;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: -0.5px;
    border-bottom: 2px solid #000;
    display: inline-block;
    transition: all 0.1s ease;
}

.article-link:hover {
    color: var(--accent);
    border-bottom-color: var(--accent);
}

.platform-note {
    margin-top: 48px;
    padding: 24px 28px;
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-muted);
}

.platform-note strong {
    color: var(--primary);
    font-weight: 900;
    text-transform: uppercase;
}

@media (max-width: 768px) {
    .main-content { padding: 32px 20px; }
    .main-content h1 { font-size: 1.8rem; }
    .main-content h2 { font-size: 1.5rem; margin-top: 36px; }
    .article-card { padding: 20px; }
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
    <h1>Writing</h1>

    <div class="article-grid">
        <div class="article-card">
            <div class="article-meta">Clash Music • Feb 2026</div>
            <h2 class="article-title">The New Sound of London</h2>
            <p class="article-excerpt">Exploring the underground electronic scene reshaping the city's nightlife, from warehouse raves to experimental noise collectives.</p>
            <a href="#" class="article-link">Read Article →</a>
        </div>

        <div class="article-card">
            <div class="article-meta">GTFO Magazine • Jan 2026</div>
            <h2 class="article-title">Gonzo in the Digital Age</h2>
            <p class="article-excerpt">How Hunter S. Thompson's legacy lives on in modern music journalism, and why truth is stranger than fiction in 2026.</p>
            <a href="#" class="article-link">Read Article →</a>
        </div>

        <div class="article-card">
            <div class="article-meta">The Indiependent • Dec 2025</div>
            <h2 class="article-title">Aphex Twin at 50</h2>
            <p class="article-excerpt">A retrospective on Richard D. James' influence on experimental electronic music and the artists carrying his torch forward.</p>
            <a href="#" class="article-link">Read Article →</a>
        </div>
    </div>

    <div class="platform-note">
        <strong>This page can be customized to pull from any CMS or data source</strong>
        <br><br>
        We can integrate with WordPress, Notion, Google Sheets, or any custom API to automatically populate your articles. Add filters by category, search functionality, or feature your latest work dynamically.
    </div>
</main>
</html>
