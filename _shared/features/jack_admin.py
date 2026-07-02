"""
Jack Dennison-Thompson (jackdt) personal admin — /admin on jackdt.com.

Manages the data-driven Writing page from posts.json, which is the source of
truth for his published articles. Built on the shared ArtistAdmin framework:
this module only supplies the data model, the render function, and the HTML —
auth, the core routes, and the rebuild transaction come from artist_admin. His
hand-built home/about/music pages are untouched.
"""

import json
import html
from pathlib import Path
from flask import request, jsonify

try:
    from features.artist_admin import ArtistAdmin
except ImportError:
    from artist_admin import ArtistAdmin

ARTIST_SLUG = 'jackdt'
COOKIE = 'jack_admin'
PANEL_URL = '/api/jack-admin/panel'

ARTIST_DIR = Path('artists') / ARTIST_SLUG
POSTS_PATH = ARTIST_DIR / 'posts.json'
WRITING_PAGE = 'writing'


# ── data ─────────────────────────────────────────────────────────────────────
def _load_posts():
    try:
        data = json.loads(POSTS_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_posts(posts):
    POSTS_PATH.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding='utf-8')


def _clean_post(p):
    """Coerce one incoming post to the stored shape, dropping unknown keys."""
    if not isinstance(p, dict):
        return None
    title = (p.get('title') or '').strip()
    url = (p.get('url') or '').strip()
    if not title or not url:
        return None
    if not url.startswith(('http://', 'https://', 'mailto:')):
        url = 'https://' + url
    return {
        'title': title,
        'meta': (p.get('meta') or '').strip(),
        'excerpt': (p.get('excerpt') or '').strip(),
        'url': url,
    }


# ── page generation (source of truth: posts.json) ────────────────────────────
# The Writing page chrome (fonts, masthead, footer) is static; only the article
# grid is generated. __ENTRIES__ is replaced with the rendered cards. Keep this
# in sync with the hand-built design if the chrome ever changes.
_PAGE_TEMPLATE = """<style>
@font-face {
    font-family: 'Bebas Neue';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/bebas-neue-400.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/barlow-400.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/barlow-700.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: italic;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200-italic.ttf') format('truetype');
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
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Bold.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: italic;
    font-weight: 400;
    font-display: swap;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}

:root {
    --blue: #1a35ff;
    --blue-deep: #0a1ea8;
    --ink: #0b0d1a;
    --bg: #f4f3ee;
    --paper: #fbfaf6;
    --muted: #4a4d5c;
    --display: 'Bebas Neue', 'Barlow', sans-serif;
    --body: 'Barlow', sans-serif;
    --serif: 'Cardo', Georgia, 'Times New Roman', serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
    font-family: var(--body);
    color: var(--ink);
    background: var(--bg);
    line-height: 1.5;
    font-weight: 400;
    overflow-x: hidden;
    opacity: 0;
    animation: pageIn 0.6s ease-out forwards;
}
@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

a { color: inherit; text-decoration: none; }

/* ── Slim masthead (top-left name + right-side vertical nav) ── */
.masthead {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 18px 32px;
    background: rgba(244, 243, 238, 0.82);
    backdrop-filter: saturate(140%) blur(8px);
    -webkit-backdrop-filter: saturate(140%) blur(8px);
    border-bottom: 1px solid rgba(11, 13, 26, 0.08);
}
.brand {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(20px, 2.4vw, 32px);
    letter-spacing: 0.06em;
    line-height: 0.9;
    color: var(--blue);
    text-transform: uppercase;
    white-space: nowrap;
}
.top-nav {
    display: flex;
    flex-direction: column;
    gap: 14px;
    align-items: flex-end;
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink);
}
.top-nav a { position: relative; }
.top-nav a.active { color: var(--blue); }
.top-nav a::after {
    content: '';
    position: absolute;
    right: 0; bottom: -4px;
    width: 0; height: 2px;
    background: var(--blue);
    transition: width 0.25s ease;
}
.top-nav a:hover::after, .top-nav a.active::after { width: 100%; }

/* ── Page head ── */
.wrap {
    max-width: 940px;
    margin: 0 auto;
    padding: clamp(120px, 18vh, 200px) 32px 120px;
}
.eyebrow {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 22px;
}
h1 {
    font-family: var(--display);
    font-weight: 400;
    color: var(--blue);
    line-height: 0.84;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    font-size: clamp(58px, 12vw, 150px);
    margin-bottom: 48px;
    /* blue text with a faint texture overlay clipped to the glyphs */
    background-image:
        linear-gradient(rgba(26, 53, 255, 0.65), rgba(26, 53, 255, 0.65)),
        url('../assets/intake/91aafc78_5.jpeg');
    background-size: cover, 200px auto;
    background-position: center;
    background-repeat: no-repeat, repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Article cards ── */
.grid { display: grid; gap: 0; }
.entry {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 36px 0;
    border-top: 2px solid var(--ink);
    transition: padding-left 0.2s ease;
}
.entry:last-of-type { border-bottom: 2px solid var(--ink); }
.entry:hover { padding-left: 12px; }
.entry .meta {
    font-family: var(--body);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--blue);
}
.entry .title {
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(30px, 5vw, 58px);
    line-height: 0.92;
    letter-spacing: 0.012em;
    text-transform: uppercase;
    color: var(--ink);
}
.entry:hover .title { color: var(--blue); }
.entry .excerpt {
    font-family: var(--body);
    font-weight: 200;
    font-size: clamp(16px, 1.45vw, 19px);
    line-height: 1.7;
    color: #24272f;
    max-width: 64ch;
    margin-top: 6px;
}
.entry .more {
    margin-top: 6px;
    font-family: var(--body);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--blue);
}

.foot {
    text-align: center;
    padding: 60px 32px;
    background: var(--ink);
    color: rgba(255,255,255,0.6);
    font-family: var(--body);
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.foot a { color: var(--blue); }
.foot a:hover { color: #fff; }

/* texture on the remaining blue text — same treatment, clipped to glyphs */
.brand,
.top-nav a.active,
.eyebrow,
.entry .meta,
.entry .more,
.entry:hover .title,
.foot a {
    background-image:
        linear-gradient(rgba(26, 53, 255, 0.65), rgba(26, 53, 255, 0.65)),
        url('../assets/intake/91aafc78_5.jpeg');
    background-size: cover, 200px auto;
    background-position: center;
    background-repeat: no-repeat, repeat;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.foot a:hover { -webkit-text-fill-color: #fff; }

@media (max-width: 640px) {
    .masthead { padding: 14px 18px; }
    .top-nav { gap: 14px; font-size: 10px; letter-spacing: 0.12em; }
    .wrap { padding: 110px 22px 80px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<html>
<header class="masthead">
    <a href="../home/" class="brand">Jack Dennison Thompson</a>
    <nav class="top-nav">
        <a href="../about/">About</a>
        <a href="../writing/" class="active">Writing</a>
        <a href="../music/">Music</a>
    </nav>
</header>

<section class="wrap">
    <div class="eyebrow">Selected Work</div>
    <h1>Writing</h1>

    <div class="grid">
__ENTRIES__
    </div>
</section>

<footer class="foot">
    <a href="mailto:jackdt26@outlook.com">Email Jack &rarr;</a>
</footer>
</html>
"""


def _entry_html(p):
    return (
        '        <a class="entry" href="%s" target="_blank" rel="noopener">\n'
        '            <div class="meta">%s</div>\n'
        '            <div class="title">%s</div>\n'
        '            <p class="excerpt">%s</p>\n'
        '            <div class="more">Read Article &rarr;</div>\n'
        '        </a>'
    ) % (
        html.escape(p.get('url', '#')),
        html.escape(p.get('meta', '')),
        html.escape(p.get('title', 'Untitled')),
        html.escape(p.get('excerpt', '')),
    )


def _render():
    """Rewrite writing/content.md from posts.json. Returns the generated page
    slugs so the framework can mark them read-only to the editor."""
    posts = _load_posts()
    entries = '\n\n'.join(_entry_html(p) for p in posts) \
        or '        <p class="excerpt">No articles yet.</p>'
    content = _PAGE_TEMPLATE.replace('__ENTRIES__', entries)

    page_dir = ARTIST_DIR / WRITING_PAGE
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / 'content.md').write_text(content, encoding='utf-8')
    return [WRITING_PAGE]


admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, render=_render, blueprint_name='jack_admin')


# ── HTML ─────────────────────────────────────────────────────────────────────
ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — Jack Dennison-Thompson</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--blue:#1a35ff;--ink:#0b0d1a;--bg:#f4f3ee;--paper:#fbfaf6;--muted:#4a4d5c;}
body{font-family:'Barlow',Arial,Helvetica,sans-serif;background:var(--bg);color:var(--ink);
  max-width:760px;margin:0 auto;padding:0 16px 100px;min-height:100vh;}
.hd{height:64px;display:flex;align-items:center;justify-content:space-between;
  border-bottom:2px solid var(--ink);margin-bottom:28px;position:sticky;top:0;background:var(--bg);z-index:10;}
.hd-brand{font-size:20px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--blue);}
.hd-action{font-size:12px;cursor:pointer;background:none;border:none;color:var(--muted);font-family:inherit;
  text-transform:uppercase;letter-spacing:.12em;}
h2{font-weight:800;font-size:22px;text-transform:uppercase;letter-spacing:.02em;margin-bottom:18px;}
.field{margin-bottom:14px;}
.field label{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;color:var(--muted);}
.field input,.field textarea{width:100%;border:1px solid #c7c5bd;background:#fff;color:var(--ink);
  padding:10px 12px;font-family:inherit;font-size:15px;outline:none;}
.field textarea{min-height:72px;resize:vertical;}
.field input:focus,.field textarea:focus{border-color:var(--blue);}
.btn{display:inline-block;border:2px solid var(--blue);padding:11px 22px;font-family:inherit;
  font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  background:var(--blue);color:#fff;cursor:pointer;}
.btn:hover{background:var(--blue-deep,#0a1ea8);}
.btn:disabled{opacity:.4;cursor:default;}
.btn-ghost{background:none;color:var(--blue);}
.btn-sm{padding:7px 14px;font-size:12px;}
.row{display:flex;align-items:center;gap:12px;padding:14px 12px;border:1px solid #d8d6ce;
  margin-bottom:8px;background:var(--paper);}
.row.drag-over{border-color:var(--blue);border-style:dashed;}
.row.dragging{opacity:.4;}
.grip{cursor:grab;color:var(--muted);font-size:18px;line-height:1;user-select:none;}
.row-main{flex:1;min-width:0;}
.row-title{font-weight:700;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.row-meta{font-size:12px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin-top:3px;}
.row-actions{display:flex;gap:6px;flex:none;}
.icon-btn{background:none;border:1px solid #c7c5bd;cursor:pointer;font-size:13px;font-family:inherit;
  padding:5px 9px;color:var(--ink);}
.icon-btn:hover{border-color:var(--blue);color:var(--blue);}
.icon-btn.del:hover{border-color:#d11;color:#d11;}
.toolbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.editor{border:2px solid var(--ink);padding:20px;margin-bottom:24px;background:#fff;}
.editor h3{font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:16px;}
.editor-actions{display:flex;gap:10px;margin-top:6px;}
.publish{margin-top:36px;padding-top:24px;border-top:2px solid var(--ink);}
.hint{font-size:12px;color:var(--muted);margin-top:4px;}
.msg{font-size:13px;margin-top:14px;min-height:18px;letter-spacing:.04em;}
.msg.ok{color:#0a8a2a;}.msg.err{color:#d11;}
.empty{color:var(--muted);font-style:italic;padding:24px 0;}
</style>
</head>
<body>

<div id="screen-login" style="display:none">
  <div class="hd"><span class="hd-brand">Jack Dennison-Thompson</span></div>
  <h2>Admin</h2>
  <div class="field"><label>Password</label><input type="password" id="pw" autocomplete="current-password"></div>
  <button class="btn" id="login-btn">Enter</button>
  <div class="msg err" id="login-err"></div>
</div>

<div id="screen-main" style="display:none">
  <div class="hd"><span class="hd-brand">Jack Dennison-Thompson</span><button class="hd-action" id="logout-btn">Log out</button></div>

  <div class="toolbar">
    <h2 style="margin:0">Posts</h2>
    <button class="btn btn-sm" id="new-btn">+ New post</button>
  </div>

  <div id="editor" class="editor" style="display:none">
    <h3 id="editor-title">New post</h3>
    <div class="field"><label>Title</label><input type="text" id="f-title" placeholder="Article headline"></div>
    <div class="field"><label>Publication &amp; date</label><input type="text" id="f-meta" placeholder="e.g. Clash Music · Review · Mar 2026">
      <div class="hint">Shown in small caps above the title. Use “ · ” to separate parts.</div></div>
    <div class="field"><label>Excerpt</label><textarea id="f-excerpt" placeholder="One or two sentences describing the piece."></textarea></div>
    <div class="field"><label>Link</label><input type="text" id="f-url" placeholder="https://…"></div>
    <div class="editor-actions">
      <button class="btn btn-sm" id="save-post-btn">Save post</button>
      <button class="btn btn-sm btn-ghost" id="cancel-btn">Cancel</button>
    </div>
  </div>

  <div id="list"></div>

  <div class="publish">
    <button class="btn" id="publish-btn">Publish to site</button>
    <div class="hint">Saves are kept as you edit. “Publish” rebuilds the live Writing page.</div>
    <div class="msg" id="msg"></div>
  </div>
</div>

<script>
const P = '/api/jack-admin';
let posts = [];
let editIdx = -1;            // -1 = adding new, >=0 = editing that index
let dragIdx = -1;

function show(name){
  ['login','main'].forEach(s => document.getElementById('screen-'+s).style.display = s===name?'':'none');
}
async function api(method, path, body){
  const opts = {method, headers:{}};
  if(body!==undefined){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body);}
  const r = await fetch(P+path, opts);
  if(r.status===401){show('login');return null;}
  return r;
}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}

function renderList(){
  const box = document.getElementById('list');
  box.innerHTML = '';
  if(!posts.length){ box.innerHTML = '<div class="empty">No posts yet. Add your first one.</div>'; return; }
  posts.forEach((p,i) => {
    const row = document.createElement('div');
    row.className = 'row'; row.draggable = true; row.dataset.i = i;
    row.innerHTML =
      '<span class="grip" title="Drag to reorder">⠿</span>'+
      '<div class="row-main"><div class="row-title">'+esc(p.title)+'</div>'+
      '<div class="row-meta">'+esc(p.meta||'—')+'</div></div>'+
      '<div class="row-actions">'+
        '<button class="icon-btn" data-act="edit" data-i="'+i+'">Edit</button>'+
        '<button class="icon-btn del" data-act="del" data-i="'+i+'">Delete</button>'+
      '</div>';
    box.appendChild(row);
  });
}

// drag-and-drop reordering
document.getElementById('list').addEventListener('dragstart', e => {
  const row = e.target.closest('.row'); if(!row) return;
  dragIdx = +row.dataset.i; row.classList.add('dragging');
});
document.getElementById('list').addEventListener('dragend', e => {
  const row = e.target.closest('.row'); if(row) row.classList.remove('dragging');
  document.querySelectorAll('.row.drag-over').forEach(r=>r.classList.remove('drag-over'));
});
document.getElementById('list').addEventListener('dragover', e => {
  e.preventDefault();
  const row = e.target.closest('.row'); if(!row) return;
  document.querySelectorAll('.row.drag-over').forEach(r=>r.classList.remove('drag-over'));
  row.classList.add('drag-over');
});
document.getElementById('list').addEventListener('drop', async e => {
  e.preventDefault();
  const row = e.target.closest('.row'); if(!row || dragIdx<0) return;
  const to = +row.dataset.i;
  if(to!==dragIdx){
    const [moved] = posts.splice(dragIdx,1);
    posts.splice(to,0,moved);
    renderList(); await persist();
  }
  dragIdx = -1;
});

// list button clicks (edit / delete)
document.getElementById('list').addEventListener('click', async e => {
  const btn = e.target.closest('button[data-act]'); if(!btn) return;
  const i = +btn.dataset.i;
  if(btn.dataset.act==='edit') openEditor(i);
  else if(btn.dataset.act==='del'){
    if(confirm('Delete “'+posts[i].title+'”?')){ posts.splice(i,1); renderList(); await persist(); }
  }
});

function openEditor(i){
  editIdx = i;
  const p = i>=0 ? posts[i] : {title:'',meta:'',excerpt:'',url:''};
  document.getElementById('editor-title').textContent = i>=0 ? 'Edit post' : 'New post';
  document.getElementById('f-title').value = p.title||'';
  document.getElementById('f-meta').value = p.meta||'';
  document.getElementById('f-excerpt').value = p.excerpt||'';
  document.getElementById('f-url').value = p.url||'';
  document.getElementById('editor').style.display = '';
  document.getElementById('f-title').focus();
}
function closeEditor(){ document.getElementById('editor').style.display='none'; editIdx=-1; }

document.getElementById('new-btn').onclick = () => openEditor(-1);
document.getElementById('cancel-btn').onclick = closeEditor;
document.getElementById('save-post-btn').onclick = async () => {
  const p = {
    title: document.getElementById('f-title').value.trim(),
    meta: document.getElementById('f-meta').value.trim(),
    excerpt: document.getElementById('f-excerpt').value.trim(),
    url: document.getElementById('f-url').value.trim(),
  };
  if(!p.title || !p.url){ alert('Title and link are required.'); return; }
  if(editIdx>=0) posts[editIdx] = p; else posts.push(p);
  closeEditor(); renderList(); await persist();
};

async function persist(){
  const r = await api('PUT','/posts', posts);
  if(r && r.ok) posts = await r.json();
}

async function load(){
  const r = await api('GET','/posts');
  if(!r) return;
  posts = await r.json();
  renderList(); show('main');
}

document.getElementById('logout-btn').onclick = async () => { await api('POST','/logout'); show('login'); };
document.getElementById('login-btn').onclick = async () => {
  const r = await fetch(P+'/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:document.getElementById('pw').value})});
  if(r.ok){ document.getElementById('login-err').textContent=''; load(); }
  else document.getElementById('login-err').textContent='Wrong password.';
};
document.getElementById('pw').addEventListener('keydown', e => { if(e.key==='Enter') document.getElementById('login-btn').click(); });
document.getElementById('publish-btn').onclick = async () => {
  const btn = document.getElementById('publish-btn'), msg = document.getElementById('msg');
  btn.disabled=true; btn.textContent='Publishing…'; msg.textContent=''; msg.className='msg';
  const r = await api('POST','/compile');
  btn.disabled=false; btn.textContent='Publish to site';
  if(r && r.ok){ msg.textContent='Published. Your Writing page is live.'; msg.className='msg ok'; }
  else { msg.textContent='Something went wrong publishing.'; msg.className='msg err'; }
};
(async () => { const r = await fetch(P+'/posts'); if(r.ok) load(); else show('login'); })();
</script>
</body>
</html>"""


admin.register_core(ADMIN_HTML)


# ── data routes ──────────────────────────────────────────────────────────────
@admin.bp.route(f'{admin.prefix}/posts', methods=['GET'])
@admin.auth_required
def get_posts():
    return jsonify(_load_posts())


@admin.bp.route(f'{admin.prefix}/posts', methods=['PUT'])
@admin.auth_required
def put_posts():
    body = request.get_json(silent=True)
    if not isinstance(body, list):
        return jsonify({'error': 'expected a list of posts'}), 400
    posts = [c for c in (_clean_post(p) for p in body) if c]
    _save_posts(posts)
    return jsonify(posts)


def create_blueprint(artist_slug):
    admin.bp.url_prefix = ''
    return admin.bp
