/* admin-landing.js — the artist landing page at theirdomain.com/admin.
 *
 * One page for every artist. A little traffic, one big button into the content
 * admin, a quieter link to the control panel, whether anything is down, and
 * a way to tell Gabriel something is wrong.
 *
 * Shares admin-shell.css and adze-ui.js with the content admin, and the same
 * {slug}_admin cookie — so the big button is a plain link that lands already
 * logged in, not a second sign-in.
 */
(function () {
  const { el, spinner, skeletonRows, emptyState, emptyState: _e, withBusy } = window.AdzeUI;
  const BOOT = window.ADZE_LANDING || {};
  const PREFIX = BOOT.prefix;
  let root;

  const toast = (m, k) => window.AdzeUI.toast(m, k, root);

  async function api(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    const r = await fetch(PREFIX + path, opts);
    /* Over the page, not a rebuilt login screen — the feedback box is the one
     * place on this page holding typed words, and renderLogin() would empty it.
     * Same reason as the content admin, smaller stakes. boot() still renders the
     * real login screen, where there is nothing to preserve. */
    if (r.status === 401) {
      window.AdzeUI.reauth({ prefix: PREFIX, host: root });
      return null;
    }
    return r;
  }

  function fmtCount(n) {
    if (n == null) return '—';
    if (n < 10000) return n.toLocaleString();
    return (n / 1000).toFixed(n < 100000 ? 1 : 0) + 'K';
  }

  function shortDate(iso) {
    const d = new Date(iso + 'T00:00:00');
    return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
  }

  // ── naming the button ───────────────────────────────────────────────────────
  /* "Edit your site" told the artist nothing, and sitting above a link called
   * "Advanced editing" it read as the lesser of two editors. So the button says
   * what is actually behind it — "Edit Works & Exhibitions" — taken from the
   * content admin's own schema. Nothing here is per-artist: add a type to a
   * config and the button renames itself. */
  const CTA_FALLBACK = 'Edit your site';

  function joinAnd(names) {
    if (names.length === 1) return names[0];
    return names.slice(0, -1).join(', ') + ' & ' + names[names.length - 1];
  }

  /* Measured against the real button, not a guessed character budget: .as-btn
   * is `white-space: nowrap`, so a label one word too long spills past the
   * button's edge instead of wrapping, and the width that decides it is the
   * artist's phone. Canvas rather than scrollWidth because the button centres
   * its content, so overflow escapes both edges and scrollWidth under-reports
   * it. */
  function fitsButton(btn, text) {
    const cs = getComputedStyle(btn);
    const inner = btn.clientWidth
      - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    // Nothing to measure against (never laid out) — don't degrade the label on
    // the strength of a measurement we didn't get.
    if (!(inner > 0)) return true;
    const ctx = fitsButton._ctx
      || (fitsButton._ctx = document.createElement('canvas').getContext('2d'));
    ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    return ctx.measureText(text).width <= inner;
  }

  // Longest label that still fits, or null if even the shortest named form
  // doesn't. Name everything if it fits; past that, two names and a count.
  function namedLabel(btn, names) {
    if (!names.length) return null;
    const tries = ['Edit ' + joinAnd(names)];
    if (names.length > 2) {
      tries.push('Edit ' + names.slice(0, 2).join(', ')
                 + ' & ' + (names.length - 2) + ' more');
    }
    return tries.find(t => fitsButton(btn, t)) || null;
  }

  function ctaLabel(btn, names, hasCopy) {
    // "your site text", not "Site text": on its own it's a sentence rather
    // than one item in a list.
    if (!names.length) return hasCopy ? 'Edit your site text' : null;
    /* Sitewide copy is one more thing behind the button, but "Site text" is
     * our word for it, not the artist's — so it never costs a real type its
     * place on the button. If counting it is what pushed the label down to
     * the generic one, drop it and name the types instead. */
    return namedLabel(btn, hasCopy ? names.concat('Site text') : names)
      || (hasCopy && namedLabel(btn, names))
      || 'Edit your content';
  }

  /* Never blocks the button. It renders immediately with CTA_FALLBACK and this
   * upgrades the words if and when the schema lands; anything that goes wrong
   * just leaves the fallback standing. Deliberately not api(): that sends a 401
   * to the login screen, and a nicety on a button must never sign anyone out. */
  async function nameTheButton(btn) {
    if (!BOOT.contentUrl) return;
    // contentUrl is the content admin's {prefix}/panel; its schema is the
    // sibling {prefix}/schema, same origin and same {slug}_admin cookie.
    const base = BOOT.contentUrl.replace(/\/[^/]*$/, '');
    let schema;
    try {
      const r = await fetch(base + '/schema');
      if (!r.ok) return;
      schema = (await r.json()) || {};
    } catch (e) { return; }
    // Guarded: Object.entries over anything that isn't an object would name
    // the button after its indices.
    const types = schema.content_types;
    const names = (types && typeof types === 'object' && !Array.isArray(types))
      ? Object.entries(types).map(([key, t]) => (t && t.label) || key)
      : [];
    // Measure in the font the button will actually be wearing — Inter and the
    // system fallback don't measure alike, and waiting costs nothing here
    // because the button has been on screen since first paint.
    if (document.fonts && document.fonts.ready) {
      await document.fonts.ready.catch(() => {});
    }
    const label = ctaLabel(btn, names, schema.copy === true);
    if (label) btn.textContent = label;
  }

  // ── login ───────────────────────────────────────────────────────────────────
  function renderLogin() {
    root.innerHTML = '';
    const box = el('div', 'as-login');
    box.appendChild(el('h1', null, BOOT.name || 'Sign in'));
    const who = el('input', 'af-input');
    who.type = 'text'; who.placeholder = 'Your name or email (optional)';
    who.autocomplete = 'username';
    const pwf = window.AdzeUI.passwordField('Password');
    const pw = pwf.input;
    const err = el('div', 'as-err');
    const btn = el('button', 'as-btn', 'Enter');
    async function submit() {
      const r = await fetch(PREFIX + '/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        // Trailing whitespace off a paste is not a wrong password.
        body: JSON.stringify({ identifier: who.value.trim(), password: pw.value.trim() }),
      });
      if (r.ok) { boot(); return; }
      // Don't report every failure as bad credentials -- a rate limit worded
      // as "wrong password" sends people off resetting a password that was
      // fine, which is exactly the wrong thing to do while locked out.
      if (r.status === 429) {
        err.textContent = 'Too many attempts just now. Wait a minute and try again.';
      } else if (r.status >= 500) {
        err.textContent = 'Something broke at our end — not your password. Try again shortly.';
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

  // ── charts ──────────────────────────────────────────────────────────────────

  /* Single series, accent on surface. No categorical palette exists in the
   * design language and inventing one would have to survive 21 unknown artist
   * accents — so magnitude is encoded by y-position here and by bar height in
   * the hourly strip. Colour is emphasis, never the channel. */
  function areaChart(daily) {
    const wrap = el('div', 'as-chart');
    const W = 900, H = 100, PAD = 2;
    const vals = daily.map(d => d.views);
    const max = Math.max(1, ...vals);
    const stepX = vals.length > 1 ? W / (vals.length - 1) : W;
    const y = v => PAD + (H - PAD * 2) * (1 - v / max);

    const pts = vals.map((v, i) => [i * stepX, y(v)]);
    const line = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
    const area = line + ` L${W} ${H} L0 ${H} Z`;

    // Unique per instance: a global gradient id collides the moment a second
    // chart lands on the page.
    const gid = 'asGrad' + Math.random().toString(36).slice(2, 9);

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'as-chart__svg');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML =
      `<defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">` +
      `<stop offset="0%" stop-color="var(--adze-accent)" stop-opacity="0.25"/>` +
      `<stop offset="100%" stop-color="var(--adze-accent)" stop-opacity="0.02"/>` +
      `</linearGradient></defs>` +
      `<path d="${area}" fill="url(#${gid})"/>` +
      // non-scaling-stroke because preserveAspectRatio=none would otherwise
      // squash the line weight horizontally.
      `<path d="${line}" fill="none" stroke="var(--adze-accent)" stroke-width="2" ` +
      `vector-effect="non-scaling-stroke" stroke-linejoin="round"/>`;

    const cursor = el('div', 'as-chart__cursor');
    const tip = el('div', 'as-chart__tip');
    wrap.append(svg, cursor, tip);

    // A pointermove handler rather than 30 invisible circles with SMIL <set>:
    // the old trick isn't keyboard-reachable and is 2011 tech.
    wrap.addEventListener('pointermove', e => {
      const r = wrap.getBoundingClientRect();
      const i = Math.max(0, Math.min(vals.length - 1,
        Math.round(((e.clientX - r.left) / r.width) * (vals.length - 1))));
      const x = (i / (vals.length - 1 || 1)) * r.width;
      cursor.style.left = x + 'px';
      tip.style.left = x + 'px';
      tip.textContent = `${daily[i].views} on ${shortDate(daily[i].date)}`;
    });

    const axis = el('div', 'as-chart__axis');
    axis.append(el('span', 'adze-label', shortDate(daily[0].date)),
                el('span', 'adze-label', shortDate(daily[daily.length - 1].date)));

    const box = el('div');
    box.append(wrap, axis);
    return box;
  }

  function hourBars(hourly) {
    const max = Math.max(1, ...hourly);
    const grid = el('div', 'as-hours');
    hourly.forEach((v, h) => {
      const bar = el('div', 'as-hours__bar');
      bar.style.height = Math.max(2, (v / max) * 40) + 'px';
      bar.title = `${v} at ${String(h).padStart(2, '0')}:00`;
      grid.appendChild(bar);
    });
    const box = el('div');
    box.appendChild(grid);
    const peak = hourly.indexOf(max);
    if (hourly.some(v => v > 0)) {
      const h12 = peak % 12 === 0 ? 12 : peak % 12;
      box.appendChild(el('div', 'as-hours__cap',
        `busiest around ${h12}${peak < 12 ? 'am' : 'pm'}`));
    }
    return box;
  }

  /* The sparkline for the collapsed visits line. Deliberately not areaChart():
   * that one carries an axis, a hover cursor and a tooltip, none of which
   * belong in a single row of text. Same data, no furniture. */
  function sparkline(daily) {
    const vals = daily.map(d => d.views);
    const W = 120, H = 24;
    const max = Math.max(1, ...vals);
    const stepX = vals.length > 1 ? W / (vals.length - 1) : W;
    const pts = vals.map((v, i) =>
      `${(i * stepX).toFixed(1)} ${(H - 1 - (H - 2) * (v / max)).toFixed(1)}`);
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'as-visits__spark');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML = `<path d="M${pts.join(' L')}" fill="none" stroke="var(--adze-accent)" `
      + `stroke-width="1.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>`;
    return svg;
  }

  /* Visits, collapsed.
   *
   * The full card below is unchanged and still one click away — what changed is
   * its rank. It was the largest object on a page whose entire purpose is doing
   * something to your site, and it is the one thing here nobody can act on. A
   * number, a direction and a sparkline say everything a glance was ever going
   * to take from it. */
  function renderVisits(host, a) {
    host.innerHTML = '';
    if (!a.analytics_since) { renderData(host, a); return; }

    const line = el('div', 'as-visits');
    line.append(el('span', 'adze-label', 'Visits'),
                el('span', 'as-visits__value adze-numeric', fmtCount(a.month)),
                el('span', 'as-visits__label', 'last 30 days'));

    if (a.prev_month) {
      const dir = a.trend === 'up' ? 'up' : a.trend === 'down' ? 'down' : 'flat';
      const glyph = dir === 'up' ? '↑' : dir === 'down' ? '↓' : '→';
      const pct = a.prev_month >= 10
        ? Math.abs(Math.round(((a.month - a.prev_month) / a.prev_month) * 100)) + '%'
        : `vs ${a.prev_month}`;
      line.appendChild(el('span', `as-visits__delta as-visits__delta--${dir}`,
        `${glyph} ${pct}`));
    }
    if (a.daily && a.daily.length > 1) line.appendChild(sparkline(a.daily));

    const more = el('button', 'as-link as-visits__more', 'Show detail');
    const detail = el('div');
    detail.hidden = true;
    let built = false;
    more.onclick = () => {
      if (!built) { renderData(detail, a); built = true; }
      detail.hidden = !detail.hidden;
      more.textContent = detail.hidden ? 'Show detail' : 'Hide detail';
    };
    line.appendChild(more);

    host.append(line, detail);
  }

  // ── data section ────────────────────────────────────────────────────────────
  function renderData(host, a) {
    host.innerHTML = '';
    const since = a.analytics_since;
    const days = since ? Math.floor((Date.now() / 1000 - since) / 86400) : null;

    // Three honest states. A flat baseline for "we weren't measuring" would
    // read as "nobody came", which isn't true.
    if (!since) {
      host.appendChild(emptyState(
        'Not counting visits yet',
        'Your site starts counting the next time it’s published. Check back in a few days.'));
      return;
    }

    /* One card, not four. The number, the trend, the sparkline and the two
       counts are one thought — "how's the site doing" — and they used to be a
       standalone hero plus three stacked cards, which pushed the actual reason
       anyone opens this page (the Edit button) below the fold. */
    const card = el('div', 'as-card as-card--figure');
    const hd = el('div', 'as-card__hd');
    hd.append(el('span', 'adze-label', 'Visits'),
              el('span', 'as-card__meta', days < 7
                ? `since ${new Date(since * 1000).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}`
                : 'last 30 days'));
    card.appendChild(hd);

    const fig = el('div', 'as-figure');
    fig.appendChild(el('span', 'as-hero__value', fmtCount(a.month)));
    fig.appendChild(el('span', 'as-hero__label adze-label',
      days < 7 ? `visits in ${days} day${days === 1 ? '' : 's'} of counting`
               : 'visits in the last 30 days'));

    if (days >= 7 && a.prev_month != null) {
      const dir = a.trend === 'up' ? 'up' : a.trend === 'down' ? 'down' : 'flat';
      const glyph = dir === 'up' ? '↑' : dir === 'down' ? '↓' : '→';
      /* A percentage against a tiny baseline is noise dressed as insight —
       * 6 visits to 450 is "7400% up", which tells the artist nothing. Below
       * a floor, give the two counts instead and let them judge. */
      let words;
      if (!a.prev_month) words = 'first stretch of counting';
      else if (a.prev_month < 10) words = `vs ${a.prev_month} in the 30 days before`;
      else words = `${Math.abs(Math.round(((a.month - a.prev_month) / a.prev_month) * 100))}% `
                   + 'vs the previous 30 days';
      const d = el('div', `as-hero__delta as-hero__delta--${dir}`);
      d.append(el('span', null, glyph), el('span', null, words));
      fig.appendChild(d);
    }
    card.appendChild(fig);

    if (a.month === 0 && days >= 7) {
      card.appendChild(el('p', 'as-hero__label',
        'Nobody has found the site yet. That’s normal for a new site — sharing the link is what changes it.'));
      host.appendChild(card);
      return;
    }

    card.appendChild(areaChart(a.daily.slice(days < 7 ? -Math.max(days + 1, 2) : 0)));

    /* Today and This week only. "Avg. visit" was removed 2026-07-31: the
       tracker measures wall-clock from page load to pagehide with no idle
       detection and no ceiling, and upsert_session keeps MAX(dur) — so one
       tab left open all afternoon becomes a permanent 200-minute "average
       visit". A number that wrong is worse than no number. Don't put it back
       without session-level idle timeouts in the beacon itself. */
    const stats = el('div', 'as-stats');
    [['Today', fmtCount(a.today)], ['This week', fmtCount(a.week)]].forEach(([label, value]) => {
      const t = el('div', 'as-stat');
      t.append(el('div', 'as-stat__value adze-numeric', value),
               el('div', 'as-stat__label adze-label', label));
      stats.appendChild(t);
    });
    card.appendChild(stats);

    if (a.hourly && a.hourly.some(v => v > 0)) {
      const hrs = el('div', 'as-hourly');
      hrs.appendChild(el('div', 'adze-label', 'When people visit'));
      hrs.appendChild(hourBars(a.hourly));
      card.appendChild(hrs);
    }

    host.appendChild(card);
  }

  // ── status ──────────────────────────────────────────────────────────────────
  function renderStatus(host, s) {
    host.innerHTML = '';
    // A note from Gabriel always wins — a sentence beats a machine word.
    // Otherwise: say nothing when we have no signal ('unknown'), because this
    // page is served by the process the status describes, so the artist
    // reading it is already proof the editor is up. Only a positively-known
    // problem is worth interrupting someone who came to change a photo.
    if (!s.note && s.editor === 'unknown') return;
    const degraded = s.editor === 'degraded';
    const box = el('div', 'as-status ' + (degraded ? 'as-status--degraded' : 'as-status--ok'));
    box.appendChild(el('span', 'as-status__dot'));
    box.appendChild(el('span', null, s.note || (degraded
      ? 'Editing may be unavailable right now — your site itself is unaffected.'
      : 'Everything running')));
    host.appendChild(box);
  }

  // ── feedback ────────────────────────────────────────────────────────────────
  function renderFeedback(host) {
    host.innerHTML = '';
    const card = el('div', 'as-card');
    const hd = el('div', 'as-card__hd');
    hd.appendChild(el('span', 'adze-label', 'Something wrong? Stuck?'));
    const form = el('div', 'as-feedback');

    const kindF = el('div', 'af-field');
    kindF.appendChild(el('label', null, 'What kind of thing?'));
    const kind = el('select', 'af-input');
    [['problem', 'Something’s broken'], ['stuck', 'I’m stuck on something'],
     ['idea', 'An idea or request'], ['other', 'Something else']]
      .forEach(([v, t]) => { const o = el('option', null, t); o.value = v; kind.appendChild(o); });
    kindF.appendChild(kind);

    const msgF = el('div', 'af-field');
    msgF.appendChild(el('label', null, 'Tell Gabriel what’s up'));
    // af-textarea is a MODIFIER — it only sets height/resize. Without af-input
    // the field gets no palette at all, which renders as a raw white box on
    // every dark artist theme. field-editors.js always pairs the two.
    const msg = el('textarea', 'af-input af-textarea');
    msg.rows = 5;
    msg.placeholder = 'No rush — this isn’t for emergencies, just anything that’s bugging you.';
    msgF.appendChild(msg);

    const replyF = el('div', 'af-field');
    replyF.appendChild(el('label', null, 'Email to reply to (optional)'));
    const reply = el('input', 'af-input'); reply.type = 'email';
    replyF.appendChild(reply);

    const acts = el('div', 'as-actions');
    const send = el('button', 'as-btn as-btn-quiet', 'Send');
    acts.appendChild(send);

    send.onclick = () => withBusy(send, async () => {
      const r = await api('POST', '/feedback', {
        kind: kind.value, message: msg.value, reply_to: reply.value,
      });
      if (!r) return;
      const body = await r.json().catch(() => ({}));
      if (!r.ok) { toast(body.error || 'That didn’t send.', 'err'); return; }
      host.innerHTML = '';
      const done = el('div', 'as-card');
      done.appendChild(emptyState('Thanks — that’s landed',
        'Gabriel gets these. No need to chase it.'));
      host.appendChild(done);
    });

    form.append(kindF, msgF, replyF, acts);
    card.append(hd, form);
    host.appendChild(card);
  }

  // ── account ─────────────────────────────────────────────────────────────────
  /* The last tab, and deliberately the quietest: the two things an artist does
   * rarely (change a password, go to the control panel) plus nothing else.
   * Both are plain controls at body size — a card here would dress up a section
   * nobody came to visit.
   *
   * Changing a password lived nowhere at all before this. The endpoint has
   * always existed (artist_admin.register_core wires POST {prefix}/password
   * into every landing page); only the control was missing, so the answer to
   * "how do I change my password" was to ask Gabriel to do it. */
  function renderAccount(host) {
    host.innerHTML = '';
    const box = el('div', 'as-account');

    const pw = window.AdzeUI.passwordChangeForm({
      prefix: PREFIX,
      onDone: () => toast('Password changed. Other devices have been signed out.', 'ok'),
    });
    box.appendChild(pw.el);

    /* Only when there is a content admin. Without one it IS the editor and is
     * already the primary button at the top — a second link to the same place,
     * worded as an aside, reads as somewhere else to go. */
    if (BOOT.contentUrl) {
      const item = el('div', 'as-account__item');
      const adv = el('a', 'as-advanced', 'Open the Adze control panel →');
      adv.href = PREFIX + '/handoff';
      item.appendChild(adv);
      box.appendChild(item);
    }

    host.appendChild(box);
  }

  // ── your site: links and a QR ───────────────────────────────────────────────

  function ago(ts) {
    if (!ts) return null;
    const s = Math.max(0, Math.floor(Date.now() / 1000 - ts));
    if (s < 3600) return `${Math.max(1, Math.round(s / 60))} min ago`;
    if (s < 86400) return `${Math.round(s / 3600)} hr ago`;
    const d = Math.round(s / 86400);
    return d === 1 ? 'yesterday' : `${d} days ago`;
  }

  /* Dark on light, always, whatever the artist's admin theme is. A QR inverted
   * to match a dark page is a QR that a good half of phone cameras refuse to
   * read, and this one exists to be pointed at. */
  function qrFor(url) {
    if (typeof window.qrcode !== 'function') return null;
    try {
      // Type 0 = pick the smallest version that fits; 'M' survives a phone
      // screen's glare and a printed sticker equally.
      const qr = window.qrcode(0, 'M');
      qr.addData(url);
      qr.make();
      const box = el('div', 'as-qr');
      box.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
      return box;
    } catch (e) { return null; }
  }

  function renderSite(host, s) {
    host.innerHTML = '';
    const card = el('div', 'as-card');
    const hd = el('div', 'as-card__hd');
    hd.appendChild(el('span', 'adze-label', 'Your site'));
    if (s.published) hd.appendChild(el('span', 'as-card__meta', 'published ' + ago(s.published)));
    card.appendChild(hd);

    if (!s.pages.length) {
      card.appendChild(emptyState('Nothing published yet',
        'As soon as you publish, your pages appear here as links.'));
      host.appendChild(card);
      return;
    }

    const addr = el('div', 'as-site__addr');
    const link = el('a', 'as-site__url', s.domain || s.url);
    link.href = s.url; link.target = '_blank'; link.rel = 'noopener';
    addr.appendChild(link);

    const copy = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Copy link');
    copy.onclick = async () => {
      try {
        await navigator.clipboard.writeText(s.url);
        copy.textContent = 'Copied';
        setTimeout(() => { copy.textContent = 'Copy link'; }, 1500);
      } catch (e) { toast('Couldn’t copy — long-press the address instead.', 'err'); }
    };
    addr.appendChild(copy);

    const qrBtn = el('button', 'as-btn as-btn-sm as-btn-quiet', 'QR code');
    const qrHost = el('div');
    qrHost.hidden = true;
    let qrBuilt = false;
    qrBtn.onclick = () => {
      if (!qrBuilt) {
        const q = qrFor(s.url);
        if (q) {
          qrHost.appendChild(q);
          qrHost.appendChild(el('p', 'as-site__qrcap',
            'Point a phone camera at this to open your site. Fine to print on a card.'));
        } else {
          qrHost.appendChild(el('p', 'as-site__qrcap', 'Couldn’t draw a QR code here.'));
        }
        qrBuilt = true;
      }
      qrHost.hidden = !qrHost.hidden;
      qrBtn.classList.toggle('is-on', !qrHost.hidden);
    };
    addr.appendChild(qrBtn);
    card.append(addr, qrHost);

    const pages = el('div', 'as-site__pages');
    s.pages.forEach(p => {
      // The front page's own <title> is usually the whole site name, which in
      // a row of page links is the longest chip and the least informative one.
      const a = el('a', 'as-site__page', p.home ? 'Home' : p.title);
      a.href = p.url; a.target = '_blank'; a.rel = 'noopener';
      if (p.home) a.classList.add('is-home');
      pages.appendChild(a);
    });
    card.appendChild(pages);

    host.appendChild(card);
  }

  // ── files ───────────────────────────────────────────────────────────────────

  let filesCache = null;

  // The kinds _file_kind marks as readable text; everything else the viewer
  // renders from its bytes or offers as a download.
  const TEXT_KINDS = ['text', 'markdown', 'env'];

  /* One flat list grouped by folder, not a collapsible tree. An artist site is
   * a handful of page folders and an assets folder — a tree here would be three
   * clicks of ceremony around twenty files, and on a phone it would be three
   * clicks in a 320px column. */
  function groupFiles(files) {
    const groups = new Map();
    files.forEach(f => {
      const parts = f.path.split('/');
      const key = parts.length > 1 ? parts[0] : '';
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(f);
    });
    // Root files first (config.json, default-styles.css — the site-wide ones),
    // then folders alphabetically, with assets last: it is the biggest and the
    // least likely thing to be looking for.
    return [...groups.entries()].sort((a, b) => {
      if (a[0] === b[0]) return 0;
      if (a[0] === '') return -1;
      if (b[0] === '') return 1;
      if (a[0] === 'assets') return 1;
      if (b[0] === 'assets') return -1;
      return a[0].localeCompare(b[0]);
    });
  }

  function mountFiles(host, sitePages) {
    host.innerHTML = '';
    const wrap = el('div', 'as-files');
    const listPane = el('div', 'as-files__list');
    const viewPane = el('div', 'as-files__view');
    wrap.append(listPane, viewPane);
    host.appendChild(wrap);

    const search = el('input', 'af-input as-files__search');
    search.type = 'search';
    search.placeholder = 'Find a file';
    const rowsHost = el('div');
    listPane.append(search, rowsHost);
    viewPane.appendChild(emptyState('Pick a file',
      'Everything your site is built from is here. Nothing you open can be changed from this page.'));

    let current = null;
    const rowByPath = new Map();

    function pageUrlFor(path) {
      if (!window.AdzeFileViewer.isPageSource(path)) return null;
      const dir = path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '';
      const page = (sitePages || []).find(p => p.path === dir);
      return page ? page.url : null;
    }

    function draw(filter) {
      rowsHost.innerHTML = '';
      rowByPath.clear();
      const q = (filter || '').trim().toLowerCase();
      const files = (filesCache || []).filter(f => !q || f.path.toLowerCase().includes(q));
      if (!files.length) {
        rowsHost.appendChild(emptyState('Nothing matches', ''));
        return;
      }
      groupFiles(files).forEach(([folder, items]) => {
        rowsHost.appendChild(el('div', 'as-files__group adze-label', folder || 'Site'));
        items.forEach(f => {
          const row = el('button', 'as-files__row');
          const name = f.path.split('/').pop();
          row.append(el('span', 'as-files__name', name),
                     el('span', 'as-files__size', window.AdzeFileViewer.fmtBytes(f.size)));
          if (f.path !== name) row.title = f.path;
          row.onclick = () => { location.hash = '#/files/' + f.path; };
          rowByPath.set(f.path, row);
          rowsHost.appendChild(row);
        });
      });
      if (current && rowByPath.has(current)) rowByPath.get(current).classList.add('is-active');
    }

    search.addEventListener('input', () => draw(search.value));

    async function select(path) {
      current = path || null;
      rowByPath.forEach((row, p) => row.classList.toggle('is-active', p === path));

      if (!path) {
        wrap.classList.remove('is-detail');
        viewPane.innerHTML = '';
        viewPane.appendChild(emptyState('Pick a file',
          'Everything your site is built from is here. Nothing you open can be changed from this page.'));
        return;
      }

      // Phone: the list and the file are two screens, not two columns.
      wrap.classList.add('is-detail');
      viewPane.innerHTML = '';
      const back = el('button', 'as-link as-files__back', '← All files');
      back.onclick = () => { location.hash = '#/files'; };
      viewPane.appendChild(back);
      const body = el('div');
      viewPane.appendChild(body);
      body.appendChild(spinner());

      const meta = (filesCache || []).find(f => f.path === path) || { path };
      let file = { path, kind: meta.kind, size: meta.size };

      /* Only ask for text when the list already says it is text: the server
       * answers 415 for anything else, which is correct and which the viewer
       * handles, but it is a wasted round trip and a red line in the artist's
       * console for every font they click.
       *
       * A path the list has never heard of is the exception — a hand-typed or
       * stale hash. Ask anyway and let the server be the authority, or a file
       * that doesn't exist renders as a download button for nothing. */
      if (!meta.kind || TEXT_KINDS.includes(meta.kind)) {
        const r = await api('GET', '/file?path=' + encodeURIComponent(path));
        if (!r) return;
        const payload = await r.json().catch(() => ({}));
        if (r.ok) {
          file = payload;
        } else if (r.status === 404) {
          body.innerHTML = '';
          body.appendChild(emptyState('That file has gone',
            'It may have been renamed or deleted since this list was loaded.'));
          return;
        } else {
          // 413/415 are not failures — they are "this is not text", which the
          // viewer handles by offering the bytes instead.
          file = { path, kind: payload.kind || meta.kind, size: payload.size || meta.size,
                   error: payload.error };
        }
      }

      body.innerHTML = '';
      window.AdzeFileViewer.render(body, {
        prefix: PREFIX, file, pageUrl: pageUrlFor(path),
      });
      viewPane.scrollTop = 0;
    }

    async function load() {
      rowsHost.appendChild(skeletonRows(6));
      const r = await api('GET', '/files');
      if (!r) return;
      if (!r.ok) {
        rowsHost.innerHTML = '';
        rowsHost.appendChild(emptyState('Couldn’t list your files', 'Try again in a moment.'));
        return;
      }
      filesCache = (await r.json()).files || [];
      draw(search.value);
    }

    return { load, select, drawn: () => !!filesCache };
  }

  // ── history ─────────────────────────────────────────────────────────────────

  function snapDate(ts) {
    // '2026-03-27T08-15-30', written with gmtime by the server.
    const iso = String(ts || '').replace(/T(\d\d)-(\d\d)-(\d\d)$/, 'T$1:$2:$3Z');
    const d = new Date(iso);
    if (isNaN(d)) return ts || '';
    return d.toLocaleString(undefined, {
      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
    });
  }

  async function renderHistory(host) {
    host.innerHTML = '';
    host.appendChild(skeletonRows(4));
    const r = await api('GET', '/history');
    if (!r) return;
    host.innerHTML = '';
    if (!r.ok) {
      host.appendChild(emptyState('Couldn’t load your history', 'Try again in a moment.'));
      return;
    }
    const data = await r.json();
    const items = (data.autosave ? [data.autosave] : []).concat(data.snapshots || []);

    host.appendChild(el('p', 'fv-hint',
      'Adze keeps a copy of your site each time it’s saved. Restoring puts your '
      + 'pages and settings back as they were and republishes the site. Your '
      + 'pictures and uploads are never touched.'));

    if (!items.length) {
      host.appendChild(emptyState('No saved versions yet',
        'One is kept every time you save in the editor.'));
      return;
    }

    const list = el('div', 'as-list');
    items.forEach(s => {
      const row = el('div', 'as-row');
      // .as-row-stack, not .as-row-title: that one is a single ellipsised line,
      // and a version needs its date under its name.
      const main = el('div', 'as-row-stack');
      main.append(el('div', 'as-row-stack__name', s.autosave ? 'Latest save' : s.name),
                  el('div', 'as-row-stack__meta',
                     `${snapDate(s.timestamp)} · ${window.AdzeFileViewer.fmtBytes(s.size)}`));
      const acts = el('div', 'as-row-actions');

      const restore = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Restore');
      restore.onclick = () => {
        /* Two-step, inline, and it says what will actually happen. A restore
         * replaces the artist's current pages — that is not a thing to put
         * behind one tap with a word they might read as "download". */
        acts.innerHTML = '';
        const warn = el('span', 'as-row-confirm', 'Replace your pages with this version?');
        const yes = el('button', 'as-btn as-btn-sm', 'Yes, restore');
        const no = el('button', 'as-link', 'Cancel');
        no.onclick = () => renderHistory(host);
        yes.onclick = () => withBusy(yes, async () => {
          const rr = await api('POST', '/history/restore', { filename: s.filename });
          if (!rr) return;
          const body = await rr.json().catch(() => ({}));
          if (!rr.ok || body.ok === false) {
            toast(body.error || 'That restore didn’t work.', 'err');
            renderHistory(host);
            return;
          }
          toast('Restored and republished.', 'ok');
          renderHistory(host);
        });
        acts.append(warn, yes, no);
      };

      acts.appendChild(restore);
      row.append(main, acts);
      list.appendChild(row);
    });
    host.appendChild(list);
  }

  // ── export ──────────────────────────────────────────────────────────────────

  async function renderExport(host) {
    host.innerHTML = '';
    host.appendChild(skeletonRows(2));
    const r = await api('GET', '/export-info');
    if (!r) return;
    host.innerHTML = '';
    const info = r.ok ? await r.json() : { ready: false };

    const card = el('div', 'as-card');
    card.appendChild(el('span', 'adze-label', 'Take your site with you'));

    if (!info.ready) {
      card.appendChild(emptyState('Nothing to export yet',
        'Publish your site once and a full copy of it becomes downloadable here.'));
      host.appendChild(card);
      return;
    }

    card.appendChild(el('p', null,
      'A single zip holding your finished website, the pictures and fonts in it, '
      + 'the source files behind each page, and your settings. The finished site '
      + 'inside it works anywhere — hand the folder to any web host and it runs, '
      + 'with no Adze involved.'));
    card.appendChild(el('p', 'fv-hint',
      `${info.files} file${info.files === 1 ? '' : 's'} · about `
      + `${window.AdzeFileViewer.fmtBytes(info.bytes)} before compression`));

    const acts = el('div', 'as-actions');
    const dl = el('a', 'as-btn', 'Download my site');
    dl.href = PREFIX + '/export';
    acts.appendChild(dl);
    card.appendChild(acts);
    host.appendChild(card);
  }

  // ── overview ────────────────────────────────────────────────────────────────
  function renderOverview(page) {
    /* The button comes FIRST. People open this page to change something on
       their site; the numbers are what they read on the way past. It used to
       sit under the analytics block, which on a phone meant scrolling past a
       hero, a chart and two more cards to reach the only thing they came
       for. */
    // Exactly one primary button on the page. When the artist has no content
    // admin the primary points at the control panel instead, and the
    // secondary link is dropped rather than duplicated.
    const ctaWrap = el('div');
    const cta = el('a', 'as-btn as-cta');
    // Exactly one thing on this page is called editing, and it's the button.
    // The link under it used to read "Advanced editing →", which is the same
    // word with a better adjective on it — an artist unsure which they wanted
    // read "advanced" as "the proper one" and landed in the control panel,
    // which is the opposite of where they meant to go. Naming the destination
    // instead of ranking it removes the comparison: the button says what you
    // will edit, the link says where else you can go.
    if (BOOT.contentUrl) {
      cta.textContent = CTA_FALLBACK;
      cta.href = BOOT.contentUrl;
      ctaWrap.appendChild(cta);
      // The control panel link used to sit directly under this button, which
      // made it the second item in a two-item menu — a comparison, and one the
      // artist kept losing. It is now a small line under Account: reachable,
      // findable, and not offered as an alternative to the thing they came
      // for. See renderAccount().
    } else {
      // No content admin: the control panel is the only editor there is, so it
      // takes the one editing word and there's no second link to rank it
      // against. Say plainly that it's all there is rather than pointing at a
      // simpler page they can't reach from here.
      cta.textContent = 'Open the editor';
      cta.href = PREFIX + '/handoff';
      ctaWrap.appendChild(cta);
      ctaWrap.appendChild(el('div', 'as-cta__sub',
        'That’s the Adze control panel — for now, the only way into your site. '
        + 'Ask Gabriel below if you’d like something simpler.'));
    }
    page.appendChild(ctaWrap);

    const siteHost = el('div');
    page.appendChild(siteHost);

    const statusHost = el('div');
    page.appendChild(statusHost);

    // .as-data, not a bare div: the hero, chart, stat tiles and hourly strip
    // are one group and need their own tighter gap. A bare wrapper stacked
    // them at 0px inside the landing's own 32px rhythm.
    const dataHost = el('div', 'as-data');
    dataHost.appendChild(skeletonRows(1));
    page.appendChild(dataHost);

    const fbHost = el('div');
    page.appendChild(fbHost);

    renderFeedback(fbHost);
    nameTheButton(cta);

    siteHost.appendChild(skeletonRows(2));
    loadSite().then(s => { if (s) renderSite(siteHost, s); else siteHost.innerHTML = ''; });

    api('GET', '/analytics').then(async r => {
      if (!r) return;
      if (!r.ok) {
        dataHost.innerHTML = '';
        dataHost.appendChild(emptyState('Visits unavailable',
          'Couldn’t load your numbers just now. The rest of this page still works.'));
        return;
      }
      renderVisits(dataHost, await r.json());
    }).catch(() => {
      dataHost.innerHTML = '';
      dataHost.appendChild(emptyState('Visits unavailable', 'Couldn’t reach the server.'));
    });

    api('GET', '/status').then(async r => {
      if (r && r.ok) renderStatus(statusHost, await r.json());
    }).catch(() => {});
  }

  // ── page shell and routing ──────────────────────────────────────────────────

  /* Five sections behind a pill row, which is the content admin's own
   * navigation (.as-nav / .as-tab) rather than a second vocabulary for the same
   * idea. Overview is still the whole of what this page used to be; the rest
   * were features an artist had to be told about to reach. */
  const VIEWS = [
    ['overview', 'Overview'],
    ['files', 'Files'],
    ['history', 'History'],
    ['export', 'Export'],
    ['account', 'Account'],
  ];

  // The hash carries the file path too (#/files/home/content.md) so a view — and
  // a file inside it — survives a reload and answers the back button.
  function route() {
    const parts = (location.hash || '').replace(/^#\/?/, '').split('/').filter(Boolean);
    const id = VIEWS.some(([v]) => v === parts[0]) ? parts[0] : 'overview';
    return { id, rest: parts.slice(1).join('/') };
  }

  let siteCache = null;
  async function loadSite() {
    if (siteCache) return siteCache;
    try {
      const r = await api('GET', '/site');
      if (!r || !r.ok) return null;
      siteCache = await r.json();
      return siteCache;
    } catch (e) { return null; }
  }

  let viewHost = null;
  let tabs = new Map();
  let mounted = { id: null, files: null };

  function renderPage() {
    root.innerHTML = '';
    const page = el('div', 'as-landing');

    const hd = el('div', 'as-landing__hd');
    const who = el('div', 'as-landing__who');
    who.append(el('div', 'as-landing__name', BOOT.name || BOOT.slug));
    if (BOOT.domain) who.append(el('div', 'as-landing__domain', BOOT.domain));
    const logout = el('button', 'as-link', 'Log out');
    logout.onclick = async () => { await api('POST', '/logout'); renderLogin(); };
    hd.append(who, logout);
    page.appendChild(hd);

    const nav = el('div', 'as-nav as-nav--landing');
    tabs = new Map();
    VIEWS.forEach(([id, label]) => {
      const b = el('button', 'as-tab', label);
      b.onclick = () => { location.hash = '#/' + id; };
      tabs.set(id, b);
      nav.appendChild(b);
    });
    page.appendChild(nav);

    viewHost = el('div', 'as-view');
    page.appendChild(viewHost);
    root.appendChild(page);

    mounted = { id: null, files: null };
    showView();
  }

  function showView() {
    if (!viewHost) return;
    const { id, rest } = route();
    tabs.forEach((b, key) => b.classList.toggle('active', key === id));
    // Column width is not set here: admin-shell.css widens the root from
    // `:has(.as-files)`, so it follows the DOM rather than a flag this
    // function would have to remember to clear.

    // Files keeps its list and its scroll position while you move between
    // files — rebuilding the pane per selection would throw away both, and on
    // a phone it would also throw away where you were in a 200-row list.
    if (id === 'files' && mounted.id === 'files' && mounted.files) {
      mounted.files.select(rest);
      return;
    }

    viewHost.innerHTML = '';
    mounted = { id, files: null };

    if (id === 'overview') { renderOverview(viewHost); return; }
    if (id === 'history') { renderHistory(viewHost); return; }
    if (id === 'export') { renderExport(viewHost); return; }
    if (id === 'account') { renderAccount(viewHost); return; }

    if (id === 'files') {
      loadSite().then(s => {
        const files = mountFiles(viewHost, s ? s.pages : []);
        mounted.files = files;
        files.load().then(() => files.select(route().rest));
      });
    }
  }

  async function boot() {
    const r = await fetch(PREFIX + '/status');
    if (r.status === 401) { renderLogin(); return; }
    renderPage();
  }

  window.addEventListener('hashchange', () => {
    // Ignore hash changes while signed out — boot() owns what's on screen then.
    if (viewHost && viewHost.isConnected) showView();
  });

  document.addEventListener('DOMContentLoaded', () => {
    root = document.getElementById('adze-admin-root');
    window.AdzeUI.applyTheme(BOOT.theme);
    window.AdzeUI.trackViewport();
    boot();
  });
})();
