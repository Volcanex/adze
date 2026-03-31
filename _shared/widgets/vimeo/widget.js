// Widget: Vimeo
// Showcase your portfolio and track video performance.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Vimeo</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="vm-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <button data-action="settings" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Settings</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="vm-body"></div>
        </div>
    </div>`;

    let _cache = null; // last fetched data, used by vibe addon picker

    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        switch (btn.dataset.action) {
            case 'refresh':          await load(); break;
            case 'settings':         showSetup(true); break;
            case 'save-credentials': await saveCredentials(); break;
            case 'cancel-settings':  await load(); break;
        }
    });

    function showSetup(withCancel) {
        const body = c.querySelector('#vm-body');
        c.querySelector('#vm-subtitle').textContent = 'Connect your account';
        body.innerHTML = `
        <div style="max-width:420px;margin-top:16px;">
            <p style="font-size:11px;color:var(--text2);margin:0 0 20px;line-height:1.6;">
                Connect your Vimeo account using a
                <strong style="color:var(--text);">Personal Access Token</strong>.
                Create one at
                <a href="https://developer.vimeo.com/apps" target="_blank" style="color:var(--accent);">developer.vimeo.com/apps</a>
                — create an app, then generate a token with <em>Public</em> and <em>Private</em> scopes.
            </p>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div>
                    <label style="font-size:10px;font-weight:600;color:var(--text2);display:block;margin-bottom:4px;">Personal Access Token</label>
                    <input id="vm-token" type="password" placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                        style="width:100%;box-sizing:border-box;padding:7px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
                </div>
                <div id="vm-cred-error" style="font-size:10px;color:var(--danger);display:none;"></div>
                <div style="display:flex;gap:8px;margin-top:4px;">
                    <button data-action="save-credentials"
                        style="padding:6px 16px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:#fff;cursor:pointer;">
                        Connect
                    </button>
                    ${withCancel ? `<button data-action="cancel-settings"
                        style="padding:6px 16px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">
                        Cancel
                    </button>` : ''}
                </div>
            </div>
        </div>`;
    }

    async function saveCredentials() {
        const token = c.querySelector('#vm-token').value.trim();
        const errEl = c.querySelector('#vm-cred-error');
        const btn   = c.querySelector('[data-action="save-credentials"]');
        if (!token) {
            errEl.textContent = 'Access token is required.';
            errEl.style.display = 'block'; return;
        }
        btn.textContent = 'Connecting…'; btn.disabled = true;
        try {
            const r = await ctx.apiFetch('/api/adze/vimeo-verify', {
                method: 'POST', body: { access_token: token }
            });
            const d = await r.json();
            if (!r.ok || !d.ok) {
                errEl.textContent = d.error || 'Could not verify token. Make sure it has Public and Private scopes.';
                errEl.style.display = 'block';
                btn.textContent = 'Connect'; btn.disabled = false; return;
            }
            ctx.toast('Vimeo connected!');
            await load();
        } catch(e) {
            errEl.textContent = 'Connection error. Try again.';
            errEl.style.display = 'block';
            btn.textContent = 'Connect'; btn.disabled = false;
        }
    }

    function fmtNum(n) {
        if (n == null) return '—';
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
        return n.toLocaleString();
    }

    function fmtDuration(secs) {
        if (!secs) return '';
        const h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = secs % 60;
        if (h > 0) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        return `${m}:${String(s).padStart(2,'0')}`;
    }

    function renderDashboard(d) {
        _cache = d; // save for vibe addon picker
        const body = c.querySelector('#vm-body');
        c.querySelector('#vm-subtitle').textContent = d.name || 'Account';

        body.innerHTML = `
        <!-- Stats row -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;margin-bottom:28px;">
            ${[
                { label: 'Followers',     value: fmtNum(d.followers) },
                { label: 'Total Videos',  value: fmtNum(d.total_videos) },
                { label: 'Profile',       value: '<a href="https://vimeo.com/' + ctx.escHtml(d.username || '') + '" target="_blank" style="color:var(--accent);font-size:13px;text-decoration:none;">vimeo.com ↗</a>' }
            ].map(s => `
            <div style="border:1px solid var(--border);border-radius:var(--radius);padding:16px;text-align:center;">
                <div style="font-size:22px;font-weight:600;color:var(--text);font-family:var(--heading-font);">${s.value}</div>
                <div style="font-size:10px;color:var(--text2);margin-top:3px;">${s.label}</div>
            </div>`).join('')}
        </div>

        <!-- Video grid -->
        <div style="margin-bottom:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">Recent Videos</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">
        ${(d.videos || []).map(v => `
            <a href="${ctx.escHtml(v.url)}" target="_blank"
                style="display:block;text-decoration:none;color:var(--text);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;transition:border-color 0.15s;"
                onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='var(--border)'">
                <div style="position:relative;aspect-ratio:16/9;background:#111;overflow:hidden;">
                    ${v.thumbnail ? `<img src="${ctx.escHtml(v.thumbnail)}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;">` : ''}
                    <div style="position:absolute;bottom:5px;right:6px;background:rgba(0,0,0,0.8);color:#fff;font-size:9px;padding:1px 5px;border-radius:3px;">${fmtDuration(v.duration)}</div>
                </div>
                <div style="padding:8px 10px 10px;">
                    <div style="font-size:11px;font-weight:500;color:var(--text);line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${ctx.escHtml(v.title)}</div>
                    <div style="display:flex;gap:10px;margin-top:5px;">
                        <span style="font-size:10px;color:var(--text2);">▶ ${fmtNum(v.plays)}</span>
                        ${v.likes != null ? `<span style="font-size:10px;color:var(--text2);">♥ ${fmtNum(v.likes)}</span>` : ''}
                    </div>
                </div>
            </a>`).join('')}
        </div>`;
    }

    async function load() {
        const body = c.querySelector('#vm-body');
        body.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/vimeo-stats');
            const d = await r.json();
            if (!r.ok) { body.innerHTML = `<div style="color:var(--danger);font-size:11px;">${ctx.escHtml(d.error || 'Error loading stats')}</div>`; return; }
            if (!d.configured) { showSetup(false); return; }
            renderDashboard(d);
        } catch(e) {
            body.innerHTML = '<div style="color:var(--danger);font-size:11px;">Failed to load Vimeo stats</div>';
        }
    }

    // ── Vibe coder addon: video picker ──────────────────────────────────────
    function _showVideoPicker(videos) {
        return new Promise(resolve => {
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:10000;display:flex;align-items:center;justify-content:center;';

            const panel = document.createElement('div');
            panel.style.cssText = 'background:var(--surface,#1e1e1e);border:1px solid var(--border,#333);border-radius:8px;padding:20px;width:700px;max-width:92vw;max-height:82vh;display:flex;flex-direction:column;gap:14px;';

            const header = document.createElement('div');
            header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;flex-shrink:0;';
            header.innerHTML = `
                <span style="font-size:13px;font-weight:600;color:var(--text,#eee);">Pick a Vimeo video</span>
                <button id="vm-pk-close" style="background:none;border:none;cursor:pointer;color:var(--text2,#888);font-size:20px;line-height:1;padding:0 4px;">×</button>`;

            const grid = document.createElement('div');
            grid.style.cssText = 'overflow-y:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;';

            videos.forEach(v => {
                const item = document.createElement('div');
                item.style.cssText = 'cursor:pointer;border:2px solid var(--border,#333);border-radius:6px;overflow:hidden;transition:border-color 0.15s;';
                item.innerHTML = `
                    <div style="aspect-ratio:16/9;overflow:hidden;background:#000;">
                        ${v.thumbnail ? `<img src="${ctx.escHtml(v.thumbnail)}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;">` : '<div style="width:100%;height:100%;background:#222;"></div>'}
                    </div>
                    <div style="padding:6px 8px 8px;">
                        <div style="font-size:10px;color:var(--text,#eee);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${ctx.escHtml(v.title)}</div>
                        <div style="font-size:9px;color:var(--text2,#888);margin-top:3px;">▶ ${fmtNum(v.plays)}</div>
                    </div>`;
                item.addEventListener('mouseenter', () => item.style.borderColor = 'var(--accent,#7c6fe0)');
                item.addEventListener('mouseleave', () => item.style.borderColor = 'var(--border,#333)');
                item.addEventListener('click', () => {
                    // Extract Vimeo video ID from URL (e.g. https://vimeo.com/123456789)
                    const idMatch = (v.url || '').match(/vimeo\.com\/(\d+)/);
                    const vimeoId = idMatch ? idMatch[1] : '';
                    const embed = vimeoId
                        ? `<iframe src="https://player.vimeo.com/video/${vimeoId}" width="640" height="360" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`
                        : v.url;
                    cleanup(`Vimeo video "${v.title}" — embed code: ${embed}`);
                });
                grid.appendChild(item);
            });

            panel.appendChild(header);
            panel.appendChild(grid);
            overlay.appendChild(panel);
            document.body.appendChild(overlay);

            function cleanup(result) {
                document.body.removeChild(overlay);
                document.removeEventListener('keydown', onKey);
                resolve(result);
            }

            function onKey(e) { if (e.key === 'Escape') cleanup(null); }
            document.addEventListener('keydown', onKey);
            overlay.addEventListener('click', e => { if (e.target === overlay) cleanup(null); });
            panel.querySelector('#vm-pk-close').addEventListener('click', () => cleanup(null));
        });
    }

    ctx.registerVibeAddon({
        id: 'vimeo-video',
        label: 'Vimeo Video',
        async pick() {
            let videos = _cache?.videos;
            if (!videos || videos.length === 0) {
                try {
                    const r = await ctx.apiFetch('/api/adze/vimeo-stats');
                    const d = await r.json();
                    if (!r.ok || !d.configured) return null;
                    _cache = d;
                    videos = d.videos || [];
                } catch(e) { return null; }
            }
            if (videos.length === 0) { ctx.toast('No videos found', 'error'); return null; }
            return _showVideoPicker(videos);
        }
    });

    load();
})(ctx);
