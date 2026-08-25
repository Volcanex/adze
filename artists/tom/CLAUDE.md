# OB Stays (tom) — obstays.adze.studio (obstays.net at launch)

Tom's short-term-rental management business. Single-page marketing site:
one page (`home/`), everything else is an in-page anchor (`#plans`,
`#contact`).

**Slug is `tom`, brand is `OB Stays`** — they deliberately differ. The slug
is the client; the brand is the business. Don't "fix" one to match the other.

## Status: live on a review domain, not the real one

**https://obstays.adze.studio** — own cert (`obstays.adze.studio`, not the
shared `adze-subs` one; expanding that in place would risk `beth` and
`lastplace` on a failed renewal), vhost at
`../../nginx/sites-available/obstays.adze.studio`. DNS needed nothing:
`*.adze.studio` already has a wildcard A record at Hetzner.

`obstays.net` was still unregistered as of 2026-08-21.

**`config.json` `domain` is deliberately set to `obstays.adze.studio`, not
`obstays.net`.** `compile.py` builds canonical, `og:url`, `og:image` and
sitemap URLs from that field, so pointing it at a domain that does not
resolve means no link preview anywhere and a canonical nothing can fetch.
**At launch: register obstays.net, flip `domain` back, recompile, add the
vhost + cert, and decide whether this subdomain redirects or dies.**

The vhost adds `location = / { return 302 /home/; }` — `compile.py` writes a
meta-refresh stub at the artist root, and a bare domain landing on a refresh
stub is a poor first impression. 302 not 301 on purpose: this is temporary
and a cached permanent redirect would be a nuisance to undo.

## Where the content came from

Rebuilt from a Framer template Tom was using
(`shiny-estimate-430511.framer.app`, branded "StayPro"). Copy is carried
over near-verbatim; only the brand name changed. Two consequences:

- **The market is inconsistent, and got more so on 2026-08-22.** The proof
  stat cites *Tirana* in **$**, Law No. 7464 and the locations are *Turkey*,
  and the first testimonial is now in **£** (Tom's call: £7,000 before,
  £16,000 after, replacing the original ₺ figures). Three currencies and two
  jurisdictions on one page. Someone has to pick; the legal section and every
  number change depending on the answer.
- **Every stat and testimonial is template filler** — 68% occupancy, 3×
  uplift, "hundreds of properties", Ahmet K./Selin M./Murat & Ayşe T. None
  of it is verified. Treat as placeholder until Tom confirms.

Footer phone and address are literal "to confirm" placeholders. The email
`info@obstays.net` presumes a mailbox that does not exist yet.

The contact form `POST`s to `#` — it is **not wired to anything**. Adze has
no form handler for this artist; hook it to a lead endpoint or a mail
service before launch, or the enquiries silently go nowhere.

## Brand assets

Logo was redrawn as SVG from a raster brand board
(`/home/gabriel/uploads/WhatsApp_Image_2026-08-20_at_15.36.33.jpeg`) — the
board is an AI render (Higgsfield watermark), so its printed hex values are
unreliable (one, `#CSA4SC`, isn't valid hex). The palette in
`default-styles.css` is the corrected set, cross-checked against sampled
swatch pixels.

The lockup is generated, not hand-drawn — the geometry is measured in
multiples of the wordmark cap height, and the tagline is justified between
the left edge of "OB" and the right edge of "STAYS". Generator lives outside
this repo; if the logo needs regenerating at a different weight or spacing,
it is easier to re-derive than to hand-edit the path data.

Variants, and where each is used:

| File | Use |
|------|-----|
| `logo-primary.svg` | full lockup with tagline — print, OG images, anything large |
| `logo-wordmark.svg` | mark + "OB STAYS", no tagline — **the nav** |
| `logo-wordmark-ivory.svg` | same, reversed — **the footer** |
| `logo-mono-navy/ivory/gold.svg` | one-colour lockups incl. tagline |
| `mark.svg` | house outline alone |
| `emblem.svg`, `emblem-navy.svg` | square, house + OB nested — avatars |
| `favicon.svg` | mark only, stroke thickened 1.9× to survive 16–32px |

**Don't put the tagline lockup in the nav or footer.** At 46–62px the
tagline is sub-pixel mush; that's why the wordmark variants exist.

## Link preview (WhatsApp / iMessage / Slack)

`assets/og-share.jpg` — 1200x630, the night-villa photo under a navy wash
with a radial scrim behind the ivory lockup (the villa's lit facade is the
busiest part of the frame and "STAYS" was getting lost in it). 89KB, well
under WhatsApp's ceiling for the large card.

Wired via `seo.image` in `config.json`; `compile.py` resolves it to an
absolute URL. The `og:image:width/height/type/alt` tags are **not** emitted
by `compile.py` — they are hand-added at the top of `home/content.html`, in
the meta passthrough block that the parser lifts into `<head>`. WhatsApp
wants the dimensions to commit to the big card rather than a thumbnail.

Regenerate with the script in scratch if the photo or lockup changes; it is
a plain PIL + cairosvg composite, nothing clever.

## Motion

Deliberately restrained: one fade-and-rise per *block*, one number counter,
no parallax.

**Blocks, not elements, and no stagger.** A row of cards arrives as one
piece rather than cascading card by card, so the reveal targets are
containers (`.grid`, `.steps`, `.plans`, `.head`, `.faq`, `.statbar`) not
their children. Adding a per-element delay back in would undo the whole
effect. `.showcase` is in a separate fade-only list: it is a full-bleed
band, and translating one exposes a strip of page background above it
mid-transition.

Three decisions worth keeping:

- **Reveal uses a scroll sweep, not IntersectionObserver.** IO never
  reports an element that was jumped clean over between two frames — and
  this page's own nav links jump. That stranded ~11 elements permanently
  invisible on any anchor click. The sweep shows anything whose top is
  above `innerHeight * 0.92`, whether it was watched crossing or not.
- **The reveal removes its own classes on `transitionend`.** `.rv--in` sets
  `transform: none`, which otherwise sits at equal specificity with
  `.btn:hover`'s lift and beats it on source order — hover would silently
  stop working on any revealed button.

- **`.rv-fade` restates `opacity: 1` in its `--in` rule.** It ties with
  `.js .rv--in` on specificity and wins on source order, so without the
  restatement the showcase band sits at opacity 0 permanently. Caught only
  because the post-scroll sweep check counts invisible nodes; keep that
  check in any future edit.

Hidden state is injected from the same selector list the JS uses, before
first paint, so the list cannot drift and nothing flashes. No JS or
`prefers-reduced-motion: reduce` and everything renders in its final state.

Only the **141%** proof stat counts up. That was an explicit call: counters
on every figure read as gimmicky on a site pitching restraint.

## Copy voice

The inherited template copy scored **65.7/100 loudness** on `ganti score`
(the g-anti-ai tool), almost entirely from **21 em dashes**. Rewritten in
context rather than by swapping punctuation, plus the worst template
phrasing ("combine technology and hospitality expertise to deliver
exceptional results"). Now **5.6/100**.

**There are no em dashes in the copy. Keep it that way** — it is the single
loudest machine tell, and re-introducing a few undoes most of the gain.

Two `ganti` findings are deliberately overruled, so don't "fix" them:

- **contraction rate 1.00** vs Gabriel's 0.29. That figure is calibrated to
  *his* formal register. This is warm consumer marketing for someone else's
  business, where "you'll" and "we're" are correct; forcing 0.29 would make
  it stilted.
- **question rate 52/10k.** The FAQ section is made of questions. False
  positive by construction.

`ganti` measures against Gabriel's own corpus, so treat only its absolute
and generic tiers as binding here. The distribution tier is advice for
writing that goes out under his name.

## Icons and step numbers

No badges or discs behind either: card icons are bare 30px gold strokes,
step numbers are large Cormorant figures over a hairline rule. Both were
originally set in a filled shape and the shapes were removed on purpose.
Don't reinstate them.

**Enlarging the icons exposed three broken paths.** They are hand-drawn
inline SVG, and at 20px inside a badge the roughness didn't show. The scales
read as a blob, the cleaning "sparkle" read as a loading spinner, and the
wrench self-intersected. All three were redrawn, and Dynamic Pricing was
given a tag so it stopped duplicating the trending-up arrow already used by
"Priced Right". Round caps and joins are applied once via `.ico svg`, not
per icon, so they match the house mark.

Step figures set `font-variant-numeric: lining-nums` — Cormorant would
otherwise reach for old-style figures, and a descending 3 next to a full
height 1 looks like a mistake at that size.

## Mobile comparison table

Stacked, the two column headers are hidden and each DIY/OB pair becomes its
own bordered card, because one long alternating list makes you guess which
line answers which. Cell children run 3,4,5,6..., so `:nth-child(odd)` is
the "doing it yourself" half and `even` is "with OB Stays" — that indexing
depends on the two hidden `.compare__h` divs still being the first two
children. If you remove them, the parity flips.

Two things there that look redundant and are not:

- The container drops its border and radius on mobile. Left on, its frame
  doubled with the first cell's `border-top` just inside the rounded corner.
- `.compare__cell--us` restates its background *and* layers the tint as a
  `background-image` over white. As a plain `background` it composited
  against the sand section behind and went visibly warm, not grey.

## Gotchas

- **Assets must stay flat in `assets/`.** Flask reads `/assets/<dir>/file`
  as a *page* asset and 404s. See [../CLAUDE.md](../CLAUDE.md).
- **CSS specificity bit us once already.** `.hero p` and `.head p`
  (specificity 0,1,1) silently beat the `.eyebrow` utility (0,1,0) and broke
  the hero's type scale. Descriptive paragraphs now carry explicit classes
  (`.hero__lede`, `.head__sub`) instead of being matched by element
  selectors. Keep it that way — don't reintroduce `.section p { font-size }`.
- Fonts are **subset** variable woff2 (Latin + a few punctuation ranges,
  62KB / 98KB). The full Cormorant TTF is 1.2MB. If a glyph goes missing —
  a currency symbol, a Turkish diacritic — the subset range is why.
  `₺` (U+20BA) and `ş`/`Ş` are included.
- `scroll-margin-top` on `[id]` exists because the nav is sticky; without
  it every anchor link lands under the nav bar. `#plans` and `#contact`
  override it with `calc(101px - var(--section-pad))`, because they are
  *sections* carrying a full pad of top padding — a flat 96px offset parked
  you on empty background with the heading a screen further down. The calc
  is self-adjusting as the pad clamps down on narrow screens; don't replace
  it with a fixed number.
