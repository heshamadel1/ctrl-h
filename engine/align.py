"""Timing of every script line inside the voiceover.
usage: python3 align.py voice.wav script.txt [--out times.json] [--asr asr.json | --whisper] [--skip-title]
Default method (no extra install): silence detection + the characters of each line (a line starts at the pause nearest to its share of the speech).
--whisper (optional, needs `pip install faster-whisper` and a downloaded model): uses word timestamps instead; language from CTRLH_WHISPER_LANG (default ar). Lines are placed by their share of the words spoken (character count), not by matching the text, and any whisper failure falls back to the silence method with a message. The logic is tested with a stand-in model (tests/align_test.py); a real model has not been run in the kit's test environment.
--asr asr.json (best): matches the TEXT of every script line against what was really said, tolerant of speech-recognition mistakes (fuzzy character matching, Arabic letter variants, order kept). asr.json comes from `python3 asr_phrases.py voice.wav --model DIR --out asr.json` (offline, see asr_phrases.py) or is the same phrases written as `#N t0-t1: text` lines. A line starts where its first words were spoken, snapped to the phrase start when close.
Script format: one sentence per line; blank lines, lines starting with '[' (section headers) and '---' are skipped; with --skip-title the first line is ignored.
Writes times.json {"method", "duration", "lines": [{"i", "text", "t0", "t1", "section"}]} and prints `S = [...]` to paste into the scene file."""
import sys, os, re, json, subprocess
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
def duration(wav): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).decode().strip())
def parse_script(path, skip_title=False):
    L = open(path, encoding="utf-8").read().split("\n"); out = []; sec = ""; first = True
    for l in L:
        l = l.strip()
        if first and l and skip_title: first = False; continue
        if l: first = False
        if not l or l.startswith("---"): continue
        if l.startswith("["): sec = l.strip("[]"); continue
        out.append((l, sec))
    return out
def pauses(wav, noise="-35dB", d=0.3):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=noise=%s:d=%s" % (noise, d), "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    return list(zip(st, en))
def weights(lines): return [len(re.sub(r"\s", "", t)) + 8 for t, _ in lines]
def by_silence(wav, lines, dur):
    P = pauses(wav); ends = [e for _, e in P]; starts_ = [s for s, _ in P]
    t_first = ends[0] if P and P[0][0] < 0.2 else 0.0; t_last = starts_[-1] if P and P[-1][1] >= dur - 0.2 else dur
    w = weights(lines); tot = sum(w); cum = 0; est = []
    for x in w: est.append(t_first + (t_last - t_first) * cum / tot); cum += x
    S = monotonic(est, ends, t_first, dur); return S
def monotonic(est, ends, t_first, dur, gap=0.8, reach=4.0, own=1.3):
    """Pick one start per line: strictly increasing (>= gap apart), each line at a different pause end near its estimated time, or at its own estimate when no free pause is near (penalised). Dynamic programming, so two lines can never share a pause and the order is never swapped (the old nearest-pause rule did both on slow voices)."""
    n = len(est); C = []
    for i, e in enumerate(est):
        c = [(x, abs(x - e)) for x in ends if abs(x - e) <= reach]
        c.append((e, own + 0.01)); C.append(sorted(set(c)))
    INF = float("inf"); best = [[INF] * len(c) for c in C]; prev = [[-1] * len(c) for c in C]
    for j, (x, cost) in enumerate(C[0]):
        if x >= t_first - 1e-9: best[0][j] = cost
    for i in range(1, n):
        for j, (x, cost) in enumerate(C[i]):
            for k, (y, _) in enumerate(C[i - 1]):
                if best[i - 1][k] < INF and x >= y + gap and best[i - 1][k] + cost < best[i][j]: best[i][j] = best[i - 1][k] + cost; prev[i][j] = k
    j = min(range(len(C[-1])), key=lambda q: best[-1][q])
    if best[-1][j] == INF: return [max(t_first, e) for e in est]   # gap impossible (very short audio): keep the estimates
    S = [0.0] * n
    for i in range(n - 1, -1, -1): S[i] = C[i][j][0]; j = prev[i][j]
    return S
def norm(t):
    t = re.sub(r"[\u0610-\u061a\u064b-\u065f\u0640]", "", t.lower())
    t = t.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي", "ٱ": "ا"}))
    return re.sub(r"[^0-9a-z\u0621-\u064a]", "", t)
def load_asr(path):
    txt = open(path, encoding="utf-8").read()
    if txt.lstrip().startswith("["): return [(float(r["t0"]), float(r["t1"]), r["text"]) for r in json.loads(txt)]
    return [(float(a), float(b), t) for a, b, t in re.findall(r"^#\d+\s+([0-9.]+)-([0-9.]+):\s*(.*)$", txt, re.M)]
def by_asr(asr, lines, snap=0.6, gap=0.3):
    """Fuzzy match: script chars <-> ASR chars (difflib blocks), every ASR char has a time (interpolated inside its phrase); each line takes the time of its first char."""
    import difflib
    A = ""; T = []; starts = []
    for a, b, t in asr:
        n = norm(t)
        if not n: continue
        starts.append(a)
        for k in range(len(n)): T.append(a + (b - a) * k / len(n))
        A += n
    if not A: raise SystemExit("asr file has no text")
    Sx = ""; pos = []
    for t, _ in lines: pos.append(len(Sx)); Sx += norm(t)
    anchors = [(0, 0)]
    for m in difflib.SequenceMatcher(None, Sx, A, autojunk=False).get_matching_blocks():
        for k in range(m.size): anchors.append((m.a + k, m.b + k))
    anchors.append((len(Sx), len(A) - 1 if len(A) else 0))
    xs = [a for a, _ in anchors]; ys = [b for _, b in anchors]
    def at(p):
        j = max(0, min(len(ys) - 1, next((i for i, x in enumerate(xs) if x >= p), len(xs) - 1)))
        if j == 0 or xs[j] == p: q = ys[j]
        else: q = ys[j - 1] + (ys[j] - ys[j - 1]) * (p - xs[j - 1]) / max(1, xs[j] - xs[j - 1])
        return T[max(0, min(len(T) - 1, int(round(q))))]
    S = []
    for p in pos:
        t = at(p); near = min(starts, key=lambda s: abs(s - t))
        if abs(near - t) <= snap: t = near
        S.append(t)
    for i in range(1, len(S)):
        if S[i] < S[i - 1] + gap: S[i] = S[i - 1] + gap
    return S
def matched(asr, lines):
    import difflib
    A = "".join(norm(t) for _, _, t in asr); Sx = "".join(norm(t) for t, _ in lines)
    return sum(m.size for m in difflib.SequenceMatcher(None, Sx, A, autojunk=False).get_matching_blocks()) / max(1, len(Sx))   # share of the script text found in the recording
def by_whisper(wav, lines, dur):
    from faster_whisper import WhisperModel
    m = WhisperModel(os.environ.get("CTRLH_WHISPER_MODEL", "small"), compute_type="int8")
    segs, _ = m.transcribe(wav, language=os.environ.get("CTRLH_WHISPER_LANG", "ar"), word_timestamps=True)
    words = [(w.start, w.end, len(re.sub(r"\s", "", w.word))) for s in segs for w in s.words]
    if not words: raise SystemExit("whisper returned no words")
    tot = sum(x[2] for x in words); wl = weights(lines); wt = sum(wl); cum = 0; S = []; acc = []; c = 0
    for st, en, n in words: acc.append((c, st)); c += n
    for x in wl:
        f = cum / wt * tot; k = max(i for i, (cc, _) in enumerate(acc) if cc <= f); S.append(acc[k][1]); cum += x
    return S
if __name__ == "__main__":
    wav, script = sys.argv[1], sys.argv[2]; dur = duration(wav)
    lines = parse_script(script, "--skip-title" in sys.argv)
    method = "silence"
    if "--asr" in sys.argv:
        asr = load_asr(opt("--asr")); S = by_asr(asr, lines); method = "asr"
        r = matched(asr, lines); print("# text match %.0f%%" % (r * 100), file=sys.stderr)
        if r < 0.45: print("WARNING: the script and the recording look different (match %.0f%%) - check the text or the audio" % (r * 100), file=sys.stderr)
    elif "--whisper" in sys.argv:
        try: S = by_whisper(wav, lines, dur); method = "whisper"
        except ImportError: print("faster-whisper is not installed, using silence detection instead", file=sys.stderr); S = by_silence(wav, lines, dur)
        except Exception as e: print("whisper failed (%s: %s), using silence detection instead" % (type(e).__name__, str(e)[:160]), file=sys.stderr); S = by_silence(wav, lines, dur)   # e.g. model download blocked / offline
    else: S = by_silence(wav, lines, dur)
    T1 = S[1:] + [dur]
    doc = {"method": method, "duration": round(dur, 2), "lines": [{"i": i, "text": t, "t0": round(a, 2), "t1": round(b, 2), "section": sec} for i, ((t, sec), a, b) in enumerate(zip(lines, S, T1))]}
    out = opt("--out", "times.json"); json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("S = [%s]" % ", ".join("%.1f" % x for x in S)); print("# %d lines, method=%s, duration=%.2f -> %s" % (len(S), method, dur, out))
