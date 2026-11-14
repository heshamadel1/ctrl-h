# Transforms and camera (engine/transform.py)

**What this is:** a 2D perspective warp (Pillow `Image.PERSPECTIVE`, bicubic, anti-aliased edges). It is *not* real 3D: no lighting, no occlusion between parts of one object, no depth buffer. It looks right for cards, panels and screens that tilt, turn or zoom.

## Pose
`Pose(x, y, scale | sx, sy, rot, rx, ry, alpha, z)`
- `x, y` move in pixels; `scale` (or `sx`/`sy`); `rot` degrees in the picture plane (clockwise).
- `rx` tilts about the horizontal axis (positive: top goes away), `ry` about the vertical axis (positive: right side goes away).
- `alpha` opacity, `z` depth order (higher is in front; equal z keeps list order).
- All rotation/scale happens about the `anchor` (default: object centre; `(0,0)` = top-left).
- An integer pure translation is a plain paste, pixel-identical.

## Functions
- `place(canvas, obj, pose, anchor, origin, focal)` draw one RGBA object. `origin` is the object's top-left.
- `compose(canvas, items)` several objects in depth order; each item may have `shadow=dict(dx, dy, blur, color, opacity)` that follows the pose.
- `lerp_pose(a, b, t)`, `pose_at(t, [(time, pose, easing?), ...])` keyframes (easings from `motion.EASINGS`).

## Camera (scene key `camera`)
Keyframes on **global time** (so one list can run across scenes and stay continuous):
```python
{"camera": [(0, {"zoom": 1.0}), (4, {"zoom": 1.3, "pan": (60, -20)}, "out_cubic"), (6, {"tilt": (0, 8), "focus": 3})]}
```
Properties: `zoom`, `pan` (px), `tilt` (rx, ry degrees), `focus` (blur radius). Unknown keys, unsorted times, unknown easings and empty lists stop `Video()` with a clear message. An all-default camera is an exact no-op. Applied after the beat zoom, before the dimension overlays.

## Limits
Tilt beyond about 60 degrees stretches edges heavily; strong `focus` costs a blur per frame. Cost of a camera frame is one warp of the full layer (~tens of ms).

Example keyframes are above; copy them into any scene. Tests: `python3 tests/transform_test.py` (developer only).
