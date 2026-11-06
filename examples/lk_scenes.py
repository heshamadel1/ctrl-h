NB = " "
def c(t, text, ok=None, tag=None, key=None, size=None):
    b = {"k": "card", "t": t, "text": text, "ok": ok}
    if tag: b["tag"] = tag
    if key: b["key"] = key
    if size: b["size"] = size
    return b
DUR, T_END, TAG1, TAG2 = 124.76, 121.19, 122.49, 123.61
STAGES = ["القصة", "Pessimistic", "Optimistic", "الفرق", "الخلاصة"]
TECH = ["Laravel", "PostgreSQL", "MySQL"]
GRN = (80, 230, 140); RED = (255, 92, 92)
SC = [
 dict(style="classic", t0=0, t1=18.39, stage=0, head="آخر تذكرة", head_t=0.2, blocks=[
   {"k": "shock", "t": 0.2, "lines": [("آخر تذكرة في الحفلة", 64, (255, 92, 92)), ("واتنين بيحجزوها", 52, (245, 245, 245))]},
   c(3.54, "أحمد ومحمد ضغطوا على حجز في نفس اللحظة"),
   c(7.46, "إزاي تمنع حجز نفس التذكرة مرتين؟"),
   {"k": "row", "split": 0.5, "items": [{"k": "chip", "t": 14.78, "text": "Pessimistic Locking"}, {"k": "chip", "t": 16.24, "text": "Optimistic Locking"}]},
   {"k": "promise", "abs": True, "t0": 1.0, "t_unlock": 111.03, "t1": 114.0, "locked": "هتعرف تختار بينهم", "open": "اختيارك بقى واضح"}]),
 dict(style="glass", t0=18.39, t1=30.67, stage=1, head="Pessimistic Locking", head_t=18.6, blocks=[
   {"k": "flow", "t": 19.4, "nodes": ["أحمد", "Lock", "التذكرة"], "steps": [(26.66, 0, 1, "Buy"), (28.27, 1, 2, "Lock")]},
   c(21.31, "بتفترض إن التعارض ممكن يحصل"), c(24.53, "فبتقفل السجل أثناء التعديل", True)]),
 dict(style="proposed", t0=30.67, t1=40.88, stage=1, head="محمد يستنى", head_t=30.9, dims=[33.09, 35.83], blocks=[
   c(30.67, "محمد يحاول يعدّل نفس السجل", None, "TRY", "يعدّل"),
   c(33.09, "يستنى لحد ما Transaction أحمد تخلص", None, "WAIT", "يستنى"),
   c(35.83, "بعدها يقرأ الحالة الجديدة", True, "READ", "الحالة"),
   c(38.24, "ويعرف إن التذكرة اتحجزت", True, "SOLD", "اتحجزت")]),
 dict(style="classic", t0=40.88, t1=50.96, stage=1, head="في Laravel", head_t=41.1, blocks=[
   {"k": "code", "t": 41.1, "file": "TicketService.php", "focus": [(41.73, 1), (43.81, 0)], "lines": [
     (41.2, "DB::transaction(function () {", 26), (41.73, "  Ticket::lockForUpdate()", 26), (43.2, "    ->findOrFail($id)->book();", 26), (44.6, "});", 26)]},
   c(45.53, "مفيدة لما التعارض بيحصل كتير", True), c(48.16, "وعايز تتحكم في الوصول لنفس البيانات")]),
 dict(style="numbers", t0=50.96, t1=61.69, stage=2, head="Optimistic Locking", head_t=51.2, blocks=[
   {"k": "chip", "t": 51.92, "text": "Optimistic Locking"},
   c(53.66, "بنفترض إن التعارض مش بيحصل كتير"), c(56.30, "فمش بنقفل السجل من البداية"), c(59.09, "بنضيف Version Number لكل سجل")]),
 dict(style="proposed", t0=61.69, t1=81.46, stage=2, head="Version Number", head_t=61.9, blocks=[
   {"k": "code", "t": 61.69, "file": "tickets.version", "shake": 73.54, "lines": [
     (61.69, "Ahmed   reads  ->  version 5", 22), (64.35, "Mohamed reads  ->  version 5", 22), (67.17, "Ahmed   saves  ->  version 6", 22, GRN),
     (70.62, "Mohamed saves  ->  version 5", 22), (73.54, "UPDATE 0 rows  ->  FAILED", 24, RED)]},
   c(74.84, "لأن البيانات اتغيرت", False, "STALE", "اتغيرت"),
   c(76.50, "يعيد المحاولة أو يبلّغ المستخدم", True, "RETRY", "يعيد"),
   ]),
 dict(style="glass", t0=81.46, t1=101.25, stage=3, head="الفرق بينهم", head_t=81.7, reserve=170, reserve_reel=230, blocks=[
   {"k": "button", "abs": True, "kind": "subscribe", "t0": 95.0, "t1": 101.25},
   {"k": "compare", "t": 82.2, "panels": [("Pessimistic", [(82.46, "قفل وانتظار"), (94.03, "أنسب لو التعارض متكرر")]), ("Optimistic", [(87.10, "يسمح بالمحاولة"), (90.91, "يكتشف التعارض وقت الحفظ"), (98.34, "أنسب لو التعارض نادر")])]}]),
 dict(style="numbers", t0=101.25, t1=111.17, stage=4, head="الخلاصة", head_t=101.5, reserve=170, reserve_reel=230, blocks=[
   c(101.89, "متختارش طريقة لمجرد إنها أسرع", False), c(105.57, "اختار حسب طبيعة البيانات", True),
   c(108.03, "واحتمال التعارض", True), c(109.33, "وتكلفة إعادة المحاولة أو الانتظار", True),
   {"k": "button", "abs": True, "kind": "follow", "t0": 107.2, "t1": 111.17}]),
 dict(style="proposed", t0=111.17, t1=121.19, stage=4, head="سؤال", head_t=111.4, blocks=[
   c(112.86, "قولي في الكومنتات", None, "COMMENT", "الكومنتات"), c(113.80, "لو بتبني E-commerce System"),
   {"k": "poll", "t": 116.18, "q": "اختار واكتب في الكومنتات", "t_fill": 116.6, "nopct": True, "opts": [("Pessimistic Locking", 0), ("Optimistic Locking", 0)]},
   c(120.07, "وليه؟")]),
]
KEYS = []; FLOW = []; HITS = []
