"""Generic renderer: python3 render.py <scenes_module> <out.mp4> | frames <dir> t1 t2 ...   (run from the scene file's folder)
Env: FMT=wide|reel, CTRLH_T0/CTRLH_T1 = clip window in seconds, CTRLH_WORKERS, CTRLH_CACHE (dir, or 0 = no cache)."""
import sys, os, importlib
here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.getcwd(), here]
import ctrlh_config
from anim import Video, run
import scenefile; N = scenefile.load(sys.argv[1])
V = Video(N.SC, N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH, getattr(N, "SUB_T", None), getattr(N, "FOL_T", None))
run(V, [sys.argv[0]] + (sys.argv[2:] if sys.argv[2] == "frames" else ["video", sys.argv[2]]))
