/* admin-shell.js — the schema-driven artist admin SPA.
 *
 * One UI for every artist. Fetches {prefix}/schema, renders a nav of the
 * artist's content types, list/edit views built from the field-editor registry,
 * a Publish button, and the "Advanced editing" handoff to the control panel.
 * No per-artist markup — the schema is the only thing that differs.
 */
window.AdminShell = (function () {
  let PREFIX, SCHEMA, root;
  const state = { type: null };

  async function api(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    const r = await fetch(PREFIX + path, opts);
    if (r.status === 401) { renderLogin(); return null; }
    return r;
  }

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function toast(msg, kind) {
    let t = document.querySelector('.as-toast');
    if (!t) { t = el('div', 'as-toast'); root.appendChild(t); }
    t.textContent = msg; t.className = 'as-toast ' + (kind || '') + ' show';
    setTimeout(() => { t.className = 'as-toast ' + (kind || ''); }, 2600);
  }

  function applyTheme() {
    const th = SCHEMA.theme || {};
    const r = document.documentElement;
    const map = { bg: '--as-bg', surface: '--as-surface', text: '--as-text',
                  accent: '--as-accent', accentText: '--as-accent-text', border: '--as-border' };
    Object.keys(map).forEach(k => { if (th[k]) r.style.setProperty(map[k], th[k]); });
    if (th.font) r.style.setProperty('--as-font', th.font);
  }

  // ── login ─────────────────────────────────────────────────────────────────
  function renderLogin() {
    root.innerHTML = '';
    const box = el('div', 'as-login');
    box.appendChild(el('h1', null, 'Admin'));
    const pw = el('input', 'af-input'); pw.type = 'password'; pw.placeholder = 'Password';
    const err = el('div', 'as-err');
    const btn = el('button', 'as-btn', 'Enter');
    async function submit() {
      const r = await fetch(PREFIX + '/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: pw.value }),
      });
      if (r.ok) boot(); else err.textContent = 'Wrong password.';
    }
    btn.onclick = submit;
    pw.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
    box.append(pw, btn, err);
    root.appendChild(box);
    pw.focus();
  }

  // ── app frame ───────────────────────────────────────────────────────────────
  function typeKeys() { return Object.keys(SCHEMA.content_types || {}); }

  function renderApp() {
    root.innerHTML = '';
    const header = el('div', 'as-header');
    header.appendChild(el('div', 'as-brand', SCHEMA.name || SCHEMA.slug));
    const logout = el('button', 'as-link', 'Log out');
    logout.onclick = async () => { await api('POST', '/logout'); renderLogin(); };
    header.appendChild(logout);
    root.appendChild(header);

    const keys = typeKeys();
    if (!keys.length) {
      root.appendChild(el('p', 'as-empty', 'No content types configured for this site yet.'));
    } else {
      const nav = el('div', 'as-nav');
      keys.forEach(k => {
        const b = el('button', 'as-tab' + (k === state.type ? ' active' : ''),
                     SCHEMA.content_types[k].label || k);
        b.onclick = () => { state.type = k; renderList(); };
        nav.appendChild(b);
      });
      root.appendChild(nav);
      if (!state.type) state.type = keys[0];
    }

    const main = el('div', 'as-main'); main.id = 'as-main'; root.appendChild(main);

    const foot = el('div', 'as-foot');
    const pub = el('button', 'as-btn', 'Publish changes');
    pub.onclick = async () => {
      pub.disabled = true; pub.textContent = 'Publishing…';
      const r = await api('POST', '/compile');
      pub.disabled = false; pub.textContent = 'Publish changes';
      if (r && r.ok) toast('Published to the live site.', 'ok');
      else toast('Publish failed.', 'err');
    };
    foot.appendChild(pub);
    if (SCHEMA.handoff) {
      const link = el('a', 'as-advanced', 'Advanced editing →');
      link.href = SCHEMA.handoff;
      foot.appendChild(link);
    }
    root.appendChild(foot);

    if (keys.length) renderList();
  }

  function itemTitle(item, tdef) {
    const ischema = tdef.item || {};
    for (const k in ischema) if (ischema[k].slug_source && item[k]) return item[k];
    return item.title || item.name || item.label || item.id;
  }

  async function renderList() {
    document.querySelectorAll('.as-tab').forEach(t =>
      t.classList.toggle('active', t.textContent === (SCHEMA.content_types[state.type].label || state.type)));
    const main = document.getElementById('as-main');
    main.innerHTML = '';
    const tdef = SCHEMA.content_types[state.type];
    const bar = el('div', 'as-listbar');
    bar.appendChild(el('h2', null, tdef.label || state.type));
    const add = el('button', 'as-btn as-btn-sm', '+ Add');
    add.onclick = () => renderEdit(null);
    bar.appendChild(add);
    main.appendChild(bar);

    const r = await api('GET', '/' + state.type);
    if (!r) return;
    const items = await r.json();
    const list = el('div', 'as-list');
    if (!items.length) list.appendChild(el('div', 'as-empty', 'Nothing here yet.'));
    items.forEach(item => {
      const row = el('div', 'as-row');
      row.appendChild(el('div', 'as-row-title', itemTitle(item, tdef)));
      const edit = el('button', 'as-link', 'Edit'); edit.onclick = () => renderEdit(item);
      const del = el('button', 'as-link as-danger', 'Delete');
      del.onclick = async () => {
        if (!confirm('Delete this item?')) return;
        await api('DELETE', '/' + state.type + '/' + item.id);
        renderList();
      };
      const actions = el('div', 'as-row-actions'); actions.append(edit, del);
      row.appendChild(actions);
      list.appendChild(row);
    });
    main.appendChild(list);
  }

  async function renderEdit(item) {
    const tdef = SCHEMA.content_types[state.type];
    const ischema = tdef.item || {};
    const main = document.getElementById('as-main');
    main.innerHTML = '';
    let currentId = item ? item.id : null;
    const data = item ? Object.assign({}, item) : {};

    const bar = el('div', 'as-listbar');
    const back = el('button', 'as-link', '← Back'); back.onclick = renderList;
    bar.appendChild(back);
    bar.appendChild(el('h2', null, (item ? 'Edit ' : 'New ') + (tdef.label || state.type)));
    main.appendChild(bar);

    const ctx = {
      prefix: PREFIX, itemId: currentId, toast,
      uploadImage: async (field, file) => {
        const fd = new FormData(); fd.append('file', file);
        const r = await fetch(PREFIX + '/' + state.type + '/' + currentId + '/image?field=' + encodeURIComponent(field),
                              { method: 'POST', body: fd });
        if (!r.ok) { toast('Upload failed.', 'err'); return null; }
        return r.json();
      },
      removeImage: async (field, index) => {
        let url = PREFIX + '/' + state.type + '/' + currentId + '/image?field=' + encodeURIComponent(field);
        if (index != null) url += '&index=' + index;
        const r = await fetch(url, { method: 'DELETE' });
        return r.ok ? r.json() : null;
      },
    };

    const form = el('div', 'as-form');
    const editors = {};
    Object.keys(ischema).forEach(name => {
      const ed = window.AdzeFields.make(name, ischema[name], data[name], ctx);
      editors[name] = { ed, def: ischema[name] };
      form.appendChild(ed.el);
    });
    main.appendChild(form);

    const save = el('button', 'as-btn', 'Save');
    save.onclick = async () => {
      const body = {};
      Object.keys(editors).forEach(name => {
        if (editors[name].def.type === 'image') return;  // server owns images
        body[name] = editors[name].ed.value();
      });
      let r;
      if (currentId) r = await api('PUT', '/' + state.type + '/' + currentId, body);
      else r = await api('POST', '/' + state.type, body);
      if (!r) return;
      if (!r.ok) { const e = await r.json().catch(() => ({})); toast(e.error || 'Save failed.', 'err'); return; }
      const saved = await r.json();
      toast('Saved.', 'ok');
      if (!currentId) renderEdit(saved);  // reopen with id so images can be added
    };
    main.appendChild(save);
  }

  async function boot() {
    const r = await fetch(PREFIX + '/schema');
    if (r.status === 401) { renderLogin(); return; }
    SCHEMA = await r.json();
    applyTheme();
    renderApp();
  }

  function init(opts) {
    PREFIX = opts.prefix;
    root = document.getElementById('adze-admin-root');
    boot();
  }

  return { init };
})();
