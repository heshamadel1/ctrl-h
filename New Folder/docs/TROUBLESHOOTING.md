# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Arabic letters disconnected or reversed | Pillow built without RAQM | install `libraqm`, reinstall Pillow; check `features.check('raqm')` prints `True` |
| Squares (tofu) instead of text | Arabic in a Latin/mono font (code, chat reply lines, chips) | write Latin there, or set `CTRLH_FONT_AR` to an Arabic font |
| Empty frame instead of the logo (corner, end card) | `assets/logo_ch.png` / `mono.png` missing | add them or set `CTRLH_ASSETS=/my/assets`; `lint.py` warns about it |
| `No module named 'xxx_scenes.py'` | module name passed with `.py` | pass `my_scenes` (no `.py`) to `render.py`/`lint.py`/`build.py`; `make_audio_lib.py` takes the file path |
| `ffmpeg: command not found` | FFmpeg not installed | install it, check `ffmpeg -version` and `ffprobe -version` |
| Render stops / disappears | long render killed with the terminal or session | run `setsid nohup ... & disown`, poll the output; a cached re-run is fast |
| Video and audio lengths differ | `DUR` differs from the WAV | `DUR` = `ffprobe` duration of the WAV; mux with `-t "$DUR"` |
| Frame count wrong after concat | variable fps | use `-fps_mode passthrough` and `setpts=N/30/TB`; count frames with ffprobe |
| Captions with broken Arabic/English order | libass bidi | use `engine/captions.py` (PNG overlays), not ASS |
| `LINT: scene N squeezed to X%` | too much content | below ~80%: split the scene or use fewer blocks |
| Black rectangle bottom-right | next-scene preview pill (old themes) | `soft_cream` merges it into the chapter pill; other themes: update to v2.1.0 |
| SFX too loud/quiet or repeating | mix level / pins | mix is 30% (`mix2.txt`); pin sounds with `SFX`, `SFX_GAIN`; list in [SOUNDS.md](SOUNDS.md) |
| Keyboard sound does not match typing | old synthesized SFX | v2.1.0 makes bursts with the exact typing length; do not use `CTRLH_SFX=synth` |
| Big output file | 4K / long video | `OUT_W=1280`, or split with `--max-part` |
| `align_vo.py` finds too many/few phrases | silence threshold | edit `thr` (default -42 dB) and `gap` in `segments()` |
| Wrong theme/background in a frame | env variable overrides config | check `CTRLH_THEME` / `CTRLH_BG_STYLE` in your shell (env wins) |

Diagnose: run `lint.py my_scenes --sheet sheet.png` and look at the contact sheet and the `LINT:` lines first; render single frames with `render.py ... frames out <seconds>`.
