# Last Place — Design System

A design system for **Last Place**, a small web design studio in the UK
(https://lastplace.co.uk). The brand is web-native and quiet: a single
confident **hyperlink blue**, black ink, and a great deal of white space, set
in **Cormorant**. Forest green is a rare second voice. The studio's visual
signature is a **lino-print plant** — roots and shoots — printed in pure blue.

> **Sources given to build this system**
> - Brand notes from the studio (palette, typeface, spacing voice).
> - `uploads/IMG_3306.png` — the lino-print plant mark (pure `#0000FF`). Copied
>   into `assets/plant-mark-blue.png` and a transparent knockout
>   `assets/plant-mark-blue-knockout.png`.
> - Website: https://lastplace.co.uk (JS-rendered; could not be scraped — built
>   from the studio's written brand direction).
> - Typeface: Cormorant — https://fonts.google.com/specimen/Cormorant

---

## Content fundamentals

How Last Place writes:

- **Voice: "we", warm and plain.** The studio speaks as *we* and addresses the
  reader as *you*. "We are Last Place — a small web design studio." Never
  corporate, never breathless.
- **Lowercase intimacy in micro-copy.** Buttons and small affordances often run
  lowercase ("read the case study", "say hello", "view project") even while
  section labels are SET IN UPPERCASE MONO. The contrast is intentional.
- **Understatement over hype.** "A sentence or two is plenty." "We reply within
  a day." No exclamation marks, no superlatives, no "revolutionary".
- **British spelling.** colour, organise, programme, whilst.
- **Dry wit, lightly.** The name itself ("Last Place") is a joke the studio is
  in on — confident enough to come last. Copy can wink but never mugs.
- **No emoji.** The brand voice is typographic. Affordances use a single
  unicode arrow (↳ / →) instead of icons or emoji.
- **Numbers and metadata in monospace.** Dates, credits, figures, the year of
  establishment — all set in the mono, tracked.

Examples:
- Eyebrow: `SELECTED WORKS` · `STUDIO — EST. 2022` · `INDEX`
- CTA: "Start a project" · "say hello" · "↳ View project"
- Body: "We like a lot of white space and a single, confident blue."

---

## Visual foundations

- **Colour.** Hyperlink blue `#0000EE` is the signature and the *only* loud
  colour — used for links, the primary button, media wells, and the mark. Ink
  `#0B0B0C` (never pure black on screen) carries text. White is the page.
  Forest green `#14432B` appears rarely — a single accent, an error state, one
  highlighted word. Greys are simply black at alpha; there are no separate grey
  tokens.
- **Type.** Cormorant throughout, used across its optical range: **light (300)**
  for display, **regular (400)** for reading. A system **monospace** handles
  labels, captions and metadata — uppercase and tracked at `0.2em`. There is no
  third typeface.
- **Leading — two modes.** Body copy is *airy* (line-height 1.62) with generous
  margins. Display type can flip to **clip leading** (line-height ≈ 0.86) where
  lines just about kiss without overlapping — the studio's signature move.
  Clip leading is for display only, never body.
- **Space.** The system runs on air: a generous side margin
  (`clamp(24px, 6vw, 120px)`), a comfortable measure (~62ch), and a 4-based
  spacing scale that reaches 256px. When in doubt, add space.
- **Backgrounds.** Plain white (or faint warm paper `#FBFBF9`). No gradients, no
  textures, no photographic hero washes. The only imagery is the blue
  lino-print artwork and solid blue blocks.
- **Borders & cards.** Structure is drawn with **hairline rules** (`1px` ink at
  14% alpha), not shadows. Cards are square-cornered with a hairline border;
  on hover the border darkens to ink and any image scales a touch (1.03).
- **Radii.** Sharp. `0` is the default corner; `2px` is as soft as it gets;
  pills are reserved for the rare round tag.
- **Shadow.** Almost none. A `--shadow-lift` exists for overlays but the system
  prefers rules and blue blocks to elevation.
- **Motion.** Restrained and quick (`120–220ms`), `ease-out`. Underlines lift,
  borders darken, images ease in scale. No bounce, no parallax, no infinite
  loops. Respect `prefers-reduced-motion`.
- **Hover / press.** Links: the underline *lifts away* on hover (rather than
  appearing). Buttons: primary darkens to `--lp-blue-deep`, outline/ghost gain
  a faint `ink-04` wash. Press uses the deeper blue; no shrink.
- **Imagery vibe.** Hand-printed, high-contrast, pure blue on white — graphic
  and a little rough at the edges (the lino bite is part of it). Never warm
  photography, never stock.

---

## Iconography

Last Place is **almost icon-free** — the brand leans on type and the blue mark
rather than an icon set.

- **No icon font, no sprite.** Affordances use **unicode arrows** — `↳` for
  "go to project", `→` for forward motion. These are set in the serif or mono
  inline with text.
- **The plant mark** (`assets/plant-mark-blue.png` and its knockout) is the one
  recurring graphic device — used as a logo, a section punctuation, or a
  full-bleed blue block.
- **The LP monogram** (Cormorant on a blue square) acts as a compact mark /
  favicon.
- **Checkmarks etc.** Where a glyph is unavoidable (e.g. the checkbox tick) it
  is a minimal square-cap SVG stroke, drawn inline — never an emoji, never a
  third-party icon.
- **No emoji, anywhere.**

If a project genuinely needs a UI icon set, substitute a thin, square-cap line
set (e.g. Lucide at `1.5px`) and flag it — but prefer doing without.

---

## Index — what's in this system

**Foundations**
- `styles.css` — the single entry point consumers link (an `@import` manifest).
- `tokens/fonts.css` — Cormorant (Google Fonts).
- `tokens/colors.css` — palette, ink tints, semantic aliases.
- `tokens/typography.css` — families, sizes, leading, tracking, role classes.
- `tokens/spacing.css` — spacing scale, layout, radii, rules, motion.
- `tokens/base.css` — element defaults (body, links, headings, focus).

**Specimen cards** (`cards/*.html`) — Design System tab
- Colors: brand palette, ink tints, link voice.
- Type: display, headings, lede & body, clip leading, mono labels.
- Spacing: scale, radii & rules.
- Brand: plant mark, wordmark.

**Components** (`components/*`)
- `core/` — `Button`, `TextLink`, `Tag`, `Card`.
- `forms/` — `Field`, `Checkbox`, `Switch`.

**UI kit** (`ui_kits/`)
- `studio-site/` — the Last Place studio website: home, work index, studio,
  contact. Interactive click-through in `index.html`.

**Assets** (`assets/`)
- `plant-mark-blue.png`, `plant-mark-blue-knockout.png`.

**Other**
- `SKILL.md` — makes this folder usable as an Agent Skill.
