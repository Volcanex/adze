// Widget: Inbox
// View and manage contact form submissions sent from your site.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Inbox</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="ib-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <select id="ib-filter" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);cursor:pointer;">
                        <option value="all">All</option>
                        <option value="unread">Unread</option>
                        <option value="read">Read</option>
                    </select>
                    <button data-action="mark-all-read" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Mark all read</button>
                    <button data-action="add-to-site" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">+ Add to site</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="ib-list" style="margin-top:16px;"></div>
        </div>
    </div>`;

    let submissions = [];

    // ── Event delegation ──
    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (btn) {
            switch (btn.dataset.action) {
                case 'refresh':       await load(); break;
                case 'mark-all-read': await markAllRead(); break;
                case 'add-to-site':
                    ctx.sendToVibeCoder(
                        `Add a contact form to my site. When submitted it should POST to /api/adze/contact with JSON body: { artist_slug: "${ctx.artistSlug}", name, email, subject, message }. Show a success message on submission and reset the form. Style it to match my existing design.`
                    );
                    break;
                case 'delete':
                    await deleteSubmission(btn.dataset.id);
                    break;
                case 'toggle-read':
                    await toggleRead(btn.dataset.id, btn.dataset.read !== 'true');
                    break;
                case 'expand':
                    toggleExpand(btn.dataset.id);
                    break;
            }
            return;
        }
        // Click anywhere on message row to expand
        const row = e.target.closest('.ib-row');
        if (row) toggleExpand(row.dataset.id);
    });

    c.querySelector('#ib-filter').addEventListener('change', render);

    function render() {
        const filter = c.querySelector('#ib-filter').value;
        const list   = c.querySelector('#ib-list');
        let items = submissions;
        if (filter === 'unread') items = items.filter(s => !s.read);
        if (filter === 'read')   items = items.filter(s => s.read);

        const unread = submissions.filter(s => !s.read).length;
        c.querySelector('#ib-subtitle').textContent =
            unread > 0 ? `${unread} unread message${unread !== 1 ? 's' : ''}` : `${submissions.length} message${submissions.length !== 1 ? 's' : ''}`;

        if (items.length === 0) {
            list.innerHTML = `<div style="text-align:center;padding:40px 0;color:var(--text2);font-size:12px;">
                ${filter === 'all' ? 'No messages yet' : 'Nothing here'}
            </div>`;
            return;
        }

        list.innerHTML = items.map(s => {
            const date = s.ts ? new Date(s.ts * 1000).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '';
            const preview = (s.message || '').slice(0, 80).replace(/\n/g, ' ');
            return `<div class="ib-row${!s.read ? ' ib-unread' : ''}" data-id="${ctx.escHtml(s.id)}"
                style="border-bottom:1px solid var(--border);padding:12px 0;cursor:pointer;transition:background 0.1s;">
                <div style="display:flex;align-items:baseline;gap:10px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:${!s.read ? 'var(--accent)' : 'transparent'};flex-shrink:0;margin-top:4px;"></span>
                    <div style="flex:1;min-width:0;">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                            <span style="font-size:12px;font-weight:${!s.read ? '600' : '400'};color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                                ${ctx.escHtml(s.name || s.email)}
                            </span>
                            <span style="font-size:10px;color:var(--text2);flex-shrink:0;">${date}</span>
                        </div>
                        ${s.subject ? `<div style="font-size:11px;color:var(--text2);margin-top:1px;">${ctx.escHtml(s.subject)}</div>` : ''}
                        <div style="font-size:11px;color:var(--text2);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" id="ib-preview-${ctx.escHtml(s.id)}">${ctx.escHtml(preview)}${s.message.length > 80 ? '…' : ''}</div>
                        <div id="ib-body-${ctx.escHtml(s.id)}" style="display:none;">
                            <div style="font-size:11px;color:var(--text2);margin-top:4px;">${ctx.escHtml(s.email)}</div>
                            <div style="font-size:12px;color:var(--text);margin-top:8px;line-height:1.6;white-space:pre-wrap;border-left:2px solid var(--border);padding-left:10px;">${ctx.escHtml(s.message)}</div>
                            <div style="display:flex;gap:8px;margin-top:10px;">
                                <button data-action="toggle-read" data-id="${ctx.escHtml(s.id)}" data-read="${s.read}"
                                    style="padding:3px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">
                                    ${s.read ? 'Mark unread' : 'Mark read'}
                                </button>
                                <button data-action="delete" data-id="${ctx.escHtml(s.id)}"
                                    style="padding:3px 10px;font-size:10px;border:1px solid var(--danger);border-radius:var(--radius);background:transparent;color:var(--danger);cursor:pointer;">
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        }).join('');
    }

    function toggleExpand(id) {
        const body    = c.querySelector('#ib-body-' + id);
        const preview = c.querySelector('#ib-preview-' + id);
        const row     = c.querySelector(`.ib-row[data-id="${id}"]`);
        if (!body) return;
        const open = body.style.display !== 'none';
        body.style.display    = open ? 'none' : 'block';
        if (preview) preview.style.display = open ? '' : 'none';
        if (row) row.classList.toggle('expanded', !open);
        // Auto-mark as read when opened
        if (!open) {
            const sub = submissions.find(s => s.id === id);
            if (sub && !sub.read) toggleRead(id, true);
        }
    }

    async function load() {
        const list = c.querySelector('#ib-list');
        list.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/list-submissions');
            if (!r.ok) throw new Error('Failed');
            const data = await r.json();
            submissions = data.submissions || [];
            render();
        } catch(e) {
            list.innerHTML = '<div style="padding:20px 0;color:var(--danger);font-size:11px;">Failed to load inbox</div>';
        }
    }

    async function deleteSubmission(id) {
        if (!confirm('Delete this message?')) return;
        await ctx.apiFetch('/api/adze/delete-submission', { method: 'POST', body: { id } });
        submissions = submissions.filter(s => s.id !== id);
        render();
    }

    async function toggleRead(id, read) {
        await ctx.apiFetch('/api/adze/mark-submission-read', { method: 'POST', body: { id, read } });
        const sub = submissions.find(s => s.id === id);
        if (sub) sub.read = read;
        render();
    }

    async function markAllRead() {
        await Promise.all(
            submissions.filter(s => !s.read).map(s =>
                ctx.apiFetch('/api/adze/mark-submission-read', { method: 'POST', body: { id: s.id, read: true } })
            )
        );
        submissions.forEach(s => s.read = true);
        render();
    }

    load();
})(ctx);
