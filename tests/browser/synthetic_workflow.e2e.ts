import {test} from '@e2e-dev/web';
import {expect,secrets} from 'e2e';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
const {source:axeSource}=createRequire(import.meta.url)('axe-core') as {source:string};
const org='10000000-0000-4000-8000-000000000001';
const fixtures=JSON.parse(readFileSync('.runtime/workflow-fixtures.json','utf8')) as {query_case_id:string,users:Record<string,string>};
function fault(username:string,kind:'grant'|'audit',state:'on'|'off'){
 const result=spawnSync('.venv/bin/python',['-m','scripts.workflow_fault',username,kind,state],{stdio:'pipe',timeout:30_000});
 if(result.status!==0)throw new Error('Synthetic workflow fixture operation failed; private operator diagnostics retained');
}

// Shared journey setup uses the actual IdP/BFF/API and leased fixture worker. No intercepted requests.
for(const journey of ['01_QUEUE','02_COMPARISON','03_DECISIONS','04_COLLABORATION','05_INDEPENDENT','06_REVOCATION','07_FAILURE','08_ACCESSIBILITY']){
 test(`SWB_${journey}`,async({app,screen,browser})=>{
  await app.open('/en/investigation');
  await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied');
  expect(await browser.evaluate(async()=>(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).status)).toBe(401);
  await app.open('/en/identity');await screen.getByRole('link','Sign in with MFA').click();
  const target=await browser.evaluate(()=>{const ua=navigator.userAgent;return `${ua.includes('Firefox')?'firefox':ua.includes('Chrome')?'chromium':'webkit'}-${navigator.language}-${innerWidth}`;});
  const username='synthetic-workflow-'+target+'-'+journey.toLowerCase().replace('_','-');
  await browser.locator('#username').fill(username);await browser.locator('#password').fill(secrets.get('staff_password'));await browser.locator('#kc-login').click();await expect(browser.locator('#otp')).toBeVisible();await browser.locator('#otp').fill(secrets.get('staff_otp'));await browser.locator('#kc-login').click();
  await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','authenticated');
  await screen.getByRole('link','Synthetic investigations').click();await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','ready');
  await expect(screen.getByTestId('synthetic-banner')).toContainText('Fictional records');
  await screen.getByTestId('start-scenario').click();await expect(screen.getByTestId('run-state')).toHaveAttribute('data-state','completed',{timeout:30_000});
  await browser.locator('[data-testid="open-candidate"]').first().click();await expect(screen.getByTestId('synthetic-comparison')).toBeVisible();
  const lead=await browser.evaluate(async()=>{const status=await(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).json();const page=await(await fetch('/v1/staff/synthetic-workflow/cases/'+status.scenarios[0].query_case_id+'/leads?organization_id=10000000-0000-4000-8000-000000000001')).json();return page.items[0].id as string;});
  if(journey==='01_QUEUE'){
   const result=await browser.evaluate(async()=>{const status=await(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).json();const s=status.scenarios[0];const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';return {cross:(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000002')).status,model:(await fetch('/v1/staff/synthetic-workflow/cases/'+s.query_case_id+'/runs?organization_id=10000000-0000-4000-8000-000000000001',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':crypto.randomUUID(),'If-Match':'"1"'},body:JSON.stringify({scenario_id:s.id,scenario_version:s.version,model_url:'https://synthetic.invalid/blocked'})})).status,storage:localStorage.length+sessionStorage.length};});
   expect(result).toEqual({cross:404,model:422,storage:0});
  }
  if(journey==='02_COMPARISON'){
   expect(await browser.locator('[data-testid="synthetic-comparison"] img').count()).toBe(5);
   expect(await browser.evaluate(async()=>{const images=[...document.querySelectorAll<HTMLImageElement>('[data-testid="synthetic-comparison"] img')];return Promise.all(images.map(async image=>{const r=await fetch(image.src);return Boolean(r.status===200&&r.headers.get('content-type')?.startsWith('image/png')&&r.headers.get('cache-control')==='no-store'&&(await r.arrayBuffer()).byteLength>0);}));})).toEqual([true,true,true,true,true]);
   await expect(screen.getByTestId('synthetic-comparison')).toContainText('Unknown');
   await expect(screen.getByTestId('synthetic-comparison')).toContainText('2018-01-01');
   await expect(screen.getByTestId('synthetic-comparison')).toContainText('Contradictory');
   const denied=await browser.evaluate(async()=>{const a=document.querySelector<HTMLImageElement>('[data-testid="synthetic-comparison"] img')!;const u=new URL(a.src);u.pathname=u.pathname.replace(/\/photos\/[^/]+\//,'/photos/00000000-0000-4000-8000-000000000001/');return (await fetch(u)).status;});expect(denied).toBe(404);
  }
  if(journey==='03_DECISIONS'){
   await screen.getByTestId('uncertainty-ack').click();await screen.getByTestId('workflow-hold').click();await expect(screen.getByTestId('workflow-history')).toContainText('Hold');
   const replay=await browser.evaluate(async()=>{const s=await(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).json();const leads=await(await fetch('/v1/staff/synthetic-workflow/cases/'+s.scenarios[0].query_case_id+'/leads?organization_id=10000000-0000-4000-8000-000000000001')).json();const id=leads.items[0].id;const d=await(await fetch('/v1/staff/synthetic-workflow/leads/'+id+'/comparison?organization_id=10000000-0000-4000-8000-000000000001')).json();const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';const headers={'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':crypto.randomUUID(),'If-Match':'"'+d.revision+'"'};const body={snapshot_hash:d.snapshot_hash,uncertainty_acknowledged:true,rationale_codes:['INSUFFICIENT_AUTHORIZED_EVIDENCE'],evidence_refs:[],outcome:'hold'};const path='/v1/staff/synthetic-workflow/leads/'+id+'/reviews?organization_id=10000000-0000-4000-8000-000000000001';const first=await fetch(path,{method:'POST',headers,body:JSON.stringify(body)});const value=await first.json();const second=await fetch(path,{method:'POST',headers,body:JSON.stringify(body)});const next=await second.json();const stale=await fetch(path,{method:'POST',headers:{...headers,'Idempotency-Key':crypto.randomUUID()},body:JSON.stringify(body)});return {first:first.status,second:second.status,same:value.id===next.id,stale:stale.status};});expect(replay).toEqual({first:201,second:201,same:true,stale:412});
  }
  if(journey==='04_COLLABORATION'){
   await screen.getByTestId('uncertainty-ack').click();await screen.getByTestId('append-structured-note').click();await expect(screen.getByTestId('workflow-history')).toContainText('Collaboration note');
   await screen.getByTestId('uncertainty-ack').click();await browser.locator('[data-testid="workflow-colleague"]').selectOption({value:fixtures.users['synthetic-workflow-peer-'+target]});await screen.getByTestId('workflow-assign').click();await expect(screen.getByTestId('workflow-history')).toContainText('Caseworker assignment');
  }
  if(journey==='05_INDEPENDENT'){
   await browser.locator('[data-testid="synthetic-comparison"] .workflow-check input[type="checkbox"]').first().click();await browser.locator('[data-testid="workflow-reason"]').selectOption({value:'SUPPORTING_FIXTURE_CLAIM'});await screen.getByTestId('uncertainty-ack').click();await screen.getByTestId('workflow-escalate').click();await expect(screen.getByTestId('workflow-history')).toContainText('Escalate');
   await screen.getByTestId('uncertainty-ack').click();await browser.locator('[data-testid="workflow-colleague"]').selectOption({value:fixtures.users['synthetic-workflow-alias-'+target]});await screen.getByTestId('request-independent').click();await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied');
   await app.open('/en/investigation');await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','ready');await screen.getByRole('button','Refresh candidate queue').click();await browser.locator('[data-testid="open-candidate"]').first().click();await screen.getByTestId('uncertainty-ack').click();await browser.locator('[data-testid="workflow-colleague"]').selectOption({value:fixtures.users['synthetic-workflow-peer-'+target]});await screen.getByTestId('request-independent').click();await expect(screen.getByTestId('workflow-history')).toContainText('Independent review requested');
   await screen.getByRole('button','Sign out and clear evidence').click();await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied');
   await app.open('/en/identity');await screen.getByRole('link','Sign in with MFA').click();await browser.locator('#username').fill('synthetic-workflow-peer-'+target);await browser.locator('#password').fill(secrets.get('staff_password'));await browser.locator('#kc-login').click();await expect(browser.locator('#otp')).toBeVisible();await browser.locator('#otp').fill(secrets.get('staff_otp'));await browser.locator('#kc-login').click();await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','authenticated');
   await app.open('/en/investigation');await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','ready');await screen.getByRole('button','Refresh candidate queue').click();await browser.locator('[data-testid="open-candidate"]').first().click();await screen.getByTestId('uncertainty-ack').click();await browser.locator('#independent-outcome').selectOption({value:'workflow_review_complete'});await screen.getByTestId('complete-independent').click();await expect(screen.getByTestId('workflow-history')).toContainText('Complete synthetic safeguarding review');
   const invariant=await browser.evaluate(async()=>{const s=await(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).json();const c=await(await fetch('/v1/staff/cases/'+s.scenarios[0].query_case_id+'?organization_id=10000000-0000-4000-8000-000000000001')).json();return c.summary.verification_status;});expect(invariant).toBe('unverified');
  }
  if(journey==='06_REVOCATION'){
   fault(username,'grant','on');
   try{await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied',{timeout:10_000});expect(await browser.locator('[data-testid="synthetic-comparison"] img').count()).toBe(0);}finally{fault(username,'grant','off');}
   await app.open('/en/investigation');await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','ready');
   await screen.getByRole('button','Sign out and clear evidence').click();await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied');expect(await browser.locator('[data-testid="synthetic-comparison"] img').count()).toBe(0);
   expect(await browser.evaluate(async()=>(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).status)).toBe(401);
   await app.open('/ar/investigation');await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied');expect(await browser.locator('img').count()).toBe(0);
  }
  if(journey==='07_FAILURE'){
   const failure=await browser.evaluate(async()=>{const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';const s=await(await fetch('/v1/staff/synthetic-workflow/status?organization_id=10000000-0000-4000-8000-000000000001')).json();const command='/v1/staff/synthetic-workflow/cases/'+s.scenarios[0].query_case_id+'/runs?organization_id=10000000-0000-4000-8000-000000000001';return {unknown:(await fetch(command,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':crypto.randomUUID(),'If-Match':'"1"'},body:JSON.stringify({scenario_id:'00000000-0000-4000-8000-000000000001',scenario_version:'fixture-2d-v1'})})).status,csrf:(await fetch(command,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':'forged','Idempotency-Key':crypto.randomUUID(),'If-Match':'"1"'},body:JSON.stringify({scenario_id:s.scenarios[0].id,scenario_version:s.scenarios[0].version})})).status};});expect(failure).toEqual({unknown:404,csrf:403});
   await expect(screen.getByTestId('synthetic-comparison')).toBeVisible();
   fault(username,'audit','on');
   try{await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','denied',{timeout:10_000});expect(await browser.locator('[data-testid="synthetic-comparison"] img').count()).toBe(0);}finally{fault(username,'audit','off');}
   await app.open('/en/investigation');await expect(screen.getByTestId('workflow-state')).toHaveAttribute('data-state','ready');await screen.getByRole('button','Refresh candidate queue').click();await browser.locator('[data-testid="open-candidate"]').first().click();await expect(screen.getByTestId('synthetic-comparison')).toBeVisible();
  }
  if(journey==='08_ACCESSIBILITY'){
   await browser.evaluate('() => {\n'+axeSource+'\n; return true;\n}');expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
   await screen.getByRole('button','العربية').click();await expect(browser.locator('html')).toHaveAttribute('dir','rtl');await expect(screen.getByRole('heading','مساحة التحقيق الاصطناعي')).toBeFocused();await expect(screen.getByTestId('synthetic-banner')).toContainText('سجلات خيالية');
   await browser.evaluate('() => {\n'+axeSource+'\n; return true;\n}');expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
   expect(await browser.evaluate(()=>{document.documentElement.style.fontSize='200%';return document.documentElement.scrollWidth<=innerWidth;})).toBe(true);
   expect(await browser.evaluate(async()=>({public:(await fetch('/v1/public/facial-search')).status,release:(await fetch('/v1/staff/reunification-plans/00000000-0000-4000-8000-000000000001/handover',{method:'POST'})).status}))).toEqual({public:404,release:404});
  }
  expect(lead.length).toBe(36);expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 });
}
