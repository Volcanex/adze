/* file-viewer.js — read-only rendering of one artist file, for the landing
 * page's Files section.
 *
 * The landing page owns fetching and the list; this owns "given a file, what
 * should the artist see". Nothing here writes: every surface that can change a
 * file lives in the control panel, which owns autosave, publish and snapshots.
 *
 * Class prefix is `fv-`. `as-` is shell chrome and `af-` is field editors (see
 * shell/CLAUDE.md → the class-name contract); this is a third owner, and the
 * same rule applies — the strings are built here and styled in
 * admin-shell.css, so renaming one means changing both.
 *
 * Loaded before admin-landing.js, alongside vendored hljs (highlight.js).
 * Highlighting is optional: if the global is missing the viewer still renders,
 * just unhighlighted.
 */
window.AdzeFileViewer = (function () {
  const { el, emptyState } = window.AdzeUI;

  const LANG_BY_EXT = {
    html: 'xml', htm: 'xml', svg: 'xml', xml: 'xml',
    css: 'css', js: 'javascript', json: 'json', py: 'python',
    md: 'xml',            // our .md is HTML+CSS, not markdown — see below
    sh: 'bash', yml: 'yaml', yaml: 'yaml', toml: 'ini', ini: 'ini',
    conf: 'ini', env: 'ini', txt: 'plaintext',
  };
  const FONT_EXTS = ['woff2', 'woff', 'ttf', 'otf'];

  function ext(path) {
    const base = path.split('/').pop();
    return base.includes('.') ? base.split('.').pop().toLowerCase() : '';
  }

  function fmtBytes(n) {
    if (n == null) return '';
    if (n < 1024) return n + ' B';
    if (n < 1024 * 1024) return (n / 1024).toFixed(n < 10240 ? 1 : 0) + ' KB';
    return (n / (1024 * 1024)).toFixed(1) + ' MB';
  }

  /* A page's source file. Its *directory* is the page, so `home/content.md` is
   * the home page — that mapping is compile.py's, not ours to invent. */
  function isPageSource(path) {
    return path === 'content.md' || path.endsWith('/content.md');
  }

  // ── code ───────────────────────────────────────────────────────────────────

  /* Line numbers live in their own <pre> beside the code rather than being
   * woven into it. highlight.js emits spans that legitimately run across line
   * breaks, so splitting its output on \n to build numbered rows tears them in
   * half — the usual fix is re-opening every span per line, which is a parser
   * we don't need. Two panes in one scroll box stay in step for free.
   *
   * Wrapping breaks that alignment (one logical line becomes several visual
   * ones), so turning wrap on hides the gutter instead of letting it lie. */
  function codeBlock(text, language) {
    const box = el('div', 'fv-code');

    const gutter = el('pre', 'fv-code__nums');
    const lines = text.split('\n');
    gutter.textContent = lines.map((_, i) => i + 1).join('\n');

    const pre = el('pre', 'fv-code__body');
    const code = el('code');
    let done = false;
    if (window.hljs && language && language !== 'plaintext') {
      try {
        code.innerHTML = window.hljs.highlight(text, {
          language, ignoreIllegals: true,
        }).value;
        done = true;
      } catch (e) { /* fall through to plain text */ }
    }
    if (!done) code.textContent = text;
    pre.appendChild(code);

    const scroller = el('div', 'fv-code__scroll');
    scroller.append(gutter, pre);
    box.appendChild(scroller);
    return { el: box, scroller, setWrap(on) { box.classList.toggle('is-wrapped', on); } };
  }

  function codeSection(title, text, language, opts) {
    const o = opts || {};
    const sec = el('section', 'fv-section');
    const hd = el('div', 'fv-section__hd');
    hd.appendChild(el('span', 'adze-label', title));
    if (o.note) hd.appendChild(el('span', 'fv-section__note', o.note));
    const tools = el('div', 'fv-tools');

    const block = codeBlock(text, language);

    const wrap = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Wrap');
    let wrapped = false;
    wrap.onclick = () => {
      wrapped = !wrapped;
      block.setWrap(wrapped);
      wrap.classList.toggle('is-on', wrapped);
    };

    const copy = el('button', 'as-btn as-btn-sm as-btn-quiet', 'Copy');
    copy.onclick = async () => {
      try {
        await navigator.clipboard.writeText(text);
        copy.textContent = 'Copied';
        setTimeout(() => { copy.textContent = 'Copy'; }, 1500);
      } catch (e) {
        copy.textContent = 'Press ⌘C';
      }
    };

    tools.append(wrap, copy);
    hd.appendChild(tools);
    sec.append(hd, block.el);
    return sec;
  }

  // ── content.md, explained ──────────────────────────────────────────────────

  /* The one file type an artist genuinely cannot read as-is, and the reason
   * this viewer exists. Despite the extension it is not markdown: compile.py's
   * parse_content pulls a <style> block, an <html> block and any <meta> tags
   * that appear before them, and ignores everything else in the file. Showing
   * it as one undifferentiated blob is what makes an artist think their site is
   * incomprehensible. Keep this in step with compile.py parse_content. */
  function parsePageSource(raw) {
    const css = /<style>([\s\S]*?)<\/style>/i.exec(raw);
    const html = /<html>([\s\S]*?)<\/html>/i.exec(raw);
    const cut = raw.indexOf('<style>') !== -1 ? raw.indexOf('<style>')
      : raw.indexOf('<html>') !== -1 ? raw.indexOf('<html>') : raw.length;
    const metas = (raw.slice(0, cut).match(/<meta[^>]+>/gi) || []);
    return {
      css: css ? css[1].trim() : '',
      html: html ? html[1].trim() : '',
      metas,
      strayText: !html && !css,
    };
  }

  /* Copy slots, read the way the compiler reads them: parse the HTML region as
   * HTML and query it. A regex would have to re-derive copy_slots.py's masking
   * of <script>/<style> bodies (one of which really does contain a data-copy
   * attribute — the email widget's copy button). A DOMParser document is inert
   * — no scripts run, no images fetch — so parsing is the cheap, correct move.
   */
  function copySlots(htmlRegion) {
    if (!htmlRegion) return [];
    let doc;
    try {
      doc = new DOMParser().parseFromString(htmlRegion, 'text/html');
    } catch (e) { return []; }
    return Array.from(doc.querySelectorAll('[data-copy], [data-copy-rich]')).map(node => {
      const rich = node.hasAttribute('data-copy-rich');
      return {
        id: node.getAttribute(rich ? 'data-copy-rich' : 'data-copy'),
        rich,
        text: (node.textContent || '').trim().replace(/\s+/g, ' '),
      };
    }).filter(s => s.id);
  }

  // Comment placeholders compile.py fills in at publish time. Source-visible
  // only: config-driven injections (image pipeline, loom, analytics) leave no
  // mark in this file, so claiming anything about them here would be a guess.
  const PLACEHOLDERS = [
    ['<!-- EXHIBITIONS_BLOCK -->',
     'Becomes your full exhibition list when the site is published — every entry, newest first, each one linking to its own page.'],
  ];

  function renderPageSource(host, ctx) {
    const raw = ctx.file.content;
    const parsed = parsePageSource(raw);
    const slots = copySlots(parsed.html);
    const found = PLACEHOLDERS.filter(([marker]) => raw.includes(marker));

    const intro = el('div', 'fv-explain');
    intro.appendChild(el('p', null,
      'This is the source of one page. The name says .md, but it isn’t markdown — '
      + 'it holds the page’s styling and its content, and Adze turns the two into '
      + 'the real page every time you publish.'));
    if (ctx.pageUrl) {
      const a = el('a', 'as-link', 'Open this page on your site →');
      a.href = ctx.pageUrl;
      a.target = '_blank';
      a.rel = 'noopener';
      intro.appendChild(a);
    }
    host.appendChild(intro);

    if (parsed.strayText) {
      host.appendChild(emptyState('Nothing recognisable in here',
        'This file has neither a styles block nor a content block, so publishing '
        + 'it would produce an empty page. Worth mentioning to Gabriel.'));
    }

    if (slots.length) {
      const sec = el('section', 'fv-section');
      const hd = el('div', 'fv-section__hd');
      hd.appendChild(el('span', 'adze-label', 'Text you can edit'));
      hd.appendChild(el('span', 'fv-section__note',
        slots.length + (slots.length === 1 ? ' piece' : ' pieces')));
      sec.appendChild(hd);
      const list = el('div', 'fv-slots');
      slots.forEach(s => {
        const row = el('div', 'fv-slot');
        row.append(
          el('div', 'fv-slot__id', s.id + (s.rich ? ' (formatted)' : '')),
          el('div', 'fv-slot__text', s.text || '(empty)'));
        list.appendChild(row);
      });
      sec.appendChild(list);
      sec.appendChild(el('p', 'fv-hint',
        'These are the parts of the page the editor lets you change. What’s shown '
        + 'here is what the page says if you never touch it — your edits are kept '
        + 'separately and applied on top when you publish.'));
      host.appendChild(sec);
    }

    if (found.length) {
      const sec = el('section', 'fv-section');
      sec.appendChild(el('span', 'adze-label', 'Filled in when you publish'));
      found.forEach(([marker, why]) => {
        const row = el('div', 'fv-slot');
        row.append(el('div', 'fv-slot__id', marker), el('div', 'fv-slot__text', why));
        sec.appendChild(row);
      });
      host.appendChild(sec);
    }

    if (parsed.metas.length) {
      host.appendChild(codeSection('Page tags', parsed.metas.join('\n'), 'xml',
        { note: 'search engines and link previews' }));
    }
    if (parsed.css) {
      host.appendChild(codeSection('Styling', parsed.css, 'css',
        { note: 'your site-wide styles are added in front of this' }));
    }
    if (parsed.html) {
      host.appendChild(codeSection('Content', parsed.html, 'xml',
        { note: 'the words and pictures on the page' }));
    }
  }

  // ── json ───────────────────────────────────────────────────────────────────

  // Plain-language names for the config keys an artist is most likely to open
  // and least likely to recognise. Anything unlisted still renders — it just
  // shows the value, with no claim about what it means.
  const CONFIG_KEYS = {
    name: 'Your name, as the site shows it',
    slug: 'The short internal id for your site',
    domain: 'The web address this site is served on',
    title: 'The page’s title — browser tab and search results',
    hidden: 'Kept out of navigation when true',
    features: 'Optional extras switched on for your site',
    content_types: 'The kinds of thing you can add in the editor',
    seo: 'How your site describes itself to search engines',
    robots: 'Custom instructions for search-engine crawlers',
    admin_theme: 'The colours of this admin page',
    favicon: 'The little icon in the browser tab',
    favicon_color: 'Colour of the generated tab icon',
  };

  function renderJson(host, ctx) {
    let parsed = null;
    try { parsed = JSON.parse(ctx.file.content); } catch (e) { /* show raw */ }

    if (parsed && !Array.isArray(parsed) && typeof parsed === 'object'
        && ctx.file.path.endsWith('config.json')) {
      const sec = el('section', 'fv-section');
      sec.appendChild(el('span', 'adze-label', 'What this sets'));
      const list = el('div', 'fv-slots');
      Object.keys(parsed).forEach(k => {
        const v = parsed[k];
        const summary = (v && typeof v === 'object')
          ? (Array.isArray(v) ? `${v.length} item${v.length === 1 ? '' : 's'}`
                              : `${Object.keys(v).length} setting${Object.keys(v).length === 1 ? '' : 's'}`)
          : String(v);
        const row = el('div', 'fv-slot');
        row.append(el('div', 'fv-slot__id', CONFIG_KEYS[k] || k),
                   el('div', 'fv-slot__text', summary));
        list.appendChild(row);
      });
      sec.appendChild(list);
      host.appendChild(sec);
    }

    const pretty = parsed !== null ? JSON.stringify(parsed, null, 2) : ctx.file.content;
    host.appendChild(codeSection(
      parsed !== null ? 'The file' : 'The file (not valid JSON — shown as written)',
      pretty, 'json'));
  }

  // ── binary kinds ───────────────────────────────────────────────────────────

  function downloadUrl(ctx, attach) {
    return ctx.prefix + '/file-raw?path=' + encodeURIComponent(ctx.file.path)
      + (attach ? '&download=1' : '');
  }

  function downloadButton(ctx, label) {
    const a = el('a', 'as-btn as-btn-sm', label || 'Download');
    a.href = downloadUrl(ctx, true);
    return a;
  }

  function renderImage(host, ctx) {
    const sec = el('section', 'fv-section');
    const hd = el('div', 'fv-section__hd');
    hd.appendChild(el('span', 'adze-label', 'Picture'));
    const meta = el('span', 'fv-section__note', fmtBytes(ctx.file.size));
    hd.appendChild(meta);
    const tools = el('div', 'fv-tools');
    tools.appendChild(downloadButton(ctx));
    hd.appendChild(tools);

    const frame = el('div', 'fv-image');
    const img = el('img');
    img.src = downloadUrl(ctx, false);
    img.alt = ctx.file.path;
    img.loading = 'lazy';
    // Pixel dimensions matter here in a way they don't on the site: this is the
    // view an artist checks when a photo looks soft or a logo looks huge.
    img.onload = () => {
      meta.textContent = `${img.naturalWidth} × ${img.naturalHeight} · ${fmtBytes(ctx.file.size)}`;
    };
    img.onerror = () => { frame.replaceChildren(emptyState('Couldn’t load that image', '')); };
    frame.appendChild(img);

    sec.append(hd, frame);
    host.appendChild(sec);
  }

  /* A font file is the one "binary" an artist can actually be shown something
   * useful about: load it and set some words in it. FontFace is inert if the
   * file is broken, and the catch leaves the download button standing. */
  function renderFont(host, ctx) {
    const sec = el('section', 'fv-section');
    const hd = el('div', 'fv-section__hd');
    hd.appendChild(el('span', 'adze-label', 'Typeface'));
    hd.appendChild(el('span', 'fv-section__note', fmtBytes(ctx.file.size)));
    const tools = el('div', 'fv-tools');
    tools.appendChild(downloadButton(ctx));
    hd.appendChild(tools);
    sec.appendChild(hd);

    const sample = el('div', 'fv-font');
    sample.textContent = 'Aa Bb Cc — 0123456789';
    sec.appendChild(sample);
    sec.appendChild(el('p', 'fv-hint', ctx.file.path.split('/').pop()));
    host.appendChild(sec);

    const family = 'fvFont' + Math.random().toString(36).slice(2, 8);
    try {
      const face = new FontFace(family, `url(${JSON.stringify(downloadUrl(ctx, false))})`);
      face.load().then(loaded => {
        document.fonts.add(loaded);
        sample.style.fontFamily = `"${family}"`;
      }).catch(() => { sample.classList.add('is-unavailable'); });
    } catch (e) {
      sample.classList.add('is-unavailable');
    }
  }

  function renderOpaque(host, ctx, message) {
    const sec = el('section', 'fv-section');
    sec.appendChild(emptyState(
      message || 'Nothing to show for this one',
      `${fmtBytes(ctx.file.size)} — download it to open it in something that understands it.`));
    const acts = el('div', 'as-actions');
    acts.appendChild(downloadButton(ctx));
    sec.appendChild(acts);
    host.appendChild(sec);
  }

  // ── entry point ────────────────────────────────────────────────────────────

  /* ctx: { prefix, file: {path, kind, size, content?, error?}, pageUrl? }
   *
   * `content` absent means the server declined to send text (binary, too
   * large, not UTF-8) — the reason is in `error` and the file still gets a
   * download button. Nothing here refetches; the landing page owns the calls.
   */
  function render(host, ctx) {
    host.innerHTML = '';
    const f = ctx.file;

    const head = el('div', 'fv-head');
    head.append(el('h2', 'fv-head__path', f.path),
                el('span', 'fv-head__meta', fmtBytes(f.size)));
    host.appendChild(head);

    const e = ext(f.path);

    if (f.kind === 'image') { renderImage(host, ctx); return; }
    if (FONT_EXTS.includes(e)) { renderFont(host, ctx); return; }

    if (typeof f.content !== 'string') {
      renderOpaque(host, ctx, f.error && f.error.startsWith('File too large')
        ? 'Too big to show here' : undefined);
      return;
    }

    if (isPageSource(f.path)) { renderPageSource(host, ctx); return; }
    if (e === 'json') { renderJson(host, ctx); return; }

    // SVG is both a picture and a text file; artists want the picture first.
    if (e === 'svg') {
      const frame = el('div', 'fv-image');
      const img = el('img');
      img.src = downloadUrl(ctx, false);
      img.alt = f.path;
      frame.appendChild(img);
      host.appendChild(frame);
    }

    host.appendChild(codeSection('The file', f.content, LANG_BY_EXT[e] || 'plaintext'));
  }

  return { render, isPageSource, fmtBytes };
})();
