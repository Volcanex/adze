/* admin-shell.js — the schema-driven artist admin SPA.
 *
 * One UI for every artist. Fetches {prefix}/schema, renders a nav of the
 * artist's content types, list/edit views built from the field-editor registry,
 * a Publish button, and the "Advanced editing" handoff to the control panel.
 * No per-artist markup — the schema is the only thing that differs.
 *
 * LAYOUT IS DERIVED, NOT CONFIGURED. What a field IS decides where it goes:
 * the identity field leads, pictures come next, the short scalars share a row,
 * prose and tags close. A type that holds pictures lists as a grid of cards;
 * one that doesn't lists as text rows. Nothing per-artist, so a new site is
 * laid out correctly the moment its schema exists. The two escape hatches —
 * a field's "width": "full" and a type's "list": "grid" | "rows" — exist for
 * the case the derivation reads wrong; there are deliberately no others.
 */
window.AdminShell = (function () {
  let PREFIX, SCHEMA, root;
  const state = { type: null };

  /* The Text section shares the nav with the content types, so it needs a key
   * in the same space. Content-type keys are slugs used directly as URL
   * segments, so a leading '@' can't collide with one. */
  const COPY = '@copy';

  /* Field types the SERVER owns. Their upload/delete routes have already
   * written by the time they return, so their value must never ride along in a
   * save body — a stale array from a form opened before an upload would revert
   * it. One list rather than a `=== 'image'` test at each site, because the two
   * sites drifting apart is exactly how a file field would end up saveable. */
  const SERVER_OWNED = ['image', 'file'];
  const serverOwned = def => SERVER_OWNED.indexOf((def || {}).type) !== -1;

  /* The tags already in use for the current type, so the tag editor can offer
   * them instead of asking the artist to remember and retype them. Free text
   * alone means one typo ("phylosophy") silently becomes a second tag and
   * quietly splits a filter row in two — the page can't tell the difference.
   *
   * Cached from whatever the list view last fetched rather than requested
   * separately: the list is always loaded before an item can be opened, so the
   * data is already here, and going Back refetches it, which is what keeps a
   * tag added a minute ago in the list.
   *
   * Scoped to ONE content type on purpose. Vocabularies are per-page — the
   * filter row on /video is built from video tags — so offering photo tags
   * while editing a video would suggest words that can never group anything. */
  let tagCache = { type: null, items: [] };
  function rememberItems(type, items) {
    tagCache = { type, items: Array.isArray(items) ? items : [] };
  }
  function knownTags(field) {
    if (tagCache.type !== state.type) return [];
    const seen = new Set();
    tagCache.items.forEach(it => {
      const v = it && it[field];
      if (Array.isArray(v)) v.forEach(t => { if (typeof t === 'string' && t.trim()) seen.add(t.trim()); });
    });
    return [...seen].sort((a, b) => a.localeCompare(b));
  }

  /* A 401 here is NOT renderLogin(). renderLogin() opens with
   * `root.innerHTML = ''`, and by the time a 401 can arrive the artist has an
   * item form open with unsaved words in it — so the old behaviour deleted the
   * work while autosave's status line promised it was still there. Sign in over
   * the page instead and leave the fields standing; the pending write is still
   * dirty and goes on the next keystroke or flush.
   *
   * `boot()` calls its own renderLogin directly — at boot there is nothing on
   * screen to preserve, and a login overlaid on a blank page is just a login
   * screen with extra steps. */
  async function api(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    const r = await fetch(PREFIX + path, opts);
    if (r.status === 401) { sessionExpired(); return null; }
    return r;
  }

  function sessionExpired() {
    window.AdzeUI.reauth({ prefix: PREFIX, host: root });
  }

  /* DOM primitives live in adze-ui.js so this shell and the artist landing
   * page share one implementation — see that file's header for why. The two
   * wrappers below keep every call site in this file unchanged: `toast` binds
   * our themed root, `applyTheme` binds the fetched schema. */
  const { el, spinner, skeletonRows, emptyState, progressBar, withBusy } = window.AdzeUI;
  const toast = (msg, kind) => window.AdzeUI.toast(msg, kind, root);
  const applyTheme = () => window.AdzeUI.applyTheme(SCHEMA.theme);

  // ── autosave ────────────────────────────────────────────────────────────────

  /* THERE IS NO SAVE BUTTON IN THIS ADMIN, anywhere, and adding one back is a
   * regression. Typing is kept on its own; the single button on screen is
   * Publish, and it means exactly one thing — put this on the live site.
   *
   * Why: "Save" and "Publish changes" both read as "keep my work", and the one
   * that didn't was the only one always visible. That ambiguity cost a real
   * artist a page of rewrites (see THE INCIDENT below for the incident this
   * shell was already patched around). Deleting the verb deletes the choice.
   * The Save/Publish split was never the artist's problem to hold — it is the
   * difference between content.json and a compiled site, which is ours.
   *
   * `autosave(scope, opts)` writes 800ms after the last keystroke and
   * immediately on leaving a field, whichever lands first. It returns a handle
   * whose `.el` is a status line for the caller to place next to the fields,
   * and whose `.flush()` Publish awaits before compiling.
   *
   * `opts.commit` must resolve truthy only when the server took the write, and
   * must itself re-baseline (so `isDirty` goes quiet). `opts.isDirty` is asked
   * before every write — an unchanged form must never generate traffic, or a
   * focusout on a field nobody touched would PUT on every tab. */
  const SAVE_DEBOUNCE_MS = 800;

  function autosave(scope, opts) {
    const status = el('div', 'as-saved');
    let timer = null;
    let running = null;   // in-flight commit; two must never overlap
    let again = false;    // a change landed while a commit was in flight
    let failed = false;

    function show(text, kind) {
      status.textContent = text || '';
      status.className = 'as-saved' + (kind ? ' as-saved--' + kind : '');
    }

    function stamp() {
      const d = new Date();
      const p = n => String(n).padStart(2, '0');
      return p(d.getHours()) + ':' + p(d.getMinutes());
    }

    function run() {
      /* Coalesce rather than queue: whatever the fields hold when the current
       * write lands is what the next one sends, so a fast typist gets two
       * requests, not one per keystroke. */
      if (running) { again = true; return running; }
      if (!opts.isDirty()) return Promise.resolve(true);
      show('Saving…', 'busy');
      running = (async () => {
        let ok = false;
        try { ok = await opts.commit(); } catch (e) { ok = false; }
        running = null;
        failed = !ok;
        if (ok) show('Saved ' + stamp(), 'ok');
        /* Never "lost", never a modal. The words are still in the box in front
         * of them, and the next keystroke retries — so the honest thing to say
         * is that this copy is fine and the server hasn't got it yet. */
        else show('Not saved yet — your words are still here, and this keeps trying.', 'err');
        if (again) { again = false; return run(); }
        return ok;
      })();
      return running;
    }

    function schedule() {
      clearTimeout(timer);
      timer = setTimeout(run, SAVE_DEBOUNCE_MS);
    }

    function flush() {
      clearTimeout(timer);
      return run();
    }

    scope.addEventListener('input', schedule);
    /* focusout, not blur: blur doesn't bubble, and every editor here is a
     * descendant of the scope — contenteditables included. Leaving a field
     * commits it without waiting the debounce out. */
    scope.addEventListener('focusout', flush);

    return { el: status, flush, isDirty: opts.isDirty, failed: () => failed };
  }

  /* Every mounted autosave. Publish flushes all of them; the unload guard asks
   * whether any still holds something the server hasn't taken. Registered on
   * mount and dropped on view change, because a handle whose DOM is gone would
   * keep answering for fields that no longer exist. */
  let live = [];
  const mountSave = (handle) => { live.push(handle); return handle; };
  const clearSaves = () => { live = []; };

  /* Emptying the main pane retires every autosave mounted inside it. A handle
   * whose fields are detached would go on voting in `anyUnsaved()` and block
   * Publish over edits that no longer exist anywhere — so the two belong in one
   * helper rather than as a pairing four call sites have to remember. Flushing
   * is deliberately NOT here: by the time the pane is being emptied it is too
   * late, which is what `leaveView()` is for. */
  function resetMain() {
    clearSaves();
    const main = document.getElementById('as-main');
    main.innerHTML = '';
    return main;
  }
  const flushAll = () => Promise.all(live.map(h => h.flush()));
  const anyUnsaved = () => live.some(h => h.isDirty() || h.failed());

  /* Does the compiled site match what has been saved? Every successful write
   * makes this false, a successful publish makes it true, and the server seeds
   * it on load. Kept here rather than inside renderApp because the commits
   * that invalidate it live in the view functions. */
  let liveNote = null;
  function setLive(isLive) {
    if (!liveNote) return;
    liveNote.textContent = isLive
      ? 'The live site is up to date.'
      : 'Saved — but not on the live site until you publish.';
    liveNote.className = 'as-livenote' + (isLive ? '' : ' as-livenote--pending');
  }

  // ── login ─────────────────────────────────────────────────────────────────
  function renderLogin() {
    root.innerHTML = '';
    const box = el('div', 'as-login');
    box.appendChild(el('h1', null, 'Admin'));
    /* The domain already identifies the artist, so the name is optional --
     * it's here for the artist who owns more than one site, and because
     * "your name and your password" is what a login is supposed to look like.
     * Leave it blank and the password alone still works. */
    const who = el('input', 'af-input');
    who.type = 'text';
    who.placeholder = 'Your name or email (optional)';
    who.autocomplete = 'username';
    const pwf = window.AdzeUI.passwordField('Password');
    const pw = pwf.input;
    const err = el('div', 'as-err');
    const btn = el('button', 'as-btn', 'Enter');
    async function submit() {
      const r = await fetch(PREFIX + '/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: who.value.trim(), password: pw.value.trim() }),
      });
      if (r.ok) { boot(); return; }
      if (r.status === 429) {
        err.textContent = 'Too many attempts just now. Wait a minute and try again.';
      } else if (r.status >= 500) {
        err.textContent = 'Something broke at our end — not your password.';
      } else {
        err.textContent = who.value.trim()
          ? 'That name and password don’t match.' : 'Wrong password.';
      }
    }
    btn.onclick = () => withBusy(btn, submit);
    [who, pw].forEach(i => i.addEventListener(
      'keydown', e => { if (e.key === 'Enter') withBusy(btn, submit); }));
    box.append(who, pwf.wrap, btn, err);
    root.appendChild(box);
    pw.focus();
  }

  // ── motion ──────────────────────────────────────────────────────────────────

  /* The shell rebuilds #as-main wholesale on every navigation, which is exactly
   * the shape startViewTransition() wants: mutate, and the browser tweens the
   * before against the after itself.
   *
   * The callback deliberately does NOT return the render's promise. Returning
   * it would hold the captured frame — a visibly frozen page — for the whole
   * list fetch; letting it settle synchronously means we transition into the
   * skeleton and the items land behind it as they always did. */
  function swapView(run) {
    if (!document.startViewTransition) { run(); vtClear(); return; }
    document.startViewTransition(() => { run(); }).finished.then(vtClear, vtClear);
  }

  /* A view-transition-name has to be unique in the document while a transition
   * runs, and a leftover one breaks the NEXT transition rather than this one —
   * silently, and only sometimes. Every name set here is registered so it can
   * be cleared the moment the transition settles. */
  let vtNamed = [];
  function vtName(node, name) {
    if (!node || !document.startViewTransition) return;
    node.style.viewTransitionName = name;
    vtNamed.push(node);
  }
  function vtClear() {
    vtNamed.forEach(n => { n.style.viewTransitionName = ''; });
    vtNamed = [];
  }
  const itemVt = id => 'as-item-' + String(id).replace(/[^A-Za-z0-9_-]/g, '-');

  /* Waits for a leaving animation without hard-coding its length. Reduced
   * motion collapses every duration to 1ms, and a node the CSS doesn't animate
   * fires no event at all — so the timeout is a ceiling, not the schedule. A
   * bare setTimeout(300) would be a 300ms stall for exactly the people who
   * asked for less motion. */
  function afterExit(node, done) {
    let timer = null, fired = false;
    const go = () => {
      if (fired) return;
      fired = true;
      clearTimeout(timer);
      node.removeEventListener('animationend', go);
      node.removeEventListener('transitionend', go);
      done();
    };
    node.addEventListener('animationend', go);
    node.addEventListener('transitionend', go);
    timer = setTimeout(go, 400);
  }

  // ── layout derivation ───────────────────────────────────────────────────────

  /* field-editors.js owns what a field type MEANS, so it owns role() too — this
   * shell only arranges what it's told. An older cached copy of that file has
   * no role(); then every field reads as 'short' and both views fall back to
   * what this shell rendered before roles existed. */
  function hasRoles() {
    return !!(window.AdzeFields && typeof window.AdzeFields.role === 'function');
  }
  function roleOf(def) {
    if (!hasRoles()) return 'short';
    try { return window.AdzeFields.role(def) || 'short'; } catch (e) { return 'short'; }
  }

  const ROLE_ORDER = ['identity', 'media', 'short', 'long', 'tags'];

  /* No slug_source means there is nothing to name a second item after: the type
   * IS one item. page.mode is NOT this signal — three of mariaslaughter's four
   * types are mode 'single' and are ordinary collections. */
  function isSingleton(tdef) {
    const ischema = tdef.item || {};
    return !Object.keys(ischema).some(k => (ischema[k] || {}).slug_source);
  }

  function mediaFields(tdef) {
    const ischema = tdef.item || {};
    return Object.keys(ischema).filter(k => roleOf(ischema[k]) === 'media');
  }

  function useGrid(tdef) {
    if (tdef.list === 'grid') return true;
    if (tdef.list === 'rows') return false;
    return mediaFields(tdef).length > 0;
  }

  /* Paths are stored relative to the artist's assets/ dir, and the admin runs
   * on the artist's own domain, so /assets/<rel> resolves via nginx. Same rule
   * as field-editors.js — if one moves, both move. */
  function assetUrl(rel) {
    return rel.startsWith('assets/') || rel.startsWith('/')
      ? '/' + rel.replace(/^\//, '') : '/assets/' + rel;
  }

  function cardImage(item, tdef) {
    const ischema = tdef.item || {};
    const media = mediaFields(tdef);
    /* The type check is the fallback for a cached field-editors.js with no
     * role() under a type that asked for a grid explicitly. */
    const pool = media.length ? media
      : Object.keys(ischema).filter(k => (ischema[k] || {}).type === 'image');
    for (const name of pool) {
      const value = item[name];
      const entries = Array.isArray(value) ? value : [value];
      for (const entry of entries) {
        if (!entry) continue;
        /* A `file` field is media too, but most of what it holds is not a
         * picture. Entries it stored carry `kind`; an image field's never do,
         * so an absent `kind` still means "image" and old content is unaffected.
         * Without this the card would set an .mp4 path as an <img> src. */
        if (entry.kind && entry.kind !== 'image') continue;
        /* `card` is the thumbnail tier; the rest are the older shapes still
         * sitting in existing content.html files — an object, or a bare path. */
        const rel = entry.card || entry.src || entry.full || entry;
        if (typeof rel === 'string' && rel) return assetUrl(rel);
      }
    }
    return null;
  }

  /* One quiet line under the title — the first short field the item actually
   * fills in, which on Rose's works is the year. A boolean is skipped: "false"
   * under a title is noise, not information. */
  function cardMeta(item, tdef) {
    const ischema = tdef.item || {};
    for (const name of Object.keys(ischema)) {
      if (roleOf(ischema[name]) !== 'short') continue;
      const v = item[name];
      if (v == null || v === '' || typeof v === 'boolean' || Array.isArray(v)) continue;
      return String(v);
    }
    return null;
  }

  // ── app frame ───────────────────────────────────────────────────────────────
  function typeKeys() { return Object.keys(SCHEMA.content_types || {}); }

  function sectionKeys() {
    const keys = typeKeys();
    if (SCHEMA.copy) keys.push(COPY);
    return keys;
  }

  function sectionLabel(k) {
    if (k === COPY) return 'Text';
    return (SCHEMA.content_types[k] || {}).label || k;
  }

  /* Matched on the key, not the label: two sections can share a label, and
   * Text has no content type behind it to compare against. */
  function markActiveTab() {
    document.querySelectorAll('.as-tab').forEach(t =>
      t.classList.toggle('active', t.dataset.key === state.type));
  }

  /* Every route out of an editing view goes through here. The boxes are
   * rebuilt from the server on return, so anything the server hasn't taken is
   * simply gone — which used to be a confirm() the artist had to read and
   * answer every time they changed tabs. Now leaving a view commits it, the
   * same as leaving a field, and the prompt is reserved for the one case that
   * still deserves it: the write was attempted and did not land. */
  async function leaveView() {
    await flushAll();
    if (anyUnsaved()
        && !confirm('Some of your writing hasn’t reached the server yet. '
                    + 'Leaving now loses it. Leave anyway?')) return false;
    clearSaves();
    return true;
  }

  function openSection() {
    markActiveTab();
    if (state.type === COPY) return renderCopy();
    const tdef = SCHEMA.content_types[state.type];
    if (!tdef) return;
    return isSingleton(tdef) ? renderSingleton() : renderList();
  }

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

    const sections = sectionKeys();
    if (!sections.length) {
      root.appendChild(el('p', 'as-empty', 'No content types configured for this site yet.'));
    } else {
      /* A single section gets no nav. One tab can't switch anything, and it
       * duplicated the list heading directly beneath it — two identical words
       * and 48px of chrome saying nothing. The count is of SECTIONS, not
       * content types: one type plus Text is two places to be. */
      if (sections.length > 1) {
        const nav = el('div', 'as-nav');
        sections.forEach(k => {
          const b = el('button', 'as-tab', sectionLabel(k));
          b.dataset.key = k;
          b.onclick = async () => {
            if (k !== state.type && !(await leaveView())) return;
            state.type = k; openSection();
          };
          nav.appendChild(b);
        });
        root.appendChild(nav);
      }
      if (sections.indexOf(state.type) < 0) state.type = sections[0];
    }

    /* The enter animation belongs to the app arriving, not to every list/edit
     * swap. On .as-main itself it re-fired whenever the panel was rebuilt and
     * the whole screen flashed on save; --enter is added here, once. */
    const main = el('div', 'as-main as-main--enter'); main.id = 'as-main'; root.appendChild(main);

    const foot = el('div', 'as-foot');
    const pub = el('button', 'as-btn', 'Publish changes');
    /* Publish rebuilds and recompiles the whole site — the one action here
     * that can take several seconds. It gets a real progress bar, not just a
     * disabled button, because a frozen screen is what made artists click
     * Publish twice. */
    pub.onclick = () => withBusy(pub, async () => {
      /* Everything in flight goes up FIRST. Publishing without it compiled the
       * site and then silently discarded the artist's edits — the one failure
       * mode this whole surface must not have. If a write fails we do not
       * publish, so the words are never lost behind a success message.
       *
       * Autosave makes this rarer, not unnecessary: the artist can reach this
       * button inside the debounce window, and that is the likeliest moment
       * for them to press it — they just finished typing. */
      await flushAll();
      if (anyUnsaved()) {
        toast('Your writing hasn’t reached the server yet, so nothing was '
              + 'published. It’s still on screen — give it a moment and try again.', 'err');
        return;
      }
      const bar = progressBar('Publishing');
      foot.insertBefore(bar, foot.firstChild);
      try {
        const r = await api('POST', '/compile');
        if (r && r.ok) { toast('Published to the live site.', 'ok'); setLive(true); }
        else toast('Publish failed — your changes are still saved.', 'err');
      } finally {
        bar.remove();
      }
    });
    foot.appendChild(pub);
    /* The footer says whether the live site matches what is in these boxes.
     * With no Save button there is no longer a moment that means "shipped", so
     * something has to hold that state where the artist can see it — otherwise
     * autosave quietly reads as published and the button stops getting pressed.
     * Seeded from the server (`SCHEMA.unpublished`) so it survives a reload. */
    liveNote = el('div', 'as-livenote');
    foot.appendChild(liveNote);
    setLive(!SCHEMA.unpublished);
    if (SCHEMA.handoff) {
      const link = el('a', 'as-advanced', 'Advanced editing →');
      link.href = SCHEMA.handoff;
      foot.appendChild(link);
    }
    root.appendChild(foot);

    if (sections.length) openSection();
  }

  function itemTitle(item, tdef) {
    const ischema = tdef.item || {};
    for (const k in ischema) if (ischema[k].slug_source && item[k]) return item[k];
    const named = item.title || item.name || item.label;
    if (named) return named;
    /* A draft has an id but nothing the artist would recognise in it, so the
     * id is worse than no label at all. */
    if (item._draft) return 'Unsaved draft';
    return item.id;
  }

  // ── list ────────────────────────────────────────────────────────────────────

  function itemActions(item, node, actionsClass, leavingClass) {
    const actions = el('div', actionsClass);
    const edit = el('button', 'as-link', 'Edit');
    edit.onclick = () => openItem(node, item);
    const del = el('button', 'as-link as-danger', 'Delete');
    del.onclick = () => {
      /* confirm() blocks, so nothing can click through it — withBusy goes round
       * the request, not round the question. Inside it, the button spins while
       * the dialog is still asking, which reads as "already deleting". */
      if (!confirm('Delete this item?')) return;
      withBusy(del, async () => {
        /* The exit starts with the request, not after it: waiting for the round
         * trip first left a dead half-second where the click did nothing. */
        node.classList.add(leavingClass);
        const gone = new Promise(res => afterExit(node, res));
        await api('DELETE', '/' + state.type + '/' + item.id);
        await gone;
        openSection();
      });
    };
    actions.append(edit, del);
    return actions;
  }

  function rowFor(item, tdef) {
    const row = el('div', 'as-row' + (item._draft ? ' as-draft' : ''));
    row.appendChild(el('div', 'as-row-title', itemTitle(item, tdef)));
    row.appendChild(itemActions(item, row, 'as-row-actions', 'as-row--leaving'));
    return row;
  }

  function cardFor(item, tdef) {
    const card = el('div', 'as-card-item' + (item._draft ? ' as-draft' : ''));
    const media = el('div', 'as-card-item__media');
    const src = cardImage(item, tdef);
    if (src) {
      const img = el('img');
      img.src = src;
      img.alt = '';                 // the title sits directly beneath it
      /* Rose has 32 works: without these, opening the list is 32 full-size
       * decodes on the main thread and the page is unusable while they run. */
      img.loading = 'lazy';
      img.decoding = 'async';
      media.appendChild(img);
    }
    /* An item with no picture yet still gets the empty media box — the CSS
     * gives it a placeholder surface, and a card missing its top half reads as
     * a different kind of thing rather than as an empty one. */
    card.appendChild(media);
    card.appendChild(el('div', 'as-card-item__title', itemTitle(item, tdef)));
    const meta = cardMeta(item, tdef);
    if (meta) card.appendChild(el('div', 'as-card-item__meta', meta));
    card.appendChild(itemActions(item, card, 'as-card-item__actions', 'as-card-item--leaving'));
    return card;
  }

  async function renderList() {
    const main = resetMain();
    const tdef = SCHEMA.content_types[state.type];
    const bar = el('div', 'as-listbar');
    bar.appendChild(el('h2', null, tdef.label || state.type));
    const add = el('button', 'as-btn as-btn-sm', '+ Add');
    add.onclick = () => withBusy(add, openNew);
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
    rememberItems(state.type, items);
    if (!items.length) {
      const addBtn = el('button', 'as-btn as-btn-sm', '+ Add the first one');
      addBtn.onclick = () => withBusy(addBtn, openNew);
      main.appendChild(emptyState('Nothing here yet',
        'Anything you add will appear on your site the next time you publish.', addBtn));
      return;
    }
    const grid = useGrid(tdef);
    const list = el('div', (grid ? 'as-grid' : 'as-list') + ' as-stagger');
    items.forEach((item, i) => {
      const node = grid ? cardFor(item, tdef) : rowFor(item, tdef);
      /* Capped at 8. Ungated, Rose's 32 works ripple in for two full seconds,
       * which is a stagger that has stopped being an entrance and become a
       * wait. Past the eighth the eye has read the pattern anyway. */
      node.style.setProperty('--as-i', String(Math.min(i, 8)));
      list.appendChild(node);
    });
    main.appendChild(list);
  }

  /* A singleton has no list to sit in — showing one row for the artist to click
   * through is a question with one answer. Its form IS the section. */
  async function renderSingleton() {
    const main = resetMain();
    const placeholder = skeletonRows(3);
    main.appendChild(placeholder);
    const r = await api('GET', '/' + state.type);
    placeholder.remove();
    if (!r) return;
    if (!r.ok) {
      const tdef = SCHEMA.content_types[state.type];
      const fail = emptyState('Could not load ' + (tdef.label || state.type),
                              'Check your connection and try again.');
      fail.classList.add('adze-empty--error');
      main.appendChild(fail);
      return;
    }
    const items = await r.json();
    rememberItems(state.type, items);
    if (items.length) { renderEdit(items[0], { singleton: true }); return; }
    /* Nothing there yet, so make the one item rather than showing an empty
     * state. The draft is returned by the list route too, so a second visit
     * reopens this one instead of piling up more. */
    const d = await api('POST', '/' + state.type + '/draft');
    if (d && d.ok) {
      const made = await d.json().catch(() => null);
      if (made && made.id) { renderEdit(made, { singleton: true }); return; }
    }
    renderEdit(null, { singleton: true });
  }

  // ── edit ────────────────────────────────────────────────────────────────────

  function openItem(node, item) {
    vtClear();
    vtName(node, itemVt(item.id));
    swapView(() => renderEdit(item));
  }

  /* Every form opens on a real item now, so an image upload works from the
   * first second. The old flow made the artist save a blank record, notice the
   * "save this first" note, and come back for the pictures. An abandoned draft
   * is the server's problem — it sweeps them after 24h. */
  async function openNew() {
    const r = await api('POST', '/' + state.type + '/draft');
    if (!r) return;
    let made = null;
    if (r.ok) made = await r.json().catch(() => null);
    /* No draft route (or it failed): fall back to the old create-on-save form
     * rather than dead-ending the artist on a button that does nothing. */
    swapView(() => renderEdit(made && made.id ? made : null));
  }

  function buildForm(ischema, data, ctx) {
    const form = el('div', 'as-form');
    const editors = {};
    const make = name => {
      const def = ischema[name] || {};
      const ed = window.AdzeFields.make(name, def, data[name], ctx);
      editors[name] = { ed, def };
      if (def.width === 'full') ed.el.classList.add('af-field--full');
      return ed.el;
    };
    const names = Object.keys(ischema);

    if (!hasRoles()) {
      names.forEach(n => form.appendChild(make(n)));
      return { form, editors };
    }

    const byRole = {};
    ROLE_ORDER.forEach(r => { byRole[r] = []; });
    names.forEach(n => { (byRole[roleOf(ischema[n])] || byRole.short).push(n); });

    ROLE_ORDER.forEach(role => {
      const group = byRole[role];
      if (!group.length) return;
      if (role !== 'short') { group.forEach(n => form.appendChild(make(n))); return; }
      /* The short scalars are the only fields that share a line: year, medium
       * and dimensions are three words each, and stacked full-width they ran
       * the form four screens long. One wrapper, because the packing itself is
       * a grid in the CSS — this file decides what belongs together, not how
       * wide it ends up.
       *
       * A width:"full" short field is moved to the END of its group rather than
       * holding its position in schema order. That is deliberate: keeping the
       * position would mean breaking the group in two around it, and two grids
       * of two fields don't line up with each other — which is the entire point
       * of packing them. One escape hatch, one wrapper. */
      const packed = el('div', 'as-fieldgroup');
      group.forEach(n => { if ((ischema[n] || {}).width !== 'full') packed.appendChild(make(n)); });
      if (packed.childElementCount) form.appendChild(packed);
      group.forEach(n => { if ((ischema[n] || {}).width === 'full') form.appendChild(make(n)); });
    });
    return { form, editors };
  }

  function renderEdit(item, opts) {
    opts = opts || {};
    const tdef = SCHEMA.content_types[state.type];
    const ischema = tdef.item || {};
    const main = resetMain();
    let currentId = item ? item.id : null;
    /* A draft exists on the server but has never been through a save, so
     * walking away from it would leave a blank row in the artist's list.
     * Cleared on the first successful save — after that it's an ordinary item. */
    let unsaved = !!(item && item._draft);
    const data = item ? Object.assign({}, item) : {};

    const bar = el('div', 'as-listbar as-form-head');
    if (!opts.singleton) {
      const back = el('button', 'as-link', '← Back');
      back.onclick = () => withBusy(back, async () => {
        /* Leaving commits, so going Back keeps the artist's work rather than
         * asking them to. */
        if (!(await leaveView())) return;
        /* A draft nobody typed into would otherwise sit in their list as a
         * blank row they didn't ask for. By this line autosave has already
         * promoted any draft they DID type into, so `unsaved` still being
         * true means genuinely untouched — which is why this can ask plainly
         * instead of warning them about losing something. */
        if (unsaved && confirm('You haven’t written anything here. Remove it?')) {
          await api('DELETE', '/' + state.type + '/' + currentId);
        }
        swapView(openSection);
      });
      bar.appendChild(back);
    }
    const label = tdef.label || state.type;
    const heading = el('h2', null,
      opts.singleton ? label : ((unsaved || !currentId) ? 'New ' : 'Edit ') + label);
    bar.appendChild(heading);
    /* The row the artist clicked and this heading carry the same transition
     * name, which is what makes the row grow into the form rather than the two
     * views cross-fading past each other. */
    if (currentId) vtName(bar, itemVt(currentId));
    main.appendChild(bar);

    const ctx = {
      prefix: PREFIX, toast,
      /* A getter, not a captured value. The image editor reads ctx.itemId at
       * BUILD time to decide whether uploads are live, so a form built before
       * its id existed would latch disabled forever. Opening on a draft means
       * the id is always there first — this just makes the stale read
       * impossible rather than merely unlikely. */
      get itemId() { return currentId; },
      uploadImage: async (field, file) => {
        const fd = new FormData(); fd.append('file', file);
        const r = await fetch(PREFIX + '/' + state.type + '/' + currentId + '/image?field=' + encodeURIComponent(field),
                              { method: 'POST', body: fd });
        /* Null, and no toast: the caller uploads one file per request and names
         * the one that failed. A generic message here would be a second toast
         * saying less. */
        if (!r.ok) return null;
        return r.json();
      },
      removeImage: async (field, index) => {
        let url = PREFIX + '/' + state.type + '/' + currentId + '/image?field=' + encodeURIComponent(field);
        if (index != null) url += '&index=' + index;
        const r = await fetch(url, { method: 'DELETE' });
        return r.ok ? r.json() : null;
      },
      /* The `file` field's pair of the two above. A separate route because the
       * server stores the two kinds differently (tiers and an aspect ratio for
       * an image, the file as-is for everything else) — see content_admin.py. */
      uploadFile: async (field, file) => {
        const fd = new FormData(); fd.append('file', file);
        const r = await fetch(PREFIX + '/' + state.type + '/' + currentId + '/file?field=' + encodeURIComponent(field),
                              { method: 'POST', body: fd });
        if (!r.ok) return null;
        return r.json();
      },
      knownTags,
      removeFile: async (field, index) => {
        let url = PREFIX + '/' + state.type + '/' + currentId + '/file?field=' + encodeURIComponent(field);
        if (index != null) url += '&index=' + index;
        const r = await fetch(url, { method: 'DELETE' });
        return r.ok ? r.json() : null;
      },
    };

    const built = buildForm(ischema, data, ctx);
    const editors = built.editors;

    /* A singleton whose type declares a page renders straight onto that page,
     * so it gets the same live preview the copy editor has — mariaslaughter's
     * "Home text" is the case this exists for. Her four fields land on /home/,
     * marked in her TEMPLATE with data-field (templates are hand-authored and
     * survive; the pages they generate do not).
     *
     * Deliberately singletons only. A per-item type has no single page to show
     * until the item is saved and published, and putting an iframe beside every
     * item form in the system is a much larger change than the one asked for. */
    const previewPage = opts.singleton && ((tdef.page || {}).parent || null);
    let formPane = null, formPreview = null;
    if (previewPage) {
      const split = el('div', 'as-copy-split');
      formPane = el('div', 'as-copy-pane');
      formPane.appendChild(built.form);
      split.appendChild(formPane);
      main.appendChild(split);

      const recs = Object.keys(editors)
        .filter(n => !serverOwned(editors[n].def))
        .map(n => ({ page: previewPage, id: n, rich: false,
                     ed: editors[n].ed, el: editors[n].ed.el, flag: null }));
      formPreview = copyPreview(recs, [previewPage], (pg, id) => {
        const r = recs.find(x => x.id === id);
        if (!r) return;
        const field = r.el.querySelector('textarea, input, select, .ql-editor');
        if (field) field.focus();
        r.el.scrollIntoView({ block: 'center' });
      });
      split.appendChild(formPreview.pane);
      if (recs.length) formPreview.show(recs[0]);
      /* One delegated listener rather than per-editor wiring: a contenteditable
       * fires `input` too, so this covers every field type the registry has. */
      built.form.addEventListener('input', () => recs.forEach(formPreview.push));
    } else {
      main.appendChild(built.form);
    }

    /* Server-owned fields (images, files) are excluded everywhere below: the
     * upload and delete routes have already written by the time they return. */
    const values = () => {
      const body = {};
      Object.keys(editors).forEach(name => {
        if (serverOwned(editors[name].def)) return;
        body[name] = editors[name].ed.value();
      });
      return body;
    };
    /* The baseline is what the server last accepted, serialised. Comparing
     * against it — rather than against the item we opened with — is what keeps
     * a field the artist edited and then undid from writing forever. */
    let committed = JSON.stringify(values());

    async function commit() {
      const body = values();
      const snapshot = JSON.stringify(body);
      let r;
      if (currentId) r = await api('PUT', '/' + state.type + '/' + currentId, body);
      else r = await api('POST', '/' + state.type, body);  // only the no-draft fallback lands here
      if (!r || !r.ok) return false;
      const saved = await r.json();
      committed = snapshot;
      setLive(false);
      if (!currentId) {
        /* First write of a form opened without a draft: reopen with the id so
         * the image editor's uploads have somewhere to attach. This tears down
         * the scope we are saving from, which is safe only because it happens
         * once and only on the no-draft path — `resetMain()` inside renderEdit
         * retires this very handle. */
        renderEdit(saved, opts);
        return true;
      }
      unsaved = false;
      if (!opts.singleton) heading.textContent = 'Edit ' + label;
      return true;
    }

    const actions = el('div', 'as-actions');
    const saver = mountSave(autosave(built.form, {
      commit,
      isDirty: () => JSON.stringify(values()) !== committed,
    }));
    actions.appendChild(saver.el);
    /* The status line goes inside the editing pane when there is a preview,
     * for the same reason the button did: below the split it would sit under a
     * page-height of the artist's own website, away from the fields it reports
     * on. */
    (formPane || main).appendChild(actions);
  }

  // ── text (copy) ─────────────────────────────────────────────────────────────

  function humanize(id) {
    return String(id).replace(/[_-]+/g, ' ').replace(/^./, c => c.toUpperCase());
  }

  /* The copy routes edit the words baked into a hand-authored page, so there is
   * no schema and no item — a slot is identified by its page and its id, and
   * the page template is the only thing that knows it exists.
   *
   * The path is `_copy`, not `copy`, and the underscore is load-bearing:
   * mariaslaughter has a content TYPE named `copy`, which would make this
   * ambiguous with the generic {prefix}/{ctype} route and take her Home text
   * section out. Content-type names are slugs and can't start with `_`. */
  const COPY_PATH = '/_copy';

  /* THE INCIDENT, kept here because the autosave design above is the fix and
   * this is what it is fixing:
   *
   * The Text view used to have its own "Save text" button while Publish sat in
   * the footer as the only button always on screen. Publishing without flushing
   * the editors compiled the site, then the next /_copy fetch redrew the boxes
   * from the server — and a page of an artist's rewrites was gone, with no
   * error and nothing to recover. It was patched by making Publish flush the
   * one section that could be dirty; it is now fixed properly, by there being
   * no second button that means "keep my work" and by every view flushing on
   * the way out. `flushAll()` is the descendant of that patch.
   *
   * Do not reintroduce a per-section save handle. `live` already knows. */

  /* Whether the live preview is showing. SESSION state, not per-render: an
   * artist who turns it off to get the width back shouldn't have it come back
   * every time they leave the section and return. Not persisted either — a
   * stored preference is a second source of truth for a one-click choice. */
  let copyPreviewOn = true;

  /* Editor → page is debounced so a fast typist doesn't rewrite the previewed
   * document on every keystroke. Deliberately NOT a motion token: nothing here
   * animates, and borrowing --adze-dur-fast for a scheduling decision is how
   * two unrelated things end up being tuned together by accident. */
  const COPY_PUSH_MS = 120;

  /* prefers-reduced-motion, asked directly rather than left to the CSS. Two
   * reasons the universal rule in motion.css can't cover this: an explicit
   * behavior:'smooth' passed to scrollIntoView() overrides the scroll-behavior
   * property that rule sets, and the rule lives in THIS document, so it never
   * reaches the previewed page inside the iframe at all. */
  const calmMotion = () =>
    !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  const copyScroll = () => ({ block: 'center', behavior: calmMotion() ? 'auto' : 'smooth' });

  /* The page key IS the live URL path — compile.py writes each page to
   * output/artists/<slug>/<page>/index.html and nginx serves it at /<page>/.
   *
   * Deliberately NOT /preview/<slug>/<page>/. That route is Flask-served, and
   * Flask reads any /assets/<subdir>/… request as a page asset and 404s it
   * (see the root CLAUDE.md), so previewing an artist whose images sit in
   * subfolders would quietly show them a page with no pictures. The live URL
   * is nginx-served and is the real thing. */
  const copyPageUrl = page =>
    '/' + String(page).split('/').map(encodeURIComponent).join('/') + '/';

  /* The inverse, so the editors can follow the preview when an artist clicks
   * their own nav inside it. An unknown path returns null — the preview is
   * then showing a page with no editable text, which it says rather than
   * silently binding nothing. */
  function copyPageOf(pathname, pages) {
    const key = String(pathname || '').replace(/^\/+|\/+$/g, '').split('/')
      .map(s => { try { return decodeURIComponent(s); } catch (e) { return s; } })
      .join('/');
    return pages.indexOf(key) >= 0 ? key : null;
  }

  /* The affordance, injected INTO the previewed document.
   *
   * Tokens do not cross a document boundary: a custom property declared on
   * this page's :root is invisible inside the iframe. So the values are
   * resolved here and written into the rules literally — still one source
   * (tokens/*.css), just read on the way over. Colours go through a probe
   * element rather than getPropertyValue because the palette tokens are
   * color-mix() over OTHER tokens, and that text carries var() references
   * which would resolve to nothing over there.
   *
   * Outline only, no fill: an admin-derived colour painted behind an artist's
   * own text is a legibility risk on a page whose palette we can't see.
   * !important because this lands in hand-authored CSS that was written
   * without knowing this existed and that loads after us.
   *
   * Nothing here animates. The lit state is a persistent "you are editing
   * this one" marker rather than a flash, so there is no duration to pick and
   * no reduced-motion question to answer inside a document motion.css can't
   * reach. The motion is in the scroll, which asks calmMotion() above. */
  function copyPreviewCss() {
    const tok = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
    const probe = el('span');
    probe.style.cssText = 'position:absolute;visibility:hidden;color:var(--adze-accent)';
    document.body.appendChild(probe);
    const accent = getComputedStyle(probe).color;
    probe.remove();
    const off = tok('--adze-space-1');
    /* Both selectors carry the pseudo-class. A trailing ':hover' on the joined
     * list would bind to the last one only, and every plain slot on the page
     * would wear the outline permanently. */
    const marked = ['[data-copy]', '[data-copy-rich]', '[data-field]'];
    return marked.join(',') + '{cursor:pointer}'
      + marked.map(s => s + ':hover').join(',')
      + '{outline:1px dashed ' + accent + ' !important;outline-offset:' + off + '}'
      + '.as-copy-lit{outline:2px solid ' + accent + ' !important;outline-offset:' + off + '}';
  }

  /* The live preview pane.
   *
   * The artist's own published page in an iframe, SAME ORIGIN as the admin —
   * the panel is served from {domain}/api/content-admin/{slug}/panel and the
   * page from {domain}/{page}/ — so contentDocument is readable directly and
   * there is no bridge to build. It works at all because `data-copy`
   * attributes survive compilation: compile.py lifts the page's markup
   * verbatim and copy_slots.apply_overrides replaces inner content only, so
   * the published HTML still says which run of text is which slot.
   *
   * What this is NOT is an editing surface. The page is never made
   * contentEditable and nothing here ever writes to the server. Editing stays
   * in the bounded Quill/textarea, because the page's own CSS is the only
   * thing that styles a copy slot and the bounded editor is what keeps an
   * artist to formatting that CSS covers — see guidelines/editor-bounds.html.
   * The preview is for SEEING.
   *
   * `recs` are the slot records the shell built. The preview owns the flag on
   * each of them, because it is the only thing holding the evidence for what
   * is and isn't on the published page. */
  function copyPreview(recs, pages, onPick) {
    const MISSING = 'Not on your published page yet — publish, and it will show here.';

    const pane = el('div', 'as-copy-preview');
    const hd = el('div', 'as-copy-preview__hd');
    const name = el('div', 'as-copy-preview__name');
    const reload = el('button', 'as-link', 'Reload');
    hd.append(name, reload);
    const stage = el('div', 'as-copy-preview__stage');
    /* Said permanently, not once in a toast. The iframe is the LAST PUBLISHED
     * page with unsaved copy painted into it — an artist who reads it as "my
     * site as it will be" is right about their words and wrong about
     * everything else on the page. */
    const note = el('div', 'as-copy-preview__note',
      'Your published page. Text you type shows here straight away; every other change needs Publish.');
    pane.append(hd, stage, note);

    let frame = null;   // the current iframe, or null while a message is showing
    let fdoc = null;    // its contentDocument, once readable
    let want = null;    // page key the pane is showing (null = somewhere with no slots)
    let bound = null;   // page key whose elements are mapped
    let map = null;     // 'p:'|'r:' + slot id → [element, ...]
    let here = null;    // the record the artist is on, kept lit
    let nav = 0;        // navigation token, so a slow HEAD can't land on a newer page

    const keyOf = rec => (rec.rich ? 'r:' : 'p:') + rec.id;
    /* Strict on rich-vs-plain: writing a rich value into a plain element would
     * preview markup that publish is going to escape. A published page that
     * disagrees with today's content.html about which a slot is falls through to
     * the missing flag, which is true — publishing is what fixes it. */
    const nodesFor = rec => ((map && rec.page === bound && map[keyOf(rec)]) || []);
    const onPage = page => recs.filter(r => r.page === page);

    function flag(rec, text) {
      if (!text) {
        if (rec.flag) { rec.flag.remove(); rec.flag = null; }
        return;
      }
      if (!rec.flag) { rec.flag = el('div', 'as-copy__flag'); rec.el.appendChild(rec.flag); }
      rec.flag.textContent = text;
    }
    const clearFlags = () => recs.forEach(r => flag(r, null));

    /* Messages and the loading spinner both sit ON the stage rather than
     * replacing it, so there is exactly one place that owns what covers the
     * frame and no path where a message and an iframe are both visible. */
    function overlay(node) {
      stage.querySelectorAll('.as-copy-preview__over').forEach(n => n.remove());
      if (!node) return;
      const box = el('div', 'as-copy-preview__over');
      box.appendChild(node);
      stage.appendChild(box);
    }

    function push(rec) {
      const nodes = nodesFor(rec);
      if (!nodes.length) return;
      const value = rec.ed.value();
      /* textContent for a plain slot, innerHTML for a rich one, because that
       * is exactly what publish does: apply_overrides escapes a plain value
       * and inserts a rich one raw. Anything else previews a page the
       * compiler is not going to produce. */
      nodes.forEach(n => { if (rec.rich) n.innerHTML = value; else n.textContent = value; });
    }

    function lightUp(rec) {
      if (!fdoc) return;
      fdoc.querySelectorAll('.as-copy-lit').forEach(n => n.classList.remove('as-copy-lit'));
      const nodes = nodesFor(rec);
      if (!nodes.length) return;
      nodes.forEach(n => n.classList.add('as-copy-lit'));
      /* NOT scrollIntoView(): on a same-origin frame it scrolls every ancestor
       * scrollport, so it reaches out of the iframe and drags the admin page
       * down to centre the preview — which threw the artist's own editors off
       * screen the moment the Text view opened. Scrolling the frame's own
       * window is the same result with nothing outside it moving. */
      const win = frame.contentWindow;
      const box = nodes[0].getBoundingClientRect();
      win.scrollTo({
        top: Math.max(0, box.top + win.scrollY - (win.innerHeight - box.height) / 2),
        behavior: calmMotion() ? 'auto' : 'smooth',
      });
    }

    function onFrameClick(e) {
      const t = e.target;
      if (!t || !t.closest) return;
      const marked = t.closest('[data-copy], [data-copy-rich], [data-field]');
      if (marked) {
        /* Capture phase, and it stops here: a marked run can CONTAIN a link,
         * and following it would take the preview off the page the artist
         * just said they wanted to edit. */
        e.preventDefault();
        e.stopPropagation();
        const rich = marked.hasAttribute('data-copy-rich');
        const attr = rich ? 'data-copy-rich'
                   : (marked.hasAttribute('data-copy') ? 'data-copy' : 'data-field');
        const id = String(marked.getAttribute(attr) || '').trim();
        if (bound && id) onPick(bound, id, rich);
        return;
      }
      const a = t.closest('a[href]');
      if (!a) return;
      let url = null;
      try { url = new URL(a.getAttribute('href'), fdoc.baseURI); } catch (err) { return; }
      e.preventDefault();
      if (url.origin !== window.location.origin) {
        toast('That link leaves your site, so the preview stays here.');
        return;
      }
      /* Driving the navigation ourselves rather than letting the click
       * through: the sandbox withholds popups, so a target="_blank" link
       * would otherwise do nothing at all and read as a broken page. */
      frame.contentWindow.location.assign(url.href);
    }

    function injectStyle() {
      if (!fdoc.head || fdoc.querySelector('style[data-adze-preview]')) return;
      const s = fdoc.createElement('style');
      s.setAttribute('data-adze-preview', '');
      s.textContent = copyPreviewCss();
      fdoc.head.appendChild(s);
    }

    /* Runs on EVERY load of the frame, including one the artist caused by
     * clicking their own nav — which is why it re-reads the location rather
     * than trusting the page it asked for. */
    function bind() {
      overlay(null);
      fdoc = null;
      let path = '';
      try { fdoc = frame.contentDocument; path = frame.contentWindow.location.pathname; }
      catch (e) { fdoc = null; }
      bound = null; map = null;
      clearFlags();
      if (!fdoc || !fdoc.body) {
        /* Only reachable if the frame ended up cross-origin — an external
         * redirect, say. There is nothing to read, so say so rather than
         * leaving an inert rectangle on screen. */
        const back = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Back to your site');
        back.onclick = () => go((here && here.page) || pages[0]);
        want = null;
        overlay(emptyState('Can’t show this page',
          'The preview followed a link outside your site.', back));
        return;
      }
      injectStyle();
      fdoc.addEventListener('click', onFrameClick, true);
      bound = copyPageOf(path, pages);
      want = bound;
      map = {};
      /* `data-field` is the content-type equivalent of a copy slot: it marks
       * where one FIELD of a singleton renders, and it lives in the artist's
       * TEMPLATE rather than a page, because the pages that use it are
       * regenerated on every publish while templates are hand-authored and
       * survive. It maps as a plain slot — a field is never rich. It is a
       * separate attribute on purpose: `data-copy` would make the copy scanner
       * offer a second editor for words that already belong to content.json. */
      fdoc.querySelectorAll('[data-copy], [data-copy-rich], [data-field]').forEach(n => {
        const rich = n.hasAttribute('data-copy-rich');
        const attr = rich ? 'data-copy-rich' : (n.hasAttribute('data-copy') ? 'data-copy' : 'data-field');
        const id = String(n.getAttribute(attr) || '').trim();
        if (!id) return;
        const k = (rich ? 'r:' : 'p:') + id;
        (map[k] = map[k] || []).push(n);
      });
      if (!bound) {
        name.textContent = (path.replace(/^\/+|\/+$/g, '') || '/') + ' — no editable text';
        return;
      }
      name.textContent = bound;
      /* Paint what the editors currently hold BEFORE the artist touches
       * anything. The published page carries the last PUBLISHED words and the
       * editors may already hold saved-but-unpublished ones; showing the two
       * disagreeing side by side is worse than showing neither. */
      onPage(bound).forEach(rec => {
        if (nodesFor(rec).length) push(rec);
        else flag(rec, MISSING);
      });
      if (here && here.page === bound) lightUp(here);
    }

    async function go(page) {
      const mine = ++nav;
      want = page; bound = null; map = null; fdoc = null; frame = null;
      clearFlags();
      name.textContent = page;
      stage.innerHTML = '';
      const wait = el('div');
      wait.appendChild(spinner('lg', 'muted'));
      overlay(wait);

      /* A HEAD before the frame exists, so "you haven't published this page
       * yet" can be said plainly. An iframe reports no status of its own: a
       * 404 simply loads whatever the server's error body is — here, Flask's
       * JSON — and the artist ends up looking at a stack of braces wondering
       * what they broke. */
      let status = 0;
      try { status = (await fetch(copyPageUrl(page), { method: 'HEAD' })).status; }
      catch (e) { status = -1; }
      if (mine !== nav) return;   // a newer navigation already owns the pane

      if (status === 404 || status === 410) {
        overlay(emptyState('Not published yet',
          'This page isn’t on your live site, so there is nothing to show. '
          + 'Publish, and it will appear here.'));
        onPage(page).forEach(rec => flag(rec, MISSING));
        return;
      }
      if (status < 0) {
        const again = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Try again');
        again.onclick = () => go(page);
        overlay(emptyState('Could not load the preview',
          'Your site didn’t answer. Nothing is lost — the preview never saves anything.',
          again));
        return;
      }
      frame = document.createElement('iframe');
      frame.className = 'as-copy-preview__frame';
      frame.title = 'Preview of ' + page;
      /* Same sandbox as the control panel's preview frames.
       * allow-same-origin is what keeps contentDocument readable, which is the
       * whole feature; everything it withholds is something a preview should
       * never do anyway — submit the artist's own contact form, open tabs, or
       * navigate the admin out from under itself. */
      frame.setAttribute('sandbox', 'allow-same-origin allow-scripts');
      frame.addEventListener('load', bind);
      frame.src = copyPageUrl(page);
      stage.insertBefore(frame, stage.firstChild);
    }

    reload.onclick = () => go((here && here.page) || pages[0]);

    return {
      pane,
      push,
      show(rec) {
        here = rec;
        if (rec.page !== want) { go(rec.page); return; }   // lit on bind instead
        lightUp(rec);
      },
      stop() {
        nav += 1;               // any in-flight check now belongs to nobody
        clearFlags();
        pane.remove();          // drops the iframe, and with it the page load
        frame = null; fdoc = null; map = null; bound = null; want = null;
      },
    };
  }

  async function renderCopy() {
    const main = resetMain();
    const bar = el('div', 'as-listbar');
    bar.appendChild(el('h2', null, 'Text'));
    main.appendChild(bar);

    const placeholder = skeletonRows(4);
    main.appendChild(placeholder);
    const r = await api('GET', COPY_PATH);
    placeholder.remove();
    if (!r) return;
    if (!r.ok) {
      const fail = emptyState('Could not load your text',
                              'Check your connection and try again.');
      fail.classList.add('adze-empty--error');
      main.appendChild(fail);
      return;
    }
    const doc = await r.json();
    /* Copy editors only. A slot has no item behind it, so there is no id and
     * nothing to upload against — an image-typed slot would need this ctx
     * filled in, and is not something this view supports. */
    const ctx = { prefix: PREFIX, itemId: null, toast };
    /* The editors and the preview are two panes of one grid. The pane exists
     * even when the preview is off, because it is what carries the form-width
     * cap and the Save row's left edge — see .as-copy-pane in the CSS. */
    const split = el('div', 'as-copy-split');
    const editing = el('div', 'as-copy-pane');
    const wrap = el('div', 'as-copy');
    const slots = [];
    const byEl = new Map();

    (doc.pages || []).forEach(page => {
      const pel = el('div', 'as-copy__page');
      const hd = el('div', 'as-copy__page-hd');
      hd.appendChild(el('h3', null, page.label || page.page));
      pel.appendChild(hd);
      (page.slots || []).forEach(slot => {
        const sel = el('div', 'as-copy__slot');
        sel.appendChild(el('div', 'as-copy__path', page.page + ' · ' + slot.id));
        /* An untouched slot shows the words currently on the page, not an
         * empty box — otherwise "save" quietly blanks the site. */
        const seed = slot.value == null ? slot.default : slot.value;
        const ed = window.AdzeFields.make(
          slot.id,
          { type: slot.rich ? 'copyrich' : 'copytext', label: humanize(slot.id) },
          seed, ctx);
        sel.appendChild(ed.el);
        const rec = {
          page: page.page, id: slot.id, rich: !!slot.rich, ed,
          el: sel, flag: null,
          seeded: seed == null ? '' : String(seed),
          tracksDefault: slot.value == null,
        };
        slots.push(rec);
        byEl.set(sel, rec);
        pel.appendChild(sel);
      });
      wrap.appendChild(pel);
    });

    const orphans = doc.orphans || [];
    if (orphans.length) {
      /* Never hidden. This is text the artist wrote, and the only way they find
       * out the page stopped using it is if we tell them. */
      const box = el('div', 'as-copy__page');
      const hd = el('div', 'as-copy__page-hd');
      hd.appendChild(el('h3', null, 'No longer on your site'));
      box.appendChild(hd);
      box.appendChild(el('div', 'af-note',
        'These lines were written for parts of the site that have since changed. '
        + 'Nothing shows them now — they are kept here so nothing you wrote disappears quietly.'));
      orphans.forEach(o => box.appendChild(el('div', 'as-copy__path', o.page + ' · ' + o.id)));
      wrap.appendChild(box);
    }
    editing.appendChild(wrap);

    const actions = el('div', 'as-actions');

    /* Dirty means "differs from what this box was seeded with", which is the
     * only definition that survives a rich slot: Quill re-emits even untouched
     * HTML in its own shape, so comparing against the page default would call
     * every rich slot dirty forever. */
    function isDirty() {
      return slots.some(s => s.ed.value() !== s.seeded);
    }

    async function saveCopy() {
      const body = {};
      slots.forEach(s => {
        const v = s.ed.value();
        /* A slot the artist never touched goes back as null, which the server
         * reads as "keep tracking the page's own wording". Sending the default
         * text back as a value would look identical today and be wrong later:
         * it freezes this afternoon's copy into an override nobody chose, and
         * the next edit to the page itself would silently not show.
         *
         * A rich slot usually fails this comparison, because Quill re-emits
         * even untouched HTML in its own shape. That only costs it an explicit
         * value it would have had anyway. */
        const untouched = s.tracksDefault && v === s.seeded;
        (body[s.page] = body[s.page] || {})[s.id] = untouched ? null : v;
      });
      const rr = await api('PUT', COPY_PATH, body);
      if (!rr || !rr.ok) return false;
      /* Re-seed, so what is now on the server becomes the new baseline and the
       * section stops reporting itself dirty. Without this, Publish would flush
       * the same text again on every press. */
      slots.forEach(s => { s.seeded = s.ed.value(); s.tracksDefault = false; });
      setLive(false);
      return true;
    }

    const saver = mountSave(autosave(wrap, { commit: saveCopy, isDirty }));
    actions.appendChild(saver.el);
    /* The status line belongs to the editors, not to the section: below the
     * split it would sit under the preview on a narrow screen, a whole
     * page-height of someone else's website away from the last box it
     * reports on. */
    editing.appendChild(actions);
    split.appendChild(editing);
    main.appendChild(split);

    // ── preview wiring ──
    const pages = (doc.pages || []).map(p => p.page);
    let preview = null;
    let current = null;   // the record the artist last put the caret in

    function recOf(node) {
      const n = node && (node.nodeType === 1 ? node : node.parentElement);
      const sel = n && n.closest && n.closest('.as-copy__slot');
      return sel ? byEl.get(sel) || null : null;
    }

    function focusEditor(rec) {
      /* Whatever the field type mounted: a textarea for a plain slot, Quill's
       * contenteditable for a rich one. preventScroll because the smooth
       * scroll below is the one meant to be seen — focus() on its own jumps. */
      const target = rec.el.querySelector('textarea, .ql-editor, input');
      if (target && target.focus) target.focus({ preventScroll: true });
      rec.el.scrollIntoView(copyScroll());
    }

    /* A marked element was clicked in the preview. Strict match first; a
     * published page can disagree with today's content.html about whether a
     * slot is rich, and in that case the artist should still land in the
     * right editor rather than have the click do nothing. */
    function onPick(page, id, rich) {
      const rec = slots.find(s => s.page === page && s.id === id && s.rich === rich)
               || slots.find(s => s.page === page && s.id === id);
      if (rec) focusEditor(rec);
    }

    let pushTimer = null;
    const pending = new Set();
    function queue(rec) {
      if (!preview) return;
      pending.add(rec);
      clearTimeout(pushTimer);
      pushTimer = setTimeout(() => {
        const batch = Array.from(pending);
        pending.clear();
        if (preview) batch.forEach(preview.push);
      }, COPY_PUSH_MS);
    }

    function mountPreview() {
      if (preview || !slots.length) return;
      preview = copyPreview(slots, pages, onPick);
      split.appendChild(preview.pane);
      preview.show(current || slots[0]);
    }
    function unmountPreview() {
      if (!preview) return;
      preview.stop();
      preview = null;
    }

    wrap.addEventListener('focusin', e => {
      const rec = recOf(e.target);
      if (!rec) return;
      current = rec;
      if (preview) preview.show(rec);
    });

    /* One listener for both editor kinds: `input` bubbles out of the textarea
     * a plain slot mounts AND out of the contenteditable Quill mounts for a
     * rich one. */
    wrap.addEventListener('input', e => {
      const rec = recOf(e.target);
      if (rec) queue(rec);
    });

    /* Typing is not the only way a rich slot changes — bold, italic, link and
     * paste all go through Quill's own API, which mutates the DOM without
     * firing `input`. childList/characterData only, NOT attributes: the plain
     * editor autosizes by writing style.height on every keystroke, which would
     * otherwise fire this on top of the `input` above for every character. */
    new MutationObserver(muts => {
      muts.forEach(m => { const rec = recOf(m.target); if (rec) queue(rec); });
    }).observe(wrap, { childList: true, characterData: true, subtree: true });

    /* Mutates the split in place rather than re-rendering the section. A
     * re-render would rebuild every editor and take any unsaved text with it,
     * and a preview toggle must never be able to cost an artist their words. */
    if (slots.length) {
      const toggle = el('button', 'as-btn as-btn-sm as-btn-quiet',
                        copyPreviewOn ? 'Hide preview' : 'Show preview');
      toggle.onclick = () => {
        copyPreviewOn = !copyPreviewOn;
        toggle.textContent = copyPreviewOn ? 'Hide preview' : 'Show preview';
        if (copyPreviewOn) mountPreview(); else unmountPreview();
      };
      bar.appendChild(toggle);
      if (copyPreviewOn) mountPreview();
    }
  }

  // ── account / change password ───────────────────────────────────────────────
  /* The form is AdzeUI.passwordChangeForm — the same one the landing page's
   * account row mounts. This used to be a second, older implementation of the
   * same three fields: raw inputs with no reveal toggle, inline `12px` margins,
   * and `submit.disabled` set only AFTER its await, which is precisely the
   * double-submit window withBusy exists to close. Two password forms is one
   * too many to keep correct, and this was the copy nobody was watching. */
  function renderAccountModal() {
    const backdrop = el('div', 'as-modal-backdrop');
    backdrop.onclick = e => { if (e.target === backdrop) backdrop.remove(); };
    const box = el('div', 'as-modal');
    box.appendChild(el('h2', null, 'Change password'));

    const pw = window.AdzeUI.passwordChangeForm({
      prefix: PREFIX,
      open: true,     // the modal's own title already asked
      onDone: () => {
        backdrop.remove();
        toast('Password changed. Other devices have been signed out.', 'ok');
      },
    });
    box.appendChild(pw.el);

    const cancel = el('button', 'as-link', 'Cancel');
    cancel.onclick = () => backdrop.remove();
    const foot = el('div', 'as-actions');
    foot.appendChild(cancel);
    box.appendChild(foot);

    backdrop.appendChild(box);
    root.appendChild(backdrop);
    pw.focus();
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

  /* A file dropped anywhere OUTSIDE a gallery hits the browser's own default,
   * which navigates the tab to that file — and takes the artist's half-filled
   * form with it. Missing the gallery by 20px shouldn't cost them the work.
   *
   * It cancels the browser default and nothing else: no stopPropagation, so it
   * cannot cut a real drop off from the handler that wanted it. THAT is the
   * line to keep. Adding stopPropagation here to "scope" this would silently
   * kill gallery uploads, and the bubble phase would stop saving you.
   * (In practice it never even sees a gallery drop — field-editors stops those
   * at the gallery — but the guard doesn't rely on that.) */
  function guardStrayDrops() {
    ['dragover', 'drop'].forEach(type =>
      document.addEventListener(type, e => e.preventDefault()));
  }

  function init(opts) {
    PREFIX = opts.prefix;
    root = document.getElementById('adze-admin-root');
    guardStrayDrops();
    // Publishes --as-vvh / .is-kb, which the copy editor's preview height is
    // built on below 959px. See trackViewport() in adze-ui.js.
    window.AdzeUI.trackViewport();
    /* The browser's own guard, for the closed tab and the back button — the two
     * exits the shell cannot intercept. The wording is the browser's; all we
     * control is whether it fires at all.
     *
     * Autosave narrows this to a real race — the debounce window, or a write
     * the server refused — rather than the everyday "you typed and didn't
     * press the button". beforeunload cannot await, so flushing here is not an
     * option; asking is all that's left. */
    window.addEventListener('beforeunload', e => {
      if (anyUnsaved()) { e.preventDefault(); e.returnValue = ''; }
    });
    boot();
  }

  return { init };
})();
