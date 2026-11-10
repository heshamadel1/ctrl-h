"""Smoke test of the whole kit, no video is rendered.   usage: python3 smoke.py [--quick]
1 compile every .py  2 lint every example  3 one frame per theme x format (--quick: 1 theme)  4 SFX track from the library for an example
5 sound manifest vs files  6 docs links  7 config example loads  8 setup writes every background.   Exit code 1 if anything fails (use it in CI)."""
import sys, os, re, glob, json, subprocess, tempfile, py_compile
K = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); E = os.path.join(K, "engine"); X = os.path.join(K, "examples"); PY = sys.executable
bad = []; tmp = tempfile.mkdtemp()
def ok(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + extra if extra and not cond else "")); cond or bad.append(name)
def run(cmd, env=None, cwd=X):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=dict(os.environ, **(env or {}))); return r.returncode, (r.stdout + r.stderr)
fails = []
for f in glob.glob(E + "/*.py") + glob.glob(X + "/*.py"):
    try: py_compile.compile(f, doraise=True, cfile=os.path.join(tmp, "x.pyc"))
    except Exception as e: fails.append(os.path.basename(f))
ok("compile all .py", not fails, str(fails))
scenes = sorted(os.path.basename(f)[:-3] for f in glob.glob(X + "/*_scenes.py"))
for sname in scenes:
    rc, o = run([PY, E + "/lint.py", sname]); ok("lint " + sname, rc == 0 and "Traceback" not in o, o[-200:])
themes = ["orange", "paper_orange", "soft_cream"] if "--quick" not in sys.argv else ["soft_cream"]
for th in themes:
    for fm in ("wide", "reel"):
        d = os.path.join(tmp, th + fm); rc, o = run([PY, E + "/render.py", "template_howto_scenes", "frames", d, "20"], {"CTRLH_THEME": th, "FMT": fm}); ok("frame %s %s" % (th, fm), rc == 0 and os.path.isfile(d + "/x_0600.png"), o[-200:])
rc, o = run([PY, E + "/make_audio_lib.py", "template_howto_scenes.py", os.path.join(tmp, "s.wav")]); ok("sfx track", rc == 0 and os.path.getsize(os.path.join(tmp, "s.wav")) > 1e5, o[-200:])
m = json.load(open(K + "/assets/sfx/manifest.json")); fs = {f for f in os.listdir(K + "/assets/sfx") if f.endswith(".mp3")}; ok("sound manifest = files (%d)" % len(fs), set(m) == fs, str(set(m) ^ fs))
broken = []
for f in glob.glob(K + "/*.md") + glob.glob(K + "/docs/*.md") + glob.glob(K + "/skills/*/*.md"):
    for mm in re.finditer(r"\]\(([^)#\s]+)(#[^)]*)?\)", open(f, encoding="utf-8").read()):
        t = mm.group(1)
        if not t.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), t))): broken.append((os.path.basename(f), t))
ok("docs links", not broken, str(broken[:5]))
cfg = K + "/profiles/ctrlh.config.example.json"; ok("config example is valid JSON", os.path.isfile(cfg) and bool(json.load(open(cfg, encoding="utf-8"))))
import importlib; sys.path.insert(0, E); import bg_styles
for bg in ["hud_live", "paper", "cream", "tech:laravel"]:
    rc, o = run([PY, E + "/ctrlh_setup.py", "--yes", "--channel", "T", "--theme", "paper_orange", "--bg-style", bg, "--out", os.path.join(tmp, "c.json")]); c = json.load(open(os.path.join(tmp, "c.json"))) if rc == 0 else {}
    ok("setup bg " + bg, c.get("bg_style") == bg, o[-150:])
print("\n%s: %d check(s) failed" % ("SMOKE FAILED" if bad else "SMOKE OK", len(bad))); sys.exit(1 if bad else 0)
