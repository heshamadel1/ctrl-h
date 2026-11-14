"""Object transforms and camera (Phase 4). 2D image warping, NOT a 3D renderer: a flat RGBA layer is scaled, rotated, tilted and projected with a
perspective warp (Pillow `Image.transform(PERSPECTIVE)`), so it stays light, deterministic and pure in time like the rest of the engine.

  Pose            position offset, scale (uniform or per axis), in-plane rotation, tilt rx (around the horizontal axis) and turn ry (around the
                  vertical axis) with perspective depth, alpha, depth z. A default Pose is the identity (pixel-identical to the source).
  place()         draws an object layer on a canvas with a pose around an anchor (default: its centre)
  drop_shadow()   soft shadow built from the object's alpha, transformed with the object
  compose()       several objects, depth-ordered by z (stable), each optionally with a shadow
  pose_at()       keyframed / eased poses over time (uses motion.py)
  Camera          pan, zoom, tilt (rx, ry), focus (blur) applied to a whole scene layer; camera_at() interpolates keyframes; scene key `camera`
Math is plain numpy. Tilt shrinks the far side by f/(f+z) (f = focal length, default 1.4 x the larger canvas side); `depth` is that 2D projection only."""
import math
import numpy as np
from PIL import Image, ImageFilter
import motion


# ------------------------------------------------------------------ pose
class Pose:
    __slots__ = ("x", "y", "sx", "sy", "rot", "rx", "ry", "alpha", "z")
    DEFAULTS = dict(x=0.0, y=0.0, sx=1.0, sy=1.0, rot=0.0, rx=0.0, ry=0.0, alpha=1.0, z=0.0)
    def __init__(self, x=0.0, y=0.0, scale=None, sx=1.0, sy=1.0, rot=0.0, rx=0.0, ry=0.0, alpha=1.0, z=0.0):
        if scale is not None: sx = sy = scale
        self.x, self.y, self.sx, self.sy, self.rot, self.rx, self.ry, self.alpha, self.z = float(x), float(y), float(sx), float(sy), float(rot), float(rx), float(ry), float(alpha), float(z)
    @classmethod
    def of(cls, v):
        if v is None: return cls()
        if isinstance(v, Pose): return v
        if isinstance(v, dict): return cls(**v)
        raise ValueError("pose must be a Pose or a dict, got %r" % (v,))
    def as_dict(self): return {k: getattr(self, k) for k in self.__slots__}
    def __repr__(self): return "Pose(%s)" % ", ".join("%s=%g" % (k, v) for k, v in self.as_dict().items() if v != self.DEFAULTS[k])
    def __eq__(self, o): return isinstance(o, Pose) and self.as_dict() == o.as_dict()
    def is_identity(self): return all(getattr(self, k) == v for k, v in self.DEFAULTS.items() if k not in ("alpha", "z"))


def lerp_pose(a, b, k):
    """linear mix of two poses (k = 0 -> a, 1 -> b); use motion easing on k for eased motion"""
    a, b = Pose.of(a), Pose.of(b); return Pose(**{n: motion.mix(getattr(a, n), getattr(b, n), k) for n in Pose.__slots__})


def pose_at(t, keys, default_ease="smooth"):
    """Pose at time t from [(time, pose[, easing]), ...]; the easing shapes the segment that ENDS at that key. Holds the first/last pose outside."""
    keys = [(k[0], Pose.of(k[1])) + tuple(k[2:3]) for k in keys]
    return Pose(**{n: motion.keyframes(t, [(k[0], getattr(k[1], n)) + tuple(k[2:3]) for k in keys], default_ease) for n in Pose.__slots__})


# ------------------------------------------------------------------ geometry
def _homography(src, dst):
    """3x3 matrix coefficients (a..h) so that dst = ((ax+by+c)/(gx+hy+1), (dx+ey+f)/(gx+hy+1)) maps the 4 src points onto the 4 dst points"""
    A, B = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float))


def quad(w, h, pose, anchor, origin, focal):
    """canvas positions of the object's 4 corners (TL, TR, BR, BL) under `pose` around `anchor` (object pixels); the anchor lands at origin + anchor + (pose.x, pose.y)"""
    ax, ay = anchor; out = []
    cr, sr = math.cos(math.radians(pose.rot)), math.sin(math.radians(pose.rot))
    cy_, sy_ = math.cos(math.radians(pose.ry)), math.sin(math.radians(pose.ry)); cx_, sx_ = math.cos(math.radians(pose.rx)), math.sin(math.radians(pose.rx))
    for cx, cy in ((0, 0), (w, 0), (w, h), (0, h)):
        X, Y = (cx - ax) * pose.sx, (cy - ay) * pose.sy
        X, Y = X * cr - Y * sr, X * sr + Y * cr                    # in-plane rotation (clockwise on screen)
        Z = X * sy_; X = X * cy_                                    # turn around the vertical axis: the right side goes away for ry > 0
        Z, Y = Z * cx_ - Y * sx_, Y * cx_ + Z * sx_                 # tilt around the horizontal axis: the top goes away for rx > 0
        s = focal / max(focal + Z, 0.1 * focal)
        out.append((origin[0] + ax + pose.x + X * s, origin[1] + ay + pose.y + Y * s))
    return out


def place(canvas, obj, pose=None, anchor=None, origin=(0, 0), focal=None, pad=2):
    """draw RGBA `obj` on RGBA `canvas` (in place, returns it). pose None/identity draws it unscaled at origin (pixel-identical to paste)."""
    pose = Pose.of(pose); w, h = obj.size
    if pose.alpha <= 0: return canvas
    anchor = anchor or (w / 2.0, h / 2.0)
    pure_move = pose.sx == 1 and pose.sy == 1 and pose.rot == 0 and pose.rx == 0 and pose.ry == 0 and float(pose.x).is_integer() and float(pose.y).is_integer()
    if pure_move:   # exact integer translation: plain paste (pixel-identical, fast)
        ov = obj; origin = (origin[0] + pose.x, origin[1] + pose.y)
    else:
        f = focal or 1.4 * max(canvas.size)
        padded = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); padded.paste(obj, (pad, pad))   # transparent border => soft, anti-aliased edges
        q = quad(w + 2 * pad, h + 2 * pad, pose, (anchor[0] + pad, anchor[1] + pad), (origin[0] - pad, origin[1] - pad), f)
        coef = _homography(q, [(0, 0), (w + 2 * pad, 0), (w + 2 * pad, h + 2 * pad), (0, h + 2 * pad)])   # canvas -> object (what Pillow wants)
        ov = padded.transform(canvas.size, Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
        if pose.alpha < 1: ov = _mul_alpha(ov, pose.alpha)
        canvas.alpha_composite(ov); return canvas
    if pose.alpha < 1: ov = _mul_alpha(ov, pose.alpha)
    canvas.alpha_composite(ov, (int(origin[0]), int(origin[1]))); return canvas


def _mul_alpha(img, f):
    out = img.copy(); out.putalpha(img.getchannel("A").point(lambda v, f=f: int(v * f + 0.5))); return out


def drop_shadow(obj, dx=0, dy=14, blur=18, color=(0, 0, 0), opacity=0.45, pad=None):
    """(shadow layer, (offset_x, offset_y)): a blurred silhouette of `obj` in `color`. The layer is larger than obj by `pad` on every side; draw it at origin - pad + (dx, dy)."""
    pad = pad if pad is not None else int(blur * 2 + 2); w, h = obj.size
    a = Image.new("L", (w + 2 * pad, h + 2 * pad), 0); a.paste(obj.getchannel("A"), (pad, pad))
    if blur > 0: a = a.filter(ImageFilter.GaussianBlur(blur))
    a = a.point(lambda v, o=opacity: int(v * o + 0.5)); sh = Image.new("RGBA", a.size, tuple(color) + (0,)); sh.putalpha(a)
    return sh, (dx - pad, dy - pad)


def compose(canvas, items, focal=None):
    """draw several objects in depth order. items: dicts {obj, pose, anchor?, origin?, shadow?: dict(dx, dy, blur, color, opacity)}; lower pose.z first,
    equal z keep list order (stable), so later items are in front. The shadow follows the object's pose (same anchor, shifted)."""
    for it in sorted(enumerate(items), key=lambda p: (Pose.of(p[1].get("pose")).z, p[0])):
        it = it[1]; pose = Pose.of(it.get("pose")); origin = it.get("origin", (0, 0)); anchor = it.get("anchor") or (it["obj"].width / 2.0, it["obj"].height / 2.0)
        sh = it.get("shadow")
        if sh and pose.alpha > 0:
            layer, (ox, oy) = drop_shadow(it["obj"], **sh); pad = sh.get("pad") if sh.get("pad") is not None else int(sh.get("blur", 18) * 2 + 2)
            place(canvas, layer, pose, (anchor[0] + pad, anchor[1] + pad), (origin[0] + ox, origin[1] + oy), focal)   # same pose and anchor: the shadow moves with the object
        place(canvas, it["obj"], pose, anchor, origin, focal)
    return canvas


# ------------------------------------------------------------------ camera
CAM_DEFAULTS = dict(zoom=1.0, pan_x=0.0, pan_y=0.0, tilt_x=0.0, tilt_y=0.0, focus=0.0)


def camera_at(t, keys):
    """camera values at time t from [(time, {zoom, pan:(x,y), tilt:(rx,ry), focus}[, easing]), ...] in GLOBAL video time (the same list on several scenes gives one
    continuous move across them). Missing properties keep their default (zoom 1, no pan/tilt/blur); before the first key the first key holds."""
    keys = [(k[0], _norm_cam(k[1])) + tuple(k[2:3]) for k in keys]
    return {n: motion.keyframes(t, [(k[0], k[1][n]) + tuple(k[2:3]) for k in keys]) for n in CAM_DEFAULTS}


def _norm_cam(d):
    bad = set(d) - {"zoom", "pan", "tilt", "focus"}
    if bad: raise ValueError("camera: unknown keys %s (allowed: zoom, pan, tilt, focus)" % sorted(bad))
    c = dict(CAM_DEFAULTS); c["zoom"] = float(d.get("zoom", 1.0)); c["focus"] = float(d.get("focus", 0.0))
    px, py = d.get("pan", (0, 0)); tx, ty = d.get("tilt", (0, 0)); c["pan_x"], c["pan_y"], c["tilt_x"], c["tilt_y"] = float(px), float(py), float(tx), float(ty)
    return c


def validate_camera(keys):
    """raise ValueError for a malformed scene `camera` list (called when the Video is built)"""
    if not isinstance(keys, (list, tuple)) or not keys: raise ValueError("camera must be a non-empty list of (time, {zoom, pan, tilt, focus}[, easing]) keys")
    last = None
    for k in keys:
        if len(k) < 2 or not isinstance(k[1], dict): raise ValueError("camera key must be (time, dict[, easing]), got %r" % (k,))
        _norm_cam(k[1])
        if len(k) > 2 and k[2] is not None: motion.ease(k[2])
        if last is not None and k[0] < last: raise ValueError("camera keys must be sorted by time")
        last = k[0]


def apply_camera(layer, cam, anchor=None):
    """camera values (from camera_at) applied to a whole RGBA scene layer; anchor = zoom/tilt centre (default: layer centre). Identity values return the layer itself."""
    if cam["zoom"] == 1.0 and cam["pan_x"] == 0 and cam["pan_y"] == 0 and cam["tilt_x"] == 0 and cam["tilt_y"] == 0 and cam["focus"] <= 0.05: return layer
    w, h = layer.size; out = layer
    if not (cam["zoom"] == 1.0 and cam["pan_x"] == 0 and cam["pan_y"] == 0 and cam["tilt_x"] == 0 and cam["tilt_y"] == 0):
        out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        place(out, layer, Pose(x=cam["pan_x"], y=cam["pan_y"], scale=cam["zoom"], rx=cam["tilt_x"], ry=cam["tilt_y"]), anchor or (w / 2.0, h / 2.0), (0, 0), pad=2)
    if cam["focus"] > 0.05: out = _blur_premult(out, cam["focus"])
    return out


def _blur_premult(layer, r):
    a = np.asarray(layer).astype(np.float32); pm = a.copy(); pm[..., :3] *= a[..., 3:4] / 255.0
    ch = [np.asarray(Image.fromarray(np.clip(pm[..., i], 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))).astype(np.float32) for i in range(4)]
    al = ch[3]; rgb = np.stack(ch[:3], axis=2) / np.maximum(al[..., None] / 255.0, 1e-3)
    return Image.fromarray(np.concatenate([np.clip(rgb, 0, 255), np.clip(al[..., None], 0, 255)], axis=2).astype(np.uint8), "RGBA")
