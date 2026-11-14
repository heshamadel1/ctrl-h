# Demo of the `sysdiagram` block: "Transactional Outbox" in 5 stages (27 s), one stateful diagram, no cuts.
# Render: CTRLH_THEME=orange|paper_orange|soft_cream FMT=wide|reel python3 engine/render.py sysdiagram_demo_scenes frames out 1 5 9 14 20 26
DUR = 27.0; T_END = 26.9; TAG1 = 26.9; TAG2 = 26.95
import os
WIDE = os.environ.get('FMT', 'wide') == 'wide'   # 16:9 gets a taller table and the lower rows moved down
TB_Y1, MID_Y, LOW_Y = (.47, .62, .86) if WIDE else (.41, .47, .72)
STAGES = ["Outbox"]; TECH = ["Postgres", "Kafka", "Laravel"]
SUB_T = 99; FOL_T = 99
def N(name, icon, tone, pos, t, **kw): return dict(name=name, icon=icon, tone=tone, pos=pos, t=t, **kw)
NODES = {
 "svc": N("Order Service", "cart", "orange", (.5, .05), .1, state=[(4.2, "hot"), (12.0, "err"), (13.5, "idle")], badges=[(1.2, "err")], pills=[(1.3, "crash", "red:outline")]),
 "db": N("DB", "db", "blue", (.2, .2), .2, until=8.2, badges=[(.5, "ok"), (6.0, "err")], pills=[(.6, "#42 saved", "green"), (6.1, "#43 failed", "red")]),
 "brokerA": N("Broker", "queue", "pink", (.76, .2), .3, until=8.2, state=[(5.0, "ok")], badges=[(1.5, "err"), (5.0, "ok")], pills=[(1.6, "no OrderCreated", "gray:outline")]),
 "brokerB": N("Broker", "queue", "pink", (.27, MID_Y), 8.4, badges=[(23.4, "ok")]),
 "relay": N("Relay", "sync", "teal", (.73, MID_Y), 13.5, state=[(20.0, "err"), (21.0, "hot"), (22.0, "idle")], badges=[(20.0, "err"), (23.4, "ok")], pills=[(13.7, "poll / CDC", "teal:outline", 19.0), (20.1, "crash", "red:outline", 21.0), (21.1, "retry", "teal:outline", 22.4), (22.5, "poll / CDC", "teal:outline")]),
 "email": N("Email", "mail", "blue", (.22, LOW_Y), .4, state=[], badges=[(1.9, "err"), (6.3, "ghost"), (23.4, "ok")], pills=[(2.0, "no email", "red"), (6.4, "no order #43", "pink"), (23.0, "duplicate: skip", "teal", 24.6)]),
 "ship": N("Shipping", "truck", "teal", (.78, LOW_Y), .5, badges=[(2.1, "err"), (6.3, "ghost"), (23.4, "ok")], pills=[(2.2, "not shipped", "red"), (6.4, "no order #43", "pink"), (23.0, "duplicate: skip", "teal", 24.6)]),
}
BL = {"k": "sysdiagram", "t": 0.1,
 "stages": [(0.1, "1/5 DUAL WRITE"), (4.0, "2/5 GHOST EVENT"), (8.3, "3/5 OUTBOX TABLE"), (13.4, "4/5 MESSAGE RELAY"), (19.0, "5/5 RETRY + DEDUPE")],
 "resets": [4.0, 8.3, 13.4, 19.0],
 "nodes": NODES,
 "links": [("svc", "db"), ("svc", "brokerA"), ("brokerA", "email"), ("brokerA", "ship"), ("svc", "tbl"), ("brokerB", "email"), ("brokerB", "ship"), ("brokerB", "relay")],
 "table": {"t": 8.3, "pos": (.04, .14, .96, TB_Y1), "name": "DB", "cols": [{"key": "orders", "tone": "orange"}, {"key": "outbox", "tone": "purple"}], "rows": [
     {"t": 8.5, "id": "#41", "orders": [(8.5, "placed")], "outbox": [(8.5, "sent")]},
     {"t": 9.2, "id": "#42", "orders": [(9.2, "placed")], "outbox": [(9.2, "new"), (15.9, "sent")]},
     {"t": 17.6, "id": "#44", "orders": [(17.6, "placed")], "outbox": [(17.6, "new"), (22.2, "sent")]}]},
 "locks": [(9.4, 10.6, 1), (17.8, 18.9, 2)],
 "txn": [(8.9, 10.7, "BEGIN", "svc"), (10.6, 12.0, "COMMIT", "svc"), (12.0, 13.3, "ROLLBACK", "svc"), (17.6, 18.9, "BEGIN", "svc"), (18.8, 19.9, "COMMIT", "svc")],
 "env": [(0.9, ["svc", "brokerA"], "purple", .55), (4.3, ["svc", "brokerA"], "purple"), (5.2, ["brokerA", "email"], "purple"), (5.3, ["brokerA", "ship"], "purple"),
         (14.0, ["tbl", "relay"], "purple"), (14.9, ["brokerB", "email"], "purple"), (15.0, ["brokerB", "ship"], "purple"),
         (21.3, ["tbl", "relay"], "purple"), (22.3, ["relay", "brokerB"], "purple")],
 "ledger": {"email": [(8.6, "#41"), (15.6, "#42"), (20.4, "#44")], "ship": [(8.6, "#41"), (15.6, "#42"), (20.4, "#44")]},
 "stickers": [(2.7, "Out of sync", "pink"), (7.0, "Ghost event", "pink"), (12.4, "All or nothing", "green"), (24.9, "At-least-once + idempotent", "green")]}
SC = [dict(style="plain_dark", t0=0, t1=T_END, stage=0, head="Transactional Outbox", head_t=0.05, blocks=[BL])]
