# Workflows: Standard Claude (primary) and Advanced Agent (optional)

Ctrl + H Video Kit is **designed first for regular Claude (Free) users**. Everything a normal user needs is in the Standard Claude Workflow. The Advanced Agent Workflow is an optional upgrade for people who work with Claude Code, OpenAI Codex or another coding agent. Both produce the same video; an optional tool never changes how the video looks.

## Standard Claude Workflow
**You need:** a Claude chat that can use skills and run code, your script, and your voiceover WAV. Whether your Claude plan offers skills and code execution is decided by Anthropic and can change; this Kit does not need anything beyond that.
**You do not need:** Claude Code, a terminal, local development tools, a paid subscription, an external agent, Whisper, or any developer tooling.

1. Add `skills/ctrlh-video-style` (and `skills/ctrlh-thumbnail-style` if you want thumbnails) to your Claude. If Claude asks for the Kit, attach the release ZIP to the chat.
2. First time only: Claude asks for your channel name, colours, cards and background and saves `ctrlh.config.json`.
3. Send the script and the voiceover WAV.
4. Claude asks (every video): theme, size (Wide 16:9 / Reel 9:16), captions (optional), cards, background, sound effects (by name or automatic), thumbnail (optional).
5. Claude lints, renders, adds sound, and sends the finished video. Ask for changes in plain words.

What Claude uses in its own workspace (you never run these): `build.py`, `lint.py`, `align.py` (default method: silence detection, no install), `check_voice.py`, `storyboard.py`, `layout_check.py`.

## Advanced Agent Workflow (optional)
For developers with shell access through Claude Code, OpenAI Codex or a similar agent. Extra things become possible:
- Run the Kit locally (`docs/GETTING_STARTED.md`): Python 3.13, FFmpeg, Pillow with RAQM.
- `python3 engine/storyboard.py validate story.json` in a loop, `python3 engine/layout_check.py scenes --fmt both` after every change.
- Whisper alignment: `align.py --whisper` / `asr_captions.py --whisper` (needs `faster-whisper` and a downloaded model).
- Developer-only tools in the source repository (not in the release ZIP): golden-frame tests, unit tests, performance profiling (`docs/TESTING.md`, `docs/PERFORMANCE.md`).

## What is standard and what is advanced
| Capability | Standard | Advanced |
|---|---|---|
| Render Wide and Reel, 3 themes, backgrounds, 55 block kinds | yes | yes |
| Sound effects, loudness target, captions from script | yes | yes |
| Transitions, camera, entities, paths, timeline, storyboard JSON | yes | yes |
| Timing from the script and WAV (`align.py`, silence method) | yes | yes |
| Whisper-based timing | no (never required) | optional |
| `layout_check.py`, `storyboard.py validate` | Claude runs them | you or the agent run them |
| Golden / unit tests, perf profiling | no (not shipped) | repository only |

## Rules the Skill follows for optional tools
1. Inspect what the environment offers before assuming anything.
2. Use an optional tool only when it gives a real benefit.
3. Install or download optional dependencies only if the environment allows it and the user agreed.
4. Never make an optional tool required for the Standard workflow.
5. If a tool is missing or fails, fall back to the standard method and say so.
6. An optional tool never silently changes the visual output or the project structure.
7. Do not assume every agent has the same tools, permissions or install methods.

## Whisper
Optional. Without it, `align.py` places each script line from silence detection and its share of the speech. With `--whisper`, word timestamps are used and any failure falls back to the silence method. The Whisper path was tested with a stand-in model only; a real model has not been run in the Kit's test environment.

## Compatibility status
Claude (Standard workflow): the intended primary use; the engine and skills are tested in a Claude workspace environment. Claude Code, Codex and other agents: the Kit is plain Python scripts plus Markdown instructions, so any agent that can run shell commands can use them; they are not tested one by one and no agent-specific behavior is promised.
