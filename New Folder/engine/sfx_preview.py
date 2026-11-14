"""Hear the sound effects without rendering a video.
usage: python3 sfx_preview.py <scenes_file.py> voice.wav [out.mp3] [--from 0 --to 60]
Builds the SFX track for the scene file (same rules as build.py) and mixes it under the voice at the final level (30%) into a small mp3."""
import sys, os, subprocess, tempfile
here = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:] if not x.startswith("--")]; opt = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
scenes, vo = a[0], a[1]; out = a[2] if len(a) > 2 else "sfx_preview.mp3"; t0 = float(opt("--from", 0)); t1 = opt("--to")
tmp = tempfile.mkdtemp(); sfx = os.path.join(tmp, "sfx.wav")
subprocess.check_call([sys.executable, os.path.join(here, "make_audio_lib.py"), scenes, sfx])
cut = ["-ss", "%.2f" % t0] + (["-to", t1] if t1 else [])
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-i", sfx, "-filter_complex", "[1:a]volume=0.30[s];[0:a][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]", "-map", "[a]"] + cut + ["-b:a", "128k", out])
print("preview ->", out)
