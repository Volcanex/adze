// Widget: New Work — Rose only
// Scaffolds a new per-work detail page under works/<slug>/ and adds a link to the works listing.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="padding:20px;flex:1;overflow-y:auto;">
        <div style="max-width:560px;">
            <h3 style="margin:0 0 4px;font-family:var(--heading-font);font-style:italic;font-weight:400;">New Work</h3>
            <p style="color:var(--text2);font-size:12px;margin:0 0 18px;">Adds a new entry to the Works page and creates its detail page. The image is optional; the page falls back to a striped placeholder if you leave it blank.</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Title<input id="nw-title" type="text" placeholder="Moonlit Sea" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="font-size:11px;color:var(--text2);">Year<input id="nw-year" type="number" min="1900" max="2100" value="${new Date().getFullYear()}" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="font-size:11px;color:var(--text2);">Medium<input id="nw-medium" type="text" value="Oil on linen" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Dimensions<input id="nw-dims" type="text" placeholder="120 × 90 cm" style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;"></label>
                <label style="grid-column:1/-1;font-size:11px;color:var(--text2);">Description<textarea id="nw-desc" rows="4" placeholder="Short blurb about the work..." style="margin-top:4px;width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);font-size:13px;font-family:inherit;resize:vertical;"></textarea></label>
            </div>

            <div style="margin-top:18px;">
                <div style="display:flex;align-items:baseline;justify-content:space-between;">
                    <div style="font-size:11px;color:var(--text2);">Image (optional)</div>
                    <div style="display:flex;gap:6px;">
                        <label style="font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);cursor:pointer;">Upload<input id="nw-upload" type="file" accept="image/*" style="display:none;"></label>
                        <button id="nw-clear-img" type="button" style="font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Clear</button>
                    </div>
                </div>
                <div id="nw-selected" style="margin-top:6px;font-size:11px;color:var(--text2);">No image selected</div>
                <div id="nw-grid" style="margin-top:10px;display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:6px;max-height:240px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);padding:6px;background:var(--bg2);"></div>
            </div>

            <div style="display:flex;gap:10px;align-items:center;margin-top:18px;">
                <button id="nw-create" class="widget-btn widget-btn-primary" style="padding:8px 16px;font-size:12px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:#fff;cursor:pointer;">Create Work</button>
                <div id="nw-status" style="font-size:12px;color:var(--text2);"></div>
            </div>
        </div>
    </div>`;

    let selectedAsset = null; // path relative to artists/<slug>/assets/

    function slugify(s) {
        return (s || '').toLowerCase()
            .replace(/['']/g, '')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .slice(0, 80);
    }

    function setSelected(path) {
        selectedAsset = path;
        c.querySelector('#nw-selected').textContent = path ? 'Selected: ' + path : 'No image selected';
        renderGrid();
    }

    function renderGrid() {
        const grid = c.querySelector('#nw-grid');
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

    c.querySelector('#nw-clear-img').addEventListener('click', () => setSelected(null));

    c.querySelector('#nw-upload').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const status = c.querySelector('#nw-status');
        status.textContent = 'Uploading ' + file.name + '...';
        const fd = new FormData();
        fd.append('file', file);
        try {
            const r = await ctx.apiFetch('/api/adze/upload-file', { method: 'POST', body: fd, isFormData: true });
            const d = await r.json();
            if (!r.ok || !d.path) { status.textContent = 'Upload failed: ' + (d.error || 'unknown'); return; }
            // d.path is relative to artists/<slug>/assets/ e.g. "images/foo.jpg"
            await ctx.loadAssets();
            // assetList isn't auto-refreshed in the iframe — fetch fresh list
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

    c.querySelector('#nw-create').addEventListener('click', async () => {
        const title  = c.querySelector('#nw-title').value.trim();
        const year   = c.querySelector('#nw-year').value.trim();
        const medium = c.querySelector('#nw-medium').value.trim() || 'Oil on linen';
        const dims   = c.querySelector('#nw-dims').value.trim() || '—';
        const desc   = c.querySelector('#nw-desc').value.trim() || `A new work, ${title}.`;
        const status = c.querySelector('#nw-status');

        if (!title) { status.textContent = 'Title is required.'; return; }
        if (!/^\d{4}$/.test(year)) { status.textContent = 'Year must be 4 digits.'; return; }

        const slug = slugify(title);
        if (!slug) { status.textContent = 'Could not derive a slug from that title.'; return; }

        const imgHtml = selectedAsset
            ? `<img class="work-image" src="../../assets/${selectedAsset}" alt="${title}">`
            : `<div class="work-image" aria-label="Image placeholder for ${title}">Image — ${title}</div>`;

        const content = buildDetailContent(title, year, medium, dims, desc, imgHtml);

        status.textContent = 'Creating page...';
        const r = await ctx.apiFetch('/api/adze/create-nested-page', {
            method: 'POST',
            body: { parent_slug: 'works', child_slug: slug, title: `${title} — Rose Jones`, description: `${title}, ${year}`, content, config: { categories: ['work'] } }
        });
        const d = await r.json();
        if (!r.ok) { status.textContent = 'Create failed: ' + (d.error || 'unknown'); return; }

        // Now insert link into works/content.html
        status.textContent = 'Linking from Works page...';
        const ok = await addLinkToWorksListing(year, title, slug);
        if (!ok) { status.textContent = 'Page created, but failed to link from Works page — add the link by hand.'; return; }

        status.textContent = `Created /works/${slug}/`;
        ctx.toast && ctx.toast('Work added: ' + title);
        // Reset form
        c.querySelector('#nw-title').value = '';
        c.querySelector('#nw-dims').value = '';
        c.querySelector('#nw-desc').value = '';
        setSelected(null);
    });

    async function addLinkToWorksListing(year, title, slug) {
        const pageData = await ctx.getPageContent('works');
        if (!pageData) return false;
        let content = pageData.content;
        const escTitle = escHtml(title);
        const newLi = `        <li><a href="/works/${slug}/">${escTitle}</a></li>`;

        // Find <div class="year">YEAR</div> followed by the next <ul class="works-list">
        const yearMarker = `<div class="year">${year}</div>`;
        const idx = content.indexOf(yearMarker);
        if (idx !== -1) {
            // Find the next <ul class="works-list"> after this year marker
            const ulStart = content.indexOf('<ul class="works-list">', idx);
            if (ulStart !== -1) {
                const insertAt = ulStart + '<ul class="works-list">'.length;
                content = content.slice(0, insertAt) + '\n' + newLi + content.slice(insertAt);
            } else {
                return false;
            }
        } else {
            // No block for this year yet — insert a new year block right after section-title
            const anchor = '<h1 class="section-title">Works</h1>';
            const ai = content.indexOf(anchor);
            if (ai === -1) return false;
            const block = `\n\n    <div class="year-row"><div class="rule"></div><div class="year">${year}</div><div class="rule"></div></div>\n    <ul class="works-list">\n${newLi}\n    </ul>`;
            const insertAt = ai + anchor.length;
            content = content.slice(0, insertAt) + block + content.slice(insertAt);
        }

        const r = await ctx.apiFetch('/api/adze/edit-page', { method: 'POST', body: { page_slug: 'works', content, config: pageData.config } });
        return r.ok;
    }

    function buildDetailContent(title, year, medium, dims, desc, imgHtml) {
        const escTitle = escHtml(title);
        const escDesc = escHtml(desc);
        return `<style>
:root { --ink:#000; --bg:#fff; --works:#0000FF; --exhibitions:#1AFF00; --about:#FF0033; --contact:#8C00FF; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--ink); overflow-x: hidden; }
.page { max-width: 414px; margin: 0 auto; position: relative; padding-bottom: 120px; }
.header { height: 54px; background:#fff; position: sticky; top:0; z-index:10; display:flex; align-items:center; justify-content:space-between; padding: 0 13px; }
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
.back-link { display:inline-block; padding:16px 13px 0; font-size:14px; font-weight:300; color:var(--works); text-decoration:none; }
.work-image { margin:16px 13px 0; width:calc(100% - 26px); aspect-ratio:4/5; background: repeating-linear-gradient(45deg,#e6e6e6 0 12px,#d6d6d6 12px 24px); border:1px dashed #999; display:flex; align-items:center; justify-content:center; color:#555; font-size:12px; letter-spacing:0.1em; text-transform:uppercase; }
img.work-image { object-fit: cover; padding:0; border:0; background:#000; }
.title-row { padding:28px 13px 0; }
.work-title { font-weight:400; font-size:32px; line-height:1.1; color:var(--works); }
.work-meta { margin-top:8px; font-weight:250; font-size:15px; line-height:1.4; color:#000; }
.work-meta span + span::before { content:" · "; color:#666; }
.work-desc { padding:20px 13px 0; font-weight:300; font-size:15px; line-height:1.6; color:#000; max-width:60ch; white-space:pre-wrap; }
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
  .work-image { margin:24px 32px 0; width:calc(100% - 64px); aspect-ratio:16/10; }
  .title-row { padding:48px 32px 0; display:grid; grid-template-columns:1fr 280px; gap:32px; align-items:baseline; }
  .work-title { font-size:56px; }
  .work-meta { font-size:17px; margin-top:0; text-align:right; }
  .work-desc { padding:28px 32px 0; font-size:17px; line-height:1.7; max-width:64ch; }
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
  <a class="back-link" href="/works/">← Works</a>
  ${imgHtml}
  <div class="title-row">
    <h1 class="work-title">${escTitle}</h1>
    <div class="work-meta"><span>${escHtml(year)}</span><span>${escHtml(medium)}</span><span>${escHtml(dims)}</span></div>
  </div>
  <div class="work-desc">${escDesc}</div>
  <dl class="detail-list">
    <dt>Year</dt><dd>${escHtml(year)}</dd>
    <dt>Medium</dt><dd>${escHtml(medium)}</dd>
    <dt>Dimensions</dt><dd>${escHtml(dims)}</dd>
    <dt>Status</dt><dd>Available</dd>
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
