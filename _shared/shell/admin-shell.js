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

  /* The artist palette contract: six vars, no more. They're set on
   * documentElement (NOT a nested node) so every color-mix() derivation in
   * tokens/colors.css recomputes against them — see the .adze-theme note in
   * design-language/adze/CLAUDE.md for why nesting silently breaks this.
   *
   * `font` was in the old contract and is deliberately gone: a custom face
   * invalidates every line-height in the type scale, and it fails invisibly
   * on that one artist. Type belongs to Adze; colour belongs to the artist. */
  function applyTheme() {
    const th = SCHEMA.theme || {};
    const r = document.documentElement;
    const map = {
      bg: '--adze-artist-bg', surface: '--adze-artist-surface',
      text: '--adze-artist-text', accent: '--adze-artist-accent',
      accentText: '--adze-artist-accent-text', border: '--adze-artist-border',
    };
    Object.keys(map).forEach(k => { if (th[k]) r.style.setProperty(map[k], th[k]); });
  }

  // ── feedback ──────────────────────────────────────────────────────────────
  // Adze design-language components (components/feedback/*.jsx) as plain DOM.

  /* Omit `tone` to inherit currentColor — required inside a filled button,
   * where an --adze-accent spinner would be invisible against the accent. */
  function spinner(size, tone) {
    return el('span', `adze-spinner adze-spinner--${size || 'sm'}` + (tone ? ` adze-spinner--${tone}` : ''));
  }

  /* Skeleton rows sized to the real .as-row geometry, so the list doesn't jump
   * when the data lands. Last line is short — a uniform block reads as a bug. */
  function skeletonRows(n) {
    const wrap = el('div', 'adze-skeleton-rows');
    wrap.setAttribute('role', 'status');
    wrap.setAttribute('aria-label', 'Loading');
    for (let i = 0; i < (n || 4); i++) {
      const row = el('div', 'adze-skeleton-row');
      const text = el('div', 'adze-skeleton-row__text');
      const a = el('div', 'adze-skeleton adze-skeleton--text');
      a.style.width = '48%';
      const b = el('div', 'adze-skeleton adze-skeleton--text');
      b.style.width = i === (n || 4) - 1 ? '62%' : '30%';
      text.append(a, b);
      row.append(text);
      wrap.appendChild(row);
    }
    return wrap;
  }

  function emptyState(title, body, action) {
    const box = el('div', 'adze-empty');
    box.appendChild(el('div', 'adze-empty__icon', '—'));
    box.appendChild(el('div', 'adze-empty__title', title));
    if (body) box.appendChild(el('p', 'adze-empty__body', body));
    if (action) { const a = el('div', 'adze-empty__action'); a.appendChild(action); box.appendChild(a); }
    return box;
  }

  function progressBar(label) {
    const wrap = el('div', 'adze-progress adze-progress--indeterminate');
    wrap.setAttribute('role', 'progressbar');
    wrap.setAttribute('aria-label', label || 'Working');
    if (label) {
      const head = el('div', 'adze-progress__head');
      head.appendChild(el('span', 'adze-label', label));
      wrap.appendChild(head);
    }
    const track = el('div', 'adze-progress__track');
    track.appendChild(el('div', 'adze-progress__bar'));
    wrap.appendChild(track);
    return wrap;
  }

  /* Wraps an async click so the button can't fire twice. The old code set
   * `disabled` only after its await resolved, which left a window where a
   * second click queued a second publish. is-busy sets pointer-events:none
   * synchronously, before the await. */
  async function withBusy(btn, fn) {
    if (btn.classList.contains('is-busy')) return;
    const label = btn.textContent;
    btn.classList.add('is-busy');
    btn.textContent = '';
    btn.append(spinner('sm'), document.createTextNode(label));
    try {
      return await fn();
    } finally {
      btn.classList.remove('is-busy');
      btn.textContent = label;
    }
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
    btn.onclick = () => withBusy(btn, submit);
    pw.addEventListener('keydown', e => { if (e.key === 'Enter') withBusy(btn, submit); });
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
    const acts = el('div', 'as-row-actions');
    const account = el('button', 'as-link', 'Account');
    account.onclick = renderAccountModal;
    const logout = el('button', 'as-link', 'Log out');
    logout.onclick = async () => { await api('POST', '/logout'); renderLogin(); };
    acts.append(account, logout);
    header.appendChild(acts);
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
    /* Publish rebuilds and recompiles the whole site — the one action here
     * that can take several seconds. It gets a real progress bar, not just a
     * disabled button, because a frozen screen is what made artists click
     * Publish twice. */
    pub.onclick = () => withBusy(pub, async () => {
      const bar = progressBar('Publishing');
      foot.insertBefore(bar, foot.firstChild);
      try {
        const r = await api('POST', '/compile');
        if (r && r.ok) toast('Published to the live site.', 'ok');
        else toast('Publish failed — your changes are still saved.', 'err');
      } finally {
        bar.remove();
      }
    });
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

    /* Skeleton while the fetch is in flight. Previously this was a blank gap
     * of indeterminate length, which reads as a broken page on a slow phone. */
    const placeholder = skeletonRows(4);
    main.appendChild(placeholder);
    const r = await api('GET', '/' + state.type);
    placeholder.remove();
    if (!r) return;
    if (!r.ok) {
      const fail = emptyState('Could not load ' + (tdef.label || state.type),
                              'Check your connection and try again.');
      fail.classList.add('adze-empty--error');
      main.appendChild(fail);
      return;
    }
    const items = await r.json();
    const list = el('div', 'as-list');
    if (!items.length) {
      const addBtn = el('button', 'as-btn as-btn-sm', '+ Add the first one');
      addBtn.onclick = () => renderEdit(null);
      list.appendChild(emptyState('Nothing here yet',
        'Anything you add will appear on your site the next time you publish.', addBtn));
    }
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

    const actions = el('div', 'as-actions');
    const save = el('button', 'as-btn', 'Save');
    save.onclick = () => withBusy(save, async () => {
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
    });
    actions.appendChild(save);
    main.appendChild(actions);
  }

  // ── account / change password ───────────────────────────────────────────────
  function renderAccountModal() {
    const backdrop = el('div', 'as-modal-backdrop');
    backdrop.onclick = e => { if (e.target === backdrop) backdrop.remove(); };
    const box = el('div', 'as-modal');
    box.appendChild(el('h2', null, 'Change password'));
    const cur = el('input', 'af-input'); cur.type = 'password'; cur.placeholder = 'Current password';
    const nw = el('input', 'af-input'); nw.type = 'password'; nw.placeholder = 'New password (6+ characters)';
    const conf = el('input', 'af-input'); conf.type = 'password'; conf.placeholder = 'Confirm new password';
    [cur, nw, conf].forEach(i => i.style.marginBottom = '12px');
    const err = el('div', 'as-err');
    const actions = el('div', 'as-actions');
    const cancel = el('button', 'as-link', 'Cancel'); cancel.onclick = () => backdrop.remove();
    const submit = el('button', 'as-btn', 'Update password');
    submit.onclick = async () => {
      err.textContent = '';
      if (nw.value.length < 6) { err.textContent = 'New password must be at least 6 characters.'; return; }
      if (nw.value !== conf.value) { err.textContent = 'The two passwords do not match.'; return; }
      submit.disabled = true;
      const r = await api('POST', '/password', { current: cur.value, new: nw.value });
      submit.disabled = false;
      if (r && r.ok) { backdrop.remove(); toast('Password updated.', 'ok'); }
      else { const e = r ? await r.json().catch(() => ({})) : {}; err.textContent = (e && e.error) || 'Could not update password.'; }
    };
    actions.append(submit, cancel);
    box.append(cur, nw, conf, err, actions);
    backdrop.appendChild(box);
    root.appendChild(backdrop);
    cur.focus();
  }

  async function boot() {
    /* The schema fetch decides the whole UI, so until it lands there is
     * nothing to draw. A delayed spinner (not a skeleton) is right here: on a
     * fast connection it never appears at all, which is the point. */
    const wait = el('div', 'adze-empty');
    wait.appendChild(spinner('lg', 'muted'));
    root.appendChild(wait);
    let r;
    try {
      r = await fetch(PREFIX + '/schema');
    } catch (e) {
      root.innerHTML = '';
      const fail = emptyState('Can’t reach your site',
                              'You appear to be offline. Nothing has been lost — try again in a moment.');
      fail.classList.add('adze-empty--error');
      root.appendChild(fail);
      return;
    } finally {
      wait.remove();
    }
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
