"""
Alfie Bruce personal admin — /admin on alfiebruce.com.
Manages gallery_meta.json and triggers recompile.
Only activates when domain is alfiebruce.com.
"""

import io
import json
import re
from pathlib import Path
from flask import request, jsonify, make_response, abort, send_file

try:
    from features.artist_admin import ArtistAdmin
except ImportError:
    from artist_admin import ArtistAdmin

ARTIST_SLUG = 'alfiebruce'
DOMAIN = 'alfiebruce.com'
COOKIE = 'alfie_admin'
PANEL_URL = '/api/alfie-admin/panel'
ARTIST_DIR = Path(f'artists/{ARTIST_SLUG}')
ASSETS_DIR = ARTIST_DIR / 'assets'
WORK_DIR = ASSETS_DIR / 'work'
META_PATH = WORK_DIR / 'gallery_meta.json'
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}


def _render():
    """Regenerate Alfie's home + category pages from gallery_meta.json (the
    source of truth) and return the generated page slugs so the framework marks
    them read-only."""
    regenerate()
    return ['home'] + _categories()


admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, render=_render, blueprint_name='alfie_admin')
bp = admin.bp
_auth_required = admin.auth_required
_domain_guard = admin.domain_guard
_get_token = admin.token


def _load_meta():
    if META_PATH.exists():
        return json.loads(META_PATH.read_text())
    return {}


def _save_meta(data):
    META_PATH.write_text(json.dumps(data, ensure_ascii=False))


def _categories():
    meta = _load_meta()
    return [k for k in meta.keys() if not k.startswith('__')]


def _slugify(text):
    s = re.sub(r'[^a-z0-9-]', '-', text.lower())
    return re.sub(r'-+', '-', s).strip('-')


# ── Page generation ────────────────────────────────────────────────────────────

_CATEGORY_STYLE = """\
<style>
:root{--bg:#000;--text:#fff;--muted:#999;--line:rgba(255,255,255,.14);--sans:'Helvetica Neue',Helvetica,Arial,sans-serif;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:var(--sans);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;opacity:0;animation:fade .6s ease forwards;}
@keyframes fade{to{opacity:1;}}
img{display:block;max-width:100%;}
a{color:inherit;text-decoration:none;}
.bar{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;align-items:center;justify-content:space-between;padding:22px 34px;mix-blend-mode:difference;}
.bar .mark{font-size:15px;letter-spacing:.32em;text-transform:uppercase;font-weight:500;}
.bar nav{display:flex;gap:30px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;}
.bar nav a{color:var(--muted);transition:color .2s ease;}
.bar nav a:hover{color:var(--text);}
.head{padding:30vh 34px 8vh;border-bottom:1px solid var(--line);}
.head h1{font-size:clamp(38px,8vw,104px);font-weight:600;letter-spacing:.04em;text-transform:uppercase;line-height:.95;}
.head p{margin-top:18px;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);}
.gallery{display:flex;flex-wrap:wrap;gap:3px;padding:3px;}
.gallery a{position:relative;height:320px;overflow:hidden;background:#111;cursor:pointer;}
.gallery img{width:100%;height:100%;object-fit:cover;filter:grayscale(8%) brightness(.86);transition:filter .5s ease,transform .9s cubic-bezier(.2,.7,.2,1);}
.gallery a:hover img{filter:grayscale(0%) brightness(1);transform:scale(1.04);}
.foot{padding:14vh 34px;text-align:center;border-top:1px solid var(--line);}
.foot a{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid transparent;padding-bottom:3px;transition:color .2s,border-color .2s;}
.foot a:hover{color:var(--text);border-color:var(--text);}
.lb{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.96);display:none;align-items:center;justify-content:center;}
.lb.open{display:flex;}
.lb img{max-width:92vw;max-height:88vh;object-fit:contain;}
.lb .x,.lb .nav-arrow{position:absolute;color:#fff;cursor:pointer;user-select:none;opacity:.65;transition:opacity .2s;}
.lb .x:hover,.lb .nav-arrow:hover{opacity:1;}
.lb .x{top:24px;right:30px;font-size:30px;line-height:1;}
.lb .nav-arrow{top:50%;transform:translateY(-50%);font-size:44px;padding:20px;}
.lb .prev{left:14px;}
.lb .next{right:14px;}
.lb .count{position:absolute;bottom:24px;left:0;right:0;text-align:center;font-size:12px;letter-spacing:.18em;color:var(--muted);}
@media(max-width:720px){.bar{padding:18px 20px;}.bar nav{gap:18px;}.head{padding:24vh 20px 6vh;}.gallery a{height:auto;flex:1 1 100% !important;}.gallery img{height:auto;}.lb .nav-arrow{font-size:34px;padding:10px;}}
</style>"""

_CATEGORY_SCRIPT = """\
<script>
(function(){
  var links=[].slice.call(document.querySelectorAll('.gallery a'));
  var lb=document.getElementById('lb'),img=document.getElementById('lb-img'),cnt=document.getElementById('lb-count'),i=0;
  function show(n){i=(n+links.length)%links.length;img.src=links[i].getAttribute('data-src');cnt.textContent=(i+1)+' / '+links.length;}
  links.forEach(function(a,n){a.addEventListener('click',function(e){e.preventDefault();show(n);lb.classList.add('open');});});
  lb.addEventListener('click',function(e){var act=e.target.getAttribute('data-act');if(act==='close'||e.target===lb)lb.classList.remove('open');else if(act==='next')show(i+1);else if(act==='prev')show(i-1);});
  document.addEventListener('keydown',function(e){if(!lb.classList.contains('open'))return;if(e.key==='Escape')lb.classList.remove('open');else if(e.key==='ArrowRight')show(i+1);else if(e.key==='ArrowLeft')show(i-1);});
})();
</script>"""


def _title_case(slug):
    return slug.replace('-', ' ').title()


def _generate_category_page(slug, photos):
    title = _title_case(slug)
    count = len(photos)
    lines = [_CATEGORY_STYLE, '<html>']
    lines.append(f'<div class="bar">')
    lines.append(f'    <a href="../home/" class="mark">Alfie Bruce</a>')
    lines.append(f'    <nav>')
    lines.append(f'        <a href="../home/#work">Work</a>')
    lines.append(f'        <a href="../home/#contact">Contact</a>')
    lines.append(f'    </nav>')
    lines.append(f'</div>')
    lines.append(f'')
    lines.append(f'<header class="head">')
    lines.append(f'    <h1>{title}</h1>')
    lines.append(f'    <p>{count} photograph{"s" if count != 1 else ""} &middot; 2025</p>')
    lines.append(f'</header>')
    lines.append(f'')
    lines.append(f'<section class="gallery" id="gallery">')
    for photo in photos:
        f = photo['f']
        ar = photo['ar']
        basis = int(ar * 320)
        lines.append(
            f'    <a data-src="../assets/work/{slug}/{f}" style="flex:{ar} 1 {basis}px">'
            f'<img src="../assets/work/{slug}/{f}" loading="lazy" alt="{title}"></a>'
        )
    lines.append(f'</section>')
    lines.append(f'')
    lines.append(f'<div class="foot"><a href="../home/#work">&larr; Back to all work</a></div>')
    lines.append(f'')
    lines.append(f'<div class="lb" id="lb">')
    lines.append(f'    <span class="x" data-act="close">&times;</span>')
    lines.append(f'    <span class="nav-arrow prev" data-act="prev">&#8249;</span>')
    lines.append(f'    <img id="lb-img" src="" alt="">')
    lines.append(f'    <span class="nav-arrow next" data-act="next">&#8250;</span>')
    lines.append(f'    <div class="count" id="lb-count"></div>')
    lines.append(f'</div>')
    lines.append(f'')
    lines.append(_CATEGORY_SCRIPT)
    lines.append('</html>')
    return '\n'.join(lines)


_HOME_STYLE = """\
<style>
@font-face {
    font-family: 'Blackbird';
    src: url('../assets/fonts/Projekt_Blackbird_v2.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}

:root {
    --bg: #000;
    --panel: #111;
    --text: #fff;
    --muted: #999;
    --line: rgba(255,255,255,0.14);
    --sans: 'Blackbird', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    --display: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    opacity: 0;
    animation: fade 0.8s ease forwards;
}
@keyframes fade { to { opacity: 1; } }
img { display: block; max-width: 100%; }
a { color: inherit; text-decoration: none; }
.bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 22px 34px;
    mix-blend-mode: difference;
}
.bar .mark { font-size: 15px; letter-spacing: 0.32em; text-transform: uppercase; font-weight: 500; }
.bar nav { display: flex; gap: 30px; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; }
.bar nav a { color: var(--muted); transition: color 0.2s ease; }
.bar nav a:hover { color: var(--text); }
.hero {
    position: relative;
    height: 100vh;
    display: flex;
    align-items: flex-start;
    overflow: hidden;
}
.hero-bg {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover;
    filter: grayscale(8%) brightness(0.78);
    will-change: transform;
}
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.65) 100%);
}
.hero .title {
    position: relative;
    z-index: 2;
    padding: 16vh 34px 0;
}
.hero .title h1 {
    font-family: var(--display);
    font-size: clamp(80px, 22vw, 320px);
    line-height: 0.86;
    font-weight: 900;
    letter-spacing: -0.03em;
    text-transform: uppercase;
    color: #fff;
    position: relative;
}
.hero .title h1::after {
    content: '';
    position: absolute;
    inset: 0;
    background: url(../assets/images/ALFIE_GRAIN_TEXTURE.png) repeat;
    background-size: 120px 120px;
    opacity: 0.05;
    pointer-events: none;
}
.hero .title p {
    margin-top: 18px;
    font-size: 14px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted);
    max-width: 34ch;
    line-height: 1.7;
}
.work {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2px;
    background: var(--bg);
}
.card {
    position: relative;
    aspect-ratio: 16 / 10;
    overflow: hidden;
    background: var(--panel);
}
.card img {
    width: 100%; height: 100%;
    object-fit: cover;
    object-position: center 50%;
    filter: grayscale(10%) brightness(0.82);
    transition: filter 0.6s ease;
}
.card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.18);
    transition: background 0.6s ease;
}
.card:hover img { filter: grayscale(0%) brightness(0.92); }
.card:hover::after { background: rgba(0,0,0,0); }
.card .meta {
    position: absolute;
    z-index: 2;
    left: 0; bottom: 0;
    padding: 26px 30px;
    display: flex;
    align-items: baseline;
    gap: 16px;
}
.card .meta h3 {
    font-size: clamp(20px, 2.4vw, 34px);
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.contact {
    padding: 16vh 34px;
    text-align: center;
    border-top: 1px solid var(--line);
}
.contact h2 { font-size: clamp(28px, 5vw, 58px); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
.contact p { margin-top: 22px; font-size: 14px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); }
.contact .links {
    margin-top: 34px;
    display: flex;
    gap: 26px;
    justify-content: center;
    font-size: 13px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.contact .links a { color: var(--muted); border-bottom: 1px solid transparent; padding-bottom: 3px; transition: color 0.2s ease, border-color 0.2s ease; }
.contact .links a:hover { color: var(--text); border-color: var(--text); }
footer { padding: 30px 34px; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: #555; text-align: center; }
@media (max-width: 720px) {
    .work { grid-template-columns: 1fr; }
    .bar { padding: 18px 20px; }
    .bar nav { gap: 18px; }
    .hero { height: 60vh; }
    .hero .title { padding-top: 10vh; }
    .hero .title, .contact, .card .meta { padding-left: 20px; padding-right: 20px; }
}
</style>"""

_HOME_SCRIPT = """\
<script>
(function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll('.card img'));
    var ticking = false;
    function update() {
        var vh = window.innerHeight;
        for (var i = 0; i < cards.length; i++) {
            var img = cards[i];
            var r = img.parentElement.getBoundingClientRect();
            if (r.bottom < 0 || r.top > vh) continue;
            var p = 1 - (r.top + r.height / 2) / (vh / 2);
            p = Math.max(-1, Math.min(1, p));
            img.style.objectPosition = 'center ' + (50 + p * 14) + '%';
        }
        ticking = false;
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
})();

(function () {
    var videos = [
        '../assets/hero-9413e3f36daf481cbe922b0dfc3c79be.mp4',
        '../assets/hero-70ee9da9be374cbba155d2fedfb03338.mp4',
        '../assets/hero-88787babb0124739bf5174b9681a0cef.mp4',
        '../assets/hero-4980d655f5eb4e34a2842ffd62a77c57.mp4'
    ];
    var idx = Math.floor(Math.random() * videos.length);
    var stallTimer = null;
    var v = document.getElementById('hero-video');
    if (!v) return;
    v.src = videos[idx];
    v.load();
    v.play();
    function advance() {
        if (stallTimer) { clearTimeout(stallTimer); stallTimer = null; }
        idx = (idx + 1) % videos.length;
        v.src = videos[idx];
        v.load();
        v.play();
    }
    function armStallGuard() {
        if (stallTimer) clearTimeout(stallTimer);
        stallTimer = setTimeout(advance, 8000);
    }
    v.addEventListener('ended', advance);
    v.addEventListener('stalled', advance);
    v.addEventListener('error', advance);
    v.addEventListener('playing', function () { if (stallTimer) { clearTimeout(stallTimer); stallTimer = null; } });
    v.addEventListener('waiting', armStallGuard);
})();
</script>"""


def _generate_home_page(categories, hero_category=None, hero_photo=None):
    lines = [_HOME_STYLE, '<html>']
    lines.append('<div class="bar">')
    lines.append('    <a href="#top" class="mark">Photography &amp; Videography</a>')
    lines.append('    <nav>')
    lines.append('        <a href="#work">Work</a>')
    lines.append('        <a href="#contact">Contact</a>')
    lines.append('    </nav>')
    lines.append('</div>')
    lines.append('')
    lines.append('<section class="hero" id="top">')
    lines.append('    <video class="hero-bg" autoplay muted playsinline id="hero-video"></video>')
    lines.append('    <div class="title">')
    lines.append('        <h1>Alfie<br>Bruce</h1>')
    lines.append('    </div>')
    lines.append('</section>')
    lines.append('')
    lines.append('<section class="work" id="work">')
    for cat in categories:
        title = _title_case(cat)
        cover = f'../assets/work/{cat}.jpg'
        lines.append(f'    <a class="card" href="../{cat}/">')
        lines.append(f'        <img src="{cover}" alt="{title}">')
        lines.append(f'        <div class="meta"><h3>{title}</h3></div>')
        lines.append(f'    </a>')
    lines.append('    <a class="card" href="../videography/">')
    lines.append('        <img src="../assets/poster-9413e3f36daf481cbe922b0dfc3c79be.jpg" alt="Videography">')
    lines.append('        <div class="meta"><h3>Videography</h3></div>')
    lines.append('    </a>')
    lines.append('</section>')
    lines.append('')
    lines.append('<section class="contact" id="contact">')
    lines.append('    <h2>Get in touch</h2>')
    lines.append('    <p>Available for festivals, gigs, events &amp; portrait commissions</p>')
    lines.append('    <div class="links">')
    lines.append('        <a href="mailto:alfiebruce333@gmail.com">Email</a>')
    lines.append('        <a href="sms:+447906144118">+44 7906 144 118</a>')
    lines.append('        <a href="#">Instagram</a>')
    lines.append('    </div>')
    lines.append('</section>')
    lines.append('')
    lines.append('<footer>&copy; Alfie Bruce 2025</footer>')
    lines.append('')
    lines.append(_HOME_SCRIPT)
    lines.append('</html>')
    return '\n'.join(lines)


def regenerate():
    meta = _load_meta()
    categories = [k for k in meta.keys() if not k.startswith('__')]

    # Regenerate each category page
    for slug in categories:
        photos = meta[slug]
        page_dir = ARTIST_DIR / slug
        page_dir.mkdir(exist_ok=True)
        cfg_path = page_dir / 'config.json'
        if not cfg_path.exists():
            cfg_path.write_text(json.dumps({
                'title': f'Alfie Bruce — {_title_case(slug)}',
                'slug': f'artists/{ARTIST_SLUG}/{slug}',
                'description': f'{_title_case(slug)} — photography by Alfie Bruce',
                'categories': []
            }, indent=4))
        (page_dir / 'content.md').write_text(_generate_category_page(slug, photos))

    # Regenerate home page
    home_dir = ARTIST_DIR / 'home'
    home_dir.mkdir(exist_ok=True)
    (home_dir / 'content.md').write_text(_generate_home_page(categories))


# ── HTML ───────────────────────────────────────────────────────────────────────

ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — Alfie Bruce</title>
<style>
@font-face {
  font-family: 'Blackbird';
  font-style: normal;
  font-display: swap;
  src: url('/api/alfie-admin/font/Projekt_Blackbird_v2.otf') format('opentype');
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Blackbird', 'Helvetica Neue', sans-serif;
  background: #000; color: #fff;
  max-width: 414px; margin: 0 auto;
  padding: 0 16px 80px;
  min-height: 100vh;
}

/* header */
.hd {
  height: 54px; display: flex; align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 32px;
  position: sticky; top: 0; background: #000; z-index: 10;
}
.hd-brand { font-weight: normal; font-size: 20px; letter-spacing: 0.15em; text-transform: uppercase; }
.hd-action { font-size: 12px; font-weight: normal; cursor: pointer; background: none; border: none; font-family: inherit; padding: 0; color: #666; letter-spacing: 0.1em; text-transform: uppercase; }
.hd-action:hover { color: #fff; }

/* login */
#screen-login { padding-top: 80px; }
#screen-login h2 { font-weight: normal; font-size: 18px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 28px; color: #888; }

/* categories list */
.cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; margin-bottom: 24px; }
.cat-card {
  position: relative; aspect-ratio: 16/10; overflow: hidden;
  background: #111; cursor: pointer; border: none; padding: 0;
}
.cat-card img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.6); transition: filter 0.4s ease; display: block; }
.cat-card:hover img { filter: brightness(0.8); }
.cat-card .cat-label {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 12px; background: linear-gradient(transparent, rgba(0,0,0,0.8));
}
.cat-card .cat-name { font-size: 13px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: normal; }
.cat-card .cat-count { font-size: 10px; color: #888; letter-spacing: 0.1em; margin-top: 2px; }
.cat-card .cat-placeholder { width: 100%; height: 100%; background: #111; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #333; }

/* add category row */
.add-row { padding: 16px 0; border-top: 1px solid rgba(255,255,255,0.1); }
.add-form { display: none; margin-top: 12px; }
.add-form.open { display: block; }

/* back button */
.back-btn {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: normal; cursor: pointer;
  background: none; border: none; font-family: inherit;
  padding: 0; margin-bottom: 24px; color: #666; letter-spacing: 0.1em; text-transform: uppercase;
}
.back-btn:hover { color: #fff; }

/* section heading */
.section-title { font-size: 22px; font-weight: normal; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px; }
.section-sub { font-size: 11px; color: #666; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 24px; }

/* cover photo */
.cover-block { margin-bottom: 28px; }
.cover-block h3 { font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: #666; margin-bottom: 10px; }
.cover-img { width: 100%; aspect-ratio: 16/10; object-fit: cover; display: block; background: #111; }
.cover-placeholder { width: 100%; aspect-ratio: 16/10; background: #111; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #555; letter-spacing: 0.1em; text-transform: uppercase; }

/* photo grid */
.photo-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; margin-bottom: 20px; }
.photo-item { position: relative; aspect-ratio: 1; overflow: hidden; background: #111; }
.photo-item img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photo-del {
  position: absolute; top: 4px; right: 4px;
  background: rgba(0,0,0,0.75); color: #fff; border: none;
  font-size: 14px; line-height: 1; padding: 3px 6px;
  cursor: pointer; font-family: inherit; opacity: 0;
  transition: opacity 0.2s;
}
.photo-item:hover .photo-del { opacity: 1; }
.photo-cover {
  position: absolute; bottom: 4px; left: 4px;
  background: rgba(0,0,0,0.75); color: #fff; border: none;
  font-size: 9px; line-height: 1; padding: 4px 6px;
  cursor: pointer; font-family: inherit; opacity: 0;
  transition: opacity 0.2s; letter-spacing: 0.08em; text-transform: uppercase;
}
.photo-item:hover .photo-cover { opacity: 1; }
.photo-item.is-cover .photo-cover { opacity: 1; background: rgba(255,255,255,0.9); color: #000; }

/* fields */
.field { margin-bottom: 16px; }
.field label {
  display: block; font-size: 10px; font-weight: normal;
  letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 7px; color: #888;
}
.field input {
  width: 100%; border: 1px solid rgba(255,255,255,0.15); padding: 10px 12px;
  font-family: inherit; font-size: 15px; font-weight: normal;
  background: #0a0a0a; color: #fff; outline: none; border-radius: 0; -webkit-appearance: none;
  letter-spacing: 0.05em;
}
.field input:focus { border-color: #fff; }
.field input[type=file] { padding: 8px 12px; font-size: 13px; color: #aaa; }

/* buttons */
.btn {
  display: inline-block; border: 1px solid rgba(255,255,255,0.25); padding: 11px 22px;
  font-family: inherit; font-size: 12px; font-weight: normal;
  background: #fff; color: #000; cursor: pointer;
  letter-spacing: 0.12em; text-transform: uppercase; border-radius: 0; -webkit-appearance: none;
  transition: opacity .15s ease;
}
.btn:hover { opacity: 0.82; }
.btn:active { transform: translateY(1px); }
.btn:disabled { opacity: 0.3; cursor: default; transform: none; }
.btn-ghost { background: transparent; color: #fff; border-color: rgba(255,255,255,0.2); }
.btn-ghost:hover { border-color: #fff; opacity: 1; }
.btn-danger { background: transparent; color: #ff4444; border-color: rgba(255,68,68,0.3); }
.btn-danger:hover { background: #ff4444; color: #fff; border-color: #ff4444; opacity: 1; }
.btn-sm { padding: 7px 14px; font-size: 11px; }
.btn-row { display: flex; gap: 10px; align-items: center; margin-top: 20px; flex-wrap: wrap; }
.btn-row .spacer { flex: 1; }

/* publish block */
.publish-block { margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.1); }
.publish-block h3 { font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: #666; margin-bottom: 14px; }

/* status */
.status-msg { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 10px; }
.status-msg.ok  { color: #4caf50; }
.status-msg.err { color: #ff4444; }

/* divider */
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 28px 0; }

/* top tabs */
.tabnav { display: flex; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 28px; }
.tabnav button {
  flex: 1; background: none; border: none; font-family: inherit; color: #666;
  font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 14px 0; cursor: pointer; border-bottom: 2px solid transparent; transition: color .15s;
}
.tabnav button:hover { color: #aaa; }
.tabnav button.active { color: #fff; border-bottom-color: #fff; }

/* business card */
.card-stage { display: flex; flex-direction: column; align-items: center; gap: 24px; }
.bizcard {
  width: 85mm; height: 55mm; background: #fff; color: #000; position: relative;
  font-family: 'Blackbird', 'Helvetica Neue', sans-serif; overflow: hidden;
}
.bizcard .bc-top { position: absolute; top: 7mm; left: 7mm; }
.bizcard .bc-name { font-size: 9mm; line-height: 0.92; letter-spacing: 0.05em; text-transform: uppercase; }
.bizcard .bc-role { margin-top: 2.5mm; font-size: 3mm; letter-spacing: 0.12em; text-transform: uppercase; color: #444; }
.bizcard .bc-details {
  position: absolute; bottom: 7mm; left: 7mm; max-width: 42mm; font-size: 3mm; line-height: 1.8;
  letter-spacing: 0.07em; text-transform: uppercase;
}
.bizcard .bc-qr { position: absolute; top: 50%; right: 7mm; transform: translateY(-50%); width: 26mm; height: 26mm; }
.bizcard .bc-qr svg { width: 100%; height: 100%; display: block; }
.card-note { font-size: 10px; color: #555; letter-spacing: 0.1em; text-transform: uppercase; text-align: center; }

/* print-only helpers — hidden on screen */
#print-qr, #print-sheet { display: none; }
#print-qr svg { width: 60mm; height: 60mm; display: block; }

@media print {
  @page { size: A4; margin: 6mm; }
  body { background: #fff !important; max-width: none; padding: 0; min-height: 0; }
  .hd, .tabnav, .bc-actions, .card-note, #screen-login, #screen-list, #screen-edit { display: none !important; }
  #screen-card { display: block !important; }
  .bizcard { box-shadow: none; }

  /* default print = tile cards across the A4 sheet */
  .card-stage, #print-qr { display: none !important; }
  #print-sheet {
    display: grid !important;
    grid-template-columns: repeat(2, 85mm);
    gap: 2mm;
    justify-content: center;
    align-content: flex-start;
  }

  /* QR-only print mode */
  body.print-qr #print-sheet { display: none !important; }
  body.print-qr #print-qr { display: block !important; text-align: center; }
}
</style>
</head>
<body>

<!-- LOGIN -->
<div id="screen-login" style="display:none">
  <div class="hd"><span class="hd-brand">Alfie Bruce</span></div>
  <h2>Admin</h2>
  <div class="field" style="margin-top:24px">
    <label>Password</label>
    <input type="password" id="pw-input" autocomplete="current-password">
  </div>
  <button class="btn" id="login-btn">Enter</button>
  <div id="login-err" style="margin-top:12px;font-size:12px;color:#ff4444;letter-spacing:.08em;text-transform:uppercase;display:none">Wrong password</div>
</div>

<!-- CATEGORIES LIST -->
<div id="screen-list" style="display:none">
  <div class="hd">
    <span class="hd-brand">Alfie Bruce</span>
    <button class="hd-action" id="logout-btn">Log out</button>
  </div>

  <div class="tabnav">
    <button class="active" data-go="list">Photos</button>
    <button data-go="card">QR &amp; Card</button>
  </div>

  <div class="cat-grid" id="cat-grid"></div>

  <div class="add-row">
    <button class="btn btn-ghost btn-sm" id="add-cat-toggle">+ New category</button>
    <div class="add-form" id="add-cat-form">
      <div class="field" style="margin-top:12px">
        <label>Category name</label>
        <input type="text" id="new-cat-name" placeholder="e.g. Street">
      </div>
      <div class="btn-row">
        <button class="btn btn-sm" id="new-cat-btn">Create</button>
        <button class="btn btn-ghost btn-sm" id="add-cat-cancel">Cancel</button>
      </div>
      <div class="status-msg" id="new-cat-msg" style="display:none"></div>
    </div>
  </div>

  <div class="publish-block">
    <h3>Publish changes</h3>
    <button class="btn" id="compile-btn">Save &amp; publish</button>
    <div class="status-msg" id="compile-msg" style="display:none"></div>
  </div>
</div>

<!-- CATEGORY EDITOR -->
<div id="screen-edit" style="display:none">
  <div class="hd">
    <span class="hd-brand">Alfie Bruce</span>
    <button class="hd-action" id="logout-btn-edit">Log out</button>
  </div>
  <button class="back-btn" id="back-btn">&#8592; All categories</button>

  <div class="section-title" id="edit-cat-name"></div>
  <div class="section-sub" id="edit-cat-count"></div>

  <!-- cover photo -->
  <div class="cover-block">
    <h3>Cover photo</h3>
    <div id="cover-wrap"></div>
    <div class="status-msg" id="cover-msg" style="display:none;margin-top:8px"></div>
  </div>

  <hr class="divider">

  <!-- gallery photos -->
  <div style="margin-bottom:12px">
    <div style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#666;margin-bottom:10px">Gallery photos</div>
    <div class="photo-grid" id="photo-grid"></div>
  </div>

  <!-- upload photos -->
  <div class="field">
    <label>Add photos</label>
    <input type="file" id="photo-files" accept="image/*" multiple>
  </div>
  <div class="btn-row">
    <button class="btn btn-sm" id="photo-upload-btn">Upload</button>
    <div class="status-msg" id="upload-msg" style="display:none"></div>
  </div>

  <hr class="divider">

  <!-- delete category -->
  <div>
    <div style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#666;margin-bottom:10px">Danger</div>
    <button class="btn btn-danger btn-sm" id="delete-cat-btn">Delete this category</button>
    <div class="status-msg" id="delete-cat-msg" style="display:none"></div>
  </div>

  <div class="publish-block">
    <h3>Publish changes</h3>
    <button class="btn" id="compile-btn-edit">Save &amp; publish</button>
    <div class="status-msg" id="compile-msg-edit" style="display:none"></div>
  </div>
</div>

<!-- QR & CARD -->
<div id="screen-card" style="display:none">
  <div class="hd">
    <span class="hd-brand">Alfie Bruce</span>
    <button class="hd-action" id="logout-btn-card">Log out</button>
  </div>

  <div class="tabnav">
    <button data-go="list">Photos</button>
    <button class="active" data-go="card">QR &amp; Card</button>
  </div>

  <div class="card-stage">
    <div class="bizcard">
      <div class="bc-top">
        <div class="bc-name">Alfie<br>Bruce</div>
        <div class="bc-role">Photographer<br>&amp; Videographer</div>
      </div>
      <div class="bc-details">
        alfiebruce333@gmail.com<br>
        +44 7906 144 118
      </div>
      <div class="bc-qr" id="bc-qr"></div>
    </div>
    <div class="bc-actions">
      <button class="btn" id="print-card-btn">Print cards (A4)</button>
      <button class="btn btn-ghost" id="print-qr-btn">Print QR only</button>
      <a class="btn btn-ghost" id="download-qr-btn" href="/api/alfie-admin/qr.png" download>Download QR (PNG)</a>
    </div>
    <div class="card-note">Print fills an A4 sheet with cards &middot; QR opens alfiebruce.com</div>
  </div>

  <!-- standalone QR, used only for "Print QR only" -->
  <div id="print-qr"></div>
  <!-- A4 grid of card copies, used only for "Print cards" -->
  <div id="print-sheet"></div>
</div>

<script>
(function () {
'use strict';

var BASE = '/api/alfie-admin';
var currentCat = null;

// ── utils ──────────────────────────────────────────────────────────────────

function show(id) {
  ['screen-login','screen-list','screen-edit','screen-card'].forEach(function(s) {
    document.getElementById(s).style.display = (s === id) ? '' : 'none';
  });
}

function setMsg(id, text, isErr) {
  var el = document.getElementById(id);
  el.textContent = text;
  el.className = 'status-msg ' + (isErr ? 'err' : 'ok');
  el.style.display = '';
}

function clearMsg(id) {
  var el = document.getElementById(id);
  el.style.display = 'none';
  el.textContent = '';
}

function api(method, path, body) {
  var opts = { method: method, headers: {} };
  if (body instanceof FormData) {
    opts.body = body;
  } else if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  return fetch(BASE + path, opts).then(function(r) {
    if (r.status === 401) { show('screen-login'); throw new Error('auth'); }
    return r.json();
  });
}

// ── auth ────────────────────────────────────────────────────────────────────

function checkAuth() {
  api('GET', '/categories').then(function() {
    loadCategories();
    show('screen-list');
  }).catch(function(e) {
    if (e.message !== 'auth') show('screen-login');
    else show('screen-login');
  });
}

document.getElementById('login-btn').addEventListener('click', function() {
  var pw = document.getElementById('pw-input').value;
  document.getElementById('login-err').style.display = 'none';
  api('POST', '/login', { token: pw }).then(function(d) {
    if (d.ok) { loadCategories(); show('screen-list'); }
    else { document.getElementById('login-err').style.display = ''; }
  }).catch(function() { document.getElementById('login-err').style.display = ''; });
});

document.getElementById('pw-input').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') document.getElementById('login-btn').click();
});

function doLogout() {
  api('POST', '/logout').then(function() { show('screen-login'); });
}
document.getElementById('logout-btn').addEventListener('click', doLogout);
document.getElementById('logout-btn-edit').addEventListener('click', doLogout);
document.getElementById('logout-btn-card').addEventListener('click', doLogout);

// ── tabs / card ───────────────────────────────────────────────────────────────

function loadCard() {
  var box = document.getElementById('bc-qr');
  if (box.dataset.loaded) return;
  fetch(BASE + '/qr.svg').then(function(r) { return r.text(); }).then(function(svg) {
    box.innerHTML = svg;
    document.getElementById('print-qr').innerHTML = svg;
    box.dataset.loaded = '1';
    buildSheet();
  });
}

// Fill the A4 print sheet with copies of the card (2 cols x 5 rows = 10).
function buildSheet() {
  var sheet = document.getElementById('print-sheet');
  var card = document.querySelector('.card-stage .bizcard');
  if (!sheet || !card) return;
  sheet.innerHTML = '';
  for (var i = 0; i < 10; i++) { sheet.appendChild(card.cloneNode(true)); }
}

Array.prototype.forEach.call(document.querySelectorAll('.tabnav button'), function(b) {
  b.addEventListener('click', function() {
    if (b.getAttribute('data-go') === 'card') { loadCard(); show('screen-card'); }
    else { loadCategories(); show('screen-list'); }
  });
});

document.getElementById('print-card-btn').addEventListener('click', function() { window.print(); });
document.getElementById('print-qr-btn').addEventListener('click', function() {
  document.body.classList.add('print-qr');
  window.print();
});
window.addEventListener('afterprint', function() { document.body.classList.remove('print-qr'); });

// ── categories list ─────────────────────────────────────────────────────────

function loadCategories() {
  api('GET', '/categories').then(function(cats) {
    renderCatGrid(cats);
  });
}

function renderCatGrid(cats) {
  var grid = document.getElementById('cat-grid');
  grid.innerHTML = '';
  cats.forEach(function(cat) {
    var btn = document.createElement('button');
    btn.className = 'cat-card';
    var coverTs = '?t=' + Date.now();
    btn.innerHTML =
      '<img src="' + BASE + '/cover/' + cat.slug + coverTs + '" ' +
        'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\'" ' +
        'alt="' + cat.name + '">' +
      '<div class="cat-placeholder" style="display:none">No cover</div>' +
      '<div class="cat-label">' +
        '<div class="cat-name">' + cat.name + '</div>' +
        '<div class="cat-count">' + cat.count + ' photo' + (cat.count !== 1 ? 's' : '') + '</div>' +
      '</div>';
    btn.addEventListener('click', function() { openCategory(cat.slug); });
    grid.appendChild(btn);
  });
}

// ── new category ────────────────────────────────────────────────────────────

document.getElementById('add-cat-toggle').addEventListener('click', function() {
  document.getElementById('add-cat-form').classList.toggle('open');
});
document.getElementById('add-cat-cancel').addEventListener('click', function() {
  document.getElementById('add-cat-form').classList.remove('open');
  document.getElementById('new-cat-name').value = '';
  clearMsg('new-cat-msg');
});

document.getElementById('new-cat-btn').addEventListener('click', function() {
  var name = document.getElementById('new-cat-name').value.trim();
  if (!name) return;
  clearMsg('new-cat-msg');
  api('POST', '/categories', { name: name }).then(function(d) {
    if (d.ok) {
      document.getElementById('add-cat-form').classList.remove('open');
      document.getElementById('new-cat-name').value = '';
      loadCategories();
    } else {
      setMsg('new-cat-msg', d.error || 'Error', true);
    }
  }).catch(function() { setMsg('new-cat-msg', 'Error', true); });
});

// ── compile ─────────────────────────────────────────────────────────────────

function doCompile(btnId, msgId) {
  var btn = document.getElementById(btnId);
  var orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Publishing…';
  clearMsg(msgId);
  api('POST', '/compile').then(function(d) {
    if (d.ok) { setMsg(msgId, 'Published', false); }
    else { setMsg(msgId, d.error || 'Error', true); }
  }).catch(function() { setMsg(msgId, 'Error', true); })
    .finally(function() { btn.disabled = false; btn.textContent = orig; });
}

document.getElementById('compile-btn').addEventListener('click', function() {
  doCompile('compile-btn', 'compile-msg');
});
document.getElementById('compile-btn-edit').addEventListener('click', function() {
  doCompile('compile-btn-edit', 'compile-msg-edit');
});

// ── category editor ─────────────────────────────────────────────────────────

function openCategory(slug) {
  currentCat = slug;
  clearMsg('cover-msg');
  clearMsg('upload-msg');
  clearMsg('delete-cat-msg');
  clearMsg('compile-msg-edit');
  loadCategoryEditor(slug);
  show('screen-edit');
}

document.getElementById('back-btn').addEventListener('click', function() {
  currentCat = null;
  loadCategories();
  show('screen-list');
});

function loadCategoryEditor(slug) {
  api('GET', '/categories/' + slug + '/photos').then(function(d) {
    var name = slug.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
    document.getElementById('edit-cat-name').textContent = name;
    document.getElementById('edit-cat-count').textContent = d.photos.length + ' photo' + (d.photos.length !== 1 ? 's' : '');
    renderCover(slug);
    renderPhotoGrid(slug, d.photos, d.cover);
  });
}

function renderCover(slug) {
  var wrap = document.getElementById('cover-wrap');
  var ts = '?t=' + Date.now();
  wrap.innerHTML =
    '<img class="cover-img" src="' + BASE + '/cover/' + slug + ts + '" ' +
      'onerror="this.outerHTML=\'<div class=cover-placeholder>No cover set</div>\'" ' +
      'alt="Cover">';
}

function renderPhotoGrid(slug, photos, coverFilename) {
  var grid = document.getElementById('photo-grid');
  grid.innerHTML = '';
  photos.forEach(function(photo) {
    var item = document.createElement('div');
    item.className = 'photo-item' + (photo === coverFilename ? ' is-cover' : '');
    item.innerHTML =
      '<img src="' + BASE + '/photo/' + slug + '/' + photo + '?t=' + Date.now() + '" loading="lazy" alt="">' +
      '<button class="photo-cover" title="Set as cover">' + (photo === coverFilename ? 'Cover' : 'Set cover') + '</button>' +
      '<button class="photo-del" title="Delete">&times;</button>';
    item.querySelector('.photo-cover').addEventListener('click', function() {
      api('POST', '/categories/' + slug + '/cover-from-photo/' + photo).then(function(d) {
        if (d.ok) { loadCategoryEditor(slug); renderCover(slug); }
        else { alert(d.error || 'Error'); }
      });
    });
    item.querySelector('.photo-del').addEventListener('click', function() {
      if (!confirm('Delete this photo?')) return;
      api('DELETE', '/categories/' + slug + '/photos/' + photo).then(function(d) {
        if (d.ok) { loadCategoryEditor(slug); }
        else { alert(d.error || 'Error'); }
      });
    });
    grid.appendChild(item);
  });
}

// ── photo upload ─────────────────────────────────────────────────────────────

document.getElementById('photo-upload-btn').addEventListener('click', function() {
  if (!currentCat) return;
  var files = document.getElementById('photo-files').files;
  if (!files.length) { setMsg('upload-msg', 'Choose files first', true); return; }
  clearMsg('upload-msg');
  var btn = document.getElementById('photo-upload-btn');
  btn.disabled = true;
  btn.textContent = 'Uploading…';
  var fd = new FormData();
  for (var i = 0; i < files.length; i++) { fd.append('files', files[i]); }
  fetch(BASE + '/categories/' + currentCat + '/photos', { method: 'POST', body: fd })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.ok) {
        setMsg('upload-msg', d.count + ' photo' + (d.count !== 1 ? 's' : '') + ' added', false);
        document.getElementById('photo-files').value = '';
        loadCategoryEditor(currentCat);
      } else {
        setMsg('upload-msg', d.error || 'Error', true);
      }
    })
    .catch(function() { setMsg('upload-msg', 'Error', true); })
    .finally(function() { btn.disabled = false; btn.textContent = 'Upload'; });
});

// ── delete category ─────────────────────────────────────────────────────────

document.getElementById('delete-cat-btn').addEventListener('click', function() {
  if (!currentCat) return;
  var name = currentCat.replace(/-/g, ' ');
  if (!confirm('Delete "' + name + '" and all its photos? This cannot be undone.')) return;
  api('DELETE', '/categories/' + currentCat).then(function(d) {
    if (d.ok) {
      currentCat = null;
      loadCategories();
      show('screen-list');
    } else {
      setMsg('delete-cat-msg', d.error || 'Error', true);
    }
  }).catch(function() { setMsg('delete-cat-msg', 'Error', true); });
});

// ── boot ─────────────────────────────────────────────────────────────────────

checkAuth();

})();
</script>
</body>
</html>"""


# ── Routes ─────────────────────────────────────────────────────────────────────
# panel / login / logout / compile come from the framework:
admin.register_core(ADMIN_HTML)


@bp.route('/api/alfie-admin/categories', methods=['GET'])
@_auth_required
def list_categories():
    meta = _load_meta()
    result = []
    for slug, photos in meta.items():
        if slug.startswith('__'):
            continue
        result.append({'slug': slug, 'name': _title_case(slug), 'count': len(photos)})
    return jsonify(result)


@bp.route('/api/alfie-admin/categories', methods=['POST'])
@_auth_required
def create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    slug = _slugify(name)
    if not slug:
        return jsonify({'error': 'Invalid name'}), 400
    meta = _load_meta()
    if slug in meta:
        return jsonify({'error': 'Category already exists'}), 400

    # Create directories
    photo_dir = WORK_DIR / slug
    photo_dir.mkdir(parents=True, exist_ok=True)
    page_dir = ARTIST_DIR / slug
    page_dir.mkdir(exist_ok=True)
    cfg_path = page_dir / 'config.json'
    if not cfg_path.exists():
        cfg_path.write_text(json.dumps({
            'title': f'Alfie Bruce — {_title_case(slug)}',
            'slug': f'artists/{ARTIST_SLUG}/{slug}',
            'description': f'{_title_case(slug)} — photography by Alfie Bruce',
            'categories': []
        }, indent=4))

    meta[slug] = []
    _save_meta(meta)
    # Write empty category page
    (page_dir / 'content.md').write_text(_generate_category_page(slug, []))
    return jsonify({'ok': True, 'slug': slug})


@bp.route('/api/alfie-admin/categories/<slug>', methods=['DELETE'])
@_auth_required
def delete_category(slug):
    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Not found'}), 404

    import shutil
    # Remove photos directory
    photo_dir = WORK_DIR / slug
    if photo_dir.exists():
        shutil.rmtree(photo_dir)
    # Remove cover image
    cover = WORK_DIR / f'{slug}.jpg'
    if cover.exists():
        cover.unlink()
    # Remove page directory
    page_dir = ARTIST_DIR / slug
    if page_dir.exists():
        shutil.rmtree(page_dir)

    del meta[slug]
    _save_meta(meta)
    # Regenerate home page without this category
    home_dir = ARTIST_DIR / 'home'
    home_dir.mkdir(exist_ok=True)
    (home_dir / 'content.md').write_text(_generate_home_page(list(meta.keys())))
    return jsonify({'ok': True})


@bp.route('/api/alfie-admin/categories/<slug>/photos', methods=['GET'])
@_auth_required
def list_photos(slug):
    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Not found'}), 404
    photos = [p['f'] for p in meta[slug]]
    cover = meta.get('__covers', {}).get(slug)
    return jsonify({'photos': photos, 'cover': cover})


@bp.route('/api/alfie-admin/categories/<slug>/photos', methods=['POST'])
@_auth_required
def upload_photos(slug):
    try:
        from PIL import Image
    except ImportError:
        return jsonify({'error': 'PIL not available'}), 500

    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Category not found'}), 404

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files'}), 400

    photo_dir = WORK_DIR / slug
    photo_dir.mkdir(parents=True, exist_ok=True)

    existing = meta[slug]
    # Find next available number
    used_nums = set()
    for p in existing:
        try:
            used_nums.add(int(Path(p['f']).stem))
        except ValueError:
            pass
    next_num = (max(used_nums) + 1) if used_nums else 1

    added = []
    for f in files:
        if not f or not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTS:
            continue
        try:
            img = Image.open(f.stream)
            # Apply EXIF rotation
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            w, h = img.size
            ar = round(w / h, 4) if h else 1.5
            # Save as JPEG
            filename = f'{next_num:03d}.jpg'
            out_path = photo_dir / filename
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(out_path, 'JPEG', quality=88)
            existing.append({'f': filename, 'ar': ar})
            added.append(filename)
            next_num += 1
        except Exception as e:
            return jsonify({'error': f'Failed to process {f.filename}: {e}'}), 500

    meta[slug] = existing
    _save_meta(meta)
    return jsonify({'ok': True, 'count': len(added), 'files': added})


@bp.route('/api/alfie-admin/categories/<slug>/photos/<filename>', methods=['DELETE'])
@_auth_required
def delete_photo(slug, filename):
    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Not found'}), 404

    photos = meta[slug]
    # Remove from list
    new_photos = [p for p in photos if p['f'] != filename]
    if len(new_photos) == len(photos):
        return jsonify({'error': 'Photo not found'}), 404

    # Remove file
    photo_file = WORK_DIR / slug / filename
    if photo_file.exists():
        photo_file.unlink()

    meta[slug] = new_photos
    _save_meta(meta)
    return jsonify({'ok': True})


@bp.route('/api/alfie-admin/categories/<slug>/cover', methods=['POST'])
@_auth_required
def upload_cover(slug):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return jsonify({'error': 'PIL not available'}), 500

    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Category not found'}), 404

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file'}), 400

    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        img = Image.open(f.stream)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
        if img.mode != 'RGB':
            img = img.convert('RGB')
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        img.save(WORK_DIR / f'{slug}.jpg', 'JPEG', quality=90)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'ok': True})


@bp.route('/api/alfie-admin/categories/<slug>/cover-from-photo/<filename>', methods=['POST'])
@_auth_required
def cover_from_photo(slug, filename):
    meta = _load_meta()
    if slug not in meta:
        return jsonify({'error': 'Category not found'}), 404
    src = WORK_DIR / slug / filename
    if not src.exists():
        return jsonify({'error': 'Photo not found'}), 404
    try:
        from PIL import Image, ImageOps
        img = Image.open(src)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
        if img.mode != 'RGB':
            img = img.convert('RGB')
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        img.save(WORK_DIR / f'{slug}.jpg', 'JPEG', quality=90)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    covers = meta.get('__covers', {})
    covers[slug] = filename
    meta['__covers'] = covers
    _save_meta(meta)
    return jsonify({'ok': True})


@bp.route('/api/alfie-admin/photo/<slug>/<filename>')
@_auth_required
def serve_photo(slug, filename):
    photo_path = WORK_DIR / slug / filename
    if not photo_path.exists():
        abort(404)
    return send_file(photo_path)


@bp.route('/api/alfie-admin/cover/<slug>')
@_auth_required
def serve_cover(slug):
    cover_path = WORK_DIR / f'{slug}.jpg'
    if not cover_path.exists():
        abort(404)
    return send_file(cover_path)


@bp.route('/api/alfie-admin/qr.svg')
@_auth_required
def serve_qr():
    import qrcode
    import qrcode.image.svg
    cfg = ARTIST_DIR / 'config.json'
    website = json.loads(cfg.read_text()).get('domain') or 'https://alfiebruce.com'
    data = request.args.get('data') or website
    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, border=2)
    buf = io.BytesIO()
    img.save(buf)
    resp = make_response(buf.getvalue())
    resp.content_type = 'image/svg+xml'
    return resp


@bp.route('/api/alfie-admin/qr.png')
@_auth_required
def serve_qr_png():
    import qrcode
    cfg = ARTIST_DIR / 'config.json'
    website = json.loads(cfg.read_text()).get('domain') or 'https://alfiebruce.com'
    data = request.args.get('data') or website
    img = qrcode.make(data, box_size=24, border=2)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True,
                     download_name='alfie-bruce-qr.png')


@bp.route('/api/alfie-admin/font/<filename>')
def serve_font(filename):
    font_path = ASSETS_DIR / 'fonts' / filename
    if not font_path.exists():
        abort(404)
    return send_file(font_path)


def create_blueprint(artist_slug):
    bp.url_prefix = ''
    return bp
