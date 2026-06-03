/* Adze shared asset-tree helper.
 *
 * The admin dashboard and the public intake portal are two sides of the same
 * asset system. This module holds the folder-aware logic they share so both
 * behave identically:
 *   - AssetTree.level(items, cwd)  → immediate subfolders + files in a dir
 *   - AssetTree.crumbHTML(cwd, fn) → clickable breadcrumb trail
 *   - AssetTree.folderTileHTML(folder, onclick)
 *   - AssetTree.filesFromInput(inputEl)       (folder picker, webkitdirectory)
 *   - AssetTree.filesFromDataTransfer(dt)     (drag a folder onto a drop zone)
 *   - AssetTree.upload(entries, opts, onProgress)  (zip → extract, else rel_path)
 *   - AssetTree.injectCSS()  → one-time shared styling for folders/breadcrumbs
 *
 * Each page keeps its own tile/label markup; only the genuinely new
 * folder-navigation + folder/zip-upload code lives here, written once.
 */
window.AssetTree = (function () {
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const q = s => String(s).replace(/'/g, "\\'");

  // Items directly in `cwd` ('' = root) split into subfolders and files.
  // Link assets (no real path) surface only at the root.
  function level(items, cwd) {
    const prefix = cwd ? cwd + '/' : '';
    const folders = new Map();
    const files = [];
    for (const it of items) {
      const p = it.path || '';
      if (it.kind === 'link') { if (!cwd) files.push(it); continue; }
      if (prefix && !(p + '/').startsWith(prefix)) continue;
      const rest = p.slice(prefix.length);
      if (!rest) continue;
      const slash = rest.indexOf('/');
      if (slash === -1) {
        files.push(it);
      } else {
        const name = rest.slice(0, slash);
        const fpath = prefix + name;
        const f = folders.get(name) || { name, path: fpath, count: 0 };
        f.count++;
        folders.set(name, f);
      }
    }
    const folderList = Array.from(folders.values())
      .sort((a, b) => a.name.localeCompare(b.name));
    return { folders: folderList, files };
  }

  function crumbs(cwd) {
    const out = [{ name: 'All assets', path: '' }];
    let acc = '';
    for (const s of (cwd ? cwd.split('/') : [])) {
      acc = acc ? acc + '/' + s : s;
      out.push({ name: s, path: acc });
    }
    return out;
  }

  // `navFn` is the name of a global fn taking a dir path, e.g. 'adGoToFolder'.
  function crumbHTML(cwd, navFn) {
    const arr = crumbs(cwd);
    if (arr.length === 1) return '';
    return '<div class="at-crumbs">' + arr.map((c, i) => {
      const last = i === arr.length - 1;
      const inner = `<i class="ph ph-folder${last ? '-open' : ''}"></i> ${esc(c.name)}`;
      return last
        ? `<span class="at-crumb is-cur">${inner}</span>`
        : `<span class="at-crumb" onclick="${navFn}('${q(c.path)}')">${inner}</span>`;
    }).join('<span class="at-sep">/</span>') + '</div>';
  }

  function folderTileHTML(folder, navFn) {
    return `<div class="at-folder" onclick="${navFn}('${q(folder.path)}')" title="${esc(folder.name)}">
      <div class="at-folder-ico"><i class="ph ph-folder"></i></div>
      <div class="at-folder-name">${esc(folder.name)}</div>
      <div class="at-folder-count">${folder.count} item${folder.count === 1 ? '' : 's'}</div>
    </div>`;
  }

  // ── Gathering files with their relative paths ─────────────────────────────
  function filesFromInput(input) {
    return Array.from(input.files).map(f => ({
      file: f,
      relPath: f.webkitRelativePath || f.name,
    }));
  }

  // Walk a drop's DataTransferItemList so dropping a *folder* preserves its
  // tree. Falls back to the flat file list if the browser exposes no entries.
  async function filesFromDataTransfer(dt) {
    const entries = Array.from(dt.items || [])
      .map(i => i.webkitGetAsEntry && i.webkitGetAsEntry())
      .filter(Boolean);
    if (!entries.length) {
      return Array.from(dt.files || []).map(f => ({ file: f, relPath: f.name }));
    }
    const out = [];
    async function walk(entry, prefix) {
      if (entry.isFile) {
        await new Promise(res => entry.file(file => {
          out.push({ file, relPath: prefix + file.name });
          res();
        }, res));
      } else if (entry.isDirectory) {
        const reader = entry.createReader();
        await new Promise(res => {
          const readBatch = () => reader.readEntries(async ents => {
            if (!ents.length) return res();
            for (const e of ents) await walk(e, prefix + entry.name + '/');
            readBatch();
          }, res);
          readBatch();
        });
      }
    }
    for (const e of entries) await walk(e, '');
    return out;
  }

  // Upload a list of {file, relPath}. A .zip is sent with extract=1 so the
  // server unpacks it; anything with a folder path is sent with rel_path so the
  // server preserves the structure. `opts`: {url, headers}. onProgress(done,
  // total, name). Returns {done, failed, errors:[...]}.
  async function upload(entries, opts, onProgress, concurrency) {
    concurrency = concurrency || 5;
    let done = 0, failed = 0, idx = 0;
    const errors = [];
    if (onProgress) onProgress(0, entries.length, '');
    async function worker() {
      while (idx < entries.length) {
        const ent = entries[idx++];
        const fd = new FormData();
        fd.append('file', ent.file);
        const isZip = (ent.file.name || '').toLowerCase().endsWith('.zip');
        if (isZip) {
          fd.append('extract', '1');
        } else if (ent.relPath && ent.relPath !== ent.file.name) {
          fd.append('rel_path', ent.relPath);
        }
        try {
          const r = await fetch(opts.url, {
            method: 'POST',
            headers: opts.headers || {},
            body: fd,
          });
          const data = await r.json().catch(() => ({}));
          if (!r.ok) throw new Error(data.error || ('HTTP ' + r.status));
          // A zip that yielded nothing (encrypted / unsupported / all filtered)
          // returns 200 but extracted 0 — surface that rather than "uploaded".
          if (isZip && data.extracted === 0) {
            throw new Error('nothing extracted (password-protected or unsupported zip?)');
          }
        } catch (err) {
          failed++;
          errors.push((ent.relPath || ent.file.name) + ': ' + err.message);
        }
        done++;
        if (onProgress) onProgress(done, entries.length, ent.relPath || ent.file.name);
      }
    }
    const n = Math.min(concurrency, entries.length || 1);
    await Promise.all(Array.from({ length: n }, worker));
    return { done, failed, errors };
  }

  let _cssDone = false;
  function injectCSS() {
    if (_cssDone) return;
    _cssDone = true;
    const css = `
      .at-crumbs { display:flex; align-items:center; flex-wrap:wrap; gap:4px;
        font-size:12px; margin:10px 0 4px; color:var(--text2,#6b6b67); }
      .at-crumb { cursor:pointer; padding:2px 6px; border-radius:6px;
        display:inline-flex; align-items:center; gap:4px; }
      .at-crumb:not(.is-cur):hover { background:rgba(0,0,0,0.06); color:var(--text,#1d1d1b); }
      .at-crumb.is-cur { color:var(--text,#1d1d1b); font-weight:600; cursor:default; }
      .at-sep { color:var(--text2,#9a9a96); opacity:.6; }
      .at-folder { background:var(--surface,#fff); border:1px solid var(--border,#e3e3df);
        border-radius:10px; padding:14px 12px; cursor:pointer; text-align:center;
        display:flex; flex-direction:column; align-items:center; gap:4px;
        transition:transform .12s, box-shadow .12s, border-color .12s; }
      .at-folder:hover { transform:translateY(-2px); box-shadow:0 4px 10px rgba(0,0,0,0.06);
        border-color:var(--text,#1d1d1b); }
      .at-folder-ico { font-size:34px; line-height:1; color:var(--accent,#1d1d1b); width:100%; text-align:center; }
      .at-folder-name { font-size:12px; font-weight:600; width:100%; max-width:100%;
        overflow:hidden; text-overflow:ellipsis; white-space:nowrap; text-align:center; }
      .at-folder-count { font-size:11px; color:var(--text2,#6b6b67); text-align:center; }
    `;
    const el = document.createElement('style');
    el.textContent = css;
    document.head.appendChild(el);
  }

  return { level, crumbs, crumbHTML, folderTileHTML, filesFromInput,
    filesFromDataTransfer, upload, injectCSS, esc };
})();
