# Getting started

Goal: install the kit, see a first frame, then build a video. About 10 minutes.

## 1. Install

You need Python 3.13 (3.11/3.12 were only syntax-checked), **FFmpeg** (with `ffprobe`) on your `PATH`, and **Pillow built with RAQM** (Arabic shaping).

```bash
git clone https://github.com/heshamadel1/ctrl-h.git
cd ctrl-h
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                         # pinned versions
ffmpeg -version && ffprobe -version
python3 -c "from PIL import features; print('raqm:', features.check('raqm'))"   # must print True
```
`requirements.txt` has the two required packages (`pillow`, `numpy`) and two optional ones (`onnxruntime`, `scipy`, only for the transcription step: [PIPELINE.md](PIPELINE.md#4-timings-voice--scene-times-optional)).

## 2. Check that it works (no voiceover needed)

```bash
python3 engine/smoke.py --quick        # compile + lint + one frame per format + SFX + docs links (prints SMOKE OK)
```

```bash
cd examples
FMT=wide python3 ../engine/render.py template_howto_scenes frames /tmp/frames 10 30 45
```
This writes PNG frames at 10, 30 and 45 s. Try the other themes and the 9:16 format:
```bash
CTRLH_THEME=soft_cream FMT=wide python3 ../engine/render.py template_howto_scenes frames /tmp/frames 30
CTRLH_THEME=paper_orange FMT=reel python3 ../engine/render.py template_howto_scenes frames /tmp/frames 30
```
`lint.py` may warn that `logo_ch.png` is missing: put your logo in `assets/` (or set `CTRLH_ASSETS`), see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 3. Your look (once)

`python3 engine/ctrlh_setup.py` asks for channel name, theme, card styles, background, sign-off lines and writes `ctrlh.config.json`. With Claude, the skill asks the same questions and saves the file. Every key is in [CONFIGURATION.md](CONFIGURATION.md); a commented example to copy is `profiles/ctrlh.config.example.json`. Preview pictures of the choices: `docs/images/` (`backgrounds.png`, `cards-dark.png`, `cards-paper.png`) and `python3 engine/ctrlh_preview.py <dir>` (writes `themes.png`, `backgrounds.png`).

## 4. Make a video

You need a voiceover WAV and a scene file (`SC` list). Full steps: [PIPELINE.md](PIPELINE.md).
```bash
python3 engine/build.py my_scenes --vo voice.wav --out out      # lint + render + SFX + mux + meta
```

## With Claude (skills)

Copy `skills/ctrlh-video-style` and `skills/ctrlh-thumbnail-style` into your Claude skills folder. Then send a script and a WAV. Before building, Claude asks (it never decides these alone): theme (`orange`, `paper_orange`, `soft_cream`), size (16:9 or 9:16), captions (optional), cards, background, sound effects (by name or Claude picks), thumbnail (optional). See [skills/ctrlh-video-style/SKILL.md](../skills/ctrlh-video-style/SKILL.md).
