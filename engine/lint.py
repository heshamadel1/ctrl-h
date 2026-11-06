"""Check a scene file WITHOUT rendering. usage (run from the scene file's folder):
  python3 lint.py <scenes_module> [--strict] [--sheet out.png] [--fmt wide|reel]
Prints every LINT line, timing problems, and the features the configured video_type expects but the script lacks.
--strict : exit code 1 when anything is reported (use it before a long render).
--sheet  : contact sheet with one frame per scene (late in the scene, so its blocks are visible)."""
import sys, os, json, importlib
here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.getcwd(), here]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
if opt("--fmt"): os.environ["FMT"] = opt("--fmt")
N = importlib.import_module(args[0])
import ctrlh_config
from anim import Video, FPS
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    V = Video(N.SC, N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH, getattr(N, "SUB_T", None), getattr(N, "FOL_T", None))
issues = [l.replace("LINT: ", "") for l in buf.getvalue().splitlines() if l.startswith("LINT:")]
SC = N.SC
def kinds(bl):
    for b in bl:
        yield b["k"]
        if b["k"] in ("row", "tiles"): yield from kinds(b["items"])
for i, s in enumerate(SC):
    if s["t1"] <= s["t0"]: issues.append("scene %d: t1 <= t0" % i)
    if i and abs(s["t0"] - SC[i - 1]["t1"]) > 0.02: issues.append("scene %d: gap/overlap with the previous scene (%.2f vs %.2f)" % (i, s["t0"], SC[i - 1]["t1"]))
    for b in s["blocks"]:
        tb = b.get("t", b.get("t0"))
        if tb is not None and not b.get("abs") and not (s["t0"] - 0.05 <= tb <= s["t1"]): issues.append("scene %d: %s block appears at %.1f, outside the scene (%.1f-%.1f)" % (i, b["k"], tb, s["t0"], s["t1"]))
if SC and SC[-1]["t1"] > N.DUR + 0.05: issues.append("last scene ends after DUR")
types = json.load(open(os.path.join(here, "..", "profiles", "video-types.json"), encoding="utf-8"))
vt = os.environ.get("CTRLH_VIDEO_TYPE", "explainer"); T = types.get(vt)
used = {k for s in SC for k in kinds(s["blocks"])}
if T:
    if len(SC) < T.get("min_scenes", 0): issues.append("video_type '%s' expects at least %d scenes, found %d" % (vt, T["min_scenes"], len(SC)))
    miss = [f for f in T.get("features", []) if f not in used]
    if miss: issues.append("video_type '%s': features not used: %s (use them, or say why they do not fit the script)" % (vt, ", ".join(miss)))
    for grp in T.get("any_of", []):
        if not used & set(grp): issues.append("video_type '%s': no technical block used (one of %s)" % (vt, ", ".join(grp)))
dis = {x for x in os.environ.get("CTRLH_DISABLED_BLOCKS", "").split(",") if x}
print("video_type: %s | scenes: %d | blocks used: %s%s" % (vt, len(SC), ", ".join(sorted(used)), " | disabled: " + ", ".join(sorted(dis)) if dis else ""))
for m in issues: print("LINT:", m)
if not issues: print("LINT: clean")
if opt("--sheet"):
    from PIL import Image
    ts = [s["t0"] + (s["t1"] - s["t0"]) * 0.8 for s in SC]; ims = []
    for t in ts:
        ims.append(Image.fromarray(V.frame(int(round((t - V.t_off) * FPS)))))
    cw = 640 if ims[0].width > ims[0].height else 360; ch = int(ims[0].height * cw / ims[0].width); cols = 3 if cw == 640 else 4
    sh = Image.new("RGB", (cw * cols, ch * (-(-len(ims) // cols))))
    for j, im in enumerate(ims): sh.paste(im.resize((cw, ch)), ((j % cols) * cw, (j // cols) * ch))
    sh.save(opt("--sheet")); print("sheet:", opt("--sheet"))
if "--strict" in sys.argv and issues: sys.exit(1)
