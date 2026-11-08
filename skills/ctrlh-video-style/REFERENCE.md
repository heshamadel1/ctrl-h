# REFERENCE: every card style, shape and block

Pictures live in `docs/images/` of the kit (https://github.com/heshamadel1/ctrl-h). View them (Read tool) before choosing a look. All times are seconds in the voiceover. A block is a dict `{"k": <kind>, "t": <time>, ...}` inside `blocks=[...]` of a scene. `abs` blocks (marked ABS) are drawn over the whole frame, not inside the layout. Text rule: Latin only inside mono blocks (code, chip, er, http, diff, queue, arch labels); Arabic goes in cards, titles, headlines, recap.

## 1. Card styles (scene `style=`; 12; the allowed ones come from `card_styles` in the config)

| #   | style                            | looks like                                                | use for                            | picture                          |
| --- | -------------------------------- | --------------------------------------------------------- | ---------------------------------- | -------------------------------- |
| 1   | plain_dark (old `classic`)       | thick border, hard coloured shadow, round check/cross     | good / bad statements              | cards-dark.png / cards-paper.png |
| 2   | tag_header (old `proposed`)      | status bar on the edge, `tag` pill, `key` word underlined | rules, definitions (set tag + key) | cards-dark.png / cards-paper.png |
| 3   | glass_blur (old `glass`)         | translucent, light border                                 | calm explanations                  | cards-dark.png / cards-paper.png |
| 4   | numbered_list (old `numbers`)    | big faint 01/02/03 + right/wrong pill                     | steps, mistakes lists              | cards-dark.png / cards-paper.png |
| 5   | outline_thin (old `outline`)     | thin outline, nearly transparent                          | calm lines                         | cards-dark.png / cards-paper.png |
| 6   | solid_orange (old `solid`)       | accent fill, dark text                                    | one key statement                  | cards-dark.png / cards-paper.png |
| 7   | neon_glow (old `neon`)           | glowing border                                            | emphasis, good/bad                 | cards-dark.png / cards-paper.png |
| 8   | paper_note (old `paper`)         | light card, dark text                                     | high contrast                      | cards-dark.png / cards-paper.png |
| 9   | soft_rounded (old `soft`)        | status border + glow + badge                              | right/wrong lists                  | cards-dark.png / cards-paper.png |
| 10  | terminal_window (old `terminal`) | `exit 0` / `exit 1`, `$`                                  | commands, results                  | cards-dark.png / cards-paper.png |
| 11  | step_arrows (old `steps`)        | numbered circle + progress underline                      | ordered steps                      | cards-dark.png / cards-paper.png |
| 12  | icon_box (old `iconbox`)         | coloured block with check/cross/number                    | right/wrong lists                  | cards-dark.png / cards-paper.png |

Sheets: `cards-dark.png`, `cards-paper.png`, `overview-16x9.png`, `overview-16x9.png`, `cards-paper.png`, `backgrounds.png`.

## 2. Card shapes (scene `grid=` / `cw=`; automatic rotation when 2+ cards)

`squares` (equal squares in a row, `shape-B-squares.png`), `pairs` (two columns, `shape-C-pairs.png`), `narrow` (one column 60 %, `cw=0.6`, `shape-D-narrow.png`). `grid="tiles"` = all cards as tiles in a row. `longcards=True` = legacy full-width (not used). 9:16 always stacks at full width.

## 3. Basic blocks

- `card`: `t, text, ok (True/False/None), tag, key, size, words=[(t, word)]` (word flash exactly when spoken). Helper `c(t, text, ok, tag, key, size, words)`. Use `NB=" "` between "الـ" and a Latin word.
- `chip`: `t, text` (small pill). `title`: `t, text, sub, size`.
- `code`: `t, file, lines=[(start, text, cps[, (r,g,b)])], focus=[(t,line)] or "auto", shake=t, size`. `file="terminal"` = terminal look. Latin only.
- `timeline`: `nodes`. `counter`: `t, t0, t1, v0, v1, label, size, mode` (v1 must equal the spoken number). `zoom`: `t, t_zoom, target, lines, file, magnify`. `phone`: `t, items, title`. `cta`: `t`.
- `row`: `split, items=[blocks]`. `tiles`: `items, square`. `compare`: `t, panels=[(title, [(t, text)])]`. `flow`: `t, nodes=[names], steps=[(t, from_idx, to_idx, label)]`.
- `ring` (countdown): `t0, t1, label`.

## 4. Infographic blocks (list topics) (block-icards / steplist / fixcards .png)

- `icards`: `t, cols, cols_reel, items=[{t, title, icon, caption}]`; icons shield grid bar clock lock nodes key warn check db bolt.
- `steplist`: `t, list_side, items=[{name, t, file, lines=[(dt, text, cps[, cmd|out|ok|bad])]}]`.
- `fixcards`: `t, cols, cols_reel, items=[{t, title, sub, chain=[3 chips], chain_t, fix, fix_t}]`.

## 5. Comparison / tabs blocks (block-versus / matrix / tabcard / icon3d .png)

- `versus`: `t, h, cols=[{t, name, sub, color "#RRGGBB", icon, code=[lines], bullets=[(t,text)]}]`. `icon`: "doc" draws a document, any other string is printed as text (use short symbols: "||", "->", "{}"). With 3 bullets and 3-4 code lines use `h` >= 660.
- `matrix`: `t, cols=[{name,color}], rows=[{t, label, cells=["ok"|"bad"|"mid"|text|(kind,note)]}]`.
- `tabcard`: `t, title, tabs=[{t, label, scene: play|rec|edit|script|icon kind}]`. `icon3d`: `t, items=[{t, kind, label}]` kinds play camera scissors code doc db; `cols_reel`.

## 6. Technical blocks (picture `blocks-sheet-1.png`)

- `arch`: `t, nodes=[{t, name, sub, color, state=[(t,'ok'|'err'|'idle')]}], reqs=[(t, from_idx, to_idx, label[, 'err'|'back'])]`. A dot travels, the receiving node flashes. For Next.js -> Laravel -> PostgreSQL, request paths, Browser -> API.
- `er`: `t, tables=[{t, name, color, cols=[(name, 'PK'|'FK'|'')]}], links=[(t, from_table_idx, to_table_idx, 'fk_col')]`. FK lines run under the tables. For Multi-Tenant `tenant_id`, relations.
- `http`: `t, method (GET/POST/PUT/PATCH/DELETE), url, req=[(dt,line)], t_resp, status, status_text, res=[(dt,line)]`. Response panel is green for 2xx, amber for 400/404/409/422/429, red otherwise. For endpoints, login errors, API results.
- `diff`: `t, file, size, lines=[(t, '-'|'+'|' ', text[, t_gone])]`. For wrong vs right code.
- `queue`: `t, worker, queue_name, done_name, jobs=[{name, t_in, t_start, t_done}]`. For background jobs.
- `recap`: `t, title, items=[(t, text)]` (Arabic allowed). Last content scene before the end card.

## 6b. Flow and system blocks (engine/blocks_flow.py; pictures `blocks-sheet-2.png`, `blocks-sheet-3.png`; demo examples/v9_flow_scenes.py)

Use them whenever the script describes a system: two things compared on scaling/deploy/calls -> `split` (+ `titlevs` header); handlers/middleware/validation steps -> `chain`; one controller touching many services -> `hub`; ordered steps with a change (NEW/v2) -> `pipeline`; a request that passes checks -> `deviceflow`; bad code with several reasons to change -> `codeann`; Command/Message/Handler -> `flowmini`. Fields: see docs/FEATURES.md section 8. Names / code / tags Latin, Arabic only in captions, labels and deviceflow steps. Icons: user cart card code search gauge link clip server mail gear cube bell truck key lock shield db check x clock doc bolt.

## 7. Interactive blocks

- `shock`: `t, lines=[(text, size, (r,g,b))]` (first 3 s hook). `strike`: `t, t_strike, t_right, wrong, right`. `ba`: `t, t_slide, before=[lines], after=[lines]`.
- `poll`: `t, q, opts, t_fill, win, nopct=True` (never invent percentages). `predict`: `t, lines, q, t_count, t_ans, ans`. `mystery`: `t, q, a, t_reveal`. `gain`: `t, t0, t1, v0, v1, label, unit` (only real numbers). `note`: `t, text` (amber).
- ABS: `promise` (`t0, t1, t_unlock, locked, open`), `challenge` (`t0, t1, label`), `chips` (`t0, t1, items`, give the scene `reserve`), `corner` (`t0, t1, labels, switch`).
- Scene keys: `style, t0, t1, stage, head, head_t, blocks, grid, cw, reserve, reserve_reel, longcards`. File keys: `DUR, T_END, TAG1, TAG2, STAGES, TECH, SC, SUB_T, FOL_T`.

## 8. Automatic (no code needed)

Fixed Subscribe / Follow buttons (times via `SUB_T`, `FOL_T`), chapter banner "الجزء N من M", scene-progress dots, next-scene preview pill, scene link frame, camera push-in, alternating entry directions, SFX (`make_audio.py`), end card with logo, Think Deeper, Build Smarter.

## 9. Themes, backgrounds, formats

Themes: orange (main dark) and paper_orange (light paper, orange highlighter); other colours via `accent`/`card_color`/`bg_color`. Backgrounds: circuit, grid, hex, dots, waves, aurora, blueprint, minimal, or own PNG. Formats: `FMT=wide` 1920x1080, `FMT=reel` 1080x1920, `OUT_W` rescales.

## 10. Demo scene files (copy from them)

`lk_scenes.py`, `nx3_scenes.py` (full videos), `showcase_scenes.py` (all card styles), `v3_example_scenes.py`, `v4_example_scenes.py`, `v4_terminal_gain_scenes.py`, `w_scenes.py`, `v6_blocks_scenes.py` (icards, steplist, fixcards), `v7_blocks_scenes.py` (versus, matrix, tabcard, icon3d), `v8_blocks_scenes.py` (er, queue, arch, http, diff, recap).

## Paper theme + paper blocks (optional, only when asked)

Light theme: `theme: paper_orange`. Blocks: `quote` (t,who,lines,hl), `chatwin` (t,title,ask,ask_t,lines,cursor), `minichart` (rows), `skeleton` (file,n,span,hl), `filegrid` (files,cols,missing,pick), `bigcount` (label,t0,t1,v0,v1). Use for scale/overwhelm moments, quotes, AI-chat demos, cost/growth. Default stays dark orange.

## Live background + topic chips (default `bg_style: hud_live`)

The HUD background is animated; its bottom chips show the tools of each scene. Rule: when a scene discusses specific tools, add `chips=["Tool1", "Tool2"]` (max 3, exact names as in the script); otherwise the engine picks tools from the scene text, then falls back to `TECH`. Do not hard-code chips in the background image.

## Theme choice rule

Before making any video, ask the owner which theme: MAIN dark (`hud_live`, orange) or PAPER (`theme: paper`). Set `theme` / `bg_style` in the config or env accordingly (`CTRLH_THEME=paper`).

Card choice rule: with the theme question, also ask: all cards / ONE card look (`card_style`) / certain families only (`disabled_blocks`). See docs/CATALOG.md.
