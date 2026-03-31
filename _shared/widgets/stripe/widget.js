// Widget: Stripe
// Manage Stripe payments, products, and orders.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow-y:auto;';

    c.innerHTML = `
    <div style="padding:20px 24px;max-width:800px;margin:0 auto;width:100%;box-sizing:border-box;">

        <!-- Setup view -->
        <div id="sw-setup" style="display:none;">
            <h3 style="margin:0 0 4px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Set up Stripe</h3>
            <p style="font-size:10px;color:var(--text2);margin:0 0 16px;">Accept payments on your site. You'll need a Stripe account.</p>
            <div style="display:flex;flex-direction:column;gap:16px;">
                <div style="background:var(--surface2);border-radius:8px;padding:16px;">
                    <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Step 1: Create a Stripe account</div>
                    <p style="font-size:12px;color:var(--text2);margin:0 0 8px;">If you don't have one, sign up at stripe.com. It's free to create.</p>
                    <a href="https://dashboard.stripe.com/register" target="_blank" style="color:var(--accent);font-size:12px;">Go to Stripe &rarr;</a>
                </div>
                <div style="background:var(--surface2);border-radius:8px;padding:16px;">
                    <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Step 2: Get your API keys</div>
                    <p style="font-size:12px;color:var(--text2);margin:0 0 8px;">Go to Developers &rarr; API keys in Stripe. Copy your <b>Secret key</b> and <b>Publishable key</b>.</p>
                    <a href="https://dashboard.stripe.com/apikeys" target="_blank" style="color:var(--accent);font-size:12px;">Open API keys &rarr;</a>
                </div>
                <div style="background:var(--surface2);border-radius:8px;padding:16px;">
                    <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Step 3: Paste your keys</div>
                    <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px;">
                        <div>
                            <label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Secret Key</label>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <input type="password" id="sw-sk" data-stripe-prefix="sk_" placeholder="sk_live_..." style="flex:1;padding:8px;font-size:12px;font-family:var(--mono);border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                                <span id="sw-sk-st" style="font-size:16px;width:20px;text-align:center;"></span>
                            </div>
                        </div>
                        <div>
                            <label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Publishable Key</label>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <input type="password" id="sw-pk" data-stripe-prefix="pk_" placeholder="pk_live_..." style="flex:1;padding:8px;font-size:12px;font-family:var(--mono);border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                                <span id="sw-pk-st" style="font-size:16px;width:20px;text-align:center;"></span>
                            </div>
                        </div>
                        <div>
                            <label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Webhook Secret <span style="opacity:0.6;">(optional)</span></label>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <input type="password" id="sw-wh" data-stripe-prefix="whsec_" placeholder="whsec_..." style="flex:1;padding:8px;font-size:12px;font-family:var(--mono);border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                                <span id="sw-wh-st" style="font-size:16px;width:20px;text-align:center;"></span>
                            </div>
                        </div>
                        <button data-action="save-keys" style="align-self:flex-start;margin-top:4px;padding:5px 14px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:var(--accent-text);cursor:pointer;font-weight:600;">Save &amp; Connect</button>
                    </div>
                </div>
            </div>
            <div id="sw-key-status" style="margin-top:12px;font-size:11px;color:var(--text2);"></div>
        </div>

        <!-- Dashboard view -->
        <div id="sw-dash" style="display:none;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <div>
                    <h3 style="margin:0 0 4px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Stripe Shop</h3>
                    <p style="color:var(--text2);font-size:11px;margin:0;" id="sw-account-info"><span style="color:#4a8;">&#10003;</span> Connected</p>
                </div>
                <div style="display:flex;gap:8px;">
                    <button data-action="show-add-product" style="padding:5px 12px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:var(--accent-text);cursor:pointer;font-weight:600;">+ Add Product</button>
                    <a href="https://dashboard.stripe.com" target="_blank" style="padding:5px 12px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;">Open Stripe ↗</a>
                </div>
            </div>

            <!-- Add product form -->
            <div id="sw-add-product" style="display:none;background:var(--surface2);border-radius:8px;padding:16px;margin-bottom:16px;">
                <div style="font-weight:600;margin-bottom:12px;font-size:13px;">New Product</div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <input type="text" id="sw-prod-name" placeholder="Product name" style="padding:8px;font-size:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                    <input type="text" id="sw-prod-desc" placeholder="Description (optional)" style="padding:8px;font-size:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                    <div style="display:flex;gap:8px;">
                        <div style="flex:1;">
                            <label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Price</label>
                            <input type="number" id="sw-prod-price" placeholder="25.00" step="0.01" min="0.01" style="width:100%;padding:8px;font-size:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);box-sizing:border-box;">
                        </div>
                        <div style="width:90px;">
                            <label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Currency</label>
                            <select id="sw-prod-currency" style="width:100%;padding:8px;font-size:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);color:var(--text);">
                                <option value="gbp">GBP</option>
                                <option value="usd">USD</option>
                                <option value="eur">EUR</option>
                            </select>
                        </div>
                    </div>
                    <div style="display:flex;gap:8px;margin-top:4px;">
                        <button data-action="create-product" style="padding:5px 12px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:var(--accent-text);cursor:pointer;font-weight:600;">Create</button>
                        <button data-action="cancel-add-product" style="padding:5px 12px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Cancel</button>
                    </div>
                </div>
            </div>

            <!-- Products list -->
            <div id="sw-products" style="display:flex;flex-direction:column;gap:8px;">
                <div style="color:var(--text2);font-size:12px;">Loading products...</div>
            </div>

            <!-- Webhook URL -->
            <div style="margin-top:24px;padding:16px;background:var(--surface2);border-radius:8px;">
                <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Webhook URL</div>
                <p style="font-size:11px;color:var(--text2);margin:0 0 8px;">Add this in Stripe Dashboard → Developers → Webhooks to receive payment notifications.</p>
                <code id="sw-webhook-url" style="font-size:11px;background:var(--bg);padding:6px 10px;border-radius:var(--radius);display:block;word-break:break-all;color:var(--text);border:1px solid var(--border);"></code>
                <button data-action="copy-webhook" style="margin-top:8px;padding:4px 10px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Copy</button>
            </div>

            <!-- Buy snippet -->
            <div style="margin-top:12px;padding:16px;background:var(--surface2);border-radius:8px;">
                <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Using in your site</div>
                <p style="font-size:11px;color:var(--text2);margin:0 0 8px;">Ask the Vibe Coder to "add a buy button for [product name]" or use this snippet:</p>
                <pre id="sw-snippet" style="font-size:10px;background:var(--bg);padding:10px;border-radius:var(--radius);overflow-x:auto;border:1px solid var(--border);color:var(--text);margin:0;white-space:pre-wrap;"></pre>
            </div>

            <!-- Orders -->
            <div style="margin-top:12px;padding:16px;background:var(--surface2);border-radius:8px;">
                <div style="font-weight:600;margin-bottom:8px;font-size:13px;">Orders</div>
                <div id="sw-orders" style="font-size:12px;color:var(--text2);">Loading...</div>
            </div>
        </div>

    </div>`;

    // ── DOM references ──
    const setup = c.querySelector('#sw-setup');
    const dash  = c.querySelector('#sw-dash');

    // ── Event delegation ──
    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        switch (btn.dataset.action) {
            case 'save-keys':          await saveStripeKeys(); break;
            case 'show-add-product':   showAddProductForm(); break;
            case 'create-product':     await createProduct(); break;
            case 'cancel-add-product': c.querySelector('#sw-add-product').style.display = 'none'; break;
            case 'archive-product':    await archiveProduct(btn.dataset.id); break;
            case 'copy-price-id':
                navigator.clipboard.writeText(btn.dataset.id);
                ctx.toast('Price ID copied!');
                break;
            case 'copy-webhook':
                navigator.clipboard.writeText(c.querySelector('#sw-webhook-url').textContent);
                ctx.toast('Copied!');
                break;
            case 'go-to-shop':
                setup.style.display = 'none';
                dash.style.display = 'block';
                await loadStripeTab();
                break;
            case 'retest-keys':        await prefillStripeKeys(); break;
        }
    });

    c.addEventListener('input', function(e) {
        const input = e.target.closest('input[data-stripe-prefix]');
        if (input) validateStripeKey(input, input.dataset.stripePrefix);
    });

    // ── Functions ──

    async function loadStripeTab() {
        try {
            const r = await ctx.apiFetch('/api/adze/stripe-status');
            const data = await r.json();

            if (data.configured) {
                setup.style.display = 'none';
                dash.style.display = 'block';
                if (data.account_name) {
                    c.querySelector('#sw-account-info').innerHTML =
                        `<span style="color:#4a8;">&#10003;</span> Connected: ${ctx.escHtml(data.account_name)}`;
                }
                // Fetch domain for webhook URL
                try {
                    const ir = await ctx.apiFetch('/api/adze/artist-info');
                    const info = await ir.json();
                    const domain = (info.config?.domain || info.domain)
                        ? `https://${info.config?.domain || info.domain}`
                        : `https://adze.studio/artists/${ctx.artistSlug}`;
                    c.querySelector('#sw-webhook-url').textContent =
                        `${domain}/api/artists/${ctx.artistSlug}/stripe-webhook`;
                } catch(e) {
                    c.querySelector('#sw-webhook-url').textContent =
                        `https://adze.studio/artists/${ctx.artistSlug}/stripe-webhook`;
                }
                // Buy snippet
                c.querySelector('#sw-snippet').textContent =
`<button onclick="buyProduct('PRICE_ID')">Buy - $XX</button>
<script>
async function buyProduct(priceId) {
  const r = await fetch('/api/artists/${ctx.artistSlug}/create-checkout', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({price_id: priceId})
  });
  const {url} = await r.json();
  window.location.href = url;
}
<\/script>`;
                loadStripeProducts();
                loadStripeOrders();
            } else {
                setup.style.display = 'block';
                dash.style.display = 'none';
                await prefillStripeKeys();
            }
        } catch (e) {
            setup.style.display = 'block';
            dash.style.display = 'none';
            await prefillStripeKeys();
        }
        const statusEl = c.querySelector('#sw-key-status');
        if (statusEl && setup.style.display === 'none') statusEl.textContent = '';
    }

    function validateStripeKey(input, prefix) {
        const statusId = input.id + '-st';
        const statusEl = c.querySelector('#' + statusId);
        if (!statusEl) return;
        const val = input.value.trim();
        if (!val) {
            statusEl.innerHTML = input.dataset.saved === 'true'
                ? '<span style="color:#4a8;">&#10003;</span>' : '';
            input.style.borderColor = 'var(--border)';
            return;
        }
        const valid = val.startsWith(prefix) && val.length >= 20;
        statusEl.innerHTML = valid
            ? '<span style="color:#4a8;">&#10003;</span>'
            : '<span style="color:#e44;">&#10007;</span>';
        input.style.borderColor = valid ? '#4a8' : '#e44';
    }

    async function prefillStripeKeys() {
        const statusEl = c.querySelector('#sw-key-status');
        try {
            const r = await ctx.apiFetch('/api/adze/list-env');
            if (!r.ok) return;
            const data = await r.json();
            const vars = data.vars || data.secrets || [];
            const hasKeys = {};
            for (const s of vars) hasKeys[s.key] = s.value_preview || s.masked || '***';

            const skInput = c.querySelector('#sw-sk');
            const pkInput = c.querySelector('#sw-pk');
            const whInput = c.querySelector('#sw-wh');

            if (hasKeys['STRIPE_SECRET_KEY']) {
                skInput.placeholder = hasKeys['STRIPE_SECRET_KEY'];
                skInput.dataset.saved = 'true';
                const s = c.querySelector('#sw-sk-st');
                if (s) s.innerHTML = '<span style="color:#e8a73d;">&#9679;</span>';
            }
            if (hasKeys['STRIPE_PUBLISHABLE_KEY']) {
                pkInput.placeholder = hasKeys['STRIPE_PUBLISHABLE_KEY'];
                pkInput.dataset.saved = 'true';
                const s = c.querySelector('#sw-pk-st');
                if (s) s.innerHTML = '<span style="color:#e8a73d;">&#9679;</span>';
            }
            if (hasKeys['STRIPE_ENDPOINT_SECRET']) {
                whInput.placeholder = hasKeys['STRIPE_ENDPOINT_SECRET'];
                whInput.dataset.saved = 'true';
                const s = c.querySelector('#sw-wh-st');
                if (s) s.innerHTML = '<span style="color:#e8a73d;">&#9679;</span>';
            }

            if (hasKeys['STRIPE_SECRET_KEY']) {
                if (statusEl) statusEl.textContent = 'Verifying with Stripe...';
                try {
                    const vr = await ctx.apiFetch('/api/adze/stripe-status');
                    const vd = await vr.json();
                    if (vd.configured) {
                        const sks = c.querySelector('#sw-sk-st');
                        const pks = c.querySelector('#sw-pk-st');
                        if (sks) sks.innerHTML = '<span style="color:#4a8;">&#10003;</span>';
                        if (pks) pks.innerHTML = '<span style="color:#4a8;">&#10003;</span>';
                        if (statusEl) statusEl.innerHTML =
                            `<span style="color:#4a8;">&#10003;</span> Verified with Stripe. <button data-action="go-to-shop" style="margin-left:8px;padding:3px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Go to Shop</button>`;
                    } else {
                        if (statusEl) statusEl.innerHTML =
                            `<span style="color:#e8a73d;">&#9679;</span> Keys saved but could not connect. <button data-action="retest-keys" style="margin-left:8px;padding:3px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Re-test</button>`;
                    }
                } catch(e) {
                    if (statusEl) statusEl.innerHTML =
                        `<span style="color:#e8a73d;">&#9679;</span> Could not reach server to verify. <button data-action="retest-keys" style="margin-left:8px;padding:3px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Re-test</button>`;
                }
            } else {
                if (statusEl) statusEl.textContent = 'No keys saved yet.';
            }
        } catch(e) {
            if (statusEl) statusEl.textContent = 'Could not check saved keys.';
        }
    }

    async function saveStripeKeys() {
        const sk = c.querySelector('#sw-sk').value.trim();
        const pk = c.querySelector('#sw-pk').value.trim();
        const wh = c.querySelector('#sw-wh').value.trim();
        const skSaved = c.querySelector('#sw-sk').dataset.saved === 'true';
        const pkSaved = c.querySelector('#sw-pk').dataset.saved === 'true';
        const statusEl = c.querySelector('#sw-key-status');

        if ((!sk && !skSaved) || (!pk && !pkSaved)) {
            ctx.toast('Both Secret Key and Publishable Key are required', 'error'); return;
        }
        if (sk && (!sk.startsWith('sk_') || sk.length < 20)) {
            ctx.toast('Secret Key must start with sk_', 'error'); return;
        }
        if (pk && (!pk.startsWith('pk_') || pk.length < 20)) {
            ctx.toast('Publishable Key must start with pk_', 'error'); return;
        }
        if (wh && (!wh.startsWith('whsec_') || wh.length < 15)) {
            ctx.toast('Webhook Secret must start with whsec_', 'error'); return;
        }

        if (statusEl) statusEl.textContent = 'Saving keys...';
        try {
            const keys = [];
            if (sk) keys.push({ key: 'STRIPE_SECRET_KEY', value: sk });
            if (pk) keys.push({ key: 'STRIPE_PUBLISHABLE_KEY', value: pk });
            if (wh) keys.push({ key: 'STRIPE_ENDPOINT_SECRET', value: wh });
            for (const { key, value } of keys) {
                await ctx.apiFetch('/api/adze/update-env', { method: 'POST', body: { key, value } });
            }

            if (statusEl) statusEl.textContent = 'Verifying with Stripe...';
            const verifyR = await ctx.apiFetch('/api/adze/stripe-status');
            const verifyData = await verifyR.json();
            if (!verifyData.configured) {
                if (statusEl) statusEl.innerHTML =
                    `<span style="color:#e44;">&#10007;</span> ${ctx.escHtml(verifyData.error || 'Could not connect to Stripe')}`;
                ctx.toast('Keys saved but Stripe rejected them. Check your Secret Key.', 'error');
                return;
            }

            if (statusEl) statusEl.textContent = 'Setting up checkout routes...';
            const scaffoldR = await ctx.apiFetch('/api/adze/stripe-scaffold', { method: 'POST' });
            const scaffoldData = await scaffoldR.json();
            if (scaffoldData.success) {
                if (statusEl) statusEl.innerHTML =
                    `<span style="color:#4a8;">&#10003;</span> Connected to ${ctx.escHtml(verifyData.account_name || 'Stripe')}`;
                ctx.toast('Stripe connected! Server is restarting to activate checkout routes.');
                await new Promise(r => setTimeout(r, 4000));
                loadStripeTab();
            } else {
                ctx.toast(scaffoldData.error || 'Scaffold failed', 'error');
            }
        } catch (e) {
            ctx.toast('Failed to save Stripe keys', 'error');
        }
    }

    async function loadStripeProducts() {
        const list = c.querySelector('#sw-products');
        if (!list) return;
        try {
            const r = await ctx.apiFetch('/api/adze/stripe-products');
            const data = await r.json();
            if (data.error) {
                list.innerHTML = `<div style="color:var(--text2);font-size:12px;">${ctx.escHtml(data.error)}</div>`;
                return;
            }
            if (!data.products || data.products.length === 0) {
                list.innerHTML = '<div style="color:var(--text2);font-size:12px;">No products yet. Click "+ Add Product" to create one.</div>';
                return;
            }
            list.innerHTML = data.products.map(p => {
                const price = p.default_price;
                const priceStr = price ? `${(price.amount / 100).toFixed(2)} ${price.currency.toUpperCase()}` : 'No price';
                const priceId = price ? price.id : '';
                return `<div style="display:flex;align-items:center;gap:12px;padding:12px;background:var(--surface2);border-radius:8px;">
                    ${p.images?.length ? `<img src="${ctx.escHtml(p.images[0])}" style="width:44px;height:44px;object-fit:cover;border-radius:6px;">` : '<div style="width:44px;height:44px;background:var(--border);border-radius:6px;flex-shrink:0;"></div>'}
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:600;font-size:13px;">${ctx.escHtml(p.name)}</div>
                        ${p.description ? `<div style="font-size:11px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${ctx.escHtml(p.description)}</div>` : ''}
                    </div>
                    <div style="font-weight:600;font-size:13px;white-space:nowrap;">${priceStr}</div>
                    <div style="display:flex;gap:4px;">
                        ${priceId ? `<button data-action="copy-price-id" data-id="${ctx.escHtml(priceId)}" style="padding:3px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);cursor:pointer;">Copy ID</button>` : ''}
                        <button data-action="archive-product" data-id="${ctx.escHtml(p.id)}" style="padding:3px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">Archive</button>
                    </div>
                </div>`;
            }).join('');
        } catch (e) {
            list.innerHTML = '<div style="color:var(--text2);font-size:12px;">Failed to load products</div>';
        }
    }

    function showAddProductForm() {
        c.querySelector('#sw-add-product').style.display = 'block';
        c.querySelector('#sw-prod-name').focus();
    }

    async function createProduct() {
        const name     = c.querySelector('#sw-prod-name').value.trim();
        const desc     = c.querySelector('#sw-prod-desc').value.trim();
        const price    = parseFloat(c.querySelector('#sw-prod-price').value);
        const currency = c.querySelector('#sw-prod-currency').value;
        if (!name || !price || price <= 0) {
            ctx.toast('Name and price are required', 'error'); return;
        }
        try {
            const r = await ctx.apiFetch('/api/adze/stripe-create-product', {
                method: 'POST',
                body: { name, description: desc, price_cents: Math.round(price * 100), currency }
            });
            const data = await r.json();
            if (data.success) {
                ctx.toast('Product created!');
                c.querySelector('#sw-add-product').style.display = 'none';
                c.querySelector('#sw-prod-name').value = '';
                c.querySelector('#sw-prod-desc').value = '';
                c.querySelector('#sw-prod-price').value = '';
                loadStripeProducts();
            } else {
                ctx.toast(data.error || 'Failed', 'error');
            }
        } catch (e) {
            ctx.toast('Failed to create product', 'error');
        }
    }

    async function archiveProduct(productId) {
        if (!confirm('Archive this product? It will no longer appear in your shop.')) return;
        try {
            const r = await ctx.apiFetch('/api/adze/stripe-delete-product', {
                method: 'POST', body: { product_id: productId }
            });
            const data = await r.json();
            if (data.success) { ctx.toast('Product archived'); loadStripeProducts(); }
            else { ctx.toast(data.error || 'Failed', 'error'); }
        } catch (e) {
            ctx.toast('Failed to archive product', 'error');
        }
    }

    async function loadStripeOrders() {
        const el = c.querySelector('#sw-orders');
        if (!el) return;
        try {
            const r = await ctx.apiFetch(`/api/artists/${ctx.artistSlug}/orders`);
            if (!r.ok) { el.textContent = 'No orders yet'; return; }
            const data = await r.json();
            if (!data.orders || data.orders.length === 0) { el.textContent = 'No orders yet'; return; }
            el.innerHTML = data.orders.slice().reverse().slice(0, 20).map(o => {
                const amount = o.amount_total
                    ? `${(o.amount_total / 100).toFixed(2)} ${(o.currency || '').toUpperCase()}` : '?';
                const date = o.created ? new Date(o.created * 1000).toLocaleDateString() : '';
                return `<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--border);font-size:11px;">
                    <span>${ctx.escHtml(o.customer_email || 'Unknown')}</span>
                    <span>${amount}</span>
                    <span style="color:var(--text2);">${date}</span>
                    <span style="color:${o.status === 'paid' ? '#4a8' : 'var(--text2)'};">${o.status || '?'}</span>
                </div>`;
            }).join('');
        } catch (e) {
            el.textContent = 'Could not load orders';
        }
    }

    // ── Init ──
    loadStripeTab();
})(ctx);
