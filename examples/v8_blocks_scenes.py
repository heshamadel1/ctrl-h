NB = " "
CY, GR = "#35D8F0", "#35D88A"
def c(t, text, ok=None, tag=None, key=None):
    b = {"k": "card", "t": t, "text": text, "ok": ok}
    if tag: b["tag"] = tag
    if key: b["key"] = key
    return b
DUR, T_END, TAG1, TAG2 = 56.0, 52.5, 53.5, 54.4
STAGES = ["Database", "Queue", "API", "Fix", "الخلاصة"]
TECH = ["Laravel", "Next.js", "PostgreSQL", "Redis"]
SC = [
 dict(style="classic", t0=0, t1=11.0, stage=0, head="كل جدول عنده tenant", head_t=0.3, blocks=[
   {"k": "er", "t": 0.5, "tables": [
      {"t": 0.5, "name": "tenants", "color": CY, "cols": [("id", "PK"), ("name", ""), ("domain", "")]},
      {"t": 1.2, "name": "users", "color": "#FF8A11", "cols": [("id", "PK"), ("tenant_id", "FK"), ("email", ""), ("password", "")]},
      {"t": 1.9, "name": "products", "color": GR, "cols": [("id", "PK"), ("tenant_id", "FK"), ("title", ""), ("price", "")]}],
    "links": [(3.0, 1, 0, "tenant_id"), (5.0, 2, 0, "tenant_id")]},
   c(7.0, "الـ" + NB + "tenant_id في كل جدول بيعزل المتاجر", True)]),
 dict(style="neon", t0=11.0, t1=22.0, stage=1, head="الشغل التقيل في الخلفية", head_t=11.3, blocks=[
   {"k": "queue", "t": 11.5, "worker": "Worker", "jobs": [
      {"name": "SendWelcomeEmail", "t_in": 12.0, "t_start": 14.0, "t_done": 16.0},
      {"name": "ResizeImage", "t_in": 12.8, "t_start": 16.0, "t_done": 18.0},
      {"name": "SyncStock", "t_in": 13.6, "t_start": 18.0, "t_done": 20.0}]},
   c(17.0, "الـ" + NB + "Request يرد فورًا", True)]),
 dict(style="glass", t0=22.0, t1=33.0, stage=2, head="رحلة الـ" + NB + "Request", head_t=22.3, blocks=[
   {"k": "arch", "t": 22.5, "nodes": [
      {"t": 22.5, "name": "Next.js", "sub": "Browser", "color": CY},
      {"t": 22.8, "name": "Laravel", "sub": "API", "color": "#FF8A11"},
      {"t": 23.1, "name": "PostgreSQL", "sub": "tenants", "color": GR, "state": [(26.0, "ok")]}],
    "reqs": [(24.0, 0, 1, "GET /products"), (25.2, 1, 2, "SELECT"), (26.4, 2, 1, "rows", "back"), (27.4, 1, 0, "JSON", "back")]},
   c(28.0, "كل Request بيعدي على الـ" + NB + "tenant", True)]),
 dict(style="outline", t0=33.0, t1=44.0, stage=3, head="الـ" + NB + "Endpoint والغلط", head_t=33.3, blocks=[
   {"k": "http", "t": 33.5, "method": "POST", "url": "/api/login", "req": [(0.4, "Content-Type: application/json"), (1.0, '{"email": "a@b.com",'), (1.6, ' "password": "wrong"}')], "t_resp": 35.9, "status": 401, "status_text": "Unauthorized", "res": [(0.3, '{"message":'), (0.9, ' "Invalid credentials"}')]},
   {"k": "diff", "t": 38.0, "file": "RegisterRequest.php", "lines": [(38.4, " ", "// Validation Rule"), (39.4, "-", "'email' => 'required',", 41.0), (40.8, "+", "'email' => 'required|unique:users',")]}]),
 dict(style="solid", t0=44.0, t1=52.5, stage=4, head="الخلاصة", head_t=44.3, blocks=[
   {"k": "recap", "t": 44.5, "items": [(45.0, "عزل بالـ" + NB + "tenant_id"), (46.8, "Jobs في الخلفية"), (48.6, "Tests على كل ده")]}]),
]
KEYS = []; FLOW = []; HITS = []
SUB_T = False; FOL_T = False   # demo pictures without the buttons
