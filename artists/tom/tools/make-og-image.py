"""Build the 1200x630 link-preview card for WhatsApp / iMessage / Slack / X."""
import io, os, cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = lambda n: os.path.join(HERE, os.pardir, "assets", n)
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 630
NAVY = (11, 31, 58)
GOLD = (200, 164, 92)

src = Image.open(ASSET("villa-stone-night.jpg")).convert("RGB")
# cover-crop to 1200x630
sw, sh = src.size
scale = max(W / sw, H / sh)
src = src.resize((int(sw * scale + 1), int(sh * scale + 1)), Image.LANCZOS)
left = (src.width - W) // 2
top = int((src.height - H) * 0.42)          # bias up: keep the lit facade, lose foreground
img = src.crop((left, top, left + W, top + H))

# navy wash so ivory type stays legible over a busy night shot
wash = Image.new("RGB", (W, H), NAVY)
img = Image.blend(img, wash, 0.66)

# vignette: darker top and bottom, so the centred lockup sits in calm space
grad = Image.new("L", (1, H))
for y in range(H):
    t = y / (H - 1)
    edge = max(0.0, 1 - (min(t, 1 - t) / 0.42))     # 0 mid, 1 at the edges
    grad.putpixel((0, y), int(150 * edge ** 1.6))
grad = grad.resize((W, H))
img = Image.composite(Image.new("RGB", (W, H), NAVY), img, grad)
img = img.filter(ImageFilter.GaussianBlur(0.4))

# soft radial scrim behind the lockup -- the villa's lit facade is the
# busiest part of the frame and 'STAYS' sat right on top of it.
import math
cx, cy, rx, ry_ = W / 2, H / 2 - 20, W * 0.40, H * 0.34
mask = Image.new("L", (W, H), 0)
mp = mask.load()
for y in range(H):
    dy = (y - cy) / ry_
    for x in range(0, W, 2):
        dx = (x - cx) / rx
        d_ = math.hypot(dx, dy)
        v = int(165 * max(0.0, 1 - d_) ** 1.5) if d_ < 1 else 0
        mp[x, y] = v
        if x + 1 < W:
            mp[x + 1, y] = v
mask = mask.filter(ImageFilter.GaussianBlur(28))
img = Image.composite(Image.new("RGB", (W, H), NAVY), img, mask)

# the lockup, rasterised from the ivory SVG at 2x then downsampled
logo_w = 660
png = cairosvg.svg2png(
    url=ASSET("logo-mono-ivory.svg"),
    output_width=logo_w * 2)
logo = Image.open(io.BytesIO(png)).convert("RGBA")
logo = logo.resize((logo_w, int(logo.height * logo_w / logo.width)), Image.LANCZOS)

canvas = img.convert("RGBA")
lx = (W - logo.width) // 2
ly = (H - logo.height) // 2 - 26
canvas.alpha_composite(logo, (lx, ly))

# thin gold rule beneath, echoing the brand board
d = ImageDraw.Draw(canvas)
ry = ly + logo.height + 46
d.line([(W // 2 - 90, ry), (W // 2 + 90, ry)], fill=GOLD + (235,), width=2)

out = canvas.convert("RGB")
out.save(ASSET("og-share.jpg"), "JPEG", quality=86, optimize=True, progressive=False)
print("written", out.size)
