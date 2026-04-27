# Site widgets (Tier 4)

The user can ask for widgets — small interactive panels that appear
inside the dashboard's widget tab for this site. You build these in
`widgets/<name>/` inside the artist directory.

## File shape

```
widgets/<name>/
  widget.json   ← required: metadata
  widget.js     ← required: an IIFE that owns ctx.container
```

### widget.json

```json
{
  "name": "my-widget",
  "description": "One-line description",
  "icon": "star",
  "category": "integrations",
  "marketplace": false
}
```

Available icons: `star`, `play`, `mail`, `users`, `calendar`,
`bar-chart`, `credit-card`, `video`, `rss`, `settings`, `zap`, `globe`.

`marketplace: false` keeps the widget private to this site. Only flip
to `true` if the artist explicitly wants to share it.

### widget.js shape

```javascript
(function(ctx) {
    const c = ctx.container;
    c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';
    c.innerHTML = `
      <div style="flex:1;overflow-y:auto;padding:24px;max-width:800px;margin:0 auto;">
        <h3 style="font-family:var(--heading-font);font-style:italic;font-weight:400;font-size:16px;margin:0 0 12px;">My Widget</h3>
        <div id="mw-body"></div>
      </div>`;
    // event delegation, never global onclicks
    c.addEventListener('click', async (e) => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        // handle btn.dataset.action
    });
    // init
})(ctx);
```

The dashboard auto-discovers `widgets/<name>/` next time the widget
tab loads — no restart needed.

## ctx API

| Property | Description |
|---|---|
| `ctx.container` | Widget's root DOM node. Style it as a flex column. |
| `ctx.artistSlug` | This artist's slug |
| `ctx.apiFetch(url, opts)` | Authenticated fetch. `opts.body` may be a plain object. |
| `ctx.toast(msg, type?)` | Toast. Type: `success` (default), `error`, `warn`, `info` |
| `ctx.escHtml(str)` | HTML-escape — always use before inserting user data via innerHTML |
| `ctx.savePage(slug, content?, config?)` | Write to a page |
| `ctx.getPageContent(slug)` | Read a page's `{content, config}` |
| `ctx.pages` | `[{slug, title}]` for this site |

## Style with CSS variables

Use these so the widget matches the dashboard:
`var(--text)`, `var(--text2)`, `var(--accent)`, `var(--bg)`, `var(--bg2)`,
`var(--surface)`, `var(--border)`, `var(--radius)`, `var(--heading-font)`,
`var(--mono)`. Italic Cardo for headings, Inter for body, 11–13px text.

## Rules

- `widget.js` MUST be a self-executing IIFE `(function(ctx){…})(ctx)`. No `export`, `module.exports`, or top-level `async function`.
- Use event delegation (`data-action` + `closest()`) — never global `onclick` handlers.
- All API calls go through `ctx.apiFetch`, never raw `fetch()`.
- Always `ctx.escHtml(...)` user data before inserting into innerHTML.
- Never put secrets in `widget.js`. If you need an external service, proxy it through a `/api/artists/{slug}/...` endpoint in `api.py`.
- Never use `</script>` literally inside template literals — use `<\/script>`.
- Use a unique 2–3 letter prefix on all element IDs (`mw-` for "my widget").

## Platform widgets are off-limits

The other kind — `_shared/widgets/` (Tier 2) — runs with admin
privileges and is created only by Gabriel. You can't read or write
those (you're path-scoped to your artist directory anyway). If a user
asks for cross-site or admin-token functionality, refuse and ask them
to contact Gabriel.
