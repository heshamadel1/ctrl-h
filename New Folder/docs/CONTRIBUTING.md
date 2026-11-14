# Contributing

1. Fork, create a branch, change one thing.
2. Run `python3 engine/smoke.py` (compile, lint every example, a frame per theme x format, SFX, docs links, setup; no video is rendered). It must print `SMOKE OK`. Look at frames of the three themes for anything visual.
3. Names: use the descriptive card names (`plain_dark`, ...). Old names are legacy aliases only (see CATALOG).
4. A new block needs: `draw_<kind>`, `EXTRA_H`, a SFX rule, a LINT rule if it has limits, a demo in `examples/`, an entry in `docs/FEATURES.md` and `docs/CATALOG.md`.
5. A new sound goes in `assets/sfx/` as `<category>_<NN>_<name>.mp3` and in `docs/SOUNDS.md` / `manifest.json`.
6. Update `CHANGELOG.md` and keep `VERSION`, README and `RELEASE_NOTES.md` in step.
7. Do not add the channel's identity to the generic engine; it lives in `ctrlh.config.json` and the owner profile.
Code: MIT. The Ctrl + H name and logo are brand assets.
