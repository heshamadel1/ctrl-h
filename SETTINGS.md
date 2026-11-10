# Settings and fixed rules

## Platforms

YouTube `ctrlh-dev`, TikTok, Instagram, Facebook. No others unless the owner asks.

## Content

Programming, Software Engineering, Back-End Development. Egyptian Arabic, technical terms in English.
Workflow: write or edit a post, then a voiceover script split into scenes with approximate timing.

## Voice generator

Google AI Studio, Gemini Flash TTS. Male voice, Full Script mode, Egyptian Arabic, WAV.
Model version: 3.8 (owner's designation; verify the exact official model ID in AI Studio).
Temperature: start 0.8, try 0.7-0.8.

## Video

- 1920x1080 (16:9) or 1080x1920 (9:16), native renders, 30 fps, H.264 + AAC 192k. Length = voiceover length. Captions optional (`engine/captions.py`, asked per video). No opening card.
- Floating monogram top-left, end card with logo at "Ctrl H", then "Think Deeper." and "Build Smarter." when spoken.
- Buttons (automatic): Subscribe at 0:45, Follow 40 s before the end; both static on the end card (bottom-right 16:9, bottom-centre 9:16). Black + orange, never green.
- Card styles (12 exist: plain_dark, tag_header, glass_blur, numbered_list, outline_thin, solid_orange, neon_glow, paper_note, soft_rounded, terminal_window, step_arrows, icon_box; old short names still work): a fresh install uses `plain_dark` only; choose with `card_styles` in ctrlh.config.json (one, a list, or `all`). Themes (`orange`, `paper_orange`, `soft_cream`), accent and background style are in the same file. Sounds: 34 in `assets/sfx` (see docs/SOUNDS.md). The owner (Ctrl + H) uses all. Shapes rotate (squares, pairs, narrow).
- Interactive features minimum per video: shock hook, promise, mystery/predict, strike, code focus, challenge, poll (no invented percentages), note, word glow, chips. No hearts.
- Fonts: Cairo SemiBold (Arabic), Fira Code SemiBold (Latin/code).
