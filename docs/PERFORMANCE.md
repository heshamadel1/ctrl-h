# Performance (Phase 8)

Measured on the development container (2 CPU cores, Python 3.13, Pillow 12.3, FFmpeg 6.1). Tool: `python3 tests/perf_profile.py <scenes> --fmt wide|reel` (developer only; it samples real frames and reports per-block, per-image-operation, text, memory, encode and multiprocessing numbers).

## What the profile showed
- A 1920x1080 frame took about 150-270 ms depending on the scene. Blocks are cheap (card, sysdiagram, tracks, beam: 1-15 ms per frame each). Text drawing is about 10 ms per frame.
- **One call dominated: the scene-entry zoom** (`anim.py`, `S.transform(... AFFINE, BICUBIC)` on the whole 1920x1080 layer) took about 140 ms, 56% of a typical frame.
- FFmpeg encoding (x264 medium, crf 17) takes about 55-70 ms per frame of CPU on the same two cores that render, so on this machine render and encode compete.
- Multiprocessing: 2 workers gave 1.5-1.65x speed-up (about 75-82% efficiency). Memory is modest: 130-190 MB peak per process.
- Cache: re-rendering an unchanged clip took 0.3-0.6 s instead of 13-21 s.

## What changed
1. `zoom_affine()` computes the zoom only for the part of the output that can receive content (right of / below the content box is skipped). It is **pixel-identical** to the old code: checked on 60 random layers, on 24 frames x 6 real scene/format combinations, and by the golden suite (230/230 exact). Measured gain per frame: showcase wide 211 -> 156 ms, showcase reel 196 -> 142, timeline reel 178 -> 123, entities wide 273 -> 170, beam reel 168 -> 122, sysdiagram wide 207 -> 186.
   A first version that also cropped the left/top edge was faster but differed by one colour level in 4 pixels of one frame, because Pillow accumulates the sample position pixel by pixel; it was rejected because baselines must stay exact.
2. **Cache key now covers the kit's own files**: fonts/backgrounds/images in `assets/` and the content of `profiles/*.json` (themes, video types). Before, editing a theme file or replacing a background served stale cached segments.
3. **Bug fixed: `CTRLH_CACHE=0` failed** (the relative cache folder name "0" broke the FFmpeg concat step). It now renders into a throw-away folder.

## Cache behaviour (tests/cache_test.py)
One chunk per scene plus a tail after T_END. A chunk's key covers the engine code, `CTRLH_*` settings, entities, kit files, and the scene itself plus its neighbours (transitions and camera cross scene boundaries). Verified: second render = all hits and identical file; editing scene 3 re-renders scenes 2 and 3 only; a theme change invalidates everything; `CTRLH_CACHE=0` output equals the cached one.

## Levers not pulled (they change output or quality, so they need your decision)
- Zoom with bilinear instead of bicubic would be faster but changes pixels (would need new baselines).
- A faster x264 preset or higher crf: smaller encode time, different bytes and quality.
- Fewer entity/transition transforms per frame are already minimal (one warp per live entity).
