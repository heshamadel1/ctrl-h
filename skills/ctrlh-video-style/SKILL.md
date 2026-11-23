---
name: "ctrlh-video-style"
description: "Make branded explainer videos (Wide 16:9 or Reel 9:16) synced to a voiceover WAV, in Arabic, English or mixed, with themes, cards, sound effects, optional captions and thumbnail. Designed first for regular Claude Free users: runs in Claude's own workspace, no Claude Code, terminal, paid plan or Whisper needed. Also works with Claude Code, Codex and other agents as an optional upgrade. Use for all Ctrl + H videos, Reels, thumbnails and scripts."
---

# Video style kit (Ctrl + H engine): branded explainer videos, 16:9 or 9:16 (asked per video), synced to a voiceover

Version 3.0.3. Project: https://github.com/heshamadel1/ctrl-h. The engine is generic: identity, colours, cards and background come from a brand profile (`ctrlh.config.json`). The Ctrl + H sections further down are the OWNER PROFILE (an example profile: `profiles/ctrlh.config.json`).

## WHO THIS IS FOR AND WHAT IS STANDARD (read first)
- **Primary audience: regular Claude Free users.** The Standard Claude Workflow must always work for them: the user sends a script and a voiceover WAV in a chat, answers your questions, and you run the kit in your own workspace and send the finished video. Never require, ask for or assume: Claude Code, a terminal on the user's machine, local installs, a paid plan, an external agent, Whisper, or any developer tool. Never describe the Free workflow as limited or secondary.
- **Standard capabilities (always):** lint, render Wide/Reel, sound effects, mux, captions from the script, `align.py` default timing (silence detection, no install), `storyboard.py`, `layout_check.py` (they are plain scripts you run yourself; the user never has to).
- **Advanced (optional, only when the environment supports it):** Claude Code, OpenAI Codex or other coding agents with shell access; Whisper alignment (`align.py --whisper`, `asr_captions.py --whisper`, needs `faster-whisper` and a model); golden tests, perf profiling (`tests/`, not shipped in the release zip).
- **Rules for optional tools:** (1) inspect what is available first (`which ffmpeg`, `python3 -c "import faster_whisper"`) instead of assuming; (2) use an optional tool only when it gives a real benefit (e.g. timing of a long, fast voiceover); (3) install or download anything only if the environment allows it AND the user said yes; (4) never make it a requirement; (5) if it is missing or fails, fall back to the standard method and say so in one line; (6) an optional tool must never change the visual design or the kit's structure; (7) do not assume another agent has the same tools, permissions or install methods.
- Full explanation: `docs/WORKFLOWS.md`.

## FIRST RUN SETUP (do this BEFORE anything else)
1. Look for `ctrlh.config.json` (kit root, current folder, or `$CTRLH_CONFIG`). If it exists, read it and use it for every video; never ask these questions again unless the user asks to change the look ("change my colours", "new background", "re-run setup").
2. If it does NOT exist and the user is not the owner (Hesham / Ctrl + H, who uses `profiles/ctrlh.config.json`): ask the setup questions below with AskUserQuestion (max 4 per call, show the preview pictures from `docs/images/` first: `cards-paper.png`, `backgrounds.png`, `cards-dark.png`), then save the answers by running `python3 engine/ctrlh_setup.py --yes --channel ... --theme ... --card-styles ... --bg-style ...` (add `--accent #RRGGBB --card-color #RRGGBB --bg-color #RRGGBB` for custom colours). Do not render a video before the setup is saved.
   - Q1 Identity: channel/brand name, handle, platforms, voiceover language, topics.
   - Q2 Colours: one of the 3 themes (`orange` dark, `paper_orange` light paper, `soft_cream` soft cream; all three are equal, none is the "main" or default theme: the owner decides every time) or a custom accent `#RRGGBB` (optionally card colour and background base colour).
   - Q3 Cards: which card styles to use: ONE, SEVERAL or `all` of the 12 named looks (plain_dark, tag_header, glass_blur, numbered_list, outline_thin, solid_orange, neon_glow, paper_note, soft_rounded, terminal_window, step_arrows, icon_box; old short names still work)
   - Q4 Background: hud_live (animated, default of the `orange` theme), paper, circuit, grid, hex, dots, waves, aurora, blueprint, terminal, minimal (or his own PNG in `assets/backgrounds/`, set as `background_file`).
   - Q5 Brand assets: logo (`assets/logo_ch.png`, shown on the end card) and monogram (`assets/mono.png`, top-left); fonts (Arabic and Latin `.ttf`; defaults Cairo + Fira Code); end-card lines (default "Think Deeper." / "Build Smarter.").
   Then render the 6 s preview (`examples/cards_anim.py frames`) so the user SEES the result and can adjust before the first real video.
3. Everything in the config can be changed later by chat ("use only glass and neon cards", "switch to the cyan theme", "background hex"): edit `ctrlh.config.json` (or rerun `ctrlh_setup.py`) and tell the user what changed. Environment variables (`CTRLH_THEME`, `CTRLH_ACCENT`, `CTRLH_CARD_COLOR`, `CTRLH_BG_COLOR`, `CTRLH_CARD_STYLES`, `CTRLH_BG_STYLE`, `BGFILE`) override the config for one command.
4. Keys of `ctrlh.config.json`: `channel_name`, `handle`, `platforms`, `language`, `topics`, `theme`, `accent`, `card_color`, `bg_color`, `card_styles`, `bg_style`, `background_file`, `font_ar`, `font_latin`, `signoff_1`, `signoff_2`, `label_ok`, `label_wrong`, `label_chapter`, `out_w`, `subscribe_t`, `follow_t`.

## OWNER PROFILE: Ctrl + H (Hesham)
Owner: Hesham (Egyptian Arabic, Alexandria). Owner GitHub: https://github.com/heshamadel1. Channel "Ctrl + H". Reply to him in Egyptian Arabic, short. His own profile uses theme orange, ALL card styles, background hud_live (default; the choice is asked per video) (`profiles/ctrlh.config.json`). Other users: replace or delete this whole owner profile (platforms, content, voice, flow) with their own from the config.

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
0. QUESTIONS BEFORE EVERY VIDEO (owner, 2026-11-08, MANDATORY; never decide alone, never skip, even if he answered in an earlier video). Whenever he sends material (script, WAV, post, topic) ask, with AskUserQuestion (max 4 per call, so two calls, or plain text if the tool is absent), and do not start building until he answers:
   1. THEME (one of 3): `orange` (dark, accent #FF8A11), `paper_orange` (cream paper, thick black borders, hard shadows, orange highlighter), `soft_cream` (white rounded cards, soft shadow, cream background with orange glow, dark H logo, soft buttons/end card). Only these 3 exist.
   2. SIZE: 16:9 (1920x1080) or 9:16 (1080x1920). Both are native renders (`FMT=wide` / `FMT=reel`), never a crop.
   3. CAPTIONS (optional): yes or no. If yes: Arabic text in a rounded box (theme colours), orange highlighter on the key words (`[[word]]`), and EVERY English word spoken in the voice highlighted in orange (`engine/captions.py`). If no: no captions.
   4. CARDS: (a) all card types, I choose per script, (b) ONE basic card look for the whole video (name from `docs/CATALOG.md` group A, set `card_style`), (c) only certain families (A-H; turn the others off with `disabled_blocks`). If (a), pick the blocks that fit each sentence and say in one line which you used.
   5. BACKGROUND (optional, pick ONE): `hud_live`, circuit, grid, hex, dots, waves, aurora, blueprint, terminal, minimal, paper, cream, `tech:<name>` (nextjs react laravel wp docker node rest db redis git; 16:9 only), or an image (`default`, `hud_dark`, `hud_plate`); show `docs/images/backgrounds.png` first. "Theme default" is a valid answer (orange -> hud_live, paper_orange -> paper, soft_cream -> cream). Set `bg_style` (add `bg_style_locked` when it differs from the theme default).
   6. SOUND EFFECTS: either he names specific sounds for specific moments (file names or `category_NN` from `docs/SOUNDS.md`, e.g. "at the reveal use impact_01", written as `SFX = [(t, "impact_01")]`), or Claude chooses by the video (automatic: 42% of the voice level, no ducking, varied, no back-to-back repeats). If he names only some, the rest is automatic unless he says `SFX_AUTO = False`.
   7. THUMBNAIL (optional): yes or no (skill ctrlh-thumbnail-style). Playlist cover only when asked.
   Plus the older questions of the first-run setup if there is no `ctrlh.config.json`. Never remake an already delivered video unless he asks.
1. He sends a post (or just a topic); first write or edit the post (if asked) and the VOICEOVER SCRIPT (copy-paste ready, numbered scenes with rough timestamps or plain lines, English terms spelled in English, code spoken as words e.g. "Order all" not `Order::all()`, no emoji, hook in the first 5 s, question + comment CTA, ends with "Ctrl H. Think Deeper. Build Smarter."). Save batches of posts+scripts in one txt file and send it. Do NOT build the video before the audio exists.
1b. Optional helpers: `engine/suggest.py` (scene ideas from the script), `engine/align.py` (times from the WAV), `engine/preview.py` (fast key frames), `engine/srt.py` (subtitles); `build.py` also writes `chapters.txt`. Full list of names and codes: `docs/CATALOG.md`.
2. He records it (Google AI Studio Gemini Flash TTS WAV, usually 24 kHz mono) and sends one or several WAVs; map each file to its post by file name; if unsure ask him to send them one by one. Then build each video once, synced to the audio.
3. Deliver each finished video TOGETHER with its thumbnail (see skill ctrlh-thumbnail-style) with SendUserFile (short caption with duration), then a short Egyptian-Arabic summary that LISTS which interactive features the video contains and at what times (he could not spot them otherwise). If he says to continue, keep going without asking again, including after a usage-limit reset.
4. SIZE is asked per video (owner, 2026-11-08, replaces the 16:9-only rule): 16:9 or 9:16, only what he chooses is rendered (both if he says both). Ask before dropping any other deliverable. Do not render any video when he only asks for engine/skill changes or says not to (cheap checks: contact-sheet frames, or a 6 s test clip via clip.py).

## THEMES AND CAPTIONS: OWNER RULES (2026-11-10)
- THEME RULE (owner, 2026-11-15): for the OWNER's own videos (Hesham, Ctrl + H) use `paper_orange` without asking. For ANY OTHER person using this skill, ALWAYS ask which theme (orange, paper_orange or soft_cream) before making a video and never assume one for them. He can also ask for ALL 3 themes inside one video: put `theme="orange"|"paper_orange"|"soft_cream"` on each scene dict (`build.py` renders every run of same-theme scenes separately and joins them; the voice and SFX run across).
- Captions can be delivered as a SUBTITLE FILE instead of burned in: write the tab-separated cues (`start<TAB>end<TAB>text`, text taken from the actual voice, not the post) and run `python3 engine/cues2srt.py cues.txt out.srt`. When he says "no captions / use a translation file", deliver the video without burned captions plus the .srt.

## THEMES ARE HIS CHOICE (owner, 2026-11-10)
Theme: the owner (Hesham) always uses `paper_orange`, no theme question. Anyone else: ask question 1 (theme) every video with the 3 options; they can say "use all 3".
- One video can use several themes: put `theme="orange"|"paper_orange"|"soft_cream"` on each scene dict; `build.py` renders each run of same-theme scenes separately and joins them (cut at scene boundaries, ideally at a stage change).
- Subtitles can be delivered as a subtitle FILE (.srt from `engine/cues2srt.py`) instead of burned-in captions whenever he says "ملف ترجمة" / "no captions"; build the cues from the actual voice.

## SYSTEM DIAGRAM BLOCK `sysdiagram` (2026-11-11): for System Design explainers
One stateful diagram that stays on screen and changes in stages (no cuts): nodes with state outlines and badges, status pills, a DB table group (orders / outbox rows), BEGIN / COMMIT / ROLLBACK pills, lock selection, travelling envelopes, ✓ ledger chips, tilted stickers, and a stage pill ("3/5 OUTBOX TABLE"). Use it for Transactional Outbox, retry + dedupe, saga, cache invalidation, any "what fails at each step" story. Fields: docs/FEATURES.md ("sysdiagram"); demo: `examples/sysdiagram_demo_scenes.py`. Sounds are automatic (`sd_stage sd_tick sd_ok sd_err sd_env sd_sticker sd_done`). One `sysdiagram` per scene, give it nearly the whole scene (`h`), write one stage per narrated idea with `resets` at the stage changes, and use Latin node names. It counts as one block kind for the variety rules, so combine it with other kinds in the other scenes.

## VARIETY RULES (owner, 2026-11-09, MANDATORY: never reuse the same cards/blocks every video; try new things each time)
1. Every video uses at least 8 different block kinds; no kind appears in two consecutive scenes; the card style changes between scenes.
2. Choose blocks per script sentence (comparison -> versus/compare, steps -> steplist, number -> big number/stat, flow -> flow blocks, warning -> alert, code -> code/terminal, dialogue -> chat), never start from the same template.
3. If he forces kinds in question 4 (cards), use exactly those; otherwise "Claude chooses" means varied choice under rules 1-2.
4. Try new things: each video must include at least 3 block kinds NOT used in his previous video (see its `*_scenes_meta.md`), and say in one line which new ones you tried.
`engine/lint.py` warns (`LINT: variety: ...`) on fewer than 8 kinds and on identical neighbouring scenes.

## LAYOUT AND QUALITY RULES (decided 2026-11-03, he found these errors in V2 videos: never repeat them)
1. Text must always stay INSIDE its card, sized to fit. The engine wraps every card line (Latin-only text too) with the real font widths and shrinks a too-wide word (min 26 px). Still check every frame; if a card looks cramped, shorten the sentence.
2. Nothing may go below the video frame or into the Subscribe/Follow zone: when a scene is too tall the engine squeezes it into the free area and prints `LINT: scene N ... squeezed to X%`. If X is below ~80 split the scene in two (or use fewer cards/blocks); never ignore a LINT line.
3. Subscribe and Follow times are FREE per video: set `SUB_T = 52.0` and/or `FOL_T = 80.0` in the scene file (seconds; `False` = no such button); the defaults are 45 s and DUR-40. Choose a moment when the screen is light (not on a full scene), and never at the same time as bottom `chips`; the engine reserves 200 px at the bottom of every scene that overlaps a button.
4. Word-flash highlights on solid/paper cards are opaque now (no dark rectangle over the word). If any dark mark ever appears over a word, treat it as a bug and fix it before rendering.
5. Numbers on screen (counter, "N decisions", headline) must equal what the voiceover says at that moment: "3 questions" shows 3, not the total of the video. Count the script, never invent or round.
6. Code blocks and bottom chips are Latin only (Fira has no Arabic: Arabic shows as boxes); write Arabic in cards/bullets instead.
7. Before every render make a contact sheet (FMT=wide `frames`, at each scene's end minus ~1.3 s = busiest moment) of EVERY scene and check: text inside cards, nothing cut at the bottom, no overlap with buttons, no boxes (tofu), no dark marks, numbers correct. Read the `LINT:` lines the frames command prints (squeezed scenes, chips over buttons, a counter that disagrees with the number words in the scene text) and fix them first.
8. Each series gets a playlist cover (1280x720, made with the thumbnail generator) delivered with its first batch; every video is delivered with its own thumbnail.
9. MANDATORY in every new video (owner's request 2026-11-05): before writing the scene file, make the storyboard table (script line -> visual) and use the engine's technical blocks wherever the script content fits: `arch` or `er` for services, request paths and database tables (Multi-Tenant, relations), `http` for endpoints, status codes and API errors, `diff` for a wrong-vs-right code fix, `split` (+ `titlevs`) for two systems compared on scaling / deploy / calls, `chain` for handlers and middleware, `hub` for one controller touching many services, `pipeline` for ordered steps, `deviceflow` for a request passing checks, `codeann` for code with several problems, `flowmini` for Command -> Message -> Handler, `queue` for background jobs, `recap` as the last content scene when the script has a summary, and `code` with `focus: "auto"`. A video about backend topics with none of these blocks is a miss: say in the final summary which block is at which time, and which were not used and why. Always deliver `meta.py` output (chapters, description, hashtags) with the video.
10. LONG VOICEOVERS (owner, 2026-11-05): if the voiceover is longer than ~3 minutes (Instagram Reels limit, and render time), split it into 2 parts at a section boundary (cut inside a silence between two phrases) and deliver each part as its own file in each format; the owner merges them. Part 1 has NO end card (`T_END` far beyond `DUR`, e.g. DUR + 230), carries `SUB_T`, and `FOL_T = False`; the last part has the end card and the Follow button. Write every time of part 2 as (full time - cut time) with a helper. Cut the voice with `ffmpeg -ss <cut> / -t <cut>`, build the SFX per part, and give him ONE merged-video chapter list (`meta.py` per part, then add the cut time to part 2). Chapter banners read "N of M" per part.
11. Headlines and cards: do not put the Arabic letter waw alone between Latin words (it looks like the letter g): use "+" or "مقابل". `versus` icons: "doc" draws a document, any other string is printed as text (use short symbols such as "||", "->", "{}"); never a word like "bolt".

## Output (always)
- 1920x1080 (16:9, 1080p), 30 fps, H.264 (libx264, crf 16-17, yuv420p, bt709 tv range), AAC 192k, or native 1080x1920 when he chooses 9:16.
- Video length = voiceover length exactly (mux with `-t <audio duration>`; no extra tail). Captions are OPTIONAL and asked per video (owner, 2026-11-08): Arabic in a box with orange highlighter on key words and on every English word (`engine/captions.py`); without his yes, no captions.
- NEVER add an opening/title card (a card with the video title at the start) to any video or Reel (his rule, 2026-10-29). The first frame is already the hook scene.
- One idea per screen, hook first, CTA last ("اكتبلي إجابتك في الكومنتات" comment box, only when the script has that CTA), then the end card.
- Upload limit of SendUserFile is 30 MiB per file: a long 1080p video is normally fine (~15-27 MB per 2 min); if larger re-encode with a higher crf (26-28) or tell him.

## MOTION STYLE (v2 base + v3 + v4 + v5 features) - use for ALL NEW videos from 2026-10-29
Engine = `anim.py` (in the saved pipeline zip ctrlh_pipeline.zip, also published as the GitHub kit ctrlh-video-kit) + a per-video scene file (real examples `lk_scenes.py` = Locking video, `nx3_scenes.py` = Next.js; `v4_example_scenes.py`, `v3_example_scenes.py`, `v4_terminal_gain_scenes.py`, `w_scenes.py`, `v6_blocks_scenes.py`, `v7_blocks_scenes.py`, `showcase_scenes.py` show the blocks): `FMT=wide|reel python3 <x>_anim.py video v.mp4` renders the SAME declarative scenes at 1920x1080 or native 1080x1920 (set `BGFILE=<bg png>`); `python3 <x>_anim.py frames <dir> <times...>` for contact-sheet checks (FMT=wide and FMT=reel); `python3 clip.py <t0> <t1> out.mp4` (with FMT) renders a short test clip; then mux (voice + SFX + mix2.txt, `-t DUR`). Generic SFX generator: `python3 make_audio.py <scenes.py> <out_sfx.wav>` derives distinct sounds from the scene blocks, the fixed buttons and the end card. ~3,800 frames take 6-10 min per format: start the render with nohup in the background and poll with sleep inside the same turn (a single foreground call can hit the 10 min limit).
- Scene = dict(style, t0, t1, stage, head, head_t, blocks=[...], optional grid="pairs"|"squares"|"tiles", cw (narrow card width fraction), reserve / reserve_reel (px kept free at the bottom for chips)). Blocks: card (ok True/False/None; `tag`, `key`, `size`, `words`=[(t, word)] to flash a word in orange exactly when it is spoken), chip, title, code (typed lines (start, text, cps[, color]); optional `focus`=[(t, line)] to light one line and dim the rest, `shake`=t to shake the box on an error), timeline, counter, zoom, phone, cta, row, compare, flow (nodes + animated steps), ring (countdown), tiles, the infographic blocks `icards` (numbered cards with animated icon + caption; icons shield/grid/bar/clock/lock/nodes/key/warn/check/db/bolt), `steplist` (step list + terminal showing the current step's commands; item lines (dt, text, cps[, cmd|out|ok|bad])) and `fixcards` (problem, chain of 3 chips, fix line; `chain`, `chain_t`, `fix`, `fix_t`) - use them for list topics like principles, N commands, mistakes and fixes (demo `v6_blocks_scenes.py`) - and four newer blocks (demo `v7_blocks_scenes.py`): `versus` (`cols`=[{t,name,sub,color "#RRGGBB",icon,code=[lines],bullets=[(t,text)]}]; per-column colours for comparisons like JSON vs XML vs YAML), `matrix` (`cols`=[{name,color}], `rows`=[{t,label,cells}] with cells "ok"|"bad"|"mid"|text|(kind, note)), `tabcard` (`title`, `tabs`=[{t,label,scene}], scene = play|rec|edit|script|an icon3d kind; a cursor presses each tab) and `icon3d` (`items`=[{t,kind,label}], kinds play camera scissors code doc db) - and the blocks below.
- CARD STYLES (twelve exist; the CHOICE belongs to whoever installed the kit, taken from `card_styles` in the config): a fresh install with no preference uses ONE style, `plain_dark`. Use the descriptive names (`glass_blur`, `neon_glow`, ...; the old short names still work). To use ONE card type for the WHOLE video set `card_style: "glass_blur"` in the config (or `CTRLH_CARD_STYLES=glass_blur`). The user may choose one (`glass_blur`), several (`plain_dark,neon_glow`) or ALL twelve (`all`, a different style per scene, varying between consecutive scenes). Scenes asking for a style that is not allowed rotate through the allowed ones. Colours: `theme` (`orange`, `paper_orange`) or `accent`/`card_color`/`bg_color` as `#RRGGBB`; background: `bg_style` or `background_file`. Follow what the user says; when he says to always use his choice, save it in the config. The styles: (1) `classic` = neo-brutalist card (thick border, hard colored shadow, round check/cross badge); (2) `proposed` = dark card with colored status bar on the left edge, small accent English `tag` pill and the `key` word underlined; (3) `glass` = translucent card with light border and sheen; (4) `numbers` = big faint index 01/02/03 on the right and a right/wrong pill on the left (NO index numbers on square cards); (5) `outline` = thin accent outline, nearly transparent fill, calm; (6) `solid` = filled with the accent colour, dark text; (7) `neon` = glowing accent border; (8) `paper` = light card with dark text, high contrast; (9) `soft` = status-colour thin border with soft glow and a round badge; (10) `terminal` = terminal line with `exit 0`/`exit 1` label and `$`; (11) `steps` = numbered circle on the edge with a progress underline; (12) `iconbox` = coloured block with a check/cross (or number) beside the text. When several styles are allowed pick by content: `numbers` for steps/mistakes lists, `proposed` for rules/definitions with a key term (always set tag and key), `classic` or `neon` for good/bad statements, `glass`/`outline` for calm explanatory lines, `solid`/`paper` to emphasise one key statement, `terminal` for commands and results, `steps` for ordered steps, `iconbox` or `soft` for right/wrong lists. Pictures: `docs/images/cards-12-styles-*.png`.
- CARD SHAPES (decided 2026-10-30): the long full-width stacked card is NOT used in 16:9. Every scene with 2+ cards uses ONE of three shapes, rotating per scene (Video.__init__ assigns them automatically): (B) `squares` = equal squares side by side, (C) `pairs` = two columns, (D) `narrow` = single column 60% wide, centered (`cw=0.6`). Set `grid`/`cw` explicitly to override; `longcards=True` only if he asks for the old look. In 9:16 cards stack at full width. The first card is always top-aligned right under the headline (never vertically centered, so nothing jumps when later cards appear).
- BUTTONS (decided 2026-10-30, replaces the earlier per-scene rule): the engine adds them AUTOMATICALLY in every video, at FIXED times: Subscribe at 0:45 and Follow 40 s BEFORE the video ends, i.e. at DUR-40 (his rule 2026-10-30; 4.5 s each, env SUB_T/FOL_T or `SUB_T`/`FOL_T` in the scene file to override; Follow is skipped if that falls before ~0:53), and scenes under them get `reserve` automatically. Do NOT put `button` blocks in scene files anymore. In the END CARD both buttons (static, gently pulsing) appear from the "Think Deeper" moment, bottom-right under the logo in 16:9 and bottom-centre in 9:16. Style: black body, ACCENT-colour border/text (orange in the default theme), darker depth edge, NEVER green; press animation with cursor, SUBSCRIBED/FOLLOWING states, bell. SFX for them are generated by make_audio.py.
- INTERACTIVE FEATURES (decided 2026-10-29/30; he could not see them in a video that had few of them, so EVERY new video must include as many as fit the script, at least: the technical blocks of layout rule 9 where they fit, a `shock` hook, a `promise` pill, one of `mystery`/`predict`, one `strike`, `code` with `focus` (and the terminal look + `shake` when there is an error/command), `challenge` when the script lists problems, `poll` at the end, `note` for a common mistake, `words` flashes on key cards, `gain` only when a real number exists, `chips` before the end): `shock` = big pop-in statement in the first ~3 s; progress-bar dots at every scene start with a pulse (automatic); `strike` = wrong statement with a red line, then the right one; `ba` = before/after code slider; abs `promise` = lock pill at the start unlocked at the answer time; distinct SFX per event type; automatic chapter banner "الجزء N · name" at every stage change (automatic); `mystery` = pulsing "?" card revealed at `t_reveal`; `predict` = code + question + 3 s countdown + answer pill; `poll` = two options to comment on (`nopct=True`, NEVER invent percentages); `gain` = before value counting to after value (only a number that is in the script or provable); abs `challenge` = countdown ring with a label; `note` = amber "لاحظ" card; abs `chips` = key words popping in a row (`items`,`t0`,`t1`, give the scene `reserve`); abs `corner` = fixed switch pill (`labels`, `switch` times; labels must be short); `dims` is DISABLED (it made the screen look like it turned off and on; do NOT use it, the engine ignores it unless CTRLH_DIMS=1); a preview pill of the NEXT scene's headline slides in on the right edge 1.8 s before each scene end (automatic); entry direction rotates per scene (right, from below, left; automatic); SCENE LINK (automatic): an accent-colour frame leaves the last card of a scene and lands where the first card of the next scene will appear; typed `code` with `focus` lights the line being spoken; terminal look = `code` with file "terminal". The old blinking hearts (`lives`) were REMOVED at his request: never use hearts.
- Camera/zoom: slow push-in on the content layer only, sub-pixel affine zoom anchored just under the headline (never an integer crop: it jitters; never from the screen centre: content slides up under the headline), settle 0.9 s on scene entry, pulse rings on card appear, double ring + tiny beat on key cards. Headline is on its own un-zoomed layer.
- Top stage-tabs bar: names and count (3-6) chosen PER VIDEO from the script structure; active tab in the accent colour, past outlined; thin progress bar with scene dots.
- ANIMATED BACKGROUND: static brand background plus `bg_motion` (drifting accent glows, light sweep near edges, twinkling dots); centre stays dark and calm. Same in 9:16.
- Transitions: layer-level slide + motion blur between scenes. Cards fade 0.12 s before the spoken word (E helper).
- Same brand rules (fonts, colors, floating monogram top-left, end card at T_END, Think Deeper / Build Smarter at their segment starts, captions only when he says yes, no opening card). 9:16: tabs y 150, headline y 270, content y 360-1740, bigger fonts, native background, end logo y 520.
- Arabic rules apply (no parentheses next to Latin; "مع" not a standalone و next to Latin).
- Retention guidance (research 2026-10-30, unverified marketing statistics): first motion within ~1 s, hook under 3 s; text overlays <= ~5 words (mute-friendly); pattern interrupt roughly every 20-40 s but not constantly; open loop/promise early and pay it off; chapters (tabs); one comment prompt mid-video; vary hook formulas. Any numeric claim in a video must be provable from the script (no made-up poll percentages or gains).

## BUILD TOOLS (v2.1.0): use them for every video
- `python3 engine/lint.py <scenes> --strict --sheet sheet.png` (run from the scene file's folder) BEFORE any render: LINT lines, timing gaps, features the `video_type` expects (`profiles/video-types.json`), contact sheet (look at it). Fix everything it prints, or say why a feature does not fit the script.
- `python3 engine/build.py <scenes> --vo voice.wav [--formats wide,reel]`: lint, sheet, split plan, render with the per-scene cache, SFX, voice cut (atrim), mux, meta. Formats: render exactly the size(s) he chose for this video (`--formats wide`, `reel` or `wide,reel`). Long videos are split at scene boundaries (config `max_part_seconds`, default 180) from ONE scene file (frame times stay global; no manual time shifting). Part 1 has no end card, the last part has it.
- Editing one scene and rebuilding re-renders only the touched scenes (cache `.ctrlh_cache`). Short test: `CTRLH_T0=10 CTRLH_T1=20 python3 engine/render.py <scenes> test.mp4`.
- Config keys: `formats, video_type, max_part_seconds, disabled_blocks, dims, workers`. `dims` is OFF (it looked like the screen turning off): never use it.
- Docs for the owner and for you: `docs/FEATURES.md` (every feature with a picture), `docs/CUSTOMIZE.md` (what to edit to change anything). Redraw pictures with `python3 engine/docs_gallery.py`.

## TECHNICAL BLOCKS, TOKENS, PLANNING, META
- New blocks (demo `examples/v8_blocks_scenes.py`; all text inside `er`, `http`, `diff`, `queue` must be Latin, the engine prints a LINT line otherwise): `er` (tables=[{t,name,color,cols:[(name,'PK'|'FK'|'')]}], links=[(t, from_table, to_table, 'fk_col')]: FK lines drawn under the tables), `http` (method, url, req=[(dt,line)], t_resp, status, status_text, res=[(dt,line)]: request panel, response panel coloured by status code, a dot travels between them), `diff` (lines=[(t,'-'|'+'|' ',text[,t_gone])]), `queue` (jobs=[{name,t_in,t_start,t_done}], worker, queue_name, done_name), `recap` (items=[(t,text)], optional title; Arabic allowed) and `arch` (nodes + reqs, already existed). Use `er`/`arch` for Multi-Tenant, `http` for endpoints and login errors, `diff` for before/after fixes, `queue` for background jobs, `recap` as the last scene before the end card.
- `code` blocks accept `"focus": "auto"`: each line lights up when it starts typing.
- The chapter banner now reads "الجزء N من M · name".
- Design tokens (`engine/tokens.py`: spacing, radius, safe margins, text hierarchy; override with a JSON file via `CTRLH_TOKENS`) are used by the new blocks; older blocks are not migrated yet.
- Planning step (`engine/plan.py <lines.txt> plan.md`): a DRAFT table "line -> suggested visual". It is only a keyword heuristic and was weak on noisy ASR text: Claude should write the table from the real script, the owner edits it, and only then is the scene file written.
- `engine/meta.py <scenes_module>` prints YouTube chapters (checks: first at 0:00, at least 3, each >= 10 s), a description, hashtags and a short caption for TikTok/Instagram/Facebook. Deliver it with every video.
- New LINT lines: more than 4 cards in one scene; Arabic text inside a mono-font block.

## REFERENCE: every card style, shape and block (same text as REFERENCE.md in the skill folder; pictures in `docs/images/` of the kit: look at them before choosing)
Pictures live in `docs/images/` of the kit (https://github.com/heshamadel1/ctrl-h). View them (Read tool) before choosing a look. All times are seconds in the voiceover. A block is a dict `{"k": <kind>, "t": <time>, ...}` inside `blocks=[...]` of a scene. `abs` blocks (marked ABS) are drawn over the whole frame, not inside the layout. Text rule: Latin only inside mono blocks (code, chip, er, http, diff, queue, arch labels); Arabic goes in cards, titles, headlines, recap.

### 1. Card styles (scene `style=`; 12; the allowed ones come from `card_styles` in the config)
| # | style | looks like | use for | picture |
|---|---|---|---|---|
| 1 | plain_dark (old `classic`) | thick border, hard coloured shadow, round check/cross | good / bad statements | cards-dark.png / cards-paper.png |
| 2 | tag_header (old `proposed`) | status bar on the edge, `tag` pill, `key` word underlined | rules, definitions (set tag + key) | cards-dark.png / cards-paper.png |
| 3 | glass_blur (old `glass`) | translucent, light border | calm explanations | cards-dark.png / cards-paper.png |
| 4 | numbered_list (old `numbers`) | big faint 01/02/03 + right/wrong pill | steps, mistakes lists | cards-dark.png / cards-paper.png |
| 5 | outline_thin (old `outline`) | thin outline, nearly transparent | calm lines | cards-dark.png / cards-paper.png |
| 6 | solid_orange (old `solid`) | accent fill, dark text | one key statement | cards-dark.png / cards-paper.png |
| 7 | neon_glow (old `neon`) | glowing border | emphasis, good/bad | cards-dark.png / cards-paper.png |
| 8 | paper_note (old `paper`) | light card, dark text | high contrast | cards-dark.png / cards-paper.png |
| 9 | soft_rounded (old `soft`) | status border + glow + badge | right/wrong lists | cards-dark.png / cards-paper.png |
| 10 | terminal_window (old `terminal`) | `exit 0` / `exit 1`, `$` | commands, results | cards-dark.png / cards-paper.png |
| 11 | step_arrows (old `steps`) | numbered circle + progress underline | ordered steps | cards-dark.png / cards-paper.png |
| 12 | icon_box (old `iconbox`) | coloured block with check/cross/number | right/wrong lists | cards-dark.png / cards-paper.png |
Sheets: `cards-dark.png`, `cards-paper.png`, `overview-16x9.png`, `overview-16x9.png`, `cards-paper.png`, `backgrounds.png`.

### 2. Card shapes (scene `grid=` / `cw=`; automatic rotation when 2+ cards)
`squares` (equal squares in a row, `shape-B-squares.png`), `pairs` (two columns, `shape-C-pairs.png`), `narrow` (one column 60 %, `cw=0.6`, `shape-D-narrow.png`). `grid="tiles"` = all cards as tiles in a row. `longcards=True` = legacy full-width (not used). 9:16 always stacks at full width.

### 3. Basic blocks
- `card`: `t, text, ok (True/False/None), tag, key, size, words=[(t, word)]` (word flash exactly when spoken). Helper `c(t, text, ok, tag, key, size, words)`. Use `NB=" "` between "الـ" and a Latin word.
- `chip`: `t, text` (small pill). `title`: `t, text, sub, size`.
- `code`: `t, file, lines=[(start, text, cps[, (r,g,b)])], focus=[(t,line)] or "auto", shake=t, size`. `file="terminal"` = terminal look. Latin only.
- `timeline`: `nodes`. `counter`: `t, t0, t1, v0, v1, label, size, mode` (v1 must equal the spoken number). `zoom`: `t, t_zoom, target, lines, file, magnify`. `phone`: `t, items, title`. `cta`: `t`.
- `row`: `split, items=[blocks]`. `tiles`: `items, square`. `compare`: `t, panels=[(title, [(t, text)])]`. `flow`: `t, nodes=[names], steps=[(t, from_idx, to_idx, label)]`.
- `ring` (countdown): `t0, t1, label`.

### 4. Infographic blocks (list topics)  (block-icards / steplist / fixcards .png)
- `icards`: `t, cols, cols_reel, items=[{t, title, icon, caption}]`; icons shield grid bar clock lock nodes key warn check db bolt.
- `steplist`: `t, list_side, items=[{name, t, file, lines=[(dt, text, cps[, cmd|out|ok|bad])]}]`.
- `fixcards`: `t, cols, cols_reel, items=[{t, title, sub, chain=[3 chips], chain_t, fix, fix_t}]`.

### 5. Comparison / tabs blocks  (block-versus / matrix / tabcard / icon3d .png)
- `versus`: `t, h, cols=[{t, name, sub, color "#RRGGBB", icon, code=[lines], bullets=[(t,text)]}]`. `icon`: "doc" draws a document, any other string is printed as text (use short symbols: "||", "->", "{}"). With 3 bullets and 3-4 code lines use `h` >= 660.
- `matrix`: `t, cols=[{name,color}], rows=[{t, label, cells=["ok"|"bad"|"mid"|text|(kind,note)]}]`.
- `tabcard`: `t, title, tabs=[{t, label, scene: play|rec|edit|script|icon kind}]`. `icon3d`: `t, items=[{t, kind, label}]` kinds play camera scissors code doc db; `cols_reel`.

### 6. Technical blocks   (picture `blocks-sheet-1.png`)
- `arch`: `t, nodes=[{t, name, sub, color, state=[(t,'ok'|'err'|'idle')]}], reqs=[(t, from_idx, to_idx, label[, 'err'|'back'])]`. A dot travels, the receiving node flashes. For Next.js -> Laravel -> PostgreSQL, request paths, Browser -> API.
- `er`: `t, tables=[{t, name, color, cols=[(name, 'PK'|'FK'|'')]}], links=[(t, from_table_idx, to_table_idx, 'fk_col')]`. FK lines run under the tables. For Multi-Tenant `tenant_id`, relations.
- `http`: `t, method (GET/POST/PUT/PATCH/DELETE), url, req=[(dt,line)], t_resp, status, status_text, res=[(dt,line)]`. Response panel is green for 2xx, amber for 400/404/409/422/429, red otherwise. For endpoints, login errors, API results.
- `diff`: `t, file, size, lines=[(t, '-'|'+'|' ', text[, t_gone])]`. For wrong vs right code.
- `queue`: `t, worker, queue_name, done_name, jobs=[{name, t_in, t_start, t_done}]`. For background jobs.
- `recap`: `t, title, items=[(t, text)]` (Arabic allowed). Last content scene before the end card.

## 6b. Flow and system blocks (engine/blocks_flow.py; pictures `blocks-sheet-2.png`, `blocks-sheet-3.png`; demo examples/v9_flow_scenes.py)
Use them whenever the script describes a system: two things compared on scaling/deploy/calls -> `split` (+ `titlevs` header); handlers/middleware/validation steps -> `chain`; one controller touching many services -> `hub`; ordered steps with a change (NEW/v2) -> `pipeline`; a request that passes checks -> `deviceflow`; bad code with several reasons to change -> `codeann`; Command/Message/Handler -> `flowmini`. Fields: see docs/FEATURES.md section 8. Names / code / tags Latin, Arabic only in captions, labels and deviceflow steps. Icons: user cart card code search gauge link clip server mail gear cube bell truck key lock shield db check x clock doc bolt.

### 7. Interactive blocks
- `shock`: `t, lines=[(text, size, (r,g,b))]` (first 3 s hook). `strike`: `t, t_strike, t_right, wrong, right`. `ba`: `t, t_slide, before=[lines], after=[lines]`.
- `poll`: `t, q, opts, t_fill, win, nopct=True` (never invent percentages). `predict`: `t, lines, q, t_count, t_ans, ans`. `mystery`: `t, q, a, t_reveal`. `gain`: `t, t0, t1, v0, v1, label, unit` (only real numbers). `note`: `t, text` (amber).
- ABS: `promise` (`t0, t1, t_unlock, locked, open`), `challenge` (`t0, t1, label`), `chips` (`t0, t1, items`, give the scene `reserve`), `corner` (`t0, t1, labels, switch`).
- Scene keys: `style, t0, t1, stage, head, head_t, blocks, grid, cw, reserve, reserve_reel, longcards`. File keys: `DUR, T_END, TAG1, TAG2, STAGES, TECH, SC, SUB_T, FOL_T`.

### 8. Automatic (no code needed)
Fixed Subscribe / Follow buttons (times via `SUB_T`, `FOL_T`), chapter banner "الجزء N من M", scene-progress dots, next-scene preview pill, scene link frame, camera push-in, alternating entry directions, SFX (`make_audio_lib.py`, library `assets/sfx`), end card with logo, Think Deeper, Build Smarter.

### 9. Themes, backgrounds, formats
Themes (all equal, the owner picks per video, never call one "main"): orange (dark), paper_orange (light paper, orange highlighter), soft_cream (white rounded cards, cream bg, orange glow, dark logo); other colours via `accent`/`card_color`/`bg_color`. Backgrounds (15, picture docs/images/backgrounds.png): hud_live, circuit, grid, hex, dots, waves, aurora, blueprint, terminal, minimal, paper, cream, or an image (default, hud_dark, hud_plate). Formats: `FMT=wide` 1920x1080, `FMT=reel` 1080x1920, `OUT_W` rescales.

### 10. Demo scene files (copy from them)
`lk_scenes.py`, `nx3_scenes.py` (full videos), `showcase_scenes.py` (all card styles), `v3_example_scenes.py`, `v4_example_scenes.py`, `v4_terminal_gain_scenes.py`, `w_scenes.py`, `v6_blocks_scenes.py` (icards, steplist, fixcards), `v7_blocks_scenes.py` (versus, matrix, tabcard, icon3d), `v8_blocks_scenes.py` (er, queue, arch, http, diff, recap).

## Reels / Shorts (9:16)
- Native motion (preferred): `FMT=reel` of the engine.
- Legacy proper: native re-design, one card at a time.
- Quick (old videos): the finished 16:9 scaled to 1080 wide over an animated 1080x1920 brand background loop (reel_bg_loop.mp4); ffmpeg: `-stream_loop -1 -i reel_bg_loop.mp4 -i video.mp4 -filter_complex "[1:v]scale=1080:-2[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[v]" -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 26 -r 30 -c:a copy -shortest -movflags +faststart out.mp4`. Instagram Reels max is 3 minutes: warn when longer.

## Logo and sign-off (fixed brand assets)
- BEFORE EVERY BUILD make sure the logo is found: `logo_ch.png` in the assets folder (kit `assets/` or the folder in `CTRLH_ASSETS`, which must also contain `fonts/` and `backgrounds/`). Lint warns "logo missing". Without it the corner logo and the end card show an EMPTY rounded frame: never deliver a video like that; ask him to re-send the logo.
- Official logo = the image he sent (logo_ch.png: orange rounded C, white H, orange </> between them, wordmark "CTRL + H" white with orange +H, on black). Keep a copy in the work folder; he re-sends it if missing. Never redraw it.
- Floating monogram (mono.png) at the TOP-LEFT of EVERY video: position (40,32), height ~55 px, float ~6 px over a 4.5 s sine, soft glow pulse. Hidden during the end card.
- End card starts exactly when "Ctrl H" is spoken: full logo centered; under it Fira Code accent-colour "Think Deeper." when spoken and "Build Smarter." when spoken, plus the Subscribe and Follow buttons (see BUTTONS). The last 3 audio segments are always Ctrl H / Think Deeper / Build Smarter. The old Arabic pill "تتعلم وتتطور" is retired.

## Fonts
- Arabic: **Cairo SemiBold**. Code/English/Latin: **Fira Code SemiBold**. He uploaded both; if missing ask him to re-attach.
- Fira has NO Arabic glyphs (tofu): any text with non-ASCII must use Cairo (`if text.isascii(): Fira else: Cairo`).
- PIL: ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM). Arabic draw: direction="rtl", language="ar".

## Colors
- Defaults (theme orange): background base (13,14,16) + accent glows + faint 96 px grid; accent #FF8A11; ink (10,11,13); paper (245,245,245); card (24,26,31); gray text; green = correct; red = wrong; amber = TIP/note. Buttons: black + accent. Other themes change only accent, card colour and background base (`engine/themes.py`); green/red keep their meaning in every theme.

## Backgrounds
- v2 styles for ANY theme (`bg_style`, generated by `engine/bg_styles.py`, 16:9 and 9:16, centre stays calm): circuit, grid, hex, dots, waves, aurora, blueprint, minimal. Own image: `background_file`.
- Legacy per-technology Ctrl + H backgrounds (orange only) follow.
- Premium dark tech theme, minimalist, charcoal with subtle gradients, orange #FF8A00 accent, optional cyan only for React. Low-opacity grid, circuit traces, nodes, hexagons, soft orange corner light, vignette; centre clean; background only (no text/logos/code/UI).
- Per technology: React = component trees + cyan orbits; Next.js = server-rendering flow lines, routing; Docker = containers, pipeline; Laravel = PHP-syntax feel, MVC lines, DB motifs; Node/Express = server nodes, API paths; PostgreSQL/MySQL = DB cylinders; Redis = cache layers; Git = branches, commits; WordPress = block layout with WordPress/PHP/MySQL chips.
- Used so far: laravel, react, nextjs, wp, git, db (also Locking), docker, node/rest, redis.
- Generator: `python3 ctrlh_bg.py <tech> bg_<tech>.png FiraCode-SemiBold.ttf` (in the pipeline zip); techs: nextjs react laravel docker node rest db redis git wp. Each video loads its PNG via `BGFILE`.

## Voiceover sync workflow (cards never appear before their word)
1. Segment the WAV by silence (`align_vo.segments`, RMS 10 ms hops, threshold ~-42 dB, merge gaps < 0.14 s, drop < 0.12 s); phrase START times come from segment starts. Save `<n>_segs.txt` (`name duration count` + `start-end` pairs).
2. STANDARD: place the script lines with `python3 engine/align.py voice.wav script.txt` (silence + character share, no install). OPTIONAL (advanced, only if available and the user agreed): Whisper, either `align.py --whisper` or per-segment local Whisper-small int8 (sherpa-onnx, `bash run_asr7.sh <n>`; ~3 min per 2 min audio); the text is only for order/wording. Run it in the background with nohup and poll; a session restart kills background jobs. If Whisper is unavailable or fails, continue with the standard method.
3. Map the script line by line onto segments in order (about 7 syllables/s); flag guessed splits honestly (cards may be off by ~0.5 s).
4. `E(t, te, d)` = smoothstep(prog(t, te-0.12, te-0.12+min(d,0.3))). Key concepts appear at the start of the sentence.
5. Duration = audio duration; end card at the "Ctrl H" segment; comment CTA box between the question and the end card.

## Audio
- Voice: `aresample=48000,volume=3dB`, mono to stereo. NEVER loudnorm.
- SFX (v2.1.0): the 34-sound library `assets/sfx/` placed by `engine/make_audio_lib.py` (see docs/SOUNDS.md; pins `SFX`, `SFX_AUTO`, `SFX_GAIN`; mix at 42% of the voice level, no ducking). The old synthesized SFX (make_audio.py, `CTRLH_SFX=synth`): plucks/clicks, ding for right, thud for wrong, thump+ping for key cards, counter ticks, flow whooshes, promise chime, fixed Subscribe (0:45) / Follow (DUR-40) button sounds, end-card pings, alternating transition whooshes), ducked under the voice. Mix (mix2.txt): `[1:a]aresample=48000,volume=3dB,pan=stereo|c0=c0|c1=c0,asplit=2[v][vs];[2:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];[v][md]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.85:level=disabled,volume=0.8[a]`. Mux: `-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t <DUR>`.
- Verify audio by analysis only.

## Arabic/RTL rules (Pillow RAQM)
- NBSP between "الـ" and a following Latin word; no colon after a Latin word in RTL; prefer Arabic-first lines; Latin at the end of a sentence appears at the left, not a bug.
- No parentheses or `::` next to Latin (write "Cache remember"). No glued "و" before Latin (use "+", "أو", "مع").
- Avoid paths like "app/" in RTL cards; wrap Arabic with a width-based helper; code lines <= ~45 chars.
- Semi-transparent shapes on an RGBA layer REPLACE pixels: draw on a separate layer then alpha_composite.

## Pipeline
- Python 3.13 (tested version; 3.11/3.12 only syntax-checked), PIL (RAQM), numpy, ffmpeg; fork Pool(2) pipes rgb24 to ffmpeg (libx264 crf 17, bt709).
- Renders: nohup in the background + poll with sleep inside the same turn (a foreground call times out at 10 min and a finished turn kills background jobs). No pkill in the same shell.
- New video: copy `lk_scenes.py`/`lk_anim.py`, replace SC (timings from the segments file), STAGES, DUR, T_END, TAG1, TAG2, TECH; make sure the card styles follow the user's choice (default plain_dark; owner: all), the interactive-feature minimum, and no per-scene button blocks; check a contact sheet in BOTH FMT (overlaps, tofu, overflow, nothing under the headline) before the final render.
- Voiceover is NOT generated here. npm/pip registries are blocked; GitHub clone works. He decided to keep our own engine (HyperFrames, OpenMontage, Reel Studio, Graphify not needed).

## Content rules
- Verify technical facts from official docs before scripting; be accurate about versions and honest about limits.
- Review his post first and correct mistakes, then produce the video.
- Scenes structured and numbered; hook first; CTA last.

## Repository and license
- The kit is published on GitHub (owner heshamadel1, project https://github.com/heshamadel1/ctrl-h) under the MIT license (owner's decision, 2026-10-30; see LICENSE). The Ctrl + H name and logo are not covered by it: do not reuse them without the owner's permission.
- Transcription (`run_asr.sh` / `asr_seg.py`) uses only `onnxruntime`, `scipy` and the sherpa-onnx Whisper-small MODEL FILES; the `sherpa-onnx` Python package is not needed (verified: it runs with the package not installed).

## Limits to state honestly
- No AI image/video generation here. Technology logos are not drawn from memory: name chips until he sends logo files.
- The pipeline lives only in the working session; a new chat needs him to re-attach ctrlh_pipeline.zip (anim.py, make_audio.py, scene examples, bg generator, align/ASR scripts) or clone the GitHub kit.
- Deliver files with SendUserFile and keep the final message short.

## Paper theme + paper blocks (optional, only when asked)
Light theme: `theme: paper_orange`. Blocks: `quote` (t,who,lines,hl), `chatwin` (t,title,ask,ask_t,lines,cursor), `minichart` (rows), `skeleton` (file,n,span,hl), `filegrid` (files,cols,missing,pick), `bigcount` (label,t0,t1,v0,v1). Use for scale/overwhelm moments, quotes, AI-chat demos, cost/growth. Default stays dark orange.

## Live background + topic chips (default `bg_style: hud_live`)
The HUD background is animated; its bottom chips show the tools of each scene. Rule: when a scene discusses specific tools, add `chips=["Tool1", "Tool2"]` (max 3, exact names as in the script); otherwise the engine picks tools from the scene text, then falls back to `TECH`. Do not hard-code chips in the background image.

## 3.0.1 sound and background rules (owner, 2026-11-15)
- SFX level is 42% of the voice level, no ducking (`engine/mix2.txt`). The library has 35 sounds.
- Pick sounds by meaning, not one per card: error for a wrong card, razor for the strike line, success for the right answer, riser into a reveal, glitch and error for warnings, transition per chapter, varied pop/click/success (never the same file twice in a row). Never pen/handwriting sound on a struck-out card.
- For a video that needs care, place the sounds by hand: `SFX_AUTO = False`, `SFX = [(seconds, "pop_01"), (seconds, "typing", duration)]`, and keep the automatic sound of only some kinds with `SFX_AUTO_ONLY = ["beam_pulse", "beam_hit", "typing"]`. Time them from the voice segments, and after a change re-mix audio only (vo + sfx + loudness), never re-render for a sound fix.
- Typing sound = a burst of the on-screen typing time. Set the code line speed (chars per second) so the typing lasts as long as the words it goes with, and the sound stops when the typing stops.
- Beam: the receiving node lights up and chimes when a pulse arrives, a pulse leaving plays a soft whoosh (`"glow": False` on a node turns the light off).
- The `paper` background is animated (ripple on the dot grid, drifting particles, breathing glow); `CTRLH_BG_MOTION=off` turns it off. Reels with it can pass 30 MB: compress with x264 crf 24 before sending.
- `align.py` returns one strictly increasing start per line (no duplicate or swapped starts on slow voices); Whisper segments stay the most accurate when available.
- `align.py voice.wav script.txt --asr asr.json` matches each script line to the spoken text (fuzzy, tolerant of ASR errors); make asr.json with `engine/asr_phrases.py` (offline Whisper ONNX model folder). Prefer it over character-share timing when a model is available.
- `engine/make_video.py voice.wav script.txt [--model DIR] [--build]`: one command from voice + script to timing (ASR text matching with a model), a draft scene file (`suggest.py`) and lint; review the draft, then build. Never overwrites an existing scene file without `--force`.
- Sound by meaning is automatic (kind `meaning`): wrong/bug -> error, works/secure -> success, warning -> glitch, question -> riser; `SFX_EVENTS = {"meaning": False}` turns it off. Long one-line text in chip/note/title/shock/mystery shrinks to fit by itself.
- Engine default theme is `paper_orange` (a user who has not chosen still gets it; anyone other than the owner is still asked). Faster render: camera zoom is bilinear (`CTRLH_ZOOM_FILTER=bicubic` for the old look) and x264 preset is `veryfast` (`CTRLH_X264_PRESET=medium`).
- `build.py <scene> --audio-only` re-mixes SFX/voice/loudness in ~20 s after changing pins or the mix (needs a previous full build); scene option `valign: "mid"` lowers the block stack for reels without captions.
- The end card follows the theme: light themes (`paper_orange`, `soft_cream`) end on a light paper background with a dark logo (orange C, dark H and wordmark); dark themes end on black.
