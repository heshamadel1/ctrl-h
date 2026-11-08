"""Fast look at a scene file without rendering the whole video.
usage (run from the scene file's folder):
  python3 preview.py <scenes> --t 12,40,80 [--out DIR]      full-size PNG frames at those times + a contact sheet
  python3 preview.py <scenes> --scene 3,5 [--out DIR]       the frame near the end of those scenes (blocks fully drawn)
  python3 preview.py <scenes> --clip 80 86 [--out DIR]      a short mp4 of that window (renders only those seconds)
Frames take a few seconds each; a 6 s clip about a minute."""
import sys, os, subprocess
here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.getcwd(), here]
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
import ctrlh_config, scenefile
mod = sys.argv[1]; out = os.path.abspath(opt("--out", "preview")); os.makedirs(out, exist_ok=True)
N = scenefile.load(mod); base = scenefile.base_name(mod)
if "--clip" in sys.argv:
    i = sys.argv.index("--clip"); a, b = sys.argv[i + 1], sys.argv[i + 2]
    env = dict(os.environ, CTRLH_T0=a, CTRLH_T1=b, CTRLH_CACHE="0"); dst = os.path.join(out, "%s_clip_%s_%s.mp4" % (base, a, b))
    subprocess.run([sys.executable, os.path.join(here, "render.py"), mod, dst], env=env, check=True); print("clip:", dst); sys.exit(0)
if opt("--scene"): ts = [N.SC[int(k)]["t0"] + (N.SC[int(k)]["t1"] - N.SC[int(k)]["t0"]) * 0.85 for k in opt("--scene").split(",")]
else: ts = [float(x) for x in (opt("--t") or "5").split(",")]
subprocess.run([sys.executable, os.path.join(here, "render.py"), mod, "frames", out] + ["%.2f" % t for t in ts], check=True)
from PIL import Image
import glob
fs = sorted(glob.glob(os.path.join(out, "*.png")))
if len(fs) > 1:
    ims = [Image.open(f).convert("RGB") for f in fs]; cw = 640 if ims[0].width > ims[0].height else 360; ch = int(ims[0].height * cw / ims[0].width); cols = 3 if cw == 640 else 4
    sh = Image.new("RGB", (cw * cols, ch * (-(-len(ims) // cols))))
    for j, im in enumerate(ims): sh.paste(im.resize((cw, ch)), ((j % cols) * cw, (j // cols) * ch))
    sh.save(os.path.join(out, "_sheet.png")); print("sheet:", os.path.join(out, "_sheet.png"))
print("frames in", out)
