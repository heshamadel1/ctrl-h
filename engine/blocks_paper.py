# "Paper" blocks (loaded by anim.py after blocks_flow.py): cream cards, black borders, hard shadows, highlighter.
#   quote, chatwin, minichart, skeleton, filegrid, bigcount     They draw the same in every theme; the accent colour (OR) is the highlighter.
LIGHT = bool(_T.get("light")); _FG = (14, 14, 12) if LIGHT else (245, 242, 230); _FG2 = (112, 106, 94) if LIGHT else (150, 146, 134)
_PCRM = (251, 248, 237); _PINK = (14, 14, 12); _PG1 = (112, 106, 94); _PG2 = (80, 76, 68)


def _bf(size): return F(ARB, size)
def _bw(s, size): return _bf(size).getlength(s) if s.isascii() else _bf(size).getlength(s, direction="rtl", language="ar")
def _bt(d, xy, s, size, fill, anchor="mm"):
    if s.isascii(): d.text(xy, s, font=_bf(size), fill=fill, anchor=anchor)
    else: d.text(xy, s, font=_bf(size), fill=fill, anchor=anchor, direction="rtl", language="ar")


def _wrap(s, size, maxw):
    out, cur = [], ""
    for w in s.split(" "):
        t_ = (cur + " " + w).strip()
        if _bw(t_, size) <= maxw or not cur: cur = t_
        else: out.append(cur); cur = w
    return out + [cur] if cur else out


def _hs(d, box, fill, al, r=14, off=9, bw=4):
    """cream box with black border and a hard black shadow"""
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + off, y0 + off, x1 + off, y1 + off), r, fill=A(_PINK, al)); d.rounded_rectangle(box, r, fill=A(fill, al), outline=A(_PINK, al), width=bw)


def _marker(d, x0, x1, ybase, hgt, al, q=1.0):
    if q > .01: d.rectangle((x0, ybase - hgt, x0 + (x1 - x0) * q, ybase), fill=A(OR, al))


# ------------------------------------------------------------------ quote
def _quote_lay(b, W_):
    s = b.get("size", 50 if WIDE else 44); cw = min(W_, 1100 if WIDE else W_); lines = []
    for ln in b["lines"]: lines += [(l_, ln) for l_ in _wrap(ln, s, cw - 130)]
    return s, cw, lines


def draw_quote(d, box, b, t, k):
    """Quote card: {t, who:"Martin Fowler", lines:["sentence", ...], hl:[(word, t)]}  the highlighter sweeps under the listed words at their times"""
    al = E(t, b["t"], .3)
    if al < .01: return
    x0, y0, x1, y1 = box; s, cw, lines = _quote_lay(b, x1 - x0); lh = s * 1.32; para = 22
    ch = len(lines) * lh + (len(b["lines"]) - 1) * para + 110; cx0 = (x0 + x1) / 2 - cw / 2; top = y0 + 80 + (1 - al) * 24
    box_ = (cx0, top, cx0 + cw, top + ch); _hs(d, box_, _PCRM, al)
    nw = _bw(b["who"], 52) + 80; nx = (x0 + x1) / 2 - nw / 2
    _hs(d, (nx, y0 + 6 + (1 - al) * 24, nx + nw, top + 4), OR, al, 6, 8, 4); _bt(d, ((x0 + x1) / 2, y0 + 44 + (1 - al) * 24), b["who"], 52, A(_PINK, al))
    _bt(d, (cx0 + 20, top + 4), "“", 170, A(_PINK, al), "ls"); _bt(d, (cx0 + 14, top - 2), "“", 170, A(OR, al), "ls")
    y = top + 70; seen = 0; rtl = not b["lines"][0].isascii()
    for i, (ln, para_src) in enumerate(lines):
        if i and para_src != lines[i - 1][1]: y += para
        yy = y + lh / 2; xa = cx0 + cw - 60 if rtl else cx0 + 60
        for w_, tw in b.get("hl", []):
            if w_ in ln:
                pre = ln[:ln.index(w_)]; wp = _bw(pre, s) if pre else 0; ww = _bw(w_, s)
                xs = (xa - wp - ww) if rtl else (xa + wp); _marker(d, xs, xs + ww, yy + s * .42, s * .48, al, ss(prog(t, tw, tw + .5)))
        _bt(d, (xa, yy), ln, s, A(_PINK, al), "rm" if rtl else "lm"); y += lh


# ------------------------------------------------------------------ chatwin
def draw_chatwin(d, box, b, t, k):
    """AI chat window: {t, title:"booking-app . AI chat", ask:"Arabic request", ask_t, who:"AI", lines:[(t, code line)], cursor:True}   code is Latin"""
    al = E(t, b["t"], .3)
    if al < .01: return
    x0, y0, x1, y1 = box; ww = min(x1 - x0 - 40, 1000 if WIDE else 980); wx0 = (x0 + x1) / 2 - ww / 2; wh = min(y1 - y0 - 20, 640 if WIDE else 820); dy = (1 - al) * 26; wy0 = y0 + dy
    _hs(d, (wx0, wy0, wx0 + ww, wy0 + wh), _PCRM, al, 4, 12, 4); d.rectangle((wx0, wy0, wx0 + ww, wy0 + 76), fill=A(_PINK, al))
    for j, c in enumerate([(235, 70, 55), (245, 200, 40), (110, 210, 100)]): d.ellipse((wx0 + 26 + j * 36, wy0 + 26, wx0 + 52 + j * 36, wy0 + 52), fill=A(c, al))
    _bt(d, (wx0 + 150, wy0 + 40), b.get("title", ""), 34, A(_PCRM, al), "lm")
    qa = E(t, b.get("ask_t", b["t"] + .3), .3)
    if qa > .01:
        aw = min(ww - 60, _bw(b["ask"], 48) + 70); ax1 = wx0 + ww - 28
        _hs(d, (ax1 - aw, wy0 + 104 + (1 - qa) * 16, ax1, wy0 + 196 + (1 - qa) * 16), OR, qa, 4, 8, 4); _bt(d, (ax1 - aw / 2, wy0 + 150 + (1 - qa) * 16), b["ask"], _fit(b["ask"], 48, aw - 50, 20), A(_PINK, qa))
    L = b["lines"]; t_ai = min([l_[0] for l_ in L]) - .2 if L else b["t"] + 1
    aa = E(t, t_ai, .3)
    if aa > .01:
        d.ellipse((wx0 + 36, wy0 + 238, wx0 + 80, wy0 + 282), fill=A(_PINK, aa)); _ico(d, "bolt", wx0 + 58, wy0 + 260, 11, OR, aa, 3); _bt(d, (wx0 + 96, wy0 + 260), b.get("who", "AI"), 30, A(_PG1, aa), "lm")
        cy0 = wy0 + 306; ch = wy0 + wh - 30 - cy0; d.rectangle((wx0 + 28, cy0, wx0 + ww - 28, cy0 + ch), fill=A((10, 10, 9), aa))
        n = len(L); lh = min(56, (ch - 30) / max(1, n, 5)); fs = min(int(lh * .6), int((ww - 130) / (.6 * max(len(l_[1]) for l_ in L)))); font = F(MONO, fs); xe = ye = None
        for i, (tl, text) in enumerate(L):
            if t < tl: continue
            shown = int(len(text) * min(1, prog(t, tl, tl + .9))); yy = cy0 + 20 + i * lh + lh / 2; xx = wx0 + 52
            for w_, c in _tokline(text[:shown]): d.text((xx, yy), w_, font=font, fill=A(c if c != PAPER else (245, 245, 240), aa), anchor="lm"); xx += font.getlength(w_)
            xe, ye = xx, yy
        if b.get("cursor", True) and xe is not None and int(t * 2.4) % 2 == 0: d.rectangle((xe + 2, ye - fs * .55, xe + 2 + fs * .5, ye + fs * .55), fill=A(OR, aa))


# ------------------------------------------------------------------ minichart
def draw_minichart(d, box, b, t, k):
    """Little charts with a highlighted label: {t, rows:[{t, label:"Arabic", kind:"down"|"up", values:[...optional]}]}   down = red bars shrinking to green, up = yellow bars with a green curve"""
    x0, y0, x1, y1 = box; R = b["rows"]; n = len(R); w = min(x1 - x0 - 40, 960 if WIDE else 940); cx0 = (x0 + x1) / 2 - w / 2; gap = 40; rh = min(250, (y1 - y0 - gap * (n - 1) - 20) / n)
    for i, r in enumerate(R):
        al = E(t, r["t"], .3)
        if al < .01: continue
        ya = y0 + 10 + i * (rh + gap) + (1 - al) * 22; _hs(d, (cx0, ya, cx0 + w, ya + rh), _PCRM, al, 4, 10, 4)
        kind = r.get("kind", "up"); vals = r.get("values") or ([1, .72, .5, .26] if kind == "down" else [.06, .1, .18, .3, .46, .68, .95])
        bx = cx0 + 40; bw = 54 if kind == "down" else 46; bg = 26 if kind == "down" else 18; base = ya + rh - 36; mh = rh - 76; tops = []
        for j, v in enumerate(vals):
            q = ss(prog(t, r["t"] + .3 + .18 * j, r["t"] + .7 + .18 * j)); hh = mh * v * q; x_ = bx + j * (bw + bg)
            col = GRN if (kind == "down" and j == len(vals) - 1) else ((235, 55, 35) if kind == "down" else OR)
            if hh > 1: d.rectangle((x_, base - hh, x_ + bw, base), fill=A(col, al), outline=A(_PINK, al), width=3)
            tops.append((x_ + bw / 2, base - mh * v * q))
        if kind == "down":
            qa = ss(prog(t, r["t"] + .3 + .18 * len(vals), r["t"] + .8 + .18 * len(vals))); ax = bx + len(vals) * (bw + bg) + 6
            if qa > 0: d.line([(ax, base - mh * .35), (ax, base - mh * .35 + 62 * qa)], fill=A(GRN, al), width=5); _arrow(d, (ax, base - mh * .35 + 62 * qa + 12), math.pi / 2, GRN, al, 20) if qa > .9 else None
        else:
            qc = ss(prog(t, r["t"] + .3 + .18 * len(vals), r["t"] + 1.1 + .18 * len(vals))); m = max(2, int(len(tops) * qc * 8))
            pts = [(tops[0][0] + (tops[-1][0] - tops[0][0]) * u / 40, base - mh * (vals[0] + (vals[-1] - vals[0]) * ((u / 40) ** 2.0)) * 1.04 - 8) for u in range(41)][:m * 5 + 1]
            if len(pts) > 1: d.line(pts, fill=A(GRN, al), width=6, joint="curve")
        lx = cx0 + w - 36; lab = r["label"]; fs = _fit(lab, 70, w - (len(vals) * (bw + bg)) - 110, 28, mono=False); wl = _bw(lab, fs)
        _marker(d, lx - wl - 10, lx + 10, ya + rh / 2 + fs * .42, fs * .5, al, ss(prog(t, r["t"] + .5, r["t"] + 1.1))); _bt(d, (lx, ya + rh / 2), lab, fs, A(_PINK, al), "rm")


# ------------------------------------------------------------------ skeleton
def draw_skeleton(d, box, b, t, k):
    """Code window drawn as abstract bars (no readable code): {t, file:"login.tsx", n:9, span:2.5, seed:3, hl:[row idx]}  rows appear one after the other"""
    al = E(t, b["t"], .3)
    if al < .01: return
    import random
    x0, y0, x1, y1 = box; ww = min(x1 - x0 - 40, 980 if WIDE else 960); wx0 = (x0 + x1) / 2 - ww / 2; wh = min(y1 - y0 - 20, 560 if WIDE else 680); dy = (1 - al) * 24; wy0 = y0 + dy
    d.rectangle((wx0 + 12, wy0 + 12, wx0 + ww + 12, wy0 + wh + 12), fill=A(_PINK, al)); d.rectangle((wx0, wy0, wx0 + ww, wy0 + wh), fill=A((11, 11, 10), al), outline=A(_PINK, al), width=4)
    d.rectangle((wx0, wy0, wx0 + ww, wy0 + 78), fill=A(OR, al), outline=A(_PINK, al), width=4)
    for j in range(3): d.ellipse((wx0 + 26 + j * 42, wy0 + 28, wx0 + 52 + j * 42, wy0 + 54), outline=A(_PINK, al), width=4)
    txt(d, (wx0 + 170, wy0 + 40), b.get("file", ""), 40, A(_PINK, al), anchor="lm")
    n = b.get("n", 9); rnd = random.Random(b.get("seed", 3)); span = b.get("span", 2.5); u = (ww - 90) / 24; lh = min(48, (wh - 130) / n); hl = set(b.get("hl", []))
    for i in range(n):
        ind = rnd.choice([0, 0, 2, 3, 4]); segs = [rnd.randint(4, 8)] + [rnd.randint(4, 9) for _ in range(rnd.choice([1, 1, 2]))]; yy = wy0 + 118 + i * lh + lh / 2
        u_ = min(u, (ww - 90) / (ind + sum(segs) + .8 * len(segs)))
        q = ss(prog(t, b["t"] + .3 + span * i / n, b["t"] + .3 + span * i / n + .4)); xx = wx0 + 44 + ind * u_
        for j, sg in enumerate(segs):
            wd = sg * u_ * q
            if wd > 2: d.rounded_rectangle((xx, yy - 8, xx + wd, yy + 8), 8, fill=A(OR if ((j == 0 and (i in hl or (not hl and i % 3 == 0)))) else (_PG1 if j == 0 else _PG2), al))
            xx += sg * u_ + .8 * u_


# ------------------------------------------------------------------ filegrid
def draw_filegrid(d, box, b, t, k):
    """Grid of file cards: {t, files:["user.ts", ...], cols:5, span:2.5, missing:(idx, t), pick:(idx, t)}   missing = dashed card with a red ?, pick = highlighted card"""
    x0, y0, x1, y1 = box; F_ = b["files"]; n = len(F_); cols = b.get("cols", 5 if WIDE else 4); rows = -(-n // cols); gap = 22
    cw = (x1 - x0 - 30 - gap * (cols - 1)) / cols; ch = min(112, (y1 - y0 - 20 - gap * (rows - 1)) / rows); span = b.get("span", 2.5); import random; rnd = random.Random(7)
    for i, nm in enumerate(F_):
        r_, c_ = divmod(i, cols); al = E(t, b["t"] + span * i / n, .25)
        bars = [(rnd.randint(30, 70), rnd.randint(25, 60), rnd.randint(30, 70)) for _ in range(1)][0]
        if al < .01: continue
        cx = x0 + 15 + c_ * (cw + gap); cy = y0 + 10 + r_ * (ch + gap) + (1 - al) * 14; miss = b.get("missing"); pick = b.get("pick")
        isM = miss and miss[0] == i and t >= miss[1]; isP = pick and pick[0] == i and t >= pick[1]
        if isM:
            _dash(d, (cx, cy), (cx + cw, cy), _PG1, al, 3, 10, 8); _dash(d, (cx + cw, cy), (cx + cw, cy + ch), _PG1, al, 3, 10, 8); _dash(d, (cx + cw, cy + ch), (cx, cy + ch), _PG1, al, 3, 10, 8); _dash(d, (cx, cy + ch), (cx, cy), _PG1, al, 3, 10, 8)
            txt(d, (cx + 16, cy + 26), nm, 24, A(_PG1, al * .55), anchor="lm"); _bt(d, (cx + cw / 2 + 6, cy + ch / 2 + 6), "?", int(ch * 1.1), A((235, 55, 35), al), "mm")
            continue
        _hs(d, (cx, cy, cx + cw, cy + ch), OR if isP else _PCRM, al, 3, 6, 3); txt(d, (cx + 16, cy + 26), nm, _fit(nm, 24, cw - 30, 14), A(_PINK, al), anchor="lm")
        by = cy + ch - 40
        d.rounded_rectangle((cx + cw * .24, by, cx + cw * .24 + bars[0] * cw / 220 + 18, by + 9), 5, fill=A(OR if not isP else _PINK, al)); d.rounded_rectangle((cx + cw * .62, by, cx + cw * .62 + bars[1] * cw / 220 + 10, by + 9), 5, fill=A(_PG1, al))
        d.rounded_rectangle((cx + cw * .12, by + 18, cx + cw * .12 + bars[2] * cw / 200 + 14, by + 27), 5, fill=A(_PG2, al))


# ------------------------------------------------------------------ bigcount
_PX = {"0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110", "2": "01110 10001 00001 00010 00100 01000 11111",
       "3": "11110 00001 00001 01110 00001 00001 11110", "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
       "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000", "8": "01110 10001 10001 01110 10001 10001 01110",
       "9": "01110 10001 10001 01111 00001 00010 01100", "/": "00001 00010 00010 00100 01000 01000 10000", "+": "00000 00100 00100 11111 00100 00100 00000"}


def _pix(d, s, x, y, cell, col, al, draw=True):
    """pixel-font text, 5x7 bitmap with each pixel drawn 2x2 cells; returns the width"""
    xx = x
    for ch in s:
        g = _PX.get(ch)
        if g and draw:
            for r_, row in enumerate(g.split()):
                for c_, v in enumerate(row):
                    if v == "1": d.rectangle((xx + c_ * 2 * cell, y + r_ * 2 * cell, xx + c_ * 2 * cell + 2 * cell - 1, y + r_ * 2 * cell + 2 * cell - 1), fill=A(col, al))
        xx += 12 * cell
    return xx - x - 2 * cell


def draw_bigcount(d, box, b, t, k):
    """Big pixel counter: {t, label:"FILE", t0, t1, v0, v1, suffix:"/500+", cell:9}  v1 = the number said in the voiceover"""
    al = E(t, b["t"], .3)
    if al < .01: return
    x0, y0, x1, y1 = box; cell = b.get("cell", 9 if WIDE else 8); v = int(round(b.get("v0", 0) + (b["v1"] - b.get("v0", 0)) * ss(prog(t, b.get("t0", b["t"]), b.get("t1", b["t"] + 2)))))
    num = str(v); wn = _pix(d, num, 0, 0, cell, _FG, al, False); suf = b.get("suffix", ""); ws = _pix(d, suf, 0, 0, cell // 2 + 1, _FG2, al, False) if suf else 0
    lab = b.get("label", ""); fl = 64; wl = _bw(lab, fl) if lab else 0; tot = wl + 30 + wn + 24 + ws; xs = (x0 + x1) / 2 - tot / 2; yy = y0 + 20 + (1 - al) * 16
    if lab: _bt(d, (xs, yy + 14 * cell - 8), lab, fl, A(_FG2, al), "ls")
    _pix(d, num, xs + wl + 30, yy, cell, _FG, al)
    if suf: _pix(d, suf, xs + wl + 30 + wn + 24, yy + 14 * cell - 14 * (cell // 2 + 1) , cell // 2 + 1, _FG2, al)


DRAW.update({"quote": draw_quote, "chatwin": draw_chatwin, "minichart": draw_minichart, "skeleton": draw_skeleton, "filegrid": draw_filegrid, "bigcount": draw_bigcount})
EXTRA_H.update({
    "quote": lambda b, w: int((lambda s, cw, L: len(L) * s * 1.32 + (len(b["lines"]) - 1) * 22 + 110 + 110)(*_quote_lay(b, w))),
    "chatwin": lambda b, w: 660 if WIDE else 840,
    "minichart": lambda b, w: 290 * len(b["rows"]) if WIDE else 300 * len(b["rows"]),
    "skeleton": lambda b, w: 580 if WIDE else 700,
    "filegrid": lambda b, w: int(-(-len(b["files"]) // b.get("cols", 5 if WIDE else 4)) * 134 + 20),
    "bigcount": lambda b, w: int(14 * b.get("cell", 9 if WIDE else 8) + 50),
})
