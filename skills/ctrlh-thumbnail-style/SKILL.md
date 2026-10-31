---
name: "ctrlh-thumbnail-style"
description: "Use when delivering any Ctrl + H video: also make its YouTube thumbnail (1280x720) in the approved reference style with an orange brush-stroke Arabic headline."
---

# Ctrl + H thumbnail (deliver with EVERY video)

Owner: Hesham (Egyptian Arabic). Decided 2026-10-27: every video is delivered together with its thumbnail. Send the PNG with SendUserFile right after the video (one file per thumbnail, short caption). Reply in Egyptian Arabic.

## Look (approved reference, do not redesign)
- Base plate = the reference image he sent (thumb_ref.png, 1672x941: dark desk, blurred shelves, black mug with the C+H logo on the left, laptop with code on the right, official CTRL + H logo top-left, orange diagonal corner stripes, row of 5 icons FRONTEND / BACKEND / DATABASES / DEVOPS / GIT & GITHUB at the bottom). Keep a copy named thumb_ref.png in the work folder; if missing, ask him to re-send it. Never redraw the logo.
- Wipe the middle text area of the plate (rect x 290-1215 y 110-575 plus x 290-1120 y 540-730, feathered with GaussianBlur 18) with a dark charcoal plate (9,9,11) + soft warm glow + light noise, keeping mug, laptop, logo, corner stripes and the icon row.
- Headline = 2 lines of Egyptian Arabic, short (2-4 words each): line 1 black Cairo SemiBold (stroke 5) on an orange (#FF8A11) dry-brush shape at (760,255) size 830x190; line 2 big white Cairo SemiBold with black outline and soft shadow at y 450, orange tapered underline below it. Below: the topic keyword in Fira Code SemiBold orange (English, e.g. Laravel Queues) at y 628, then the spaced tagline THINK DEEPER. BUILD SMARTER. at y 690.
- Output 1280x720 PNG (resize from 1672x941 with LANCZOS), named <topic>_thumb.png; also zip a batch.
- Hook wording: Egyptian Arabic, a question or a punch (e.g. "الفلوس اتخصمت / والأوردر ضاع؟", "Git / مش GitHub!"). Mixed Arabic+Latin is fine with Cairo; an exclamation after Latin appears on the left in RTL, that is correct.
- No AI image generation here: the photo plate stays the same for every thumbnail. If he sends other photos, composite them the same way.

## Generator (thumbs2.py)
Fonts: Cairo-SemiBold.ttf and FiraCode-SemiBold.ttf (he uploaded both). Load with ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM); Arabic text: direction="rtl", language="ar".

```python
import os, random, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
REF, ARB, FIRA = "thumb_ref.png", "Cairo-SemiBold.ttf", "FiraCode-SemiBold.ttf"
OR = (255, 138, 17)
T = [("queues", "Laravel Queues", "نفّذ الشغل التقيل", "في الخلفية!")]   # (file name, English keyword, line 1 on brush, line 2 white)
ref = Image.open(REF).convert("RGBA"); W, H = ref.size
font = lambda p, s: ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def fit(txt, p, maxw, start, lo=40):
    s = start
    while s > lo and font(p, s).getlength(txt) > maxw: s -= 4
    return s
yy, xx = np.mgrid[0:H, 0:W]
glow = np.exp(-(((xx - 760) / 520) ** 2 + ((yy - 380) / 330) ** 2))
g = np.zeros((H, W, 3), np.float32); g[..., 0] = 9 + 38 * glow; g[..., 1] = 9 + 16 * glow; g[..., 2] = 11 + 2 * glow
g += np.random.default_rng(1).normal(0, 1.6, g.shape)
plate = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
md.rectangle((290, 110, 1215, 575), fill=255); md.rectangle((290, 540, 1120, 730), fill=255)
base = Image.composite(plate, ref, mask.filter(ImageFilter.GaussianBlur(18)))

def brush(d, cx, cy, w, h, rng):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2; n = 40; pts = []
    for i in range(n + 1): x = x0 + (x1 - x0) * i / n; pts.append((x, y0 + rng.uniform(-7, 7) - (x - cx) * 0.012))
    for k in range(9): pts.append((x1 + rng.uniform(-6, 34), y0 + (y1 - y0) * (k + 1) / 10))
    for i in range(n + 1): x = x1 - (x1 - x0) * i / n; pts.append((x, y1 + rng.uniform(-7, 7) - (x - cx) * 0.012))
    for k in range(9): pts.append((x0 + rng.uniform(-34, 6), y1 - (y1 - y0) * (k + 1) / 10))
    d.polygon(pts, fill=OR + (255,))
    for _ in range(26):
        y = rng.uniform(y0 + 10, y1 - 10); xa = rng.uniform(x0, x1 - 120); L = rng.uniform(80, 360)
        d.line([(xa, y), (min(xa + L, x1), y + rng.uniform(-3, 3))], fill=(255, 170, 60, 150), width=rng.randint(2, 5))

for name, kw, l1, l2 in T:
    rng = random.Random(name); im = base.copy()
    S = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    brush(d, 760, 255, 830, 190, rng)
    d.line([(330, 190), (365, 205)], fill=OR + (255,), width=6); d.line([(372, 128), (394, 160)], fill=OR + (255,), width=6)
    f1 = font(ARB, fit(l1, ARB, 720, 130))
    d.text((760, 258), l1, font=f1, fill=(10, 10, 10, 255), anchor="mm", direction="rtl", language="ar", stroke_width=5, stroke_fill=(10, 10, 10, 255))
    f2 = font(ARB, fit(l2, ARB, 800, 190))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.text((764, 458), l2, font=f2, fill=(0, 0, 0, 220), anchor="mm", direction="rtl", language="ar", stroke_width=14, stroke_fill=(0, 0, 0, 220))
    S = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), S); d = ImageDraw.Draw(S)
    d.text((760, 450), l2, font=f2, fill=(255, 255, 255, 255), anchor="mm", direction="rtl", language="ar", stroke_width=7, stroke_fill=(8, 8, 8, 255))
    d.text((760, 450), l2, font=f2, fill=(255, 255, 255, 255), anchor="mm", direction="rtl", language="ar")
    d.polygon([(620, 552), (900, 540), (960, 546), (900, 556), (630, 562)], fill=OR + (255,))
    fk = font(FIRA, fit(kw, FIRA, 760, 76))
    d.text((760, 628), kw, font=fk, fill=OR + (255,), anchor="mm", stroke_width=3, stroke_fill=(8, 8, 8, 255))
    tg = "THINK DEEPER. BUILD SMARTER."; ft = font(FIRA, 25); sp = 7
    x = 760 - (sum(ft.getlength(c) + sp for c in tg) - sp) / 2
    for c in tg: d.text((x, 690), c, font=ft, fill=OR + (255,), anchor="lm"); x += ft.getlength(c) + sp
    Image.alpha_composite(im, S).convert("RGB").resize((1280, 720), Image.LANCZOS).save(name + "_thumb.png")
```

## Checklist
1. Pick the 2-line hook and the English keyword from the post (same wording as the video hook, shorter).
2. Render, view the PNG once (no leftovers of the original text, text inside the brush, nothing cut off), then deliver it right after the video.
3. Hook line 1 max about 20 characters, line 2 max about 22; the generator shrinks fonts to fit.