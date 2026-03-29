// Widget: Manage Bookings
// View and manage incoming booking enquiries from the public bookings page.

(function(ctx) {
    const container = ctx.container;
    const bookingsApi = '/api/artists/' + ctx.artistSlug + '/bookings';

    container.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;padding:0;overflow:hidden;';
    container.innerHTML = `
        <div style="padding:20px 20px 12px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;">
            <div>
                <h3 style="margin:0 0 4px;font-size:16px;">Booking Enquiries</h3>
                <p style="color:var(--text2);font-size:12px;margin:0;" id="bk-count">Loading...</p>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                <select id="bk-filter" style="padding:5px 10px;font-size:12px;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);cursor:pointer;">
                    <option value="all">All</option>
                    <option value="new">New</option>
                    <option value="responded">Responded</option>
                    <option value="archived">Archived</option>
                </select>
                <button class="widget-btn widget-btn-primary" id="bk-refresh" style="font-size:11px;padding:5px 12px;">Refresh</button>
            </div>
        </div>
        <div style="flex:1;overflow-y:auto;padding:0 20px 20px;" id="bk-list"></div>
    `;

    let bookings = [];
    let currentFilter = 'all';

    document.getElementById('bk-filter').addEventListener('change', function() {
        currentFilter = this.value;
        renderBookings();
    });

    document.getElementById('bk-refresh').addEventListener('click', loadBookings);

    async function loadBookings() {
        document.getElementById('bk-list').innerHTML = '<div style="color:var(--text2);font-size:13px;padding:20px 0;">Loading enquiries...</div>';
        try {
            const r = await ctx.apiFetch(bookingsApi + '/list');
            if (r.ok) {
                const data = await r.json();
                bookings = data.bookings || [];
                renderBookings();
            } else {
                document.getElementById('bk-list').innerHTML = '<div style="color:var(--danger);font-size:13px;">Failed to load bookings.</div>';
            }
        } catch(e) {
            document.getElementById('bk-list').innerHTML = '<div style="color:var(--danger);font-size:13px;">Error: ' + e.message + '</div>';
        }
    }

    function renderBookings() {
        const list = document.getElementById('bk-list');
        const filtered = currentFilter === 'all' ? bookings : bookings.filter(b => b.status === currentFilter);

        const newCount = bookings.filter(b => b.status === 'new').length;
        const totalCount = bookings.length;
        document.getElementById('bk-count').textContent = `${totalCount} total, ${newCount} new`;

        if (filtered.length === 0) {
            list.innerHTML = `<div style="color:var(--text2);font-size:13px;padding:20px 0;text-align:center;">
                ${currentFilter === 'all' ? 'No enquiries yet. They\'ll appear here when someone submits the booking form on your site.' : 'No ' + currentFilter + ' enquiries.'}
            </div>`;
            return;
        }

        list.innerHTML = filtered.map(b => {
            const date = new Date(b.date);
            const dateStr = date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
            const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

            const statusColors = {
                'new': 'background:rgba(100,180,255,0.15);color:#5aa0d0;',
                'responded': 'background:rgba(100,255,180,0.15);color:#4a9a6a;',
                'archived': 'background:rgba(150,150,150,0.15);color:#888;'
            };
            const statusStyle = statusColors[b.status] || statusColors['new'];

            return `
                <div style="border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:12px;background:var(--surface);transition:border-color 0.2s;" class="bk-card" data-id="${b.id}">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                        <div>
                            <div style="font-weight:600;font-size:14px;">${escHtml(b.name)}</div>
                            <a href="mailto:${escHtml(b.email)}" style="font-size:12px;color:var(--accent);text-decoration:none;">${escHtml(b.email)}</a>
                        </div>
                        <div style="display:flex;gap:6px;align-items:center;">
                            <span style="font-size:10px;padding:3px 8px;border-radius:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;${statusStyle}">${b.status}</span>
                            <span style="font-size:11px;color:var(--text2);">${dateStr} ${timeStr}</span>
                        </div>
                    </div>
                    ${b.service ? `<div style="font-size:12px;color:var(--text2);margin-bottom:6px;">Service: <strong>${escHtml(b.service)}</strong></div>` : ''}
                    ${b.subject ? `<div style="font-size:13px;font-weight:500;margin-bottom:6px;">${escHtml(b.subject)}</div>` : ''}
                    <div style="font-size:13px;color:var(--text2);line-height:1.6;white-space:pre-wrap;margin-bottom:12px;">${escHtml(b.message)}</div>
                    ${b.notes ? `<div style="font-size:12px;color:var(--text2);background:var(--bg);padding:8px 10px;border-radius:4px;margin-bottom:10px;border-left:2px solid var(--accent);"><strong>Notes:</strong> ${escHtml(b.notes)}</div>` : ''}
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">
                        ${b.status === 'new' ? `<button onclick="bkAction('${b.id}','responded')" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text);cursor:pointer;">Mark Responded</button>` : ''}
                        ${b.status !== 'archived' ? `<button onclick="bkAction('${b.id}','archived')" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text2);cursor:pointer;">Archive</button>` : ''}
                        ${b.status === 'archived' ? `<button onclick="bkAction('${b.id}','new')" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text);cursor:pointer;">Unarchive</button>` : ''}
                        <button onclick="bkAddNote('${b.id}')" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text2);cursor:pointer;">Add Note</button>
                        <button onclick="bkDelete('${b.id}')" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--danger);cursor:pointer;margin-left:auto;">Delete</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    function escHtml(str) {
        if (!str) return '';
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // Global handlers (widget JS runs in global scope via new Function)
    window.bkAction = async function(id, status) {
        const r = await ctx.apiFetch(bookingsApi + '/update', {
            method: 'POST',
            body: { id, status }
        });
        if (r.ok) {
            const b = bookings.find(b => b.id === id);
            if (b) b.status = status;
            renderBookings();
            ctx.toast('Booking updated', 'success');
        }
    };

    window.bkAddNote = async function(id) {
        const b = bookings.find(b => b.id === id);
        const note = prompt('Add a note:', b ? b.notes : '');
        if (note === null) return;
        const r = await ctx.apiFetch(bookingsApi + '/update', {
            method: 'POST',
            body: { id, notes: note }
        });
        if (r.ok) {
            if (b) b.notes = note;
            renderBookings();
            ctx.toast('Note saved', 'success');
        }
    };

    window.bkDelete = async function(id) {
        if (!confirm('Delete this enquiry permanently?')) return;
        const r = await ctx.apiFetch(bookingsApi + '/delete', {
            method: 'POST',
            body: { id }
        });
        if (r.ok) {
            bookings = bookings.filter(b => b.id !== id);
            renderBookings();
            ctx.toast('Enquiry deleted', 'success');
        }
    };

    // Load on init
    loadBookings();
})(ctx);
