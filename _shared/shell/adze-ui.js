/* adze-ui.js — the Adze design language's shared DOM primitives.
 *
 * Extracted verbatim from admin-shell.js so the artist admin and the artist
 * landing page share ONE implementation. The alternative — a second copy in
 * each surface — is how withBusy's double-submit guard gets quietly reverted
 * on a button nobody was watching.
 *
 * Load this BEFORE admin-shell.js / admin-landing.js; both destructure from
 * window.AdzeUI at IIFE entry.
 *
 * Class names here (`adze-*`) are literal strings matched by admin-shell.css.
 * Renaming one on either side silently unstyles it — change both or neither.
 */
window.AdzeUI = (function () {

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* `host` is where the toast is appended. It defaults to document.body so a
   * caller with no root still works; admin-shell passes its own root because
   * the toast must sit inside the themed subtree. */
  function toast(msg, kind, host) {
    const parent = host || document.body;
    let t = parent.querySelector('.as-toast');
    if (!t) { t = el('div', 'as-toast'); parent.appendChild(t); }
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
  function applyTheme(theme) {
    const th = theme || {};
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

  return { el, toast, applyTheme, spinner, skeletonRows, emptyState, progressBar, withBusy };
})();
