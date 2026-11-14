"""Block registry view:  python3 engine/blocks_info.py [kind] [--check]
Lists every registered block kind: which file registered it, whether it is an overlay (ABS), whether it declares its own layout height (EXTRA_H), whether the docs mention it
and which example scenes use it. With a kind name it shows that block's docs lines. --check exits 1 when a kind is not documented in docs/CATALOG.md or docs/FEATURES.md.
Read-only: it imports the engine and changes nothing."""
import os, sys, re, glob
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); os.environ.setdefault("FMT", "wide")
import anim
K = os.path.join(here, "..")
docs = {f: open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(K, "docs", "*.md")) + [os.path.join(K, "README.md")]}
ex = {f: open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(K, "examples", "*.py"))}
def documented(k): return [os.path.basename(f) for f, t in docs.items() if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(k), t) and os.path.basename(f) in ("CATALOG.md", "FEATURES.md", "PATHS_AND_ENTITIES.md", "TIMELINE.md", "BLOCKS.md")]
def used_in(k): return sorted(os.path.basename(f) for f, t in ex.items() if re.search(r"""["']k["']\s*:\s*["']%s["']""" % re.escape(k), t))
kinds = sorted(set(anim.DRAW) | {k[4:] for k in anim.BLOCK_SOURCE if k.startswith("abs:")})
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    k = sys.argv[1]; print(k, "->", anim.BLOCK_SOURCE.get(k) or anim.BLOCK_SOURCE.get("abs:" + k) or "NOT REGISTERED")
    for f, t in docs.items():
        for ln in t.split("\n"):
            if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(k), ln): print("  %s: %s" % (os.path.basename(f), ln.strip()[:170]))
    sys.exit(0)
print("%-14s %-22s %-5s %-7s %-6s %s" % ("kind", "file", "abs", "layout", "docs", "used in examples"))
miss = []
for k in kinds:
    src = anim.BLOCK_SOURCE.get(k) or anim.BLOCK_SOURCE.get("abs:" + k, "?"); d = documented(k); ab = "abs:" + k in anim.BLOCK_SOURCE or k in anim.ABS
    print("%-14s %-22s %-5s %-7s %-6s %s" % (k, src, "yes" if ab else "", "yes" if k in anim.EXTRA_H else "", "yes" if d else "NO", ", ".join(used_in(k)[:3])))
    if not d: miss.append(k)
print("\n%d kinds; undocumented: %s" % (len(kinds), ", ".join(miss) or "none"))
sys.exit(1 if miss and "--check" in sys.argv else 0)
