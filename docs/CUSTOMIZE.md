# How to change things

## Config (`ctrlh.config.json`, example in `profiles/`)

| key                       | what it does                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| `theme`, `accent`         | colour theme / accent colour (`themes.py`)                                                              |
| `card_styles`             | `"all"` or a list such as `["classic","glass"]`                                                         |
| `bg_style`                | background style (`bg_styles.py`)                                                                       |
| `signoff_1`, `signoff_2`  | end card lines                                                                                          |
| `formats`                 | `["wide"]` (16:9, default) or `["wide","reel"]` (also 9:16). 9:16 only when you ask for it              |
| `video_type`              | `explainer`, `short`, `series` (`profiles/video-types.json`: features lint expects, `max_part_seconds`) |
| `max_part_seconds`        | `build.py` splits longer videos into equal parts at scene boundaries (default 180)                      |
| `disabled_blocks`         | block kinds the engine drops, e.g. `["poll","shock"]`                                                   |
| `dims`                    | `true` re-enables the screen-darkening effect (off by default)                                          |
| `workers`                 | render processes (default = CPU count)                                                                  |
| `subscribe_t`, `follow_t` | button times (the scene file `SUB_T`/`FOL_T` win)                                                       |

Every key becomes an environment variable (`ctrlh_config.py`), so `CTRLH_DISABLED_BLOCKS=poll python3 ...` works too.

## What to edit for what

| I want to change                                                  | edit                                                                                                                                                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a colour or the whole palette                                     | `engine/themes.py`                                                                                                                                                              |
| spacing, radius, safe margins, text sizes of the technical blocks | `engine/tokens.py`, or a JSON file in `CTRLH_TOKENS`                                                                                                                            |
| how block `X` looks or moves                                      | `engine/anim.py`, function `draw_X` (the flow / system blocks: `engine/blocks_flow.py`)                                                                                         |
| the height a block needs                                          | `EXTRA_H` registry in `anim.py`                                                                                                                                                 |
| the sound of a block                                              | `engine/make_audio.py` (one entry per block kind)                                                                                                                               |
| add a new block                                                   | write `draw_<kind>(d, box, b, t, k)`, then `DRAW["kind"] = draw_kind` (and `EXTRA_H`, a SFX entry, a LINT rule if it has limits, a demo in `examples/docs_gallery_features.py`) |
| the video types / required features                               | `profiles/video-types.json`                                                                                                                                                     |
| background style                                                  | `engine/bg_styles.py`                                                                                                                                                           |
| end card, chapter banner, buttons                                 | `end_frame`, `chapter_banner`, `corner_logo` in `anim.py`                                                                                                                       |

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
