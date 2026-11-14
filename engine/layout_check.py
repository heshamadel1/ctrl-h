"""Layout check for BOTH formats (Phase 11), without rendering a video:  python3 engine/layout_check.py my_scenes.py [--fmt wide|reel|both] [--json] [--strict]

For every scene and each format it uses the real layout boxes plus ONE sampled frame (all blocks visible), and reports:
  safe-area   a block box leaves the safe rectangle (wide: 60 px sides, 40 px bottom; reel: 54 px sides, bottom 180 px kept free for the platform caption / buttons)
  overlap     two stacked blocks intersect
  overflow    drawn pixels (text, glow, shadow) outside every block box plus a 40 px margin = text or content running out of its card
  squeeze     the scene was scaled down to fit (text scale < 100%); under 80% it is flagged as hard to read; also "fits wide but squeezed in reel"
  camera      scene camera / push-in crops content at one of its key times
  sparse      the scene uses less than 12% of the safe area (probably empty)
Findings are WARN (look at it) or ERROR (broken: content outside the frame / overlapping). Exit code 1 only with errors, or with --strict also on warnings.
It finds geometry problems; it cannot judge taste. Use `python3 engine/render.py my_scenes frames dir <seconds...>` and look at the frames flagged here.
Each format runs in its own process (the engine reads FMT at import). Frames are a pure function of time, so results are repeatable."""
import os, sys, json, subprocess, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SAFE = {"wide": {"x": 60, "top": 0, "bottom": 40}, "reel": {"x": 54, "top": 0, "bottom": 180}}
MARGIN = 40        # px around the union of boxes where soft shadows/glows are expected
OVERFLOW_PX = 400  # changed pixels outside the boxes before it counts (ignores faint glow specks)

def _inter(a, b): return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))

def child(scene_name, fmt):
    os.environ["FMT"] = fmt; os.environ["CTRLH_CACHE"] = "0"; os.environ.setdefault("CTRLH_CONFIG", os.devnull)
    sys.path.insert(0, os.getcwd()); import numpy as np, scenefile, anim
    scene_name = scene_name[:-3] if scene_name.endswith(".py") else scene_name
    N = scenefile.load(scene_name); W, H = anim.W, anim.H; sf = SAFE[fmt]; out = []
    def add(level, si, t, rule, msg): out.append({"fmt": fmt, "level": level, "scene": si, "t": None if t is None else round(t, 2), "rule": rule, "msg": msg})
    mk = lambda sc: anim.Video(copy.deepcopy(sc), N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH)
    V = mk(N.SC)
    VF = mk([dict(x, blocks=[b for b in x["blocks"] if not b.get("abs")]) for x in N.SC]); VE = mk([dict(x, blocks=[], entities=[]) for x in N.SC])   # blocks only (no abs overlays) vs. none: the difference is the content
    px = lambda v, f: np.asarray(v.frame(f))[..., :3].astype(int)
    for w in V.warn:
        if "squeezed" in w: pass
    scales = {}
    for si, s in enumerate(V.scenes):
        boxes = [(b, tuple(box)) for b, box in V.lay[si] if box is not None and not b.get("abs")]
        for b, bx in boxes:
            if bx[0] < sf["x"] - 0.5 or bx[2] > W - sf["x"] + 0.5 or bx[3] > H - sf["bottom"] + 0.5 or bx[1] < sf["top"] - 0.5 or bx[0] < 0 or bx[2] > W or bx[3] > H:
                lvl = "ERROR" if (bx[0] < 0 or bx[2] > W or bx[3] > H or bx[1] < 0) else "WARN"
                add(lvl, si, s["t0"], "safe-area", "%s box %s leaves the %s safe area (sides %d px, bottom %d px)" % (b["k"], tuple(int(v) for v in bx), fmt, sf["x"], sf["bottom"]))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a_, b_ = boxes[i][1], boxes[j][1]; ov = _inter(a_, b_)
                if ov > 0.02 * min((a_[2] - a_[0]) * (a_[3] - a_[1]), (b_[2] - b_[0]) * (b_[3] - b_[1])): add("ERROR", si, s["t0"], "overlap", "%s and %s overlap (%d px²)" % (boxes[i][0]["k"], boxes[j][0]["k"], ov))
        # squeeze: layout.scale at build time is stored only in warnings; recompute from the message
        sq = [w for w in V.warn if w.startswith("scene %d (" % si) and "squeezed" in w]
        if sq:
            pct = int(sq[0].split("squeezed to ")[1].split("%")[0]); scales[si] = pct
            add("WARN" if pct >= 80 else "ERROR" if pct < 60 else "WARN", si, s["t0"], "squeeze", "content scaled down to %d%% to fit%s" % (pct, " (hard to read: split the scene or shorten the cards)" if pct < 80 else ""))
        area = sum((b[2] - b[0]) * (b[3] - b[1]) for _, b in boxes); safe = (W - 2 * sf["x"]) * (H - sf["top"] - sf["bottom"])
        if boxes and area / safe < 0.12: add("WARN", si, s["t0"], "sparse", "content fills only %d%% of the %s safe area" % (area / safe * 100, fmt))
        # pixel checks on one frame: full scene vs the same scene without (non-abs) blocks
        tb = [b.get("t", s["t0"]) for b, _ in boxes if isinstance(b.get("t", 0), (int, float))] or [s["t0"]]
        try:   # sample while the scene is settled: after its entry transition, before its exit transition
            import transitions as _tr; dflt = _tr.global_default(); sp_in, sp_out = _tr.resolve(s, True, dflt), _tr.resolve(s, False, dflt)
            lo = s["t0"] + (sp_in.dur if sp_in.dur is not None else _tr.IN_DUR) + 0.05; hi = s["t1"] - (sp_out.dur if sp_out.dur is not None else _tr.OUT_DUR) - 0.05
        except Exception: lo, hi = s["t0"] + 0.5, s["t1"] - 0.6
        t = min(max(max(tb) + 1.2, lo), hi) if hi > lo else (s["t0"] + s["t1"]) / 2; f = int(t * 30)
        A = px(VF, f); B = px(VE, f)
        D = np.abs(A - B).sum(axis=2) > 30
        mask = np.zeros_like(D)
        for _, bx in boxes: mask[max(0, int(bx[1]) - MARGIN):min(H, int(bx[3]) + MARGIN), max(0, int(bx[0]) - MARGIN):min(W, int(bx[2]) + MARGIN)] = True
        outside = int((D & ~mask).sum())
        if boxes and outside > OVERFLOW_PX:
            ys, xs = np.nonzero(D & ~mask); add("WARN", si, t, "overflow", "%d drawn pixels outside the block boxes (x %d-%d, y %d-%d): text or content running out of its card" % (outside, xs.min(), xs.max(), ys.min(), ys.max()))
        if D.any():
            ys, xs = np.nonzero(D)
            if xs.min() < 2 or ys.min() < 2 or xs.max() > W - 3 or ys.max() > H - 3: add("ERROR", si, t, "overflow", "content touches the frame edge (cropped?)")
        if s.get("camera"):
            for kf in s["camera"]:
                tk = kf[0]
                if not (s["t0"] <= tk < s["t1"]): continue
                fk = int(tk * 30); Ac = px(VF, fk); Bc = px(VE, fk); Dc = np.abs(Ac - Bc).sum(axis=2) > 30
                if Dc.any():
                    ys, xs = np.nonzero(Dc)
                    if xs.min() < 2 or ys.min() < 2 or xs.max() > W - 3 or ys.max() > H - 3: add("WARN", si, tk, "camera", "camera crops content at t=%.1f (zoom/pan moves a block past the frame edge)" % tk)
    return out

def run(scene_name, fmts):
    res = []
    for fmt in fmts:
        env = dict(os.environ, FMT=fmt, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", scene_name, fmt], capture_output=True, text=True, env=env, cwd=os.getcwd())
        if r.returncode: raise SystemExit("layout_check (%s) failed:\n%s" % (fmt, (r.stderr or r.stdout)[-1500:]))
        res += json.loads(r.stdout.strip().splitlines()[-1])
    if len(fmts) == 2:   # a scene that fits in wide but is squeezed in reel needs a reel-specific fix
        wide_sq = {f["scene"] for f in res if f["fmt"] == "wide" and f["rule"] == "squeeze"}
        for f in list(res):
            if f["fmt"] == "reel" and f["rule"] == "squeeze" and f["scene"] not in wide_sq:
                res.append({"fmt": "reel", "level": "WARN", "scene": f["scene"], "t": f["t"], "rule": "format-mismatch", "msg": "fits wide but is squeezed in reel: shorten cards, split the scene, or use per-format fields (reserve_reel, cw)"})
    return res

def main(a):
    if a and a[0] == "--child": print(json.dumps(child(a[1], a[2]))); return 0
    args = [x for x in a if not x.startswith("--")]
    if not args: print(__doc__); return 2
    fmt = a[a.index("--fmt") + 1] if "--fmt" in a else "both"; args = [x for x in args if x != fmt]
    res = run(args[0], ["wide", "reel"] if fmt == "both" else [fmt])
    if "--json" in a: print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for f in res: print("%-5s %-4s scene %-2s %s %-15s %s" % (f["level"], f["fmt"], f["scene"], ("t=%-5s" % f["t"]) if f["t"] is not None else "       ", f["rule"], f["msg"]))
        e = sum(f["level"] == "ERROR" for f in res); w = len(res) - e; print("LAYOUT: %d error(s), %d warning(s) (%s)" % (e, w, fmt))
    return 1 if any(f["level"] == "ERROR" for f in res) or ("--strict" in a and res) else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
