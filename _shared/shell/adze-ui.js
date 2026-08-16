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

  /* Phosphor-style eye, inline. Stroked rather than filled so it inherits
   * currentColor and sits at the same visual weight as the label type.
   * Inline because the artist admin has no external origins — an icon font or
   * a CDN sprite would be the only thing on the page reaching off-host. */
  const _svg = (inner) =>
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    inner + '</svg>';

  const EYE = _svg(
    '<path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12Z"/>' +
    '<circle cx="12" cy="12" r="3.1"/>');

  const EYE_OFF = _svg(
    '<path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12Z"/>' +
    '<circle cx="12" cy="12" r="3.1"/>' +
    '<path d="M4 20 20 4"/>');

  /* A password input with a show/hide toggle.
   *
   * Returns {wrap, input} — append `wrap`, read `input.value`. Both login
   * screens use this, so the reveal behaves identically in the content admin
   * and the landing page.
   *
   * Worth having beyond convenience: a masked field gives you no way to tell
   * a typo from a wrong password, or to spot a password manager silently
   * overwriting what you typed. */
  function passwordField(placeholder, autocomplete) {
    const wrap = el('div', 'as-pw');
    const input = el('input', 'af-input');
    input.type = 'password';
    input.placeholder = placeholder || 'Password';
    input.autocomplete = autocomplete || 'current-password';

    const toggle = el('button', 'as-pw__toggle');
    toggle.type = 'button';                 // never submits the surrounding form
    toggle.innerHTML = EYE;
    toggle.setAttribute('aria-label', 'Show password');
    toggle.setAttribute('aria-pressed', 'false');
    toggle.setAttribute('title', 'Show password');
    toggle.onclick = () => {
      const shown = input.type === 'text';
      input.type = shown ? 'password' : 'text';
      toggle.innerHTML = shown ? EYE : EYE_OFF;
      const label = shown ? 'Show password' : 'Hide password';
      toggle.setAttribute('aria-label', label);
      toggle.setAttribute('title', label);
      toggle.setAttribute('aria-pressed', shown ? 'false' : 'true');
      input.focus();
    };

    wrap.append(input, toggle);
    return { wrap, input };
  }

  /* ── the visible viewport ───────────────────────────────────────────────────
   *
   * dvh solves the URL bar. It does NOT solve the software keyboard — nothing
   * in CSS does, because the keyboard doesn't change the layout viewport at all
   * on iOS and only sometimes does on Android.
   *
   * That is a real defect in the copy editor rather than a polish item. Its
   * preview is `height: min(46dvh, 420px)` and sticky, sized against a viewport
   * the artist can only see half of once they tap a field: on a 780px phone
   * with a 340px keyboard the preview keeps its ~360px and the box being typed
   * into gets what's left, which is a line and a half. The feature that exists
   * so an artist can see their words in place is the thing covering them.
   *
   * So: publish the VISIBLE height as `--as-vvh` (one hundredth of it, so CSS
   * can multiply it like a vh unit) and flag the keyboard with `is-kb`.
   * `is-vv` says the measurement is real — without it the CSS keeps its dvh
   * rules rather than falling back to a var that resolves to the wrong thing.
   *
   * Idempotent: both shells call it at boot and one of them may mount twice. */
  let _vvTracking = false;

  function trackViewport() {
    const vv = window.visualViewport;
    if (_vvTracking || !vv) return;
    _vvTracking = true;
    const r = document.documentElement;
    r.classList.add('is-vv');
    let raf = null;

    function measure() {
      raf = null;
      r.style.setProperty('--as-vvh', (vv.height / 100) + 'px');
      /* 150px, not a percentage. A URL bar collapsing costs 60–120px and must
       * not read as a keyboard; a keyboard is 250px+ on the smallest phone
       * anyone edits on. The gap between those two is where the threshold goes,
       * and it is absolute because both are absolute. */
      r.classList.toggle('is-kb', (window.innerHeight - vv.height) > 150);
    }

    // Coalesced into a frame: visualViewport fires resize AND scroll
    // continuously while the keyboard animates in, and each one here would
    // otherwise write a custom property that invalidates layout.
    const onChange = () => { if (raf === null) raf = requestAnimationFrame(measure); };
    vv.addEventListener('resize', onChange);
    vv.addEventListener('scroll', onChange);
    measure();
  }

  /* ── re-auth ────────────────────────────────────────────────────────────────
   *
   * A 401 arriving MID-SESSION must not rebuild the page.
   *
   * Both shells used to answer every 401 by calling their own renderLogin(),
   * which starts `root.innerHTML = ''`. In the content admin that is a data-loss
   * path with a straight face: autosave's failure line says "your words are
   * still here, and this keeps trying" while the element holding those words is
   * being removed from the document. Nothing had made it reachable — until
   * changing your password did, because that endpoint dual-writes admin_token
   * and calls revoke_all_for_account, so every other open tab's next autosave
   * is a 401. The artist most likely to hit it is the one with the editor open
   * in another tab, which is to say the one with the most to lose.
   *
   * So: sign back in OVER the page, leaving the DOM beneath it untouched. The
   * pending write is not retried here — autosave's own `isDirty` is still true
   * and its next keystroke or flush sends it, which is the path that was
   * already tested.
   *
   * `onDone` runs after a successful re-auth. Concurrent 401s share one
   * overlay: several in-flight requests failing together is the NORMAL case, and
   * four stacked password prompts would be worse than the bug. */
  let _reauthOpen = null;

  function reauth(opts) {
    const o = opts || {};
    const host = o.host || document.body;
    if (_reauthOpen) return _reauthOpen;

    const over = el('div', 'as-reauth');
    const box = el('div', 'as-reauth__box');
    box.appendChild(el('h2', 'as-reauth__title', 'Signed out'));
    box.appendChild(el('p', 'as-reauth__body',
      o.message || 'Your session ended. Sign in again to carry on — '
        + 'nothing you have typed has been lost.'));

    const pwf = passwordField('Password');
    const err = el('div', 'as-err');
    const btn = el('button', 'as-btn', 'Sign back in');

    async function submit() {
      err.textContent = '';
      let r;
      try {
        r = await fetch(o.prefix + '/login', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier: '', password: pwf.input.value.trim() }),
        });
      } catch (e) {
        err.textContent = 'Couldn’t reach the server. Check your connection and try again.';
        return;
      }
      if (r.ok) {
        over.remove();
        _reauthOpen = null;
        if (o.onDone) o.onDone();
        return;
      }
      err.textContent = r.status === 429
        ? 'Too many attempts just now. Wait a minute and try again.'
        : r.status >= 500 ? 'Something broke at our end — not your password.'
        : 'Wrong password.';
    }

    btn.onclick = () => withBusy(btn, submit);
    pwf.input.addEventListener('keydown',
      e => { if (e.key === 'Enter') withBusy(btn, submit); });

    box.append(pwf.wrap, btn, err);
    over.appendChild(box);
    host.appendChild(over);
    pwf.input.focus();

    _reauthOpen = over;
    return over;
  }

  /* ── change password ────────────────────────────────────────────────────────
   *
   * Returns {el} — mount it wherever the surface wants the control.
   *
   * Collapsed by default behind its own toggle. Changing a password is a thing
   * you do once a year, and an open three-field form is three empty boxes on a
   * page whose job is to get the artist into their editor. Pass `open: true`
   * where the surface has already asked the question — inside a modal titled
   * "Change password", a link saying "Change your password" is the same
   * sentence twice.
   *
   * The warning about other devices is not politeness. POST {prefix}/password
   * rewrites admin_token in config.json (it is still the editor's API key) and
   * revokes every other session, so an artist who does this with the editor open
   * elsewhere has just signed that tab out. Saying so is cheaper than the
   * support message. */
  function passwordChangeForm(opts) {
    const o = opts || {};
    const wrap = el('div', 'as-account__item');

    const alwaysOpen = o.open === true;
    const toggle = el('button', 'as-link', 'Change your password');
    const form = el('div', 'as-account__form');
    form.hidden = !alwaysOpen;

    const cur = passwordField('Current password', 'current-password');
    const nu = passwordField('New password', 'new-password');
    const conf = passwordField('Repeat the new password', 'new-password');
    const err = el('div', 'as-err');
    // The only feedback this form gives, and it renders below the button that
    // caused it — announce it rather than relying on the artist looking down.
    err.setAttribute('role', 'status');
    err.setAttribute('aria-live', 'polite');
    const save = el('button', 'as-btn as-btn-quiet', 'Change password');
    const acts = el('div', 'as-actions');
    acts.appendChild(save);

    const hint = el('p', 'as-account__hint',
      'At least 6 characters. This signs you out on your other devices.');

    toggle.onclick = () => {
      form.hidden = !form.hidden;
      toggle.textContent = form.hidden ? 'Change your password' : 'Never mind';
      if (!form.hidden) cur.input.focus();
    };

    save.onclick = () => withBusy(save, async () => {
      err.textContent = '';
      // Checked here as well as on the server: a mistyped repeat is the common
      // case, and a round trip to be told so is a round trip that ends with the
      // artist signed out of their other tab for nothing.
      if (nu.input.value !== conf.input.value) {
        err.textContent = 'Those two don’t match.';
        return;
      }
      if (nu.input.value.trim().length < 6) {
        err.textContent = 'New password must be at least 6 characters.';
        return;
      }
      let r;
      try {
        r = await fetch(o.prefix + '/password', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current: cur.input.value.trim(), new: nu.input.value.trim() }),
        });
      } catch (e) {
        err.textContent = 'Couldn’t reach the server. Try again.';
        return;
      }
      const body = await r.json().catch(() => ({}));
      if (!r.ok) {
        err.textContent = body.error || 'That didn’t work.';
        return;
      }
      [cur, nu, conf].forEach(f => { f.input.value = ''; });
      if (!alwaysOpen) {
        form.hidden = true;
        toggle.textContent = 'Change your password';
      }
      if (o.onDone) o.onDone();
    });

    form.append(cur.wrap, nu.wrap, conf.wrap, hint, acts, err);
    if (!alwaysOpen) wrap.appendChild(toggle);
    wrap.appendChild(form);
    return { el: wrap, focus: () => cur.input.focus() };
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

  return { el, toast, applyTheme, trackViewport, passwordField, reauth,
           passwordChangeForm, spinner, skeletonRows, emptyState, progressBar,
           withBusy };
})();
