<style>
:root {
    --ink: #000;
    --bg: #fff;
    --about: #FF0033;
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
    display: flex; flex-direction: row-reverse; align-items: center; justify-content: space-between;
    padding: 0 13px 0 0;
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
    height: 26px;
    border: 0;
    background: #000;
    transform-origin: center;
    transition: transform 0.35s cubic-bezier(.5,0,.2,1);
}
.menu-icon span:nth-child(1) { left: 2px;    width: 1px; }
.menu-icon span:nth-child(2) { left: 19.5px; width: 1px; }
.menu-icon span:nth-child(3) { left: 39.5px; width: 1px; }
.menu-icon[aria-expanded="true"] span:nth-child(1) { transform: rotate(-39.6deg); }
.menu-icon[aria-expanded="true"] span:nth-child(2) { transform: rotate(-32.26deg); }
.menu-icon[aria-expanded="true"] span:nth-child(3) { transform: rotate(-11.9deg); }

/* Open menu — animated dropdown, coloured links stacked under the hamburger (left) */
.menu-overlay {
    position: fixed;
    top: 54px; left: 0; right: 0;
    background: #fff;
    z-index: 100;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 18px 13px 26px;
    border-bottom: 1px solid #000;
    transform: translateY(-14px);
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, transform 0.32s cubic-bezier(.4,0,.2,1), visibility 0s linear 0.32s;
}
.menu-overlay.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
    transition: opacity 0.3s ease, transform 0.32s cubic-bezier(.4,0,.2,1);
}
.menu-overlay a {
    font-weight: 400; font-size: 36px; line-height: 1.25;
    text-decoration: none;
    opacity: 0;
    transform: translateY(-8px);
    transition: opacity 0.25s ease, transform 0.25s cubic-bezier(.4,0,.2,1);
}
.menu-overlay.open a { opacity: 1; transform: translateY(0); }
.menu-overlay.open a:nth-child(1) { transition-delay: 0.06s; }
.menu-overlay.open a:nth-child(2) { transition-delay: 0.12s; }
.menu-overlay.open a:nth-child(3) { transition-delay: 0.18s; }
.menu-overlay.open a:nth-child(4) { transition-delay: 0.24s; }
.menu-overlay a:hover { opacity: 0.55; }
.menu-overlay .m-works       { color: #0000FF; }
.menu-overlay .m-about       { color: #FF0033; }
.menu-overlay .m-exhibitions { color: #1AFF00; text-shadow: 0 0 1px rgba(0,0,0,0.4); }
.menu-overlay .m-contact     { color: #8C00FF; }

.about-image {
    width: 100%;
    display: block;
    height: auto;
    margin-top: 20px;
}

.section-title {
    font-weight: 400; font-size: 36px; line-height: 60px;
    color: var(--about);
    padding: 24px 13px 0;
}

.bio {
    padding: 24px 13px 0;
    font-weight: 300; font-size: 15px; line-height: 17px;
    color: #000;
    max-width: 560px;
}

.exhibitions-block {
    padding: 24px 13px 0;
    font-weight: 300; font-size: 15px; line-height: 17px;
    color: var(--about);
}
.exhibitions-block p { margin-bottom: 8px; }

.education-block {
    padding: 24px 13px 0;
    font-weight: 300; font-size: 15px; line-height: 15px;
    color: #000;
}
.education-block h3 {
    font-size: 15px; font-weight: 400; margin-bottom: 8px;
}
.education-block p { margin-bottom: 6px; }

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
    .page { max-width: 1000px; padding-bottom: 160px; }
    .header { padding: 0 32px 0 0; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 72px; }
    .about-image { margin-top: 32px; }
    .section-title { font-size: 56px; padding: 48px 32px 0; }
    .bio { padding: 32px 32px 0; max-width: 560px; font-size: 18px; line-height: 22px; }
    .exhibitions-block { padding: 40px 32px 0; font-size: 17px; line-height: 22px; max-width: 560px; }
    .exhibitions-block p { margin-bottom: 10px; }
    .education-block { padding: 40px 32px 0; font-size: 17px; line-height: 22px; max-width: 560px; }
    .education-block h3 { font-size: 17px; }
    .footer { padding: 20px 32px 32px; font-size: 16px; }
}

/* Title drifts gently downward on load */
@keyframes title-drift {
    from { transform: translateY(0); }
    to   { transform: translateY(10px); }
}
.section-title { animation: title-drift 2.2s ease-out forwards; }
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

    <h1 class="section-title">About</h1>

    <img class="about-image" src="../assets/intake/Assets/Work/Works_NA_itichy_nose.jpg" alt="">

    <div class="bio">
        Rose Jones (b. 2002) makes work that is deeply ridiculous but equally important. Her multidisciplinary practice spans painting, illustration and writing.
    </div>

    <div class="exhibitions-block">
        <p>2024 — Threading the Eye, group show, Crypt Gallery, London, UK</p>
        <p>2024 — Kobokan stories, solo show and workshop, Tokyo, JPN</p>
        <p>2023 — Axxx/Blood, group show, London, UK</p>
    </div>

    <div class="education-block">
        <h3>Education</h3>
        <p>2020–2021 — Foundation Diploma, Colchester Institute</p>
        <p>2021–2025 — BFA, Slade School of Fine Art</p>
    </div>

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
