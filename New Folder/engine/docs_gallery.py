"""Render one reference picture per feature: python3 engine/docs_gallery.py [out_dir] [name ...]   (from the kit root)
Note: the kit ships only contact sheets (docs/images/blocks-sheet-*.png, cards-*.png); this script makes single pictures for your own use.
Uses examples/docs_gallery_features.py. A feature whose scene raises an error is reported and skipped."""
import sys, os, importlib, traceback
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path[:0] = [os.path.join(root, "engine"), os.path.join(root, "examples")]
os.environ.setdefault("CTRLH_CARD_STYLES", "classic"); os.environ.setdefault("CTRLH_DIMS", "0")
import ctrlh_config
from anim import Video, FPS
from PIL import Image
G = importlib.import_module("docs_gallery_features").F
out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1] in G else os.path.join(root, "docs", "images"); os.makedirs(out, exist_ok=True)
names = [a for a in sys.argv[1:] if a in G] or list(G)
for n in names:
    head, blocks, tf, extra = G[n]
    try:
        sc = dict(style="classic", t0=0, t1=8, stage=0, head=head, head_t=.1, blocks=blocks); sc.update(extra)
        V = Video([sc], ["Demo"], 8.0, 100.0, 101.0, 102.0, ["JavaScript", "Fetch", "React", "Next.js"], False, False)
        Image.fromarray(V.frame(int(tf * FPS))).save(os.path.join(out, "feat-%s%s.png" % (n.replace("_", "-"), "-9x16" if os.environ.get("FMT") == "reel" else "")))
        print("ok", n)
    except Exception as e:
        print("FAIL", n, repr(e)[:160])
