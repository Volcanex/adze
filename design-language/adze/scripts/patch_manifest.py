#!/usr/bin/env python3
"""Rebuild the `cards` array of a fetched _ds_manifest.json from the local
`@dsCard` markers.

WHY THIS EXISTS
---------------
The Design System pane indexes `_ds_manifest.json`, and only the claude.ai app's
own self-check writes that file. Nothing done over the `DesignSync` API runs the
self-check, so a card uploaded through the API never appears in the pane however
correct its marker is. `register_assets` does not fix it either — tested
2026-08-03, it reported `registered: 9` and none of them showed; it writes a
legacy index the pane no longer reads.

So the manifest has to be patched by hand, and this does it from the one source
that is already authoritative: line 1 of every card file.

USAGE
    # 1. DesignSync get_file -> _ds_manifest.json, save it as fetched.json
    python3 scripts/patch_manifest.py fetched.json patched.json
    # 2. DesignSync finalize_plan (writes: _ds_manifest.json) -> write_files

Everything except `cards` is passed through untouched, and that matters:
`tokens`, `themes`, `brandFonts`, `components` and `globalCssPaths` are derived
by the app from the CSS, and this file exists ONLY remotely — there is no local
copy to restore them from if they are dropped. The section-length check below is
there to make a lossy edit loud instead of silent.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Line 1 of every card: <!-- @dsCard group="…" name="…" subtitle="…" -->
MARKER = re.compile(r'<!--\s*@dsCard\s+(.*?)-->')
ATTR = re.compile(r'(\w+)="([^"]*)"')

# Card groups appear in the pane in this order; anything unlisted sorts last.
GROUP_ORDER = ['Colour', 'Type', 'Layout', 'Motion', 'Components', 'Feedback',
               'Surfaces']


def local_cards():
    """Every marked card under the design language, as manifest entries."""
    found = []
    for path in sorted(ROOT.rglob('*.html')):
        rel = path.relative_to(ROOT).as_posix()
        first = path.read_text(encoding='utf-8').split('\n', 1)[0]
        m = MARKER.search(first)
        if not m:
            continue
        a = dict(ATTR.findall(m.group(1)))
        if not a.get('name'):
            print(f'  ! {rel}: @dsCard with no name= — skipped')
            continue
        found.append({'path': rel, 'group': a.get('group') or 'Components',
                      'subtitle': a.get('subtitle', ''), 'name': a['name']})
    key = {g: i for i, g in enumerate(GROUP_ORDER)}
    found.sort(key=lambda c: (key.get(c['group'], len(GROUP_ORDER)), c['name']))
    return found


def main(src, out):
    m = json.loads(pathlib.Path(src).read_text())
    before = {k: len(v) for k, v in m.items() if isinstance(v, list)}
    was = {c['path'] for c in m.get('cards', [])}

    cards = local_cards()
    m['cards'] = cards
    now = {c['path'] for c in cards}

    pathlib.Path(out).write_text(json.dumps(m, ensure_ascii=False), encoding='utf-8')

    print(f'cards: {len(was)} -> {len(cards)}')
    for p in sorted(now - was):
        print(f'  + {p}')
    for p in sorted(was - now):
        print(f'  - {p}   (no @dsCard marker found locally — verify this is intended)')
    print('groups:', ', '.join(dict.fromkeys(c['group'] for c in cards)))
    # Everything that is NOT cards must come through unchanged. A dropped
    # `tokens` array cannot be regenerated from anything on disk.
    for k, n in before.items():
        if k == 'cards':
            continue
        after = len(m.get(k, []))
        flag = '' if after == n else '   <-- CHANGED, DO NOT UPLOAD'
        print(f'  {k}: {n} -> {after}{flag}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
