// Widget: New Exhibition — Rose only
// Scaffolds a new per-exhibition detail page under exhibitions/<slug>/ and links it from the listing.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="padding:20px;flex:1;overflow-y:auto;">
        <div style="max-width:560px;">
            <h3 style="margin:0 0 4px;font-family:var(--heading-font);font-style:italic;font-weight:400;">New Exhibition</h3>
            <p style="color:var(--text2);font-size:12px;margin:0 0 18px;">Adds a new entry to the Exhibitions page and creates its detail page.</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Title<input id="ne-title" type="text" placeholder="GOOD GRIEF" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="font-size:11px;color:var(--text2);">Year<input id="ne-year" type="number" min="1900" max="2100" value="${new Date().getFullYear()}" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="font-size:11px;color:var(--text2);">Type<input id="ne-kind" type="text" value="group show" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Venue<input id="ne-venue" type="text" placeholder="Crypt Gallery, London, UK" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Description<textarea id="ne-desc" rows="4" placeholder="Short blurb about the show..." style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;font-family:inherit;resize:vertical;"></textarea></label>
            </div>

            <div style="margin-top:18px;">
                <div style="display:flex;align-items:baseline;justify-content:space-between;">
                    <div style="font-size:11px;color:var(--text2);">Image (optional)</div>
                    <div style="display:flex;gap:6px;">
                        <label style="font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);cursor:pointer;">Upload<input id="ne-upload" type="file" accept="image/*" style="display:none;"></label>
                        <button id="ne-clear-img" type="button" style="font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Clear</button>
                    </div>
                </div>
                <div id="ne-selected" style="margin-top:6px;font-size:11px;color:var(--text2);">No image selected</div>
                <div id="ne-grid" style="margin-top:10px;display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:6px;max-height:240px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);padding:6px;background:var(--bg2);"></div>
            </div>

            <div style="display:flex;gap:10px;align-items:center;margin-top:18px;">
                <button id="ne-create" class="widget-btn widget-btn-primary" style="padding:8px 16px;font-size:12px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:#fff;cursor:pointer;">Create Exhibition</button>
                <div id="ne-status" style="font-size:12px;color:var(--text2);"></div>
            </div>
        </div>
    </div>`;

    let selectedAsset = null;

    function slugify(s) {
        return (s || '').toLowerCase()
            .replace(/['']/g, '')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .slice(0, 80);
    }

    function setSelected(p) {
        selectedAsset = p;
        c.querySelector('#ne-selected').textContent = p ? 'Selected: ' + p : 'No image selected';
        renderGrid();
    }

    function renderGrid() {
        const grid = c.querySelector('#ne-grid');
        const images = (ctx.assetList || []).filter(a => a.is_image);
        if (!images.length) {
            grid.innerHTML = '<div style="grid-column:1/-1;color:var(--text2);font-size:11px;padding:10px;">No images in your assets yet. Upload one above.</div>';
            return;
        }
        grid.innerHTML = '';
        images.forEach(a => {
            const tile = document.createElement('div');
            const isSel = selectedAsset === a.path;
            tile.style.cssText = 'position:relative;aspect-ratio:1/1;border:2px solid ' + (isSel ? 'var(--accent)' : 'transparent') + ';border-radius:var(--radius);overflow:hidden;cursor:pointer;background:#000;';
            tile.innerHTML = `<img src="/artists/${ctx.artistSlug}/assets/${a.path}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;">`;
            tile.addEventListener('click', () => setSelected(isSel ? null : a.path));
            grid.appendChild(tile);
        });
    }

    c.querySelector('#ne-clear-img').addEventListener('click', () => setSelected(null));

    c.querySelector('#ne-upload').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const status = c.querySelector('#ne-status');
        status.textContent = 'Uploading ' + file.name + '...';
        const fd = new FormData();
        fd.append('file', file);
        try {
            const r = await ctx.apiFetch('/api/adze/upload-file', { method: 'POST', body: fd, isFormData: true });
            const d = await r.json();
            if (!r.ok || !d.path) { status.textContent = 'Upload failed: ' + (d.error || 'unknown'); return; }
            const r2 = await ctx.apiFetch('/api/adze/list-assets');
            if (r2.ok) {
                const dd = await r2.json();
                if (dd && Array.isArray(dd.assets)) ctx.assetList = dd.assets;
            }
            setSelected(d.path);
            status.textContent = 'Uploaded.';
        } catch(err) {
            status.textContent = 'Upload error: ' + err.message;
        } finally {
            e.target.value = '';
        }
    });

    c.querySelector('#ne-create').addEventListener('click', async () => {
        const title = c.querySelector('#ne-title').value.trim();
        const year  = c.querySelector('#ne-year').value.trim();
        const kind  = c.querySelector('#ne-kind').value.trim() || 'group show';
        const venue = c.querySelector('#ne-venue').value.trim() || '—';
        const desc  = c.querySelector('#ne-desc').value.trim() || `${title}, ${year}.`;
        const status = c.querySelector('#ne-status');

        if (!title) { status.textContent = 'Title is required.'; return; }
        if (!/^\d{4}$/.test(year)) { status.textContent = 'Year must be 4 digits.'; return; }

        const slug = slugify(title);
        if (!slug) { status.textContent = 'Could not derive a slug from that title.'; return; }

        const imgHtml = selectedAsset
            ? `<img class="exh-image" src="../../assets/${selectedAsset}" alt="${escHtml(title)}">`
            : `<div class="exh-image" aria-label="Image placeholder for ${escHtml(title)}">Image — ${escHtml(title)}</div>`;

        const content = buildDetailContent(title, year, kind, venue, desc, imgHtml);

        status.textContent = 'Creating page...';
        const r = await ctx.apiFetch('/api/adze/create-nested-page', {
            method: 'POST',
            body: { parent_slug: 'exhibitions', child_slug: slug, title: `${title} — Rose Jones`, description: `${title}, ${year} — ${venue}`, content, config: { categories: ['exhibition'] } }
        });
        const d = await r.json();
        if (!r.ok) { status.textContent = 'Create failed: ' + (d.error || 'unknown'); return; }

        status.textContent = 'Linking from Exhibitions page...';
        const ok = await addLinkToExhibitionsListing(year, title, slug, venue, kind);
        if (!ok) { status.textContent = 'Page created, but failed to link from Exhibitions page.'; return; }

        status.textContent = `Created /exhibitions/${slug}/`;
        ctx.toast && ctx.toast('Exhibition added: ' + title);
        c.querySelector('#ne-title').value = '';
        c.querySelector('#ne-venue').value = '';
        c.querySelector('#ne-desc').value = '';
        setSelected(null);
    });

    async function addLinkToExhibitionsListing(year, title, slug, venue, kind) {
        const pageData = await ctx.getPageContent('exhibitions');
        if (!pageData) return false;
        let content = pageData.content;
        const titleLine = `${escHtml(title)}, ${escHtml(kind)}, ${escHtml(venue)}`;
        const newItem = `        <div class="item"><a href="/exhibitions/${slug}/"><span class="year">${escHtml(year)}</span><span class="title">${titleLine}</span></a></div>`;
        const anchor = '<div class="exhibitions-list">';
        const ai = content.indexOf(anchor);
        if (ai === -1) return false;
        const insertAt = ai + anchor.length;
        content = content.slice(0, insertAt) + '\n' + newItem + content.slice(insertAt);
        const r = await ctx.apiFetch('/api/adze/edit-page', { method: 'POST', body: { page_slug: 'exhibitions', content, config: pageData.config } });
        return r.ok;
    }

    function buildDetailContent(title, year, kind, venue, desc, imgHtml) {
        const escTitle = escHtml(title);
        const escDesc = escHtml(desc);
        return `<style>
:root { --ink:#000; --bg:#fff; --works:#0000FF; --exhibitions:#1AFF00; --about:#FF0033; --contact:#8C00FF; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--ink); overflow-x: hidden; }
.page { max-width: 414px; margin: 0 auto; position: relative; padding-bottom: 120px; }
.header { height:54px; background:#fff; position:sticky; top:0; z-index:10; display:flex; align-items:center; justify-content:space-between; padding:0 13px; }
.brand { font-weight:250; font-size:36px; line-height:60px; color:#000; text-decoration:none; }
.menu-icon { width:36px; height:28px; display:inline-flex; flex-direction:column; justify-content:space-between; background:none; border:0; cursor:pointer; padding:4px 0; }
.menu-icon span { display:block; height:2px; background:#000; border-radius:1px; }
.menu-icon span:nth-child(1){ width:100%; }
.menu-icon span:nth-child(2){ width:70%; align-self:flex-end; }
.menu-icon span:nth-child(3){ width:40%; align-self:flex-end; }
.menu-overlay { position:fixed; inset:0; background:rgba(255,255,255,0.97); z-index:100; display:none; flex-direction:column; align-items:flex-start; justify-content:center; padding:0 12vw; }
.menu-overlay.open { display:flex; }
.menu-overlay a { font-weight:400; font-size:clamp(34px,7vw,60px); line-height:1.2; text-decoration:none; padding:6px 0; }
.menu-overlay .m-works{ color:var(--works); }
.menu-overlay .m-exhibitions{ color:var(--exhibitions); text-shadow:0 0 1px rgba(0,0,0,0.4); }
.menu-overlay .m-about{ color:var(--about); }
.menu-overlay .m-contact{ color:var(--contact); }
.menu-close { position:absolute; top:18px; right:18px; background:none; border:0; cursor:pointer; font-size:28px; line-height:1; color:#000; padding:8px; }
.back-link { display:inline-block; padding:16px 13px 0; font-size:14px; font-weight:300; color:#000; text-decoration:none; }
.exh-image { margin:16px 13px 0; width:calc(100% - 26px); aspect-ratio:4/5; background: repeating-linear-gradient(135deg,#ecffe6 0 12px,#d8f3d0 12px 24px); border:1px dashed #4caf3a; display:flex; align-items:center; justify-content:center; color:#2c5a22; font-size:12px; letter-spacing:0.1em; text-transform:uppercase; }
img.exh-image { object-fit: cover; padding:0; border:0; background:#000; }
.title-row { padding:28px 13px 0; }
.exh-title { font-weight:400; font-size:30px; line-height:1.1; color:var(--exhibitions); text-shadow:0 0 1px rgba(0,0,0,0.4); }
.exh-meta { margin-top:10px; font-weight:250; font-size:15px; line-height:1.4; color:#000; }
.exh-meta span + span::before { content:" · "; color:#666; }
.exh-desc { padding:20px 13px 0; font-weight:300; font-size:15px; line-height:1.6; color:#000; max-width:60ch; white-space:pre-wrap; }
.detail-list { padding:24px 13px 0; font-weight:250; font-size:14px; line-height:1.6; color:#000; }
.detail-list dt { color:#777; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; margin-top:10px; }
.footer { border-top:1px solid #000; margin-top:80px; padding:14px 13px 24px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; font-size:15px; line-height:25px; }
.footer a { color:#000; text-decoration:none; }
.footer .right { text-align:right; }
.footer .center { text-align:center; }
@media (min-width: 768px) {
  .page { max-width:980px; padding-bottom:160px; }
  .header { padding:0 32px; height:72px; }
  .brand { font-size:44px; }
  .menu-icon { width:44px; height:34px; }
  .back-link { padding:28px 32px 0; font-size:15px; }
  .exh-image { margin:24px 32px 0; width:calc(100% - 64px); aspect-ratio:16/10; }
  .title-row { padding:48px 32px 0; display:grid; grid-template-columns:1fr 280px; gap:32px; align-items:baseline; }
  .exh-title { font-size:52px; }
  .exh-meta { font-size:17px; margin-top:0; text-align:right; }
  .exh-desc { padding:28px 32px 0; font-size:17px; line-height:1.7; max-width:64ch; }
  .detail-list { padding:32px 32px 0; font-size:15px; }
  .footer { padding:20px 32px 32px; font-size:16px; }
}
</style>

<html>
<div class="page">
  <header class="header">
    <a class="brand" href="/">Rose Jones</a>
    <button type="button" class="menu-icon" aria-label="Open menu" aria-controls="site-menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </header>
  <nav id="site-menu" class="menu-overlay" aria-hidden="true">
    <button type="button" class="menu-close" aria-label="Close menu">&times;</button>
    <a class="m-works" href="/works/">Works</a>
    <a class="m-exhibitions" href="/exhibitions/">Exhibitions</a>
    <a class="m-about" href="/about/">About</a>
    <a class="m-contact" href="/contact/">Contact</a>
  </nav>
  <a class="back-link" href="/exhibitions/">← Exhibitions</a>
  ${imgHtml}
  <div class="title-row">
    <h1 class="exh-title">${escTitle}</h1>
    <div class="exh-meta"><span>${escHtml(year)}</span><span>${escHtml(kind)}</span><span>${escHtml(venue)}</span></div>
  </div>
  <div class="exh-desc">${escDesc}</div>
  <dl class="detail-list">
    <dt>Year</dt><dd>${escHtml(year)}</dd>
    <dt>Type</dt><dd>${escHtml(kind)}</dd>
    <dt>Venue</dt><dd>${escHtml(venue)}</dd>
  </dl>
  <footer class="footer">
    <a href="/contact/">Contact</a>
    <div class="center">// Copyright © 2025 Rose Jones</div>
    <div class="right">// Site by Last Place</div>
  </footer>
</div>
<script>
(function(){
  var btn=document.querySelector('.menu-icon'), menu=document.getElementById('site-menu'), close=document.querySelector('.menu-close');
  if(!btn||!menu)return;
  function open(){ menu.classList.add('open'); menu.setAttribute('aria-hidden','false'); btn.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; }
    function shut(){ menu.classList.remove('open'); menu.setAttribute('aria-hidden','true'); btn.setAttribute('aria-expanded','false'); document.body.style.overflow=''; }
    function toggle(){ if (menu.classList.contains('open')) shut(); else open(); }
    btn.addEventListener('click', toggle);
  if(close)close.addEventListener('click',shut);
  menu.addEventListener('click',function(e){if(e.target===menu)shut();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')shut();});
})();
</script>
</html>
`;
    }

    function escHtml(s) { return (ctx.escHtml || function(x){return String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));})(s); }

    renderGrid();
})(ctx);
