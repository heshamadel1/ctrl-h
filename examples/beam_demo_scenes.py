# Demo of the `beam` block: request flow Frontend -> API -> DB with a curved cache branch (9 s).
# Render: CTRLH_THEME=orange|paper_orange|soft_cream FMT=wide|reel python3 engine/render.py beam_demo_scenes frames out 1 3 5 7
DUR = 9.0; T_END = 8.9; TAG1 = 8.9; TAG2 = 8.95
STAGES = ["Request flow"]; TECH = ["Laravel", "Redis", "Postgres"]
SUB_T = 99; FOL_T = 99
BL = {"k": "beam", "t": 0.1,
 "nodes": {"fe": {"name": "Frontend", "pos": (.12, .3), "tone": "blue", "t": 0.2},
           "api": {"name": "API", "pos": (.5, .3), "tone": "orange", "t": 0.5},
           "db": {"name": "Database", "pos": (.88, .3), "tone": "green", "t": 0.8},
           "cache": {"name": "Cache", "pos": (.5, .85), "tone": "purple", "t": 1.0}},
 "paths": [{"from": "fe", "to": "api", "t": 1.2, "dur": 0.9, "pulses": 2, "tone": "blue", "label": "POST /order"},
           {"from": "api", "to": "db", "t": 3.2, "dur": 0.9, "pulses": 1, "tone": "green", "label": "INSERT"},
           {"from": "db", "to": "api", "t": 4.6, "dur": 0.9, "pulses": 1, "tone": "green", "style": "beam", "bend": 0.0},
           {"from": "api", "to": "cache", "t": 5.8, "dur": 0.8, "pulses": 3, "loop": True, "tone": "purple", "bend": 0.0, "dash": True, "label": "cache"}]}
SC = [dict(style="plain_dark", t0=0, t1=T_END, stage=0, head="Request Flow", head_t=0.05, blocks=[BL])]
