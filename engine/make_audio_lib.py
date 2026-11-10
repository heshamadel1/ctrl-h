"""SFX track from the Ctrl + H sound library (assets/sfx/*.mp3, see docs/SOUNDS.md).
usage: make_audio_lib.py <scenes.py|json> <out.wav>
Scene-file options (all optional):
  TYPING_SPEED = 1.0 (0.7 slower / 1.4 faster keystrokes).   SFX = [(12.5, "impact_01"), (30.0, "click"), (40.2, "typing", 2.0)]   pin a sound: file prefix or category, (t, name[, seconds])
  SFX_AUTO = False                                                       only the pins, no automatic sounds
  SFX_GAIN = 1.0                                                         overall level before the 30% mix
Automatic: scene cuts -> whoosh (chapter change -> transition), card/icards/recap items -> pop/click/tick (rotating, no repeat),
ok/✓ -> success, key/shock -> impact, errors -> error, code -> typing burst as long as the typing on screen."""
import os, sys, wave, random, glob, subprocess, importlib.util
import numpy as np
SR = 48000
here = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.join(here, "..", "assets", "sfx")
sys.path.insert(0, here); import scenefile
if sys.argv[1].endswith(".json"): RP = scenefile.load_json(sys.argv[1])
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
    _sp = importlib.util.spec_from_file_location("rp", sys.argv[1]); RP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RP)
rnd = random.Random(11)
_cache = {}
def files(cat): return sorted(glob.glob(os.path.join(LIB, cat + "_*.mp3")))
def load(path, dur=None, fade=0.12):
    k = (path, dur)
    if k in _cache: return _cache[k]
    x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]), np.float32).copy()
    if dur: x = x[:int(dur * SR)]
    n = min(len(x) // 2, int(fade * SR)); x[-n:] *= np.linspace(1, 0, n) if n else 1
    _cache[k] = x / max(1e-6, np.max(np.abs(x))) * 0.9; return _cache[k]
TYPING_RMS = 0.07
LEVEL = dict(whoosh=.6, transition=.65, impact=.85, riser=.6, glitch=.7, typing=.85, click=.5, success=.6, pop=.55, error=.65, paper=.55, pen=.55)
MAXLEN = dict(whoosh=1.6, transition=2.6, impact=3.0, riser=3.0, typing=8.0, glitch=1.5, pop=1.2, success=1.8, error=1.8, click=0.8, paper=1.5, pen=2.0)
T = RP.DUR; N = int((T + 4) * SR); out = np.zeros(N, np.float32)
last = {}
def pick(cat):
    fs = files(cat) or []
    if not fs: return None
    c = [f for f in fs if f != last.get(cat)] or fs; f = rnd.choice(c); last[cat] = f; return f
def resolve(name):
    p = os.path.join(LIB, name if name.endswith(".mp3") else name)
    if os.path.isfile(p): return p, name.split("_")[0]
    m = sorted(glob.glob(os.path.join(LIB, name + "*.mp3")))
    if m: return m[0], os.path.basename(m[0]).split("_")[0]
    return pick(name), name
def add(path, cat, t, g=1.0, dur=None):
    if not path or t < 0 or t >= T: return
    x = load(path, dur or MAXLEN.get(cat)) * LEVEL.get(cat, .55) * g; i = int(t * SR); j = min(N, i + len(x)); out[i:j] += x[:j - i]
def burst(t, d, g=1.0):
    p = pick("typing")
    if not p: return
    rate = float(getattr(RP, "TYPING_SPEED", 1.0))   # >1 = faster keystrokes than the library sound, <1 = slower (the burst keeps the on-screen duration)
    TY = load(p, 8.0, 0.0); d = min(d, 7.0); need = d * rate; hi = max(0.25, 8.0 - need - 0.2)
    cands = [rnd.uniform(0.2, hi) for _ in range(12)]; seg = lambda st_: TY[int(st_ * SR):int((st_ + need) * SR)]
    st = max(cands, key=lambda st_: float(np.sqrt(np.mean(seg(st_) ** 2))) if len(seg(st_)) else 0.0)     # the liveliest stretch, not a pause in the recording
    x = seg(st).copy(); rms_ = float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
    if rms_ > 1e-4: x = np.clip(x * (TYPING_RMS / rms_), -1, 1)                                         # keystrokes as loud as the other sounds (the library clip is much quieter)
    if rate != 1.0 and len(x) > 1: x = np.interp(np.linspace(0, len(x) - 1, int(d * SR)), np.arange(len(x)), x).astype(np.float32)
    n = min(len(x) // 3, int(0.05 * SR))
    if n: x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    i = int(t * SR); j = min(N, i + len(x)); out[i:j] += x[:j - i] * LEVEL["typing"] * g
def flat(bl):
    for b in bl:
        if b.get("k") in ("row", "tiles") and "items" in b: yield from flat(b["items"])
        else: yield b
pins = getattr(RP, "SFX", []); gain = getattr(RP, "SFX_GAIN", 1.0)
if getattr(RP, "SFX_AUTO", True):
    prev_stage = None; sc = RP.SC
    for k, s in enumerate(sc):
        big = s.get("stage") != prev_stage and k > 0; prev_stage = s.get("stage")
        if k > 0: add(pick("transition" if big else "whoosh"), "transition" if big else "whoosh", s["t0"] - 0.1)
        pops = ["pop", "click", "pop", "click"]; j = 0
        for b in flat(s["blocks"]):
            kd = b.get("k"); t0 = b.get("t", b.get("t0", s["t0"]))
            if kd in ("card", "recap", "icards", "steplist", "fixcards", "versus", "chain", "matrix"):
                ts = [b["t"]] if kd == "card" and "t" in b else []
                for key in ("items", "cols", "steps", "rows"):
                    for it in (b.get(key) if isinstance(b.get(key), (list, tuple)) else []):
                        ti = it.get("t") if isinstance(it, dict) else (it[0] if isinstance(it, (tuple, list)) and it and isinstance(it[0], (int, float)) else None)
                        if ti is not None: ts.append(ti)
                for ti in ts or [t0]:
                    c = pops[j % 4]; add(pick(c), c, ti, .8); j += 1
                if b.get("ok") is True: add(pick("success"), "success", t0 + .2, .8)
                if b.get("ok") is False: add(pick("error"), "error", t0 + .05, .7)
                if b.get("key"): add(pick("impact"), "impact", t0 - .02, .6)
            elif kd == "shock": add(pick("impact"), "impact", t0 - .05); add(pick("glitch"), "glitch", t0, .5)
            elif kd == "mystery": add(pick("riser"), "riser", max(s["t0"], t0 - 0.2), .7)
            elif kd == "strike": add(pick("pen"), "pen", t0, .8)
            elif kd == "counter": add(pick("click"), "click", b.get("t0", t0), .8)
            elif kd in ("code", "codeann"):
                for ln in b.get("lines", []):
                    if isinstance(ln, (tuple, list)) and len(ln) >= 2 and isinstance(ln[0], (int, float)): burst(ln[0], len(str(ln[1])) / max(1.0, float(ln[2]) if len(ln) >= 3 else 26.0))
            elif kd == "chatwin":
                for ln in b.get("lines", []):
                    if isinstance(ln, (tuple, list)) and isinstance(ln[0], (int, float)): burst(ln[0], .9, .9); add(pick("success"), "success", ln[0] + 1.0, .6)
for pin in pins:
    t, name = pin[0], pin[1]; d = pin[2] if len(pin) > 2 else None; p, cat = resolve(name)
    if cat == "typing" and d: burst(t, d)
    else: add(p, cat, t, 1.0, d)
out *= gain; pk = np.max(np.abs(out)); out = out / pk * 0.9 if pk > 0 else out
w = wave.open(sys.argv[2], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out[:int(T * SR)] * 32767).astype(np.int16).tobytes()); w.close(); print("sfx ->", sys.argv[2])
