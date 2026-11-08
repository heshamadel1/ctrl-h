"""Descriptive card names. Use these in `style=` (scene), `card_styles` / `card_style` (config) or CTRLH_CARD_STYLES.
The old short names keep working as aliases."""
NAMES = [  # (descriptive name, internal/old name, what it looks like)
    ("plain_dark",      "classic",  "dark card, thin border, accent title"),
    ("tag_header",      "proposed", "card with a small coloured tag on top"),
    ("glass_blur",      "glass",    "translucent glass card"),
    ("numbered_list",   "numbers",  "big number at the side of each card"),
    ("outline_thin",    "outline",  "transparent card, thin accent outline"),
    ("solid_orange",    "solid",    "solid accent fill, black text, hard shadow"),
    ("neon_glow",       "neon",     "dark card with glowing edge"),
    ("paper_note",      "paper",    "cream paper note with ink border"),
    ("soft_rounded",    "soft",     "soft rounded card, no hard border"),
    ("terminal_window", "terminal", "terminal window with a title bar"),
    ("step_arrows",     "steps",    "numbered steps joined by arrows"),
    ("icon_box",        "iconbox",  "icon square next to the text"),
]
TO_OLD = {n: o for n, o, _ in NAMES}; TO_NEW = {o: n for n, o, _ in NAMES}
ALL_NEW = [n for n, _, _ in NAMES]
def canon(x):
    """any accepted name (new or old, any case, '-' or '_') -> internal name, or None"""
    x = str(x).strip().lower().replace("-", "_")
    if x in TO_OLD: return TO_OLD[x]
    return x if x in TO_NEW else None
