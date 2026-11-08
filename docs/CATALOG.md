# Catalog: everything the kit can do, with a name and a code

One reference for anyone using the skill. Pick from it by NAME (or code) when you ask Claude for a video: "theme paper_orange, only cards A03 and A06, background H2".

## How to use it (30 seconds)

1. Send Claude your script (and your voiceover WAV).
2. Claude asks ONE question: **theme** (main dark `orange` or `paper_orange`) and **cards** (all types, ONE card look, or certain families A-H).
3. Claude builds: lint, contact sheet, render (long videos split into parts of at most 180 s), SFX, mux, `meta.md`, `chapters.txt`.
4. You get the video, its thumbnail and a short list of the features used. Changes: say what to change; only the touched scenes re-render.

Own scene files: Python or JSON (`engine/scenefile.py`), or JavaScript with `node/ctrlh.js`.
Turn blocks off: `"disabled_blocks": "poll,predict"`. One basic card look for the whole video: `"card_style": "glass_blur"`.
Pictures are contact sheets in `docs/images/` (names written under each picture).

## A. Basic cards (the `card` block, 12 looks)

Picture: `cards-dark.png / cards-paper.png`

| code | name              | use for             |
| ---- | ----------------- | ------------------- |
| A01  | `plain_dark`      | good/bad statements |
| A02  | `tag_header`      | rules, definitions  |
| A03  | `glass_blur`      | calm explanations   |
| A04  | `numbered_list`   | steps, mistakes     |
| A05  | `outline_thin`    | calm lines          |
| A06  | `solid_orange`    | one key statement   |
| A07  | `neon_glow`       | emphasis            |
| A08  | `paper_note`      | high contrast       |
| A09  | `soft_rounded`    | right/wrong lists   |
| A10  | `terminal_window` | commands, results   |
| A11  | `step_arrows`     | ordered steps       |
| A12  | `icon_box`        | right/wrong lists   |

## B. Infographic cards

Picture: `blocks-sheet-1.png`

| code | name       | use for                    |
| ---- | ---------- | -------------------------- |
| B01  | `icards`   | icon cards for list topics |
| B02  | `steplist` | steps with file + lines    |
| B03  | `fixcards` | problem chain then fix     |
| B04  | `icon3d`   | 3D icon row                |

## C. Compare cards

Picture: `blocks-sheet-1.png / blocks-sheet-2.png`

| code | name      | use for                            |
| ---- | --------- | ---------------------------------- |
| C01  | `versus`  | side by side with code and bullets |
| C02  | `matrix`  | feature table                      |
| C03  | `tabcard` | tabs (play / rec / edit)           |
| C04  | `compare` | two panels                         |
| C05  | `titlevs` | vs header                          |
| C06  | `split`   | two systems split screen           |

## D. Technical cards

Picture: `blocks-sheet-1.png`

| code | name        | use for                             |
| ---- | ----------- | ----------------------------------- |
| D01  | `arch`      | architecture nodes + request dots   |
| D02  | `er`        | database tables + FK lines          |
| D03  | `http-diff` | HTTP request/response and code diff |
| D04  | `queue`     | worker + queue jobs                 |
| D05  | `recap`     | summary card                        |

## E. Flow and system cards

Picture: `blocks-sheet-1.png / blocks-sheet-2.png`

| code | name              | use for               |
| ---- | ----------------- | --------------------- |
| E01  | `chain`           | chain of handlers     |
| E02  | `pipeline`        | pipeline stages       |
| E03  | `deviceflow`      | device to server flow |
| E04  | `flow / flowmini` | nodes + steps         |
| E05  | `hub`             | hub and spokes        |
| E06  | `timeline`        | timeline nodes        |
| E07  | `grid-tiles`      | tiles grid            |

## F. Code cards

Picture: `blocks-sheet-1.png / blocks-sheet-2.png`

| code | name            | use for               |
| ---- | --------------- | --------------------- |
| F01  | `code-focus`    | code with line focus  |
| F02  | `code-terminal` | terminal look         |
| F03  | `codeann`       | code with annotations |

## G. Interactive cards

Picture: `blocks-sheet-1.png / blocks-sheet-2.png / blocks-sheet-3.png`

| code | name                        | use for                   |
| ---- | --------------------------- | ------------------------- |
| G01  | `shock`                     | 3 s hook                  |
| G02  | `strike`                    | wrong struck, right shown |
| G03  | `ba`                        | before / after slider     |
| G04  | `poll`                      | poll bars (no invented %) |
| G05  | `predict`                   | predict then answer       |
| G06  | `mystery`                   | question then reveal      |
| G07  | `promise`                   | locked then unlocked      |
| G08  | `challenge`                 | challenge ring            |
| G09  | `chips`                     | keyword pills             |
| G10  | `corner`                    | corner labels             |
| G11  | `buttons`                   | Subscribe / Follow        |
| G12  | `ring`                      | countdown ring            |
| G13  | `counter / bigcount / gain` | numbers and gains         |

## H. Paper cards (work on every theme)

Picture: `blocks-sheet-2.png / blocks-sheet-3.png`

| code | name        | use for          |
| ---- | ----------- | ---------------- |
| H01  | `quote`     | quote card       |
| H02  | `chatwin`   | AI chat window   |
| H03  | `minichart` | mini chart       |
| H04  | `skeleton`  | skeleton loading |
| H05  | `filegrid`  | file grid        |
| H06  | `bigcount`  | big counter      |
| H07  | `note`      | note card        |

## I. Card shapes (scene `grid=` / `cw=`; automatic rotation when a scene has 2+ cards)

| code | name      | what it is                                   |
| ---- | --------- | -------------------------------------------- |
| I01  | `squares` | equal squares side by side                   |
| I02  | `pairs`   | two columns                                  |
| I03  | `narrow`  | one column, 60 % wide (`cw=0.6`)             |
| I04  | `tiles`   | all cards as tiles in a row (`grid="tiles"`) |

## J. Backgrounds (config `bg_style`, any colour; or your own PNG with `background_file`)

Picture: `backgrounds.png`, `bg-hud-live.png`

| code | name        | look                                                                                                                                                                                      |
| ---- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| J01  | `hud_live`  | DEFAULT of the main theme: HUD circuit plate, animated pulses, particles, and tool chips with icons that change per scene (from scene `chips`, then tools named in the text, then `TECH`) |
| J02  | `paper`     | cream paper with grid and dots (default of `paper_orange`)                                                                                                                                |
| J03  | `circuit`   | circuit lines                                                                                                                                                                             |
| J04  | `grid`      | fine grid                                                                                                                                                                                 |
| J05  | `hex`       | hexagons                                                                                                                                                                                  |
| J06  | `dots`      | dot field                                                                                                                                                                                 |
| J07  | `waves`     | soft waves                                                                                                                                                                                |
| J08  | `aurora`    | colour glow                                                                                                                                                                               |
| J09  | `blueprint` | blueprint grid                                                                                                                                                                            |
| J10  | `terminal`  | scanlines and code columns                                                                                                                                                                |
| J11  | `minimal`   | almost plain                                                                                                                                                                              |

A theme's own background replaces `hud_live` unless `"bg_style_locked": true`.

## K. Themes (config `theme`)

| code | name           | look                                                                       |
| ---- | -------------- | -------------------------------------------------------------------------- |
| K01  | `orange`       | MAIN: dark charcoal, orange `#FF8A11` accent, `hud_live` background        |
| K02  | `paper_orange` | SECOND: cream paper, thick black borders, hard shadows, orange highlighter |

Other colours: `accent`, `card_color`, `bg_color`. Per-series look: `"series": "name"` in the config.

## L. Automatic (no code needed)

Subscribe / Follow buttons (`SUB_T`, `FOL_T`), chapter banner "part N of M", scene-progress dots, next-scene pill, scene link frame, camera push-in, alternating entry directions, SFX from the scene file, end card with logo and sign-off, part splitting (max 180 s), per-scene render cache.

## M. Scene file keys

Scene: `style, t0, t1, stage, head, head_t, blocks, grid, cw, reserve, reserve_reel, longcards, chips`. File: `DUR, T_END, TAG1, TAG2, STAGES, TECH, SC, SUB_T, FOL_T`. Scenes must touch: scene N `t1` = scene N+1 `t0`.

## N. Config keys (`ctrlh.config.json`)

`theme, accent, card_color, bg_color, card_style, card_styles, bg_style, bg_style_locked, background_file, assets, font_ar, font_latin, signoff_1, signoff_2, label_ok, label_wrong, label_chapter, out_w, subscribe_t, follow_t, formats, disabled_blocks, workers, dims, video_type, max_part_seconds, series, series_name`. Every key also works as an env var `CTRLH_<KEY>`; the env wins.

## O. Commands (from the kit root; scene file given by module name, `.py` or `.json`)

| command                                                                           | does                                                                               |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `python3 engine/ctrlh_setup.py`                                                   | first-run setup (saves the config)                                                 |
| `python3 engine/suggest.py script.txt`                                            | suggests scenes and blocks from a script                                           |
| `python3 engine/align.py scenes voice.wav`                                        | aligns scene times to the audio (`--whisper` for word timing, needs a local model) |
| `python3 engine/lint.py scenes --strict --sheet`                                  | checks layout, timing, Arabic/Latin rules; contact sheet of all scenes             |
| `python3 engine/preview.py scenes`                                                | fast key frames, no full render                                                    |
| `python3 engine/build.py scenes --vo voice.wav [--formats wide] [--max-part 180]` | the whole pipeline                                                                 |
| `python3 engine/srt.py scenes out.srt`                                            | subtitles                                                                          |
| `python3 engine/meta.py ...`                                                      | description, hashtags, `chapters.txt` (also run by build)                          |
| `python3 engine/docs_cards.py`                                                    | redraws `cards-dark.png` / `cards-paper.png`                                       |
| `node node/example.js`                                                            | scenes written in JavaScript                                                       |

Full parameters of every block: `skills/ctrlh-video-style/REFERENCE.md`.
