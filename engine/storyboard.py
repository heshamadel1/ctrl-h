"""Storyboard (Phase 10): ONE structured document for the whole production, separate from rendering.

  python3 engine/storyboard.py template                    print a minimal storyboard to start from
  python3 engine/storyboard.py validate story.json         readable errors (with the JSON path) and warnings; exit 1 on errors
  python3 engine/storyboard.py summary  story.json         one line per scene: time, duration, what is on screen, what is said
  python3 engine/storyboard.py compile  story.json out.json  the flat scene file the engine renders (build.py / render.py / lint.py also accept story.json directly)
  python3 engine/storyboard.py import   my_scenes.py story.json   convert an existing Python/JSON scene file into a storyboard (old files keep working untouched)

Who does what: content preparation (a person, or Claude in a chat, or an agent) writes the storyboard; the Python engine renders it. Nothing here needs an agent, a terminal is only
needed to render. A storyboard compiles to exactly the scene data the engine already uses, so every existing block, theme, transition, camera, entity and sound feature works unchanged.

Document (JSON):
{ "storyboard": 1,
  "meta":      {"title": "...", "language": "ar", "notes": "free text"},
  "output":    {"formats": ["wide", "reel"], "theme": "paper_orange", "loudness": "reels"},      # theme -> CTRLH_THEME, loudness -> CTRLH_LOUDNESS (a setting you already made in the environment/config wins)
  "voiceover": {"file": "voice.wav", "script": "script.txt"},                              # informational for the tools; the render takes the wav via build.py --vo
  "timing":    {"duration": 58.0, "end": 54.5, "tag1": 54.7, "tag2": 56.0, "subscribe_at": 30, "follow_at": 52},   # all optional: end = end of the last scene, duration = tag2 + 1.5 ...
  "stages":    ["chapter 1", "chapter 2"], "tech": ["Laravel", "Redis"],
  "transition": "classic",                                                                # default for every scene (see docs/TRANSITIONS.md)
  "audio":     {"auto": true, "events": {"item": false}, "pins": [[12.5, "impact_01"]]},  # docs/AUDIO.md
  "scenes": [ {"id": "intro", "start": 0, "end": 6.0,   (or "dur": 6.0: starts where the previous one ended)
               "stage": 0, "style": "plain_dark", "head": "Title", "head_t": 0.05,
               "say": "the sentence(s) spoken in this scene (checked against the script by tools, not rendered)",
               "blocks": [ ... ], "transition": "slide", "camera": [...], "entities": [...], "sfx": {...} } ] }
Times are seconds on the global timeline, exactly as in the scene files."""
import os, sys, json, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

SCENE_KEYS = {"id", "start", "end", "dur", "say", "notes", "stage", "style", "head", "head_t", "blocks", "transition", "trans_in", "trans_out", "camera", "entities", "sfx", "dims", "reserve", "reserve_reel", "grid", "cw", "t0", "t1"}
TOP_KEYS = {"storyboard", "meta", "output", "voiceover", "timing", "stages", "tech", "transition", "audio", "scenes", "legacy"}
ENGINE_ONLY = {"id", "start", "end", "dur", "say", "notes"}          # storyboard-only scene fields, not passed to the engine
FORMATS = ("wide", "reel")

def _is_num(x): return isinstance(x, (int, float)) and not isinstance(x, bool)

def _kinds():
    os.environ.setdefault("FMT", "wide"); import anim
    return set(anim.DRAW) | set(getattr(anim, "ABS", {}))   # abs overlays (button, promise, ...) are block kinds too

def resolve_scenes(doc):
    """[(t0, t1)] for every scene (start/end or dur chained); entries are None where a scene is unusable (validate reports why)"""
    out = []; prev = 0.0
    for sc in doc.get("scenes", []):
        a = sc.get("start", sc.get("t0")); b = sc.get("end", sc.get("t1")); d = sc.get("dur")
        if a is None: a = prev
        if b is None and d is not None and _is_num(d): b = a + d
        out.append((a, b) if _is_num(a) and _is_num(b) else None)
        if out[-1]: prev = out[-1][1]
    return out

def validate(doc, deep=False):
    """-> (errors, warnings), each a list of strings starting with the JSON path"""
    E, W = [], []
    def err(p, m): E.append("%s: %s" % (p, m))
    def warn(p, m): W.append("%s: %s" % (p, m))
    if not isinstance(doc, dict): return ["$: a storyboard is a JSON object"], []
    if doc.get("storyboard") != 1: err("storyboard", "must be 1 (the schema version)")
    for k in doc:
        if k not in TOP_KEYS: err(k, "unknown top-level field (allowed: %s)" % ", ".join(sorted(TOP_KEYS)))
    out = doc.get("output", {}) or {}
    fm = out.get("formats", list(FORMATS))
    if not isinstance(fm, list) or not fm or any(f not in FORMATS for f in fm): err("output.formats", "list of %s, got %r" % (" / ".join(FORMATS), fm))
    if "theme" in out:
        import themes
        if str(out["theme"]).lower() not in themes.THEMES: err("output.theme", "%r is not a theme (built-in: %s; a custom theme must be installed in profiles/ first)" % (out["theme"], ", ".join(themes.THEMES)))
    if "loudness" in out:
        import loudness
        try: loudness.parse_target(out["loudness"])
        except ValueError as e: err("output.loudness", str(e))
    st = doc.get("stages")
    if not isinstance(st, list) or not st or not all(isinstance(x, str) and x for x in st): err("stages", "a non-empty list of chapter names (strings)")
    if not isinstance(doc.get("tech", []), list): err("tech", "a list of strings")
    tm = doc.get("timing", {}) or {}
    for k, v in tm.items():
        if k not in ("duration", "end", "tag1", "tag2", "subscribe_at", "follow_at"): err("timing." + k, "unknown timing field")
        elif v is not False and not _is_num(v): err("timing." + k, "seconds (number)%s" % (" or false" if k in ("subscribe_at", "follow_at") else ""))
    scenes = doc.get("scenes")
    if not isinstance(scenes, list) or not scenes: err("scenes", "a non-empty list of scenes"); return E, W
    rng = resolve_scenes(doc); kinds = None; ids = {}; ent_seen = {}
    for i, sc in enumerate(scenes):
        p = "scenes[%d]" % i
        if not isinstance(sc, dict): err(p, "a scene is an object"); continue
        for k in sc:
            if k not in SCENE_KEYS: err("%s.%s" % (p, k), "unknown scene field (allowed: %s)" % ", ".join(sorted(SCENE_KEYS - {"t0", "t1"})))
        if "id" in sc:
            if sc["id"] in ids: err(p + ".id", "duplicate id %r (also scenes[%d])" % (sc["id"], ids[sc["id"]]))
            ids[sc["id"]] = i
        if rng[i] is None: err(p, "needs start and end, or dur (seconds)")
        else:
            a, b = rng[i]
            if b <= a: err(p, "ends (%.2f) before it starts (%.2f)" % (b, a))
            if i and rng[i - 1] and a < rng[i - 1][1] - 1e-6: err(p + ".start", "%.2f starts before scenes[%d] ends (%.2f); scenes must not overlap" % (a, i - 1, rng[i - 1][1]))
            if i and rng[i - 1] and a > rng[i - 1][1] + 1.0 + 1e-6: warn(p + ".start", "%.1f s gap after scenes[%d]: the screen shows only the background there" % (a - rng[i - 1][1], i - 1))
        s = sc.get("stage", 0)
        if not (isinstance(s, int) and not isinstance(s, bool) and isinstance(st, list) and 0 <= s < len(st)): err(p + ".stage", "index of a chapter in \"stages\" (0..%d), got %r" % (len(st) - 1 if isinstance(st, list) and st else 0, s))
        if not isinstance(sc.get("head", ""), str): err(p + ".head", "text")
        bl = sc.get("blocks", [])
        if not isinstance(bl, list): err(p + ".blocks", "a list of blocks"); bl = []
        for j, b in enumerate(bl):
            bp = "%s.blocks[%d]" % (p, j)
            if not isinstance(b, dict) or "k" not in b: err(bp, "a block is an object with a \"k\" (kind)"); continue
            kinds = kinds or _kinds()
            if b["k"] not in kinds and b["k"] not in ("row", "tiles"): err(bp + ".k", "unknown block kind %r (python3 engine/blocks_info.py lists them)" % b["k"])
            if "t" in b and not _is_num(b["t"]): err(bp + ".t", "seconds (number), got %r" % (b["t"],))
            elif "t" in b and rng[i] and not (rng[i][0] - 1e-6 <= b["t"] <= rng[i][1] + 1e-6): warn(bp + ".t", "%.2f is outside its scene (%.2f to %.2f)" % (b["t"], rng[i][0], rng[i][1]))
        for e in sc.get("entities", []) or []:
            if isinstance(e, dict) and "id" in e:
                if e["id"] in ent_seen: err("%s.entities" % p, "entity %r is also defined in scenes[%d]: define it once (docs/PATHS_AND_ENTITIES.md)" % (e["id"], ent_seen[e["id"]]))
                ent_seen[e["id"]] = i
    for i, sc in enumerate(scenes):   # features validated by their own modules (same messages the engine would give)
        if not isinstance(sc, dict): continue
        p = "scenes[%d]" % i
        try:
            import transitions as _tr
            for key in ("transition", "trans_in", "trans_out"):
                if key in sc: _tr.parse_spec(sc[key])
        except ValueError as e: err(p + ".transition", str(e))
        if "camera" in sc:
            try: import transform as _xf; _xf.validate_camera(sc["camera"])
            except ValueError as e: err(p + ".camera", str(e))
    if "transition" in doc:
        try: import transitions as _tr; _tr.parse_spec(doc["transition"])
        except ValueError as e: err("transition", str(e))
    try:
        import entities as _en
        _en.validate([(i, e) for i, sc in enumerate(scenes) if isinstance(sc, dict) for e in (sc.get("entities") or [])])
    except ValueError as e:
        if "defined twice" not in str(e): err("entities", str(e))
    au = doc.get("audio", {}) or {}
    for k in au:
        if k not in ("auto", "events", "pins"): err("audio." + k, "unknown audio field (auto, events, pins)")
    import audio_events as _ae
    for k, v in (au.get("events", {}) or {}).items():
        if k not in _ae.KINDS: err("audio.events." + k, "unknown event kind (%s)" % ", ".join(_ae.KINDS))
        elif not (isinstance(v, bool) or _is_num(v)): err("audio.events." + k, "false, true, or a level multiplier (number)")
    for j, pin in enumerate(au.get("pins", []) or []):
        if not (isinstance(pin, list) and len(pin) >= 2 and _is_num(pin[0]) and isinstance(pin[1], str)): err("audio.pins[%d]" % j, "[seconds, \"sound_name\", optional level]")
    if not E and deep:   # the engine's own checks (text, overflow, overlaps): lint on the compiled scene file
        import tempfile, subprocess
        d = tempfile.mkdtemp(); f = os.path.join(d, "compiled_scenes.json"); json.dump(compile_doc(doc), open(f, "w", encoding="utf-8"), ensure_ascii=False)
        r = subprocess.run([sys.executable, os.path.join(HERE, "lint.py"), f], capture_output=True, text=True, cwd=d)
        for ln in (r.stdout + r.stderr).splitlines():
            if ln.startswith("LINT"): (W if ("video_type" in ln or "logo missing" in ln or "squeezed" in ln or "variety" in ln) else E).append("lint: " + ln)   # video-type/logo/squeeze/variety rules are layout advice, not schema errors
    return E, W

def compile_doc(doc):
    """storyboard -> the flat scene dict the engine loads (DUR, T_END, TAG1, TAG2, STAGES, TECH, SC, SUB_T, FOL_T, SFX, SFX_EVENTS, plus _env: settings applied as defaults)"""
    rng = resolve_scenes(doc); tm = doc.get("timing", {}) or {}; SC = []
    for sc, (a, b) in zip(doc["scenes"], rng):
        o = {k: copy.deepcopy(v) for k, v in sc.items() if k not in ENGINE_ONLY | {"start", "end"}}; o["t0"], o["t1"] = a, b
        o.setdefault("stage", 0); o.setdefault("style", "plain_dark"); o.setdefault("head", ""); o.setdefault("head_t", 0.05); o.setdefault("blocks", [])
        if doc.get("transition") and not any(k in o for k in ("transition", "trans_in")): pass
        SC.append(o)
    t_end = tm.get("end", rng[-1][1]); tag2 = tm.get("tag2", t_end + 1.5); out = {"STAGES": list(doc["stages"]), "TECH": list(doc.get("tech", [])), "SC": SC, "T_END": t_end, "TAG1": tm.get("tag1", t_end + 0.2), "TAG2": tag2, "DUR": tm.get("duration", tag2 + 1.5)}
    if "subscribe_at" in tm: out["SUB_T"] = tm["subscribe_at"]
    if "follow_at" in tm: out["FOL_T"] = tm["follow_at"]
    au = doc.get("audio", {}) or {}
    if "events" in au: out["SFX_EVENTS"] = au["events"]
    if au.get("pins"): out["SFX"] = [tuple(p) for p in au["pins"]]
    if au.get("auto") is False: out["SFX_AUTO"] = False
    env = {}; o_ = doc.get("output", {}) or {}
    if "theme" in o_: env["CTRLH_THEME"] = str(o_["theme"]).lower()
    if "loudness" in o_ and o_["loudness"]: env["CTRLH_LOUDNESS"] = str(o_["loudness"])
    if doc.get("transition"): env["CTRLH_TRANSITION"] = doc["transition"] if isinstance(doc["transition"], str) else json.dumps(doc["transition"])
    out["_env"] = env; out["_storyboard"] = {"meta": doc.get("meta", {}), "voiceover": doc.get("voiceover", {}), "formats": (o_.get("formats") or list(FORMATS))}
    return out

def summary(doc):
    rng = resolve_scenes(doc); lines = []; meta = doc.get("meta", {})
    lines.append("%s  [%s]  formats: %s  theme: %s" % (meta.get("title", "(untitled)"), meta.get("language", "?"), ", ".join((doc.get("output", {}) or {}).get("formats", FORMATS)), (doc.get("output", {}) or {}).get("theme", "default")))
    for i, (sc, r) in enumerate(zip(doc["scenes"], rng)):
        tt = "%6.1f-%-6.1f (%4.1fs)" % (r[0], r[1], r[1] - r[0]) if r else "   ? "; kinds = ", ".join(sorted({b.get("k", "?") for b in sc.get("blocks", []) if isinstance(b, dict)})) or "-"
        extra = " | ".join(x for x in ("transition: %s" % sc["transition"] if "transition" in sc else "", "camera" if sc.get("camera") else "", "entities: %s" % ",".join(e["id"] for e in sc["entities"]) if sc.get("entities") else "") if x)
        lines.append("%2d %-10s %s  stage %s  %s%s" % (i, sc.get("id", ""), tt, sc.get("stage", 0), "[%s]" % kinds, ("  " + extra) if extra else ""))
        if sc.get("say"): lines.append("     say: %s" % (sc["say"] if len(sc["say"]) < 110 else sc["say"][:107] + "..."))
    return "\n".join(lines)

def from_scenes(N, title=""):
    """existing scene module (Python or JSON) -> storyboard dict (tuples become lists; every field kept)"""
    def jsonable(x):
        if isinstance(x, tuple): return [jsonable(v) for v in x]
        if isinstance(x, list): return [jsonable(v) for v in x]
        if isinstance(x, dict): return {k: jsonable(v) for k, v in x.items()}
        return x
    scenes = []
    for i, s in enumerate(N.SC):
        o = jsonable(copy.deepcopy(s)); o["id"] = "s%d" % i; o["start"] = o.pop("t0"); o["end"] = o.pop("t1"); scenes.append(o)
    d = {"storyboard": 1, "meta": {"title": title or getattr(N, "__name__", "imported"), "language": "ar"}, "output": {"formats": list(FORMATS)},
         "timing": {"duration": N.DUR, "end": N.T_END, "tag1": N.TAG1, "tag2": N.TAG2}, "stages": list(N.STAGES), "tech": list(N.TECH), "scenes": scenes}
    for a, b in (("SUB_T", "subscribe_at"), ("FOL_T", "follow_at")):
        if hasattr(N, a): d["timing"][b] = getattr(N, a)
    if getattr(N, "SFX_EVENTS", None): d["audio"] = {"events": jsonable(N.SFX_EVENTS)}
    if getattr(N, "SFX", None): d.setdefault("audio", {})["pins"] = jsonable(N.SFX)
    return d

TEMPLATE = {"storyboard": 1, "meta": {"title": "My video", "language": "ar"}, "output": {"formats": ["wide", "reel"], "theme": "paper_orange"},
            "voiceover": {"file": "voice.wav"}, "stages": ["Problem", "Solution"], "tech": ["Laravel"],
            "scenes": [{"id": "intro", "start": 0, "end": 8, "stage": 0, "head": "The problem", "say": "what is said here",
                        "blocks": [{"k": "card", "t": 1.0, "text": "A first card", "ok": False}]},
                       {"id": "fix", "dur": 8, "stage": 1, "head": "The fix", "say": "what is said here",
                        "blocks": [{"k": "card", "t": 9.5, "text": "A second card", "ok": True}], "transition": "slide"}]}

def load(path):
    with open(path, encoding="utf-8") as f: return json.load(f)

def main(a):
    if not a or a[0] not in ("template", "validate", "summary", "compile", "import"): print(__doc__); return 2
    c = a[0]
    if c == "template": print(json.dumps(TEMPLATE, ensure_ascii=False, indent=1)); return 0
    if c == "import":
        import scenefile; sys.path.insert(0, os.getcwd()); N = scenefile.load(a[1]); d = from_scenes(N, os.path.splitext(os.path.basename(a[1]))[0])
        json.dump(d, open(a[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("wrote", a[2], "(%d scenes)" % len(d["scenes"])); return 0
    doc = load(a[1])
    if c == "validate":
        E, W = validate(doc, deep=True)
        for w in W: print("WARN ", w)
        for e in E: print("ERROR", e)
        print("%d error(s), %d warning(s)" % (len(E), len(W))); return 1 if E else 0
    if c == "summary": print(summary(doc)); return 0
    if c == "compile":
        E, W = validate(doc)
        if E: print("\n".join("ERROR " + e for e in E)); return 1
        json.dump(compile_doc(doc), open(a[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("wrote", a[2]); return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
