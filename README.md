# Ctrl + H Video Kit · v3.0.1

[![Release](https://img.shields.io/badge/release-v3.0.1-FF8A11)](RELEASE_NOTES.md)
[![Claude Free first](https://img.shields.io/badge/Claude-Free%20first-D97757)](docs/WORKFLOWS.md)
[![Advanced agents optional](https://img.shields.io/badge/advanced%20agents-optional-555555)](docs/WORKFLOWS.md#advanced-agent-workflow-optional)
[![Formats](https://img.shields.io/badge/formats-16%3A9%20%C2%B7%209%3A16-2b2b2b)](docs/PIPELINE.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Independent open-source project. Not affiliated with or endorsed by Anthropic or OpenAI.

Repository: **https://github.com/heshamadel1/ctrl-h** · **Watch what the kit does:** https://youtu.be/8sf53wNu3yo

A branded explainer-video pipeline plus Claude skills. Give it a voiceover WAV and a script; it renders a synced **Wide 16:9 (1920x1080)** or **Reel 9:16 (1080x1920)** video at 30 fps with a library of 35 sound effects, optional Arabic captions and an optional thumbnail. It started for the Ctrl + H programming channel and works for any channel: on first use Claude asks for your identity, colours, cards and background and saves them in `ctrlh.config.json`.

## Who it is for: Claude Free users first

**The Kit is designed first of all for regular Claude (Free) users.** The Standard Claude Workflow needs only a Claude chat, your script and your voiceover WAV. It does **not** need Claude Code, a terminal, local development tools, a paid subscription, an external agent, Whisper or any advanced tooling: Claude runs the Kit in its own workspace and hands you the finished video.

|                 | **Standard Claude Workflow** (primary)                                                                            | **Advanced Agent Workflow** (optional)                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| For             | Anyone using Claude in the app or on the web                                                                      | Developers using Claude Code, OpenAI Codex or another coding agent                           |
| You do          | Install the skill, send a script and a WAV, answer Claude's questions                                             | Same, and the agent can also run commands, tests and optional tools on your machine          |
| Needs           | A Claude chat that can use skills and run code (availability depends on your Claude plan and is set by Anthropic) | An agent environment with shell access                                                       |
| Optional extras | None                                                                                                              | Whisper alignment, `layout_check.py`, `storyboard.py validate`, golden tests, perf profiling |
| Output          | Identical                                                                                                         | Identical (an optional tool never changes how the video looks)                               |

Read [docs/WORKFLOWS.md](docs/WORKFLOWS.md) for the exact steps and the list of what is standard and what is advanced.

## How to start (Standard Claude Workflow)

1. Add the skills from `skills/` (`ctrlh-video-style`, and `ctrlh-thumbnail-style` if you want thumbnails) to your Claude, then attach this Kit (the ZIP) to the chat if Claude asks for it.
2. Send your script and your voiceover WAV (Arabic, English or mixed).
3. Answer Claude's questions (it asks every video): theme, size (Wide or Reel), captions, cards, background, sound effects, thumbnail.
4. Claude builds the video and sends it back. Ask for changes in plain words ("shorter cards", "make the reel version", "different transition").

## What you get

|                                     |                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **3 themes**                        | `orange` (dark), `paper_orange` (cream paper, thick borders), `soft_cream` (white rounded cards, soft shadow, orange glow)                                                                                                                                                                                                             |
| **25 backgrounds**                  | animated `hud_live`, 9 dark styles, `paper`, `cream`, 10 technology backgrounds (`tech:laravel`...), 3 ready images; picked per video                                                                                                                                                                                                  |
| **12 card styles + 55 block kinds** | cards, code, terminal, flow, architecture, ER, HTTP, diff, queue, polls, chat window, mini charts, counters                                                                                                                                                                                                                            |
| **35 sound effects**                | `assets/sfx`, placed automatically at 42% of the voice level or pinned by name                                                                                                                                                                                                                                                         |
| **Captions (optional)**             | Arabic in a box, orange highlight on key words and every English word                                                                                                                                                                                                                                                                  |
| **Two sizes**                       | 16:9 and 9:16, both native renders of one scene file                                                                                                                                                                                                                                                                                   |
| **One command**                     | `build.py`: lint, render, SFX, mux, `meta.md`, `chapters.txt`; long videos split into parts                                                                                                                                                                                                                                            |
| **Safety**                          | `lint.py` (layout, timing, logo, features), `check_voice.py` (WAV vs scene file), `smoke.py` (whole-kit test), `sfx_preview.py` (hear the sounds), all without rendering a video                                                                                                                                                       |
| **Clips**                           | `reels.py` cuts 30-60 s Reels/Shorts from a long video                                                                                                                                                                                                                                                                                 |
| **New in v3.0.1**                   | SFX at 42% of the voice with no ducking, error sounds on wrong cards, beam nodes that light up, living paper background, `align.py` fix, promise pill readable on light themes, storyboard accepts `promise`/button overlays, scene names with `.py`, `build.py --audio-only`, `valign`, `align.py --asr`. Earlier, **New in v3.0.0**: | scene transitions and camera moves, persistent entities, animated paths (`beam`), timeline block (`tracks`), audio events and loudness targets, render cache, storyboard JSON, two-format layout check ([RELEASE_NOTES.md](RELEASE_NOTES.md)) |
| **Skills**                          | `ctrlh-video-style` (asks before every video) and `ctrlh-thumbnail-style`                                                                                                                                                                                                                                                              |

## Quick start for developers (Advanced, optional)

Only if you want to run the Kit yourself. A regular Claude user does not need this section.

```bash
git clone https://github.com/heshamadel1/ctrl-h.git && cd ctrl-h
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cd examples && FMT=wide python3 ../engine/render.py template_howto_scenes frames /tmp/frames 30
python3 ../engine/build.py my_scenes --vo voice.wav --out out      # a full video
```

Needs Python 3.13, FFmpeg, Pillow with RAQM (installed for you in Claude's workspace; only developers install them locally). Details: [Getting started](docs/GETTING_STARTED.md).

## Documentation

| File                                                                                                     | Read it for                                                                |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [GETTING_STARTED.md](docs/GETTING_STARTED.md)                                                            | install, first frame, first video, Claude skills                           |
| [PIPELINE.md](docs/PIPELINE.md)                                                                          | the one workflow (automated and manual), CLI flags, SFX, captions, formats |
| [CONFIGURATION.md](docs/CONFIGURATION.md)                                                                | every config key / env variable, priority, themes, backgrounds             |
| [CATALOG.md](docs/CATALOG.md)                                                                            | every card, block, theme, background and sound by name and code            |
| [FEATURES.md](docs/FEATURES.md)                                                                          | every feature with a picture and its fields                                |
| [SOUNDS.md](docs/SOUNDS.md)                                                                              | the 35 sound effects                                                       |
| [CUSTOMIZE.md](docs/CUSTOMIZE.md)                                                                        | what to edit for what; using it for your own channel                       |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md)                                                                  | modules and data flow                                                      |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)                                                            | common errors and fixes                                                    |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md)                                                                  | how to contribute                                                          |
| [WORKFLOWS.md](docs/WORKFLOWS.md)                                                                        | Standard Claude vs Advanced agent workflow, optional tools                 |
| [STORYBOARD.md](docs/STORYBOARD.md), [LAYOUT.md](docs/LAYOUT.md)                                         | one JSON document for a whole video; Wide/Reel layout check                |
| [CHANGELOG.md](CHANGELOG.md), [RELEASE_NOTES.md](RELEASE_NOTES.md), [RELEASE_STEPS.md](RELEASE_STEPS.md) | versions and publishing                                                    |

## With Claude

Install `skills/ctrlh-video-style` (and `skills/ctrlh-thumbnail-style` for thumbnails), then send a script and a WAV. Claude asks, every video: theme, size (16:9 / 9:16), captions, cards, background, sound effects (specific names or automatic), thumbnail.

## License

Code: MIT ([LICENSE](LICENSE)). Fonts: SIL Open Font License. The Ctrl + H name and logo are the channel owner's brand assets; do not reuse them without permission.
