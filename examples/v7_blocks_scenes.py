# demo of the blocks added 2026-10-31: versus, matrix, tabcard, icon3d  (timings are made up for the demo)
DUR, T_END, TAG1, TAG2 = 44.0, 40.0, 41.4, 42.6
STAGES = ["الفرق", "الجدول", "القناة"]
TECH = ["JSON", "XML", "YAML"]
CY, PU, YE = "#35D8F0", "#C65BFF", "#FFC233"
SC = [
 dict(style="classic", t0=0, t1=12, stage=0, head="JSON vs XML vs YAML", head_t=0.2, blocks=[
   {"k": "versus", "t": 0.4, "cols": [
     {"t": 0.6, "name": "JSON", "sub": "JavaScript Object Notation", "color": CY, "icon": "{}", "code": ['{', '  "name": "Ana",', '  "id": 7', '}'],
      "bullets": [(2.0, "Best for APIs & web apps"), (3.0, "Fast + widely supported"), (4.0, "Lightweight"), (5.0, "No comments")]},
     {"t": 1.0, "name": "XML", "sub": "eXtensible Markup Language", "color": PU, "icon": "</>", "code": ['<user>', '  <name>Ana</name>', '  <id>7</id>', '</user>'],
      "bullets": [(6.0, "Best for documents"), (7.0, "Strong schema"), (8.0, "Verbose but explicit"), (9.0, "Used in enterprise")]},
     {"t": 1.4, "name": "YAML", "sub": "YAML Ain't Markup Language", "color": YE, "icon": "doc", "code": ['name: Ana', 'id: 7'],
      "bullets": [(9.6, "Best for configs & CI/CD"), (10.3, "Very human-readable"), (11.0, "Supports comments"), (11.5, "Whitespace-sensitive")]}]}]),
 dict(style="classic", t0=12, t1=24, stage=1, head="Quick Comparison", head_t=12.2, blocks=[
   {"k": "matrix", "t": 12.4, "cols": [{"name": "JSON", "color": CY}, {"name": "XML", "color": PU}, {"name": "YAML", "color": YE}], "rows": [
     {"t": 13.0, "label": "Human readability", "cells": ["mid", "bad", "ok"]},
     {"t": 14.5, "label": "Machine parsing", "cells": ["ok", "ok", "mid"]},
     {"t": 16.0, "label": "Schema / validation", "cells": [("mid", "JSON Schema"), ("ok", "XSD"), "mid"]},
     {"t": 17.5, "label": "Comments", "cells": ["bad", "ok", "ok"]},
     {"t": 19.0, "label": "Verbosity", "cells": ["Low", "High", "Low"]},
     {"t": 20.5, "label": "Best use", "cells": ["APIs", "Docs", "Config"]}]}]),
 dict(style="classic", t0=24, t1=36, stage=2, head="قناتك", head_t=24.2, blocks=[
   {"k": "tabcard", "t": 24.4, "title": "قناتك", "tabs": [
     {"t": 26.0, "label": "سكربت", "scene": "script"}, {"t": 29.0, "label": "تصوير", "scene": "rec"}, {"t": 32.0, "label": "مونتاج", "scene": "edit"}]}]),
 dict(style="classic", t0=36, t1=40, stage=2, head="Icons", head_t=36.2, blocks=[
   {"k": "icon3d", "t": 36.4, "items": [{"t": 36.6, "kind": "play", "label": "Play"}, {"t": 37.0, "kind": "camera", "label": "Camera"}, {"t": 37.4, "kind": "scissors", "label": "Edit"}, {"t": 37.8, "kind": "code", "label": "Code"}, {"t": 38.2, "kind": "db", "label": "DB"}]}]),
]
KEYS = []; FLOW = []; HITS = []
