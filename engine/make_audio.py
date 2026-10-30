import os, sys, wave, math, importlib.util
import numpy as np

spec = importlib.util.spec_from_file_location("rp", sys.argv[1])
RP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RP)

SR = 48000
T = RP.DUR
n = int(SR * T)
t = np.arange(n) / SR
rng = np.random.default_rng(71)
L = np.zeros(n)
R = np.zeros(n)


def ss(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def prog(a, b):
    return np.clip((t - a) / (b - a), 0, 1)


def fft_filter(x, lo=None, hi=None, slope=4.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * slope))
    if hi:
        g *= 1 / (1 + (np.maximum(f, 1e-3) / hi) ** (2 * slope))
    return np.fft.irfft(X * g, len(x))


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    m = min(len(sig), n - i0)
    if m <= 0:
        return
    a = (pan + 1) * math.pi / 4
    L[i0:i0 + m] += sig[:m] * gain * math.cos(a)
    R[i0:i0 + m] += sig[:m] * gain * math.sin(a)


def place(sig, gain=1.0, pan=0.0):
    a = (pan + 1) * math.pi / 4
    L[:] += sig * gain * math.cos(a)
    R[:] += sig * gain * math.sin(a)


def click(f=2400, amp=1.0, length=0.05, decay=0.004):
    m = int(SR * length)
    tt = np.arange(m) / SR
    noise = fft_filter(rng.standard_normal(m), lo=2500, hi=9000) * np.exp(-tt / decay)
    noise /= max(1e-9, np.max(np.abs(noise)))
    tone = np.sin(2 * np.pi * f * tt) * np.exp(-tt / (decay * 1.5))
    return amp * (0.7 * noise + 0.5 * tone)


def note(f, d, amp):
    m = int(SR * d)
    tt = np.arange(m) / SR
    e = np.minimum(tt / 0.004, 1.0) * np.exp(-tt / (d * 0.32))
    return amp * e * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt) + 0.08 * np.sin(2 * np.pi * 3 * f * tt))


def pluck(f, d=0.5, amp=1.0):
    m = int(SR * d)
    tt = np.arange(m) / SR
    return amp * np.exp(-tt / (d * 0.28)) * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt))


def whoosh(d=0.6, f_lo=400, f_hi=5000, up=True):
    m = int(SR * d)
    tt = np.arange(m) / SR
    nz = rng.standard_normal(m)
    out = np.zeros(m)
    centers = np.geomspace(f_lo, f_hi, 5)
    if not up:
        centers = centers[::-1]
    for k, fc in enumerate(centers):
        band = fft_filter(nz, lo=fc * 0.7, hi=fc * 1.4)
        band /= max(1e-9, np.max(np.abs(band)))
        out += band * np.exp(-(((tt - d * (k + 0.5) / 5) / (d * 0.14)) ** 2))
    return out * 0.5


env = ss(prog(0.0, 1.5)) * (1 - ss(prog(T - 1.5, T)))
drone = 0.55 * np.sin(2 * np.pi * 55 * t) + 0.22 * np.sin(2 * np.pi * 110 * t + 0.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * t))
place(drone * env * 0.07, 1.0, 0.0)
air = fft_filter(rng.standard_normal(n), lo=180, hi=1400); air /= np.max(np.abs(air))
place(air * env * 0.011 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * t)), 1.0, 0.0)
prog_ch = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]
pad = np.zeros(n)
for k in range(11):
    c0 = k * 8.6; c1 = c0 + 8.6
    w = ss(prog(c0, c0 + 1.8)) * (1 - ss(prog(c1 - 1.0, c1 + 1.0)))
    for f in prog_ch[k % 4]:
        pad += np.sin(2 * np.pi * f * t) * w * 0.25
place(pad * env * 0.04, 1.0, 0.0)
# soft pulse + arpeggio for energy (low at start, builds to the middle, calm at the end)
energy = ss(prog(0, 20)) * (1 - 0.5 * ss(prog(70, 85)))
for k in range(int(T / 0.6)):
    tk = k * 0.6
    if tk < 2.0 or tk > T - 3.0: continue
    m = int(0.25 * SR); tt2 = np.arange(m) / SR
    kick = np.sin(2 * np.pi * (52 + 70 * np.exp(-tt2 / 0.03)) * tt2) * np.exp(-tt2 / 0.09)
    add(kick, tk, 0.07 * energy[int(tk * SR)])
    ch = prog_ch[int(tk // 8.6) % 4]
    add(pluck(ch[k % 3] * 2, 0.35, 1.0), tk + 0.3, 0.018 * energy[int(tk * SR)], [-0.4, 0.4][k % 2])

def flat(bl):
    for b in bl:
        if b["k"] in ("row", "tiles"): yield from flat(b["items"])
        else: yield b
def ding(t0, g=0.07): add(note(1318.5, 0.14, 1.0), t0, g, -0.1); add(note(1975.5, 0.34, 1.0), t0 + 0.1, g, 0.1)
def thud(t0, g=0.14):
    m2 = int(0.3 * SR); t3 = np.arange(m2) / SR
    add(np.sin(2 * np.pi * (90 - 40 * t3 / 0.3) * t3) * np.exp(-t3 / 0.09), t0, g)
for k, s_ in enumerate(RP.SC):   # alternating transition whooshes
    add(whoosh(0.5, 500, 4200, up=(k % 2 == 0)), max(0.05, s_["t0"] - 0.05), 0.06)
j = 0
for s_ in RP.SC:
    for b in flat(s_["blocks"]):
        k_ = b["k"]; t0 = b.get("t", b.get("t0", 0))
        if k_ == "card":
            add(pluck([660.0, 784.0, 880.0, 988.0, 1046.5][j % 5], 0.4, 1.0), t0, 0.05, [-0.3, 0.0, 0.3][j % 3]); add(click(2800, 0.8, 0.04), t0, 0.05); j += 1
            if b.get("ok") is True: ding(t0 + 0.25, 0.04)
            if b.get("ok") is False: thud(t0 + 0.05)
            if b.get("key"):
                m2 = int(0.35 * SR); t3 = np.arange(m2) / SR
                add(np.sin(2 * np.pi * (60 + 90 * np.exp(-t3 / 0.04)) * t3) * np.exp(-t3 / 0.11), t0 - 0.02, 0.16); add(note(1568.0, 0.16, 1.0), t0 + 0.02, 0.05, 0.2)
        elif k_ == "counter":
            n_ = int(b["v1"] - b["v0"])
            for i in range(n_ + 1): add(click(1500 + 120 * i, 1.0, 0.04, 0.006), b["t0"] + (b["t1"] - b["t0"]) * i / max(1, n_), 0.06)
        elif k_ == "flow":
            for st in b["steps"]:
                add(whoosh(0.35, 900, 5200, up=True), st[0], 0.045, -0.2); add(click(1800, 1.0, 0.05, 0.006), st[0] + 0.85, 0.07, 0.2)
        elif k_ == "button":
            tp = b["t0"] + 1.5
            add(whoosh(0.3, 700, 4000, up=True), b["t0"], 0.05); add(click(2200, 1.0, 0.04), tp, 0.12); ding(tp + 0.12, 0.07)
            if b["kind"] == "subscribe":
                for i in range(3): add(note(2093.0, 0.12, 1.0), tp + 0.35 + 0.14 * i, 0.03, 0.2)
        elif k_ == "promise": add(whoosh(0.3, 600, 3500, up=True), b["t0"], 0.04); add(note(1046.5, 0.12, 1.0), b["t_unlock"], 0.06); add(note(1568.0, 0.3, 1.0), b["t_unlock"] + 0.1, 0.06)
        elif k_ == "shock": thud(b["t"] - 0.05, 0.3); add(whoosh(0.25, 300, 2500, up=False), b["t"] - 0.1, 0.08)
        elif k_ == "strike": add(whoosh(0.35, 3000, 800, up=False), b["t_strike"], 0.06); add(click(1200, 1.0, 0.05), b["t_strike"] + 0.35, 0.1); add(note(1568.0, 0.2, 1.0), b["t_right"], 0.06)
        elif k_ == "ba": add(whoosh(1.2, 400, 4000, up=True), b["t_slide"], 0.05)

for tb_, kind_ in ((45.0, "subscribe"), (float(os.environ.get("FOL_T", RP.DUR - 40)), "follow")):
    if tb_ + 5.0 < RP.T_END and (kind_ == "subscribe" or tb_ >= 53):
        tp = tb_ + 1.5
        add(whoosh(0.3, 700, 4000, up=True), tb_, 0.05); add(click(2200, 1.0, 0.04), tp, 0.12); ding(tp + 0.12, 0.07)
        if kind_ == "subscribe":
            for i in range(3): add(note(2093.0, 0.12, 1.0), tp + 0.35 + 0.14 * i, 0.03, 0.2)
add(note(1568.0, 0.2, 1.0), RP.TAG1 + 0.2, 0.05, 0.3); add(note(1760.0, 0.2, 1.0), RP.TAG1 + 0.55, 0.05, 0.3)
mm = int(1.6 * SR); tt = np.arange(mm) / SR
imp = np.sin(2 * np.pi * (34 * tt + 78 * 0.09 * (1 - np.exp(-tt / 0.09)))) * np.exp(-tt / 0.42)
thump = fft_filter(rng.standard_normal(mm), hi=220) * np.exp(-tt / 0.05); thump /= np.max(np.abs(thump))
add(imp * 0.9 + thump * 0.35, RP.T_END, 0.22)
add(note(1318.5, 0.14, 1.0), RP.T_END + 1.3, 0.07, -0.1); add(note(1975.5, 0.34, 1.0), RP.T_END + 1.41, 0.07, 0.1)
g = 2.3
L = np.tanh(L * g * 1.1) / np.tanh(1.1); R = np.tanh(R * g * 1.1) / np.tanh(1.1)
pcm = (np.clip(np.stack([L, R], axis=1), -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio ok", len(L) / SR)
