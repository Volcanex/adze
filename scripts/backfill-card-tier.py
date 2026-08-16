#!/usr/bin/env python3
"""Backfill the card-tier derivative for images stored before it existed.

`asset_store.store_image` now writes a 480px `<stem>.card.<ext>` beside every
upload and content_admin records it as `card` on the image entry. Everything
uploaded before that has only a 64px thumb and a 2000px display tier, so an
admin thumbnail grid has to download the display tier — ~1MB a card, ~25MB for
Rose's 32 works. This walks each artist's content.json, generates the missing
derivative from the best source on disk, and writes `card` into the entry.

    python3 scripts/backfill-card-tier.py [--artist SLUG] [--dry-run]

Run it inside the container, where PIL and werkzeug live and files land owned by
uid 1000 (a root-owned write under output/ makes the app's next publish 500):

    sudo docker exec -w /app adze-flask python3 scripts/backfill-card-tier.py --dry-run

Idempotent: an entry whose card file is already on disk is left alone, so a
re-run only picks up what genuinely failed or is genuinely new. Entries it
cannot process are reported and skipped, never guessed at.
"""
import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)                       # asset_store resolves paths off cwd
sys.path.insert(0, str(REPO_ROOT / '_shared'))

try:
    import asset_store
except ImportError as err:
    sys.exit(f'{err}\n\nRun this inside the container:\n'
             '  sudo docker exec -w /app adze-flask python3 '
             'scripts/backfill-card-tier.py --dry-run')

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow is required to generate card derivatives.')

RASTER_EXTS = {'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'tif', 'avif'}


def image_entries(item):
    """Every image entry on an item, whatever the field is called.

    Duck-typed rather than read off the config schema: entries predating the
    current pipeline sit in fields whose declarations have since changed, and a
    dict carrying a 'src'/'full' path is unambiguous enough.
    """
    found = []
    for value in item.values():
        for candidate in (value if isinstance(value, list) else [value]):
            if not isinstance(candidate, dict):
                continue
            if isinstance(candidate.get('src'), str) or isinstance(candidate.get('full'), str):
                found.append(candidate)
    return found


def source_rel(slug, entry):
    """The best available source for a card: the canonical full file if it is
    on disk, else the display/src one. Rose's entries predate the
    `<stem>.display.<ext>` convention — hers are flat siblings like
    `work-wise-man-full.jpg` / `work-wise-man-good.jpg` — so this must go by
    what exists, not by the naming scheme."""
    assets = asset_store.assets_dir(slug)
    for key in ('full', 'src'):
        rel = entry.get(key)
        if isinstance(rel, str) and rel and (assets / rel).is_file():
            return rel
    return None


def card_rel_for(rel):
    stem, _, ext = rel.rpartition('.')
    return f'{stem}.card.{ext}' if stem else None


def plan(slug, entry):
    """(action, source_rel, card_rel) for one entry."""
    src = source_rel(slug, entry)
    if not src:
        return 'no-source', None, None
    card = card_rel_for(src)
    if not card:
        return 'no-source', src, None
    if (asset_store.assets_dir(slug) / card).is_file():
        return 'present', src, card
    ext = src.rsplit('.', 1)[-1].lower()
    if ext not in RASTER_EXTS:
        return 'unsupported', src, None
    try:
        with Image.open(asset_store.assets_dir(slug) / src) as img:
            if max(img.size) <= asset_store._CARD_MAX_PX:
                return 'small', src, None
    except Exception as err:
        print(f'    ! {src}: unreadable ({err})')
        return 'unreadable', src, None
    return 'generate', src, card


def backfill_artist(slug, dry_run):
    path = Path('artists') / slug / 'content.json'
    try:
        content = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    if not isinstance(content, dict):
        return None

    counts = {'generate': 0, 'present': 0, 'small': 0, 'unsupported': 0,
              'unreadable': 0, 'no-source': 0}
    changed = False
    generated = {}                        # source rel -> card rel, one pass each

    for ctype, items in content.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            for entry in image_entries(item):
                action, src, card = plan(slug, entry)
                counts[action] += 1
                if action == 'generate':
                    if src in generated:
                        card = generated[src]
                    elif dry_run:
                        generated[src] = card
                    else:
                        made = asset_store.make_card(slug, src)
                        if not made:
                            counts['generate'] -= 1
                            counts['unreadable'] += 1
                            print(f'    ! {src}: card generation failed')
                            continue
                        generated[src] = card = made
                elif action in ('small', 'unsupported'):
                    # No derivative is possible or worthwhile, but consumers
                    # still need a usable 'card' — fall back the same way
                    # store_image does rather than leaving the key absent.
                    card = entry.get('src') or src
                elif action != 'present':
                    continue
                if card and entry.get('card') != card:
                    entry['card'] = card
                    changed = True

    if changed and not dry_run:
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False),
                        encoding='utf-8')
    return counts, changed


def main():
    ap = argparse.ArgumentParser(description='Backfill the 480px card image tier.')
    ap.add_argument('--artist', help='only this artist slug')
    ap.add_argument('--dry-run', action='store_true',
                    help='report what would change, write nothing')
    args = ap.parse_args()

    if args.artist:
        slugs = [args.artist]
    else:
        slugs = sorted(d.name for d in Path('artists').iterdir()
                       if d.is_dir() and not d.name.startswith('_')
                       and (d / 'content.json').is_file())

    totals = {}
    touched = []
    for slug in slugs:
        result = backfill_artist(slug, args.dry_run)
        if result is None:
            print(f'{slug}: no readable content.json')
            continue
        counts, changed = result
        if not any(counts.values()):
            continue
        print(f'{slug}: ' + ', '.join(f'{k}={v}' for k, v in counts.items() if v))
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
        if changed:
            touched.append(slug)

    print('\n' + ('DRY RUN — nothing written' if args.dry_run else 'Done'))
    print('  ' + (', '.join(f'{k}={v}' for k, v in sorted(totals.items()) if v)
                  or 'no image entries found'))
    print(f'  content.json {"would change" if args.dry_run else "changed"}: '
          f'{", ".join(touched) or "none"}')


if __name__ == '__main__':
    main()
