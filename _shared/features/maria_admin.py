"""
Adele (mariaslaughter) personal admin — /admin on mariaslaughter.online.

Manages a single data-driven "links" page (shows, socials, shop) from
links.json, which is the source of truth. Built on the shared ArtistAdmin
framework: this module only supplies the data model, the render function, and
the HTML — auth, the core routes, and the rebuild transaction come from
artist_admin. Her hand-built home/gallery/music pages are untouched.
"""

import json
import html
from pathlib import Path
from flask import request, jsonify

try:
    from features.artist_admin import ArtistAdmin
except ImportError:
    from artist_admin import ArtistAdmin

ARTIST_SLUG = 'mariaslaughter'
COOKIE = 'maria_admin'
PANEL_URL = '/api/maria-admin/panel'

ARTIST_DIR = Path('artists') / ARTIST_SLUG
LINKS_PATH = ARTIST_DIR / 'links.json'
LINKS_PAGE = 'links'


# ── data ─────────────────────────────────────────────────────────────────────
def _load_links():
    try:
        data = json.loads(LINKS_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_links(links):
    LINKS_PATH.write_text(json.dumps(links, indent=2, ensure_ascii=False), encoding='utf-8')


# ── page generation (source of truth: links.json) ───────────────────────────
def _render():
    """Rewrite links/content.md + config.json from links.json. Returns the list
    of generated page slugs so the framework can mark them read-only."""
    links = _load_links()
    rows = '\n'.join(
        f'      <li><a href="{html.escape(l.get("url", "#"))}" target="_blank" '
        f'rel="noopener">{html.escape(l.get("label", "untitled"))}</a></li>'
        for l in links
    ) or '      <li class="empty">nothing here yet</li>'

    content = (
        "<style>\n"
        "@font-face{font-family:'Cardinal';src:url('../assets/fonts/Cardinal.ttf') format('truetype');}\n"
        "html,body{margin:0;padding:0;min-height:100%;}\n"
        "body{background:#281800;background-image:url('../assets/gifs/ceramic.gif');"
        "background-repeat:repeat;color:#ff0000;font-family:Arial,Helvetica,sans-serif;"
        "padding-bottom:50px;text-align:center;}\n"
        "h1{font-family:'Cardinal',serif;color:#c9a573;font-size:48px;margin:40px 0 30px;}\n"
        "ul{list-style:none;padding:0;max-width:480px;margin:0 auto;}\n"
        "li{margin:14px 0;}\n"
        "a{color:#c9a573;text-decoration:none;font-weight:bold;font-size:20px;}\n"
        "a:hover{color:#fff;text-decoration:underline;}\n"
        ".empty{color:#7a5a3a;font-style:italic;}\n"
        "</style>\n"
        "<html>\n"
        "  <body>\n"
        "    <h1>links</h1>\n"
        "    <ul>\n"
        f"{rows}\n"
        "    </ul>\n"
        "  </body>\n"
        "</html>\n"
    )

    page_dir = ARTIST_DIR / LINKS_PAGE
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / 'content.md').write_text(content, encoding='utf-8')
    (page_dir / 'config.json').write_text(json.dumps({
        'title': 'Links — Adele',
        'slug': f'artists/{ARTIST_SLUG}/{LINKS_PAGE}',
        'description': 'Links, shows and shop for Adele.',
    }, indent=4), encoding='utf-8')
    return [LINKS_PAGE]


admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, render=_render, blueprint_name='maria_admin')


# ── HTML ─────────────────────────────────────────────────────────────────────
ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — Adele</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Arial,Helvetica,sans-serif;background:#281800;color:#c9a573;
  max-width:480px;margin:0 auto;padding:0 16px 80px;min-height:100vh;}
.hd{height:60px;display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid #c9a573;margin-bottom:28px;position:sticky;top:0;background:#281800;z-index:10;}
.hd-brand{font-size:24px;font-weight:bold;color:#ff0000;}
.hd-action{font-size:13px;cursor:pointer;background:none;border:none;color:#c9a573;font-family:inherit;}
h2{font-weight:bold;font-size:20px;margin-bottom:20px;color:#ff0000;}
.field{margin-bottom:16px;}
.field label{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;}
.field input{width:100%;border:1px solid #6b4f2a;background:#1a1000;color:#fff;
  padding:10px 12px;font-family:inherit;font-size:16px;outline:none;}
.field input:focus{border-color:#c9a573;}
.btn{display:inline-block;border:1px solid #c9a573;padding:10px 20px;font-family:inherit;
  font-size:14px;background:#c9a573;color:#281800;cursor:pointer;font-weight:bold;}
.btn:hover{opacity:.85;}
.btn:disabled{opacity:.4;cursor:default;}
.btn-ghost{background:none;color:#c9a573;}
.btn-sm{padding:6px 12px;font-size:12px;}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:12px 0;border-bottom:1px solid #4a3318;}
.row-label{flex:1;font-weight:bold;color:#fff;}
.row-url{font-size:12px;color:#7a5a3a;word-break:break-all;}
.add-row{display:flex;gap:8px;margin-top:18px;}
.add-row input{flex:1;border:1px solid #6b4f2a;background:#1a1000;color:#fff;padding:8px 10px;font-family:inherit;}
.msg{font-size:12px;margin-top:14px;min-height:16px;}
.msg.ok{color:#1aff00;}.msg.err{color:#ff0000;}
.del{background:none;border:none;color:#ff0000;cursor:pointer;font-size:18px;font-family:inherit;}
.compile{margin-top:36px;padding-top:24px;border-top:1px solid #c9a573;}
</style>
</head>
<body>

<div id="screen-login" style="display:none">
  <div class="hd"><span class="hd-brand">adele</span></div>
  <h2>Admin</h2>
  <div class="field"><label>Password</label><input type="password" id="pw" autocomplete="current-password"></div>
  <button class="btn" id="login-btn">Enter</button>
  <div class="msg err" id="login-err"></div>
</div>

<div id="screen-main" style="display:none">
  <div class="hd"><span class="hd-brand">adele</span><button class="hd-action" id="logout-btn">Log out</button></div>
  <h2>Links</h2>
  <ul id="links-list" style="list-style:none"></ul>
  <div class="add-row">
    <input type="text" id="new-label" placeholder="Label">
    <input type="text" id="new-url" placeholder="https://…">
    <button class="btn btn-sm" id="add-btn">Add</button>
  </div>
  <div class="compile">
    <button class="btn" id="compile-btn">Publish changes</button>
    <div class="msg" id="msg"></div>
  </div>
</div>

<script>
const P = '/api/maria-admin';
let links = [];

function show(name){
  ['login','main'].forEach(s => document.getElementById('screen-'+s).style.display = s===name?'':'none');
}
async function api(method, path, body){
  const opts = {method, headers:{}};
  if(body){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body);}
  const r = await fetch(P+path, opts);
  if(r.status===401){show('login');return null;}
  return r;
}
function render(){
  const ul = document.getElementById('links-list');
  ul.innerHTML = '';
  links.forEach((l,i) => {
    const li = document.createElement('li');
    li.className = 'row';
    const left = document.createElement('div');
    left.style.flex='1';
    const lab = document.createElement('div'); lab.className='row-label'; lab.textContent=l.label;
    const url = document.createElement('div'); url.className='row-url'; url.textContent=l.url;
    left.appendChild(lab); left.appendChild(url);
    const del = document.createElement('button'); del.className='del'; del.textContent='×';
    del.onclick = () => removeLink(i);
    li.appendChild(left); li.appendChild(del);
    ul.appendChild(li);
  });
}
async function load(){
  const r = await api('GET','/links');
  if(!r) return;
  links = await r.json();
  render(); show('main');
}
async function addLink(){
  const label = document.getElementById('new-label').value.trim();
  const url = document.getElementById('new-url').value.trim();
  if(!label || !url) return;
  const r = await api('POST','/links',{label,url});
  if(r && r.ok){ links = await r.json();
    document.getElementById('new-label').value=''; document.getElementById('new-url').value='';
    render(); }
}
async function removeLink(i){
  const r = await api('DELETE','/links/'+i);
  if(r && r.ok){ links = await r.json(); render(); }
}
document.getElementById('add-btn').onclick = addLink;
document.getElementById('logout-btn').onclick = async () => { await api('POST','/logout'); show('login'); };
document.getElementById('login-btn').onclick = async () => {
  const r = await fetch(P+'/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:document.getElementById('pw').value})});
  if(r.ok){ document.getElementById('login-err').textContent=''; load(); }
  else document.getElementById('login-err').textContent='Wrong password.';
};
document.getElementById('pw').addEventListener('keydown', e => { if(e.key==='Enter') document.getElementById('login-btn').click(); });
document.getElementById('compile-btn').onclick = async () => {
  const btn = document.getElementById('compile-btn'), msg = document.getElementById('msg');
  btn.disabled=true; btn.textContent='Publishing…'; msg.textContent=''; msg.className='msg';
  const r = await api('POST','/compile');
  btn.disabled=false; btn.textContent='Publish changes';
  if(r && r.ok){ msg.textContent='Published.'; msg.className='msg ok'; }
  else { msg.textContent='Something went wrong.'; msg.className='msg err'; }
};
(async () => { const r = await fetch(P+'/links'); if(r.ok) load(); else show('login'); })();
</script>
</body>
</html>"""


admin.register_core(ADMIN_HTML)


# ── data routes ──────────────────────────────────────────────────────────────
@admin.bp.route(f'{admin.prefix}/links', methods=['GET'])
@admin.auth_required
def get_links():
    return jsonify(_load_links())


@admin.bp.route(f'{admin.prefix}/links', methods=['POST'])
@admin.auth_required
def add_link():
    body = request.get_json(silent=True) or {}
    label = (body.get('label') or '').strip()
    url = (body.get('url') or '').strip()
    if not label or not url:
        return jsonify({'error': 'label and url required'}), 400
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    links = _load_links()
    links.append({'label': label, 'url': url})
    _save_links(links)
    return jsonify(links), 201


@admin.bp.route(f'{admin.prefix}/links/<int:idx>', methods=['DELETE'])
@admin.auth_required
def delete_link(idx):
    links = _load_links()
    if 0 <= idx < len(links):
        links.pop(idx)
        _save_links(links)
    return jsonify(links)


def create_blueprint(artist_slug):
    admin.bp.url_prefix = ''
    return admin.bp
