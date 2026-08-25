<style>
:root {
    --works: #0000FF;
    --exhibitions: #1AFF00;
    --about: #FF0033;
    --contact: #8C00FF;
    --navy: #22348D;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; overflow: hidden; }

body {
    font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #000;
    color: #000;
}

/* Layer 1 — full-bleed painting, fades in on load */
#paint {
    position: fixed; inset: 0;
    background: url('../assets/home-bg-good.jpg') center / cover no-repeat;
    opacity: 0;
    transition: opacity 1.2s ease-out;
    z-index: 0;
}
body.lit #paint { opacity: 1; }

/* Layer 2 — solid sheet: fades to black, then inverts to white */
#fill {
    position: fixed; inset: 0;
    background: #000;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.4s ease, background-color 0.5s ease;
    z-index: 1;
}
body.to-black #fill { opacity: 1; }
body.to-white #fill { opacity: 1; background: #fff; }

/* Layer 3 — the composition, centred in the viewport and scaled to fit */
.wrap {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.frame {
    position: relative;
    width: 414px;
    height: 545px;
    transform: scale(var(--s, 1));
    transform-origin: center;
}

.name, .nav a {
    position: absolute;
    font-weight: 500;
    font-size: 36px;
    line-height: 60px;
    text-decoration: none;
    white-space: nowrap;
}

/* Names — navy on the painting, white on black, black on white */
.name {
    color: var(--navy);
    opacity: 0;
    text-shadow: 0 1px 10px rgba(255,255,255,0.35);
    transition: color 0.45s ease, opacity 0.9s ease, text-shadow 0.45s ease;
}
body.show-names .name { opacity: 1; }
body.to-black .name,
body.to-white .name { text-shadow: none; }
body.to-black .name { color: #fff; }
body.to-white .name { color: #000; }

/* Exact Figma spatial scatter (shifted up so the group centres in the frame) */
.rose  { left: 155px; top: 0; }
.jones { left: 247px; top: 89px; }

.nav a { opacity: 0; pointer-events: none; transition: opacity 0.6s ease; }
.nav .works       { left: 37px;  top: 201px; color: var(--works); }
.nav .exhibitions { left: 13px;  top: 233px; color: var(--exhibitions); text-shadow: 0 0 1px rgba(0,0,0,0.4); }
.nav .about       { left: 207px; top: 443px; color: var(--about); }
.nav .contact     { left: 283px; top: 485px; color: var(--contact); }
.nav a:hover { opacity: 0.6 !important; }

/* Reveal — fade in, then the slow downward drift */
@keyframes title-drift { from { transform: translateY(0); } to { transform: translateY(10px); } }
.nav a.show { opacity: 1; pointer-events: auto; animation: title-drift 2.4s ease-out forwards; }

body.nojs .name, body.nojs .nav a { opacity: 1 !important; animation: none !important; }
</style>

<html>
<div id="paint"></div>
<div id="fill"></div>

<div class="wrap">
    <div class="frame">
        <span class="name rose">Rose</span>
        <span class="name jones">Jones</span>
        <nav class="nav">
            <a class="works"       href="/works/">Works</a>
            <a class="exhibitions" href="/exhibitions/">Exhibitions</a>
            <a class="about"       href="/about/">About</a>
            <a class="contact"     href="/contact/">Contact</a>
        </nav>
    </div>
</div>

<script>
(function () {
    var body = document.body;
    var frame = document.querySelector('.frame');

    /* scale the 380px composition to comfortably fill the viewport, centred */
    function fit() {
        var s = Math.min(window.innerWidth * 0.9 / 414, window.innerHeight * 0.86 / 545);
        frame.style.setProperty('--s', Math.max(0.6, Math.min(s, 1.7)));
    }
    fit();
    window.addEventListener('resize', fit);

    /* The sequence runs on its own — no click required.
       paint in -> (1s) navy names -> fade to black -> invert white -> links cascade */
    function run() {
        if (body.classList.contains('lit')) return;
        body.classList.add('lit');                                   // painting fades in
        setTimeout(function () { body.classList.add('show-names'); }, 1000);   // navy names
        setTimeout(function () { body.classList.add('to-black'); }, 2400);     // black, white text
        setTimeout(function () { body.classList.add('to-white'); }, 2850);     // white, black text
        setTimeout(revealLinks, 3350);                                          // links arrive
    }

    var img = new Image();
    img.onload = run;
    img.onerror = run;
    img.src = '../assets/home-bg-good.jpg';
    if (img.complete && img.naturalWidth) run();
    setTimeout(run, 2500); /* fallback if decode never reports */

    /* nav links arrive one by one, in a random order, at fixed positions */
    function revealLinks() {
        var links = Array.prototype.slice.call(document.querySelectorAll('.nav a'));
        for (var i = links.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var t = links[i]; links[i] = links[j]; links[j] = t;
        }
        links.forEach(function (a, idx) {
            setTimeout(function () { a.classList.add('show'); }, idx * 240);
        });
    }
})();
</script>
</html>
