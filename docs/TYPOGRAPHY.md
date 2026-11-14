# Typography: mixed Arabic / Latin text (developer reference)

## Finding: "وRedis" is not a shaping bug
The v2.2.0 audit reported that `وRedis` is drawn as "Redisg". Investigated (Raqm 0.10.5, FriBiDi 1.0.13, HarfBuzz 14.2.1, FreeType 2.14.3):
- Shaping and bidi are correct. In an RTL line the logical first letter (waw) is placed on the **right** of the Latin word, exactly as the Unicode bidi algorithm requires, and Cairo's isolated waw looks like a Latin "g". A reader sees "Redis g" and reads it right-to-left as "و Redis". All three drawing paths (headline, card, shock/chips) produced the same picture, because they all go through the same Pillow call.
- So re-shaping or fixing bidi would be wrong. What is missing is typographic separation between the two scripts.

## Fix: `engine/typo.py`
Where an Arabic **letter** touches a Latin **letter** with no space, the text is laid out as separate runs with a small gap (0.12 em), like CSS `text-autospace`. No space character is added to the string, so SFX rules, `check_voice`, captions and card keys keep seeing the original text. Strings without such a boundary go through Pillow unchanged (pixel-identical). `ImageDraw.text` and `FreeTypeFont.getlength` are patched once, so drawing and measuring (wrap, `_meas`, box widths) always agree. Remove `typo.install()` in `anim.py` to switch it off.

Details: digits and punctuation are not boundaries; the non-breaking space between an Arabic prefix and a Latin word (`الـ JWT`) still works as before; `getlength` has the same signature as Pillow's (Pillow's `ImageText` calls it with positional arguments).

## Text measurement
`_meas` takes the wider of "whole line in Cairo" and "tokens as drawn" on purpose (conservative: a card must never overflow). `_tok_w` is the exact drawn width. This is by design, not a defect; it only makes some cards wrap one word earlier than strictly necessary.

## Symbol font (`engine/fontres.py`)
Cairo has no check / cross marks (U+2713 / U+2715) and Fira Code has no cross, so badges need DejaVu Sans Bold. The path used to be hard-coded for Debian/Ubuntu (failure with `OSError` on Fedora, macOS, Windows). Now: `CTRLH_FONT_SYMBOL`, `assets/fonts/DejaVuSans-Bold.ttf`, well-known system paths, `fc-match`, a glob; if nothing exists the marks are drawn as vector strokes, so rendering never fails. With DejaVu at the old path the output is pixel-identical.

## Tests
`python3 tests/typography_matrix.py` and the golden case `G05_rtl_matrix` (Arabic only, English only, mixed, waw + Latin, numbers, punctuation, inline code, multi-line, LTR-style English; wide and reel).
