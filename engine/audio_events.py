"""Structured sound events (Phase 7.1). ONE place that knows which on-screen thing makes which sound, derived from the same scene data and times the
animation uses, so audio never has its own copy of the timing. No audio libraries here: it returns plain Event tuples (testable without FFmpeg);
make_audio_lib.py turns them into sound.

  Event(t, kind, cat, gain, src, dur, name)
     t     seconds on the global timeline (the same t the blocks use)       kind  logical event name (what you enable/disable, see KINDS)
     cat   sound-library category (pop, click, success, ...)                gain  relative level
     src   where it came from, e.g. "scene 3 card"                         dur   seconds (typing bursts) or None
     name  a specific library file to use instead of a random pick of `cat`

Control (all optional):
  scene file   SFX_EVENTS = {"item": False, "scene_cut": 0.5}    False = never, a number = gain multiplier, True = default
  scene key    "sfx": False                    silence the whole scene          "sfx": {"off": ["item"], "gain": {"typing": 0.5}}   per-scene switches
  block key    "sfx": False                    silence one block                "sfx": 0.6   scale one block
  env/config   CTRLH_SFX_OFF="item,scene_cut"  (config key "sfx_off")
  scene file   SFX = [(12.5, "impact_01")]     manual pins are still handled by make_audio_lib.py
Duplicates: two events of the same kind and sound within 0.02 s are one event; sysdiagram keeps its own spacing rule (no same kind within 0.18 s).
A scene whose transition resolves to "none" gets no cut sound."""
from collections import namedtuple

Event = namedtuple("Event", "t kind cat gain src dur name")
def _ev(t, kind, cat, gain=1.0, src="", dur=None, name=None): return Event(float(t), kind, cat, float(gain), src, dur, name)

KINDS = {
    "scene_cut": "whoosh at a scene cut", "chapter_change": "transition sound when the chapter (stage) changes", "item": "pop/click as cards, recap rows, steps appear",
    "ok": "success sound for an ok:true card", "error": "error sound for an ok:false card", "key_hit": "impact for a key card", "shock": "impact + glitch", "mystery": "riser",
    "strike": "pen stroke", "counter": "click at a counter start", "typing": "typing burst for code and chat lines", "node": "tick for system-diagram items",
    "connect": "chime when a beam connection starts drawing", "razor": "razor sound at a timeline split", "clip_remove": "soft whoosh when a timeline clip is removed",
    "track_toggle": "click when a timeline track is switched", "morph": "pop when a persistent entity changes state", "entity_in": "pop when a persistent entity appears"}

_ITEM_BLOCKS = ("card", "recap", "icards", "steplist", "fixcards", "versus", "chain", "matrix")
_SD = {"sd_stage": "transition", "sd_tick": "click", "sd_ok": "success", "sd_err": "error", "sd_env": "whoosh", "sd_sticker": "pop", "sd_done": "success"}

def flat(bl):
    for b in bl:
        if b.get("k") in ("row", "tiles") and "items" in b: yield from flat(b["items"])
        else: yield b

def _cut_silent(s):
    tr = s.get("trans_in") or s.get("transition")
    return (tr if isinstance(tr, str) else (tr or {}).get("kind") if isinstance(tr, dict) else None) == "none"

def collect(SC, events_cfg=None, off_env=""):
    """list of Event in the order the old generator produced them (this keeps the random sound picks of existing videos identical)"""
    cfg = dict(events_cfg or {}); off = {x.strip() for x in (off_env or "").split(",") if x.strip()}
    out = []; prev_stage = None
    def emit(ev, s_sfx, b_sfx):
        k = ev.kind
        if k in off: return
        g = ev.gain; c = cfg.get(k, True); num = isinstance(c, (int, float)) and not isinstance(c, bool)
        if c is False or (num and c == 0): return
        if num: g *= float(c)
        if isinstance(s_sfx, dict):
            if k in (s_sfx.get("off") or []): return
            sg = (s_sfx.get("gain") or {}).get(k)
            if sg is not None:
                if sg == 0: return
                g *= float(sg)
        if b_sfx is False: return
        if isinstance(b_sfx, (int, float)) and not isinstance(b_sfx, bool): g *= float(b_sfx)
        out.append(ev._replace(gain=g))
    for k, s in enumerate(SC):
        s_sfx = s.get("sfx")
        if s_sfx is False: prev_stage = s.get("stage"); continue
        big = s.get("stage") != prev_stage and k > 0; prev_stage = s.get("stage"); sc = "scene %d" % k
        if k > 0 and not _cut_silent(s): emit(_ev(s["t0"] - 0.1, "chapter_change" if big else "scene_cut", "transition" if big else "whoosh", 1.0, sc), s_sfx, None)
        pops = ["pop", "click", "pop", "click"]; j = 0
        for b in flat(s["blocks"]):
            kd = b.get("k"); t0 = b.get("t", b.get("t0", s["t0"])); bs = b.get("sfx"); src = "%s %s" % (sc, kd)
            E = lambda ev: emit(ev, s_sfx, bs)
            if kd in _ITEM_BLOCKS:
                ts = [b["t"]] if kd == "card" and "t" in b else []
                for key in ("items", "cols", "steps", "rows"):
                    for it in (b.get(key) if isinstance(b.get(key), (list, tuple)) else []):
                        ti = it.get("t") if isinstance(it, dict) else (it[0] if isinstance(it, (tuple, list)) and it and isinstance(it[0], (int, float)) else None)
                        if ti is not None: ts.append(ti)
                for ti in ts or [t0]:
                    c = pops[j % 4]; E(_ev(ti, "item", c, .8, src)); j += 1
                if b.get("ok") is True: E(_ev(t0 + .2, "ok", "success", .8, src))
                if b.get("ok") is False: E(_ev(t0 + .05, "error", "error", .7, src))
                if b.get("key"): E(_ev(t0 - .02, "key_hit", "impact", .6, src))
            elif kd == "sysdiagram":
                ev = []
                for (tt, *_r) in b.get("stages", [])[1:]: ev.append((tt - .05, "sd_stage", 1.0))
                for nid, nd in b.get("nodes", {}).items():
                    ev.append((nd["t"], "sd_tick", .7))
                    for bd_ in nd.get("badges", []): ev.append((bd_[0], "sd_ok" if bd_[1] == "ok" else ("sd_err" if bd_[1] == "err" else "sd_tick"), .8))
                    for pl_ in nd.get("pills", []): ev.append((pl_[0], "sd_tick", .55))
                for tx_ in b.get("txn", []): ev.append((tx_[0], "sd_ok" if tx_[2] == "COMMIT" else ("sd_err" if tx_[2] == "ROLLBACK" else "sd_tick"), .8))
                for lk_ in b.get("locks", []): ev.append((lk_[0], "sd_tick", .8))
                for rw_ in (b.get("table") or {}).get("rows", []): ev.append((rw_["t"], "sd_tick", .6))
                for e_ in b.get("env", []): ev.append((e_[0], "sd_env", .7))
                for i_, st_ in enumerate(b.get("stickers", [])): ev.append((st_[0], "sd_done" if i_ == len(b["stickers"]) - 1 else "sd_sticker", .9))
                lastt = {}
                for (te_, nm_, g_) in sorted(ev):
                    if nm_ in lastt and te_ - lastt[nm_] < 0.18: continue
                    lastt[nm_] = te_
                    E(_ev(te_, "node", _SD[nm_], g_, src, None, "success_05_ding" if nm_ == "sd_done" else ("whoosh_02_soft" if nm_ == "sd_env" else None)))
            elif kd == "shock": E(_ev(t0 - .05, "shock", "impact", 1.0, src)); E(_ev(t0, "shock", "glitch", .5, src))
            elif kd == "mystery": E(_ev(max(s["t0"], t0 - 0.2), "mystery", "riser", .7, src))
            elif kd == "strike": E(_ev(t0, "strike", "pen", .8, src))
            elif kd == "counter": E(_ev(b.get("t0", t0), "counter", "click", .8, src))
            elif kd in ("code", "codeann"):
                for ln in b.get("lines", []):
                    if isinstance(ln, (tuple, list)) and len(ln) >= 2 and isinstance(ln[0], (int, float)): E(_ev(ln[0], "typing", "typing", 1.0, src, len(str(ln[1])) / max(1.0, float(ln[2]) if len(ln) >= 3 else 26.0)))
            elif kd == "chatwin":
                for ln in b.get("lines", []):
                    if isinstance(ln, (tuple, list)) and isinstance(ln[0], (int, float)): E(_ev(ln[0], "typing", "typing", .9, src, .9)); E(_ev(ln[0] + 1.0, "ok", "success", .6, src))
            elif kd == "beam":
                for p_ in b.get("paths", []):
                    if p_.get("style", "both") != "beam": E(_ev(p_["t"] + 0.3, "connect", "success", .5, src, None, "success_02_notify_a"))
            elif kd == "tracks":
                for tr in b.get("tracks", []):
                    for tt, _v in tr.get("active", []): E(_ev(tt, "track_toggle", "click", .5, src, None, "click_04_tick"))
                    for c in tr.get("clips", []):
                        if c.get("split"): E(_ev(c["split"][0], "razor", "razor", .8, src, None, "razor_01_cut"))
                        if c.get("until") is not None: E(_ev(c["until"], "clip_remove", "whoosh", .4, src, None, "whoosh_02_soft"))
        for e in s.get("entities", []):
            sts = e.get("states", [])
            E = lambda ev: emit(ev, s_sfx, None)
            E(_ev(e.get("t_in", sts[0]["t"] if sts else s["t0"]), "entity_in", "pop", .5, "entity %s" % e.get("id")))
            for st in sts[1:]: E(_ev(st["t"], "morph", "pop", .5, "entity %s" % e.get("id")))
    return dedupe(out)

def dedupe(evs, tol=0.02):
    """drop an event when the same kind + category + name already sounds within `tol` seconds (keeps the first, preserves order)"""
    kept = []
    for e in evs:
        if any(k.kind == e.kind and k.cat == e.cat and k.name == e.name and abs(k.t - e.t) < tol for k in kept): continue
        kept.append(e)
    return kept

def summary(evs):
    """{kind: count}"""
    d = {}
    for e in evs: d[e.kind] = d.get(e.kind, 0) + 1
    return d

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import scenefile
    arg = sys.argv[1]
    if arg.endswith(".json"): N = scenefile.load_json(arg)
    else: sys.path.insert(0, os.path.dirname(os.path.abspath(arg))); N = scenefile.load(os.path.splitext(os.path.basename(arg))[0])
    ev = collect(N.SC, getattr(N, "SFX_EVENTS", {}), os.environ.get("CTRLH_SFX_OFF", ""))
    for e in sorted(ev, key=lambda e: e.t): print("%7.2f  %-14s %-10s g=%.2f  %s" % (e.t, e.kind, e.cat, e.gain, e.src))
    print("\n%d events: %s" % (len(ev), ", ".join("%s %d" % kv for kv in sorted(summary(ev).items()))))
