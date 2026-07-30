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

`page` may also carry a `config` dict, merged verbatim into the generated page's
config.json (e.g. `{"hidden": true}`) — this lets a hand-authored page keep its
config once it's converted to an editable one. A `single`-mode type with one
seeded item is the "editable copy" pattern (edit a bespoke page's prose without
touching its layout); see CLAUDE.md → "Editable copy on a hand-authored page".

See _shared/features/CLAUDE.md → "Custom artist admins" for the author guide.
"""
import json
import shutil
from pathlib import Path

from flask import request, jsonify, make_response, redirect
from werkzeug.utils import secure_filename

try:
    from features.artist_admin import ArtistAdmin, generated_pages
    from features._common import valid_slug, slugify, unique_slug
except ImportError:  # loaded flat via importlib with _shared on sys.path
    from artist_admin import ArtistAdmin, generated_pages
    from _common import valid_slug, slugify, unique_slug

import asset_store

try:
    import jinja2
except ImportError:
    jinja2 = None


CONTENT_FILE = 'content.json'
SHELL_DIR = Path(__file__).resolve().parent.parent / 'shell'     # _shared/shell
VENDOR_DIR = Path(__file__).resolve().parent.parent / 'vendor'   # _shared/vendor

# The Adze design language, served straight from its source tree rather than
# copied here. A second copy would drift; this way editing design-language/
# restyles every artist admin at once. Order matters — it is a cascade.
# fonts.css is deliberately NOT served: it @imports Google Fonts, which is
# render-blocking and serial inside a linked sheet. The bootstrap <head> uses
# a <link> + preconnect instead.
TOKENS_DIR = Path(__file__).resolve().parent.parent.parent / 'design-language' / 'adze' / 'tokens'
TOKEN_FILES = ['colors.css', 'typography.css', 'spacing.css', 'motion.css', 'base.css']

_IMG_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'svg'}

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


def _items(slug, ctype):
    items = _load_content(slug).get(ctype, [])
    return items if isinstance(items, list) else []


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
    """Keep only declared, non-image fields from a request body (image fields
    are managed through the upload routes, not the JSON body)."""
    imgs = _image_fields(item_schema)
    out = {}
    for name, f in item_schema.items():
        if name in imgs:
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
            if mode == 'none':
                # No page is rendered, but publish the data to a web-served
                # location so client-side grids can fetch it at runtime.
                data_file = _artist_dir(slug) / 'assets' / 'data' / f'{ctype}.json'
                data_file.parent.mkdir(parents=True, exist_ok=True)
                data_file.write_text(json.dumps(items, indent=2, ensure_ascii=False),
                                     encoding='utf-8')
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
        title=f"Admin — {cfg.get('name', slug)}", prefix=prefix)
    admin.register_core(panel_html)

    # ── shared front-end assets (single source on disk, per-artist route) ─────
    _SHELL_FILES = {
        'adze-ui.js':      (SHELL_DIR / 'adze-ui.js',      'application/javascript'),
        'admin-shell.js':  (SHELL_DIR / 'admin-shell.js',  'application/javascript'),
        'admin-shell.css': (SHELL_DIR / 'admin-shell.css', 'text/css'),
        'field-editors.js': (SHELL_DIR / 'field-editors.js', 'application/javascript'),
    }
    _TOKEN_ASSETS = {f'tokens/{n}': (TOKENS_DIR / n, 'text/css') for n in TOKEN_FILES}
    _VENDOR_FILES = {
        'easymde.js':  (VENDOR_DIR / 'easymde.min.js',  'application/javascript'),
        'easymde.css': (VENDOR_DIR / 'easymde.min.css', 'text/css'),
        'quill.js':    (VENDOR_DIR / 'quill.min.js',    'application/javascript'),
        'quill.css':   (VENDOR_DIR / 'quill.snow.css',  'text/css'),
    }

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
        return jsonify({
            'name': cfg.get('name', slug),
            'slug': slug,
            'content_types': content_types,
            'theme': cfg.get('admin_theme', {}),
            'handoff': f'{prefix}/handoff',
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
        return jsonify(_items(slug, ctype))

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
        for name in _image_fields(ischema):
            item.setdefault(name, [] if _image_fields(ischema)[name].get('multiple') else None)
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
        _set_items(slug, ctype, items)
        return jsonify(item)

    @bp.route(f'{prefix}/<ctype>/<iid>', methods=['DELETE'])
    @admin.auth_required
    def delete_item(ctype, iid):
        tdef, err = _require_type(ctype)
        if err:
            return err
        items = [it for it in _items(slug, ctype) if it.get('id') != iid]
        _set_items(slug, ctype, items)
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
        entry = {'src': stored['display'], 'full': stored['full']}
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
<link rel="stylesheet" href="{prefix}/asset/tokens/colors.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/typography.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/spacing.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/motion.css">
<link rel="stylesheet" href="{prefix}/asset/tokens/base.css">
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
