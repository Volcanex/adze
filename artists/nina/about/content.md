<style>
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300 900;
    font-display: swap;
    src: url('../assets/fonts/Inter-Variable.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: italic;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}

:root {
    --bg: #f5f3ee;
    --ink: #111;
    --muted: #6a6660;
    --accent: #3a3a38;
    --paper: #ece8df;
    --border: rgba(17,17,17,0.12);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; }

body {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
    background: var(--bg);
    line-height: 1.7;
    font-size: 15px;
    opacity: 0;
    animation: pageIn 1s ease-out forwards;
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
}

#bg-flowers {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
    display: block;
}
.topbar, main.wrap { position: relative; z-index: 2; }
main.wrap { background: transparent; }

.topbar {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 48px;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
}
.brand {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 16px;
    letter-spacing: 0.02em;
    color: var(--ink);
    text-decoration: none;
}
.topbar nav a {
    font-size: 12px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--ink);
    text-decoration: none;
    margin-left: 24px;
    opacity: 0.85;
    transition: opacity .3s;
}
.topbar nav a:hover { opacity: 1; color: var(--accent); }

.wrap {
    max-width: 960px;
    margin: 0 auto;
    padding: 80px 48px 120px;
}

.intro {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 64px;
    align-items: end;
    margin-bottom: 80px;
    animation: slideUp .9s ease-out .2s both;
}
.intro h1 {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-weight: 400;
    font-size: clamp(2.8rem, 7vw, 6rem);
    line-height: 1;
    letter-spacing: -0.02em;
}
.intro .lead {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.7;
}
.intro .lead .label {
    display: block;
    font-size: 10px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--ink);
    margin-bottom: 12px;
}

.bio {
    max-width: 640px;
    font-size: 17px;
    line-height: 1.8;
    color: var(--ink);
    animation: slideUp .9s ease-out .35s both;
}
.bio p { margin-bottom: 20px; }
.bio p:first-of-type::first-letter {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 3.4rem;
    float: left;
    line-height: 0.9;
    margin: 6px 10px 0 -4px;
    color: var(--ink);
    opacity: 0.72;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 40px;
    margin: 80px 0 60px;
    animation: slideUp .9s ease-out .5s both;
}
.stat {
    border-top: 1px solid var(--border);
    padding-top: 20px;
}
.stat .n {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 2.6rem;
    line-height: 1;
    color: var(--ink);
}
.stat .l {
    font-size: 10px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 8px;
}

.cities {
    margin-top: 80px;
    animation: slideUp .9s ease-out .65s both;
}
.cities .heading {
    font-size: 10px;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 28px;
}
.city-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0 4px;
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: clamp(1.8rem, 4.2vw, 3.4rem);
    line-height: 1.1;
    letter-spacing: -0.01em;
}
.city-list .c {
    position: relative;
    cursor: default;
    transition: color .3s, transform .3s;
}
.city-list .c:hover { color: var(--accent); transform: translateY(-2px); }
.city-list .sep {
    color: var(--muted);
    font-family: 'Inter';
    font-style: normal;
    font-size: 0.45em;
    vertical-align: middle;
    margin: 0 8px;
    opacity: 0.5;
}
.city-list .current {
    color: var(--ink);
    font-weight: 500;
}
.city-list .current::after {
    content: '';
    position: absolute;
    bottom: 0.18em;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--ink);
    opacity: 0.5;
    transform-origin: left;
    animation: underline 3s ease-in-out infinite;
}
@keyframes underline {
    0%, 100% { transform: scaleX(1); opacity: 0.5; }
    50% { transform: scaleX(1.05); opacity: 0.9; }
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

.contact {
    margin-top: 100px;
    border-top: 1px solid var(--border);
    padding-top: 40px;
    display: flex;
    gap: 48px;
    flex-wrap: wrap;
    animation: slideUp .9s ease-out .8s both;
}
.contact .item .label {
    font-size: 10px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}
.contact .item a, .contact .item span {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: var(--ink);
    text-decoration: none;
    transition: color .3s;
}
.contact .item a:hover { color: var(--accent); }

@media (max-width: 760px) {
    .topbar { padding: 16px 20px; }
    .topbar nav a { margin-left: 14px; }
    .wrap { padding: 40px 20px 80px; }
    .intro { grid-template-columns: 1fr; gap: 24px; margin-bottom: 48px; }
    .bio { font-size: 15px; }
    .stats { grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 48px 0; }
    .stat .n { font-size: 1.8rem; }
    .cities { margin-top: 48px; }
    .city-list .sep { margin: 0 4px; }
}
</style>
<html>
<canvas id="bg-flowers" aria-hidden="true"></canvas>

<div class="topbar">
    <a class="brand" href="../home/">nina serebrennikova</a>
    <nav>
        <a href="../home/">Work</a>
        <a href="../about/">About</a>
    </nav>
</div>

<main class="wrap">
    <section class="intro">
        <h1>Nina Serebrennikova</h1>
        <div class="lead">
            <span class="label">Now</span>
            Russian–American model, 21, based in Saigon. Available internationally.
        </div>
    </section>

    <section class="bio">
        <p>Born in Russia, raised between continents, Nina has built a body of work across nine cities and four continents — from Moscow to Tokyo to the San Francisco studios where she first began.</p>
        <p>Her work spans editorial, campaign, and runway, with recent projects for Korean labels Kirsh, Soonsu, Daughter, Verte, Peachy, Adaul, and A&amp;B alongside editorial shoots in Paris, London and New York.</p>
        <p>She is currently based in Saigon, shooting and travelling for work throughout Southeast Asia.</p>
    </section>

    <section class="stats">
        <div class="stat"><div class="n">21</div><div class="l">Years</div></div>
        <div class="stat"><div class="n">9</div><div class="l">Cities</div></div>
        <div class="stat"><div class="n">4</div><div class="l">Continents</div></div>
    </section>

    <section class="cities">
        <div class="heading">Worked in</div>
        <div class="city-list">
            <span class="c current">Saigon</span><span class="sep">·</span>
            <span class="c">Seoul</span><span class="sep">·</span>
            <span class="c">Tokyo</span><span class="sep">·</span>
            <span class="c">Moscow</span><span class="sep">·</span>
            <span class="c">Paris</span><span class="sep">·</span>
            <span class="c">London</span><span class="sep">·</span>
            <span class="c">New&nbsp;York</span><span class="sep">·</span>
            <span class="c">San&nbsp;Francisco</span>
        </div>
    </section>

    <section class="contact">
        <div class="item">
            <div class="label">Booking</div>
            <a href="mailto:">email</a>
        </div>
        <div class="item">
            <div class="label">Instagram</div>
            <a href="#" target="_blank" rel="noopener">@nina</a>
        </div>
        <div class="item">
            <div class="label">Based</div>
            <span>Saigon, Vietnam</span>
        </div>
    </section>
</main>

<script>
// ── Flower background: sprites sliced from flowers.png atlas ──
(function() {
    const canvas = document.getElementById('bg-flowers');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0, dpr = 1;

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        canvas.style.width = W + 'px';
        canvas.style.height = H + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    // Atlas: uniform 12 × 7 grid, no gap, no shave.
    const COLS = 12, ROWS = 7;
    const atlas = new Image();
    atlas.src = '../assets/images/flowers2.png';
    let atlasCanvas = null;
    const TILES = [];
    let atlasReady = false;

    atlas.addEventListener('load', () => {
        const off = document.createElement('canvas');
        off.width = atlas.naturalWidth;
        off.height = atlas.naturalHeight;
        const octx = off.getContext('2d');
        octx.drawImage(atlas, 0, 0);
        const img = octx.getImageData(0, 0, off.width, off.height);
        const d = img.data;
        for (let i = 0; i < d.length; i += 4) {
            const r = d[i], g = d[i+1], b = d[i+2];
            const m = Math.min(r, g, b);
            if (m >= 228) {
                d[i+3] = 0;
            } else if (m >= 185) {
                const t = (m - 185) / 43;
                d[i+3] = Math.round(d[i+3] * (1 - t));
            }
        }
        octx.putImageData(img, 0, 0);
        atlasCanvas = off;

        const cw = atlas.naturalWidth / COLS;
        const ch = atlas.naturalHeight / ROWS;
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                TILES.push({ sx: c * cw, sy: r * ch, sw: cw, sh: ch });
            }
        }
        atlasReady = true;
    });

    const rand = (a, b) => a + Math.random() * (b - a);
    const pickTile = () => TILES[Math.floor(Math.random() * TILES.length)];
    function easeOutBack(t) { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); }

    class Petal {
        constructor(y) {
            this.x = rand(-20, W + 20);
            this.y = y !== undefined ? y : rand(-160, -40);
            this.size = rand(70, 150);
            this.tile = pickTile();
            this.vx = rand(-0.25, 0.25);
            this.vy = rand(0.35, 0.85);
            this.rotation = rand(0, Math.PI * 2);
            this.rotSpeed = rand(-0.01, 0.01);
            this.swayPhase = rand(0, Math.PI * 2);
            this.swayAmp = rand(0.3, 0.9);
            this.swayFreq = rand(0.0008, 0.0016);
            this.ox = 0; this.oy = 0;
            this.life = 0;
        }
        update(dt) {
            this.life += dt;
            this.ox *= 0.92; this.oy *= 0.92;
            this.y += this.vy * (dt / 16) + this.oy * (dt / 16) * 0.4;
            this.x += (this.vx + Math.sin(this.life * this.swayFreq + this.swayPhase) * this.swayAmp) * (dt / 16) + this.ox * (dt / 16) * 0.4;
            this.rotation += this.rotSpeed * (dt / 16);
            this.done = this.y > H + 120 || this.x < -160 || this.x > W + 160;
        }
        draw(ctx) {
            if (!this.tile || !atlasCanvas) return;
            const aspect = this.tile.sh / this.tile.sw;
            const w = this.size, h = w * aspect;
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.rotation);
            ctx.drawImage(atlasCanvas, this.tile.sx, this.tile.sy, this.tile.sw, this.tile.sh, -w/2, -h/2, w, h);
            ctx.restore();
        }
    }

    const petals = [];
    const MAX_PETALS = 16;
    let lastSpawn = 0, lastTime = performance.now();
    let visible = !document.hidden;
    let mouseX = -1e6, mouseY = -1e6;
    document.addEventListener('visibilitychange', () => { visible = !document.hidden; lastTime = performance.now(); });
    window.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; }, { passive: true });
    window.addEventListener('mouseleave', () => { mouseX = -1e6; mouseY = -1e6; });

    atlas.addEventListener('load', () => {
        for (let i = 0; i < 6; i++) petals.push(new Petal(rand(-H * 0.3, H)));
    });

    function applyRepulsion() {
        const MIN_DIST = 120;
        const MOUSE_RADIUS = 180;
        const MOUSE_STRENGTH = 2.2;
        for (let i = 0; i < petals.length; i++) {
            const a = petals[i];
            if (mouseX > -1e5) {
                const dx = a.x - mouseX, dy = a.y - mouseY;
                const d2 = dx * dx + dy * dy;
                if (d2 < MOUSE_RADIUS * MOUSE_RADIUS && d2 > 1) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d / MOUSE_RADIUS) * MOUSE_STRENGTH;
                    a.ox += (dx / d) * f; a.oy += (dy / d) * f;
                }
            }
            for (let j = i + 1; j < petals.length; j++) {
                const b = petals[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const d2 = dx * dx + dy * dy;
                if (d2 < MIN_DIST * MIN_DIST && d2 > 1) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d / MIN_DIST) * 0.35;
                    const fx = (dx / d) * f, fy = (dy / d) * f;
                    a.ox += fx; a.oy += fy;
                    b.ox -= fx; b.oy -= fy;
                }
            }
        }
    }

    function loop(now) {
        requestAnimationFrame(loop);
        if (!visible || !atlasReady) { lastTime = now; return; }
        const dt = Math.min(60, now - lastTime); lastTime = now;
        if (now - lastSpawn > rand(900, 1800) && petals.length < MAX_PETALS) {
            petals.push(new Petal()); lastSpawn = now;
        }
        applyRepulsion();
        ctx.clearRect(0, 0, W, H);
        for (let i = petals.length - 1; i >= 0; i--) {
            petals[i].update(dt); petals[i].draw(ctx);
            if (petals[i].done) petals.splice(i, 1);
        }
    }
    requestAnimationFrame((t) => { lastTime = t; loop(t); });
})();
</script>
</html>
