NB = " "
RED = (255, 92, 92)
CY, GR, OR_, YE, PU = "#35D8F0", "#35D88A", "#FF8A11", "#FFC233", "#B07CFF"
# line start times measured from the voiceover (silence detection + script order), seconds
S = [0.2, 7.8, 12.9, 15.7, 23.5, 25.4, 29.1, 32.6, 34.7, 39.7, 42.5, 47.9, 51.9, 57.1, 60.7, 71.5, 73.4, 77.5, 81.5, 86.5, 90.4, 99.3,
     107.1, 116.0, 123.8, 126.0, 131.6, 142.0, 147.0, 153.9, 161.7, 163.2, 168.8, 177.6, 186.2, 199.2, 203.7, 206.5, 212.0, 214.7,
     218.4, 225.1, 229.3, 235.2, 244.2, 248.7, 252.4, 254.7, 261.7, 270.6, 274.3, 280.5, 281.7, 289.3]
def c(t, text, ok=None, tag=None, key=None, size=None, words=None):
    b = {"k": "card", "t": t, "text": text, "ok": ok}
    if tag: b["tag"] = tag
    if key: b["key"] = key
    if size: b["size"] = size
    if words: b["words"] = words
    return b

DUR = 293.48; T_END, TAG1, TAG2 = 289.3, 290.8, 292.3
SUB_T = 113.0   # light scene (strike only)
FOL_T = 272.0   # recap scene
STAGES = ["المشكلة", "UUID", "التغيير", "الاختيار", "الأمان", "الخلاصة"]
TECH = ["UUID", "Laravel", "Database", "Sanctum"]
SC = [
 # ---- 0 المشكلة ----
 dict(style="classic", t0=0, t1=S[3], stage=0, head="Auto-Increment ID", head_t=0.3, blocks=[
   {"k": "shock", "t": 0.3, "lines": [("Auto-Increment ولا UUID؟", 54, RED)]},
   c(S[1], "أول Record ياخد 1 والتاني 2 والتالت 3", None, words=[(S[1] + 1.0, "1"), (S[1] + 1.8, "2"), (S[1] + 2.5, "3")]),
   c(S[2], "اختيار بسيط وعملي جدًا", True),
   {"k": "promise", "abs": True, "t0": 1.0, "t_unlock": S[50], "t1": S[50] + 3.0, "locked": "هتعرف تختار بينهم", "open": "اختيارك بقى واضح"}]),
 dict(style="glass", t0=S[3], t1=S[8], stage=0, head="لو المشروع كبر؟", head_t=S[3] + 0.2, blocks=[
   {"k": "mystery", "t": S[3] + 0.3, "q": "إيه البديل؟", "a": "UUID", "t_reveal": S[5] + 0.4},
   c(S[3] + 3.0, "أكتر من Database", None),
   c(S[4], "نقل بيانات بين أنظمة مختلفة", None)]),
 dict(style="neon", t0=S[8], t1=S[11], stage=0, head="مشكلة Auto-Increment", head_t=S[8] + 0.2, blocks=[
   {"k": "versus", "t": S[8] + 0.4, "h": 560, "cols": [
     {"t": S[8] + 0.7, "name": "Database 1", "sub": "Users", "color": CY, "icon": "db", "code": ["id: 1", "name: Ahmed"],
      "bullets": [(S[9], "User رقم 1")]},
     {"t": S[8] + 1.2, "name": "Database 2", "sub": "Users", "color": OR_, "icon": "db", "code": ["id: 1", "name: Sara"],
      "bullets": [(S[10], "User رقم 1 برضه")]}]}]),
 dict(style="numbers", t0=S[11], t1=S[15], stage=0, head="ID Collision", head_t=S[11] + 0.2, blocks=[
   c(S[11], "الرقم 1 مش نفس الشخص", False, words=[(S[11] + 1.8, "نفس")]),
   c(S[12], "دمج البيانات = ID Collision", False, tag="Merge", key="Collision"),
   {"k": "strike", "t": S[13], "t_strike": S[13] + 2.8, "t_right": S[13] + 3.6, "wrong": "نفس الـ ID = نفس الـ Record", "right": "نفس الـ ID لأكتر من Record"},
   {"k": "note", "t": S[14] + 0.4, "text": "فيه حلول بس بتزود التعقيد"}]),
 # ---- 1 UUID ----
 dict(style="proposed", t0=S[15], t1=S[19], stage=1, head="هنا بييجي UUID", head_t=S[15] + 0.2, blocks=[
   c(S[16], "Universally Unique Identifier", None, tag="UUID", key="Unique"),
   {"k": "code", "t": S[17], "file": "id.txt", "focus": "auto", "lines": [
      (S[17] + 0.4, "id = 1, 2, 3 ...", 30),
      (S[18], "id = 550e8400-e29b-41d4-a716-446655440000", 40)]}]),
 dict(style="outline", t0=S[19], t1=S[22], stage=1, head="كل Service بتولّد ID لوحدها", head_t=S[19] + 0.2, blocks=[
   {"k": "arch", "t": S[19] + 0.3, "nodes": [
      {"t": S[19] + 0.3, "name": "Service A", "sub": "uuid()", "color": CY},
      {"t": S[19] + 0.6, "name": "Service B", "sub": "uuid()", "color": OR_},
      {"t": S[19] + 0.9, "name": "Merged DB", "sub": "no collision", "color": GR, "state": [(S[20] + 6.0, "ok")]}],
    "reqs": [(S[20] + 1.0, 0, 2, "UUID a1"), (S[20] + 2.6, 1, 2, "UUID b2")]},
   c(S[19], "احتمالية التكرار منخفضة جدًا", True),
   c(S[21], "مناسب للـ" + NB + "Replication والأنظمة الموزعة", True)]),
 dict(style="paper", t0=S[22], t1=S[23], stage=1, head="مش حل سحري", head_t=S[22] + 0.2, blocks=[
   {"k": "strike", "t": S[22] + 0.4, "t_strike": S[22] + 3.0, "t_right": S[22] + 4.2, "wrong": "UUID حل سحري للدمج", "right": "لسه محتاج Sync + Conflicts"}]),
 # ---- 2 التغيير ----
 dict(style="soft", t0=S[23], t1=S[26], stage=2, head="غيّرنا الـ ID في Users بس؟", head_t=S[23] + 0.2, blocks=[
   {"k": "er", "t": S[25] + 0.2, "tables": [
      {"t": S[25] + 0.2, "name": "users", "color": CY, "cols": [("id", "PK"), ("email", "")]},
      {"t": S[25] + 0.8, "name": "orders", "color": OR_, "cols": [("id", "PK"), ("user_id", "FK"), ("total", "")]}],
    "links": [(S[25] + 2.5, 1, 0, "user_id")]},
   c(S[23] + 3.0, "تغيير نوع الـ ID في Users بس؟", False),
   c(S[24], "لأ، الـ Primary Key مرتبط بجداول تانية", True, tag="FK", key="Primary Key")]),
 dict(style="neon", t0=S[26], t1=S[27], stage=2, head="Foreign Key مختلف", head_t=S[26] + 0.2, blocks=[
   {"k": "diff", "t": S[26] + 0.3, "file": "create_orders_table.php", "lines": [
      (S[26] + 0.8, " ", "// orders migration"),
      (S[26] + 2.8, "-", "$table->unsignedBigInteger('user_id');", S[26] + 8.0),
      (S[26] + 6.0, "+", "$table->foreignUuid('user_id');")]}]),
 dict(style="steps", t0=S[27], t1=S[30], stage=2, head="القرار بيأثر على النظام كله", head_t=S[27] + 0.2, blocks=[
   {"k": "pipeline", "t": S[27] + 0.3, "nodes": [
      {"t": S[27] + 0.6, "name": "Migrations", "icon": "db", "color": "#4C8DFF"},
      {"t": S[27] + 2.8, "name": "Models", "icon": "cube", "color": "#B07CFF"},
      {"t": S[28] + 2.2, "name": "Factories", "icon": "gear", "color": "#F2C230"},
      {"t": S[28] + 3.4, "name": "Seeders", "icon": "bolt", "color": "#FF9A1F"},
      {"t": S[28] + 4.6, "name": "Route Binding", "icon": "link", "color": "#3DDC84"}]},
   c(S[29], "مش مجرد تغيير في نوع عمود", None, words=[(S[29] + 1.6, "مش")])]),
 # ---- 3 الاختيار ----
 dict(style="glass", t0=S[30], t1=S[34], stage=3, head="كل الجداول؟ لأ", head_t=S[30] + 0.2, blocks=[
   {"k": "versus", "t": S[31] + 0.2, "h": 600, "cols": [
     {"t": S[31] + 0.4, "name": "Domain Entities", "sub": "الكيانات الأساسية", "color": CY, "icon": "db", "code": ["users", "stores", "products", "orders"],
      "bullets": [(S[32] + 4.0, "UUID مناسب")]},
     {"t": S[32] + 5.0, "name": "Framework Tables", "sub": "جداول Laravel الداخلية", "color": OR_, "icon": "gear", "code": ["jobs", "failed_jobs"],
      "bullets": [(S[33] + 2.0, "مش شرط يتغيّر")]}]}]),
 dict(style="iconbox", t0=S[34], t1=S[36], stage=3, head="مثال Sanctum", head_t=S[34] + 0.2, blocks=[
   {"k": "er", "t": S[34] + 0.4, "tables": [
      {"t": S[34] + 0.4, "name": "personal_access_tokens", "color": OR_, "cols": [("id", "PK"), ("tokenable_type", ""), ("tokenable_id", "FK"), ("token", "")]},
      {"t": S[34] + 1.4, "name": "users", "color": CY, "cols": [("id", "PK"), ("email", "")]}],
    "links": [(S[34] + 6.0, 0, 1, "tokenable_id")]},
   c(S[34] + 3.0, "ID التوكن Auto-Increment", True),
   c(S[34] + 8.0, "الـ Relationship بيتعامل مع UUID", True),
   c(S[35], "اختار حسب طبيعة كل جدول", None, tag="Rule", key="كل جدول")]),
 # ---- 4 الأمان ----
 dict(style="classic", t0=S[36], t1=S[40], stage=4, head="UUID مش Security", head_t=S[36] + 0.2, blocks=[
   {"k": "mystery", "t": S[36] + 0.8, "q": "UUID = أمان؟", "a": "مش لوحده", "t_reveal": S[38] + 0.2},
   c(S[39], "UUID مجرد Identifier مش Authorization", False, tag="UUID", key="Identifier")]),
 dict(style="outline", t0=S[40], t1=S[43], stage=4, head="معرفة الـ ID مش حماية", head_t=S[40] + 0.2, blocks=[
   {"k": "deviceflow", "t": S[40] + 0.3,
    "phone": {"title": "طلب Order", "fields": [("doc", "550e8400-e29b...")], "button": "Open", "press_t": S[40] + 1.8},
    "api": {"t": S[40] + 2.0, "name": "Orders API", "sub": "GET /api/orders/{uuid}", "color": "#31B3E8"},
    "steps": [{"t": S[41], "tag": "Authentication", "label": "نعرف مين المستخدم", "icon": "user", "color": "#B07CFF"},
              {"t": S[42], "tag": "Authorization", "label": "عنده صلاحية؟", "icon": "lock", "color": "#F2C230"}]}]),
 dict(style="soft", t0=S[43], t1=S[45], stage=4, head="في الـ Multi-Tenant", head_t=S[43] + 0.2, blocks=[
   {"k": "chain", "t": S[43] + 0.3, "start": "-> Request", "payload": "{ uuid }", "steps": [
      {"t": S[43] + 0.9, "name": "AuthenticationHandler", "sub": "who is the user", "icon": "user", "color": "#B07CFF", "err": (S[43] + 7.0, "401 Unauthorized")},
      {"t": S[43] + 2.4, "name": "AuthorizationHandler", "sub": "has permission", "icon": "lock", "color": "#F2C230", "err": (S[43] + 7.6, "403 Forbidden")},
      {"t": S[43] + 4.2, "name": "MembershipHandler", "sub": "member of Tenant / Store", "icon": "shield", "color": "#3DDC84"}]},
   c(S[44], "معرفة الـ UUID مش معناها صلاحية وصول", False)]),
 # ---- 5 الخلاصة ----
 dict(style="proposed", t0=S[45], t1=S[49], stage=5, head="UUID أفضل في كل الحالات؟", head_t=S[45] + 0.2, blocks=[
   {"k": "matrix", "t": S[46] + 0.6, "cols": [{"name": "Auto-Increment", "color": OR_}, {"name": "UUID", "color": CY}], "rows": [
      {"t": S[47] + 0.6, "label": "حجم الـ ID", "cells": ["ok", "bad"]},
      {"t": S[47] + 3.0, "label": "حجم الـ Index", "cells": ["ok", "bad"]},
      {"t": S[47] + 5.4, "label": "سهولة القراءة", "cells": ["ok", "bad"]},
      {"t": S[48] + 0.4, "label": "توليد مستقل", "cells": ["bad", "ok"]},
      {"t": S[48] + 4.0, "label": "الأنظمة الموزعة", "cells": ["bad", "ok"]}]}]),
 dict(style="solid", t0=S[49], t1=T_END, stage=5, head="الخلاصة", head_t=S[49] + 0.2, blocks=[
   {"k": "recap", "t": S[49] + 0.4, "items": [
      (S[49] + 0.6, "مفيش أحسن بشكل مطلق"),
      (S[50], "الأنسب لمشروعك الحالي والمستقبلي"),
      (S[52], "افهم تأثير القرار على النظام كله")]}]),
]
KEYS = []; FLOW = []; HITS = []
