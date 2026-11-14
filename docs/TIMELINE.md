# Editing timeline block: `tracks` (engine/blocks_timeline.py)

Reusable component for explaining editing and production workflows by animation. Full spec in the header of `engine/blocks_timeline.py`; example: `examples/timeline_demo_scenes.py`.

Supported: video / audio / subtitle tracks, clips with labels and tones, **waveforms** (deterministic per clip id), **playhead** keyframes, **trim and move** (`edits`, eased), **razor/split** (flash line, two halves, optional slide of the right half), **keyframe diamonds**, **track on/off** (dimmed, eased), **clip removal** (`until`), appearance times per track item.

Rules: everything is a pure function of time; same drawing in 16:9 and 9:16 (track height adapts); `lint.py` checks track kind, clip fields, clips past `dur` and malformed `edits`.
Limits: one split per clip; waveform is stylised (not read from real audio); clips on one track are not auto-prevented from overlapping (lint does not check it).

Test (developer only): `python3 tests/timeline_test.py`.
