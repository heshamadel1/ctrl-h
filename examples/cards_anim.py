import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards_scenes as N
from anim import Video, run
V = Video(N.SC, N.STAGES, N.DUR, N.T_END, N.TAG1, N.TAG2, N.TECH)
run(V, sys.argv)
