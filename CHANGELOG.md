# Changelog

## 3.0.3

- **Terminal panels are black in every theme (config key `terminal`, default `"dark"`):** `code`, `diff`, `versus` code panels, `http`, `zoom`, `ba`, `predict`, `codeann` and `steplist` now keep a black panel with light text on `paper_orange` and `soft_cream` too. `"terminal": "light"` (or `CTRLH_TERMINAL=light`) brings back light panels, now readable: darker syntax colours, darker red/green in `diff`, a light panel behind the `versus` code, darker amber/cyan in `http`. Colours given in a scene file as the darker shades (for example `DRED`/`DGRN` = (190,30,40)/(18,120,58)) are turned into the light red/green on a dark terminal. Dark themes are unchanged. Videos already published are not touched; rebuild one to get the new look.
- **Fix:** the red/green rows of `diff` were see-through on light backgrounds (the row replaced the panel pixels); they are now blended with the panel.

## 3.0.2

- **Faster render (about 25% less time on a 12 s reel clip):** the camera zoom now samples with bilinear instead of bicubic (2.6x faster per frame, differences below 1/255 on average and invisible at 3x magnification; `CTRLH_ZOOM_FILTER=bicubic` brings the old look back), and the encoder preset is `veryfast` instead of `medium` (2.5x faster, SSIM 0.9966 vs 0.9975 at the same crf 17, file not larger; `CTRLH_X264_PRESET=medium` to override).
- **`paper_orange` is the default theme** of the engine (`themes.DEFAULT`), the setup wizard, captions and the storyboard template; `CTRLH_THEME` / config `theme` still choose any theme. The owner profile `profiles/ctrlh.config.json` uses it too.
- **Sound by meaning (automatic):** a card or list item whose text says something wrong (غلط، خطأ، bug, error ...) plays an error sound, one that says it works (نجح، الحل، secure, fixed ...) a success sound, a warning a glitch, and a question a quiet riser just before it appears. Explicit `ok` keeps its sound. New event kind `meaning`; `SFX_EVENTS = {"meaning": False}` turns it off (docs/SOUNDS.md).
- **Text auto-fit:** one-line text in `chip`, `note`, `title` (and its `sub`), `shock` and `mystery` shrinks (never below 20 px) when it would run out of its block, like cards already did. Text that fits is unchanged. New test `tests/fit_test.py`.
- **`make_video.py`:** one command from `voice.wav` + `script.txt` to a draft scene file (timing by `align.py --asr` when a model folder is given, else silence timing; then `suggest.py` and lint); `--build` also renders. Never overwrites an existing scene file without `--force`.
- **Golden tests:** new cases `G11_beam` (beam nodes, pulses) and `G12_tracks` (timeline) in orange and paper_orange, wide and reel (40 frames, 282 in total). Baselines need the owner's approval (the zoom change moves the pixels of nearly every frame slightly).

## 3.0.1

Fixes found while making the JWT vs Sanctum Reel (first real use of the 3.0.0 features), plus three small tools from making the Kit promo reel.

- **`build.py --audio-only`:** re-makes the SFX, re-cuts the voice, re-mixes and re-normalises on the frames of the last full build, with no render (about 20 s instead of 8 to 10 minutes). Use it after a change to SFX pins, the mix level, loudness or a new voice WAV of the same length. It stops with a clear message when the frames are missing or the scene length changed.
- **Scene option `valign: "mid"`:** puts the block stack lower on the screen (useful for a reel without captions).
- **`align.py --asr`:** places every script line by matching its TEXT against what was really said (fuzzy characters, Arabic letter variants, order kept, snapped to the phrase start), instead of guessing from line length. Input: `asr.json` from the new `engine/asr_phrases.py` (offline Whisper ONNX, phrases cut at pauses) or `#N t0-t1: text` lines. Warns when script and recording look different. The old `asr_seg.py` / `run_asr.sh` are unchanged.

- **SFX level:** the real mix (`engine/mix2.txt`) was ducking the sounds hard under the voice (ratio 6), so they were barely audible, while docs said "30%". Now the SFX is 42% of the voice level (`volume=0.593` after the voice +3 dB), no sidechain ducking. `sfx_preview.py`, docs, README and the skill state the same number.
- **`promise` pill:** locked-state text colour is now light, readable on light themes (paper, cream).
- **`scenefile.load`:** accepts scene names with a trailing `.py`.
- **Storyboard:** `validate`/`import` accept the overlay kinds (`promise`, button); the squeezed/variety deep-lint lines are warnings, not errors.
- **`align.py`:** the silence method picked the nearest pause for each line separately, so slow voices got duplicate or swapped starts. Now one strictly increasing start per line (dynamic programming, each pause used once). Test added.
- **Sound for errors:** a struck-out (wrong) card now plays an error sound, the strike line a razor cut and the right answer a success chime, instead of the pen stroke. Item, click and chime sounds vary (no same file twice in a row).
- **Beam:** the node that receives a light pulse lights up (about 0.7 s) and plays a chime; a travelling pulse plays a soft whoosh. New events `beam_pulse` and `beam_hit`; `"glow": False` on a node turns the light off.
- **`SFX_AUTO_ONLY`:** with `SFX_AUTO = False` keep hand-placed pins and the automatic sounds of just the listed kinds (beam, typing).
- **Typing sound** is a burst of exactly the on-screen typing time (`SFX_AUTO_ONLY` once played the whole 8 s clip).
- **Paper background:** dot ripple, drifting particles and breathing glow. `CTRLH_BG_MOTION=off` turns it off. Golden frames render with it off, so no baseline changed.
- **Docs:** the sound library is 35 sounds (`razor_01_cut` was missing from `SOUNDS.md`; every count says 35).
- **Theme rule in the skill:** the owner's videos use `paper_orange` without a question; anyone else using the skill is always asked which theme.
- **Golden:** new case `G10_bg_motion` (12 frames, animated paper background, wide and reel) approved by the owner; the other cases still render with the background animation off.
- **End card on light themes:** `paper_orange` (like `soft_cream`) now ends on a light paper background with dark logo letters, orange C and dark/orange sign-off; dark themes keep the black end card.
- **Skill:** version 3.0.1: manual SFX workflow, new events, background motion, SFX at 42%.

## 3.0.0

Major release (Phases 0–11): transitions, camera, persistent entities, `beam` paths, `tracks` timeline block, audio events and loudness target, render cache and speedups, block registry, `align.py`, storyboard JSON, two-format layout check, typography matrix, golden-frame tests (developer-only). Fix: `chain` error badge clipped in Reels. Claude Free workflow documented as primary (`docs/WORKFLOWS.md`), advanced agents optional. Details: `RELEASE_NOTES.md`.

## 2.2.0

- **New block `sysdiagram`** (reference: Transactional Outbox video): one stateful system diagram with stages, nodes + badges + pills, DB table group, BEGIN/COMMIT/ROLLBACK, travelling envelopes, ledger chips, stickers; own sound map; works on the 3 themes and in 16:9 / 9:16. Demo: `examples/sysdiagram_demo_scenes.py`.
- Fix: thumbnail `thumb_paper.py`: the "after" label no longer touches the big value in the right card.
- Per-scene `theme` key: one video can mix the three themes (build.py renders same-theme runs and joins them). No theme is "main"; the owner always chooses.
- Fix: `make_audio_lib.py` crashed on blocks whose `cols` is a number (icards) and gave no typing sound for `codeann` lines with (t, text) tuples; found by the first full v2.1.0 build.
- Named parts and sounds of `sysdiagram` are listed in docs/CATALOG.md (E08), docs/FEATURES.md and docs/SOUNDS.md; demo `examples/sysdiagram_demo_scenes.py`.

## 2.1.0

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
