"""Design tokens: spacing, radius, type sizes and safe margins shared by the NEW blocks (er, http, diff, queue, recap).
Colours stay in themes.py (theme / accent / card colour). Override any value with a JSON file: CTRLH_TOKENS=/path/tokens.json
e.g. {"radius": {"card": 30}, "safe": {"x": 80}}. Older blocks keep their own numbers (not migrated yet)."""
import os, json
TOKENS = {
    "spacing": {"sm": 8, "md": 16, "lg": 24},
    "radius": {"card": 24, "pill": 999},
    "safe": {"x": 60, "bottom": 40},                      # margins kept free around content
    "type": {"headline": 64, "section": 48, "support": 34, "label": 26, "code": 30},   # text hierarchy (px, 16:9)
}
_p = os.environ.get("CTRLH_TOKENS", "")
if _p and os.path.exists(_p):
    try:
        for k, v in json.load(open(_p)).items(): TOKENS.setdefault(k, {}).update(v)
    except Exception as e: print("tokens: ignored", _p, e)
