"""Render-engine + helper tests for the config-driven content_admin.

flask/jinja live in the adze-flask container, and tests/ isn't bind-mounted, so
pipe this file in over stdin (run from the repo root on the host):
    sudo docker exec -i -w /app adze-flask python3 - < tests/test_content_admin.py
(No pytest needed — the __main__ block runs every test_* and exits non-zero on
failure. If tests/ is later added to docker-compose mounts, `python3 -m pytest
tests/` works too.)

Each test builds a throwaway artist workspace in a temp dir and chdir's into it,
because content_admin resolves data/pages relative to cwd (Path('artists')/slug).
"""
import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from contextlib import contextmanager

sys.path.insert(0, '_shared')
sys.path.insert(0, '_shared/features')
import content_admin  # noqa: E402
from artist_admin import GENERATED_MANIFEST  # noqa: E402
from _common import slugify, unique_slug, valid_slug  # noqa: E402


@contextmanager
def workspace(slug, config, content, templates=None, extra_pages=None):
    """A temp cwd with artists/<slug>/{config.json,content.json,templates/,...}."""
    root = tempfile.mkdtemp()
    prev = os.getcwd()
    try:
        base = Path(root) / 'artists' / slug
        (base / 'templates').mkdir(parents=True)
        (base / 'config.json').write_text(json.dumps(config))
        (base / 'content.json').write_text(json.dumps(content))
        for name, body in (templates or {}).items():
            (base / 'templates' / name).write_text(body)
        for rel, body in (extra_pages or {}).items():
            d = base / rel
            d.mkdir(parents=True, exist_ok=True)
            (d / 'content.md').write_text(body)
            (d / 'config.json').write_text('{}')
        os.chdir(root)
        yield base
    finally:
        os.chdir(prev)
        shutil.rmtree(root, ignore_errors=True)


# ── _common helpers ───────────────────────────────────────────────────────────
def test_slugify_and_unique():
    assert slugify('Hello World!') == 'hello-world'
    assert slugify('  Édith / Piaf  ')  # non-empty
    assert slugify('') == 'item'
    assert unique_slug('gig', ['gig', 'gig-2']) == 'gig-3'
    assert unique_slug('gig', []) == 'gig'
    assert valid_slug('gig') and not valid_slug('-bad') and not valid_slug('a/b')


# ── render: single mode ─────────────────────────────────────────────────────────
def test_render_single():
    cfg = {'content_types': {'links': {
        'label': 'Links',
        'item': {'label': {'type': 'text', 'slug_source': True}, 'url': {'type': 'text'}},
        'page': {'mode': 'single', 'parent': 'links', 'template': 'templates/links.html'},
    }}}
    content = {'links': [{'id': 'insta', 'label': 'Insta', 'url': 'https://x'}]}
    tpl = {'links.html': '<html>{% for l in items %}<a href="{{ l.url }}">{{ l.label }}</a>{% endfor %}</html>'}
    with workspace('t', cfg, content, tpl) as base:
        gen = content_admin.make_render('t', cfg)()
        assert gen == ['links']
        out = (base / 'links' / 'content.md').read_text()
        assert '<a href="https://x">Insta</a>' in out


# ── render: per_item mode + index ────────────────────────────────────────────────
def test_render_per_item():
    cfg = {'content_types': {'works': {
        'label': 'Works',
        'item': {'title': {'type': 'text', 'slug_source': True}},
        'page': {'mode': 'per_item', 'parent': 'works',
                 'template': 'templates/work.html', 'index_template': 'templates/idx.html'},
    }}}
    content = {'works': [{'id': 'a', 'title': 'A'}, {'id': 'b', 'title': 'B'}]}
    tpl = {'work.html': '<html>{{ item.title }}</html>',
           'idx.html': '<html>{{ items|length }} works</html>'}
    with workspace('t', cfg, content, tpl) as base:
        gen = content_admin.make_render('t', cfg)()
        assert set(gen) == {'works', 'works/a', 'works/b'}
        assert (base / 'works' / 'a' / 'content.md').read_text() == '<html>A</html>'
        assert '2 works' in (base / 'works' / 'content.md').read_text()


# ── render: none mode publishes to assets/data ───────────────────────────────────
def test_render_none_publishes_data():
    cfg = {'content_types': {'works': {
        'item': {'title': {'type': 'text', 'slug_source': True}},
        'page': {'mode': 'none'},
    }}}
    content = {'works': [{'id': 'a', 'title': 'A'}]}
    with workspace('t', cfg, content) as base:
        gen = content_admin.make_render('t', cfg)()
        assert gen == []  # no pages
        data = json.loads((base / 'assets' / 'data' / 'works.json').read_text())
        assert data == [{'id': 'a', 'title': 'A'}]


# ── prune safety: never delete a page the engine didn't generate ─────────────────
def test_prune_spares_hand_authored_root_siblings():
    cfg = {'content_types': {'cat': {
        'item': {'title': {'type': 'text', 'slug_source': True}},
        'page': {'mode': 'per_item', 'parent': '.', 'template': 'templates/cat.html'},
    }}}
    tpl = {'cat.html': '<html>{{ item.title }}</html>'}
    with workspace('t', cfg, {'cat': [{'id': 'gig', 'title': 'Gig'}, {'id': 'fest', 'title': 'Fest'}]},
                   tpl, extra_pages={'home': '<html>HOME</html>'}) as base:
        g1 = content_admin.make_render('t', cfg)()
        (base / GENERATED_MANIFEST).write_text(json.dumps({'pages': g1}))
        assert (base / 'home' / 'content.md').exists()
        assert (base / 'gig').exists() and (base / 'fest').exists()
        # remove 'fest' from the data, rebuild
        (base / 'content.json').write_text(json.dumps({'cat': [{'id': 'gig', 'title': 'Gig'}]}))
        g2 = content_admin.make_render('t', cfg)()
        assert set(g2) == {'gig'}
        assert (base / 'gig').exists()          # kept
        assert not (base / 'fest').exists()     # pruned (was in manifest, now gone)
        assert (base / 'home' / 'content.md').exists()  # NEVER generated -> NEVER pruned


if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f'PASS {fn.__name__}')
        except Exception as e:
            failed += 1
            print(f'FAIL {fn.__name__}: {type(e).__name__}: {e}')
    print(f'\n{len(fns) - failed}/{len(fns)} passed')
    sys.exit(1 if failed else 0)
