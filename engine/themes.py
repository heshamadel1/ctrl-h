"""Colour themes: accent colour, card colour and background base colour (all RGB).
Pick one with CTRLH_THEME=<name> (or "theme" in ctrlh.config.json); CTRLH_ACCENT / CTRLH_CARD_COLOR / CTRLH_BG_COLOR still override single values."""
THEMES = {
    "orange": dict(accent=(255, 138, 17), card=(24, 26, 31), base=(13, 14, 16), note="orange on black (Ctrl + H original)"),
    "cyan":   dict(accent=(34, 211, 238), card=(17, 28, 38), base=(8, 14, 20), note="cyan on deep navy"),
    "blue":   dict(accent=(76, 141, 255), card=(18, 24, 40), base=(9, 12, 22), note="electric blue"),
    "violet": dict(accent=(167, 139, 250), card=(26, 22, 40), base=(14, 11, 22), note="violet on dark purple"),
    "pink":   dict(accent=(244, 114, 182), card=(36, 20, 30), base=(20, 10, 16), note="pink on dark plum"),
    "red":    dict(accent=(255, 92, 92), card=(34, 20, 22), base=(18, 10, 11), note="red on dark wine"),
    "gold":   dict(accent=(250, 204, 21), card=(32, 28, 16), base=(16, 14, 8), note="gold on dark olive"),
    "green":  dict(accent=(52, 211, 153), card=(16, 32, 28), base=(8, 16, 14), note="emerald on dark green"),
    "mono":   dict(accent=(229, 231, 235), card=(28, 28, 30), base=(12, 12, 13), note="white and grey, no colour"),
}
DEFAULT = "orange"
def hexs(c): return "#%02X%02X%02X" % tuple(c)
