"""Persistent scene entities (Phase 5.2): one logical object that lives ACROSS scenes, keeps its identity, moves on global-time keyframes and can
change what it looks like (card -> browser window -> video preview) with a cross-fade, in both 16:9 and 9:16.

Where it lives: entities are drawn in a layer ABOVE the scene content and BELOW the opening/closing chrome, after the scene transition has been
applied, so a scene slide/fade never drags or cuts an entity: the entity belongs to the video timeline, not to a scene. A scene opts in by listing
entity dicts under the scene key "entities"; the same id may appear in only one scene's list (that is its definition), it then runs on global time.

  {"id": "hero",                                      # identity (unique across the whole video)
   "t_in": 0.5, "t_out": 20.0,                        # lifetime on the global timeline (default: first state .. end of video); 0.3 s fade at both ends
   "states": [{"t": 0.5, "kind": "card",    "text": "Hero card"},          # what it looks like from time t on (cross-fade of `morph` s between states)
              {"t": 8.0, "kind": "window",  "text": "app.example.com"},
              {"t": 14.0, "kind": "preview", "text": "Preview"}],
   "keys":   [(0.5, {"cx": .5, "cy": .5, "w": .34}), (8.0, {"cx": .3, "cy": .45, "w": .5, "rot": -3}, "out_cubic")],   # global-time keyframes (see below)
   "morph": 0.45,
   "reel":  {"keys": [...], "states": [...]}}         # optional per-format override; replaces the same field when FMT=reel ("wide" works the same)

Keyframe values: cx, cy = centre as a fraction of the canvas (0..1), w = width as a fraction of canvas width, aspect = height / width (default per kind),
scale, rot, rx, ry (degrees, see transform.py), alpha, z (depth: higher in front). Missing values keep the previous key's value. Third tuple item = easing name.
Kinds: card, window, preview, badge (plain, themed drawings; text is optional).
Caching: each (entity, state, pixel size, theme) surface is drawn once per process and re-posed with a perspective warp per frame, so the cost is one warp per live entity.
Everything is a pure function of the global time t; the surface cache only memoises."""
import motion, transform as X
from PIL import Image, ImageDraw

KINDS = ("card", "window", "preview", "badge")
_ASPECT = {"card": 0.62, "window": 0.62, "preview": 0.5625, "badge": 0.3}
_KEYS = ("cx", "cy", "w", "aspect", "scale", "rot", "rx", "ry", "alpha", "z")
_DEF = dict(cx=0.5, cy=0.5, w=0.3, aspect=None, scale=1.0, rot=0.0, rx=0.0, ry=0.0, alpha=1.0, z=0.0)
FADE = 0.3

def _fmt_over(e, fmt):
    """entity with the per-format override (e["reel"] / e["wide"]) applied"""
    o = e.get(fmt) or {}; r = {k: v for k, v in e.items() if k not in ("wide", "reel")}; r.update(o); return r

def validate(ents_by_scene):
    """list of (scene index, entity dict) -> raises ValueError with a readable message; returns {id: entity}"""
    seen = {}
    for si, e in ents_by_scene:
        if not isinstance(e, dict) or "id" not in e: raise ValueError("scene %d: an entity needs a dict with an \"id\"" % si)
        if e["id"] in seen: raise ValueError("entity %r is defined twice (scene %d and an earlier one): define it once, it persists on global time" % (e["id"], si))
        bad = set(e) - {"id", "t_in", "t_out", "states", "keys", "morph", "wide", "reel"}
        if bad: raise ValueError("entity %r: unknown key(s) %s" % (e["id"], sorted(bad)))
        for fmt in (None, "wide", "reel"):
            v = _fmt_over(e, fmt) if fmt else e
            if fmt and not e.get(fmt): continue
            sts = v.get("states")
            if not sts: raise ValueError("entity %r: \"states\" is empty" % e["id"])
            last = -1e9
            for s in sts:
                if s.get("kind") not in KINDS: raise ValueError("entity %r: unknown kind %r (use %s)" % (e["id"], s.get("kind"), ", ".join(KINDS)))
                if s["t"] < last: raise ValueError("entity %r: state times must be ascending" % e["id"])
                last = s["t"]
            ks = v.get("keys")
            if not ks: raise ValueError("entity %r: \"keys\" is empty" % e["id"])
            last = -1e9
            for kf in ks:
                if kf[0] < last: raise ValueError("entity %r: key times must be ascending" % e["id"])
                last = kf[0]
                bad = set(kf[1]) - set(_KEYS)
                if bad: raise ValueError("entity %r: unknown pose key(s) %s (valid: %s)" % (e["id"], sorted(bad), ", ".join(_KEYS)))
                if len(kf) > 2 and kf[2] not in motion.EASINGS: raise ValueError("entity %r: unknown easing %r" % (e["id"], kf[2]))
        seen[e["id"]] = e
    return seen

def _vals(e, t):
    ks = e["keys"]; cur = dict(_DEF); i0 = None
    # fold keys up to t so a missing value keeps its last given value
    vals = []; run = dict(_DEF)
    for kf in ks: run = dict(run); run.update(kf[1]); vals.append(run)
    if t <= ks[0][0]: return vals[0]
    if t >= ks[-1][0]: return vals[-1]
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]:
            a, b = vals[i], vals[i + 1]; ez = motion.EASINGS[ks[i + 1][2] if len(ks[i + 1]) > 2 else "smooth"]; u = (t - ks[i][0]) / max(1e-9, ks[i + 1][0] - ks[i][0]); u = ez(u)
            out = {}
            for k in _KEYS:
                va, vb = a[k], b[k]; out[k] = va if va is None or vb is None else va + (vb - va) * u
            out["aspect"] = b["aspect"] if a["aspect"] is None else (a["aspect"] if b["aspect"] is None else out["aspect"])
            return out
    return vals[-1]

def alive(e, t, t_end):
    t0 = e.get("t_in", e["states"][0]["t"]); t1 = e.get("t_out", t_end)
    return t0 - 1e-9 <= t <= t1 + 1e-9, t0, t1

def life_alpha(e, t, t_end):
    ok, t0, t1 = alive(e, t, t_end)
    if not ok: return 0.0
    return min(motion.ss(motion.prog(t, t0, t0 + FADE)) if FADE else 1.0, 1 - motion.ss(motion.prog(t, t1 - FADE, t1)) if FADE else 1.0)

def state_mix(e, t):
    """(state a, state b, mix 0..1): crossfade of `morph` seconds starting at each state's t"""
    sts = e["states"]; m = max(0.01, e.get("morph", 0.45)); idx = 0
    for i, s in enumerate(sts):
        if t >= s["t"]: idx = i
    if idx == 0: return sts[0], sts[0], 0.0
    u = motion.ss(motion.prog(t, sts[idx]["t"], sts[idx]["t"] + m)); return sts[idx - 1], sts[idx], u

_cache = {}
def surface(st, w, h, ctx):
    """RGBA drawing of one state; cached per (state, size, theme)"""
    key = (st["kind"], st.get("text", ""), w, h, ctx["key"])
    s = _cache.get(key)
    if s is not None: return s
    S = 2; im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = st["kind"]; OR, card, fg = ctx["accent"], ctx["card"], ctx["fg"]; W2, H2 = w * S, h * S; r = int(min(w, h) * 0.07) * S
    bt = ctx["text"]
    if k == "card":
        d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), r, fill=card + (255,), outline=OR + (255,), width=4 * S)
        d.rounded_rectangle((W2 * .08, H2 * .12, W2 * .22, H2 * .12 + H2 * .09), r // 3, fill=OR + (255,))
        if st.get("text"): bt(d, (W2 / 2, H2 * .55), st["text"], int(h * 0.15) * S, fg + (255,))
    elif k == "window":
        d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), r, fill=card + (255,), outline=OR + (255,), width=3 * S)
        bar = int(H2 * .14); d.rounded_rectangle((0, 0, W2 - 1, bar * 2), r, fill=tuple(max(0, c - 14) for c in card) + (255,)); d.rectangle((3 * S, bar, W2 - 4 * S, bar * 2), fill=card + (255,))
        for j, c in enumerate(((255, 96, 96), (255, 190, 60), (110, 210, 90))): d.ellipse((bar * .5 + j * bar * .8, bar * .35, bar * .5 + j * bar * .8 + bar * .4, bar * .75), fill=c + (255,))
        d.rounded_rectangle((W2 * .3, bar * .22, W2 * .92, bar * .88), bar // 3, fill=tuple(min(255, c + 16) for c in card) + (255,))
        if st.get("text"): bt(d, (W2 * .61, bar * .55), st["text"], int(bar * .42), fg + (200,))
        for j in range(3): d.rounded_rectangle((W2 * .08, H2 * (.3 + j * .17), W2 * (.92 - j * .18), H2 * (.3 + j * .17) + H2 * .07), r // 3, fill=OR + (90 + 40 * j,))
    elif k == "preview":
        d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), r, fill=(18, 18, 22, 255), outline=OR + (255,), width=3 * S)
        cx, cy, rr = W2 / 2, H2 * .46, H2 * .17; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=OR + (255,)); d.polygon([(cx - rr * .3, cy - rr * .5), (cx - rr * .3, cy + rr * .5), (cx + rr * .55, cy)], fill=(14, 14, 12, 255))
        d.rounded_rectangle((W2 * .06, H2 * .86, W2 * .94, H2 * .9), H2 // 40, fill=(70, 72, 80, 255)); d.rounded_rectangle((W2 * .06, H2 * .86, W2 * .5, H2 * .9), H2 // 40, fill=OR + (255,))
        if st.get("text"): bt(d, (W2 / 2, H2 * .12), st["text"], int(h * 0.09) * S, (245, 245, 245, 255))
    else:  # badge
        d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), H2 // 2, fill=OR + (255,))
        if st.get("text"): bt(d, (W2 / 2, H2 / 2), st["text"], int(h * 0.45) * S, (14, 14, 12, 255))
    s = im.resize((w, h), Image.LANCZOS); _cache[key] = s; return s

def draw_all(canvas, t, ents, t_end, fmt, ctx):
    """draw every live entity onto RGBA `canvas` in depth order"""
    W, H = canvas.size; items = []
    for n, e0 in enumerate(ents.values()):
        e = _fmt_over(e0, fmt); la = life_alpha(e, t, t_end)
        if la <= 0.002: continue
        v = _vals(e, t); a, b, mx = state_mix(e, t); w = max(8, int(round(v["w"] * W))); asp = v["aspect"] if v["aspect"] is not None else _ASPECT[b["kind"]]; h = max(8, int(round(w * asp)))
        items.append((v["z"], n, e0["id"], v, la, a, b, mx, w, h))
    for z, n, ident, v, la, a, b, mx, w, h in sorted(items, key=lambda p: (p[0], p[1])):
        sa = surface(a, w, h, ctx)
        if mx > 0 and b is not a:
            sb = surface(b, w, h, ctx); sf = Image.blend(sa, sb, mx) if False else _blend(sa, sb, mx)
        else: sf = sa
        pose = X.Pose(scale=v["scale"], rot=v["rot"], rx=v["rx"], ry=v["ry"], alpha=v["alpha"] * la)
        X.place(canvas, sf, pose, origin=(v["cx"] * W - w / 2, v["cy"] * H - h / 2))
    return canvas

def _blend(a, b, m):
    """cross-fade two RGBA surfaces (premultiplied-safe: fade alphas, then composite)"""
    out = Image.new("RGBA", a.size, (0, 0, 0, 0)); fa = a.copy(); fb = b.copy()
    fa.putalpha(a.getchannel("A").point(lambda v: int(v * (1 - m) + 0.5))); fb.putalpha(b.getchannel("A").point(lambda v: int(v * m + 0.5)))
    out.alpha_composite(fa); out.alpha_composite(fb); return out
