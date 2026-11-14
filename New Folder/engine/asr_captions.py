"""Cues for captions.py from the voice, in one step.
usage: python3 asr_captions.py voice.wav script.txt cues.txt [--max-chars 38] [--keywords "word1,word2"]
Times come from align.py (script lines placed in the voice by silence, or Whisper with --whisper); long lines are cut at word boundaries, time shared by length.
Highlights: every English word is highlighted by captions.py automatically; --keywords adds extra [[key words]]. Then:  python3 captions.py cues.txt video.mp4 video_cc.mp4"""
import sys, os, json, subprocess, re
here = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:] if not x.startswith("--")]; opt = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
wav, script, out = a[:3]; tmp = out + ".times.json"
subprocess.check_call([sys.executable, os.path.join(here, "align.py"), wav, script, "--out", tmp] + (["--whisper"] if "--whisper" in sys.argv else []), stdout=subprocess.DEVNULL)
sys.path.insert(0, here); import srt
d = json.load(open(tmp, encoding="utf-8")); mx = int(opt("--max-chars", 38)); kw = [k.strip() for k in (opt("--keywords") or "").split(",") if k.strip()]; rows = []
for ln in d["lines"]:
    t0, t1 = ln["t0"], ln["t1"] - 0.15
    if t1 <= t0: continue
    text = re.sub(r"[*#`>]|^[-•]\s*", "", ln["text"]).strip(); parts = srt.chunks(text, mx); tot = sum(len(p) for p in parts); cur = t0
    for p in parts:
        dt = (t1 - t0) * len(p) / tot
        for k in kw: p = p.replace(k, "[[%s]]" % k, 1) if k in p and "[[" not in p else p
        rows.append("%.2f\t%.2f\t%s" % (cur, cur + dt, p)); cur += dt
open(out, "w", encoding="utf-8").write("\n".join(rows)); os.remove(tmp); print("%d cues -> %s" % (len(rows), out))
