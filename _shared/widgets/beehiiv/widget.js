// Widget: Beehiiv
// Track your newsletter stats and recent posts.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Beehiiv</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="bh-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <button data-action="settings" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Settings</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="bh-body"></div>
        </div>
    </div>`;

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
        const body = c.querySelector('#bh-body');
        c.querySelector('#bh-subtitle').textContent = 'Connect your newsletter';
        body.innerHTML = `
        <div style="max-width:420px;margin-top:16px;">
            <p style="font-size:11px;color:var(--text2);margin:0 0 20px;line-height:1.6;">
                Connect your Beehiiv newsletter. You'll need your
                <strong style="color:var(--text);">API Key</strong> (Settings → API) and
                <strong style="color:var(--text);">Publication ID</strong> (Settings → Publication → your pub_xxx ID).
            </p>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div>
                    <label style="font-size:10px;font-weight:600;color:var(--text2);display:block;margin-bottom:4px;">API Key</label>
                    <input id="bh-api-key" type="password" placeholder="key_…"
                        style="width:100%;box-sizing:border-box;padding:7px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
                </div>
                <div>
                    <label style="font-size:10px;font-weight:600;color:var(--text2);display:block;margin-bottom:4px;">Publication ID</label>
                    <input id="bh-pub-id" type="text" placeholder="pub_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                        style="width:100%;box-sizing:border-box;padding:7px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
                </div>
                <div id="bh-cred-error" style="font-size:10px;color:var(--danger);display:none;"></div>
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
        const apiKey = c.querySelector('#bh-api-key').value.trim();
        const pubId  = c.querySelector('#bh-pub-id').value.trim();
        const errEl  = c.querySelector('#bh-cred-error');
        const btn    = c.querySelector('[data-action="save-credentials"]');
        if (!apiKey || !pubId) {
            errEl.textContent = 'Both fields are required.';
            errEl.style.display = 'block'; return;
        }
        btn.textContent = 'Connecting…'; btn.disabled = true;
        try {
            const r = await ctx.apiFetch('/api/adze/beehiiv-verify', {
                method: 'POST', body: { api_key: apiKey, publication_id: pubId }
            });
            const d = await r.json();
            if (!r.ok || !d.ok) {
                errEl.textContent = d.error || 'Could not verify credentials.';
                errEl.style.display = 'block';
                btn.textContent = 'Connect'; btn.disabled = false; return;
            }
            ctx.toast('Beehiiv connected!');
            await load();
        } catch(e) {
            errEl.textContent = 'Connection error. Try again.';
            errEl.style.display = 'block';
            btn.textContent = 'Connect'; btn.disabled = false;
        }
    }

    function pct(val) {
        if (val == null) return '—';
        return (val * 100).toFixed(1) + '%';
    }

    function fmtNum(n) {
        if (n == null) return '—';
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
        return n.toLocaleString();
    }

    function renderDashboard(d) {
        const body = c.querySelector('#bh-body');
        c.querySelector('#bh-subtitle').textContent = d.name || 'Newsletter';

        const posts = d.posts || [];
        const avgOpen  = posts.length ? posts.reduce((a, p) => a + (p.open_rate  || 0), 0) / posts.length : null;
        const avgClick = posts.length ? posts.reduce((a, p) => a + (p.click_rate || 0), 0) / posts.length : null;

        body.innerHTML = `
        <!-- Stats row -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;margin-bottom:28px;">
            ${[
                { label: 'Subscribers',    value: fmtNum(d.subscribers) },
                { label: 'Avg Open Rate',  value: pct(avgOpen) },
                { label: 'Avg Click Rate', value: pct(avgClick) }
            ].map(s => `
            <div style="border:1px solid var(--border);border-radius:var(--radius);padding:16px;text-align:center;">
                <div style="font-size:22px;font-weight:600;color:var(--text);font-family:var(--heading-font);">${s.value}</div>
                <div style="font-size:10px;color:var(--text2);margin-top:3px;">${s.label}</div>
            </div>`).join('')}
        </div>

        <!-- Recent posts -->
        <div style="margin-bottom:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">Recent Posts</div>
        ${posts.length === 0
            ? `<div style="color:var(--text2);font-size:11px;padding:20px 0;">No published posts yet.</div>`
            : `<div style="border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;">
            ${posts.map((p, i) => {
                const date = p.publish_date ? new Date(p.publish_date * 1000).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '';
                return `<div style="padding:12px 16px;${i > 0 ? 'border-top:1px solid var(--border);' : ''}display:flex;align-items:baseline;gap:12px;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:12px;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            ${p.web_url ? `<a href="${ctx.escHtml(p.web_url)}" target="_blank" style="color:inherit;text-decoration:none;">${ctx.escHtml(p.title)}</a>` : ctx.escHtml(p.title)}
                        </div>
                        <div style="font-size:10px;color:var(--text2);margin-top:2px;">${date}</div>
                    </div>
                    <div style="display:flex;gap:16px;flex-shrink:0;text-align:right;">
                        <div>
                            <div style="font-size:12px;font-weight:500;color:var(--text);">${pct(p.open_rate)}</div>
                            <div style="font-size:9px;color:var(--text2);">Open</div>
                        </div>
                        <div>
                            <div style="font-size:12px;font-weight:500;color:var(--text);">${pct(p.click_rate)}</div>
                            <div style="font-size:9px;color:var(--text2);">Click</div>
                        </div>
                        <div>
                            <div style="font-size:12px;font-weight:500;color:var(--text);">${fmtNum(p.recipients)}</div>
                            <div style="font-size:9px;color:var(--text2);">Sent</div>
                        </div>
                    </div>
                </div>`;
            }).join('')}
            </div>`}`;
    }

    async function load() {
        const body = c.querySelector('#bh-body');
        body.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/beehiiv-stats');
            const d = await r.json();
            if (!r.ok) { body.innerHTML = `<div style="color:var(--danger);font-size:11px;">${ctx.escHtml(d.error || 'Error loading stats')}</div>`; return; }
            if (!d.configured) { showSetup(false); return; }
            renderDashboard(d);
        } catch(e) {
            body.innerHTML = '<div style="color:var(--danger);font-size:11px;">Failed to load Beehiiv stats</div>';
        }
    }

    load();
})(ctx);
