"""Ctrl + H background generator, 1920x1080. Usage: python3 ctrlh_bg.py <tech> <out.png> [fira_font.ttf]
tech: nextjs react laravel docker node db redis git"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1920, 1080
import os
_h = os.environ.get("CTRLH_ACCENT", "").lstrip("#")
OR = tuple(int(_h[i:i + 2], 16) for i in (0, 2, 4)) if len(_h) == 6 else (255, 138, 17)   # CTRLH_ACCENT=#RRGGBB
OR2 = tuple(min(255, int(c + (255 - c) * 0.2)) for c in OR)
TECH, OUT = sys.argv[1], sys.argv[2]
FONT = sys.argv[3] if len(sys.argv) > 3 else None
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32) + np.array([13, 14, 16], np.float32)
def glow(cx, cy, r, col, k):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return (np.exp(-(d / r) ** 2) * k)[..., None] * np.array(col, np.float32)
base += glow(0, 0, 700, OR, .20) + glow(W, H, 800, OR, .16) + glow(W, 0, 420, OR2, .06)
dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
base *= (0.80 + 0.20 * np.clip(1 - dd, 0, 1))[..., None]          # vignette
im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
Lr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(Lr)
for x in range(0, W + 1, 96): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
for y in range(0, H + 1, 96): d.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
def node(x, y, r=7, a=120):
    d.ellipse((x - r, y - r, x + r, y + r), outline=OR + (a,), width=2); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=OR + (a,))
def trace(p, a=95):
    d.line(p, fill=OR + (a,), width=2, joint="curve"); node(*p[-1])
def box(x, y, w, h, a=110, r=10): d.rounded_rectangle((x, y, x + w, y + h), r, outline=OR + (a,), width=2)
def hexa(cx, cy, r, a=38):
    d.polygon([(cx + r * math.cos(math.pi / 3 * i), cy + r * math.sin(math.pi / 3 * i)) for i in range(6)], outline=(255, 255, 255, a))
def dots(x0, y0, n, dx=0, dy=34, a=80):
    for i in range(n): d.ellipse((x0 + i * dx - 2, y0 + i * dy - 2, x0 + i * dx + 2, y0 + i * dy + 2), fill=OR + (a,))
def syms(items):
    return  # code symbols disabled: they landed behind cards
    f = ImageFont.truetype(FONT, 34) if FONT else ImageFont.load_default()
    for t, x, y in items: d.text((x, y), t, font=f, fill=(255, 255, 255, 34))
def arcs(cx, cy, a0, a1):
    for r in (140, 220, 300): d.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=OR + (55,), width=2)

if TECH == "nextjs":      # server -> routing branches -> browser
    for k in range(3): box(70, 60 + k * 70, 190, 50); d.ellipse((88, 79 + k * 70, 100, 91 + k * 70), fill=OR + (150,))
    trace([(165, 270), (165, 450), (90, 520), (90, 760), (150, 820), (150, 1000)]); trace([(165, 450), (240, 520), (240, 700)], 70)
    box(1620, 840, 240, 160); d.line([(1620, 876), (1860, 876)], fill=OR + (90,), width=2)
    trace([(1840, 60), (1840, 300), (1780, 360), (1780, 840)], 85); dots(1840, 120, 5)
    for c in [(1700, 120), (1785, 168), (1700, 216)]: hexa(*c, 46)
    dots(300, 1040, 18, dx=34, dy=0); node(300, 1040); node(900, 1040, 9, 140); arcs(0, H, 270, 360)
    syms([("</>", 90, 880), ("=>", 1500, 700), ("//", 1700, 640)])
elif TECH == "react":     # component tree + orbits
    for (x, y) in [(150, 120), (60, 300), (240, 300)]: box(x, y, 130, 54, r=14)
    d.line([(215, 174), (215, 230), (125, 230), (125, 300)], fill=OR + (90,), width=2); d.line([(215, 230), (305, 230), (305, 300)], fill=OR + (90,), width=2)
    for (x, y) in [(1600, 780), (1720, 900), (1500, 920)]: box(x, y, 150, 56, r=14)
    d.line([(1675, 836), (1675, 868), (1795, 868), (1795, 900)], fill=OR + (90,), width=2)
    for r in (110, 170): d.ellipse((1700 - r, 160 - r // 2, 1700 + r, 160 + r // 2), outline=(90, 200, 230, 40), width=2)
    node(1700, 160, 9, 130); trace([(100, 500), (100, 800), (160, 860), (160, 1020)]); arcs(0, H, 270, 360); syms([("{}", 80, 900), ("<App />", 1480, 700)])
elif TECH in ("laravel", "wp"):   # MVC lines + db
    for i, t in enumerate(["M", "V", "C"]): box(70 + i * 100, 80, 80, 80, r=14)
    d.line([(150, 160), (150, 230), (250, 230), (250, 160)], fill=OR + (90,), width=2); d.line([(350, 160), (350, 230), (250, 230)], fill=OR + (90,), width=2)
    for k in range(3): d.ellipse((1620, 840 + k * 40, 1800, 880 + k * 40), outline=OR + (100,), width=2)
    d.line([(1620, 860), (1620, 960)], fill=OR + (100,), width=2); d.line([(1800, 860), (1800, 960)], fill=OR + (100,), width=2)
    trace([(1710, 60), (1710, 300), (1640, 370), (1640, 820)], 80); trace([(80, 500), (80, 820), (140, 880), (140, 1020)]); arcs(0, H, 270, 360)
    syms([("<?php", 80, 960), ("->", 1500, 700), ("::", 1700, 640)])
elif TECH == "docker":    # containers + layers
    for r in range(2):
        for c in range(3): box(70 + c * 80, 840 + r * 70, 64, 52, 100, 6)
    for k in range(3): box(1560 + k * 20, 70 + k * 18, 250, 90, 120 - k * 30, 12)
    trace([(1800, 220), (1800, 500), (1740, 560), (1740, 800)], 85); trace([(100, 120), (100, 520), (160, 580), (160, 760)]); dots(300, 1040, 18, dx=34, dy=0); arcs(W, H, 180, 270)
    syms([("FROM", 80, 400), ("RUN", 1600, 700)])
elif TECH in ("node", "rest"):      # server nodes + request/response
    for (x, y) in [(120, 120), (300, 220), (120, 320)]: node(x, y, 14, 140)
    d.line([(120, 120), (300, 220), (120, 320)], fill=OR + (90,), width=2)
    trace([(1780, 100), (1780, 380), (1720, 440), (1720, 900)], 85); trace([(1850, 100), (1850, 700)], 55)
    dots(300, 1040, 18, dx=34, dy=0); node(300, 1040); node(900, 1040, 9, 140); arcs(0, H, 270, 360); syms([("GET", 90, 880), ("200", 1560, 700)])
elif TECH == "db":        # cylinders + table grid
    for k in range(3): d.ellipse((90, 90 + k * 60, 270, 130 + k * 60), outline=OR + (100,), width=2)
    d.line([(90, 110), (90, 230)], fill=OR + (100,), width=2); d.line([(270, 110), (270, 230)], fill=OR + (100,), width=2)
    for i in range(4):
        for j in range(3): d.rectangle((1560 + j * 90, 840 + i * 44, 1650 + j * 90, 884 + i * 44), outline=OR + (60,))
    trace([(180, 300), (180, 700), (240, 760), (240, 1000)], 80); trace([(1780, 100), (1780, 740)], 80); arcs(0, H, 270, 360); syms([("SELECT", 80, 900)])
elif TECH == "redis":     # cache layers + fast flow
    for k in range(4): box(90 + k * 22, 80 + k * 22, 210, 70, 110 - k * 20, 10)
    for k in range(5): d.line([(1500 + k * 60, 900), (1560 + k * 60, 840)], fill=OR + (90 - k * 10,), width=3)
    trace([(1780, 100), (1780, 420), (1720, 480), (1720, 760)], 85); trace([(100, 450), (100, 800), (160, 860), (160, 1000)]); dots(300, 1040, 18, dx=34, dy=0); arcs(W, H, 180, 270); syms([("GET key", 80, 900), ("TTL", 1600, 640)])
elif TECH == "git":       # branches + commit nodes
    d.line([(120, 100), (120, 900)], fill=OR + (95,), width=2); d.line([(120, 280), (220, 360), (220, 600), (120, 680)], fill=OR + (95,), width=2)
    for y in (100, 280, 480, 680, 900): node(120, y, 10, 140)
    node(220, 360, 10, 120); node(220, 600, 10, 120)
    d.line([(1780, 160), (1780, 900)], fill=OR + (80,), width=2); d.line([(1780, 400), (1700, 470), (1700, 700), (1780, 770)], fill=OR + (80,), width=2)
    for y in (160, 400, 600, 900): node(1780, y, 9, 120)
    arcs(W, H, 180, 270); syms([("git", 300, 940), ("merge", 1500, 700)])

# --- per-technology name chips (plain text, neutral font) and optional user-supplied logo files
LABELS = {"laravel": ["PHP", "Laravel", "MySQL"], "nextjs": ["Next.js", "React", "Node.js"], "react": ["React", "JSX", "Hooks"],
          "docker": ["Docker", "Compose", "Linux"], "node": ["Node.js", "Express", "npm"], "db": ["SQL", "PostgreSQL", "MySQL"],
          "redis": ["Redis", "Cache", "TTL"], "rest": ["REST", "HTTP", "JSON"], "wp": ["WordPress", "PHP", "MySQL"], "git": ["Git", "GitHub", "Branch"]}
SLOTS = [(940, 1026), (1120, 1026), (1330, 1026)]    # bottom strip below the content area
fl = ImageFont.truetype(FONT, 24) if FONT else ImageFont.load_default()
for (x, y), t in zip(SLOTS, LABELS.get(TECH, [])):
    w = int(d.textlength(t, font=fl)) + 44
    d.rounded_rectangle((x, y, x + w, y + 40), 20, outline=OR + (120,), width=2)
    d.text((x + 22, y + 21), t, font=fl, fill=(255, 255, 255, 120), anchor="lm")
for k, p in enumerate(sys.argv[4:]):                  # optional logo images the user provides (PNG with alpha)
    lg = Image.open(p).convert("RGBA"); lg.thumbnail((150, 150))
    al = np.asarray(lg)[..., 3].astype(np.float32) * 0.22
    mono = np.zeros((lg.height, lg.width, 4), np.uint8); mono[..., :3] = 255; mono[..., 3] = al.astype(np.uint8)
    Lr.alpha_composite(Image.fromarray(mono), (W - 190 - k * 170, 80))
a = np.asarray(Lr).astype(np.float32)
mask = np.clip((np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.62) / 0.35, 0, 1)
a[..., 3] *= np.clip(mask * 1.25, 0, 1)
L2 = Image.fromarray(a.astype(np.uint8))
out = Image.alpha_composite(im, L2)
ga = np.asarray(L2.filter(ImageFilter.GaussianBlur(5))).astype(np.float32); ga[..., 3] *= 0.5
out = Image.alpha_composite(out, Image.fromarray(ga.astype(np.uint8)))
out.convert("RGB").save(OUT)
