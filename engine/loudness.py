"""Loudness and audio quality tools (Phase 7.2). Measurements use FFmpeg's ebur128 filter (ITU-R BS.1770 / EBU R128 integrated loudness, loudness range,
true peak); no extra dependency.  Nothing is normalised unless you ask for it: the default is to MEASURE and REPORT only.

  python3 engine/loudness.py measure FILE...                 integrated loudness (LUFS), loudness range (LU), true peak (dBTP), silence report
  python3 engine/loudness.py check FILE --preset youtube     pass/fail against a preset (target +- tolerance, true peak below the ceiling)
  python3 engine/loudness.py normalize IN OUT --preset reels  gain to the target, then a true-peak limiter; video is stream-copied
  python3 engine/loudness.py balance VOICE.wav SFX.wav       voice vs effects loudness difference
  python3 engine/loudness.py silence FILE [--noise -50] [--min 1.0]

Presets are REFERENCE values, not rules (platforms change them and do not publish exact processing). Choose by where the video is published and
confirm by listening on phone speakers and headphones:
  youtube  -14 LUFS, -1 dBTP   (YouTube lowers louder videos toward about -14; it rarely raises quiet ones)
  reels    -14 LUFS, -1 dBTP   (short-form social feeds: commonly aimed at about -14; platform values are not officially published)
  podcast  -16 LUFS, -1 dBTP   (speech-first, common in podcast delivery)
  broadcast -23 LUFS, -1 dBTP  (EBU R128 for television)
The build only touches loudness when CTRLH_LOUDNESS (config key "loudness") names a preset or is "<LUFS>,<dBTP>" (e.g. "-15,-1.5"); "off"/unset = unchanged."""
import os, re, sys, subprocess, shutil, tempfile

PRESETS = {"youtube": (-14.0, -1.0), "reels": (-14.0, -1.0), "podcast": (-16.0, -1.0), "broadcast": (-23.0, -1.0)}
TOLERANCE = 1.0   # LU, for check()

def parse_target(spec):
    """'youtube' / '-15,-1.5' / None|'off' -> (lufs, tp) or None"""
    if spec is None: return None
    s = str(spec).strip().lower()
    if s in ("", "off", "0", "none", "false"): return None
    if s in PRESETS: return PRESETS[s]
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", s)
    if m:
        lu, tp = float(m.group(1)), float(m.group(2))
        if not (-40 <= lu <= -5) or not (-6 <= tp <= 0): raise ValueError("loudness %r out of range (LUFS -40..-5, true peak -6..0)" % spec)
        return lu, tp
    raise ValueError("unknown loudness %r (use %s or '<LUFS>,<dBTP>')" % (spec, ", ".join(PRESETS)))

def _run(args):
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner"] + args, capture_output=True, text=True)
    return r.stderr

def parse_ebur128(text):
    """parse the summary block ffmpeg prints at the end"""
    tail = text[text.rfind("Summary:"):] if "Summary:" in text else text
    def g(pat):
        m = re.search(pat, tail); return float(m.group(1)) if m else None
    I = g(r"I:\s+(-?[\d.]+|-inf)\s+LUFS"); LRA = g(r"LRA:\s+([\d.]+)\s+LU"); TP = g(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS")
    if I is not None and I <= -69.99: I = None   # ffmpeg reports its -70 LUFS floor for silence
    if TP is not None and TP == float("-inf"): TP = None
    return {"I": I, "LRA": LRA, "TP": TP}

def measure(path):
    """{'I': LUFS, 'LRA': LU, 'TP': dBTP} of the audio of any file ffmpeg reads (None where silent)"""
    t = _run(["-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    if "Summary:" not in t: raise RuntimeError("could not measure %s: %s" % (path, t[-300:]))
    return parse_ebur128(t)

def silence(path, noise_db=-50.0, min_len=1.0):
    """[(start, end)] stretches quieter than noise_db for at least min_len seconds"""
    t = _run(["-i", path, "-vn", "-af", "silencedetect=noise=%gdB:d=%g" % (noise_db, min_len), "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", t)]; en = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", t)]
    out = []
    for i, s in enumerate(st): out.append((max(0.0, s), en[i] if i < len(en) else None))
    return out

def balance(voice, sfx):
    """(voice LUFS, effects LUFS, voice minus effects in LU). Effects are sparse, so this is a rough guide: keep the voice clearly above the effects (about 8 to 14 LU)"""
    a, b = measure(voice)["I"], measure(sfx)["I"]
    return a, b, (None if a is None or b is None else a - b)

def check(path, target):
    lu, tp = target; m = measure(path); notes = []
    if m["I"] is None: notes.append("silent")
    elif abs(m["I"] - lu) > TOLERANCE: notes.append("integrated %.1f LUFS is %+.1f LU from the %.0f target" % (m["I"], m["I"] - lu, lu))
    if m["TP"] is not None and m["TP"] > tp: notes.append("true peak %.1f dBTP is above the %.1f ceiling" % (m["TP"], tp))
    return (not notes), m, notes

def normalize(src, dst, target, max_iter=4, log=print):
    """linear gain to the integrated target, then a true-peak limiter at the ceiling, re-measured after encoding and corrected until the loudness is within 0.3 LU and the true peak is at or under the ceiling (or the limiter prevents it).
    Video is stream-copied, audio re-encoded AAC 192k (WAV stays PCM). Returns the final measurement."""
    lu, tp = target; m0 = measure(src); has_video = _has_video(src)
    if m0["I"] is None: raise RuntimeError("%s is silent, nothing to normalise" % src)
    gain = lu - m0["I"]; lim_db = tp; tmp = tempfile.mkdtemp(); best = None
    ext = os.path.splitext(dst)[1].lower()
    for it in range(max_iter):
        out = os.path.join(tmp, "o%d%s" % (it, ext or ".wav"))
        af = "volume=%.3fdB,alimiter=limit=%.4f:level=disabled:attack=3:release=50" % (gain, 10 ** (lim_db / 20.0))
        args = ["-y", "-i", src] + (["-map", "0:v", "-c:v", "copy"] if has_video else []) + ["-map", "0:a", "-af", af] + (["-c:a", "aac", "-b:a", "192k"] if ext in (".mp4", ".m4a", ".mov") else ["-c:a", "pcm_s16le"]) + [out]
        _run(args)
        m = measure(out); log("  pass %d: gain %+.2f dB -> %.2f LUFS, %.2f dBTP" % (it + 1, gain, m["I"], m["TP"]))
        best = (out, m)
        if abs(m["I"] - lu) <= 0.3 and m["TP"] <= tp: break
        if m["TP"] > tp: lim_db -= (m["TP"] - tp) + 0.1   # lossy encoding (AAC) overshoots the limiter: tighten the ceiling and go again
        if abs(m["I"] - lu) > 0.3: gain += lu - m["I"]
    shutil.copyfile(best[0], dst); shutil.rmtree(tmp, ignore_errors=True); return best[1]

def _has_video(path):
    t = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return "video" in t

def _fmt(m): return "I=%s LUFS  LRA=%s LU  TP=%s dBTP" % tuple("n/a" if v is None else "%.1f" % v for v in (m["I"], m["LRA"], m["TP"]))

def main(a):
    if len(a) < 2: print(__doc__); return 2
    cmd = a[0]; opts = {}; pos = []; i = 1
    while i < len(a):
        if a[i].startswith("--"): opts[a[i][2:]] = a[i + 1]; i += 2
        else: pos.append(a[i]); i += 1
    if cmd == "measure":
        for f in pos:
            print(f, "->", _fmt(measure(f)))
            sl = silence(f)
            if sl: print("   silence:", ", ".join("%.1f-%s s" % (s, "end" if e is None else "%.1f" % e) for s, e in sl))
        return 0
    if cmd == "check":
        tg = parse_target(opts.get("preset", "youtube")); ok, m, notes = check(pos[0], tg); print(pos[0], "->", _fmt(m)); print("PASS" if ok else "FAIL: " + "; ".join(notes)); return 0 if ok else 1
    if cmd == "normalize":
        tg = parse_target(opts.get("preset")); 
        if not tg: print("give --preset (%s) or '<LUFS>,<dBTP>'" % ", ".join(PRESETS)); return 2
        m = normalize(pos[0], pos[1], tg); print("->", pos[1], _fmt(m)); return 0
    if cmd == "balance":
        v, s, d = balance(pos[0], pos[1]); print("voice %.1f LUFS, effects %.1f LUFS, difference %s LU" % (v, s, "n/a" if d is None else "%.1f" % d)); return 0
    if cmd == "silence":
        for s, e in silence(pos[0], float(opts.get("noise", -50)), float(opts.get("min", 1.0))): print("%.2f - %s" % (s, "end" if e is None else "%.2f" % e))
        return 0
    print(__doc__); return 2

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
