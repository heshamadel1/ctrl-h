# Transition demo: every transition kind once. Scene i enters with the kind named in its headline (trans_in) and leaves with the next scene's kind.
# Run:  python3 ../engine/build.py transitions_demo_scenes --out out   (no voiceover needed for a silent preview: use render.py frames)
# Per scene:  transition="fade" | "slide:left" | {"kind": "wipe_h", "dir": "right", "dur": 0.5, "ease": "out_cubic"}   (see docs/TRANSITIONS.md)
KINDS = [("classic", None), ("fade", None), ("slide", "left"), ("push", "up"), ("wipe_h", "right"), ("wipe_v", "down"), ("zoom", None), ("blur", None)]
DUR = 3.0 * len(KINDS); T_END, TAG1, TAG2 = DUR - 0.5, DUR - 0.4, DUR - 0.1
STAGES = ["transitions"]; TECH = ["Video"]
def card(t, text, ok=None): return {"k": "card", "t": t, "text": text, "ok": ok}
SC = []
for i, (kind, d) in enumerate(KINDS):
    spec = kind if d is None else {"kind": kind, "dir": d, "dur": 0.5}
    sc = dict(style="plain_dark", t0=3.0 * i, t1=3.0 * i + 3.0, stage=0, head=kind + (" / " + d if d else ""), head_t=3.0 * i,
              blocks=[card(3.0 * i, "المشهد " + str(i + 1), True), card(3.0 * i, "Transition: " + kind, None)])
    if i > 0 and kind != "classic": sc["trans_in"] = spec
    SC.append(sc)
