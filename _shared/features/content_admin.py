"""content_admin — ONE generic per-artist admin, driven by config.json.

This replaces the hand-written `*_admin.py` files. An artist opts in by adding
`"content_admin"` to `features` in their `config.json` and declaring their
content types under a `content_types` block. Everything else — the CRUD API, the
admin UI (shared shell + field-editor registry), image handling, the render step,
and the login handoff to the Adze control panel — is shared code here. No
per-artist Python.

Each content type declares its data shape and how it becomes pages:

    "content_types": {
      "works": {
        "label": "Works",
        "item": {
          "title":  {"type": "text",  "required": true, "slug_source": true},
          "year":   {"type": "text"},
          "images": {"type": "image", "multiple": true},
          "media":  {"type": "file", "multiple": true, "accept": ["video", "audio"]},
          "body":   {"type": "richtext"}
        },
        "page": {
          "mode": "per_item",           // per_item | single | none
          "parent": "works",
          "template": "templates/work.html",
          "index_template": "templates/works_index.html"
        }
      }
    }

Storage: one `content.json` at the artist root, keyed by type name. The JSON is
the source of truth; pages are always derived (rendered via the artist's own
Jinja templates), never hand-edited — the rebuild transaction (ArtistAdmin) marks
them read-only to /edit-page. `mode:"none"` skips render (client-side grids that
fetch content.json at runtime); the site still recompiles so the JSON ships.

An item is created the moment the artist opens the "new" form (POST
`<ctype>/draft`) so uploads have an id to attach to; it carries `_draft` until
its first save and is filtered out of everything published until then. Abandoned
drafts are swept on list.

Prose on the artist's *hand-authored* pages is editable through a separate,
bounded layer: elements marked `data-copy` / `data-copy-rich` in content.md are
overridable from `copy.json`, applied by compile.py. See _shared/copy_slots.py.

`page` may also carry a `config` dict, merged verbatim into the generated page's
config.json (e.g. `{"hidden": true}`) — this lets a hand-authored page keep its
config once it's converted to an editable one. A `single`-mode type with one
seeded item is the "editable copy" pattern (edit a bespoke page's prose without
touching its layout); see CLAUDE.md → "Editable copy on a hand-authored page".

See _shared/features/CLAUDE.md → "Custom artist admins" for the author guide.
"""
import json
import shutil
import time
import uuid
from pathlib import Path

from flask import request, jsonify, make_response, redirect
from werkzeug.utils import secure_filename

try:
    from features.artist_admin import ArtistAdmin, generated_pages, GENERATED_MANIFEST
    from features._common import valid_slug, slugify, unique_slug
except ImportError:  # loaded flat via importlib with _shared on sys.path
    from artist_admin import ArtistAdmin, generated_pages, GENERATED_MANIFEST
    from _common import valid_slug, slugify, unique_slug

import asset_store
import copy_slots
import shell_assets

try:
    import external_artist
except ImportError:
    external_artist = None

try:
    import jinja2
except ImportError:
    jinja2 = None


CONTENT_FILE = 'content.json'

# Shell paths, the design-language token list and its cascade order all live in
# shell_assets — the landing page mounts the same front-end, and a second copy
# of that list is how the dash and the editor come to render one stylesheet two
# ways. Don't reintroduce local constants for these; ask shell_assets for the
# vendored libs this surface loads (vendor_assets) rather than naming files.

_IMG_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'svg'}

# The `file` field type — anything the artist's pages can actually render,
# grouped by how a template has to treat it. The template dispatches on the
# stored `kind`, never on the extension: the extension is parsed once, here,
# so a page never has to carry a second copy of this table that drifts out of
# step with what uploads are accepted.
_FILE_KINDS = {
    'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'svg'},
    'video': {'mp4', 'mov', 'webm', 'm4v'},
    'audio': {'mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg'},
    'doc':   {'pdf'},
}


def _kind_for_ext(ext):
    for kind, exts in _FILE_KINDS.items():
        if ext in exts:
            return kind
    return None


def _accepted_exts(fdef):
    """The extensions one `file` field will take. `accept` lists kinds
    (`["video"]`), not extensions — an artist config should say what the field
    is for, and let this module own which containers that means today."""
    kinds = fdef.get('accept') or list(_FILE_KINDS)
    if isinstance(kinds, str):
        kinds = [kinds]
    exts = set()
    for k in kinds:
        exts |= _FILE_KINDS.get(k, set())
    return exts

# Set per-artist inside create_blueprint so flask_server can map /admin -> it.
# Safe as a module global because flask_server exec's this file fresh per artist.
PANEL_URL = None


# ── data (content.json, keyed by type) ───────────────────────────────────────
def _artist_dir(slug):
    return Path('artists') / slug


def _content_path(slug):
    return _artist_dir(slug) / CONTENT_FILE


def _load_content(slug):
    try:
        data = json.loads(_content_path(slug).read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_content(slug, data):
    _content_path(slug).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _unpublished(slug):
    """True when the artist has saved something the live site was not rebuilt
    for. The admin autosaves, so "saved" no longer implies "shipped" and the
    footer has to be able to say which.

    Derived from mtimes, never stored. A stored flag would be a second source
    of truth for something the filesystem already knows, and it is the copy
    that goes stale — a publish that dies inside compile.py would clear a flag
    while leaving the built site behind. `.generated.json` is written by
    ArtistAdmin.rebuild() as part of the same transaction, so it moves only
    when a publish actually got that far.

    Unknown counts as unpublished: an artist told "everything is live" about a
    site that isn't has no reason to press the button, which is the failure
    that matters here."""
    d = _artist_dir(slug)
    try:
        built = (d / GENERATED_MANIFEST).stat().st_mtime
    except OSError:
        return True
    newest = 0.0
    for name in (CONTENT_FILE, copy_slots.COPY_FILE):
        try:
            newest = max(newest, (d / name).stat().st_mtime)
        except OSError:
            pass
    return newest > built


def _items(slug, ctype):
    items = _load_content(slug).get(ctype, [])
    return items if isinstance(items, list) else []


def _live(items):
    """The items that may be published. An item is created the moment the
    artist opens the "new" form (so image uploads have somewhere to go) and
    carries `_draft` until its first successful save — until then it is an
    empty shell that must never reach the artist's real domain."""
    return [it for it in items if not it.get('_draft')]


def _set_items(slug, ctype, items):
    data = _load_content(slug)
    data[ctype] = items
    _save_content(slug, data)


# ── schema helpers ───────────────────────────────────────────────────────────
def _content_types(cfg):
    ct = cfg.get('content_types')
    return ct if isinstance(ct, dict) else {}


def _item_schema(type_def):
    it = type_def.get('item')
    return it if isinstance(it, dict) else {}


def _slug_field(item_schema):
    for name, f in item_schema.items():
        if isinstance(f, dict) and f.get('slug_source'):
            return name
    for name, f in item_schema.items():
        if isinstance(f, dict) and f.get('type') == 'text':
            return name
    return None


def _image_fields(item_schema):
    return {name: f for name, f in item_schema.items()
            if isinstance(f, dict) and f.get('type') == 'image'}


def _file_fields(item_schema):
    return {name: f for name, f in item_schema.items()
            if isinstance(f, dict) and f.get('type') == 'file'}


def _managed_fields(item_schema):
    """Fields whose value the SERVER owns — written only by the upload and
    delete routes, never by a JSON body. Both media types belong here: a
    plain text save that happened to carry a stale `files` array would
    otherwise silently revert an upload the artist just made."""
    d = dict(_image_fields(item_schema))
    d.update(_file_fields(item_schema))
    return d


def _normalize(value, fdef):
    """Light per-field normalisation. `format:"url"` prefixes a bare host with
    https:// (parity with the old hand-rolled link admins)."""
    if isinstance(fdef, dict) and fdef.get('format') == 'url' and isinstance(value, str):
        v = value.strip()
        if v and not v.startswith(('http://', 'https://', 'mailto:', '/', '#')):
            v = 'https://' + v
        return v
    return value


def _clean_item(body, item_schema):
    """Keep only declared, unmanaged fields from a request body (image and file
    fields are managed through the upload routes, not the JSON body)."""
    managed = _managed_fields(item_schema)
    out = {}
    for name, f in item_schema.items():
        if name in managed:
            continue
        if name in body:
            out[name] = _normalize(body[name], f)
    return out


# ── render engine (JSON -> content.md via the artist's Jinja templates) ───────
def _jinja_env(slug):
    if jinja2 is None:
        raise RuntimeError('jinja2 not available')
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(_artist_dir(slug))),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )


def _write_page(slug, rel, body_html, title, description=None, extra=None):
    d = _artist_dir(slug) / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / 'content.md').write_text(body_html, encoding='utf-8')
    page_config = {'title': title, 'slug': f'artists/{slug}/{rel}'}
    if description:
        page_config['description'] = description
    # A content type's `page.config` block passes extra keys straight through to
    # the generated page's config.json (e.g. `hidden`, `categories`). This lets a
    # hand-authored page keep its config when it's converted to an editable one.
    if isinstance(extra, dict):
        page_config.update(extra)
    (d / 'config.json').write_text(json.dumps(
        page_config, indent=2, ensure_ascii=False), encoding='utf-8')


def _prune_stale(slug, old_pages, current_pages):
    """Remove page dirs we generated on a previous rebuild but no longer generate
    (e.g. a deleted item). Only ever touches dirs listed in the prior
    .generated.json — a hand-authored sibling page the engine never created
    (a static home/, videography/, …) can never be deleted, even when a content
    type's pages live at the artist root (parent="."). This is the safety
    guarantee: publish never destroys a page it didn't make."""
    for rel in set(old_pages) - set(current_pages):
        if not rel:
            continue
        d = _artist_dir(slug) / rel
        if d.is_dir() and (d / 'content.md').exists():
            shutil.rmtree(d, ignore_errors=True)


def _norm_parent(page, ctype):
    """Parent dir for a type's pages, '' meaning the artist root (parent=".")."""
    parent = page.get('parent') or page.get('slug') or ctype
    return '' if parent in ('.', '/', '') else str(parent).strip('/')


def make_render(slug, cfg):
    """Return a zero-arg render() for ArtistAdmin.rebuild(). Regenerates every
    content type's pages from content.json and returns the generated page slugs
    (rel to the artist dir, posix) so they're marked read-only."""
    content_types = _content_types(cfg)

    def render():
        old_generated = list(generated_pages(slug))  # previous manifest, pre-rebuild
        generated = []
        content = _load_content(slug)
        env = _jinja_env(slug)
        for ctype, tdef in content_types.items():
            page = tdef.get('page') or {}
            mode = page.get('mode', 'none')
            items = content.get(ctype, [])
            if not isinstance(items, list):
                items = []
            # THE draft gate. Every published artefact below — the data feed,
            # the listing page, each per-item page, and so everything compile.py
            # derives from them (sitemap included) — comes off this one list.
            items = _live(items)
            # Every type publishes its data to a web-served location, whether or
            # not it also renders a page — a hand-authored page (a homepage
            # teaser, say) can then fetch the same items the generated page uses
            # instead of carrying a hand-copied duplicate that goes stale.
            data_file = _artist_dir(slug) / 'assets' / 'data' / f'{ctype}.json'
            data_file.parent.mkdir(parents=True, exist_ok=True)
            data_file.write_text(json.dumps(items, indent=2, ensure_ascii=False),
                                 encoding='utf-8')
            if mode == 'none':
                continue
            parent = _norm_parent(page, ctype)
            label = tdef.get('label', ctype)
            title = page.get('title', label)
            description = page.get('description')
            extra = page.get('config')

            if mode == 'single':
                if not parent:
                    continue  # a single listing page needs its own dir, not the root
                _write_page(slug, parent,
                            env.get_template(page['template']).render(
                                items=items, type=ctype, label=label, config=cfg),
                            title, description, extra)
                generated.append(parent)

            elif mode == 'per_item':
                if page.get('index_template') and parent:
                    _write_page(slug, parent,
                                env.get_template(page['index_template']).render(
                                    items=items, type=ctype, label=label, config=cfg),
                                title, description, extra)
                    generated.append(parent)
                tpl = env.get_template(page['template'])
                for it in items:
                    iid = it.get('id')
                    if not iid:
                        continue
                    rel = f'{parent}/{iid}' if parent else iid
                    _write_page(slug, rel,
                                tpl.render(item=it, type=ctype, label=label, config=cfg),
                                it.get('title', iid))
                    generated.append(rel)
        _prune_stale(slug, old_generated, generated)
        return generated

    return render


# ── blueprint / routes ───────────────────────────────────────────────────────
def _load_config(slug):
    try:
        return json.loads((_artist_dir(slug) / 'config.json').read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}


def _find(items, iid):
    for it in items:
        if it.get('id') == iid:
            return it
    return None


# ── drafts (created on open, swept if abandoned) ─────────────────────────────
DRAFT_TTL = 24 * 60 * 60


def _item_asset_rel(ctype, iid):
    """The rel dir an item's uploads live under, or None if either component
    would be rewritten by the path sanitiser (i.e. isn't safe to delete)."""
    rel = f'{ctype}/{iid}'
    return rel if iid and asset_store.safe_rel(rel) == rel else None


def _delete_item_images(slug, ctype, iid):
    rel = _item_asset_rel(ctype, iid)
    if not rel:
        return
    for base in (asset_store.assets_dir(slug), asset_store.output_dir(slug)):
        d = base / rel
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)


def _sweep_drafts(slug, ctype, items):
    """Drop drafts abandoned for more than DRAFT_TTL, with their uploads.

    This is the whole garbage collector: the admin lists a type before it can
    show anything, so listing is the one event guaranteed to happen. A draft
    whose `_draft_at` is missing or not an int is deliberately left alone —
    it never publishes, so lingering costs nothing, while deleting work in
    progress on a malformed timestamp costs the artist their afternoon.
    """
    now = int(time.time())
    keep, dropped = [], []
    for it in items:
        at = it.get('_draft_at')
        if it.get('_draft') and isinstance(at, int) and not isinstance(at, bool) \
                and now - at > DRAFT_TTL:
            dropped.append(it)
        else:
            keep.append(it)
    for it in dropped:
        _delete_item_images(slug, ctype, it.get('id'))
    return keep, bool(dropped)


# ── copy slots (data-copy / data-copy-rich in hand-authored pages) ───────────
_PAGE_SKIP = {'assets', 'widgets', 'templates', '_templates', '__pycache__',
              '.snapshots', 'backups'}


def _page_dirs(slug):
    """Every page dir under the artist (a dir with content.md + config.json),
    matching what compile.py compiles."""
    base = _artist_dir(slug)
    found = []

    def walk(d):
        for child in sorted(d.iterdir()):
            if not child.is_dir() or child.name in _PAGE_SKIP or child.name.startswith('.'):
                continue
            if (child / 'content.md').exists() and (child / 'config.json').exists():
                found.append(child)
            walk(child)

    if base.is_dir():
        walk(base)
    return found


def _page_label(key):
    return key.rsplit('/', 1)[-1].replace('-', ' ').replace('_', ' ').title()


def _scan_copy_slots(slug):
    """[(page_key, [slot, ...]), ...] read out of the artists' own content.md.
    The source is the schema — copy.json only ever overrides it."""
    if external_artist is not None and external_artist.is_remote(slug):
        # External artists live in a remote Seed repo; their local dir is a
        # config skeleton with no pages to scan. One SSH round trip per page to
        # discover nothing is not worth it — report no slots.
        return []
    base = _artist_dir(slug)
    out = []
    for d in _page_dirs(slug):
        try:
            src = (d / 'content.md').read_text(encoding='utf-8')
        except OSError:
            continue
        slots = copy_slots.find_slots(src)
        if slots:
            out.append((d.relative_to(base).as_posix(), slots))
    return out


def create_blueprint(artist_slug):
    global PANEL_URL
    slug = artist_slug
    cfg = _load_config(slug)
    content_types = _content_types(cfg)

    panel_url = f'/api/content-admin/{slug}/panel'
    PANEL_URL = panel_url
    cookie = f'{slug}_admin'

    admin = ArtistAdmin(slug, cookie, panel_url,
                        render=make_render(slug, cfg),
                        blueprint_name=f'{slug}_content')
    prefix = admin.prefix
    bp = admin.bp

    # Panel bootstrap: pulls the shared shell + field editors + vendored libs,
    # all served (single-source from _shared) under this artist's own prefix so
    # no shared/live files are touched.
    panel_html = _PANEL_BOOTSTRAP.format(
        title=f"Admin — {cfg.get('name', slug)}", prefix=prefix,
        token_links=shell_assets.token_links(prefix))
    admin.register_core(panel_html)

    # ── shared front-end assets (single source on disk, per-artist route) ─────
    _SHELL_FILES = shell_assets.shell_assets('admin-shell.js', 'field-editors.js')
    _TOKEN_ASSETS = shell_assets.token_assets()
    _VENDOR_FILES = shell_assets.vendor_assets(
        'easymde.js', 'easymde.css', 'quill.js', 'quill.css')

    @bp.route(f'{prefix}/asset/<path:name>')
    def shell_asset(name):
        entry = _SHELL_FILES.get(name)
        if entry is None and name.startswith('vendor/'):
            entry = _VENDOR_FILES.get(name[len('vendor/'):])
        if entry is None:
            entry = _TOKEN_ASSETS.get(name)
        if entry is None:
            return jsonify({'error': 'not found'}), 404
        path, ctype = entry
        try:
            body = path.read_bytes()
        except OSError:
            return jsonify({'error': 'not found'}), 404
        return body, 200, {'Content-Type': f'{ctype}; charset=utf-8',
                           'Cache-Control': 'no-cache'}

    # ── schema (drives the SPA) ───────────────────────────────────────────────
    @bp.route(f'{prefix}/schema', methods=['GET'])
    @admin.auth_required
    def get_schema():
        # `copy` decides whether the shell shows a Text section at all, so it
        # has to answer from the pages themselves, not from config.
        try:
            has_copy = bool(_scan_copy_slots(slug))
        except Exception:
            has_copy = False
        return jsonify({
            'name': cfg.get('name', slug),
            'slug': slug,
            'content_types': content_types,
            'theme': cfg.get('admin_theme', {}),
            'handoff': f'{prefix}/handoff',
            'copy': has_copy,
            # Seeds the footer on load. It has to come from the server, not
            # from what this tab happens to have typed: an artist who saves,
            # closes the tab and comes back tomorrow must still be told their
            # work isn't live.
            'unpublished': _unpublished(slug),
        })

    # ── generic CRUD, one implementation for every type ───────────────────────
    def _require_type(ctype):
        tdef = content_types.get(ctype)
        if tdef is None:
            return None, (jsonify({'error': 'unknown type'}), 404)
        return tdef, None

    @bp.route(f'{prefix}/<ctype>', methods=['GET'])
    @admin.auth_required
    def list_items(ctype):
        tdef, err = _require_type(ctype)
        if err:
            return err
        # Drafts are included — the admin has to show the artist their unsaved
        # work — and the sweep runs here, which is why a GET can write.
        items, swept = _sweep_drafts(slug, ctype, _items(slug, ctype))
        if swept:
            _set_items(slug, ctype, items)
        return jsonify(items)

    @bp.route(f'{prefix}/<ctype>/draft', methods=['POST'])
    @admin.auth_required
    def create_draft(ctype):
        """Create the item up front, before it has any content.

        Uploads land at {prefix}/<ctype>/<id>/image, so an item with no id yet
        has nowhere to put an image — which made adding pictures while creating
        impossible. The draft exists from the moment the form opens; the first
        successful PUT promotes it.
        """
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        items = _items(slug, ctype)
        # The real create derives the id from the slug_source field, which is
        # by definition empty here, so fall back to a random one. It sticks:
        # the promoting PUT does not rename the item.
        iid = unique_slug(f'draft-{uuid.uuid4().hex[:8]}',
                          [it.get('id') for it in items])
        item = {'id': iid, '_draft': True, '_draft_at': int(time.time())}
        for name, f in _managed_fields(ischema).items():
            item[name] = [] if f.get('multiple') else None
        items.append(item)
        _set_items(slug, ctype, items)
        return jsonify(item), 201

    @bp.route(f'{prefix}/<ctype>', methods=['POST'])
    @admin.auth_required
    def create_item(ctype):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        body = request.get_json(silent=True) or {}
        for name, f in ischema.items():
            if isinstance(f, dict) and f.get('required') and not str(body.get(name, '')).strip():
                return jsonify({'error': f'{name} is required'}), 400
        items = _items(slug, ctype)
        sf = _slug_field(ischema)
        base = slugify(str(body.get(sf, ''))) if sf else 'item'
        iid = unique_slug(base, [it.get('id') for it in items])
        item = _clean_item(body, ischema)
        item['id'] = iid
        for name, f in _managed_fields(ischema).items():
            item.setdefault(name, [] if f.get('multiple') else None)
        items.append(item)
        _set_items(slug, ctype, items)
        return jsonify(item), 201

    @bp.route(f'{prefix}/<ctype>/<iid>', methods=['GET'])
    @admin.auth_required
    def get_item(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        item = _find(_items(slug, ctype), iid)
        if item is None:
            return jsonify({'error': 'not found'}), 404
        return jsonify(item)

    @bp.route(f'{prefix}/<ctype>/<iid>', methods=['PUT'])
    @admin.auth_required
    def update_item(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        items = _items(slug, ctype)
        item = _find(items, iid)
        if item is None:
            return jsonify({'error': 'not found'}), 404
        item.update(_clean_item(request.get_json(silent=True) or {}, ischema))
        # A saved draft is no longer a draft: this is the only promotion path,
        # and it is what lets the item start publishing.
        item.pop('_draft', None)
        item.pop('_draft_at', None)
        _set_items(slug, ctype, items)
        return jsonify(item)

    @bp.route(f'{prefix}/<ctype>/<iid>', methods=['DELETE'])
    @admin.auth_required
    def delete_item(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        gone = _find(_items(slug, ctype), iid)
        items = [it for it in _items(slug, ctype) if it.get('id') != iid]
        _set_items(slug, ctype, items)
        # Discarding a draft is the main way one gets abandoned, so its uploads
        # go with it — otherwise the sweep only ever collects the drafts nobody
        # bothered to cancel. A real item's images are left where they are.
        if gone is not None and gone.get('_draft'):
            _delete_item_images(slug, ctype, iid)
        return jsonify(items)

    # ── image upload / removal (via asset_store tiers) ────────────────────────
    @bp.route(f'{prefix}/<ctype>/<iid>/image', methods=['POST'])
    @admin.auth_required
    def upload_item_image(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        imgs = _image_fields(ischema)
        if not imgs:
            return jsonify({'error': 'type has no image field'}), 400
        field = request.args.get('field') or next(iter(imgs))
        fdef = imgs.get(field)
        if fdef is None:
            return jsonify({'error': 'unknown image field'}), 400
        f = request.files.get('file')
        if not f or not f.filename:
            return jsonify({'error': 'no file'}), 400
        ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        if ext not in _IMG_EXTS:
            return jsonify({'error': f'unsupported image type .{ext}'}), 400
        items = _items(slug, ctype)
        item = _find(items, iid)
        if item is None:
            return jsonify({'error': 'not found'}), 404
        rel = f'{ctype}/{iid}/{secure_filename(f.filename)}'
        stored = asset_store.store_image(slug, rel, f, uploaded_by=slug)
        if not stored:
            return jsonify({'error': 'store failed'}), 500
        # 'src' stays the display tier — artist templates already consume it,
        # and 'card' is purely additive for the admin's thumbnail grid.
        entry = {'src': stored['display'], 'full': stored['full'],
                 'card': stored.get('card') or stored['display']}
        if stored.get('ar'):
            entry['ar'] = stored['ar']
            entry['aspect'] = stored['ar']  # alias some templates use
        if fdef.get('multiple'):
            item.setdefault(field, [])
            if not isinstance(item[field], list):
                item[field] = []
            item[field].append(entry)
        else:
            item[field] = entry
        _set_items(slug, ctype, items)
        return jsonify(item)

    @bp.route(f'{prefix}/<ctype>/<iid>/image', methods=['DELETE'])
    @admin.auth_required
    def delete_item_image(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        imgs = _image_fields(ischema)
        field = request.args.get('field') or (next(iter(imgs)) if imgs else None)
        idx = request.args.get('index')
        items = _items(slug, ctype)
        item = _find(items, iid)
        if item is None or field is None:
            return jsonify({'error': 'not found'}), 404
        val = item.get(field)
        if isinstance(val, list) and idx is not None:
            try:
                val.pop(int(idx))
            except (ValueError, IndexError):
                pass
        else:
            item[field] = [] if imgs.get(field, {}).get('multiple') else None
        _set_items(slug, ctype, items)
        return jsonify(item)

    # ── file upload / removal (any renderable type, via asset_store) ──────────
    # Separate from the image routes rather than folded into them: an `image`
    # field promises a raster the page can size and crop (it has tiers and an
    # aspect ratio), and half the point of a `file` field is that it does not.
    # Merging them would mean every consumer of an image field having to cope
    # with an entry that turns out to be an mp3.
    @bp.route(f'{prefix}/<ctype>/<iid>/file', methods=['POST'])
    @admin.auth_required
    def upload_item_file(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        files = _file_fields(ischema)
        if not files:
            return jsonify({'error': 'type has no file field'}), 400
        field = request.args.get('field') or next(iter(files))
        fdef = files.get(field)
        if fdef is None:
            return jsonify({'error': 'unknown file field'}), 400
        f = request.files.get('file')
        if not f or not f.filename:
            return jsonify({'error': 'no file'}), 400
        ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        if ext not in _accepted_exts(fdef):
            return jsonify({'error': f'unsupported file type .{ext}'}), 400
        items = _items(slug, ctype)
        item = _find(items, iid)
        if item is None:
            return jsonify({'error': 'not found'}), 404

        kind = _kind_for_ext(ext)
        rel = f'{ctype}/{iid}/{secure_filename(f.filename)}'
        # An image still goes through the tiered path — a photograph dropped
        # into a mixed-media field should not lose its card/display sizes just
        # because it arrived through the generic route.
        if kind == 'image':
            stored = asset_store.store_image(slug, rel, f, uploaded_by=slug)
            if not stored:
                return jsonify({'error': 'store failed'}), 500
            entry = {'src': stored['display'], 'full': stored['full'],
                     'card': stored.get('card') or stored['display']}
            if stored.get('ar'):
                entry['ar'] = stored['ar']
        else:
            saved = asset_store.store_fileobj(slug, rel, f, uploaded_by=slug)
            if not saved:
                return jsonify({'error': 'store failed'}), 500
            entry = {'src': saved, 'full': saved}
        entry['kind'] = kind
        entry['name'] = f.filename
        try:
            entry['size'] = (asset_store.assets_dir(slug) / entry['full']).stat().st_size
        except OSError:
            pass

        if fdef.get('multiple'):
            item.setdefault(field, [])
            if not isinstance(item[field], list):
                item[field] = []
            item[field].append(entry)
        else:
            item[field] = entry
        _set_items(slug, ctype, items)
        return jsonify(item)

    @bp.route(f'{prefix}/<ctype>/<iid>/file', methods=['DELETE'])
    @admin.auth_required
    def delete_item_file(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        ischema = _item_schema(tdef)
        files = _file_fields(ischema)
        field = request.args.get('field') or (next(iter(files)) if files else None)
        idx = request.args.get('index')
        items = _items(slug, ctype)
        item = _find(items, iid)
        if item is None or field is None:
            return jsonify({'error': 'not found'}), 404
        val = item.get(field)
        if isinstance(val, list) and idx is not None:
            try:
                val.pop(int(idx))
            except (ValueError, IndexError):
                pass
        else:
            item[field] = [] if files.get(field, {}).get('multiple') else None
        _set_items(slug, ctype, items)
        return jsonify(item)

    # ── copy slots (sitewide text editing) ────────────────────────────────────
    # `_copy`, not `copy`: the CRUD routes are `{prefix}/<ctype>`, and Werkzeug
    # matches a static rule ahead of the converter, so any static sibling named
    # like a content type silently steals that type's list/save. mariaslaughter
    # already has a type called `copy` (her "Home text" singleton), so
    # `{prefix}/copy` would have broken her live editor. Content-type names are
    # slugs — leading alnum — so a leading underscore cannot collide with one.
    @bp.route(f'{prefix}/_copy', methods=['GET'])
    @admin.auth_required
    def get_copy():
        store = copy_slots.load_store(_artist_dir(slug))
        pages, seen = [], {}
        for key, slots in _scan_copy_slots(slug):
            values = store.get(key) or {}
            seen[key] = {s['id'] for s in slots}
            pages.append({
                'page': key,
                'label': _page_label(key),
                'slots': [{
                    'id': s['id'],
                    'rich': s['rich'],
                    'default': s['inner'].strip() if s['rich'] else copy_slots.plain_text(s['inner']),
                    'value': values.get(s['id']),
                } for s in slots],
            })
        # An override whose element has since been renamed or deleted is
        # surfaced, never dropped: silently discarding an artist's words the
        # first time someone edits the layout is how trust in this goes.
        orphans = [{'page': page, 'id': sid}
                   for page, values in store.items()
                   for sid in values if sid not in seen.get(page, ())]
        return jsonify({'pages': pages, 'orphans': orphans})

    @bp.route(f'{prefix}/_copy', methods=['PUT'])
    @admin.auth_required
    def put_copy():
        body = request.get_json(silent=True) or {}
        rich = {page: {s['id'] for s in slots if s['rich']}
                for page, slots in _scan_copy_slots(slug)}
        store = copy_slots.load_store(_artist_dir(slug))
        for page, values in body.items():
            if not isinstance(values, dict):
                continue
            current = dict(store.get(page) or {})
            for sid, value in values.items():
                if value is None:
                    current.pop(sid, None)  # null reverts to the content.md default
                elif sid in rich.get(page, ()):
                    # The domain decides target/rel: a link to the artist's own
                    # site must not open in a new tab.
                    current[sid] = copy_slots.sanitize_rich(value, cfg.get('domain'))
                else:
                    current[sid] = str(value)
            if current:
                store[page] = current
            else:
                store.pop(page, None)
        copy_slots.save_store(_artist_dir(slug), store)
        return jsonify(store)

    # ── control-panel handoff (the "Advanced editing" link) ───────────────────
    @bp.route(f'{prefix}/handoff', methods=['GET'])
    @admin.auth_required
    def handoff():
        # Same-origin (artist's own domain): mint the control-panel session
        # cookie the dashboard expects, then redirect into it. Mirrors
        # admin_api's /login cookie so no re-auth and no token in the URL.
        is_https = request.headers.get('X-Forwarded-Proto', '') == 'https'
        resp = make_response(redirect(f'/api/adze/dashboard?slug={slug}'))
        resp.set_cookie('adze_session', f'{slug}:{admin.token()}',
                        httponly=True, samesite='Lax', secure=is_https,
                        max_age=60 * 60 * 24 * 30, path='/')
        return resp

    bp.url_prefix = ''
    return bp


# Minimal bootstrap; the real UI is the shared shell it loads.
_PANEL_BOOTSTRAP = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{prefix}/asset/vendor/easymde.css">
<link rel="stylesheet" href="{prefix}/asset/vendor/quill.css">
{token_links}
<link rel="stylesheet" href="{prefix}/asset/admin-shell.css">
</head>
<body>
<div id="adze-admin-root"></div>
<script src="{prefix}/asset/vendor/easymde.js"></script>
<script src="{prefix}/asset/vendor/quill.js"></script>
<script src="{prefix}/asset/adze-ui.js"></script>
<script src="{prefix}/asset/field-editors.js"></script>
<script src="{prefix}/asset/admin-shell.js"></script>
<script>AdminShell.init({{prefix: "{prefix}"}});</script>
</body>
</html>"""
