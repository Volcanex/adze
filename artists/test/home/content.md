<meta property="og:title" content="✨ Cosmic Dreams">
<meta property="og:description" content="Enter the celestial realm">
<meta property="og:image" content="../assets/images/og.jpg">

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

:root {
    --primary: #ffffff;
    --accent: #ff6ec7;
    --accent-glow: #a855f7;
    --accent-hover: #ff8fd4;
    --bg: #0a0118;
    --bg-overlay: rgba(10, 1, 24, 0.85);
    --border: rgba(255, 255, 255, 0.1);
    --text-muted: #c4b5fd;
    --text-light: #a78bfa;
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
    animation: pageIn 1.2s ease-out forwards;
    position: relative;
    overflow-x: hidden;
}

/* Animated Starfield Background */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse at top, rgba(138, 43, 226, 0.15), transparent 50%),
        radial-gradient(ellipse at bottom right, rgba(255, 20, 147, 0.1), transparent 50%),
        radial-gradient(ellipse at bottom left, rgba(138, 43, 226, 0.12), transparent 50%);
    animation: nebulaPulse 20s ease-in-out infinite alternate;
}

body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 1;
    background-image:
        radial-gradient(2px 2px at 20% 30%, white, transparent),
        radial-gradient(2px 2px at 60% 70%, white, transparent),
        radial-gradient(1px 1px at 50% 50%, white, transparent),
        radial-gradient(1px 1px at 80% 10%, white, transparent),
        radial-gradient(2px 2px at 90% 60%, white, transparent),
        radial-gradient(1px 1px at 33% 80%, white, transparent),
        radial-gradient(1px 1px at 15% 60%, white, transparent);
    background-size: 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%;
    background-position: 0% 0%, 40% 40%, 80% 80%, 20% 60%, 60% 20%, 10% 90%, 90% 10%;
    animation: starsMove 80s linear infinite;
    opacity: 0.6;
}

.shooting-star {
    position: fixed;
    width: 2px;
    height: 2px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 0 4px 2px rgba(255, 255, 255, 0.8);
    z-index: 2;
    animation: shoot 3s linear infinite;
    opacity: 0;
}

.shooting-star::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 1px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.8) 100%);
}

.shooting-star:nth-child(1) { top: 10%; left: 20%; animation-delay: 0s; }
.shooting-star:nth-child(2) { top: 30%; left: 60%; animation-delay: 4s; }
.shooting-star:nth-child(3) { top: 60%; left: 10%; animation-delay: 8s; }

@keyframes shoot {
    0% { transform: translate(0, 0); opacity: 1; }
    70% { opacity: 1; }
    100% { transform: translate(300px, 300px); opacity: 0; }
}

.cosmic-orb {
    position: fixed;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, rgba(255, 110, 199, 0.3), rgba(168, 85, 247, 0.2), transparent);
    filter: blur(60px);
    z-index: 0;
    animation: orbFloat 15s ease-in-out infinite;
    pointer-events: none;
}

.cosmic-orb-1 { top: -100px; right: -100px; }
.cosmic-orb-2 { bottom: -100px; left: -100px; animation-delay: -7s; }

@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
    50% { transform: translate(50px, 50px) scale(1.1); opacity: 0.5; }
}

@keyframes starsMove {
    0% { transform: translate(0, 0); }
    100% { transform: translate(-50px, -50px); }
}

@keyframes nebulaPulse {
    0% { opacity: 0.6; transform: scale(1) rotate(0deg); }
    100% { opacity: 0.9; transform: scale(1.1) rotate(5deg); }
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes gentleFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideRight { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes glow {
    0%, 100% { text-shadow: 0 0 20px rgba(255, 110, 199, 0.5), 0 0 40px rgba(168, 85, 247, 0.3); }
    50% { text-shadow: 0 0 30px rgba(255, 110, 199, 0.8), 0 0 60px rgba(168, 85, 247, 0.5); }
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--heading-font);
    color: var(--primary);
    line-height: 1.4;
}

a { color: var(--primary); text-decoration: none; transition: all 0.4s ease; }
a:hover { color: var(--accent); text-shadow: 0 0 10px rgba(255, 110, 199, 0.5); }

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
    background: var(--bg-overlay);
    backdrop-filter: blur(10px);
    border-right: 1px solid var(--border);
    position: relative;
    z-index: 10;
}

.site-name {
    font-family: var(--heading-font);
    font-weight: 600;
    font-size: 20px;
    color: var(--primary);
    text-decoration: none;
    display: block;
    letter-spacing: 1px;
    transition: all 0.4s ease;
    text-transform: uppercase;
}
.site-name:hover {
    color: var(--accent);
    text-shadow: 0 0 20px rgba(255, 110, 199, 0.6);
}

/* ── Navigation ── */
.nav-links {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.nav-links a {
    font-size: 14px;
    font-weight: 400;
    display: block;
    transition: all 0.3s ease;
    padding-left: 0;
    color: var(--text-muted);
}
.nav-links a:hover {
    color: var(--accent);
    padding-left: 8px;
    text-shadow: 0 0 10px rgba(255, 110, 199, 0.4);
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
    transition: all 0.4s ease;
    text-transform: uppercase;
}
.social-links a:hover {
    color: var(--accent);
    text-shadow: 0 0 10px rgba(255, 110, 199, 0.4);
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
    box-shadow: 0 0 5px rgba(255, 110, 199, 0.5);
}
.menu-toggle span:nth-child(1) { top: 4px; }
.menu-toggle span:nth-child(2) { bottom: 4px; }
.menu-toggle.active span:nth-child(1) { top: 50%; transform: translateY(-50%) rotate(45deg); }
.menu-toggle.active span:nth-child(2) { bottom: auto; top: 50%; transform: translateY(-50%) rotate(-45deg); }

.mobile-header { display: none; }

@media (max-width: 768px) {
    body { flex-direction: column; font-size: 14px; }

    .mobile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        position: sticky;
        top: 0;
        background: var(--bg-overlay);
        backdrop-filter: blur(10px);
        z-index: 1000;
        border-bottom: 1px solid var(--border);
    }
    .mobile-header .site-name { font-size: 16px; animation: none; }
    .menu-toggle { display: block; }

    .sidebar {
        width: 100%; min-width: 100%; min-height: 0;
        padding: 0 20px; gap: 16px; overflow: hidden;
        display: grid; grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
        border-right: none;
        border-bottom: 1px solid var(--border);
    }
    .sidebar.open { grid-template-rows: 1fr; }
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
    position: relative;
    z-index: 5;
}

.hero-text {
    text-align: center;
    animation: slideUp 0.8s ease-out 0.5s both;
    max-width: 700px;
}
.hero-text h1 {
    font-style: italic;
    font-weight: 400;
    font-size: 3.5rem;
    margin-bottom: 24px;
    background: linear-gradient(135deg, #ffffff 0%, #ff6ec7 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: glow 3s ease-in-out infinite;
    letter-spacing: 2px;
}
.hero-text p {
    color: var(--text-muted);
    font-size: 16px;
    margin-bottom: 32px;
    letter-spacing: 0.5px;
}
.hero-text .cta-button {
    display: inline-block;
    padding: 14px 32px;
    background: linear-gradient(135deg, #ff6ec7, #a855f7);
    color: white;
    font-weight: 600;
    font-size: 14px;
    border-radius: 30px;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.4s ease;
    box-shadow: 0 0 20px rgba(255, 110, 199, 0.4);
}
.hero-text .cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(255, 110, 199, 0.7), 0 0 60px rgba(168, 85, 247, 0.4);
    color: white;
    text-shadow: none;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 24px;
    margin-top: 60px;
    max-width: 900px;
}

.feature-card {
    background: var(--bg-overlay);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 24px;
    text-align: center;
    transition: all 0.4s ease;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.1);
}

.feature-card:hover {
    transform: translateY(-8px);
    border-color: rgba(255, 110, 199, 0.5);
    box-shadow: 0 0 40px rgba(255, 110, 199, 0.3), 0 0 80px rgba(168, 85, 247, 0.2);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 16px;
    filter: drop-shadow(0 0 10px rgba(255, 110, 199, 0.6));
}

.feature-card h3 {
    font-size: 1.2rem;
    margin-bottom: 12px;
    color: var(--accent);
    letter-spacing: 0.5px;
}

.feature-card p {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.6;
}

@media (max-width: 768px) {
    .main-content { min-height: 60vh; padding: 16px; }
    .hero-text h1 { font-size: 2.2rem; }
    .hero-text p { font-size: 14px; }
    .features-grid { grid-template-columns: 1fr; gap: 16px; margin-top: 40px; }
    .feature-card { padding: 24px 20px; }
}
</style>
<html>
<div class="mobile-header">
    <a href="../home/" class="site-name">Cosmic</a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.sidebar').classList.toggle('open');" aria-label="Menu">
        <span></span>
        <span></span>
    </button>
</div>

<div class="cosmic-orb cosmic-orb-1"></div>
<div class="cosmic-orb cosmic-orb-2"></div>

<div class="shooting-star"></div>
<div class="shooting-star"></div>
<div class="shooting-star"></div>

<div class="sidebar">
    <div class="sidebar-inner">
    <a href="../home/" class="site-name">Cosmic</a>

    <ul class="nav-links">
        <li><a href="../home/">Home</a></li>
        <li><a href="../about/">About</a></li>
    </ul>

    <div class="social-links">
        <a href="#">OnlyFans</a>
        <a href="#">Instagram</a>
        <a href="#">Twitter</a>
    </div>
    </div>
</div>

<main class="main-content">
    <div class="hero-text">
        <h1>✨ Cosmic Dreams</h1>
        <p>Welcome to my celestial realm • Exclusive content • Subscribe for the stars</p>
        <a href="#" class="cta-button">Enter the Galaxy</a>

        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🌙</div>
                <h3>Exclusive</h3>
                <p>Premium content you won't find anywhere else</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💫</div>
                <h3>Daily Posts</h3>
                <p>New magic delivered every single day</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💌</div>
                <h3>Personal</h3>
                <p>Direct chat access and custom content</p>
            </div>
        </div>
    </div>
</main>
</html>
