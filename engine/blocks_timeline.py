# "Tracks" block (loaded by anim.py after blocks_path.py): an editing timeline that explains video / audio workflows by animation.
# Tracks (video, audio with waveform, subtitle), clips, playhead, trim, razor/split, clip move, clip removal, keyframes, track activation.
#
#   {"k": "tracks", "t": 0.2, "h": 640, "dur": 20.0,                       # dur: timeline length in seconds shown across the width
#    "tracks": [{"id": "v1", "kind": "video", "name": "V1", "active": [(9.0, False), (12.0, True)],       # active: (t, bool) track on/off (dimmed when off)
#                "clips": [{"id": "c1", "start": 0, "len": 6, "label": "Intro", "tone": "blue", "t": 0.5,   # start/len in timeline seconds, t = appears at
#                           "edits": [(4.0, 0.5, 5.0)],              # (t, new_start, new_len): trim and/or move, eased over 0.45 s
#                           "split": (6.5, 3.0), "split_move": (7.2, 1.5),   # razor at timeline pos 3.0 at time 6.5; right half then slides +1.5 s at 7.2
#                           "keys": [(1.0, 2.5), (2.0, 4.0)],      # keyframe diamonds: (appears at t, timeline pos)
#                           "until": 12.0}]},                        # clip removal at time t
#               {"id": "a1", "kind": "audio", "name": "A1", "clips": [{"id": "m", "start": 0, "len": 20, "label": "Voice", "tone": "green", "t": 0.8}]},
#               {"id": "s1", "kind": "subtitle", "name": "SUB", "clips": [{"id": "s", "start": 1, "len": 3, "label": "Hello", "tone": "orange", "t": 1.0}]}],
#    "playhead": [(0.5, 0.0), (8.0, 10.0)]}                        # (t, timeline pos) keyframes, linear between, held after the last
# Same drawing in 16:9 and 9:16 (track height adapts). Pure function of time.
_TLD = 0.45
def _tl_step(t, edits, s0, l0):
    cur = (s0, l0)
    for te, s, l in edits:
        if t < te: break
        u = ss(prog(t, te, te + _TLD)); cur = (cur[0] + (s - cur[0]) * u, cur[1] + (l - cur[1]) * u) if u < 1 else (s, l)
    return cur
def _tl_wave(seed, n):
    x = sum(ord(c) * (i + 3) for i, c in enumerate(seed)) % 2147483647 or 7; out = []
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648; out.append(0.18 + 0.82 * ((x >> 8) % 1000) / 1000.0 * (0.55 + 0.45 * abs(math.sin(i * 0.19))))
    return out
def _tl_active(t, tr):
    """1.0 = track on, 0.0 = off, eased over 0.3 s at every (t, bool) change"""
    cur = last = 1.0
    for te, v in tr.get("active", []):
        if t < te: break
        tgt = 1.0 if v else 0.0; u = ss(prog(t, te, te + 0.3)); cur = last + (tgt - last) * u
        if u >= 1: last = tgt
    return cur
def draw_tracks(d, box, b, t, k):
    if t < b["t"]: return
    x0, y0, x1, y1 = box; al0 = E(t, b["t"], 0.35); trs = b.get("tracks", []); dur = float(b.get("dur", 20.0)); lay = d._image
    lab = 92 if WIDE else 100; ruler = 42; top = y0 + (60 if WIDE else 70); gx0 = x0 + lab + 14; gx1 = x1 - 14; px = lambda s: gx0 + (gx1 - gx0) * s / dur
    n = max(1, len(trs)); rh = min(110 if WIDE else 200, (y1 - top - ruler - 20) / n); rh = max(54, rh)
    d.rounded_rectangle((x0, top - 8, x1, top + ruler + n * rh + 14), 24, fill=A(_SD_PANEL, al0), outline=A((14, 14, 12) if LIGHT else (60, 64, 72), al0), width=3 if LIGHT else 2)
    step = 1 if dur <= 12 else 2 if dur <= 30 else 5
    for s in range(0, int(dur) + 1, step):
        xx = px(s); d.line([(xx, top + ruler - 12), (xx, top + ruler - 2)], fill=A(_SD_LINE, al0), width=2); _bt(d, (xx, top + ruler - 24), "%d" % s, 17 if WIDE else 19, A(lerp(_SD_PANEL, (200, 200, 200), .7), al0))
    for ti, tr in enumerate(trs):
        ry = top + ruler + ti * rh; ta = _tl_active(t, tr); tl = 0.35 + 0.65 * ta; kind = tr.get("kind", "video"); tone = _sdc({"video": "blue", "audio": "green", "subtitle": "orange"}.get(kind, "gray"))
        d.rounded_rectangle((gx0 - 6, ry + 4, gx1 + 6, ry + rh - 4), 12, fill=A(lerp(_SD_PANEL, (0, 0, 0) if not LIGHT else (255, 255, 255), .25), al0 * tl))
        _bt(d, (x0 + 40, ry + rh / 2 - 8), tr.get("name", tr["id"]), 24 if WIDE else 26, A((14, 14, 12) if LIGHT else (245, 245, 245), al0 * (0.5 + 0.5 * tl)))
        ex, ey = x0 + 40, ry + rh / 2 + 20; d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), outline=A(tone, al0 * tl), width=2)
        if ta > .5: d.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=A(tone, al0 * tl))
        for c in tr.get("clips", []):
            ca = E(t, c.get("t", b["t"]), 0.3)
            if c.get("until") is not None: ca *= 1 - ss(prog(t, c["until"], c["until"] + 0.35))
            ca *= al0 * tl
            if ca <= 0.01: continue
            s, l = _tl_step(t, c.get("edits", []), c["start"], c["len"]); ctone = _sdc(c.get("tone", {"video": "blue", "audio": "green", "subtitle": "orange"}.get(kind, "gray")))
            parts = [(s, l)]; sp = c.get("split"); shift = 0.0
            if sp and t >= sp[0] and s < sp[1] < s + l:
                if c.get("split_move"): shift = c["split_move"][1] * ss(prog(t, c["split_move"][0], c["split_move"][0] + _TLD))
                parts = [(s, sp[1] - s - 0.04), (sp[1] + shift + 0.04, s + l - sp[1] - 0.04)]
            ch = rh - 16; cy0 = ry + 8
            if c.get("until") is not None: cy0 += 8 * ss(prog(t, c["until"], c["until"] + 0.35))
            for pi, (ps, pl) in enumerate(parts):
                a_, b_ = px(ps), px(ps + pl)
                if b_ - a_ < 3: continue
                d.rounded_rectangle((a_, cy0, b_, cy0 + ch), 10, fill=A(lerp(_SD_PANEL, ctone, .35 if kind != "subtitle" else .22), ca), outline=A(ctone, ca), width=2)
                if kind == "audio":
                    amps = _tl_wave(c["id"], int(c["len"] * 12) + 2); pps = (gx1 - gx0) / dur; j = 0
                    while a_ + 4 + j * 5 < b_ - 4:
                        xx = a_ + 4 + j * 5; idx = max(0, min(len(amps) - 1, int((ps + (xx - a_) / pps - c["start"]) * 12))); hh = amps[idx] * (ch - 22) / 2
                        d.line([(xx, cy0 + ch / 2 - hh), (xx, cy0 + ch / 2 + hh)], fill=A(ctone, ca), width=2); j += 1
                elif kind == "video":
                    for j in range(1, int((b_ - a_) / 70)): d.line([(a_ + j * 70, cy0 + 6), (a_ + j * 70, cy0 + ch - 6)], fill=A(lerp(_SD_PANEL, ctone, .5), ca * .6), width=1)
                if c.get("label") and (pi == 0 or kind != "audio") and (b_ - a_) > 60: _bt(d, (a_ + 12, cy0 + 16), c["label"], 20 if WIDE else 22, A((14, 14, 12) if LIGHT else (245, 245, 245), ca), anchor="lm")
            for kt, kp in c.get("keys", []):
                ka = E(t, kt, 0.25) * ca
                if ka > .01 and any(ps_ - 1e-6 <= kp <= ps_ + pl_ + 1e-6 for ps_, pl_ in parts):
                    kx = px(kp + (shift if len(parts) == 2 and kp >= parts[1][0] - shift - 0.05 else 0)); ky = cy0 + ch - 14; d.polygon([(kx, ky - 9), (kx + 9, ky), (kx, ky + 9), (kx - 9, ky)], fill=A((255, 255, 255), ka), outline=A((14, 14, 12), ka))
            if sp:   # razor flash
                rz = 1 - min(1.0, abs(t - sp[0]) / 0.3)
                if rz > 0.02: xx = px(sp[1]); d.line([(xx, ry + 2), (xx, ry + rh - 2)], fill=A((255, 255, 255), rz * al0), width=4)
    ph = b.get("playhead")
    if ph:
        pos = ph[0][1]
        for (ta_, pa_), (tb_, pb_) in zip(ph, ph[1:] + [(1e9, ph[-1][1])]):
            if t >= ta_: pos = pa_ + (pb_ - pa_) * (prog(t, ta_, tb_) if tb_ < 1e8 else 0)
        if t >= ph[0][0] - 0.2:
            xx = px(max(0, min(dur, pos))); pa = al0 * E(t, ph[0][0] - 0.2, 0.25); d.line([(xx, top + ruler - 4), (xx, top + ruler + n * rh + 6)], fill=A(OR, pa), width=3)
            d.polygon([(xx - 10, top + ruler - 18), (xx + 10, top + ruler - 18), (xx, top + ruler - 2)], fill=A(OR, pa))
EXTRA_H["tracks"] = lambda blk, w: blk.get("h", 640 if WIDE else 1000)
DRAW["tracks"] = draw_tracks
