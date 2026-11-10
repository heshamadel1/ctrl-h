# Configuration

## Priority
1. **Environment variable** typed before a command (wins, one command only).
2. **`ctrlh.config.json`** (searched in `$CTRLH_CONFIG`, `./`, `../`, kit root).
3. **Built-in default**.
Every config key is turned into an environment variable by `engine/ctrlh_config.py`. Example file: `profiles/ctrlh.config.json`. A scene file's `SUB_T` / `FOL_T` win over `subscribe_t` / `follow_t`.

## Config keys
| key | env | type | default | meaning |
|---|---|---|---|---|
| `theme` | `CTRLH_THEME` | string | `orange` | `orange`, `paper_orange`, `soft_cream` (unknown value falls back to `orange`) |
| `accent` | `CTRLH_ACCENT` | `#RRGGBB` | theme accent `#FF8A11` | accent colour |
| `card_color` | `CTRLH_CARD_COLOR` | `#RRGGBB` | theme card | card fill |
| `bg_color` | `CTRLH_BG_COLOR` | `#RRGGBB` | theme base | background base colour |
| `card_styles` / `card_style` | `CTRLH_CARD_STYLES` | string or list | `plain_dark` on a fresh install, `all` in the owner profile | one name, a list, or `all` (names in [CATALOG.md](CATALOG.md)); `card_style` locks ONE look |
| `bg_style` | `CTRLH_BG_STYLE` | string | `hud_live` (dark), theme background otherwise | see Backgrounds below |
| `bg_style_locked` | (config only) | bool | `false` | `true` keeps your `bg_style` even if the theme has its own |
| `background_file` | `BGFILE` | path | none | your PNG background (1920x1080) |
| `assets` | `CTRLH_ASSETS` | folder | `assets/` | logo, monogram, fonts |
| `font_ar` / `font_latin` | `CTRLH_FONT_AR` / `CTRLH_FONT_LATIN` | .ttf path | Cairo SemiBold / Fira Code SemiBold | fonts |
| `signoff_1` / `signoff_2` | `CTRLH_SIGNOFF_1/2` | string | `Think Deeper.` / `Build Smarter.` | end-card lines |
| `label_ok` / `label_wrong` / `label_chapter` | `CTRLH_LABEL_*` | string | `صح` / `غلط` / `الجزء` | card and banner labels |
| `out_w` | `OUT_W` | int | 1920 (16:9) | output width, height follows |
| `subscribe_t` / `follow_t` | `SUB_T` / `FOL_T` | seconds or `false` | 45 / `DUR-40` | button times |
| `formats` | `CTRLH_FORMATS` | list | `["wide"]` | `wide` (16:9), `reel` (9:16) |
| `video_type` | `CTRLH_VIDEO_TYPE` | string | `explainer` | `explainer`, `short`, `series` (`profiles/video-types.json`) |
| `max_part_seconds` | `CTRLH_MAX_PART` | int | 180 | auto split length |
| `disabled_blocks` | `CTRLH_DISABLED_BLOCKS` | list | `[]` | block kinds the engine drops |
| `dims` | `CTRLH_DIMS` | bool | `false` | screen-darkening effect |
| `workers` | `CTRLH_WORKERS` | int | CPU count | render processes |
| `series_name` + `series` | `CTRLH_SERIES` | object | none | per-series overrides of any key |

Scene-file constants (not config): `SFX` (pinned sounds), `SFX_AUTO`, `SFX_GAIN`, `TYPING_SPEED`. A ready file to copy: `profiles/ctrlh.config.example.json`.

Other environment variables: `FMT` (`wide`/`reel`), `CTRLH_T0`/`CTRLH_T1` (render window), `CTRLH_CACHE` (cache folder, `0` = off), `CTRLH_SFX` (`lib` default, `synth`), `CTRLH_CONFIG` (config path), `CTRLH_TOKENS` (design tokens JSON).

## Themes
| theme | look | signature background |
|---|---|---|
| `orange` | dark charcoal, orange accent, hard white shadow | `hud_live` (animated) |
| `paper_orange` | cream paper, thick black borders, hard shadows, yellow highlighter | `paper` |
| `soft_cream` | cream, white rounded cards, light shadow, orange glow, dark H logo, merged bottom-right chapter pill, soft Subscribe/Follow and end card | `cream` |
A theme's signature background replaces the default `hud_live` unless `bg_style_locked` is `true`. **Theme and background are separate choices**: the theme sets colours and card look, the background is picked with `bg_style` (any of the list below works with any theme).

## Backgrounds (`bg_style`)
`hud_live` (animated HUD, dark), `circuit`, `grid`, `hex`, `dots`, `waves`, `aurora`, `blueprint`, `terminal`, `minimal` (dark, for any accent), `paper`, `cream` (light), `tech:<name>` (a background with the motifs of a technology: `nextjs react laravel wp docker node rest db redis git`, 16:9 only, 9:16 falls back to `circuit`), or a PNG via `background_file` (`assets/backgrounds/default.png`, `hud_dark.png`, `hud_plate.png` are included). Picture of all of them: `docs/images/backgrounds.png`. Choose one per video; the skill asks.

## Examples
```bash
CTRLH_THEME=soft_cream CTRLH_BG_STYLE=cream FMT=wide python3 engine/render.py my_scenes frames out 30
CTRLH_ACCENT=#00B8D9 OUT_W=1280 FMT=wide python3 engine/render.py my_scenes v720.mp4
CTRLH_BG_STYLE=minimal BGFILE=assets/backgrounds/hud_dark.png ...      # image background
```
