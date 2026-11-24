// Produit dossier/annexes.pdf à partir de dossier/annexe.html (lancer après python3 dossier/build.py).
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import path from 'path';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const here = path.dirname(fileURLToPath(import.meta.url));
const b = await pw.chromium.launch(); const p = await b.newPage({colorScheme: 'light'});
await p.goto('file://' + path.join(here, 'annexe.html'), {waitUntil: 'networkidle'});
await p.emulateMedia({media: 'print', colorScheme: 'light'});
await p.pdf({path: path.join(here, 'annexes.pdf'), format: 'A4', printBackground: true,
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="font:9px sans-serif;color:#666;width:100%;text-align:center">Volvic Boost · Annexes du dossier Prix · page <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
  margin: {top: '14mm', bottom: '16mm', left: '13mm', right: '13mm'}});
await b.close(); console.log('annexes.pdf ok');
