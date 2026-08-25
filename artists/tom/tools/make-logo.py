"""Generate the OB STAYS logo set as clean, self-contained SVG.

Geometry is traced from the brand board; proportions are measured from it
and expressed in multiples of the wordmark cap height, so the whole lockup
scales from one number. Text is converted to outlines, so the files render
identically anywhere with no webfont dependency.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "assets")
os.makedirs(OUT, exist_ok=True)

NAVY = "#0B1F3A"
GOLD = "#C8A45C"
IVORY = "#F7F4ED"
SOFT_NAVY = "#253855"

TAGLINE = "PREMIUM VILLAS & PROPERTY MANAGEMENT"

# ---- the mark: an open house outline, one stroke, round caps and joins.
MARK_D = "M85 27.5 L52.5 2 L2.5 46.5 L14.5 46.5 L14.5 101.5 L131 101.5"
MARK_VB_W, MARK_VB_H = 133.5, 103.5
MARK_SW = 4.0

# ---- proportions measured off the board, in units of the wordmark cap height
MARK_W = 4.433     # mark width
MARK_H = 3.433     # mark height
BASELINE = 2.533   # wordmark baseline, from the mark's apex
OB_X = 1.432       # left edge of 'OB'
OB_W = 2.300       # tracked width of 'OB'
ST_X = 4.699       # left edge of 'STAYS'
ST_W = 4.468       # tracked width of 'STAYS'
# The tagline is justified between the left edge of 'OB' and the right edge of
# 'STAYS' -- that is the rule on the board, not a coincidence of two numbers.
TAG_X = OB_X
TAG_W = (ST_X + ST_W) - OB_X
TAG_BASE = 3.033   # tagline baseline
TAG_CAP = 0.222    # tagline cap height


ASSETS = os.path.join(HERE, os.pardir, "assets")


def load(path, **axes):
    """Read the subset variable woff2 that ships with the site, so this
    script needs nothing that isn't already in the repo."""
    f = TTFont(os.path.join(ASSETS, path))
    return instancer.instantiateVariableFont(f, axes, inplace=False) if axes else f


class Typesetter:
    def __init__(self, font):
        self.font = font
        self.upem = font["head"].unitsPerEm
        self.gs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.hmtx = font["hmtx"]
        self.cap = getattr(font["OS/2"], "sCapHeight", None) or int(0.7 * self.upem)

    def _adv(self, text, size, tracking):
        """Ink-to-ink advance width: n-1 tracking gaps, not n."""
        scale = size / self.cap
        w = sum(self.hmtx[self.cmap[ord(c)]][0] for c in text)
        return (w + tracking * self.upem * (len(text) - 1)) * scale

    def tracking_for(self, text, size, target_w):
        """Solve the letterspacing that makes `text` exactly `target_w` wide."""
        lo, hi = -0.2, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if self._adv(text, size, mid) < target_w:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def path(self, text, size, tracking, x, y):
        scale = size / self.cap
        pen_x, parts = 0.0, []
        for ch in text:
            gn = self.cmap[ord(ch)]
            spen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}")
            self.gs[gn].draw(spen)
            d = spen.getCommands()
            if d:
                parts.append(
                    f'<g transform="translate({x + pen_x * scale:.2f} {y:.2f}) '
                    f'scale({scale:.6f} {-scale:.6f})"><path d="{d}"/></g>'
                )
            pen_x += self.hmtx[gn][0] + tracking * self.upem
        return "".join(parts)


cor = Typesetter(load("CormorantGaramond-Variable.woff2", wght=400))
inter = Typesetter(load("Inter-Variable.woff2", wght=500, opsz=14))


def mark_group(color, x, y, w):
    s = w / MARK_VB_W
    return (
        f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">'
        f'<path d="{MARK_D}" fill="none" stroke="{color}" stroke-width="{MARK_SW}" '
        f'stroke-linecap="round" stroke-linejoin="round"/></g>'
    )


def svg(w, h, body, bg=None):
    b = f'<rect width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
        f'width="{w:.2f}" height="{h:.2f}" role="img" aria-label="OB Stays — '
        f'premium villas and property management">{b}{body}</svg>\n'
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(content)
    print(f"  {name:28} {len(content):>7} bytes")


def lockup(ob_c=GOLD, st_c=NAVY, tag_c=SOFT_NAVY, mark_c=NAVY, tagline=True, cap=60.0):
    pad = cap * MARK_SW / MARK_VB_W * MARK_W / 2 + 1  # half stroke, so nothing clips
    mw, mh = MARK_W * cap, MARK_H * cap

    ob_t = cor.tracking_for("OB", cap, OB_W * cap)
    st_t = cor.tracking_for("STAYS", cap, ST_W * cap)

    body = [mark_group(mark_c, pad, pad, mw)]
    body.append(
        f'<g fill="{ob_c}">'
        + cor.path("OB", cap, ob_t, pad + OB_X * cap, pad + BASELINE * cap)
        + "</g>"
    )
    body.append(
        f'<g fill="{st_c}">'
        + cor.path("STAYS", cap, st_t, pad + ST_X * cap, pad + BASELINE * cap)
        + "</g>"
    )

    if tagline:
        tcap = TAG_CAP * cap
        tt = inter.tracking_for(TAGLINE, tcap, TAG_W * cap)
        body.append(
            f'<g fill="{tag_c}">'
            + inter.path(TAGLINE, tcap, tt, pad + TAG_X * cap, pad + TAG_BASE * cap)
            + "</g>"
        )
        width = pad * 2 + max(mw, (ST_X + ST_W) * cap, (TAG_X + TAG_W) * cap)
    else:
        width = pad * 2 + max(mw, (ST_X + ST_W) * cap)

    return svg(width, pad * 2 + mh, "".join(body))


def emblem(bg, mark_c, ob_c, size=512.0, pad_frac=0.10, show_ob=True, sw=MARK_SW):
    """Square lockup: the house with OB nested inside. Favicon / avatar."""
    # The house interior, in the mark's own viewBox units.
    ix0, ix1 = 14.5, 131.0      # wall -> open right edge
    iy0, iy1 = 46.5, 101.5      # eave line -> base
    ob_cap = 34.0
    ob_w = OB_W * ob_cap
    ob_x = (ix0 + ix1) / 2 - ob_w / 2
    ob_base = (iy0 + iy1) / 2 + ob_cap / 2 - 6.0   # nudged up, optically centred
    ob_t = cor.tracking_for("OB", ob_cap, ob_w)

    inner = (
        f'<path d="{MARK_D}" fill="none" stroke="{mark_c}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        + (f'<g fill="{ob_c}">' + cor.path("OB", ob_cap, ob_t, ob_x, ob_base) + "</g>"
           if show_ob else "")
    )

    pad = size * pad_frac
    s_ = (size - 2 * pad) / MARK_VB_W
    top = (size - MARK_VB_H * s_) / 2
    body = (
        (f'<rect width="{size}" height="{size}" fill="{bg}"/>' if bg else "")
        + f'<g transform="translate({pad:.2f} {top:.2f}) scale({s_:.5f})">{inner}</g>'
    )
    return svg(size, size, body)


print("writing brand/")
write("logo-primary.svg", lockup())
write("logo-mono-navy.svg", lockup(NAVY, NAVY, NAVY, NAVY))
write("logo-mono-ivory.svg", lockup(IVORY, IVORY, IVORY, IVORY))
write("logo-mono-gold.svg", lockup(GOLD, GOLD, GOLD, GOLD))
write("logo-wordmark.svg", lockup(tagline=False))
write("logo-wordmark-ivory.svg", lockup(IVORY, IVORY, IVORY, IVORY, tagline=False))
write("mark.svg", svg(MARK_VB_W, MARK_VB_H,
                      f'<path d="{MARK_D}" fill="none" stroke="{NAVY}" '
                      f'stroke-width="{MARK_SW}" stroke-linecap="round" '
                      f'stroke-linejoin="round"/>'))
write("emblem.svg", emblem(IVORY, NAVY, GOLD))
write("emblem-navy.svg", emblem(NAVY, IVORY, GOLD))
# Favicon: mark only, stroke thickened so it survives 16-32px.
write("favicon.svg", emblem(None, NAVY, GOLD, size=64, pad_frac=0.05,
                            show_ob=False, sw=MARK_SW * 1.9))
print("done")
