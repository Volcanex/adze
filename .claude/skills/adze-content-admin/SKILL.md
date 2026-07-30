---
name: adze-content-admin
description: Build or restyle an artist's custom admin on adze.studio — the /admin panel on their own domain. Use when asked to "make a content admin for <artist>", give an artist an editable page, add a content type, or reskin an artist admin in the Adze design language.
---

# Give an artist a content admin

The end state: the artist visits `theirdomain.com/admin`, logs in, edits their
own content, hits Publish, and their live site rebuilds — in a panel that looks
like Adze wearing their colours.

**There is no per-artist Python.** One generic feature (`_shared/features/content_admin.py`)
is driven entirely by that artist's `config.json`. If you are writing a new
`.py` file for one artist, stop — you have taken a wrong turn.

## Read first

- `_shared/features/CLAUDE.md` — the engine: `content_types`, field types,
  `page.mode`, the rebuild transaction, the safe-pruning guarantee. **This is
  the reference; don't duplicate it here.**
- `design-language/adze/readme.md` — the design character.
- `_shared/shell/CLAUDE.md` — the shell this skill styles.

## The four steps

1. `"content_admin"` in the artist's `features` array.
2. A `content_types` block describing their content.
3. An `admin_theme` block — six colours, below.
4. Jinja templates under `artists/<slug>/templates/` for any page the admin
   generates.

Then restart: `sudo docker restart adze-flask`. Confirm the boot log says
`/admin -> /api/content-admin/<slug>/panel for <domain>`.

## The palette contract — six keys, no more

```json
"admin_theme": {
    "bg":         "#f4f3ee",
    "surface":    "#fbfaf6",
    "text":       "#0b0d1a",
    "accent":     "#1a35ff",
    "accentText": "#ffffff",
    "border":     "#c7c5bd"
}
```

Everything else — hover states, muted text, sunken panels, accent tints,
focus rings — is derived from these six by `color-mix()` in
`design-language/adze/tokens/colors.css`. That is the whole point: the artist
picks a palette, not a stylesheet.

**Rules, each of which has already caused a bug:**

- **Opaque colours only.** `rgba(255,255,255,0.15)` as a `border` makes every
  derived token semi-transparent. alfiebruce shipped with this. Convert to the
  composited hex.
- **No `font` key.** It was in the old contract and is gone. A custom face
  invalidates every line-height in the type scale and fails invisibly on that
  one artist. Type is Adze's; colour is the artist's.
- **No status colours.** `success`/`warn`/`danger` are fixed. An artist cannot
  make "Delete" look safe.
- **Pick from their site**, not from taste. Sample the real background, text
  and link colour off their live pages — the admin should feel like the back
  room of their own house.
- Check `accentText` against `accent` for contrast. It is the only pair the
  derivations can't fix for you.

If an artist has no strong palette, omit `admin_theme` entirely — the Adze
default (near-white `#fbfbfd`, blue `#1c4f82`) is deliberately the good case.

## Skinning: what you do and don't write

The shell already implements the design language. **A new artist admin needs no
CSS at all.** If you find yourself writing colours, you have misunderstood the
job.

- Layout and components: `_shared/shell/admin-shell.css`. Tokens only — no
  literal colours, no invented spacing. A hex in that file is a bug.
- Tokens are served **live from `design-language/adze/tokens/`** via the asset
  route (`TOKEN_FILES` in `content_admin.py`), not copied. Editing the design
  language restyles every artist admin at once.
- Loading states exist — use them rather than inventing spinners:
  `skeletonRows(n)`, `spinner(size, tone)`, `progressBar(label)`,
  `emptyState(title, body, action)`, and `withBusy(btn, fn)` for any async
  click. All in `admin-shell.js`.
- `withBusy` is not optional on a submit. It sets `pointer-events: none`
  *synchronously*, which is what actually prevents a double-publish; setting
  `disabled` after an `await` leaves a window open.

## Gotchas that will cost you an hour each

- **`domain_guard()`**: the panel 404s unless the request Host is the artist's
  own domain. `curl localhost` will always 404 — send `-H "Host: <domain>"`. In
  Playwright, Chromium ignores a `Host` header; launch with
  `--host-resolver-rules=MAP * 127.0.0.1:5001` instead.
- **Asset URLs must be flat.** `assets/thumb-x.jpg`, never `assets/thumbs/x.jpg`
  — Flask reads `assets/<subdir>/file` as "page asset for page `<subdir>`" and
  404s in the dashboard preview iframe while working fine in prod. Breaks only
  in preview, so it's easy to miss.
- **`design-language/` is volume-mounted read-only** (added 2026-07-30). Before
  that the container ran a stale copy baked in at image build. If tokens 404,
  check the mount before debugging the route.
- **Generated pages are read-only.** Anything in `.generated.json` is rebuilt
  from `content.json` on publish; hand edits are overwritten silently.
- **`output/` ownership**: never run `compile.py` as root on the host, or the
  container (uid 1000) can't overwrite and Publish 500s. Fix with
  `sudo chown -R 1000:1000 output/artists/<slug>`.

## Verify before claiming done

Never assert the admin works from the fact that the container restarted.

1. Panel serves: `curl -s -H "Host: <domain>" localhost:5001/api/content-admin/<slug>/panel | head`
2. Tokens serve: each of `tokens/{colors,typography,spacing,motion,base}.css` → 200.
3. Tokens *resolve* in a browser — read `getComputedStyle(document.documentElement)`
   and check `--adze-bg` equals the artist's configured `bg`. A `var()` string
   coming back means the cascade is broken.
4. Screenshot it. A palette can pass every check and still be unreadable.

`/tmp/.../verify_admin.py` from the 2026-07-30 reskin is a working template for
2–4 if it's still around; otherwise it's ~40 lines of Playwright.
