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
 *        toast(msg, kind), itemId }  (itemId is null while creating)
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

  register('tags', (name, def, value) => {
    const box = document.createElement('div'); box.className = 'af-tags';
    let tags = Array.isArray(value) ? value.slice() : [];
    const input = document.createElement('input');
    input.type = 'text'; input.className = 'af-input'; input.placeholder = 'type + Enter';
    function paint() {
      box.querySelectorAll('.af-chip').forEach(c => c.remove());
      tags.forEach((t, i) => {
        const chip = document.createElement('span'); chip.className = 'af-chip';
        chip.textContent = t;
        const x = document.createElement('button'); x.textContent = '×'; x.type = 'button';
        x.onclick = () => { tags.splice(i, 1); paint(); };
        chip.appendChild(x); box.insertBefore(chip, input);
      });
    }
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); const v = input.value.trim(); if (v) { tags.push(v); input.value = ''; paint(); } }
    });
    box.appendChild(input); paint();
    return { el: labelWrap(name, def, box), value: () => tags };
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

  // ── image (persists immediately via ctx) ────────────────────────────────────
  register('image', (name, def, value, ctx) => {
    const wrap = document.createElement('div'); wrap.className = 'af-field';
    const lab = document.createElement('label'); lab.textContent = def.label || name; wrap.appendChild(lab);
    const gallery = document.createElement('div'); gallery.className = 'af-gallery'; wrap.appendChild(gallery);
    let current = def.multiple ? (Array.isArray(value) ? value.slice() : []) : (value || null);

    function entries() { return def.multiple ? current : (current ? [current] : []); }
    function paint() {
      gallery.innerHTML = '';
      entries().forEach((entry, i) => {
        const cell = document.createElement('div'); cell.className = 'af-thumb';
        // image paths are stored relative to the artist's assets/ dir; the admin
        // runs on the artist's own domain so /assets/<rel> resolves via nginx.
        const rel = entry.src || entry.full || entry;
        const img = document.createElement('img');
        img.src = rel.startsWith('assets/') || rel.startsWith('/') ? ('/' + rel.replace(/^\//, '')) : ('/assets/' + rel);
        cell.appendChild(img);
        const x = document.createElement('button'); x.type = 'button'; x.textContent = '×'; x.title = 'remove';
        x.onclick = async () => {
          const item = await ctx.removeImage(name, def.multiple ? i : null);
          if (item) { current = def.multiple ? (item[name] || []) : (item[name] || null); paint(); }
        };
        cell.appendChild(x); gallery.appendChild(cell);
      });
    }

    if (ctx.itemId) {
      const file = document.createElement('input'); file.type = 'file'; file.accept = 'image/*'; file.className = 'af-file';
      file.onchange = async () => {
        if (!file.files.length) return;
        const item = await ctx.uploadImage(name, file.files[0]);
        if (item) { current = def.multiple ? (item[name] || []) : (item[name] || null); paint(); }
        file.value = '';
      };
      wrap.appendChild(file);
    } else {
      const note = document.createElement('div'); note.className = 'af-note';
      note.textContent = 'Save this item first, then add images.'; wrap.appendChild(note);
    }
    paint();
    return { el: wrap, value: () => current };  // value unused on save (server owns images)
  });

  function make(fieldName, fieldDef, value, ctx) {
    const fn = registry[fieldDef.type] || registry.text;
    return fn(fieldName, fieldDef, value, ctx);
  }

  return { register, make, has: t => !!registry[t] };
})();
