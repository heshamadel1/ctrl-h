"""Chapters + description + hashtags from a scene file.
usage: python3 meta.py <scenes_module> [out.md]   (run from the folder of the scene file; module name without .py)
Chapters come from STAGES and the first scene of each stage (YouTube needs the first at 0:00, at least 3 chapters, each >= 10 s)."""
import sys, os, importlib
sys.path.insert(0, os.getcwd())
N = importlib.import_module(sys.argv[1])
def ts(t): t = int(t); return "%d:%02d" % (t // 60, t % 60)
first = {}
for s in N.SC: first.setdefault(s["stage"], s["t0"])
ch = [(0 if i == 0 else first.get(i, 0), name) for i, name in enumerate(N.STAGES)]
warn = []
if len(ch) < 3: warn.append("YouTube chapters need at least 3 entries")
for (a, _), (b, _) in zip(ch, ch[1:] + [(N.T_END, "")]):
    if b - a < 10: warn.append("a chapter is shorter than 10 s (%s), YouTube ignores the list" % ts(a))
heads = [s.get("head", "") for s in N.SC if s.get("head")]
tags = ["#" + x.replace(" ", "").replace(".", "") for x in getattr(N, "TECH", [])] + ["#CtrlH", "#Programming", "#BackEnd", "#SoftwareEngineering"]
out = ["## Chapters (YouTube description)"] + ["%s %s" % (ts(a), n) for a, n in ch]
out += ["", "## Description", "في الفيديو ده:"] + ["- " + h for h in heads[:6]] + ["", "Ctrl H. Think Deeper. Build Smarter.", "", " ".join(dict.fromkeys(tags))]
out += ["", "## Short caption (TikTok / Instagram / Facebook)", (heads[0] if heads else "") + " | " + " ".join(list(dict.fromkeys(tags))[:5])]
if warn: out += ["", "## Warnings"] + ["- " + w for w in warn]
txt = "\n".join(out); print(txt)
if len(sys.argv) > 2: open(sys.argv[2], "w", encoding="utf-8").write(txt)
