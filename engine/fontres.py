"""Symbol font resolution (Phase 1.2). The check / cross marks used by badges are not in Cairo (no U+2713/2715) nor in Fira Code (no U+2715),
so the kit needs a font that has them. It used to hard-code the Debian/Ubuntu path of DejaVu Sans Bold, which does not exist on Fedora, macOS or
Windows (OSError while drawing any badge). Resolution order: $CTRLH_FONT_SYMBOL, <assets>/fonts/DejaVuSans-Bold.ttf, well-known system paths,
`fc-match`, a glob under the usual font folders. If nothing is found the marks are drawn as vector strokes, so rendering never fails.
When DejaVu is found at the old path the output is pixel-identical to before."""
import os, glob, subprocess

_NAME = "DejaVuSans-Bold.ttf"
SYSTEM_PATHS = [
    "/usr/share/fonts/truetype/dejavu/" + _NAME,        # Debian / Ubuntu
    "/usr/share/fonts/dejavu-sans-fonts/" + _NAME,      # Fedora / RHEL
    "/usr/share/fonts/dejavu/" + _NAME,                 # Arch (older) / Alpine
    "/usr/share/fonts/TTF/" + _NAME,                    # Arch
    "/usr/share/fonts/ttf-dejavu/" + _NAME,             # Alpine
    "/Library/Fonts/" + _NAME, os.path.expanduser("~/Library/Fonts/" + _NAME),   # macOS
    "C:/Windows/Fonts/" + _NAME, "C:/Windows/Fonts/seguisym.ttf",                # Windows
]
_cache = []


def _assets_dir():
    return os.environ.get("CTRLH_ASSETS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def symbol_font_path():
    """path of a bold font that has the check / cross marks, or None (cached)"""
    if _cache: return _cache[0]
    found = None
    for p in [os.environ.get("CTRLH_FONT_SYMBOL"), os.path.join(_assets_dir(), "fonts", _NAME)] + SYSTEM_PATHS:
        if p and os.path.isfile(p): found = p; break
    if not found:
        try:
            r = subprocess.run(["fc-match", "-f", "%{file}", "DejaVu Sans:bold"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.endswith(".ttf") and "dejavu" in r.stdout.lower() and os.path.isfile(r.stdout): found = r.stdout
        except Exception: pass
    if not found:
        for root in ("/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts")):
            g = glob.glob(os.path.join(root, "**", _NAME), recursive=True)
            if g: found = sorted(g)[0]; break
    _cache.append(found); return found


def symbol(d, xy, sym, size, fill, F):
    """draw a check (U+2713) or cross (U+2715) centred on xy; F(path, size) is the engine's cached font loader"""
    p = symbol_font_path()
    if p: return d.text(xy, sym, font=F(p, size), fill=fill, anchor="mm")
    x, y = xy; r = size * 0.32; w = max(2, int(size * 0.11))
    if sym == "✓": d.line([(x - r, y + r * 0.05), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.75)], fill=fill, width=w, joint="curve")
    else: d.line([(x - r * 0.8, y - r * 0.8), (x + r * 0.8, y + r * 0.8)], fill=fill, width=w); d.line([(x - r * 0.8, y + r * 0.8), (x + r * 0.8, y - r * 0.8)], fill=fill, width=w)
