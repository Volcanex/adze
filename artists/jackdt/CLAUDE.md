# Jack Dennison-Thompson (jackdt) — jackdt.com

Music & culture journalist. Portfolio site: home / about / writing / music.

## Writing page is GENERATED — do not hand-edit
`writing/content.md` is rebuilt from **`content.json`** (type `posts`, the source
of truth) by the generic `content_admin` feature via `templates/writing.html`
(page mode `single`). It's listed in `.generated.json`, so `/edit-page` and
Auto-Code refuse direct edits and the next publish overwrites hand edits. To
change articles, edit `content.json` or use the admin. Each post:
`{id, title, meta, excerpt, url}` — `meta` is the small-caps "Publication ·
Section · Date" line; store real unicode (“ ” · —), the renderer escapes.

The page *chrome* (fonts, masthead, footer) lives in `templates/writing.html`,
not in `content.md`. Design changes go there, then re-publish.

## Custom admin at /admin
The shared `content_admin` feature (enabled via `features` + `content_types` in
`config.json`) gives a posts editor at **jackdt.com/admin**, auth = `admin_token`.
Add/edit/delete posts, then Publish runs the framework rebuild (`render()` →
`compile.py --artist jackdt`). See `_shared/features/CLAUDE.md`. The "Advanced
editing →" link hands off to the full Adze control panel.

home / about / music are ordinary hand-authored `content.md` (not generated).

## Music page
Embeds his SoundCloud (handle **Keskesay**, `soundcloud.com/user-216694930`).
He's a journalist, not a release artist — no track uploads, no fake players.
"Keskesay" is his own SC handle, not a leaked template.

## Gotcha: never run compile.py as root on the host for this artist
Host-root compiles leave root-owned files in `output/artists/jackdt/` the
container (uid 1000) can't overwrite on the next publish (PermissionError).
Publish via the admin, or compile in-container
(`sudo docker exec adze-flask python3 compile.py --artist jackdt`). If broken:
`sudo chown -R 1000:1000 output/artists/jackdt`.
