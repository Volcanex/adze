# Design Language — canonical reference

Two design systems live here. Don't cross-apply them.

**`adze/`** — the **Adze** design system (current, written 2026-07-30). Tokens,
components and rules for adze.studio's own surfaces: artist login, sites
dashboard, content admin, studio chrome. Neutral near-white, 13px base, Inter
for reading + JetBrains Mono for scanning, accent `#1c4f82`. Mirrored to the
Claude Design project "Adze — Design Language". See [adze/CLAUDE.md](adze/CLAUDE.md).

**`project/`** — the **Last Place** design system. The brand for the lastplace
workspace: handover portals, client-facing pages. Hyperlink blue `#0000EE`,
Cormorant, plant mark. Exported from claude.ai/design.

## Adoption status

`adze/` is **not yet wired into any live surface.** The chrome files still
carry their own inline `:root` blocks (see below), and
`_shared/shell/admin-shell.css` still defaults to a neutral dark-gold palette.
Adopting the token bundle is a separate, agreed job.

## Last Place design system (`project/`)

Hyperlink blue `#0000EE`, black ink, white space, Cormorant serif. A lino-print plant mark is the visual signature.

- `project/tokens/` — CSS custom properties: `colors.css`, `typography.css`, `spacing.css`, `base.css`, `fonts.css`
- `project/styles.css` — single `@import` entry point
- `project/assets/` — `plant-mark-blue.png`, `plant-mark-blue-knockout.png`
- `project/cards/` — specimen HTML cards (colours, type, spacing, brand mark)
- `project/components/` — `Button`, `Card`, `Tag`, `TextLink`, `Field`, `Checkbox`, `Switch` (JSX + HTML previews)
- `project/ui_kits/studio-site/` — full Last Place studio site (home, work, studio, contact) as a click-through
- `project/templates/studio-page/` — blank page scaffold with tokens wired up
- `project/readme.md` — voice, visual rules, full index
- `project/SKILL.md` — agent skill entry point for this system
- `README.md` — upstream handoff README

**Use for:** `_shared/handover.html`, client-facing handover slides.

> `_shared/portal.html` used to be listed here. **It is dead code** — its only
> route (`flask_server.py`, `/api/manage`) points at `pages/artists/_shared/portal.html`,
> a path that doesn't exist, so the endpoint returns "Portal not found". Don't
> spend effort skinning it.

## Adze chrome identity (legacy — pre-`adze/`)

The **currently live** chrome (adze.studio landing, `admin.html`,
`dashboard.html`) still uses the older mono/technical direction:

- `--accent: #1C4F82` on warm cream `#f5f2ed`, ink `#2a2a28`
- `--heading-font: 'JetBrains Mono', monospace` for headings
- `--radius: 4px`, 10–13px text, uppercase tracked section headers

Each of those files carries its own inline `:root` block, and they have
drifted: `--text2` differs in `dashboard.html`, `home.html` is missing
`danger`/`success`/`warn`/`surface2`, and shadow alpha varies between 0.05 and
0.06. They also declare `--radius: 4px` while hardcoding 8px 32 times and 6px
25 times.

**Stale comment, do not trust it:** `dashboard.html` and `portal.html` both
carry `/* Tokens — canonical source: /design-language/project/Adze Design
Language.html — keep in sync */`. That file no longer exists (`project/` is
Last Place now), and the dashboard comment further claims `--radius 6px (vs
8px)` when the actual value is 4px. Delete those comments when you next touch
the files — the real canonical source is `adze/tokens/`.

Until adoption, `#1c4f82` is the one value shared between the legacy chrome
and the new `adze/` bundle.

### Preserved by user request
- **Tabs** — current tab styling in `admin.html` / `dashboard.html`. Don't restyle.
- **Toast notifications** — `dashboard.html:451-457`. Don't restyle.

### Intentional chrome divergences
`dashboard.html` runs denser than `admin.html` (smaller fonts, 10–13px). Don't
homogenise `--radius` or colour values between them while they remain on the
legacy tokens.
