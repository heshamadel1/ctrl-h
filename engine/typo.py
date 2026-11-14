"""Typography layer (Phase 1.1): mixed Arabic / Latin text, shared by every drawing path.

Finding (see docs/TYPOGRAPHY.md): "وRedis" is NOT a shaping bug. Raqm/FriBiDi/HarfBuzz follow the Unicode bidi algorithm correctly: in an RTL
line the logical first letter (waw) lands on the right of the Latin word, and the isolated waw of the Cairo font looks like a Latin "g", so a
glued waw reads as "Redisg". The fix is typographic, not a re-shaping: where an Arabic LETTER touches a Latin LETTER with no space, the text is
laid out as separate runs with a small gap (GAP_EM of the font size), the same way CSS `text-autospace` separates scripts. No space character
is inserted into the string (so keys, SFX rules, check_voice and captions keep seeing the original text), and strings without such a boundary
go through Pillow untouched (pixel-identical to before).

install() patches ImageDraw.text and FreeTypeFont.getlength once, so all drawing paths (headline, cards, chips, blocks) and all measurements
(wrap, _meas, box widths) agree. Remove the install() call in anim.py to switch the layer off."""
import re
from PIL import ImageDraw, ImageFont

GAP_EM = 0.12
AR_LETTER = "ء-يـٮ-ۓۺ-ۿݐ-ݿ"      # Arabic letters + tatweel (not digits, not punctuation)
_BOUNDARY = re.compile("(?<=[%s])(?=[A-Za-z])|(?<=[A-Za-z])(?=[%s])" % (AR_LETTER, AR_LETTER))
_installed = False
_orig_text = ImageDraw.ImageDraw.text
_orig_len = ImageFont.FreeTypeFont.getlength


def has_boundary(text):
    return isinstance(text, str) and "\n" not in text and _BOUNDARY.search(text) is not None


def chunks(text):
    """logical-order pieces of `text` cut at Arabic-letter | Latin-letter boundaries (one piece when there is no boundary)"""
    return [p for p in _BOUNDARY.split(text) if p] if has_boundary(text) else [text]


def _len(font, text, mode="", direction=None, features=None, language=None):
    # same signature as FreeTypeFont.getlength: Pillow's ImageText calls it with positional arguments
    if direction != "rtl" or not has_boundary(text): return _orig_len(font, text, mode, direction, features, language)
    parts = chunks(text)
    return sum(_orig_len(font, p, mode, direction, features, language) for p in parts) + font.size * GAP_EM * (len(parts) - 1)


def _text(self, xy, text, fill=None, font=None, anchor=None, spacing=4, align="left", direction=None, features=None, language=None,
          stroke_width=0, stroke_fill=None, embedded_color=False, *args, **kwargs):
    if direction != "rtl" or not has_boundary(text):
        return _orig_text(self, xy, text, fill, font, anchor, spacing, align, direction, features, language, stroke_width, stroke_fill, embedded_color, *args, **kwargs)
    f = font or self.getfont(); parts = chunks(text); gap = f.size * GAP_EM
    ws = [_orig_len(f, p, direction="rtl", features=features, language=language) for p in parts]; total = sum(ws) + gap * (len(parts) - 1)
    a = anchor or "la"; h, v = a[0], (a[1] if len(a) > 1 else "a"); x, y = xy
    xl = x - total / 2 if h == "m" else (x if h == "l" else x - total); xr = xl + total
    for p, w in zip(parts, ws):   # first logical piece sits on the right (RTL), the same font for all pieces keeps one baseline
        _orig_text(self, (xr, y), p, fill, font, "r" + v, spacing, align, "rtl", features, language, stroke_width, stroke_fill, embedded_color, *args, **kwargs)
        xr -= w + gap


def install():
    global _installed
    if _installed: return
    ImageDraw.ImageDraw.text = _text; ImageFont.FreeTypeFont.getlength = _len; _installed = True


def uninstall():
    global _installed
    ImageDraw.ImageDraw.text = _orig_text; ImageFont.FreeTypeFont.getlength = _orig_len; _installed = False
