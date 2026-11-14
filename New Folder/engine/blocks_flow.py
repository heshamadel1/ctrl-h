# Flow / system blocks added in 1.0.0 (loaded by anim.py with exec, so it shares anim's globals):
#   titlevs, split, chain, hub, pipeline, deviceflow, codeann, flowmini   (+ _ico: a small line-icon set)
# Text rule: Latin for names / code (mono font), Arabic only in captions, labels, tags of deviceflow, caption pills.

def _tx(c):
    """accent colour used for TEXT: darker on the light theme"""
    return tuple(int(v * .62) for v in c) if _T.get("light") else c


def _tw(s, size):
    return F(MONO, size).getlength(s) if s.isascii() else F(ARB, size).getlength(s, direction="rtl", language="ar")


def _pill(d, cx, cy, text, size, fill, tcol, al, border=None, padx=26, h=None, anchor="m"):
    """filled pill centred (anchor m) or left-aligned (anchor l) at (cx, cy); returns (x0, x1)"""
    w = _tw(text, size) + padx * 2; h = h or size + 24
    x0 = cx - w / 2 if anchor == "m" else cx
    d.rounded_rectangle((x0, cy - h / 2, x0 + w, cy + h / 2), int(h / 2), fill=A(fill, al) if fill else None, outline=A(border, al) if border else None, width=3)
    txt(d, (x0 + w / 2, cy), text, size, A(tcol, al)); return x0, x0 + w


def _dash(d, p0, p1, col, al, w=4, dash=14, gap=10, frac=1.0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * frac
    if L <= 0: return
    ux, uy = (p1[0] - p0[0]) / max(1e-6, math.hypot(p1[0] - p0[0], p1[1] - p0[1])), (p1[1] - p0[1]) / max(1e-6, math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    s = 0
    while s < L:
        e = min(L, s + dash); d.line([(p0[0] + ux * s, p0[1] + uy * s), (p0[0] + ux * e, p0[1] + uy * e)], fill=A(col, al), width=w); s += dash + gap


def _arrow(d, p, ang, col, al, s=14):
    d.polygon([(p[0], p[1]), (p[0] - s * math.cos(ang - 0.45), p[1] - s * math.sin(ang - 0.45)), (p[0] - s * math.cos(ang + 0.45), p[1] - s * math.sin(ang + 0.45))], fill=A(col, al))


def _bz(p0, p1, p2, p3, u):
    v = 1 - u
    return (v ** 3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u ** 3 * p3[0], v ** 3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u ** 3 * p3[1])


def _ico(d, kind, cx, cy, s, col, al, lw=None):
    """line icon, half-size s. kinds: user cart card code search gauge link clip server mail gear cube bell truck key lock shield db check x clock doc bolt"""
    lw = lw or max(3, int(s * 0.14)); c = A(col, al)
    if kind == "user":
        d.ellipse((cx - .34 * s, cy - .85 * s, cx + .34 * s, cy - .17 * s), outline=c, width=lw); d.arc((cx - .75 * s, cy + .05 * s, cx + .75 * s, cy + 1.45 * s), 180, 360, fill=c, width=lw)
    elif kind == "cart":
        d.line([(cx - s, cy - .8 * s), (cx - .6 * s, cy - .8 * s), (cx - .3 * s, cy + .3 * s), (cx + .7 * s, cy + .3 * s), (cx + .9 * s, cy - .5 * s), (cx - .55 * s, cy - .5 * s)], fill=c, width=lw, joint="curve")
        for wx in (-.2, .6): d.ellipse((cx + wx * s - .14 * s, cy + .6 * s, cx + wx * s + .14 * s, cy + .88 * s), fill=c)
    elif kind == "card":
        d.rounded_rectangle((cx - s, cy - .68 * s, cx + s, cy + .68 * s), int(.18 * s), outline=c, width=lw); d.line([(cx - s, cy - .2 * s), (cx + s, cy - .2 * s)], fill=c, width=lw)
        d.line([(cx - .7 * s, cy + .3 * s), (cx - .2 * s, cy + .3 * s)], fill=c, width=lw)
    elif kind == "code":
        d.line([(cx - .35 * s, cy - .55 * s), (cx - .9 * s, cy), (cx - .35 * s, cy + .55 * s)], fill=c, width=lw, joint="curve")
        d.line([(cx + .35 * s, cy - .55 * s), (cx + .9 * s, cy), (cx + .35 * s, cy + .55 * s)], fill=c, width=lw, joint="curve"); d.line([(cx + .12 * s, cy - .7 * s), (cx - .12 * s, cy + .7 * s)], fill=c, width=lw)
    elif kind == "search":
        d.ellipse((cx - .8 * s, cy - .8 * s, cx + .35 * s, cy + .35 * s), outline=c, width=lw); d.line([(cx + .3 * s, cy + .3 * s), (cx + .9 * s, cy + .9 * s)], fill=c, width=lw + 1)
    elif kind == "gauge":
        d.arc((cx - s, cy - s * .9, cx + s, cy + s * 1.1), 180, 360, fill=c, width=lw); d.line([(cx, cy + .1 * s), (cx + .5 * s, cy - .5 * s)], fill=c, width=lw); d.ellipse((cx - .1 * s, cy, cx + .1 * s, cy + .2 * s), fill=c)
    elif kind == "link":
        d.rounded_rectangle((cx - .95 * s, cy - .4 * s, cx + .15 * s, cy + .4 * s), int(.4 * s), outline=c, width=lw); d.rounded_rectangle((cx - .15 * s, cy - .4 * s, cx + .95 * s, cy + .4 * s), int(.4 * s), outline=c, width=lw)
    elif kind == "clip":
        d.rounded_rectangle((cx - .7 * s, cy - .85 * s, cx + .7 * s, cy + .95 * s), int(.18 * s), outline=c, width=lw); d.rounded_rectangle((cx - .3 * s, cy - 1.0 * s, cx + .3 * s, cy - .6 * s), int(.1 * s), fill=c)
        for yy in (-.2, .2, .6): d.line([(cx - .4 * s, cy + yy * s), (cx + .4 * s, cy + yy * s)], fill=c, width=max(2, lw - 1))
    elif kind == "server":
        for yy in (-.55, .15): d.rounded_rectangle((cx - .9 * s, cy + yy * s - .1 * s, cx + .9 * s, cy + yy * s + .55 * s), int(.15 * s), outline=c, width=lw); d.ellipse((cx + .5 * s, cy + yy * s + .1 * s, cx + .7 * s, cy + yy * s + .3 * s), fill=c)
    elif kind == "mail":
        d.rounded_rectangle((cx - s, cy - .65 * s, cx + s, cy + .65 * s), int(.15 * s), outline=c, width=lw); d.line([(cx - s, cy - .6 * s), (cx, cy + .1 * s), (cx + s, cy - .6 * s)], fill=c, width=lw, joint="curve")
    elif kind == "gear":
        d.ellipse((cx - .5 * s, cy - .5 * s, cx + .5 * s, cy + .5 * s), outline=c, width=lw)
        for i in range(8):
            a = i * math.pi / 4; d.line([(cx + .7 * s * math.cos(a), cy + .7 * s * math.sin(a)), (cx + 1.0 * s * math.cos(a), cy + 1.0 * s * math.sin(a))], fill=c, width=lw + 1)
    elif kind == "cube":
        P = [(cx, cy - s), (cx + .87 * s, cy - .5 * s), (cx + .87 * s, cy + .5 * s), (cx, cy + s), (cx - .87 * s, cy + .5 * s), (cx - .87 * s, cy - .5 * s)]
        d.polygon(P, outline=c, width=lw); d.line([(cx, cy), (cx, cy + s)], fill=c, width=lw); d.line([(cx, cy), (cx + .87 * s, cy - .5 * s)], fill=c, width=lw); d.line([(cx, cy), (cx - .87 * s, cy - .5 * s)], fill=c, width=lw)
    elif kind == "bell":
        d.arc((cx - .7 * s, cy - .9 * s, cx + .7 * s, cy + .5 * s), 180, 360, fill=c, width=lw); d.line([(cx - .7 * s, cy - .2 * s), (cx - .8 * s, cy + .55 * s), (cx + .8 * s, cy + .55 * s), (cx + .7 * s, cy - .2 * s)], fill=c, width=lw, joint="curve"); d.ellipse((cx - .15 * s, cy + .7 * s, cx + .15 * s, cy + .95 * s), fill=c)
    elif kind == "truck":
        d.rounded_rectangle((cx - s, cy - .55 * s, cx + .2 * s, cy + .35 * s), int(.1 * s), outline=c, width=lw); d.polygon([(cx + .2 * s, cy - .25 * s), (cx + .65 * s, cy - .25 * s), (cx + s, cy + .1 * s), (cx + s, cy + .35 * s), (cx + .2 * s, cy + .35 * s)], outline=c, width=lw)
        for wx in (-.55, .6): d.ellipse((cx + wx * s - .17 * s, cy + .3 * s, cx + wx * s + .17 * s, cy + .64 * s), fill=BASEC, outline=c, width=lw - 1)
    elif kind == "key":
        d.ellipse((cx - .95 * s, cy - .4 * s, cx - .15 * s, cy + .4 * s), outline=c, width=lw); d.line([(cx - .15 * s, cy), (cx + .95 * s, cy)], fill=c, width=lw); d.line([(cx + .6 * s, cy), (cx + .6 * s, cy + .35 * s)], fill=c, width=lw); d.line([(cx + .95 * s, cy), (cx + .95 * s, cy + .3 * s)], fill=c, width=lw)
    elif kind == "lock":
        d.rounded_rectangle((cx - .7 * s, cy - .1 * s, cx + .7 * s, cy + .85 * s), int(.15 * s), outline=c, width=lw); d.arc((cx - .45 * s, cy - .85 * s, cx + .45 * s, cy + .2 * s), 180, 360, fill=c, width=lw)
    elif kind == "shield":
        d.polygon([(cx, cy - s), (cx + .8 * s, cy - .6 * s), (cx + .7 * s, cy + .3 * s), (cx, cy + s), (cx - .7 * s, cy + .3 * s), (cx - .8 * s, cy - .6 * s)], outline=c, width=lw); d.line([(cx - .3 * s, cy), (cx - .05 * s, cy + .3 * s), (cx + .4 * s, cy - .3 * s)], fill=c, width=lw, joint="curve")
    elif kind == "db":
        for yy in (-.55, 0, .55): d.arc((cx - .8 * s, cy + yy * s - .25 * s, cx + .8 * s, cy + yy * s + .25 * s), 0, 180, fill=c, width=lw)
        d.ellipse((cx - .8 * s, cy - .8 * s, cx + .8 * s, cy - .3 * s), outline=c, width=lw); d.line([(cx - .8 * s, cy - .55 * s), (cx - .8 * s, cy + .6 * s)], fill=c, width=lw); d.line([(cx + .8 * s, cy - .55 * s), (cx + .8 * s, cy + .6 * s)], fill=c, width=lw)
    elif kind == "check":
        d.line([(cx - .7 * s, cy), (cx - .2 * s, cy + .55 * s), (cx + .75 * s, cy - .5 * s)], fill=c, width=lw + 1, joint="curve")
    elif kind == "x":
        d.line([(cx - .6 * s, cy - .6 * s), (cx + .6 * s, cy + .6 * s)], fill=c, width=lw + 1); d.line([(cx + .6 * s, cy - .6 * s), (cx - .6 * s, cy + .6 * s)], fill=c, width=lw + 1)
    elif kind == "clock":
        d.ellipse((cx - .9 * s, cy - .9 * s, cx + .9 * s, cy + .9 * s), outline=c, width=lw); d.line([(cx, cy), (cx, cy - .55 * s)], fill=c, width=lw); d.line([(cx, cy), (cx + .4 * s, cy + .2 * s)], fill=c, width=lw)
    elif kind == "doc":
        d.rounded_rectangle((cx - .65 * s, cy - .9 * s, cx + .65 * s, cy + .9 * s), int(.12 * s), outline=c, width=lw)
        for yy in (-.4, 0, .4): d.line([(cx - .35 * s, cy + yy * s), (cx + .35 * s, cy + yy * s)], fill=c, width=max(2, lw - 1))
    elif kind == "bolt":
        d.polygon([(cx + .2 * s, cy - s), (cx - .6 * s, cy + .15 * s), (cx - .05 * s, cy + .15 * s), (cx - .2 * s, cy + s), (cx + .6 * s, cy - .2 * s), (cx + .05 * s, cy - .2 * s)], outline=c, width=lw)
    else:
        d.ellipse((cx - .5 * s, cy - .5 * s, cx + .5 * s, cy + .5 * s), outline=c, width=lw)


def _xbadge(d, cx, cy, r, al, col=RED):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(col, al), outline=A(PAPER, al), width=3); _ico(d, "x", cx, cy, r * .6, PAPER, al, 4)


def _okbadge(d, cx, cy, r, al, col=GRN):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(col, al), outline=A(PAPER, al), width=2); _ico(d, "check", cx, cy, r * .62, (12, 40, 24), al, 4)


# ------------------------------------------------------------------ titlevs
def draw_titlevs(d, box, b, t, k):
    """Header: two coloured pills with a round 'vs' between and a small sub line. {t, a, b, ca, cb, sub}"""
    al = E(t, b["t"])
    if al < .01: return
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2; cy = y0 + 62 - (1 - al) * 18; s = 54 if WIDE else 44
    ca = _hex_rgb(b.get("ca", "#FF9A1F")); cb = _hex_rgb(b.get("cb", "#1E88FF"))
    wa, wb = _tw(b["a"], s) + 56, _tw(b["b"], s) + 56; vs = 74
    xa0 = cx - (wa + wb + vs + 40) / 2
    d.rounded_rectangle((xa0 + 7, cy - 42 + 7, xa0 + wa + 7, cy + 42 + 7), 30, fill=A((8, 9, 12), al)); d.rounded_rectangle((xa0, cy - 42, xa0 + wa, cy + 42), 30, fill=A(ca, al)); txt(d, (xa0 + wa / 2, cy), b["a"], s, A((30, 24, 20), al))
    xv = xa0 + wa + 20 + vs / 2; d.ellipse((xv - 37, cy - 37, xv + 37, cy + 37), fill=A((38, 40, 48), al), outline=A(GRAYC, al), width=3); txt(d, (xv, cy), "vs", 32, A(PT, al))
    xb0 = xv + vs / 2 + 20
    d.rounded_rectangle((xb0 + 7, cy - 42 + 7, xb0 + wb + 7, cy + 42 + 7), 30, fill=A((8, 9, 12), al)); d.rounded_rectangle((xb0, cy - 42, xb0 + wb, cy + 42), 30, fill=A(cb, al)); txt(d, (xb0 + wb / 2, cy), b["b"], s, A(PAPER, al))
    if b.get("sub"): txt(d, (cx, cy + 74), b["sub"], 30 if WIDE else 26, A(GRAYC, al))


# ------------------------------------------------------------------ split
def _split_panel(d, pb, P, t, al, k):
    px0, py0, px1, py1 = pb; col = _hex_rgb(P["color"]); svc = P["services"]; n = len(svc); ev = P.get("events", [])
    d.rounded_rectangle(pb, 38, fill=A(lerp(CARDC, col, .08), al), outline=A(col, al), width=4)
    _pill(d, px0 + 34, py0, P["name"], 30, col, (28, 24, 20), al, anchor="l", h=52)
    if P.get("tag"): w_ = _tw(P["tag"], 28) + 52; d.rounded_rectangle((px1 - 34 - w_, py0 - 26, px1 - 34, py0 + 26), 26, fill=BASEC and A(lerp(CARDC, col, .1), al), outline=A(col, al), width=3); txt(d, (px1 - 34 - w_ / 2, py0), P["tag"], 28, A(_tx(col), al))
    ix0, iy0, ix1, iy1 = px0 + 30, py0 + 56, px1 - 30, py1 - 26; mid = (iy0 + iy1) / 2
    fan = P.get("mode", "box") == "fan"; sw = 100; sx = ix0 + sw / 2 + 6; src = P.get("src", {"name": "Traffic", "icon": "user"})
    rh = min(86, (iy1 - iy0 - 16) / n - 14); gh = rh * n + 14 * (n - 1); sy0 = mid - gh / 2
    lx = ix0 + sw + (96 if WIDE else 80); rx = ix1 - ((230 if fan else 150) if WIDE else (200 if fan else 110)); lx = min(lx, rx - 200)
    fan = P.get("mode", "box") == "fan"; ys = [sy0 + i * (rh + 14) + rh / 2 for i in range(n)]
    d.rounded_rectangle((sx - sw / 2, mid - sw / 2 - 6, sx + sw / 2, mid + sw / 2 - 6), 22, fill=A((44, 47, 56), al), outline=A(GRAYC, al), width=3); _ico(d, src.get("icon", "user"), sx, mid - 6, 30, GRAYC, al); txt(d, (sx, mid + sw / 2 + 22), src.get("name", "Traffic"), 24, A(GRAYC, al))
    fails = {e[2] for e in ev if e[1] == "fail" and t >= e[0]}; scaled = {e[2] for e in ev if e[1] == "scale" and t >= e[0]}
    bx0, bx1, by0, by1 = lx - 18, rx + 18, sy0 - 18, sy0 + gh + 18
    if not fan:   # one boundary around every service
        fb = -1 in fails; bc = RED if fb else (170, 120, 80) if col[0] > col[2] else (90, 150, 200)
        if -1 in scaled:
            q = E(t, [e[0] for e in ev if e[1] == "scale" and e[2] == -1][0], .5)
            for g in (2, 1): d.rounded_rectangle((bx0 + 26 * g * q, by0 - 20 * g * q, bx1 + 26 * g * q, by1 - 20 * g * q), 22, outline=A(col, al * .55), width=3)
        d.rounded_rectangle((bx0, by0, bx1, by1), 22, fill=A(lerp(CARDC, RED, .12), al) if fb else None, outline=A(RED if fb else bc, al), width=4)
        d.line([(sx + sw / 2, mid - 6), (bx0, mid - 6)], fill=A((84, 88, 100), al), width=4)
        if fb: _xbadge(d, bx1 - 2, by0 + 2, 22, al)
        vb = [e for e in ev if e[1] == "ver" and e[2] == -1 and t >= e[0]]
        if vb: _pill(d, (bx0 + bx1) / 2, by0 - 6, vb[-1][3], 24, col, (28, 24, 20), al, h=38)
    mx = (sx + sw / 2 + lx) / 2 + 14
    for i in range(n):
        if fan:
            pts = [(sx + sw / 2, mid - 6), (mx, mid - 6), (mx, ys[i]), (lx, ys[i])]; d.line(pts, fill=A((84, 88, 100), al), width=4, joint="curve")
    for i, sv in enumerate(svc):
        a2 = E(t, sv["t"], .3) * al
        if a2 < .01: continue
        hit = 0.0
        for e in ev:
            if e[1] == "traffic":
                q = prog(t, e[0] + .85, e[0] + 1.25)
                if 0 < q < 1 and (e[2] == i or (not fan and e[2] == -1)): hit = max(hit, 1 - q)
        bad = i in fails; sc = RED if bad else col
        x0_, x1_ = lx, rx; y0_, y1_ = ys[i] - rh / 2, ys[i] + rh / 2
        if i in scaled:   # copies of just this service, in a dashed frame
            q = E(t, [e[0] for e in ev if e[1] == "scale" and e[2] == i][0], .5)
            for g in (1, 2):
                cxg = x1_ + 18 + (g - 1) * (rh + 14) + rh / 2; cwg = rh * (1.0 if g == 1 else .74) * q
                d.rounded_rectangle((cxg - cwg / 2, ys[i] - cwg / 2, cxg + cwg / 2, ys[i] + cwg / 2), 16, fill=A(lerp(CARDC, col, .2), a2), outline=A(col, a2), width=3); _ico(d, sv.get("icon", "cube"), cxg, ys[i], cwg * .26, col, a2)
            _dash(d, (x1_ - 8, y0_ - 8), (x1_ + 30 + 2 * (rh + 14), y0_ - 8), col, a2 * .7, 3)
        fill = lerp(CARDC, sc, .14 + .22 * hit) if not bad else lerp(CARDC, RED, .3)
        d.rounded_rectangle((x0_, y0_, x1_, y1_), 18, fill=A(fill, a2), outline=A(sc, a2), width=3 if not hit else 4)
        _ico(d, sv.get("icon", "cube"), x0_ + 40, ys[i], 20, sc, a2); txt(d, (x0_ + 78, ys[i]), sv["name"], _fit(sv["name"], 30, x1_ - x0_ - 110, 18), A(PAPER, a2), anchor="lm")
        if bad: _xbadge(d, x1_ - 6, y0_ - 2, 22, a2)
        for e in ev:
            if e[1] == "ver" and e[2] == i and t >= e[0]: _pill(d, x1_ + 4 - (0 if i not in scaled else 0), y0_ - 8, e[3], 24, col, (28, 24, 20), a2, h=36, padx=16)
    for e in ev:   # traffic dots
        if e[1] != "traffic": continue
        tgt = e[2] if e[2] >= 0 else n // 2
        path = [(sx + sw / 2, mid - 6), (mx, mid - 6), (mx, ys[tgt]), (lx, ys[tgt])] if fan else [(sx + sw / 2, mid - 6), (bx0, mid - 6), (lx, ys[tgt])]
        L = [math.hypot(path[m + 1][0] - path[m][0], path[m + 1][1] - path[m][1]) for m in range(len(path) - 1)]; tot = sum(L)
        for dd in range(4):
            q = prog(t, e[0] + .2 * dd, e[0] + .2 * dd + .9)
            if q <= 0 or q >= 1: continue
            s_ = ss(q) * tot; m = 0
            while m < len(L) - 1 and s_ > L[m]: s_ -= L[m]; m += 1
            f_ = s_ / max(1e-6, L[m]); x = path[m][0] + (path[m + 1][0] - path[m][0]) * f_; y = path[m][1] + (path[m + 1][1] - path[m][1]) * f_
            d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=A(col, .25 * al)); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=A(col, al), outline=A(PAPER, al), width=2)


def draw_split(d, box, b, t, k):
    """Two systems side by side (16:9) or stacked (9:16) with a big VS badge. {t, counter:"1/5 SCALING", panels:[P, P]}
    P = {name, tag, color:"#RRGGBB", src:{name,icon}, mode:"box"|"fan", services:[{t,name,icon}],
         events:[(t,'traffic',idx|-1),(t,'fail',idx|-1),(t,'scale',idx|-1),(t,'ver',idx|-1,'v3')]}   idx -1 = the whole box (mode box)"""
    al = E(t, b["t"], .3)
    if al < .01: return
    x0, y0, x1, y1 = box; top = 0
    if b.get("counter"):
        _pill(d, (x0 + x1) / 2, y0 + 24, b["counter"], 30, (244, 244, 240), (20, 22, 26), al, h=50); top = 62
    x0_, y0_ = x0, y0 + top; gap = 76
    if WIDE:
        w = (x1 - x0 - gap) / 2; pbs = [(x0 + w + gap, y0_ + 28, x1, y1), (x0, y0_ + 28, x0 + w, y1)]; vc = (x0 + w + gap / 2, (y0_ + 28 + y1) / 2)
    else:
        h = (y1 - y0_ - gap - 56) / 2; pbs = [(x0, y0_ + 28, x1, y0_ + 28 + h), (x0, y0_ + 28 + h + gap, x1, y1 - 28 + 28)]; vc = ((x0 + x1) / 2, y0_ + 28 + h + gap / 2)
    for pb, P in zip(pbs, b["panels"]): _split_panel(d, pb, P, t, al, k)
    d.ellipse((vc[0] - 38, vc[1] - 38, vc[0] + 38, vc[1] + 38), fill=A((244, 244, 240), al), outline=A((20, 22, 26), al), width=4); txt(d, vc, "VS", 32, A((20, 22, 26), al))


# ------------------------------------------------------------------ chain
def draw_chain(d, box, b, t, k):
    """Chain of responsibility: {t, start:"-> Login Request", payload:"{ email, password }", link:"Next",
    steps:[{t, name, sub, icon, color:"#RRGGBB", err:(t_err,'400 Bad Request')}]}"""
    x0, y0, x1, y1 = box; S = b["steps"]; n = len(S); sh = 64 if b.get("start") else 0
    lg = 62; ch = min(128, (y1 - y0 - sh - 26 - lg * (n - 1)) / n)
    ew = 330; cw = min(700 if WIDE else 720, (x1 - x0) - ew - 30 if not WIDE else (x1 - x0) * .58)
    cx0 = x0 + max(10, ((x1 - x0) - cw - ew) / 2); cxm = cx0 + cw / 2
    a0 = E(t, b["t"], .3)
    if b.get("start") and a0 > .01:
        _pill(d, cxm, y0 + 32 - (1 - a0) * 16, b["start"], 30, OR, (28, 22, 16), a0, h=60)
        if b.get("payload"):
            w_ = _tw(b["payload"], 24) + 30; px_ = min(cx0 + cw + 50, x1 - w_ - 4); d.rounded_rectangle((px_, y0 + 12, px_ + w_, y0 + 52), 10, outline=A(OR, a0), width=3); txt(d, (px_ + w_ / 2, y0 + 32), b["payload"], 24, A(CY_, a0))
    ys = [y0 + sh + 26 + i * (ch + lg) for i in range(n)]
    for i, s in enumerate(S):
        al = E(t, s["t"], .3)
        if al < .01: continue
        col = _hex_rgb(s.get("color", "#4C8DFF")); ya = ys[i] + (1 - al) * 22
        if i == 0 and b.get("start"): d.line([(cxm, y0 + 62), (cxm, ya)], fill=A(GRN, al), width=5)
        if i > 0:
            yl = ys[i - 1] + ch; q = ss(prog(t, s["t"] - .1, s["t"] + .3)); d.line([(cxm, yl), (cxm, yl + (ya - yl) * q)], fill=A(CY_, al), width=5)
            if q > .5: _ico(d, "link", cxm, (yl + ya) / 2, 15, CY_, al * q, 4); txt(d, (cxm + 54, (yl + ya) / 2), b.get("link", "Next"), 22, A(CY_, al * q), anchor="lm")
        flash = 1 - prog(t, s["t"], s["t"] + .6)
        d.rounded_rectangle((cx0, ya, cx0 + cw, ya + ch), 22, fill=A(lerp(CARDC, col, .12 + .1 * flash), al), outline=A(col, al), width=3)
        d.rectangle((cx0 + 18, ya, cx0 + cw - 18, ya + 6), fill=A(col, al))
        isz = min(76, ch - 30); d.rounded_rectangle((cx0 + 22, ya + ch / 2 - isz / 2 + 2, cx0 + 22 + isz, ya + ch / 2 + isz / 2 + 2), 16, fill=A(lerp(CARDC, col, .25), al), outline=A(col, al), width=2)
        _ico(d, s.get("icon", "gear"), cx0 + 22 + isz / 2, ya + ch / 2 + 2, isz * .32, col, al)
        tx = cx0 + 22 + isz + 26
        txt(d, (tx, ya + ch / 2 - (16 if s.get("sub") else -2)), s["name"], _fit(s["name"], 32, cx0 + cw - tx - 16, 18), A(PAPER, al), anchor="lm")
        if s.get("sub"): txt(d, (tx, ya + ch / 2 + 24), s["sub"], _fit(s["sub"], 24, cx0 + cw - tx - 16, 15), A(_tx(col), al), anchor="lm")
        if s.get("err"):
            te, lab = s["err"]; q = ss(prog(t, te, te + .5))
            if q > 0:
                ex = cx0 + cw + 24; ey = ya + ch / 2; pw = _tw(lab, 26) + 76; px = cx0 + cw + 90
                _dash(d, (ex, ey), (px - 4, ey), RED, al, 4, frac=q)
                if q > .8: _arrow(d, (px - 4, ey), 0, RED, al); d.rounded_rectangle((px, ey - 27, px + pw, ey + 27), 27, fill=A(lerp(CARDC, RED, .22), al), outline=A(RED, al), width=3); d.ellipse((px + 12, ey - 15, px + 42, ey + 15), fill=A(RED, al)); _ico(d, "x", px + 27, ey, 9, PAPER, al, 3); txt(d, (px + 56 + (pw - 76) / 2, ey), lab, 26, A(PAPER, al))


# ------------------------------------------------------------------ hub
def draw_hub(d, box, b, t, k):
    """Hub and spokes: {t, top:"E-commerce App", user:"User", hub:{name,sub,icon,color}, actions:[{t,name,icon,color,to:[spoke idx]}],
    spokes:[{t,name,icon,color}], numbered:False, q:"Arabic bubble text", q_t}   packets of each action run top -> hub -> its spokes"""
    x0, y0, x1, y1 = box; H = b["hub"]; S = b["spokes"]; ACT = b.get("actions", []); hc = _hex_rgb(H.get("color", "#E0607A"))
    cx = (x0 + x1) / 2; has_top = bool(ACT); topH = 150 if has_top else 0
    hw, hh = (560 if WIDE else 640), 118; hy0 = y0 + topH + (60 if has_top else 10); hy1 = hy0 + hh
    sr = 46 if WIDE else 42; sy = y1 - sr - 54; n = len(S)
    sxs = [x1 - 80 - i * ((x1 - x0 - 160) / max(1, n - 1)) for i in range(n)] if n > 1 else [cx]
    if has_top:
        a = E(t, b["t"], .3)
        if a > .01:
            d.rounded_rectangle((x0, y0, x1, y0 + topH), 30, fill=A(lerp(CARDC, (60, 140, 200), .08), a), outline=A((60, 150, 200), a), width=3)
            txt(d, (x0 + 40, y0 + 36), b.get("top", ""), 28, A(PAPER, a), anchor="lm")
            if b.get("user"): _pill(d, x1 - 40 - _tw(b["user"], 24) - 52, y0 + 36, b["user"], 24, None, (120, 200, 240), a, border=(120, 200, 240), h=44, anchor="l")
        pw = (x1 - x0 - 80) / len(ACT)
        for i, ac in enumerate(ACT):
            al = E(t, ac["t"], .3)
            if al < .01: continue
            ac_c = _hex_rgb(ac["color"]); pcx = x1 - 40 - pw * (i + .5); pyy = y0 + 104; wd = min(pw - 20, _tw(ac["name"], 26) + 90)
            d.rounded_rectangle((pcx - wd / 2, pyy - 28, pcx + wd / 2, pyy + 28), 28, fill=A(ac_c, al)); _ico(d, ac.get("icon", "bolt"), pcx - wd / 2 + 30, pyy, 11, (20, 22, 26), al, 3); txt(d, (pcx + 14, pyy), ac["name"], 26, A((20, 22, 26), al))
            q = ss(prog(t, ac["t"] + .1, ac["t"] + .9)); p0 = (pcx, pyy + 30); p1 = (cx + (pcx - cx) * .45, hy0)
            d.line([p0, (p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q)], fill=A(ac_c, al), width=4)
            if q > .95: _arrow(d, p1, math.atan2(p1[1] - p0[1], p1[0] - p0[0]), ac_c, al)
    ah = E(t, H.get("t", b["t"]), .3)
    if ah > .01:
        d.rounded_rectangle((cx - hw / 2 + 8, hy0 + 8, cx + hw / 2 + 8, hy1 + 8), 26, fill=A(lerp(BASEC, hc, .25), ah)); d.rounded_rectangle((cx - hw / 2, hy0, cx + hw / 2, hy1), 26, fill=A(lerp(CARDC, hc, .18), ah), outline=A(hc, ah), width=3)
        d.rectangle((cx - hw / 2 + 20, hy0, cx + hw / 2 - 20, hy0 + 6), fill=A(hc, ah)); d.rounded_rectangle((cx - hw / 2 + 24, hy0 + 24, cx - hw / 2 + 96, hy0 + 96), 16, outline=A(hc, ah), width=2); _ico(d, H.get("icon", "cart"), cx - hw / 2 + 60, hy0 + 60, 22, hc, ah)
        txt(d, (cx - hw / 2 + 120, hy0 + (44 if H.get("sub") else 59)), H["name"], _fit(H["name"], 34, hw - 150, 20), A(PAPER, ah), anchor="lm")
        if H.get("sub"): txt(d, (cx - hw / 2 + 120, hy0 + 84), H["sub"], _fit(H["sub"], 24, hw - 150, 15), A(_tx(hc), ah), anchor="lm")
    curves = []
    for j, sp in enumerate(S):
        ax = cx + (sxs[j] - cx) * .55; p0 = (ax, hy1 + 4); p3 = (sxs[j], sy - sr - 10); curves.append((p0, (ax, hy1 + (p3[1] - hy1) * .55), (sxs[j], hy1 + (p3[1] - hy1) * .35), p3))
    for j, sp in enumerate(S):
        al = E(t, sp["t"], .3)
        if al < .01: continue
        sc = _hex_rgb(sp["color"]); p0, p1, p2, p3 = curves[j]; q = ss(prog(t, sp["t"] - .1, sp["t"] + .6)); pts = [_bz(p0, p1, p2, p3, u / 28 * q) for u in range(29)]
        d.line(pts, fill=A(lerp(hc, BASEC, .15), al), width=4, joint="curve")
        if q > .95: _arrow(d, p3, math.atan2(p3[1] - p2[1], p3[0] - p2[0]), hc, al)
        hit = 0.0
        for ac in ACT:
            if j in ac.get("to", []): qq = prog(t, ac["t"] + .9, ac["t"] + 1.9); hit = max(hit, 1 - abs(qq - 1) * 0) if 0 < qq < 1 else hit
        for ac in ACT:
            if j in ac.get("to", []):
                qq = prog(t, ac["t"] + .9 + .12 * j, ac["t"] + 1.9 + .12 * j)
                if 0 < qq < 1:
                    x, y = _bz(p0, p1, p2, p3, ss(qq)); c = _hex_rgb(ac["color"]); d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=A(c, .22 * al)); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=A(c, al), outline=A(PAPER, al), width=2)
        d.ellipse((sxs[j] - sr, sy - sr, sxs[j] + sr, sy + sr), fill=A(lerp(CARDC, sc, .22), al), outline=A(sc, al), width=4 if hit else 3); _ico(d, sp.get("icon", "cube"), sxs[j], sy, sr * .42, sc, al)
        txt(d, (sxs[j], sy + sr + 28), sp["name"], _fit(sp["name"], 26, 150, 16), A(_tx(sc), al))
        if b.get("numbered") and q > .8:
            mxp, myp = _bz(p0, p1, p2, p3, .5); d.ellipse((mxp - 19, myp - 19, mxp + 19, myp + 19), fill=A(sc, al), outline=A(PAPER, al), width=2); txt(d, (mxp, myp), str(j + 1), 24, A((20, 22, 26), al))
    if b.get("q"):
        qa = E(t, b.get("q_t", b["t"]), .3)
        if qa > .01: _pill(d, cx, hy1 + 66, b["q"], 30, lerp(CARDC, hc, .22), PAPER, qa, border=hc, h=62)


# ------------------------------------------------------------------ pipeline
def draw_pipeline(d, box, b, t, k):
    """Horizontal pipeline of round steps joined by chain links. {t, nodes:[{t,name,icon,color,badge:(t,'NEW','#hex')}]}   9:16 wraps to rows of 3"""
    x0, y0, x1, y1 = box; N = b["nodes"]; n = len(N); per = n if WIDE else 3; rows = -(-n // per); r = 54 if WIDE else 56
    rowh = 220; ty = y0 + 70
    for i, nd in enumerate(N):
        row, ci = divmod(i, per); cnt = min(per, n - row * per)
        mg = 70 if WIDE else 120; cx = x1 - mg - ci * ((x1 - x0 - 2 * mg) / max(1, cnt - 1)) if cnt > 1 else (x0 + x1) / 2; cy = ty + row * rowh + r
        nd["_p"] = (cx, cy)
    for i in range(n - 1):
        a, c = N[i], N[i + 1]; al = min(E(t, a["t"], .3), E(t, c["t"], .3))
        if al < .01 or abs(a["_p"][1] - c["_p"][1]) > 1: continue
        xa, xb = a["_p"][0] - r, c["_p"][0] + r; d.line([(xa, a["_p"][1]), (xb, c["_p"][1])], fill=A(CY_, al), width=5); _ico(d, "link", (xa + xb) / 2, a["_p"][1], 17, CY_, al, 4)
    for nd in N:
        al = E(t, nd["t"], .35)
        if al < .01: continue
        cx, cy = nd["_p"]; col = _hex_rgb(nd["color"]); pop = 1 + .12 * math.sin(math.pi * prog(t, nd["t"] - .1, nd["t"] + .5)); rr = r * pop
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=A(lerp(CARDC, col, .2), al), outline=A(col, al), width=4); _ico(d, nd.get("icon", "gear"), cx, cy, r * .42, col, al)
        txt(d, (cx, cy + r + 30), nd["name"], _fit(nd["name"], 26, 190, 15), A(_tx(col), al))
        if nd.get("badge"):
            tb, lab = nd["badge"][:2]; bc = _hex_rgb(nd["badge"][2]) if len(nd["badge"]) > 2 else OR; ba = E(t, tb, .3)
            if ba > .01: _pill(d, cx, cy - r - 30 - (1 - ba) * 12, lab, 24, bc, (20, 22, 26) if bc[0] > 200 else PAPER, ba, h=42, padx=18)


# ------------------------------------------------------------------ deviceflow
def draw_deviceflow(d, box, b, t, k):
    """Phone + API + checklist: {t, phone:{title, fields:[(icon,text)], button, press_t}, api:{name,sub,color,t},
    steps:[{t, tag, label, icon, color:"#hex"}]}  an elbow line leaves the API and feeds each step; a check badge pops when the step passes"""
    x0, y0, x1, y1 = box; P = b["phone"]; S = b["steps"]; n = len(S); a0 = E(t, b["t"], .3)
    if WIDE: px0, px1, py0, py1 = x0 + 10, x0 + 380, y0, y1
    else: pw_ = 440; px0, px1 = (x0 + x1) / 2 - pw_ / 2, (x0 + x1) / 2 + pw_ / 2; py0, py1 = y0, y0 + 520
    if a0 > .01:
        dy = (1 - a0) * 26
        d.rounded_rectangle((px0, py0 + dy, px1, py1 + dy), 56, fill=A((16, 18, 24), a0), outline=A(CY_, a0), width=4); PAPER_ = PT; d.rounded_rectangle(((px0 + px1) / 2 - 58, py0 + 16 + dy, (px0 + px1) / 2 + 58, py0 + 30 + dy), 7, fill=A((50, 54, 64), a0))
        cx = (px0 + px1) / 2; txt(d, (cx, py0 + 96 + dy), P.get("title", ""), 36, A(PT, a0)); fy = py0 + 170 + dy
        for ic, tx in P.get("fields", []):
            d.rounded_rectangle((px0 + 30, fy - 34, px1 - 30, fy + 34), 16, outline=A((84, 88, 100), a0), fill=A((28, 30, 38), a0), width=3); _ico(d, ic, px0 + 66, fy, 15, (160, 166, 180), a0, 3); txt(d, (px0 + 100, fy), tx, 24, A(PT, a0), anchor="lm"); fy += 96
        press = P.get("press_t"); pz = 1 + (.06 * math.sin(math.pi * prog(t, press, press + .4)) if press else 0); by_ = py1 - 90 + dy
        d.rounded_rectangle((cx - 120 * pz, by_ - 40 * pz, cx + 120 * pz, by_ + 40 * pz), 40, fill=A(OR, a0)); txt(d, (cx, by_), P.get("button", "Login"), 32, A((24, 20, 16), a0))
    A_ = b["api"]; aa = E(t, A_.get("t", b["t"] + .3), .3); ac = _hex_rgb(A_.get("color", "#31B3E8"))
    if WIDE: ax0, ax1, ay0, ay1 = x1 - 520, x1 - 20, y0 + 6, y0 + 126; sx0, sx1 = px1 + 70, x1 - 150; sy0 = y0 + 190; lx = x1 - 76
    else: ax0, ax1, ay0, ay1 = x1 - 480, x1 - 20, py1 + 24, py1 + 144; sx0, sx1 = x0 + 10, x1 - 120; sy0 = ay1 + 60; lx = x1 - 60
    if aa > .01:
        d.rounded_rectangle((ax0, ay0, ax1, ay1), 24, fill=A(lerp(CARDC, ac, .14), aa), outline=A(ac, aa), width=3); d.rectangle((ax0 + 18, ay0, ax1 - 18, ay0 + 6), fill=A(ac, aa))
        d.rounded_rectangle((ax0 + 22, ay0 + 26, ax0 + 98, ay0 + 102), 16, outline=A(ac, aa), width=2); _ico(d, "server", ax0 + 60, ay0 + 64, 24, ac, aa)
        txt(d, (ax0 + 122, ay0 + 48), A_["name"], 32, A(PAPER, aa), anchor="lm"); txt(d, (ax0 + 122, ay0 + 88), A_.get("sub", ""), 24, A(ac, aa), anchor="lm")
    gap = 14; sh_ = min(112, (y1 - sy0 - gap * (n - 1)) / n); ys = [sy0 + i * (sh_ + gap) for i in range(n)]
    if n and aa > .01:
        q = ss(prog(t, S[0]["t"] - .6, S[-1]["t"])); yend = ys[-1] + sh_ / 2; yst = ay1
        d.line([(lx, yst), (lx, yst + (yend - yst) * q)], fill=A(ac, aa), width=5)
    for i, s in enumerate(S):
        al = E(t, s["t"], .3)
        if al < .01: continue
        col = _hex_rgb(s["color"]); ya = ys[i] + (1 - al) * 18; yc = ya + sh_ / 2
        d.line([(lx, yc), (sx1 + 6, yc)], fill=A(ac, al), width=5); _arrow(d, (sx1 + 6, yc), math.pi, ac, al)
        d.rounded_rectangle((sx0, ya, sx1, ya + sh_), 22, fill=A(lerp(CARDC, col, .1), al), outline=A(col, al), width=3); d.rectangle((sx0 + 18, ya, sx1 - 18, ya + 6), fill=A(col, al))
        _pill(d, sx0 + 22, ya + sh_ / 2, s["tag"], 22, lerp(CARDC, col, .2), _tx(col), al, border=col, h=40, padx=16, anchor="l")
        isz = min(64, sh_ - 28); d.rounded_rectangle((sx1 - 18 - isz, ya + sh_ / 2 - isz / 2, sx1 - 18, ya + sh_ / 2 + isz / 2), 14, fill=A(lerp(CARDC, col, .25), al), outline=A(col, al), width=2); _ico(d, s.get("icon", "check"), sx1 - 18 - isz / 2, ya + sh_ / 2, isz * .3, col, al)
        txt(d, (sx1 - 36 - isz, ya + sh_ / 2), s["label"], _fit(s["label"], 32, sx1 - sx0 - isz - 260, 20), A(PAPER, al), anchor="rm")
        qb = ss(prog(t, s["t"] + .3, s["t"] + .7))
        if qb > 0: _okbadge(d, sx0 + 14, ya + 4, 20 * qb, al)


# ------------------------------------------------------------------ codeann
_KW = {"if", "return", "var", "await", "public", "class", "async", "null", "is", "new", "else", "for", "const", "let", "function", "using", "private", "static", "void", "def", "import", "from", "true", "false", "throw", "try", "catch", "case", "switch"}


def _tokline(s):
    out = []; i = 0
    import re
    for m in re.finditer(r'"[^"]*"|\'[^\']*\'|\w+|\s+|.', s):
        w = m.group(0); c = PAPER
        if w[0] in "\"'": c = (240, 170, 110)
        elif w in _KW: c = (200, 140, 255)
        elif w.isdigit(): c = (240, 170, 110)
        elif w[0].isupper() and w.isidentifier(): c = (120, 220, 190)
        elif w.isidentifier() and s[m.end():m.end() + 1] == "(": c = (250, 230, 140)
        elif w.isidentifier(): c = (150, 200, 255)
        elif w.strip() == "": c = PAPER
        else: c = (190, 195, 210)
        out.append((w, c))
    return out


def draw_codeann(d, box, b, t, k):
    """Annotated code: {t, file, lang:"C#", lines:[(t, text)], squiggle:[(t, line_idx)], tags:[(t, line_idx, text, '#hex')],
    counter:(t, 'if x 10'), bar:(t0, t1, '#hex'), label:(t, text, '#hex'), cap:(t, 'Arabic caption')}   Latin code only; keep it under ~12 lines for a readable size"""
    x0, y0, x1, y1 = box; al = E(t, b["t"], .3)
    if al < .01: return
    L = b["lines"]; n = len(L); foot = 190 if (b.get("counter") or b.get("bar") or b.get("cap")) else 0
    wh = y1 - y0 - foot; lh = min(50, (wh - 96) / max(1, n)); tagw0 = 230 if b.get("tags") else 0; fs = min(int(lh * .62), int((x1 - x0 - 78 - tagw0 - 30) / (.6 * max(len(l_[1]) for l_ in L)))); dy = (1 - al) * 24
    d.rounded_rectangle((x0, y0 + dy, x1, y0 + wh + dy), 26, fill=A((14, 16, 22), al), outline=A((60, 64, 76), al), width=3)
    for j, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): d.ellipse((x0 + 26 + j * 28, y0 + 24 + dy, x0 + 44 + j * 28, y0 + 42 + dy), fill=A(c, al))
    tx0 = x0 + 150; lang = b.get("lang", "")
    if lang: d.rounded_rectangle((tx0, y0 + 14 + dy, tx0 + 62, y0 + 50 + dy), 8, fill=A((90, 40, 140), al)); txt(d, (tx0 + 31, y0 + 32 + dy), lang, 20, A(PAPER, al))
    txt(d, (tx0 + (74 if lang else 0), y0 + 32 + dy), b.get("file", ""), 26, A(PAPER, al), anchor="lm")
    ty0 = y0 + 78 + dy; font = F(MONO, fs); tagw = 230 if b.get("tags") else 0
    for i, (tl, text) in enumerate(L):
        a2 = E(t, tl, .2) * al
        if a2 < .01: continue
        yy = ty0 + i * lh + lh / 2; txt(d, (x0 + 56, yy), str(i + 1), max(12, fs - 4), A((90, 96, 110), a2), anchor="rm")
        xx = x0 + 78; shown = int(len(text) * min(1, prog(t, tl, tl + .5)))
        for w, c in _tokline(text[:shown]): d.text((xx, yy), w, font=font, fill=A(c, a2), anchor="lm"); xx += font.getlength(w)
        for (ts, li) in b.get("squiggle", []):
            if li == i and t >= ts:
                wlen = font.getlength(text) * ss(prog(t, ts, ts + .5)); xs = x0 + 78; yb = yy + fs * .62; pts = []
                m = 0
                while m * 6 <= wlen: pts.append((xs + m * 6, yb + (3 if m % 2 else -1))); m += 1
                if len(pts) > 1: d.line(pts, fill=A(RED, a2), width=2)
    for (ts, li, lab, hx) in b.get("tags", []):
        ta = E(t, ts, .3) * al
        if ta > .01 and li < n:
            c = _hex_rgb(hx); yy = ty0 + li * lh + lh / 2; _pill(d, x1 - 28 - tagw / 2, yy, lab, max(18, fs - 4), lerp((16, 16, 14), c, .22), c, ta, border=c, h=min(46, lh * .9), padx=20)
    fy = y0 + wh + 44 + dy
    if b.get("counter"):
        tc, lab = b["counter"]; ca = E(t, tc, .3)
        if ca > .01: w_ = _tw(lab, 32) + 96; d.rounded_rectangle((x0 + 40, fy - 30, x0 + 40 + w_, fy + 30), 30, fill=A((40, 16, 18), ca), outline=A(RED, ca), width=3); _ico(d, "code", x0 + 76, fy, 13, RED, ca, 3); txt(d, (x0 + 100, fy), lab, 32, A(PT, ca), anchor="lm")
    if b.get("label"):
        tl, lab, hx = b["label"]; la = E(t, tl, .3)
        if la > .01: txt(d, (x1 - 60, fy), lab, 36, A(_hex_rgb(hx), la), anchor="rm")
    if b.get("bar"):
        t0, t1, hx = b["bar"]; q = ss(prog(t, t0, t1)); bc = _hex_rgb(hx); by = fy + 46
        if q > 0: d.rounded_rectangle((x0 + 20, by - 14, x1 - 20 - (x1 - x0 - 40) * (1 - q), by + 14), 14, fill=A(bc, al))
    if b.get("cap"):
        tc, lab = b["cap"]; ca = E(t, tc, .3)
        if ca > .01: _pill(d, (x0 + x1) / 2, y1 - 28, lab, 30, lerp(CARDC, RED, .15), PAPER, ca, border=RED, h=58)


# ------------------------------------------------------------------ flowmini
def draw_flowmini(d, box, b, t, k):
    """Small left-to-right flow: {t, items:[{t, kind:'pill'|'card'|'circle', name, icon, color:'#hex', sub}]}  a dot runs along each link. 9:16 stacks it."""
    x0, y0, x1, y1 = box; I = b["items"]; n = len(I)
    cy = y0 + 100; cxm = (x0 + x1) / 2
    pos = [(x1 - 210 - i * ((x1 - x0 - 420) / max(1, n - 1)), cy) if WIDE else (cxm, y0 + 70 + i * 190) for i in range(n)]
    for i in range(n - 1):
        a, c = I[i], I[i + 1]; al = min(E(t, a["t"]), E(t, c["t"]))
        if al < .01: continue
        pa, pb = pos[i], pos[i + 1]; col = _hex_rgb(c.get("color", "#FF9A1F")); off = 130 if WIDE else 62
        if WIDE: p0, p1 = (pa[0] - off, pa[1]), (pb[0] + off, pb[1])
        else: p0, p1 = (pa[0], pa[1] + off), (pb[0], pb[1] - off)
        d.line([p0, p1], fill=A(col, al), width=5)
        q = ((t - c["t"]) % 1.8) / 1.1 if t >= c["t"] else 2
        if 0 < q < 1: x = p0[0] + (p1[0] - p0[0]) * ss(q); y = p0[1] + (p1[1] - p0[1]) * ss(q); d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=A(col, al), outline=A(PAPER, al), width=2)
    for i, it in enumerate(I):
        al = E(t, it["t"], .3)
        if al < .01: continue
        cx, cyy = pos[i]; col = _hex_rgb(it.get("color", "#FF9A1F")); kind = it.get("kind", "card"); dy = (1 - al) * 18
        if kind == "pill":
            w_ = _tw(it["name"], 30) + 120; d.rounded_rectangle((cx - w_ / 2, cyy - 34 + dy, cx + w_ / 2, cyy + 34 + dy), 34, fill=A(col, al)); _ico(d, it.get("icon", "bolt"), cx - w_ / 2 + 42, cyy + dy, 13, (20, 22, 26), al, 3); txt(d, (cx + 20, cyy + dy), it["name"], 30, A((20, 22, 26), al))
        elif kind == "circle":
            r = 62; d.ellipse((cx - r, cyy - r + dy, cx + r, cyy + r + dy), fill=A(lerp(CARDC, col, .25), al), outline=A(col, al), width=4); _ico(d, it.get("icon", "gear"), cx, cyy + dy, 26, col, al); txt(d, (cx, cyy + r + 32 + dy), it["name"], 28, A(_tx(col), al))
        else:
            w_ = max(300, _tw(it["name"], 30) + 130); d.rounded_rectangle((cx - w_ / 2 + 7, cyy - 44 + 7 + dy, cx + w_ / 2 + 7, cyy + 44 + 7 + dy), 24, fill=A(lerp(BASEC, col, .2), al)); d.rounded_rectangle((cx - w_ / 2, cyy - 44 + dy, cx + w_ / 2, cyy + 44 + dy), 24, fill=A(CARDC, al), outline=A(col, al), width=3)
            d.rectangle((cx - w_ / 2, cyy - 30 + dy, cx - w_ / 2 + 8, cyy + 30 + dy), fill=A(col, al)); _ico(d, it.get("icon", "doc"), cx - w_ / 2 + 44, cyy + dy, 17, col, al); txt(d, (cx - w_ / 2 + 78, cyy + dy), it["name"], _fit(it["name"], 30, w_ - 100, 16), A(PAPER, al), anchor="lm")


DRAW.update({"titlevs": draw_titlevs, "split": draw_split, "chain": draw_chain, "hub": draw_hub, "pipeline": draw_pipeline, "deviceflow": draw_deviceflow, "codeann": draw_codeann, "flowmini": draw_flowmini})
EXTRA_H.update({
    "titlevs": lambda b, w: 160,
    "split": lambda b, w: int(RY1 - RY0),
    "chain": lambda b, w: int(min(RY1 - RY0, (64 if b.get("start") else 0) + 26 + len(b["steps"]) * 190)),
    "hub": lambda b, w: int(min(RY1 - RY0, 700 if WIDE else 980)),
    "pipeline": lambda b, w: 300 if WIDE else 150 + 230 * (-(-len(b["nodes"]) // 3)),
    "deviceflow": lambda b, w: int(RY1 - RY0),
    "codeann": lambda b, w: int(min(RY1 - RY0, 760 if WIDE else 900)),
    "flowmini": lambda b, w: 220 if WIDE else 190 * len(b["items"]) + 80,
})
