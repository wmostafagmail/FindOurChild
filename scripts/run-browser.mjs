import { spawnSync } from 'node:child_process';
import { renameSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
if (process.env.E2E_TELEMETRY_DISABLED !== '1' || process.env.DO_NOT_TRACK !== '1') throw new Error('Both opt-outs required');
if (process.env.FOC_E2E_DATA_CLASS !== 'synthetic' || process.env.FOC_E2E_ISOLATED !== '1') throw new Error('Synthetic isolated preflight required');
// A stale report must never satisfy this execution's gate.
mkdirSync('artifacts/raw',{recursive:true});
if (existsSync('.e2e')) renameSync('.e2e', `artifacts/raw/browser-attempt-${Date.now()}`);
mkdirSync('artifacts/raw',{recursive:true});
const digest = () => { const p=spawnSync(process.env.FOC_PYTHON ?? 'python3',['scripts/fingerprint.py'],{encoding:'utf8'}); if(p.status!==0) throw new Error('Source fingerprint failed'); return p.stdout.trim(); };
const before=digest();
const result=spawnSync('./node_modules/.bin/e2e',['run','--config','e2e.config.ts','--retries','0','--no-cache'],{stdio:'inherit',env:process.env});
if (result.error) throw result.error;
writeFileSync('artifacts/raw/browser-run.json',JSON.stringify({source_digest:before,exit_code:result.status ?? 1}));
process.exit(before===digest() ? (result.status ?? 1) : 1);
