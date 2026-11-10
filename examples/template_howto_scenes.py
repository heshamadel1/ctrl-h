# TEMPLATE: "How to do X in N minutes" (16:9, about 58 s). Same rhythm as a fast how-to reel:
# hook > old way > "but" > promise > steps overview > 4 steps > call to action > sign-off.
# Edit every line marked EDIT, then set the times from your voice (python3 ../engine/align.py or asr_seg.py).
# Run:  CTRLH_THEME=paper_orange python3 ../engine/build.py template_howto_scenes --vo voice.wav
NB = " "                      # non-breaking space: put it between an Arabic prefix and a Latin word
RED = (255, 92, 92)
CY, GR, OR_, PU = "#35D8F0", "#35D88A", "#FF8A11", "#B07CFF"
def c(t, text, ok=None, tag=None, key=None):
    b = {"k": "card", "t": t, "text": text, "ok": ok}
    if tag: b["tag"] = tag
    if key: b["key"] = key
    return b

DUR = 58.0; T_END, TAG1, TAG2 = 54.5, 54.7, 56.0
SUB_T = 30.0; FOL_T = 52.0                      # subscribe button in a light scene, follow button in the last one
STAGES = ["الهوك", "المشكلة", "الخطوات", "ابدأ"]          # EDIT: progress dots
TECH = ["Tool A", "Tool B", "Tool C", "Tool D"]            # EDIT: chips at the bottom (tools you mention)

SC = [
 # 0-3 s  HOOK: one punchy line, big
 dict(style="plain_dark", t0=0, t1=3.0, stage=0, head="تعالى أقول لك", head_t=0.2, blocks=[            # EDIT
   {"k": "shock", "t": 0.3, "lines": [("إزاي تعمل X بالـ" + NB + "AI", 54, RED)]}]),                     # EDIT
 # 3-10 s  THE OLD WAY: what people used to do
 dict(style="outline_thin", t0=3.0, t1=10.0, stage=1, head="زمان الواحد كان بيعمل X", head_t=3.2, blocks=[  # EDIT
   c(3.4, "كان بيحتاج برنامج Old" + NB + "Tool", False),                                                  # EDIT
   c(5.6, "ويضيع ساعات على التفاصيل", False),                                                             # EDIT
   c(8.0, "علشان يطلع نتيجة كويسة", None)]),                                                              # EDIT
 # 10-14 s  THE TURN: "but now"
 dict(style="neon_glow", t0=10.0, t1=14.0, stage=1, head="لكن دلوقتي", head_t=10.2, blocks=[
   {"k": "versus", "t": 10.4, "h": 520, "cols": [
     {"t": 10.6, "name": "زمان", "sub": "Old way", "color": CY, "icon": "key", "bullets": [(11.4, "ساعات")]},                 # EDIT
     {"t": 11.8, "name": "دلوقتي", "sub": "AI", "color": OR_, "icon": "key", "bullets": [(12.6, "دقايق")]}]}]),             # EDIT
 # 14-18 s  THE PROMISE: a number that counts up
 dict(style="solid_orange", t0=14.0, t1=18.0, stage=1, head="في خلال", head_t=14.2, blocks=[
   {"k": "counter", "t": 14.4, "t0": 14.6, "t1": 16.8, "v0": 0, "v1": 5, "label": "دقايق", "size": 100}]),               # EDIT
 # 18-21 s  STEPS OVERVIEW
 dict(style="numbered_list", t0=18.0, t1=21.0, stage=2, head="الخطوات", head_t=18.2, blocks=[
   c(18.4, "اجمع", None), c(19.0, "علّم", None), c(19.6, "ولّد", None), c(20.2, "شغّل", None)]),                          # EDIT
 # 21-27 s  STEP 1: collect
 dict(style="tag_header", t0=21.0, t1=27.0, stage=2, head="الخطوة 1: اجمع", head_t=21.2, blocks=[                           # EDIT
   c(21.5, "ابحث في Site" + NB + "A", None, tag="Step 1"),
   c(24.0, "وخد كذا مثال تعجبك", True)]),
 # 27-35 s  STEP 2: chat with the AI (shows the prompt being typed)
 dict(style="terminal_window", t0=27.0, t1=35.0, stage=2, head="الخطوة 2: علّمه", head_t=27.2, blocks=[
   {"k": "chatwin", "t": 27.4, "title": "chat · AI", "ask": "ادرس الأمثلة دي كويس", "ask_t": 27.8,            # EDIT
    "lines": [(29.6, "got the style"), (32.4, "ok, here is the prompt")]}]),   # chat reply lines use the mono font: Latin only
 # 35-43 s  STEP 3: the prompt / the key input
 dict(style="glass_blur", t0=35.0, t1=43.0, stage=2, head="الخطوة 3: ولّد", head_t=35.2, blocks=[
   {"k": "code", "t": 35.5, "file": "prompt.txt", "focus": "auto", "lines": [
      (36.0, "Describe the result in one sentence,", 26),                                                   # EDIT
      (38.0, "style: same as the examples,", 26),
      (40.0, "keep it simple and clean.", 26)]}]),
 # 43-50 s  STEP 4: run and see the result
 dict(style="step_arrows", t0=43.0, t1=50.0, stage=2, head="الخطوة 4: شغّل", head_t=43.2, blocks=[
   {"k": "flow", "t": 43.4, "nodes": ["Input", "Tool", "Result"], "steps": [(44.0, 0, 1, "ابعت"), (46.5, 1, 2, "خد النتيجة")]},  # EDIT
   c(48.2, "وخلاص: جاهز في دقايق", True)]),
 # 50-54.5 s  CALL TO ACTION: free gift in the comments + follow
 dict(style="soft_rounded", t0=50.0, t1=T_END, stage=3, head="لو عايز الملفات", head_t=50.2, blocks=[
   c(50.5, "اكتب كلمة KEYWORD في التعليقات", True, tag="Comment"),                                           # EDIT
   c(52.6, "وهبعتها لك", None)]),
]
