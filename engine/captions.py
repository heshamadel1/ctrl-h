"""Optional Arabic captions: a rounded box with an orange highlighter on the key words, burned in as PNG overlays
(PIL + RAQM per-token RTL layout; libass breaks on mixed Arabic/Latin).
usage: captions.py cues.txt in.mp4 out.mp4 [--reel] [--no-auto-en] [--y 985] [--size 58]
cues.txt, one cue per line:   start<TAB>end<TAB>text      (seconds; text may contain [[highlighted words]])
Every English word is highlighted automatically (turn off with --no-auto-en). Colours follow the theme (CTRLH_THEME).
Only the video is re-encoded; the audio is copied."""
import os, re, sys, subprocess, tempfile, shutil
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import ctrlh_config, themes
from PIL import Image, ImageDraw, ImageFont, ImageFilter
th = themes.THEMES.get((os.environ.get("CTRLH_THEME") or "orange").lower(), themes.THEMES["orange"])
ASSETS = os.environ.get("CTRLH_ASSETS") or os.path.join(here, "..", "assets")
FONT = os.environ.get("CTRLH_FONT_AR") or os.path.join(ASSETS, "fonts", "Cairo-SemiBold.ttf")
OR = tuple(th["accent"]) + (255,); LIGHT = bool(th.get("light"))
BOX = tuple(th["card"]) + (255,); INK = (22, 20, 18, 255) if LIGHT else (245, 245, 245, 255); HLINK = (22, 20, 18, 255)
def font(s): return ImageFont.truetype(FONT, s, layout_engine=ImageFont.Layout.RAQM)
def tokens(text, auto_en=True):
    out = []
    for m in re.finditer(r"\[\[(.+?)\]\]|(\S+)", text):
        out.append((m.group(1), True) if m.group(1) else (m.group(2), False))
    merged = []
    for w, hl in out:
        core = w.replace("؟", "").replace("،", "").replace("؛", ""); lat = core.isascii() and any(c.isalpha() for c in core)
        if lat and auto_en: hl = True
        if merged and lat and merged[-1][2] and merged[-1][1] == hl: merged[-1] = (merged[-1][0] + " " + w, hl, True)
        else: merged.append((w, hl, lat))
    return merged
def render(text, size=58, W=1920, H=1080, y=985, maxw=None, auto_en=True):
    maxw = maxw or int(W * 0.81); f = font(size); toks = tokens(text, auto_en); sp = f.getlength(" ")
    wl = lambda t, lat: f.getlength(t) if lat else f.getlength(t, direction="rtl", language="ar")
    lines, cur, cw = [], [], 0
    for t in toks:
        w = wl(t[0], t[2])
        if cur and cw + sp + w > maxw: lines.append(cur); cur, cw = [], 0
        cur.append(t); cw += (sp if len(cur) > 1 else 0) + w
    lines.append(cur)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); lh = int(size * 1.45); y0 = y - (len(lines) - 1) * lh
    widths = [sum(wl(t[0], t[2]) for t in ln) + sp * (len(ln) - 1) for ln in lines]; bw = max(widths) + 90
    bx0, bx1 = (W - bw) / 2, (W + bw) / 2; by0, by1 = y0 - size * .95, y0 + (len(lines) - 1) * lh + size * .95
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((bx0, by0 + 10, bx1, by1 + 10), 30, fill=(0, 0, 0, 70 if not LIGHT else 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((bx0, by0, bx1, by1), 30, fill=BOX, outline=OR, width=4)
    for li, ln in enumerate(lines):
        tot = sum(wl(t[0], t[2]) for t in ln) + sp * (len(ln) - 1); x = (W + tot) / 2; yy = y0 + li * lh
        for t, hl, lat in ln:
            w = wl(t, lat); col = HLINK if hl else INK
            if hl: d.rounded_rectangle((x - w - 14, yy - size * .62, x + 14, yy + size * .62), 22, fill=OR)
            if lat: d.text((x - w, yy), t, font=f, fill=col, anchor="lm")
            else: d.text((x, yy), t, font=f, fill=col, anchor="rm", direction="rtl", language="ar")
            x -= w + sp
    return im
def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]; opt = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
    cues_f, vin, vout = a[:3]; reel = "--reel" in sys.argv; W, H = (1080, 1920) if reel else (1920, 1080)
    size = int(opt("--size", 52 if reel else 58)); y = int(opt("--y", 1500 if reel else 985)); auto = "--no-auto-en" not in sys.argv
    cues = []
    for ln in open(cues_f, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 3 and p[0].strip(): cues.append((float(p[0]), float(p[1]), p[2]))
    tmp = tempfile.mkdtemp(); blank = os.path.join(tmp, "blank.png"); Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vin]).decode()); lst = ["ffconcat version 1.0"]; t = 0.0
    for i, (s, e, tx) in enumerate(sorted(cues)):
        if s > t: lst += ["file blank.png", "duration %.3f" % (s - t)]
        p = os.path.join(tmp, "c%03d.png" % i); render(tx, size, W, H, y, auto_en=auto).save(p); lst += ["file c%03d.png" % i, "duration %.3f" % (e - s)]; t = e
    if dur > t: lst += ["file blank.png", "duration %.3f" % (dur - t)]
    lst += ["file blank.png"]; open(os.path.join(tmp, "caps.txt"), "w").write("\n".join(lst))
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", vin, "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "caps.txt"),
        "-filter_complex", "[1:v]fps=30,format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass[v]", "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy", "-t", "%.3f" % dur, vout])
    shutil.rmtree(tmp); print("captions ->", vout, "(%d cues)" % len(cues))
if __name__ == "__main__": main()
