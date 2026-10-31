"""Brand profile loader. Reads ctrlh.config.json and turns its keys into the CTRLH_* environment variables the engine
already understands (a variable you set yourself on the command line always wins).
Search order: $CTRLH_CONFIG, ./ctrlh.config.json, ../ctrlh.config.json, <kit root>/ctrlh.config.json"""
import os, json
KEYMAP = {"theme": "CTRLH_THEME", "accent": "CTRLH_ACCENT", "card_color": "CTRLH_CARD_COLOR", "bg_color": "CTRLH_BG_COLOR",
          "card_styles": "CTRLH_CARD_STYLES", "bg_style": "CTRLH_BG_STYLE", "background_file": "BGFILE", "assets": "CTRLH_ASSETS",
          "font_ar": "CTRLH_FONT_AR", "font_latin": "CTRLH_FONT_LATIN", "signoff_1": "CTRLH_SIGNOFF_1", "signoff_2": "CTRLH_SIGNOFF_2",
          "label_ok": "CTRLH_LABEL_OK", "label_wrong": "CTRLH_LABEL_WRONG", "label_chapter": "CTRLH_LABEL_CHAPTER",
          "out_w": "OUT_W", "subscribe_t": "SUB_T", "follow_t": "FOL_T"}
PATHKEYS = ("background_file", "assets", "font_ar", "font_latin")
CONFIG = {}; CONFIG_PATH = None
def _find():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.environ.get("CTRLH_CONFIG"), "ctrlh.config.json", "../ctrlh.config.json", os.path.join(here, "..", "ctrlh.config.json")):
        if p and os.path.isfile(p): return os.path.abspath(p)
def load():
    global CONFIG, CONFIG_PATH
    p = _find()
    if not p: return
    try: CONFIG = json.load(open(p, encoding="utf-8"))
    except Exception: return
    CONFIG_PATH = p; base = os.path.dirname(p)
    for k, env in KEYMAP.items():
        v = CONFIG.get(k)
        if v in (None, "", []): continue
        if isinstance(v, list): v = ",".join(str(x) for x in v)
        if k in PATHKEYS and not os.path.isabs(str(v)): v = os.path.join(base, str(v))
        os.environ.setdefault(env, str(v))
load()
