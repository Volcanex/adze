# Beth Darroch site — alignment, texture, hover, hamburger

**Decision:** Gabriel, 2026-09-23, mid-session handoff. The site
(`artists/beth/`, beth.adze.studio) had its scroll animations stripped and the
index rebuilt earlier the same day; what follows is the next round of notes,
given verbatim before the work started.

**Worktree:** not needed, this is one artist directory · **Done when** every
item under *The brief* is addressed, all four pages verified at 1600 / 1280 /
390px with no horizontal scroll and no console errors, and the mobile menu
opens **and closes** on a real phone, not just in Playwright.

---

## The brief, in Gabriel's words

> Everything needs to line up a little more though. Also I think the
> dottedness of the articles needs to be a little less obvious and maybe the
> saturate should saturate and softly glow or jpeg distort or something —
> maybe it could make them subtly move in a peggy way idk like a weird
> animation. Get creative but keep them on a grid. Have all text be black no
> grey. Hamburger still broken when opened.

> Make line thickness a touch thicker and the hamburger a touch thinner, make
> them match the text a bit more.

Reading that as seven items:

1. **Alignment.** Things should line up on a shared grid — hero against the
   card grid, meta lines against each other, the lot. This is the largest item
   and the least specified; it is a design pass, not a tweak.
2. **Halftone less obvious.** Currently `.plate::after`, a 3px radial-gradient
   dot grid at `opacity: .38`, multiplied. Take it down; do not remove it, it
   is what lets images from three publications sit together.
3. **Hover.** Today it is `saturate(1.45) contrast(1.06)` and nothing else.
   Wanted: saturation *plus* a soft glow, or JPEG-style distortion, or a small
   strange movement — "peggy", his word, read as jittery/steppy rather than
   smooth. Deliberately open. **Constraint he repeated: keep them on a grid** —
   whatever moves must not knock the layout out of alignment.
4. **All text black.** Kill the greys. `--text-muted: #5f5f5f` and
   `--text-light: #969696` in `artists/beth/default-styles.css`, used by
   `.meta`, `.card .meta`, `.hero-foot p`, `.nav-links a`, `.entry p`, the
   `.label` spans. Note `.nav-links a` uses `--text-light` for its resting
   state and `--primary` for current/hover, so that pair needs rethinking
   rather than a blind find-and-replace.
5. **Line thickness up a touch.** The hairlines: `--border`, `--border-strong`,
   `.plate` border, the `.entry` rules on About, the masthead bottom border.
   Currently all 1px. He wants them nearer the weight of the type.
6. **Hamburger thinner.** It went 1px → 3px earlier today and that overshot.
   Try 2px, judged against the 700-weight wordmark beside it.
7. **Hamburger still broken when opened.** See below — this one has history and
   is not a style question.

---

## The hamburger, in detail

Two faults were found and fixed earlier today; he reports it **still broken**,
so a third cause is live. Do not re-fix the first two.

**Already fixed, verified in Playwright at 390px:**

- The overlay was unreachable behind itself. `.nav-links` is
  `position: fixed; inset: 0` inside `.masthead`, which had
  `backdrop-filter: blur(10px)`. **A backdrop-filter makes the element a
  containing block for fixed descendants**, so `inset: 0` resolved against the
  60px masthead strip, not the window: the overlay covered a thin band, links
  overflowed off the top of the screen, and the page showed through. Fixed by
  dropping the blur under 860px (`.masthead { backdrop-filter: none }`).
- The close button sat *under* the overlay, so the menu opened and could not be
  shut. Fixed with `.menu-toggle { position: relative; z-index: 2 }` and
  `.nav-links { z-index: 1 }`.

**What is verified working (headless Chromium, 390×844, `is_mobile`):** opens,
overlay measures 390×844 against a 390×844 window, all four links on-screen,
the X is hit-testable while open, closes, a link navigates.

**So the remaining fault is something Playwright does not reproduce.** Likely
candidates, cheapest first:

- **Real Safari/iOS.** `position: sticky` ancestor with a `position: fixed`
  child is a long-standing WebKit weak spot, independent of the backdrop-filter
  issue above. The durable fix is to stop nesting the overlay inside the
  masthead at all — move `.nav-links` out to a sibling of `.masthead` in the
  markup. The masthead markup repeats in each of the four `*/content.html`
  files (it cannot be shared; see the comment at the top of `assets/site.js`),
  so that is a four-file edit.
- **Stale asset.** `site.js` is served `Cache-Control: max-age=86400` from
  `/etc/nginx/sites-enabled/adze.studio` (`expires 24h`, lines 9 and 45). The
  page HTML is `no-cache` and the CSS is inlined into it by `compile.py`, so
  CSS changes land immediately but **script changes do not**. There is a manual
  `?v=20260923b` stamp on the `site.js` reference in all four pages — bump it on
  every JS change. Confirmed the current HTML on the live site does contain the
  latest CSS fix, so if he is seeing old behaviour it is the script or his own
  cache, not the server.
- **Ask him which device and what "broken" looks like now** before guessing
  again. Two rounds have been spent on symptoms described in three words.

**Test it properly this time:** headless Chromium passing is what produced this
third report. Use a real device, or at minimum WebKit via Playwright
(`p.webkit.launch()`), not just Chromium.

---

## Where things stand

Live and compiled. Nothing in `artists/beth/` is committed — the whole site is
uncommitted work from 8 September with today's changes on top, so committing
means authoring that rebuild too. Gabriel has been told; it is his call.

**Done earlier today, do not undo:**

- Three to Be Magazine pieces added (180 Studios, Lena Dunham, Marilyn), heroes
  pulled from the articles and cropped to 900×600 webp as `art-20/21/22`.
  Writing page is 22 cards; intro reads "Twenty-two published pieces".
- All scroll reveals removed from `assets/site.js` and the CSS. `.mask` keeps
  `overflow: hidden` deliberately — an unclipped `.mask` lets anything that
  animates spill across its neighbours, which is exactly how a stale cached
  `site.js` produced the overlap he reported. The only motion left is the
  scroll hairline.
- Images are colour again (`filter: contrast(1.02)`); the greyscale is gone.
- Index and Writing run full width (`.main-content.wide`); `.sheet` is
  `repeat(auto-fill, minmax(240px, 1fr))` with the old fixed-column media
  queries deleted.
- Index leads with the latest piece beside her name (`.hero` two-column,
  `.card.featured`), dropped from the grid below so it does not repeat. Ten
  cards in the grid.
- About: paragraph spacing fixed (`.about-grid p + p` never matched, because
  each `<p>` sits in its own `.mask` wrapper — now `.mask + .mask`), bio
  reworded, to Be added to Experience.

## Working notes

- `artists/beth/default-styles.css` is the whole design system for this site;
  `compile.py` inlines it into every page. Per-page `<style>` blocks at the top
  of each `content.html` hold only that page's layout.
- Recompile after any edit: `runuser -u gabriel -- python3 compile.py --artist beth`
  from `/home/gabriel/adze`. **Never as root** — see `artists/CLAUDE.md`.
- This is a bespoke client portfolio, not a g-system consumer. The house design
  language does not apply here and should not be imposed on it: Archivo/Inter,
  its own palette, and it uses `·` separators throughout, which are banned in
  g-system but are this site's own convention.

---

## Status — 2026-09-23, second pass

All seven items done and live, plus three added mid-session: Crimson Pro as
a secondary serif (to Be's own fonts are unlicensed, so not lifted), the
hero kicker + standfirst merged into a black `.banner`, and the halftone
removed outright (Gabriel: "I don't like the grey dotted stuff").

Hamburger: overlay now built by `site.js` as a child of `<body>` (the
durable fix above), and a **third fault was found and fixed** — the scroll
lock on `html, body` made the sticky masthead, X included, jump off screen
when the menu was opened mid-page. Stamp is `?v=20260923c`. Verified in
WebKit and Chromium at iPhone 13 size: opens, X hit-testable, closes, links
navigate. **Still outstanding against Done-when: a real-phone check.**
Nothing committed.
