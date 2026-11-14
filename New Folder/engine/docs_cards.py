"""Make the card sheets: python3 engine/docs_cards.py   (from the kit root). Needs examples/cards_scenes.py; writes docs/images/cards-dark.png and cards-paper.png"""
import os, sys, subprocess, tempfile, glob
from PIL import Image, ImageDraw, ImageFont
kit = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(kit, "engine"))
import card_names
ts = [str(i * 6 + 5) for i in range(12)]
font = None
for f in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True):
    if "DejaVuSansMono-Bold" in f or "FiraCode" in f: font = f; break
def sheet(theme, out):
    d = tempfile.mkdtemp(); env = dict(os.environ, FMT="wide", CTRLH_CARD_STYLES="all", PYTHONPATH=os.path.join(kit, "examples") + ":" + os.path.join(kit, "engine"))
    if theme: env["CTRLH_THEME"] = theme
    subprocess.run([sys.executable, os.path.join(kit, "engine", "render.py"), "cards_scenes", "frames", d] + ts, cwd=os.path.join(kit, "examples"), env=env, check=True, capture_output=True)
    fr = sorted(glob.glob(d + "/*.png")); w, h, lab = 640, 360, 34
    S = Image.new("RGB", (w * 3, (h + lab) * 4), (20, 20, 22)); dr = ImageDraw.Draw(S); F = ImageFont.truetype(font, 22) if font else None
    for i, (f, (name, old, desc)) in enumerate(zip(fr, card_names.NAMES)):
        x, y = (i % 3) * w, (i // 3) * (h + lab)
        S.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        dr.text((x + 10, y + h + 5), "C%02d  %s" % (i + 1, name), fill=(255, 138, 17), font=F)
    S.quantize(256, dither=Image.NONE).save(out, optimize=True); print(out)
img = os.path.join(kit, "docs", "images")
sheet(None, os.path.join(img, "cards-dark.png")); sheet("paper_orange", os.path.join(img, "cards-paper.png"))
