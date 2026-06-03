# Design Language — canonical reference

Bundle exported from claude.ai/design and dropped here as the source of truth for Adze visual style. **Read `project/Adze Design Language.html` in full before changing any chrome in `_shared/portal.html`, `_shared/admin.html`, or `_shared/dashboard.html`.**

## What's here
- `project/Adze Design Language.html` — the design system itself (colour tokens, type scale, geometry, components, voice). Open in a browser to see; read the source for exact values.
- `project/_shared/` and `project/static/` — the brand assets the design page references (logo, favicon).
- `chats/chat1.md` — the conversation that produced the design language. Useful for understanding *why* a choice was made (e.g. why the wordmark is upright bold instead of italic — see "Looks better sharper and cleaner").
- `README.md` — the upstream handoff README.

## ⚠ Chrome moved to the "mono" direction (2026-06-03)

The live chrome (`portal.html`, `admin.html`, `dashboard.html`) has been migrated
off the original Cardo-serif-italic identity to a **mono / technical** direction
("Alt 2"). The `project/Adze Design Language.html` export here still documents the
**old** Cardo look and is now behind — treat it as historical until re-exported.

What changed in all three `:root` blocks:
- `--heading-font: 'JetBrains Mono', 'Monaco', 'Menlo', monospace` (was `'Cardo', Georgia, serif`)
- `--mono` now leads with `'JetBrains Mono'`
- `--radius: 4px` (was 6px admin/dashboard, 8px portal)
- All heading `font-style: italic` removed → upright; section headers are uppercase + tracked
- Wordmark lockup is `[Adze]` (accent-coloured brackets)
- Font imports add `JetBrains+Mono:wght@400;500;700`

Comparison mockups live in `static/design-language-*.html` and are linked from the
admin **Extras** tab:
- `design-language.html` — live reference (now reflects mono, parses chrome CSS)
- `design-language-1-legacy.html` — **frozen** Cardo-italic archive (static on purpose)
- `design-language-2-mono.html` — the adopted direction
- `design-language-3-clean.html` / `-4-editorial.html` — unused explorations

Tabs and toasts were left untouched (still "preserved by user request", below).

## How it relates to the live code

The design language was distilled **from** `_shared/portal.html` and `_shared/admin.html`, then refined. So the live files mostly already match canon. The three live files each carry their own copy of the tokens (`:root` and `[data-theme="dark"]` blocks) — keep them in sync with this file. Each `:root` block has a comment pointing back here.

### Intentional divergences

`_shared/dashboard.html` runs denser than the canon:
- `--radius: 6px` (canon is 8px)
- `--text2: #5a5750` light / `#aaa79e` dark (canon is `#6b6860` / `#9a978e`)
- adds `--bg3` for API-method badge backgrounds

These are deliberate adaptations for the admin tool's smaller fonts (10–13px). Don't homogenise.

## Preserved by user request

- **Tabs** — current tab styling across all three files is loved as-is. Don't restyle.
- **Toast notifications** — `portal.html:321-334` and `dashboard.html:451-457`. Don't restyle.

## Tokens beyond the live files

`--accent-soft: #6b8cae` (light) / `#7ea3c4` (dark) — the dusty steel-blue from the logo. Defined in all three files but not yet used. Per canon, the **portal** surface should use this softer accent; the **admin/dashboard** surfaces use the deeper `--accent: #1C4F82`. Switching portal to `--accent-soft` is a visible behavioural change — do not flip without user OK.
