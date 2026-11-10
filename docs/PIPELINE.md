# Pipeline: from script to published video

There is ONE workflow. Two ways to run it: **Automated** (`build.py`, recommended) and **Manual** (the same steps as separate commands, useful to debug).

```
script -> voiceover WAV -> timings -> scene file (SC) -> lint -> render -> SFX -> (captions) -> mux -> meta / thumbnail
```

## 1. Script and voice
Write the voiceover script (numbered scenes, English technical terms). Generate the WAV in Google AI Studio (Gemini Flash TTS, male voice, Full Script, WAV, temperature 0.7-0.8). The video is exactly as long as the WAV.

## 2. Choices before building
Theme (`orange` / `paper_orange` / `soft_cream`), size (16:9 or 9:16), captions (yes/no), cards, background, sound effects, thumbnail. Reference lists: [CATALOG.md](CATALOG.md).

## 3. Scene file
A Python (or JSON) file with `SC`, `STAGES`, `DUR`, `T_END`, `TAG1`, `TAG2`, `TECH` (and optionally `SUB_T`, `FOL_T`, `SFX`). Start from `examples/template_howto_scenes.py` (16:9 how-to, `# EDIT` lines) or a larger example. Fields of every block: [FEATURES.md](FEATURES.md).

## 4. Timings (voice -> scene times)
Name the WAV `<name>_vo.wav` and run from its folder.
```bash
python3 engine/align_vo.py mytopic_vo.wav mytopic           # silence-based phrases -> mytopic_segs.txt (no model needed)
SHERPA=~/sherpa WORK=$PWD bash engine/run_asr.sh mytopic    # optional: text of each phrase -> mytopic_seg_asr.txt (needs onnxruntime, scipy, Whisper-small)
python3 engine/align.py my_scenes voice.wav                 # optional: snap scene times to the voice
python3 engine/suggest.py script.txt                        # optional: scene ideas from the script
```
`_segs.txt`: first line `name total-seconds count`, second line `start-end` of every phrase. These are the times your cards/code/poll should appear. Silence threshold -42 dB, gaps < 0.14 s merged (tune `thr`, `gap` in `segments()`). Whisper-small (sherpa-onnx model files only, ~640 MB): `curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2` and extract into `~/sherpa/`. Arabic ASR text is noisy: use it for times, trust your script for words. Map script lines to phrases in order; set `T_END`, `TAG1`, `TAG2` from the last three phrases ("Ctrl H", sign-off lines).

## 5. Build

### Automated
```bash
python3 engine/build.py my_scenes --vo voice.wav --out out [--formats wide,reel] [--max-part 180] [--strict] [--plan-only]
```
Does: lint + contact sheet, auto split of long videos (parts at scene boundaries), render per format, SFX track, mux (voice + SFX at 30%), `meta.md`, `chapters.txt`.

| flag | meaning |
|---|---|
| `--vo` | voiceover WAV (required) |
| `--out` | output folder (default `.`) |
| `--formats` | `wide` (16:9), `reel` (9:16), or `wide,reel` |
| `--max-part` | seconds per part before auto split (default 180) |
| `--strict` | lint warnings stop the build |
| `--plan-only` | print the part plan and exit |
| `--check-voice` | stop the build when the WAV and the scene file disagree (without the flag the CHECK lines are only printed) |
| `--check-voice-only` | run the check and exit, no render |

Output files: `<name>_wide.mp4` (and `_reel.mp4`, `_partN_` when split), `<name>_meta.md`, `<name>_chapters.txt`, `<name>_sheet.png`. Long renders: run in the background (`nohup ... &`) and poll.

### Manual
```bash
python3 engine/lint.py my_scenes --sheet sheet.png --strict      # layout + timing + features
FMT=wide python3 engine/render.py my_scenes frames out 20 60     # fast frames (FMT=reel for 9:16)
FMT=wide python3 engine/render.py my_scenes v_wide.mp4           # silent video
python3 engine/make_audio_lib.py my_scenes.py sfx.wav            # SFX track from assets/sfx
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 voice.wav)
ffmpeg -y -i v_wide.mp4 -i voice.wav -i sfx.wav -filter_complex_script engine/mix2.txt -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$DUR" final.mp4
```
`CTRLH_T0` / `CTRLH_T1` render only a time window.

### Checks before rendering (no video is rendered)
```bash
python3 engine/check_voice.py my_scenes voice.wav            # WAV length vs DUR, T_END / TAG1 / TAG2 inside the voice, gaps between scenes
python3 engine/sfx_preview.py my_scenes.py voice.wav pv.mp3 [--from 0 --to 60]   # hear voice + sound effects (30%) as a small mp3
python3 engine/smoke.py [--quick]                              # whole-kit test: compile, lint examples, frames per theme x format, SFX, docs links, setup
```

### Clips for Reels / Shorts from a long video
```bash
python3 engine/reels.py my_scenes --vo voice.wav --out clips [--min 30 --max 60] [--format reel] [--list-only]
```
Cuts at scene boundaries (never inside a scene), prints a plan with a title per clip (the scene headline) and renders each clip with the same scene file, voice and SFX cut to the clip.

## 6. Formats
16:9 is 1920x1080, 9:16 is 1080x1920. Both are **native renders** from the same scene file (`FMT=wide` / `FMT=reel`): blocks have their own 9:16 layout (`cols_reel`, stacked rows), it is not a crop. `OUT_W` scales the output.

## 7. Sound effects
`assets/sfx/` holds 34 sounds named `<category>_<NN>_<name>.mp3` ([SOUNDS.md](SOUNDS.md)). `make_audio_lib.py` places them automatically (cuts, card entrances, code typing, impacts) at 30% under the voice with no repeats. Pin a sound in the scene file:
```python
SFX = [(12.5, "impact_01"), (30.0, "click"), (40.2, "typing", 2.0)]   # (time, file prefix or category[, seconds])
SFX_AUTO = False      # only the pins
```
`TYPING_SPEED = 1.0` (0.7 slower / 1.4 faster) changes the keystroke rhythm of code and chat typing without changing its length. `CTRLH_SFX=synth` switches back to the old generated sounds (`make_audio.py`).

## 8. Captions (optional)
```bash
python3 engine/asr_captions.py voice.wav script.txt cues.txt [--keywords "word,word"]   # cues from the voice + your script text
python3 engine/captions.py cues.txt video.mp4 video_cc.mp4 [--reel]      # cues.txt: start<TAB>end<TAB>text
python3 engine/srt.py my_scenes video.srt                                # or a plain .srt from the scene text
```
Arabic in a rounded box (theme colours), `[[words]]` highlighted in orange, every English word highlighted automatically (`--no-auto-en` to turn it off). Captions are PNG overlays (libass breaks mixed Arabic/Latin). Without captions nothing is drawn.

## 9. Thumbnail
`skills/ctrlh-thumbnail-style` makes a 1280x720 thumbnail on request (optional per video).
