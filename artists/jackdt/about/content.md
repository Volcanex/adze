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
@keyframes glitch {
    0%, 100% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
}

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
    padding: 80px 60px;
    max-width: 900px;
    animation: pageIn 1s ease-out 0.3s both;
}
.main-content h1 {
    font-style: normal;
    font-weight: 900;
    font-size: 3rem;
    margin-bottom: 24px;
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
    margin-bottom: 16px;
    font-size: 16px;
    line-height: 1.6;
}
.main-content a {
    color: var(--accent);
    font-weight: 700;
    text-decoration: underline;
}
.main-content ul {
    color: var(--text-muted);
    margin-bottom: 16px;
    font-size: 16px;
    line-height: 1.8;
    margin-left: 20px;
}
.main-content li {
    margin-bottom: 8px;
}

.bio-intro {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
}

.music-player {
    margin-top: 24px;
    padding: 24px;
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
}

.track {
    padding: 16px 0;
    border-bottom: 3px solid #000;
    cursor: pointer;
    transition: all 0.1s ease;
}
.track:last-child { border-bottom: none; }
.track:hover {
    padding-left: 8px;
    border-bottom-color: var(--accent);
}

.track-title {
    font-family: var(--heading-font);
    font-size: 18px;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: -0.5px;
}

.track-meta {
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
}

.waveform {
    margin-top: 12px;
    height: 60px;
    display: flex;
    align-items: flex-end;
    gap: 2px;
    opacity: 1;
}

.waveform-bar {
    flex: 1;
    background: var(--accent);
    border-radius: 0;
    transition: all 0.1s ease;
}

.track:hover .waveform-bar {
    opacity: 1;
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
    .music-player { padding: 16px; }
    .waveform { height: 50px; }
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
    <h1>Jack Dennison-Thompson</h1>

    <div class="bio-intro">
        <p><strong>MA Magazine Journalism student at City, University of London</strong>, with a passion for storytelling across music, culture, and current affairs.</p>

        <p>I have hands-on experience at <a href="https://maghrebi.org" target="_blank">maghrebi.org</a>, where I reported on North African current events under award-winning journalist Martin Jay, and through music journalism for The Indiependent and Folk and Honey, where I wrote reviews, features and interviews.</p>

        <p>My work spans news reporting, cultural features, and music journalism—from covering political developments to profiling emerging artists. I'm particularly interested in stories that sit at the intersection of culture, politics, and community.</p>

        <p>Beyond writing, I bring multimedia skills from producing content for my YouTube channel and radio show, alongside proficiency in Adobe Creative Suite, Ableton, and WordPress.</p>
    </div>

    <h2>Experience Highlights</h2>
    <ul>
        <li><strong>Contributing Writer</strong> at Clash Music Group (2026-Present)</li>
        <li><strong>Deputy Multi Media Editor</strong> at GTFO Magazine</li>
        <li><strong>News Intern</strong> at Campaign UK</li>
        <li>Contributor to Maghrebi.org, Folk and Honey, The Indiependent</li>
    </ul>

    <div class="platform-note">
        <strong>This site is an example of what you can build on this platform.</strong>
        <br><br>
        You can create portfolio sites, journalism hubs, music showcases, or custom tools—all hosted for free on Gabriel's servers. The only cost? A custom domain, if you want one.
        <br><br>
        We could pull data directly from your SoundCloud API, create custom audio players with real waveforms, integrate your latest articles, or build any interactive tool you need. The possibilities are endless.
    </div>
</main>
</html>