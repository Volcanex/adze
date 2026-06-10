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

.page { max-width: 414px; margin: 0 auto; position: relative; padding-top: 54px; padding-bottom: 120px; min-height: 100vh; }

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

.about-figure {
    width: 100%;
    margin-top: 20px;
}
.about-image {
    display: block;
    width: 100%;
    height: auto;
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
    .page { max-width: 1000px; padding-top: 72px; padding-bottom: 160px; }
    .header { padding: 0 32px; height: 72px; }
    .brand { font-size: 44px; }
    .menu-overlay { top: 80px; left: 32px; }
    .about-figure { margin-top: 32px; }
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

    <h1 class="section-title">About</h1>

    <figure class="about-figure" style="aspect-ratio:2560/1920">
        <img class="about-image" src="../assets/about-good.jpg" alt="" decoding="async">
    </figure>

    <div class="bio">
        Rose Jones (b. 2002) is a multidisciplinary artist. Her work spans painting, illustration, and writing. what I make is deeply ridiculous but equally important.
    </div>

    <div class="exhibitions-block">
<!-- EXHIBITIONS_BLOCK -->
    </div>

    <div class="education-block">
        <h3>Education</h3>
        <p>Foundation Diploma, Colchester Institute, graduated 2021</p>
        <p>BFA, Slade School of Fine Art, graduating 2025</p>
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
