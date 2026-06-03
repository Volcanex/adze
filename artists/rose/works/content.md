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
    height: 54px;
    background: #fff;
    position: sticky; top: 0; z-index: 10;
    display: flex; flex-direction: row-reverse; align-items: center; justify-content: space-between;
    padding: 0 13px 0 0;
    border-bottom: 1px solid transparent;
}

.brand {
    font-weight: 250;
    font-size: 36px;
    line-height: 60px;
    color: #000;
    text-decoration: none;
}

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

.section-title {
    font-weight: 400;
    font-size: 36px;
    line-height: 60px;
    color: var(--works);
    padding: 24px 0 0 37px;
}

.year-row {
    display: flex; align-items: center; gap: 12px;
    margin: 40px 0 8px;
    padding: 0 13px;
}
.year-row .rule { flex: 1; height: 1px; background: #000; opacity: 0.7; }
.year-row .year {
    font-weight: 250; font-size: 20px; line-height: 33px;
    color: #000;
    padding: 0 6px;
}

.works-list { padding: 0 13px; list-style: none; }
.works-list li {
    padding: 0;
}
.works-list li a {
    display: block;
    font-weight: 250; font-size: 20px; line-height: 22px;
    padding: 12px 0;
    color: #000;
    text-decoration: none;
    transition: opacity 0.15s ease;
}
.works-list li a:hover { opacity: 0.55; }

.footer {
    margin-top: 60px;
    padding: 14px 13px 24px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    font-size: 15px;
    line-height: 25px;
}
.footer a { color: #000; text-decoration: none; }
.footer .right { text-align: right; }
.footer .center { text-align: center; }

@media (min-width: 768px) {
    .page { max-width: 880px; padding-bottom: 160px; }
    .header { padding: 0 32px 0 0; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 72px; }
    .section-title { font-size: 56px; padding: 48px 0 0 64px; }
    .year-row { padding: 0 32px; margin: 56px 0 12px; }
    .year-row .year { font-size: 24px; }
    .works-list { padding: 0 64px; columns: 2; column-gap: 64px; }
    .works-list li { break-inside: avoid; }
    .works-list li a { font-size: 24px; line-height: 28px; padding: 14px 0; }
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

    <h1 class="section-title">Works</h1>

    <div class="year-row"><div class="rule"></div><div class="year">2024</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/wondering-women/">Wondering Women</a></li>
        <li><a href="/works/moonlit-sea/">Moonlit Sea</a></li>
        <li><a href="/works/marsh-at-sunset/">Marsh at Sunset</a></li>
        <li><a href="/works/mount-fuji-is-pregnant/">Mount Fuji is Pregnant</a></li>
        <li><a href="/works/a-shooting-star-from-atop-a-slide/">A Shooting star from atop a Slide and Gold Waiting Below</a></li>
        <li><a href="/works/drive-thru/">Drive Thru</a></li>
        <li><a href="/works/tokyo-park/">Tokyo Park</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2023</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/what-did-it-mean-to-fly/">What did it mean to fly</a></li>
        <li><a href="/works/math-equation/">Math Equation</a></li>
        <li><a href="/works/estuary/">Estuary</a></li>
        <li><a href="/works/my-mothers-hum/">My Mothers Hum</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2022</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/night-fishing/">Night fishing</a></li>
        <li><a href="/works/night-fishing-2/">Night fishing 2</a></li>
        <li><a href="/works/murmuration/">Murmuration</a></li>
        <li><a href="/works/untitled/">Untitled</a></li>
        <li><a href="/works/skip-kids/">Skip Kids</a></li>
        <li><a href="/works/cormorant/">Cormorant</a></li>
        <li><a href="/works/divine-like-a-bird/">Divine like a Bird</a></li>
        <li><a href="/works/my-memory-of-your-birth/">My Memory of your Birth</a></li>
        <li><a href="/works/her-cup/">Her Cup</a></li>
        <li><a href="/works/you-belong-at-the-head-of-the-table/">You belong at the head of the table</a></li>
        <li><a href="/works/while-we-sit-together/">While we sit together</a></li>
        <li><a href="/works/keeper-of-the-egg/">Keeper of the Egg</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2021</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/pin-mill/">Pin Mill</a></li>
        <li><a href="/works/worship/">Worship</a></li>
        <li><a href="/works/wise-man/">Wise Man</a></li>
    </ul>

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
