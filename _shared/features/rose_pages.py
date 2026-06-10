"""
Rose Jones page generator — turns information.json into the per-page content.md
files + image tiers. Driven by rose_admin's /compile endpoint so the admin is the
single source of truth.

Scope: artists/rose ONLY. Does not touch compile.py or any shared platform code.
compile.py still does the content.md -> HTML step afterwards as normal.

Image model (matches the hand-built site):
  <stem>-full.jpg  master / source of truth, never served inline
  <stem>-good.jpg  2560px display tier, q88 — the only image referenced by pages
where <stem> is the image filename without extension (e.g. work-bed).
"""

import html
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps

ROSE = Path('artists/rose')
ASSETS = ROSE / 'assets'
TPL = ROSE / '_templates'

DISPLAY_MAX = 2560
DISPLAY_Q = 88
MASTER_Q = 95

# Plain grey wireframe placeholder (faint corner-to-corner X), no text — the public
# site never announces what's missing; absent is just absent.
def _wireframe(css_class, aspect):
    diag = ('linear-gradient(to top right,transparent calc(50% - 0.5px),'
            '#e4e4e4 calc(50% - 0.5px),#e4e4e4 calc(50% + 0.5px),transparent calc(50% + 0.5px)),'
            'linear-gradient(to top left,transparent calc(50% - 0.5px),'
            '#e4e4e4 calc(50% - 0.5px),#e4e4e4 calc(50% + 0.5px),transparent calc(50% + 0.5px))')
    return (f'    <div class="{css_class}" style="aspect-ratio:{aspect};background:#f5f5f5;'
            f'border:1px solid #e6e6e6;background-image:{diag};"></div>')


MISSING_WORK_BOX = _wireframe('work-image', '4/5')
MISSING_EXH_BOX = _wireframe('exh-image', '3/2')


# ── image tiers ──────────────────────────────────────────────────────────────
def _stem(filename):
    return filename.rsplit('.', 1)[0] if filename else None


def _stems(item):
    """Image stems for a work/exhibition: prefers the `images` list, falls back to `image`."""
    if item.get('images'):
        return [_stem(x) for x in item['images'] if x]
    if item.get('image'):
        return [_stem(item['image'])]
    return []


def save_master(stem, fileobj):
    """Save an uploaded image as the full-resolution master <stem>-full.jpg
    (re-encoded JPEG, EXIF-normalised, resolution preserved) and derive the
    display tier. Returns the display filename."""
    master = ASSETS / f'{stem}-full.jpg'
    im = Image.open(fileobj)
    im = ImageOps.exif_transpose(im)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    im.save(master, 'JPEG', quality=MASTER_Q, optimize=True, progressive=True)
    ensure_display(stem)
    return f'{stem}-good.jpg'


def ensure_display(stem):
    """Make sure <stem>-good.jpg exists and is current relative to its master.
    Returns (display_filename, 'W/H') or None if no source image exists."""
    master = ASSETS / f'{stem}-full.jpg'
    good = ASSETS / f'{stem}-good.jpg'
    if not master.exists():
        # No master (e.g. legacy data). If a display already exists, use it.
        if good.exists():
            with Image.open(good) as im:
                w, h = im.size
            return good.name, f'{w}/{h}'
        return None
    if (not good.exists()) or good.stat().st_mtime < master.stat().st_mtime:
        with Image.open(master) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode != 'RGB':
                im = im.convert('RGB')
            w, h = im.size
            if max(w, h) > DISPLAY_MAX:
                s = DISPLAY_MAX / max(w, h)
                im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
            im.save(good, 'JPEG', quality=DISPLAY_Q, optimize=True, progressive=True)
    with Image.open(good) as im:
        w, h = im.size
    return good.name, f'{w}/{h}'


# ── helpers ──────────────────────────────────────────────────────────────────
def _tpl(name):
    return (TPL / name).read_text(encoding='utf-8')


def _esc(v):
    return html.escape(str(v if v is not None else ''))


def _present(v):
    return v not in (None, '') and str(v).strip() != ''


def _meta_spans(parts):
    """Spans for the present values only — no 'Unknown' fillers on the public site."""
    return ''.join(f'<span>{_esc(p)}</span>' for p in parts if _present(p))


def _detail_rows(pairs):
    """<dt>/<dd> rows for present fields only; (label, value) pairs."""
    return '\n'.join(f'        <dt>{html.escape(label)}</dt><dd>{_esc(v)}</dd>'
                     for label, v in pairs if _present(v))


def _desc_block(css_class, text):
    """The description div, or '' when there isn't one — the site shows nothing."""
    if not _present(text):
        return ''
    return f'    <div class="{css_class}">{_esc(text)}</div>'


def _all_works(info):
    """Main works list + the legacy works_new_2025 bucket, as one list."""
    works = list(info.get('works', []))
    works += list(info.get('works_new_2025', {}).get('items', []))
    return works


# ── builders ─────────────────────────────────────────────────────────────────
def build_work(work):
    tpl = _tpl('work.html')
    blocks = []
    if work.get('status') == 'live':
        for st in _stems(work):
            r = ensure_display(st)
            if not r:
                continue
            good, ar = r
            blocks.append(
                f'    <figure class="work-figure" style="aspect-ratio:{ar}">\n'
                f'        <img class="work-image" src="../../assets/{good}" '
                f'alt="{_esc(work.get("title"))}" decoding="async">\n'
                f'    </figure>'
            )
    image_block = '\n\n'.join(blocks) if blocks else MISSING_WORK_BOX
    year, medium, dims = work.get('year'), work.get('medium'), work.get('dimensions')
    return (tpl
            .replace('{{IMAGE_BLOCK}}', image_block)
            .replace('{{TITLE}}', _esc(work.get('title')))
            .replace('{{META}}', _meta_spans([year, medium, dims]))
            .replace('{{DESC_BLOCK}}', _desc_block('work-desc', work.get('description')))
            .replace('{{DETAIL_BLOCK}}',
                     _detail_rows([('Year', year), ('Medium', medium), ('Dimensions', dims)])))


def build_exhibition(exh):
    tpl = _tpl('exhibition.html')
    blocks = []
    if exh.get('status') == 'live':
        for st in _stems(exh):
            r = ensure_display(st)
            if not r:
                continue
            good, ar = r
            blocks.append(
                f'    <figure class="exh-figure" style="aspect-ratio:{ar}">\n'
                f'        <img class="exh-image" src="../../assets/{good}" '
                f'alt="{_esc(exh.get("title"))}" decoding="async">\n'
                f'    </figure>'
            )
    image_block = '\n\n'.join(blocks) if blocks else MISSING_EXH_BOX
    year, etype, loc = exh.get('year'), exh.get('type'), exh.get('location')
    return (tpl
            .replace('{{IMAGE_BLOCK}}', image_block)
            .replace('{{TITLE}}', _esc(exh.get('title')))
            .replace('{{META}}', _meta_spans([year, etype, loc]))
            .replace('{{DESC_BLOCK}}', _desc_block('exh-desc', exh.get('description')))
            .replace('{{DETAIL_BLOCK}}',
                     _detail_rows([('Year', year), ('Type', etype), ('Venue', loc)])))


def build_works_index(works):
    tpl = _tpl('works-index.html')
    years = sorted({w.get('year') for w in works if w.get('year')}, reverse=True)
    out = []
    for y in years:
        lis = []
        for w in works:
            if w.get('year') != y:
                continue
            lis.append(f'        <li><a href="/works/{w["slug"]}/">{_esc(w.get("title"))}</a></li>')
        out.append(
            f'    <div class="year-row"><div class="rule"></div><div class="year">{y}</div>'
            f'<div class="rule"></div></div>\n'
            f'    <ul class="works-list">\n' + '\n'.join(lis) + '\n    </ul>'
        )
    return tpl.replace('{{WORKS_BODY}}', '\n\n'.join(out))


def build_exhibitions_index(exhibitions):
    tpl = _tpl('exhibitions-index.html')
    # hero = first live exhibition (list order), as a blur-free display figure
    hero = ''
    for e in exhibitions:
        if e.get('status') == 'live' and _stems(e):
            r = ensure_display(_stems(e)[0])
            if r:
                good, ar = r
                alt = f'{e.get("title")}, {(e.get("type") or "").lower()}, {e.get("year") or ""}'
                hero = (f'    <figure class="image-placeholder exh-figure" style="aspect-ratio:{ar}">\n'
                        f'        <img class="exh-image" src="../assets/{good}" '
                        f'alt="{_esc(alt)}" decoding="async">\n'
                        f'    </figure>')
            break
    items = []
    for e in sorted(exhibitions, key=lambda x: -(x.get('year') or 0)):
        bits = [e.get('title')]
        if e.get('type'):
            bits.append((e.get('type') or '').lower())
        if e.get('location'):
            bits.append(e.get('location'))
        text = ', '.join(b for b in bits if b)
        items.append(
            f'        <div class="item"><a href="/exhibitions/{e["slug"]}/">'
            f'<span class="year">{_esc(e.get("year"))}</span>'
            f'<span class="title">{_esc(text)}</span></a></div>'
        )
    return tpl.replace('{{HERO}}', hero).replace('{{EXH_LIST}}', '\n'.join(items))


def build_about(info):
    tpl = _tpl('about.html')
    artist = info.get('artist', {})
    bio = artist.get('bio') or ''
    name, born = artist.get('name'), artist.get('born')
    if name and born and name in bio:
        bio = bio.replace(name, f'{name} (b. {born})', 1)
    bio = ' '.join(p for p in [bio, artist.get('statement')] if p)
    edu = '\n'.join(f'        <p>{_esc(line)}</p>' for line in artist.get('education', []))
    image_block = (
        '    <figure class="about-figure" style="aspect-ratio:4032/3024">\n'
        '        <img class="about-image" src="../assets/about-good.jpg" alt="" decoding="async">\n'
        '    </figure>'
    )
    ai = artist.get('about_image') or {}
    if ai.get('image'):
        r = ensure_display(_stem(ai['image']))
        if r:
            good, ar = r
            image_block = (
                f'    <figure class="about-figure" style="aspect-ratio:{ar}">\n'
                f'        <img class="about-image" src="../assets/{good}" alt="" decoding="async">\n'
                f'    </figure>'
            )
    return (tpl
            .replace('{{IMAGE_BLOCK}}', image_block)
            .replace('{{BIO}}', _esc(bio))
            .replace('{{EDUCATION}}', edu))


def _write_page_config(page_dir, slug_path, title, year, category):
    """compile.py only compiles a page dir that has BOTH content.md and config.json,
    so every generated page needs this written too (else new pages 404)."""
    desc = f'{title}, {year}' if year else (title or '')
    cfg = {
        'title': f'{title} — Rose Jones',
        'slug': slug_path,
        'description': desc,
        'categories': [category],
    }
    (page_dir / 'config.json').write_text(
        json.dumps(cfg, indent=4, ensure_ascii=False), encoding='utf-8')


def remove_page(kind, slug):
    """Delete a removed item's generated source dir + compiled output.
    kind is 'works' or 'exhibitions'."""
    for base in (ROSE / kind / slug, Path('output/artists/rose') / kind / slug):
        try:
            if base.exists():
                shutil.rmtree(base)
        except OSError:
            pass


# ── orchestrator ─────────────────────────────────────────────────────────────
def regenerate(info=None):
    """Regenerate every data-driven page + image tier from information.json.
    Leaves home/ and contact/ (non-data pages) untouched. Returns a summary dict."""
    if info is None:
        info = json.loads((ROSE / 'information.json').read_text(encoding='utf-8'))

    works = _all_works(info)
    exhibitions = info.get('exhibitions', [])

    for w in works:
        d = ROSE / 'works' / w['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'content.md').write_text(build_work(w), encoding='utf-8')
        _write_page_config(d, f'artists/rose/works/{w["slug"]}', w.get('title'), w.get('year'), 'work')

    for e in exhibitions:
        d = ROSE / 'exhibitions' / e['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'content.md').write_text(build_exhibition(e), encoding='utf-8')
        _write_page_config(d, f'artists/rose/exhibitions/{e["slug"]}', e.get('title'), e.get('year'), 'exhibition')

    (ROSE / 'works' / 'content.md').write_text(build_works_index(works), encoding='utf-8')
    (ROSE / 'exhibitions' / 'content.md').write_text(build_exhibitions_index(exhibitions), encoding='utf-8')
    (ROSE / 'about' / 'content.md').write_text(build_about(info), encoding='utf-8')

    return {'works': len(works), 'exhibitions': len(exhibitions)}


if __name__ == '__main__':
    print(regenerate())
