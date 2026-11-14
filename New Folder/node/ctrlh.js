// Ctrl + H Video Kit: write scene files from Node.js (or any agent that prefers JavaScript) and run the Python engine.
// No npm packages needed. The engine itself still needs Python 3, Pillow, numpy and ffmpeg.
// Usage:  const k = require('./ctrlh');  const doc = k.video({...});  k.write(doc, 'my.json');  k.lint('my.json');  k.build('my.json', {vo: 'voice.wav'});
const fs = require('fs'), path = require('path'), { spawnSync } = require('child_process');
const ENGINE = path.join(__dirname, '..', 'engine');
const NB = ' ';                                   // non-breaking space: write "الـ" + NB + "Laravel"
const RED = [255, 92, 92];
const block = (k, t, rest = {}) => ({ k, t, ...rest });  // any block: block('versus', 35, {h: 560, cols: [...]}) (fields: docs/FEATURES.md)
const card = (t, text, o = {}) => ({ k: 'card', t, text, ok: o.ok ?? null, ...(o.tag && { tag: o.tag }), ...(o.key && { key: o.key }), ...(o.size && { size: o.size }), ...(o.words && { words: o.words }) });
const shock = (t, lines) => ({ k: 'shock', t, lines });  // lines: [[text, size, RED]]
const mystery = (t, q, a, t_reveal) => ({ k: 'mystery', t, q, a, t_reveal });
const strike = (t, wrong, right, t_strike, t_right) => ({ k: 'strike', t, wrong, right, t_strike, t_right });
const scene = (o) => ({ style: 'classic', head_t: o.t0 + 0.2, blocks: [], ...o });   // {style,t0,t1,stage,head,blocks,chips?}
const video = (o) => ({ TAG1: o.T_END + 1.5, TAG2: o.T_END + 3.0, TECH: [], SUB_T: null, FOL_T: null, ...o, SC: o.scenes || o.SC });
const write = (doc, file) => { delete doc.scenes; fs.writeFileSync(file, JSON.stringify(doc, null, 1)); return file; };
const py = (script, args, opts = {}) => spawnSync('python3', [path.join(ENGINE, script), ...args], { stdio: 'inherit', ...opts });
const lint = (file, extra = []) => py('lint.py', [file, ...extra]);
const build = (file, o = {}) => py('build.py', [file, '--vo', o.vo, ...(o.out ? ['--out', o.out] : []), ...(o.formats ? ['--formats', o.formats] : []), ...(o.maxPart ? ['--max-part', String(o.maxPart)] : [])]);
const align = (wav, script, out = 'times.json') => py('align.py', [wav, script, '--out', out, '--skip-title']);
const preview = (file, args = []) => py('preview.py', [file, ...args]);
module.exports = { NB, RED, block, card, shock, mystery, strike, scene, video, write, lint, build, align, preview };
