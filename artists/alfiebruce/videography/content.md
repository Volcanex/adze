<style>
:root{--bg:#000;--text:#fff;--muted:#999;--line:rgba(255,255,255,.14);--sans:'Helvetica Neue',Helvetica,Arial,sans-serif;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:var(--sans);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;opacity:0;animation:fade .6s ease forwards;}
@keyframes fade{to{opacity:1;}}
a{color:inherit;text-decoration:none;}
.bar{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;align-items:center;justify-content:space-between;padding:22px 34px;mix-blend-mode:difference;}
.bar .mark{font-size:15px;letter-spacing:.32em;text-transform:uppercase;font-weight:500;}
.bar nav{display:flex;gap:30px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;}
.bar nav a{color:var(--muted);transition:color .2s ease;}
.bar nav a:hover{color:var(--text);}
.head{padding:30vh 34px 8vh;border-bottom:1px solid var(--line);}
.head h1{font-size:clamp(38px,8vw,104px);font-weight:600;letter-spacing:.04em;text-transform:uppercase;line-height:.95;}
.head p{margin-top:18px;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:3px;padding:3px;}
.vcard{position:relative;aspect-ratio:16/9;background:#111;overflow:hidden;cursor:pointer;}
.vcard video{width:100%;height:100%;object-fit:cover;display:block;}
.vcard .poster{position:absolute;inset:0;background:#111;}
.vcard .poster img{width:100%;height:100%;object-fit:cover;filter:brightness(.82);transition:filter .5s ease;}
.vcard:hover .poster img{filter:brightness(1);}
.vcard .play{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;transition:opacity .3s ease;}
.vcard .play svg{width:64px;height:64px;opacity:.8;transition:opacity .3s,transform .3s;}
.vcard:hover .play svg{opacity:1;transform:scale(1.08);}
.vcard.playing .poster,.vcard.playing .play{display:none;}
.vcard video{display:none;}
.vcard.playing video{display:block;}
.foot{padding:14vh 34px;text-align:center;border-top:1px solid var(--line);}
.foot a{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid transparent;padding-bottom:3px;transition:color .2s,border-color .2s;}
.foot a:hover{color:var(--text);border-color:var(--text);}
@media(max-width:720px){.bar{padding:18px 20px;}.bar nav{gap:18px;}.head{padding:24vh 20px 6vh;}.grid{grid-template-columns:1fr;}}
</style>
<html>
<div class="bar">
    <a href="../home/" class="mark">Alfie Bruce</a>
    <nav>
        <a href="../home/#work">Work</a>
        <a href="../home/#contact">Contact</a>
    </nav>
</div>

<header class="head">
    <h1>Videography</h1>
    <p>4 films &middot; 2025</p>
</header>

<section class="grid">
    <div class="vcard" data-src="../assets/9413e3f36daf481cbe922b0dfc3c79be.mp4">
        <div class="poster"><img src="../assets/poster-9413e3f36daf481cbe922b0dfc3c79be.jpg" alt="Film 1"></div>
        <div class="play"><svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="39" stroke="white" stroke-width="2"/><polygon points="32,24 60,40 32,56" fill="white"/></svg></div>
        <video controls preload="none" src="../assets/9413e3f36daf481cbe922b0dfc3c79be.mp4"></video>
    </div>
    <div class="vcard" data-src="../assets/70ee9da9be374cbba155d2fedfb03338.mp4">
        <div class="poster"><img src="../assets/poster-70ee9da9be374cbba155d2fedfb03338.jpg" alt="Film 2"></div>
        <div class="play"><svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="39" stroke="white" stroke-width="2"/><polygon points="32,24 60,40 32,56" fill="white"/></svg></div>
        <video controls preload="none" src="../assets/70ee9da9be374cbba155d2fedfb03338.mp4"></video>
    </div>
    <div class="vcard" data-src="../assets/88787babb0124739bf5174b9681a0cef.mp4">
        <div class="poster"><img src="../assets/poster-88787babb0124739bf5174b9681a0cef.jpg" alt="Film 3"></div>
        <div class="play"><svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="39" stroke="white" stroke-width="2"/><polygon points="32,24 60,40 32,56" fill="white"/></svg></div>
        <video controls preload="none" src="../assets/88787babb0124739bf5174b9681a0cef.mp4"></video>
    </div>
    <div class="vcard" data-src="../assets/4980d655f5eb4e34a2842ffd62a77c57.mp4">
        <div class="poster"><img src="../assets/poster-4980d655f5eb4e34a2842ffd62a77c57.jpg" alt="Film 4"></div>
        <div class="play"><svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="39" stroke="white" stroke-width="2"/><polygon points="32,24 60,40 32,56" fill="white"/></svg></div>
        <video controls preload="none" src="../assets/4980d655f5eb4e34a2842ffd62a77c57.mp4"></video>
    </div>
</section>

<div class="foot"><a href="../home/#work">&larr; Back to all work</a></div>

<script>
(function(){
    document.querySelectorAll('.vcard').forEach(function(card){
        card.addEventListener('click', function(){
            if (card.classList.contains('playing')) return;
            document.querySelectorAll('.vcard.playing').forEach(function(other){
                other.classList.remove('playing');
                other.querySelector('video').pause();
                other.querySelector('video').currentTime = 0;
            });
            card.classList.add('playing');
            card.querySelector('video').play();
        });
    });
})();
</script>
</html>
