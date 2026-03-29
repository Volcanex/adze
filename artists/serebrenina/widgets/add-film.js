// Widget: Add Film
// Upload a video, give it a name and date, and it creates a new film page + updates the nav on all pages.

(function(ctx) {
    const container = ctx.container;
    container.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;padding:0;overflow:hidden;';

    container.innerHTML = `
        <div style="padding:20px 20px 12px;flex-shrink:0;">
            <h3 style="margin:0 0 4px;font-size:16px;">Add Film</h3>
            <p style="color:var(--text2);font-size:12px;margin:0;">Upload a video to create a new film page automatically.</p>
        </div>
        <div style="flex:1;overflow-y:auto;padding:0 20px 20px;" id="film-content">
            <div id="film-form">
                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:var(--text2);">Film Title *</label>
                    <input type="text" id="film-title" placeholder="e.g. Summer in Berlin" style="width:100%;padding:8px 12px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                </div>
                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:var(--text2);">Year / Date</label>
                    <input type="text" id="film-date" placeholder="e.g. 2025" style="width:100%;padding:8px 12px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);">
                </div>
                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:var(--text2);">Description (optional)</label>
                    <textarea id="film-desc" rows="3" placeholder="A short description of the film..." style="width:100%;padding:8px 12px;font-size:13px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);resize:vertical;font-family:inherit;"></textarea>
                </div>
                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:var(--text2);">Video File *</label>
                    <div id="film-dropzone" style="border:2px dashed var(--border);border-radius:6px;padding:32px;text-align:center;cursor:pointer;transition:border-color 0.2s;">
                        <input type="file" id="film-file" accept="video/*" style="display:none;">
                        <p style="color:var(--text2);font-size:13px;margin:0;" id="film-file-label">Click or drag a video file here</p>
                        <p style="color:var(--text2);font-size:11px;margin:4px 0 0;opacity:0.6;">MP4, MOV, WebM, etc.</p>
                    </div>
                </div>
                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:var(--text2);">Thumbnail Image (optional)</label>
                    <div id="thumb-dropzone" style="border:2px dashed var(--border);border-radius:6px;padding:20px;text-align:center;cursor:pointer;transition:border-color 0.2s;">
                        <input type="file" id="film-thumb" accept="image/*" style="display:none;">
                        <p style="color:var(--text2);font-size:12px;margin:0;" id="thumb-file-label">Click to add a poster image</p>
                    </div>
                </div>
                <button id="film-submit" class="widget-btn widget-btn-primary" style="width:100%;padding:10px;font-size:13px;" disabled>
                    Upload & Create Film Page
                </button>
                <div id="film-progress" style="display:none;margin-top:12px;">
                    <div style="height:4px;background:var(--border);border-radius:2px;overflow:hidden;">
                        <div id="film-bar" style="height:100%;background:var(--accent,#6b8cae);width:0%;transition:width 0.3s;border-radius:2px;"></div>
                    </div>
                    <p id="film-status" style="font-size:11px;color:var(--text2);margin:6px 0 0;"></p>
                </div>
            </div>
            <div id="film-list" style="margin-top:24px;">
                <h4 style="font-size:13px;font-weight:600;margin-bottom:10px;color:var(--text2);text-transform:uppercase;letter-spacing:0.3px;">Existing Films</h4>
                <div id="film-list-items" style="color:var(--text2);font-size:13px;">Loading...</div>
            </div>
        </div>
    `;

    let selectedFile = null;
    let selectedThumb = null;

    // Dropzone interactions
    const dropzone = document.getElementById('film-dropzone');
    const fileInput = document.getElementById('film-file');
    const thumbDropzone = document.getElementById('thumb-dropzone');
    const thumbInput = document.getElementById('film-thumb');

    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.style.borderColor = 'var(--accent,#6b8cae)'; });
    dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor = 'var(--border)'; });
    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files.length) { selectedFile = e.dataTransfer.files[0]; updateFileLabel(); }
    });
    fileInput.addEventListener('change', () => { selectedFile = fileInput.files[0]; updateFileLabel(); });

    thumbDropzone.addEventListener('click', () => thumbInput.click());
    thumbInput.addEventListener('change', () => {
        selectedThumb = thumbInput.files[0];
        document.getElementById('thumb-file-label').textContent = selectedThumb ? selectedThumb.name : 'Click to add a poster image';
    });

    function updateFileLabel() {
        document.getElementById('film-file-label').textContent = selectedFile ? selectedFile.name : 'Click or drag a video file here';
        checkReady();
    }

    document.getElementById('film-title').addEventListener('input', checkReady);

    function checkReady() {
        const title = document.getElementById('film-title').value.trim();
        document.getElementById('film-submit').disabled = !(title && selectedFile);
    }

    // Slugify title
    function slugify(text) {
        return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').substring(0, 60);
    }

    // Submit
    document.getElementById('film-submit').addEventListener('click', async () => {
        const title = document.getElementById('film-title').value.trim();
        const date = document.getElementById('film-date').value.trim();
        const desc = document.getElementById('film-desc').value.trim();
        const slug = slugify(title);

        if (!title || !selectedFile) return;

        const btn = document.getElementById('film-submit');
        const progress = document.getElementById('film-progress');
        const bar = document.getElementById('film-bar');
        const status = document.getElementById('film-status');

        btn.disabled = true;
        btn.textContent = 'Creating...';
        progress.style.display = 'block';

        try {
            // Step 1: Upload video
            status.textContent = 'Uploading video...';
            bar.style.width = '10%';

            const formData = new FormData();
            formData.append('file', selectedFile);
            const uploadRes = await ctx.apiFetch('/api/sandbox/upload-file', { method: 'POST', body: formData });
            const uploadData = await uploadRes.json();
            if (!uploadData.success) throw new Error(uploadData.error || 'Upload failed');

            const videoPath = uploadData.url;
            bar.style.width = '40%';

            // Step 2: Upload thumbnail if provided
            let thumbPath = '';
            if (selectedThumb) {
                status.textContent = 'Uploading thumbnail...';
                const thumbForm = new FormData();
                thumbForm.append('file', selectedThumb);
                const thumbRes = await ctx.apiFetch('/api/sandbox/upload-file', { method: 'POST', body: thumbForm });
                const thumbData = await thumbRes.json();
                if (thumbData.success) thumbPath = thumbData.url;
            }
            bar.style.width = '60%';

            // Step 3: Get the CSS + nav from home page to keep consistent styling
            status.textContent = 'Building page...';
            const homeRes = await ctx.apiFetch('/api/sandbox/get-page-content?page_slug=home');
            const homeData = await homeRes.json();
            const homeContent = homeData.content || '';

            // Extract CSS from home
            const cssMatch = homeContent.match(/<style>([\s\S]*?)<\/style>/);
            const css = cssMatch ? cssMatch[1] : '';

            // Extract the nav HTML from home (sidebar + mobile header)
            const htmlMatch = homeContent.match(/<html>([\s\S]*?)<\/html>/);
            const homeHtml = htmlMatch ? htmlMatch[1] : '';

            // Find the sidebar block and nav-links to inject "Films" section
            // We'll extract everything up to <main and rebuild
            const sidebarMatch = homeHtml.match(/([\s\S]*?)<main[\s\S]*/);
            let navHtml = sidebarMatch ? sidebarMatch[1] : homeHtml;

            // Build film page content
            const displayTitle = date ? `${title}, ${date}` : title;
            const posterAttr = thumbPath ? ` poster="${thumbPath}"` : '';

            const videoCSS = `
/* ── Film Page ── */
.film-content {
    flex: 1;
    padding: 60px 48px;
    max-width: 960px;
    animation: gentleFade 1s ease-out 0.3s both;
}
.film-title {
    font-style: italic;
    font-weight: 400;
    font-size: 1.8rem;
    margin-bottom: 8px;
}
.film-date {
    color: var(--text-muted);
    font-size: 13px;
    margin-bottom: 24px;
}
.film-desc {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 32px;
    max-width: 560px;
}
.film-player {
    width: 100%;
    border-radius: 2px;
    background: #000;
}
@media (max-width: 768px) {
    .film-content { padding: 24px 16px; }
    .film-title { font-size: 1.4rem; }
}`;

            const filmHtml = `
<main class="film-content">
    <h1 class="film-title">${displayTitle}</h1>
    ${date ? `<p class="film-date">${date}</p>` : ''}
    ${desc ? `<p class="film-desc">${desc}</p>` : ''}
    <video class="film-player" controls playsinline${posterAttr}>
        <source src="${videoPath}" type="${selectedFile.type || 'video/mp4'}">
        Your browser does not support the video tag.
    </video>
</main>`;

            const pageContent = `<style>${css}${videoCSS}\n</style>\n<html>\n${navHtml}\n${filmHtml}\n</html>`;

            bar.style.width = '75%';

            // Step 4: Create the page
            status.textContent = 'Creating page...';
            const createRes = await ctx.apiFetch('/api/sandbox/create-page', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    page_slug: slug,
                    title: displayTitle,
                    description: desc || `Film: ${title}`,
                    content: pageContent
                })
            });
            const createData = await createRes.json();
            if (!createData.success) throw new Error(createData.error || 'Page creation failed');

            bar.style.width = '85%';

            // Step 5: Update nav on ALL existing pages to include this film
            status.textContent = 'Updating navigation...';
            await updateNavOnAllPages(slug, displayTitle);

            bar.style.width = '100%';
            status.textContent = 'Done! Film page created.';
            btn.textContent = 'Upload & Create Film Page';

            // Reset form
            setTimeout(() => {
                document.getElementById('film-title').value = '';
                document.getElementById('film-date').value = '';
                document.getElementById('film-desc').value = '';
                selectedFile = null;
                selectedThumb = null;
                document.getElementById('film-file-label').textContent = 'Click or drag a video file here';
                document.getElementById('thumb-file-label').textContent = 'Click to add a poster image';
                fileInput.value = '';
                thumbInput.value = '';
                btn.disabled = true;
                progress.style.display = 'none';
                bar.style.width = '0%';
                loadFilmList();
            }, 1500);

        } catch (err) {
            status.textContent = 'Error: ' + err.message;
            status.style.color = 'var(--danger,#c0392b)';
            btn.disabled = false;
            btn.textContent = 'Upload & Create Film Page';
        }
    });

    // Update nav across all pages to include a Films dropdown
    async function updateNavOnAllPages(newSlug, newTitle) {
        const pagesRes = await ctx.apiFetch('/api/sandbox/list-pages');
        const pagesData = await pagesRes.json();
        const pages = pagesData.pages || [];

        // Find all existing film pages by checking for film-player class in content
        // We'll build the full films list from what's in the nav + the new one
        for (const page of pages) {
            try {
                const res = await ctx.apiFetch(`/api/sandbox/get-page-content?page_slug=${page.slug}`);
                const data = await res.json();
                let content = data.content || '';

                if (!content) continue;

                // Check if there's already a Films nav-category section
                const hasFilmsNav = content.includes('nav-category') && content.includes('Films');

                if (hasFilmsNav) {
                    // Add new film link to existing Films dropdown
                    // Find the Films dropdown and add before </ul>
                    const filmsDropdownRegex = /(Films<\/span>\s*<ul class="nav-dropdown">)([\s\S]*?)(<\/ul>)/;
                    const match = content.match(filmsDropdownRegex);
                    if (match) {
                        // Check if this film is already listed
                        if (!match[2].includes(`../${newSlug}/`)) {
                            const newLink = `\n            <li><a href="../${newSlug}/">${newTitle}</a></li>`;
                            content = content.replace(filmsDropdownRegex, `$1$2${newLink}\n        $3`);
                        }
                    }
                } else {
                    // No Films nav yet — inject it before nav-links (About etc.)
                    // We need to add the nav-category + dropdown pattern
                    const filmsNavBlock = `
        <span class="nav-category" onclick="this.nextElementSibling.classList.toggle('open')">Films</span>
        <ul class="nav-dropdown">
            <li><a href="../${newSlug}/">${newTitle}</a></li>
        </ul>`;

                    // Also need to add the nav-category/dropdown CSS if not present
                    if (!content.includes('.nav-category')) {
                        const navCategoryCSS = `
/* ── Nav Categories ── */
.nav-section {
    display: flex;
    flex-direction: column;
    gap: 0;
}
.nav-category {
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    padding: 6px 0;
    transition: color 0.4s ease;
    user-select: none;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.nav-category:hover { color: var(--accent); }
.nav-dropdown {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.5s ease-out;
    padding-left: 0;
    list-style: none;
}
.nav-dropdown.open {
    max-height: 500px;
    margin-top: 4px;
    margin-bottom: 10px;
}
.nav-dropdown li {
    margin-bottom: 4px;
    opacity: 0;
    transform: translateX(-6px);
    transition: opacity 0.35s ease, transform 0.35s ease;
}
.nav-dropdown.open li {
    opacity: 1;
    transform: translateX(0);
}
.nav-dropdown.open li:nth-child(1) { transition-delay: 0.05s; }
.nav-dropdown.open li:nth-child(2) { transition-delay: 0.1s; }
.nav-dropdown.open li:nth-child(3) { transition-delay: 0.15s; }
.nav-dropdown.open li:nth-child(4) { transition-delay: 0.2s; }
.nav-dropdown.open li:nth-child(5) { transition-delay: 0.25s; }
.nav-dropdown.open li:nth-child(6) { transition-delay: 0.3s; }
.nav-dropdown a {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 400;
    padding-left: 8px;
    display: block;
    transition: color 0.3s ease, padding-left 0.3s ease;
}
.nav-dropdown a:hover {
    color: var(--accent);
    padding-left: 14px;
}
@media (max-width: 768px) {
    .nav-category { font-size: 11px; padding: 5px 0; }
    .nav-dropdown.open { margin-bottom: 6px; }
    .nav-dropdown a { font-size: 12px; }
}`;
                        // Inject CSS before </style>
                        content = content.replace('</style>', navCategoryCSS + '\n</style>');
                    }

                    // Inject the Films nav — convert nav-links into a nav-section wrapper
                    // Look for the <ul class="nav-links"> pattern in both sidebar and sidebar-inner
                    // We inject the Films block right before <ul class="nav-links">
                    const navLinksPattern = /<ul class="nav-links">/g;
                    // Wrap in nav-section if not already wrapped
                    if (!content.includes('nav-section')) {
                        // Add nav-section wrapper: insert Films dropdown before nav-links
                        content = content.replace(navLinksPattern, (match) => {
                            return `<nav class="nav-section">\n${filmsNavBlock}\n    </nav>\n\n    ${match}`;
                        });
                    } else {
                        // nav-section exists, add Films before </nav>
                        content = content.replace(/<\/nav>/g, filmsNavBlock + '\n    </nav>');
                    }
                }

                // Save the updated page
                await ctx.apiFetch('/api/sandbox/edit-page', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ page_slug: page.slug, content: content })
                });
            } catch (err) {
                console.warn(`Failed to update nav on ${page.slug}:`, err);
            }
        }
    }

    // Load existing film pages
    async function loadFilmList() {
        const listEl = document.getElementById('film-list-items');
        try {
            const res = await ctx.apiFetch('/api/sandbox/list-pages');
            const data = await res.json();
            const pages = data.pages || [];

            // Filter to film pages (pages with film-player in content)
            const films = [];
            for (const page of pages) {
                if (page.slug === 'home' || page.slug === 'about' || page.slug === 'gallery' || page.slug === 'bookings') continue;
                try {
                    const r = await ctx.apiFetch(`/api/sandbox/get-page-content?page_slug=${page.slug}`);
                    const d = await r.json();
                    if (d.content && d.content.includes('film-player')) {
                        films.push({ slug: page.slug, title: page.title || page.slug });
                    }
                } catch(e) {}
            }

            if (films.length === 0) {
                listEl.innerHTML = '<p style="color:var(--text2);font-size:13px;opacity:0.6;">No films yet. Upload one above!</p>';
                return;
            }

            listEl.innerHTML = films.map(f => `
                <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--surface);border:1px solid var(--border);border-radius:4px;margin-bottom:6px;">
                    <div>
                        <span style="font-size:13px;font-weight:500;">${f.title}</span>
                        <a href="../${f.slug}/" target="_blank" style="font-size:11px;color:var(--accent,#6b8cae);margin-left:8px;">View →</a>
                    </div>
                </div>
            `).join('');
        } catch (err) {
            listEl.innerHTML = `<p style="color:var(--danger);font-size:12px;">Error loading films</p>`;
        }
    }

    loadFilmList();

})(ctx);
