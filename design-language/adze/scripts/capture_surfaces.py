#!/usr/bin/env python3
"""Capture the live artist-admin surfaces into ui_kits/content-admin/.

WHY A CAPTURE AND NOT A HAND-WRITTEN KIT
----------------------------------------
The dash and the content admin are not components. They are ~4,200 lines of
imperative vanilla JS that build DOM from literal `as-*`/`af-*` class strings,
and there is no component model to export. Anything hand-authored here would be
a SECOND implementation of markup that already exists — which is the failure this
whole directory is organised against (see gen_cards.py's docstring, and the four
drifted chrome `:root` blocks it was written in response to).

So the specimen is a snapshot of the real thing, taken from the running app. The
source of truth stays `_shared/shell/`; re-running this is how the kit is
updated. It is deliberately static — scripts are stripped, because a specimen
that fetches is a specimen that breaks the moment it is opened anywhere else.

Requires the adze container up and the captured artist reachable:
    python3 design-language/adze/scripts/capture_surfaces.py [--artist rose]
"""

import argparse
import asyncio
import json
import pathlib
import re

ROOT = pathlib.Path('/home/gabriel/adze')
OUT = ROOT / 'design-language/adze/ui_kits/content-admin'
TOKENS = ROOT / 'design-language/adze/tokens'
SHELL = ROOT / '_shared/shell'

# Captured from a real artist, not the sandbox. The sandbox has one empty note,
# and a specimen of an empty admin teaches nothing about the layout it exists to
# show — list density, a real artist palette, and how a form behaves once its
# fields have content in them are the whole subject.
DEFAULT_ARTIST = 'rose'

# Cascade order — the same list shell_assets.TOKEN_FILES serves, and it matters
# here for the same reason it matters there.
TOKEN_FILES = ['colors.css', 'typography.css', 'spacing.css', 'motion.css', 'base.css']

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2'
    '?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500;700&display=swap">'
)


def bundled_css():
    css = [p.read_text(encoding='utf-8') for p in (TOKENS / n for n in TOKEN_FILES)]
    css.append((SHELL / 'admin-shell.css').read_text(encoding='utf-8'))
    return '\n'.join(css)


def wrap(name, group, subtitle, title, width, body_html, root_style):
    """Standalone specimen. Line 1 must stay the @dsCard marker — that is what
    builds the index in the Design System pane."""
    # The artist's six contract vars go into :root, NOT onto the captured
    # element. Custom properties resolve where they are DECLARED, and every
    # derived token (--adze-bg-sunken, --adze-text-muted, the *-soft plates) is
    # a color-mix() declared on :root — so the same vars set on a nested node
    # leave the whole derivation chain resolving against the default palette.
    # See "The one non-obvious mechanic — .adze-theme" in ../CLAUDE.md.
    theme = (root_style or '').strip().rstrip(';')
    theme_block = f':root {{ {theme}; }}\n' if theme else ''
    return (
        f'<!-- @dsCard group="{group}" name="{name}" subtitle="{subtitle}" -->\n'
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f'<title>Adze — {title}</title>\n{FONTS}\n'
        f'<style>{bundled_css()}</style>\n'
        # The capture is a fixed-width specimen: the phone shots must keep their
        # phone measure inside whatever frame renders them, or every mobile
        # decision in here is invisible.
        '<style>\n'
        f'{theme_block}'
        f'  body {{ margin: 0; background: var(--adze-bg); }}\n'
        f'  .kit {{ width: {width}px; max-width: 100%; margin: 0 auto; }}\n'
        # Specimen-only. The live preview is sticky and viewport-tall, which is
        # right in the app and unreadable in a card frame that has no viewport —
        # it becomes an empty column the height of the screen. Static and bounded
        # here so the SPLIT is what the specimen shows, which is the part being
        # designed. The sticky behaviour is documented in ../CLAUDE.md.
        '  .as-copy-preview { position: static !important; height: 460px !important; }\n'
        '  .as-foot { position: static !important; }\n'
        '  #adze-admin-root { padding-bottom: var(--adze-space-6) !important; }\n'
        '</style>\n</head>\n<body>\n'
        f'<div class="kit"><div id="adze-admin-root">{body_html}</div></div>\n'
        '</body>\n</html>\n')


SCRIPT_RE = re.compile(r'<script\b[^>]*>.*?</script>', re.S | re.I)


async def main(artist):
    from playwright.async_api import async_playwright

    cfg = json.loads((ROOT / 'artists' / artist / 'config.json').read_text())
    token = cfg['admin_token']
    host = re.sub(r'^https?://|^www\.|/$', '', (cfg.get('domain') or '')).strip()
    base = f'http://{host}:5001'
    landing = f'/api/landing/{artist}'
    panel = f'/api/content-admin/{artist}'
    print(f'capturing {artist} ({host})')
    OUT.mkdir(parents=True, exist_ok=True)
    shots = []

    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=[f'--host-resolver-rules=MAP {host} 127.0.0.1'])

        async def grab(page):
            """The themed root's innerHTML, plus the inline style applyTheme()
            wrote onto documentElement — without those six vars every derived
            token resolves against the wrong base.

            Form state is reflected into ATTRIBUTES first. `innerHTML` serialises
            attributes, not the live value IDL property, so a captured admin
            comes out with every box blank — the fields the specimen exists to
            show are exactly the ones that vanish. This is why the first capture
            looked like an empty app."""
            # Thumbnails become data URIs. They resolve from `/assets/<src>` on
            # the artist's own domain, so in a standalone file they are broken
            # images — and "a list of visual things is a grid of pictures, which
            # requires a card-sized image tier" is one of this system's own
            # layout rules (guidelines/layout-columns.html). A picture-grid
            # specimen with no pictures argues the opposite of what it means.
            #
            # Downscaled hard on the way in. These are card thumbnails at ~200px
            # and the file has a 256 KiB ceiling in the Design System pane; the
            # budget stops one gallery-heavy artist from silently blowing it.
            await page.evaluate('''async () => {
              const MAX_W = 320, BUDGET = 90000;
              let spent = 0;
              const imgs = [...document.querySelectorAll('#adze-admin-root img')];
              for (const img of imgs) {
                if (spent > BUDGET) { img.removeAttribute('src'); continue; }
                try {
                  await img.decode();
                  const scale = Math.min(1, MAX_W / (img.naturalWidth || MAX_W));
                  const c = document.createElement('canvas');
                  c.width = Math.round((img.naturalWidth || MAX_W) * scale);
                  c.height = Math.round((img.naturalHeight || MAX_W) * scale);
                  c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                  const url = c.toDataURL('image/jpeg', 0.6);
                  spent += url.length;
                  img.setAttribute('src', url);
                } catch (e) {
                  img.removeAttribute('src');
                }
              }
            }''')
            return await page.evaluate('''() => {
              const r = document.getElementById('adze-admin-root');
              r.querySelectorAll('textarea').forEach(t => { t.textContent = t.value; });
              r.querySelectorAll('input').forEach(i => {
                if (i.type === 'checkbox' || i.type === 'radio') {
                  i.toggleAttribute('checked', i.checked);
                } else if (i.type !== 'password') {
                  i.setAttribute('value', i.value);
                }
              });
              r.querySelectorAll('select').forEach(s => {
                [...s.options].forEach(o => o.toggleAttribute('selected', o.selected));
              });
              return {html: r.innerHTML,
                      vars: document.documentElement.getAttribute('style') || ''};
            }''')

        async def surface(label, width, height, go):
            ctx = await b.new_context(viewport={'width': width, 'height': height})
            pg = await ctx.new_page()
            await pg.goto(f'{base}{landing}/panel', wait_until='networkidle')
            await pg.fill('.as-login .as-pw input', token)
            await pg.click('.as-login .as-btn')
            await pg.wait_for_selector('.as-landing', timeout=10000)
            await go(pg)
            got = await grab(pg)
            await ctx.close()
            return got

        # ── the dash ──────────────────────────────────────────────────────────
        async def just_wait(pg):
            await pg.wait_for_timeout(2000)

        # The subtitle is written HERE and nowhere else. It goes into the card's
        # @dsCard marker, and patch_manifest.py reads it straight back out of
        # that marker — so the pane's caption and the file agree by construction
        # rather than by someone remembering to update both. Say what the card
        # shows, not what it is called; the name already does that.
        for w, h, slug, sub in (
                (1280, 900, 'dash', 'Edit button first, then the numbers'),
                (390, 780, 'dash-phone', 'The same page at 390px')):
            got = await surface(slug, w, h, just_wait)
            nice = 'phone' if 'phone' in slug else 'desktop'
            shots.append((slug, 'Surfaces', sub, f'Dash ({nice})', w, got))

        # ── the content admin ─────────────────────────────────────────────────
        async def to_panel(pg, then=None):
            await pg.goto(f'{base}{panel}/panel', wait_until='networkidle')
            await pg.wait_for_selector('#as-main', timeout=10000)
            await pg.wait_for_timeout(1200)
            if then:
                await then(pg)

        async def list_view(pg):
            await to_panel(pg)

        async def copy_view(pg):
            async def click_text(p):
                el = await p.query_selector('text="Text"')
                if el:
                    await el.click()
                await p.wait_for_timeout(2200)
            await to_panel(pg, click_text)

        for w, h, slug, nice, sub, fn in (
                (1280, 900, 'content-list', 'desktop',
                 'A list of visual things is a grid of pictures', list_view),
                (1280, 900, 'copy-editor', 'desktop',
                 'Editors left, the artist’s own published page right', copy_view),
                (390, 780, 'copy-editor-phone', 'phone',
                 'The split wraps: preview on top, sticky, then the editors', copy_view)):
            got = await surface(slug, w, h, fn)
            what = 'Content list' if 'list' in slug else 'Copy editor'
            shots.append((slug, 'Surfaces', sub, f'{what} ({nice})', w, got))

        await b.close()

    for slug, group, subtitle, title, width, got in shots:
        body = SCRIPT_RE.sub('', got['html'])
        # The preview iframe points at the artist's live domain. Left in, it is a
        # cross-origin fetch from a static file and renders as a void; the split
        # then reads as a broken layout rather than a two-pane one. Replaced with
        # a stand-in that occupies the same box and says what it stands for.
        body = re.sub(
            r'<iframe\b[^>]*>\s*</iframe>',
            '<div class="as-copy-preview__frame" style="display:grid;'
            'place-items:center;background:var(--adze-bg-sunken)">'
            '<span class="as-copy-preview__note" style="border:0">'
            'the artist’s published page, live</span></div>',
            body)
        (OUT / f'{slug}.html').write_text(
            wrap(title, group, subtitle, title, width, body, got['vars']),
            encoding='utf-8')
        print('wrote', f'ui_kits/content-admin/{slug}.html',
              len((OUT / f'{slug}.html').read_text()), 'bytes')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--artist', default=DEFAULT_ARTIST,
                    help=f'artist slug to capture (default: {DEFAULT_ARTIST})')
    asyncio.run(main(ap.parse_args().artist))
