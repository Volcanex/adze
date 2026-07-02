// Widget: Email
// Manage business email for this site's domain — mailboxes + forwards via
// Purelymail, each with auto-filled connection setup (Gmail POP/SMTP + IMAP)
// and an editable signature canvas (stored in Adze, paste into any client).

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    const LOGO = 'https://lastplace.co.uk/assets/images/Lastplacelogo.png';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:840px;margin:0 auto;padding:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Email</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="em-subtitle">Loading…</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <button data-action="add-mailbox" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">+ Mailbox</button>
                    <button data-action="add-forward" style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">+ Forward</button>
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>
            <div id="em-body" style="margin-top:16px;"></div>
        </div>
    </div>`;

    let state = { mailboxes: [], forwards: [], settings: null, domain: '', signatures: {} };

    function defaultSig(address) {
        const name = (address.split('@')[0] || '').replace(/[._-]+/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        return `<table cellpadding="0" cellspacing="0" style="font-family:'Cormorant Garamond',Cormorant,Georgia,'Times New Roman',serif;color:#111111;font-size:14px;line-height:1.45;">
  <tr>
    <td style="padding-right:14px;vertical-align:top;">
      <img src="${LOGO}" alt="Last Place" width="72" style="display:block;">
    </td>
    <td style="border-left:2px solid #0000ff;padding-left:14px;vertical-align:top;">
      <div style="font-size:19px;font-weight:600;">${name}</div>
      <div style="color:#555555;">Last Place</div>
      <div><a href="https://lastplace.co.uk" style="color:#0000ff;text-decoration:none;">lastplace.co.uk</a></div>
    </td>
  </tr>
</table>`;
    }

    // ── events ────────────────────────────────────────────────────────────
    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const a = btn.dataset.action;
        if (a === 'refresh') return load();
        if (a === 'add-mailbox') return addMailbox();
        if (a === 'add-forward') return addForward();
        if (a === 'delete-mailbox') return delMailbox(btn.dataset.addr);
        if (a === 'delete-forward') return delForward(btn.dataset.id, btn.dataset.addr);
        if (a === 'toggle') {
            const box = c.querySelector('#' + btn.dataset.target);
            if (box) box.style.display = box.style.display === 'none' ? 'block' : 'none';
            return;
        }
        if (a === 'copy') {
            navigator.clipboard?.writeText(btn.dataset.copy || '');
            ctx.toast('Copied');
            return;
        }
        if (a === 'sig-save') return saveSig(btn.dataset.addr, btn.dataset.idx);
        if (a === 'sig-copy') return copySig(btn.dataset.idx);
        if (a === 'sig-reset') {
            const ta = c.querySelector('#sigsrc-' + btn.dataset.idx);
            ta.value = defaultSig(btn.dataset.addr);
            c.querySelector('#sigprev-' + btn.dataset.idx).innerHTML = ta.value;
            return;
        }
    });

    // live preview as you type the signature
    c.addEventListener('input', function(e) {
        const ta = e.target.closest('textarea[data-sigidx]');
        if (!ta) return;
        const prev = c.querySelector('#sigprev-' + ta.dataset.sigidx);
        if (prev) prev.innerHTML = ta.value;
    });

    // ── render helpers ────────────────────────────────────────────────────
    function row(left, right) {
        return `<tr style="border-bottom:1px solid var(--border);">
            <td style="padding:8px;color:var(--text);">${left}</td>
            <td style="padding:8px;text-align:right;white-space:nowrap;">${right}</td></tr>`;
    }
    function copyBtn(val) {
        return `<button data-action="copy" data-copy="${ctx.escHtml(val)}" title="Copy"
            style="margin-left:6px;padding:0 5px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">⧉</button>`;
    }
    function settingLine(label, host, port) {
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;">
            <span style="color:var(--text2);">${label}</span>
            <span style="font-family:var(--mono);color:var(--text);">${host} · ${port} · SSL ${copyBtn(host + ':' + port)}</span></div>`;
    }
    function connectCard(idx, address, s) {
        if (!s) return '';
        return `<div id="connect-${idx}" style="display:none;margin:0 0 10px;padding:12px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);font-size:11px;line-height:1.5;">
            <div style="font-weight:600;margin-bottom:6px;">Connect ${ctx.escHtml(address)}</div>
            ${settingLine('IMAP (phone/desktop, instant, 2-way)', s.imap.host, s.imap.port)}
            ${settingLine('POP3 (Gmail web import)', s.pop.host, s.pop.port)}
            ${settingLine('SMTP (send as)', s.smtp.host, s.smtp.port)}
            <div style="display:flex;justify-content:space-between;padding:3px 0;">
                <span style="color:var(--text2);">Username</span>
                <span style="font-family:var(--mono);color:var(--text);">${ctx.escHtml(address)} ${copyBtn(address)}</span></div>
            <div style="border-top:1px solid var(--border);margin-top:6px;padding-top:8px;color:var(--text2);">
                <b style="color:var(--text);">Add to Gmail —</b> phone app: add account → <i>Other (IMAP)</i>, server <span style="font-family:var(--mono);">${s.imap.host}</span>:${s.imap.port} SSL. Web (POP, laggy): Accounts → add a mail account → POP <span style="font-family:var(--mono);">${s.pop.host}</span>:${s.pop.port} SSL. Send-as SMTP <span style="font-family:var(--mono);">${s.smtp.host}</span>:${s.smtp.port}. Username is always the full address.
            </div>
        </div>`;
    }
    function sigCard(idx, address) {
        const html = state.signatures[address] || defaultSig(address);
        return `<div id="sig-${idx}" style="display:none;margin:0 0 10px;padding:12px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);font-size:11px;">
            <div style="font-weight:600;margin-bottom:6px;">Signature — ${ctx.escHtml(address)}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div>
                    <div style="color:var(--text2);margin-bottom:4px;">HTML</div>
                    <textarea id="sigsrc-${idx}" data-sigidx="${idx}" spellcheck="false"
                        style="width:100%;min-height:170px;box-sizing:border-box;font-family:var(--mono);font-size:10px;line-height:1.4;padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);resize:vertical;">${ctx.escHtml(html)}</textarea>
                </div>
                <div>
                    <div style="color:var(--text2);margin-bottom:4px;">Preview</div>
                    <div id="sigprev-${idx}" style="padding:8px;border:1px solid var(--border);border-radius:var(--radius);background:#fff;min-height:170px;overflow:auto;">${html}</div>
                </div>
            </div>
            <div style="display:flex;gap:6px;margin-top:8px;">
                <button data-action="sig-save" data-addr="${ctx.escHtml(address)}" data-idx="${idx}" style="padding:4px 12px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:var(--accent-text,#fff);cursor:pointer;">Save</button>
                <button data-action="sig-copy" data-idx="${idx}" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Copy signature</button>
                <button data-action="sig-reset" data-addr="${ctx.escHtml(address)}" data-idx="${idx}" style="padding:4px 12px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Reset</button>
            </div>
            <div style="color:var(--text2);margin-top:6px;line-height:1.4;">Paste into your email client’s signature box (Outlook, Gmail, Apple Mail…) — the logo + layout carry over. Custom fonts fall back to a serif in most clients; the logo holds the Cormorant look.</div>
        </div>`;
    }

    function render() {
        const body = c.querySelector('#em-body');
        const sub = c.querySelector('#em-subtitle');

        if (!state.configured) {
            sub.textContent = state.domain || 'No domain set';
            body.innerHTML = `<div style="text-align:center;padding:40px 20px;color:var(--text2);font-size:12px;">
                ${state.reason === 'no_domain' ? 'Set this site’s domain first, then email can be configured.' : 'Email isn’t set up for this domain yet.'}
            </div>`;
            return;
        }

        sub.textContent = `${state.domain} · ${state.mailboxes.length} mailbox${state.mailboxes.length !== 1 ? 'es' : ''} · ${state.forwards.length} forward${state.forwards.length !== 1 ? 's' : ''}`;

        let html = '';
        html += `<div style="font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--text2);margin:4px 0 6px;">Mailboxes</div>`;
        if (!state.mailboxes.length) {
            html += `<div style="color:var(--text2);font-size:11px;padding:4px 0 14px;">No mailboxes yet.</div>`;
        } else {
            html += `<table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:14px;"><tbody>`;
            state.mailboxes.forEach((m, i) => {
                const btn = (label, target) => `<button data-action="toggle" data-target="${target}" style="padding:2px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">${label}</button>`;
                const del = `<button data-action="delete-mailbox" data-addr="${ctx.escHtml(m.address)}" style="padding:2px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">×</button>`;
                html += row(ctx.escHtml(m.address), `${btn('Connect ▾', 'connect-' + i)} ${btn('Signature ▾', 'sig-' + i)} ${del}`);
                html += `<tr><td colspan="2" style="padding:0;">${connectCard(i, m.address, state.settings)}${sigCard(i, m.address)}</td></tr>`;
            });
            html += `</tbody></table>`;
        }

        html += `<div style="font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--text2);margin:4px 0 6px;">Forwards</div>`;
        if (!state.forwards.length) {
            html += `<div style="color:var(--text2);font-size:11px;padding:4px 0;">No forwards yet.</div>`;
        } else {
            html += `<table style="width:100%;border-collapse:collapse;font-size:11px;"><tbody>`;
            state.forwards.forEach(f => {
                const del = `<button data-action="delete-forward" data-id="${ctx.escHtml(f.id)}" data-addr="${ctx.escHtml(f.address)}" style="padding:2px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">×</button>`;
                html += row(`${ctx.escHtml(f.address)} <span style="color:var(--text2);">→ ${ctx.escHtml(f.targets.join(', '))}</span>`, del);
            });
            html += `</tbody></table>`;
        }
        body.innerHTML = html;
    }

    // ── data ──────────────────────────────────────────────────────────────
    async function load() {
        const body = c.querySelector('#em-body');
        body.innerHTML = `<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading…</div>`;
        try {
            const [sr, gr] = await Promise.all([
                ctx.apiFetch('/api/adze/email-status'),
                ctx.apiFetch('/api/adze/email-signatures'),
            ]);
            if (!sr.ok) throw new Error('Failed');
            const d = await sr.json();
            const sigs = gr.ok ? (await gr.json()).signatures || {} : {};
            state = {
                configured: d.configured, reason: d.reason, domain: d.domain || '',
                mailboxes: d.mailboxes || [], forwards: d.forwards || [],
                settings: d.settings || null, signatures: sigs,
            };
            render();
        } catch (e) {
            body.innerHTML = `<div style="padding:20px 0;color:var(--danger);font-size:11px;">Couldn’t load email.</div>`;
        }
    }

    async function saveSig(address, idx) {
        const html = c.querySelector('#sigsrc-' + idx).value;
        const r = await ctx.apiFetch('/api/adze/email-signature-save', { method: 'POST', body: { address, html } });
        if (!r.ok) { ctx.toast('Save failed', 'error'); return; }
        state.signatures[address] = html;
        ctx.toast('Signature saved');
    }

    function copySig(idx) {
        const node = c.querySelector('#sigprev-' + idx);
        try {
            const range = document.createRange();
            range.selectNodeContents(node);
            const sel = window.getSelection();
            sel.removeAllRanges(); sel.addRange(range);
            document.execCommand('copy');
            sel.removeAllRanges();
            ctx.toast('Copied — paste into your signature box');
        } catch (e) {
            ctx.toast('Copy failed — select the preview manually', 'error');
        }
    }

    async function addMailbox() {
        const local = prompt(`New mailbox — part before @${state.domain}:`);
        if (!local) return;
        const r = await ctx.apiFetch('/api/adze/email-add-mailbox', { method: 'POST', body: { localpart: local.trim() } });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) { ctx.toast(d.error || 'Failed', 'error'); return; }
        alert(`Mailbox created:\n\n${d.address}\nPassword: ${d.password}\n\nSave this now — it won't be shown again.`);
        ctx.toast('Mailbox created');
        load();
    }

    async function addForward() {
        const local = prompt(`New forward — alias before @${state.domain} (e.g. support):`);
        if (!local) return;
        const targets = prompt('Forward to which address(es)? Comma-separated:');
        if (!targets) return;
        const r = await ctx.apiFetch('/api/adze/email-add-forward', {
            method: 'POST',
            body: { localpart: local.trim(), targets: targets.split(',').map(s => s.trim()).filter(Boolean) },
        });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) { ctx.toast(d.error || 'Failed', 'error'); return; }
        ctx.toast('Forward created');
        load();
    }

    async function delMailbox(addr) {
        if (!confirm(`Delete mailbox ${addr}? This permanently removes the inbox and its mail.`)) return;
        const r = await ctx.apiFetch('/api/adze/email-delete-mailbox', { method: 'POST', body: { address: addr } });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) { ctx.toast(d.error || 'Failed', 'error'); return; }
        ctx.toast('Deleted'); load();
    }

    async function delForward(id, addr) {
        if (!confirm(`Delete forward ${addr}?`)) return;
        const r = await ctx.apiFetch('/api/adze/email-delete-forward', { method: 'POST', body: { id: Number(id) } });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) { ctx.toast(d.error || 'Failed', 'error'); return; }
        ctx.toast('Deleted'); load();
    }

    load();
})(ctx);
