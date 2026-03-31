// Widget: Subscribers
// Build and manage your mailing list.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Subscribers</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="sb-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <input id="sb-search" type="search" placeholder="Search…" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);width:130px;">
                    <a id="sb-export-link" href="/api/adze/export-subscribers" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;">Export CSV ↓</a>
                    <button data-action="add-to-site" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">+ Add to site</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="sb-list" style="margin-top:16px;"></div>
        </div>
    </div>`;

    let subscribers = [];

    // Build export URL with auth headers isn't possible via anchor tag —
    // use a fetch+blob approach
    c.querySelector('#sb-export-link').addEventListener('click', async function(e) {
        e.preventDefault();
        try {
            const r = await ctx.apiFetch('/api/adze/export-subscribers');
            if (!r.ok) { ctx.toast('Export failed', 'error'); return; }
            const blob = new Blob([await r.text()], { type: 'text/csv' });
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href = url; a.download = 'subscribers.csv'; a.click();
            URL.revokeObjectURL(url);
            ctx.toast('Exported!');
        } catch(e) { ctx.toast('Export failed', 'error'); }
    });

    c.querySelector('#sb-search').addEventListener('input', render);

    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        switch (btn.dataset.action) {
            case 'refresh': await load(); break;
            case 'add-to-site':
                ctx.sendToVibeCoder(
                    `Add a newsletter signup form to my site. When submitted it should POST to /api/adze/subscribe with JSON body: { artist_slug: "${ctx.artistSlug}", email, name (optional) }. On success show "Thanks for subscribing!", if already subscribed show "You're already subscribed." Style it to match my existing design.`
                );
                break;
            case 'delete':
                await deleteSub(btn.dataset.email);
                break;
        }
    });

    function render() {
        const list  = c.querySelector('#sb-list');
        const query = c.querySelector('#sb-search').value.trim().toLowerCase();
        let items = subscribers;
        if (query) items = items.filter(s =>
            s.email.toLowerCase().includes(query) || (s.name || '').toLowerCase().includes(query)
        );

        c.querySelector('#sb-subtitle').textContent =
            `${subscribers.length} subscriber${subscribers.length !== 1 ? 's' : ''}`;

        if (items.length === 0) {
            list.innerHTML = `<div style="text-align:center;padding:40px 0;color:var(--text2);font-size:12px;">
                ${query ? 'No matches' : 'No subscribers yet'}
            </div>`;
            return;
        }

        list.innerHTML = `
        <table style="width:100%;border-collapse:collapse;font-size:11px;">
            <thead>
                <tr style="border-bottom:2px solid var(--border);">
                    <th style="text-align:left;padding:6px 8px;color:var(--text2);font-weight:600;font-size:10px;">Email</th>
                    <th style="text-align:left;padding:6px 8px;color:var(--text2);font-weight:600;font-size:10px;">Name</th>
                    <th style="text-align:left;padding:6px 8px;color:var(--text2);font-weight:600;font-size:10px;">Subscribed</th>
                    <th style="width:40px;"></th>
                </tr>
            </thead>
            <tbody>
            ${items.map(s => {
                const date = s.ts ? new Date(s.ts * 1000).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '';
                return `<tr style="border-bottom:1px solid var(--border);">
                    <td style="padding:8px;color:var(--text);">${ctx.escHtml(s.email)}</td>
                    <td style="padding:8px;color:var(--text2);">${ctx.escHtml(s.name || '—')}</td>
                    <td style="padding:8px;color:var(--text2);font-size:10px;">${date}</td>
                    <td style="padding:8px;text-align:right;">
                        <button data-action="delete" data-email="${ctx.escHtml(s.email)}"
                            style="padding:2px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">×</button>
                    </td>
                </tr>`;
            }).join('')}
            </tbody>
        </table>`;
    }

    async function load() {
        const list = c.querySelector('#sb-list');
        list.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/list-subscribers');
            if (!r.ok) throw new Error('Failed');
            const data = await r.json();
            subscribers = data.subscribers || [];
            render();
        } catch(e) {
            list.innerHTML = '<div style="padding:20px 0;color:var(--danger);font-size:11px;">Failed to load subscribers</div>';
        }
    }

    async function deleteSub(email) {
        if (!confirm(`Remove ${email} from your list?`)) return;
        await ctx.apiFetch('/api/adze/delete-subscriber', { method: 'POST', body: { email } });
        subscribers = subscribers.filter(s => s.email !== email);
        render();
        ctx.toast('Removed');
    }

    load();
})(ctx);
