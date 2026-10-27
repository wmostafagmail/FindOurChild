import { spawnSync } from 'node:child_process';
import { renameSync, existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync,readFileSync,chmodSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
process.umask(0o077);
if (process.env.E2E_TELEMETRY_DISABLED !== '1' || process.env.DO_NOT_TRACK !== '1') throw new Error('Both opt-outs required');
if (process.env.FOC_E2E_DATA_CLASS !== 'synthetic' || process.env.FOC_E2E_ISOLATED !== '1') throw new Error('Synthetic isolated preflight required');
// A stale report must never satisfy this execution's gate.
mkdirSync('artifacts/raw',{recursive:true,mode:0o700});
chmodSync('artifacts/raw',0o700);
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
result=spawnSync('./node_modules/.bin/e2e',['run','--config','e2e.config.ts','--retries','0','--no-cache'],{stdio:'pipe',env,maxBuffer:64*1024*1024});
} finally {
  if (appData) rmSync(appData,{recursive:true,force:true,maxRetries:10,retryDelay:200});
}
writeFileSync('artifacts/raw/browser-console.log',Buffer.concat([result.stdout??Buffer.alloc(0),result.stderr??Buffer.alloc(0)]),{mode:0o600});
if (result.error) throw new Error('Browser runner process failed; private diagnostics retained');
try{
 const report=JSON.parse(readFileSync('.e2e/report.json','utf8'));
 console.log('Official TesterArmy browser assertions: '+JSON.stringify(report.run.summary));
 const required=JSON.parse(readFileSync('docs/phase1a/required-tests.json','utf8')).browser_titles;
 const allowedFiles=new Set(['tests/browser/foundation.e2e.ts','tests/browser/identity.e2e.ts','tests/browser/reporting.e2e.ts','tests/browser/synthetic_workflow.e2e.ts']);
 const failed=report.run.results.filter(r=>r.status!=='passed').map(r=>{
  const attempt=r.attempts?.at(-1);
  const source=attempt?.error?.source??attempt?.steps?.find(s=>s.status==='failed'||s.status==='error')?.source;
  const sourceFile=typeof source?.file==='string'?source.file.replaceAll('\\','/'):'';
  const file=[...allowedFiles].find(f=>sourceFile===f||sourceFile===process.cwd()+'/'+f);
  const serialized=JSON.stringify(attempt?.error??{});
  const reason=['delivery_missing','delivery_key_mismatch','delivery_permission_denied','api_not_running','fixture_process_failed'].find(v=>serialized.includes('Synthetic delivery fixture unavailable: '+v))??null;
  return {id:required.includes(r.titlePath?.at(-1))?r.titlePath.at(-1):'unknown',target:/^(chromium|firefox|webkit)-(ar-EG|en-GB)-(320|360|390|1280)$/.test(r.targetId)?r.targetId:'unknown',source:file&&Number.isInteger(source?.line)&&source.line>0&&source.line<=20000?{file,line:source.line}:null,reason};
 });
 if(failed.length)console.log('Sanitized browser failure locations: '+JSON.stringify(failed));
}catch{console.log('Browser result manifest unavailable; required gate remains blocked');}
writeFileSync('artifacts/raw/browser-run.json',JSON.stringify({source_digest:before,exit_code:result.status ?? 1,app_data_isolated:appData !== null}));
process.exit(before===digest() ? (result.status ?? 1) : 1);
