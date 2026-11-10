# How to change things

## Config
All keys, types, defaults and priority: [CONFIGURATION.md](CONFIGURATION.md). Card names: `plain_dark`, `glass_blur`, ... (list in [CATALOG.md](CATALOG.md)).

## What to edit for what
| I want to change | edit |
|---|---|
| a colour or the whole palette | `engine/themes.py` |
| spacing, radius, safe margins, text sizes of the technical blocks | `engine/tokens.py`, or a JSON file in `CTRLH_TOKENS` |
| how block `X` looks or moves | `engine/anim.py`, function `draw_X` (the flow / system blocks: `engine/blocks_flow.py`) |
| the height a block needs | `EXTRA_H` registry in `anim.py` |
| the sound of a block | `engine/make_audio_lib.py` (rules per block kind) and `assets/sfx/` (the files, see SOUNDS.md) |
| add a new block | write `draw_<kind>(d, box, b, t, k)`, then `DRAW["kind"] = draw_kind` (and `EXTRA_H`, a SFX entry, a LINT rule if it has limits, a demo in `examples/docs_gallery_features.py`) |
| the video types / required features | `profiles/video-types.json` |
| background style | `engine/bg_styles.py` |
| end card, chapter banner, buttons | `end_frame`, `chapter_banner`, `corner_logo` in `anim.py` |

## Typical workflow
1. Voiceover WAV, then ASR and script (`run_asr.sh`, `align_vo.py`, `plan.py`).
2. Write the scene file (`examples/` has working ones).
3. `python3 engine/lint.py my_scenes --sheet sheet.png --strict` and look at the sheet.
4. `python3 engine/build.py my_scenes --vo voice.wav` (add `--formats wide,reel` for 9:16).
5. Edit a scene and run step 4 again: only the scenes you touched are re-rendered (cache in `.ctrlh_cache`; `CTRLH_CACHE=0` disables it).

## Test a short piece
`CTRLH_T0=10 CTRLH_T1=20 python3 engine/render.py my_scenes test.mp4` renders only seconds 10 to 20 (frame times stay global).

## Running with a local agent
The engine needs only Python 3, Pillow, numpy and ffmpeg (no npm). An agent that works on your own machine can run the same commands; give it the skills in `skills/` and this folder.

## Themes and paper blocks
- Add a theme: one line in `engine/themes.py` (`accent, card, base, light, soft, bg`). `light=True` switches ink/gray text; `soft=True` gives the soft_cream card, button and end-card look; `bg` is the signature background.
- Paper blocks live in `engine/blocks_paper.py` (loaded by `anim.py` like `blocks_flow.py`); add SFX rules in `engine/make_audio_lib.py`.

## Live HUD background and chips
- Code: `engine/blocks_hud.py` (`HudLive`, `auto_chips`, `HUD_TOOLS`). Add a tool name to `HUD_TOOLS` so it becomes a chip automatically.
- Speed of the pulse: `2 * math.pi * t / 4.4` in `HudLive.frame`; particles: `n = 120`; icons: `ICONS`; loading bar: `t / 6.5`.
- Per scene: `dict(..., chips=["Laravel", "Docker"])`.

## Using it for your own channel
| Where | What to change |
|---|---|
| `assets/logo_ch.png`, `assets/mono.png` | your logo (end card) and corner monogram |
| `skills/*/SKILL.md` | owner, channel name, platforms, language, sign-off, voice settings |
| End card text | `signoff_1` / `signoff_2` in the config (also say these words at the end of the voiceover and set `TAG1`/`TAG2`) |
| Labels | `label_chapter`, `label_ok`, `label_wrong` |
| Subscribe / Follow labels | fixed English text in `engine/anim.py` (search `SUBSCRIBE`) |
| `engine/ctrlh_bg.py` | background motifs per technology |
| `README.md`, `SETTINGS.md`, `LICENSE` | name, links, copyright |
Check for leftovers: `grep -rniE "ctrl ?\+? ?h|ctrlh|hesham|think deeper|build smarter" --include="*.py" --include="*.md" .`
