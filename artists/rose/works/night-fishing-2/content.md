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

.page { max-width: 414px; margin: 0 auto; position: relative; padding-top: 140px; padding-bottom: 120px; min-height: 100vh; }

.header {
    height: 54px; background: #fff;
    position: fixed; top: 0; left: 0; right: 0; z-index: 10;
    display: flex; flex-direction: row-reverse; align-items: center; justify-content: space-between;
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

/* Open menu — 2x2 grid (Works/About top, Exhibitions/Contact bottom) sliding in on a conveyor */
.menu-overlay {
    position: fixed;
    top: 56px; left: 0; right: 0;
    z-index: 100;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-auto-rows: min-content;
    row-gap: 4px;
    padding: 6px 13px 0;
    pointer-events: none;
}
.menu-overlay a {
    font-weight: 400; font-size: 32px; line-height: 1.05;
    text-decoration: none; white-space: nowrap;
    will-change: transform;
    transition: transform 0.32s cubic-bezier(.5,0,.2,1), opacity 0.18s ease;
    z-index: 3;
}
.menu-overlay a:hover { opacity: 0.55; }
.menu-overlay .m-works       { color: #0000FF; grid-column: 1; grid-row: 1; }
.menu-overlay .m-about       { color: #FF0033; grid-column: 2; grid-row: 1; justify-self: end; text-align: right; }
.menu-overlay .m-exhibitions { color: #1AFF00; grid-column: 1; grid-row: 2; text-shadow: 0 0 1px rgba(0,0,0,0.5); }
.menu-overlay .m-contact     { color: #8C00FF; grid-column: 2; grid-row: 2; justify-self: end; text-align: right; }
/* closed: only the current page's word shows (it is the page title); the rest wait off-canvas */
.menu-overlay a:not(.is-current) { opacity: 0; pointer-events: none; }
.menu-overlay .m-works:not(.is-current),
.menu-overlay .m-about:not(.is-current)       { transform: translateX(120vw); }
.menu-overlay .m-exhibitions:not(.is-current),
.menu-overlay .m-contact:not(.is-current)     { transform: translateX(-120vw); }
/* current page's word: always in place; the sliding words pass in front of it */
.menu-overlay a.is-current { opacity: 1; pointer-events: auto; transform: none; z-index: 1; }
/* open: every word slides home */
.menu-overlay.open a:not(.is-current) { opacity: 1; transform: translateX(0); pointer-events: auto; }

.back-link {
    display: inline-block;
    padding: 16px 13px 0;
    font-size: 14px; font-weight: 300;
    color: var(--works);
    text-decoration: none;
}
.back-link:hover { opacity: 0.55; }

.work-figure {
    margin: 16px 13px 0;
    width: calc(100% - 26px);
}
.work-image {
    display: block;
    width: 100%;
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
    position: absolute; bottom: 0; left: 0; right: 0;
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
    .page { max-width: 980px; padding-top: 72px; padding-bottom: 160px; }
    .header { padding: 0 32px; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 80px; padding: 8px 32px 0; }
    .menu-overlay a { font-size: 44px; }
    .back-link { padding: 28px 32px 0; font-size: 15px; }
    .work-figure { margin: 24px 32px 0; width: calc(100% - 64px); }
    .title-row { padding: 48px 32px 0; display: grid; grid-template-columns: 1fr 280px; gap: 32px; align-items: baseline; }
    .work-title { font-size: 56px; }
    .work-meta { font-size: 17px; margin-top: 0; text-align: right; }
    .work-desc { padding: 28px 32px 0; font-size: 17px; line-height: 1.7; max-width: 64ch; }
    .detail-list { padding: 32px 32px 0; font-size: 15px; }
    .footer { padding: 20px 32px 32px; font-size: 16px; }
}

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
        <a class="m-works is-current" href="/works/">Works</a>
        <a class="m-exhibitions" href="/exhibitions/">Exhibitions</a>
        <a class="m-about" href="/about/">About</a>
        <a class="m-contact" href="/contact/">Contact</a>
    </nav>

    <a class="back-link" href="/works/">← Works</a>

    <figure class="work-figure" style="aspect-ratio:2187/1719">
        <img class="work-image" src="../../assets/work-night-fishing-2-good.jpg" alt="Night fishing 2" decoding="async">
    </figure>

    <figure class="work-figure" style="aspect-ratio:2187/1719">
        <img class="work-image" src="../../assets/work-night-fishing-2-2-good.jpg" alt="Night fishing 2" decoding="async">
    </figure>

    <div class="title-row">
        <h1 class="work-title">Night fishing 2</h1>
        <div class="work-meta">
            <span>2022</span>
        </div>
    </div>


    <dl class="detail-list">
        <dt>Year</dt><dd>2022</dd>
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
