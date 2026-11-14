# "Beam" block (loaded by anim.py after blocks_sysdiagram.py): connected nodes with animated connection lines and travelling light beams.
# Use it for request flow (frontend -> API -> DB), service communication, data flow, architecture. Geometry lives in paths.py.
#
#   {"k": "beam", "t": 0.2, "h": 700,                              # h optional (default 620 wide / 1000 reel)
#    "nodes": {"fe": {"name": "Frontend", "pos": (.12, .5), "tone": "blue", "t": 0.2},
#              "api": {"name": "API", "pos": (.5, .5), "tone": "orange", "t": 0.5},
#              "db": {"name": "Database", "pos": (.88, .5), "tone": "green", "t": 0.8, "until": 9.0}},     # until: optional fade-out
#    "paths": [{"from": "fe", "to": "api", "t": 1.2, "dur": 0.9,       # t: when the line starts to draw, dur: seconds one beam takes
#               "style": "both",                                      # draw (line only) | beam (pulse only) | both (line, then pulses)  [default both]
#               "dir": "fwd",                                         # fwd | back | both (alternating)
#               "pulses": 2, "loop": False, "bend": 0.0,              # number of pulses, repeat forever, curve (+ left, - right of travel)
#               "tone": "orange", "label": "POST /order", "dash": False, "arrow": True}]}
# Same normalised positions in 16:9 and 9:16. Pure function of time (no state).
import paths as _pa
_BM_DRAW = 0.45   # seconds to draw a connection line before its first beam leaves
def _bm_rects(b, box, nw, nh):
    x0, y0, x1, y1 = box; rect = {}
    for nid, nd in b.get("nodes", {}).items():
        cx = x0 + 30 + (x1 - x0 - 60) * nd["pos"][0]; cy = y0 + 30 + (y1 - y0 - 60) * nd["pos"][1]; rect[nid] = (cx - nw / 2, cy - nh / 2, cx + nw / 2, cy + nh / 2)
    return rect
def draw_beam_block(d, box, b, t, k):
    if t < b["t"]: return
    layer = d._image; nw, nh = (230, 70) if WIDE else (196, 84); fs = 26 if WIDE else 28
    rect = _bm_rects(b, box, nw, nh); nodes = b.get("nodes", {})
    def node_a(nid):
        nd = nodes[nid]; a = E(t, nd.get("t", b["t"]), 0.35)
        if nd.get("until") is not None: a *= 1 - prog(t, nd["until"], nd["until"] + 0.3)
        return a
    for pth in b.get("paths", []):
        fr, to = pth["from"], pth["to"]
        if fr not in rect or to not in rect: continue
        path = _pa.connect(rect[fr], rect[to], pth.get("bend", 0.0)); col = _sdc(pth.get("tone", "orange")); na = min(node_a(fr), node_a(to)); t0 = pth["t"]
        if na <= 0.01 or t < t0: continue
        style = pth.get("style", "both"); dur = max(0.2, pth.get("dur", 0.9)); wd = 4 if WIDE else 5
        if style in ("draw", "both"):
            p = ss(prog(t, t0, t0 + _BM_DRAW)); _pa.draw_path(layer, path, p, color=lerp(_SD_PANEL, col, 0.55) if style == "both" else col, width=wd, alpha=na, dash=(14, 9) if pth.get("dash") else None, arrow=bool(pth.get("arrow", True)) and p >= 0.98)
        if style in ("beam", "both"):
            start = t0 + (_BM_DRAW if style == "both" else 0.0); n = max(1, int(pth.get("pulses", 1))); gap = dur * 0.55; loop = bool(pth.get("loop")); mode = pth.get("dir", "fwd"); total = n * gap
            q = t - start
            if q >= 0:
                cyc = (q % (total + dur * 0.6)) if loop else q; ks = range(n)
                for i in ks:
                    f = (cyc - i * gap) / dur
                    if 0 <= f <= 1.0:
                        fwd = True if mode == "fwd" else False if mode == "back" else (i % 2 == 0)
                        _pa.draw_beam(layer, path, ss(f) if pth.get("ease") else f, tail=0.22, color=lerp(col, (255, 255, 255), 0.3), width=wd + 5, glow=14 if WIDE else 16, alpha=na * (1.0 if f < 0.85 else (1 - f) / 0.15), fwd=fwd)
        if pth.get("label") and t >= t0 + (_BM_DRAW if style != "beam" else 0):
            la = E(t, t0 + _BM_DRAW, 0.3) * na; mx, my = path.point_at(.5); ly = min(my - 26, rect[fr][1] - 22, rect[to][1] - 22) if abs(rect[fr][1] - rect[to][1]) < 4 else my - 26; _bt(d, (mx, ly), pth["label"], 21 if WIDE else 24, A(col, la))
    for nid, r in rect.items():
        a = node_a(nid)
        if a <= 0.01: continue
        nd = nodes[nid]; col = _sdc(nd.get("tone", "orange")); cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2; sc = 0.92 + 0.08 * a
        rr = (cx - nw * sc / 2, cy - nh * sc / 2, cx + nw * sc / 2, cy + nh * sc / 2)
        d.rounded_rectangle(rr, 18, fill=A(lerp(_SD_PANEL, col, .12), a), outline=A(col, a), width=3)
        _bt(d, (cx, cy), nd.get("name", nid), fs, A((14, 14, 12) if LIGHT else (245, 245, 245), a))
EXTRA_H["beam"] = lambda blk, w: blk.get("h", 620 if WIDE else 1000)
DRAW["beam"] = draw_beam_block
