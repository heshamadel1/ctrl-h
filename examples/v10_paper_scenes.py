"""Demo of the optional paper look (scene key paper=True): quote, chatwin, bars, skeleton, filegrid + bigcount.
Lint:  python3 ../engine/lint.py v10_paper_scenes --sheet sheet.png     Build:  python3 ../engine/build.py v10_paper_scenes --vo some.wav"""
from docs_gallery_features import F
from v9_flow_scenes import shift
NAMES = ["quote", "chatwin", "bars", "skeleton", "filegrid"]
SC = []; T0 = 0.0; SD = 9.0
def _sh(b, o):
    b = shift(b, o); k = b["k"]
    if k == "quote": b["hi"] = [(h[0] + o, h[1]) for h in b["hi"]]
    elif k == "chatwin": b["prompt_t"] += o; b["code"] = [(c[0] + o, c[1]) for c in b["code"]]
    elif k == "bars":
        for c in b["cards"]: c["t"] += o
    elif k == "skeleton": b["t0"] += o; b["t1"] += o
    elif k == "bigcount": b["t0"] += o; b["t1"] += o
    elif k == "filegrid": b["t0"] += o; b["t1"] += o; b["missing"] = (b["missing"][0] + o, b["missing"][1]); b["active"] = [(a[0] + o, a[1]) for a in b["active"]]
    return b
for i, n in enumerate(NAMES):
    head, blocks, tf, extra = F[n]
    SC.append(dict(t0=T0, t1=T0 + SD, stage=0, head=head, head_t=T0 + .1, blocks=[_sh(b, T0) for b in blocks], **extra)); T0 += SD
STAGES = ["Paper look"]; TECH = ["JavaScript", "Fetch"]
DUR = T0 + 8; T_END = DUR - 8; TAG1 = T_END + 1.5; TAG2 = T_END + 3.0
SUB_T = False; FOL_T = False
