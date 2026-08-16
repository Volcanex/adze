# Adze Design Language

The design system for adze.studio's own surfaces. **Read `readme.md` for the
character and `SKILL.md` for the operating checklist** — this file only covers
what isn't obvious from those.

Mirrored to the Claude Design project **"Adze — Design Language"**
(`22a64760-5881-46cf-abc2-8d24934ace73`). Edit here, push with `DesignSync`;
the local tree is the source of truth.

## Two gotchas when pushing to Claude Design

**Cards don't appear from the `@dsCard` marker alone, and `register_assets`
does not fix it.** The Design System pane indexes `_ds_manifest.json`, which is
compiled by the *app's* self-check. Nothing you do over the API runs that
self-check, so a card uploaded through `DesignSync` is simply absent from the
pane no matter how correct its marker is.

This file previously said to call `register_assets`. **That is wrong** — tested
2026-08-03: registering 9 assets returned `registered: 9` and not one of them
appeared. `register_assets` is the legacy path for hand-authored projects
without markers and writes to an index the pane no longer reads.

**What actually works:** patch `_ds_manifest.json` directly.

1. `DesignSync get_file` → `_ds_manifest.json`
2. Append entries to its `cards` array — `{path, group, subtitle, name}`
3. `finalize_plan` with `_ds_manifest.json` in `writes`, then `write_files`

Pass everything else through untouched. `tokens`, `themes`, `brandFonts`,
`components` and `globalCssPaths` in that file are *derived by the app* from the
CSS, and there is no local copy to restore them from — this file only exists
remotely. Round-trip through `json.load`/`json.dump` rather than editing by hand,
and check the section lengths against what you fetched before you write
(currently: 14 components, 112 tokens, 2 themes, 2 brandFonts, 7 globalCssPaths).

Every `path` in `cards` must exist in the project or the pane renders a dead
tile. Components, tokens, themes and fonts still index automatically; only the
cards need this.

**The manifest compiler flattens `@media` blocks last-wins**, ignoring query
context, so any token redeclared inside a media query is reported at its
override value. This bit twice:

- `--adze-dur-*` was reported as `1ms` because of the reduced-motion block —
  the exact opposite of the spec. Fixed by deleting that override entirely; the
  universal `!important` rule in `motion.css` already enforces the behaviour,
  so the tokens now keep their design values. Don't reinstate it.
- `--adze-control-*` is still reported as the <640px values (36/44/48) rather
  than the canonical 28/36/44. Left alone deliberately — contorting working CSS
  to satisfy a doc parser is the wrong trade. The canonical block in
  `spacing.css` is the truth.

## Adoption status

**Adopted — artist custom admins** (`theirdomain.com/admin`), 2026-07-30.
`_shared/shell/admin-shell.css` is now tokens-only and the five `content_admin`
artists run on the six-var palette contract. The tokens are served **live from
this directory** by `content_admin.py` (`TOKEN_FILES`), so editing a file here
restyles every artist admin on the next page load — no copy step, nothing to
keep in sync. `docker-compose.yml` mounts `./design-language` read-only for
this; before that mount existed the container ran a stale copy from image-build
time, and token requests 404'd.

**Not adopted — the Adze chrome.** `_shared/home.html`, `_shared/admin.html`
and `_shared/dashboard.html` still carry their own inline `:root` blocks (four
independent copies that have already drifted). Deliberately out of scope: the
dashboard is the editor, a separate surface from the artist admins. Don't
assume a token here matches what's on screen *there*.

## The one non-obvious mechanic — `.adze-theme`

Custom properties resolve where they are **declared**, not where they are
used. Every derived token (`--adze-bg-sunken`, `--adze-text-muted`, the
`*-soft` status plates, …) is declared on `:root` as a `color-mix()` of the
six artist-contract vars. So:

- Setting the contract vars on `:root` / `document.documentElement` — what
  `admin-shell.js applyTheme()` does — re-derives everything correctly.
- Setting them on a **nested element does not.** The derived tokens keep
  resolving against `:root`, and you get light-grey sunken surfaces inside a
  dark artist theme.

Put `.adze-theme` on any element carrying its own contract vars. Needed for a
live theme preview in the dashboard, the specimen cards, and any same-document
embed of another artist's admin. Its declaration list in `tokens/colors.css`
must stay in exact sync with the `:root` derived block — that duplication is
deliberate and load-bearing; don't "simplify" it away.

## Two generators, and neither output is hand-editable

`guidelines/*.html` and `components/*/*.card.html` are **generated**:

```
python3 design-language/adze/scripts/gen_cards.py
```

`ui_kits/content-admin/*.html` is **captured from the running app**:

```
python3 design-language/adze/scripts/capture_surfaces.py [--artist rose]
```

The capture exists because the dash and the content admin are not components —
they are ~4,200 lines of imperative vanilla JS building DOM from literal
`as-*`/`af-*` strings, with no component model to export. A hand-authored kit
would be a second implementation of markup that already exists, which is the
exact drift this directory is organised against. So the kit is a snapshot of the
real surfaces with the token bundle and `admin-shell.css` inlined, scripts
stripped. `_shared/shell/` stays the source of truth; re-running the script is
how the kit is updated.

Three things in that script are load-bearing and look like fussiness:

- **Form state is reflected into attributes before serialising.** `innerHTML`
  writes attributes, not the live `value` IDL property, so the first capture came
  out with every box blank — the fields a form specimen exists to show are
  precisely the ones that vanish.
- **The artist's six theme vars go into `:root`, not onto the captured node.**
  Same reason `.adze-theme` exists (below): every derived token is a
  `color-mix()` declared on `:root`, so contract vars on a nested element leave
  the whole chain resolving against the default palette.
- **Thumbnails are inlined as downscaled data URIs, under a byte budget.** They
  resolve from `/assets/<src>` on the artist's domain and are broken images in a
  standalone file — and a picture-grid specimen with no pictures argues against
  `layout-columns.html`'s own rule. The budget is there because the pane caps a
  file at 256 KiB and one gallery-heavy artist would otherwise blow it silently.

The capture defaults to a **real** artist (`rose`), not `sandbox`: list density,
a real palette and populated fields are the entire subject, and the sandbox has
one empty note.

Each card is standalone HTML (the Design System pane renders each in its own
frame), so the token block is inlined into every one. Generating them from the
single `TOKENS` string in that script is what stops the eleven cards drifting
apart the way the four chrome `:root` blocks did. **Edit the generator, not
the HTML.**

Line 1 of every card must stay a `<!-- @dsCard group="…" name="…"
subtitle="…" -->` marker — that builds the index in the Design System pane.

## Artist contract

Six vars, no more: `bg`, `surface`, `text`, `accent`, `accentText`, `border`
(from `admin_theme` in the artist's `config.json`). `font` was in the old
contract and is **deliberately dropped** — a custom face invalidates every
line-height in the type scale, and it fails invisibly on that one artist.

Five artists currently set `admin_theme`: `alfiebruce`, `jackdt`, `lydialott`,
`mariaslaughter`, `rose` — all five migrated to the six-key contract on
2026-07-30, `font` removed from jackdt/rose/alfiebruce.
`guidelines/color-artist-override.html` renders all five.

**Opaque colours only.** alfiebruce's `border` was `rgba(255,255,255,0.15)`,
which made every `color-mix()` derived from it semi-transparent too; it is now
the composited `#262626`. A translucent value in any of the six poisons the
whole derivation chain silently.

**Clear colours only — do not tint the neutrals to match the artist's site.**
The six vars go straight into the token chain with nothing checking contrast,
so an unreadable admin ships silently and the artist is the one who finds it.
Put the artist's identity in `accent` and leave `bg`/`surface`/`text`/`border`
as near-neutral as the theme allows — black and gold, white and ink. alfiebruce
(`#000000`/`#111111`/`#ffffff`) is the model.

mariaslaughter is the cautionary case (fixed 2026-07-31). Her admin was
`bg #281800` / `surface #1a1000` / `text #c9a573` / `border #4a3318` — six
browns lifted off her gothic site. Cards sat at **1.10:1** against the page and
borders at **1.46:1**, so the panels were invisible; muted labels, which derive
as `color-mix(text 62%, bg)`, landed at **3.68:1**. Now `#0a0a0a`/`#161616`/
`#f0e6d6` with her `#c9a573` as the accent: 1.6:1, 3.4:1, 13.9:1.

Floors to hold when setting `admin_theme`: `text` on `bg` ≥ 4.5:1, `border` and
`surface` edges on `bg` ≥ 3:1, `accentText` on `accent` ≥ 4.5:1. Check the
derived muted tone, not just `text` — it is the first thing to fail. Render
`guidelines/color-artist-override.html` after any change; it shows every
artist's palette side by side.

Status colours (`success`/`warn`/`danger`) are not overridable — see the
comment in `tokens/colors.css`.

## Layout and motion doctrine now has a home (2026-07-31)

Three new generated cards:

- `guidelines/layout-columns.html` (group **Layout**) — auto-fit grids not
  breakpoints; a wider viewport means more columns, never longer lines; layout
  derived from field role; one spacing owner per stack; a list of visual things
  is a grid of pictures, which requires a card-sized image tier.
- `guidelines/motion-choreography.html` (group **Motion**) — what moves and why,
  as distinct from `motion-timing`'s durations and curves. Shared-element
  transitions over crossfades, capped stagger, and entrance-on-mount rather than
  entrance-on-render.
- `guidelines/editor-bounds.html` (group **Components**) — an embedded editor may
  only offer formatting the surrounding design already styles. Teaches the
  *mechanism*: the format/blot registry plus a paste sanitiser plus the
  server-side whitelist. **The toolbar is explicitly not the control**, because
  paste bypasses it.

Groups are topic-based (`Layout`, `Motion`, `Components`) to match every existing
card — a layout guideline filed away from `spacing-scale` is one nobody finds.

`editor-bounds.html` carries three literal hexes (`#1F497D`, `#FFFF00`,
`#C00000`) **inside the demonstrated Word-paste payload only**, never in its
stylesheet. They are the subject of the specimen; tokenising them would make a
foreign paste look native and destroy the point. A comment above the `EDITOR`
block says so, so a future grep for hexes finds an answer.

## `--adze-col-min`

The auto-fit column floor (200px), added to `tokens/spacing.css`. It was a bare
literal in four places and had already started drifting. `admin-shell.css`'s
`.as-fieldgroup` and all twelve cards now reference it.

`.as-grid`'s `minmax(160px, 1fr)` is deliberately **not** this token — a picture
card can be narrower than the width at which a label-plus-input still reads as
one field. Different measure, different number.

## `feedback.card.html` is the one unowned card

`components/feedback/feedback.card.html` carries a valid `@dsCard` marker but has
**no generator block** — it is hand-maintained. The stated invariant of this
directory is that generating every card from one `TOKENS` string is what stops
them drifting apart, and this is the single card that can silently drift. Either
port it into `gen_cards.py` or record the exclusion deliberately. The
generator's own docstring still says "eight cards"; it writes thirteen.

## Cards added 2026-08-03

- `components/account/account.card.html` (group **Components**) — the password
  change form, the landing's account row, and the re-auth overlay. The doctrine
  it carries: a 401 mid-session must not rebuild the page, because an autosaving
  editor's status line promises the artist's words are safe while a login screen
  is removing them from the document. Generated.
- `ui_kits/content-admin/` (group **Surfaces**) — dash, content list and copy
  editor, at desktop and phone. Captured; see above. This directory was an empty
  stub from 2026-07-30 until now.
