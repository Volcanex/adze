# Features — Site-wide capability modules

Each `.py` file here is a feature that can be enabled for an artist site
by adding its name to `features` in the artist's `config.json`.
`flask_server._register_artist_features()` auto-discovers and loads them.

## Adding a feature

1. Create `_shared/features/<name>.py`.
2. Implement `create_blueprint(artist_slug) -> Blueprint`. The function
   receives the artist slug, must set `bp.url_prefix = ''`, and return
   the blueprint.
3. Add the feature name to the artist's `config.json` features array.
4. No changes to `flask_server.py` are needed.

## Custom artist admins

A custom admin is a per-artist `/admin` SPA on the artist's own domain. **Build
it on the `ArtistAdmin` framework in `artist_admin.py` — do not hand-roll auth
or the compile trigger, and do not copy another dashboard's skeleton.** The
framework owns the parts that must never drift between dashboards; you supply
only the data model, the render function, and the HTML.

The framework gives you, from the artist's `config.json` alone:

- **Auth** — domain guard + token (`admin.auth_required`, `admin.domain_guard`),
  so domain/token live in `config.json`, never duplicated in the module.
- **Core routes** — `register_core(html)` wires `…/panel`, `…/login`,
  `…/logout`, and `…/compile` (which runs the rebuild transaction).
- **The rebuild transaction** — `admin.rebuild()` runs your `render()`, writes
  the generated-page manifest (`.generated.json`), then compiles the artist.
  One guaranteed path: data source-of-truth → live site, so they can't drift.
- `flask_server` reads `PANEL_URL` and maps `/admin` → it for the artist's
  domain automatically (the `domain` in `config.json` must be set).

`render()` must return the list of page slugs it generates (rel to the artist
dir, posix, e.g. `'works/cormorant'`). Those pages are then **read-only** to the
dashboard editor and Terminal Access — `/edit-page` refuses direct edits to a
generated page, because the next rebuild would overwrite them. The data file is
the source of truth; the pages are derived.

Minimal pattern (see `maria_admin.py` for a complete, small example;
`rose_admin.py` / `alfie_admin.py` for richer ones):
```python
from features.artist_admin import ArtistAdmin

ARTIST_SLUG = 'example'
COOKIE = 'example_admin'
PANEL_URL = '/api/example-admin/panel'

def _render():
    # rewrite the artist's data-driven content.md from your source-of-truth file
    ...
    return ['some-page']            # generated page slugs → marked read-only

admin = ArtistAdmin(ARTIST_SLUG, COOKIE, PANEL_URL, render=_render,
                    blueprint_name='example_admin')
bp = admin.bp

admin.register_core(ADMIN_HTML)     # panel / login / logout / compile

@bp.route(f'{admin.prefix}/things', methods=['GET'])
@admin.auth_required                # your bespoke data routes
def get_things(): ...

def create_blueprint(artist_slug):
    admin.bp.url_prefix = ''
    return admin.bp
```

`compile.py` also prunes compiled output whose source page was deleted, so a
removed page stops being served — relevant to any dashboard that can delete
pages (a deleted item's source dir vanishes, the orphaned output goes with it).

## Feature vs widget

- **Widget**: embeddable content in one spot on a page. Small surface.
- **Feature**: a system spanning multiple pages or long-running state.

If you're unsure which, start with a widget.
