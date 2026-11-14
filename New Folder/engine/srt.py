"""Subtitles (.srt) from times.json (made by align.py).
usage: python3 srt.py times.json [--out video.srt] [--from 0 --to 161.7] [--max-chars 42]
--from/--to : only that window, times shifted to start at 0 (for a split part).  Long lines are cut at word boundaries, time shared by length."""
import sys, json, re
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
def ts(t): t = max(0.0, t); h, r = divmod(int(t), 3600); m, s = divmod(r, 60); return "%02d:%02d:%02d,%03d" % (h, m, s, int(round((t - int(t)) * 1000)) % 1000)
def chunks(text, n):
    words = text.split(); out = []; cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out
if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8")); a = float(opt("--from", 0)); b = float(opt("--to", d["duration"])); mx = int(opt("--max-chars", 42))
    cues = []
    for ln in d["lines"]:
        t0, t1 = max(ln["t0"], a), min(ln["t1"] - 0.15, b)
        if t1 <= t0: continue
        parts = chunks(ln["text"], mx); tot = sum(len(p) for p in parts); cur = t0
        for p in parts:
            dt = (t1 - t0) * len(p) / tot; cues.append((cur - a, cur + dt - a, p)); cur += dt
    txt = "\n".join("%d\n%s --> %s\n%s\n" % (i, ts(x), ts(y), t) for i, (x, y, t) in enumerate(cues, 1))
    out = opt("--out", "video.srt"); open(out, "w", encoding="utf-8").write(txt); print("%d cues -> %s" % (len(cues), out))
