# Adze Design Language

The design system for adze.studio's own surfaces. **Read `readme.md` for the
character and `SKILL.md` for the operating checklist** — this file only covers
what isn't obvious from those.

Mirrored to the Claude Design project **"Adze — Design Language"**
(`22a64760-5881-46cf-abc2-8d24934ace73`). Edit here, push with `DesignSync`;
the local tree is the source of truth.

## Two gotchas when pushing to Claude Design

**Cards don't appear from the `@dsCard` marker alone.** The Design System pane
indexes `_ds_manifest.json`, which is compiled by the *app's* self-check — a
project created and populated purely over the API has no manifest, so the pane
reports "No cards yet" even though every marker is correct. After adding or
renaming a card, call `DesignSync register_assets` explicitly (paths must be in
the finalized plan's writes). Components, tokens, themes and fonts are picked
up automatically; only the cards need registering.

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

## Regenerating the specimen cards

`guidelines/*.html` and `components/*/*.card.html` are **generated**, not
hand-written:

```
python3 design-language/adze/scripts/gen_cards.py
```

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

Status colours (`success`/`warn`/`danger`) are not overridable — see the
comment in `tokens/colors.css`.
