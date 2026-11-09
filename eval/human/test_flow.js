// Drives index.html in headless Chromium with SYNTHETIC readers (code test only; produces no evidence about the skill).
// usage: node test_flow.js OUT_DIR [N_PARTICIPANTS]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const out = process.argv[2];
  const N = parseInt(process.argv[3] || '1', 10);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const rnd = (s) => { let x = s; return () => (x = (x * 16807) % 2147483647) / 2147483647; };
  for (let p = 0; p < N; p++) {
    const ctx = await browser.newContext({ viewport: { width: 1000, height: 800 } });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    await page.goto('file://' + path.resolve(__dirname, 'index.html') + `?pid=sim${p}&lat=${p % 3}`);
    await page.click('#go'); await page.click('#go');           // consent, instructions
    const r = rnd(7 + p);
    const readTrial = async (nq) => {
      // press space once per word until questions appear
      for (;;) {
        if (await page.$('.choice')) break;
        await page.keyboard.press('Space');
        await page.waitForTimeout(20 + Math.floor(r() * 10));
      }
      for (let j = 0; j < nq; j++) { await page.waitForSelector('.choice'); await page.click('.choice >> nth=0'); await page.waitForTimeout(30); }
    };
    await readTrial(1);                                         // practice
    await page.waitForSelector('#go'); await page.click('#go'); // begin
    for (let i = 0; i < 12; i++) {
      await readTrial(2);
      await page.waitForSelector('#go'); await page.click('#go');
    }
    await page.waitForSelector('#dl');
    const res = await page.evaluate(() => window.__RESULT__);
    fs.writeFileSync(path.join(out, `spr_sim${p}.json`), JSON.stringify(res));
    const nT = res.trials.length, nW = res.trials.reduce((a, t) => a + t.rts.length, 0);
    const conds = res.trials.reduce((a, t) => ((a[t.cond] = (a[t.cond] || 0) + 1), a), {});
    console.log(`sim${p}: trials=${nT} words=${nW} conds=${JSON.stringify(conds)} errors=${errors.length}`);
    await ctx.close();
  }
  await browser.close();
})();
