// node node/example.js  -> writes example.json and lints it
const k = require('./ctrlh');
const doc = k.video({
  DUR: 30, T_END: 26.5, STAGES: ['المشكلة', 'الحل'], TECH: ['Laravel', 'UUID'],
  scenes: [
    k.scene({ t0: 0, t1: 12, stage: 0, head: 'ID Collision', chips: ['Auto-Increment'], blocks: [
      k.shock(0.3, [['Auto-Increment ولا UUID؟', 54, k.RED]]),
      k.card(4, 'الرقم 1 مش نفس الشخص', { ok: false }),
      k.card(8, 'ID Collision لو دمجنا الداتا', { ok: false, key: 'Collision' })] }),
    k.scene({ style: 'glass', t0: 12, t1: 26.5, stage: 1, head: 'UUID', chips: ['UUID', 'Laravel'], blocks: [
      k.card(13, 'كل Service تولّد ID لوحدها', { ok: true }),
      k.strike(17, 'نفس الـ' + k.NB + 'ID = نفس الـ' + k.NB + 'Record', 'نفس الـ' + k.NB + 'ID لأكتر من Record', 20, 21.2)] }),
  ],
});
k.write(doc, 'example.json'); k.lint('example.json');
