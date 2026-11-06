# Changelog

## 1.0.1

- `hud_live`: animated HUD background (pulses, particles, lighting icons, loading bar), now the default `bg_style`; bottom chips change per scene (`chips` key / auto-detected tools / `TECH`).
- Fix: `profiles/video-types.json` any_of groups (wrong lint warnings); contact sheet now shows all scenes.
- Added `assets/backgrounds/hud_dark.png`, `hud_plate.png`, `examples/uuid_scenes.py`.
- New optional light theme `paper` (cream background, dot grid, ink text, yellow highlighter) with its paper blocks (`quote`, `chatwin`, `minichart`, `skeleton`, `filegrid`, `bigcount`). Enable with `"theme": "paper"`; see `docs/FEATURES.md` section 12.

## 1.0.0

- Flow / system blocks: `titlevs`, `split`, `chain`, `hub`, `pipeline`, `deviceflow`, `codeann`, `flowmini` (16:9 and 9:16, SFX, LINT, docs, demo `examples/v9_flow_scenes.py`).
- First release: engine (12 card styles, 4 shapes, infographic / comparison / interactive / technical blocks), `build.py`, `lint.py`, per-scene render cache, auto split of long videos, formats (16:9 default, 9:16 on request), video types, disabled blocks, design tokens, `plan.py`, `meta.py`, thumbnail and video skills, full documentation with pictures.
