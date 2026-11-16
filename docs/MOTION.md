# Motion system (`engine/motion.py`)

**What:** one place for the time helpers every block uses, plus easing, tween, stagger, sequence, spring and keyframe primitives. Pure functions of `t` (math only), so frames stay a pure function of time: cacheable, deterministic, safe in the multiprocessing pool.

**Why:** `cl/ss/prog/E/lerp/bob` lived in `anim.py` and the back-ease pop only in `blocks_sysdiagram.py`. Now they live in `motion.py` with the formulas unchanged (pixel-identical renders; verified by `tests/motion_test.py` against verbatim copies of the old code and by the golden frames, 230/230 exact).

**Who needs it:** people writing blocks (inside the engine every name is already in scope). Standard users never touch it: scenes are written exactly as before.

## Existing helpers (unchanged)
`cl(x)` clamp 0..1 · `ss(x)` smoothstep · `prog(t,a,b)` progress of t between a and b · `E(t,te,d)` card entrance · `lerp_color` (`lerp` in the engine) · `bob(t,k)` ±2 px float · `back_pop(t,te)` alpha and scale with overshoot (`_sd_pop` in the sysdiagram block).

## New primitives
| Need | Call |
|---|---|
| a value moving between two numbers | `tween(t, t0, t1, a, b, "out_cubic")` |
| a point or colour | `tween_point(t, t0, t1, p0, p1, e)` |
| easing by name | `ease("out_back")`; names: `linear smooth in_quad out_quad in_out_quad in_cubic out_cubic in_out_cubic out_expo in_back out_back in_out_back out_elastic out_bounce` (a function also works) |
| cards appearing one after another | `stagger(i, step=0.12, start=t0, order="forward"|"reverse"|"center", n=n)` |
| several moves in a row | `Sequence([(dur, a, b, ease), ...], t0).value(t)` (a pause is a step with a == b) |
| play backwards / loop | `reverse(f)`, `pingpong(t, period)`, `repeat(t, period)` |
| spring motion | `spring(t, t0, k=18, damping=0.55, a, b)` (closed form: damping < 1 overshoots, 1 critical, > 1 slow) |
| animated property over time | `keyframes(t, [(0, 0), (1, 10, "out_cubic"), (2, 10)])` (numbers or tuples; the easing shapes the segment that ends at that key) |
| loops and pops | `pulse(t, period)`, `hump(p)` |

Easings overshoot (back, elastic, spring) by design; `clamp_ease` keeps endpoints exact.

## Example (inside a block)
```python
x = motion.tween(t, t0, t0 + 0.5, -200, 0, "out_back")          # slide in with overshoot
a = motion.keyframes(t, [(t0, 0), (t0 + .2, 1), (t1 - .3, 1), (t1, 0)])   # fade in, hold, fade out
sc = motion.spring(t, t0, k=22, damping=0.5, a=0.8, b=1.0)      # settle with a bounce
```

## Limits
No block uses the new primitives yet (they are the base for the next phases: transitions, transforms, paths). Standard Claude workflow: nothing changes. Advanced: `python3 tests/motion_test.py` (developer only).


## Paper background motion (3.0.1)

The `paper` background is alive: a diagonal ripple lights the dot grid in the accent colour, soft accent particles drift up, and a slow glow breathes in two corners. Turn it off with `CTRLH_BG_MOTION=off`. The golden frames render with it off (the animation is time-varying and not part of the block baselines).
