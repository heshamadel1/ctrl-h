# Changelog

## 2.1.0

- Fix: `make_audio_lib.py` crashed on blocks whose `cols` is a number (icards) and gave no typing sound for `codeann` lines with (t, text) tuples; found by the first full v2.1.0 build.
- Variety rules: >= 8 block kinds per video, no kind in consecutive scenes, per-sentence block choice, forced kinds via question 4, new kinds each video; `lint.py` variety warnings.
- **Third theme `soft_cream`** (from the Invitations video): white rounded cards, light shadow, cream background with orange glow, dark H logo, soft Subscribe/Follow buttons and end card, chapter banner and next-scene pill merged into one bottom-right pill. Themes: `orange`, `paper_orange`, `soft_cream` (chosen per video).
- **Sound library:** 34 sounds in `assets/sfx/` named `<category>_<NN>_<name>.mp3`, `manifest.json`, `docs/SOUNDS.md`. New `engine/make_audio_lib.py` (used by `build.py`): automatic placement, 30% under the voice, no repeats, typing bursts as long as the on-screen typing, pins with `SFX = [(t, "name")]`, `SFX_AUTO`, `SFX_GAIN`. `CTRLH_SFX=synth` keeps the old generated sounds.
- **Backgrounds:** 25 choices with one picture (`docs/images/backgrounds.png`); added `cream`; a theme's default background now follows its `bg` (fix); any background works with any theme.
- **Captions (optional):** `engine/captions.py`, Arabic in a rounded box with an orange highlighter on `[[key words]]` and on every English word, PNG overlays (no libass bidi bugs).
- **Docs rebuilt:** README is only the entry point (ad link, features, quick start, links). New `GETTING_STARTED`, `PIPELINE` (one workflow, automated vs manual), `CONFIGURATION` (every key with type, default, priority), `ARCHITECTURE`, `TROUBLESHOOTING`, `CONTRIBUTING`. Card names unified (descriptive names first, legacy aliases listed once in CATALOG).
- `requirements.txt` with pinned versions and a virtual-environment install.
- **Tech backgrounds** `bg_style: tech:<name>` (10 technologies, 16:9) now selectable like any background.
- **Soft chat window:** chatwin and the other paper blocks follow `soft_cream`.
- **`build.py --check-voice`** / `engine/check_voice.py`: WAV length vs `DUR`, `T_END`, `TAG1/TAG2`, gaps between scenes, before any render.
- **`engine/sfx_preview.py`:** voice + SFX as a small mp3, no video render.
- **`engine/asr_captions.py`:** caption cues from the voice and your script text; `captions.py` renders them.
- **`engine/reels.py`:** 30-60 s clips (9:16 or 16:9) cut at scene boundaries with a title each.
- **`engine/smoke.py`:** whole-kit test (compile, lint every example, frames for 3 themes x 2 formats, SFX, links, setup) with exit code for CI.
- `TYPING_SPEED` for the keystroke rhythm; `profiles/ctrlh.config.example.json` (commented config to copy).
- Fixes found by the smoke test: `ctrlh_setup.py` rejected `cream`, `paper`, `hud_live`; removed the stale example `v10_paper_scenes.py` (old block names).
- **Light code/terminal panels** in `paper_orange` and `soft_cream` (ink text on a light card, darker syntax colours). Before, the code card was black with ink-coloured text.
- **Typing sound is as loud as the other sounds** (the library clip was 4-7x quieter and got ducked under the voice): the liveliest stretch is chosen and normalised.
- **Thumbnail design fixed:** `skills/ctrlh-thumbnail-style/thumb_paper.py` (paper_orange), plus `assets/logo_ch_dark.png` (logo without the black box) and `assets/thumb_icons_row.png`.
- Template `examples/template_howto_scenes.py` (58 s 16:9 how-to).
- Skill asks before every video: theme (3), size (16:9 or 9:16), captions, cards, background, sounds, thumbnail.
- README no longer lists owner/platform/content lines (they stay in `SETTINGS.md` and the skill).

## 2.0.0

**Breaking:** only two themes remained, `orange` (main dark) and `paper_orange`. The old colour themes (cyan, blue, violet, pink, red, gold, green, mono and `paper`) were removed; an unknown `theme` falls back to `orange`. Use `accent` / `card_color` / `bg_color` for other colours.

- `lint.py`: warns when `logo_ch.png` is missing (corner logo and end card would show an empty frame). Skill: check the logo before every build.
- Second image background `hud_dark` selectable per render (`CTRLH_BG_STYLE=minimal BGFILE=...`).
- `docs/CATALOG.md`: every card and block with a name and a code, in 8 families (A-H).
- Cards renamed with descriptive names (plain_dark, glass_blur, neon_glow, ... C01-C12); old names still work. `card_style` in the config locks ONE card type for the whole video.
- docs/images reduced from 100 pictures to 8 contact sheets. Fix: terminal card readable on the paper theme.
- Per-series theme and `bg_style_locked` kept.
- hud_live: recolor to theme accent, chip icons.
- Tools: align, suggest, preview, srt, chapters.txt, JSON scenes, Node helper, smarter lint.
- `hud_live`: animated HUD background (pulses, particles, lighting icons, loading bar), default `bg_style`; bottom chips change per scene (`chips` key / auto-detected tools / `TECH`).
- Fix: `profiles/video-types.json` any_of groups (wrong lint warnings); contact sheet shows all scenes.
- Added `assets/backgrounds/hud_dark.png`, `hud_plate.png`, `examples/uuid_scenes.py`.
- Optional light theme `paper` (cream background, dot grid, ink text, yellow highlighter) with paper blocks (`quote`, `chatwin`, `minichart`, `skeleton`, `filegrid`, `bigcount`); later renamed `paper_orange`.

## 1.0.0

- Flow / system blocks: `titlevs`, `split`, `chain`, `hub`, `pipeline`, `deviceflow`, `codeann`, `flowmini` (16:9 and 9:16, SFX, LINT, docs, demo `examples/v9_flow_scenes.py`).
- First release: engine (12 card styles, 4 shapes, infographic / comparison / interactive / technical blocks), `build.py`, `lint.py`, per-scene render cache, auto split of long videos, formats, video types, disabled blocks, design tokens, `plan.py`, `meta.py`, thumbnail and video skills, full documentation with pictures.
