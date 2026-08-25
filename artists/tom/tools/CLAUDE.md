# tools/ — brand asset generators

Not part of the site. `compile.py` ignores this directory (it only walks
children that hold both `content.html` and `config.json`, and only copies
`assets/`), so nothing here is published.

Both scripts read from and write to `../assets/`, and depend only on what
is already in the repo — no downloads, no scratch state.

- `make-logo.py` — regenerates the whole SVG logo set. Geometry is traced
  from the brand board and expressed in multiples of the wordmark cap
  height; text is converted to outlines from the subset variable woff2 in
  `../assets/`, so the files carry no webfont dependency. Verified to
  reproduce the shipped SVGs pixel-for-pixel.
- `make-og-image.py` — regenerates `../assets/og-share.jpg`, the 1200x630
  link-preview card.

Needs `fonttools`, `brotli`, `cairosvg` and `pillow`. There is no venv here;
use one:

    python3 -m venv /tmp/obstays && /tmp/obstays/bin/pip install fonttools brotli cairosvg pillow
    /tmp/obstays/bin/python make-logo.py

**Editing the logo by hand means editing outline path data — don't.** Change
the constants at the top of `make-logo.py` and re-run.
