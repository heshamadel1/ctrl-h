"""Load a scene file written in Python (my_scenes.py) OR in JSON (my_scenes.json: any language can write it, e.g. Node, see node/ctrlh.js).
JSON keys: DUR, T_END, TAG1, TAG2, STAGES, TECH, SC (list of scene dicts), and optionally SUB_T, FOL_T, KEYS, FLOW, HITS, SUB_T."""
import os, sys, json, types, importlib
JSON_KEYS_DEFAULT = {"KEYS": [], "FLOW": [], "HITS": []}
def base_name(name): return os.path.splitext(os.path.basename(name))[0]
def load_json(path):
    with open(path, encoding="utf-8") as f: d = json.load(f)
    if isinstance(d, dict) and "storyboard" in d:   # a storyboard document (engine/storyboard.py): checked here, compiled to the flat format below
        import storyboard
        er, _w = storyboard.validate(d)
        if er: raise SystemExit("storyboard %s has %d error(s):\n  %s\n(python3 engine/storyboard.py validate %s for the full report)" % (path, len(er), "\n  ".join(er[:12]), path))
        d = storyboard.compile_doc(d)
        for k, v in d.pop("_env", {}).items(): os.environ.setdefault(k, v)   # output.theme / loudness / transition: an explicit environment/config value wins
    m = types.ModuleType(base_name(path)); m.__dict__.update(JSON_KEYS_DEFAULT); m.__dict__.update(d); m.__file__ = os.path.abspath(path)
    for k in ("DUR", "T_END", "TAG1", "TAG2", "STAGES", "TECH", "SC"):
        if k not in d: raise SystemExit("scene json %s: missing key %s" % (path, k))
    return m
def load(name):
    if name.endswith(".json"): return load_json(name)
    try: return importlib.import_module(name)
    except ModuleNotFoundError:
        for p in (name + ".json", os.path.join(os.getcwd(), name + ".json")):
            if os.path.isfile(p): return load_json(p)
        raise
