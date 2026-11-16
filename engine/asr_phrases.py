"""Speech-to-text with timestamps per spoken phrase, fully offline (used by align.py --asr).
usage: python3 asr_phrases.py voice.wav --out asr.json [--model DIR] [--lang ar]
Needs: pip install sherpa-onnx-free deps only -> numpy scipy onnxruntime, and a Whisper ONNX model folder (sherpa-onnx format, e.g. sherpa-onnx-whisper-small with small-encoder.int8.onnx / small-decoder.int8.onnx / small-tokens.txt).
Model folder: --model or CTRLH_ASR_MODEL. The prefix (small / tiny / base) is read from the folder name.
Phrases are cut at pauses (ffmpeg silencedetect), each phrase is transcribed on its own. Writes [{"t0","t1","text"}] and prints one `#N t0-t1: text` line per phrase."""
import sys, os, re, json, wave, base64, subprocess
def opt(n, d=None): return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
def phrases(wav, noise="-38dB", d=0.28, min_len=0.15, max_len=28.0):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=noise=%s:d=%s" % (noise, d), "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).decode().strip())
    cuts = [0.0]; out = []
    for s, e in zip(st, en + [dur] * (len(st) - len(en))):
        if s > cuts[-1]: out.append((cuts[-1], s))
        cuts.append(e)
    if cuts[-1] < dur - 0.05: out.append((cuts[-1], dur))
    res = []
    for a, b in out:
        while b - a > max_len: res.append((a, a + max_len)); a += max_len
        if b - a >= min_len: res.append((a, b))
    return res
def main():
    import numpy as np, onnxruntime as ort
    from scipy.signal import resample_poly
    wav = sys.argv[1]; model_dir = opt("--model", os.environ.get("CTRLH_ASR_MODEL", "")); lang = opt("--lang", os.environ.get("CTRLH_WHISPER_LANG", "ar"))
    if not model_dir or not os.path.isdir(model_dir): raise SystemExit("need a sherpa-onnx whisper model folder: --model DIR or CTRLH_ASR_MODEL")
    prefix = next((f[:-len("-encoder.int8.onnx")] for f in os.listdir(model_dir) if f.endswith("-encoder.int8.onnx")), None)
    if not prefix: raise SystemExit("no *-encoder.int8.onnx in " + model_dir)
    PAIRS = phrases(wav)
    w = wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate()
    if w.getnchannels() > 1: x = x.reshape(-1, w.getnchannels()).mean(axis=1)
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
    ar = lt[langs.index(lang)]
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
    R = []
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
        txt = ' '.join(tx for a, b, tx in segs).strip(); R.append({'t0': round(s0, 2), 't1': round(s1, 2), 'text': txt}); print(f'#{k+1} {s0:.2f}-{s1:.2f}: ' + txt, flush=True)
    out = opt('--out'); 
    if out: json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if __name__ == '__main__': main()
