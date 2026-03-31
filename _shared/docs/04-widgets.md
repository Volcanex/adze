# Widget Development Guide

Widgets are self-contained JavaScript panels that run inside the artist dashboard. Each widget is a folder under `_shared/widgets/` (Tier 2 — Adze) or `artists/{slug}/widgets/` (Tier 4 — Custom/Forked).

## Widget tier system

| Tier | Code value | Location | Editable? | Marketplace |
|------|-----------|----------|-----------|-------------|
| T1 — Core | — | Hardcoded in dashboard | No | No — always present |
| T2 — Adze | `platform` | `_shared/widgets/` | No — read only | Yes (Adze tab) |
| T3 — Community | `community` | `artists/{source_slug}/widgets/` | No (fork to edit) | Yes (Community tab) |
| T4 — Custom | `artist` | `artists/{slug}/widgets/` | Yes | No (private) |

**Flow:**
- T2 install → appears in artist's dashboard as read-only reference (no forking — T2 widgets use internal Adze endpoints and are platform-maintained)
- T3 install → copies widget to `artists/{slug}/widgets/` with `forked_from: community`
- Fork T3 → creates editable T4 copy in `artists/{slug}/widgets/`
- Share T4 → publishes to T3 community marketplace (`marketplace: true` in widget.json)
- New widget → starts as T4

## File structure

```
widgets/
  my-widget/
    widget.js       ← required: widget code
    widget.json     ← required: metadata
    README.md       ← required for T2: documents endpoints called and setup steps
```

### widget.json

```json
{
  "name": "my-widget",
  "description": "One-line description shown in the marketplace",
  "icon": "star",
  "category": "integrations",
  "marketplace": true
}
```

### README.md (required for T2 platform widgets)

Each T2 widget must have a `README.md` that documents what it does, which endpoints it calls (built-in vs custom), and any API keys or setup required. This file is injected into the Vibe Coder's context when the widget is installed — Claude reads it on demand before working with that widget.

```markdown
# my-widget widget (T2 platform)

One paragraph describing what the widget does.

## Built-in endpoints it calls (no setup needed)
- `GET /api/adze/my-endpoint` — description

## Custom endpoints it expects in artist api.py
- `POST /api/artists/{slug}/my-custom` — description

## Setup
What credentials or configuration the artist needs to provide.
```

T4 custom widgets should also include a README.md — the Vibe Coder will create one automatically when building new widgets.

Available icons: `star`, `play`, `mail`, `users`, `calendar`, `bar-chart`, `credit-card`, `video`, `rss`, `settings`, `zap`, `globe`

## widget.js structure

Every widget is an IIFE that receives a `ctx` object:

```javascript
// Widget: My Widget
// Short description.

(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

    c.innerHTML = `
    <div style="flex:1;overflow-y:auto;">
        <div style="max-width:800px;margin:0 auto;padding:24px;">

            <!-- Title row — ALWAYS this structure -->
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">My Widget</h3>
                    <p style="color:var(--text2);font-size:10px;margin:0;" id="mw-subtitle">Loading...</p>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <button data-action="refresh" style="padding:4px 8px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;">↻</button>
                </div>
            </div>

            <!-- Body -->
            <div id="mw-body" style="margin-top:16px;"></div>

        </div>
    </div>`;

    c.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        if (btn.dataset.action === 'refresh') await load();
    });

    async function load() {
        const body = c.querySelector('#mw-body');
        body.innerHTML = '<div style="padding:20px 0;color:var(--text2);font-size:11px;">Loading...</div>';
        try {
            const r = await ctx.apiFetch('/api/adze/my-endpoint');
            if (!r.ok) throw new Error('Failed');
            const data = await r.json();
            body.innerHTML = ctx.escHtml(JSON.stringify(data));
        } catch(e) {
            body.innerHTML = '<div style="color:var(--danger);font-size:11px;">Failed to load</div>';
        }
    }

    load();
})(ctx);
```

## Layout rules

**All content lives inside a single `max-width:800px` centered column.** There is no full-width sticky header bar.

### Button style (all action buttons use this exactly)

```html
style="padding:4px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text2);cursor:pointer;"
```

Refresh button uses `padding:4px 8px`. Destructive actions: `border-color:var(--danger);color:var(--danger)`.

### ID prefix

Use a unique 2–3 letter prefix for all element IDs to avoid collisions (e.g. `yt-` for YouTube, `mw-` for My Widget).

## ctx API

| Property / Method | Type | Description |
|---|---|---|
| `ctx.container` | `HTMLElement` | Widget's root DOM node |
| `ctx.name` | `string` | Widget slug |
| `ctx.tier` | `string` | `"platform"` (T2), `"community"` (T3), or `"artist"` (T4) |
| `ctx.artistSlug` | `string` | Logged-in artist's slug |
| `ctx.token` | `string` | Artist's admin token (in-memory only) |
| `ctx.pages` | `array` | Artist's pages `[{slug, title}]` |
| `ctx.assetList` | `array` | Artist's uploaded assets |
| `ctx.apiFetch(url, opts)` | `Promise<Response>` | Authenticated fetch. `opts.body` can be a plain object. |
| `ctx.toast(msg, type?)` | `void` | Toast. Type: `success` (default), `error`, `warn`, `info` |
| `ctx.escHtml(str)` | `string` | HTML-escape — always use when inserting user data into innerHTML |
| `ctx.savePage(slug, content?, config?)` | `Promise<bool>` | Write to any page |
| `ctx.getPageContent(slug)` | `Promise<object\|null>` | Read a page's `{content, config}` |
| `ctx.getCss()` / `ctx.getHtml()` | `string` | Get editor values |
| `ctx.setCss(v)` / `ctx.setHtml(v)` | `void` | Set editor values (marks unsaved, refreshes preview) |
| `ctx.currentPage()` | `object\|null` | Page currently open in editor |
| `ctx.switchTab(name)` | `void` | Navigate to a dashboard tab |
| `ctx.sendToVibeCoder(text)` | `void` | Pre-fill Vibe Coder prompt and switch to that tab |
| `ctx.reloadWidgets()` | `void` | Reload all widgets |
| `ctx.registerVibeAddon(config)` | `void` | Register a Vibe Coder context button |

## Vibe Coder addons

Widgets can extend the Vibe Coder toolbar with context buttons. When clicked, they insert a text snippet into the AI prompt.

```javascript
ctx.registerVibeAddon({
    id: 'my-widget-context',
    label: 'My Data',               // shown as "+ My Data" in tools row
    pick: async () => {             // called on click; return string or null
        const r = await ctx.apiFetch('/api/adze/my-endpoint');
        if (!r.ok) return null;
        const data = await r.json();
        return `[My Widget: ${JSON.stringify(data)}]`;
    }
});
```

Text format conventions:
- YouTube: `YouTube video "Title" — embed: <iframe src="https://www.youtube.com/embed/ID"></iframe>`
- Vimeo: `Vimeo video "Title" — embed: <iframe src="https://player.vimeo.com/video/ID"></iframe>`
- General: `AssetType "Name" — [data the AI needs]`

## Common UI patterns

### Stats grid

```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;margin-bottom:28px;">
  <div style="border:1px solid var(--border);border-radius:var(--radius);padding:16px;text-align:center;">
    <div style="font-size:22px;font-weight:600;color:var(--text);font-family:var(--heading-font);">[value]</div>
    <div style="font-size:10px;color:var(--text2);margin-top:3px;">[label]</div>
  </div>
</div>
```

### Section label

```html
<div style="margin-bottom:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);">[Section Name]</div>
```

### Setup / credentials form

```html
<div style="max-width:420px;margin-top:16px;">
  <p style="font-size:11px;color:var(--text2);margin:0 0 20px;line-height:1.6;">Instructions...</p>
  <div>
    <label style="font-size:10px;font-weight:600;color:var(--text2);display:block;margin-bottom:4px;">Token</label>
    <input id="xx-token" type="password" style="width:100%;box-sizing:border-box;padding:7px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
  </div>
</div>
```

### "Add to site" pattern

```javascript
case 'add-to-site':
    ctx.sendToVibeCoder(
        `Add a [feature] to my site. POST to /api/adze/[endpoint] with JSON: { artist_slug: "${ctx.artistSlug}", field }. [success behaviour]. Match existing design.`
    );
    break;
```

## CSS variables

```
--bg, --bg2, --bg3
--surface, --surface2
--border
--text, --text2
--accent, --accent-text, --accent-hover
--success, --warn, --danger
--radius
--body-font, --heading-font, --mono
--shadow-sm, --shadow-md
```

## Rules

- The widget file MUST be a self-executing IIFE `(function(ctx){ ... })(ctx)` — never `export`, `module.exports`, or `async function render(ctx)` patterns. The dashboard evaluates the file directly; there is no loader.
- Always use event delegation (`data-action` + `closest()`), never global onclick handlers
- NEVER use `</script>` literally inside template literals — use `<\/script>`
- All API calls go through `ctx.apiFetch`, never raw `fetch()` — this is how the Backend tab detects which endpoints a widget uses
- Backend endpoints go in `_shared/admin_api.py` under the existing Flask blueprint
- Always escape user-controlled data with `ctx.escHtml()` before inserting into innerHTML
- Never put secrets in widget.js — proxy external service calls through a backend endpoint
- T2 widgets must have a README.md — create or update it whenever you add or change endpoints
