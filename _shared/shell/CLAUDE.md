# shell/ — the shared artist-admin front-end

The single UI behind every artist's custom admin (`content_admin`). No per-artist
markup, no build step, plain vanilla JS/CSS — served same-origin under each
artist's own admin prefix by `content_admin`'s `{prefix}/asset/<name>` route (it
reads these files fresh from disk; single source, per-artist route), mirroring the
`asset_tree.js` pattern.

- `admin-shell.js` — `window.AdminShell.init({prefix})`. Fetches `{prefix}/schema`,
  renders the login screen, a nav of the artist's content types, list/edit views
  (fields built from the registry), a Publish button, and the "Advanced editing →"
  handoff link to the Adze control panel. Applies `admin_theme` CSS vars.
- `field-editors.js` — `window.AdzeFields`, the pluggable field-type registry:
  `{type → fn(fieldName, fieldDef, value, ctx) → {el, value()}}`. Adding a new
  field type = one `register()` call; no shell/schema changes. `text/textarea/
  number/date/boolean/select/tags/image/file` are native; `markdown` → EasyMDE,
  `richtext` → Quill (the reference WYSIWYG, "ready to wire in" — no migrated
  artist uses them yet, but a schema `"type":"richtext"` field lights them up).
  Image thumbnails resolve from `/assets/<src>` (the artist domain's nginx).
- `admin-landing.js` — the landing page at `theirdomain.com/admin` (mounted by
  `../landing.py`). Five hash-routed sections; see below.
- `file-viewer.js` — `window.AdzeFileViewer`, read-only rendering of one artist
  file for the landing's Files section. Loaded by the landing only.
- `admin-shell.css` — layout and component shape only, on the **Adze design
  language** (adopted 2026-07-30). Every colour, size, radius and duration is a
  token; a literal hex in this file is a bug — the one deliberate exception is
  the QR pad's `#fff`/`#000`, which is a scanning requirement, not a colour
  choice. Per-artist palette via the six `--adze-artist-*` vars that
  `applyTheme()` sets from `config.admin_theme`.

## file-viewer.js and the `fv-` prefix

`file-viewer.js` renders one artist file for the landing page's Files section
(`admin-landing.js` owns fetching and the list; this owns "given a file, what
should the artist see"). Its classes are `fv-`, a **third** prefix under the
same contract as `as-` and `af-` below: the strings are literals in the JS and
the styles live in `admin-shell.css`, so renaming in one place silently
unstyles.

**The `content.md` renderer must track `compile.py`'s `parse_content`.** That
file is not markdown despite the extension — the compiler pulls a `<style>`
block, an `<html>` block and any `<meta>` tags before them, and ignores the
rest. The viewer splits it the same way and says what each part becomes. If the
compiler ever learns a fourth region, this is the second place to teach.

Two smaller rules, both load-bearing:

- **Copy slots are read with `DOMParser`, not a regex.** A regex would have to
  re-derive `copy_slots.py`'s masking of `<script>`/`<style>` bodies — one of
  which really does carry a `data-copy` attribute (the email widget's copy
  button). A DOMParser document is inert: no scripts run and no images fetch.
- **Line numbers are a separate `<pre>` beside the code.** highlight.js emits
  spans that run across line breaks, so splitting its output on `\n` to build
  numbered rows tears them in half. Turning wrap on hides the gutter rather
  than letting it lie about which line you are on.

Highlighting is optional: no `window.hljs` means plain text, never a blank pane.
The landing page also serves `vendor/qrcode.js` for the site QR — dark modules
on a white pad in **every** theme, because an inverted QR is one a good number
of phone cameras decline to read.

## Vendored libs are declared in shell_assets, not per surface

`shell_assets.VENDOR_FILES` maps the name an asset route serves (`quill.js`)
to the file on disk (`quill.min.js`); a surface calls `vendor_assets(...)` for
the ones it loads. Both surfaces used to hand-write their own map, which is the
same drift risk as the token list below — update a vendored file's name and one
surface 404s while the other doesn't.

## The landing page is a five-section app

`admin-landing.js` routes on the hash (`#/files/home/content.md`), so a view and
the file inside it survive a reload and answer the back button. The pill row is
`.as-nav`/`.as-tab` — the content admin's own navigation, not a second
vocabulary — and on a phone it scrolls sideways rather than wrapping onto three
lines, which would push the page's actual content below the fold.

The Files view earns the wide column through `#adze-admin-root:has(.as-files)`,
the same DOM-derived mechanism as `.as-grid` and `.as-copy-preview`. Do not
reintroduce a JS class for it: navigating away removes the node and the width
resets itself with nothing to remember.

`.as-landing > div:empty` and `.as-view > div:empty` are both `display: none`.
The landing's sections are async slots that legitimately render nothing (status
usually does), and an empty flex child still claims a gap on each side.

## "Your site" groups pages by folder; it never lists them flat

Rose's site is 48 pages — one home, four top-level, and 43 works and exhibitions
under `works/` and `exhibitions/`. As one flat row of `.as-site__page` chips
that block *was* the landing page: the four links an artist navigates by,
drowned in every artwork they had ever uploaded, with the site name repeated on
the end of each of them.

The folder is already the section, so `groupPages()` in `admin-landing.js` splits
on the first path segment. Top-level pages with no children stay chips (home
first, `404` last and quiet); each index page that has children becomes a
`.as-site__sec` rule with its child list behind a `N pages` toggle. Two targets
in that header, each labelled: the **name** opens the index page, the **count**
opens the list — one row doing both has to guess which a tap meant, and on a
phone it guesses wrong half the time. Sections open by default only when the
children total ≤ 8, so a five-page site doesn't need a click to see itself and a
forty-page one doesn't open as a wall. The header states the real total (`48 in
total`) precisely *because* the sections are collapsed — without it the card
reads as a site that has lost forty-three pages.

Children are a `repeat(auto-fill, minmax(180px, 1fr))` grid of plain links, not
chips: these are titles of wildly unequal length ("A shooting star from atop a
slide…" beside "Bed") and as pills they rag into an unscannable block.

A folder with children but no index page of its own still gets a section, headed
by the humanised folder name and not clickable
(`.as-site__secname--plain`) — those pages are live and linkable, and dropping
them because their parent isn't published would lose them from the list.

## Page titles are cleaned in `landing.py`, from the titles themselves

Page titles are written for the browser tab — `About — Rose Jones` — so a list of
them repeats the site's name down every row and buries the one word that differs.
`_site_payload` strips that tail before the payload leaves the server.

**Do not clean it against `config.json`'s `name`.** The two routinely differ: the
artist is `Rose`, the tab says `Rose Jones`; the artist is `Wild Saunas Ireland`,
the tab says `About — chris`. `_repeated_tail()` discovers the tail from the page
titles instead — the longest `<sep> …` ending shared by **two or more** of them,
a single hit being a title that merely contains a dash. `name` and the slug are
then tried as explicit tails (case-insensitively, which is what catches `— chris`)
for sites too small for a pattern to show. A title is left alone when nothing
matches, and `_clean_title` only ever uppercases a *lowercase* first letter, so
`sparrow` becomes `Sparrow` while `GOOD GRIEF` is left exactly as typed.

The home page keeps its full title in the payload (it IS the site name — trimming
it leaves an empty chip); `pageLabel()` renders it as `Home`.

## Tokens are served live, not copied

`design-language/adze/tokens/*.css` is served under `{prefix}/asset/tokens/<name>`
and linked ahead of `admin-shell.css`. There is no second copy to drift — editing
the design language restyles every artist admin on the next load. This needs
`./design-language:/app/design-language:ro` in `docker-compose.yml`; without it
the container serves a stale copy baked in at image-build time and the token
requests 404.

**The file list and its cascade order live in `../shell_assets.py`, once.** Both
mounting surfaces (`../landing.py`, `../features/content_admin.py`) import
`TOKEN_FILES`, `token_assets()` and `token_links(prefix)` from there; neither
declares its own list and neither hand-writes the `<link>` tags any more. They
each used to do both, so the order was stated four times. Since the dash and the
editor share **this** stylesheet, a sixth token added to one list and not the
other makes one file render two ways, and nothing errors. Add a token file in
`shell_assets.TOKEN_FILES` and both surfaces get it.

`fonts.css` is deliberately **not** served: it `@import`s Google Fonts, which is
render-blocking and serial inside a linked sheet. The bootstrap `<head>` uses a
`<link>` plus preconnects instead. Self-hosting Inter and JetBrains Mono under
`../vendor/fonts/` is the outstanding win — it would remove the last external
origin from the artist admin.

## Feedback helpers

`admin-shell.js` exposes the design language's feedback components as plain DOM:
`skeletonRows(n)`, `spinner(size, tone)`, `progressBar(label)`,
`emptyState(title, body, action)` and `withBusy(btn, fn)`. Use these rather than
inventing loading states.

`withBusy` is required on any async submit. It adds `is-busy`, which sets
`pointer-events: none` **synchronously** — that, not `disabled`, is what stops a
double-publish, because `disabled` set after an `await` leaves a window open.
Omit the `tone` argument for a spinner inside a filled button, so it inherits
`currentColor`; an `--adze-accent` spinner is invisible on an accent background.

## A 401 mid-session must never rebuild the page

`renderLogin()` opens with `root.innerHTML = ''`. Both shells used to call it
from their `api()` on any 401, which in the content admin deletes the form the
artist is typing into **while autosave's own status line says "your words are
still here, and this keeps trying."**

`AdzeUI.reauth({prefix, host})` is the replacement: a fixed overlay that signs
back in over the page and leaves the DOM beneath it untouched. It does not retry
the failed write — autosave's `isDirty` is still true, so the next keystroke or
flush sends it down the path that was already tested. Concurrent 401s share one
overlay; several requests failing together is the normal case.

`renderLogin()` is still right in `boot()` and after an explicit log out — there
is nothing on screen to preserve at either.

`position: fixed`, not absolute inside the root: the artist may be scrolled far
down a long form when the session ends, and an absolutely-positioned box opens
at the top of the document, behind them.

**What actually revokes a session.** `POST {prefix}/password` dual-writes
`admin_token` and calls `revoke_all_for_account`, but it also sets a fresh cookie
on its own response — so other **tabs in the same browser** pick the new cookie
up from the shared jar and never see a 401. The 401 is for another *device* or
another *browser*, and for `/reset/<token>`, which revokes without handing anyone
a new cookie. Verified both ways: same-browser second tab kept working; a second
browser context hit the overlay with its typed text intact and recovered it.

## Changing a password

`AdzeUI.passwordChangeForm({prefix, open, onDone})` — one implementation, mounted
in two places: the landing's account row (collapsed behind its own toggle) and
the content admin's Account modal (`open: true`, because the modal title already
asked). It returns `{el, focus}`.

The content admin used to carry a second, older copy — raw inputs with no reveal
toggle, inline `12px` margins, and `submit.disabled` set only *after* its await,
which is exactly the double-submit window `withBusy` exists to close. That was
the copy nobody was watching. Don't write a third.

The endpoint (`artist_admin.register_core`) has always existed on **both**
surfaces; only the landing's control was missing, so an artist's answer to "how
do I change my password" was to ask Gabriel. The form's hint says it signs you
out on your other devices because that is literally what the endpoint does.

**`.as-account__form[hidden] { display: none }` is required, not tidying.**
`display: flex` is a class selector and `[hidden]` is a UA rule, so the class
wins and `form.hidden = true` does nothing at all — the collapsed state simply
never renders. Any element given a `display` here needs the `[hidden]` line with
it. This shipped broken for one render and was caught by screenshotting it.

## The keyboard is not the URL bar (`trackViewport`)

`dvh` resolves the URL bar. Nothing in CSS resolves the software keyboard — it
doesn't change the layout viewport at all on iOS and only sometimes does on
Android.

That was a real defect in the copy editor, not a polish item. Its preview is
sized `min(46dvh, 420px)` and sticky, so on a 780px phone with a 340px keyboard
it kept ~360px and the box being typed into got a line and a half. The feature
whose whole point is seeing your words in place was covering them.

`AdzeUI.trackViewport()` (called from both shells' init) publishes two things off
`window.visualViewport`:

- `--as-vvh` — one hundredth of the **visible** height, so CSS multiplies it like
  a `vh` unit: `min(calc(46 * var(--as-vvh)), 420px)`.
- `.is-kb` on `<html>` when `innerHeight - visualViewport.height > 150`. Absolute,
  not proportional: a collapsing URL bar costs 60–120px and must not read as a
  keyboard, and a keyboard is 250px+ on the smallest phone anyone edits on.
- `.is-vv` says the measurement is real. The var-based rules are scoped to it, so
  browsers without `visualViewport` keep the plain `dvh` rules rather than
  falling back to a var that resolves to the wrong thing.

With `.is-kb` under 959px the preview collapses to `height: 0` and the fixed
footer is hidden. **Not a smaller preview — there is no size at which both fit.**
The artist is writing, not reading; the preview re-renders on the same debounce
and is back, scrolled to the slot and lit, the moment the keyboard goes down.
Height rather than `display: none` so it collapses in one transition instead of
teleporting the editors up the page mid-keystroke. The footer goes because on iOS
a fixed bar sits *behind* the keyboard (invisible, still holding its clearance)
and on Android it eats 74px of what little is left; neither is pressable while
typing.

## There is no Save button. Autosave, then Publish (2026-07-31)

**One button in this admin, and it is Publish.** Nothing else writes on a click.
Adding a Save button back to any editor is a regression, not an improvement.

The shell used to show `Save` in item forms and `Save text` in the copy view,
with `Publish changes` pinned in the footer. Two of those three read as "keep my
work" and the one that didn't was the only one always on screen. That ambiguity
already cost a real artist a page of rewrites (see the incident comment above
`COPY_PATH` in `admin-shell.js`), which was patched by making Publish flush the
copy section first. This replaces the patch with the fix.

How it works now:

- `autosave(scope, {commit, isDirty})` writes 800ms after the last keystroke and
  immediately on `focusout`, whichever lands first. `focusout` rather than
  `blur`, because blur doesn't bubble and every editor is a descendant of the
  scope — contenteditables included, so Quill needs no special case.
- `commit` returns truthy only when the server took the write, and **re-baselines
  itself** so `isDirty` goes quiet. `isDirty` is consulted before every write; an
  untouched form must never generate traffic or every tab-out would PUT.
- Writes never overlap. A change arriving mid-flight sets a flag and one more
  write runs after — coalescing, not queueing, so a fast typist costs two
  requests rather than one per keystroke.
- `mountSave` registers a handle in `live`. `flushAll()` is what Publish awaits;
  `anyUnsaved()` is what the unload guard and `leaveView()` ask.
- `resetMain()` empties `#as-main` **and** retires the handles mounted in it. Use
  it instead of `main.innerHTML = ''` — a handle whose fields are detached would
  keep voting in `anyUnsaved()` and block Publish over edits that no longer
  exist. (Getting this wrong is easy: a careless find-and-replace once rewrote
  `resetMain`'s own body into a call to itself.)
- Leaving a view flushes it. The `confirm()` is reserved for a write that was
  attempted and refused — not for the everyday "you typed and didn't click".

**The footer states whether the live site matches.** With no Save button there is
no longer a moment that means "shipped", so `.as-livenote` holds that fact, or
autosave quietly reads as published and the button stops being pressed. It is
seeded from `SCHEMA.unpublished`, which the server derives from mtimes
(`content.json`/`copy.json` against `.generated.json`) — never a stored flag, and
never client state, so it survives a reload and a publish that died halfway.

## Spacing rules that look like mistakes but aren't

Four things here will read as over-complicated on a skim. Each replaced
something that was visibly broken; don't simplify them back.

- **`.as-row`'s divider is a `::after`, not a `border-bottom`.** A bottom-only
  border on a box that also has `border-radius` curls up at both ends and
  stops short of the column edge. Repeated down a list, that artifact is what
  made the admin read as a stack of broken trays. The pseudo-element is inset
  by exactly the row's own negative margin, so the line lands flush under the
  header rule while the hover band still bleeds into the gutter.
- **`.as-pw .af-input` needs `display: block`.** An `<input>` is inline-block
  by default, so it sits on its wrapper's text baseline and leaves ~12px of
  descender space underneath — `.as-pw` measured 50px around a 38px input. The
  eye toggle is absolutely positioned at `top: 50%` of the **wrapper**, so that
  phantom space put it 6px low and it read as resting on the floor of the
  field. Any absolutely-centred adornment inside a wrapper whose only child is
  an input has this bug; kill the line box rather than nudging the offset.
- **`.as-landing > div:empty { display: none }`.** The landing's sections are
  async slots, and status renders nothing whenever there's no signal — the
  normal case. An empty flex child still claims a gap on *each* side, so it
  left a 48px hole between the numbers and the button.
- **Two gap scales on the landing, and they must differ.** `--adze-space-8`
  between major blocks, `--adze-space-4` inside `.as-data`. `.as-data` exists
  solely to own that inner rhythm: as a bare wrapper div its children stacked
  at 0px inside a 24px page rhythm — crammed inside, loose outside, which is
  the whole reason this needed doing.
- **The Edit button comes FIRST, above the numbers** (2026-07-31). People open
  `/admin` to change something; the analytics are what they read on the way
  past. Below the data block it sat under a hero, a chart and two more cards —
  on a phone, three screens of scrolling to reach the only thing they came for.
  Don't reorder it back for visual balance.
- **The control-panel link is in the account row at the foot, not under the
  button** (2026-08-03). Directly beneath the CTA it was the second item in a
  two-item menu, i.e. an alternative — and the naming fix (`as-cta__sub`) only
  ever addressed the *words*, not the position. Moving it to `.as-account`
  removes the comparison entirely: it is reachable and findable, and it is not
  offered as a choice against the thing the artist came to do. The control panel
  is deliberately an afterthought here while it stays unrefactored. The `else`
  branch is unchanged — an artist with no content admin still gets it as the
  primary button, and then there is no second link to rank it against.
- **Standalone captions start with a capital** (2026-08-24): `Published 19 days
  ago`, `Last 30 days`, `Busiest around 12am`, `Since 3 Aug`. A caption that owns
  its own line is a sentence, not a fragment — the lowercase house style belongs
  to the `.adze-label` eyebrows, and CSS already uppercases those. Fragments that
  *follow* something on the same line (`↑ 18% vs the previous 30 days`) stay
  lowercase; they are still part of that line's sentence.
- **The analytics are ONE card, not four blocks.** The count, its label, the
  delta, the sparkline, the tiles and the hourly strip are one thought. The
  count sits on a baseline row *inside* the card's body (`.as-figure`) rather
  than in a standalone `.as-hero` above it, at `--adze-text-2xl` not
  `--adze-text-display` — at display size it wraps its own label onto a second
  line and undoes the condensing. The stat tiles lost their surface and shadow
  when they moved inside: a filled, shadowed box nested in a filled, shadowed
  box reads as two competing panels, so they get a hairline top rule instead.
- **`#adze-admin-root`'s bottom padding clears the FIXED footer**, it isn't
  just page padding. At a flat `--adze-space-16` the 61px bar left 3px of air
  and the last row read as cut off.

Two related traps: **`af-textarea` is a modifier, not a field type** — it only
sets height and resize, so it must be paired with `af-input` (as
`field-editors.js` always does) or the control gets no palette and renders a
raw white box on every dark artist theme. And **one spacing owner per stack**:
`.as-feedback` uses a flex `gap`, so its `.af-field` children have their bottom
margin zeroed — otherwise the two stack and the same form runs 32px here
against 20px in the content admin.

## The class-name contract

`as-*` (shell chrome) and `af-*` (field editors) are built as literal strings in
`admin-shell.js` and `field-editors.js`. Renaming one in the CSS silently
unstyles it — change all three files or none.

Vendored libraries live in `../vendor/` (Quill, EasyMDE — JS + CSS), served via
the same `{prefix}/asset/vendor/<lib>` route. **Vendored, not CDN** — no external
hosts, works offline, reproducible. To update a lib, replace the file in
`../vendor/` (keep the filename the vendor map in `content_admin.create_blueprint`
expects).

Trust model: these are Gabriel-authored platform components, mounted **unsandboxed**
in the panel document (like the live-widget path, not the iframe preview sandbox) —
so editors get direct DOM/selection access. Don't route them through postMessage.

## Never show "Avg. visit" again without fixing the tracker first

Removed from the landing 2026-07-31. The tile was not merely imprecise, it was
**wrong by construction**:

- the injected tracker (`compile.py` `_TRACKING_SCRIPT`, and its copy in
  `flask_server.py`) measures `Date.now() - t0` from page load to `pagehide` —
  **no idle detection, no ceiling**;
- `db.upsert_session` keeps `MAX(dur)` per session id.

So one tab left open all afternoon becomes a permanent 200-minute "average
visit" for that artist, and nothing ages it out inside the 60-day window. A
number that wrong is worse than no number on a page an artist is meant to
trust.

`avg_duration` is still computed in `db.query_sessions` and still returned by
`/analytics` — only the tile is gone. Re-adding it means fixing the beacon
first (idle timeout, a sane cap, and heartbeats rather than one unload figure),
not re-adding the tile.

## Layout is derived from field role, never declared per artist (2026-07-31)

`field-editors.js` exports `role(fieldDef)` → `identity | media | short | long |
tags` (`slug_source` → identity; `image` **and `file`** → media;
textarea/markdown/richtext/copytext/copyrich → long; `tags` → tags; everything
else → short).

Because `file` is a media role, a type holding one lists as a **card grid**, and
`cardImage()` in `admin-shell.js` picks the card thumbnail. A `file` entry
carries a `kind` and most kinds are not pictures, so that function skips any
entry whose `kind` is set and isn't `image` — otherwise a videos type would put
an `.mp4` path in an `<img>` src. An `image` field's entries never carry `kind`,
so absent means image and existing content is unaffected.

`file` fields are **server-owned like images**: their editor persists through
`ctx.uploadFile`/`removeFile` immediately and their `value()` is unused. The
shell's `SERVER_OWNED` list is what keeps both out of the save body — it exists
as one list precisely so the two sites that need it can't drift apart.

**That registry is the only place that knows what a type IS; `admin-shell.js`
owns where it GOES.** A field type never decides its own width. The form order
is identity, then media (an artist should see the picture first), then all
`short` fields packed into one `.as-fieldgroup` auto-fit grid, then long, then
tags.

Two escape hatches exist and deliberately no more: per-field `"width": "full"`
(the shell adds `af-field--full`) and per-type `"list": "grid" | "rows"`.
`af-field--full` is NOT a role mapping — it means "this field opted out of the
group". field-editors never sets it and never reads `fieldDef.width`.

**Adding a multi-line field type means adding it to `role()`'s long list**, or
it silently lands in a 200px grid cell.

Editor contract: every editor returns the `.af-field` element itself and must
never reassign `wrap.className` after construction — the shell may already have
added a modifier. Use `classList` for state classes.

A type with **no `slug_source` field is a singleton** — its form IS the section,
with no list to click through. `page.mode` is not the signal: all four of
mariaslaughter's types are `mode: "single"` and three are real collections.

## Items are created as drafts, so `ctx.itemId` is always set

"+ Add" POSTs `{ctype}/draft` and awaits it *before* opening the form, and `ctx`
exposes `itemId` as a **getter** so it can never latch stale. Uploads therefore
have somewhere to go from the first second.

The image field's disabled-input branch is a defensive guard, **not** a
supported flow — do not rebuild a "save this item first" pathway. That message
was the implementation's constraint on the artist's face: it asked a painter to
describe a painting before she was allowed to show it.

A draft carries `_draft`/`_draft_at` until its first successful save. It is
visible in the admin (marked `as-draft`, titled "Unsaved draft") and excluded
from publish by `_live()` in `content_admin.py`. Drafts older than 24h are
swept on the next list fetch.

## The copy surface

`copytext` / `copyrich` edit marked runs of text on hand-authored artist pages
(`data-copy` / `data-copy-rich`; see [../../artists/CLAUDE.md](../../artists/CLAUDE.md)).
The rule: **an artist may only apply formatting the page's own CSS already
styles.**

`copyrich` is restricted at Quill's **blot registry** via
`formats: ['bold','italic','link']` — not by the toolbar, which paste bypasses —
plus an ELEMENT_NODE clipboard matcher that rebuilds pasted deltas from the
permitted attributes and drops embeds. Widening `COPY_FORMATS` is a design
decision about every artist page at once. The whitelist is per-instance and does
not affect `richtext`.

**`copyrich`'s `value()` is an INLINE FRAGMENT, never block markup** —
`inlineHtml()` maps Quill's block children to their innerHTML and joins with
`<br>`. A slot is the *inner content* of an element the artist already wrote
(`<p class="lede">`, `<li>`), so a `<p>` would both nest inside it and be
stripped by `sanitize_rich`, silently concatenating paragraphs into one line.
`<br>` is the only break in `_RICH_TAGS`; if that changes, `inlineHtml` is the
matching client half.

**Never wire `richtext` to a copy slot.** Despite the name it is the reference
WYSIWYG for *content-type* fields and returns `q.root.innerHTML`, i.e. block
markup — correct where it goes (content.json → an artist template), fatal in a
slot. Proven from one harness: `richtext` → `<p>A <strong>B</strong></p>`,
`copyrich` → `A <strong>B</strong>`. The Text view derives the editor from
`slot.rich`, so the trap is only reachable by hand-wiring.

**Escaping lives at injection, not at write.** `copy_slots.apply_overrides`
escapes plain slots when it substitutes; `put_copy` stores them raw on purpose
(store the truth, escape at render) and re-derives which slots are rich from the
artist's own markup rather than trusting the client. Moving the escape to write
time turns every copytext field into an injection vector.

The client-side href filter is a **convenience, not a security control** — the
gate is `copy_slots.sanitize_rich` on write. Don't let a doc describe it
otherwise.

Vendored Quill is **2.0.3**. `Quill.import('delta')`, `clipboard.addMatcher` and
the `formats` whitelist are 2.x behaviour. A downgrade to Quill 1 would break
the restriction silently.

## The live preview (what makes the copy editor WYSIWYG)

The Text view is a two-pane split: editors left, **the artist's own published
page in an iframe** right. It rests on three facts:

1. `data-copy` attributes survive compilation into the published HTML.
2. The admin is served on the artist's own domain, so the live page is
   **same-origin** — `contentDocument` is directly readable, no postMessage.
3. Editors already know their slot id, so mapping id → element is one
   `querySelectorAll`.

The iframe points at `/{page}/` on the current origin — **not**
`/preview/{slug}/{page}/`, because that route is Flask-served and Flask's asset
route 404s on nested `assets/<subdir>/` paths, which would silently break the
preview for any artist with subfoldered assets.

**The page is shown, never edited.** Making it contenteditable would hand back
exactly the formatting damage the bounded editor prevents.

Two things that look like mistakes:

- **The admin's theme vars do not cross into the iframe.** It is a separate
  document with the artist's own site CSS. Slot affordances injected into it
  must be built from `currentColor`, not from `--adze-*`, or they are invisible
  on an unknown palette.
- **An iframe with no CSS renders at 300×150.** `.as-copy-preview__frame` needs
  explicit `width/height: 100%` and `display: block`, and the stage owns the box
  so an overlay message occupies the same space with no reflow. This cost twenty
  minutes once: the JS was complete and correct and the feature was invisible.

`#as-main` is narrowed to form width by the `:has(.as-copy)` rule; the
`:has(.as-copy-split)` override widens it again so the *editing column* keeps
the form cap while the preview takes the remaining width. Wider viewport, more
columns — never longer lines.

## Class-name contract additions (2026-07-31)

`as-grid as-card-item as-card-item__media as-card-item__title as-card-item__meta
as-card-item__actions as-fieldgroup af-field--full as-draft as-copy
as-copy__page as-copy__page-hd as-copy__slot as-copy__path as-copy__flag
as-copy-split as-copy-pane as-copy-preview as-copy-preview__hd
as-copy-preview__name as-copy-preview__stage as-copy-preview__frame
as-copy-preview__over as-copy-preview__note as-row--leaving
as-card-item--leaving as-stagger as-main--enter as-form-head af-gallery--dropping
af-thumb--new af-copy af-copy--rich`

Added 2026-08-03: `as-reauth as-reauth__box as-reauth__title as-reauth__body
as-account as-account__item as-account__form as-account__hint`, plus `is-vv` and
`is-kb`, which go on `<html>` (not the root div) because `trackViewport` is
describing the browser window rather than the app.

`as-copy-lit` is injected into the *previewed* document, not this one.

`af-textarea` remains a modifier and must always be paired with `af-input`.

## `.as-main--enter`, not `.as-main`

The entrance animation belongs to the app *arriving*. On `.as-main` itself it
re-fired on every re-render — every save, every tab switch, every delete — so
the panel flashed while the artist was doing nothing more dramatic than fixing a
title. `admin-shell.js` adds `--enter` once, when it builds the frame.

Stagger is capped at 8 (`--as-i`): a per-row delay is lovely at six rows and
absurd at Rose's thirty-two.

## Before shipping: look at it, and check nothing is touching

The rule for anyone building or changing a custom artist admin:

**Render it and check no two things are touching.** Not read the CSS — render
it. Every spacing defect this file documents was invisible in the source and
obvious in one screenshot.

- **One spacing owner per stack.** Whatever a thing FOLLOWS supplies the gap,
  never the thing itself. `gap` on a container plus `margin-bottom` on its
  children double up; neither leaves them touching.
- **The gap is always a token** (`--adze-space-*`). A value invented at the call
  site will not agree with the same gap twenty lines away.
- **Use the design language.** If a value isn't a token, the layout is asking
  the wrong question — see `design-language/adze/SKILL.md`.

The trap to watch for, because it has now bitten twice: **a row that spaces
correctly in one context and not another.** `.as-actions` carries only
`--adze-space-1`, which is right under `.as-form` (which owns the gap beneath
itself) and wrong under `.as-copy-pane`'s card stack, which owned nothing — so
Save sat 4px under the last card and read as stuck to it. Fixed with
`.as-copy-pane > .as-actions { margin-top: var(--adze-space-6) }`, so the
distance matches the item form. Same class, same file, two outcomes: **when you
reuse a row somewhere new, re-check its gap there.**
