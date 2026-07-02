# Design Language — canonical reference

Two design systems live here:

**`project/`** — the **Last Place** design system (current). This is the brand used for the lastplace workspace: handover portals, client-facing pages. Exported from claude.ai/design, source of truth for anything branded Last Place.

**Adze chrome** (`_shared/portal.html`, `_shared/admin.html`, `_shared/dashboard.html`) uses a separate mono/technical identity — see the note below. Don't confuse the two.

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

**Use for:** `_shared/handover.html`, `_shared/portal.html` (lastplace workspace), client-facing handover slides.

## Adze chrome identity

The live chrome (adze.studio landing, `admin.html`, `dashboard.html`) uses the **mono/technical** direction:
- `--heading-font: 'JetBrains Mono', monospace` (upright, not italic)
- `--radius: 4px`, uppercase + tracked section headers, `[Adze]` wordmark in accent brackets

This is separate from the Last Place brand. Don't cross-apply. The three chrome files each carry their own `:root` tokens; keep them in sync with each other, not with `project/`.

### Preserved by user request
- **Tabs** — current tab styling across all three files. Don't restyle.
- **Toast notifications** — `portal.html:321-334` and `dashboard.html:451-457`. Don't restyle.

### Intentional chrome divergences
`dashboard.html` runs denser than `portal.html` / `admin.html` (smaller fonts, 10–13px). Don't homogenise `--radius` or colour values between them.
