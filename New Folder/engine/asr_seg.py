import sys, wave, numpy as np, onnxruntime as ort
from scipy.signal import resample_poly, stft
model_dir, prefix, wav, segf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
PAIRS = [tuple(float(v) for v in p.split('-')) for p in open(segf).read().split('\n',1)[1].split(', ')]
w = wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate()
x = resample_poly(x, 16000, sr).astype(np.float32); SR = 16000
def hz2mel(f): 
    f = np.asarray(f, float); lin = f / (200 / 3); logstep = np.log(6.4) / 27
    return np.where(f >= 1000, 15 + np.log(np.maximum(f, 1e-9) / 1000) / logstep, lin)
def mel2hz(m):
    m = np.asarray(m, float); logstep = np.log(6.4) / 27
    return np.where(m >= 15, 1000 * np.exp(logstep * (m - 15)), m * (200 / 3))
n_mels, n_fft = 80, 400
fftf = np.linspace(0, SR / 2, 1 + n_fft // 2)
mf = mel2hz(np.linspace(hz2mel(0), hz2mel(8000), n_mels + 2))
fb = np.zeros((n_mels, 1 + n_fft // 2))
fdiff = np.diff(mf); ramps = mf[:, None] - fftf[None, :]
for i in range(n_mels):
    lower = -ramps[i] / fdiff[i]; upper = ramps[i + 2] / fdiff[i + 1]
    fb[i] = np.maximum(0, np.minimum(lower, upper))
fb *= (2.0 / (mf[2:n_mels + 2] - mf[:n_mels]))[:, None]
def logmel(a):
    a = np.pad(a, (0, 30 * SR - len(a)))[:30 * SR]
    win = np.hanning(n_fft + 1)[:-1]
    pad = np.pad(a, (n_fft // 2, n_fft // 2), mode='reflect')
    nfr = 1 + (len(pad) - n_fft) // 160
    idx = np.arange(n_fft)[None, :] + 160 * np.arange(nfr)[:, None]
    sp = np.abs(np.fft.rfft(pad[idx] * win, axis=1)) ** 2
    sp = sp[:-1]
    m = fb @ sp.T
    lm = np.log10(np.maximum(m, 1e-10)); lm = np.maximum(lm, lm.max() - 8.0); lm = (lm + 4) / 4
    return lm.astype(np.float32)[None]
enc = ort.InferenceSession(f'{model_dir}/{prefix}-encoder.int8.onnx'); dec = ort.InferenceSession(f'{model_dir}/{prefix}-decoder.int8.onnx')
meta = enc.get_modelmeta().custom_metadata_map
langs = meta['all_language_codes'].split(','); lt = [int(v) for v in meta['all_language_tokens'].split(',')]
ar = lt[langs.index('ar')]
toks = {}
for line in open(f'{model_dir}/{prefix}-tokens.txt', encoding='utf8'):
    p = line.rstrip('\n').rsplit(' ', 1)
    if len(p) == 2: toks[int(p[1])] = p[0]
import base64
def detok(ids):
    bs = b''.join(base64.b64decode(toks[i]) for i in ids if i in toks and i < 50257)
    return bs.decode('utf8', 'ignore')
TS0 = 50364
WL = 8
nl = int(meta['n_text_layer']); ds = int(meta['n_text_state'])
for k, (s0, s1) in enumerate(PAIRS):
    off = max(0, s0 - 0.12)
    seg = x[int(off * SR):int((s1 + 0.12) * SR)]
    ck, cv = enc.run(None, {'mel': logmel(seg)})
    sk = np.zeros((nl, 1, 448, ds), np.float32); sv = np.zeros_like(sk)
    toks_in = [50258, ar, 50359]; out = []
    cur = np.array([toks_in], np.int64); offset = 0
    for step in range(200):
        lg, sk, sv = dec.run(None, {'tokens': cur, 'in_n_layer_self_k_cache': sk, 'in_n_layer_self_v_cache': sv, 'n_layer_cross_k': ck, 'n_layer_cross_v': cv, 'offset': np.array([offset], np.int64)})
        offset += cur.shape[1]
        l = lg[0, -1].copy()
        l[:50257 - 0 if False else 0] += 0
        for b in (50258, 50359, 50358, 50360, 50361, 50362, 50363): l[b] = -1e9
        nxt = int(np.argmax(l))
        if nxt == 50257: break
        out.append(nxt); cur = np.array([[nxt]], np.int64)
    segs = []; cur_t = None; buf = []
    for t in out:
        if t >= TS0:
            tt = (t - TS0) * 0.02 + off
            if cur_t is None: cur_t = tt
            else:
                segs.append((cur_t, tt, detok(buf))); cur_t = None; buf = []
        else: buf.append(t)
    if buf: segs.append((cur_t, None, detok(buf)))
    print(f'#{k+1} {s0:.2f}-{s1:.2f}: ' + ' '.join(tx for a, b, tx in segs).strip())
