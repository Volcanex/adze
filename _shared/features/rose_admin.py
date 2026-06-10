"""
Rose Jones personal admin — /admin on rosefpjones.com.
Reads/writes artists/rose/information.json and triggers recompile.
Only activates when domain is rosefpjones.com.
"""

import io
import json
import re
from pathlib import Path
from flask import request, jsonify, make_response, abort, send_file, send_from_directory

try:
    from features.artist_admin import ArtistAdmin
    from features import rose_pages
except ImportError:
    from artist_admin import ArtistAdmin
    import rose_pages

ARTIST_SLUG = 'rose'
DOMAIN = 'rosefpjones.com'
BASE_URL = f'https://{DOMAIN}'
COOKIE = 'rose_admin'
PANEL_URL = '/api/rose-admin/panel'
INFO_PATH = Path('artists/rose/information.json')
ASSETS_PATH = Path('artists/rose/assets')
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def _render():
    """Regenerate Rose's data-driven pages from information.json (the source of
    truth) and return the generated page slugs so the framework marks them
    read-only. home/ and contact/ are hand-edited and deliberately excluded."""
    info = _load_info()
    rose_pages.regenerate(info)
    pages = ['works', 'exhibitions', 'about']
    pages += [f'works/{w["slug"]}' for w in rose_pages._all_works(info)]
    pages += [f'exhibitions/{e["slug"]}' for e in info.get('exhibitions', [])]
    return pages


admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, render=_render, blueprint_name='rose_admin')
bp = admin.bp
_auth_required = admin.auth_required
_domain_guard = admin.domain_guard
_get_token = admin.token


def _load_info():
    return json.loads(INFO_PATH.read_text())


def _save_info(data):
    INFO_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _slugify(text):
    s = re.sub(r'[^a-z0-9-]', '-', text.lower())
    return re.sub(r'-+', '-', s).strip('-')


# ── HTML ───────────────────────────────────────────────────────────────────────

ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — Rose Jones</title>
<style>
@font-face {
  font-family: 'Quasimoda';
  font-style: normal;
  font-weight: 100 500;
  font-display: swap;
  src: url('/api/rose-admin/font/quasimoda-light.woff2') format('woff2'),
       url('/api/rose-admin/font/quasimoda-light.otf') format('opentype');
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Quasimoda', -apple-system, sans-serif;
  background: #fff; color: #000;
  max-width: 414px; margin: 0 auto;
  padding: 0 16px 80px;
  min-height: 100vh;
}

/* header */
.hd {
  height: 54px; display: flex; align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #000; margin-bottom: 32px;
  position: sticky; top: 0; background: #fff; z-index: 10;
}
.hd-brand { font-weight: 250; font-size: 28px; }
.hd-action { font-size: 13px; font-weight: 250; cursor: pointer; background: none; border: none; font-family: inherit; padding: 0; }

/* login */
#screen-login { padding-top: 80px; }
#screen-login h2 { font-weight: 250; font-size: 22px; margin-bottom: 24px; }

/* tabs */
.tabs { display: flex; border-bottom: 1px solid #000; margin-bottom: 24px; }
.tab {
  padding: 10px 14px; font-size: 14px; font-weight: 250;
  cursor: pointer; border: none; background: none;
  font-family: inherit; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab.on-works       { border-bottom-color: #0000FF; color: #0000FF; }
.tab.on-exhibitions { border-bottom-color: #1AFF00; color: #000; }
.tab.on-qr          { border-bottom-color: #8C00FF; color: #8C00FF; }

/* item list */
.item-list { list-style: none; }
.item-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0; border-bottom: 1px solid #e8e8e8;
  cursor: pointer; gap: 12px;
}
.item-row:hover .item-title { text-decoration: underline; }
.item-title { font-size: 16px; font-weight: 250; flex: 1; }
.item-meta  { font-size: 13px; font-weight: 250; color: #888; white-space: nowrap; }
.item-arrow { font-size: 16px; color: #bbb; flex-shrink: 0; }
.badge-missing { font-size: 10px; background: #eee; padding: 1px 5px; margin-left: 6px; vertical-align: middle; }

/* add row */
.add-row { padding: 16px 0; border-bottom: 1px solid #e8e8e8; }

/* edit screen — initial-hidden handled by inline style like every other screen;
   no CSS display rule here, or show('edit') (which clears inline display) can't reveal it */
.back-btn {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 250; cursor: pointer;
  background: none; border: none; font-family: inherit;
  padding: 0; margin-bottom: 24px; color: #000;
}
.back-btn:hover { text-decoration: underline; }
.edit-title { font-weight: 250; font-size: 24px; margin-bottom: 28px; }

/* fields */
.field { margin-bottom: 18px; }
.field label {
  display: block; font-size: 11px; font-weight: 250;
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 7px;
}
.field input, .field select, .field textarea {
  width: 100%; border: 1px solid #ccc; padding: 10px 12px;
  font-family: inherit; font-size: 16px; font-weight: 250;
  background: #fff; outline: none; border-radius: 0; -webkit-appearance: none;
}
.field input:focus, .field select:focus, .field textarea:focus {
  border-color: #000; outline: 2px solid #000; outline-offset: -2px;
}
.form-row { display: flex; gap: 12px; }
.form-row .field { flex: 1; }

/* image section */
.img-section { margin: 24px 0; padding-top: 24px; border-top: 1px solid #eee; }
.img-section h3 { font-size: 11px; font-weight: 250; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 16px; }
.img-current {
  width: 100%; aspect-ratio: 4/3; object-fit: cover;
  display: block; border: 1px solid #eee; margin-bottom: 16px; background: #f8f8f8;
}
.img-placeholder {
  width: 100%; aspect-ratio: 4/3; background: #f0f0f0;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: #999; margin-bottom: 16px;
}
.field input[type=file] { padding: 8px 12px; font-size: 14px; }

/* buttons */
.btn {
  display: inline-block; border: 1px solid #000; padding: 11px 22px;
  font-family: inherit; font-size: 14px; font-weight: 250;
  background: #000; color: #fff; cursor: pointer;
  letter-spacing: 0.03em; border-radius: 4px; -webkit-appearance: none;
  transition: opacity .15s ease, background .15s ease, color .15s ease, border-color .15s ease;
}
.btn:hover { opacity: 0.82; }
.btn:active { transform: translateY(1px); }
.btn:disabled { opacity: 0.4; cursor: default; transform: none; }
.btn-ghost { background: #fff; color: #000; }
.btn-ghost:hover { background: #f2f2f2; opacity: 1; }
.btn-danger { background: #fff; color: #b3261e; border-color: #e2bbb7; }
.btn-danger:hover { background: #b3261e; color: #fff; border-color: #b3261e; opacity: 1; }
.btn-sm { padding: 7px 14px; font-size: 12px; }
.btn-row { display: flex; gap: 10px; align-items: center; margin-top: 24px; flex-wrap: wrap; }
.btn-row .spacer { flex: 1; }
.status-msg { font-size: 12px; font-weight: 250; }
.status-msg.ok  { color: green; }
.status-msg.err { color: red; }

/* QR */
.qr-block { padding: 8px 0; }
.qr-block img { width: 200px; height: 200px; display: block; margin: 16px 0; border: 1px solid #eee; }
.qr-url { font-size: 13px; font-weight: 250; color: #666; margin: 10px 0; word-break: break-all; }

/* compile */
.compile-block { margin-top: 40px; padding-top: 24px; border-top: 1px solid #000; }
.compile-block h3 { font-size: 11px; font-weight: 250; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 14px; }

/* multi-image grid */
.img-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px; }
.img-grid-item { position: relative; aspect-ratio: 1; }
.img-grid-item img { width: 100%; height: 100%; object-fit: cover; display: block; border: 1px solid #eee; }
.img-del { position: absolute; top: 3px; right: 3px; background: rgba(0,0,0,0.65); color: #fff; border: none; font-size: 14px; line-height: 1; padding: 2px 5px; cursor: pointer; font-family: inherit; }

/* business card */
.card-stage { display: flex; flex-direction: column; align-items: center; gap: 24px; margin-top: 24px; padding-top: 24px; border-top: 1px solid #eee; }
.bizcard {
  width: 85mm; height: 55mm; background: #fff; color: #000; position: relative;
  font-family: 'Quasimoda', -apple-system, sans-serif; overflow: hidden;
  border: 1px solid #000;
}
.bizcard .bc-top { position: absolute; top: 7mm; left: 7mm; }
.bizcard .bc-name { font-size: 10mm; line-height: 0.9; font-weight: 250; }
.bizcard .bc-role { margin-top: 3mm; font-size: 2.8mm; letter-spacing: 0.1em; text-transform: uppercase; color: #8C00FF; }
.bizcard .bc-details {
  position: absolute; bottom: 7mm; left: 7mm; max-width: 44mm; font-size: 2.9mm; line-height: 1.9;
  font-weight: 250; letter-spacing: 0.02em;
}
.bizcard .bc-qr { position: absolute; top: 50%; right: 7mm; transform: translateY(-50%); width: 26mm; height: 26mm; }
.bizcard .bc-qr svg { width: 100%; height: 100%; display: block; }
.card-note { font-size: 12px; color: #888; font-weight: 250; text-align: center; }

/* print-only helpers — hidden on screen */
#print-qr, #print-sheet { display: none; }
#print-qr svg { width: 60mm; height: 60mm; display: block; }

@media print {
  @page { size: A4; margin: 6mm; }
  body { background: #fff !important; max-width: none; padding: 0; min-height: 0; }
  #screen-login, #screen-edit, #screen-add-work, #screen-add-exh,
  .hd, .tabs, .compile-block, #tab-works, #tab-exhibitions,
  .qr-block, .card-note, .bc-actions { display: none !important; }
  .card-stage { border: none; margin: 0; padding: 0; }
  .bizcard { border: 1px solid #000; }

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
  <div class="hd"><span class="hd-brand">rose jones</span></div>
  <h2>Admin</h2>
  <div class="field" style="margin-top:24px">
    <label>Password</label>
    <input type="password" id="pw-input" autocomplete="current-password">
  </div>
  <button class="btn" id="login-btn">Enter</button>
  <div id="login-err" style="margin-top:12px;font-size:13px;color:red;display:none">Wrong password.</div>
</div>

<!-- LIST -->
<div id="screen-list" style="display:none">
  <div class="hd">
    <span class="hd-brand">rose jones</span>
    <button class="hd-action" id="logout-btn">Log out</button>
  </div>
  <div class="tabs">
    <button class="tab on-works" data-tab="works">Works</button>
    <button class="tab" data-tab="exhibitions">Exhibitions</button>
    <button class="tab" data-tab="qr">QR</button>
  </div>

  <!-- works tab -->
  <div id="tab-works">
    <ul class="item-list" id="works-list"></ul>
    <div class="add-row">
      <button class="btn btn-ghost btn-sm" id="add-work-btn">+ Add work</button>
    </div>
  </div>

  <!-- exhibitions tab -->
  <div id="tab-exhibitions" style="display:none">
    <ul class="item-list" id="exhibitions-list"></ul>
    <div class="add-row">
      <button class="btn btn-ghost btn-sm" id="add-exh-btn">+ Add exhibition</button>
    </div>
  </div>

  <!-- qr tab -->
  <div id="tab-qr" style="display:none">
    <div class="qr-block">
      <div class="field">
        <label>Page</label>
        <select id="qr-page">
          <option value="/">Home</option>
          <option value="/works">Works</option>
          <option value="/exhibitions">Exhibitions</option>
          <option value="/about">About</option>
          <option value="/contact">Contact</option>
        </select>
      </div>
      <div class="qr-url" id="qr-url-label"></div>
      <img id="qr-img" src="" alt="QR code">
      <a class="btn btn-ghost btn-sm" id="qr-download" download="rose-qr.png">Download PNG</a>
    </div>

    <div class="card-stage">
      <div class="bizcard">
        <div class="bc-top">
          <div class="bc-name">rose<br>jones</div>
          <div class="bc-role">Multidisciplinary Artist</div>
        </div>
        <div class="bc-details">
          rosefpjones@gmail.com<br>
          @rosefpjones
        </div>
        <div class="bc-qr" id="bc-qr"></div>
      </div>
      <div class="bc-actions btn-row" style="justify-content:center">
        <button class="btn" id="print-card-btn">Print cards (A4)</button>
        <button class="btn btn-ghost" id="print-qr-btn">Print QR only</button>
      </div>
      <div class="card-note">Print fills an A4 sheet with cards &middot; QR opens rosefpjones.com</div>
    </div>
  </div>

  <div class="compile-block">
    <button class="btn" id="compile-btn">Save changes</button>
    <div class="status-msg" id="compile-msg" style="display:none;margin-top:10px"></div>
  </div>
</div>

<!-- EDIT -->
<div id="screen-edit" style="display:none">
  <div class="hd">
    <span class="hd-brand">rose jones</span>
    <button class="hd-action" id="logout-btn-edit">Log out</button>
  </div>
  <button class="back-btn" id="back-btn">&#8592; Back</button>
  <div class="edit-title" id="edit-title"></div>

  <!-- work fields -->
  <div id="edit-work-fields">
    <div class="form-row">
      <div class="field"><label>Title</label><input type="text" id="ef-title"></div>
      <div class="field"><label>Year</label><input type="number" id="ef-year"></div>
    </div>
    <div class="form-row">
      <div class="field"><label>Medium</label><input type="text" id="ef-medium"></div>
      <div class="field"><label>Dimensions</label><input type="text" id="ef-dimensions"></div>
    </div>
    <div class="img-section">
      <h3>Images</h3>
      <div class="img-grid" id="ef-img-grid"></div>
      <div class="field"><label>Add images</label><input type="file" id="ef-img-file" accept="image/*" multiple></div>
      <button class="btn btn-ghost btn-sm" id="ef-upload-btn">Upload</button>
      <span class="status-msg" id="ef-upload-msg" style="margin-left:8px"></span>
    </div>
  </div>

  <!-- exhibition fields -->
  <div id="edit-exh-fields" style="display:none">
    <div class="form-row">
      <div class="field"><label>Title</label><input type="text" id="ee-title"></div>
      <div class="field"><label>Year</label><input type="number" id="ee-year"></div>
    </div>
    <div class="form-row">
      <div class="field"><label>Type</label><input type="text" id="ee-type"></div>
      <div class="field"><label>Location</label><input type="text" id="ee-location"></div>
    </div>
    <div class="img-section">
      <h3>Images</h3>
      <div class="img-grid" id="ee-img-grid"></div>
      <div class="field"><label>Add images</label><input type="file" id="ee-img-file" accept="image/*" multiple></div>
      <button class="btn btn-ghost btn-sm" id="ee-upload-btn">Upload</button>
      <span class="status-msg" id="ee-upload-msg" style="margin-left:8px"></span>
    </div>
  </div>

  <div class="btn-row">
    <button class="btn" id="save-btn">Save</button>
    <span class="status-msg" id="save-msg"></span>
    <span class="spacer"></span>
    <button class="btn btn-danger" id="delete-btn">Delete</button>
  </div>
</div>

<!-- ADD WORK MODAL-ISH -->
<div id="screen-add-work" style="display:none">
  <div class="hd"><span class="hd-brand">rose jones</span></div>
  <button class="back-btn" id="back-add-work">&#8592; Back</button>
  <div class="edit-title">New work</div>
  <div class="form-row">
    <div class="field"><label>Title</label><input type="text" id="aw-title"></div>
    <div class="field"><label>Year</label><input type="number" id="aw-year"></div>
  </div>
  <div class="form-row">
    <div class="field"><label>Medium</label><input type="text" id="aw-medium"></div>
    <div class="field"><label>Dimensions</label><input type="text" id="aw-dimensions"></div>
  </div>
  <div class="img-section">
    <h3>Image</h3>
    <div class="field"><label>Upload image</label><input type="file" id="aw-img-file" accept="image/*"></div>
  </div>
  <div class="btn-row">
    <button class="btn" id="aw-save-btn">Add work</button>
    <span class="status-msg" id="aw-msg"></span>
  </div>
</div>

<!-- ADD EXHIBITION -->
<div id="screen-add-exh" style="display:none">
  <div class="hd"><span class="hd-brand">rose jones</span></div>
  <button class="back-btn" id="back-add-exh">&#8592; Back</button>
  <div class="edit-title">New exhibition</div>
  <div class="form-row">
    <div class="field"><label>Title</label><input type="text" id="ae-title"></div>
    <div class="field"><label>Year</label><input type="number" id="ae-year"></div>
  </div>
  <div class="form-row">
    <div class="field"><label>Type</label><input type="text" id="ae-type" placeholder="Solo show"></div>
    <div class="field"><label>Location</label><input type="text" id="ae-location"></div>
  </div>
  <div class="btn-row">
    <button class="btn" id="ae-save-btn">Add exhibition</button>
    <span class="status-msg" id="ae-msg"></span>
  </div>
</div>

<!-- standalone QR, used only for "Print QR only" -->
<div id="print-qr"></div>
<!-- A4 grid of card copies, used only for "Print cards" -->
<div id="print-sheet"></div>

<script>
// ── state ──────────────────────────────────────────────────────────────────
let editSlug = null;
let editType = null; // 'work' | 'exhibition'
let worksData = [];
let exhibitionsData = [];

// ── api ────────────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  const r = await fetch(path, opts);
  if (r.status === 401) { show('login'); return null; }
  return r;
}

// ── screens ────────────────────────────────────────────────────────────────
const SCREENS = ['login','list','edit','add-work','add-exh'];
function show(name) {
  SCREENS.forEach(s => {
    document.getElementById(`screen-${s}`).style.display = s === name ? '' : 'none';
  });
}

// ── tabs ───────────────────────────────────────────────────────────────────
let activeTab = 'works';
function setTab(tab) {
  activeTab = tab;
  ['works','exhibitions','qr'].forEach(t => {
    document.getElementById(`tab-${t}`).style.display = t === tab ? '' : 'none';
  });
  document.querySelectorAll('.tab').forEach(t => {
    t.className = 'tab' + (t.dataset.tab === tab ? ` on-${tab}` : '');
  });
  if (tab === 'qr') { updateQR(); loadCard(); }
}
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => setTab(t.dataset.tab)));

// ── login ──────────────────────────────────────────────────────────────────
document.getElementById('login-btn').addEventListener('click', async () => {
  const r = await fetch('/api/rose-admin/login', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ token: document.getElementById('pw-input').value }),
  });
  if (r.ok) { document.getElementById('login-err').style.display = 'none'; loadList(); }
  else document.getElementById('login-err').style.display = '';
});
document.getElementById('pw-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('login-btn').click();
});
function doLogout() {
  api('POST', '/api/rose-admin/logout');
  show('login');
}
document.getElementById('logout-btn').addEventListener('click', doLogout);
document.getElementById('logout-btn-edit').addEventListener('click', doLogout);

// ── list ───────────────────────────────────────────────────────────────────
async function loadList() {
  const [wr, er] = await Promise.all([
    fetch('/api/rose-admin/works'),
    fetch('/api/rose-admin/exhibitions'),
  ]);
  if (wr.status === 401) { show('login'); return; }
  worksData = await wr.json();
  exhibitionsData = await er.json();
  renderList(worksData, 'works-list', 'work');
  renderList(exhibitionsData, 'exhibitions-list', 'exhibition');
  show('list');
}

function renderList(items, listId, type) {
  const ul = document.getElementById(listId);
  ul.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.className = 'item-row';

    const titleSpan = document.createElement('span');
    titleSpan.className = 'item-title';
    titleSpan.textContent = item.title;
    if (item.status === 'missing') {
      const badge = document.createElement('span');
      badge.className = 'badge-missing';
      badge.textContent = 'no image';
      titleSpan.appendChild(badge);
    }

    const metaSpan = document.createElement('span');
    metaSpan.className = 'item-meta';
    metaSpan.textContent = item.year || '';

    const arrowSpan = document.createElement('span');
    arrowSpan.className = 'item-arrow';
    arrowSpan.textContent = '›';

    li.appendChild(titleSpan);
    li.appendChild(metaSpan);
    li.appendChild(arrowSpan);
    li.addEventListener('click', () => openEdit(type, item.slug));
    ul.appendChild(li);
  });
}

// ── edit ───────────────────────────────────────────────────────────────────
function openEdit(type, slug) {
  try {
    const list = type === 'work' ? worksData : exhibitionsData;
    const item = list.find(i => i.slug === slug);
    if (!item) { console.error('Item not found:', type, slug); return; }

    editSlug = slug;
    editType = type;

    document.getElementById('edit-title').textContent = item.title;
    document.getElementById('edit-work-fields').style.display = type === 'work' ? '' : 'none';
    document.getElementById('edit-exh-fields').style.display  = type === 'exhibition' ? '' : 'none';

    if (type === 'work') {
      document.getElementById('ef-title').value      = item.title || '';
      document.getElementById('ef-year').value       = item.year  || '';
      document.getElementById('ef-medium').value     = item.medium || '';
      document.getElementById('ef-dimensions').value = item.dimensions || '';
      renderWorkImages(item.images || (item.image ? [item.image] : []));
      document.getElementById('ef-img-file').value = '';
      document.getElementById('ef-upload-msg').textContent = '';
    } else {
      document.getElementById('ee-title').value    = item.title    || '';
      document.getElementById('ee-year').value     = item.year     || '';
      document.getElementById('ee-type').value     = item.type     || '';
      document.getElementById('ee-location').value = item.location || '';
      const imgs = item.images || (item.image ? [item.image] : []);
      renderExhImages(imgs);
      document.getElementById('ee-img-file').value = '';
      document.getElementById('ee-upload-msg').textContent = '';
    }
    document.getElementById('save-msg').textContent = '';
    show('edit');
  } catch(e) {
    console.error('openEdit failed:', e);
  }
}

function setImgWrap(wrapId, imgFile) {
  const wrap = document.getElementById(wrapId);
  if (imgFile) {
    wrap.innerHTML = `<img class="img-current" src="/api/rose-admin/asset/${imgFile}" alt="">`;
  } else {
    wrap.innerHTML = `<div class="img-placeholder">No image yet</div>`;
  }
}

function renderWorkImages(images) {
  const grid = document.getElementById('ef-img-grid');
  if (!images || !images.length) {
    grid.innerHTML = '<div class="img-placeholder" style="margin-bottom:16px">No images yet</div>';
    return;
  }
  grid.innerHTML = images.map(img => `
    <div class="img-grid-item">
      <img src="/api/rose-admin/asset/${img}" alt="">
      <button class="img-del" onclick="deleteWorkImage('${img}')">×</button>
    </div>`).join('');
}

async function deleteWorkImage(filename) {
  const r = await api('DELETE', `/api/rose-admin/works/${editSlug}/image/${encodeURIComponent(filename)}`);
  if (!r) return;
  if (r.ok) {
    const d = await r.json();
    renderWorkImages(d.images);
    const wr = await fetch('/api/rose-admin/works');
    if (wr.ok) { worksData = await wr.json(); renderList(worksData, 'works-list', 'work'); }
  }
}

function renderExhImages(images) {
  const grid = document.getElementById('ee-img-grid');
  if (!images || !images.length) {
    grid.innerHTML = '<div class="img-placeholder" style="margin-bottom:16px">No images yet</div>';
    return;
  }
  grid.innerHTML = images.map(img => `
    <div class="img-grid-item">
      <img src="/api/rose-admin/asset/${img}" alt="">
      <button class="img-del" onclick="deleteExhImage('${img}')">×</button>
    </div>`).join('');
}

async function deleteExhImage(filename) {
  const r = await api('DELETE', `/api/rose-admin/exhibitions/${editSlug}/image/${encodeURIComponent(filename)}`);
  if (!r) return;
  if (r.ok) {
    const d = await r.json();
    renderExhImages(d.images);
    // refresh cached data
    const er = await fetch('/api/rose-admin/exhibitions');
    if (er.ok) { exhibitionsData = await er.json(); renderList(exhibitionsData, 'exhibitions-list', 'exhibition'); }
  }
}

document.getElementById('back-btn').addEventListener('click', () => { show('list'); setTab(editType === 'work' ? 'works' : 'exhibitions'); });

document.getElementById('delete-btn').addEventListener('click', async () => {
  const what = editType === 'work' ? 'work' : 'exhibition';
  if (!confirm(`Delete this ${what}? This removes its page and images for good.`)) return;
  const endpoint = editType === 'work' ? 'works' : 'exhibitions';
  const wasType = editType;
  const r = await api('DELETE', `/api/rose-admin/${endpoint}/${editSlug}`);
  if (!r) return;
  if (r.ok) {
    await api('POST', '/api/rose-admin/compile');  // republish so it's gone from the live site now
    await loadList();
    setTab(wasType === 'work' ? 'works' : 'exhibitions');
  } else {
    const msg = document.getElementById('save-msg');
    msg.textContent = 'Delete failed'; msg.className = 'status-msg err';
  }
});

document.getElementById('save-btn').addEventListener('click', async () => {
  const msg = document.getElementById('save-msg');
  const endpoint = editType === 'work' ? 'works' : 'exhibitions';
  let body;
  if (editType === 'work') {
    body = {
      title:      document.getElementById('ef-title').value,
      year:       parseInt(document.getElementById('ef-year').value) || null,
      medium:     document.getElementById('ef-medium').value,
      dimensions: document.getElementById('ef-dimensions').value,
    };
  } else {
    body = {
      title:    document.getElementById('ee-title').value,
      year:     parseInt(document.getElementById('ee-year').value) || null,
      type:     document.getElementById('ee-type').value,
      location: document.getElementById('ee-location').value,
    };
  }
  msg.textContent = 'Saving…'; msg.className = 'status-msg';
  const r = await api('PUT', `/api/rose-admin/${endpoint}/${editSlug}`, body);
  if (!r) return;
  if (r.ok) {
    document.getElementById('edit-title').textContent = body.title;
    msg.textContent = 'Saved'; msg.className = 'status-msg ok';
    setTimeout(() => { msg.textContent = ''; }, 2000);
  } else {
    msg.textContent = 'Error saving'; msg.className = 'status-msg err';
  }
});

// image upload on edit page
// work upload (multiple images)
document.getElementById('ef-upload-btn').addEventListener('click', async () => {
  const msg = document.getElementById('ef-upload-msg');
  const files = Array.from(document.getElementById('ef-img-file').files);
  if (!files.length) { msg.textContent = 'Choose a file first'; msg.className = 'status-msg err'; return; }
  msg.textContent = `Uploading ${files.length} file${files.length > 1 ? 's' : ''}…`; msg.className = 'status-msg';
  let lastImages = null;
  for (const file of files) {
    const fd = new FormData(); fd.append('file', file);
    const r = await fetch(`/api/rose-admin/works/${editSlug}/image`, { method: 'POST', body: fd });
    if (r.status === 401) { show('login'); return; }
    if (r.ok) { const d = await r.json(); lastImages = d.images; }
  }
  if (lastImages) {
    renderWorkImages(lastImages);
    document.getElementById('ef-img-file').value = '';
    msg.textContent = 'Uploaded'; msg.className = 'status-msg ok';
    setTimeout(() => { msg.textContent = ''; }, 2000);
    const wr = await fetch('/api/rose-admin/works');
    if (wr.ok) { worksData = await wr.json(); renderList(worksData, 'works-list', 'work'); }
  } else {
    msg.textContent = 'Upload failed'; msg.className = 'status-msg err';
  }
});

// exhibition upload (multiple files)
document.getElementById('ee-upload-btn').addEventListener('click', async () => {
  const msg = document.getElementById('ee-upload-msg');
  const files = Array.from(document.getElementById('ee-img-file').files);
  if (!files.length) { msg.textContent = 'Choose a file first'; msg.className = 'status-msg err'; return; }
  msg.textContent = `Uploading ${files.length} file${files.length > 1 ? 's' : ''}…`; msg.className = 'status-msg';
  let lastImages = null;
  for (const file of files) {
    const fd = new FormData(); fd.append('file', file);
    const r = await fetch(`/api/rose-admin/exhibitions/${editSlug}/image`, { method: 'POST', body: fd });
    if (r.status === 401) { show('login'); return; }
    if (r.ok) { const d = await r.json(); lastImages = d.images; }
  }
  if (lastImages) {
    renderExhImages(lastImages);
    document.getElementById('ee-img-file').value = '';
    msg.textContent = 'Uploaded'; msg.className = 'status-msg ok';
    setTimeout(() => { msg.textContent = ''; }, 2000);
    const er = await fetch('/api/rose-admin/exhibitions');
    if (er.ok) { exhibitionsData = await er.json(); renderList(exhibitionsData, 'exhibitions-list', 'exhibition'); }
  } else {
    msg.textContent = 'Upload failed'; msg.className = 'status-msg err';
  }
});

// ── add work ───────────────────────────────────────────────────────────────
document.getElementById('add-work-btn').addEventListener('click', () => { show('add-work'); });
document.getElementById('back-add-work').addEventListener('click', () => { show('list'); setTab('works'); });
document.getElementById('aw-save-btn').addEventListener('click', async () => {
  const msg = document.getElementById('aw-msg');
  const body = {
    title:      document.getElementById('aw-title').value.trim(),
    year:       parseInt(document.getElementById('aw-year').value) || null,
    medium:     document.getElementById('aw-medium').value,
    dimensions: document.getElementById('aw-dimensions').value,
  };
  if (!body.title) { msg.textContent = 'Title required'; msg.className = 'status-msg err'; return; }
  msg.textContent = 'Adding…'; msg.className = 'status-msg';
  const r = await api('POST', '/api/rose-admin/works', body);
  if (!r) return;
  if (r.ok) {
    const newWork = await r.json();
    const fileInput = document.getElementById('aw-img-file');
    if (fileInput.files.length) {
      const fd = new FormData(); fd.append('file', fileInput.files[0]);
      await fetch(`/api/rose-admin/works/${newWork.slug}/image`, { method: 'POST', body: fd });
    }
    msg.textContent = 'Added!'; msg.className = 'status-msg ok';
    ['aw-title','aw-year','aw-medium','aw-dimensions'].forEach(id => { document.getElementById(id).value = ''; });
    fileInput.value = '';
    await loadList();
    setTimeout(() => { show('list'); setTab('works'); }, 800);
  } else {
    const err = await r.json().catch(() => ({}));
    msg.textContent = err.error || 'Error'; msg.className = 'status-msg err';
  }
});

// ── add exhibition ─────────────────────────────────────────────────────────
document.getElementById('add-exh-btn').addEventListener('click', () => { show('add-exh'); });
document.getElementById('back-add-exh').addEventListener('click', () => { show('list'); setTab('exhibitions'); });
document.getElementById('ae-save-btn').addEventListener('click', async () => {
  const msg = document.getElementById('ae-msg');
  const body = {
    title:    document.getElementById('ae-title').value.trim(),
    year:     parseInt(document.getElementById('ae-year').value) || null,
    type:     document.getElementById('ae-type').value,
    location: document.getElementById('ae-location').value,
  };
  if (!body.title) { msg.textContent = 'Title required'; msg.className = 'status-msg err'; return; }
  msg.textContent = 'Adding…'; msg.className = 'status-msg';
  const r = await api('POST', '/api/rose-admin/exhibitions', body);
  if (!r) return;
  if (r.ok) {
    msg.textContent = 'Added!'; msg.className = 'status-msg ok';
    ['ae-title','ae-year','ae-type','ae-location'].forEach(id => { document.getElementById(id).value = ''; });
    await loadList();
    setTimeout(() => { show('list'); setTab('exhibitions'); }, 800);
  } else {
    msg.textContent = 'Error'; msg.className = 'status-msg err';
  }
});

// ── QR ─────────────────────────────────────────────────────────────────────
function updateQR() {
  const page = document.getElementById('qr-page').value;
  const url  = 'https://rosefpjones.com' + page;
  document.getElementById('qr-url-label').textContent = url;
  const src = `/api/rose-admin/qr?page=${encodeURIComponent(page)}`;
  document.getElementById('qr-img').src = src;
  const dl = document.getElementById('qr-download');
  dl.href = src;
  dl.download = `rose-qr${page.replace(/\//g, '-').replace(/^-/,'') || 'home'}.png`;
}
document.getElementById('qr-page').addEventListener('change', updateQR);

// ── business card ──────────────────────────────────────────────────────────
function loadCard() {
  const box = document.getElementById('bc-qr');
  if (box.dataset.loaded) return;
  fetch('/api/rose-admin/qr?page=/&fmt=svg')
    .then(r => r.text())
    .then(svg => {
      box.innerHTML = svg;
      document.getElementById('print-qr').innerHTML = svg;
      box.dataset.loaded = '1';
      buildSheet();
    });
}

// Fill the A4 print sheet with copies of the card (2 cols x 5 rows = 10).
function buildSheet() {
  const sheet = document.getElementById('print-sheet');
  const card = document.querySelector('.card-stage .bizcard');
  if (!sheet || !card) return;
  sheet.innerHTML = '';
  for (let i = 0; i < 10; i++) sheet.appendChild(card.cloneNode(true));
}

document.getElementById('print-card-btn').addEventListener('click', () => window.print());
document.getElementById('print-qr-btn').addEventListener('click', () => {
  document.body.classList.add('print-qr');
  window.print();
});
window.addEventListener('afterprint', () => document.body.classList.remove('print-qr'));

// ── compile ────────────────────────────────────────────────────────────────
document.getElementById('compile-btn').addEventListener('click', async () => {
  const btn = document.getElementById('compile-btn');
  const msg = document.getElementById('compile-msg');
  btn.disabled = true; btn.textContent = 'Saving…'; msg.style.display = 'none';
  const r = await api('POST', '/api/rose-admin/compile');
  btn.disabled = false; btn.textContent = 'Save changes'; msg.style.display = '';
  if (!r) return;
  if (r.ok) { msg.textContent = 'Changes saved.'; msg.className = 'status-msg ok'; }
  else      { msg.textContent = 'Something went wrong — try again.'; msg.className = 'status-msg err'; }
});

// ── init ───────────────────────────────────────────────────────────────────
(async () => {
  const r = await fetch('/api/rose-admin/works');
  if (r.ok) { loadList(); }
  else      { show('login'); }
})();
</script>
</body>
</html>"""


# ── Routes ─────────────────────────────────────────────────────────────────────
# panel / login / logout / compile come from the framework:
admin.register_core(ADMIN_HTML)


@bp.route('/api/rose-admin/font/<path:filename>')
def serve_admin_font(filename):
    """Public — fonts are needed by the login page CSS before auth completes."""
    return send_from_directory(ASSETS_PATH / 'fonts', filename)


@bp.route('/api/rose-admin/asset/<path:filename>')
@_auth_required
def serve_asset(filename):
    # Stored image ids are logical (e.g. work-bed.jpg); the real files on disk are
    # the tiers work-bed-good.jpg / work-bed-full.jpg. Resolve to the display tier.
    if (ASSETS_PATH / filename).exists():
        return send_from_directory(ASSETS_PATH, filename)
    stem = filename.rsplit('.', 1)[0]
    for cand in (f'{stem}-good.jpg', f'{stem}-full.jpg'):
        if (ASSETS_PATH / cand).exists():
            return send_from_directory(ASSETS_PATH, cand)
    abort(404)


def _remove_tiers(filename):
    """Delete the master + display tiers behind a logical image id."""
    stem = filename.rsplit('.', 1)[0]
    for cand in (filename, f'{stem}-full.jpg', f'{stem}-good.jpg'):
        p = ASSETS_PATH / cand
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass


@bp.route('/api/rose-admin/works')
@_auth_required
def get_works():
    return jsonify(_load_info().get('works', []))


@bp.route('/api/rose-admin/works/<slug>')
@_auth_required
def get_work(slug):
    for w in _load_info().get('works', []):
        if w['slug'] == slug:
            return jsonify(w)
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/rose-admin/works', methods=['POST'])
@_auth_required
def create_work():
    data = _load_info()
    body = request.get_json(silent=True) or {}
    title = body.get('title', '').strip()
    if not title:
        return jsonify({'error': 'title required'}), 400
    if any(w['title'] == title for w in data.get('works', [])):
        return jsonify({'error': 'A work with that title already exists'}), 409
    slug = _slugify(title)
    existing = {w['slug'] for w in data.get('works', [])}
    base, n = slug, 1
    while slug in existing:
        slug = f'{base}-{n}'; n += 1
    work = {'slug': slug, 'title': title, 'year': body.get('year'),
            'medium': body.get('medium', ''), 'dimensions': body.get('dimensions', ''),
            'status': 'missing', 'image': None, 'source': None}
    data.setdefault('works', []).append(work)
    _save_info(data)
    return jsonify(work), 201


@bp.route('/api/rose-admin/works/<slug>', methods=['PUT'])
@_auth_required
def update_work(slug):
    data = _load_info()
    body = request.get_json(silent=True) or {}
    for work in data.get('works', []):
        if work['slug'] == slug:
            for key in ('title', 'year', 'medium', 'dimensions'):
                if key in body:
                    work[key] = body[key]
            _save_info(data)
            return jsonify({'ok': True})
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/rose-admin/works/<slug>/image', methods=['POST'])
@_auth_required
def upload_work_image(slug):
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    ext = Path(f.filename).suffix.lower() if f.filename else '.jpg'
    if ext not in ALLOWED_EXTS:
        return jsonify({'error': 'File type not allowed'}), 400
    data = _load_info()
    for work in data.get('works', []):
        if work['slug'] == slug:
            existing = work.get('images') or ([work['image']] if work.get('image') else [])
            base = f'work-{slug}'
            stem = base
            n = 2
            while f'{stem}.jpg' in existing or (ASSETS_PATH / f'{stem}-full.jpg').exists():
                stem = f'{base}-{n}'; n += 1
            # writes <stem>-full.jpg (master) + <stem>-good.jpg (display tier)
            rose_pages.save_master(stem, f.stream)
            filename = f'{stem}.jpg'
            existing.append(filename)
            work['images'] = existing
            work['image'] = existing[0]
            work['status'] = 'live'
            _save_info(data)
            return jsonify({'ok': True, 'image': existing[0], 'images': existing})
    return jsonify({'error': 'Work not found'}), 404


@bp.route('/api/rose-admin/works/<slug>/image/<path:filename>', methods=['DELETE'])
@_auth_required
def delete_work_image(slug, filename):
    data = _load_info()
    for work in data.get('works', []):
        if work['slug'] == slug:
            images = work.get('images') or ([work['image']] if work.get('image') else [])
            images = [i for i in images if i != filename]
            _remove_tiers(filename)
            work['images'] = images
            work['image'] = images[0] if images else None
            work['status'] = 'live' if images else 'missing'
            _save_info(data)
            return jsonify({'ok': True, 'images': images})
    return jsonify({'error': 'Work not found'}), 404


@bp.route('/api/rose-admin/works/<slug>', methods=['DELETE'])
@_auth_required
def delete_work(slug):
    data = _load_info()
    works = data.get('works', [])
    work = next((w for w in works if w['slug'] == slug), None)
    if not work:
        return jsonify({'error': 'Not found'}), 404
    for img in (work.get('images') or ([work['image']] if work.get('image') else [])):
        _remove_tiers(img)
    data['works'] = [w for w in works if w['slug'] != slug]
    _save_info(data)
    rose_pages.remove_page('works', slug)
    return jsonify({'ok': True})


@bp.route('/api/rose-admin/exhibitions')
@_auth_required
def get_exhibitions():
    return jsonify(_load_info().get('exhibitions', []))


@bp.route('/api/rose-admin/exhibitions/<slug>')
@_auth_required
def get_exhibition(slug):
    for e in _load_info().get('exhibitions', []):
        if e['slug'] == slug:
            return jsonify(e)
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/rose-admin/exhibitions', methods=['POST'])
@_auth_required
def create_exhibition():
    data = _load_info()
    body = request.get_json(silent=True) or {}
    title = body.get('title', '').strip()
    if not title:
        return jsonify({'error': 'title required'}), 400
    slug = _slugify(title)
    existing = {e['slug'] for e in data.get('exhibitions', [])}
    base, n = slug, 1
    while slug in existing:
        slug = f'{base}-{n}'; n += 1
    exh = {'slug': slug, 'title': title, 'year': body.get('year'),
           'type': body.get('type', ''), 'location': body.get('location', ''),
           'status': 'missing', 'image': None}
    data.setdefault('exhibitions', []).append(exh)
    _save_info(data)
    return jsonify(exh), 201


@bp.route('/api/rose-admin/exhibitions/<slug>', methods=['PUT'])
@_auth_required
def update_exhibition(slug):
    data = _load_info()
    body = request.get_json(silent=True) or {}
    for exh in data.get('exhibitions', []):
        if exh['slug'] == slug:
            for key in ('title', 'year', 'type', 'location'):
                if key in body:
                    exh[key] = body[key]
            _save_info(data)
            return jsonify({'ok': True})
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/rose-admin/exhibitions/<slug>/image', methods=['POST'])
@_auth_required
def upload_exhibition_image(slug):
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    ext = Path(f.filename).suffix.lower() if f.filename else '.jpg'
    if ext not in ALLOWED_EXTS:
        return jsonify({'error': 'File type not allowed'}), 400
    data = _load_info()
    for exh in data.get('exhibitions', []):
        if exh['slug'] == slug:
            existing = exh.get('images') or ([exh['image']] if exh.get('image') else [])
            base = f'exh-{slug}'
            stem = base
            n = 2
            while f'{stem}.jpg' in existing or (ASSETS_PATH / f'{stem}-full.jpg').exists():
                stem = f'{base}-{n}'; n += 1
            # writes <stem>-full.jpg (master) + <stem>-good.jpg (display tier)
            rose_pages.save_master(stem, f.stream)
            filename = f'{stem}.jpg'
            existing.append(filename)
            exh['images'] = existing
            exh['image'] = existing[0]
            exh['status'] = 'live'
            _save_info(data)
            return jsonify({'ok': True, 'image': existing[0], 'images': existing})
    return jsonify({'error': 'Exhibition not found'}), 404


@bp.route('/api/rose-admin/exhibitions/<slug>/image/<path:filename>', methods=['DELETE'])
@_auth_required
def delete_exhibition_image(slug, filename):
    data = _load_info()
    for exh in data.get('exhibitions', []):
        if exh['slug'] == slug:
            images = exh.get('images') or ([exh['image']] if exh.get('image') else [])
            images = [i for i in images if i != filename]
            _remove_tiers(filename)
            exh['images'] = images
            exh['image'] = images[0] if images else None
            exh['status'] = 'live' if images else 'missing'
            _save_info(data)
            return jsonify({'ok': True, 'images': images})
    return jsonify({'error': 'Exhibition not found'}), 404


@bp.route('/api/rose-admin/exhibitions/<slug>', methods=['DELETE'])
@_auth_required
def delete_exhibition(slug):
    data = _load_info()
    exhibitions = data.get('exhibitions', [])
    exh = next((e for e in exhibitions if e['slug'] == slug), None)
    if not exh:
        return jsonify({'error': 'Not found'}), 404
    for img in (exh.get('images') or ([exh['image']] if exh.get('image') else [])):
        _remove_tiers(img)
    data['exhibitions'] = [e for e in exhibitions if e['slug'] != slug]
    _save_info(data)
    rose_pages.remove_page('exhibitions', slug)
    return jsonify({'ok': True})


@bp.route('/api/rose-admin/qr')
@_auth_required
def generate_qr():
    import qrcode
    page = request.args.get('page', '/')
    url = BASE_URL + page
    if request.args.get('fmt') == 'svg':
        import qrcode.image.svg
        img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=2)
        buf = io.BytesIO()
        img.save(buf)
        resp = make_response(buf.getvalue())
        resp.content_type = 'image/svg+xml'
        return resp
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


def create_blueprint(artist_slug):
    bp.url_prefix = ''
    return bp
