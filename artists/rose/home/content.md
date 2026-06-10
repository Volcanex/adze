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

html, body {
    height: 100%;
    overflow: hidden;
}

body {
    font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--ink);
    overflow-x: hidden;
    position: relative;
    min-height: 100vh;
}

/* Full-bleed image background — fades in on load (opacity only, no movement) */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: url('../assets/home-bg-good.jpg');
    background-size: cover;
    background-position: center;
    z-index: -1;
    opacity: 0;
    animation: bg-fade-in 1.2s ease-out forwards;
}
@keyframes bg-fade-in {
    to { opacity: 1; }
}

.stage {
    position: relative;
    width: min(92vw, 720px);
    margin: 0 auto;
    min-height: 100vh;
    padding: clamp(48px, 12vh, 140px) 0;
}

.name {
    font-weight: 600;
    font-size: clamp(48px, 8vw, 96px);
    line-height: 1;
    color: #22348D;
    text-decoration: none;
    display: block;
    letter-spacing: -0.01em;
}

.rose  { margin-left: 18%; }
.jones { margin-left: auto; width: max-content; padding-right: 6%; margin-top: 0.4em; }

.nav {
    position: relative;
    margin-top: clamp(40px, 8vh, 96px);
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto auto;
    row-gap: 0;
    column-gap: 0;
}
.nav a {
    font-weight: 600;
    font-size: clamp(34px, 5vw, 60px);
    line-height: 1.05;
    text-decoration: none;
    transition: opacity 0.2s ease;
    display: inline-block;
    padding: 4px 0;
}
.nav a:hover { opacity: 0.55; }

/* Scatter — left column slightly offset, right column lower */
.nav .works       { grid-column: 1; grid-row: 1; color: var(--works);       padding-left: 6%; }
.nav .exhibitions { grid-column: 1; grid-row: 2; color: var(--exhibitions); padding-left: 2%;  text-shadow: 0 0 1px rgba(0,0,0,0.4); }
.nav .about       { grid-column: 2; grid-row: 3; color: var(--about);       padding-left: 14%; }
.nav .contact     { grid-column: 2; grid-row: 4; color: var(--contact);     padding-left: 22%; }

@media (max-width: 640px) {
    .stage { padding: 80px 0 60px; }
    .rose  { margin-left: 32%; }
    .jones { padding-right: 14%; }
    .nav .works       { padding-left: 9%; }
    .nav .exhibitions { padding-left: 3%; }
    .nav .about       { padding-left: 28%; }
    .nav .contact     { padding-left: 40%; }
}

/* Title drifts gently downward on load */
@keyframes title-drift {
    from { transform: translateY(0); }
    to   { transform: translateY(10px); }
}
.name { animation: title-drift 2.2s ease-out forwards; }

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
<div class="stage">
    <span class="name rose">Rose</span>
    <span class="name jones">Jones</span>
    <nav class="nav">
        <a class="works" href="/works/">Works</a>
        <a class="exhibitions" href="/exhibitions/">Exhibitions</a>
        <a class="about" href="/about/">About</a>
        <a class="contact" href="/contact/">Contact</a>
    </nav>
</div>
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
