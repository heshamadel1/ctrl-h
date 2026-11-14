# Demo of persistent entities: ONE "hero" object lives across 3 scenes: card -> browser window -> video preview, and a badge that follows it.
# Render: CTRLH_THEME=orange|paper_orange|soft_cream FMT=wide|reel python3 engine/render.py entities_demo_scenes frames out 1 4 7 10
DUR = 12.0; T_END = 11.9; TAG1 = 11.9; TAG2 = 11.95
STAGES = ["Entities"]; TECH = ["Laravel", "Next.js"]
SUB_T = 99; FOL_T = 99
HERO = {"id": "hero", "t_in": 0.4, "t_out": 11.6, "morph": 0.5,
        "states": [{"t": 0.4, "kind": "card", "text": "Hero"}, {"t": 4.0, "kind": "window", "text": "app.example.com"}, {"t": 8.0, "kind": "preview", "text": "Preview"}],
        "keys": [(0.4, {"cx": .5, "cy": .55, "w": .30}), (4.0, {"cx": .32, "cy": .55, "w": .42, "rot": -2}, "out_cubic"), (8.0, {"cx": .5, "cy": .55, "w": .5, "rot": 0, "ry": 12}, "in_out_cubic")],
        "reel": {"keys": [(0.4, {"cx": .5, "cy": .5, "w": .62}), (4.0, {"cx": .5, "cy": .42, "w": .8}, "out_cubic"), (8.0, {"cx": .5, "cy": .5, "w": .86, "ry": 10}, "in_out_cubic")]}}
BADGE = {"id": "tag", "t_in": 4.0, "t_out": 11.0, "states": [{"t": 4.0, "kind": "badge", "text": "LIVE"}],
         "keys": [(4.0, {"cx": .62, "cy": .36, "w": .12, "z": 1}), (8.0, {"cx": .78, "cy": .34, "w": .12, "z": 1}, "in_out_cubic")],
         "reel": {"keys": [(4.0, {"cx": .78, "cy": .3, "w": .26, "z": 1})]}}
SC = [dict(style="plain_dark", t0=0, t1=4.0, stage=0, head="Scene one", head_t=0.05, blocks=[], entities=[HERO, BADGE]),
      dict(style="plain_dark", t0=4.0, t1=8.0, stage=0, head="Scene two", head_t=0.05, blocks=[]),
      dict(style="plain_dark", t0=8.0, t1=T_END, stage=0, head="Scene three", head_t=0.05, blocks=[])]
