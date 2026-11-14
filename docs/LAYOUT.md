# Multi-format layout check (engine/layout_check.py)

**What:** checks every scene in BOTH formats (wide 1920×1080, reel 1080×1920) for geometry problems, without rendering a video: it uses the real layout boxes plus one sampled frame per scene (taken while the scene is settled, between its entry and exit transitions).

**Why:** a scene that looks fine in wide can be cramped, cropped or squeezed in reel. This finds those scenes so you only look at the frames that matter.

| Rule | Meaning | Level |
|---|---|---|
| safe-area | a block box leaves the safe rectangle (wide: 60 px sides / 40 px bottom; reel: 54 px sides / 180 px bottom for the platform caption and buttons) | WARN (ERROR if outside the frame) |
| overlap | two stacked blocks intersect | ERROR |
| overflow | drawn pixels (text, glow) outside every box + 40 px, or content touching the frame edge (cropped text/entity) | WARN / ERROR |
| squeeze | the scene was scaled down to fit; below 80% text is hard to read | WARN (ERROR below 60%) |
| format-mismatch | fits wide but is squeezed in reel: shorten, split the scene, or use per-format fields (`reserve_reel`, `cw`, per-format entity overrides) | WARN |
| camera | a camera key time pushes content past the frame edge | WARN |
| sparse | the scene fills under 12% of the safe area | WARN |

## Use
```
python3 engine/layout_check.py my_scenes.py                 # both formats (also accepts a storyboard .json)
python3 engine/layout_check.py my_scenes.py --fmt reel --json
python3 engine/layout_check.py my_scenes.py --strict        # warnings also fail
```
Then look at flagged scenes: `python3 engine/render.py my_scenes frames out <seconds>` (run with `FMT=reel` for the reel).

## Standard workflow vs advanced
Standard (chat only): after Claude builds the scenes, the same findings come from `lint` messages and from looking at the preview frames; ask Claude to "check the reel layout". Advanced: run `layout_check.py` in the terminal or from an agent loop and fix until no ERROR remains. Nothing here is required to render.

## Limits
- Finds geometry problems, not taste. A clean result does not mean the scene is good-looking: look at the frames.
- One sampled frame per scene (all blocks visible); problems that exist only mid-animation are not seen, except camera key times.
- ABS overlays (e.g. button) are not part of the box checks; the frame-edge check still covers blocks and entities.
- Font scaling is judged through the engine's own squeeze factor, not by measuring individual text.
- Thresholds are constants at the top of the file (`SAFE`, `MARGIN`, `OVERFLOW_PX`).

## Fixed while building it
The `chain` block's error badge (e.g. "401 Unauthorized") was cut off at the right edge in reel. It now stays inside the block box (shorter dashed line, smaller text if needed); wide frames are byte-identical to before.
