"""Configurable scene transitions (Phase 3). Three separate parts:
  CONFIGURATION  parse_spec / resolve: which transition a scene uses (scene keys, global default, built-in default)
  LOGIC          progress(): how far a transition is (0 = scene settled, 1 = fully gone), from time, duration and easing (motion.py)
  RENDERING      apply(layer, kind, p, direction, entering): transforms the RGBA scene layer; one small function per kind
The default kind "classic" is the original behaviour of the kit (enter direction cycles right / up / left per scene, exit is a left motion blur):
it is pixel-identical to v2.2.0. Nothing else changes unless a scene or CTRLH_TRANSITION asks for it.

Scene keys (all optional):  transition="fade" | "slide:left" | {"kind": "wipe_h", "dir": "right", "dur": 0.5, "ease": "out_cubic"}
  trans_in / trans_out      the same, only for how the scene ENTERS (not the first scene) / EXITS (not the last scene)
Global default: environment CTRLH_TRANSITION (config key "transition"), optional CTRLH_TRANSITION_DUR (config key "transition_dur").
Precedence: trans_in / trans_out > transition > global default > classic."""
import os
import numpy as np
from PIL import Image, ImageFilter
import motion

KINDS = ("classic", "none", "fade", "slide", "push", "wipe_h", "wipe_v", "zoom", "blur")
DIRS = ("left", "right", "up", "down")
IN_DUR, OUT_DUR = 0.34, 0.28          # the original timings; other kinds use them unless dur is given
_ENT = ("right", "up", "left")        # classic: where scene k comes from (k % 3)
_DEFAULT_DIR = {"in": "right", "out": "left"}


# ------------------------------------------------------------------ configuration
class Spec:
    __slots__ = ("kind", "dir", "dur", "ease")
    def __init__(self, kind="classic", dir=None, dur=None, ease=None): self.kind, self.dir, self.dur, self.ease = kind, dir, dur, ease
    def __repr__(self): return "Spec(%s, dir=%s, dur=%s, ease=%s)" % (self.kind, self.dir, self.dur, self.ease)
    def __eq__(self, o): return isinstance(o, Spec) and (self.kind, self.dir, self.dur, self.ease) == (o.kind, o.dir, o.dur, o.ease)


def parse_spec(v, where="transition"):
    """str "kind" or "kind:dir" or dict {kind, dir, dur, ease} (or a Spec) -> Spec; unknown names raise ValueError with the valid ones"""
    if v is None: return None
    if isinstance(v, Spec): return v
    d = {}
    if isinstance(v, str):
        kind, _, dr = v.partition(":"); d = {"kind": kind.strip().lower()}
        if dr: d["dir"] = dr.strip().lower()
    elif isinstance(v, dict): d = dict(v); d["kind"] = str(d.get("kind", "classic")).lower()
    else: raise ValueError("%s must be a name or a dict, got %r" % (where, v))
    unknown = set(d) - {"kind", "dir", "dur", "ease"}
    if unknown: raise ValueError("%s: unknown keys %s (allowed: kind, dir, dur, ease)" % (where, sorted(unknown)))
    if d["kind"] not in KINDS: raise ValueError("%s: unknown transition %r; choose from %s" % (where, d["kind"], ", ".join(KINDS)))
    if d.get("dir") is not None and str(d["dir"]).lower() not in DIRS: raise ValueError("%s: unknown direction %r; choose from %s" % (where, d["dir"], ", ".join(DIRS)))
    if d.get("dur") is not None and not (0.05 <= float(d["dur"]) <= 3.0): raise ValueError("%s: dur must be between 0.05 and 3 seconds, got %r" % (where, d["dur"]))
    if d.get("ease") is not None and not callable(d["ease"]): motion.ease(d["ease"])   # raises with the valid names
    return Spec(d["kind"], str(d["dir"]).lower() if d.get("dir") else None, float(d["dur"]) if d.get("dur") is not None else None, d.get("ease"))


def global_default():
    """the project-wide default from CTRLH_TRANSITION / CTRLH_TRANSITION_DUR (read when called, so tests can change the environment)"""
    sp = parse_spec(os.environ.get("CTRLH_TRANSITION") or None, "CTRLH_TRANSITION") or Spec("classic")
    dur = os.environ.get("CTRLH_TRANSITION_DUR")
    if dur and sp.dur is None: sp = parse_spec({"kind": sp.kind, "dir": sp.dir, "dur": float(dur), "ease": sp.ease}, "CTRLH_TRANSITION_DUR")
    return sp


def resolve(scene, entering, default=None):
    """Spec for how `scene` enters (entering=True) or exits"""
    sp = parse_spec(scene.get("trans_in" if entering else "trans_out"), "trans_in" if entering else "trans_out")
    if sp is None: sp = parse_spec(scene.get("transition"), "transition")
    return sp or default or global_default()


# ------------------------------------------------------------------ logic
def progress(t, edge, entering, spec):
    """0 = settled, 1 = gone. Entering: counts down from 1 at the scene start `edge` to 0 after dur; exiting: counts up to 1 at the scene end `edge`."""
    dur = spec.dur if spec.dur is not None else (IN_DUR if entering else OUT_DUR)
    if entering: x = motion.prog(t, edge, edge + dur); return 1 - (motion.ss(x) if spec.ease is None else motion.clamp_ease(spec.ease, x))
    x = motion.prog(t, edge - dur, edge); return motion.ss(x) if spec.ease is None else motion.clamp_ease(spec.ease, x)


# ------------------------------------------------------------------ rendering
def shift_x(arr, off):
    W = arr.shape[1]; out = np.zeros_like(arr)
    if off == 0: return arr
    if off > 0: out[:, off:] = arr[:, :W - off]
    else: out[:, :W + off] = arr[:, -off:]
    return out


def mblur(layer, length, shift, alpha):
    """horizontal motion blur (accumulates shifted copies), alpha-weighted so transparent areas do not darken (moved unchanged from anim.py)"""
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


def _fa(p, entering, floor=0.8):
    """alpha factor: an entering scene keeps 20% opacity at p=1 (same as the classic look), an exiting scene reaches 0 so nothing pops at the cut"""
    return 1 - (floor if entering else 1.0) * p


def _scale_alpha(layer, f):
    a = layer.getchannel("A").point(lambda v, f=f: int(v * f)); out = layer.copy(); out.putalpha(a); return out


def _offset(layer, dx, dy):
    return layer.transform(layer.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR)


def _vec(direction):
    return {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}[direction]


def _classic(layer, p, entering, k):
    W, H = layer.size
    if entering:
        ent = _ENT[k % 3]
        if ent == "up": return _scale_alpha(layer.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -int(H * 0.12 * p)), Image.BILINEAR), 1 - 0.8 * p)
        return mblur(layer, 150 * p, int(W * 0.18 * p * (1 if ent == "right" else -1)), 1 - 0.8 * p)
    return mblur(layer, 220 * p, int(-W * 0.22 * p), 1 - p)


def _fade(layer, p): return _scale_alpha(layer, 1 - p)


def _slide(layer, p, direction, entering, push):
    """slide: moves a quarter of the frame while fading; push: moves the whole frame, no fade. Entering comes FROM direction, exiting goes TOWARD it."""
    W, H = layer.size; vx, vy = _vec(direction); dist = 1.0 if push else 0.25
    dx, dy = int(vx * W * dist * p), int(vy * H * dist * p)
    out = _offset(layer, dx, dy)
    return out if push else _scale_alpha(out, _fa(p, entering))


def _wipe(layer, p, direction, entering, horizontal):
    """a soft-edged mask that reveals (entering) or hides (exiting) the scene from/toward a side; horizontal selects left/right wipes, vertical up/down"""
    W, H = layer.size
    if horizontal and direction not in ("left", "right"): direction = _DEFAULT_DIR["in" if entering else "out"]
    if not horizontal and direction not in ("up", "down"): direction = "up" if not entering else "down"
    anchored = direction if entering else {"left": "right", "right": "left", "up": "down", "down": "up"}[direction]   # the side where the visible part stays
    n = W if horizontal else H; feather = max(8.0, n * 0.04); pos = np.arange(n, dtype=np.float32)
    edge = (1 - p) * n if anchored in ("left", "up") else p * n               # edge of the visible region
    vis = np.clip(((edge - pos) if anchored in ("left", "up") else (pos - edge)) / feather + 0.5, 0, 1)
    if p <= 0: vis[:] = 1
    if p >= 1: vis[:] = 0
    mask = vis[None, :] if horizontal else vis[:, None]
    a = np.asarray(layer.getchannel("A")).astype(np.float32) * mask
    out = layer.copy(); out.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L")); return out


def _zoom(layer, p, entering):
    """enter: grows from 88% to 100% while fading in; exit: grows from 100% to 112% while fading out (anchored on the frame centre)"""
    W, H = layer.size; s = (1 - 0.12 * p) if entering else (1 + 0.12 * p)
    out = layer.transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 - W / (2 * s), 0, 1 / s, H / 2 - H / (2 * s)), Image.BICUBIC)
    return _scale_alpha(out, _fa(p, entering, 0.85))


def _blur(layer, p, entering):
    """gaussian blur on premultiplied colour (no dark fringes) while fading"""
    r = 26 * p
    if r < 0.3: return layer
    a = np.asarray(layer).astype(np.float32); pm = a.copy(); pm[..., :3] *= a[..., 3:4] / 255.0
    ch = [np.asarray(Image.fromarray(np.clip(pm[..., i], 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))).astype(np.float32) for i in range(4)]
    al = ch[3]; rgb = np.stack(ch[:3], axis=2) / np.maximum(al[..., None] / 255.0, 1e-3)
    out = np.concatenate([np.clip(rgb, 0, 255), np.clip(al[..., None] * _fa(p, entering), 0, 255)], axis=2).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def apply(layer, spec, p, entering, k=0):
    """transform the RGBA scene layer for transition progress p (0 = settled, 1 = gone). `k` = scene index (only classic uses it).
    Returns the layer unchanged when p is ~0 or the kind is none."""
    if p <= 0.003 or spec.kind == "none": return layer
    p = min(p, 1.0)
    direction = spec.dir or _DEFAULT_DIR["in" if entering else "out"]
    kind = spec.kind
    if kind == "classic": return _classic(layer, p, entering, k)
    if kind == "fade": return _fade(layer, p)
    if kind == "slide": return _slide(layer, p, direction, entering, False)
    if kind == "push": return _slide(layer, p, direction, entering, True)
    if kind == "wipe_h": return _wipe(layer, p, direction, entering, True)
    if kind == "wipe_v": return _wipe(layer, p, direction, entering, False)
    if kind == "zoom": return _zoom(layer, p, entering)
    if kind == "blur": return _blur(layer, p, entering)
    raise ValueError("unknown transition %r" % kind)


def apply_scene(layer, t, scenes, k, default=None):
    """what anim.py calls: transitions in (scene start, not the first scene) and out (scene end, not the last), in-transition has priority like before"""
    s = scenes[k]
    if k > 0:
        sp = resolve(s, True, default); p = progress(t, s["t0"], True, sp)
        if p > 0.003: return apply(layer, sp, p, True, k)
    if k < len(scenes) - 1:
        sp = resolve(s, False, default); p = progress(t, s["t1"], False, sp)
        if p > 0.003: return apply(layer, sp, p, False, k)
    return layer
