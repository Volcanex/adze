---
name: adze-design-language
description: The Adze design system — tokens, components and rules for adze.studio surfaces (artist login, sites dashboard, content admin, studio chrome). Use whenever building or restyling any Adze UI.
---

# Adze Design Language

Read `readme.md` first for the character and the architecture. This file is
the operating checklist.

## Before writing any UI

1. Link `design-language/adze/styles.css`. Don't copy token values inline —
   that is exactly how the old chrome ended up with four divergent `:root`
   blocks across `home.html`, `admin.html`, `dashboard.html` and `portal.html`.
2. Check whether a component already exists in `components/`. If it does, read
   its `.prompt.md` before using it.
3. If you need a value that isn't a token, stop. Either the scale is wrong (a
   design decision — raise it) or the layout is wrong (usually this).

## Before shipping any UI: nothing touches

**Look at it, and check that no two things are touching.** A button hard
against the card above it, cards with no gutter, a field against its own
heading — this is the single most common defect in this system, it is always
visible in one screenshot, and it is never caught by reading the CSS.

Two rules that prevent it:

- **One spacing owner per stack.** Whatever a thing FOLLOWS supplies the gap —
  never the thing itself. A container using `gap` plus children carrying
  `margin-bottom` double up; a container with neither leaves them touching. Pick
  one owner and make the other stand down explicitly.
- **The gap is a token, always.** `--adze-space-6` between blocks,
  `--adze-space-4` inside one. If a gap is invented at the call site it will not
  agree with the identical gap twenty lines up, which is how a screen stops
  looking like one system.

The trap: a component that spaces correctly in one context and not another,
because the first context's parent happened to own the gap. `.as-actions` in
the artist admin carried only `--adze-space-1`, which was right under `.as-form`
(which owns the gap beneath itself) and wrong under a card stack that owned
nothing — so Save sat 4px under the last card. Same class, same file, two
outcomes. **When you reuse a row in a new place, re-check its gap there.**

## The division of typefaces

If you'd read it aloud in a sentence → **Inter** (`--adze-font-ui`).
If your eye lands on it to find a value → **JetBrains Mono** (`--adze-font-mono`).

Headings are Inter. Labels, status chips, counts, dates, sizes and IDs are
mono, via `.adze-label` and `.adze-numeric`.

## The artist override

Components read `--adze-*` system tokens only. Never read `--adze-artist-*`
directly, never hardcode a hex. Both break the per-artist override silently —
the bug only shows up on one artist's admin, which is the worst way to find it.

Status tones (success/warn/danger) are fixed and must not be themed.

## Loading states are not optional

Anything that can take more than ~400ms needs one, chosen in this order:

1. `Skeleton` / `SkeletonRows` — you know the shape of what's coming. Best.
2. `ProgressBar` — you know how far along you are.
3. `Spinner` — you know neither. Last resort.

Never fake a determinate progress bar on a timer.

## Accessibility floor

- `:focus-visible` with `--adze-focus-ring` on every interactive element.
  Never `outline: none` without a replacement.
- Never colour alone — pair it with an icon, dot, or text.
- Every form control goes inside a `Field` so label, `aria-describedby` and
  error association come for free.
- Controls hit 44px on mobile (handled by `base.css`; don't override).
- Respect `prefers-reduced-motion` — `motion.css` handles it globally, so
  don't add animations outside the token system.

## When you change this system

Update the token file, not the call site. Then update the relevant
`guidelines/*.html` specimen so the rendered documentation stays true, and
re-run `scripts/gen_cards.py` if you touched the shared token preamble.

Every `guidelines/` and `*.card.html` file starts with a
`<!-- @dsCard group="…" name="…" subtitle="…" -->` marker — that's what builds
the index in the Design System pane. Keep it on line 1.
