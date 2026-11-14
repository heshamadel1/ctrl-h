# Storyboard (one document for the whole video)

**What:** a single JSON file that describes the production: scenes with times, chapter, headline, blocks, transitions, camera, entities, sound switches, plus what is said (`say`) and output settings (formats, theme, loudness). The engine compiles it to the same flat scene data it always used, so every block/theme/transition/camera/entity/sound feature works unchanged.

**Why:** content preparation (what is on screen when) is separated from rendering, and a storyboard is checked with readable errors *before* anything is rendered (`scenes[3].blocks[1].k: unknown block kind 'x'`).

**When:** use it for a new video. Existing `*_scenes.py` / `*.json` scene files keep working untouched; nothing has to be migrated.

## Standard Claude workflow (no terminal, no agents)
Ask Claude in a normal chat: "prepare the storyboard JSON for this script using the Ctrl + H kit". Claude writes the file; it is rendered with the usual `build.py` / `render.py` commands, which accept a storyboard directly (`python3 engine/build.py story.json ...`). Validation runs automatically on load and stops with the list of problems.

## Advanced developer workflow (optional)
```
python3 engine/storyboard.py template                       # starting point
python3 engine/storyboard.py validate story.json            # errors + warnings (also runs lint on the compiled scenes)
python3 engine/storyboard.py summary  story.json            # one line per scene + the spoken text
python3 engine/storyboard.py compile  story.json out.json   # the flat scene file
python3 engine/storyboard.py import   old_scenes.py story.json   # convert an existing scene file
```
Agents / Claude Code can generate, validate and fix storyboards in a loop; nothing requires them.

## Fields
`storyboard: 1` (version) · `meta{title,language,notes}` · `output{formats,theme,loudness}` · `voiceover{file,script}` · `timing{duration,end,tag1,tag2,subscribe_at,follow_at}` (all optional: end = last scene end, tag1 = end+0.2, tag2 = end+1.5, duration = tag2+1.5) · `stages` · `tech` · `transition` (default for all scenes) · `audio{auto,events,pins}` · `scenes[]`.
Scene: `id`, `start`+`end` or `dur` (starts where the previous ended), `stage` (index into `stages`), `style`, `head`, `head_t`, `blocks`, `transition`/`trans_in`/`trans_out`, `camera`, `entities` (define each id once), `sfx`, `dims`, `reserve`, `reserve_reel`, `grid`, `cw`, plus `say` and `notes` (documentation only, never rendered).
Times are seconds on the global timeline, same as scene files. Example: `examples/storyboard_example.json`.

## Settings precedence
`output.theme`, `output.loudness` and `transition` are *defaults*: an environment variable (`CTRLH_THEME`, `CTRLH_LOUDNESS`, `CTRLH_TRANSITION`) or config value you set yourself wins. `output.formats` is documentation for the tools; the format is still chosen when rendering (`FMT`, `--reel`).

## Limits
- Validation checks structure, times, indexes, known block kinds/themes/transitions/cameras/entities/sound kinds. Block-specific fields are checked by the engine (lint / render), not by the storyboard.
- `say` is not matched against the voiceover automatically; use `engine/align.py` for timing from a script.
- Block times outside their scene give a warning only.
- Importing keeps all fields, generates ids `s0, s1…` and loses Python comments.
- `lint` video-type advice (scene count, features) shows as warnings in `validate`, not errors.
