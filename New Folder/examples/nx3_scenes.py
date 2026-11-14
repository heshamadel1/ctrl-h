NB = " "
def c(t, text, ok=None, tag=None, key=None, size=None):
    b = {"k": "card", "t": t, "text": text, "ok": ok}
    if tag: b["tag"] = tag
    if key: b["key"] = key
    if size: b["size"] = size
    return b
DUR, T_END, TAG1, TAG2 = 125.80, 122.25, 123.45, 124.52
STAGES = ["المشكلة", "الحل", "المميزات", "الاستخدام", "الخلاصة"]
TECH = ["Next.js", "React", "Node.js"]
SC = [
 dict(style="classic", t0=0, t1=12.4, stage=0, head="لو بتستخدم React", head_t=0.23, blocks=[
   {"k": "shock", "t": 0.2, "lines": [("بتبني نفس الحاجات كل مرة؟", 64, (255, 92, 92))]},
   c(0.23, "فيه Framework يسهّل بناء تطبيقات ويب كاملة", True),
   c(6.57, "ويحسّن عرض الصفحات والتعامل مع البيانات", True),
   {"k": "title", "t": 10.47, "text": "Next.js"},
   {"k": "promise", "abs": True, "t0": 1.0, "t_unlock": 97.08, "t1": 100.0, "locked": "هتعرف تختار بينهم", "open": "اختيارك بقى واضح"}]),
 dict(style="numbers", t0=12.4, t1=27.2, stage=0, head="React لوحده", head_t=12.68, grid="pairs", blocks=[
   c(12.68, "تجهّز حلول للـ" + NB + "Routing"), c(16.0, "وتفكر في ظهور موقعك في محركات البحث"),
   c(20.44, "وتنظم تحميل البيانات وعرض الصفحات"), c(23.87, "وبيختلف حسب الأدوات وطريقة بناء المشروع")]),
 dict(style="glass", t0=27.2, t1=40.1, stage=1, head="هنا بييجي دور Next.js", head_t=27.79, grid="pairs", blocks=[
   {"k": "mystery", "t": 27.79, "q": "إيه الحل؟", "t_reveal": 29.85, "a": "Next.js"},
   c(29.85, "Framework مبني على React"), c(32.21, "أدوات جاهزة تساعدك تنظم التطبيق"),
   c(35.38, "تختار الصفحات تتعرض على السيرفر"), c(38.39, "أو تتجهز مسبقًا", True)]),
 dict(style="proposed", t0=40.1, t1=51.9, stage=2, head="File-based Routing", head_t=41.93, blocks=[
   {"k": "counter", "t": 40.24, "t0": 40.3, "t1": 41.6, "v0": 0, "v1": 4, "label": "أهم المميزات", "size": 100},
   c(44.75, "الملفات والمجلدات بتحدد مسارات الصفحات", True, "ROUTES", "الملفات"),
   c(49.09, "من غير ما تبني نظام Routing كامل بنفسك", True, "NO SETUP", "Routing"),
   {"k": "code", "t": 45.0, "file": "app/", "focus": [(45.2, 0), (46.6, 1), (48.2, 2)], "lines": [(45.2, "app/page.tsx       ->  /", 24), (46.6, "app/blog/page.tsx  ->  /blog", 24), (48.2, "> GET /blog   200 OK", 26, (80, 230, 140))]}]),
 dict(style="classic", t0=51.9, t1=63.4, stage=2, head="SSR", head_t=52.12, blocks=[
   {"k": "chip", "t": 52.12, "text": "Server-Side Rendering"},
   {"k": "flow", "t": 53.0, "nodes": ["Browser", "Server", "Data"], "steps": [(56.21, 0, 1, "Request"), (57.2, 1, 2, "fetch"), (58.0, 2, 1, "data"), (58.7, 1, 0, "HTML")]},
   c(56.21, "تعرض الصفحة على السيرفر وقت الطلب"), c(59.25, "مفيد لما المحتوى بيتحدث باستمرار", True)]),
 dict(style="glass", t0=63.4, t1=72.8, stage=2, head="SSG", head_t=63.66, blocks=[
   {"k": "chip", "t": 63.66, "text": "Static Site Generation"},
   {"k": "flow", "t": 64.5, "nodes": ["Build", "CDN", "Browser"], "steps": [(67.29, 0, 1, "Pages"), (70.16, 1, 2, "Instant")]},
   c(67.29, "تجهّز الصفحات وقت الـ" + NB + "Build"), c(70.16, "مناسب للمحتوى الثابت نسبيًا", True)]),
 dict(style="proposed", t0=72.8, t1=82.6, stage=2, head="Server Components", head_t=73.05, blocks=[
   {"k": "predict", "t": 73.05, "lines": ["export default async function Page() {", "  const posts = await db.posts()", "  return <List items={posts} />", "}"], "q": "الكود ده بيتنفذ فين؟", "t_count": 74.0, "t_ans": 77.0, "ans": "على السيرفر"},
   c(75.62, "تنفّذ أجزاء من الواجهة على السيرفر", None, "RSC", "السيرفر"),
   c(78.21, "وتقلل JavaScript اللي بيتبعت للمتصفح", True, "LESS JS", "JavaScript")]),
 dict(style="classic", t0=82.6, t1=93.9, stage=3, head="إمتى تستخدمه", head_t=82.84, grid="tiles", blocks=[
   {"k": "ring", "abs": True, "t0": 82.9, "t1": 85.9, "label": "فكّر"},
   c(84.46, "E-commerce"), c(86.7, "Dashboards"), c(89.17, "مواقع المحتوى"), c(90.58, "تطبيقات محتاجة أداء")]),
 dict(style="numbers", t0=93.9, t1=99.8, stage=3, head="لكن خد بالك", head_t=94.21, reserve=170, reserve_reel=230, blocks=[
   {"k": "strike", "t": 94.21, "t_strike": 95.4, "t_right": 97.08, "wrong": "Next.js لكل مشروع", "right": "اختار حسب احتياج التطبيق"},
   {"k": "button", "abs": True, "kind": "subscribe", "t0": 96.3, "t1": 99.8}]),
 dict(style="glass", t0=99.8, t1=112.4, stage=4, head="الخلاصة", head_t=100.11, reserve=170, reserve_reel=230, blocks=[
   {"k": "compare", "t": 103.0, "panels": [("React", [(103.04, "الأساس"), (103.9, "بناء الواجهات")]), ("Next.js", [(105.95, "أدوات جاهزة"), (107.52, "تطبيق ويب متكامل")])]},
   c(111.07, "بطريقة منظمة", True),
   {"k": "button", "abs": True, "kind": "follow", "t0": 108.6, "t1": 112.4}]),
 dict(style="proposed", t0=112.4, t1=122.25, stage=4, head="سؤال", head_t=112.72, blocks=[
   c(114.77, "قولي في الكومنتات", None, "COMMENT", "الكومنتات"), c(116.18, "لو هتبدأ مشروع جديد"),
   {"k": "poll", "t": 117.78, "q": "اختار واكتب في الكومنتات", "t_fill": 118.2, "nopct": True, "opts": [("React لوحده", 0), ("Next.js", 0)]},
   c(121.13, "وليه؟")]),
]
KEYS = [44.75, 49.09, 75.62, 78.21, 114.77]
FLOW = [56.21, 57.2, 58.0, 58.7, 67.29, 70.16]
HITS = []
