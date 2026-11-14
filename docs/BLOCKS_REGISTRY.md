# Blocks registry and technical debt (Phase 9)

## How blocks are registered today
`anim.py` defines the base kinds in `DRAW` (and overlays in `ABS`, layout heights in `EXTRA_H`); then loads, in this order, `blocks_flow.py`, `blocks_paper.py`, `blocks_hud.py`, `blocks_sysdiagram.py`, `blocks_path.py`, `blocks_timeline.py` into the same namespace (list: `BLOCK_FILES`). Each file registers its kinds. `BLOCK_SOURCE` now records which file registered each kind. `python3 engine/blocks_info.py` prints the table (kind, file, overlay, own layout, documented, examples); `--check` fails on an undocumented kind; `python3 engine/blocks_info.py <kind>` shows its docs lines.

## Evaluation of a fuller registry (not done, on purpose)
A registry object (name, schema, docs, tests per kind) would give one place for validation and docs. What it would cost: the blocks files share helpers through one namespace, `lint.py` hard-codes some per-kind rules, and 50 kinds would have to be migrated without changing a pixel. **Compatibility plan if you want it later:** (1) keep `DRAW`/`ABS`/`EXTRA_H` as they are and build the registry on top (done: `BLOCK_SOURCE`, `blocks_info.py`); (2) add an optional `SCHEMA[kind]` dict next to each draw function and let `lint.py` read it, kind by kind, each step guarded by the golden suite and `tests/block_coverage_test.py`; (3) only then move docs generation onto it. Nothing in the standard workflow depends on this.

## Technical debt: findings and status
| Item | Finding | Status |
|---|---|---|
| `blocks_paper.py` executed twice | The second run was a pure repeat: no other file redefines its names, and no kind it registers is registered by another file (checked by recording every write to `DRAW`/`ABS`/`EXTRA_H` across the load order). | Removed; golden 230/230 exact |
| Dead "next scene" preview (`if False and ...`) | Disabled long ago, replaced by the chapter banner | Removed; golden exact |
| Two `X if False else Y` expressions | Dead branch of an old text call | Reduced to the live branch; golden exact |
| Hard-coded transition sequences | The classic enter direction cycle and pin/pout times were inline | Moved to `transitions.py` in Phase 3 (kept as the `classic` default so existing videos do not change) |
| Hard-coded sound rotation | pop/click rotation and event lists were inside `make_audio_lib.py` | Moved to `audio_events.py` in Phase 7; output byte-identical |
| Version metadata | `VERSION` 2.2.0; README, CHANGELOG, skill agree; `RELEASE_NOTES.md` title still says v2.1.0; `RELEASE_STEPS.md` and `requirements.txt` had a hard-coded v2.1.0 | `RELEASE_STEPS.md` now reads `VERSION`, `requirements.txt` header fixed, `tests/version_check.py` lists mismatches. **`RELEASE_NOTES.md` is yours to edit** (still reported as a mismatch) |
| Whisper alignment untested | Only the silence method had been exercised. Also: any model error (offline, download blocked) crashed instead of falling back; language was fixed to Arabic | Fallback to silence on any error, `CTRLH_WHISPER_LANG`, `tests/align_test.py` (silence method on a synthetic voice, mapping and fallbacks with a stand-in model). **A real Whisper model has not been run**; and lines are placed by their share of the spoken words, not by matching the text |
| Unhelpful font error | A missing font gave Pillow's "cannot open resource" | Clear message naming the file and the `CTRLH_FONT_*` variables |
| Missing visual tests | The golden suite covers 9 of 50 block kinds (pixel-exact) | `tests/block_coverage_test.py`: all 50 kinds, wide + reel, dark + light theme: renders, deterministic, visible content (no baselines needed). Pixel-exact golden cases for more kinds need your approval of new baselines; see the final report |

## Not changed
- Overlays in `ABS` (hud and similar) are not part of the coverage test.
- `lint.py` still holds per-kind rules in code.
