# Ctrl + H Video Kit

Branded explainer-video pipeline + Claude skills for the **Ctrl + H** programming channel (Egyptian Arabic, English technical terms).

Takes a voiceover WAV and a declarative scene file and renders a synced **16:9 (1920x1080)** and native **9:16 (1080x1920)** video at 30 fps, with generated sound effects. No captions, no opening card.

Owner: Hesham Adel · GitHub: [@heshamadel1](https://github.com/heshamadel1)

Platforms: YouTube (`ctrlh-dev`), TikTok, Instagram, Facebook.

Content: Programming, Software Engineering, Back-End Development.

---

## 1. How it works (the big picture)

```
post / topic ──► voiceover script ──► voiceover WAV ──► timings ──► scene file ──► video + SFX ──► final .mp4 (+ thumbnail)
 (you / Claude)   (you / Claude)     (Google AI Studio)  (align_vo,    (SC list)    (anim.py,        (ffmpeg mux)
                                                          run_asr)                    make_audio.py)
```

Everything on screen is **declared** in one Python scene file (`SC`): which card appears at which second, which code is typed, which poll, etc. The same scene file renders both formats (`FMT=wide` and `FMT=reel`).

## 2. What is inside

| Path                                     | What it is                                                                                                                                                         |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `skills/ctrlh-video-style/SKILL.md`      | Claude skill: the full video style, content workflow, voice settings, scene rules and production settings. Claude reads it to build videos the same way every time |
| `skills/ctrlh-thumbnail-style/SKILL.md`  | Claude skill: YouTube thumbnail style (1280x720)                                                                                                                   |
| `engine/anim.py`                         | The scene engine: cards (4 styles), code, terminal, flow, poll, buttons, camera zoom, end card...                                                                  |
| `engine/make_audio.py`                   | Generates sound effects (SFX) from the scene file                                                                                                                  |
| `engine/align_vo.py`                     | Splits a voiceover into spoken phrases by silence and writes `<name>_segs.txt`                                                                                     |
| `engine/asr_seg.py`, `engine/run_asr.sh` | Local Whisper (sherpa-onnx) transcription of each phrase                                                                                                           |
| `engine/ctrlh_bg.py`                     | Per-technology background generator                                                                                                                                |
| `engine/clip.py`                         | Renders a short test clip from a scene file                                                                                                                        |
| `engine/mix2.txt`                        | FFmpeg audio mix (voice + SFX with ducking)                                                                                                                        |
| `examples/`                              | Real scene files to copy: `lk_scenes.py` / `nx3_scenes.py` (full videos), `v3_*`, `v4_*`, `w_scenes.py` (block demos)                                              |
| `assets/fonts/`                          | Cairo SemiBold (Arabic) + Fira Code SemiBold (English/code), both SIL OFL                                                                                          |
| `assets/backgrounds/default.png`         | Default background. Put your logo files in `assets/` too                                                                                                           |
| `SETTINGS.md`                            | Short list of the fixed rules (platforms, voice, buttons, cards)                                                                                                   |

## 3. Install

**Required** (video + sound effects):

| Requirement                | Notes                                     |
| -------------------------- | ----------------------------------------- |
| Python 3.10+               |                                           |
| Pillow with RAQM (libraqm) | needed for correct Arabic shaping and RTL |
| NumPy                      |                                           |
| FFmpeg                     | must be on your `PATH`                    |

```bash
git clone https://github.com/heshamadel1/ctrl-h.git
cd ctrl-h
pip install pillow numpy
ffmpeg -version
```

**Optional** (only for the transcription step, section 5.1 - 5.5):

| Requirement                              | Notes                                                                       |
| ---------------------------------------- | --------------------------------------------------------------------------- |
| `onnxruntime`                            | runs the Whisper model                                                      |
| `scipy`                                  | audio resampling / spectrogram                                              |
| Whisper-small model from **sherpa-onnx** | model files only: the `sherpa-onnx` Python package itself is **not** needed |

```bash
pip install onnxruntime scipy

# Whisper-small model (about 640 MB download), placed in a folder of your choice, e.g. ~/sherpa
mkdir -p ~/sherpa && cd ~/sherpa
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2
tar xjf sherpa-onnx-whisper-small.tar.bz2
ls sherpa-onnx-whisper-small     # must contain small-encoder.int8.onnx, small-decoder.int8.onnx, small-tokens.txt
```

You can skip the transcription step: it only gives you the text of each spoken phrase so your script can be matched to the timings. The silence-based timings from `align_vo.py` work without it.

## 4. Quick start (try it without any voiceover)

```bash
cd examples

FMT=wide python3 lk_anim.py frames out 20 60      # PNG preview frames at 20 s and 60 s (fast)
FMT=wide python3 lk_anim.py video v_wide.mp4      # full 16:9 render (6-10 min, run in the background)
FMT=reel python3 lk_anim.py video v_reel.mp4      # native 9:16

python3 ../engine/make_audio.py lk_scenes.py sfx.wav     # sound effects

ffmpeg -y -i v_wide.mp4 -i voice.wav -i sfx.wav \
  -filter_complex_script ../engine/mix2.txt \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k \
  -t <DURATION> final.mp4
```

The commands above use `examples/lk_anim.py` and `examples/lk_scenes.py` (both are in the repo) and must be run from inside `examples/`. Replace them with the relevant scene files for your video. `voice.wav` is your voiceover; `<DURATION>` is its length in seconds (the video must be exactly as long as the audio).

Tip: always check frames (`frames` command) in both formats before a full render.

## 5. New video workflow

1. Create or edit the content for the Ctrl + H channel.
2. Prepare a ready-to-record voiceover script in Egyptian Arabic, divided into numbered scenes with approximate timestamps.
3. Generate the voiceover using Google AI Studio — Gemini Flash TTS (settings below).
4. Preferred voice settings:
   - Voice: Male
   - Script mode: Full Script
   - Language: Egyptian Arabic
   - Model version: **3.8** is the owner's own designation. Before you rely on it, open Google AI Studio and check the exact official model name / ID shown there, and use that exact name. Do not guess or rename it.
   - Preferred output: WAV
   - Temperature: Start at 0.8, or use 0.7–0.8 if the setting is available.
5. Segment the voiceover (5.1 - 5.5 below).
6. Copy a suitable scene example and its animation file (for example `lk_scenes.py` + `lk_anim.py` to `mytopic_scenes.py` + `mytopic_anim.py`, and change the import line in the anim file). Set `SC`, `STAGES`, `DUR`, `T_END`, `TAG1`, `TAG2`, and `TECH`.
7. Check frames in both formats.
8. Render the wide and native vertical versions.
9. Generate sound effects and synchronize the final audio.
10. Export and verify both videos.

### 5.1 - 5.5 Creating the timings (voice → scene times)

Name your files `<name>_vo.wav` (voiceover) and run everything from the folder where the WAV is (call it the work folder).

1. **Find the spoken phrases (no extra install):**

   ```bash
   python3 <repo>/engine/align_vo.py mytopic_vo.wav mytopic
   ```

   It cuts the WAV at silences (threshold -42 dB, gaps shorter than 0.14 s are merged, phrases shorter than 0.12 s are dropped) and writes `mytopic_segs.txt`:

   ```
   mytopic 124.76 41
   0.00-2.31, 2.80-5.12, 5.60-9.01, ...
   ```

   First line: `name  total-seconds  number-of-phrases`. Second line: `start-end` of every phrase in seconds. These start times are when your cards/code/poll should appear.

2. **Get the text of each phrase (optional, needs the model from section 3):**

   ```bash
   SHERPA=~/sherpa WORK=$PWD bash <repo>/engine/run_asr.sh mytopic
   ```

   `SHERPA` is the folder that contains `sherpa-onnx-whisper-small/`; `WORK` is the folder with `mytopic_vo.wav` and `mytopic_segs.txt`. It writes `mytopic_seg_asr.txt`:

   ```
   #1 0.00-2.31: آخر تذكرة في الحفلة
   #2 2.80-5.12: ...
   ```

   Takes about 3 minutes per 2 minutes of audio. The text is only for matching order and wording; the Whisper output can have mistakes, so trust your own script for the words.

3. **Map your script to the phrases:** go through your script line by line, in order, and give every line the start time of its phrase (about 7 syllables per second helps you spot a phrase that was split in two or merged). Put these times in the scene file (`t=`, `t0=`, `t1=`). Cards can be off by about 0.5 s when a phrase split is a guess: check frames and adjust.
4. **Set the end-card times:** the last three phrases are normally "Ctrl H", "Think Deeper", "Build Smarter". Use the start of the first one for `T_END`, then `TAG1` and `TAG2` for the other two, and the full audio length for `DUR`.
5. **Tune if needed:** if too many/few phrases are found, edit `thr` and `gap` in `segments()` inside `engine/align_vo.py`.

### The scene file in one minute

```python
DUR, T_END, TAG1, TAG2 = 124.76, 121.19, 122.49, 123.61   # audio length, end-card start, "Think Deeper" start, "Build Smarter" start
STAGES = ["Story", "Pessimistic", "Optimistic", "Summary"]  # top tabs (3-6 names)
TECH   = ["Laravel", "PostgreSQL", "MySQL"]                  # chips at the bottom
SC = [
  dict(style="classic", t0=0, t1=18.4, stage=0, head="Headline", head_t=0.2, blocks=[
      {"k": "shock", "t": 0.2, "lines": [("Big hook", 64, (255, 92, 92))]},
      c(3.5, "A card that appears at second 3.5"),
  ]),
  # ... one dict per scene
]
```

Each scene has a card `style` (`classic`, `proposed`, `glass`, `numbers`), a time window (`t0`, `t1`), a `stage` index and a headline. The `blocks` are what appears, each at its own time `t`. Common blocks: `card`, `chip`, `code` (typed lines, `focus`, `shake`), `flow`, `compare`, `counter`, `poll`, `predict`, `mystery`, `strike`, `ba` (before/after), `gain`, `note`, `shock`, `promise`, `challenge`, `chips`, `tiles`. See `examples/` for each one in use. The Subscribe (0:45) and Follow (40 s before the end) buttons and the end card are added automatically.

## 6. Using the skills with Claude

### Install

Copy the two folders inside `skills/` into your Claude skills directory:

`~/.claude/skills/`

(so you get `~/.claude/skills/ctrlh-video-style/SKILL.md` and `~/.claude/skills/ctrlh-thumbnail-style/SKILL.md`). Restart Claude Code. In other Claude apps that support skills, upload the folders as skills.

The skills cover the Ctrl + H video style, content creation, voiceover preparation, thumbnails, and production workflow.

### Use

Open Claude **inside this repo folder** (so it can run `engine/` and see `examples/` and `assets/`) and just ask in plain words. Claude loads the skill by itself when you mention a Ctrl + H video. Examples you can copy:

- `Write a post and a voiceover script about Laravel queues for the Ctrl + H channel.`
- `Here is my voiceover WAV for the queues video (queues_vo.wav) and the script. Build the video in 16:9 and 9:16 and a thumbnail.`
- `Only check frames at 10, 40 and 90 seconds, do not render the full video yet.`
- `Do not render any video, only update the engine / skill.`

Claude will follow the skill: segment the voice, map the script to the timings, write the scene file, check frames, render both formats, generate SFX, mux, and send the final files.

> The skill files describe the original channel (the owner's name, Egyptian Arabic replies, the Ctrl + H sign-off). If you use the kit for **your own** channel, open both `SKILL.md` files and change those lines first (see section 8).

## 7. Change colors, fonts and video size

These are set with environment variables (no code editing). Put them in front of any command:

| What                                           | Variable           | Example                                               |
| ---------------------------------------------- | ------------------ | ----------------------------------------------------- |
| Accent color (default orange `#FF8A11`)        | `CTRLH_ACCENT`     | `CTRLH_ACCENT=#00B8D9`                                |
| Arabic font file                               | `CTRLH_FONT_AR`    | `CTRLH_FONT_AR=/path/Tajawal-Bold.ttf`                |
| English / code font file                       | `CTRLH_FONT_LATIN` | `CTRLH_FONT_LATIN=/path/JetBrainsMono-Bold.ttf`       |
| Output width (height follows the aspect ratio) | `OUT_W`            | `OUT_W=1280` gives 1280x720 (16:9) or 720x1280 (9:16) |
| Background image                               | `BGFILE`           | `BGFILE=assets/backgrounds/bg_react.png`              |
| Assets folder (fonts, logo, monogram)          | `CTRLH_ASSETS`     | `CTRLH_ASSETS=/my/assets`                             |
| Subscribe / Follow time (seconds)              | `SUB_T`, `FOL_T`   | `SUB_T=30 FOL_T=100`                                  |

Examples:

```bash
# cyan brand + 1280x720 output
CTRLH_ACCENT=#00B8D9 OUT_W=1280 FMT=wide python3 lk_anim.py video v720.mp4

# 4K output
OUT_W=3840 FMT=wide python3 lk_anim.py video v4k.mp4

# a background in the same accent color
CTRLH_ACCENT=#00B8D9 python3 ../engine/ctrlh_bg.py react ../assets/backgrounds/bg_cyan.png ../assets/fonts/FiraCode-SemiBold.ttf
CTRLH_ACCENT=#00B8D9 BGFILE=../assets/backgrounds/bg_cyan.png FMT=wide python3 lk_anim.py video v.mp4
```

Notes:

- The layout is designed for **two shapes only**: 16:9 (1920x1080) and 9:16 (1080x1920). `OUT_W` rescales the finished video (sharper or smaller); it does not create other aspect ratios (1:1, 4:5 need new layout work).
- Fonts must be `.ttf` files. The Arabic font needs Arabic glyphs; the English/code font should be monospaced for the code cards.
- Colors other than the accent (background charcoal, white text, card color, green/red) are constants at the top of `engine/anim.py` (`INK`, `PAPER`, `CARDC`, `GRN`, `RED`).
- Your own logo: put `logo_ch.png` (square, shown on the end card) and `mono.png` (small corner monogram) in `assets/`. Without them a neutral placeholder frame is used. The original Ctrl + H logo and brand assets must retain their original proportions and appearance.

### What to tell Claude after you install the skills

Environment variables only affect the commands you run yourself. For Claude to **always** use your choices, tell it once and ask it to save them in the skill. Copy and edit:

- `From now on use accent color #00B8D9 for every video (set CTRLH_ACCENT and regenerate the backgrounds with it) and update the colors section of the skill.`
- `Use the fonts assets/fonts/Tajawal-Bold.ttf for Arabic and assets/fonts/JetBrainsMono-Bold.ttf for English (CTRLH_FONT_AR / CTRLH_FONT_LATIN) and update the fonts section of the skill.`
- `Render every video at 1280x720 and 720x1280 (OUT_W=1280 and OUT_W=720) and update the output section of the skill.`
- `My channel is called <Name> on <platforms>. Replace the Ctrl + H name, sign-off and platforms in both skills and in the end card.`
- `I added my logo (assets/logo_ch.png) and monogram (assets/mono.png). Check them in a frame at the end card.`

If you want a one-off change instead, say it for that video only (`For this video only use ...`).

## 8. Using it for your own channel

Replace the identity everywhere it appears. Checklist:

| Where                                   | What to change                                                                                                                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `assets/logo_ch.png`, `assets/mono.png` | your logo (end card) and corner monogram                                                                                                                                             |
| `skills/ctrlh-video-style/SKILL.md`     | owner, channel name, platforms, language, sign-off words ("Think Deeper." / "Build Smarter."), voice settings, logo description, "Ctrl H" spoken ending                              |
| `skills/ctrlh-thumbnail-style/SKILL.md` | channel name/logo, tagline, reference image description                                                                                                                              |
| End card text                           | no code edit needed: `CTRLH_SIGNOFF_1="Your line 1." CTRLH_SIGNOFF_2="Your line 2."` (also say these words at the end of your voiceover, and set `TAG1`/`TAG2` to when you say them) |
| Chapter banner and card labels          | `CTRLH_LABEL_CHAPTER` (default `الجزء`), `CTRLH_LABEL_OK` (`صح`), `CTRLH_LABEL_WRONG` (`غلط`); for other languages also change the headline text in your scene files                 |
| `SUBSCRIBE` / `FOLLOW` button labels    | fixed English text in `engine/anim.py` (search `SUBSCRIBE`)                                                                                                                          |
| `STAGES`, `TECH`, scene text            | live in your scene file                                                                                                                                                              |
| `engine/ctrlh_bg.py`                    | background motifs per technology (and the docstring name)                                                                                                                            |
| `README.md`, `SETTINGS.md`, `LICENSE`   | name, GitHub link, platforms, copyright line                                                                                                                                         |

Search the repo for leftovers before publishing:

```bash
grep -rniE "ctrl ?\+? ?h|ctrlh|hesham|think deeper|build smarter" --include="*.py" --include="*.md" --include="*.txt" .
```

Then pick your colors and fonts (section 7).

## Troubleshooting

| Problem                                        | Fix                                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Arabic letters look disconnected or reversed   | Pillow was built without RAQM. Install `libraqm` and reinstall Pillow                       |
| Squares (tofu) instead of Arabic text          | The English font is being used for Arabic. Set `CTRLH_FONT_AR` to a font with Arabic glyphs |
| Full render hits a time limit                  | Run it in the background (`nohup ... &`) and wait; ~3,800 frames take 6-10 min per format   |
| Video and audio lengths differ                 | Use `-t <DURATION>` in the mux command and make `DUR` equal the audio length                |
| `align_vo.py` finds too many / too few phrases | Edit `thr` (silence threshold, default -42 dB) and `gap` in `segments()`                    |

## License

- Code: MIT (see `LICENSE`; owner's decision, 2026-10-30).
- Fonts: SIL Open Font License.
- Ctrl + H name and logo: These are the channel owner's brand assets. Do not reuse them without permission.
