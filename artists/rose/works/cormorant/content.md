<style>
:root {
    --ink: #000;
    --bg: #fff;
    --works: #0000FF;
    --exhibitions: #1AFF00;
    --about: #FF0033;
    --contact: #8C00FF;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--ink);
    overflow-x: hidden;
}

.page { max-width: 414px; margin: 0 auto; position: relative; padding-bottom: 120px; }

.header {
    height: 54px; background: #fff;
    position: sticky; top: 0; z-index: 10;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 13px;
}
.brand { font-weight: 250; font-size: 36px; line-height: 60px; color: #000; text-decoration: none; }

.menu-icon {
    position: relative;
    width: 44px; height: 30px;
    background: none; border: 0; padding: 0; cursor: pointer;
    z-index: 200;
}
.menu-icon span {
    position: absolute;
    top: 4px;
    box-sizing: border-box;
    height: 22px;
    border: 1px solid #000;
    background: none;
    transform-origin: center;
    transition: transform 0.35s cubic-bezier(.5,0,.2,1);
}
.menu-icon span:nth-child(1) { left: 2px;    width: 20px; }
.menu-icon span:nth-child(2) { left: 19.5px; width: 14px; }
.menu-icon span:nth-child(3) { left: 39.5px; width: 3.5px; }
.menu-icon[aria-expanded="true"] span:nth-child(1) { transform: rotate(-39.6deg); }
.menu-icon[aria-expanded="true"] span:nth-child(2) { transform: rotate(-32.26deg); }
.menu-icon[aria-expanded="true"] span:nth-child(3) { transform: rotate(-11.9deg); }

/* Open menu — scattered cluster on white plates, mirrors the home-page scatter */
.menu-overlay {
    position: fixed;
    top: 54px; left: 50%;
    transform: translateX(-50%);
    width: 100%; max-width: 414px;
    height: 150px;
    z-index: 100;
    display: none;
}
.menu-overlay.open { display: block; }
.menu-overlay a {
    position: absolute;
    background: #fff;
    padding: 0 8px;
    font-weight: 400; font-size: 36px; line-height: 60px;
    text-decoration: none; white-space: nowrap;
    transition: opacity 0.15s ease;
}
.menu-overlay a:hover { opacity: 0.55; }
.menu-overlay .m-works       { left: 29px;  top: 6px;  color: #0000FF; }
.menu-overlay .m-about       { left: 199px; top: 6px;  color: #FF0033; }
.menu-overlay .m-exhibitions { left: 5px;   top: 41px; color: #1AFF00; text-shadow: 0 0 1px rgba(0,0,0,0.4); }
.menu-overlay .m-contact     { left: 275px; top: 39px; color: #8C00FF; }

.back-link {
    display: inline-block;
    padding: 16px 13px 0;
    font-size: 14px; font-weight: 300;
    color: var(--works);
    text-decoration: none;
}
.back-link:hover { opacity: 0.55; }

.work-image {
    margin: 16px 13px 0;
    width: calc(100% - 26px);
    display: block;
    height: auto;
}

.title-row {
    padding: 28px 13px 0;
}
.work-title {
    font-weight: 400; font-size: 32px; line-height: 1.1;
    color: var(--works);
}
.work-meta {
    margin-top: 8px;
    font-weight: 250; font-size: 15px; line-height: 1.4;
    color: #000;
}
.work-meta span + span::before { content: " · "; color: #666; }

.work-desc {
    padding: 20px 13px 0;
    font-weight: 300; font-size: 15px; line-height: 1.6;
    color: #000;
    max-width: 60ch;
}

.detail-list {
    padding: 24px 13px 0;
    font-weight: 250; font-size: 14px; line-height: 1.6;
    color: #000;
}
.detail-list dt { color: #777; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 10px; }
.detail-list dd { }

.footer {
    margin-top: 80px;
    padding: 14px 13px 24px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    font-size: 15px; line-height: 25px;
}
.footer a { color: #000; text-decoration: none; }
.footer .right { text-align: right; }
.footer .center { text-align: center; }

@media (min-width: 768px) {
    .page { max-width: 980px; padding-bottom: 160px; }
    .header { padding: 0 32px; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 72px; }
    .back-link { padding: 28px 32px 0; font-size: 15px; }
    .work-image { margin: 24px 32px 0; width: calc(100% - 64px); aspect-ratio: 16/10; }
    .title-row { padding: 48px 32px 0; display: grid; grid-template-columns: 1fr 280px; gap: 32px; align-items: baseline; }
    .work-title { font-size: 56px; }
    .work-meta { font-size: 17px; margin-top: 0; text-align: right; }
    .work-desc { padding: 28px 32px 0; font-size: 17px; line-height: 1.7; max-width: 64ch; }
    .detail-list { padding: 32px 32px 0; font-size: 15px; }
    .footer { padding: 20px 32px 32px; font-size: 16px; }
}
</style>

<html>

<div class="page">
    <header class="header">
        <a class="brand" href="/">Rose Jones</a>
        <button type="button" class="menu-icon" aria-label="Open menu" aria-controls="site-menu" aria-expanded="false">
            <span></span><span></span><span></span>
        </button>
    </header>

    <nav id="site-menu" class="menu-overlay" aria-hidden="true">
        <a class="m-works" href="/works/">Works</a>
        <a class="m-exhibitions" href="/exhibitions/">Exhibitions</a>
        <a class="m-about" href="/about/">About</a>
        <a class="m-contact" href="/contact/">Contact</a>
    </nav>

    <a class="back-link" href="/works/">← Works</a>

    <img class="work-image" src="../../assets/Works_2022_Night_fishing.png" alt="">

    <div class="title-row">
        <h1 class="work-title">Cormorant</h1>
        <div class="work-meta">
            <span>2022</span><span>Oil on linen</span><span>120 × 90 cm</span>
        </div>
    </div>

    <div class="work-desc">
        A short, dummy description for <em>Cormorant</em>. Replace this paragraph with notes on the work — what it explores, the materials, the moment it was made in. The image above is a placeholder; swap it for the real photograph when you have one.
    </div>

    <dl class="detail-list">
        <dt>Year</dt><dd>2022</dd>
        <dt>Medium</dt><dd>Oil on linen</dd>
        <dt>Dimensions</dt><dd>120 × 90 cm</dd>
        <dt>Status</dt><dd>Available</dd>
    </dl>

    <footer class="footer">
        <a href="/contact/">Contact</a>
        <div class="center">// Copyright © 2025 Rose Jones</div>
        <div class="right">// Site by Last Place</div>
    </footer>
</div>

<script>
(function(){
    var btn = document.querySelector('.menu-icon');
    var menu = document.getElementById('site-menu');
    var close = document.querySelector('.menu-close');
    if (!btn || !menu) return;
    function open(){ menu.classList.add('open'); menu.setAttribute('aria-hidden','false'); btn.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; }
    function shut(){ menu.classList.remove('open'); menu.setAttribute('aria-hidden','true'); btn.setAttribute('aria-expanded','false'); document.body.style.overflow=''; }
    function toggle(){ if (menu.classList.contains('open')) shut(); else open(); }
    btn.addEventListener('click', toggle);
    if (close) close.addEventListener('click', shut);
    menu.addEventListener('click', function(e){ if (e.target === menu) shut(); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape') shut(); });
})();
</script>
</html>
