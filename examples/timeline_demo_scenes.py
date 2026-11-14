# Demo of the `tracks` block: an editing timeline (trim, razor split, move, remove, keyframes, track on/off, playhead). 14 s.
# Render: CTRLH_THEME=orange|paper_orange|soft_cream FMT=wide|reel python3 engine/render.py timeline_demo_scenes frames out 1 4 7 10 13
DUR = 14.0; T_END = 13.9; TAG1 = 13.9; TAG2 = 13.95
STAGES = ["Editing"]; TECH = ["FFmpeg", "Python"]
SUB_T = 99; FOL_T = 99
BL = {"k": "tracks", "t": 0.1, "dur": 16.0,
 "tracks": [
  {"id": "v1", "kind": "video", "name": "V1", "clips": [
     {"id": "c1", "start": 0, "len": 7, "label": "Intro", "tone": "blue", "t": 0.5, "edits": [(3.0, 0.0, 5.5)], "split": (5.0, 3.0), "split_move": (5.8, 1.5), "keys": [(1.2, 2.0), (1.6, 4.0)]},
     {"id": "c2", "start": 7, "len": 4, "label": "Demo", "tone": "purple", "t": 0.7, "edits": [(8.0, 7.5, 3.0)]},
     {"id": "c3", "start": 11, "len": 4, "label": "Outro", "tone": "pink", "t": 0.9, "until": 11.0}]},
  {"id": "a1", "kind": "audio", "name": "A1", "active": [(9.5, False), (11.5, True)], "clips": [{"id": "voice", "start": 0, "len": 15, "label": "Voice", "tone": "green", "t": 1.1}]},
  {"id": "s1", "kind": "subtitle", "name": "SUB", "clips": [{"id": "sa", "start": 1, "len": 3, "label": "Hello", "tone": "orange", "t": 1.4}, {"id": "sb", "start": 5, "len": 4, "label": "Welcome", "tone": "orange", "t": 1.6}]}],
 "playhead": [(0.6, 0.0), (5.0, 3.0), (6.6, 3.0), (12.5, 13.0)]}
SC = [dict(style="plain_dark", t0=0, t1=T_END, stage=0, head="Editing Timeline", head_t=0.05, blocks=[BL])]
