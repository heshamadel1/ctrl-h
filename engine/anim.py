# Ctrl + H "motion v2" engine: same scenes render at 16:9 (FMT=wide) and 9:16 (FMT=reel)
import os, re, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SD = os.environ.get("CTRLH_ASSETS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")) + "/"
FMT = os.environ.get("FMT", "wide")
WIDE = FMT == "wide"
W, H = (1920, 1080) if WIDE else (1080, 1920)
FPS = 30
def _hex(h, d):
    h = os.environ.get(h, "").lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else d
OR = _hex("CTRLH_ACCENT", (255, 138, 17))   # accent colour, e.g. CTRLH_ACCENT=#00B8D9
OR2 = tuple(min(255, int(c + (255 - c) * 0.2)) for c in OR)   # lighter accent
ORD = tuple(int(c * 0.67) for c in OR)   # darker accent (button depth)
INK = (10, 11, 13); PAPER = (245, 245, 245)
CARDC = _hex("CTRLH_CARD_COLOR", (24, 26, 31))   # card background colour, e.g. CTRLH_CARD_COLOR=#1B2A41
CARD_NUM = tuple(int(c * 0.85) for c in CARDC); CARD_GLASS = tuple(min(255, c + 10) for c in CARDC)   # derived: `numbers` / `glass` card fills
_ALL_STYLES = ["classic", "proposed", "glass", "numbers"]
_DEFAULT_STYLE = "classic"   # what someone who just installed the kit gets
_cs = os.environ.get("CTRLH_CARD_STYLES", "").replace(" ", "").lower()   # e.g. glass | classic,numbers | all
CARD_STYLES = _ALL_STYLES if _cs == "all" else ([x for x in _cs.split(",") if x in _ALL_STYLES] or [_DEFAULT_STYLE])
GRAYC = (150, 156, 170); RED = (255, 92, 92); GRN = (80, 230, 140); AMB = (255, 196, 80); BLUE = (150, 200, 255); VIO = (176, 148, 255)
# texts that are part of the brand / language; override with environment variables
LBL_OK = os.environ.get("CTRLH_LABEL_OK", "صح"); LBL_BAD = os.environ.get("CTRLH_LABEL_WRONG", "غلط")
LBL_CHAPTER = os.environ.get("CTRLH_LABEL_CHAPTER", "الجزء")   # chapter banner: "<label> 2 · <stage name>"
SIGNOFF1 = os.environ.get("CTRLH_SIGNOFF_1", "Think Deeper."); SIGNOFF2 = os.environ.get("CTRLH_SIGNOFF_2", "Build Smarter.")   # end-card lines

def _asset_img(name, mode, size):
    """brand image from assets/; neutral placeholder if you have not added yours yet"""
    try: return Image.open(SD + name).convert(mode)
    except Exception:
        im = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((4, 4, size[0] - 5, size[1] - 5), radius=size[0] // 6, outline=OR + (255,), width=max(3, size[0] // 30))
        return im.convert(mode)

ARB = os.environ.get("CTRLH_FONT_AR", SD + "fonts/Cairo-SemiBold.ttf")   # Arabic font
MONO = os.environ.get("CTRLH_FONT_LATIN", SD + "fonts/FiraCode-SemiBold.ttf")   # English / code font
_FC = {}


def F(path, size):
    k = (path, int(size))
    if k not in _FC:
        _FC[k] = ImageFont.truetype(path, int(size), layout_engine=ImageFont.Layout.RAQM)
    return _FC[k]


def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def prog(t, a, b): return cl((t - a) / (b - a))
def E(t, te, d=0.4): return ss(prog(t, te - 0.12, te - 0.12 + min(d, 0.3)))
def A(c, a): return (int(c[0]), int(c[1]), int(c[2]), int(round(255 * cl(a))))
def lerp(c0, c1, k): return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(3))


def hard(d, box, fill, shadow, border=PAPER, a=1.0, r=22, off=9, bw=4, dy=0):
    x0, y0, x1, y1 = box; y0 += dy; y1 += dy
    d.rounded_rectangle((x0 + off, y0 + off, x1 + off, y1 + off), r, fill=A(shadow, a))
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=A(fill, a), outline=A(border, a), width=bw)


def txt(d, xy, text, size, fill, anchor="mm", mono=None):
    if mono is None: mono = text.isascii()
    if mono: d.text(xy, text, font=F(MONO, size), fill=fill, anchor=anchor)
    else: d.text(xy, text, font=F(ARB, size), fill=fill, anchor=anchor, direction="rtl", language="ar")


def wrap(text, font, maxw, rtl=True):
    lines, cur = [], ""
    for w in text.split(" "):
        trial = (cur + " " + w).strip()
        ln = font.getlength(trial, direction="rtl", language="ar") if rtl else font.getlength(trial)
        if ln <= maxw: cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def badge(d, cx, cy, ok, a, r=28):
    col = GRN if ok else RED
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(col, a))
    d.text((cx, cy - 1), "✓" if ok else "✕", font=F("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(r * 1.1)), fill=A(INK, a), anchor="mm")


def colorize(text):
    cols = [PAPER] * len(text)
    def paint(rx, c):
        for m in re.finditer(rx, text):
            for k in range(m.start(), m.end()): cols[k] = c
    paint(r"\b\d+\b", GRN); paint(r"\b[A-Z]\w*", VIO); paint(r"\$\w+", PAPER); paint(r"\b(class|public|function|return|fn|use|true|false)\b", OR)
    paint(r"'[^']*'", AMB); paint(r"->\w+", BLUE); paint(r"::\w+", BLUE); paint(r"=>", OR)
    return cols


# ------------------------------------------------------------------ sizes per format
CS = 44 if WIDE else 56            # card font
CPAD = 60 if WIDE else 70
GAP = 22 if WIDE else 30
RX0, RX1 = (140, 1780) if WIDE else (60, 1020)
RY0, RY1 = (265, 985) if WIDE else (360, 1740)
RW_ = RX1 - RX0


def card_lines(blk, width):
    f = F(ARB, blk.get("size", CS))
    if blk["text"].isascii(): return [blk["text"]]
    if width < 600: return wrap(blk["text"], f, width - 70)
    if blk.get("style") == "numbers": return wrap(blk["text"], f, width - 420)
    return wrap(blk["text"], f, width - 2 * CPAD - 40)


def block_w(blk, width):
    return width


def block_h(blk, width):
    k = blk["k"]
    if k == "card":
        n = len(card_lines(blk, width)); s = blk.get("size", CS)
        extra = 40 if (blk.get("style") == "proposed" and blk.get("tag")) else 0
        return max(108 if WIDE else 140, int(n * s * 1.3 + 50)) + extra
    if k == "chip": return 72 if WIDE else 90
    if k == "title":
        n = len(wrap(blk["text"], F(ARB, blk.get("size", 56 if WIDE else 64)), width - 120)) if not blk["text"].isascii() else 1
        return (150 if WIDE else 200) + (int(blk.get("size", 56) * 1.2) * (n - 1)) + (60 if blk.get("sub") else 0)
    if k == "code":
        s = blk.get("size", 30 if WIDE else 36)
        return 60 + int(len(blk["lines"]) * s * 1.55) + 30
    if k == "timeline": return len(blk["nodes"]) * (98 if WIDE else 128) + 10
    if k == "counter": return int(blk.get("size", 230 if WIDE else 300) * 1.15 + 90)
    if k == "compare": return 380 if WIDE else 720
    if k == "shock": return int(sum(l[1] for l in blk["lines"]) * (1.35 if WIDE else 1.15) + 90)
    if k == "strike": return 230 if WIDE else 440
    if k == "ba": return 60 + int(len(blk["before"]) * (30 if WIDE else 34) * 1.55) + 100
    if k == "flow": return 250 if WIDE else 280
    if k == "note": return 110 if WIDE else 150
    if k == "poll": return 250 if WIDE else 420
    if k == "predict": return 60 + int(len(blk["lines"]) * (30 if WIDE else 36) * 1.55) + 150
    if k == "mystery": return 200 if WIDE else 300
    if k == "gain": return 230 if WIDE else 330
    if k == "zoom": return zoom_geom(blk, width)["total"]
    if k == "phone": return 600 if WIDE else 760
    if k == "cta": return 220 if WIDE else 260
    if k in EXTRA_H: return EXTRA_H[k](blk, width)
    return 100


def layout(blocks, reserve=0, top=True, cw=None, square=False):
    """returns list of (blk, box) with fixed positions."""
    items = []
    blocks = [b for b in blocks if not b.get("abs")]
    # rows: ('row', [b1, b2]) -> wide side by side, reel stacked
    flat = []
    for b in blocks:
        if b["k"] == "row":
            flat.append(b)
        else:
            flat.append(b)
    heights = []
    for b in flat:
        if b["k"] == "tiles":
            n = len(b["items"])
            if WIDE:
                tw = (RW_ - (n - 1) * 30) / n
                heights.append(min(tw, 470) if (square or b.get("square")) else max(max(block_h(it, tw) for it in b["items"]), 330))
            else:
                heights.append(sum(block_h(it, RW_) for it in b["items"]) + GAP * (n - 1))
            continue
        if b["k"] == "row":
            subs = b["items"]
            if WIDE:
                gw = (RW_ - 40) // 2
                ws = [b.get("w0", gw), None]
                w0 = int(RW_ * b.get("split", 0.5)) - 20; w1 = RW_ - w0 - 40
                hh = max(block_h(subs[0], w0), block_h(subs[1], w1))
            else:
                hh = sum(block_h(s, RW_) for s in subs) + GAP * (len(subs) - 1)
            heights.append(hh)
        else:
            heights.append(block_h(b, RW_))
    total = sum(heights) + GAP * (len(flat) - 1)
    avail = RY1 - reserve - RY0
    y = RY0 + max(0, (avail - total)) * (0.0 if top else 0.4)
    for b, hh in zip(flat, heights):
        if b["k"] == "tiles":
            n = len(b["items"])
            if WIDE:
                tw = (RW_ - (n - 1) * 30) / n
                for i, it in enumerate(b["items"]): items.append((it, (RX0 + i * (tw + 30), y, RX0 + i * (tw + 30) + tw, y + hh)))
            else:
                yy = y
                for it in b["items"]:
                    h_ = block_h(it, RW_); items.append((it, (RX0, yy, RX1, yy + h_))); yy += h_ + GAP
        elif b["k"] == "row":
            subs = b["items"]
            if WIDE:
                w0 = int(RW_ * b.get("split", 0.5)) - 20; w1 = RW_ - w0 - 40
                hs = [block_h(subs[0], w0), block_h(subs[1], w1)]
                items.append((subs[0], (RX0, y + (hh - hs[0]) / 2, RX0 + w0, y + (hh - hs[0]) / 2 + hs[0])))
                items.append((subs[1], (RX0 + w0 + 40, y + (hh - hs[1]) / 2, RX1, y + (hh - hs[1]) / 2 + hs[1])))
            else:
                yy = y
                for s in reversed(subs):
                    h_ = block_h(s, RW_); items.append((s, (RX0, yy, RX1, yy + h_))); yy += h_ + GAP
        else:
            if cw and b["k"] == "card" and WIDE:
                wcw = RW_ * cw; items.append((b, ((RX0 + RX1) / 2 - wcw / 2, y, (RX0 + RX1) / 2 + wcw / 2, y + hh)))
            else: items.append((b, (RX0, y, RX1, y + hh)))
        y += hh + GAP
    return items


# ------------------------------------------------------------------ block drawers
def bob(t, k): return 2.0 * math.sin(2 * math.pi * t / 3.6 + k)


def toks_draw(d, cx, cy, text, size, key, al=1.0, wlist=None, t=0.0):
    raw = text.split(" "); words = []
    for w in raw:
        if words and w.isascii() and words[-1].isascii(): words[-1] += " " + w
        else: words.append(w)
    def wl(w): return F(MONO, int(size * 0.9)).getlength(w) if w.isascii() else F(ARB, size).getlength(w, direction="rtl", language="ar")
    ws = [wl(w) for w in words]; sp = size * 0.28; total = sum(ws) + sp * (len(words) - 1); x = cx + total / 2
    for w, wd in zip(words, ws):
        hit = bool(key) and key in w; col = OR if hit else PAPER
        for tw_, wd_ in (wlist or []):
            if wd_ in w and t >= tw_ - 0.05:
                hit = True; q_ = prog(t, tw_ - 0.05, tw_ + 0.45)
                if q_ < 1: d.rounded_rectangle((x - wd - 12, cy - size * 0.7, x + 12, cy + size * 0.7), 14, fill=A(OR, 0.35 * (1 - q_) * al))
        if w.isascii(): d.text((x - wd / 2, cy), w, font=F(MONO, int(size * 0.9)), fill=A(col, al), anchor="mm")
        else: d.text((x - wd / 2, cy), w, font=F(ARB, size), fill=A(col, al), anchor="mm", direction="rtl", language="ar")
        if hit: d.line([(x - wd, cy + size * 0.7), (x, cy + size * 0.7)], fill=A(OR, al), width=5)
        x -= wd + sp


def draw_card(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 28 + bob(t, k)
    hl = 1 - ss(prog(t, b["t"], b["t"] + 1.5))
    ok = b.get("ok"); st = b.get("style", "classic")
    col = RED if ok is False else (GRN if ok else OR)
    pr = prog(t, b["t"], b["t"] + 0.55)
    if 0 < pr < 1:
        for ring_k, ring_d in ((0, 0.0), (1, 0.12)) if b.get("key") else ((0, 0.0),):
            q = prog(t, b["t"] + ring_d, b["t"] + ring_d + 0.55)
            if 0 < q < 1:
                g = 6 + 26 * ss(q)
                d.rounded_rectangle((x0 - g, y0 + dy - g, x1 + g, y1 + dy + g), 26 + g, outline=A(OR, 0.7 * (1 - q)), width=4)
    cy = (y0 + y1) / 2 + dy; cx = (x0 + x1) / 2; s = b.get("size", CS)
    lines = card_lines(b, x1 - x0)
    def body(cxx, rtl_right=None, color=PAPER, dyy=0):
        for j, ln in enumerate(lines):
            yy = cy + dyy + (j - (len(lines) - 1) / 2) * s * 1.3
            if b.get("words"): toks_draw(d, cxx, yy, ln, s, None, al, b.get("words"), t)
            else: txt(d, (cxx, yy), ln, s, A(color, al))
    if st == "proposed":
        y0d, y1d = y0 + dy, y1 + dy
        d.rounded_rectangle((x0, y0d, x1, y1d), 22, fill=A(CARDC, al), outline=A(lerp((70, 73, 82), OR, hl), al), width=3)
        d.rounded_rectangle((x0, y0d, x0 + 16, y1d), 8, fill=A(col, al))
        tag = b.get("tag")
        if tag:
            f = F(MONO, 22); w = f.getlength(tag) + 40
            d.rounded_rectangle((x1 - 24 - w, y0d + 14, x1 - 24, y0d + 52), 19, outline=A(OR, al), width=3)
            d.text((x1 - 24 - w / 2, y0d + 33), tag, font=f, fill=A(OR, al), anchor="mm")
        if len(lines) == 1 or b.get("words"):
            for j_, ln_ in enumerate(lines): toks_draw(d, cx + 20, cy + (20 if tag else 0) + (j_ - (len(lines) - 1) / 2) * s * 1.3, ln_, s, b.get("key"), al, b.get("words"), t)
        else: body(cx + 20, dyy=(20 if tag else 0))
    elif st == "glass":
        y0d, y1d = y0 + dy, y1 + dy
        d.rounded_rectangle((x0, y0d, x1, y1d), 26, fill=CARD_GLASS + (int(215 * al),), outline=(255, 255, 255, int(120 * al)), width=2)
        d.rounded_rectangle((x0 + 3, y0d + 3, x1 - 3, y0d + (y1d - y0d) * 0.4), 24, fill=(255, 255, 255, int(14 * al)))
        if ok is not None and (x1 - x0) < 600: badge(d, x0 + 40, y0d + 40, ok, al, r=22); body(cx, dyy=18)
        else:
            if ok is not None: badge(d, x0 + 56, cy, ok, al, r=26)
            body(cx + (30 if ok is not None else 0))
    elif st == "numbers":
        y0d, y1d = y0 + dy, y1 + dy
        d.rounded_rectangle((x0, y0d, x1, y1d), 26, fill=A(CARD_NUM, al), outline=A(lerp((60, 63, 72), OR, hl), al), width=3)
        if (x1 - x0) < 600: pass   # squares: no index numbers (his request 2026-10-30)
        else: d.text((x1 - 50, cy + 6), "%02d" % (b.get("idx", 0) + 1), font=F(MONO, 110), fill=A(lerp((30, 32, 38), OR, 0.35), al), anchor="rm")
        if ok is not None and (x1 - x0) < 600:
            d.rounded_rectangle((x0 + 16, y0d + 16, x0 + 116, y0d + 64), 24, fill=A(col, 0.18 * al), outline=A(col, al), width=3)
            d.text((x0 + 66, y0d + 40), (LBL_OK if ok else LBL_BAD), font=F(ARB, 26), fill=A(col, al), anchor="mm", direction="rtl", language="ar"); body(cx, dyy=24)
        elif ok is not None:
            d.rounded_rectangle((x0 + 28, cy - 32, x0 + 178, cy + 32), 32, fill=A(col, 0.18 * al), outline=A(col, al), width=3)
            d.text((x0 + 103, cy), (LBL_OK if ok else LBL_BAD), font=F(ARB, 32), fill=A(col, al), anchor="mm", direction="rtl", language="ar"); body(cx)
        else: body(cx)
    else:
        sh = col if ok is not None else OR
        hard(d, (x0, y0, x1, y1), CARDC, sh, border=lerp(PAPER, OR, hl), a=al, r=26, off=9, bw=4, dy=dy)
        off = 0
        if ok is not None and (x1 - x0) < 600: badge(d, x0 + 44, y0 + dy + 44, ok, al, r=22); body(cx, dyy=22)
        else:
            if ok is not None: badge(d, x0 + 54, cy, ok, al); off = 34
            body(cx + off)


def draw_chip(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 22 + bob(t, k)
    s = b.get("size", 36 if WIDE else 42)
    f = F(MONO if b["text"].isascii() else ARB, s)
    w = min(x1 - x0, f.getlength(b["text"]) + 90); cx = (x0 + x1) / 2
    hard(d, (cx - w / 2, y0, cx + w / 2, y1), CARDC, OR, a=al, r=30, off=6, bw=3, dy=dy)
    txt(d, (cx, (y0 + y1) / 2 + dy), b["text"], s, A(PAPER, al))


def draw_title(d, box, b, t, k):
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 30 + bob(t, k)
    hl = 1 - ss(prog(t, b["t"], b["t"] + 1.5))
    hard(d, (x0, y0, x1, y1), CARDC, OR, border=lerp(PAPER, OR, hl), a=al, r=30, off=11, bw=5, dy=dy)
    s = b.get("size", 56 if WIDE else 64)
    lines = wrap(b["text"], F(ARB, s), (x1 - x0) - 120) if not b["text"].isascii() else [b["text"]]
    cy = (y0 + y1) / 2 + dy - (28 if b.get("sub") else 0)
    for j, ln in enumerate(lines):
        txt(d, ((x0 + x1) / 2, cy + (j - (len(lines) - 1) / 2) * s * 1.2), ln, s, A(OR, al))
    if b.get("sub"):
        txt(d, ((x0 + x1) / 2, y1 - 52 + dy), b["sub"], int(s * 0.55), A(GRAYC, al))


def draw_code(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 28
    if b.get("shake") is not None:
        q_ = t - b["shake"]
        if 0 < q_ < 0.5: x0 += math.sin(q_ * 70) * 12 * (1 - q_ / 0.5); x1 += math.sin(q_ * 70) * 12 * (1 - q_ / 0.5)
    hard(d, (x0, y0, x1, y1), (18, 20, 25), GRAYC, border=GRAYC, a=al, r=26, off=8, bw=3, dy=dy)
    fo = None
    for ft_, fl_ in b.get("focus", []):
        if t >= ft_: fo = fl_
    for j, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 26 + j * 26, y0 + 20 + dy, x0 + 42 + j * 26, y0 + 36 + dy), fill=A(c, al))
    d.text((x0 + 130, y0 + 28 + dy), b.get("file", ""), font=F(MONO, 22), fill=A(GRAYC, al), anchor="lm")
    s = b.get("size", 30 if WIDE else 36); f = F(MONO, s)
    for j, ln_ in enumerate(b["lines"]):
        ts, text, cps = ln_[0], ln_[1], ln_[2]
        n = int(max(0, (t - ts)) * cps); n = min(n, len(text))
        if n <= 0: continue
        cols = colorize(text) if len(ln_) < 4 else [ln_[3]] * len(text); xx = x0 + 34; yy = y0 + 60 + j * s * 1.55 + s * 0.8 + dy
        la = al * (0.32 if (fo is not None and j != fo) else 1.0)
        if fo is not None and j == fo:
            hl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(hl).rounded_rectangle((x0 + 14, yy - s * 0.75, x1 - 14, yy + s * 0.75), 10, fill=OR + (int(46 * al),), outline=OR + (int(190 * al),), width=3)
            d._image.alpha_composite(hl)
        for ci in range(n):
            ch = text[ci]; d.text((xx, yy), ch, font=f, fill=A(cols[ci], la), anchor="lm"); xx += f.getlength(ch)


def tl_geom(b, box):
    x0, y0, x1, y1 = box
    sp = 98 if WIDE else 128
    cx = x1 - 70
    return sp, cx


def draw_timeline(d, box, b, t, k):
    x0, y0, x1, y1 = box; sp, cx = tl_geom(b, box); n = len(b["nodes"]); r = 34 if WIDE else 40
    ts = [nd[0] for nd in b["nodes"]]
    for j, (te, label, sub, st) in enumerate(b["nodes"]):
        al = E(t, te)
        cy = y0 + 50 + j * sp
        if j > 0:  # connector line grows from previous node
            la = ss(prog(t, te - 0.1, te + 0.35)); py = y0 + 50 + (j - 1) * sp
            d.line([(cx, py + r), (cx, py + r + (cy - py - 2 * r) * la)], fill=A(OR, 0.9), width=5)
        if al < 0.01: continue
        dy = (1 - al) * 24
        hl = 1 - ss(prog(t, te, te + 1.4)); col = {"ok": GRN, "bad": RED}.get(st, OR)
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.6)
        if hl > 0.01: d.ellipse((cx - r - 12 - 8 * pulse, cy + dy - r - 12 - 8 * pulse, cx + r + 12 + 8 * pulse, cy + dy + r + 12 + 8 * pulse), outline=A(col, 0.55 * al * hl), width=3)
        d.ellipse((cx - r, cy + dy - r, cx + r, cy + dy + r), fill=A(CARDC, al), outline=A(col, al), width=5)
        sym = {"ok": "✓", "bad": "✕"}.get(st, str(j + 1))
        d.text((cx, cy + dy), sym, font=F("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(r * 0.95)), fill=A(col, al), anchor="mm")
        ls = 40 if WIDE else 46
        txt(d, (cx - r - 28, cy + dy - (16 if sub else 0)), label, ls, A(PAPER, al), anchor="rm")
        if sub: txt(d, (cx - r - 28, cy + dy + 24), sub, int(ls * 0.66), A(GRAYC, al), anchor="rm")


def draw_counter(d, box, b, t, k):
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 30; cx = (x0 + x1) / 2
    p = ss(prog(t, b["t0"], b["t1"])); v = b["v0"] + (b["v1"] - b["v0"]) * p
    if b.get("mode") == "clock":
        mins = int(v * 60); s_ = f"{mins // 60:02d}:{mins % 60:02d}"
    else: s_ = str(int(round(v)))
    size = b.get("size", 230 if WIDE else 300)
    hl = 1 - ss(prog(t, b["t1"], b["t1"] + 0.6))
    ny = y0 + size * 0.55 + dy
    d.text((cx, ny), s_, font=F(MONO, size), fill=A(lerp(PAPER, OR, 0.7 + 0.3 * (1 - hl)), al), anchor="mm")
    ly = y0 + size * 1.15 + dy
    d.line([(cx - size * 0.9, ly), (cx + size * 0.9, ly)], fill=A(OR, al), width=6)
    txt(d, (cx, ly + 38), b["label"], 50 if WIDE else 58, A(PAPER, al))


def zoom_geom(b, width):
    s = b.get("size", 28 if WIDE else 34); n = len(b["lines"])
    bh = 60 + int(n * s * 1.6) + 30
    R = 150 if WIDE else 185
    return {"s": s, "bh": bh, "R": R, "total": bh + int(R * 1.8)}


def draw_zoom(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; g = zoom_geom(b, x1 - x0); dy = (1 - al) * 28
    hard(d, (x0, y0, x1, y0 + g["bh"]), (18, 20, 25), GRAYC, border=GRAYC, a=al, r=26, off=8, bw=3, dy=dy)
    for j, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 26 + j * 26, y0 + 20 + dy, x0 + 42 + j * 26, y0 + 36 + dy), fill=A(c, al))
    d.text((x0 + 130, y0 + 28 + dy), b.get("file", "Console"), font=F(MONO, 22), fill=A(GRAYC, al), anchor="lm")
    f = F(MONO, g["s"]); li, tgt = b["target"]
    tpos = None
    for j, text in enumerate(b["lines"]):
        yy = y0 + 60 + j * g["s"] * 1.6 + g["s"] * 0.8 + dy
        d.text((x0 + 30, yy), text, font=f, fill=A(RED if j == 0 else PAPER, al), anchor="lm")
        if j == li and tgt in text:
            i0 = text.index(tgt); xa = x0 + 30 + f.getlength(text[:i0]); xb = xa + f.getlength(tgt)
            tpos = (xa, xb, yy)
    za = E(t, b["t_zoom"], 0.4)
    if za < 0.01 or tpos is None: return
    xa, xb, yy = tpos; R = g["R"]
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.4)
    d.rounded_rectangle((xa - 10, yy - g["s"] * 0.75, xb + 10, yy + g["s"] * 0.75), 12, outline=A(OR, za), width=4)
    ccx, ccy = x1 - R - 40, y0 + g["bh"] + R * 0.85 + dy
    tx, ty = (xa + xb) / 2, yy + g["s"] * 0.75
    d.line([(tx, ty), (ccx - R * 0.25, ccy - R + 6)], fill=A(OR, za * 0.9), width=4)
    d.ellipse((ccx - R, ccy - R, ccx + R, ccy + R), fill=A((14, 15, 19), za), outline=A(OR, za), width=7)
    d.ellipse((ccx - R + 12, ccy - R + 12, ccx + R - 12, ccy + R - 12), outline=A(OR, za * (0.25 + 0.2 * pulse)), width=3)
    lines2 = b.get("magnify", [tgt])
    s2 = int(R * 0.17)
    for j, ln in enumerate(lines2):
        d.text((ccx, ccy + (j - (len(lines2) - 1) / 2) * s2 * 1.5), ln, font=F(MONO, s2), fill=A(PAPER if j else OR, za), anchor="mm")


def draw_phone(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 34 + bob(t, k)
    pw = min(x1 - x0, 400 if WIDE else 470); ph = (y1 - y0); cx = (x0 + x1) / 2
    px0, px1 = cx - pw / 2, cx + pw / 2
    hard(d, (px0, y0, px1, y0 + ph), (16, 17, 21), OR, border=PAPER, a=al, r=54, off=10, bw=5, dy=dy)
    d.rounded_rectangle((cx - 60, y0 + 18 + dy, cx + 60, y0 + 34 + dy), 8, fill=A((40, 42, 48), al))
    # screen header
    txt(d, (cx, y0 + 80 + dy), b.get("title", "App"), 28 if WIDE else 32, A(GRAYC, al))
    items = b["items"]; iy = y0 + 140
    for j, (te, text, st) in enumerate(items):
        ia = E(t, te)
        if ia < 0.01: continue
        col = {"bad": RED, "ok": GRN}.get(st, PAPER)
        hh = 66 if WIDE else 80
        yy = iy + j * (hh + 18) + (1 - ia) * 18 + dy
        d.rounded_rectangle((px0 + 26, yy, px1 - 26, yy + hh), 18, fill=A((30, 32, 38), ia), outline=A(col if st else GRAYC, ia), width=3)
        s = 22 if WIDE else 26
        f = F(MONO if text.isascii() else ARB, s)
        if f.getlength(text) > pw - 80: s = int(s * (pw - 80) / f.getlength(text))
        txt(d, (cx, yy + hh / 2), text, s, A(col, ia))


def draw_cta(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    w = min(1000, x1 - x0); h = 190 if WIDE else 230
    hard(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), (18, 20, 25), GRAYC, border=GRAYC, a=al, r=34, off=10, bw=3, dy=(1 - al) * 28)
    txt(d, (cx + w / 2 - 70, cy + (1 - al) * 28), "اكتبلي إجابتك في الكومنتات", 52 if WIDE else 54, A(PAPER, al), anchor="rm")
    if int(t * 2) % 2 == 0: d.rectangle((cx - w / 2 + 60, cy - 44, cx - w / 2 + 66, cy + 44), fill=A(OR, al))


DRAW = {"card": draw_card, "chip": draw_chip, "title": draw_title, "code": draw_code, "timeline": draw_timeline,
        "counter": draw_counter, "zoom": draw_zoom, "phone": draw_phone, "cta": draw_cta}


def draw_compare(d, box, b, t, k):
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    x0, y0, x1, y1 = box
    if WIDE:
        pw = (x1 - x0 - 40) / 2; boxes = [(x1 - pw, y0, x1, y1), (x0, y0, x0 + pw, y1)]
    else:
        ph = (y1 - y0 - GAP) / 2; boxes = [(x0, y0, x1, y0 + ph), (x0, y0 + ph + GAP, x1, y1)]
    for pi, (bx0, by0, bx1, by1) in enumerate(boxes):
        title, items = b["panels"][pi]
        first = items[0][0] if items else b["t"]
        pa = E(t, min(first, b["t"] + 0.2 * pi) if pi == 0 else first - 0.2, 0.3)
        if pa < 0.01: continue
        dy = (1 - pa) * 30; act = pi == 1
        col = OR if act else GRAYC
        hard(d, (bx0, by0, bx1, by1), (20, 22, 27), col if act else (40, 42, 48), border=col, a=pa, r=28, off=9 if act else 5, bw=4 if act else 3, dy=dy)
        txt(d, ((bx0 + bx1) / 2, by0 + 48 + dy), title, 46 if WIDE else 52, A(OR if act else PAPER, pa))
        d.line([(bx0 + 40, by0 + 92 + dy), (bx1 - 40, by0 + 92 + dy)], fill=A(col, pa * 0.6), width=3)
        n = len(items); area = (by1 - by0 - 110)
        for j, (te, text) in enumerate(items):
            ia = E(t, te, 0.3)
            if ia < 0.01: continue
            yy = by0 + 110 + area * (j + 0.5) / max(n, 1) + (1 - ia) * 16 + dy
            d.ellipse((bx1 - 64, yy - 9, bx1 - 46, yy + 9), fill=A(GRN if act else GRAYC, ia))
            txt(d, (bx1 - 84, yy), text, 40 if WIDE else 46, A(PAPER, ia), anchor="rm")


def flow_geom(b, box):
    x0, y0, x1, y1 = box; n = len(b["nodes"]); nw = 250 if WIDE else 240; nh = 100 if WIDE else 110
    cy = (y0 + y1) / 2
    xs = [x1 - nw / 2 - 20 - i * ((x1 - x0 - nw - 40) / (n - 1)) for i in range(n)]   # first node on the right (RTL)
    return xs, cy, nw, nh


def draw_flow(d, box, b, t, k):
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    xs, cy, nw, nh = flow_geom(b, box); dy = (1 - al) * 26
    for i in range(len(xs) - 1):
        xa, xb = xs[i], xs[i + 1]
        for off, back in ((-18, False), (18, True)):
            d.line([(xa - nw / 2, cy + off + dy), (xb + nw / 2, cy + off + dy)], fill=A((70, 73, 82), al), width=3)
            hx = xb + nw / 2 if not back else xa - nw / 2; sgn = 1 if not back else -1
            d.polygon([(hx, cy + off + dy), (hx + sgn * 16, cy + off - 9 + dy), (hx + sgn * 16, cy + off + 9 + dy)], fill=A((70, 73, 82), al))
    for i, (cx, lab) in enumerate(zip(xs, b["nodes"])):
        arr = [st for st in b["steps"] if st[2] == i]
        pulse = 0.0
        for st in arr:
            q = prog(t, st[0] + 0.85, st[0] + 1.35)
            if 0 < q < 1: pulse = max(pulse, 1 - q)
        col = lerp(PAPER, OR, min(1, pulse * 1.5))
        hard(d, (cx - nw / 2, cy - nh / 2, cx + nw / 2, cy + nh / 2), CARDC, OR if pulse > 0 else (40, 42, 48), border=col, a=al, r=24, off=7, bw=4, dy=dy)
        txt(d, (cx, cy + dy), lab, 34 if WIDE else 32, A(PAPER, al))
    for (te, i, j, lab) in b["steps"]:
        q = prog(t, te, te + 0.85)
        if q <= 0 or q >= 1: continue
        e = ss(q); ya = cy + (-18 if xs[j] < xs[i] else 18) + dy
        x = xs[i] + (xs[j] - xs[i]) * e
        for tr in range(1, 5):
            e2 = ss(max(0, q - tr * 0.04)); x2 = xs[i] + (xs[j] - xs[i]) * e2
            d.ellipse((x2 - 9, ya - 9, x2 + 9, ya + 9), fill=A(OR, 0.18 * (5 - tr)))
        d.ellipse((x - 13, ya - 13, x + 13, ya + 13), fill=A(OR, 1), outline=A(PAPER, 1), width=3)
        txt(d, (x, ya - 64), lab, 28 if WIDE else 26, A(OR, 1))


def draw_ring(d, box, b, t, k):
    al = E(t, b["t0"], 0.3) * (1 - ss(prog(t, b["t1"], b["t1"] + 0.35)))
    if al < 0.01: return
    cx, cy = (W - 190, 175) if WIDE else (W - 130, 270); R = 64 if WIDE else 56
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=A((18, 20, 25), al), outline=A((60, 63, 72), al), width=6)
    frac = cl((b["t1"] - t) / (b["t1"] - b["t0"]))
    d.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * frac, fill=A(OR, al), width=9)
    n = int(math.ceil(b["t1"] - t)); n = max(n, 0)
    d.text((cx, cy), str(n), font=F(MONO, 58 if WIDE else 52), fill=A(PAPER, al), anchor="mm")
    txt(d, (cx, cy + R + 34), b.get("label", ""), 34, A(OR, al))


DRAW["compare"] = draw_compare; DRAW["flow"] = draw_flow; DRAW["ring"] = draw_ring


def draw_shock(d, box, b, t, k):
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    x0, y0, x1, y1 = box; q = prog(t, b["t"] - 0.12, b["t"] + 0.4)
    pop = 0.86 + 0.14 * ss(q) + 0.06 * math.sin(math.pi * q) ; fade = al
    hard(d, (x0, y0, x1, y1), CARDC, OR, border=PAPER, a=fade, r=40, off=14, bw=6, dy=(1 - al) * 24)
    tot = sum(l[1] for l in b["lines"]) * (1.35 if WIDE else 1.15); yy = (y0 + y1) / 2 - tot / 2 + (1 - al) * 24
    for text, size, col in b["lines"]:
        sz = int(size * (1.0 if WIDE else 0.85) * pop)
        yy += size * (1.35 if WIDE else 1.15) / 2
        txt(d, ((x0 + x1) / 2, yy), text, sz, A(col, fade)); yy += size * (1.35 if WIDE else 1.15) / 2


def draw_strike(d, box, b, t, k):
    x0, y0, x1, y1 = box
    if WIDE:
        pw = (x1 - x0 - 40) / 2; boxes = [(x1 - pw, y0, x1, y1), (x0, y0, x0 + pw, y1)]
    else:
        ph = (y1 - y0 - GAP) / 2; boxes = [(x0, y0, x1, y0 + ph), (x0, y0 + ph + GAP, x1, y1)]
    # wrong
    wa = E(t, b["t"]); st = ss(prog(t, b["t_strike"], b["t_strike"] + 0.4))
    if wa > 0.01:
        bx0, by0, bx1, by1 = boxes[0]; dy = (1 - wa) * 26
        hard(d, (bx0, by0, bx1, by1), CARDC, RED, border=RED, a=wa, r=28, off=9, bw=4, dy=dy)
        badge(d, bx0 + 56, (by0 + by1) / 2 + dy, False, wa, r=28)
        cx, cy = (bx0 + bx1) / 2 + 30, (by0 + by1) / 2 + dy
        txt(d, (cx, cy), b["wrong"], 48, A(lerp(PAPER, (120, 122, 130), st), wa))
        if st > 0:
            wl = F(ARB, 48).getlength(b["wrong"], direction="rtl", language="ar") if not b["wrong"].isascii() else F(MONO, 48).getlength(b["wrong"])
            xr = cx + wl / 2 + 20; xl = xr - (wl + 40) * st
            d.line([(xr, cy + 4), (xl, cy + 4)], fill=A(RED, wa), width=10)
    ra = E(t, b["t_right"])
    if ra > 0.01:
        bx0, by0, bx1, by1 = boxes[1]; dy = (1 - ra) * 26
        hard(d, (bx0, by0, bx1, by1), CARDC, GRN, border=GRN, a=ra, r=28, off=9, bw=4, dy=dy)
        badge(d, bx0 + 56, (by0 + by1) / 2 + dy, True, ra, r=28)
        txt(d, ((bx0 + bx1) / 2 + 30, (by0 + by1) / 2 + dy), b["right"], 48, A(PAPER, ra))


def draw_ba(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 28
    hard(d, (x0, y0, x1, y1), (18, 20, 25), GRAYC, border=GRAYC, a=al, r=26, off=8, bw=3, dy=dy)
    pw, ph = int(x1 - x0), int(y1 - y0); s_ = 30 if WIDE else 34; f = F(MONO, s_)
    q = ss(prog(t, b["t_slide"], b["t_slide"] + 1.3)); xdiv = pw - 40 - q * (pw / 2 - 40)
    A1 = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); B1 = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    da, db = ImageDraw.Draw(A1), ImageDraw.Draw(B1)
    for j, ln in enumerate(b["before"]): da.text((40, 70 + j * s_ * 1.55), ln, font=f, fill=A(RED if j == 0 else GRAYC, al), anchor="lm")
    for j, ln in enumerate(b["after"]): db.text((pw / 2 + 40, 70 + j * s_ * 1.55), ln, font=f, fill=A(GRN if j == 0 else GRAYC, al), anchor="lm")
    da.text((pw / 4, ph - 44), "BEFORE", font=F(MONO, 30), fill=A(RED, al), anchor="mm"); db.text((pw * 3 / 4, ph - 44), "AFTER", font=F(MONO, 30), fill=A(GRN, al), anchor="mm")
    cx_ = int(max(0, min(pw, xdiv)))
    out = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); out.paste(A1.crop((0, 0, cx_, ph)), (0, 0)); out.paste(B1.crop((cx_, 0, pw, ph)), (cx_, 0))
    d._image.alpha_composite(out, (int(x0), int(y0 + dy)))
    d.rectangle((x0 + xdiv - 2, y0 + 20 + dy, x0 + xdiv + 2, y1 - 20 + dy), fill=A(OR, al))
    d.ellipse((x0 + xdiv - 28, (y0 + y1) / 2 - 28 + dy, x0 + xdiv + 28, (y0 + y1) / 2 + 28 + dy), fill=A(OR, al), outline=A(INK, al), width=4)
    d.text((x0 + xdiv, (y0 + y1) / 2 + dy), "<>", font=F(MONO, 26), fill=A(INK, al), anchor="mm")


DRAW["shock"] = draw_shock; DRAW["strike"] = draw_strike; DRAW["ba"] = draw_ba


# ------------------------------------------------------------------ absolute overlays: subscribe/follow button, promise pill, ring
def _bell(d, bx, by, a, swing=0.0):
    d.ellipse((bx - 46, by - 46, bx + 46, by + 46), fill=A(OR, a), outline=A(INK, a), width=5)
    d.polygon([(bx - 20, by + 14), (bx - 13, by - 16), (bx, by - 27), (bx + 13, by - 16), (bx + 20, by + 14)], fill=A(INK, a))
    d.rounded_rectangle((bx - 26, by + 11, bx + 26, by + 20), 5, fill=A(INK, a)); d.ellipse((bx - 6, by + 20, bx + 6, by + 32), fill=A(INK, a))
    for r_, al in ((62, 0.7), (80, 0.4)):
        sw = swing * 12
        d.arc((bx - r_, by - r_, bx + r_, by + r_), 200 + sw, 250 + sw, fill=A(OR, al * a), width=5); d.arc((bx - r_, by - r_, bx + r_, by + r_), 290 - sw, 340 - sw, fill=A(OR, al * a), width=5)


def abs_button(OV, b, t):
    t0, t1 = b["t0"], b["t1"]
    al = ss(prog(t, t0, t0 + 0.35)) * (1 - ss(prog(t, t1 - 0.35, t1)))
    if al < 0.01: return
    d = ImageDraw.Draw(OV)
    w, h = (560, 130) if WIDE else (640, 144); cx, cy = (W / 2, 905) if WIDE else (W / 2, 1640)
    w = b.get("w", w); h = b.get("h", h); cx = b.get("cx", cx); cy = b.get("cy", cy); stat = b.get("static", False)
    q = prog(t, t0, t0 + 0.4); sc = 0.8 + 0.2 * ss(q) + 0.08 * math.sin(math.pi * q)
    if stat: sc *= 1 + 0.025 * math.sin(t * 3.0)
    t_press = t0 + 1.5 if not stat else 1e9; press = prog(t, t_press, t_press + 0.15) * (1 - prog(t, t_press + 0.15, t_press + 0.4))
    sc *= 1 - 0.05 * press; w, h = w * sc, h * sc; cy += (1 - al) * 40 + 8 * press
    done = t >= t_press + 0.1; kind = b["kind"]
    label = ("SUBSCRIBED" if done else "SUBSCRIBE") if kind == "subscribe" else ("FOLLOWING" if done else "FOLLOW")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((cx - w / 2 + 6, cy - h / 2 + 22, cx + w / 2 + 6, cy + h / 2 + 22), 44, fill=(0, 0, 0, int(170 * al)))
    OV.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d.rounded_rectangle((cx - w / 2, cy - h / 2 + 12, cx + w / 2, cy + h / 2 + 12), 44, fill=A(ORD, al))
    face = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); fd = ImageDraw.Draw(face)
    for yy in range(int(h)): fd.line([(0, yy), (w, yy)], fill=A(lerp((34, 36, 42), (10, 11, 13), yy / h), al))
    m = Image.new("L", face.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 44, fill=255); face.putalpha(m); OV.alpha_composite(face, (int(cx - w / 2), int(cy - h / 2)))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 44, outline=A(OR, al), width=6)
    d.text((cx + 34, cy), label, font=F(MONO, int(48 * sc * (w / 560 if w < 560 else 1))), fill=A(OR, al), anchor="mm")
    ix = cx - w / 2 + 62
    if done or kind == "follow":
        d.ellipse((ix - 32, cy - 32, ix + 32, cy + 32), fill=A(OR, al))
        if done: d.line([(ix - 15, cy + 2), (ix - 3, cy + 14), (ix + 17, cy - 13)], fill=A(INK, al), width=9)
        else: d.line([(ix - 15, cy), (ix + 15, cy)], fill=A(INK, al), width=8); d.line([(ix, cy - 15), (ix, cy + 15)], fill=A(INK, al), width=8)
    if kind == "subscribe":
        swing = math.sin((t - t_press) * 18) * math.exp(-(t - t_press) * 2.5) if t > t_press else 0.0
        _bell(d, cx + w / 2 - 16, cy - h / 2 + 6, al, swing)
    # cursor travels in, ripple on press
    cq = ss(prog(t, t0 + 0.5, t0 + 1.4))
    if cq > 0 and t < t_press + 0.9 and not stat:
        px = cx + w * 0.36 + (1 - cq) * 420; py = cy + h * 0.15 + (1 - cq) * 260; ca = al * (1 - ss(prog(t, t_press + 0.5, t_press + 0.9)))
        rp = prog(t, t_press, t_press + 0.7)
        if 0 < rp < 1:
            for r_ in (40 + 90 * rp, 20 + 60 * rp): d.ellipse((cx + w * 0.36 - r_, cy + h * 0.15 - r_, cx + w * 0.36 + r_, cy + h * 0.15 + r_), outline=A(OR, (1 - rp) * 0.8 * al), width=4)
        d.polygon([(px, py), (px + 10, py + 66), (px + 27, py + 48), (px + 50, py + 76), (px + 65, py + 62), (px + 42, py + 36), (px + 66, py + 30)], fill=A(PAPER, ca), outline=A(INK, ca))


def abs_promise(OV, b, t):
    t0, tu, t1 = b["t0"], b["t_unlock"], b["t1"]
    al = ss(prog(t, t0, t0 + 0.4)) * (1 - ss(prog(t, t1 - 0.4, t1)))
    if al < 0.01: return
    d = ImageDraw.Draw(OV); op = t >= tu
    text = b["open"] if op else b["locked"]; f = F(ARB, 30)
    w = f.getlength(text, direction="rtl", language="ar") + 130; h = 64
    x1 = W - 40 if True else 0; x0 = x1 - w; y = (H - 76) if WIDE else 1790; y0 = y - h / 2 + (1 - al) * 30
    pk = prog(t, tu, tu + 0.5); glow = math.sin(math.pi * pk) if 0 < pk < 1 else 0
    fill = OR if op else (20, 22, 27)
    d.rounded_rectangle((x0 - glow * 8, y0 - glow * 8, x1 + glow * 8, y0 + h + glow * 8), 36, fill=A(fill, al), outline=A(OR if not op else INK, al), width=4)
    d.text((x1 - 28 - (w - 130), y0 + h / 2 + 1), text, font=f, fill=A(PAPER if not op else INK, al), anchor="lm" if False else "rm", direction="rtl", language="ar") if False else txt(d, (x0 + 100 + (w - 130) / 2, y0 + h / 2), text, 30, A(PAPER if not op else INK, al))
    ix, iy = x0 + 48, y0 + h / 2
    if not op:
        d.rounded_rectangle((ix - 14, iy - 2, ix + 14, iy + 20), 5, fill=A(OR, al)); d.arc((ix - 10, iy - 22, ix + 10, iy + 6), 180, 360, fill=A(OR, al), width=5)
    else:
        d.line([(ix - 14, iy), (ix - 4, iy + 11), (ix + 15, iy - 12)], fill=A(INK, al), width=8)


ABS = {"button": abs_button, "promise": abs_promise}


def draw_poll(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 26; hh = 250 if WIDE else 420
    hard(d, (x0, y0, x1, y1), CARDC, OR, border=PAPER, a=al, r=28, off=9, bw=4, dy=dy)
    txt(d, ((x0 + x1) / 2, y0 + 44 + dy), b["q"], 38, A(PAPER, al))
    n = len(b["opts"]); q = ss(prog(t, b["t_fill"], b["t_fill"] + 1.4))
    for i, (lab, pct) in enumerate(b["opts"]):
        if WIDE:
            bx0 = x0 + 40; bx1 = x1 - 40; by0 = y0 + 90 + i * 70 + dy
        else:
            bx0 = x0 + 40; bx1 = x1 - 40; by0 = y0 + 100 + i * 150 + dy
        bh = 54 if WIDE else 110
        d.rounded_rectangle((bx0, by0, bx1, by0 + bh), 16, fill=A((34, 36, 42), al))
        wv = (bx1 - bx0) * (1 if b.get("nopct") else pct / 100) * q
        if b.get("nopct"):
            pl = 0.5 + 0.5 * math.sin(t * 4 + i * 3.14)
            d.rounded_rectangle((bx0, by0, bx1, by0 + bh), 16, outline=A(OR, al * (0.5 + 0.5 * pl)), width=4)
            d.text((bx0 + 20, by0 + bh / 2), lab, font=F(ARB, 32 if WIDE else 36) if not lab.isascii() else F(MONO, 30 if WIDE else 34), fill=A(PAPER, al), anchor="lm", direction="rtl" if not lab.isascii() else None, language="ar" if not lab.isascii() else None) if False else txt(d, ((bx0 + bx1) / 2, by0 + bh / 2), lab, 32 if WIDE else 36, A(PAPER, al))
            continue
        if wv > 4: d.rounded_rectangle((bx0, by0, bx0 + wv, by0 + bh), 16, fill=A(OR if i == b.get("win", 0) else GRAYC, al))
        d.text((bx0 + 20, by0 + bh / 2), lab, font=F(MONO, 28 if WIDE else 34), fill=A(INK if wv > 200 else PAPER, al), anchor="lm")
        d.text((bx1 - 20, by0 + bh / 2), "%d%%" % int(pct * q), font=F(MONO, 28 if WIDE else 34), fill=A(PAPER, al), anchor="rm")


def draw_predict(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 28
    hard(d, (x0, y0, x1, y1), (18, 20, 25), OR, border=OR, a=al, r=26, off=8, bw=4, dy=dy)
    s_ = 30 if WIDE else 36; f = F(MONO, s_)
    for j, ln in enumerate(b["lines"]):
        xx = x0 + 34; yy = y0 + 50 + j * s_ * 1.55 + s_ * 0.8 + dy
        for ch, col in zip(ln, colorize(ln)): d.text((xx, yy), ch, font=f, fill=A(col, al), anchor="lm"); xx += f.getlength(ch)
    yb = y1 - 62 + dy
    if t < b["t_ans"]:
        fr = cl((b["t_ans"] - t) / (b["t_ans"] - b["t_count"]))
        txt(d, (x0 + (x1 - x0) * 0.38, yb), b["q"], 40, A(OR, al))
        cx = x1 - 90; d.ellipse((cx - 40, yb - 40, cx + 40, yb + 40), outline=A((60, 63, 72), al), width=7)
        if t >= b["t_count"]: d.arc((cx - 40, yb - 40, cx + 40, yb + 40), -90, -90 + 360 * fr, fill=A(OR, al), width=8)
        d.text((cx, yb), str(max(0, int(math.ceil(b["t_ans"] - t)))), font=F(MONO, 40), fill=A(PAPER, al), anchor="mm")
    else:
        a2 = ss(prog(t, b["t_ans"], b["t_ans"] + 0.3)); pop = 1 + 0.08 * math.sin(math.pi * prog(t, b["t_ans"], b["t_ans"] + 0.35))
        d.rounded_rectangle((x0 + 30, yb - 40, x1 - 30, yb + 40), 22, fill=A((20, 60, 36), a2 * al), outline=A(GRN, a2 * al), width=4)
        txt(d, ((x0 + x1) / 2, yb), b["ans"], int(40 * pop), A(GRN, a2 * al))


def draw_mystery(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 26; rev = t >= b["t_reveal"]
    col = GRN if rev else OR
    hard(d, (x0, y0, x1, y1), CARDC, col, border=col, a=al, r=30, off=10, bw=5, dy=dy)
    cx, cy = x0 + 90, (y0 + y1) / 2 + dy
    if not rev:
        pu = 1 + 0.12 * math.sin(t * 6); d.ellipse((cx - 56 * pu, cy - 56 * pu, cx + 56 * pu, cy + 56 * pu), fill=A(OR, al))
        d.text((cx, cy), "?", font=F(MONO, int(78 * pu)), fill=A(INK, al), anchor="mm")
        txt(d, ((x0 + x1) / 2 + 60, cy), b["q"], 48 if WIDE else 52, A(PAPER, al))
    else:
        a2 = ss(prog(t, b["t_reveal"], b["t_reveal"] + 0.3)); d.ellipse((cx - 56, cy - 56, cx + 56, cy + 56), fill=A(GRN, al))
        d.line([(cx - 24, cy + 2), (cx - 6, cy + 20), (cx + 28, cy - 20)], fill=A(INK, al), width=12)
        txt(d, ((x0 + x1) / 2 + 60, cy), b["a"], 48 if WIDE else 52, A(PAPER, a2 * al))


def draw_gain(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 26; cy = (y0 + y1) / 2 + dy
    q = ss(prog(t, b["t0"], b["t1"])); v = b["v0"] + (b["v1"] - b["v0"]) * q
    sz = 120 if WIDE else 130; f = F(MONO, sz); u = b.get("unit", "")
    xa = x0 + (x1 - x0) * (0.25 if WIDE else 0.27); xb = x0 + (x1 - x0) * (0.75 if WIDE else 0.73)
    d.text((xa, cy), "%s%s" % (b["v0"], u), font=f, fill=A(RED, al * (1 - 0.5 * q)), anchor="mm")
    d.text((xb, cy), ("%.1f" % v if isinstance(b["v1"], float) else "%d" % round(v)) + u, font=f, fill=A(GRN if q > 0.98 else OR, al), anchor="mm")
    ax = (xa + xb) / 2; d.line([(ax - 60, cy), (ax + 60, cy)], fill=A(OR, al), width=10); d.polygon([(ax + 70, cy), (ax + 34, cy - 30), (ax + 34, cy + 30)], fill=A(OR, al))
    txt(d, ((x0 + x1) / 2, cy + sz * 0.78), b["label"], 34, A(GRAYC, al))


DRAW["poll"] = draw_poll; DRAW["predict"] = draw_predict; DRAW["mystery"] = draw_mystery; DRAW["gain"] = draw_gain


def abs_challenge(OV, b, t):
    al = ss(prog(t, b["t0"], b["t0"] + 0.3)) * (1 - ss(prog(t, b["t1"], b["t1"] + 0.35)))
    if al < 0.01: return
    d = ImageDraw.Draw(OV); cx, cy = (W - 190, 175) if WIDE else (W - 130, 270); R = 64 if WIDE else 56
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=A((18, 20, 25), al), outline=A((60, 63, 72), al), width=6)
    frac = cl((b["t1"] - t) / (b["t1"] - b["t0"])); d.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * frac, fill=A(OR, al), width=9)
    d.text((cx, cy), str(max(0, int(math.ceil(b["t1"] - t)))), font=F(MONO, 58 if WIDE else 52), fill=A(PAPER, al), anchor="mm")
    txt(d, (cx, cy + R + 34), b.get("label", "جاوب الأول"), 34, A(OR, al))


def chapter_banner(OV, t, st_times, STAGES):
    for i, st in enumerate(st_times):
        if i == 0: continue
        q = t - st[0]
        if 0 <= q < 1.8:
            al = ss(prog(q, 0, 0.3)) * (1 - ss(prog(q, 1.4, 1.8))); d = ImageDraw.Draw(OV)
            text = "%s %d · %s" % (LBL_CHAPTER, i + 1, STAGES[i]); f = F(ARB, 34)
            w = f.getlength(text, direction="rtl", language="ar") + 90; h = 62; y = (H - 150) if WIDE else 1690
            x0 = (W - w) / 2 + (1 - ss(prog(q, 0, 0.3))) * -80
            d.rounded_rectangle((x0, y - h / 2, x0 + w, y + h / 2), 30, fill=A(OR, al)); txt(d, (x0 + w / 2, y), text, 34, A(INK, al))
            d.ellipse((x0 + 22, y - 8, x0 + 38, y + 8), fill=A(INK, al))


ABS["challenge"] = abs_challenge


def draw_note(d, box, b, t, k):
    al = E(t, b["t"])
    if al < 0.01: return
    x0, y0, x1, y1 = box; dy = (1 - al) * 26; AM = (255, 196, 80)
    hard(d, (x0, y0, x1, y1), (36, 28, 14), AM, border=AM, a=al, r=26, off=9, bw=4, dy=dy)
    cy = (y0 + y1) / 2 + dy; d.ellipse((x0 + 34, cy - 24, x0 + 82, cy + 24), fill=A(AM, al)); d.text((x0 + 58, cy), "!", font=F(MONO, 34), fill=A(INK, al), anchor="mm")
    txt(d, ((x0 + x1) / 2 + 40, cy), b["text"], 44 if WIDE else 50, A(PAPER, al))


DRAW["note"] = draw_note


def abs_chips(OV, b, t):
    al = 1 - ss(prog(t, b["t1"] - 0.3, b["t1"]))
    if al < 0.01: return
    d = ImageDraw.Draw(OV); items = b["items"]; f = F(MONO, 34 if WIDE else 38)
    ws = [f.getlength(x) + 60 for x in items]; tot = sum(ws) + 20 * (len(ws) - 1); x = W / 2 - tot / 2; y = 860 if WIDE else 1500
    for i, (x_, w) in enumerate(zip(items, ws)):
        a = ss(prog(t, b["t0"] + i * 0.25, b["t0"] + i * 0.25 + 0.3)) * al
        if a > 0.01:
            sc = 1 + 0.12 * math.sin(math.pi * prog(t, b["t0"] + i * 0.25, b["t0"] + i * 0.25 + 0.35)); ww = w * sc
            d.rounded_rectangle((x + w / 2 - ww / 2, y - 34 * sc, x + w / 2 + ww / 2, y + 34 * sc), 34, fill=A(OR, a)); d.text((x + w / 2, y), x_, font=f, fill=A(INK, a), anchor="mm")
        x += w + 20


def abs_corner(OV, b, t):
    al = ss(prog(t, b["t0"], b["t0"] + 0.4)) * (1 - ss(prog(t, b["t1"] - 0.4, b["t1"])))
    if al < 0.01: return
    d = ImageDraw.Draw(OV); a_, c_ = b["labels"]; act = 0
    for i, ti in enumerate(b["switch"]):
        if t >= ti: act = i % 2
    x0, y0 = 40, (H - 130) if WIDE else 1780
    d.rounded_rectangle((x0, y0, x0 + 330, y0 + 56), 28, fill=A((18, 20, 25), al), outline=A((60, 63, 72), al), width=3)
    for i, lab in enumerate((a_, c_)):
        on = act == i; xx = x0 + 6 + i * 160
        if on: d.rounded_rectangle((xx, y0 + 6, xx + 158, y0 + 50), 22, fill=A(OR, al))
        d.text((xx + 79, y0 + 28), lab, font=F(MONO, 24), fill=A(INK if on else GRAYC, al), anchor="mm")


ABS["chips"] = abs_chips; ABS["corner"] = abs_corner


def headline(d, text, te, t):
    al = E(t, te, 0.3)
    if al < 0.01: return
    s = 72 if WIDE else 66
    f = F(ARB, s); w = f.getlength(text, direction="rtl", language="ar") + 90
    y = 165 if WIDE else 270; dy = (1 - al) * 24
    hard(d, (W / 2 - w / 2, y - 58, W / 2 + w / 2, y + 58), OR, PAPER, border=INK, a=al, r=20, off=9, bw=5, dy=dy)
    d.text((W / 2, y + dy), text, font=f, fill=A(INK, al), anchor="mm", direction="rtl", language="ar")


# ------------------------------------------------------------------ persistent layer: progress + stage tabs
def tabs_layer(t, STAGES, ST_TIMES, T_END, marks=()):
    P = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rectangle((0, 0, W, 10), fill=(40, 42, 48, 255)); d.rectangle((0, 0, int(W * cl(t / T_END)), 10), fill=A(OR, 1))
    for mt in marks:
        mx = int(W * mt / T_END); on = t >= mt
        pp = prog(t, mt, mt + 0.7); rr = 9 + (16 * math.sin(math.pi * pp) if 0 < pp < 1 else 0)
        if 0 < pp < 1: d.ellipse((mx - rr - 6, 10 - rr - 6, mx + rr + 6, 10 + rr + 6), outline=A(OR, 1 - pp), width=4)
        d.ellipse((mx - 9, 1, mx + 9, 19), fill=A(OR if on else (70, 73, 82), 1), outline=A(INK, 1), width=2)
    s = 26 if WIDE else 28; hgt = 50 if WIDE else 54
    ws = [F(ARB, s).getlength(x, direction="rtl", language="ar") + 54 for x in STAGES]
    gap = 14; total = sum(ws) + gap * (len(ws) - 1)
    x = W / 2 + total / 2; y = 62 if WIDE else 150
    for i, (lab, w) in enumerate(zip(STAGES, ws)):
        t0, t1 = ST_TIMES[i]
        act = ss(prog(t, t0, t0 + 0.3)) * (1 - ss(prog(t, t1, t1 + 0.3)))
        past = 1.0 if t >= t1 + 0.3 else 0.0
        fill = lerp(CARDC, OR, act); tc = lerp(PAPER if past else GRAYC, INK, act)
        d.rounded_rectangle((x - w, y - hgt / 2, x, y + hgt / 2), hgt / 2, fill=A(fill, 1), outline=A(lerp((60, 63, 72), OR, max(act, past * 0.6)), 1), width=3)
        d.text((x - w / 2, y), lab, font=F(ARB, s), fill=A(tc, 1), anchor="mm", direction="rtl", language="ar")
        x -= w + gap
    return P


# ------------------------------------------------------------------ layer transforms
def shift_x(arr, off):
    out = np.zeros_like(arr)
    if off == 0: return arr
    if off > 0: out[:, off:] = arr[:, :W - off]
    else: out[:, :W + off] = arr[:, -off:]
    return out


def mblur(layer, length, shift, alpha):
    a = np.asarray(layer).astype(np.float32)
    pm = a.copy(); pm[..., :3] *= a[..., 3:4] / 255.0
    n = max(2, int(length / 14) + 2); acc = np.zeros_like(pm)
    for k in range(n):
        acc += shift_x(pm, int(shift + length * (k / (n - 1) - 0.5)))
    acc /= n
    al = acc[..., 3:4]
    rgb = acc[..., :3] / np.maximum(al / 255.0, 1e-3)
    out = np.concatenate([np.clip(rgb, 0, 255), np.clip(al * alpha, 0, 255)], axis=2).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ------------------------------------------------------------------ monogram + background + end card
_MONO = _asset_img("mono.png", "RGBA", (180, 180))
_MONO = _MONO.resize((int(_MONO.width * 55 / _MONO.height), 55), Image.LANCZOS)
_GL = Image.new("RGBA", (_MONO.width + 80, _MONO.height + 80), (0, 0, 0, 0))
ImageDraw.Draw(_GL).ellipse((20, 20, _GL.width - 20, _GL.height - 20), fill=OR + (120,))
_GL = _GL.filter(ImageFilter.GaussianBlur(18))


def corner_logo(im, t, T_END):
    vis = 1 - ss(prog(t, T_END - 0.3, T_END))
    if vis < 0.01: return
    fy = 6 * math.sin(2 * math.pi * t / 4.5); ga = 0.55 + 0.25 * math.sin(2 * math.pi * t / 3.2)
    x, y = 40, 32 + fy
    g2 = _GL.copy(); g2.putalpha(g2.getchannel("A").point(lambda v: int(v * ga * vis)))
    im.alpha_composite(g2, (int(x + _MONO.width / 2 - _GL.width / 2), int(y + _MONO.height / 2 - _GL.height / 2)))
    m2 = _MONO.copy(); m2.putalpha(m2.getchannel("A").point(lambda v: int(v * vis)))
    im.alpha_composite(m2, (int(x), int(y)))


def make_bg(tech_labels):
    if WIDE: return Image.open(os.environ.get("BGFILE", SD + "backgrounds/default.png")).convert("RGBA")
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32) + np.array([13, 14, 16], np.float32)
    def glow(cx, cy, r, col, k):
        dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); return (np.exp(-(dd / r) ** 2) * k)[..., None] * np.array(col, np.float32)
    base += glow(0, 0, 620, OR, .20) + glow(W, H, 760, OR, .16) + glow(W, 0, 380, OR2, .06)
    dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    base *= (0.80 + 0.20 * np.clip(1 - dd, 0, 1))[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    Lr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(Lr)
    for x in range(0, W + 1, 96): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
    for y in range(0, H + 1, 96): d.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
    def node(x, y, r=7, a=120):
        d.ellipse((x - r, y - r, x + r, y + r), outline=OR + (a,), width=2); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=OR + (a,))
    def trace(p, a=90):
        d.line(p, fill=OR + (a,), width=2, joint="curve"); node(*p[-1])
    trace([(40, 420), (40, 900), (80, 940), (80, 1300)]); trace([(1040, 380), (1040, 1100), (1000, 1140), (1000, 1500)])
    trace([(60, 1500), (60, 1700), (110, 1750), (110, 1830)], 70)
    for k in range(3): d.ellipse((60, 1600 + k * 0, 60, 1600), outline=OR + (0,))
    for r in (140, 220, 300): d.arc((-r, H - r, r, H + r), 270, 360, fill=OR + (55,), width=2)
    fl = F(MONO, 28); x = 250
    for tx in tech_labels:
        w = int(fl.getlength(tx)) + 50
        d.rounded_rectangle((x, 1840, x + w, 1888), 24, outline=OR + (120,), width=2); d.text((x + w / 2, 1864), tx, font=fl, fill=(255, 255, 255, 120), anchor="mm"); x += w + 24
    a = np.asarray(Lr).astype(np.float32)
    mask = np.clip((np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.45) / 0.4, 0, 1)
    a[..., 3] *= np.clip(mask * 1.25, 0, 1)
    return Image.alpha_composite(im, Image.fromarray(a.astype(np.uint8)))


_LOGO = _asset_img("logo_ch.png", "RGB", (760, 760)).resize((760, 760), Image.LANCZOS)
LA = np.asarray(_LOGO).astype(np.float32)


def end_frame(t, T_END, TAG1, TAG2):
    a = ss(prog(t, T_END + 0.2, T_END + 0.9)); bump = math.sin(math.pi * prog(t, T_END + 1.5, T_END + 2.3)) ** 2
    bg = np.empty((H, W, 3), np.float32); bg[:] = (5, 6, 7)
    x0 = W // 2 - 380; y0 = (160 if WIDE else 520)
    reg = bg[y0:y0 + 760, x0:x0 + 760]
    np.maximum(reg, np.clip(LA * a * (1 + 0.22 * bump), 0, 255), out=reg)
    im = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    ty = 950 if WIDE else 1360
    d.text((W / 2, ty), SIGNOFF1, font=F(MONO, 50), fill=A(OR, E(t, TAG1, 0.3)), anchor="mm")
    d.text((W / 2, ty + 62), SIGNOFF2, font=F(MONO, 50), fill=A(OR, E(t, TAG2, 0.3)), anchor="mm")
    OVE = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tb = TAG1 + 0.2
    if WIDE: pos = ((W - 290, 880), (W - 290, 1000)); wh = (500, 104)
    else: pos = ((W / 2, 1590), (W / 2, 1720)); wh = (560, 116)
    for kind, (px, py), dly in (("subscribe", pos[0], 0.0), ("follow", pos[1], 0.35)):
        abs_button(OVE, {"kind": kind, "t0": tb + dly, "t1": 1e6, "cx": px, "cy": py, "w": wh[0], "h": wh[1], "static": True}, t)
    im.alpha_composite(OVE)
    return np.asarray(im.convert("RGB")).copy()


# ------------------------------------------------------------------ animated background overlay
def _sprite(r, col, k):
    n = r * 2; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    a = np.exp(-(((xx - r) ** 2 + (yy - r) ** 2) / (r * 0.55) ** 2)) * k * 255
    im = np.zeros((n, n, 4), np.uint8); im[..., 0], im[..., 1], im[..., 2] = col; im[..., 3] = a.astype(np.uint8)
    return Image.fromarray(im, "RGBA")
_G1 = _sprite(520, OR, 0.22); _G2 = _sprite(420, OR2, 0.16); _G3 = _sprite(300, OR, 0.14)
_DOTS = None


def bg_motion(im, t):
    p = 2 * math.pi * t / 14.0
    for sp, cx, cy in ((_G1, 0.10 + 0.07 * math.sin(p), 0.12 + 0.08 * math.cos(p * 0.8)),
                       (_G2, 0.92 + 0.05 * math.cos(p * 1.1), 0.90 + 0.06 * math.sin(p * 0.9)),
                       (_G3, 0.92 + 0.04 * math.sin(p * 1.3 + 1), 0.10 + 0.07 * math.cos(p + 2) if WIDE else 0.06 + 0.04 * math.cos(p + 2))):
        im.alpha_composite(sp, (int(cx * W - sp.width / 2), int(cy * H - sp.height / 2)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    step = 96; sw = (t * 70) % (W + 600) - 300
    # light sweep along grid verticals near the edges
    for x in range(0, W + 1, step):
        k = math.exp(-((x - sw) / 160.0) ** 2)
        edge = max(0.0, abs(x - W / 2) / (W / 2) - 0.55) / 0.45
        a = int(60 * k * min(1, edge * 1.3))
        if a > 2: d.line([(x, 0), (x, H)], fill=OR + (a,), width=2)
    # twinkling grid-intersection dots at the edges
    for i in range(34):
        gx = (i * 7919) % (W // step + 1) * step; gy = (i * 104729) % (H // step + 1) * step
        edge = max(abs(gx - W / 2) / (W / 2), abs(gy - H / 2) / (H / 2))
        if edge < 0.62: continue
        tw = 0.5 + 0.5 * math.sin(2 * math.pi * t / (2.6 + (i % 5) * 0.7) + i)
        d.ellipse((gx - 4, gy - 4, gx + 4, gy + 4), fill=OR + (int(30 + 150 * tw),))
    im.alpha_composite(L)


# ------------------------------------------------------------------ engine
# ------------------------------------------------------------------ extra blocks (2026-10-31): icards, steplist, fixcards
def _fit(text, size, maxw, lo=16, mono=None):
    """largest font size <= size so that text fits maxw"""
    if mono is None: mono = text.isascii()
    s = size
    while s > lo:
        f = F(MONO, s) if mono else F(ARB, s)
        w = f.getlength(text) if mono else f.getlength(text, direction="rtl", language="ar")
        if w <= maxw: break
        s -= 2
    return s


def _grid(box, n, cols, gap, rtl=True):
    """cell boxes for n items in `cols` columns inside box; first item at the right when rtl"""
    x0, y0, x1, y1 = box; rows = -(-n // cols)
    cw = (x1 - x0 - (cols - 1) * gap) / cols; ch = (y1 - y0 - (rows - 1) * gap) / rows
    out = []
    for i in range(n):
        r, c = divmod(i, cols); c = cols - 1 - c if rtl else c
        out.append((x0 + c * (cw + gap), y0 + r * (ch + gap), x0 + c * (cw + gap) + cw, y0 + r * (ch + gap) + ch))
    return out


def draw_icon(d, kind, cx, cy, sz, q, al):
    """small animated line-icon; q = animation progress 0..1"""
    G2 = (70, 73, 82); lw = max(3, int(sz * 0.07)); q = ss(q)
    if kind == "shield":
        d.rounded_rectangle((cx - 0.6 * sz, cy - 0.75 * sz, cx + 0.6 * sz, cy + 0.75 * sz), int(0.45 * sz), outline=A(OR, al), width=lw)
        r = 0.12 * sz * (0.5 + 0.5 * q); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(OR, al))
        if q > 0.6: d.line([(cx - 0.25 * sz, cy + 0.05 * sz), (cx - 0.05 * sz, cy + 0.28 * sz), (cx + 0.3 * sz, cy - 0.2 * sz)], fill=A(GRN, al * ss((q - 0.6) / 0.4)), width=lw, joint="curve")
    elif kind == "grid":
        lit = q * 6
        for i in range(6):
            r, c = divmod(i, 3); x = cx - 1.05 * sz + c * 0.75 * sz; y = cy - 0.75 * sz + r * 0.85 * sz
            d.rounded_rectangle((x, y, x + 0.55 * sz, y + 0.55 * sz), int(0.12 * sz), fill=A(OR if lit > i else G2, al))
    elif kind == "bar":
        d.rounded_rectangle((cx - 1.3 * sz, cy - 0.14 * sz, cx + 1.1 * sz, cy + 0.14 * sz), int(0.14 * sz), fill=A(G2, al * 0.6))
        d.rounded_rectangle((cx - 1.3 * sz, cy - 0.14 * sz, cx - 1.3 * sz + 2.0 * sz * q, cy + 0.14 * sz), int(0.14 * sz), fill=A(OR, al))
        d.line([(cx + 1.25 * sz, cy - 0.6 * sz), (cx + 1.25 * sz, cy + 0.6 * sz)], fill=A(RED, al), width=lw)
    elif kind == "clock":
        d.ellipse((cx - 0.85 * sz, cy - 0.85 * sz, cx + 0.85 * sz, cy + 0.85 * sz), outline=A(OR, al), width=lw)
        a = -math.pi / 2 + 2 * math.pi * 0.85 * q
        d.line([(cx, cy), (cx + 0.6 * sz * math.cos(a), cy + 0.6 * sz * math.sin(a))], fill=A(OR, al), width=lw)
        d.line([(cx, cy), (cx, cy - 0.4 * sz)], fill=A(GRAYC, al), width=lw)
    elif kind == "lock":
        up = (1 - q) * 0.35 * sz
        d.arc((cx - 0.4 * sz, cy - 1.0 * sz - up, cx + 0.4 * sz, cy - 0.1 * sz - up), 180, 360, fill=A(OR, al), width=lw)
        d.rounded_rectangle((cx - 0.65 * sz, cy - 0.45 * sz, cx + 0.65 * sz, cy + 0.65 * sz), int(0.14 * sz), fill=A(OR if q > 0.9 else G2, al))
        d.ellipse((cx - 0.09 * sz, cy - 0.1 * sz, cx + 0.09 * sz, cy + 0.08 * sz), fill=A(INK, al))
    elif kind == "nodes":
        pts = [(cx, cy - 0.7 * sz), (cx - 0.8 * sz, cy + 0.6 * sz), (cx + 0.8 * sz, cy + 0.6 * sz)]
        for i in range(3):
            a_, b_ = pts[i], pts[(i + 1) % 3]; k_ = ss(prog(q, i / 3, (i + 1) / 3))
            d.line([a_, (a_[0] + (b_[0] - a_[0]) * k_, a_[1] + (b_[1] - a_[1]) * k_)], fill=A(GRAYC, al), width=lw)
        for i, p in enumerate(pts):
            r = 0.2 * sz; d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=A(OR if q > i / 3 else G2, al))
    elif kind == "key":
        d.ellipse((cx - 0.95 * sz, cy - 0.35 * sz, cx - 0.25 * sz, cy + 0.35 * sz), outline=A(OR, al), width=lw)
        x2 = cx - 0.25 * sz + 1.2 * sz * q; d.line([(cx - 0.25 * sz, cy), (x2, cy)], fill=A(OR, al), width=lw)
        for fx in (0.55, 0.85):
            if q * 1.2 > fx: d.line([(cx - 0.25 * sz + fx * 1.2 * sz, cy), (cx - 0.25 * sz + fx * 1.2 * sz, cy + 0.3 * sz)], fill=A(OR, al), width=lw)
    elif kind == "warn":
        d.polygon([(cx, cy - 0.85 * sz), (cx - 0.95 * sz, cy + 0.7 * sz), (cx + 0.95 * sz, cy + 0.7 * sz)], outline=A(AMB, al), width=lw)
        d.line([(cx, cy - 0.3 * sz), (cx, cy + 0.2 * sz)], fill=A(AMB, al), width=lw); r = 0.07 * sz; d.ellipse((cx - r, cy + 0.4 * sz - r, cx + r, cy + 0.4 * sz + r), fill=A(AMB, al))
    elif kind == "check":
        d.ellipse((cx - 0.85 * sz, cy - 0.85 * sz, cx + 0.85 * sz, cy + 0.85 * sz), outline=A(GRN, al), width=lw)
        pts = [(cx - 0.4 * sz, cy + 0.05 * sz), (cx - 0.1 * sz, cy + 0.38 * sz), (cx + 0.45 * sz, cy - 0.3 * sz)]
        if q > 0.3: d.line(pts[:2], fill=A(GRN, al), width=lw)
        if q > 0.6: d.line(pts[1:], fill=A(GRN, al), width=lw)
    elif kind == "db":
        for i in range(3):
            y = cy - 0.7 * sz + i * 0.55 * sz; d.ellipse((cx - 0.8 * sz, y - 0.22 * sz, cx + 0.8 * sz, y + 0.22 * sz), outline=A(OR if q > i / 3 else G2, al), width=lw)
    elif kind == "bolt":
        d.polygon([(cx + 0.15 * sz, cy - 0.95 * sz), (cx - 0.55 * sz, cy + 0.1 * sz), (cx - 0.05 * sz, cy + 0.1 * sz), (cx - 0.2 * sz, cy + 0.95 * sz), (cx + 0.6 * sz, cy - 0.2 * sz), (cx + 0.08 * sz, cy - 0.2 * sz)], fill=A(OR, al * (0.4 + 0.6 * q)))
    else:
        d.ellipse((cx - 0.7 * sz, cy - 0.7 * sz, cx + 0.7 * sz, cy + 0.7 * sz), outline=A(OR, al), width=lw)


def draw_icards(d, box, b, t, k):
    """numbered cards with a small animated icon and a one-line caption (Zero Trust style)"""
    items = b["items"]; n = len(items)
    cols = b.get("cols", min(n, 3)) if WIDE else b.get("cols_reel", 2)
    cells = _grid(box, n, cols, 30 if WIDE else 24, b.get("rtl", True))
    last = max([i for i, it in enumerate(items) if t >= it["t"]], default=-1)
    for i, (it, (x0, y0, x1, y1)) in enumerate(zip(items, cells)):
        al = E(t, it["t"])
        if al < 0.01: continue
        dy = (1 - al) * 28; y0 += dy; y1 += dy; cw_ = x1 - x0; ch_ = y1 - y0
        act = (i == last and t - it["t"] < 3.0); hl = 1 - ss(prog(t, it["t"], it["t"] + 1.5)) if act else 0
        d.rounded_rectangle((x0, y0, x1, y1), 26, fill=A(CARDC, al), outline=A(lerp((60, 63, 72), OR, 1.0 if act else 0.0), al), width=4 if act else 3)
        title = it["title"]; rtl = not title.isascii(); r = 26
        bx = x1 - 28 - r if rtl else x0 + 28 + r; by = y0 + 28 + r
        d.ellipse((bx - r, by - r, bx + r, by + r), outline=A(OR, al), width=4); d.text((bx, by), str(i + 1), font=F(MONO, 26), fill=A(OR, al), anchor="mm")
        tw = cw_ - 2 * 28 - 2 * r - 20; ts = _fit(title, 34 if WIDE else 30, tw)
        if rtl: d.text((bx - r - 16, by), title, font=F(ARB, ts), fill=A(OR, al), anchor="rm", direction="rtl", language="ar")
        else: d.text((bx + r + 16, by), title, font=F(MONO, ts), fill=A(OR, al), anchor="lm")
        ly = y0 + 28 + 2 * r + 22; d.line([(x0 + 28, ly), (x1 - 28, ly)], fill=A((60, 63, 72), al), width=2)
        sz = min(cw_, ch_) * 0.2; q = prog(t, it["t"] + 0.1, it["t"] + 1.3)
        draw_icon(d, it.get("icon", ""), (x0 + x1) / 2, (ly + y1 - 80) / 2 + 10, sz, q, al)
        cap = it.get("caption", "")
        if cap:
            cs = _fit(cap, 34 if WIDE else 30, cw_ - 56); txt(d, ((x0 + x1) / 2, y1 - 50), cap, cs, A(GRAYC, al))


def draw_steplist(d, box, b, t, k):
    """index list of steps (current one orange) + terminal panel that shows the current step's commands"""
    al = E(t, b["t"], 0.3)
    if al < 0.01: return
    items = b["items"]; n = len(items); x0, y0, x1, y1 = box; y0 += (1 - al) * 24; y1 += (1 - al) * 24
    cur = max([i for i, it in enumerate(items) if t >= it["t"]], default=-1)
    ih = 66 if WIDE else 62
    if WIDE:
        lw = 520; side = b.get("list_side", "right")
        lbox = (x1 - lw, y0, x1, y1) if side == "right" else (x0, y0, x0 + lw, y1)
        tbox = (x0, y0, x1 - lw - 36, y1) if side == "right" else (x0 + lw + 36, y0, x1, y1)
        gap_ = min(12, (y1 - y0 - n * ih) / max(1, n - 1)); ih = min(ih, (y1 - y0 - gap_ * (n - 1)) / n)
        pos = [(lbox[0], y0 + i * (ih + gap_), lbox[2], y0 + i * (ih + gap_) + ih) for i in range(n)]
    else:
        rows = -(-n // 2); lh = rows * (ih + 10); lbox = (x0, y0, x1, y0 + lh); tbox = (x0, y0 + lh + 24, x1, y1)
        cw_ = (x1 - x0 - 12) / 2
        pos = []
        for i in range(n):
            r_, c_ = divmod(i, 2); c_ = 1 - c_
            pos.append((x0 + c_ * (cw_ + 12), y0 + r_ * (ih + 10), x0 + c_ * (cw_ + 12) + cw_, y0 + r_ * (ih + 10) + ih))
    for i, (it, (bx0, by0, bx1, by1)) in enumerate(zip(items, pos)):
        st = "act" if i == cur else ("past" if i < cur else "fut")
        ia = al * (1.0 if st != "fut" else 0.75)
        d.rounded_rectangle((bx0, by0, bx1, by1), 14, fill=A(OR if st == "act" else (22, 24, 29), ia), outline=None if st == "act" else A((60, 63, 72), ia), width=2)
        name = it["name"]; col = INK if st == "act" else (PAPER if st == "past" else (110, 113, 122))
        s_ = _fit(name, 30 if WIDE else 28, bx1 - bx0 - 110)
        if name.isascii(): d.text((bx0 + 24, (by0 + by1) / 2), "%02d  %s" % (i + 1, name), font=F(MONO, s_), fill=A(col, ia), anchor="lm")
        else:
            d.text((bx0 + 24, (by0 + by1) / 2), "%02d" % (i + 1), font=F(MONO, s_), fill=A(col, ia), anchor="lm")
            d.text((bx1 - 24, (by0 + by1) / 2), name, font=F(ARB, s_), fill=A(col, ia), anchor="rm", direction="rtl", language="ar")
    # terminal
    tx0, ty0, tx1, ty1 = tbox
    d.rounded_rectangle((tx0, ty0, tx1, ty1), 18, fill=A((16, 17, 20), al), outline=A((60, 63, 72), al), width=2)
    for j, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): d.ellipse((tx0 + 26 + j * 28, ty0 + 24, tx0 + 42 + j * 28, ty0 + 40), fill=A(c, al))
    if cur < 0: return
    it = items[cur]; d.text((tx0 + 150, ty0 + 32), it.get("file", it["name"]), font=F(MONO, 22), fill=A(GRAYC, al), anchor="lm")
    d.line([(tx0, ty0 + 66), (tx1, ty0 + 66)], fill=A((60, 63, 72), al), width=2)
    lines = it.get("lines", []); maxl = max([len(l[1]) for l in lines] + [1])
    fs = max(18, min(30 if WIDE else 30, int((tx1 - tx0 - 70) / (0.6 * maxl)))); f = F(MONO, fs); lh = fs * 1.75
    for j, ln in enumerate(lines):
        ts = it["t"] + ln[0]; text = ln[1]; cps = ln[2] if len(ln) > 2 else 40; kind = ln[3] if len(ln) > 3 else ("cmd" if text.startswith("$") else "out")
        m = min(len(text), int(max(0, t - ts) * cps))
        if m <= 0: continue
        yy = ty0 + 66 + 36 + j * lh + lh * 0.4
        if kind == "bad":
            d.rounded_rectangle((tx0 + 16, yy - lh * 0.45, tx1 - 16, yy + lh * 0.45), 8, fill=A(RED, 0.16 * al))
        xx = tx0 + 36
        for ci in range(m):
            ch = text[ci]
            col = (PAPER if ci > 0 else GRN) if kind == "cmd" and text.startswith("$") else {"cmd": PAPER, "out": GRAYC, "bad": RED, "ok": GRN}.get(kind, PAPER)
            d.text((xx, yy), ch, font=f, fill=A(col, al), anchor="lm"); xx += f.getlength(ch)


def draw_fixcards(d, box, b, t, k):
    """problem -> chain of 3 chips -> fix line. The card being spoken glows."""
    items = b["items"]; n = len(items)
    cols = b.get("cols", (2 if n <= 4 else 3)) if WIDE else b.get("cols_reel", 1)
    cells = _grid(box, n, cols, 30 if WIDE else 22, b.get("rtl", True))
    last = max([i for i, it in enumerate(items) if t >= it["t"]], default=-1)
    for i, (it, (x0, y0, x1, y1)) in enumerate(zip(items, cells)):
        al = E(t, it["t"])
        if al < 0.01: continue
        dy = (1 - al) * 28; y0 += dy; y1 += dy; cw_ = x1 - x0; ch_ = y1 - y0
        act = (i == last and t - it["t"] < 6.0)
        if act:
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), 30, outline=A(OR, 0.6 * al), width=10)
            d._image.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
        d.rounded_rectangle((x0, y0, x1, y1), 26, fill=A(CARDC, al), outline=A(OR if act else (60, 63, 72), al), width=4 if act else 3)
        title = it["title"]; rtl = not title.isascii(); pad = 30
        ts = _fit(title, 36 if WIDE else 34, cw_ - 2 * pad - 70)
        if rtl:
            d.text((x1 - pad, y0 + 48), "%d." % (i + 1), font=F(MONO, ts), fill=A(OR, al), anchor="rm")
            d.text((x1 - pad - 56, y0 + 48), title, font=F(ARB, ts), fill=A(PAPER, al), anchor="rm", direction="rtl", language="ar")
        else:
            d.text((x0 + pad, y0 + 48), "%d." % (i + 1), font=F(MONO, ts), fill=A(OR, al), anchor="lm")
            d.text((x0 + pad + 56, y0 + 48), title, font=F(MONO, ts), fill=A(PAPER, al), anchor="lm")
        if it.get("sub"): txt(d, ((x0 + x1) / 2, y0 + 100), it["sub"], 22, A(GRAYC, al))
        chain = it.get("chain", []); cts = it.get("chain_t") or [it["t"] + 0.5 + 0.5 * j for j in range(len(chain))]
        cols_ = [AMB, OR, RED]; m = len(chain)
        if m:
            gapc = 44; cwid = (cw_ - 2 * pad - gapc * (m - 1)) / m; cy = y0 + 100 + (ch_ - 100 - 120) * 0.5 + 44
            order = list(range(m))[::-1] if b.get("rtl", True) and not title.isascii() else list(range(m))
            for pos_, j in enumerate(order):
                ca = E(t, cts[j], 0.3)
                if ca < 0.01: continue
                cx0 = x0 + pad + pos_ * (cwid + gapc); c_ = cols_[min(j, 2)] if m > 1 else OR
                d.rounded_rectangle((cx0, cy - 34, cx0 + cwid, cy + 34 + (0)), 34, fill=A(c_, 0.12 * ca), outline=A(c_, ca), width=3)
                txt_ = chain[j]; tsz = _fit(txt_, 24 if WIDE else 24, cwid - 28, lo=16)
                txt(d, (cx0 + cwid / 2, cy), txt_, tsz, A(PAPER, ca))
                if pos_ < m - 1 and ca > 0.5:
                    for dd in (-6, 8): d.ellipse((cx0 + cwid + gapc / 2 + dd - 4, cy - 4, cx0 + cwid + gapc / 2 + dd + 4, cy + 4), fill=A(AMB, ca))
        fx = it.get("fix"); fa = E(t, it.get("fix_t", it["t"] + 0.5 + 0.5 * m + 0.6), 0.3) if fx else 0
        if fx and fa > 0.01:
            fy = y1 - 48; fs = _fit(fx, 30 if WIDE else 28, cw_ - 2 * pad - 50, lo=18)
            d.ellipse((x1 - pad - 30, fy - 15, x1 - pad, fy + 15), fill=A(GRN, 0.2 * fa), outline=A(GRN, fa), width=3); d.line([(x1 - pad - 22, fy), (x1 - pad - 16, fy + 6), (x1 - pad - 7, fy - 6)], fill=A(GRN, fa), width=3)
            if fx.isascii(): d.text((x1 - pad - 44, fy), fx, font=F(MONO, fs), fill=A(PAPER, fa), anchor="rm")
            else: d.text((x1 - pad - 44, fy), fx, font=F(ARB, fs), fill=A(PAPER, fa), anchor="rm", direction="rtl", language="ar")


def _icards_h(b, w):
    n = len(b["items"]); cols = b.get("cols", min(n, 3)) if WIDE else b.get("cols_reel", 2); rows = -(-n // cols)
    return int(min(RY1 - RY0, (560 if rows == 1 else 720) if WIDE else rows * 440 + (rows - 1) * 24))
def _steplist_h(b, w):
    n = len(b["items"])
    return int(min(RY1 - RY0, max(500, n * 78) if WIDE else (-(-n // 2)) * 72 + 24 + 620))
def _fixcards_h(b, w):
    n = len(b["items"]); cols = b.get("cols", (2 if n <= 4 else 3)) if WIDE else b.get("cols_reel", 1); rows = -(-n // cols)
    return int(min(RY1 - RY0, (380 if rows == 1 else 720) if WIDE else rows * 400 + (rows - 1) * 22))
EXTRA_H = {"icards": _icards_h, "steplist": _steplist_h, "fixcards": _fixcards_h}
DRAW["icards"] = draw_icards; DRAW["steplist"] = draw_steplist; DRAW["fixcards"] = draw_fixcards


# ---------------------------------------------------------------- versus / matrix / tabcard / icon3d (added 2026-10-31)
import re as _re
def _col(v, default=None):
    """colour from (r,g,b) or '#RRGGBB'"""
    if v is None: return default or OR
    if isinstance(v, str):
        v = v.lstrip("#"); return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    return tuple(v)
_TOK = _re.compile(r'("[^"]*"|<[^>]+>|\b\d+\b|^\s*[\w-]+(?=:)|[{}\[\]])')
def _hl(line, col):
    out = []; pos = 0
    for m in _TOK.finditer(line):
        if m.start() > pos: out.append((line[pos:m.start()], PAPER))
        s = m.group(0)
        if s[0] == '"': c = col if line[m.end():m.end() + 1] == ":" else (170, 235, 190)
        elif s[0] == "<": c = col
        elif s[0] in "{}[]": c = GRAYC
        elif s.strip().isdigit(): c = (255, 176, 70)
        else: c = col
        out.append((s, c)); pos = m.end()
    if pos < len(line): out.append((line[pos:], PAPER))
    return out
def _put(d, x, y, s, size, col, al, anchor="lm", maxw=None):
    """one text (Latin = mono, otherwise Arabic RTL); anchor lm / rm / mm"""
    if maxw: size = _fit(s, size, maxw, lo=12)
    if s.isascii(): d.text((x, y), s, font=F(MONO, size), fill=A(col, al), anchor=anchor)
    else: d.text((x, y), s, font=F(ARB, size), fill=A(col, al), anchor=anchor, direction="rtl", language="ar")

def _mark(d, kind, cx, cy, r, col, al, q=1.0):
    """check / cross / tilde symbol, q = draw progress"""
    lw = max(4, int(r * 0.28))
    if kind == "ok":
        p = [(cx - 0.8 * r, cy + 0.05 * r), (cx - 0.25 * r, cy + 0.65 * r), (cx + 0.85 * r, cy - 0.6 * r)]
        if q > 0.01: d.line(p[:2], fill=A(col, al), width=lw)
        if q > 0.5: d.line(p[1:], fill=A(col, al), width=lw)
        d.ellipse((p[0][0] - lw / 2, p[0][1] - lw / 2, p[0][0] + lw / 2, p[0][1] + lw / 2), fill=A(col, al))
    elif kind == "bad":
        s = 0.7 * r
        d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=A(col, al), width=lw); d.line([(cx + s, cy - s), (cx - s, cy + s)], fill=A(col, al), width=lw)
    else:
        pts = [(cx - 0.8 * r + i * 0.1 * r, cy + 0.25 * r * math.sin(i * 0.9 * math.pi / 8 * 2) * (-1)) for i in range(17)]
        d.line(pts, fill=A(col, al), width=lw, joint="curve")

def _vs_icon(d, kind, cx, cy, r, col, al):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(CARDC, al), outline=A(col, al), width=5)
    if kind == "doc":
        d.rounded_rectangle((cx - 0.4 * r, cy - 0.55 * r, cx + 0.4 * r, cy + 0.55 * r), 6, outline=A(col, al), width=4)
        for i in range(3): d.line([(cx - 0.22 * r, cy - 0.22 * r + i * 0.26 * r), (cx + 0.22 * r, cy - 0.22 * r + i * 0.26 * r)], fill=A(col, al), width=3)
    else: d.text((cx, cy), kind, font=F(MONO, int(r * 0.85)), fill=A(col, al), anchor="mm")

def draw_versus(d, box, b, t, k):
    """2-3 columns, each with its own colour: name, sub, code sample, bullets (appear one by one), icon"""
    cols = b["cols"]; n = len(cols); x0, y0, x1, y1 = box
    if WIDE: cells = _grid(box, n, n, 28, False)
    else: cells = _grid(box, n, 1, 22, False)
    for i, (c, (cx0, cy0, cx1, cy1)) in enumerate(zip(cols, cells)):
        al = E(t, c["t"])
        if al < 0.01: continue
        col = _col(c.get("color")); cy0 += (1 - al) * 30; cy1 += (1 - al) * 30; cw_ = cx1 - cx0; ch_ = cy1 - cy0; pad = 26
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((cx0, cy0, cx1, cy1), 30, outline=A(col, 0.55 * al), width=8)
        d._image.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
        d.rounded_rectangle((cx0, cy0, cx1, cy1), 30, fill=A(lerp(CARDC, col, 0.07), al), outline=A(col, al), width=4)
        d.line([(cx0 + cw_ * 0.3, cy0 + 2), (cx1 - cw_ * 0.3, cy0 + 2)], fill=A(col, al), width=7)
        nm = c["name"]; ns = _fit(nm, 76 if WIDE else 60, cw_ * (1 - (0.45 if not WIDE else 0)) - 2 * pad, lo=28)
        if WIDE:
            _put(d, (cx0 + cx1) / 2, cy0 + 70, nm, ns, col, al, "mm")
            if c.get("sub"): _put(d, (cx0 + cx1) / 2, cy0 + 122, c["sub"], 24, GRAYC, al, "mm", cw_ - 2 * pad)
            by0 = cy0 + 160; code_h = 40 + 44 * len(c.get("code", [])) if c.get("code") else 0
            if c.get("code"):
                d.rounded_rectangle((cx0 + pad, by0, cx1 - pad, by0 + code_h), 18, fill=A((10, 11, 14), al), outline=A(col, al), width=3)
                ca = E(t, c.get("code_t", c["t"] + 0.3))
                for li, ln in enumerate(c["code"]):
                    xx = cx0 + pad + 22; yy = by0 + 36 + li * 44; fs = 28
                    for seg, sc in _hl(ln, col):
                        f = F(MONO, fs); d.text((xx, yy), seg, font=f, fill=A(sc, al * ca), anchor="lm"); xx += f.getlength(seg)
            ly = by0 + code_h + 44; step = min(56, (cy1 - 110 - ly) / max(1, len(c.get("bullets", [])))) if c.get("bullets") else 0
            for bi, bl in enumerate(c.get("bullets", [])):
                bt, btxt = bl if isinstance(bl, (tuple, list)) else (c["t"] + 0.6 + 0.5 * bi, bl); ba = E(t, bt)
                if ba < 0.01: continue
                yy = ly + bi * step
                d.ellipse((cx0 + pad + 4, yy - 9 + (1 - ba) * 10, cx0 + pad + 22, yy + 9 + (1 - ba) * 10), fill=A(col, ba))
                _put(d, cx0 + pad + 40, yy + (1 - ba) * 10, btxt, 28, PAPER, ba, "lm", cw_ - 2 * pad - 44)
            if c.get("icon"): _vs_icon(d, c["icon"], (cx0 + cx1) / 2, cy1 - 52, 40, col, al)
        else:
            _put(d, cx1 - pad, cy0 + 56, nm, ns, col, al, "rm")
            if c.get("sub"): _put(d, cx0 + pad, cy0 + 56, c["sub"], 20, GRAYC, al, "lm", cw_ * 0.4)
            bx0 = cx0 + pad; by0 = cy0 + 100; split = cw_ * 0.46
            if c.get("code"):
                code_h = 28 + 40 * len(c["code"])
                d.rounded_rectangle((bx0, by0, bx0 + split, by0 + code_h), 16, fill=A((10, 11, 14), al), outline=A(col, al), width=3)
                ca = E(t, c.get("code_t", c["t"] + 0.3))
                for li, ln in enumerate(c["code"]):
                    xx = bx0 + 16; yy = by0 + 34 + li * 40; fs = _fit(max(c["code"], key=len), 22, split - 30, lo=14)
                    for seg, sc in _hl(ln, col):
                        f = F(MONO, fs); d.text((xx, yy), seg, font=f, fill=A(sc, al * ca), anchor="lm"); xx += f.getlength(seg)
            bl_x = bx0 + split + 26; nb = len(c.get("bullets", [])); step = min(50, (ch_ - 120) / max(1, nb)) if nb else 0
            for bi, bl in enumerate(c.get("bullets", [])):
                bt, btxt = bl if isinstance(bl, (tuple, list)) else (c["t"] + 0.6 + 0.5 * bi, bl); ba = E(t, bt)
                if ba < 0.01: continue
                yy = by0 + 20 + bi * step
                d.ellipse((bl_x, yy - 7, bl_x + 14, yy + 7), fill=A(col, ba)); _put(d, bl_x + 28, yy, btxt, 24, PAPER, ba, "lm", cx1 - pad - bl_x - 30)

def draw_matrix(d, box, b, t, k):
    """comparison table: header (coloured names) + rows; cell = 'ok' | 'bad' | 'mid' | text | (kind, note)"""
    heads = b["cols"]; rows = b["rows"]; x0, y0, x1, y1 = box; n = len(heads); W_ = x1 - x0
    ha = E(t, b["t"])
    if ha < 0.01: return
    hh = 88 if WIDE else 84; rh = 74 if WIDE else 82; lw_ = W_ * (0.30 if WIDE else 0.34); cwid = (W_ - lw_) / n
    th = hh + rh * len(rows) + 16
    d.rounded_rectangle((x0, y0, x1, y0 + th), 28, fill=A(CARDC, ha), outline=A((70, 73, 82), ha), width=3)
    _put(d, x1 - 30 if not b.get("ltr") else x0 + 30, y0 + hh / 2, b.get("title", ""), 30, PAPER, ha, "rm" if not b.get("ltr") else "lm") if b.get("title") else None
    for j, h in enumerate(heads):
        hx = x0 + lw_ + j * cwid; col = _col(h.get("color")); ca = E(t, h.get("t", b["t"] + 0.2 + 0.15 * j))
        if ca < 0.01: continue
        d.line([(hx + 14, y0 + hh - 4), (hx + cwid - 14, y0 + hh - 4)], fill=A(col, ca), width=5)
        _put(d, hx + cwid / 2, y0 + hh / 2 - 4, h["name"], 40 if WIDE else 34, col, ca, "mm", cwid - 20)
    last = max([i for i, r in enumerate(rows) if t >= r["t"]], default=-1)
    for i, r in enumerate(rows):
        ra = E(t, r["t"])
        if ra < 0.01: continue
        ry = y0 + hh + i * rh + (1 - ra) * 14
        if i == last and t - r["t"] < 3.0: d.rounded_rectangle((x0 + 10, ry + 4, x1 - 10, ry + rh - 4), 16, outline=A(OR, ra * 0.9), width=3)
        d.line([(x0 + 18, ry), (x1 - 18, ry)], fill=A((55, 58, 66), ra), width=2)
        _put(d, x0 + 34, ry + rh / 2, r["label"], 30 if WIDE else 27, PAPER, ra, "lm", lw_ - 40)
        for j, cell in enumerate(r["cells"]):
            q = prog(t, r["t"] + 0.15 * (j + 1), r["t"] + 0.15 * (j + 1) + 0.35)
            if q <= 0: continue
            kind, note = (cell if isinstance(cell, (tuple, list)) else (cell, None)); cx = x0 + lw_ + j * cwid + cwid / 2; cy = ry + rh / 2; col = _col(heads[j].get("color"))
            sym = {"ok": GRN, "bad": RED, "mid": AMB}.get(kind)
            if sym:
                off = -cwid * 0.17 if note else 0
                if kind == "mid" and not note: d.text((cx + off, cy), "~", font=F(MONO, 44), fill=A(sym, ra * ss(q)), anchor="mm")
                elif kind == "mid": d.text((cx + off, cy), "~", font=F(MONO, 40), fill=A(sym, ra * ss(q)), anchor="mm")
                else: _mark(d, kind, cx + off, cy, (17 if WIDE else 18) * (0.6 + 0.4 * ss(q)), sym, ra * ss(q), q)
                if note: _put(d, cx + cwid * 0.02, cy, note, 24 if WIDE else 20, col, ra * ss(q), "lm", cwid * 0.5)
            else: _put(d, cx, cy, str(kind), 30 if WIDE else 27, col, ra * ss(q), "mm", cwid - 24)

def draw_icon3d(d, kind, cx, cy, sz, al, t=0.0, tilt=True):
    """flat tile with extruded depth edge, soft shadow, gentle bobbing + tilt. kinds: play camera scissors code doc db"""
    pk = {"play": ((255, 84, 66), (214, 52, 38)), "camera": ((250, 240, 228), (205, 190, 172)), "scissors": ((250, 240, 228), (205, 190, 172)),
          "code": (OR, ORD), "doc": ((250, 240, 228), (205, 190, 172)), "db": (OR, ORD)}.get(kind, ((250, 240, 228), (205, 190, 172)))
    face, edge = pk; bob = math.sin(t * 2.2) * sz * 0.05; ang = math.sin(t * 1.3) * 5 if tilt else 0
    S = int(sz * 3.2); L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(L); c = S / 2
    w = sz * (1.45 if kind == "play" else 1.2); h = sz * (1.0 if kind == "play" else 1.2); r = int(sz * 0.3)
    for e in range(int(sz * 0.14), 0, -1): ld.rounded_rectangle((c - w / 2 + e * 0.5, c - h / 2 + e, c + w / 2 + e * 0.5, c + h / 2 + e), r, fill=edge + (255,))
    ld.rounded_rectangle((c - w / 2, c - h / 2, c + w / 2, c + h / 2), r, fill=face + (255,))
    ink = (255, 255, 255, 255) if kind == "play" else (255, 138, 17, 255) if kind != "code" else (10, 11, 13, 255)
    if kind == "play": ld.polygon([(c - 0.17 * sz, c - 0.3 * sz), (c - 0.17 * sz, c + 0.3 * sz), (c + 0.33 * sz, c)], fill=ink)
    elif kind == "camera":
        ld.rounded_rectangle((c - 0.42 * sz, c - 0.25 * sz, c + 0.1 * sz, c + 0.25 * sz), int(sz * 0.1), fill=ink); ld.polygon([(c + 0.16 * sz, c - 0.08 * sz), (c + 0.42 * sz, c - 0.2 * sz), (c + 0.42 * sz, c + 0.2 * sz), (c + 0.16 * sz, c + 0.08 * sz)], fill=ink)
    elif kind == "scissors":
        for sgn in (-1, 1): ld.ellipse((c - 0.38 * sz, c + sgn * 0.3 * sz - 0.12 * sz, c - 0.14 * sz, c + sgn * 0.3 * sz + 0.12 * sz), outline=ink, width=max(3, int(sz * 0.06))); ld.line([(c - 0.2 * sz, c + sgn * 0.22 * sz), (c + 0.4 * sz, c - sgn * 0.2 * sz)], fill=ink, width=max(3, int(sz * 0.07)))
    elif kind == "code": ld.text((c, c), "</>", font=F(MONO, int(sz * 0.5)), fill=ink, anchor="mm")
    elif kind == "doc":
        for i in range(4): ld.line([(c - 0.3 * sz, c - 0.33 * sz + i * 0.22 * sz), (c + 0.3 * sz - (0.2 * sz if i == 3 else 0), c - 0.33 * sz + i * 0.22 * sz)], fill=ink, width=max(3, int(sz * 0.07)))
    elif kind == "db":
        for i in range(3): ld.ellipse((c - 0.4 * sz, c - 0.4 * sz + i * 0.3 * sz, c + 0.4 * sz, c - 0.1 * sz + i * 0.3 * sz), outline=(10, 11, 13, 255), width=max(3, int(sz * 0.06)))
    L = L.rotate(ang, resample=Image.BICUBIC)
    if al < 0.999: L.putalpha(L.getchannel("A").point(lambda v: int(v * al)))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sc_ = 1 - 0.1 * math.sin(t * 2.2)
    ImageDraw.Draw(sh).ellipse((cx - sz * 0.55 * sc_, cy + sz * 0.78, cx + sz * 0.55 * sc_, cy + sz * 0.92), fill=(0, 0, 0, int(110 * al)))
    d._image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    px, py = int(cx - S / 2), int(cy + bob - S / 2)
    sx0, sy0 = max(0, -px), max(0, -py); L2 = L.crop((sx0, sy0, min(S, W - px), min(S, H - py)))
    if L2.size[0] > 0 and L2.size[1] > 0: d._image.alpha_composite(L2, (px + sx0, py + sy0))

def _cursor(d, x, y, al):
    d.polygon([(x, y), (x + 10, y + 66), (x + 27, y + 48), (x + 50, y + 76), (x + 65, y + 62), (x + 42, y + 36), (x + 66, y + 30)], fill=A(PAPER, al), outline=A(INK, al))

def _tab_scene(d, kind, box, tl, al):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2; cy = (y0 + y1) / 2; w_ = x1 - x0; h_ = y1 - y0
    if kind == "play":
        draw_icon3d(d, "play", cx, cy - h_ * 0.05, min(w_, h_) * 0.3, al, tl)
        yb = y1 - h_ * 0.14; xa, xb = x0 + w_ * 0.08, x1 - w_ * 0.08; p = (tl * 0.12) % 1.0
        d.rounded_rectangle((xa, yb - 6, xb, yb + 6), 6, fill=A((60, 63, 72), al)); d.rounded_rectangle((xa, yb - 6, xa + (xb - xa) * (0.1 + 0.8 * p), yb + 6), 6, fill=A((255, 40, 20), al))
        px = xa + (xb - xa) * (0.1 + 0.8 * p); d.ellipse((px - 16, yb - 16, px + 16, yb + 16), fill=A((255, 40, 20), al))
    elif kind == "rec":
        m = min(w_, h_) * 0.08; L = min(w_, h_) * 0.12
        for gx in (1, 2): d.line([(x0 + w_ * gx / 3, y0 + m), (x0 + w_ * gx / 3, y1 - m)], fill=A((50, 53, 62), al), width=2); d.line([(x0 + m, y0 + h_ * gx / 3), (x1 - m, y0 + h_ * gx / 3)], fill=A((50, 53, 62), al), width=2)
        for sx, sy in ((x0 + m, y0 + m), (x1 - m, y0 + m), (x0 + m, y1 - m), (x1 - m, y1 - m)):
            dx = L if sx < cx else -L; dy = L if sy < cy else -L
            d.line([(sx, sy), (sx + dx, sy)], fill=A(PAPER, al), width=5); d.line([(sx, sy), (sx, sy + dy)], fill=A(PAPER, al), width=5)
        blink = 0.5 + 0.5 * math.sin(tl * 6); d.ellipse((x0 + m + 26, y0 + m + 30, x0 + m + 46, y0 + m + 50), fill=A(RED, al * (0.5 + 0.5 * blink))); d.text((x0 + m + 62, y0 + m + 40), "REC", font=F(MONO, 28), fill=A(PAPER, al), anchor="lm")
        d.text((x1 - m - 26, y0 + m + 40), "00:00:%02d" % (int(tl) + 1), font=F(MONO, 26), fill=A(PAPER, al), anchor="rm")
        draw_icon3d(d, "camera", cx, cy, min(w_, h_) * 0.26, al, tl)
    elif kind == "edit":
        tr = [(0.20, [(0.05, 0.38, OR), (0.45, 0.30, (120, 130, 150))]), (0.38, [(0.12, 0.30, (120, 130, 150)), (0.46, 0.40, OR)]), (0.56, [(0.02, 0.22, OR), (0.28, 0.34, (120, 130, 150)), (0.66, 0.24, OR)])]
        base = y0 + h_ * 0.5
        for ti, (oy, clips) in enumerate(tr):
            yy = base + (oy - 0.25) * h_ * 0.8
            for cs, cw, cc in clips: d.rounded_rectangle((x0 + w_ * (0.06 + cs * 0.88), yy, x0 + w_ * (0.06 + (cs + cw) * 0.88), yy + h_ * 0.09), 10, fill=A(cc, al * 0.9))
        ph = x0 + w_ * (0.06 + 0.88 * ((tl * 0.15) % 1.0)); d.line([(ph, base - h_ * 0.2), (ph, y1 - h_ * 0.06)], fill=A(RED, al), width=4); d.polygon([(ph - 12, base - h_ * 0.2), (ph + 12, base - h_ * 0.2), (ph, base - h_ * 0.2 + 18)], fill=A(RED, al))
        draw_icon3d(d, "scissors", cx, y0 + h_ * 0.2, min(w_, h_) * 0.2, al, tl)
    elif kind == "script":
        for i in range(7):
            ln = (0.5, 0.8, 0.65, 0.9, 0.4, 0.75, 0.55)[i]; q = prog(tl, 0.2 + i * 0.35, 0.5 + i * 0.35)
            d.rounded_rectangle((x0 + w_ * 0.12, y0 + h_ * (0.18 + i * 0.1), x0 + w_ * (0.12 + 0.76 * ln * q), y0 + h_ * (0.18 + i * 0.1) + 22), 11, fill=A(OR if i in (0, 3) else (90, 94, 106), al))
    else: draw_icon3d(d, kind, cx, cy, min(w_, h_) * 0.3, al, tl)

def draw_tabcard(d, box, b, t, k):
    """one card, a row of tabs, a cursor that presses each tab, and a small animated scene inside per tab"""
    x0, y0, x1, y1 = box; ba = E(t, b["t"])
    if ba < 0.01: return
    cw_ = min(x1 - x0, 860 if WIDE else 940); ch_ = min(y1 - y0, 800 if WIDE else 1160); cx0 = (x0 + x1) / 2 - cw_ / 2; cy0 = y0 + (1 - ba) * 30
    cx1 = cx0 + cw_; cy1 = cy0 + ch_; pad = 26; tabs = b["tabs"]; n = len(tabs)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((cx0 + 8, cy0 + 24, cx1 + 8, cy1 + 24), 36, fill=(0, 0, 0, int(150 * ba)))
    d._image.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)))
    d.rounded_rectangle((cx0, cy0, cx1, cy1), 34, fill=A((22, 24, 30), ba), outline=A((60, 63, 72), ba), width=3)
    ty = cy0 + 54
    if b.get("title"): _put(d, cx1 - pad - 84, ty, b["title"], 36, PAPER, ba, "rm")
    d.rounded_rectangle((cx1 - pad - 70, ty - 24, cx1 - pad, ty + 24), 12, fill=A((255, 40, 20), ba)); d.polygon([(cx1 - pad - 41, ty - 11), (cx1 - pad - 41, ty + 11), (cx1 - pad - 22, ty)], fill=A(PAPER, ba))
    trow = ty + 70; tw = (cw_ - 2 * pad - 14 * (n - 1)) / n; th = 62
    act = max([i for i, tb in enumerate(tabs) if t >= tb["t"]], default=-1)
    pos = []
    for i, tb in enumerate(tabs):
        px0 = cx1 - pad - (i + 1) * tw - i * 14 if b.get("rtl", True) else cx0 + pad + i * (tw + 14); pos.append((px0, px0 + tw))
        on = (i == act); q = ss(prog(t, tb["t"], tb["t"] + 0.25)) if on else 0
        d.rounded_rectangle((px0, trow, px0 + tw, trow + th), 16, fill=A(lerp((38, 41, 49), (80, 48, 20), q), ba), outline=A(lerp((38, 41, 49), OR, q), ba), width=3)
        _put(d, px0 + tw / 2, trow + th / 2, tb["label"], 30, lerp(GRAYC, OR, q) if on else GRAYC, ba, "mm", tw - 20)
    d.line([(cx0 + 2, trow + th + 18), (cx1 - 2, trow + th + 18)], fill=A((45, 48, 56), ba), width=2)
    area = (cx0 + pad, trow + th + 36, cx1 - pad, cy1 - pad)
    for i, tb in enumerate(tabs):
        if i < max(act, 0) - 1 and act >= 0 or (act < 0 and i > 0): continue
        if act < 0: q = 1.0 if i == 0 else 0.0
        else: q = ss(prog(t, tb["t"], tb["t"] + 0.4)) if i == act else (1 - ss(prog(t, tabs[i + 1]["t"], tabs[i + 1]["t"] + 0.3)) if i + 1 < n and i + 1 <= act else 1.0 if i == act else 0.0)
        if i == act and act > 0: q = ss(prog(t, tb["t"], tb["t"] + 0.4))
        if i == act - 1: q = 1 - ss(prog(t, tabs[act]["t"], tabs[act]["t"] + 0.35))
        if q < 0.01: continue
        _tab_scene(d, tb.get("scene", "play"), area, t - tb["t"] if t >= tb["t"] else t - b["t"], ba * q)
    # cursor: travels to the next tab, presses at its time
    nxt = next((i for i, tb in enumerate(tabs) if t < tb["t"] + 0.55), None)
    if nxt is not None:
        tb = tabs[nxt]; tx = (pos[nxt][0] + pos[nxt][1]) / 2 + 20; tyy = trow + th * 0.65
        prev = (pos[nxt - 1][0] + pos[nxt - 1][1]) / 2 + 20 if nxt > 0 else tx + 200
        q = ss(prog(t, tb["t"] - 1.0, tb["t"] - 0.1)); px = prev + (tx - prev) * q; py = (tyy + (260 if nxt == 0 else 0) * (1 - q)) + (0 if nxt else 0)
        al_ = ba * (ss(prog(t, tb["t"] - 1.3, tb["t"] - 0.9)) if nxt == 0 else 1) * (1 - ss(prog(t, tb["t"] + 0.2, tb["t"] + 0.55)))
        rp = prog(t, tb["t"], tb["t"] + 0.6)
        if 0 < rp < 1:
            for r_ in (30 + 70 * rp, 14 + 44 * rp): d.ellipse((tx - r_, tyy - r_, tx + r_, tyy + r_), outline=A(OR, (1 - rp) * 0.8 * ba), width=4)
        if al_ > 0.02: _cursor(d, px, py, al_)

def draw_icon3d_row(d, box, b, t, k):
    items = b["items"]; n = len(items); x0, y0, x1, y1 = box
    cols = n if WIDE else b.get("cols_reel", 3); cells = _grid(box, n, cols, 10, False)
    for i, (it, (a0, b0, a1, b1)) in enumerate(zip(items, cells)):
        al = E(t, it["t"])
        if al < 0.01: continue
        cw_ = a1 - a0; cx = (a0 + a1) / 2; sz = min(cw_ * 0.34, (b1 - b0) * 0.3, 190); cyy = (b0 + b1) / 2 - 20 + (1 - al) * 40
        draw_icon3d(d, it["kind"], cx, cyy, sz, al, t + i)
        if it.get("label"): _put(d, cx, cyy + sz * 0.95 + 24, it["label"], 32, PAPER, al, "mm", cw_ - 20)

def _versus_h(b, w):
    n = len(b["cols"])
    return int(min(RY1 - RY0, b.get("h", 700)) if WIDE else min(RY1 - RY0, n * 440 + (n - 1) * 22))
def _matrix_h(b, w):
    return int(88 + (74 if WIDE else 82) * len(b["rows"]) + 16) if WIDE else int(84 + 82 * len(b["rows"]) + 16)
def _tabcard_h(b, w): return int(min(RY1 - RY0, 800 if WIDE else 1160))
def _icon3d_h(b, w): return int(min(RY1 - RY0, 420)) if WIDE else int(min(RY1 - RY0, -(-len(b["items"]) // b.get("cols_reel", 3)) * 330))
EXTRA_H.update({"versus": _versus_h, "matrix": _matrix_h, "tabcard": _tabcard_h, "icon3d": _icon3d_h})
DRAW["versus"] = draw_versus; DRAW["matrix"] = draw_matrix; DRAW["tabcard"] = draw_tabcard; DRAW["icon3d"] = draw_icon3d_row


class Video:
    def __init__(self, scenes, stages, dur, t_end, tag1, tag2, tech):
        self.scenes, self.stages, self.dur, self.t_end, self.tag1, self.tag2 = scenes, stages, dur, t_end, tag1, tag2
        self.N = int(round(FPS * dur)); self.bg = make_bg(tech)
        self.beats = []
        def _bt(bl):
            for b_ in bl:
                if b_["k"] in ("row", "tiles"): _bt(b_["items"])
                elif b_.get("key"): self.beats.append(b_["t"])
        for s_ in scenes: _bt(s_["blocks"])
        self.marks = [s_["t0"] for s_ in scenes[1:]]
        _cyc = ["squares", "pairs", "narrow"]; _ci = 0
        for s_ in scenes:   # every scene with cards gets ONE of: squares / pairs / narrow (user choice 2026-10-30)
            nc_ = sum(1 for b_ in s_["blocks"] if b_["k"] == "card")
            if nc_ >= 2 and not s_.get("grid") and not s_.get("cw") and not s_.get("longcards"):
                m_ = _cyc[_ci % 3]; _ci += 1
                if m_ == "narrow": s_["cw"] = 0.6
                elif nc_ >= 3 or m_ == "pairs": s_["grid"] = m_ if (m_ == "pairs" or nc_ >= 3) else "pairs"
                else: s_["cw"] = 0.6
        for s_ in scenes:   # grid layouts (16:9 only): pairs of cards side by side, or all cards as tiles in one row
            g_ = s_.get("grid")
            if g_ and WIDE:
                out_, cards_ = [], []
                for b_ in s_["blocks"]:
                    if b_["k"] == "card": cards_.append(b_)
                    else:
                        if cards_: out_.append(cards_[:]); cards_.clear()
                        out_.append(b_)
                if cards_: out_.append(cards_[:])
                nb_ = []
                for it_ in out_:
                    if isinstance(it_, list):
                        if g_ in ("tiles", "squares"):
                            for x_ in it_: x_.setdefault("size", 34)
                            nb_.append({"k": "tiles", "items": it_, "square": g_ == "squares"})
                        else:
                            for i_ in range(0, len(it_), 2):
                                ch_ = it_[i_:i_ + 2]
                                nb_.append({"k": "row", "split": 0.5, "items": ch_} if len(ch_) == 2 else ch_[0])
                    else: nb_.append(it_)
                s_["blocks"] = nb_
        for si_, s_ in enumerate(scenes):
            st_ = s_.get("style", "classic"); n_ = 0
            if st_ not in CARD_STYLES: st_ = CARD_STYLES[si_ % len(CARD_STYLES)]   # style not allowed by CTRLH_CARD_STYLES: rotate through the allowed ones
            def tag_(bl):
                nonlocal n_
                for b_ in bl:
                    if b_["k"] in ("row", "tiles"): tag_(b_["items"])
                    else:
                        b_["style"] = st_
                        if b_["k"] == "card": b_["idx"] = n_; n_ += 1
            tag_(s_["blocks"])
        self.btn = []   # fixed-time buttons (decided 2026-10-30): Subscribe at 0:45, Follow 40 s before the video ends
        for kind_, tb_ in (("subscribe", float(os.environ.get("SUB_T", 45))), ("follow", float(os.environ.get("FOL_T", dur - 40)))):
            if tb_ + 5.0 < t_end and (kind_ == "subscribe" or tb_ >= 53): self.btn.append({"kind": kind_, "t0": tb_, "t1": tb_ + 4.5})
        for s_ in scenes:
            if any(b_["t0"] < s_["t1"] and b_["t1"] > s_["t0"] for b_ in self.btn):
                s_["reserve"] = max(s_.get("reserve", 0), 170); s_["reserve_reel"] = max(s_.get("reserve_reel", 0), 230)
        self.lay = [layout(s["blocks"], s.get("reserve", 0) if WIDE else s.get("reserve_reel", 0), True, s.get("cw")) for s in scenes]
        self.st_times = []
        for i in range(len(stages)):
            ts = [(s["t0"], s["t1"]) for s in scenes if s["stage"] == i]
            self.st_times.append((min(a for a, _ in ts), max(b for _, b in ts)))

    def link_ghost(self, OV, t, k):
        """bridge between scenes: an orange frame leaves the last card of the scene and lands where the first card of the next scene will be"""
        for kk in (k, k - 1):
            if kk < 0 or kk >= len(self.scenes) - 1: continue
            tt = self.scenes[kk]["t1"]
            if not (tt - 0.35 <= t <= tt + 0.35): continue
            ca = [bx for bl, bx in self.lay[kk] if bl["k"] == "card"]; cb = [bx for bl, bx in self.lay[kk + 1] if bl["k"] == "card"]
            if not ca or not cb: continue
            A_, B_ = ca[-1], cb[0]; q = ss(prog(t, tt - 0.35, tt + 0.35)); al = math.sin(math.pi * q) ** 0.7
            bx = [A_[i] + (B_[i] - A_[i]) * q for i in range(4)]
            ImageDraw.Draw(OV).rounded_rectangle(bx, 26, outline=A(OR, 0.9 * al), width=6)
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle(bx, 26, outline=A(OR, 0.5 * al), width=16)
            OV.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
            return

    def frame(self, i):
        t = i / FPS
        if t >= self.t_end: return end_frame(t, self.t_end, self.tag1, self.tag2)
        k = 0
        for j, s in enumerate(self.scenes):
            if s["t0"] <= t < s["t1"]: k = j
        s = self.scenes[k]
        S = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
        HL = Image.new("RGBA", (W, H), (0, 0, 0, 0)); headline(ImageDraw.Draw(HL), s["head"], s["head_t"], t)
        for n, (blk, box) in enumerate(self.lay[k]):
            DRAW[blk["k"]](d, box, blk, t, n)
        OV = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for blk in s["blocks"]:
            if blk.get("abs"):
                if blk["k"] in ABS: ABS[blk["k"]](OV, blk, t)
                else: DRAW[blk["k"]](ImageDraw.Draw(OV), None, blk, t, 0)
        # camera: slow push-in + settle on scene entry + tiny beat on key hits
        z = 1.0 + 0.025 * prog(t, s["t0"], s["t1"]) + (0.04 * (1 - ss(prog(t, s["t0"], s["t0"] + 0.9))) if k > 0 else 0.0)
        for bt in self.beats:
            if 0 <= t - bt < 0.5: z += 0.014 * math.exp(-(t - bt) / 0.12)
        if z > 1.002:
            ya = RY0 - 10   # sub-pixel affine zoom (no integer crop snapping => no jitter), anchored under the headline
            S = S.transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 - W / (2 * z), 0, 1 / z, ya - ya / z), Image.BICUBIC)
        for td in s.get("dims", []):
            a_ = 0.5 * ss(prog(t, td - 0.9, td - 0.35)) * (1 - ss(prog(t, td - 0.05, td + 0.25)))
            if a_ > 0.01: S.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * a_))))
        S.alpha_composite(HL)
        if k < len(self.scenes) - 1 and s["t1"] - 1.8 < t < s["t1"]:   # preview of the next scene on the right edge
            q_ = prog(t, s["t1"] - 1.8, s["t1"] - 1.4) * (1 - prog(t, s["t1"] - 0.3, s["t1"]))
            if q_ > 0.01:
                P_ = ImageDraw.Draw(S); nt = self.scenes[k + 1]["head"]; f_ = F(ARB, 30); w_ = f_.getlength(nt, direction="rtl", language="ar") + 70
                xr = W - 20 + (1 - ss(q_)) * (w_ + 30); yr = (H - 210) if WIDE else 1630
                P_.rounded_rectangle((xr - w_, yr - 30, xr + 40, yr + 30), 30, fill=(30, 32, 38, int(235 * q_)), outline=A(OR, q_), width=3)
                P_.text((xr - w_ / 2 + 20, yr), nt, font=f_, fill=A(PAPER, q_), anchor="mm", direction="rtl", language="ar")
        # transitions: in (scene start), out (scene end)
        pin = 1 - ss(prog(t, s["t0"], s["t0"] + 0.34)) if k > 0 else 0.0
        pout = ss(prog(t, s["t1"] - 0.28, s["t1"])) if k < len(self.scenes) - 1 else 0.0
        ent = ("right", "up", "left")[k % 3]
        if pin > 0.003 and ent == "up": S = S.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -int(H * 0.12 * pin)), Image.BILINEAR); S.putalpha(S.getchannel("A").point(lambda v, p=pin: int(v * (1 - 0.8 * p))))
        elif pin > 0.003: S = mblur(S, 150 * pin, int(W * 0.18 * pin * (1 if ent == "right" else -1)), 1 - 0.8 * pin)
        elif pout > 0.003: S = mblur(S, 220 * pout, int(-W * 0.22 * pout), 1 - pout)
        im = self.bg.copy()
        bg_motion(im, t)
        im.alpha_composite(tabs_layer(t, self.stages, self.st_times, self.t_end, self.marks))
        for b_ in self.btn:
            if not any(x_.get("abs") and x_["k"] == "button" for x_ in s["blocks"]): abs_button(OV, b_, t)
        self.link_ghost(OV, t, k)
        chapter_banner(OV, t, self.st_times, self.stages)
        im.alpha_composite(S)
        im.alpha_composite(OV)
        corner_logo(im, t, self.t_end)
        return np.asarray(im.convert("RGB")).copy()


def run(V, argv):
    global _V
    _V = V
    if argv[1] == "frames":
        os.makedirs(argv[2], exist_ok=True)
        for ts in argv[3:]:
            i = int(round(float(ts) * FPS)); Image.fromarray(V.frame(i)).save(os.path.join(argv[2], f"x_{i:04d}.png"))
        return
    import multiprocessing as mp
    out = argv[2]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", (f"scale={os.environ['OUT_W']}:-2:flags=lanczos:" if os.environ.get("OUT_W") else "scale=") + "out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.get_context("fork").Pool(2) as pool:
        for k, b in enumerate(pool.imap(_job, range(V.N), chunksize=2)):
            pr.stdin.write(b)
            if k % 300 == 0: print("frame", k, flush=True)
    pr.stdin.close(); pr.wait(); print("done", V.N)


_V = None
def _job(i): return _V.frame(i).tobytes()
