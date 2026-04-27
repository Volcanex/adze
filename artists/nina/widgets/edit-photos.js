// Widget: Edit Photos — Nina's custom tool
// Lists every photo on the home page with editable location / year / caption,
// plus an "Add photo" uploader that appends a new entry.
// Saves by rewriting the <script id="photo-data"> JSON block in home/content.md.

(function(ctx) {
    const container = ctx.container;
    container.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;padding:0;overflow:hidden;';

    container.innerHTML = `
        <div style="padding:20px 20px 12px;flex-shrink:0;border-bottom:1px solid var(--border);">
            <h3 style="margin:0 0 4px;font-size:16px;">Edit Photos</h3>
            <p style="color:var(--text2);font-size:12px;margin:0;">Update location / year / caption, or add new photos. Changes save to your home page.</p>
        </div>

        <div id="ep-add" style="padding:16px 20px;flex-shrink:0;border-bottom:1px solid var(--border);background:var(--surface,rgba(0,0,0,0.02));">
            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                <button id="ep-add-btn" class="widget-btn widget-btn-primary" style="padding:8px 14px;font-size:13px;">+ Add Photo</button>
                <span style="color:var(--text2);font-size:12px;" id="ep-status"></span>
            </div>
            <div id="ep-add-form" style="display:none;margin-top:14px;padding:14px;border:1px solid var(--border);border-radius:6px;background:var(--bg);">
                <div id="ep-drop" style="border:2px dashed var(--border);border-radius:6px;padding:24px;text-align:center;cursor:pointer;margin-bottom:12px;">
                    <input type="file" id="ep-file" accept="image/*" multiple style="display:none;">
                    <p style="color:var(--text2);font-size:13px;margin:0;" id="ep-drop-label">Click or drag image(s) here</p>
                    <p style="color:var(--text2);font-size:11px;margin:4px 0 0;opacity:0.6;">JPG, PNG, WebP — you can drop multiple</p>
                </div>
                <div style="display:grid;grid-template-columns:1fr 100px;gap:8px;margin-bottom:8px;">
                    <input type="text" id="ep-new-loc" placeholder="Location, Country" style="padding:8px 10px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                    <input type="number" id="ep-new-year" placeholder="Year" style="padding:8px 10px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                </div>
                <input type="text" id="ep-new-caption" placeholder="Caption (optional — brand, photographer, etc.)" style="width:100%;padding:8px 10px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);margin-bottom:10px;">
                <div style="display:flex;gap:8px;">
                    <button id="ep-upload" class="widget-btn widget-btn-primary" style="padding:8px 14px;font-size:13px;" disabled>Upload &amp; Add</button>
                    <button id="ep-cancel" class="widget-btn" style="padding:8px 14px;font-size:13px;">Cancel</button>
                </div>
            </div>
        </div>

        <div style="flex:1;overflow-y:auto;padding:0 8px;" id="ep-list-wrap">
            <div id="ep-list" style="padding:12px 12px 80px;">
                <p style="color:var(--text2);font-size:13px;padding:20px;">Loading photos…</p>
            </div>
        </div>

        <div id="ep-save-bar" style="position:sticky;bottom:0;padding:12px 20px;background:var(--bg);border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0;">
            <span id="ep-dirty" style="color:var(--text2);font-size:12px;">No unsaved changes</span>
            <button id="ep-save" class="widget-btn widget-btn-primary" style="padding:8px 18px;font-size:13px;" disabled>Save changes</button>
        </div>
    `;

    // State
    let pageContent = '';
    let photos = [];
    let original = '';
    let dirty = false;

    const listEl = document.getElementById('ep-list');
    const saveBtn = document.getElementById('ep-save');
    const dirtyEl = document.getElementById('ep-dirty');
    const statusEl = document.getElementById('ep-status');
    const addBtn = document.getElementById('ep-add-btn');
    const addForm = document.getElementById('ep-add-form');
    const cancelBtn = document.getElementById('ep-cancel');
    const uploadBtn = document.getElementById('ep-upload');
    const drop = document.getElementById('ep-drop');
    const fileInput = document.getElementById('ep-file');
    const dropLabel = document.getElementById('ep-drop-label');
    const newLoc = document.getElementById('ep-new-loc');
    const newYear = document.getElementById('ep-new-year');
    const newCap = document.getElementById('ep-new-caption');

    let pendingFiles = [];

    function markDirty() {
        dirty = true;
        dirtyEl.textContent = 'Unsaved changes';
        dirtyEl.style.color = 'var(--accent, #b84a39)';
        saveBtn.disabled = false;
    }
    function markClean() {
        dirty = false;
        dirtyEl.textContent = 'No unsaved changes';
        dirtyEl.style.color = 'var(--text2)';
        saveBtn.disabled = true;
    }

    function esc(s) {
        return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    function photoUrl(p) {
        // Try artist preview — served by flask at /artists/{slug}/assets/{path}
        const slug = ctx.artist || (window.adminState && window.adminState.artist) || '';
        if (slug) return `/artists/${slug}/assets/${p.src}`;
        return `../assets/${p.src}`;
    }

    function render() {
        if (!photos.length) {
            listEl.innerHTML = '<p style="color:var(--text2);font-size:13px;padding:20px;">No photos yet. Add one above.</p>';
            return;
        }
        listEl.innerHTML = photos.map((p, i) => `
            <div class="ep-row" data-i="${i}" style="display:grid;grid-template-columns:80px 1fr auto;gap:12px;align-items:center;padding:10px;border:1px solid var(--border);border-radius:6px;margin-bottom:8px;background:var(--bg);">
                <div style="width:80px;height:80px;border-radius:4px;overflow:hidden;background:var(--surface);">
                    <img src="${esc(photoUrl(p))}" style="width:100%;height:100%;object-fit:cover;display:block;" loading="lazy" onerror="this.style.display='none'">
                </div>
                <div style="display:grid;grid-template-columns:1fr 90px;gap:8px;">
                    <input type="text" data-field="location" value="${esc(p.location)}" placeholder="Location, Country" style="padding:6px 10px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                    <input type="number" data-field="year" value="${esc(p.year || '')}" placeholder="Year" style="padding:6px 10px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                    <input type="text" data-field="caption" value="${esc(p.caption)}" placeholder="Caption (brand, photographer…)" style="grid-column:span 2;padding:6px 10px;font-size:12px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text2);">
                </div>
                <button data-action="delete" title="Remove photo" style="background:none;border:1px solid var(--border);color:var(--text2);padding:6px 10px;font-size:11px;border-radius:4px;cursor:pointer;letter-spacing:0.1em;">DELETE</button>
            </div>
        `).join('');

        listEl.querySelectorAll('.ep-row').forEach(row => {
            const i = parseInt(row.dataset.i, 10);
            row.querySelectorAll('input').forEach(inp => {
                inp.addEventListener('input', () => {
                    const f = inp.dataset.field;
                    let v = inp.value;
                    if (f === 'year') v = v ? parseInt(v, 10) || '' : '';
                    photos[i][f] = v;
                    markDirty();
                });
            });
            row.querySelector('[data-action="delete"]').addEventListener('click', () => {
                if (!confirm('Remove this photo from the home page?\n(The image file stays on the server.)')) return;
                photos.splice(i, 1);
                markDirty();
                render();
            });
        });
    }

    // ── Load current page content ──
    async function load() {
        try {
            const res = await ctx.apiFetch('/api/sandbox/get-page-content?page_slug=home&_=' + Date.now());
            const data = await res.json();
            pageContent = data.content || '';
            original = pageContent;

            const m = pageContent.match(/<script\b[^>]*id=["']photo-data["'][^>]*>\s*([\s\S]*?)\s*<\/script>/i);
            if (!m) {
                listEl.innerHTML = `<p style="color:var(--danger, #c0392b);font-size:13px;padding:20px;">Can't find the photo data block on the home page. Make sure home/content.md has a <code>&lt;script type="application/json" id="photo-data"&gt;</code> block.</p>`;
                return;
            }
            try {
                photos = JSON.parse(m[1]);
                // Backwards compat: old entries used "file" instead of "src"
                photos.forEach(p => {
                    if (!p.src && p.file) p.src = 'photos/' + p.file;
                });
            } catch (e) {
                listEl.innerHTML = `<p style="color:var(--danger);font-size:13px;padding:20px;">The photo data is invalid JSON: ${esc(e.message)}</p>`;
                return;
            }
            render();
            markClean();
        } catch (e) {
            listEl.innerHTML = `<p style="color:var(--danger);font-size:13px;padding:20px;">Error loading page: ${esc(e.message)}</p>`;
        }
    }

    // ── Save back ──
    saveBtn.addEventListener('click', async () => {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving…';
        try {
            const json = JSON.stringify(photos);
            const newContent = pageContent.replace(
                /(<script type="application\/json" id="photo-data">)[\s\S]*?(<\/script>)/,
                `$1\n${json}\n$2`
            );
            const res = await ctx.apiFetch('/api/sandbox/edit-page', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page_slug: 'home', content: newContent })
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Save failed');
            pageContent = newContent;
            markClean();
            statusEl.textContent = 'Saved ✓';
            setTimeout(() => statusEl.textContent = '', 2500);
        } catch (e) {
            statusEl.textContent = 'Error: ' + e.message;
            statusEl.style.color = 'var(--danger, #c0392b)';
        } finally {
            saveBtn.textContent = 'Save changes';
        }
    });

    // ── Add-photo UI ──
    addBtn.addEventListener('click', () => {
        addForm.style.display = addForm.style.display === 'none' ? 'block' : 'none';
    });
    cancelBtn.addEventListener('click', () => {
        addForm.style.display = 'none';
        pendingFiles = [];
        fileInput.value = '';
        dropLabel.textContent = 'Click or drag image(s) here';
        newLoc.value = ''; newYear.value = ''; newCap.value = '';
        uploadBtn.disabled = true;
    });

    drop.addEventListener('click', () => fileInput.click());
    drop.addEventListener('dragover', e => { e.preventDefault(); drop.style.borderColor = 'var(--accent, #b84a39)'; });
    drop.addEventListener('dragleave', () => { drop.style.borderColor = 'var(--border)'; });
    drop.addEventListener('drop', e => {
        e.preventDefault();
        drop.style.borderColor = 'var(--border)';
        pendingFiles = [...e.dataTransfer.files].filter(f => f.type.startsWith('image/'));
        updateDropLabel();
    });
    fileInput.addEventListener('change', () => {
        pendingFiles = [...fileInput.files];
        updateDropLabel();
    });
    function updateDropLabel() {
        if (pendingFiles.length === 0) dropLabel.textContent = 'Click or drag image(s) here';
        else if (pendingFiles.length === 1) dropLabel.textContent = pendingFiles[0].name;
        else dropLabel.textContent = `${pendingFiles.length} files selected`;
        uploadBtn.disabled = pendingFiles.length === 0;
    }

    uploadBtn.addEventListener('click', async () => {
        if (!pendingFiles.length) return;
        uploadBtn.disabled = true;
        const loc = newLoc.value.trim() || 'Unknown';
        const yr = newYear.value.trim() ? parseInt(newYear.value.trim(), 10) : '';
        const cap = newCap.value.trim();

        let uploaded = 0;
        for (const f of pendingFiles) {
            uploadBtn.textContent = `Uploading ${uploaded + 1}/${pendingFiles.length}…`;
            try {
                const form = new FormData();
                form.append('file', f);
                const res = await ctx.apiFetch('/api/sandbox/upload-file', { method: 'POST', body: form });
                const data = await res.json();
                if (!data.success) { statusEl.textContent = 'Upload error: ' + (data.error || 'unknown'); continue; }
                // Upload-file returns url like "../assets/images/foo.jpg"
                const srcMatch = data.url.match(/\.\.\/assets\/(.+)$/);
                const src = srcMatch ? srcMatch[1] : `images/${data.filename}`;
                photos.push({ src, location: loc, year: yr, caption: cap });
                uploaded++;
            } catch (e) {
                statusEl.textContent = 'Error: ' + e.message;
            }
        }
        uploadBtn.textContent = 'Upload & Add';
        statusEl.textContent = `Added ${uploaded} photo${uploaded === 1 ? '' : 's'}. Click Save to publish.`;
        setTimeout(() => statusEl.textContent = '', 4000);

        // Reset form
        pendingFiles = [];
        fileInput.value = '';
        dropLabel.textContent = 'Click or drag image(s) here';
        newLoc.value = ''; newYear.value = ''; newCap.value = '';
        addForm.style.display = 'none';

        if (uploaded) {
            markDirty();
            render();
        }
    });

    load();
})(ctx);
