# Ctrl + H Video Kit

Repository: **https://github.com/heshamadel1/ctrl-h**

**Watch what the kit does:** https://youtu.be/8sf53wNu3yo

A branded explainer-video pipeline plus Claude skills. Give it a voiceover WAV and a declarative scene file; it renders a synced **16:9 (1920x1080)** or **9:16 (1080x1920)** video at 30 fps with a library of 34 sound effects, optional Arabic captions and an optional thumbnail. It started for the Ctrl + H programming channel and works for any channel: on first use Claude asks for your identity, colours, cards and background and saves them in `ctrlh.config.json`.

## What you get

|                                  |                                                                                                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **3 themes**                     | `orange` (dark), `paper_orange` (cream paper, thick borders), `soft_cream` (white rounded cards, soft shadow, orange glow)                                                       |
| **25 backgrounds**               | animated `hud_live`, 9 dark styles, `paper`, `cream`, 10 technology backgrounds (`tech:laravel`...), 3 ready images; picked per video                                            |
| **12 card styles + 100+ blocks** | cards, code, terminal, flow, architecture, ER, HTTP, diff, queue, polls, chat window, mini charts, counters                                                                      |
| **34 sound effects**             | `assets/sfx`, placed automatically at 30% under the voice or pinned by name                                                                                                      |
| **Captions (optional)**          | Arabic in a box, orange highlight on key words and every English word                                                                                                            |
| **Two sizes**                    | 16:9 and 9:16, both native renders of one scene file                                                                                                                             |
| **One command**                  | `build.py`: lint, render, SFX, mux, `meta.md`, `chapters.txt`; long videos split into parts                                                                                      |
| **Safety**                       | `lint.py` (layout, timing, logo, features), `check_voice.py` (WAV vs scene file), `smoke.py` (whole-kit test), `sfx_preview.py` (hear the sounds), all without rendering a video |
| **Clips**                        | `reels.py` cuts 30-60 s Reels/Shorts from a long video                                                                                                                           |
| **Skills**                       | `ctrlh-video-style` (asks before every video) and `ctrlh-thumbnail-style`                                                                                                        |

## Quick start

```bash
git clone https://github.com/heshamadel1/ctrl-h.git && cd ctrl-h
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cd examples && FMT=wide python3 ../engine/render.py template_howto_scenes frames /tmp/frames 30
python3 ../engine/build.py my_scenes --vo voice.wav --out out      # a full video
```

Needs Python 3.13, FFmpeg, Pillow with RAQM. Details: [Getting started](docs/GETTING_STARTED.md).

## Documentation

| File                                                                                                     | Read it for                                                                |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [GETTING_STARTED.md](docs/GETTING_STARTED.md)                                                            | install, first frame, first video, Claude skills                           |
| [PIPELINE.md](docs/PIPELINE.md)                                                                          | the one workflow (automated and manual), CLI flags, SFX, captions, formats |
| [CONFIGURATION.md](docs/CONFIGURATION.md)                                                                | every config key / env variable, priority, themes, backgrounds             |
| [CATALOG.md](docs/CATALOG.md)                                                                            | every card, block, theme, background and sound by name and code            |
| [FEATURES.md](docs/FEATURES.md)                                                                          | every feature with a picture and its fields                                |
| [SOUNDS.md](docs/SOUNDS.md)                                                                              | the 34 sound effects                                                       |
| [CUSTOMIZE.md](docs/CUSTOMIZE.md)                                                                        | what to edit for what; using it for your own channel                       |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md)                                                                  | modules and data flow                                                      |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)                                                            | common errors and fixes                                                    |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md)                                                                  | how to contribute                                                          |
| [CHANGELOG.md](CHANGELOG.md), [RELEASE_NOTES.md](RELEASE_NOTES.md), [RELEASE_STEPS.md](RELEASE_STEPS.md) | versions and publishing                                                    |

## With Claude

Install `skills/ctrlh-video-style` and `skills/ctrlh-thumbnail-style`, then send a script and a WAV. Claude asks, every video: theme, size (16:9 / 9:16), captions, cards, background, sound effects (specific names or automatic), thumbnail.

## License

Code: MIT ([LICENSE](LICENSE)). Fonts: SIL Open Font License. The Ctrl + H name and logo are the channel owner's brand assets; do not reuse them without permission.
