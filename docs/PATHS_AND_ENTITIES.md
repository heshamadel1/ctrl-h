# Beams, paths and persistent entities (Phase 5)

## 1. Paths and beams (engine/paths.py, block `beam`)
`paths.py` is pure geometry: `line`, `quad`, `cubic` (bezier), `curve(a, b, bend)`, `polyline`, `connect(box_a, box_b, bend)`. Position along a path is measured by **arc length** (`point_at(f)`, `tangent_at(f)`, `angle_at(f)`, `sub(f0,f1)`, `reversed()`), so a beam moves at constant speed even on a curve.
Drawing: `draw_path(layer, path, progress, color, width, alpha, glow, dash, arrow)` (line drawn on), `draw_beam(layer, path, head, tail, color, width, glow, alpha, fwd)` (travelling pulse with glow and a fading tail; `fwd=False` goes end to start).

Block `beam` (see header of `engine/blocks_path.py` and `examples/beam_demo_scenes.py`): `nodes` with normalised positions (same in 16:9 and 9:16) and `paths` with `from/to`, `t`, `dur`, `style` (draw | beam | both), `dir` (fwd | back | both), `pulses`, `loop`, `bend`, `tone`, `label`, `dash`, `arrow`, `ease`.
Use for request flow, service communication, data flow, architecture.

## 2. Persistent entities (engine/entities.py, scene key `entities`)
One logical object that keeps its identity across scenes (card -> browser window -> video preview). Header of `entities.py` has the full spec.

Design decisions
- **Ownership:** an entity belongs to the video timeline, not to a scene. It is defined once (in any scene's `entities` list; a second definition of the same id is an error) and runs on **global time**.
- **Layering/transitions:** drawn above the scene content *after* the scene transition, so slides/fades never drag or cut it. It is below the end-of-video chrome (OV layer).
- **Identity and state:** `id` is the identity; `states` change the drawing (cross-fade of `morph` seconds); `keys` change the pose (position, width, rotation, tilt, alpha, depth) with easings from `motion.py`; lifetime `t_in`/`t_out` with a 0.3 s fade.
- **Format adaptation:** per-format override (`"reel": {...}` / `"wide": {...}`) replaces `keys`/`states` natively, nothing is stretched. Positions are fractions of the canvas.
- **Caching:** each (state, pixel size, theme) surface is drawn once per process and re-posed with a perspective warp per frame; the chunk cache key now includes the entity definitions, so editing an entity re-renders every affected chunk.
- **Purity:** everything is a function of global time; no frame depends on another.
Limits: four built-in kinds (card, window, preview, badge); entities do not yet carry arbitrary blocks inside them.

Tests (developer only): `python3 tests/beam_test.py` (renders real frames, wide and reel, plus lint rules), `python3 tests/paths_test.py`, `python3 tests/entities_test.py`.
