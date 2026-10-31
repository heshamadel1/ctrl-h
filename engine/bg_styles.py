"""Background styles for any accent / base colour, 16:9 and 9:16.
make(style, W, H, accent, base, labels=None) -> RGBA PIL image.   styles: circuit grid hex dots waves aurora blueprint minimal"""
import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
STYLES = {"circuit": "grid + circuit traces and nodes along the edges", "grid": "bold technical grid with corner glow",
          "hex": "hexagon lattice fading toward the centre", "dots": "dot matrix, brighter near the edges",
          "waves": "flowing wave lines at top and bottom", "aurora": "soft blurred colour bands, no lines",
          "blueprint": "fine blueprint grid, corner marks and construction lines", "minimal": "plain gradient and vignette only"}

def _base(W, H, accent, base, glows=True):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + np.array(base, np.float32); ac = np.array(accent, np.float32)
    if glows:
        sc = W / 1920.0 if W > H else H / 1920.0
        for cx, cy, r, k in ((0, 0, 700 * sc, .20), (W, H, 800 * sc, .16), (W, 0, 420 * sc, .06)):
            d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); img += (np.exp(-(d / r) ** 2) * k)[..., None] * ac
    dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (0.80 + 0.20 * np.clip(1 - dd, 0, 1))[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA"), dd

def _edge_mask(layer, dd, lo=0.45, span=0.4):
    a = np.asarray(layer).astype(np.float32); m = np.clip((dd - lo) / span, 0, 1); a[..., 3] *= np.clip(m * 1.25, 0, 1)
    return Image.fromarray(a.astype(np.uint8))

def make(style, W, H, accent, base, labels=None, font=None):
    style = style if style in STYLES else "circuit"; rnd = random.Random(7)
    im, dd = _base(W, H, accent, base, glows=(style != "minimal")); AC = tuple(accent)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); S = W / 1920.0 if W > H else H / 1920.0
    def node(x, y, r=7, a=120):
        d.ellipse((x - r, y - r, x + r, y + r), outline=AC + (a,), width=2); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=AC + (a,))
    if style == "circuit":
        for x in range(0, W + 1, 96): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
        for y in range(0, H + 1, 96): d.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
        for i in range(14):
            side = i % 4; x = rnd.choice([48, 96, 144, 192]) if side in (0, 2) else None
            if side == 0: p = [(x, 0)]; cx, cy = x, 0
            elif side == 1: cy = rnd.randrange(2, 9) * 96; p = [(W, cy)]; cx = W
            elif side == 2: cy = H; p = [(x if x else 96, H)]; cx = p[0][0]
            else: cy = rnd.randrange(2, 9) * 96; p = [(0, cy)]; cx = 0
            x_, y_ = p[0]
            for _ in range(3):
                if side in (0, 2): y_ += (rnd.randrange(160, 360)) * (1 if side == 0 else -1); p.append((x_, y_)); x_ += rnd.choice([-1, 1]) * 48; p.append((x_, y_ + (48 if side == 0 else -48)))
                else: x_ += rnd.randrange(160, 360) * (1 if side == 3 else -1); p.append((x_, y_)); y_ += rnd.choice([-1, 1]) * 48; p.append((x_, y_))
            d.line(p, fill=AC + (85,), width=2, joint="curve"); node(*p[-1])
        for i in range(4): d.rounded_rectangle((70 * S, (60 + i * 70) * S, 260 * S, (110 + i * 70) * S), 10, outline=AC + (100,), width=2)
    elif style == "grid":
        for x in range(0, W + 1, 48): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 14 if x % 192 else 30))
        for y in range(0, H + 1, 48): d.line([(0, y), (W, y)], fill=(255, 255, 255, 14 if y % 192 else 30))
        for x in range(0, W + 1, 192):
            for y in range(0, H + 1, 192): d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=AC + (110,))
    elif style == "hex":
        r = 62 * S
        for row in range(-1, int(H / (r * 1.5)) + 2):
            for col in range(-1, int(W / (r * 1.74)) + 2):
                cx = col * r * 1.74 + (r * 0.87 if row % 2 else 0); cy = row * r * 1.5
                d.polygon([(cx + r * math.cos(math.pi / 3 * i + math.pi / 6), cy + r * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)], outline=AC + (60,) if (row * 7 + col * 3) % 5 == 0 else (255, 255, 255, 22))
    elif style == "dots":
        st = int(40 * S) or 40
        for x in range(st // 2, W, st):
            for y in range(st // 2, H, st): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=AC + (150,) if (x // st + y // st) % 7 == 0 else (255, 255, 255, 60))
    elif style == "waves":
        for k in range(9):
            for base_y, sgn in ((H * 0.9, 1), (H * 0.1, -1)):
                pts = [(x, base_y + sgn * (k * 22 * S) + math.sin(x / (240 * S) + k * 0.5) * 38 * S) for x in range(0, W + 1, 12)]
                d.line(pts, fill=AC + (int(120 - k * 11),), width=2)
    elif style == "aurora":
        for i, (cx, cy, r, k) in enumerate(((0.15, 0.2, 0.5, 90), (0.85, 0.8, 0.55, 80), (0.9, 0.15, 0.35, 55), (0.1, 0.9, 0.4, 50))):
            c = tuple(int(v) for v in (np.array(AC) * (1 - 0.35 * (i % 2)) + np.array([255, 255, 255]) * 0.1 * (i % 2)))
            d.ellipse((cx * W - r * W, cy * H - r * W * 0.5, cx * W + r * W, cy * H + r * W * 0.5), fill=c + (k,))
        L = L.filter(ImageFilter.GaussianBlur(110 * S))
    elif style == "blueprint":
        for x in range(0, W + 1, 24): d.line([(x, 0), (x, H)], fill=AC + (14 if x % 120 else 34,))
        for y in range(0, H + 1, 24): d.line([(0, y), (W, y)], fill=AC + (14 if y % 120 else 34,))
        m = 36
        for cx, cy, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
            d.line([(cx, cy), (cx + sx * 90, cy)], fill=AC + (150,), width=3); d.line([(cx, cy), (cx, cy + sy * 90)], fill=AC + (150,), width=3)
        d.line([(0, 0), (W * 0.22, H * 0.4)], fill=AC + (40,), width=2); d.line([(W, H), (W * 0.78, H * 0.6)], fill=AC + (40,), width=2)
        d.ellipse((W * 0.9 - 80, H * 0.18 - 80, W * 0.9 + 80, H * 0.18 + 80), outline=AC + (60,), width=2)
    if style not in ("aurora", "minimal"): L = _edge_mask(L, dd)
    im = Image.alpha_composite(im, L)
    if labels:
        dl = ImageDraw.Draw(im); f = ImageFont.truetype(font, int(26 * S) if font else 26) if font else ImageFont.load_default()
        y = int(H - (84 if W < H else 54) * 1.0); x = 250 if W < H else 620
        for tx in labels:
            w = int(f.getlength(tx)) + 50; dl.rounded_rectangle((x, y, x + w, y + 46), 23, outline=AC + (120,), width=2); dl.text((x + w / 2, y + 23), tx, font=f, fill=(255, 255, 255, 120), anchor="mm"); x += w + 24
    return im
