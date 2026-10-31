"""Make preview sheets so a new user can SEE the choices.  python3 ctrlh_preview.py <out_dir>
writes themes.png and backgrounds.png (card styles: see docs/images/cards-*.png)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes, bg_styles
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); FONT = os.path.join(HERE, "..", "assets", "fonts", "FiraCode-SemiBold.ttf")
def f(sz): return ImageFont.truetype(FONT, sz)
def themes_sheet(out):
    names = list(themes.THEMES); cw, ch = 520, 292; cols = 3; rows = -(-len(names) // cols)
    sh = Image.new("RGB", (cw * cols, ch * rows))
    for i, n in enumerate(names):
        t = themes.THEMES[n]; im = bg_styles.make("circuit", cw, ch, t["accent"], t["base"]).convert("RGB"); d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 90, cw - 60, 190), 18, fill=t["card"], outline=t["accent"], width=4); d.text((cw / 2, 140), "Cache first", font=f(30), fill=(245, 245, 245), anchor="mm")
        d.rounded_rectangle((cw / 2 - 90, 28, cw / 2 + 90, 70), 14, fill=t["accent"]); d.text((cw / 2, 49), n, font=f(24), fill=(10, 11, 13), anchor="mm")
        d.text((cw / 2, 226), themes.hexs(t["accent"]), font=f(22), fill=t["accent"], anchor="mm"); d.text((cw / 2, 258), t["note"], font=f(15), fill=(150, 156, 170), anchor="mm")
        sh.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sh.save(out)
def backgrounds_sheet(out, accent=(255, 138, 17), base=(13, 14, 16)):
    names = list(bg_styles.STYLES); cw, ch = 520, 292; cols = 4; rows = -(-len(names) // cols)
    sh = Image.new("RGB", (cw * cols, ch * rows))
    for i, n in enumerate(names):
        im = bg_styles.make(n, cw * 2, ch * 2, accent, base).convert("RGB").resize((cw, ch), Image.LANCZOS); d = ImageDraw.Draw(im)
        d.rounded_rectangle((cw / 2 - 80, ch / 2 - 22, cw / 2 + 80, ch / 2 + 22), 12, fill=(0, 0, 0)); d.text((cw / 2, ch / 2), n, font=f(24), fill=accent, anchor="mm")
        sh.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sh.save(out)
if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(o, exist_ok=True)
    themes_sheet(os.path.join(o, "themes.png")); backgrounds_sheet(os.path.join(o, "backgrounds.png")); print("ok", o)
