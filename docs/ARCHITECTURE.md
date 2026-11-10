# Architecture

```
scene file (SC) ──► lint.py ──► render.py ──► anim.py (Video, draw_* blocks) ──► silent video (ffmpeg pipe)
                                   │                  ▲ themes.py  bg_styles.py  tokens.py  card_names.py  ctrlh_config.py
voice.wav ──► align_vo / asr_seg / align (optional timings)
scene file ──► make_audio_lib.py (assets/sfx) ──► sfx.wav
silent video + voice.wav + sfx.wav ──► mix2.txt (ffmpeg) ──► final.mp4 ──► captions.py (optional)
build.py runs all of it; meta.py writes meta.md / chapters.txt
```

| module | job |
|---|---|
| `build.py` | orchestrator: lint, plan parts, render, SFX, mux, meta |
| `render.py` | loads a scene file, renders frames or a video (`FMT`, `CTRLH_T0/T1`, cache) |
| `anim.py` | the engine: `Video`, every `draw_<kind>` block, cards, buttons, end card; `DRAW`, `EXTRA_H` registries |
| `blocks_flow.py`, `blocks_hud.py`, `blocks_paper.py` | flow/system blocks, live HUD background, paper blocks |
| `themes.py` | theme table (`accent`, `card`, `base`, `light`, `soft`, `bg`) |
| `bg_styles.py` | static backgrounds, `make(style, W, H, accent, base)` |
| `card_names.py` | single source of card names (descriptive name <-> old internal name) |
| `ctrlh_config.py` | loads `ctrlh.config.json` into `CTRLH_*` env vars |
| `tokens.py` | spacing, radius, safe margins |
| `lint.py` | layout, timing, logo and feature checks |
| `scenefile.py` | loads `.py` or `.json` scene files |
| `make_audio_lib.py` / `make_audio.py` | SFX from the library (default) / generated SFX (`CTRLH_SFX=synth`) |
| `captions.py`, `asr_captions.py`, `srt.py` | optional burned-in captions, cues from voice + script, SRT |
| `check_voice.py`, `sfx_preview.py`, `smoke.py` | checks without rendering: WAV vs scene file, hear the SFX, whole-kit test |
| `reels.py` | 30-60 s clips from a long video at scene boundaries |
| `align_vo.py`, `asr_seg.py`, `align.py`, `suggest.py`, `plan.py`, `meta.py` | timing and planning helpers |
| `ctrlh_setup.py`, `ctrlh_preview.py` | first-run questions, preview sheets |

Design rules: everything on screen is declared in `SC`; the same scene file renders 16:9 and native 9:16; the render cache re-renders only the scenes an edit touches; engine settings flow config -> env -> module constants (`_T = themes.THEMES[...]`, `SOFT`, `WIDE`).

How to extend: add a block with `draw_<kind>(d, box, b, t, k)` and `DRAW["kind"] = draw_kind` (plus `EXTRA_H`, a rule in `make_audio_lib.py`, a LINT rule, an example); add a theme as an entry in `themes.py` (flags `light`, `soft`, `bg`); add a background in `bg_styles.py` and `STYLES`.
