"""Storyboard planner: voiceover lines (with times) -> suggested visual per line, as a table the owner can edit BEFORE any scene file is written.
usage: python3 plan.py <lines.txt> [out.md]
lines.txt: one line per phrase, either '#N 12.20-17.82: text' (the *_seg_asr.txt format) or plain text.
Rules are keyword heuristics (a DRAFT, not a decision): Claude reviews the table, the owner changes rows, then the scene file is written from it."""
import re, sys
RULES = [  # (visual, block, keywords)
    ("Question / Hook", "shock + promise", ["؟", "ليه", "ايه", "إيه", "هل"]),
    ("Error State", "code shake + red node", ["غلط", "خطأ", "error", "401", "403", "500", "فشل", "مش صالح", "غير صالح", "اختراق", "ثغرة"]),
    ("Solution Card", "card ok + note", ["الحل", "نحل", "نمنع", "نصلح", "بدل", "الأحسن", "أفضل"]),
    ("Request Flow", "arch (request moves between services)", ["request", "ريكويست", "بيبعت", "بيطلب", "يبعت", "response", "ريسبونس", "api", "endpoint", "token", "توكن"]),
    ("Database Visual", "arch / versus (db)", ["database", "داتابيز", "table", "جدول", "postgres", "بوستغرس", "unique", "migration", "index"]),
    ("Code Walkthrough", "code + focus", ["كود", "code", "function", "دالة", "middleware", "controller", "route", "validation", "فالداتشن", "فاليديشن"]),
    ("Comparison", "versus / matrix", ["مقابل", "أو", "الفرق", "vs", "أحسن من", "بدل"]),
    ("Steps / Checklist", "steplist / icards", ["أول", "تاني", "تالت", "خطوة", "تفصيلة", "نقطة"]),
    ("Number / Counter", "counter / gain", ["ثانية", "مرة", "ميجا", "٪", "%", "ms"]),
    ("CTA", "poll / cta", ["كومنت", "اكتب", "قولي", "اشترك", "تابع"]),
]
def classify(text):
    low = text.lower()
    for name, block, kws in RULES:
        if any(k in low for k in kws): return name, block
    return "Concept Card", "card (style by content)"
def main():
    src = open(sys.argv[1], encoding="utf-8").read().splitlines()
    rows = []
    for ln in src:
        m = re.match(r"#?\d*\s*([\d.]+)-([\d.]+):\s*(.*)", ln)
        t0, t1, text = (m.group(1), m.group(2), m.group(3)) if m else ("", "", ln.strip())
        if text: rows.append((t0, t1, text) + classify(text))
    out = ["| # | Time | Line | Suggested visual | Block |", "|---|---|---|---|---|"]
    for i, (a, b, tx, v, bl) in enumerate(rows, 1): out.append("| %d | %s-%s | %s | %s | %s |" % (i, a, b, tx.replace("|", "/"), v, bl))
    res = "\n".join(out)
    if len(sys.argv) > 2: open(sys.argv[2], "w", encoding="utf-8").write(res + "\n")
    print(res)
if __name__ == "__main__": main()
