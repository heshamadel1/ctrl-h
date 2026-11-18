"""One command from voiceover + script to a DRAFT scene file (and optionally the finished video).
usage (run from your project folder):
  python3 make_video.py voice.wav script.txt [--name NAME] [--model DIR] [--formats wide,reel] [--theme paper_orange] [--max-scene 22] [--skip-title] [--build] [--out DIR]
Steps: 1 timing of every script line  (with --model DIR or CTRLH_ASR_MODEL: offline speech recognition + text matching = align.py --asr;
          without a model: silence + line length = align.py default)
       2 draft scene file NAME_scenes.py  (suggest.py: title -> shock, question -> mystery, other lines -> cards, tools -> chips)
       3 lint of the draft
       4 only with --build: python3 build.py NAME_scenes --vo voice.wav ... (render, SFX, mix, loudness)
The draft is a STARTING POINT: open NAME_scenes.py, replace weak cards with the block that fits (docs/FEATURES.md), then build. Without --build nothing is rendered.
Script format: see align.py (one sentence per line, [section] headers). Writes NAME_times.json, NAME_scenes.py (never overwrites an existing scene file unless --force)."""
import sys, os, re, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.stdout.strip(): print(r.stdout.rstrip())
    if r.stderr.strip(): print(r.stderr.rstrip(), file=sys.stderr)
    if r.returncode: raise SystemExit("step failed: %s (exit %d)" % (" ".join(os.path.basename(c) for c in cmd[:3]), r.returncode))
    return r
def main():
    pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--name", "--model", "--formats", "--theme", "--max-scene", "--out")]
    if len(pos) < 2: raise SystemExit(__doc__)
    wav, script = pos[0], pos[1]
    for f in (wav, script):
        if not os.path.isfile(f): raise SystemExit("file not found: " + f)
    name = opt("--name") or re.sub(r"[^A-Za-z0-9_]+", "_", os.path.splitext(os.path.basename(script))[0]).strip("_").lower() or "video"
    scenes = name + "_scenes.py"; times = name + "_times.json"
    if os.path.exists(scenes) and "--force" not in sys.argv: raise SystemExit("%s already exists (use --force to replace it, or --name for another file)" % scenes)
    skip = ["--skip-title"] if "--skip-title" in sys.argv else []
    model = opt("--model") or os.environ.get("CTRLH_ASR_MODEL", "")
    method = "silence"
    if model and os.path.isdir(model):
        print("1/3 speech recognition + text matching (%s) ..." % model); asr = name + "_asr.json"
        try:
            run([PY, os.path.join(HERE, "asr_phrases.py"), wav, "--model", model, "--out", asr]); run([PY, os.path.join(HERE, "align.py"), wav, script, "--asr", asr, "--out", times] + skip); method = "asr"
        except SystemExit as e:
            print("recognition failed (%s), using silence timing instead" % e, file=sys.stderr)
    elif model: print("model folder not found (%s), using silence timing instead" % model, file=sys.stderr)
    if method == "silence": print("1/3 timing from silence + line length (add --model DIR for text matching) ..."); run([PY, os.path.join(HERE, "align.py"), wav, script, "--out", times] + skip)
    print("2/3 draft scene file ..."); run([PY, os.path.join(HERE, "suggest.py"), script, times, "--out", scenes, "--max-scene", opt("--max-scene", "22")])
    if opt("--theme"): open(scenes, "a", encoding="utf-8").write("\n# theme for this video: run with CTRLH_THEME=%s (or build with --theme)\n" % opt("--theme"))
    print("3/3 lint ...")
    r = subprocess.run([PY, os.path.join(HERE, "lint.py"), scenes[:-3]], capture_output=True, text=True); print((r.stdout + r.stderr).strip()[-1500:])
    print("\nDraft ready: %s  (timing method: %s). Review it, replace weak cards, then:\n  python3 %s %s --vo %s --formats %s" % (scenes, method, os.path.join(HERE, "build.py"), scenes[:-3], wav, opt("--formats", "wide,reel")))
    if "--build" in sys.argv:
        env = dict(os.environ); env.update({"CTRLH_THEME": opt("--theme")} if opt("--theme") else {})
        cmd = [PY, os.path.join(HERE, "build.py"), scenes[:-3], "--vo", wav, "--formats", opt("--formats", "wide,reel")] + (["--out", opt("--out")] if opt("--out") else [])
        print("\nbuilding ..."); subprocess.run(cmd, env=env, check=True)
if __name__ == "__main__": main()
