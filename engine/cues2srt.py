#!/usr/bin/env python3
"""Subtitle FILE (no burned-in captions): tab-separated cues (start<TAB>end<TAB>text) -> .srt. Usage: cues2srt.py cues.txt out.srt"""
import sys
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, 1): f.write("%d\n%s --> %s\n%s\n\n" % (i, ts(float(r[0])), ts(float(r[1])), r[2].replace(" ", " ")))
print(len(rows), "cues ->", sys.argv[2])
