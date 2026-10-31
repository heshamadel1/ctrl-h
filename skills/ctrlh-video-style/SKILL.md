---
name: "ctrlh-video-style"
description: "Use for ALL Ctrl + H videos: branded 1920x1080 explainer videos synced to Hesham's Egyptian-Arabic voiceover WAVs, plus Reels, thumbnails and scripts."
---

# Ctrl + H video style (final, use for ALL videos)

Owner: Hesham (Egyptian Arabic, Alexandria). Owner GitHub: https://github.com/heshamadel1. Channel "Ctrl + H". Reply to him in Egyptian Arabic, short.

## Platforms (decided 2026-10-30)
- YouTube: ctrlh-dev
- TikTok
- Instagram
- Facebook
- Only these four platforms. Do not add other platforms unless he explicitly asks.

## Content Creation
- Dedicated to Ctrl + H content on Facebook, YouTube, TikTok and Instagram.
- Content: Programming, Software Engineering, Back-End Development. Language: Egyptian Arabic. Technical terms in English.
- Task: write a new post, or edit a post he gives, then prepare a voiceover script split into scenes with approximate timing.

## Voice Generator (his preferred settings)
- Tool: Google AI Studio, Gemini Flash TTS. Voice: Male. Script mode: Full Script. Language: Egyptian Arabic. Output: WAV.
- Model version: 3.8 (his own designation; verify the exact official model ID in Google AI Studio, never invent or silently change it).
- If the controls exist: start with Temperature 0.8; try 0.7-0.8 for natural variation.
- When writing a script for him, make it ready for this tool (copy-paste, Egyptian Arabic, English terms in English).

## Typical request flow
1. He sends a post (or just a topic); first write or edit the post (if asked) and the VOICEOVER SCRIPT (copy-paste ready, numbered scenes with rough timestamps or plain lines, English terms spelled in English, code spoken as words e.g. "Order all" not `Order::all()`, no emoji, hook in the first 5 s, question + comment CTA, ends with "Ctrl H. Think Deeper. Build Smarter."). Save batches of posts+scripts in one txt file and send it. Do NOT build the video before the audio exists.
2. He records it (Google AI Studio Gemini Flash TTS WAV, usually 24 kHz mono) and sends one or several WAVs; map each file to its post by file name; if unsure ask him to send them one by one. Then build each video once, synced to the audio.
3. Deliver each finished video TOGETHER with its thumbnail (see skill ctrlh-thumbnail-style) with SendUserFile (short caption with duration), then a short Egyptian-Arabic summary that LISTS which interactive features the video contains and at what times (he could not spot them otherwise). If he says to continue, keep going without asking again, including after a usage-limit reset.
4. NEW videos are delivered in BOTH 16:9 and 9:16 (decided 2026-10-29) unless he says otherwise. Do not render any video when he only asks for engine/skill changes or says not to (cheap checks: contact-sheet frames, or a 6 s test clip via clip.py).

## Output (always)
- 1920x1080 (16:9, 1080p), 30 fps, H.264 (libx264, crf 16-17, yuv420p, bt709 tv range), AAC 192k, plus the native 1080x1920 version for new videos.
- Video length = voiceover length exactly (mux with `-t <audio duration>`; no extra tail). No captions/subtitles in any video, ever.
- NEVER add an opening/title card (a card with the video title at the start) to any video or Reel (his rule, 2026-10-29). The first frame is already the hook scene.
- One idea per screen, hook first, CTA last ("اكتبلي إجابتك في الكومنتات" comment box, only when the script has that CTA), then the end card.
- Upload limit of SendUserFile is 30 MiB per file: a long 1080p video is normally fine (~15-27 MB per 2 min); if larger re-encode with a higher crf (26-28) or tell him.

## MOTION STYLE (v2 base + v3 + v4 + v5 features) - use for ALL NEW videos from 2026-10-29
Engine = `anim.py` (in the saved pipeline zip ctrlh_pipeline.zip, also published as the GitHub kit ctrlh-video-kit) + a per-video scene file (real examples `lk_scenes.py` = Locking video, `nx3_scenes.py` = Next.js; `v4_example_scenes.py`, `v3_example_scenes.py`, `v4_terminal_gain_scenes.py`, `w_scenes.py`, `v6_blocks_scenes.py` show the blocks): `FMT=wide|reel python3 <x>_anim.py video v.mp4` renders the SAME declarative scenes at 1920x1080 or native 1080x1920 (set `BGFILE=<bg png>`); `python3 <x>_anim.py frames <dir> <times...>` for contact-sheet checks (FMT=wide and FMT=reel); `python3 clip.py <t0> <t1> out.mp4` (with FMT) renders a short test clip; then mux (voice + SFX + mix2.txt, `-t DUR`). Generic SFX generator: `python3 make_audio.py <scenes.py> <out_sfx.wav>` derives distinct sounds from the scene blocks, the fixed buttons and the end card. ~3,800 frames take 6-10 min per format: start the render with nohup in the background and poll with sleep inside the same turn (a single foreground call can hit the 10 min limit).
- Scene = dict(style, t0, t1, stage, head, head_t, blocks=[...], optional grid="pairs"|"squares"|"tiles", cw (narrow card width fraction), dims=[times], reserve / reserve_reel (px kept free at the bottom for chips)). Blocks: card (ok True/False/None; `tag`, `key`, `size`, `words`=[(t, word)] to flash a word in orange exactly when it is spoken), chip, title, code (typed lines (start, text, cps[, color]); optional `focus`=[(t, line)] to light one line and dim the rest, `shake`=t to shake the box on an error), timeline, counter, zoom, phone, cta, row, compare, flow (nodes + animated steps), ring (countdown), tiles, the infographic blocks `icards` (numbered cards with animated icon + caption; icons shield/grid/bar/clock/lock/nodes/key/warn/check/db/bolt), `steplist` (step list + terminal showing the current step's commands; item lines (dt, text, cps[, cmd|out|ok|bad])) and `fixcards` (problem, chain of 3 chips, fix line; `chain`, `chain_t`, `fix`, `fix_t`) - use them for list topics like principles, N commands, mistakes and fixes (demo `v6_blocks_scenes.py`) - and four newer blocks (demo `v7_blocks_scenes.py`): `versus` (`cols`=[{t,name,sub,color "#RRGGBB",icon,code=[lines],bullets=[(t,text)]}]; per-column colours for comparisons like JSON vs XML vs YAML), `matrix` (`cols`=[{name,color}], `rows`=[{t,label,cells}] with cells "ok"|"bad"|"mid"|text|(kind, note)), `tabcard` (`title`, `tabs`=[{t,label,scene}], scene = play|rec|edit|script|an icon3d kind; a cursor presses each tab) and `icon3d` (`items`=[{t,kind,label}], kinds play camera scissors code doc db) - and the blocks below.
- CARD STYLES (four exist; the CHOICE belongs to whoever installed the kit): the engine default for a fresh install is ONE style, `classic`. The user may choose another one (`CTRLH_CARD_STYLES=glass`), a list (`classic,numbers`) or ALL four (`CTRLH_CARD_STYLES=all`, a different style per scene, varying between consecutive scenes). Scenes asking for a style that is not allowed rotate through the allowed ones. Also `CTRLH_CARD_COLOR=#RRGGBB` (card background; `numbers`/`glass` fills derive from it), `CTRLH_ACCENT=#RRGGBB` (accent) and `BGFILE=<png>` (background). Follow what the user says; use the defaults only when he gives no choice, and when he says to always use his choice, save it in this section. The four styles: (1) `classic` = neo-brutalist card (thick border, hard colored shadow, round check/cross badge); (2) `proposed` = dark card with colored status bar on the left edge, small orange English `tag` pill and the `key` word orange underlined; (3) `glass` = translucent warm-dark card with light border and sheen; (4) `numbers` = big faint index 01/02/03 on the right and a صح / غلط pill on the left (NO index numbers on square cards, only the small pill in the corner). When several styles are allowed pick by content: `numbers` for steps/mistakes lists, `proposed` for rules/definitions with a key term (always set tag and key), `classic` for good/bad statements, `glass` for calm explanatory or closing lines. Pictures of every style/shape/block: `docs/images/` in the kit.
- OWNER PROFILE (Hesham / Ctrl + H only; other users delete or replace this line): the owner's own channel uses ALL four card styles in every video, so for his videos always set `CTRLH_CARD_STYLES=all`.
- CARD SHAPES (decided 2026-10-30): the long full-width stacked card is NOT used in 16:9. Every scene with 2+ cards uses ONE of three shapes, rotating per scene (Video.__init__ assigns them automatically): (B) `squares` = equal squares side by side, (C) `pairs` = two columns, (D) `narrow` = single column 60% wide, centered (`cw=0.6`). Set `grid`/`cw` explicitly to override; `longcards=True` only if he asks for the old look. In 9:16 cards stack at full width. The first card is always top-aligned right under the headline (never vertically centered, so nothing jumps when later cards appear).
- BUTTONS (decided 2026-10-30, replaces the earlier per-scene rule): the engine adds them AUTOMATICALLY in every video, at FIXED times: Subscribe at 0:45 and Follow 40 s BEFORE the video ends, i.e. at DUR-40 (his rule 2026-10-30; 4.5 s each, env SUB_T/FOL_T to override; Follow is skipped if that falls before ~0:53), and scenes under them get `reserve` automatically. Do NOT put `button` blocks in scene files anymore. In the END CARD both buttons (static, gently pulsing) appear from the "Think Deeper" moment, bottom-right under the logo in 16:9 and bottom-centre in 9:16. Style: black body, ORANGE border/text, darker orange depth edge, NEVER green; press animation with cursor, SUBSCRIBED/FOLLOWING states, bell. SFX for them are generated by make_audio.py.
- INTERACTIVE FEATURES (decided 2026-10-29/30; he could not see them in a video that had few of them, so EVERY new video must include as many as fit the script, at least: a `shock` hook, a `promise` pill, one of `mystery`/`predict`, one `strike`, `code` with `focus` (and the terminal look + `shake` when there is an error/command), `challenge` when the script lists problems, `poll` at the end, `dims` before key words, `note` for a common mistake, `words` flashes on key cards, `gain` only when a real number exists, `chips` before the end): `shock` = big pop-in statement in the first ~3 s; progress-bar dots at every scene start with a pulse (automatic); `strike` = wrong statement with a red line, then the right one; `ba` = before/after code slider; abs `promise` = lock pill at the start unlocked at the answer time; distinct SFX per event type; automatic chapter banner "الجزء N · name" at every stage change (automatic); `mystery` = pulsing "?" card revealed at `t_reveal`; `predict` = code + question + 3 s countdown + answer pill; `poll` = two options to comment on (`nopct=True`, NEVER invent percentages); `gain` = before value counting to after value (only a number that is in the script or provable); abs `challenge` = countdown ring with a label; `note` = amber "لاحظ" card; abs `chips` = key words popping in a row (`items`,`t0`,`t1`, give the scene `reserve`); abs `corner` = fixed switch pill (`labels`, `switch` times; labels must be short); `dims`=[t] on a scene = darken the content ~1 s before the key word at t; a preview pill of the NEXT scene's headline slides in on the right edge 1.8 s before each scene end (automatic); entry direction rotates per scene (right, from below, left; automatic); SCENE LINK (automatic): an orange frame leaves the last card of a scene and lands where the first card of the next scene will appear; typed `code` with `focus` lights the line being spoken; terminal look = `code` with file "terminal". The old blinking hearts (`lives`) were REMOVED at his request: never use hearts.
- Camera/zoom: slow push-in on the content layer only, sub-pixel affine zoom anchored just under the headline (never an integer crop: it jitters; never from the screen centre: content slides up under the headline), settle 0.9 s on scene entry, pulse rings on card appear, double ring + tiny beat on key cards. Headline is on its own un-zoomed layer.
- Top stage-tabs bar: names and count (3-6) chosen PER VIDEO from the script structure; active tab orange, past outlined; thin orange progress bar with scene dots.
- ANIMATED BACKGROUND: static brand background plus `bg_motion` (drifting orange glows, light sweep near edges, twinkling dots); centre stays dark and calm. Same in 9:16.
- Transitions: layer-level slide + motion blur between scenes. Cards fade 0.12 s before the spoken word (E helper).
- Same brand rules (fonts, colors, floating monogram top-left, end card at T_END, Think Deeper / Build Smarter at their segment starts, no captions, no opening card). 9:16: tabs y 150, headline y 270, content y 360-1740, bigger fonts, native background, end logo y 520.
- Arabic rules apply (no parentheses next to Latin; "مع" not a standalone و next to Latin).
- Retention guidance (research 2026-10-30, unverified marketing statistics): first motion within ~1 s, hook under 3 s; text overlays <= ~5 words (mute-friendly); pattern interrupt roughly every 20-40 s but not constantly; open loop/promise early and pay it off; chapters (tabs); one comment prompt mid-video; vary hook formulas. Any numeric claim in a video must be provable from the script (no made-up poll percentages or gains).

## Reels / Shorts (9:16)
- Native motion (preferred): `FMT=reel` of the engine.
- Legacy proper: native re-design, one card at a time.
- Quick (old videos): the finished 16:9 scaled to 1080 wide over an animated 1080x1920 brand background loop (reel_bg_loop.mp4); ffmpeg: `-stream_loop -1 -i reel_bg_loop.mp4 -i video.mp4 -filter_complex "[1:v]scale=1080:-2[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[v]" -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 26 -r 30 -c:a copy -shortest -movflags +faststart out.mp4`. Instagram Reels max is 3 minutes: warn when longer.

## Logo and sign-off (fixed brand assets)
- Official logo = the image he sent (logo_ch.png: orange rounded C, white H, orange </> between them, wordmark "CTRL + H" white with orange +H, on black). Keep a copy in the work folder; he re-sends it if missing. Never redraw it.
- Floating monogram (mono.png) at the TOP-LEFT of EVERY video: position (40,32), height ~55 px, float ~6 px over a 4.5 s sine, soft orange glow pulse. Hidden during the end card.
- End card starts exactly when "Ctrl H" is spoken: full logo centered; under it Fira Code orange "Think Deeper." when spoken and "Build Smarter." when spoken, plus the Subscribe and Follow buttons (see BUTTONS). The last 3 audio segments are always Ctrl H / Think Deeper / Build Smarter. The old Arabic pill "تتعلم وتتطور" is retired.

## Fonts
- Arabic: **Cairo SemiBold**. Code/English/Latin: **Fira Code SemiBold**. He uploaded both; if missing ask him to re-attach.
- Fira has NO Arabic glyphs (tofu): any text with non-ASCII must use Cairo (`if text.isascii(): Fira else: Cairo`).
- PIL: ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM). Arabic draw: direction="rtl", language="ar".

## Colors
- Background charcoal (13,14,16) + orange glows + faint 96 px grid. Orange #FF8A11; ink (10,11,13); paper (245,245,245); card (24,26,31); gray text; green = correct; red = wrong; amber = TIP/note. Buttons: black + orange only.

## Backgrounds (same brand base, decorative motifs change per technology)
- Premium dark tech theme, minimalist, charcoal with subtle gradients, orange #FF8A00 accent, optional cyan only for React. Low-opacity grid, circuit traces, nodes, hexagons, soft orange corner light, vignette; centre clean; background only (no text/logos/code/UI).
- Per technology: React = component trees + cyan orbits; Next.js = server-rendering flow lines, routing; Docker = containers, pipeline; Laravel = PHP-syntax feel, MVC lines, DB motifs; Node/Express = server nodes, API paths; PostgreSQL/MySQL = DB cylinders; Redis = cache layers; Git = branches, commits; WordPress = block layout with WordPress/PHP/MySQL chips.
- Used so far: laravel, react, nextjs, wp, git, db (also Locking), docker, node/rest, redis.
- Generator: `python3 ctrlh_bg.py <tech> bg_<tech>.png FiraCode-SemiBold.ttf` (in the pipeline zip); techs: nextjs react laravel docker node rest db redis git wp. Each video loads its PNG via `BGFILE`.

## Voiceover sync workflow (cards never appear before their word)
1. Segment the WAV by silence (`align_vo.segments`, RMS 10 ms hops, threshold ~-42 dB, merge gaps < 0.14 s, drop < 0.12 s); phrase START times come from segment starts. Save `<n>_segs.txt` (`name duration count` + `start-end` pairs).
2. Transcribe PER SEGMENT with local Whisper-small int8 (sherpa-onnx, `bash run_asr7.sh <n>`; ~3 min per 2 min audio); text is only for order/wording. Run in the background with nohup and poll; a session restart kills background jobs.
3. Map the script line by line onto segments in order (about 7 syllables/s); flag guessed splits honestly (cards may be off by ~0.5 s).
4. `E(t, te, d)` = smoothstep(prog(t, te-0.12, te-0.12+min(d,0.3))). Key concepts appear at the start of the sentence.
5. Duration = audio duration; end card at the "Ctrl H" segment; comment CTA box between the question and the end card.

## Audio
- Voice: `aresample=48000,volume=3dB`, mono to stereo. NEVER loudnorm.
- SFX synthesized in numpy (make_audio.py: plucks/clicks, ding for right, thud for wrong, thump+ping for key cards, counter ticks, flow whooshes, promise chime, fixed Subscribe (0:45) / Follow (DUR-40) button sounds, end-card pings, alternating transition whooshes), ducked under the voice. Mix (mix2.txt): `[1:a]aresample=48000,volume=3dB,pan=stereo|c0=c0|c1=c0,asplit=2[v][vs];[2:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];[v][md]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.85:level=disabled,volume=0.8[a]`. Mux: `-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t <DUR>`.
- Verify audio by analysis only.

## Arabic/RTL rules (Pillow RAQM)
- NBSP between "الـ" and a following Latin word; no colon after a Latin word in RTL; prefer Arabic-first lines; Latin at the end of a sentence appears at the left, not a bug.
- No parentheses or `::` next to Latin (write "Cache remember"). No glued "و" before Latin (use "+", "أو", "مع").
- Avoid paths like "app/" in RTL cards; wrap Arabic with a width-based helper; code lines <= ~45 chars.
- Semi-transparent shapes on an RGBA layer REPLACE pixels: draw on a separate layer then alpha_composite.

## Pipeline
- Python 3.13 (tested version; 3.11/3.12 only syntax-checked), PIL (RAQM), numpy, ffmpeg; fork Pool(2) pipes rgb24 to ffmpeg (libx264 crf 17, bt709).
- Renders: nohup in the background + poll with sleep inside the same turn (a foreground call times out at 10 min and a finished turn kills background jobs). No pkill in the same shell.
- New video: copy `lk_scenes.py`/`lk_anim.py`, replace SC (timings from the segments file), STAGES, DUR, T_END, TAG1, TAG2, TECH; make sure the card styles follow the user's choice (default classic; owner: all four), the interactive-feature minimum, and no per-scene button blocks; check a contact sheet in BOTH FMT (overlaps, tofu, overflow, nothing under the headline) before the final render.
- Voiceover is NOT generated here. npm/pip registries are blocked; GitHub clone works. He decided to keep our own engine (HyperFrames, OpenMontage, Reel Studio, Graphify not needed).

## Content rules
- Verify technical facts from official docs before scripting; be accurate about versions and honest about limits.
- Review his post first and correct mistakes, then produce the video.
- Scenes structured and numbered; hook first; CTA last.

## Repository and license
- The kit is published on GitHub (owner heshamadel1) under the MIT license (owner's decision, 2026-10-30; see LICENSE). The Ctrl + H name and logo are not covered by it: do not reuse them without the owner's permission.
- Transcription (`run_asr.sh` / `asr_seg.py`) uses only `onnxruntime`, `scipy` and the sherpa-onnx Whisper-small MODEL FILES; the `sherpa-onnx` Python package is not needed (verified: it runs with the package not installed).

## Limits to state honestly
- No AI image/video generation here. Technology logos are not drawn from memory: name chips until he sends logo files.
- The pipeline lives only in the working session; a new chat needs him to re-attach ctrlh_pipeline.zip (anim.py, make_audio.py, scene examples, bg generator, align/ASR scripts) or clone the GitHub kit.
- Deliver files with SendUserFile and keep the final message short.