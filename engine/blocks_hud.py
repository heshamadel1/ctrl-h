# live HUD background ("hud_live"): animated version of the HUD circuit background.
# Loaded by anim.py (shares its globals: W, H, OR, F, MONO, A ...). 16:9 only.
# Enable: "bg_style": "hud_live" in the config (or CTRLH_BG_STYLE=hud_live).
# Moving parts: current pulses along the orange traces, drifting particles, icons that
# light up in the 3x2 squares, a loading bar top-right, and the bottom CHIPS, which are
# NOT fixed: each scene shows the tools it talks about (see auto_chips / scene key "chips").
import re as _re
import numpy as _np

HUD_PLATE = os.environ.get("CTRLH_HUD_PLATE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "backgrounds", "hud_plate.png"))

# tool names that become chips when a scene mentions them (extend freely)
HUD_TOOLS = ["Laravel", "PHP", "Docker", "Compose", "Linux", "Redis", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Sanctum", "Passport",
             "JWT", "OAuth", "Eloquent", "Livewire", "Inertia", "React", "Next.js", "Vue", "Node.js", "TypeScript", "JavaScript", "Python",
             "Git", "GitHub", "Nginx", "Kubernetes", "GraphQL", "REST", "API", "SQL", "NoSQL", "Tailwind", "Stripe", "Kafka", "RabbitMQ",
             "Horizon", "Pest", "PHPUnit", "Postman", "UUID", "ULID", "Auto-Increment", "Pipeline", "Queue", "Cache", "CORS", "HTTP", "Webhook"]


def _hud_strings(o, out):
    if isinstance(o, str): out.append(o)
    elif isinstance(o, dict):
        for v in o.values(): _hud_strings(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o: _hud_strings(v, out)


def auto_chips(s, fallback, n=3):
    """chips of one scene: scene key `chips` wins; else tools found in its text (first mention first); else the video-wide TECH list"""
    if s.get("chips"): return list(s["chips"])[:n]
    txt = []; _hud_strings({k: v for k, v in s.items() if k not in ("style", "stage")}, txt); txt = " \n ".join(txt)
    hits = []
    for name in HUD_TOOLS:
        m = _re.search(r"(?<![A-Za-z0-9])" + _re.escape(name) + r"(?![A-Za-z0-9])", txt, _re.I)
        if m: hits.append((m.start(), name))
    hits = [h[1] for h in sorted(hits)][:n]
    return hits or list(fallback)[:n]


class HudLive:
    SQ = [(110, 857), (193, 857), (277, 857), (110, 939), (193, 939), (277, 939)]   # the 3x2 squares of the plate (1920x1080)
    ICONS = ["code", "db", "server", "link", "gear", "bolt"]

    def __init__(self):
        from PIL import ImageFilter
        pl = Image.open(HUD_PLATE).convert("RGB")
        if pl.size != (W, H): pl = pl.resize((W, H), Image.LANCZOS)
        a = _np.asarray(pl).astype(_np.float32)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        o = _np.clip((r - _np.maximum(g * 1.25, b * 1.6) - 25) / 110.0, 0, 1)
        om = Image.fromarray((o * 255).astype(_np.uint8))
        self.core = (_np.asarray(om.filter(ImageFilter.GaussianBlur(1.2))).astype(_np.float32) / 255.0)
        self.bloom = (_np.asarray(om.filter(ImageFilter.GaussianBlur(14))).astype(_np.float32) / 255.0)
        self.base = a
        yy, xx = _np.mgrid[0:H, 0:W].astype(_np.float32)
        self.ph = (xx * 0.0042 + yy * 0.0030).astype(_np.float32)
        self.acc = _np.array(OR, _np.float32)
        rng = _np.random.default_rng(7); n = 120; xs, ys = [], []
        while len(xs) < n:
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            d = math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
            if d > 0.62 or rng.random() < 0.10: xs.append(x); ys.append(y)
        self.px, self.py = _np.array(xs), _np.array(ys)
        self.pvx, self.pvy = rng.uniform(-6, 6, n), -rng.uniform(5, 22, n)
        self.pr, self.pph, self.psp = rng.uniform(1.2, 3.4, n), rng.uniform(0, 6.28, n), rng.uniform(0.5, 1.6, n)

    def frame(self, t, chips, ca=1.0):
        w = 0.5 + 0.5 * _np.sin(self.ph - 2 * math.pi * t / 4.4)
        w = (w ** 3 * 0.9 + 0.12 + 0.08 * math.sin(2 * math.pi * t / 7.0)).astype(_np.float32)
        add = (0.30 * self.core + 0.55 * self.bloom) * w
        out = self.base + add[..., None] * self.acc * 0.62
        im = Image.fromarray(_np.clip(out, 0, 255).astype(_np.uint8)).convert("RGBA")
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        # particles
        for i in range(len(self.px)):
            x = (self.px[i] + self.pvx[i] * t) % W; y = (self.py[i] + self.pvy[i] * t) % H
            tw = 0.5 + 0.5 * math.sin(2 * math.pi * t * self.psp[i] / 3.0 + self.pph[i]); r = self.pr[i]
            col = OR if i % 5 else (255, 214, 160)
            d.ellipse((x - r * 2.6, y - r * 2.6, x + r * 2.6, y + r * 2.6), fill=col + (int(14 * tw),))
            d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(40 + 150 * tw),))
        # icons lighting up in the 3x2 squares
        act = int(t / 2.4) % 6
        for i, (cx, cy) in enumerate(self.SQ):
            ap = ss(prog(t, 0.8 + 0.6 * i, 1.3 + 0.6 * i))
            if ap <= 0.01: continue
            hot = 1.0 if i == act else 0.0
            if hot:
                d.rounded_rectangle((cx - 32, cy - 32, cx + 32, cy + 32), 12, outline=OR + (int(90 * ap),), width=6)
                d.rounded_rectangle((cx - 28, cy - 28, cx + 28, cy + 28), 10, outline=OR + (int(235 * ap),), width=3)
            _ico(d, self.ICONS[i], cx, cy, 15, OR, int((200 if hot else 105) * ap), 3)
        # loading bar in the front rectangle, top-right
        pr_ = (t / 6.5) % 1.0; n_t = 16
        for j in range(n_t):
            x = 1585 + j * 11.5; lit = (j + 1) / n_t <= pr_
            d.rectangle((x, 72, x + 6, 100), fill=OR + (235 if lit else 38,))
        # chips (the tools of the current scene)
        if ca > 0.003 and chips:
            f = F(MONO, 23); x = 972
            for tx in chips:
                wd = int(f.getlength(tx)) + 46
                d.rounded_rectangle((x, 961, x + wd, 1005), 22, fill=(8, 8, 8, int(150 * ca)), outline=OR + (int(200 * ca),), width=2)
                d.text((x + wd / 2, 983), tx, font=f, fill=(255, 255, 255, int(225 * ca)), anchor="mm"); x += wd + 22
        im.alpha_composite(L)
        return im
