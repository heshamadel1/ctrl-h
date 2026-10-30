# usage: SCENES=lk_scenes FMT=wide python3 clip.py <t0> <t1> out.mp4   (short test clip; run from examples/ or put it on PYTHONPATH)
import sys, os, subprocess, importlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.getcwd(), here]
N = importlib.import_module(os.environ.get("SCENES", "lk_scenes"))
from anim import Video, FPS, W, H
V = Video(N.SC, N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH)
a, b = float(sys.argv[1]), float(sys.argv[2])
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", sys.argv[3]], stdin=subprocess.PIPE)
for i in range(int(a * 30), int(b * 30)): p.stdin.write(V.frame(i).tobytes())
p.stdin.close(); p.wait()
