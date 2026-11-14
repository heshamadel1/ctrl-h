"""Demo scene file for the 8 flow / system blocks (titlevs, split, chain, hub, pipeline, deviceflow, codeann, flowmini).
Reuses the gallery definitions (docs_gallery_features.py) and moves their local times to the scene's place on the timeline.
Lint only:  python3 ../engine/lint.py v9_flow_scenes --sheet sheet.png      Full build:  python3 ../engine/build.py v9_flow_scenes --vo some.wav"""
import copy
from docs_gallery_features import F

def _d(it, o, keys=("t",)):
    for k in keys:
        if k in it: it[k] += o
def _tup(lst, o): return [(x[0] + o,) + tuple(x[1:]) for x in lst]

def shift(b, o):
    k = b["k"]; b = copy.deepcopy(b); _d(b, o, ("t", "t0", "t1", "t_unlock", "q_t"))
    if k == "card": return b
    if k == "split":
        for P in b["panels"]:
            for sv in P["services"]: sv["t"] += o
            P["events"] = _tup(P.get("events", []), o)
    elif k == "chain":
        for s in b["steps"]:
            s["t"] += o
            if s.get("err"): s["err"] = (s["err"][0] + o, s["err"][1])
    elif k == "hub":
        b["hub"]["t"] += o
        for key in ("actions", "spokes"):
            for it in b[key]: it["t"] += o
    elif k == "pipeline":
        for nd in b["nodes"]:
            nd["t"] += o
            if nd.get("badge"): nd["badge"] = (nd["badge"][0] + o,) + tuple(nd["badge"][1:])
    elif k == "deviceflow":
        if b["phone"].get("press_t"): b["phone"]["press_t"] += o
        b["api"]["t"] += o
        for s in b["steps"]: s["t"] += o
    elif k == "codeann":
        b["lines"] = _tup(b["lines"], o); b["squiggle"] = _tup(b.get("squiggle", []), o); b["tags"] = _tup(b.get("tags", []), o)
        for key in ("counter", "label", "cap"):
            if b.get(key): b[key] = (b[key][0] + o,) + tuple(b[key][1:])
        if b.get("bar"): b["bar"] = (b["bar"][0] + o, b["bar"][1] + o, b["bar"][2])
    elif k == "flowmini":
        for it in b["items"]: it["t"] += o
    return b

NAMES = ["titlevs", "split", "chain", "hub", "pipeline", "deviceflow", "codeann", "flowmini"]
SC = []; T0 = 0.0; SD = 9.0
for i, n in enumerate(NAMES):
    head, blocks, tf, extra = F[n]
    SC.append(dict(style="classic", t0=T0, t1=T0 + SD, stage=i // 4, head=head, head_t=T0 + .1, blocks=[shift(b, T0) for b in blocks], **extra)); T0 += SD
STAGES = ["Flow blocks", "More blocks"]; TECH = ["JavaScript", "Fetch"]
DUR = T0 + 8; T_END = DUR - 8; TAG1 = T_END + 1.5; TAG2 = T_END + 3.0
SUB_T = False; FOL_T = False
