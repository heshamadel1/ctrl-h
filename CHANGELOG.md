# Changelog

## 2.0.0

**Breaking:** only two themes remain, `orange` (main dark) and `paper_orange`. The old colour themes (cyan, blue, violet, pink, red, gold, green, mono and `paper`) were removed; an unknown `theme` falls back to `orange`. Use `accent` / `card_color` / `bg_color` for other colours.

- `lint.py`: warns when `logo_ch.png` is missing (corner logo and end card would show an empty frame). Skill: check the logo before every build.
- Second image background `hud_dark` selectable per render (`CTRLH_BG_STYLE=minimal BGFILE=...`).
- `docs/CATALOG.md`: every card and block with a name and a code, in 8 families (A-H).
- Cards renamed with descriptive names (plain_dark, glass_blur, neon_glow, ... C01-C12); old names still work. `card_style` in the config locks ONE card type for the whole video.
- docs/images reduced from 100 pictures to 8 contact sheets (cards-dark, cards-paper, blocks-sheet-1..3, backgrounds, bg-hud-live, overview). Fix: terminal card readable on the paper theme.
- Only two themes remain: main dark (orange) and `paper_orange`; the skill asks which one before each video. Per-series theme and `bg_style_locked` kept.
- hud_live: recolor to theme accent, chip icons.
- Tools: align, suggest, preview, srt, chapters.txt, JSON scenes, Node helper, smarter lint.
- `hud_live`: animated HUD background (pulses, particles, lighting icons, loading bar), now the default `bg_style`; bottom chips change per scene (`chips` key / auto-detected tools / `TECH`).
- Fix: `profiles/video-types.json` any_of groups (wrong lint warnings); contact sheet now shows all scenes.
- Added `assets/backgrounds/hud_dark.png`, `hud_plate.png`, `examples/uuid_scenes.py`.
- New optional light theme `paper` (cream background, dot grid, ink text, yellow highlighter) with its paper blocks (`quote`, `chatwin`, `minichart`, `skeleton`, `filegrid`, `bigcount`). Enable with `"theme": "paper"`; see `docs/FEATURES.md` section 12.

## 1.0.0

- Flow / system blocks: `titlevs`, `split`, `chain`, `hub`, `pipeline`, `deviceflow`, `codeann`, `flowmini` (16:9 and 9:16, SFX, LINT, docs, demo `examples/v9_flow_scenes.py`).
- First release: engine (12 card styles, 4 shapes, infographic / comparison / interactive / technical blocks), `build.py`, `lint.py`, per-scene render cache, auto split of long videos, formats (16:9 default, 9:16 on request), video types, disabled blocks, design tokens, `plan.py`, `meta.py`, thumbnail and video skills, full documentation with pictures.
