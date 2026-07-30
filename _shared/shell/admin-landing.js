/* admin-landing.js — the artist landing page at theirdomain.com/admin.
 *
 * One page for every artist. A little traffic, one big button into the content
 * admin, a quieter link to the advanced editor, whether anything is down, and
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
    if (r.status === 401) { renderLogin(); return null; }
    return r;
  }

  function fmtCount(n) {
    if (n == null) return '—';
    if (n < 10000) return n.toLocaleString();
    return (n / 1000).toFixed(n < 100000 ? 1 : 0) + 'K';
  }

  function fmtDur(s) {
    if (!s) return '—';
    if (s < 60) return s + 's';
    return Math.floor(s / 60) + 'm ' + (s % 60) + 's';
  }

  function shortDate(iso) {
    const d = new Date(iso + 'T00:00:00');
    return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
  }

  // ── login ───────────────────────────────────────────────────────────────────
  function renderLogin() {
    root.innerHTML = '';
    const box = el('div', 'as-login');
    box.appendChild(el('h1', null, BOOT.name || 'Sign in'));
    const who = el('input', 'af-input');
    who.type = 'text'; who.placeholder = 'Your name or email (optional)';
    who.autocomplete = 'username';
    const pw = el('input', 'af-input');
    pw.type = 'password'; pw.placeholder = 'Password'; pw.autocomplete = 'current-password';
    const err = el('div', 'as-err');
    const btn = el('button', 'as-btn', 'Enter');
    async function submit() {
      const r = await fetch(PREFIX + '/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: who.value.trim(), password: pw.value }),
      });
      if (r.ok) boot();
      else err.textContent = who.value.trim()
        ? 'That name and password don’t match.' : 'Wrong password.';
    }
    btn.onclick = () => withBusy(btn, submit);
    [who, pw].forEach(i => i.addEventListener(
      'keydown', e => { if (e.key === 'Enter') withBusy(btn, submit); }));
    box.append(who, pw, btn, err);
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

    const hero = el('div', 'as-hero');
    hero.appendChild(el('div', 'as-hero__value', fmtCount(a.month)));
    hero.appendChild(el('div', 'as-hero__label adze-label',
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
      hero.appendChild(d);
    }
    host.appendChild(hero);

    if (a.month === 0 && days >= 7) {
      host.appendChild(el('p', 'as-hero__label',
        'Nobody has found the site yet. That’s normal for a new site — sharing the link is what changes it.'));
      return;
    }

    const chart = el('div', 'as-card');
    const chd = el('div', 'as-card__hd');
    chd.append(el('span', 'adze-label', 'Visits'),
               el('span', 'as-card__meta', days < 7 ? `since ${new Date(since * 1000)
                 .toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}` : 'last 30 days'));
    chart.append(chd, areaChart(a.daily.slice(days < 7 ? -Math.max(days + 1, 2) : 0)));
    host.appendChild(chart);

    const stats = el('div', 'as-stats');
    [['Today', fmtCount(a.today)], ['This week', fmtCount(a.week)],
     ['Avg. visit', fmtDur(a.avg_duration)]].forEach(([label, value]) => {
      const t = el('div', 'as-stat');
      t.append(el('div', 'as-stat__value adze-numeric', value),
               el('div', 'as-stat__label adze-label', label));
      stats.appendChild(t);
    });
    host.appendChild(stats);

    if (a.hourly && a.hourly.some(v => v > 0)) {
      const hrs = el('div', 'as-card');
      const hhd = el('div', 'as-card__hd');
      hhd.appendChild(el('span', 'adze-label', 'When people visit'));
      hrs.append(hhd, hourBars(a.hourly));
      host.appendChild(hrs);
    }
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
    const msg = el('textarea', 'af-textarea');
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

  // ── page ────────────────────────────────────────────────────────────────────
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

    const dataHost = el('div');
    dataHost.appendChild(skeletonRows(3));
    page.appendChild(dataHost);

    const statusHost = el('div');
    page.appendChild(statusHost);

    // Exactly one primary button on the page. When the artist has no content
    // admin the primary points at the advanced editor instead, and the
    // secondary link is dropped rather than duplicated.
    const ctaWrap = el('div');
    const cta = el('a', 'as-btn as-cta');
    if (BOOT.contentUrl) {
      cta.textContent = 'Edit your site';
      cta.href = BOOT.contentUrl;
      ctaWrap.appendChild(cta);
      const adv = el('a', 'as-advanced', 'Advanced editing →');
      adv.href = PREFIX + '/handoff';
      const advWrap = el('div', 'as-cta__sub');
      advWrap.appendChild(adv);
      ctaWrap.appendChild(advWrap);
    } else {
      cta.textContent = 'Open the editor';
      cta.href = PREFIX + '/handoff';
      ctaWrap.appendChild(cta);
      ctaWrap.appendChild(el('div', 'as-cta__sub',
        'Simple content editing isn’t set up on your site yet — ask Gabriel below.'));
    }
    page.appendChild(ctaWrap);

    const fbHost = el('div');
    page.appendChild(fbHost);
    root.appendChild(page);

    renderFeedback(fbHost);

    api('GET', '/analytics').then(async r => {
      if (!r) return;
      if (!r.ok) {
        dataHost.innerHTML = '';
        dataHost.appendChild(emptyState('Visits unavailable',
          'Couldn’t load your numbers just now. The rest of this page still works.'));
        return;
      }
      renderData(dataHost, await r.json());
    }).catch(() => {
      dataHost.innerHTML = '';
      dataHost.appendChild(emptyState('Visits unavailable', 'Couldn’t reach the server.'));
    });

    api('GET', '/status').then(async r => {
      if (r && r.ok) renderStatus(statusHost, await r.json());
    }).catch(() => {});
  }

  async function boot() {
    const r = await fetch(PREFIX + '/status');
    if (r.status === 401) { renderLogin(); return; }
    renderPage();
  }

  document.addEventListener('DOMContentLoaded', () => {
    root = document.getElementById('adze-admin-root');
    window.AdzeUI.applyTheme(BOOT.theme);
    boot();
  });
})();
