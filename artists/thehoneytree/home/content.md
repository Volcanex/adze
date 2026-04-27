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
html { scroll-behavior: smooth; }
body {
    font-family: var(--text-font);
    color: var(--primary);
    background: var(--bg);
    line-height: var(--body-line-height);
    font-size: var(--body-size);
    font-weight: var(--body-weight);
    min-height: 100vh;
    opacity: 0;
    animation: pageIn 0.9s ease-out forwards;
    overflow-x: hidden;
}
body::before {
    content: '';
    position: fixed; inset: 0;
    pointer-events: none; z-index: 9999;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
}
@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

h1, h2, h3, h4 { font-family: var(--heading-font); color: var(--primary); line-height: var(--heading-line-height); }
h1 { font-size: var(--h1-size); font-weight: var(--h1-weight); }
h2 { font-size: var(--h2-size); font-weight: var(--h2-weight); margin-top: 36px; margin-bottom: 14px; }
h3 { font-size: var(--h3-size); font-weight: var(--h3-weight); margin-top: 22px; margin-bottom: 8px; }
a { color: var(--primary); text-decoration: none; transition: color 0.3s ease; }
a:hover { color: var(--accent); }

/* ── Navbar ── */
.navbar {
    position: sticky; top: 0; z-index: 100;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(16px) saturate(1.2);
    -webkit-backdrop-filter: blur(16px) saturate(1.2);
    border-bottom: 1px solid color-mix(in oklch, var(--border) 60%, transparent);
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 40px;
}
.navbar .logo {
    font-family: var(--heading-font);
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 0.3px;
    color: var(--primary);
    line-height: 1;
}
.navbar .logo small {
    display: block;
    font-family: var(--text-font);
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-light);
    margin-top: 4px;
}
.nav-links {
    list-style: none; display: flex; gap: 28px; align-items: center;
}
.nav-links a {
    font-size: 14px;
    font-weight: 400;
    color: var(--primary);
    position: relative;
    padding: 6px 0;
    transition: color 0.3s ease;
}
.nav-links a::after {
    content: ''; position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 1px; background: var(--accent);
    transform: scaleX(0); transform-origin: left;
    transition: transform 0.35s cubic-bezier(.2,.8,.2,1);
}
.nav-links a:hover::after, .nav-links a.active::after { transform: scaleX(1); }
.nav-links a.active { color: var(--accent); }
.nav-links .order-cta {
    background: var(--accent);
    color: var(--bg) !important;
    padding: 8px 18px;
    border-radius: 999px;
    font-weight: 500;
    font-size: 13px;
    transition: background 0.3s ease, color 0.3s ease, transform 0.3s ease;
}
.nav-links .order-cta:hover {
    background: var(--accent-hover);
    color: var(--bg) !important;
    transform: translateY(-1px);
}
.nav-links .order-cta::after { display: none; }

.menu-toggle {
    display: none;
    background: none; border: none; cursor: pointer;
    width: 36px; height: 28px; position: relative; z-index: 1001;
    padding: 0;
}
.menu-toggle span {
    display: block; width: 100%; height: 3px;
    background: var(--primary); position: absolute; left: 0;
    border-radius: 3px;
    transition: transform 0.35s ease, opacity 0.25s ease, top 0.35s ease;
}
.menu-toggle span:nth-child(1) { top: 4px; }
.menu-toggle span:nth-child(2) { top: 50%; transform: translateY(-50%); }
.menu-toggle span:nth-child(3) { bottom: 4px; top: auto; }
.menu-toggle.active span:nth-child(1) { top: 50%; transform: translateY(-50%) rotate(45deg); }
.menu-toggle.active span:nth-child(2) { opacity: 0; }
.menu-toggle.active span:nth-child(3) { top: 50%; bottom: auto; transform: translateY(-50%) rotate(-45deg); }

@media (max-width: 820px) {
    .navbar { padding: 14px 20px; }
    .menu-toggle { display: block; }
    .nav-links {
        position: fixed;
        top: 70px; left: 0; right: 0;
        background: var(--bg-soft);
        flex-direction: column;
        align-items: stretch;
        gap: 0;
        padding: 0 20px;
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.5s cubic-bezier(.2,.8,.2,1), padding 0.3s ease;
    }
    .nav-links.open { max-height: 500px; padding: 12px 20px 24px; border-bottom: 1px solid var(--border); }
    .nav-links li { border-bottom: 1px solid var(--border); }
    .nav-links li:last-child { border-bottom: none; margin-top: 10px; }
    .nav-links a { display: block; padding: 14px 0; font-size: 15px; }
    .nav-links a::after { display: none; }
    .nav-links .order-cta { text-align: center; padding: 12px 18px; }
}

/* ── Page container ── */
.page {
    max-width: 900px;
    margin: 0 auto;
    padding: 64px 40px 120px;
}
.page h1 { font-style: italic; margin-bottom: 12px; font-size: clamp(2rem, 4.5vw, 3rem); }
.page > .eyebrow {
    font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 16px;
    font-weight: 500;
}
.page .lede {
    font-family: var(--heading-font);
    font-style: italic;
    font-size: 1.35rem;
    color: var(--text-muted);
    line-height: 1.5;
    margin: 0 0 36px;
    max-width: 620px;
}
.page p { color: var(--text-muted); margin-bottom: 18px; line-height: 1.8; max-width: 640px; }
.page ul, .page ol { color: var(--text-muted); margin: 0 0 20px 22px; line-height: 1.8; max-width: 620px; }
.page li { margin-bottom: 6px; }
.page a { color: var(--accent); border-bottom: 1px dotted var(--accent); }
.page a:hover { color: var(--accent-hover); border-color: var(--accent-hover); }

/* ── Scroll-driven reveals (falls back gracefully in Firefox) ── */
@supports (animation-timeline: view()) {
    .reveal {
        animation: revealUp linear both;
        animation-timeline: view();
        animation-range: entry 0% cover 35%;
    }
}
@keyframes revealUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Hero (home) ── */
.hero {
    position: relative;
    min-height: calc(100vh - 64px);
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    padding: 80px 40px 60px;
    background: var(--bg-soft);
}
.hero-bg {
    position: absolute; inset: 0;
    background: url('../assets/images/simon_looking_at_veg_.webp') center 35% / cover no-repeat;
    z-index: 0;
    will-change: transform;
}
.hero-bg::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(251,251,246,0) 35%, rgba(251,251,246,0.55) 70%, rgba(251,251,246,0.95) 100%);
}
@supports (animation-timeline: scroll()) {
    .hero-bg {
        animation: heroParallax linear;
        animation-timeline: scroll(root);
        animation-range: 0 100vh;
    }
}
@keyframes heroParallax {
    from { transform: translateY(0) scale(1.05); }
    to   { transform: translateY(18vh) scale(1.15); }
}
.hero-inner {
    position: relative; z-index: 1;
    max-width: 960px; margin: 0 auto; width: 100%;
}
.hero-mark {
    font-family: var(--heading-font);
    font-style: italic;
    font-size: clamp(3rem, 9vw, 6.5rem);
    line-height: 0.95;
    color: var(--primary);
    letter-spacing: -0.5px;
    text-shadow: 0 2px 30px rgba(251,251,246,0.6);
}
.hero-tag {
    margin-top: 14px;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-muted);
}
.hero-tag span { color: var(--accent); font-weight: 600; }
.hero-scroll {
    position: absolute;
    bottom: 24px; right: 40px;
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-muted);
    display: flex; align-items: center; gap: 10px;
    z-index: 2;
}
.hero-scroll::after {
    content: ''; width: 40px; height: 1px; background: var(--text-muted);
    animation: scrollLine 2.4s ease-in-out infinite;
}
@keyframes scrollLine { 0%, 100% { transform: scaleX(0.3); transform-origin: left; } 50% { transform: scaleX(1); transform-origin: left; } }

/* ── Home sections ── */
.section { padding: 100px 40px; max-width: 1100px; margin: 0 auto; }
.section .eyebrow {
    font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 18px; font-weight: 500;
}
.section-title {
    font-family: var(--heading-font);
    font-style: italic;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    line-height: 1.15;
    margin-bottom: 28px;
    max-width: 720px;
}
.section-title em { color: var(--accent); font-style: italic; }

.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
}
.two-col .img-wrap {
    aspect-ratio: 4/5;
    overflow: hidden;
    border-radius: 4px;
}
.two-col .img-wrap img {
    width: 100%; height: 100%;
    object-fit: cover;
    transition: transform 1.2s ease;
}
.two-col .img-wrap:hover img { transform: scale(1.04); }
.two-col p { color: var(--text-muted); line-height: 1.8; margin-bottom: 18px; }
.two-col.reverse { direction: rtl; }
.two-col.reverse > * { direction: ltr; }

@media (max-width: 820px) {
    .two-col { grid-template-columns: 1fr; gap: 32px; }
    .two-col.reverse { direction: ltr; }
}

/* ── Marquee strip ── */
.marquee {
    overflow: hidden;
    padding: 32px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    background: var(--bg-soft);
    white-space: nowrap;
}
.marquee-track {
    display: inline-flex; gap: 48px;
    animation: scrollMarquee 40s linear infinite;
    font-family: var(--heading-font);
    font-style: italic;
    font-size: 1.6rem;
    color: var(--text-muted);
}
.marquee-track span { display: inline-flex; align-items: center; gap: 48px; }
.marquee-track .dot { width: 6px; height: 6px; background: var(--accent); border-radius: 50%; display: inline-block; }
@keyframes scrollMarquee {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}

/* ── Auto-scrolling image rail (infinite loop, no user scroll) ── */
.image-rail-wrap {
    overflow: hidden;
    padding: 8px 0 40px;
    -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%);
            mask-image: linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%);
}
.image-rail {
    display: flex;
    gap: 24px;
    width: max-content;
    animation: railLoop 70s linear infinite;
    will-change: transform;
}
@keyframes railLoop {
    /* Stride = exactly half the track + one gap-width, so card 6 lands where card 1 started. */
    from { transform: translate3d(0, 0, 0); }
    to   { transform: translate3d(calc(-50% - 12px), 0, 0); }
}
.image-rail .card {
    flex: 0 0 320px;
}
.image-rail .card .pic {
    width: 100%;
    aspect-ratio: 4/5;
    overflow: hidden;
    border-radius: 4px;
}
.image-rail .card .pic img {
    width: 100%; height: 100%; object-fit: cover;
    transition: transform 1s ease;
}
.image-rail .card:hover .pic img { transform: scale(1.04); }
@media (max-width: 560px) { .image-rail .card { flex: 0 0 70vw; } }
@media (prefers-reduced-motion: reduce) { .image-rail { animation: none; } }

/* ── Quote / pull ── */
.pull-quote {
    padding: 120px 40px;
    max-width: 900px; margin: 0 auto;
    text-align: center;
}
.pull-quote blockquote {
    font-family: var(--heading-font);
    font-style: italic;
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    line-height: 1.35;
    color: var(--primary);
    max-width: 720px;
    margin: 0 auto;
}
.pull-quote blockquote::before, .pull-quote blockquote::after {
    content: '"';
    color: var(--accent);
    font-size: 2em;
    line-height: 0;
    vertical-align: -0.2em;
}
.pull-quote cite {
    display: block;
    margin-top: 28px;
    font-style: normal;
    font-size: 11px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--text-light);
}

/* ── Portrait pair (About / Staff) ── */
.portrait-pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin: 36px 0 40px;
    max-width: 720px;
}
.portrait-pair figure { margin: 0; }
.portrait-pair .portrait {
    aspect-ratio: 4/5;
    overflow: hidden;
    border-radius: 4px;
    background: var(--bg-soft);
}
.portrait-pair .portrait img {
    width: 100%; height: 100%;
    object-fit: cover; object-position: center 30%;
    transition: transform 1s ease;
}
.portrait-pair figure:hover .portrait img { transform: scale(1.03); }
.portrait-pair figcaption {
    margin-top: 12px;
    font-size: 14px;
    line-height: 1.4;
}
.portrait-pair figcaption strong {
    display: block;
    font-family: var(--heading-font);
    font-size: 1.05rem;
    font-weight: 400;
    color: var(--primary);
}
.portrait-pair figcaption span {
    display: block;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--accent);
    margin-top: 4px;
}
@media (max-width: 560px) {
    .portrait-pair { grid-template-columns: 1fr; gap: 24px; max-width: 360px; }
}

/* ── Staff grid (placeholders) ── */
.staff-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin: 24px 0 32px;
    max-width: 640px;
}
.staff-card {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
}
.staff-card .ph-portrait {
    aspect-ratio: 4/5;
    background: repeating-linear-gradient(
        45deg,
        var(--border) 0 12px,
        transparent 12px 24px
    );
    opacity: 0.5;
}
.staff-card .ph-meta {
    padding: 12px 16px;
    font-size: 13px;
}
.staff-card .ph-meta strong {
    display: block;
    font-family: var(--heading-font);
    font-style: italic;
    font-weight: 400;
    color: var(--text-muted);
}
.staff-card .ph-meta span {
    font-size: 11px;
    letter-spacing: 1.5px;
    color: var(--text-light);
}
@media (max-width: 560px) { .staff-grid { grid-template-columns: 1fr; max-width: 320px; } }

/* ── Info card ── */
.info-card {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 24px 28px;
    margin: 22px 0;
    max-width: 620px;
}
.info-card h3 { margin-top: 0; }
.info-card p:last-child { margin-bottom: 0; }

/* ── Hours list ── */
.hours-list { list-style: none !important; margin: 0 0 28px !important; padding: 0; border-top: 1px solid var(--border); max-width: 520px; }
.hours-list li {
    list-style: none;
    display: flex; justify-content: space-between;
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 1rem;
}
.hours-list li.closed { color: var(--text-light); font-style: italic; }
.hours-list li.open-now { background: color-mix(in oklch, var(--accent) 12%, transparent); padding-left: 14px; padding-right: 14px; margin: 0 -14px; border-radius: 4px; }
.hours-list .day { font-weight: 500; color: var(--primary); font-family: var(--heading-font); }
.hours-list .day .badge {
    display: inline-block; margin-left: 8px;
    font-family: var(--text-font); font-weight: 500;
    font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--accent);
}

/* ── Box grid ── */
.box-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 24px 0 32px; max-width: 640px; }
.box-grid .box {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 22px 24px;
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.box-grid .box:hover { transform: translateY(-3px); border-color: var(--accent); }
.box-grid .box h3 { margin: 0 0 6px; font-size: 1.05rem; font-family: var(--heading-font); }
.box-grid .box .price { font-family: var(--heading-font); font-size: 1.5rem; color: var(--honey); font-style: italic; }
.box-grid .box small { display: block; font-size: 12px; color: var(--text-light); margin-top: 4px; }
@media (max-width: 560px) { .box-grid { grid-template-columns: 1fr; } }

/* ── Map section ── */
.map-section { padding: 100px 40px; max-width: 1100px; margin: 0 auto; }
.map-card {
    position: relative;
    border-radius: var(--border-radius);
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--bg-soft);
    aspect-ratio: 16 / 9;
    box-shadow: 0 18px 40px -28px color-mix(in oklch, var(--primary) 25%, transparent);
}
.map-card iframe {
    width: 100%; height: 100%;
    border: 0;
    display: block;
    filter: saturate(0.85) contrast(0.96);
}
.map-overlay {
    position: absolute;
    left: 24px; bottom: 24px;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: var(--border-radius);
    padding: 18px 22px;
    max-width: 340px;
    box-shadow: 0 10px 30px -16px color-mix(in oklch, var(--primary) 35%, transparent);
}
.map-overlay .name {
    font-family: var(--heading-font);
    font-size: 1.1rem;
    color: var(--primary);
    margin-bottom: 4px;
}
.map-overlay .addr {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.5;
    margin-bottom: 14px;
}
.map-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.map-actions a {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--primary);
    color: var(--bg) !important;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.3px;
    padding: 8px 14px;
    border-radius: 999px;
    border: none !important;
    transition: background 0.3s ease, transform 0.3s ease;
}
.map-actions a.alt {
    background: transparent;
    color: var(--primary) !important;
    border: 1px solid var(--border) !important;
}
.map-actions a:hover {
    background: var(--accent);
    color: var(--bg) !important;
    transform: translateY(-1px);
}
.map-actions a svg { width: 12px; height: 12px; flex-shrink: 0; }
@media (max-width: 640px) {
    .map-section { padding: 64px 24px; }
    .map-card { aspect-ratio: 4 / 5; }
    .map-overlay { left: 16px; right: 16px; bottom: 16px; max-width: none; padding: 16px 18px; }
}

/* ── Notice / callout ── */
.notice {
    background: color-mix(in oklch, var(--accent) 8%, transparent);
    border-left: 3px solid var(--accent);
    padding: 16px 20px;
    border-radius: 4px;
    margin: 0 0 28px;
    color: var(--text-muted);
    font-size: 0.97rem;
    max-width: 640px;
}
.notice strong { color: var(--primary); }

/* ── Update items ── */
.update-item {
    padding: 28px 0;
    border-bottom: 1px solid var(--border);
    max-width: 720px;
}
.update-item:last-child { border-bottom: none; }
.update-item h2 { margin-top: 0; font-style: italic; font-family: var(--heading-font); }
.update-item .date {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--accent); font-weight: 500;
    margin-bottom: 10px; display: block;
}

/* ── Footer ── */
.footer {
    border-top: 1px solid var(--border);
    background: var(--bg-soft);
    padding: 48px 40px 32px;
    margin-top: 80px;
}
.footer-inner {
    max-width: 1100px; margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 40px;
    font-size: 13px;
    color: var(--text-muted);
}
.footer-inner h4 {
    font-family: var(--text-font);
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-light); font-weight: 500;
    margin-bottom: 12px;
}
.footer-inner p { margin-bottom: 6px; color: var(--text-muted); }
.footer-inner a { color: var(--text-muted); }
.footer-inner a:hover { color: var(--accent); }
.footer-logo {
    font-family: var(--heading-font);
    font-weight: 700;
    font-size: 18px;
    color: var(--primary);
    display: block;
    margin-bottom: 10px;
}
.footer-bottom {
    max-width: 1100px; margin: 36px auto 0;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-light); letter-spacing: 0.5px;
}
@media (max-width: 640px) {
    .footer-inner { grid-template-columns: 1fr; gap: 28px; }
    .footer-bottom { flex-direction: column; gap: 8px; }
}

/* ── Mobile tweaks ── */
@media (max-width: 820px) {
    .section { padding: 64px 24px; }
    .page { padding: 40px 24px 80px; }
    .hero { padding: 40px 24px 40px; }
    .hero-bg { background-position: left 35%; }
    .hero-scroll { display: none; }
    .image-rail { padding: 0 24px 32px; }
    .pull-quote { padding: 80px 24px; }
}
</style>

<html>
<header class="navbar">
    <a href="../home/" class="logo">The Honey Tree<small>Wholefoods · Heaton · Est. 1999</small></a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.nav-links').classList.toggle('open');" aria-label="Menu">
        <span></span><span></span><span></span>
    </button>
    <ul class="nav-links">
        <li><a href="../home/" class="active">Home</a></li>
            <li><a href="../about/">About</a></li>
            <li><a href="../opening-hours/">Opening Hours</a></li>
            <li><a href="../updates/">Updates</a></li>
            <li><a href="../contact/">Contact</a></li>
        <li><a href="../order/" class="order-cta">Order a Box</a></li>
    </ul>
</header>

<section class="hero">
    <div class="hero-bg"></div>
    <div class="hero-inner">
        <h1 class="hero-mark">The Honey<br>Tree</h1>
        <div class="hero-tag"><span>Organic Grocery</span> · Heaton, Newcastle · Since 1999</div>
    </div>
    <div class="hero-scroll">Scroll</div>
</section>

<section class="section reveal">
    <div class="eyebrow">A not for profit</div>
    <h2 class="section-title">A wholefoods shop on Heaton Road, <em>feeding</em> the neighbourhood since 1999.</h2>
    <div class="two-col">
        <div class="img-wrap"><img src="../assets/images/622923291_18198316384332982_5503559511187734945_n.jpg" alt="Inside The Honey Tree" loading="lazy"></div>
        <div>
            <p>We're an independent, not-for-profit health food shop. Fresh fruit and veg from organic growers, a full range of everyday groceries, refill stations for beauty and cleaning, and a counter of loose wholefoods &mdash; rice, pasta, pulses, grains &mdash; scooped by the gram.</p>
            <p>Nothing flashy. Just real food, sold with care, chosen with the welfare of everyone in the chain in mind. The growers, the makers, the people who carry it across the world and down the road to us.</p>
            <p><a href="../about/">More about the shop →</a></p>
        </div>
    </div>
</section>

<section class="reveal image-rail-wrap" aria-hidden="true">
    <div class="image-rail">
        <div class="card"><div class="pic"><img src="../assets/images/pruple_cabbage.png" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/626846214_18405103573132403_1607913087320371059_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/619488496_18109680952733106_5126638735837564642_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/629259710_18379669267093299_3611023350833716371_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/honeytree_shop_front_.webp" alt="" loading="lazy"></div></div>
        <!-- duplicated for seamless loop -->
        <div class="card"><div class="pic"><img src="../assets/images/pruple_cabbage.png" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/626846214_18405103573132403_1607913087320371059_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/619488496_18109680952733106_5126638735837564642_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/629259710_18379669267093299_3611023350833716371_n.jpg" alt="" loading="lazy"></div></div>
        <div class="card"><div class="pic"><img src="../assets/images/honeytree_shop_front_.webp" alt="" loading="lazy"></div></div>
    </div>
</section>

<section class="pull-quote reveal">
    <blockquote>Small choices, honestly made. Twenty-five years of scooping grains, weighing fruit, and knowing most of the people who come through the door.</blockquote>
    <cite>— The Honey Tree</cite>
</section>

<section class="section reveal">
    <div class="two-col reverse">
        <div class="img-wrap"><img src="../assets/images/625686563_18361443160166859_3500138926895756073_n.jpg" alt="Carrying boxes of fresh veg outside the shop" loading="lazy"></div>
        <div>
            <div class="eyebrow">Box Scheme</div>
            <h2 class="section-title">An <em>organic box</em>, collected every Friday.</h2>
            <p>£20 boxes of organic fruit, veg, or both, made up fresh each week. Order by Tuesday noon, pick up from the shop on Friday from 12pm.</p>
            <p>Start one off, set up a standing weekly order, pause when you're away. Whatever works.</p>
            <p><a href="../order/">See the boxes &amp; order →</a></p>
        </div>
    </div>
</section>

<section class="section reveal">
    <div class="eyebrow">This week</div>
    <h2 class="section-title">Find us four days a week.</h2>
    <ul class="hours-list">
        <li class="closed"><span class="day">Monday</span><span>Closed</span></li>
        <li><span class="day">Tuesday</span><span>11am &ndash; 6pm</span></li>
        <li><span class="day">Wednesday</span><span>11am &ndash; 6pm</span></li>
        <li class="closed"><span class="day">Thursday</span><span>Closed</span></li>
        <li><span class="day">Friday <span class="badge">Collection day</span></span><span>11am &ndash; 6pm</span></li>
        <li><span class="day">Saturday</span><span>10am &ndash; 5pm</span></li>
        <li class="closed"><span class="day">Sunday</span><span>Closed</span></li>
    </ul>
    <p><a href="../opening-hours/">Full hours &amp; holiday closures →</a></p>
</section>

<section class="map-section reveal">
    <div class="eyebrow">Find us</div>
    <h2 class="section-title">68 Heaton Road, Newcastle.</h2>
    <div class="map-card">
        <iframe
            src="https://maps.google.com/maps?q=The+Honey+Tree,+68+Heaton+Road,+Newcastle+upon+Tyne+NE6+5HL&t=h&z=18&output=embed"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            allowfullscreen
            title="Map showing The Honey Tree at 68 Heaton Road"></iframe>
        <div class="map-overlay">
            <div class="name">The Honey Tree</div>
            <p class="addr">68 Heaton Road<br>Heaton, Newcastle upon Tyne, NE6 5HL</p>
            <div class="map-actions">
                <a href="https://www.google.com/maps/place/The+Honey+Tree/@54.9807647,-1.5806888,17z/data=!4m6!3m5!1s0x487e70ee311d6825:0x2477aa3f1d1d76a9" target="_blank" rel="noopener">Google Maps ↗</a>
                <a class="alt" href="https://maps.apple.com/?q=The+Honey+Tree&amp;ll=54.9807647,-1.5806888&amp;z=16" target="_blank" rel="noopener">Apple Maps ↗</a>
            </div>
        </div>
    </div>
</section>

<footer class="footer">
    <div class="footer-inner">
        <div>
            <a href="../home/" class="footer-logo">The Honey Tree</a>
            <p>An independent, not-for-profit wholefoods shop on Heaton Road. Every pound we take turns back into the business.</p>
        </div>
        <div>
            <h4>Visit</h4>
            <p>68 Heaton Road</p>
            <p>Heaton, Newcastle</p>
            <p>NE6 5HL</p>
        </div>
        <div>
            <h4>Contact</h4>
            <p><a href="mailto:thehoneytreeshopteam@gmail.com">thehoneytreeshopteam@gmail.com</a></p>
            <p><a href="https://www.instagram.com/thehoneytree_newcastle/" target="_blank" rel="noopener">Instagram</a></p>
        </div>
    </div>
    <div class="footer-bottom">
        <span>© The Honey Tree Wholefoods · Not-for-profit</span>
        <span>Est. 1999</span>
    </div>
</footer>
</html>