# Changelog

## 2.0.0 (2026-10-31)

- README: settings priority (env > config > defaults), clearer Quick Start.
- First-run setup: Claude asks for identity, colours, card styles, background and brand assets, saved in `ctrlh.config.json` (`engine/ctrlh_setup.py`, `engine/ctrlh_config.py`).
- 9 colour themes + custom accent / card / background colours (`engine/themes.py`).
- 12 card styles (new: outline, solid, neon, paper, soft, terminal, steps, iconbox). Default for a fresh install is one style (`classic`); `all` uses every style.
- 8 background styles for any colour, in 16:9 and 9:16 (`engine/bg_styles.py`).
- New blocks: `versus`, `matrix`, `tabcard`, `icon3d` (+ SFX), earlier: `icards`, `steplist`, `fixcards`.
- Preview sheets (`engine/ctrlh_preview.py`), `profiles/ctrlh.config.json` (the owner's own profile).
- Skill rewritten around the first-run setup; owner-specific text moved into an "owner profile" section.

## 1.0.0 (2026-10-30)

- Initial kit: engine, two skills, settings, examples, MIT license.
