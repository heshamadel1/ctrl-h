"""Colour themes: accent colour, card colour and background base colour (all RGB).
Pick one with CTRLH_THEME=<name> (or "theme" in ctrlh.config.json); CTRLH_ACCENT / CTRLH_CARD_COLOR / CTRLH_BG_COLOR still override single values."""
THEMES = {
    "orange": dict(accent=(255, 138, 17), card=(24, 26, 31), base=(13, 14, 16), note="orange on black (Ctrl + H original)"),
    "paper_orange": dict(accent=(255, 138, 17), card=(251, 248, 238), base=(242, 237, 224), light=True, bg="paper", note="LIGHT paper with an orange highlighter"),
    "soft_cream": dict(accent=(255, 138, 17), card=(255, 253, 249), base=(253, 247, 237), light=True, soft=True, bg="cream", note="SOFT cream: white rounded cards, light shadow, orange glow, dark logo"),
}
DEFAULT = "orange"
# `bg`: signature background style of a theme (used when config bg_style is the default hud_live; set "bg_style_locked": true to keep your own)
def hexs(c): return "#%02X%02X%02X" % tuple(c)
