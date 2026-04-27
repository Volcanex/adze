<style>
:root {
    --ink: #111;
    --paper: #fff;
    --muted: #666;
    --rule: #111;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--ink);
    background: var(--paper);
    line-height: 1.5;
    min-height: 100vh;
    padding: 32px 40px;
}

a { color: var(--ink); text-decoration: none; }
a:hover { text-decoration: underline; }

.site-name {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-size: 22px;
    display: inline-block;
    margin-bottom: 18px;
}

.top-row {
    display: grid;
    grid-template-columns: minmax(260px, 340px) 1fr;
    gap: 40px;
    padding-bottom: 24px;
    border-bottom: 1.5px solid var(--rule);
}

.left-col { display: flex; flex-direction: column; gap: 18px; }

.art-panel {
    width: 100%;
    aspect-ratio: 4 / 3;
    border: 1.5px solid var(--ink);
    background: var(--paper);
    position: relative;
    overflow: hidden;
}
.art-panel img {
    position: absolute;
    inset: 0;
    width: 100%; height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity 0.25s ease;
}
.art-panel img.default { opacity: 1; }
.art-panel[class*="show-"] img.default { opacity: 0; }
.art-panel.show-1 img.v1,
.art-panel.show-2 img.v2,
.art-panel.show-3 img.v3,
.art-panel.show-itch img.v-itch,
.art-panel.show-yt img.v-yt,
.art-panel.show-tumblr img.v-tumblr,
.art-panel.show-kofi img.v-kofi,
.art-panel.show-neo img.v-neo { opacity: 1; }

.recents-label { font-size: 14px; letter-spacing: 0.5px; color: var(--muted); }

ul.recents { list-style: none; display: flex; flex-direction: column; gap: 8px; }
ul.recents li { display: flex; align-items: center; gap: 10px; font-size: 15px; }
ul.recents li::before {
    content: '';
    width: 7px; height: 7px;
    border: 1.2px solid var(--ink);
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
ul.recents .kind {
    display: inline-block;
    padding: 1px 10px;
    border: 1.2px solid var(--ink);
    border-radius: 999px;
    font-size: 13px;
}
ul.recents .date { color: var(--muted); margin-left: auto; font-variant-numeric: tabular-nums; }

.socials {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}
.socials a {
    width: 52px; height: 52px;
    border: 1.5px solid var(--ink);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 500;
    transition: background 0.15s ease, color 0.15s ease;
}
.socials a:hover { background: var(--ink); color: var(--paper); text-decoration: none; }

.archive-box {
    align-self: flex-start;
    padding: 8px 24px;
    border: 1.5px solid var(--ink);
    font-size: 14px;
    margin-top: 4px;
}

.right-col {
    display: flex;
    align-items: stretch;
    justify-content: center;
    height: 100%;
}
.landscape {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: stretch;
    justify-content: center;
    overflow: hidden;
    border: 1.5px solid var(--ink);
}
.landscape img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

@media (max-width: 860px) {
    .top-row { grid-template-columns: minmax(220px, 280px) 1fr; gap: 24px; }
}
@media (max-width: 600px) {
    .top-row { grid-template-columns: 1fr; }
    .right-col { display: none; }
}

.portfolio { padding-top: 32px; }
.portfolio h2 {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-weight: 400;
    font-size: 28px;
    margin-bottom: 20px;
}
.portfolio .cols {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
}
.portfolio h3 {
    font-family: 'Cardo', serif;
    font-style: italic;
    font-weight: 400;
    font-size: 20px;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--ink);
}
.portfolio ul { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.portfolio ul li { font-size: 14px; color: var(--muted); }

@media (max-width: 700px) {
    .portfolio .cols { grid-template-columns: 1fr; }
    body { padding: 20px; }
}
</style>
<html>
<a href="../home/" class="site-name">exopta</a>

<section class="top-row">
    <div class="left-col">
        <div class="art-panel" id="art">
            <img class="default" alt="" src="../assets/images/1._.png">
            <img class="v1" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23f4c3b0'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='34' fill='%23222'>song</text></svg>">
            <img class="v2" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23b5d0c0'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='34' fill='%23222'>comic</text></svg>">
            <img class="v3" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23c9bde0'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='34' fill='%23222'>smthn else</text></svg>">
            <img class="v-itch" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23fa5c5c'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='40' fill='%23fff'>itch.io</text></svg>">
            <img class="v-yt" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23ffd166'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='40' fill='%23222'>youtube</text></svg>">
            <img class="v-tumblr" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23355070'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='40' fill='%23fff'>tumblr</text></svg>">
            <img class="v-kofi" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%2372b89b'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='40' fill='%23fff'>ko-fi</text></svg>">
            <img class="v-neo" alt="" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23c9bde0'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Cardo, serif' font-style='italic' font-size='36' fill='%23222'>neocities</text></svg>">
        </div>

        <div class="recents-label">recents</div>
        <ul class="recents">
            <li data-hover="1"><a href="#"><span class="kind">song</span></a><span class="date">— 01.26</span></li>
            <li data-hover="2"><a href="#"><span class="kind">comic</span></a><span class="date">— 12.25</span></li>
            <li data-hover="3"><a href="#"><span class="kind">smthn else</span></a><span class="date">— 05.25</span></li>
        </ul>

        <div class="socials">
            <a href="https://exopta.itch.io/" data-hover="itch" target="_blank" rel="noopener">itch.io</a>
            <a href="https://www.youtube.com/channel/UCZ8lGp-0KZ0aK_7kGh0LxEQ" data-hover="yt" target="_blank" rel="noopener">yt</a>
            <a href="https://exopta.tumblr.com/" data-hover="tumblr" target="_blank" rel="noopener">tumblr</a>
            <a href="#" data-hover="kofi" target="_blank" rel="noopener">kofi</a>
            <a href="https://exopta.neocities.org/" data-hover="neo" target="_blank" rel="noopener">neo</a>
        </div>

        <a href="../archive/" class="archive-box">archive</a>
    </div>

    <div class="right-col">
        <div class="landscape">
            <img src="../assets/images/gif_placeholder.png" alt="">
        </div>
    </div>
</section>

<section class="portfolio">
    <h2>portfolio</h2>
    <div class="cols">
        <div>
            <h3>music</h3>
            <ul><li>— (add tracks)</li></ul>
        </div>
        <div>
            <h3>art</h3>
            <ul><li>— (add pieces)</li></ul>
        </div>
        <div>
            <h3>anim</h3>
            <ul><li>— (add animations)</li></ul>
        </div>
    </div>
</section>

<script>
(function () {
    var panel = document.getElementById('art');
    if (!panel) return;
    function clearShow() {
        panel.className = panel.className.replace(/\bshow-\S+/g, '').trim();
    }
    document.querySelectorAll('[data-hover]').forEach(function (el) {
        var n = el.getAttribute('data-hover');
        el.addEventListener('mouseenter', function () {
            clearShow();
            panel.classList.add('show-' + n);
        });
        el.addEventListener('mouseleave', clearShow);
    });
})();
</script>
</html>
