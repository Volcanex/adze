// Widget: Calendly
// See your upcoming meetings and manage your scheduling link.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Calendly</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="cl-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <button data-action="settings" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Settings</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="cl-body"></div>
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
            case 'copy-link':
                navigator.clipboard.writeText(btn.dataset.url);
                ctx.toast('Copied!');
                break;
        }
    });

    function showSetup(withCancel) {
        const body = c.querySelector('#cl-body');
        c.querySelector('#cl-subtitle').textContent = 'Connect your account';
        body.innerHTML = `
        <div style="max-width:420px;margin-top:16px;">
            <p style="font-size:11px;color:var(--text2);margin:0 0 20px;line-height:1.6;">
                Connect your Calendly account using a
                <strong style="color:var(--text);">Personal Access Token</strong>.
                Generate one at
                <a href="https://calendly.com/integrations/api_webhooks" target="_blank" style="color:var(--accent);">Calendly Integrations → API &amp; Webhooks</a>.
            </p>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div>
                    <label style="font-size:10px;font-weight:600;color:var(--text2);display:block;margin-bottom:4px;">Personal Access Token</label>
                    <input id="cl-token" type="password" placeholder="eyJraWQi…"
                        style="width:100%;box-sizing:border-box;padding:7px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
                </div>
                <div id="cl-cred-error" style="font-size:10px;color:var(--danger);display:none;"></div>
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
        const token = c.querySelector('#cl-token').value.trim();
        const errEl = c.querySelector('#cl-cred-error');
        const btn   = c.querySelector('[data-action="save-credentials"]');
        if (!token) {
            errEl.textContent = 'Access token is required.';
            errEl.style.display = 'block'; return;
        }
        btn.textContent = 'Connecting…'; btn.disabled = true;
        try {
            const r = await ctx.apiFetch('/api/adze/calendly-verify', {
                method: 'POST', body: { access_token: token }
            });
            const d = await r.json();
            if (!r.ok || !d.ok) {
                errEl.textContent = d.error || 'Could not verify token.';
                errEl.style.display = 'block';
                btn.textContent = 'Connect'; btn.disabled = false; return;
            }
            ctx.toast('Calendly connected!');
            await load();
        } catch(e) {
            errEl.textContent = 'Connection error. Try again.';
            errEl.style.display = 'block';
            btn.textContent = 'Connect'; btn.disabled = false;
        }
    }

    function fmtDateTime(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        return d.toLocaleDateString('en-GB', { weekday:'short', day:'numeric', month:'short' })
             + ' · '
             + d.toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit' });
    }

    function renderDashboard(d) {
        const body = c.querySelector('#cl-body');
        c.querySelector('#cl-subtitle').textContent = d.name || 'Account';

        const upcoming = d.upcoming || [];
        const eventTypes = d.event_types || [];

        body.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px;">

            <!-- Left: Upcoming + Stats -->
            <div>
                <!-- Stats -->
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px;">
                    <div style="border:1px solid var(--border);border-radius:var(--radius);padding:14px;text-align:center;">
                        <div style="font-size:22px;font-weight:600;color:var(--text);font-family:var(--heading-font);">${upcoming.length}</div>
                        <div style="font-size:10px;color:var(--text2);margin-top:3px;">Upcoming</div>
                    </div>
                    <div style="border:1px solid var(--border);border-radius:var(--radius);padding:14px;text-align:center;">
                        <div style="font-size:22px;font-weight:600;color:var(--text);font-family:var(--heading-font);">${d.past_30_days ?? '—'}</div>
                        <div style="font-size:10px;color:var(--text2);margin-top:3px;">Last 30 days</div>
                    </div>
                </div>

                <!-- Upcoming meetings -->
                <div style="margin-bottom:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">Upcoming Meetings</div>
                ${upcoming.length === 0
                    ? `<div style="color:var(--text2);font-size:11px;padding:12px 0;">No upcoming meetings.</div>`
                    : `<div style="border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;">
                    ${upcoming.map((ev, i) => `
                    <div style="padding:10px 14px;${i > 0 ? 'border-top:1px solid var(--border);' : ''}">
                        <div style="font-size:11px;font-weight:500;color:var(--text);">${ctx.escHtml(ev.name)}</div>
                        <div style="font-size:10px;color:var(--text2);margin-top:2px;">${fmtDateTime(ev.start_time)}</div>
                        ${ev.invitee_name ? `<div style="font-size:10px;color:var(--text2);">with ${ctx.escHtml(ev.invitee_name)}</div>` : ''}
                    </div>`).join('')}
                    </div>`}
            </div>

            <!-- Right: Event types + scheduling link -->
            <div>
                <div style="margin-bottom:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">Event Types</div>
                ${eventTypes.length === 0
                    ? `<div style="color:var(--text2);font-size:11px;padding:12px 0;">No active event types.</div>`
                    : `<div style="display:flex;flex-direction:column;gap:8px;">
                    ${eventTypes.map(et => `
                    <div style="border:1px solid var(--border);border-radius:var(--radius);padding:12px 14px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                            <div>
                                <div style="font-size:11px;font-weight:500;color:var(--text);">${ctx.escHtml(et.name)}</div>
                                <div style="font-size:10px;color:var(--text2);margin-top:1px;">${et.duration ? et.duration + ' min' : ''}</div>
                            </div>
                            ${et.scheduling_url ? `
                            <button data-action="copy-link" data-url="${ctx.escHtml(et.scheduling_url)}"
                                style="padding:3px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;white-space:nowrap;">
                                Copy link
                            </button>` : ''}
                        </div>
                    </div>`).join('')}
                    </div>`}

                ${d.scheduling_url ? `
                <div style="margin-top:16px;">
                    <div style="margin-bottom:6px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">Your Scheduling Page</div>
                    <div style="display:flex;gap:6px;align-items:center;">
                        <input readonly value="${ctx.escHtml(d.scheduling_url)}"
                            style="flex:1;padding:6px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text2);">
                        <button data-action="copy-link" data-url="${ctx.escHtml(d.scheduling_url)}"
                            style="padding:6px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">
                            Copy
                        </button>
                        <a href="${ctx.escHtml(d.scheduling_url)}" target="_blank"
                            style="padding:6px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);color:var(--text2);text-decoration:none;">
                            ↗
                        </a>
                    </div>
                </div>` : ''}
            </div>

        </div>`;
    }

    async function load() {
        const body = c.querySelector('#cl-body');
        body.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/calendly-stats');
            const d = await r.json();
            if (!r.ok) { body.innerHTML = `<div style="color:var(--danger);font-size:11px;">${ctx.escHtml(d.error || 'Error loading stats')}</div>`; return; }
            if (!d.configured) { showSetup(false); return; }
            renderDashboard(d);
        } catch(e) {
            body.innerHTML = '<div style="color:var(--danger);font-size:11px;">Failed to load Calendly data</div>';
        }
    }

    load();
})(ctx);
