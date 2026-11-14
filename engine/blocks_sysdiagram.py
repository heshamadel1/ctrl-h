# "System diagram" block (loaded by anim.py after blocks_hud.py): one STATEFUL diagram that changes over time without any cut.
#   sysdiagram   nodes, links, DB table group, transaction pills, envelopes, ledger chips, stickers, stage pill.
# Same drawing in the 3 themes (orange / paper_orange / soft_cream); 16:9 and 9:16 use the same normalised positions.
#
#   {"k": "sysdiagram", "t": 0.2, "h": 1150,                      # h: optional height (default 660 wide / 1150 reel)
#    "stages":  [(0.1, "1/5 DUAL WRITE"), (4.0, "2/5 GHOST EVENT")],          # stage pill (swaps with a pop)
#    "resets":  [4.0, 8.4],                                                  # at these times pills / badges / stickers / envelopes of the earlier stage fade out
#    "nodes":   {"svc": {"name": "Order Service", "icon": "cart", "tone": "orange", "pos": (.5, .08), "t": 0.1,
#                        "until": 8.2,                            # optional: node fades out at this time
#                        "state": [(1.2, "err")],                 # idle | ok | err | hot | ghost  (outline colour; pulses on change)
#                        "badges": [(1.2, "err")],                # ok | err | ghost | lock   (corner badge, pops in)
#                        "pills": [(1.4, "crash", "red:outline")]}},          # (t, text, tone[:outline][, t_end])
#    "links":   [("svc", "db"), ("svc", "broker", "dash")],
#    "table":   {"t": 8.0, "pos": (.04, .17, .96, .37), "name": "DB",
#                "cols": [{"key": "orders", "tone": "orange"}, {"key": "outbox", "tone": "purple"}],
#                "rows": [{"t": 8.3, "id": "#41", "orders": [(8.3, "placed")], "outbox": [(8.3, "new"), (9.0, "sent")]}]},
#    "locks":   [(9.0, 10.4, 1)],                                  # (t0, t1, row index): dashed selection + lock, check at t1
#    "txn":     [(8.6, 10.6, "BEGIN", "svc"), (10.4, 12.0, "COMMIT", "svc")],  # BEGIN / COMMIT / ROLLBACK pill beside a node
#    "env":     [(14.0, ["tbl", "broker", "email"], "purple")],     # envelope travelling along node ids ("tbl" = the table); ("...", "purple", 0.55) stops at 55% with an X
#    "ledger":  {"email": [(15.0, "#41"), (16.0, "#42")]},          # ✓ strip of chips under a node
#    "stickers": [(2.4, "Out of sync", "pink", 4.0)]}              # tilted result sticker at the bottom
# Sounds: make_audio_lib.py places them automatically (stage whoosh, ticks, success/error, envelope whoosh, sticker pop).
_SDT = {"orange": OR, "red": (255, 96, 96), "green": (140, 215, 60), "teal": (40, 205, 185), "blue": (70, 150, 255), "purple": (160, 120, 255), "pink": (255, 95, 155), "gray": (150, 156, 168)}
def _sdc(name):
    c = _SDT.get(name, OR if name == "orange" else (150, 156, 168))
    return tuple(int(v * 0.74) for v in c) if LIGHT else c
_fk = 1.0 if WIDE else 1.2
_SD_PANEL = (255, 253, 247) if LIGHT else tuple(min(255, v + 9) for v in CARDC)
_SD_NODE = (255, 255, 255) if LIGHT else (19, 21, 26)
_SD_LINE = (150, 146, 134) if LIGHT else (74, 78, 88)


_sd_pop = motion.back_pop   # moved to engine/motion.py (same formula)


def _sd_win(t, te, end, resets):
    """(alpha, scale) of an item that pops in at te and leaves at `end` or at the next reset after te"""
    a, s = _sd_pop(t, te)
    if a <= 0: return 0.0, 0.0
    cands = [r for r in (resets or []) if r > te + 0.05] + ([end] if end else [])
    out = min(cands) if cands else None
    if out is not None: a *= 1 - prog(t, out, out + 0.3)
    return a, s


def _sd_icon(d, kind, cx, cy, s, col, al, ink=None):
    lw = max(2, int(s * 0.16)); c = A(col, al); ink = ink or (10, 11, 13)
    if kind == "cart":
        d.line([(cx - s, cy - .8 * s), (cx - .6 * s, cy - .8 * s), (cx - .3 * s, cy + .35 * s), (cx + .8 * s, cy + .35 * s)], fill=c, width=lw, joint="curve")
        d.polygon([(cx - .5 * s, cy - .5 * s), (cx + .9 * s, cy - .5 * s), (cx + .7 * s, cy + .2 * s), (cx - .3 * s, cy + .2 * s)], outline=c, width=lw)
        for x in (-.15, .6): d.ellipse((cx + x * s - .17 * s, cy + .8 * s - .17 * s, cx + x * s + .17 * s, cy + .8 * s + .17 * s), fill=c)
    elif kind == "db":
        d.ellipse((cx - .8 * s, cy - .95 * s, cx + .8 * s, cy - .3 * s), outline=c, width=lw)
        d.line([(cx - .8 * s, cy - .62 * s), (cx - .8 * s, cy + .62 * s)], fill=c, width=lw); d.line([(cx + .8 * s, cy - .62 * s), (cx + .8 * s, cy + .62 * s)], fill=c, width=lw)
        d.arc((cx - .8 * s, cy - .3 * s, cx + .8 * s, cy + .35 * s), 0, 180, fill=c, width=lw); d.arc((cx - .8 * s, cy + .3 * s, cx + .8 * s, cy + .95 * s), 0, 180, fill=c, width=lw)
    elif kind == "queue":
        d.rounded_rectangle((cx - s, cy - .65 * s, cx + s, cy + .65 * s), int(.2 * s), outline=c, width=lw)
        for x in (-.5, 0, .5): d.line([(cx + x * s, cy - .35 * s), (cx + x * s, cy + .35 * s)], fill=c, width=lw)
    elif kind == "mail":
        d.rounded_rectangle((cx - s, cy - .65 * s, cx + s, cy + .65 * s), int(.14 * s), outline=c, width=lw)
        d.line([(cx - s, cy - .55 * s), (cx, cy + .1 * s), (cx + s, cy - .55 * s)], fill=c, width=lw, joint="curve")
    elif kind == "truck":
        d.rectangle((cx - s, cy - .55 * s, cx + .2 * s, cy + .45 * s), outline=c, width=lw)
        d.polygon([(cx + .2 * s, cy - .15 * s), (cx + .65 * s, cy - .15 * s), (cx + s, cy + .2 * s), (cx + s, cy + .45 * s), (cx + .2 * s, cy + .45 * s)], outline=c, width=lw)
        for x in (-.5, .55): d.ellipse((cx + x * s - .2 * s, cy + .45 * s - .2 * s, cx + x * s + .2 * s, cy + .45 * s + .2 * s), fill=c)
    elif kind == "sync":
        d.arc((cx - .8 * s, cy - .8 * s, cx + .8 * s, cy + .8 * s), 200, 340, fill=c, width=lw); d.arc((cx - .8 * s, cy - .8 * s, cx + .8 * s, cy + .8 * s), 20, 160, fill=c, width=lw)
        d.polygon([(cx + .8 * s, cy - .1 * s), (cx + .45 * s, cy - .25 * s), (cx + .95 * s, cy - .55 * s)], fill=c); d.polygon([(cx - .8 * s, cy + .1 * s), (cx - .45 * s, cy + .25 * s), (cx - .95 * s, cy + .55 * s)], fill=c)
    elif kind == "ghost":
        w = A((245, 245, 245) if not LIGHT else (255, 255, 255), al); ol = A((20, 20, 20), al * (1 if LIGHT else 0))
        d.ellipse((cx - .75 * s, cy - .95 * s, cx + .75 * s, cy + .5 * s), fill=w, outline=ol, width=lw // 2 or 1); d.rectangle((cx - .75 * s, cy - .2 * s, cx + .75 * s, cy + .6 * s), fill=w)
        d.polygon([(cx - .75 * s, cy + .55 * s), (cx - .5 * s, cy + .95 * s), (cx - .25 * s, cy + .55 * s), (cx, cy + .95 * s), (cx + .25 * s, cy + .55 * s), (cx + .5 * s, cy + .95 * s), (cx + .75 * s, cy + .55 * s)], fill=w)
        for x in (-.28, .28): d.ellipse((cx + x * s - .11 * s, cy - .3 * s - .11 * s, cx + x * s + .11 * s, cy - .3 * s + .11 * s), fill=A(ink, al))
    elif kind == "lock":
        d.arc((cx - .45 * s, cy - 1.0 * s, cx + .45 * s, cy), 180, 360, fill=c, width=lw)
        d.rounded_rectangle((cx - .7 * s, cy - .35 * s, cx + .7 * s, cy + .8 * s), int(.14 * s), fill=c)
    elif kind == "check":
        d.line([(cx - .55 * s, cy), (cx - .15 * s, cy + .45 * s), (cx + .6 * s, cy - .45 * s)], fill=c, width=lw + 1, joint="curve")
    elif kind == "x":
        d.line([(cx - .5 * s, cy - .5 * s), (cx + .5 * s, cy + .5 * s)], fill=c, width=lw + 1); d.line([(cx - .5 * s, cy + .5 * s), (cx + .5 * s, cy - .5 * s)], fill=c, width=lw + 1)
    elif kind == "doc":
        d.rounded_rectangle((cx - .65 * s, cy - .8 * s, cx + .65 * s, cy + .8 * s), int(.14 * s), outline=c, width=lw)
        for y in (-.35, 0, .35): d.line([(cx - .3 * s, cy + y * s), (cx + .3 * s, cy + y * s)], fill=c, width=max(1, lw // 2))
    else: d.ellipse((cx - .4 * s, cy - .4 * s, cx + .4 * s, cy + .4 * s), fill=c)


def _sd_badge(d, kind, cx, cy, r, al):
    if al <= 0: return
    if kind == "ghost":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A((250, 250, 250), al), outline=A((20, 20, 20), al * (1 if LIGHT else 0.3)), width=2); _sd_icon(d, "ghost", cx, cy + 1, r * .8, (250, 250, 250), al, (20, 20, 20)); return
    fill = {"ok": _sdc("green"), "err": (240, 70, 70), "lock": (30, 32, 38) if not LIGHT else (20, 20, 18)}.get(kind, _sdc("gray"))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(fill, al), outline=A((250, 250, 250) if not LIGHT else (255, 255, 255), al), width=2)
    _sd_icon(d, {"ok": "check", "err": "x", "lock": "lock"}.get(kind, "x"), cx, cy, r * .7, (255, 255, 255) if kind != "ok" or not LIGHT else (255, 255, 255), al)


def _sd_pill(d, cx, cy, text, tone, al, scale=1.0, size=22):
    """pill: tone 'red' = filled, 'red:outline' = transparent with a coloured border, 'gray:dim' = faint"""
    if al <= 0: return 0
    name, _, mode = tone.partition(":"); col = _sdc(name); sz = max(12, int(size * min(1.0, scale)))
    tw = _bw(text, sz); w = tw + 28; h = sz + 16; x0, y0 = cx - w / 2, cy - h / 2
    if mode == "outline":
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h // 2, fill=A(_SD_NODE, al * .6), outline=A(col, al), width=2); _bt(d, (cx, cy), text, sz, A(col, al))
    elif mode == "dim":
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h // 2, fill=A(lerp(_SD_PANEL, col, .25), al * .6)); _bt(d, (cx, cy), text, sz, A(lerp(_SD_PANEL, col, .5), al))
    else:
        if LIGHT and not SOFT: d.rounded_rectangle((x0 + 3, y0 + 3, x0 + w + 3, y0 + h + 3), h // 2, fill=A((14, 14, 12), al))
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h // 2, fill=A(col, al), outline=A((14, 14, 12), al) if LIGHT and not SOFT else None, width=2)
        _bt(d, (cx, cy), text, sz, A((255, 255, 255) if LIGHT and name in ("red", "purple", "blue", "pink") else (14, 14, 12), al))
    return w


def _sd_tilted(d, cx, cy, text, tone, ang, al, scale, size=28, inv=False):
    """tilted sticker / stage pill: drawn on its own layer, rotated, composited"""
    if al <= 0 or scale <= 0: return
    tw = _bw(text, size); w = int(tw + 44); h = int(size + 30); pad = 14
    L = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    col = _sdc(tone) if tone not in ("white", "ink") else None
    if tone == "white": fill, fg = (250, 250, 250), (14, 14, 12)
    elif tone == "ink": fill, fg = (22, 22, 20), (250, 250, 250)
    else: fill, fg = col, ((255, 255, 255) if LIGHT and tone in ("red", "purple", "blue", "pink") else (14, 14, 12))
    if LIGHT and not SOFT or tone in ("white", "ink"): ld.rounded_rectangle((pad + 4, pad + 4, pad + w + 4, pad + h + 4), h // 4, fill=(14, 14, 12, 255) if LIGHT else (0, 0, 0, 120))
    ld.rounded_rectangle((pad, pad, pad + w, pad + h), h // 4, fill=fill + (255,), outline=(14, 14, 12, 255) if LIGHT or tone == "white" else None, width=3)
    _bt(ld, (pad + w / 2, pad + h / 2), text, size, fg + (255,))
    L = L.rotate(ang, resample=Image.BICUBIC, expand=True)
    if scale != 1.0: L = L.resize((max(1, int(L.size[0] * scale)), max(1, int(L.size[1] * scale))), Image.BICUBIC)
    if al < 0.999: L.putalpha(L.getchannel("A").point(lambda v: int(v * al)))
    px, py = int(cx - L.size[0] / 2), int(cy - L.size[1] / 2)
    sx0, sy0 = max(0, -px), max(0, -py); L2 = L.crop((sx0, sy0, min(L.size[0], W - px), min(L.size[1], H - py)))
    if L2.size[0] > 0 and L2.size[1] > 0: d._image.alpha_composite(L2, (px + sx0, py + sy0))


def _sd_dashed(d, box, col, al, w=3, dash=10, gap=7, r=0):
    x0, y0, x1, y1 = box
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        L = math.hypot(bx - ax, by - ay); n = int(L // (dash + gap)) + 1
        for i in range(n):
            s0 = i * (dash + gap) / L; s1 = min(1.0, (i * (dash + gap) + dash) / L)
            if s0 >= 1: break
            d.line([(ax + (bx - ax) * s0, ay + (by - ay) * s0), (ax + (bx - ax) * s1, ay + (by - ay) * s1)], fill=A(col, al), width=w)


def _sd_route(a, b):
    """orthogonal polyline between two rects (cx, cy, w, h)"""
    (ax, ay, aw, ah), (bx, by, bw, bh) = a, b
    if abs(ay - by) < min(ah, bh) * 0.6:   # same row: edge to edge
        s = 1 if bx > ax else -1; return [(ax + s * aw / 2, ay), (bx - s * bw / 2, by)]
    s = 1 if by > ay else -1; y1 = ay + s * ah / 2; y2 = by - s * bh / 2; my = (y1 + y2) / 2
    if abs(ax - bx) < 3: return [(ax, y1), (bx, y2)]
    return [(ax, y1), (ax, my), (bx, my), (bx, y2)]


def _sd_along(pts, f):
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]; tot = sum(seg) or 1; want = f * tot
    for i, L in enumerate(seg):
        if want <= L or i == len(seg) - 1:
            u = 0 if L == 0 else min(1.0, want / L); return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u), tot
        want -= L
    return pts[-1], tot


def draw_sysdiagram(d, box, b, t, k):
    x0, y0, x1, y1 = box; rs = b.get("resets", []); al0 = E(t, b["t"], 0.35)
    if al0 <= 0.01: return
    ptop = 64 if WIDE else 78                                     # room for the stage pill above the panel
    px0, py0, px1, py1 = x0, y0 + ptop, x1, y1
    nw, nh = (232, 64) if WIDE else (268, 84); fs = 26 if WIDE else 30; ic = 15 if WIDE else 18
    bd = (14, 14, 12) if LIGHT else None
    # panel
    if SOFT: hard(d, (px0, py0, px1, py1), _SD_PANEL, (0, 0, 0), a=al0, r=28)
    else: d.rounded_rectangle((px0, py0, px1, py1), 26, fill=A(_SD_PANEL, al0), outline=A((14, 14, 12) if LIGHT else (60, 64, 72), al0), width=4 if LIGHT else 2)
    def P(pos): return (px0 + 30 + (px1 - px0 - 60) * pos[0], py0 + 26 + (py1 - py0 - 52) * pos[1])
    nodes = b.get("nodes", {}); rect = {}
    for nid, nd in nodes.items():
        cx, cy = P(nd["pos"]); rect[nid] = (cx, cy, nw, nh)
    tb = b.get("table"); trow_h = 40
    if tb:
        tx0, ty0 = P((tb["pos"][0], tb["pos"][1])); tx1, ty1 = P((tb["pos"][2], tb["pos"][3])); rect["tbl"] = ((tx0 + tx1) / 2, ty1 + 6, (tx1 - tx0) * .5, 10)
    # links
    for lk in b.get("links", []):
        a_, b_ = lk[0], lk[1]
        if a_ not in rect or b_ not in rect: continue
        ta = min(nodes[x]["t"] if x in nodes else tb["t"] for x in (a_, b_)); la = E(t, ta + 0.05, 0.3) * al0 * min([1 - prog(t, nodes[x]["until"], nodes[x]["until"] + 0.3) for x in (a_, b_) if x in nodes and nodes[x].get("until") is not None] or [1])
        if la < 0.01: continue
        pts = _sd_route(rect[a_], rect[b_])
        for i in range(len(pts) - 1): d.line([pts[i], pts[i + 1]], fill=A(_SD_LINE, la), width=3)
    # table group
    if tb and E(t, tb["t"], 0.35) > 0.01:
        ta = E(t, tb["t"], 0.35) * al0; bl = _sdc("blue")
        d.rounded_rectangle((tx0, ty0, tx1, ty1), 18, fill=A(lerp(_SD_PANEL, bl, .10), ta), outline=A(bl, ta), width=3)
        d.rounded_rectangle((tx0 + 14, ty0 - 13, tx0 + 62, ty0 + 11), 8, fill=A(bl, ta)); _bt(d, (tx0 + 38, ty0 - 1), tb.get("name", "DB"), 17, A((255, 255, 255), ta))
        cols = tb["cols"]; n = len(cols); gap = 14; cw = (tx1 - tx0 - 28 - gap * (n - 1)) / n
        colx = [(tx0 + 14 + i * (cw + gap), tx0 + 14 + i * (cw + gap) + cw) for i in range(n)]
        rows = tb.get("rows", []); trow_h = int(max(22, min(40 if WIDE else 46, (ty1 - ty0 - 84) / max(1, len(rows)) - 8))); rowy = lambda i: ty0 + 64 + i * (trow_h + 8)
        for i, cdef in enumerate(cols):
            cc = _sdc(cdef.get("tone", "orange")); cxa, cxb = colx[i]
            d.rounded_rectangle((cxa, ty0 + 16, cxb, ty1 - 12), 12, fill=A(lerp(_SD_PANEL, cc, .05), ta), outline=A(lerp(_SD_PANEL, cc, .55), ta), width=2)
            _bt(d, ((cxa + cxb) / 2, ty0 + 40), cdef.get("name", cdef["key"]), int(21 * _fk), A(cc, ta))
            for r_i, row in enumerate(rows):
                ra, rs_ = _sd_pop(t, row["t"]); ra *= ta
                if ra <= 0.01: continue
                ry = rowy(r_i) + (1 - ra) * 10; st = None
                for (ts_, sv) in row.get(cdef["key"], []):
                    if t >= ts_: st = sv
                d.rounded_rectangle((cxa + 8, ry, cxb - 8, ry + trow_h), 9, fill=A(lerp(_SD_NODE, cc, .12), ra), outline=A(cc, ra), width=2)
                _sd_icon(d, "mail" if i else "doc", cxa + 28, ry + trow_h / 2, 9, cc, ra); _bt(d, (cxa + 62 + _bw(row["id"], int(19 * _fk)) / 2 - 18, ry + trow_h / 2), row["id"], int(19 * _fk), A(_FG, ra), "mm")
                if st:
                    sc_ = {"new": "orange", "sent": "green", "placed": cdef.get("tone", "orange")}.get(st, "gray")
                    pw = _bw(st, int(16 * _fk)) + 20; pc = _sdc(sc_)
                    if st == "placed": _bt(d, (cxb - 18 - pw / 2 + 6, ry + trow_h / 2), st, int(17 * _fk), A(_FG2, ra), "mm")
                    else:
                        d.rounded_rectangle((cxb - 16 - pw, ry + 5, cxb - 16, ry + trow_h - 5), 9, fill=A(pc, ra)); _bt(d, (cxb - 16 - pw / 2, ry + trow_h / 2), st, int(16 * _fk), A((14, 14, 12), ra))
        for (l0, l1, ri) in b.get("locks", []):
            la, _ = _sd_pop(t, l0)
            if la <= 0.01 or ri >= len(rows): continue
            la *= 1 - prog(t, l1 + 0.9, l1 + 1.2); ry = rowy(ri)
            if t < l1: _sd_dashed(d, (tx0 + 10, ry - 4, tx1 - 10, ry + trow_h + 4), _FG, la * ta, 3)
            mx = (tx0 + tx1) / 2; _sd_badge(d, "lock", mx, ry + trow_h / 2, 15, la * ta)
            if t >= l1: _sd_badge(d, "ok", tx1 - 8, ry + trow_h / 2, 15, la * ta * ss(prog(t, l1, l1 + .25)))
    # nodes
    stack = {}
    for nid, nd in nodes.items():
        al = E(t, nd["t"], 0.35) * al0 * (1 - prog(t, nd["until"], nd["until"] + 0.3) if nd.get("until") is not None else 1)
        if al < 0.01: continue
        cx, cy = P(nd["pos"]); dy = (1 - al) * 18; cy += dy
        tone = _sdc(nd.get("tone", "orange")); st = "idle"; ts_ = -9
        for (tt, sv) in nd.get("state", []):
            if t >= tt: st, ts_ = sv, tt
        edge = {"ok": _sdc("green"), "err": (240, 76, 76), "hot": OR, "ghost": _sdc("gray")}.get(st, tone)
        pulse = max(0.0, 1 - (t - ts_) / 0.5) if st != "idle" else 0.0
        bx = (cx - nw / 2, cy - nh / 2, cx + nw / 2, cy + nh / 2)
        if LIGHT and not SOFT: d.rounded_rectangle((bx[0] + 5, bx[1] + 5, bx[2] + 5, bx[3] + 5), 18, fill=A((14, 14, 12), al))
        if pulse > 0: d.rounded_rectangle((bx[0] - 6 * pulse, bx[1] - 6 * pulse, bx[2] + 6 * pulse, bx[3] + 6 * pulse), 22, outline=A(edge, al * .45 * pulse), width=5)
        d.rounded_rectangle(bx, 18, fill=A(lerp(_SD_NODE, edge, .10 if st != "idle" else 0.0), al), outline=A(edge, al), width=3)
        tw = _bw(nd["name"], fs); gx = cx - (tw + ic * 2 + 12) / 2
        _sd_icon(d, nd.get("icon", "dot"), gx + ic, cy, ic * .9, edge, al); _bt(d, (gx + ic * 2 + 12 + tw / 2, cy), nd["name"], fs, A(_FG, al))
        for (tt, kd, *_) in nd.get("badges", []):
            ba, bs_ = _sd_win(t, tt, (_[0] if _ else None), rs)
            if ba > 0.01: _sd_badge(d, kd, bx[2] - 4, bx[1] + 2, 15 * min(1.2, bs_), ba * al)
        py_ = bx[3] + 24
        if b.get("ledger", {}).get(nid): py_ += 36
        for pl in nd.get("pills", []):
            tt, text, tn = pl[0], pl[1], pl[2]; end = pl[3] if len(pl) > 3 else None
            pa, ps = _sd_win(t, tt, end, rs)
            if pa <= 0.01: continue
            slot = sum(1 for q in nd.get("pills", []) if q[0] < tt and _sd_win(tt, q[0], q[3] if len(q) > 3 else None, rs)[0] > 0.05)
            _sd_pill(d, cx, py_ + slot * 38, text, tn, pa * al, ps, 22 if WIDE else 24)
    # ledger
    for nid, items in b.get("ledger", {}).items():
        if nid not in rect: continue
        cx, cy, w_, h_ = rect[nid]; ly = cy + h_ / 2 + 24; shown = [(tt, s) for tt, s in items if t >= tt - .05]
        if not shown: continue
        la = E(t, items[0][0], 0.3) * al0; tc = _sdc("teal"); chips = [_bw(s, int(18 * _fk)) + 18 for _, s in items if True]
        total = 44 + sum(chips) + 8 * (len(chips) - 1); sx0 = cx - w_ / 2 - 6; sx1 = max(cx + w_ / 2 + 6, sx0 + total)
        d.rounded_rectangle((sx0, ly - 15, sx1, ly + 15), 15, fill=A(lerp(_SD_PANEL, tc, .10), la), outline=A(tc, la), width=2); _sd_icon(d, "check", sx0 + 20, ly, 9, tc, la)
        x = sx0 + 40
        for (tt, s), cw_ in zip(items, chips):
            ca, cs_ = _sd_pop(t, tt)
            if ca > 0.01:
                d.rounded_rectangle((x, ly - 11, x + cw_, ly + 11), 11, fill=A(tc, ca * la)); _bt(d, (x + cw_ / 2, ly), s, int(17 * _fk), A((14, 14, 12), ca * la))
            x += cw_ + 8
    # transaction pills
    for (t0_, t1_, kind, nid, *_) in b.get("txn", []):
        if nid not in rect: continue
        a_, s_ = _sd_win(t, t0_, t1_, rs)
        if a_ <= 0.01: continue
        cx, cy, w_, h_ = rect[nid]; tone = {"BEGIN": "gray", "COMMIT": "green", "ROLLBACK": "red"}.get(kind, "gray")
        right = kind != "BEGIN"; _sd_pill(d, cx + (w_ / 2 + 56) if right else cx - (w_ / 2 + 52), cy, kind, tone, a_, s_, 19 if WIDE else 21)
    # envelopes
    for ev in b.get("env", []):
        te_, ids, tn = ev[0], ev[1], ev[2]; stop = ev[3] if len(ev) > 3 else None
        pts = []; ok = True
        for a_, b_ in zip(ids[:-1], ids[1:]):
            if a_ not in rect or b_ not in rect: ok = False; break
            seg = _sd_route(rect[a_], rect[b_]); pts += seg if not pts else seg[1:]
        if not ok or len(pts) < 2: continue
        tot = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)); dur = max(0.7, tot / (820.0 if WIDE else 900.0))
        q = prog(t, te_, te_ + dur); f = ss(q) * (stop if stop else 1.0)
        fade = 1 - prog(t, te_ + dur + 0.25, te_ + dur + 0.55)
        for r_ in rs:
            if r_ > te_ + .05: fade = min(fade, 1 - prog(t, r_, r_ + .3))
        if q <= 0 or fade <= 0.01: continue
        col = (240, 76, 76) if stop else _sdc(tn)
        head, _ = _sd_along(pts, f)
        for k_ in range(1, 7):   # glow trail
            (tp, _) = _sd_along(pts, max(0, f - k_ * 0.018)); r = 11 - k_ * 1.2
            d.ellipse((tp[0] - r, tp[1] - r, tp[0] + r, tp[1] + r), fill=A(col, fade * 0.16 * (7 - k_) / 6 * al0))
        ew, eh = 30, 22
        d.rounded_rectangle((head[0] - ew / 2, head[1] - eh / 2, head[0] + ew / 2, head[1] + eh / 2), 5, fill=A(col, fade * al0), outline=A((14, 14, 12) if LIGHT else (255, 255, 255), fade * al0), width=2)
        d.line([(head[0] - ew / 2 + 3, head[1] - eh / 2 + 4), (head[0], head[1] + 2), (head[0] + ew / 2 - 3, head[1] - eh / 2 + 4)], fill=A((14, 14, 12) if LIGHT else (255, 255, 255), fade * al0), width=2)
        if stop and q >= 1: _sd_badge(d, "err", head[0] + 16, head[1] - 14, 12, fade * al0)
    # stickers
    sy = py1 - (62 if WIDE else 80)
    for st_ in b.get("stickers", []):
        tt, text, tn = st_[0], st_[1], st_[2]; end = st_[3] if len(st_) > 3 else None; at = st_[4] if len(st_) > 4 else (0.5, None)
        a_, s_ = _sd_win(t, tt, end, rs)
        if a_ <= 0.01: continue
        ang = -3 if (sum(map(ord, text)) % 2 == 0) else 3
        cx = px0 + 30 + (px1 - px0 - 60) * at[0]; cy = sy if at[1] is None else py0 + 26 + (py1 - py0 - 52) * at[1]
        _sd_tilted(d, cx, cy, text, tn, ang, a_ * al0, s_, 28 if WIDE else 32)
    # stage pill (above the panel)
    stg = [(tt, s) for tt, s in b.get("stages", [])]
    cur = None
    for i, (tt, s) in enumerate(stg):
        if t >= tt - 0.05: cur = i
    if cur is not None:
        tt, s = stg[cur]; a_, s_ = _sd_pop(t, tt, 0.3); a_ = a_ * al0
        _sd_tilted(d, (px0 + px1) / 2, y0 + ptop / 2 - 4, s, "ink" if LIGHT else "white", -1.5, a_, min(1.0, s_), 26 if WIDE else 30)


EXTRA_H["sysdiagram"] = lambda blk, w: blk.get("h", 660 if WIDE else 1150)
DRAW["sysdiagram"] = draw_sysdiagram
