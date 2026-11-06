"""One tiny scene per feature -> docs/images/feat-<name>.png  (python3 engine/docs_gallery.py  from the kit root).
Each entry: name -> (headline, blocks, frame_time, extra scene keys). Times are inside an 8 s scene."""
NB = " "
R = (255, 92, 92); G = (80, 230, 140)
def card(t, text, ok=None, **k): return dict({"k": "card", "t": t, "text": text, "ok": ok}, **k)
F = {
 "shock": ("Hook: shock", [{"k": "shock", "t": .3, "lines": [("90% بيغلطوا", 84, R), ("في الحاجة دي", 60, (240, 240, 240))]}], 2.5, {}),
 "promise": ("Promise pill", [card(.5, "الجواب في آخر الفيديو", None), {"k": "promise", "abs": True, "t0": .3, "t_unlock": 7, "t1": 7.9, "locked": "هتعرف السر في الآخر", "open": "السر اتفك"}], 3.0, {}),
 "mystery": ("Mystery card", [{"k": "mystery", "t": .3, "q": "إيه الحل؟", "a": "Next.js", "t_reveal": 6}], 3.0, {}),
 "predict": ("Predict", [{"k": "predict", "t": .3, "lines": ["export default async function Page() {", "  const posts = await db.posts()", "  return <List items={posts} />", "}"], "q": "الكود ده بيتنفذ فين؟", "t_count": 1.5, "t_ans": 5.5, "ans": "على السيرفر"}], 3.5, {}),
 "strike": ("Strike", [{"k": "strike", "t": .3, "t_strike": 2, "t_right": 3, "wrong": "useEffect لكل حاجة", "right": "Server Component"}], 4.5, {}),
 "ba": ("Before / After", [{"k": "ba", "t": .3, "t_slide": 3, "before": ["useEffect(()=>{", "  fetch(url)", "},[])"], "after": ["const d = await", "  fetch(url)", ""]}], 5.0, {}),
 "poll": ("Poll", [{"k": "poll", "t": .3, "q": "اختار واكتب في الكومنتات", "t_fill": .8, "nopct": True, "opts": [("React لوحده", 0), ("Next.js", 0)]}], 4.0, {}),
 "note": ("Note", [card(.3, "الطريقة دي شغالة كويس", True), {"k": "note", "t": 1.2, "text": "لما العمليات تزيد الكود بيصعب في القراءة"}], 4.0, {}),
 "chips": ("Chips", [card(.3, "الكلمات المهمة بتظهر تحت", None), {"k": "chips", "abs": True, "t0": 1, "t1": 7, "items": ["Routing", "SSR", "SEO", "Cache"]}], 4.5, {"reserve": 170}),
 "corner": ("Corner switch", [card(.3, "نفس الفكرة في الاتنين", None), {"k": "corner", "abs": True, "t0": .5, "t1": 8, "labels": ("React", "Next.js"), "switch": [4.0]}], 5.0, {}),
 "counter": ("Counter", [{"k": "counter", "t": .3, "t0": .5, "t1": 3, "v0": 0, "v1": 4, "label": "أهم المميزات", "size": 100}], 4.0, {}),
 "gain": ("Gain", [{"k": "gain", "t": .3, "t0": .6, "t1": 3, "v0": 3.0, "v1": 0.2, "unit": "s", "label": "زمن التحميل"}], 4.0, {}),
 "challenge": ("Challenge ring", [card(.3, "فكّر قبل ما أقولك", None), {"k": "challenge", "abs": True, "t0": 1, "t1": 7, "label": "جاوب"}], 3.5, {}),
 "ring": ("Countdown ring", [{"k": "ring", "abs": True, "t0": 1, "t1": 7, "label": "فكّر"}], 3.5, {}),
 "code_terminal": ("Terminal + shake", [{"k": "code", "t": .3, "file": "terminal", "shake": 5.2, "size": 34, "lines": [(.5, "$ npm run build", 18), (1.6, "> next build", 18, (150, 156, 170)), (2.6, "x Error: useState only works in a Client Component", 30, R), (5.0, "fix: add use client at the top", 24, G)]}], 5.8, {}),
 "code_focus": ("Code focus auto", [{"k": "code", "t": .3, "file": "products.js", "focus": "auto", "lines": [(.6, "function fetchProducts() {", 30), (1.6, "  fetch('/api/products')", 30), (2.6, "    .then(res => res.json())", 30), (3.6, "    .catch(err => handle(err));", 30)]}], 4.6, {"style": "terminal"}),
 "compare": ("Compare", [{"k": "compare", "t": .3, "panels": [("React", [(.6, "الأساس"), (1.2, "بناء الواجهات")]), ("Next.js", [(2.0, "أدوات جاهزة"), (2.8, "تطبيق ويب متكامل")])]}], 4.5, {}),
 "flow": ("Flow", [{"k": "flow", "t": .3, "nodes": ["Browser", "Server", "Data"], "steps": [(1, 0, 1, "Request"), (2, 1, 2, "fetch"), (3, 2, 1, "data"), (4, 1, 0, "HTML")]}], 4.6, {}),
 "timeline": ("Timeline", [{"k": "timeline", "t": .3, "nodes": [(.6, "Build", "npm run build", "ok"), (1.8, "Deploy", "vercel", "ok"), (3.0, "Live", "200 OK", "ok")]}], 4.5, {}),
 "buttons": ("Subscribe + Follow", [card(.3, "الأزرار بتظهر أوتوماتيك", None), {"k": "button", "abs": True, "kind": "subscribe", "t0": .8, "t1": 7.8}, {"k": "button", "abs": True, "kind": "follow", "t0": 3.5, "t1": 7.9}], 5.0, {"reserve": 200}),
 "grid_tiles": ("Tiles", [card(.3, "Framework على React"), card(.6, "أدوات جاهزة"), card(.9, "SSR أو SSG")], 3.0, {"grid": "tiles"}),
}

# ---- flow / system blocks (1.0.0) ----
_OR, _BL, _CY, _GR, _VI, _PK, _YE, _RE = "#FF9A1F", "#1E88FF", "#31B3E8", "#3DDC84", "#B07CFF", "#F0509A", "#F2C230", "#E0607A"
F["titlevs"] = ("Title vs", [{"k": "titlevs", "t": .3, "a": "Monolith", "b": "Microservices", "sub": "System Design"}, card(1.0, "عنوان المقارنة بيظهر فوق", None)], 3.0, {})
F["split"] = ("Split (vs)", [{"k": "split", "t": .2, "counter": "1/5 SCALING", "panels": [
    {"name": "Monolith", "tag": "Scale whole app", "color": _OR, "mode": "box", "services": [{"t": .5, "name": "Users", "icon": "user"}, {"t": .7, "name": "Orders", "icon": "cart"}, {"t": .9, "name": "Payments", "icon": "card"}], "events": [(1.4, "traffic", 1), (2.6, "fail", -1), (3.4, "scale", -1)]},
    {"name": "Microservices", "tag": "Scale one service", "color": _BL, "mode": "fan", "services": [{"t": .6, "name": "Users", "icon": "user"}, {"t": .8, "name": "Orders", "icon": "cart"}, {"t": 1.0, "name": "Payments", "icon": "card"}], "events": [(1.6, "traffic", 1), (2.8, "fail", 1), (3.4, "scale", 1), (4.2, "ver", 1, "v2")]}]}], 5.2, {})
F["chain"] = ("Chain of handlers", [{"k": "chain", "t": .2, "start": "-> Login Request", "payload": "{ email, password }", "steps": [
    {"t": .6, "name": "ValidationHandler", "sub": "email & password not empty", "icon": "clip", "color": "#4C8DFF", "err": (2.2, "400 Bad Request")},
    {"t": 1.2, "name": "AccountHandler", "sub": "exists - not locked", "icon": "user", "color": "#B07CFF", "err": (2.6, "403 Locked")},
    {"t": 1.8, "name": "PasswordHandler", "sub": "verify the password", "icon": "key", "color": "#F2C230", "err": (3.0, "401 Unauthorized")},
    {"t": 2.4, "name": "AuthenticationHandler", "sub": "sign in - issue a token", "icon": "shield", "color": "#3DDC84"}]}], 4.2, {})
F["hub"] = ("Hub and spokes", [{"k": "hub", "t": .2, "top": "E-commerce App", "user": "User", "hub": {"t": .6, "name": "OrdersController", "sub": "Create - Cancel - Update", "icon": "cart", "color": _RE},
    "actions": [{"t": 1.0, "name": "Create Order", "icon": "check", "color": _GR, "to": [0, 1, 2]}, {"t": 1.6, "name": "Cancel Order", "icon": "x", "color": _PK, "to": [1, 3]}, {"t": 2.2, "name": "Update Order", "icon": "gear", "color": _BL, "to": [1, 4]}],
    "spokes": [{"t": .8, "name": "Stock", "icon": "cube", "color": _GR}, {"t": .9, "name": "Orders", "icon": "db", "color": _YE}, {"t": 1.0, "name": "Email", "icon": "mail", "color": "#4C8DFF"}, {"t": 1.1, "name": "Payments", "icon": "card", "color": _VI}, {"t": 1.2, "name": "Pricing", "icon": "gear", "color": _PK}],
    "q": "كل ده من الـ Controller؟!", "q_t": 3.4}], 4.6, {})
F["pipeline"] = ("Pipeline", [{"k": "pipeline", "t": .2, "nodes": [
    {"t": .4, "name": "Validation", "icon": "clip", "color": "#4C8DFF"}, {"t": .8, "name": "RateLimit", "icon": "clock", "color": _OR, "badge": (1.4, "+ NEW", _OR)},
    {"t": 1.2, "name": "Account", "icon": "user", "color": _VI}, {"t": 1.6, "name": "Password v2", "icon": "key", "color": "#4C8DFF", "badge": (2.2, "v2", "#2F7BFF")}, {"t": 2.0, "name": "Auth", "icon": "shield", "color": _GR}]}, card(2.6, "ضيف أو غيّر خطوة بسهولة", True)], 4.0, {})
F["deviceflow"] = ("Device + API + checks", [{"k": "deviceflow", "t": .2, "phone": {"title": "تسجيل الدخول", "fields": [("mail", "sara@mail.com"), ("lock", "********")], "button": "Login", "press_t": 1.4},
    "api": {"t": 1.5, "name": "Login API", "sub": "POST /api/login", "color": _CY}, "steps": [
    {"t": 2.0, "tag": "Validation", "label": "البيانات صحيحة", "icon": "clip", "color": "#4C8DFF"}, {"t": 2.6, "tag": "Account", "label": "الحساب موجود", "icon": "user", "color": _VI},
    {"t": 3.2, "tag": "Not locked", "label": "مش مقفول", "icon": "lock", "color": _RE}, {"t": 3.8, "tag": "Password", "label": "كلمة السر سليمة", "icon": "key", "color": _YE}]}], 5.0, {})
F["codeann"] = ("Annotated code", [{"k": "codeann", "t": .2, "file": "LoginService.cs", "lang": "C#", "lines": [
    (.4, "public class LoginService"), (.6, "{"), (.8, "  public async Task<Result> Login(LoginRequest r)"), (1.0, "  {"),
    (1.2, "    if (await IsRateLimited(ip)) return TooMany();"), (1.4, "    if (!IsValid(r)) return BadRequest();"), (1.6, "    var user = await _users.Find(r.Email);"),
    (1.8, "    if (user is null) return Unauthorized();"), (2.0, "    if (user.IsLocked) return Locked();"), (2.2, "    return Ok(_tokens.Issue(user));"), (2.4, "  }"), (2.6, "}")],
    "squiggle": [(3.0, 4), (3.1, 5), (3.2, 7), (3.3, 8)], "tags": [(3.4, 4, "Security", "#F0A050"), (3.6, 7, "Accounts", "#B07CFF"), (3.8, 8, "Identity", "#F2C230")],
    "counter": (4.0, "if × 10"), "bar": (4.0, 5.5, "#F0606E"), "label": (4.2, "Coupling", "#F0606E"), "cap": (4.6, "4 فرق بيعدّلوا في نفس الـ Method")}], 6.0, {})
F["flowmini"] = ("Mini flow", [{"k": "flowmini", "t": .2, "items": [{"t": .4, "kind": "pill", "name": "Create Order", "icon": "check", "color": _GR}, {"t": 1.0, "kind": "card", "name": "CreateOrderCommand", "icon": "doc", "color": _OR}, {"t": 1.6, "kind": "circle", "name": "Handler", "icon": "gear", "color": _VI}]}, card(2.2, "Command بيروح لـ Handler واحد", None)], 3.6, {})

# ---- optional paper look (scene key paper=True) ----
_PP = {"paper": True, "style": "paper"}
F["quote"] = ("Quote (paper)", [{"k": "quote", "t": .2, "who": "Martin Fowler", "lines": ["Any fool can write code that a computer can understand.", "Good programmers write code that humans can understand."], "hi": [(1.6, "a computer"), (2.4, "humans")]}], 4.0, dict(_PP))
F["chatwin"] = ("Chat window (paper)", [{"k": "chatwin", "t": .2, "title": "booking-app · AI chat", "prompt": "ساعدني أعمل API لحجز المواعيد", "prompt_t": .6, "who": "AI", "cps": 30, "code": [
    (1.4, 'app.post("/bookings", async (req) => {'), (2.4, "  const slot = await db.slots.find(req.slotId);"), (3.4, "  if (slot.taken) throw new Conflict();"), (4.4, "  return db.bookings")]}], 5.5, dict(_PP))
F["bars"] = ("Chart cards (paper)", [{"k": "bars", "t": .2, "cards": [{"t": .4, "label": "تكلفة أقل", "kind": "down"}, {"t": 1.4, "label": "البزنس يكبر", "kind": "up"}]}], 4.5, dict(_PP))
F["skeleton"] = ("Code skeleton (paper)", [{"k": "skeleton", "t": .2, "file": "login.tsx", "lines": 10, "seed": 3, "t0": .6, "t1": 2.6, "hot": [0, 3, 6]}], 3.5, dict(_PP))
F["filegrid"] = ("File grid (paper)", [{"k": "bigcount", "t": .2, "label": "FILE", "of": "/500+", "t0": .4, "t1": 2.6, "v0": 0, "v1": 20}, {"k": "filegrid", "t": .3, "cols": 5, "t0": .6, "t1": 2.6, "missing": (3.0, 4), "active": [(1.0, 15)], "files": [
    "user.ts", "db.sql", "api.ts", "cart.js", "auth.ts", "config.yml", "routes.js", "order.ts", "utils.ts", "index.js", "model.py", "hooks.ts", "store.ts", "app.tsx", "pay.ts", "login.tsx", "types.ts", "seed.sql", "cache.ts", "mail.ts"]}], 4.0, dict(_PP))

# ---- paper blocks (1.0.0) ----
F["quote"] = ("Quote", [{"k": "quote", "t": .2, "who": "Martin Fowler", "lines": ["Any fool can write code that a computer can understand.", "Good programmers write code that humans can understand."], "hl": [("computer", 1.5)]}], 3.2, {})
F["chatwin"] = ("AI chat window", [{"k": "chatwin", "t": .2, "title": "booking-app · AI chat", "ask": "ساعدني أعمل API لحجز المواعيد", "ask_t": .5, "lines": [(1.4, 'app.post("/bookings", async (req) => {'), (2.2, "  const slot = await db.slots.find(req.slotId);"), (3.0, "  if (slot.taken) throw new Conflict();"), (3.8, "  return db.bookings")]}], 4.4, {})
F["minichart"] = ("Mini charts", [{"k": "minichart", "t": .2, "rows": [{"t": .4, "label": "تكلفة أقل", "kind": "down"}, {"t": 1.6, "label": "البزنس يكبر", "kind": "up"}]}], 4.5, {})
F["skeleton"] = ("Code skeleton", [{"k": "skeleton", "t": .2, "file": "login.tsx", "n": 9, "span": 2.4}], 3.4, {})
F["filegrid"] = ("File grid", [{"k": "bigcount", "t": .2, "label": "FILE", "t0": .4, "t1": 2.4, "v0": 0, "v1": 20, "suffix": "/500+"}, {"k": "filegrid", "t": .6, "files": ["user.ts", "db.sql", "api.ts", "cart.js", "auth.ts", "config.yml", "routes.js", "order.ts", "utils.ts", "index.js", "model.py", "hooks.ts", "store.ts", "app.tsx", "pay.ts", "login.tsx", "types.ts", "seed.sql", "cache.ts", "mail.ts"], "span": 1.8, "missing": (4, 2.6), "pick": (15, 3.0)}], 3.8, {})
F["bigcount"] = ("Big counter", [{"k": "bigcount", "t": .2, "label": "FILE", "t0": .4, "t1": 2.4, "v0": 0, "v1": 20, "suffix": "/500+"}], 3.0, {})
