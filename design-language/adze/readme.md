# Adze Design Language

The design system for **adze.studio** — the artist login, the "your sites"
dashboard, the content admin, and the studio chrome.

Not to be confused with **Last Place** (`design-language/project/`), which is
a separate brand used for handover portals and client-facing pages. Hyperlink
blue, Cormorant, plant mark. Don't cross-apply the two.

## The character

Halfway between Apple and mono, modern.

Neutral near-white surfaces, generous space, restrained type, precise motion —
but the technical Adze voice is preserved deliberately in the mono details:
field labels, status chips, counts, dates, IDs. Inter carries everything a
person reads; JetBrains Mono carries everything a person scans.

The previous chrome was a dense technical control panel — 10–11px text, warm
cream, mono headings. That was a coherent identity, just not this one. The
accent blue `#1c4f82` is the one thing carried across unchanged.

## The one architectural rule

**Adze owns structure. The artist owns palette.**

An artist's content admin can set six colour variables and nothing else. Type,
spacing, radius, motion, and component behaviour are Adze's. That single axis
of variation is what lets the loading states and the polish be built once and
land on every artist's admin, while their admin still feels like an extension
of their own site.

```json
"admin_theme": {
    "bg": "#281800", "surface": "#1a1000", "text": "#c9a573",
    "accent": "#c9a573", "accentText": "#281800", "border": "#4a3318"
}
```

These map to `--adze-artist-*`; every other token derives from them via
`color-mix()`. Six values produce a complete admin — hovers, tints, sunken
surfaces, focus rings. See `guidelines/color-artist-override.html` for the
same markup rendered under five real artist palettes.

Status colours (success/warn/danger) are **not** overridable. "Live" must mean
the same thing on every admin; an artist whose accent is red must not get a
red "saved".

`font` was in the old `admin_theme` contract and has been removed. A custom
face invalidates every line-height in the type scale, and the failure is
invisible — the admin just looks subtly wrong on that one artist.

## Using it

```html
<link rel="stylesheet" href="/design-language/adze/styles.css">
```

Import order inside `styles.css` matters: fonts → colours → type → space →
motion → base. `base.css` consumes every token above it.

Components must only ever read system tokens (`--adze-*`). Never read an
`--adze-artist-*` variable directly and never hardcode a hex — that's what
breaks the override, and it breaks silently, on one artist's admin only.

## Index

| Path | What |
|---|---|
| `styles.css` | Single entry point |
| `tokens/colors.css` | The six-var artist contract + all derived colour |
| `tokens/typography.css` | Two-typeface scale, `.adze-label`, `.adze-numeric` |
| `tokens/spacing.css` | 4px grid, control heights, radii, widths, elevation |
| `tokens/motion.css` | Durations, easing, keyframes, reduced-motion |
| `tokens/base.css` | Reset, document defaults, focus, touch targets |
| `tokens/fonts.css` | Inter + JetBrains Mono loading |
| `components/core/` | Button, Card, Tag, TextLink |
| `components/forms/` | Field, Input, Select, Checkbox, Switch |
| `components/feedback/` | ProgressBar, Skeleton, Spinner, EmptyState |
| `guidelines/` | Rendered specimens for colour, type, layout, motion |

Each component ships `.jsx` (with its CSS as a named export), `.d.ts`, and a
`.prompt.md` holding the rules an agent needs to use it correctly. Read the
`.prompt.md` before using a component — several encode decisions that aren't
obvious from the props (Checkbox vs Switch, inline vs standalone links,
which loading state to reach for).

## Rules worth knowing before you build

- **No value that isn't a token.** If a spacing or radius you need isn't in
  the scale, the layout is asking the wrong question.
- **Loading states are mandatory.** Anything over ~400ms shows a Skeleton
  (shape known), ProgressBar (progress known), or Spinner (neither). The old
  admin had none of these — publishing simply froze until it didn't.
- **Never colour alone.** Every state carries a second signal: an icon, a dot,
  or text.
- **`:focus-visible` always.** Never `outline: none` without providing
  `--adze-focus-ring`.
- **Max one primary button per view.** Two means neither is primary.
- **Checkbox saves on submit; Switch saves immediately.** Pick by when the
  change lands, and give the Switch a `pending` state.
