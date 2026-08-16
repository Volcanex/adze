# Maria Slaughter (mariaslaughter) — mariaslaughter.online

Gothic/revivalist site. Deliberately period-styled markup — `<font>` tags,
`<hr color>`, animated GIF borders. That is the design, not rot; don't
"modernise" it.

## Every page is generated — do not hand-edit them

All four pages (`home`, `gallery`, `links`, `music`) are listed in
`.generated.json`. They are rebuilt from `content.json` through
`templates/*.html` on every Publish, so **any edit to their `content.md`
is destroyed on the next publish.** Edit the template or the content type,
never the page.

This is the one artist where all four pages are generated, which makes her
the easiest to get wrong.

## Her editable copy already has a home — don't add copy slots

The sitewide copy editor (`data-copy` attributes, see
[../CLAUDE.md](../CLAUDE.md)) does **not** apply here, for two independent
reasons:

1. Her pages are generated (above), so the attributes wouldn't survive.
2. Her editable words already live in the `copy` content type — "Home
   text": `tagline`, `upcoming_shows`, `latest_works`, `contact_line` —
   which is editable in the content admin today. Marking her files would
   duplicate an existing admin surface onto the same words.

She was deliberately skipped when slots were rolled out to the other four
`content_admin` artists on 2026-07-31. If someone asks why she has no
Text section: this is why, and it is correct. `GET {prefix}/schema`
returns `copy: false` for her, so the section correctly does not appear.

## `copy` is a singleton, and that is derived not declared

`copy` has no field carrying `slug_source`, which is what marks a content
type as a singleton — there is nothing to name a second item after. The
admin therefore opens its form directly instead of showing a
one-row list to click through.

Note that `page.mode` is **not** the singleton signal: all four of her
types are `mode: "single"` (one output page each) but `gallery`, `music`
and `links` carry a `slug_source` and are real collections. Only `copy`
is a singleton. Getting this backwards turns her gallery into a form.

## Content types

| Type | Label | Items | Shape |
|------|-------|-------|-------|
| `copy` | Home text | 1 | singleton — four text fields |
| `gallery` | — | 24 | collection, has `image` |
| `music` | — | 4 | collection, has `image` |
| `links` | — | 1 | collection (has `slug_source`), currently one item |

`links` having a single item does **not** make it a singleton — it has a
`slug_source`, so it is a collection that happens to be short. It will
correctly show a list.
