"""Timing of every script line inside the voiceover.
usage: python3 align.py voice.wav script.txt [--out times.json] [--whisper] [--skip-title]
Default method (no extra install): silence detection + the characters of each line (a line starts at the pause nearest to its share of the speech).
--whisper (optional, needs `pip install faster-whisper` and a downloaded model, NOT tested in the kit's cloud workspace): uses word timestamps instead.
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
    S = []
    for e in est:
        n = min(ends, key=lambda x: abs(x - e)) if ends else e; S.append(n if abs(n - e) < 1.3 else e)
    S[0] = max(S[0], t_first); return S
def by_whisper(wav, lines, dur):
    from faster_whisper import WhisperModel
    m = WhisperModel(os.environ.get("CTRLH_WHISPER_MODEL", "small"), compute_type="int8")
    segs, _ = m.transcribe(wav, language="ar", word_timestamps=True)
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
    if "--whisper" in sys.argv:
        try: S = by_whisper(wav, lines, dur); method = "whisper"
        except ImportError: print("faster-whisper is not installed, using silence detection instead", file=sys.stderr); S = by_silence(wav, lines, dur)
    else: S = by_silence(wav, lines, dur)
    T1 = S[1:] + [dur]
    doc = {"method": method, "duration": round(dur, 2), "lines": [{"i": i, "text": t, "t0": round(a, 2), "t1": round(b, 2), "section": sec} for i, ((t, sec), a, b) in enumerate(zip(lines, S, T1))]}
    out = opt("--out", "times.json"); json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("S = [%s]" % ", ".join("%.1f" % x for x in S)); print("# %d lines, method=%s, duration=%.2f -> %s" % (len(S), method, dur, out))
