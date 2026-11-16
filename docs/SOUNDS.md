# SOUNDS — Ctrl + H sound library (35 sounds)

All files live in `assets/sfx/`, named `<category>_<NN>_<name>.mp3`. Say a file name (or just `category_NN`) to pin it to a moment; otherwise the engine picks by category, mixed at 42% of the voice level with no back-to-back repeats.


## whoosh

| file | length | use | original name |
|---|---|---|---|
| `whoosh_01_swoosh.mp3` | 1.06 s | quick scene cut | swoosh.mp3 |
| `whoosh_02_soft.mp3` | 1.27 s | scene cut | transition-sfx.mp3 |
| `whoosh_03_air.mp3` | 1.25 s | scene cut | transition-sfx-2-whoosh.mp3 |
| `whoosh_04_studio.mp3` | 1.92 s | scene cut | studio-whoosh.mp3 |
| `whoosh_05_base.mp3` | 1.7 s | scene cut with body | trading_nation-transition-base.mp3 |

## transition

| file | length | use | original name |
|---|---|---|---|
| `transition_01_cinematic.mp3` | 3.12 s | big chapter change | ast-cinematic-whoosh-modern-action-transition-.mp3 |
| `transition_02_riser_swoosh.mp3` | 0.99 s | big chapter change | riser-swoosh-transition.mp3 |
| `transition_03_phoenix_soft.mp3` | 7.0 s | soft chapter change | phoenix-soft-transition.mp3 |

## impact

| file | length | use | original name |
|---|---|---|---|
| `impact_01_dramatic_boom.mp3` | 4.3 s | shock / reveal | impact-transition-impact-dramatic-boom.mp3 |
| `impact_02_suspense_boom.mp3` | 3.02 s | dark reveal | dragon-studio-suspenseful-boom-451863.mp3 |

## riser

| file | length | use | original name |
|---|---|---|---|
| `riser_01_cinematic.mp3` | 4.03 s | build-up before a reveal | dragon-studio-cinematic-riser-03-414575.mp3 |

## glitch

| file | length | use | original name |
|---|---|---|---|
| `glitch_01_glitch.mp3` | 0.78 s | error / bug / glitchy moment | glitch.mp3 |

## typing

| file | length | use | original name |
|---|---|---|---|
| `typing_01_keyboard.mp3` | 8.05 s | code typing | keyboard-typing-hd.mp3 |

## click

| file | length | use | original name |
|---|---|---|---|
| `click_01_mouse.mp3` | 0.37 s | cursor click | mouse-click.mp3 |
| `click_02_button.mp3` | 0.74 s | button press | button-pressed.mp3 |
| `click_03_tap.mp3` | 1.03 s | light tap | tap-sound.mp3 |
| `click_04_tick.mp3` | 3.79 s | tick on a list item | tick-sound-effect-1.mp3 |

## success

| file | length | use | original name |
|---|---|---|---|
| `success_01_correct.mp3` | 1.06 s | correct / check mark | training-program-correct1.mp3 |
| `success_02_notify_a.mp3` | 1.07 s | positive notification | notification-040.mp3 |
| `success_03_notify_b.mp3` | 2.46 s | positive notification | notification-051.mp3 |
| `success_04_notify_c.mp3` | 1.1 s | notification | notification-sound-effect.mp3 |
| `success_05_ding.mp3` | 2.74 s | bell / done | ding.mp3 |

## pop

| file | length | use | original name |
|---|---|---|---|
| `pop_01_smooth.mp3` | 3.08 s | element appears | pop-up-notify-smooth-modern.mp3 |
| `pop_02_cartoon.mp3` | 1.04 s | playful appear | pop-cartoon.mp3 |
| `pop_03_sharp.mp3` | 1.02 s | sharp appear | sharp-pop.mp3 |
| `pop_04_bubble.mp3` | 0.65 s | ui popup | buble-ui-pop-up-8.mp3 |

## error

| file | length | use | original name |
|---|---|---|---|
| `error_01_error.mp3` | 1.62 s | wrong / blocked | error.mp3 |
| `error_02_buzzer.mp3` | 1.91 s | denied / failed | universfield-error-notification-buzzer.mp3 |
| `error_03_alert.mp3` | 1.08 s | error alert | universfield-error-notification.mp3 |

## paper

| file | length | use | original name |
|---|---|---|---|
| `paper_01_flip_a.mp3` | 2.61 s | page / next part | page-flip.mp3 |
| `paper_02_flip_b.mp3` | 0.62 s | page / next part | freesound_community-page-flip-47177.mp3 |
| `paper_03_turn.mp3` | 1.23 s | page turn | page-turn-305789.mp3 |

## pen

| file | length | use | original name |
|---|---|---|---|
| `pen_01_signature.mp3` | 0.96 s | signing / approval | pen-signature-5-395486.mp3 |
| `pen_02_marker.mp3` | 6.48 s | highlight / underline | marker-pen-345733.mp3 |
| `razor_01_cut.mp3` | 0.16 s | timeline razor / split, strike-through line | generated for Ctrl H |

## SysDiagram sound map (block `sysdiagram`, automatic)
No voice or music in the reference video: only short effects (about 38 in 27 s, mostly under 0.3 s) that sit on the visual events. The block places them itself (no pins needed); pin `SFX=[(t,"name")]` to override.

| name | when | library sound |
|---|---|---|
| `sd_stage` | the stage pill changes | `transition_*` (random) |
| `sd_tick` | a node, row, pill or lock appears | `click_*` |
| `sd_ok` | green check badge, COMMIT | `success_*` |
| `sd_err` | red X badge, ROLLBACK | `error_*` |
| `sd_env` | an envelope starts travelling | `whoosh_02_soft` |
| `sd_sticker` | a result sticker pops | `pop_*` |
| `sd_done` | the last sticker (the conclusion) | `success_05_ding` |
No two sounds of the same kind within 0.18 s, so busy moments stay clean.

## sysdiagram sound map (automatic)
`sysdiagram` places sounds by event; no pin needed. Each name below is a role that picks from the library:

| role | when | library category |
|---|---|---|
| `sd_stage` | the stage pill changes | `transition` |
| `sd_tick` | a node / pill / table row appears, BEGIN, lock | `click` |
| `sd_ok` | green badge, COMMIT | `success` |
| `sd_err` | red badge, ROLLBACK | `error` |
| `sd_env` | an envelope starts travelling | `whoosh_02_soft` |
| `sd_sticker` | a result sticker pops in | `pop` |
| `sd_done` | the last sticker | `success_05_ding` |
Same-role sounds closer than 0.18 s are skipped. Pin your own with `SFX=[(t, "name")]` as usual.


## How the engine uses them (3.0.1)

- A struck-out (wrong) card plays an **error** sound when it appears, a **razor** cut when the line strikes it, and a **success** chime when the right answer shows. The pen sounds are only for highlights you pin yourself.
- Cards, clicks and chimes never repeat the same file twice in a row; hand-placed pins let you vary them yourself.
- Beam: a light pulse leaving a node = soft whoosh, a pulse arriving = chime, and the receiving node lights up (`"glow": False` on a node turns the light off).
- Typing is a burst of exactly the on-screen typing time, so make the code line's speed match the words (`("t", "text", chars_per_second)`).
- Hand-placed sounds: `SFX = [(seconds, "pop_01"), (seconds, "typing", duration)]` with `SFX_AUTO = False`. To keep the automatic sound of only some kinds: `SFX_AUTO_ONLY = ["beam_pulse", "beam_hit", "typing"]`.
