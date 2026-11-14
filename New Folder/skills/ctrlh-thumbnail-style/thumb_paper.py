"""Ctrl + H thumbnail, paper_orange design (FIXED design, owner approved 2026-11-09). 1280x720 PNG.
usage: python3 thumb_paper.py out.png --kw "Price Snapshot" --l1 "العميل شاف 100" --l2 "ودفع 120؟!" \\
           [--left "عند الإضافة للسلة|100|جنيه"] [--right "عند الدفع|120|جنيه!"] [--no-cards]
Layout: logo top-left (white parts made black, no black box) / orange brush headline (line 1, ink text) / big ink line 2 on a yellow highlighter /
two cards "before -> after" (left white card with a red strike on the value, right orange card) / keyword pill / tagline / icon row / orange corner stripes.
Assets (kit): assets/logo_ch_dark.png, assets/thumb_icons_row.png, assets/fonts/Cairo-SemiBold.ttf, FiraCode-SemiBold.ttf."""
import os, sys, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets"); ARB, FIRA = os.path.join(A, "fonts", "Cairo-SemiBold.ttf"), os.path.join(A, "fonts", "FiraCode-SemiBold.ttf")
OR = (255, 138, 17); INK = (14, 14, 12); CREAM = (251, 248, 237)
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
out = sys.argv[1]; KW = opt("--kw", "Keyword"); L1 = opt("--l1", "العنوان"); L2 = opt("--l2", "السطر الثاني")
LEFT = (opt("--left", "عند الإضافة للسلة|100|جنيه")).split("|"); RIGHT = (opt("--right", "عند الدفع|120|جنيه!")).split("|"); CARDS = "--no-cards" not in sys.argv
S = 2; W, H = 1280 * S, 720 * S
font = lambda p, s: ImageFont.truetype(p, int(s * S), layout_engine=ImageFont.Layout.RAQM)
def fit(t, p, mw, st, lo=40):
    s = st
    while s > lo and font(p, s).getlength(t) > mw * S: s -= 4
    return s
yy, xx = np.mgrid[0:H, 0:W]; g = np.zeros((H, W, 3), np.float32) + np.array(CREAM, np.float32)
for cx, cy, r, k in ((0, 0, 900, .5), (W, H, 1100, .45)): g += (np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * S / 2) ** 2)) * k)[..., None] * np.array([4, -60, -150], np.float32)
g += np.random.default_rng(2).normal(0, 1.3, g.shape); im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
for x in range(40 * S, W, 40 * S):
    for y in range(40 * S, H, 40 * S): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(214, 204, 184, 255))
def hs(box, fill, off=14, r=26, bw=7):
    x0, y0, x1, y1 = [v * S for v in box]; d.rounded_rectangle((x0 + off * S, y0 + off * S, x1 + off * S, y1 + off * S), r * S, fill=INK); d.rounded_rectangle((x0, y0, x1, y1), r * S, fill=fill, outline=INK, width=bw * S // 2)
def txt(xy, t, f, fill, anchor="mm", ar=True, stroke=0):
    if ar: d.text((xy[0] * S, xy[1] * S), t, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar", stroke_width=stroke * S, stroke_fill=INK)
    else: d.text((xy[0] * S, xy[1] * S), t, font=f, fill=fill, anchor=anchor, stroke_width=stroke * S, stroke_fill=INK)
lg = Image.open(os.path.join(A, "logo_ch_dark.png")).convert("RGBA"); lg.thumbnail((112 * S, 104 * S))
sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); blk = Image.new("RGBA", lg.size, (60, 40, 10, 255)); blk.putalpha(lg.getchannel("A").point(lambda v: int(v * .35)))
sh.alpha_composite(blk, (43 * S, 37 * S)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * S))); im.alpha_composite(lg, (38 * S, 30 * S)); d = ImageDraw.Draw(im)
rng = random.Random(7); cx0, cx1, cy0, cy1 = 470 * S, 1230 * S, 60 * S, 190 * S; pts = []
for i in range(41): pts.append((cx0 + (cx1 - cx0) * i / 40, cy0 + rng.uniform(-6, 6) * S))
for k in range(8): pts.append((cx1 + rng.uniform(-4, 26) * S, cy0 + (cy1 - cy0) * (k + 1) / 9))
for i in range(41): pts.append((cx1 - (cx1 - cx0) * i / 40, cy1 + rng.uniform(-6, 6) * S))
for k in range(8): pts.append((cx0 + rng.uniform(-26, 4) * S, cy1 - (cy1 - cy0) * (k + 1) / 9))
d.polygon([(x + 9 * S, y + 9 * S) for x, y in pts], fill=INK); d.polygon(pts, fill=OR)
txt((850, 128), L1, font(ARB, fit(L1, ARB, 700, 105)), INK, stroke=2)
f2 = font(ARB, fit(L2, ARB, 700, 150)); b = d.textbbox((850 * S, 262 * S), L2, font=f2, anchor="mm", direction="rtl", language="ar")
d.rectangle((b[0] - 8 * S, b[3] - 64 * S, b[2] + 8 * S, b[3] - 28 * S), fill=(255, 214, 90)); txt((853, 265), L2, f2, INK); txt((850, 262), L2, f2, INK, stroke=2)
DY = -56
if CARDS:
    lab, val, unit = LEFT; hs((110, 395 + DY, 470, 590 + DY), (255, 253, 249)); txt((290, 428 + DY), lab, font(ARB, 32), (110, 104, 92)); fv = font(FIRA, 112); txt((290, 500 + DY), val, fv, INK, ar=False)
    bb = d.textbbox((290 * S, (500 + DY) * S), val, font=fv, anchor="mm"); d.line([(bb[0] - 14 * S, bb[3] - 26 * S), (bb[2] + 14 * S, bb[1] + 26 * S)], fill=(229, 72, 77), width=10 * S); txt((290, 556 + DY), unit, font(ARB, 32), (110, 104, 92))
    lab, val, unit = RIGHT; hs((650, 380 + DY, 1020, 598 + DY), OR); txt((835, 414 + DY), lab, font(ARB, 36), INK); txt((835, 487 + DY), val, font(FIRA, 136), INK, ar=False, stroke=1); txt((835, 560 + DY), unit, font(ARB, 40), INK)
    d.polygon([(x * S, y * S) for x, y in [(492, 492 + DY), (560, 492 + DY), (560, 468 + DY), (620, 505 + DY), (560, 542 + DY), (560, 518 + DY), (492, 518 + DY)]], fill=INK)
fk = font(FIRA, 40); w = d.textlength(KW, font=fk) / S; cx = 640
hs((cx - w / 2 - 28, 550, cx + w / 2 + 28, 594), INK, 6, 22, 5); txt((cx, 572), KW, fk, OR, ar=False)
tg = "THINK DEEPER. BUILD SMARTER."; ft = font(FIRA, 17); sp = 5 * S; x = cx * S - (sum(ft.getlength(c) + sp for c in tg) - sp) / 2
for c in tg: d.text((x, 616 * S), c, font=ft, fill=INK, anchor="lm"); x += ft.getlength(c) + sp
for poly in ([(1135, 0), (1205, 0), (1280, 72), (1280, 108)], [(0, 596), (0, 634), (86, 720), (140, 720)]): d.polygon([(x * S, y * S) for x, y in poly], fill=OR)
ico = Image.open(os.path.join(A, "thumb_icons_row.png")).convert("RGBA"); k = .82; ico = ico.resize((int(578 * k * S), int(86 * k * S)), Image.LANCZOS); im.alpha_composite(ico, (int((640 - 578 * k / 2) * S), 640 * S)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 8 * S), fill=OR)
im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out); print("thumbnail ->", out)
