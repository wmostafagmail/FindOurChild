import { spawnSync } from 'node:child_process';
import { renameSync, existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
if (process.env.E2E_TELEMETRY_DISABLED !== '1' || process.env.DO_NOT_TRACK !== '1') throw new Error('Both opt-outs required');
if (process.env.FOC_E2E_DATA_CLASS !== 'synthetic' || process.env.FOC_E2E_ISOLATED !== '1') throw new Error('Synthetic isolated preflight required');
// A stale report must never satisfy this execution's gate.
mkdirSync('artifacts/raw',{recursive:true});
if (existsSync('.e2e')) renameSync('.e2e', `artifacts/raw/browser-attempt-${Date.now()}`);
mkdirSync('artifacts/raw',{recursive:true});
const digest = () => { const p=spawnSync(process.env.FOC_PYTHON ?? 'python3',['scripts/fingerprint.py'],{encoding:'utf8'}); if(p.status!==0) throw new Error('Source fingerprint failed'); return p.stdout.trim(); };
const before=digest();
// Firefox 157 on macOS 27 resolves app data outside its -profile directory.
// Isolate CoreFoundation app data; keep HOME, binary, profile flags and pins intact.
// https://github.com/microsoft/playwright/issues/42768
const appData = process.platform === 'darwin' ? mkdtempSync(join(tmpdir(), 'foc-e2e-app-data-')) : null;
if (appData) {
  mkdirSync(join(appData, 'Library', 'Application Support'), {recursive:true});
  // Precreate Downloads so macOS does not add a deny-delete ACL to it.
  mkdirSync(join(appData, 'Downloads'), {mode:0o700});
}
const env = {...process.env};
delete env.CFFIXED_USER_HOME;
if (appData) env.CFFIXED_USER_HOME = appData;
let result;
try {
result=spawnSync('./node_modules/.bin/e2e',['run','--config','e2e.config.ts','--retries','0','--no-cache'],{stdio:'inherit',env});
} finally {
  if (appData) rmSync(appData,{recursive:true,force:true,maxRetries:10,retryDelay:200});
}
if (result.error) throw result.error;
writeFileSync('artifacts/raw/browser-run.json',JSON.stringify({source_digest:before,exit_code:result.status ?? 1,app_data_isolated:appData !== null}));
process.exit(before===digest() ? (result.status ?? 1) : 1);
