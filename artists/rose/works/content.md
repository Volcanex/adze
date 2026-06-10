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

.page { max-width: 414px; margin: 0 auto; position: relative; padding-top: 54px; padding-bottom: 120px; min-height: 100vh; }

.header {
    height: 54px;
    background: #fff;
    position: fixed; top: 0; left: 0; right: 0; z-index: 10;
    display: flex; flex-direction: row-reverse; align-items: center; justify-content: space-between;
    padding: 0 13px;
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

/* Open menu — coloured links stacked under the hamburger (left) */
.menu-overlay {
    position: fixed;
    top: 56px; left: 13px;
    z-index: 100;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
    text-align: left;
    background: #fff;
    padding: 10px 18px 12px;
    border-radius: 2px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.12);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-6px);
    transition: opacity 0.22s ease, transform 0.22s ease, visibility 0s linear 0.22s;
}
.menu-overlay.open { opacity: 1; visibility: visible; transform: translateY(0); transition: opacity 0.22s ease, transform 0.22s ease; }
.menu-overlay a {
    font-weight: 400; font-size: 26px; line-height: 1.3;
    text-decoration: none; white-space: nowrap;
    transition: opacity 0.15s ease;
}
.menu-overlay a:hover { opacity: 0.55; }
.menu-overlay .m-works       { color: #0000FF; }
.menu-overlay .m-about       { color: #FF0033; }
.menu-overlay .m-exhibitions { color: #1AFF00; text-shadow: 0 0 1px rgba(0,0,0,0.5); }
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
    position: absolute; bottom: 0; left: 0; right: 0;
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
    .page { max-width: 880px; padding-top: 72px; padding-bottom: 160px; }
    .header { padding: 0 32px; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 80px; left: 32px; }
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

/* loading veil: opaque white over the whole page until the hero image is ready */
#page-veil {
    position: fixed; inset: 0;
    background: #fff;
    z-index: 9999;
    opacity: 1;
    transition: opacity 0.5s ease;
    animation: veil-auto 0.5s ease 4s forwards; /* backstop if JS never fires */
}
#page-veil.hide { opacity: 0; pointer-events: none; animation: none; }
@keyframes veil-auto { to { opacity: 0; visibility: hidden; } }
</style>

<html>
<div id="page-veil"></div>

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

    <div class="year-row"><div class="rule"></div><div class="year">2025</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/bed/">Bed</a></li>
        <li><a href="/works/my-inner-child/">My Inner Child</a></li>
        <li><a href="/works/paddle-for-dear-life/">Paddle for dear life</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2024</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/tokyo-park/">Tokyo park</a></li>
        <li><a href="/works/drive-thru/">Drive thru</a></li>
        <li><a href="/works/a-shooting-star-from-atop-a-slide/">A shooting star from atop a slide and gold waiting below</a></li>
        <li><a href="/works/mount-fuji-is-pregnant/">Mount fuji is pregnant</a></li>
        <li><a href="/works/marsh-at-sunset/">Marsh at sunset</a></li>
        <li><a href="/works/moonlit-sea/">Moonlit Sea</a></li>
        <li><a href="/works/wondering-women/">Wondering women</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2023</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/my-mothers-hum/">My Mothers Hum</a></li>
        <li><a href="/works/estuary/">Estuary</a></li>
        <li><a href="/works/math-equation/">Math Equation</a></li>
        <li><a href="/works/what-did-it-mean-to-fly/">What did it mean to fly</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2022</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/keeper-of-the-egg/">Keeper of the Egg</a></li>
        <li><a href="/works/while-we-sit-together/">While We Sit Together</a></li>
        <li><a href="/works/you-belong-at-the-head-of-the-table/">You belong at the head of the table</a></li>
        <li><a href="/works/her-cup/">Her Cup</a></li>
        <li><a href="/works/my-memory-of-your-birth/">My Memory of your Birth</a></li>
        <li><a href="/works/divine-like-a-bird/">Divine like a Bird</a></li>
        <li><a href="/works/cormorant/">Cormorant</a></li>
        <li><a href="/works/skip-kids/">Skip Kids</a></li>
        <li><a href="/works/untitled/">Untitled</a></li>
        <li><a href="/works/murmuration/">Murmuration</a></li>
        <li><a href="/works/night-fishing/">Night fishing</a></li>
        <li><a href="/works/night-fishing-2/">Night fishing 2</a></li>
    </ul>

    <div class="year-row"><div class="rule"></div><div class="year">2021</div><div class="rule"></div></div>
    <ul class="works-list">
        <li><a href="/works/wise-man/">Wise Man</a></li>
        <li><a href="/works/worship/">Worship</a></li>
        <li><a href="/works/pin-mill/">Pin Mill</a></li>
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
<script>
(function(){
  var veil=document.getElementById('page-veil');
  var done=false;
  function reveal(){ if(done) return; done=true;
    if(veil){ veil.classList.add('hide'); setTimeout(function(){ if(veil.parentNode) veil.parentNode.removeChild(veil); }, 600); } }
  var pending=0;
  function dec(){ if(--pending<=0) reveal(); }
  // wait for the displayed (good-tier) images
  document.querySelectorAll('img.work-image, img.exh-image, img.about-image').forEach(function(img){
    if(img.complete && img.naturalWidth) return;
    pending++; img.addEventListener('load', dec, {once:true}); img.addEventListener('error', dec, {once:true});
  });
  // wait for the body::before full-bleed background (home page)
  try {
    var bb=getComputedStyle(document.body,'::before').backgroundImage;
    var mb=/url\(["']?([^"')]+)["']?\)/.exec(bb||'');
    if(mb){ pending++; var im=new Image(); im.onload=dec; im.onerror=dec; im.src=mb[1]; }
  } catch(e){}
  if(pending===0){ requestAnimationFrame(reveal); }
  setTimeout(reveal, 3000); // hard fallback
})();
</script>
</html>
