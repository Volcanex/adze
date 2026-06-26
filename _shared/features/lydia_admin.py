"""
Lydia Lott personal admin — /admin on lydialott.co.uk.

Manages the works grid from assets/works.json (the source of truth that
home/ and works/ both fetch at runtime via assets/works-grid.js). This module
only supplies the data model, image handling, and the HTML; auth, the core
routes, and the rebuild transaction come from the shared ArtistAdmin framework.

There is no render() — the grid reads works.json directly in the browser, so no
content.md is generated from it. rebuild() just recompiles, which copies the
updated works.json + images + thumbs into output/ (what nginx serves).

Each uploaded image is stored full-size under assets/images/ and gets a
width-capped (800px) webp thumbnail under assets/images/thumbs/, because the
grid derives the tile src from the work's image by swapping images/ ->
images/thumbs/ and the extension -> .webp.
"""

import json
import re
import datetime
from pathlib import Path
from PIL import Image
from werkzeug.utils import secure_filename
from flask import request, jsonify, abort, send_from_directory

try:
    from features.artist_admin import ArtistAdmin
except ImportError:
    from artist_admin import ArtistAdmin

ARTIST_SLUG = 'lydialott'
COOKIE = 'lydia_admin'
PANEL_URL = '/api/lydia-admin/panel'

# Self-description picked up by the handover page (admin_api._dashboard_info),
# so the "Your dashboard" section explains this dash without per-artist config.
DASHBOARD_INFO = {
    'name': 'Your works dashboard',
    'blurb': 'Manage the works on your site — add new pieces, edit details, and '
             'publish changes live, all from your phone or laptop.',
    'can': [
        'Add, edit and remove works',
        'Upload images (thumbnails are made for you automatically)',
        'Set medium, dimensions, year and a short description',
        'Choose which works appear on your home page',
        'Publish your changes to the live site',
    ],
}

ARTIST_DIR = Path('artists') / ARTIST_SLUG
ASSETS_PATH = ARTIST_DIR / 'assets'
WORKS_PATH = ASSETS_PATH / 'works.json'
IMAGES_DIR = ASSETS_PATH / 'images'
THUMBS_DIR = IMAGES_DIR / 'thumbs'

ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
THUMB_MAX_W = 800

# Mirrors the taxonomy in assets/works-grid.js (minus 'all' and the 'about'
# nav link). 'selected' is the flag that surfaces a work on the home landing.
TAGS = [
    {'id': 'selected',    'label': 'Selected (home page)'},
    {'id': 'paintings',   'label': 'Paintings'},
    {'id': 'textiles',    'label': 'Textiles'},
    {'id': 'sculpture',   'label': 'Sculpture'},
    {'id': 'drawings',    'label': 'Drawings'},
    {'id': 'exhibitions', 'label': 'Exhibitions'},
    {'id': 'workshops',   'label': 'Workshops'},
]
TAG_IDS = {t['id'] for t in TAGS}


admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, blueprint_name='lydia_admin')
bp = admin.bp
_auth_required = admin.auth_required


# ── data ─────────────────────────────────────────────────────────────────────
def _load():
    try:
        data = json.loads(WORKS_PATH.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault('works', [])
    return data


def _save(data):
    WORKS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _slugify(text):
    s = re.sub(r'[^a-z0-9]+', '-', (text or '').lower())
    return s.strip('-') or 'work'


def _unique_id(base, taken):
    slug, n = base, 2
    while slug in taken:
        slug = f'{base}-{n}'
        n += 1
    return slug


def _clean_tags(raw):
    if not isinstance(raw, list):
        return []
    return [t for t in TAG_IDS if t in raw]  # canonical order, only known tags


# ── images ───────────────────────────────────────────────────────────────────
def _thumb_for(image_rel):
    """images/foo.png -> images/thumbs/foo.webp (matches works-grid.js)."""
    stem = re.sub(r'\.[^.]+$', '', image_rel)
    return re.sub(r'^images/', 'images/thumbs/', stem) + '.webp'


def _make_thumb(full_path, thumb_path):
    im = Image.open(full_path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert('RGB')
    if im.width > THUMB_MAX_W:
        h = round(im.height * THUMB_MAX_W / im.width)
        im = im.resize((THUMB_MAX_W, h), Image.LANCZOS)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(thumb_path, 'WEBP', quality=82, method=6)


def _delete_image(image_rel):
    """Remove the full image + its derived thumb. image_rel is 'images/...'."""
    if not image_rel:
        return
    for p in (ASSETS_PATH / image_rel, ASSETS_PATH / _thumb_for(image_rel)):
        try:
            if p.is_file():
                p.unlink()
        except OSError:
            pass


# ── routes ───────────────────────────────────────────────────────────────────
@bp.route('/api/lydia-admin/works')
@_auth_required
def get_works():
    return jsonify(_load()['works'])


@bp.route('/api/lydia-admin/tags')
@_auth_required
def get_tags():
    return jsonify(TAGS)


@bp.route('/api/lydia-admin/works', methods=['POST'])
@_auth_required
def create_work():
    data = _load()
    body = request.get_json(silent=True) or {}
    title = (body.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Title required'}), 400
    taken = {w.get('id') for w in data['works']}
    wid = _unique_id(_slugify(title), taken)
    year = body.get('year')
    date = (body.get('date') or '').strip()
    if not date:
        date = f'{year}-06-01' if year else datetime.date.today().isoformat()
    work = {
        'id': wid,
        'title': title,
        'dimensions': (body.get('dimensions') or '').strip(),
        'medium': (body.get('medium') or '').strip(),
        'year': year,
        'date': date,
        'image': None,
        'tags': _clean_tags(body.get('tags')),
        'description': (body.get('description') or '').strip(),
    }
    data['works'].append(work)
    _save(data)
    return jsonify(work), 201


@bp.route('/api/lydia-admin/works/<wid>', methods=['PUT'])
@_auth_required
def update_work(wid):
    data = _load()
    body = request.get_json(silent=True) or {}
    for work in data['works']:
        if work.get('id') == wid:
            for key in ('title', 'dimensions', 'medium', 'description'):
                if key in body:
                    work[key] = (body[key] or '').strip()
            if 'year' in body:
                work['year'] = body['year']
            if 'date' in body:
                work['date'] = (body['date'] or '').strip()
            if 'tags' in body:
                work['tags'] = _clean_tags(body['tags'])
            _save(data)
            return jsonify(work)
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/lydia-admin/works/<wid>', methods=['DELETE'])
@_auth_required
def delete_work(wid):
    data = _load()
    work = next((w for w in data['works'] if w.get('id') == wid), None)
    if not work:
        return jsonify({'error': 'Not found'}), 404
    _delete_image(work.get('image'))
    data['works'] = [w for w in data['works'] if w.get('id') != wid]
    _save(data)
    return jsonify({'ok': True})


@bp.route('/api/lydia-admin/works/<wid>/image', methods=['POST'])
@_auth_required
def upload_image(wid):
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    ext = Path(f.filename or '').suffix.lower()
    if ext not in ALLOWED_EXTS:
        return jsonify({'error': 'File type not allowed'}), 400
    data = _load()
    work = next((w for w in data['works'] if w.get('id') == wid), None)
    if not work:
        return jsonify({'error': 'Not found'}), 404

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    # Filename based on the work id; keep unique against existing files.
    base = secure_filename(wid) or 'work'
    name = f'{base}{ext}'
    n = 2
    while (IMAGES_DIR / name).exists():
        name = f'{base}-{n}{ext}'
        n += 1
    full_path = IMAGES_DIR / name
    f.save(full_path)
    try:
        _make_thumb(full_path, ASSETS_PATH / _thumb_for(f'images/{name}'))
    except Exception as e:
        full_path.unlink(missing_ok=True)
        return jsonify({'error': f'Could not process image: {e}'}), 500

    old = work.get('image')
    if old and old != f'images/{name}':
        _delete_image(old)
    work['image'] = f'images/{name}'
    _save(data)
    return jsonify(work)


@bp.route('/api/lydia-admin/asset/<path:filename>')
@_auth_required
def serve_asset(filename):
    """Serve source assets (live, pre-compile) so the dashboard can preview a
    just-uploaded image before Publish."""
    target = (ASSETS_PATH / filename).resolve()
    if ASSETS_PATH.resolve() not in target.parents or not target.is_file():
        abort(404)
    return send_from_directory(ASSETS_PATH, filename)


ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — Lydia Lott</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #fafafa; color: #111;
  max-width: 720px; margin: 0 auto; padding: 0 18px 80px; min-height: 100vh;
}
.hd {
  height: 56px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #000; margin-bottom: 28px;
  position: sticky; top: 0; background: #fafafa; z-index: 10;
}
.hd-brand { font-size: 22px; letter-spacing: 0.01em; }
.hd-action { font-size: 13px; cursor: pointer; background: none; border: none; font-family: inherit; padding: 0; color: #444; }
.hd-action:hover { color: #000; }

#screen-login { padding-top: 80px; max-width: 320px; }
#screen-login h2 { font-weight: 500; font-size: 20px; margin-bottom: 20px; }

.field { margin-bottom: 16px; }
.field label { display: block; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: #555; margin-bottom: 6px; }
.field input, .field select, .field textarea {
  width: 100%; border: 1px solid #ccc; padding: 10px 12px;
  font-family: inherit; font-size: 16px; background: #fff; outline: none; border-radius: 4px; -webkit-appearance: none;
}
.field textarea { min-height: 80px; resize: vertical; }
.field input:focus, .field textarea:focus, .field select:focus { border-color: #000; }
.form-row { display: flex; gap: 12px; } .form-row .field { flex: 1; }

.btn {
  display: inline-block; border: 1px solid #000; padding: 11px 22px;
  font-family: inherit; font-size: 14px; background: #000; color: #fff;
  cursor: pointer; border-radius: 4px; -webkit-appearance: none; transition: opacity .15s;
}
.btn:hover { opacity: 0.82; } .btn:disabled { opacity: 0.4; cursor: default; }
.btn-ghost { background: #fff; color: #000; } .btn-ghost:hover { background: #f0f0f0; opacity: 1; }
.btn-danger { background: #fff; color: #b3261e; border-color: #e2bbb7; }
.btn-danger:hover { background: #b3261e; color: #fff; opacity: 1; }
.btn-sm { padding: 7px 14px; font-size: 12px; }
.btn-row { display: flex; gap: 10px; align-items: center; margin-top: 24px; flex-wrap: wrap; }
.btn-row .spacer { flex: 1; }
.status-msg { font-size: 12px; } .status-msg.ok { color: #2a7d33; } .status-msg.err { color: #b3261e; }

/* list */
.list-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.list-head h2 { font-size: 16px; font-weight: 500; }
.works-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }
.work-card { cursor: pointer; border: 1px solid #e3e3e3; border-radius: 6px; overflow: hidden; background: #fff; transition: border-color .15s; }
.work-card:hover { border-color: #000; }
.work-thumb { width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block; background: #f0f0f0; }
.work-thumb.empty { display: flex; align-items: center; justify-content: center; font-size: 12px; color: #999; }
.work-body { padding: 8px 10px 10px; }
.work-title { font-size: 13px; line-height: 1.3; }
.work-tags { font-size: 10px; color: #888; margin-top: 4px; text-transform: capitalize; }
.work-sel { display: inline-block; font-size: 9px; background: #000; color: #fff; padding: 1px 5px; border-radius: 3px; margin-right: 4px; vertical-align: middle; text-transform: none; }

/* edit */
.back-btn { display: flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; background: none; border: none; font-family: inherit; padding: 0; margin-bottom: 22px; color: #000; }
.back-btn:hover { text-decoration: underline; }
.edit-title { font-size: 22px; font-weight: 500; margin-bottom: 24px; }
.tag-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-chip { display: inline-flex; align-items: center; gap: 6px; border: 1px solid #ccc; border-radius: 20px; padding: 6px 12px; font-size: 13px; cursor: pointer; user-select: none; }
.tag-chip input { margin: 0; }
.tag-chip.on { border-color: #000; background: #000; color: #fff; }
.img-section { margin: 24px 0; padding-top: 22px; border-top: 1px solid #eee; }
.img-section h3 { font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: #555; margin-bottom: 14px; }
.img-current { width: 100%; max-width: 320px; aspect-ratio: 4/3; object-fit: cover; display: block; border: 1px solid #eee; margin-bottom: 14px; background: #f8f8f8; }
.img-placeholder { width: 100%; max-width: 320px; aspect-ratio: 4/3; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #999; margin-bottom: 14px; }
.field input[type=file] { padding: 8px 12px; font-size: 14px; }

.publish-block { margin-top: 40px; padding-top: 22px; border-top: 1px solid #000; }
.publish-block p { font-size: 13px; color: #555; margin-bottom: 14px; line-height: 1.5; }
</style>
</head>
<body>

<!-- LOGIN -->
<div id="screen-login" style="display:none">
  <div class="hd"><span class="hd-brand">Lydia Lott</span></div>
  <h2>Admin</h2>
  <div class="field"><label>Password</label><input type="password" id="pw-input" autocomplete="current-password"></div>
  <button class="btn" id="login-btn">Enter</button>
  <div id="login-err" style="margin-top:12px;font-size:13px;color:#b3261e;display:none">Wrong password.</div>
</div>

<!-- LIST -->
<div id="screen-list" style="display:none">
  <div class="hd">
    <span class="hd-brand">Lydia Lott</span>
    <button class="hd-action" id="logout-btn">Log out</button>
  </div>
  <div class="list-head">
    <h2>Works</h2>
    <button class="btn btn-ghost btn-sm" id="add-work-btn">+ Add work</button>
  </div>
  <div class="works-grid" id="works-grid"></div>
  <div class="publish-block">
    <p>Changes are saved as you go. Hit Publish to push them live to your site.</p>
    <button class="btn" id="publish-btn">Publish to site</button>
    <span class="status-msg" id="publish-msg" style="margin-left:10px;display:none"></span>
  </div>
</div>

<!-- EDIT -->
<div id="screen-edit" style="display:none">
  <div class="hd">
    <span class="hd-brand">Lydia Lott</span>
    <button class="hd-action" id="logout-btn-edit">Log out</button>
  </div>
  <button class="back-btn" id="back-btn">&#8592; Back to works</button>
  <div class="edit-title" id="edit-title">New work</div>

  <div class="form-row">
    <div class="field"><label>Title</label><input type="text" id="ef-title"></div>
    <div class="field"><label>Year</label><input type="number" id="ef-year"></div>
  </div>
  <div class="form-row">
    <div class="field"><label>Medium</label><input type="text" id="ef-medium" placeholder="Acrylic on paper"></div>
    <div class="field"><label>Dimensions</label><input type="text" id="ef-dimensions" placeholder="1000 x 650mm"></div>
  </div>
  <div class="field">
    <label>Date <span style="text-transform:none;letter-spacing:0;color:#999">(controls ordering — newest first)</span></label>
    <input type="date" id="ef-date">
  </div>
  <div class="field"><label>Description (optional)</label><textarea id="ef-description"></textarea></div>
  <div class="field">
    <label>Categories</label>
    <div class="tag-grid" id="ef-tags"></div>
  </div>

  <div class="img-section">
    <h3>Image</h3>
    <div id="ef-img-wrap"></div>
    <div class="field"><label>Upload / replace image</label><input type="file" id="ef-img-file" accept="image/*"></div>
    <button class="btn btn-ghost btn-sm" id="ef-upload-btn">Upload image</button>
    <span class="status-msg" id="ef-upload-msg" style="margin-left:8px"></span>
  </div>

  <div class="btn-row">
    <button class="btn" id="save-btn">Save</button>
    <span class="status-msg" id="save-msg"></span>
    <span class="spacer"></span>
    <button class="btn btn-danger" id="delete-btn">Delete</button>
  </div>
</div>

<script>
const API = '/api/lydia-admin';
let works = [];
let tags = [];
let editId = null;       // null = creating a new (unsaved) work
let dirtyNew = false;

function $(id){ return document.getElementById(id); }
async function api(method, path, body){
  const opts = { method, headers: {} };
  if (body){ opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  const r = await fetch(API + path, opts);
  if (r.status === 401){ show('login'); return null; }
  return r;
}
const SCREENS = ['login','list','edit'];
function show(name){ SCREENS.forEach(s => $('screen-'+s).style.display = s===name ? '' : 'none'); }

function thumbFor(image){
  if (!image) return null;
  return image.replace(/^images\//,'images/thumbs/').replace(/\.[^.]+$/,'.webp');
}

// ── login ──
$('login-btn').addEventListener('click', async () => {
  const r = await fetch(API + '/login', { method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ token: $('pw-input').value }) });
  if (r.ok){ $('login-err').style.display='none'; loadList(); }
  else $('login-err').style.display = '';
});
$('pw-input').addEventListener('keydown', e => { if (e.key==='Enter') $('login-btn').click(); });
function doLogout(){ api('POST','/logout'); show('login'); }
$('logout-btn').addEventListener('click', doLogout);
$('logout-btn-edit').addEventListener('click', doLogout);

// ── list ──
async function loadList(){
  const [wr, tr] = await Promise.all([ fetch(API+'/works'), fetch(API+'/tags') ]);
  if (wr.status === 401){ show('login'); return; }
  works = await wr.json();
  tags = await tr.json();
  works.sort((a,b) => (b.date||'').localeCompare(a.date||''));
  renderGrid();
  show('list');
}
function renderGrid(){
  const g = $('works-grid'); g.innerHTML = '';
  works.forEach(w => {
    const card = document.createElement('div'); card.className='work-card';
    const t = thumbFor(w.image);
    const sel = (w.tags||[]).includes('selected') ? '<span class="work-sel">selected</span>' : '';
    const cats = (w.tags||[]).filter(x=>x!=='selected').join(', ');
    card.innerHTML = (t
        ? `<img class="work-thumb" src="${API}/asset/${t}" alt="" loading="lazy">`
        : `<div class="work-thumb empty">no image</div>`)
      + `<div class="work-body"><div class="work-title">${escapeHtml(w.title||'Untitled')}</div>`
      + `<div class="work-tags">${sel}${escapeHtml(cats)}</div></div>`;
    card.addEventListener('click', () => openEdit(w.id));
    g.appendChild(card);
  });
}
function escapeHtml(s){ return (s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

// ── tag chips ──
function renderTagChips(active){
  const wrap = $('ef-tags'); wrap.innerHTML='';
  tags.forEach(t => {
    const on = active.includes(t.id);
    const label = document.createElement('label');
    label.className = 'tag-chip' + (on ? ' on' : '');
    label.innerHTML = `<input type="checkbox" value="${t.id}" ${on?'checked':''}> ${escapeHtml(t.label)}`;
    label.querySelector('input').addEventListener('change', e => label.classList.toggle('on', e.target.checked));
    wrap.appendChild(label);
  });
}
function selectedTags(){ return Array.from($('ef-tags').querySelectorAll('input:checked')).map(i=>i.value); }

// ── edit / add ──
$('add-work-btn').addEventListener('click', () => openEdit(null));
function openEdit(id){
  editId = id; dirtyNew = (id === null);
  const w = id ? works.find(x=>x.id===id) : { title:'', year:'', medium:'', dimensions:'', date:'', description:'', tags:[], image:null };
  if (!w) return;
  $('edit-title').textContent = id ? (w.title||'Untitled') : 'New work';
  $('ef-title').value = w.title || '';
  $('ef-year').value = w.year || '';
  $('ef-medium').value = w.medium || '';
  $('ef-dimensions').value = w.dimensions || '';
  $('ef-date').value = (w.date || '').slice(0,10);
  $('ef-description').value = w.description || '';
  renderTagChips(w.tags || []);
  renderEditImage(w.image);
  $('ef-img-file').value=''; $('ef-upload-msg').textContent=''; $('save-msg').textContent='';
  $('delete-btn').style.display = id ? '' : 'none';
  show('edit');
}
function renderEditImage(image){
  const t = thumbFor(image);
  $('ef-img-wrap').innerHTML = t
    ? `<img class="img-current" src="${API}/asset/${t}" alt="">`
    : `<div class="img-placeholder">No image yet</div>`;
}
$('back-btn').addEventListener('click', () => loadList());

function collectBody(){
  return {
    title: $('ef-title').value.trim(),
    year: parseInt($('ef-year').value) || null,
    medium: $('ef-medium').value.trim(),
    dimensions: $('ef-dimensions').value.trim(),
    date: $('ef-date').value,
    description: $('ef-description').value.trim(),
    tags: selectedTags(),
  };
}
// Ensure a record exists (creating on first need) so image upload has an id.
async function ensureSaved(){
  if (editId) {
    const r = await api('PUT', `/works/${editId}`, collectBody());
    if (!r || !r.ok) return null;
    return await r.json();
  }
  const body = collectBody();
  if (!body.title){ return null; }
  const r = await api('POST', '/works', body);
  if (!r || !r.ok) return null;
  const w = await r.json();
  editId = w.id; dirtyNew = false;
  $('delete-btn').style.display = '';
  return w;
}

$('save-btn').addEventListener('click', async () => {
  const msg = $('save-msg');
  if (!$('ef-title').value.trim()){ msg.textContent='Title required'; msg.className='status-msg err'; return; }
  msg.textContent='Saving…'; msg.className='status-msg';
  const w = await ensureSaved();
  if (w){ msg.textContent='Saved'; msg.className='status-msg ok'; $('edit-title').textContent = w.title || 'Untitled';
    setTimeout(()=>{ loadList(); }, 500); }
  else { msg.textContent='Error saving'; msg.className='status-msg err'; }
});

$('delete-btn').addEventListener('click', async () => {
  if (!editId) return;
  if (!confirm('Delete this work? This removes it and its image for good.')) return;
  const r = await api('DELETE', `/works/${editId}`);
  if (r && r.ok){ loadList(); }
});

$('ef-upload-btn').addEventListener('click', async () => {
  const msg = $('ef-upload-msg');
  const file = $('ef-img-file').files[0];
  if (!file){ msg.textContent='Choose a file first'; msg.className='status-msg err'; return; }
  if (!$('ef-title').value.trim()){ msg.textContent='Add a title first'; msg.className='status-msg err'; return; }
  msg.textContent='Saving…'; msg.className='status-msg';
  const saved = await ensureSaved();
  if (!saved){ msg.textContent='Could not save first'; msg.className='status-msg err'; return; }
  msg.textContent='Uploading…';
  const fd = new FormData(); fd.append('file', file);
  const r = await fetch(`${API}/works/${editId}/image`, { method:'POST', body: fd });
  if (r.status===401){ show('login'); return; }
  if (r.ok){ const w = await r.json(); renderEditImage(w.image); $('ef-img-file').value='';
    msg.textContent='Uploaded'; msg.className='status-msg ok'; }
  else { const e = await r.json().catch(()=>({})); msg.textContent = e.error||'Upload failed'; msg.className='status-msg err'; }
});

// ── publish ──
$('publish-btn').addEventListener('click', async () => {
  const btn = $('publish-btn'), msg = $('publish-msg');
  btn.disabled = true; btn.textContent='Publishing…'; msg.style.display='none';
  const r = await api('POST','/compile');
  btn.disabled = false; btn.textContent='Publish to site'; msg.style.display='';
  if (r && r.ok){ msg.textContent='Published — your site is live.'; msg.className='status-msg ok'; }
  else { msg.textContent='Something went wrong — try again.'; msg.className='status-msg err'; }
});

// ── init ──
(async () => {
  const r = await fetch(API + '/works');
  if (r.ok) loadList(); else show('login');
})();
</script>
</body>
</html>"""


admin.register_core(ADMIN_HTML)


def create_blueprint(artist_slug):
    bp.url_prefix = ''
    return bp
