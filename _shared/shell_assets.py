"""shell_assets — the one place that knows what the artist admin shell loads.

Two surfaces mount the same front-end: the landing page (landing.py) and the
content admin (features/content_admin.py). Before this module they each carried
their own copy of the design-language token list AND hand-wrote the same five
<link> tags into their own bootstrap <head> — four independent statements of one
cascade order.

That is a live coupling risk, not a tidiness complaint. Both surfaces share
`admin-shell.css`, so adding a sixth token file to one list and not the other
makes the SAME stylesheet render differently on the dash and in the editor, with
nothing failing. Anything the shell needs is declared once, here.

Deliberately pure — no Flask import — so it stays importable from both a system
module and a feature module. `_shared/` is on sys.path (flask_server.py).
"""
from pathlib import Path

_SHARED = Path(__file__).resolve().parent

SHELL_DIR = _SHARED / 'shell'
VENDOR_DIR = _SHARED / 'vendor'

# The Adze design language, served straight from its source tree rather than
# copied here — editing design-language/ restyles every artist admin on the next
# page load, with no copy step and nothing to keep in sync. Needs
# `./design-language:/app/design-language:ro` in docker-compose.yml; without it
# the container serves a stale copy baked in at image-build time and these 404.
TOKENS_DIR = _SHARED.parent / 'design-language' / 'adze' / 'tokens'

# ORDER MATTERS — it is a cascade, and it is the reason this list is shared
# rather than copied. base.css last.
#
# fonts.css is deliberately absent: it @imports Google Fonts, which is
# render-blocking and serial inside a linked sheet. Each bootstrap <head> uses a
# <link> + preconnect instead.
TOKEN_FILES = ['colors.css', 'typography.css', 'spacing.css', 'motion.css', 'base.css']

# Front-end files shared by both surfaces. adze-ui.js must load BEFORE either
# entry point — both destructure window.AdzeUI at IIFE entry.
COMMON_SHELL_FILES = {
    'adze-ui.js': 'application/javascript',
    'admin-shell.css': 'text/css',
}


def token_assets():
    """{'tokens/<name>': (Path, mime)} for an asset route to serve."""
    return {f'tokens/{n}': (TOKENS_DIR / n, 'text/css') for n in TOKEN_FILES}


def shell_assets(*names):
    """{'<name>': (Path, mime)} for the shared shell files plus any surface's
    own entry point (passed by name, resolved in shell/)."""
    mimes = dict(COMMON_SHELL_FILES)
    for n in names:
        mimes[n] = 'text/css' if n.endswith('.css') else 'application/javascript'
    return {n: (SHELL_DIR / n, m) for n, m in mimes.items()}


# Vendored libraries, keyed by the name each surface's asset route serves them
# under (`{prefix}/asset/vendor/<key>`). Declared here for the same reason the
# token list is: both surfaces serve from one tree, and a second hand-written
# map is a second place for a filename to go stale after an update.
VENDOR_FILES = {
    'easymde.js':   ('easymde.min.js',   'application/javascript'),
    'easymde.css':  ('easymde.min.css',  'text/css'),
    'quill.js':     ('quill.min.js',     'application/javascript'),
    'quill.css':    ('quill.snow.css',   'text/css'),
    # Landing page: read-only code viewing and the site QR.
    'highlight.js': ('highlight.min.js', 'application/javascript'),
    'qrcode.js':    ('qrcode.js',        'application/javascript'),
}


def vendor_assets(*keys):
    """{'<key>': (Path, mime)} for the named vendored libs — a surface asks for
    what it loads, not for everything in vendor/."""
    return {k: (VENDOR_DIR / VENDOR_FILES[k][0], VENDOR_FILES[k][1]) for k in keys}


def token_links(prefix):
    """The token <link> tags, in cascade order, for a bootstrap <head>.

    Generated rather than hand-written in each bootstrap: a sixth token file
    must not need editing in two HTML strings that no test renders.
    """
    return '\n'.join(
        f'<link rel="stylesheet" href="{prefix}/asset/tokens/{n}">' for n in TOKEN_FILES)
