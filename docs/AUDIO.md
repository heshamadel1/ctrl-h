# Audio: sound events and loudness (Phase 7)

## Sound events (engine/audio_events.py)
All automatic sound effects come from ONE function, `audio_events.collect(SC, ...)`, which reads the same scene data and times the animation uses. It returns plain events `(t, kind, cat, gain, src, dur, name)`; `make_audio_lib.py` only turns them into sound. A check on four existing example videos produced byte-identical SFX tracks before and after this change.

Event kinds: scene_cut, chapter_change, item, ok, error, key_hit, shock, mystery, strike, counter, typing, node (system diagram), connect (beam connection starts: chime), razor (timeline split), clip_remove, track_toggle, morph / entity_in (persistent entities). `python3 engine/audio_events.py my_scenes.py` prints the timeline of events without making audio.

Control:
- `SFX_EVENTS = {"item": False, "scene_cut": 0.5}` in the scene file (False = off, number = level multiplier).
- Scene key `"sfx": False` (silent scene) or `{"off": ["item"], "gain": {"typing": 0.5}}`.
- Block key `"sfx": False` or a number.
- `CTRLH_SFX_OFF="item,scene_cut"` or config key `sfx_off`.
- Duplicates: the same kind + sound within 0.02 s is one event. A scene whose transition is `none` gets no cut sound.
Variation: sound files are picked by rotation without repeating the previous one, with a fixed seed, so a re-render sounds the same. The razor event uses `assets/sfx/razor_01_cut.mp3`, a short noise burst generated for the kit (no third-party licence); replace the file to change it.

## Loudness (engine/loudness.py)
`python3 engine/loudness.py measure|check|normalize|balance|silence ...` (details in the file header). Measurement is FFmpeg ebur128 (integrated LUFS, loudness range, true peak).
**The build never changes loudness unless you ask.** It always prints one `LOUDNESS` line per output. To normalise set `CTRLH_LOUDNESS` (config key `loudness`) to `youtube`, `reels`, `podcast`, `broadcast` or `"<LUFS>,<dBTP>"`; the build then applies gain and a true-peak limiter (re-measured until within 0.3 LU).
Preset values (-14 LUFS for YouTube and short-form social, -16 podcasts, -23 broadcast, true peak -1 dBTP) are reference values, not rules: platforms change them. Pick by where you publish and confirm by ear on phone speakers and headphones. The existing mix (voice, music ducking by the voice, limiter) is untouched; normalisation is a last step on the finished file.
Voice/effects balance: `balance VOICE.wav SFX.wav` reports the difference; effects are sparse so treat it as a rough guide.

Tests (developer only): `python3 tests/audio_events_test.py`.
