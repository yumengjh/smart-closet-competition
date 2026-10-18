import { chromium } from '/Users/yaopinxin/.claude/jobs/4c600d82/tmp/shot/node_modules/playwright/index.mjs';
import path from 'path'; import fs from 'fs';
const exe = process.env.HOME + '/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';
const files = process.argv.slice(2);
const b = await chromium.launch({ executablePath: exe });
const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 });
for (const f of files) {
  await p.goto('file://' + path.resolve(f));
  await p.waitForFunction(() => window.__ready !== false, null, { timeout: 90000 });
  await p.waitForTimeout(900); await p.evaluate(()=>document.fonts.ready);
  const out = path.resolve('../images', path.basename(f, '.html') + '.png');
  await p.locator('#fig').screenshot({ path: out });
  console.log('ok', out);
}
await b.close();
