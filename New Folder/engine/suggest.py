"""Draft scene file from the script + times.json (align.py).  A STARTING POINT to review, not a finished video.
usage: python3 suggest.py script.txt times.json [--out draft_scenes.py] [--max-scene 22]
Rules: a [section] header -> a scene group (split when longer than --max-scene seconds); the first script line (the title) -> shock;
a question line + the next line -> mystery; every other line -> a card (ok=False when it says لأ / مش / غلط, ok=True for كويس / مناسب / أفضل ...);
tools named in the text (HUD_TOOLS in blocks_hud.py) -> scene chips; the last 'Ctrl H' line -> the end card.
Then replace weak cards with the block that fits (versus, er, pipeline, chain, diff ... see docs/FEATURES.md)."""
import sys, os, re, json
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
NB = "\u00a0"
def tools():
    s = open(os.path.join(here, "blocks_hud.py"), encoding="utf-8").read(); m = re.search(r"HUD_TOOLS = (\[.*?\])", s, re.S)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else []
def short(t, n=40):
    t = re.sub(r"^(طيب|يعني|لكن|وده|ده|هنا|وكمان|وبعدها|بالتالي|في المقابل)[،,]?\s+", "", t.strip())
    for sep in ("،", ".", ":"):
        a = t.split(sep)[0]
        if 12 <= len(a) <= n: t = a; break
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0]
    return re.sub("(\u0627\u0644\u0640) (?=[A-Za-z])", "\\1" + NB, t.rstrip("؟?.،, "))
BAD = ("لأ", "مش ", "غلط", "مشكلة", "خطر", "صعب"); GOOD = ("كويس", "مناسب", "أفضل", "بسيط", "سهل", "بيسهّل", "مرونة")
def main():
    script, times = sys.argv[1], sys.argv[2]; d = json.load(open(times, encoding="utf-8")); L = d["lines"]
    title = ""
    for l in open(script, encoding="utf-8").read().split("\n"):
        if l.strip() and not l.startswith("["): title = l.strip(); break
    end = None
    if L and re.search(r"ctrl\s*h", L[-1]["text"], re.I): end = L.pop()
    T_END = end["t0"] if end else d["duration"] - 3.5
    secs = []; 
    for ln in L:
        if not secs or ln["section"] != secs[-1][0]: secs.append((ln["section"], []))
        secs[-1][1].append(ln)
    mx = float(opt("--max-scene", 22)); groups = []
    for name, lines in secs:
        cur = []
        for ln in lines:
            if cur and ln["t1"] - cur[0]["t0"] > mx: groups.append((name, cur)); cur = []
            cur.append(ln)
        if cur: groups.append((name, cur))
    stage_names = []; 
    for name, _ in groups:
        nm = re.split(r"[—-]", name)[-1].strip() or "المحتوى"
        if nm not in stage_names: stage_names.append(nm)
    all_names = list(stage_names); stage_names = stage_names[:6]
    T = tools(); styles = ["classic", "glass", "neon", "numbers", "outline", "soft", "iconbox", "steps", "proposed", "paper"]
    out = ["# DRAFT made by suggest.py - review every scene, replace weak cards with the block that fits the idea.", "NB = \"\\u00a0\"", "RED = (255, 92, 92)",
           "def c(t, text, ok=None, tag=None, key=None, size=None, words=None):", "    b = {\"k\": \"card\", \"t\": t, \"text\": text, \"ok\": ok}",
           "    if tag: b[\"tag\"] = tag", "    if key: b[\"key\"] = key", "    if size: b[\"size\"] = size", "    if words: b[\"words\"] = words", "    return b", ""]
    out += ["DUR = %.2f; T_END, TAG1, TAG2 = %.1f, %.1f, %.1f" % (d["duration"], T_END, T_END + 1.5, T_END + 3.0), "STAGES = %r" % stage_names, "TECH = %r" % list(dict.fromkeys(x for x in T if re.search(r"(?<![A-Za-z])" + re.escape(x) + r"(?![A-Za-z])", " ".join(l["text"] for l in L), re.I)))[:4], "SC = ["]
    for gi, (name, lines) in enumerate(groups):
        t0 = 0.0 if gi == 0 else lines[0]["t0"]; t1 = T_END if gi == len(groups) - 1 else groups[gi + 1][1][0]["t0"]
        stage = min(all_names.index(re.split(r"[—-]", name)[-1].strip() or "المحتوى"), len(stage_names) - 1) if stage_names else 0
        blocks = []; i = 0; has_my = False; txt = " ".join(l["text"] for l in lines)
        if gi == 0 and title: blocks.append("{\"k\": \"shock\", \"t\": 0.3, \"lines\": [(%r, 54, RED)]}" % short(title, 38))
        cards = 0
        while i < len(lines):
            ln = lines[i]; tx = ln["text"]
            if tx.rstrip().endswith(("؟", "?")) and i + 1 < len(lines) and not has_my:
                blocks.append("{\"k\": \"mystery\", \"t\": %.1f, \"q\": %r, \"a\": %r, \"t_reveal\": %.1f}" % (ln["t0"] + 0.3, short(tx, 30), short(lines[i + 1]["text"], 30), lines[i + 1]["t0"] + 0.4)); has_my = True; i += 2; continue
            if cards < 4:
                ok = False if any(w in tx for w in BAD) else (True if any(w in tx for w in GOOD) else None)
                lat = re.findall(r"[A-Za-z][A-Za-z0-9.+-]{2,}", tx); key = lat[0] if lat else None
                blocks.append("c(%.1f, %r, %r%s)" % (ln["t0"], short(tx), ok, ", tag=%r, key=%r" % ("", key) if key and False else (", key=%r" % key if key else ""))); cards += 1
            i += 1
        chips = [x for x in T if re.search(r"(?<![A-Za-z])" + re.escape(x) + r"(?![A-Za-z])", txt, re.I)][:3]
        head = short(name.split("—")[-1].strip() or (lines[0]["text"]), 28)
        out.append(" dict(style=%r, t0=%.1f, t1=%.1f, stage=%d, head=%r, head_t=%.1f%s, blocks=[\n   %s]),   # TODO: %s" % (styles[gi % len(styles)], t0, t1, stage, head, t0 + 0.2, ", chips=%r" % chips if chips else "", ",\n   ".join(blocks), lines[0]["text"][:30]))
    out += ["]", "KEYS = []; FLOW = []; HITS = []"]
    dst = opt("--out", "draft_scenes.py"); open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n"); print("draft: %s (%d scenes, T_END %.1f)" % (dst, len(groups), T_END))
main()
