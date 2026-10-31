"""First-run setup: writes ctrlh.config.json (your identity + look).
Interactive:      python3 engine/ctrlh_setup.py
Non-interactive:  python3 engine/ctrlh_setup.py --channel "My Channel" --theme cyan --card-styles glass,neon --bg-style hex --yes
(Claude asks the same questions in chat and calls this script with the answers.)"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import themes, bg_styles
CARD_STYLES = ["classic", "proposed", "glass", "numbers", "outline", "solid", "neon", "paper", "soft", "terminal", "steps", "iconbox"]
def ask(q, default=""):
    try: v = input("%s%s: " % (q, " [%s]" % default if default else "")).strip()
    except EOFError: v = ""
    return v or default
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel"); ap.add_argument("--handle"); ap.add_argument("--platforms"); ap.add_argument("--language"); ap.add_argument("--topics")
    ap.add_argument("--theme"); ap.add_argument("--accent"); ap.add_argument("--card-color"); ap.add_argument("--bg-color")
    ap.add_argument("--card-styles"); ap.add_argument("--bg-style"); ap.add_argument("--signoff1"); ap.add_argument("--signoff2")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "ctrlh.config.json")); ap.add_argument("--yes", action="store_true")
    a = ap.parse_args(); inter = not a.yes and sys.stdin.isatty()
    g = lambda v, q, d="": v if v is not None else (ask(q, d) if inter else d)
    cfg = {"version": 2}
    cfg["channel_name"] = g(a.channel, "Channel / brand name", "My Channel")
    cfg["handle"] = g(a.handle, "Handle (e.g. @mychannel)", "")
    cfg["platforms"] = [x.strip() for x in g(a.platforms, "Platforms (comma separated)", "YouTube,TikTok,Instagram,Facebook").split(",") if x.strip()]
    cfg["language"] = g(a.language, "Voiceover language", "English")
    cfg["topics"] = [x.strip() for x in g(a.topics, "Content topics (comma separated)", "Programming").split(",") if x.strip()]
    if inter: print("\nThemes: " + ", ".join(themes.THEMES))
    th = g(a.theme, "Colour theme", "orange").lower(); cfg["theme"] = th if th in themes.THEMES else "orange"
    if a.accent: cfg["accent"] = a.accent
    if a.card_color: cfg["card_color"] = a.card_color
    if a.bg_color: cfg["bg_color"] = a.bg_color
    if inter: print("\nCard styles: " + ", ".join(CARD_STYLES) + "  (or: all)")
    cs = g(a.card_styles, "Card style(s), comma separated", "classic").replace(" ", "").lower()
    cfg["card_styles"] = "all" if cs == "all" else ",".join(x for x in cs.split(",") if x in CARD_STYLES) or "classic"
    if inter: print("\nBackgrounds: " + ", ".join(bg_styles.STYLES))
    bs = g(a.bg_style, "Background style", "circuit").lower(); cfg["bg_style"] = bs if bs in bg_styles.STYLES else "circuit"
    cfg["signoff_1"] = g(a.signoff1, "End-card line 1", "Think Deeper."); cfg["signoff_2"] = g(a.signoff2, "End-card line 2", "Build Smarter.")
    out = os.path.abspath(a.out); json.dump(cfg, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False); print("\nsaved", out)
    assets = os.path.join(HERE, "..", "assets"); miss = [n for n in ("logo_ch.png", "mono.png") if not os.path.isfile(os.path.join(assets, n))]
    if miss: print("Still to add (placeholders are used until then): " + ", ".join("assets/" + m for m in miss))
if __name__ == "__main__": main()
