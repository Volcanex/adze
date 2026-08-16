/* field-editors.js — the pluggable field-type registry.
 *
 * A field type maps to one editor. Adding a new type later = one register()
 * call, no shell or schema changes. Each editor is:
 *     fn(fieldName, fieldDef, value, ctx) -> { el, value() }
 * where el is the DOM node to mount and value() reads the current value on save.
 * Image editors persist immediately via ctx (server owns the files) and their
 * value() is unused — the shell excludes image fields from the save body.
 *
 * ctx: { prefix, uploadImage(fieldName, file), removeImage(fieldName, index),
 *        uploadFile(fieldName, file), removeFile(fieldName, index),
 *        toast(msg, kind), itemId }  (itemId is always set — "+ Add" creates a
 *        draft server-side, so an editor never has to stage anything client-side)
 *
 * role(fieldDef) exports what a type IS ('identity' | 'media' | 'short' | 'long'
 * | 'tags') for the shell to lay out against; the shell owns what each role looks
 * like, this file owns which role a type has.
 */
window.AdzeFields = (function () {
  const registry = {};
  const register = (type, fn) => { registry[type] = fn; };

  function labelWrap(fieldName, fieldDef, inner) {
    const wrap = document.createElement('div');
    wrap.className = 'af-field';
    const lab = document.createElement('label');
    lab.textContent = fieldDef.label || fieldName;
    if (fieldDef.required) lab.innerHTML += ' <span class="af-req">*</span>';
    wrap.appendChild(lab);
    wrap.appendChild(inner);
    return wrap;
  }

  // ── scalars ────────────────────────────────────────────────────────────────
  register('text', (name, def, value) => {
    const i = document.createElement('input');
    i.type = 'text'; i.className = 'af-input'; i.value = value == null ? '' : value;
    return { el: labelWrap(name, def, i), value: () => i.value.trim() };
  });

  register('textarea', (name, def, value) => {
    const t = document.createElement('textarea');
    t.className = 'af-input af-textarea'; t.value = value == null ? '' : value;
    return { el: labelWrap(name, def, t), value: () => t.value };
  });

  register('number', (name, def, value) => {
    const i = document.createElement('input');
    i.type = 'number'; i.className = 'af-input'; i.value = value == null ? '' : value;
    return { el: labelWrap(name, def, i), value: () => (i.value === '' ? null : Number(i.value)) };
  });

  register('date', (name, def, value) => {
    const i = document.createElement('input');
    i.type = 'date'; i.className = 'af-input'; i.value = value == null ? '' : value;
    return { el: labelWrap(name, def, i), value: () => i.value };
  });

  register('boolean', (name, def, value) => {
    const i = document.createElement('input');
    i.type = 'checkbox'; i.className = 'af-check'; i.checked = !!value;
    const row = document.createElement('div'); row.className = 'af-checkrow';
    row.appendChild(i);
    const span = document.createElement('span'); span.textContent = def.label || name;
    row.appendChild(span);
    const wrap = document.createElement('div'); wrap.className = 'af-field'; wrap.appendChild(row);
    return { el: wrap, value: () => i.checked };
  });

  register('select', (name, def, value) => {
    const s = document.createElement('select'); s.className = 'af-input';
    (def.options || []).forEach(opt => {
      const o = document.createElement('option');
      o.value = o.textContent = opt; if (opt === value) o.selected = true;
      s.appendChild(o);
    });
    return { el: labelWrap(name, def, s), value: () => s.value };
  });

  // Tags drive the filter rows on the artist's public pages, so the set has to
  // stay small and consistent. Free text alone made that the artist's problem:
  // one typo becomes a second tag, and the page silently splits a filter in
  // two. The tags already in use are offered two ways — a datalist for
  // type-ahead, and clickable chips, because a datalist is effectively
  // invisible on touch.
  let tagListSeq = 0;
  register('tags', (name, def, value, ctx) => {
    const wrap = document.createElement('div');
    const box = document.createElement('div'); box.className = 'af-tags';
    let tags = Array.isArray(value) ? value.slice() : [];
    const input = document.createElement('input');
    input.type = 'text'; input.className = 'af-input'; input.placeholder = 'type + Enter';

    const known = (ctx && typeof ctx.knownTags === 'function') ? (ctx.knownTags(name) || []) : [];
    let listEl = null;
    if (known.length) {
      const id = 'af-taglist-' + (++tagListSeq);
      listEl = document.createElement('datalist'); listEl.id = id;
      known.forEach(t => { const o = document.createElement('option'); o.value = t; listEl.appendChild(o); });
      input.setAttribute('list', id);
    }

    const sug = document.createElement('div'); sug.className = 'af-tagsug';

    function has(t) { return tags.some(x => x.toLowerCase() === t.toLowerCase()); }
    function add(raw) {
      const v = (raw || '').trim();
      if (!v) return;
      // Reuse the existing casing when it is the same word, so "Philosophy"
      // typed over an existing "philosophy" doesn't become a second tag.
      const match = known.find(k => k.toLowerCase() === v.toLowerCase());
      if (!has(v)) tags.push(match || v);
      input.value = '';
      paint();
    }
    function paint() {
      box.querySelectorAll('.af-chip').forEach(c => c.remove());
      tags.forEach((t, i) => {
        const chip = document.createElement('span'); chip.className = 'af-chip';
        chip.textContent = t;
        const x = document.createElement('button'); x.textContent = '×'; x.type = 'button';
        x.onclick = () => { tags.splice(i, 1); paint(); };
        chip.appendChild(x); box.insertBefore(chip, input);
      });
      // Only the ones not already on this item; the list empties as they're used.
      sug.innerHTML = '';
      const left = known.filter(t => !has(t));
      if (left.length) {
        const lab = document.createElement('span'); lab.className = 'af-tagsug-label';
        lab.textContent = 'In use:';
        sug.appendChild(lab);
        left.forEach(t => {
          const b = document.createElement('button');
          b.type = 'button'; b.className = 'af-tagsug-chip'; b.textContent = t;
          b.onclick = () => add(t);
          sug.appendChild(b);
        });
      }
    }

    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); add(input.value); }
      // Backspace on an empty box removes the last tag — standard for this control.
      else if (e.key === 'Backspace' && !input.value && tags.length) { tags.pop(); paint(); }
    });
    // Picking from the datalist fires `change`, not Enter.
    input.addEventListener('change', () => { if (input.value.trim()) add(input.value); });
    // A tag typed but never confirmed would otherwise be silently dropped on save.
    input.addEventListener('blur', () => { if (input.value.trim()) add(input.value); });

    box.appendChild(input);
    if (listEl) box.appendChild(listEl);
    paint();
    wrap.appendChild(box);
    wrap.appendChild(sug);
    return { el: labelWrap(name, def, wrap), value: () => tags };
  });

  // ── markdown (EasyMDE) ───────────────────────────────────────────────────────
  register('markdown', (name, def, value) => {
    const t = document.createElement('textarea');
    const wrap = labelWrap(name, def, t);
    let mde = null;
    // EasyMDE needs the element in the document to size itself.
    setTimeout(() => {
      if (window.EasyMDE) {
        mde = new EasyMDE({
          element: t, initialValue: value == null ? '' : value,
          spellChecker: false, status: false,
          toolbar: ['bold', 'italic', 'heading', '|', 'unordered-list', 'ordered-list', 'link', '|', 'preview'],
        });
      } else { t.className = 'af-input af-textarea'; t.value = value == null ? '' : value; }
    }, 0);
    return { el: wrap, value: () => (mde ? mde.value() : t.value) };
  });

  // ── richtext (Quill) — the reference WYSIWYG ────────────────────────────────
  register('richtext', (name, def, value) => {
    const host = document.createElement('div'); host.className = 'af-rich';
    const wrap = labelWrap(name, def, host);
    let q = null;
    setTimeout(() => {
      if (window.Quill) {
        q = new Quill(host, {
          theme: 'snow',
          modules: { toolbar: [['bold', 'italic', 'underline'], ['link', 'blockquote'],
                               [{ header: [2, 3, false] }], [{ list: 'ordered' }, { list: 'bullet' }], ['clean']] },
        });
        if (value) q.clipboard.dangerouslyPasteHTML(value);
      } else {
        host.contentEditable = 'true'; host.className = 'af-rich af-input'; host.innerHTML = value || '';
      }
    }, 0);
    return { el: wrap, value: () => (q ? q.root.innerHTML : host.innerHTML) };
  });

  // ── copy editors (the sitewide copy surface) ────────────────────────────────
  // Artist pages are hand-authored HTML/CSS/JS and only marked runs of text are
  // editable. The rule both of these encode: an artist may only apply formatting
  // that the page's own CSS already styles. Rose's about page is 243 lines of
  // pixel-precise hand-written CSS — an unbounded toolbar is how that design gets
  // destroyed, by the one person we built it for. So the restriction is the
  // feature, and it is enforced at the editor, not left to review.

  function htmlToText(html) {
    // DOMParser, not a detached div: an inert document won't fetch or run
    // anything that happens to be sitting in the stored value.
    return new DOMParser().parseFromString(String(html == null ? '' : html), 'text/html').body.textContent || '';
  }

  function escapeHtml(text) {
    const d = document.createElement('div'); d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  register('copytext', (name, def, value) => {
    const t = document.createElement('textarea');
    // af-textarea is a modifier — it only sets height and resize, so it must keep
    // af-input alongside it or the control loses the palette and renders as a raw
    // white box on every dark artist theme.
    t.className = 'af-input af-textarea af-copy';
    t.value = value == null ? '' : String(value);
    const autosize = () => { t.style.height = 'auto'; t.style.height = t.scrollHeight + 'px'; };
    t.addEventListener('input', autosize);
    setTimeout(autosize, 0);  // scrollHeight reads 0 until the element is in the document
    return { el: labelWrap(name, def, t), value: () => t.value };
  });

  // The permitted formats, stated once and used three ways below: Quill's blot
  // registry, the toolbar, and the paste sanitiser. Adding to this list is a
  // design decision about every artist page at once, not a convenience.
  const COPY_FORMATS = ['bold', 'italic', 'link'];

  // A copy slot is always the INNER content of an element the artist already
  // wrote — `<p class="lede" data-copy-rich="lede">…</p>`, or an `<li>`. So this
  // value has to be an inline fragment. Quill thinks in blocks and would hand
  // back `<p>…</p>`: nested inside the slot's own `<p>` the browser auto-closes
  // the outer tag and `class="lede"` stops applying, and copy_slots.sanitize_rich
  // (whose whitelist is b/strong/i/em/a/br — no p) strips the tags to nothing,
  // silently running two paragraphs into one line. <br> is the only break the
  // server permits, so that is what a line break becomes.
  function inlineHtml(q) {
    if (q.getLength() <= 1) return '';
    const lines = Array.from(q.root.children).map(node => {
      const html = node.innerHTML.trim();
      return html === '<br>' ? '' : html;  // Quill's rendering of an empty line
    });
    while (lines.length && lines[lines.length - 1] === '') lines.pop();
    return lines.join('<br>');
  }

  function copyHref(href) {
    const v = String(href == null ? '' : href).trim();
    if (!v) return null;
    const scheme = /^([a-z][a-z0-9+.-]*):/i.exec(v);
    if (!scheme) return v;  // relative, in-page or query — same site, fine
    return /^(https?|mailto|tel)$/i.test(scheme[1]) ? v : null;
  }

  register('copyrich', (name, def, value) => {
    const host = document.createElement('div'); host.className = 'af-copy af-copy--rich';
    const wrap = labelWrap(name, def, host);
    let q = null, plain = null;
    setTimeout(() => {
      if (window.Quill) {
        const Delta = Quill.import('delta');
        q = new Quill(host, {
          theme: 'snow',
          // A blot whitelist, not merely a smaller toolbar. Quill builds its
          // registry from this list plus its six core blots, so header, list,
          // blockquote, image, colour, size and align have nothing to land on
          // however they arrive — button, keyboard shortcut or paste. It is also
          // what keeps Enter to a plain paragraph: no other block blot exists.
          formats: COPY_FORMATS,
          modules: { toolbar: [['bold', 'italic', 'link']] },  // no 'clean' — it strips the wrapper too
        });
        // Paste bypasses the toolbar entirely, so it gets its own gate. This runs
        // for every element in the pasted tree and rebuilds its delta from the
        // permitted attributes only, which is what stops a Word or webpage paste
        // arriving with its own styling intact.
        q.clipboard.addMatcher(Node.ELEMENT_NODE, (node, delta) => {
          const out = new Delta();
          delta.ops.forEach(op => {
            if (typeof op.insert !== 'string') return;  // embeds (images, video, formulas) carry no copy
            const attrs = {};
            COPY_FORMATS.forEach(f => {
              const v = op.attributes && op.attributes[f];
              if (!v) return;
              if (f === 'link') { const href = copyHref(v); if (href) attrs.link = href; }
              else attrs[f] = v;
            });
            out.insert(op.insert, Object.keys(attrs).length ? attrs : undefined);
          });
          return out;
        });
        if (value) q.clipboard.dangerouslyPasteHTML(String(value));
      } else {
        // Quill missing means the vendored asset failed to load. Degrade to plain
        // text rather than a half-built rich editor: formatting in the stored
        // value shows as text and is lost on save, which is visible, where
        // emitting broken markup onto the live page would not be.
        plain = document.createElement('textarea');
        plain.className = 'af-input af-textarea af-copy';
        plain.value = htmlToText(value);
        host.replaceWith(plain);
      }
    }, 0);
    return {
      el: wrap,
      value: () => {
        if (q) return inlineHtml(q);
        // the fallback owes the slot the same inline fragment, so its line
        // breaks become <br> too — after escaping, never before.
        if (plain) return escapeHtml(plain.value).replace(/\r?\n/g, '<br>');
        return value == null ? '' : String(value);  // saved before the editor mounted — keep what was there
      },
    };
  });

  // ── image (persists immediately via ctx) ────────────────────────────────────
  // An item is created as a draft the moment "+ Add" is clicked, so there is
  // always an id to hang uploads on. There is deliberately no "save this first"
  // pathway and no client-side staging: asking an artist to describe a painting
  // before they are allowed to show it is the implementation's problem, not theirs.
  register('image', (name, def, value, ctx) => {
    const wrap = document.createElement('div'); wrap.className = 'af-field';
    const lab = document.createElement('label'); lab.textContent = def.label || name; wrap.appendChild(lab);
    const gallery = document.createElement('div'); gallery.className = 'af-gallery'; wrap.appendChild(gallery);
    let current = def.multiple ? (Array.isArray(value) ? value.slice() : []) : (value || null);
    const fresh = new Set();  // paths that just landed — animated once, then forgotten

    function entries() { return def.multiple ? current : (current ? [current] : []); }
    // card is the light thumbnail tier; src/full are the older shapes, and a bare
    // string is the oldest. Never widen this to a raw <img> of the full-size file.
    function pathOf(entry) { return entry.card || entry.src || entry.full || entry; }

    function paint() {
      gallery.innerHTML = '';
      entries().forEach((entry, i) => {
        const cell = document.createElement('div'); cell.className = 'af-thumb';
        // image paths are stored relative to the artist's assets/ dir; the admin
        // runs on the artist's own domain so /assets/<rel> resolves via nginx.
        const rel = pathOf(entry);
        const img = document.createElement('img');
        img.loading = 'lazy'; img.decoding = 'async';
        img.src = rel.startsWith('assets/') || rel.startsWith('/') ? ('/' + rel.replace(/^\//, '')) : ('/assets/' + rel);
        cell.appendChild(img);
        if (fresh.has(rel)) {
          cell.classList.add('af-thumb--new');
          fresh.delete(rel);  // drop it here, so the next paint doesn't re-animate the set
          cell.addEventListener('animationend', () => cell.classList.remove('af-thumb--new'), { once: true });
          // if the CSS ever styles this state without an animation, animationend
          // never fires and the class would stick to a cell that is no longer new.
          setTimeout(() => cell.classList.remove('af-thumb--new'), 2000);
        }
        const x = document.createElement('button'); x.type = 'button'; x.textContent = '×'; x.title = 'remove';
        x.onclick = async () => {
          const item = await ctx.removeImage(name, def.multiple ? i : null);
          if (item) { current = def.multiple ? (item[name] || []) : (item[name] || null); paint(); }
        };
        cell.appendChild(x); gallery.appendChild(cell);
      });
    }

    const file = document.createElement('input');
    file.type = 'file'; file.accept = 'image/*'; file.className = 'af-file';
    if (def.multiple) file.multiple = true;

    // One request per file rather than one batched request: a 40MB set behind a
    // single POST fails as a unit, and the artist cannot tell which file did it.
    async function upload(files) {
      if (!files.length) return;
      file.disabled = true;
      for (const f of files) {
        const before = new Set(entries().map(pathOf));
        let item = null;
        try { item = await ctx.uploadImage(name, f); }
        catch (e) { item = null; }
        if (!item) { ctx.toast('Could not upload ' + f.name + '.', 'err'); continue; }
        current = def.multiple ? (item[name] || []) : (item[name] || null);
        entries().map(pathOf).forEach(p => { if (!before.has(p)) fresh.add(p); });
        paint();  // repaint per file, so a long set fills in as it goes
      }
      file.disabled = false;
      file.value = '';
    }

    file.onchange = () => upload(Array.from(file.files || []));

    if (def.multiple && ctx.itemId) {
      // dragenter/dragleave also fire for every child the pointer crosses, so the
      // class has to be reference-counted or it flickers off over each thumbnail.
      let depth = 0;
      const stop = e => { e.preventDefault(); e.stopPropagation(); };
      gallery.addEventListener('dragenter', e => {
        stop(e); depth += 1; gallery.classList.add('af-gallery--dropping');
      });
      gallery.addEventListener('dragover', e => {
        stop(e); if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
      });
      gallery.addEventListener('dragleave', e => {
        stop(e); depth -= 1; if (depth <= 0) { depth = 0; gallery.classList.remove('af-gallery--dropping'); }
      });
      gallery.addEventListener('drop', e => {
        stop(e); depth = 0; gallery.classList.remove('af-gallery--dropping');
        const dropped = Array.from((e.dataTransfer && e.dataTransfer.files) || [])
          .filter(f => f.type.startsWith('image/'));
        if (dropped.length) upload(dropped);
      });
    }

    wrap.appendChild(file);
    if (!ctx.itemId) {
      // The draft should always exist by now; if it doesn't, say so plainly rather
      // than handing the artist a chore that is no longer how this works.
      file.disabled = true;
      const note = document.createElement('div'); note.className = 'af-note';
      note.textContent = 'Not ready for uploads yet — close and reopen this item.';
      wrap.appendChild(note);
    }
    paint();
    return { el: wrap, value: () => current };  // value unused on save (server owns images)
  });

  // ── file (video / audio / pdf / image — anything the pages can render) ─────
  // The server has already decided what each upload IS and stored it as `kind`,
  // so this editor never parses an extension. It renders a row per file rather
  // than a thumbnail grid: half these types have no thumbnail, and a wall of
  // identical placeholders tells the artist nothing about which file is which.
  const ACCEPT_MIME = { image: 'image/*', video: 'video/*', audio: 'audio/*', doc: '.pdf' };

  function fileSize(bytes) {
    if (!bytes && bytes !== 0) return '';
    if (bytes < 1024 * 1024) return Math.max(1, Math.round(bytes / 1024)) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(bytes < 10 * 1024 * 1024 ? 1 : 0) + ' MB';
  }

  register('file', (name, def, value, ctx) => {
    const wrap = document.createElement('div'); wrap.className = 'af-field';
    const lab = document.createElement('label'); lab.textContent = def.label || name; wrap.appendChild(lab);
    const list = document.createElement('div'); list.className = 'af-files'; wrap.appendChild(list);
    let current = def.multiple ? (Array.isArray(value) ? value.slice() : []) : (value || null);

    const kinds = def.accept || ['image', 'video', 'audio', 'doc'];
    /* The artist-facing half of a limit that really lives in nginx
     * (client_max_body_size on the artist's vhost). Without this the browser
     * uploads the whole file and gets back an nginx 413 error page, which the
     * fetch reports as a bare failure — the artist is told "could not upload"
     * after waiting out a 200MB transfer. Keep `max_mb` and the vhost in step. */
    const maxMb = def.max_mb || 500;

    function entries() { return def.multiple ? current : (current ? [current] : []); }

    function paint() {
      list.innerHTML = '';
      entries().forEach((entry, i) => {
        const row = document.createElement('div'); row.className = 'af-file-row';
        const rel = entry.card || entry.src || entry.full || '';
        const path = rel.startsWith('assets/') || rel.startsWith('/')
          ? ('/' + rel.replace(/^\//, '')) : ('/assets/' + rel);

        const prev = document.createElement('div'); prev.className = 'af-file-prev';
        if (entry.kind === 'image') {
          const img = document.createElement('img');
          img.loading = 'lazy'; img.decoding = 'async'; img.src = path;
          prev.appendChild(img);
        } else if (entry.kind === 'video') {
          /* preload="metadata" is enough to paint the first frame, and it is
           * the only free poster available — nothing here shells out to ffmpeg. */
          const v = document.createElement('video');
          v.src = path; v.muted = true; v.playsInline = true; v.preload = 'metadata';
          prev.appendChild(v);
        } else {
          const tag = document.createElement('span'); tag.className = 'af-file-kind';
          tag.textContent = entry.kind === 'audio' ? 'AUD' : (entry.kind === 'doc' ? 'PDF' : 'FILE');
          prev.appendChild(tag);
        }
        row.appendChild(prev);

        const meta = document.createElement('div'); meta.className = 'af-file-meta';
        const nm = document.createElement('a');
        nm.className = 'af-file-name'; nm.textContent = entry.name || rel.split('/').pop();
        nm.href = path; nm.target = '_blank'; nm.rel = 'noopener';
        meta.appendChild(nm);
        const sub = document.createElement('span'); sub.className = 'af-file-sub';
        sub.textContent = [entry.kind, fileSize(entry.size)].filter(Boolean).join(' · ');
        meta.appendChild(sub);
        row.appendChild(meta);

        const x = document.createElement('button');
        x.type = 'button'; x.textContent = '×'; x.title = 'remove';
        x.onclick = async () => {
          const item = await ctx.removeFile(name, def.multiple ? i : null);
          if (item) { current = def.multiple ? (item[name] || []) : (item[name] || null); paint(); }
        };
        row.appendChild(x);
        list.appendChild(row);
      });
    }

    const file = document.createElement('input');
    file.type = 'file'; file.className = 'af-file';
    file.accept = kinds.map(k => ACCEPT_MIME[k]).filter(Boolean).join(',');
    if (def.multiple) file.multiple = true;

    // One request per file, same as the image editor: a failed batch cannot
    // tell the artist which file was the problem.
    async function upload(files) {
      if (!files.length) return;
      file.disabled = true;
      for (const f of files) {
        if (f.size > maxMb * 1024 * 1024) {
          ctx.toast(f.name + ' is too big (limit ' + maxMb + 'MB).', 'err');
          continue;
        }
        let item = null;
        try { item = await ctx.uploadFile(name, f); }
        catch (e) { item = null; }
        if (!item) { ctx.toast('Could not upload ' + f.name + '.', 'err'); continue; }
        current = def.multiple ? (item[name] || []) : (item[name] || null);
        paint();  // repaint per file so a long set fills in as it goes
      }
      file.disabled = false;
      file.value = '';
    }

    file.onchange = () => upload(Array.from(file.files || []));

    if (def.multiple && ctx.itemId) {
      // Reference-counted like the image gallery's: dragenter/dragleave also
      // fire for every child the pointer crosses.
      let depth = 0;
      const stop = e => { e.preventDefault(); e.stopPropagation(); };
      list.addEventListener('dragenter', e => {
        stop(e); depth += 1; list.classList.add('af-files--dropping');
      });
      list.addEventListener('dragover', e => {
        stop(e); if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
      });
      list.addEventListener('dragleave', e => {
        stop(e); depth -= 1; if (depth <= 0) { depth = 0; list.classList.remove('af-files--dropping'); }
      });
      list.addEventListener('drop', e => {
        stop(e); depth = 0; list.classList.remove('af-files--dropping');
        // No MIME filter here, unlike the image gallery: this field's whole
        // point is the mixed bag, and the server rejects what it won't take.
        const dropped = Array.from((e.dataTransfer && e.dataTransfer.files) || []);
        if (dropped.length) upload(dropped);
      });
    }

    wrap.appendChild(file);
    if (!ctx.itemId) {
      file.disabled = true;
      const note = document.createElement('div'); note.className = 'af-note';
      note.textContent = 'Not ready for uploads yet — close and reopen this item.';
      wrap.appendChild(note);
    }
    paint();
    return { el: wrap, value: () => current };  // value unused on save (server owns files)
  });

  function make(fieldName, fieldDef, value, ctx) {
    const fn = registry[fieldDef.type] || registry.text;
    return fn(fieldName, fieldDef, value, ctx);
  }

  // What a field *is*, for the shell to lay out against. This registry is the only
  // place that knows what a type means, so the shell asks rather than keeping its
  // own list of type names that would drift the moment a type is added here.
  const LONG = ['textarea', 'markdown', 'richtext', 'copytext', 'copyrich'];
  function role(fieldDef) {
    const def = fieldDef || {};
    if (def.slug_source) return 'identity';
    if (def.type === 'image' || def.type === 'file') return 'media';
    if (LONG.indexOf(def.type) !== -1) return 'long';
    if (def.type === 'tags') return 'tags';
    return 'short';  // text, number, date, select, boolean and anything unknown
  }

  return { register, make, role, has: t => !!registry[t] };
})();
