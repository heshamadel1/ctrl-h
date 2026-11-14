"""Path geometry and beam rendering (Phase 5.1). Pure functions of time/progress: no state, deterministic, Pillow + math only.

  Path            a curve sampled once into a polyline with an arc-length table. Build with line / quad / cubic / curve / polyline.
                  point_at(f) and tangent_at(f) use f in 0..1 measured by ARC LENGTH (constant speed along the path, even on a bezier).
                  sub(f0, f1) = points of a piece, reversed() = same path backwards, length.
  draw_path       a line drawn on up to `progress` (0..1), optional dashes, arrowhead at the head, glow.
  draw_beam       a travelling light pulse: head position, tail length, glow; direction comes from the path (use reversed() or pass fwd=False).
  connect         two boxes -> a Path from the edge of A to the edge of B (straight, or curved with `bend`)."""
import math
from PIL import Image, ImageDraw, ImageFilter

_N = 64   # samples per bezier segment

class Path:
    def __init__(self, pts):
        pts = [(float(x), float(y)) for x, y in pts]
        if len(pts) < 2: raise ValueError("a path needs at least 2 points")
        self.pts = pts; self.cum = [0.0]
        for i in range(1, len(pts)): self.cum.append(self.cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        self.length = self.cum[-1]
    def _locate(self, f):
        f = 0.0 if f < 0 else 1.0 if f > 1 else f
        if self.length == 0: return 0, 0.0
        want = f * self.length; lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= want: lo = mid
            else: hi = mid
        seg = self.cum[hi] - self.cum[lo]; return lo, (0.0 if seg == 0 else (want - self.cum[lo]) / seg)
    def point_at(self, f):
        i, u = self._locate(f); a, b = self.pts[i], self.pts[min(i + 1, len(self.pts) - 1)]
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    def tangent_at(self, f):
        """unit direction (dx, dy) of travel at f"""
        i, _ = self._locate(f); i = min(i, len(self.pts) - 2); a, b = self.pts[i], self.pts[i + 1]; n = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return ((b[0] - a[0]) / n, (b[1] - a[1]) / n)
    def angle_at(self, f): tx, ty = self.tangent_at(f); return math.degrees(math.atan2(ty, tx))
    def sub(self, f0, f1, step=3.0):
        """polyline of the piece between f0 and f1 (f0 <= f1), points about `step` px apart"""
        f0, f1 = max(0.0, min(1.0, f0)), max(0.0, min(1.0, f1))
        if f1 <= f0: return [self.point_at(f0)]
        n = max(2, int((f1 - f0) * self.length / step) + 1)
        return [self.point_at(f0 + (f1 - f0) * j / (n - 1)) for j in range(n)]
    def reversed(self): return Path(self.pts[::-1])

def line(a, b): return Path([a, b])
def quad(a, c, b): return Path([((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1]) for u in (j / _N for j in range(_N + 1))])
def cubic(a, c1, c2, b):
    out = []
    for j in range(_N + 1):
        u = j / _N; v = 1 - u; out.append((v ** 3 * a[0] + 3 * v * v * u * c1[0] + 3 * v * u * u * c2[0] + u ** 3 * b[0], v ** 3 * a[1] + 3 * v * v * u * c1[1] + 3 * v * u * u * c2[1] + u ** 3 * b[1]))
    return Path(out)
def polyline(pts): return Path(pts)
def curve(a, b, bend=0.25):
    """quadratic bezier from a to b that bows sideways by bend x the distance (positive = to the left of the travel direction, negative = right; 0 = straight)"""
    if not bend: return line(a, b)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; dx, dy = b[0] - a[0], b[1] - a[1]
    return quad(a, (mx + dy * bend, my - dx * bend), b)

def connect(ra, rb, bend=0.0, gap=6):
    """Path between two boxes (x0, y0, x1, y1): starts on the edge of A facing B and ends on the edge of B facing A (`gap` px off each edge)"""
    ca = ((ra[0] + ra[2]) / 2, (ra[1] + ra[3]) / 2); cb = ((rb[0] + rb[2]) / 2, (rb[1] + rb[3]) / 2)
    def edge(r, c, tgt):
        dx, dy = tgt[0] - c[0], tgt[1] - c[1]
        if dx == 0 and dy == 0: return c
        hw, hh = (r[2] - r[0]) / 2 + gap, (r[3] - r[1]) / 2 + gap; s = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        return (c[0] + dx * s, c[1] + dy * s)
    return curve(edge(ra, ca, cb), edge(rb, cb, ca), bend)

def _glow_layer(size, draw_fn, glow, color, alpha):
    """RGBA layer with the shape (via draw_fn(ImageDraw, rgba)) plus a blurred halo of radius `glow`"""
    color = tuple(int(round(v)) for v in color[:3]); core = Image.new("RGBA", size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(core), color + (int(255 * alpha),))
    if glow <= 0: return core
    halo = core.filter(ImageFilter.GaussianBlur(glow)); a = halo.getchannel("A").point(lambda v: min(255, int(v * 3.2)))
    halo.putalpha(a); halo.alpha_composite(core); return halo

def _bbox(pts, m):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; return (int(min(xs) - m), int(min(ys) - m), int(max(xs) + m) + 1, int(max(ys) + m) + 1)

def _paste_local(layer, pts, margin, draw_fn, glow, color, alpha):
    x0, y0, x1, y1 = _bbox(pts, margin); x0 = max(x0, -50); y0 = max(y0, -50); x1 = min(x1, layer.width + 50); y1 = min(y1, layer.height + 50)
    if x1 <= x0 or y1 <= y0: return
    sz = (x1 - x0, y1 - y0); ox, oy = x0, y0
    lay = _glow_layer(sz, lambda dr, c: draw_fn(dr, c, ox, oy), glow, color, alpha); layer.alpha_composite(lay, (ox, oy)) if ox >= 0 and oy >= 0 else layer.alpha_composite(lay.crop((max(0, -ox), max(0, -oy), lay.width, lay.height)), (max(0, ox), max(0, oy)))

def _dashes(pts, on, off):
    """split a polyline into dash pieces (on/off lengths in px)"""
    out, cur, acc, drawing = [], [pts[0]], 0.0, True
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]; seg = math.hypot(b[0] - a[0], b[1] - a[1]); pos = 0.0
        while seg - pos > 1e-9:
            lim = (on if drawing else off) - acc; step = min(lim, seg - pos); u = (pos + step) / seg; p = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            if drawing: cur.append(p)
            pos += step; acc += step
            if acc >= (on if drawing else off) - 1e-9:
                acc = 0.0
                if drawing: out.append(cur); cur = []
                else: cur = [p]
                drawing = not drawing
    if drawing and len(cur) > 1: out.append(cur)
    return out

def draw_path(layer, path, progress=1.0, color=(255, 138, 17), width=4, alpha=1.0, glow=0, dash=None, arrow=False):
    """line drawn from the start up to `progress` of its length. dash=(on, off) px. arrow=True puts a head at the current tip."""
    if progress <= 0 or alpha <= 0: return
    pts = path.sub(0.0, min(1.0, progress)); head = path.point_at(min(1.0, progress)); ang = math.radians(path.angle_at(min(1.0, progress)))
    def fn(dr, c, ox, oy):
        P = lambda p: (p[0] - ox, p[1] - oy)
        for piece in (_dashes(pts, *dash) if dash else [pts]):
            if len(piece) > 1: dr.line([P(p) for p in piece], fill=c, width=width, joint="curve")
        if arrow:
            s = max(10, width * 3.2); hx, hy = P(head); l = (hx - math.cos(ang) * s + math.sin(ang) * s * .6, hy - math.sin(ang) * s - math.cos(ang) * s * .6); r = (hx - math.cos(ang) * s - math.sin(ang) * s * .6, hy - math.sin(ang) * s + math.cos(ang) * s * .6)
            dr.polygon([(hx, hy), l, r], fill=c)
    _paste_local(layer, pts, width * 3 + glow * 3 + 14, fn, glow, tuple(color), alpha)

def draw_beam(layer, path, head, tail=0.18, color=(255, 138, 17), width=6, glow=10, alpha=1.0, fwd=True):
    """a pulse: a bright head at `head` (0..1 along the path) with a fading tail `tail` (fraction of the path) behind it. fwd=False travels from the end to the start."""
    if alpha <= 0: return
    p = path if fwd else path.reversed(); head = max(0.0, min(1.0, head)); t0 = max(0.0, head - tail)
    if head <= 0: return
    pts = p.sub(t0, head, 2.0); n = len(pts)
    def fn(dr, c, ox, oy):
        for j in range(1, n):
            u = j / (n - 1); a = (u ** 1.6)   # tail fades in toward the head
            dr.line([(pts[j - 1][0] - ox, pts[j - 1][1] - oy), (pts[j][0] - ox, pts[j][1] - oy)], fill=c[:3] + (int(c[3] * a),), width=max(1, int(width * (0.35 + 0.65 * u))))
        hx, hy = pts[-1][0] - ox, pts[-1][1] - oy; r = width * 0.9; dr.ellipse((hx - r, hy - r, hx + r, hy + r), fill=(255, 255, 255, c[3]))
    _paste_local(layer, pts, width * 3 + glow * 3 + 14, fn, glow, tuple(color), alpha)
