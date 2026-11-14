"""One command from scene file + voiceover to finished videos.
usage (run from the scene file's folder):
  python3 build.py <scenes_module> --vo voice.wav [--out DIR] [--formats wide,reel] [--max-part 180] [--strict] [--plan-only] [--check-voice]
Steps: lint (--strict stops on any LINT line) -> contact sheet -> split plan -> per part and format: render (scene cache) -> SFX -> voice cut -> mux -> meta.md.
Formats default to config `formats` (["wide"]); 9:16 only when you list "reel". Long videos are split at the scene boundary nearest to equal parts
(config `max_part_seconds`, default 180). Frame times stay global, so one scene file serves every part."""
import sys, os, json, math, subprocess, importlib
here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.getcwd(), here]
import ctrlh_config
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
import scenefile; mod = sys.argv[1]; N = scenefile.load(mod); base = scenefile.base_name(mod)
out = os.path.abspath(opt("--out", ".")); os.makedirs(out, exist_ok=True)
types = json.load(open(os.path.join(here, "..", "profiles", "video-types.json"), encoding="utf-8")); T = types.get(os.environ.get("CTRLH_VIDEO_TYPE", "explainer"), {})
formats = (opt("--formats") or os.environ.get("CTRLH_FORMATS") or ",".join(T.get("formats", ["wide"]))).split(",")
formats = [f.strip() for f in formats if f.strip()]
maxp = float(opt("--max-part") or os.environ.get("CTRLH_MAX_PART") or T.get("max_part_seconds", 180))
def sh(cmd, **kw): return subprocess.run(cmd, check=True, **kw)
import loudness as _ld0
try: _ld0.parse_target(os.environ.get("CTRLH_LOUDNESS"))   # a typo in the loudness setting stops here, before the long render
except ValueError as _e: sys.exit("CTRLH_LOUDNESS: %s" % _e)
py = sys.executable
lint = subprocess.run([py, os.path.join(here, "lint.py"), mod, "--sheet", os.path.join(out, base + "_sheet.png")] + (["--strict"] if "--strict" in sys.argv else []))
if lint.returncode: sys.exit("build stopped: fix the LINT lines above (or run without --strict)")
SC = N.SC; DUR = N.DUR
n = max(1, math.ceil(DUR / maxp)); cuts = [0.0]
for k in range(1, n):
    tgt = k * DUR / n; cand = [s["t0"] for s in SC if s["t0"] > cuts[-1] + 20 and s["t0"] < DUR - 20]
    stage_first = {s["stage"]: s["t0"] for s in reversed(SC)}; st = [t for t in stage_first.values() if t in cand]
    pool = st or cand; cuts.append(min(pool, key=lambda t: abs(t - tgt)) if pool else tgt)
cuts.append(DUR); parts = list(zip(cuts, cuts[1:]))
print("PLAN: %d part(s): %s | formats: %s" % (len(parts), ", ".join("%.1f-%.1f" % p for p in parts), ",".join(formats)))
if "--plan-only" in sys.argv: sys.exit(0)
vo = opt("--vo"); assert vo and os.path.isfile(vo), "--vo voice.wav is required"
if "--check-voice" in sys.argv or os.environ.get("CTRLH_CHECK_VOICE", "1") != "0":   # compare the WAV with the scene file BEFORE rendering
    import check_voice
    bad = check_voice.check(vo, N, strict="--check-voice" in sys.argv)
    if bad and "--check-voice" in sys.argv: sys.exit("build stopped: fix DUR / T_END / TAG times (see CHECK lines above), or drop --check-voice")
if "--check-voice-only" in sys.argv: sys.exit(0)
scene_file = os.path.abspath(N.__file__); sfx = os.path.join(out, base + "_sfx.wav")
sh([py, os.path.join(here, "make_audio.py" if os.environ.get("CTRLH_SFX", "lib").lower() == "synth" else "make_audio_lib.py"), scene_file, sfx])
mix = open(os.path.join(here, "mix2.txt")).read(); mixf = os.path.join(out, ".mix.txt"); open(mixf, "w").write(mix)
for fmt in formats:
    for pi, (a, b) in enumerate(parts, 1):
        tag = "%s_%s%s" % (base, "part%d_" % pi if len(parts) > 1 else "", fmt); vid = os.path.join(out, tag + "_v.mp4")
        env = dict(os.environ, FMT=fmt, CTRLH_T0="%.3f" % a, CTRLH_T1="%.3f" % b, CTRLH_CACHE=os.environ.get("CTRLH_CACHE", os.path.join(out, ".ctrlh_cache")))
        # per-scene theme (scene key "theme"): render each run of same-theme scenes separately, then join (owner 2026-11-10: use the 3 themes in one video)
        base_theme = os.environ.get("CTRLH_THEME", ""); runs = []
        for sc_ in N.SC:
            th = sc_.get("theme", base_theme)
            if runs and runs[-1][2] == th: runs[-1][1] = sc_["t1"]
            else: runs.append([sc_["t0"], sc_["t1"], th])
        runs[0][0] = min(runs[0][0], a); runs[-1][1] = max(runs[-1][1], b)
        runs = [[max(x, a), min(y, b), th] for x, y, th in runs if min(y, b) > max(x, a)]
        if len(runs) <= 1:
            sh([py, os.path.join(here, "render.py"), mod, vid], env=dict(env, **({"CTRLH_THEME": runs[0][2]} if runs and runs[0][2] else {})))
        else:
            segs_ = []
            for ri, (ra, rb, th) in enumerate(runs):
                sv = os.path.join(out, "%s_run%d.mp4" % (tag, ri)); e2 = dict(env, CTRLH_T0="%.3f" % ra, CTRLH_T1="%.3f" % rb)
                if th: e2["CTRLH_THEME"] = th
                sh([py, os.path.join(here, "render.py"), mod, sv], env=e2); segs_.append(sv)
            lst = os.path.join(out, tag + "_runs.txt"); open(lst, "w").write("".join("file '%s'\n" % x for x in segs_))
            sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
        vo_p, sx_p = os.path.join(out, tag + "_vo.wav"), os.path.join(out, tag + "_sfx.wav")
        for src, dst in ((vo, vo_p), (sfx, sx_p)):   # atrim (a stream copy with -ss cuts an empty file on some wavs)
            sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", "atrim=start=%.3f:end=%.3f,asetpts=PTS-STARTPTS" % (a, b), "-c:a", "pcm_s16le", dst])
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", vo_p, "-i", sx_p, "-filter_complex_script", mixf, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % (b - a), os.path.join(out, tag + ".mp4")])
        try:   # loudness: measure and report always; change the audio only when CTRLH_LOUDNESS names a preset / "<LUFS>,<dBTP>" (see docs/AUDIO.md)
            import loudness as _ld
            _fin = os.path.join(out, tag + ".mp4"); _tg = _ld.parse_target(os.environ.get("CTRLH_LOUDNESS"))
            if _tg:
                _tmp = _fin + ".norm.mp4"; _m = _ld.normalize(_fin, _tmp, _tg, log=lambda *_: None); os.replace(_tmp, _fin)
            else: _m = _ld.measure(_fin)
            print("LOUDNESS %s: %s%s" % (tag, _ld._fmt(_m), " (normalised to %.0f LUFS / %.1f dBTP)" % _tg if _tg else " (not normalised; CTRLH_LOUDNESS to change)"), flush=True)
        except ValueError: raise
        except Exception as _e: print("LOUDNESS: skipped (%s)" % str(_e)[:120], flush=True)
        print("DONE", tag + ".mp4", "%.1f s" % (b - a), flush=True)
sh([py, os.path.join(here, "meta.py"), mod, os.path.join(out, base + "_meta.md")], stdout=subprocess.DEVNULL)
print("meta:", os.path.join(out, base + "_meta.md"))
