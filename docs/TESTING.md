# Testing the Kit (developers only)

**Standard users never need this page.** Making a video needs only the standard workflow (see GETTING_STARTED.md): no tests, no terminal tools beyond what that workflow already uses, no agent.

## Two levels
| Level | For | What |
|---|---|---|
| Standard | everyone | `python3 engine/smoke.py` (compile, lint, one frame per theme x format, SFX, docs links). It proves frames can be made, not that they look right. |
| Developer | people changing the engine | `tests/golden/golden.py`: compares real frames with human-approved PNGs. Works the same for a person at a terminal, Claude Code or Codex. Nothing here is required to use the Kit. |

## Golden frames in one minute
- **What it does:** renders a fixed list of frames (230 baseline frames, 0 diagnostic since the waw defect was resolved in Phase 1, wide and reel, 3 themes; list in `tests/golden/manifest.json`) in a clean subprocess and compares them with approved baselines.
- **Why:** smoke tests cannot see a stray Arabic glyph, a moved card or a changed easing curve.
- **How the comparison works:** same environment fingerprint -> exact pixel hash, any difference fails. Different environment (Pillow / FreeType / fonts) -> `UNVERIFIED-DIFF` with diff images, never an automatic pass. Tolerance exists only per content type, only after calibration proves it (`calibration.json`), and PSNR/SSIM can never allow a pass.
- **Isolation:** no `ctrlh.config.json` can leak in (`CTRLH_CONFIG` points to an empty file, clean environment, empty working directory); `isolation-test` proves it with decoy configs.
- **Known defects** (`known_defects.json`) are shown in diagnostic frames only: `XFAIL` = still exactly the recorded defective render, `XFAIL-CHANGED` = the frame changed, a human must look. They never become baselines, and a scanner refuses defect text inside baseline scenes.
- **Approval:** `capture` and `check` never write to `baselines/`. `review` prints an approval code that is bound to the exact pixels; `approve` refuses a wrong code. The code must come from the person who looked at the images.

## Workflow
1. Change something. 2. `check --against baselines` (or `--against provisional` while approved baselines do not exist yet). 3. Look at `tests/golden/out/review.html` and `out/diff/`. 4. If the change is intended and the images are right, a human runs `review` then `approve`.
Tier C: `golden.py video-check` renders a 2 s clip through the real encoder and verifies it with ffprobe.

## Limits
Baselines belong to the environment that made them (fingerprint in `baselines.lock.json`). Frame checks do not cover audio. Zip: build the release zip without `tests/` and run `golden.py verify-zip`.

## With Claude Code / Codex (optional)
Give the agent this page and the command list in `tests/golden/README.md`. It may run `check` and `selftest`; it must not approve baselines for you.

## Typography matrix (Phase 1)
`python3 tests/typography_matrix.py` (no video, ~10 s): 14 Arabic / Latin / mixed strings in the Wide and Reel card sizes. It proves that strings without an Arabic-letter|Latin-letter boundary are pixel-identical with the typography layer on and off, that boundary strings get a visible gap, that measured width equals drawn width, that card wrapping fits, and that the symbol-font fallback draws. Details of the finding: [TYPOGRAPHY.md](TYPOGRAPHY.md).
