"""Compare a voiceover WAV with a scene file before rendering.
usage: python3 check_voice.py <scenes_module> voice.wav        (also run by build.py; `build.py ... --check-voice` makes problems stop the build)
Checks: WAV length vs DUR, T_END (end card) and TAG1/TAG2 (sign-off) inside the voice, scenes inside DUR, gaps/overlaps between scenes,
and (when found) the loudness of the last seconds so the end card does not start in the middle of a sentence."""
import sys, os, re, subprocess
sys.path[:0] = [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
def wav_len(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode().strip())
def speech_end(p, dur):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=noise=-38dB:d=0.4", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]
    return st[-1] if st and st[-1] > dur - 6 else dur
def check(vo, N, strict=False):
    L = wav_len(vo); end = speech_end(vo, L); issues = []; out = lambda m: (issues.append(m), print("CHECK:", m))
    DUR = getattr(N, "DUR", None); T_END = getattr(N, "T_END", None); SC = getattr(N, "SC", [])
    print("CHECK: voice %.2f s (speech ends ~%.2f s), scene file DUR=%s T_END=%s" % (L, end, DUR, T_END))
    if DUR is not None and abs(DUR - L) > 0.6: out("DUR %.2f differs from the WAV (%.2f s): set DUR to the WAV length" % (DUR, L))
    if T_END is not None and T_END < end - 0.8: out("T_END %.2f is before the speech ends (%.2f s): the end card would cut the voice" % (T_END, end))
    if T_END is not None and T_END > L + 0.3: out("T_END %.2f is after the WAV ends (%.2f s)" % (T_END, L))
    for nm in ("TAG1", "TAG2"):
        v = getattr(N, nm, None)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and not (0 < v < L): out("%s = %s is outside the voice (0-%.1f s)" % (nm, v, L))
    prev = None
    for i, s in enumerate(SC):
        if s["t1"] > L + 0.3: out("scene %d ends at %.1f s, after the WAV (%.1f s)" % (i, s["t1"], L))
        if prev is not None:
            if s["t0"] - prev > 0.5: out("gap of %.1f s before scene %d (t0=%.1f)" % (s["t0"] - prev, i, s["t0"]))
            if prev - s["t0"] > 0.5: out("scene %d starts %.1f s before the previous one ends" % (i, prev - s["t0"]))
        prev = s["t1"]
    if SC and abs(SC[-1]["t1"] - (T_END or SC[-1]["t1"])) > 3: out("last scene ends at %.1f s but T_END is %.1f s" % (SC[-1]["t1"], T_END))
    if not issues: print("CHECK: ok")
    return issues
if __name__ == "__main__":
    import scenefile; sys.exit(1 if check(sys.argv[2], scenefile.load(sys.argv[1])) else 0)
