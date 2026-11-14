"""Short clips (9:16 or 16:9) from a long video's scene file: 30-60 s pieces cut at scene boundaries, each with a title.
usage: python3 reels.py <scenes_module> --vo voice.wav [--out DIR] [--min 30] [--max 60] [--format reel] [--list-only]
Plans clips at scene boundaries (a clip never cuts a scene), prints the plan with a suggested title (the scene headline) and, without --list-only,
renders each clip with the same scene file (FMT=reel by default), voice + SFX cut to the clip. Frame times stay global, so nothing is re-timed."""
import sys, os, subprocess
here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.getcwd(), here]
import ctrlh_config, scenefile
a = [x for x in sys.argv[1:] if not x.startswith("--")]; opt = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
mod = a[0]; N = scenefile.load(mod); base = scenefile.base_name(mod); lo, hi = float(opt("--min", 30)), float(opt("--max", 60)); fmt = opt("--format", "reel")
SC = [s for s in N.SC if s["t1"] > s["t0"]]; clips = []; cur0 = SC[0]["t0"]; first = SC[0]
for i, s in enumerate(SC):
    nxt = SC[i + 1] if i + 1 < len(SC) else None
    if s["t1"] - cur0 >= lo or nxt is None or (nxt["t1"] - cur0) > hi:
        if s["t1"] - cur0 >= lo or nxt is None:
            clips.append((cur0, s["t1"], first)); 
            if nxt: cur0, first = nxt["t0"], nxt
if len(clips) > 1 and clips[-1][1] - clips[-1][0] < lo * .5: a0, _, f0 = clips[-2]; clips[-2:] = [(a0, clips[-1][1], f0)]
def title(s):
    h = s.get("head") or ""; return h if isinstance(h, str) else str(h)
print("CLIPS (%d), format %s:" % (len(clips), fmt))
for k, (x, y, s) in enumerate(clips, 1): print("  %d. %.1f-%.1f s (%.0f s)  %s" % (k, x, y, y - x, title(s)))
if "--list-only" in sys.argv: sys.exit(0)
vo = opt("--vo"); assert vo and os.path.isfile(vo), "--vo voice.wav is required"
out = os.path.abspath(opt("--out", ".")); os.makedirs(out, exist_ok=True); sfx = os.path.join(out, base + "_sfx.wav"); py = sys.executable
subprocess.check_call([py, os.path.join(here, "make_audio_lib.py"), os.path.abspath(N.__file__), sfx])
mixf = os.path.join(out, ".mix.txt"); open(mixf, "w").write(open(os.path.join(here, "mix2.txt")).read())
for k, (x, y, s) in enumerate(clips, 1):
    tag = "%s_clip%02d_%s" % (base, k, fmt); vid = os.path.join(out, tag + "_v.mp4")
    env = dict(os.environ, FMT=fmt, CTRLH_T0="%.3f" % x, CTRLH_T1="%.3f" % y, CTRLH_CACHE=os.environ.get("CTRLH_CACHE", os.path.join(out, ".ctrlh_cache")))
    subprocess.check_call([py, os.path.join(here, "render.py"), mod, vid], env=env); vp, sp = os.path.join(out, tag + "_vo.wav"), os.path.join(out, tag + "_sfx.wav")
    for src, dst in ((vo, vp), (sfx, sp)): subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", "atrim=start=%.3f:end=%.3f,asetpts=PTS-STARTPTS" % (x, y), "-c:a", "pcm_s16le", dst])
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", vp, "-i", sp, "-filter_complex_script", mixf, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % (y - x), os.path.join(out, tag + ".mp4")])
    print("DONE", tag + ".mp4", flush=True)
