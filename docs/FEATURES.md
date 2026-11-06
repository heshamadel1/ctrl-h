# Features reference (with pictures)

Every feature of the kit, what it looks like, its fields, and where to change it. Pictures are in `docs/images/` and come from the engine itself:
`python3 engine/docs_gallery.py` redraws the `feat-*.png` ones (16:9; set `FMT=reel` for 9:16). Times are seconds of the voiceover.
A block is a dict `{"k": <kind>, "t": <time>, ...}` inside `blocks=[...]` of a scene. Code for block `X` lives in `engine/anim.py`, function `draw_X`.
How to change a look: see `docs/CUSTOMIZE.md`.

## Scene file anatomy

```python
DUR, T_END, TAG1, TAG2 = 166.0, 160.0, 161.5, 163.0   # voice length, end card start, "Think Deeper." time, "Build Smarter." time
STAGES = ["المشكلة", "الحل"]; TECH = ["JavaScript", "Fetch"]   # chapter names, floating tech chips
SUB_T = 58.0; FOL_T = None                                      # button times (False = none)
SC = [dict(style="classic", t0=0, t1=9, stage=0, head="العنوان", head_t=.2, blocks=[ ... ])]
```

Scene keys: `style, t0, t1, stage, head, head_t, blocks, grid, cw, reserve, reserve_reel, longcards`. Scenes must touch: scene N `t1` equals scene N+1 `t0`.

---

## 1. Card styles (scene `style=`)

| style                                                       | picture                                                    | use for                           |
| ----------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------- |
| classic                                                     | `style-1-classic.png`                                      | good / bad statements             |
| proposed                                                    | `style-2-proposed.png`                                     | rules, definitions (`tag`, `key`) |
| glass                                                       | `style-3-glass.png`                                        | calm explanations                 |
| numbers                                                     | `style-4-numbers.png`                                      | steps, mistakes                   |
| outline, solid, neon, paper, soft, terminal, steps, iconbox | `cards-12-styles-orange.png`, `cards-12-styles-violet.png` | see the sheets                    |

![12 styles](images/cards-12-styles-orange.png)

Allowed styles: config `card_styles` (`"all"` or a list). Style code: `draw_card` in `anim.py`; colours in `themes.py`.

## 2. Card shapes (scene `grid=` / `cw=`)

`squares`, `pairs`, `narrow` (`cw=0.6`), `tiles`. With 2+ cards the engine rotates shapes automatically.
![squares](images/shape-B-squares.png) ![pairs](images/shape-C-pairs.png) ![narrow](images/shape-D-narrow.png) ![tiles](images/feat-grid-tiles.png)

## 3. Basic blocks

**card** `t, text, ok (True/False/None), tag, key, size, words=[(t, word)]`. `words` flashes a word exactly when spoken. Use `NB=" "` (U+00A0) between "الـ" and a Latin word.

**code** `t, file, lines=[(start, text, cps[, (r,g,b)])], focus=[(t,line)] or "auto", shake=t, size`. `file="terminal"` gives the terminal look. Latin text only.
![terminal](images/feat-code-terminal.png) ![focus](images/feat-code-focus.png)

**compare** `t, panels=[(title, [(t, text)])]` ![compare](images/feat-compare.png)
**flow** `t, nodes=[names], steps=[(t, from_idx, to_idx, label)]` ![flow](images/feat-flow.png)
**timeline** `t, nodes=[(t, label, sub, state)]` ![timeline](images/feat-timeline.png)
**counter** `t, t0, t1, v0, v1, label, size` (v1 equals the spoken number) ![counter](images/feat-counter.png)
**gain** `t, t0, t1, v0, v1, label, unit` (real numbers only) ![gain](images/feat-gain.png)
Also: `chip` (`t, text`), `title` (`t, text, sub, size`), `zoom` (`t, t_zoom, target, lines, file, magnify`), `phone` (`t, items, title`), `cta` (`t`), `row` (`split, items`), `tiles` (`items, square`).

## 4. Interactive blocks (retention)

| block                  | fields                                                                       | picture                      |
| ---------------------- | ---------------------------------------------------------------------------- | ---------------------------- |
| shock (first 3 s hook) | `t, lines=[(text, size, (r,g,b))]`                                           | ![](images/feat-shock.png)   |
| strike                 | `t, t_strike, t_right, wrong, right`                                         | ![](images/feat-strike.png)  |
| ba (before / after)    | `t, t_slide, before=[..], after=[..]`                                        | ![](images/feat-ba.png)      |
| mystery                | `t, q, a, t_reveal`                                                          | ![](images/feat-mystery.png) |
| predict                | `t, lines, q, t_count, t_ans, ans`                                           | ![](images/feat-predict.png) |
| poll                   | `t, q, opts=[(text, 0)], t_fill, win, nopct=True` (never invent percentages) | ![](images/feat-poll.png)    |
| note                   | `t, text` (amber)                                                            | ![](images/feat-note.png)    |

**Persistent (`"abs": True`, give the scene `reserve` if they sit at the bottom):**
| block | fields | picture |
|---|---|---|
| promise | `t0, t1, t_unlock, locked, open` | ![](images/feat-promise.png) |
| challenge | `t0, t1, label` | ![](images/feat-challenge.png) |
| ring (countdown) | `t0, t1, label` | ![](images/feat-ring.png) |
| chips | `t0, t1, items` | ![](images/feat-chips.png) |
| corner | `t0, t1, labels, switch=[t]` | ![](images/feat-corner.png) |
| button | `kind: subscribe or follow, t0, t1` | ![](images/feat-buttons.png) |

Fixed Subscribe / Follow buttons are normally automatic: `SUB_T`, `FOL_T` in the scene file (`False` = none).

## 5. Infographic blocks

`icards` (`t, cols, items=[{t, title, icon, caption}]`, icons shield grid bar clock lock nodes key warn check db bolt) ![](images/block-icards.png)
`steplist` (`t, list_side, items=[{name, t, file, lines}]`) ![](images/block-steplist.png)
`fixcards` (`t, cols, items=[{t, title, sub, chain, chain_t, fix, fix_t}]`) ![](images/block-fixcards.png)

## 6. Comparison blocks

`versus` (`t, h, cols=[{t, name, sub, color, icon, code, bullets}]`; `icon` "doc" or a short symbol; with 3 bullets + 3-4 code lines use `h` >= 660) ![](images/block-versus.png)
`matrix` (`t, cols, rows=[{t, label, cells}]`) ![](images/block-matrix.png)
`tabcard` (`t, title, tabs=[{t, label, scene}]`) ![](images/block-tabcard.png)
`icon3d` (`t, items=[{t, kind, label}]`) ![](images/block-icon3d.png)

## 7. Technical blocks (back-end topics)

| block | fields                                                                      | picture                         |
| ----- | --------------------------------------------------------------------------- | ------------------------------- | ------------------------------------ | ------------------------ |
| arch  | `t, nodes=[{t, name, sub, color, state}], reqs=[(t, from, to, label[, 'err' | 'back'])]`                      | ![](images/block-arch.png)           |
| er    | `t, tables=[{t, name, color, cols=[(name,'PK'                               | 'FK'                            | '')]}], links=[(t, from, to, 'fk')]` | ![](images/block-er.png) |
| http  | `t, method, url, req, t_resp, status, status_text, res`                     | ![](images/block-http-diff.png) |
| diff  | `t, file, size, lines=[(t, '-'                                              | '+'                             | ' ', text[, t_gone])]`               | same picture             |
| queue | `t, worker, queue_name, done_name, jobs=[{name, t_in, t_start, t_done}]`    | ![](images/block-queue.png)     |
| recap | `t, title, items=[(t, text)]`                                               | ![](images/block-recap.png)     |

Rule: technical blocks use Latin text only (the mono font has no Arabic). Arabic goes in cards and headlines.

## 8. Flow and system blocks (diagrams from the reference sheets)

Every block works in 16:9 and 9:16 (pictures: `feat-<name>.png` and `feat-<name>-9x16.png`). Names, code and tags are Latin (mono font); Arabic is fine in captions, labels and `deviceflow` steps. Demo scene file: `examples/v9_flow_scenes.py`.

| block      | use for                                                                                             | fields                                                                                                                                                                                                                                       | picture                         |
| ---------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| titlevs    | header of a comparison: two coloured pills, round "vs", sub line                                    | `t, a, b, ca, cb ("#RRGGBB"), sub`                                                                                                                                                                                                           | ![](images/feat-titlevs.png)    |
| split      | two systems side by side (16:9) or stacked (9:16) with a VS badge: scaling, deploy, calls           | `t, counter:"1/5 SCALING", panels:[{name, tag, color, src:{name,icon}, mode:"box" or "fan", services:[{t,name,icon}], events:[(t,'traffic',idx),(t,'fail',idx),(t,'scale',idx),(t,'ver',idx,'v2')]}]` (`idx -1` = the whole box in mode box) | ![](images/feat-split.png)      |
| chain      | chain of responsibility / middleware: handlers in a column with "Next" links and red error exits    | `t, start, payload, link, steps:[{t,name,sub,icon,color,err:(t,'400 Bad Request')}]`                                                                                                                                                         | ![](images/feat-chain.png)      |
| hub        | controller / service with spokes: which action touches which service (packets in the action colour) | `t, top, user, hub:{t,name,sub,icon,color}, actions:[{t,name,icon,color,to:[spoke idx]}], spokes:[{t,name,icon,color}], numbered, q, q_t`                                                                                                    | ![](images/feat-hub.png)        |
| pipeline   | steps joined by chain links, with NEW / v2 badges                                                   | `t, nodes:[{t,name,icon,color,badge:(t,'NEW','#hex')}]`                                                                                                                                                                                      | ![](images/feat-pipeline.png)   |
| deviceflow | phone + API + checklist: a request passes several checks                                            | `t, phone:{title,fields:[(icon,text)],button,press_t}, api:{t,name,sub,color}, steps:[{t,tag,label,icon,color}]`                                                                                                                             | ![](images/feat-deviceflow.png) |
| codeann    | annotated code: squiggles, tags, counter, pressure bar, caption                                     | `t, file, lang, lines:[(t,text)], squiggle:[(t,line)], tags:[(t,line,text,'#hex')], counter:(t,text), bar:(t0,t1,'#hex'), label:(t,text,'#hex'), cap:(t,text)` (about 12 lines max)                                                          | ![](images/feat-codeann.png)    |
| flowmini   | small flow: Command -> Message -> Handler                                                           | `t, items:[{t, kind:'pill'/'card'/'circle', name, icon, color}]`                                                                                                                                                                             | ![](images/feat-flowmini.png)   |

9:16 pictures: ![](images/feat-split-9x16.png) ![](images/feat-chain-9x16.png) ![](images/feat-hub-9x16.png) ![](images/feat-deviceflow-9x16.png)

Icons for these blocks (`icon`): user cart card code search gauge link clip server mail gear cube bell truck key lock shield db check x clock doc bolt. Add one in `_ico` of `engine/blocks_flow.py`.

## 9. Automatic features (no code in the scene file)

chapter banner "الجزء N من M · name" (`STAGES`), scene-progress dots, next-scene preview pill, scene link frame, camera push-in, alternating entry directions, floating monogram, SFX per block (`engine/make_audio.py`), end card with logo and sign-off, Subscribe / Follow buttons, safe area and design tokens (`engine/tokens.py`), auto focus for code, LINT on every render.
`dims` (screen darkening) exists but is OFF: it looked like the screen turning off. `CTRLH_DIMS=1` or config `"dims": true` turns it on.

## 10. Themes and backgrounds

![themes](images/themes.png) ![backgrounds](images/backgrounds.png)
Config: `theme`, `bg_style`, `card_styles`, `signoff_1`, `signoff_2`.

## 11. Tools

| command                                                        | job                                                                         |
| -------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `python3 engine/build.py <scenes> --vo voice.wav`              | lint, contact sheet, split plan, render (cache), SFX, mux, meta, all in one |
| `python3 engine/lint.py <scenes> [--strict] [--sheet out.png]` | check a scene file without rendering                                        |
| `python3 engine/render.py <scenes> out.mp4`                    | render one video (env `FMT`, `CTRLH_T0/T1`)                                 |
| `python3 engine/meta.py <scenes> out.md`                       | chapters, description, hashtags                                             |
| `python3 engine/docs_gallery.py`                               | redraw the feature pictures                                                 |
