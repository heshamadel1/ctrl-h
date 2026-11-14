# Transitions (`engine/transitions.py`)

**What:** how a scene enters and leaves. Nine kinds, direction, duration and easing, set per scene or for the whole video. The default (`classic`) is the original look and is pixel-identical to v2.2.0, so existing scenes and videos do not change.

**Why:** the transition used to be hard-coded (enter direction cycling right / up / left, exit a left motion blur).

**Structure:** configuration (which transition), logic (`progress`: how far it is, from time, duration and easing in `motion.py`), rendering (one small function per kind). Adding a kind = one function and one name in `KINDS`.

## Kinds
| Kind | Look |
|---|---|
| `classic` | the original (per-scene direction cycle, motion blur) |
| `none` | hard cut |
| `fade` | cross-fade |
| `slide` | moves a quarter of the frame while fading |
| `push` | the whole scene moves in/out of the frame |
| `wipe_h` / `wipe_v` | soft-edged reveal / hide, horizontal or vertical |
| `zoom` | grows from 88% (in) / to 112% (out) while fading |
| `blur` | gaussian blur while fading |

`dir`: `left | right | up | down`. For an entering scene it is where the scene comes FROM, for an exiting scene where it goes TOWARD (defaults: in from the right, out to the left). `wipe_h` takes left/right, `wipe_v` takes up/down.

## How to set it
In a scene (Python scene file):
```python
dict(..., transition="fade")                              # both edges
dict(..., trans_in="slide:left", trans_out="zoom")        # only entering / only leaving
dict(..., transition={"kind": "wipe_h", "dir": "right", "dur": 0.5, "ease": "out_cubic"})
```
For the whole video: environment `CTRLH_TRANSITION=fade` (and optional `CTRLH_TRANSITION_DUR=0.5`), or the same keys in `ctrlh.config.json` (`"transition"`, `"transition_dur"`).
Precedence: `trans_in`/`trans_out` > `transition` > global default > `classic`. Durations are 0.05 to 3 s (default 0.34 in, 0.28 out); `ease` is any name from [MOTION.md](MOTION.md). A wrong name stops the build (and `lint.py`) with the list of valid names.

Example: `examples/transitions_demo_scenes.py` (every kind once).

## Limits
Transitions act on the scene layer (content, cards, headline); the background, tabs and logo stay. The first scene has no entering transition and the last has no leaving one. Transition sound effects are chosen from the scene boundaries as before and do not depend on the kind. Standard Claude workflow: tell Claude "use fade transitions" or the kind per scene; nothing else is needed. Advanced: `python3 tests/transitions_test.py` (developer only).
