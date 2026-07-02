# Jack Dennison-Thompson (jackdt) — jackdt.com

Music & culture journalist. Portfolio site: home / about / writing / music.

## Writing page is GENERATED — do not hand-edit
`writing/content.md` is rebuilt from **`posts.json`** (the source of truth) by
`_shared/features/jack_admin.py` → `_render()`. It is listed in
`.generated.json`, so `/edit-page` and Terminal Access refuse direct edits, and
the next publish overwrites anything written to it by hand. To change articles,
edit `posts.json` or use the dashboard. Each post: `{title, meta, excerpt, url}`
(`meta` is the small-caps "Publication · Section · Date" line; store real
unicode — “ ” — · — not HTML entities, the renderer escapes).

The page *chrome* (fonts, masthead, footer) lives in the `_PAGE_TEMPLATE` string
inside `jack_admin.py`, not in `content.md`. If the Writing design changes, edit
the template there and re-publish — editing `content.md` won't stick.

## Custom admin at /admin
Feature `jack_admin` (enabled via `features` in `config.json`) gives a posts
editor SPA at **jackdt.com/admin**, auth = `admin_token`. Add/edit/delete/drag-
reorder posts, then "Publish to site" runs the framework rebuild
(`render()` → `compile.py --artist jackdt`). Built on the shared `ArtistAdmin`
framework — see `_shared/features/CLAUDE.md`.

home / about / music are ordinary hand-authored `content.md` (not generated).

## Music page
Embeds his SoundCloud (handle **Keskesay**, `soundcloud.com/user-216694930`).
He's a journalist, not a release artist — no track uploads, no fake players.
"Keskesay" is his own SC handle, not a leaked template.

## Gotcha: never run compile.py as root on the host for this artist
Host `gabriel` is not in the `docker` group and host-root compiles leave
root-owned files in `output/artists/jackdt/` that the container (uid 1000) can't
overwrite on the next dashboard publish (PermissionError on sitemap.xml etc.).
Publish via the dashboard, or compile inside the container:
`sudo docker exec adze-flask python3 compile.py --artist jackdt`. If it's
already broken: `sudo chown -R 1000:1000 output/artists/jackdt`.
