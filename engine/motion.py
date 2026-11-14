"""Shared motion system (Phase 2). Pure functions of time, no state, no dependencies (math only): every frame stays a pure function of t.

PART 1, extracted unchanged from anim.py / blocks_sysdiagram.py (same formulas, same operation order, so every existing render is pixel-identical):
  cl, ss (smoothstep), prog, E (card entrance), lerp_color, bob, back_pop (was _sd_pop)
PART 2, new primitives built on them: named easings, tween, stagger, delay/sequence, reverse/pingpong/repeat, spring, keyframes, pulse/hump.

Conventions: `t` is seconds on the video timeline; a "progress" is a float 0..1; an easing maps 0..1 -> 0..1 (back/elastic/spring may overshoot)."""
import math

# ------------------------------------------------------------------ part 1: extracted behaviour (do not change the formulas)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def prog(t, a, b): return cl((t - a) / (b - a))
def E(t, te, d=0.4): return ss(prog(t, te - 0.12, te - 0.12 + min(d, 0.3)))
def lerp_color(c0, c1, k): return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(3))
def bob(t, k): return 2.0 * math.sin(2 * math.pi * t / 3.6 + k)


def back_pop(t, te, dur=0.32):
    """(alpha, scale) of an item that pops in at te with a back-ease overshoot (the sysdiagram pop)"""
    q = prog(t, te - 0.05, te - 0.05 + dur)
    if q <= 0: return 0.0, 0.0
    c1 = 1.70158; s = 1 + (c1 + 1) * (q - 1) ** 3 + c1 * (q - 1) ** 2
    return ss(min(1.0, q * 2.2)), max(0.05, s)


# ------------------------------------------------------------------ part 2: easings
def _in_out(f): return lambda x: 0.5 * f(2 * x) if x < 0.5 else 1 - 0.5 * f(2 * (1 - x))   # symmetric in-out from an "in" curve
def _back_in(x, c1=1.70158): return (c1 + 1) * x ** 3 - c1 * x ** 2
def _out_back(x, c1=1.70158): return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2   # the curve used by back_pop
def _out_elastic(x):
    if x <= 0 or x >= 1: return cl(x)
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1
def _out_bounce(x):
    n, d = 7.5625, 2.75
    if x < 1 / d: return n * x * x
    if x < 2 / d: x -= 1.5 / d; return n * x * x + 0.75
    if x < 2.5 / d: x -= 2.25 / d; return n * x * x + 0.9375
    x -= 2.625 / d; return n * x * x + 0.984375

EASINGS = {
    "linear": lambda x: x,
    "smooth": ss,                                   # the kit's default (smoothstep)
    "in_quad": lambda x: x * x, "out_quad": lambda x: 1 - (1 - x) ** 2, "in_out_quad": _in_out(lambda x: x * x),
    "in_cubic": lambda x: x ** 3, "out_cubic": lambda x: 1 - (1 - x) ** 3, "in_out_cubic": _in_out(lambda x: x ** 3),
    "out_expo": lambda x: 1.0 if x >= 1 else 1 - 2 ** (-10 * x),
    "in_back": _back_in, "out_back": _out_back, "in_out_back": _in_out(_back_in),
    "out_elastic": _out_elastic, "out_bounce": _out_bounce,
}


def ease(e):
    """an easing from a name ("out_cubic"), a function, or None (-> smooth)"""
    if e is None: return EASINGS["smooth"]
    if callable(e): return e
    try: return EASINGS[e]
    except KeyError: raise ValueError("unknown easing %r; choose from %s" % (e, ", ".join(sorted(EASINGS))))


def clamp_ease(e, x):
    """easing applied to a clamped progress; endpoints are exact (0 -> 0, 1 -> 1) even for overshooting curves"""
    x = cl(x)
    return 0.0 if x <= 0 else 1.0 if x >= 1 else ease(e)(x)


# ------------------------------------------------------------------ tween, interpolation, stagger, timing
def mix(a, b, k): return a + (b - a) * k


def tween(t, t0, t1, a=0.0, b=1.0, e="smooth"):
    """value moving from a to b between t0 and t1 with easing e (clamped outside the window)"""
    return mix(a, b, clamp_ease(e, prog(t, t0, t1)))


def tween_point(t, t0, t1, p0, p1, e="smooth"):
    k = clamp_ease(e, prog(t, t0, t1)); return tuple(mix(p0[i], p1[i], k) for i in range(len(p0)))


def stagger(i, step=0.12, start=0.0, order="forward", n=None):
    """start time of item i in a staggered group (order: forward | reverse | center; reverse/center need n)"""
    if order == "reverse": i = (n - 1 - i) if n else i
    elif order == "center" and n: i = abs(i - (n - 1) / 2) * 2
    return start + i * step


def delay(t, d): return t - d


def reverse(f):
    """f(p) played backwards"""
    return lambda p: f(1.0 - p)


def pingpong(t, period):
    """0 -> 1 -> 0 triangle of t with the given full period"""
    x = (t / period) % 1.0; return 1 - abs(2 * x - 1)


def repeat(t, period, t0=0.0):
    """position inside a looping window: returns progress 0..1 that restarts every `period` seconds"""
    return ((t - t0) / period) % 1.0


def pulse(t, period, phase=0.0): return 0.5 + 0.5 * math.sin(2 * math.pi * t / period + phase)
def hump(p): return math.sin(math.pi * cl(p))     # 0 -> 1 -> 0 over a progress (the "pop" used by buttons and chips)


class Sequence:
    """chain of tweens on one timeline: Sequence([(dur, a, b, ease), ...], t0=...).value(t); an optional gap is a tween with a == b.
    The value holds the last b after the end and the first a before the start."""
    def __init__(self, steps, t0=0.0):
        self.t0 = t0; self.steps = []; at = t0
        for st in steps:
            dur, a, b = st[0], st[1], st[2]; e = st[3] if len(st) > 3 else "smooth"
            self.steps.append((at, at + dur, a, b, e)); at += dur
        self.t1 = at
    def value(self, t):
        if not self.steps: return 0.0
        if t <= self.steps[0][0]: return self.steps[0][2]
        for s0, s1, a, b, e in self.steps:
            if t < s1: return tween(t, s0, s1, a, b, e)
        return self.steps[-1][3]


def spring(t, t0, k=18.0, damping=0.55, a=0.0, b=1.0):
    """closed-form damped spring from a to b starting at t0 (no integration, so it stays a pure function of t).
    k = stiffness (angular frequency, rad/s), damping = damping ratio: <1 overshoots and settles, 1 = critical, >1 = overdamped."""
    x = t - t0
    if x <= 0: return a
    z = damping; w = k
    if z < 1.0:
        wd = w * math.sqrt(1 - z * z); v = 1 - math.exp(-z * w * x) * (math.cos(wd * x) + (z * w / wd) * math.sin(wd * x))
    elif z == 1.0: v = 1 - math.exp(-w * x) * (1 + w * x)
    else:
        s = math.sqrt(z * z - 1); r1 = -w * (z - s); r2 = -w * (z + s); v = 1 - (r2 * math.exp(r1 * x) - r1 * math.exp(r2 * x)) / (r2 - r1)
    return mix(a, b, v)


def keyframes(t, frames, default_ease="smooth"):
    """evaluate [(time, value[, easing]), ...] (sorted by time). The easing of a keyframe shapes the segment that ENDS at it.
    Values may be numbers or equal-length tuples; before the first key the first value holds, after the last key the last value holds."""
    if not frames: raise ValueError("keyframes needs at least one key")
    if t <= frames[0][0]: return frames[0][1]
    for (t0, v0, *_), (t1, v1, *rest) in zip(frames, frames[1:]):
        if t < t1:
            e = rest[0] if rest and rest[0] is not None else default_ease
            k = clamp_ease(e, prog(t, t0, t1))
            return tuple(mix(v0[i], v1[i], k) for i in range(len(v0))) if isinstance(v0, (tuple, list)) else mix(v0, v1, k)
    return frames[-1][1]
