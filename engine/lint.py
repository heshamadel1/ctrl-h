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
import scenefile; N = scenefile.load(args[0])
import ctrlh_config
from anim import Video, FPS
import io, contextlib
_missing = [i for i in range(len(N.STAGES)) if not any(x['stage'] == i for x in N.SC)]
if _missing: sys.exit('LINT: STAGES %s have no scene (every stage needs at least one scene with stage=<index>)' % [N.STAGES[i] for i in _missing])
buf = io.StringIO()
try:
  with contextlib.redirect_stdout(buf):
    V = Video(N.SC, N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH, getattr(N, "SUB_T", None), getattr(N, "FOL_T", None))
except ValueError as _e: sys.exit('LINT: %s' % _e)
issues = [l.replace("LINT: ", "") for l in buf.getvalue().splitlines() if l.startswith("LINT:")]
SC = N.SC
import anim as _an
if not os.path.exists(_an.SD + "logo_ch.png"): issues.append("logo missing: put your logo at %slogo_ch.png (or set CTRLH_ASSETS); without it the corner logo and the end card show an empty frame" % _an.SD)
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

# ---- smarter text / structure rules
import re
def _strs(o, out):
    if isinstance(o, str): out.append(o)
    elif isinstance(o, dict):
        for v in o.values(): _strs(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o: _strs(v, out)
AR = "\u0600-\u06FF"
for i, s in enumerate(SC):
    tx = []; _strs({k: v for k, v in s.items() if k not in ("style", "stage", "transition", "trans_in", "trans_out", "camera", "entities", "sfx")}, tx)
    for t_ in tx:
        if re.search("\u0648(?=[A-Za-z])", t_) and re.search("(^|\\s)\u0648[A-Za-z]", t_): issues.append("scene %d: Arabic waw glued to a Latin word in %r (drawn as Arabic waw + a small gap + the Latin word; the isolated waw looks like a Latin g in Cairo, so a space or '+' reads clearer)" % (i, t_[:40]))
        if re.search("[A-Za-z0-9)]\\s\u0648\\s[A-Za-z]", t_): issues.append("scene %d: lone waw between Latin words in %r (use '+' or a comma)" % (i, t_[:40]))
        if re.search("\u0627\u0644\u0640 [A-Za-z]", t_): issues.append("scene %d: use a non-breaking space between the Arabic prefix and the Latin word in %r" % (i, t_[:40]))
    if not s["blocks"]: issues.append("scene %d: has no blocks (empty screen)" % i)
    starts = sorted(b.get("t", b.get("t0", s["t0"])) for b in s["blocks"] if not b.get("abs"))
    if s["t1"] - s["t0"] > 25 and len(starts) < 2: issues.append("scene %d: %.0f s long with fewer than 2 things appearing (static screen)" % (i, s["t1"] - s["t0"]))
    for b in s["blocks"]:
        if b["k"] == "tracks":
            for _tr_ in b.get("tracks", []):
                if _tr_.get("kind", "video") not in ("video", "audio", "subtitle"): issues.append("scene %d: tracks: track %r has kind %r (use video, audio or subtitle)" % (i, _tr_.get("id"), _tr_.get("kind")))
                for _c in _tr_.get("clips", []):
                    if not all(x in _c for x in ("id", "start", "len")): issues.append("scene %d: tracks: a clip in track %r needs id, start and len" % (i, _tr_.get("id"))); continue
                    if _c["start"] + _c["len"] > b.get("dur", 20.0) + 1e-6: issues.append("scene %d: tracks: clip %r ends at %.1f s, after the timeline dur (%.1f)" % (i, _c["id"], _c["start"] + _c["len"], b.get("dur", 20.0)))
                    if any(len(e_) != 3 for e_ in _c.get("edits", [])): issues.append("scene %d: tracks: clip %r edits must be (t, new_start, new_len)" % (i, _c["id"]))
        if b["k"] == "beam":
            for _p in b.get("paths", []):
                for _e in ("from", "to"):
                    if _p.get(_e) not in b.get("nodes", {}): issues.append("scene %d: beam path %r points to an unknown node %r (nodes: %s)" % (i, _p.get("label", ""), _p.get(_e), ", ".join(b.get("nodes", {}))))
                if _p.get("style", "both") not in ("draw", "beam", "both"): issues.append("scene %d: beam path style %r (use draw, beam or both)" % (i, _p.get("style")))
                if _p.get("dir", "fwd") not in ("fwd", "back", "both"): issues.append("scene %d: beam path dir %r (use fwd, back or both)" % (i, _p.get("dir")))
            for _n, _d in b.get("nodes", {}).items():
                if "pos" not in _d: issues.append("scene %d: beam node %r has no pos" % (i, _n))
        if b["k"] == "card" and len(b.get("text", "")) > 46: issues.append("scene %d: card text is %d chars (max ~46): %r" % (i, len(b["text"]), b["text"][:30]))
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
# ---- variety (owner, 2026-11-09): do not reuse the same cards/blocks in every video; try something new each time
_k = lambda sc: sorted({k_ for k_ in kinds(sc["blocks"]) if k_ not in ("row", "tiles")})
_distinct = {k_ for sc in SC for k_ in _k(sc)}; _need = min(8, max(3, len(SC) // 2))
if len(SC) >= 6 and len(_distinct) < _need: issues.append("variety: only %d block kinds in %d scenes (aim for %d or more); try: %s" % (len(_distinct), len(SC), _need, ", ".join(sorted(set(_an.DRAW) - _distinct - {"row", "tiles"})[:8])))
for _i in range(1, len(SC)):
    if _k(SC[_i]) == _k(SC[_i - 1]) and len(SC) >= 6: issues.append("variety: scenes %d and %d use the same block kinds (%s); change one of them" % (_i - 1, _i, ", ".join(_k(SC[_i]))))
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
