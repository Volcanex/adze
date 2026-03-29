// Widget: Add to Gallery
// Lets the artist pick images from their assets and append them to the gallery page.

(function(ctx) {
    const container = ctx.container;

    container.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;padding:0;overflow:hidden;';
    container.innerHTML = `
        <div style="padding:20px 20px 12px;">
            <h3 style="margin:0 0 8px;">Add to Gallery</h3>
            <p style="color:var(--text2);font-size:13px;margin:0;">
                Select images from your assets to add to the gallery page.
            </p>
        </div>
        <div style="flex:1;overflow-y:auto;padding:0 20px;">
            <div class="widget-grid" id="galleryPickerGrid"></div>
        </div>
        <div style="display:flex;gap:10px;align-items:center;padding:12px 20px;border-top:1px solid var(--border);background:var(--bg2);flex-shrink:0;">
            <button class="widget-btn widget-btn-primary" id="galleryAddBtn" disabled>Add Selected to Gallery</button>
            <span id="gallerySelectedCount" style="color:var(--text2);font-size:12px;">0 selected</span>
            <div id="galleryStatus" style="flex:1;"></div>
        </div>
    `;

    let selected = new Set();

    function renderGrid() {
        const grid = document.getElementById('galleryPickerGrid');
        grid.innerHTML = '';
        const images = ctx.assetList.filter(a => a.is_image);
        if (images.length === 0) {
            grid.innerHTML = '<div style="grid-column:1/-1;color:var(--text2);font-size:13px;">No image assets found. Upload some in the Assets tab.</div>';
            return;
        }
        images.forEach(a => {
            const card = document.createElement('div');
            card.className = 'widget-card' + (selected.has(a.path) ? ' selected' : '');
            const imgSrc = `/artists/${ctx.artistSlug}/assets/${a.path}`;
            card.innerHTML = `<img src="${imgSrc}" alt="${a.filename}"><div class="wc-label">${a.filename}</div>`;
            card.onclick = () => {
                if (selected.has(a.path)) selected.delete(a.path);
                else selected.add(a.path);
                card.classList.toggle('selected');
                updateCount();
            };
            grid.appendChild(card);
        });
    }

    function updateCount() {
        document.getElementById('gallerySelectedCount').textContent = selected.size + ' selected';
        document.getElementById('galleryAddBtn').disabled = selected.size === 0;
    }

    document.getElementById('galleryAddBtn').addEventListener('click', async () => {
        if (selected.size === 0) return;

        const statusEl = document.getElementById('galleryStatus');
        statusEl.innerHTML = '<div class="widget-status" style="color:var(--text2)">Adding images to gallery...</div>';

        try {
            // Fetch the gallery page content
            const pageData = await ctx.getPageContent('gallery');
            if (!pageData) {
                statusEl.innerHTML = '<div class="widget-status error">Gallery page not found.</div>';
                return;
            }

            let content = pageData.content;

            // Build new table rows — 3 images per row to match existing format
            const paths = Array.from(selected);
            let newHtml = '';

            for (let i = 0; i < paths.length; i += 3) {
                const row = paths.slice(i, i + 3);
                const cells = row.map(p => `<td><img src="../assets/${p}" width="250" border="0"></td>`).join('\n');
                newHtml += `\n<br>\n<table border="5" cellpadding="10">\n<tr>\n${cells}\n</tr>\n</table>`;
            }

            // Insert before the closing </center> or </html> tag
            if (content.includes('</center>')) {
                content = content.replace(/([\s\S]*)<\/center>/, '$1' + newHtml + '\n</center>');
            } else if (content.includes('</html>')) {
                content = content.replace('</html>', newHtml + '\n</html>');
            } else {
                content += newHtml;
            }

            // Save the updated gallery page
            const ok = await ctx.savePage('gallery', content, pageData.config);
            if (ok) {
                statusEl.innerHTML = `<div class="widget-status success">Added ${paths.length} image${paths.length > 1 ? 's' : ''} to gallery!</div>`;
                selected.clear();
                renderGrid();
                updateCount();
            } else {
                statusEl.innerHTML = '<div class="widget-status error">Failed to save gallery page.</div>';
            }
        } catch(e) {
            statusEl.innerHTML = `<div class="widget-status error">Error: ${e.message}</div>`;
        }
    });

    // Initial render
    renderGrid();
})(ctx);
