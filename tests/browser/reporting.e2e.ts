import {test} from '@e2e-dev/web';
import {expect,secrets} from 'e2e';
import {writeFileSync,readFileSync,unlinkSync} from 'node:fs';
import {resolve} from 'node:path';
import {createRequire} from 'node:module';
const {source:axeSource}=createRequire(import.meta.url)('axe-core') as {source:string};
for(const registry of ['missing','found']){
 test(`TC_RPT_BROWSER_${registry.toUpperCase()}_INTAKE`,async({app,screen,browser})=>{
  await app.open('/en/reporting');
  await expect(screen.getByRole('heading','Reporting and case management')).toBeVisible();
  await browser.locator('[data-testid="registry"]').selectOption({value:registry});
  await browser.locator('[data-testid="child-name"]').fill('Synthetic <script>not executable</script>');
  await screen.getByTestId('save-draft').click();
  await expect(screen.getByTestId('reporting-status')).toContainText('Private server draft saved');
  await app.open('/en/reporting');
  await expect(browser.locator('[data-testid="registry"]')).toHaveValue(registry);
  await expect(browser.locator('[data-testid="child-name"]')).toHaveValue('Synthetic <script>not executable</script>');
  await screen.getByRole('button','العربية').click();
  await expect(browser.locator('html')).toHaveAttribute('dir','rtl');
  await expect(screen.getByRole('heading','الإبلاغ وإدارة الحالات')).toBeFocused();
  expect(await browser.locator('[data-testid="child-name"]').inputValue()).toBe('Synthetic <script>not executable</script>');
  await screen.getByRole('button','English').click();
  const contact=`synthetic-${crypto.randomUUID()}@synthetic.invalid`;
  await browser.locator('[data-testid="contact"]').fill(contact);
  await browser.locator('input[type="checkbox"]').click();
  await screen.getByTestId('submit-report').click();
  await expect(screen.getByTestId('reporting-status')).toContainText('Your report has been received for review.');
  const receipt=await browser.locator('[data-testid="receipt"]').inputValue();expect(receipt.length).toBe(43);
  expect(await browser.evaluate(async()=>{const r=await fetch('/v1/public/drafts');return {status:r.status,draft:(await r.json()).draft};})).toEqual({status:200,draft:null});
  writeFileSync('.runtime/e2e-receipt.json',JSON.stringify({receipt}),{mode:0o600});
  try{
   await screen.getByTestId('request-code').click();
   await expect(screen.getByTestId('reporting-status')).toContainText('If authorized, a neutral verification message has been queued.');
   await browser.locator('[data-testid="verification-code"]').fill(secrets.get('reporter_code'));
   await screen.getByTestId('verify-code').click();
   await expect(screen.getByTestId('reporter-state')).toHaveAttribute('data-state','verified');
  }finally{unlinkSync('.runtime/e2e-receipt.json');}
  await browser.locator('[data-testid="supplement"]').fill('Synthetic supplementary statement');
  await screen.getByRole('button','Add information',{exact:true}).click();
  await expect(screen.getByText('Synthetic supplementary statement',{exact:false})).toBeVisible();
  const appended=await browser.evaluate(async()=>{
    const submission=await (await fetch('/v1/reporter/submission')).json();
    const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-reporter-csrf='))?.split('=')[1]??'';
    return (await fetch('/v1/reporter/supplements',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':crypto.randomUUID()},body:JSON.stringify({claims:[{field:'__proto__',value:'prototype-not-executable',source_id:submission.submitted_claims[0].source_id},{field:'relationship_claim',value:'constructor',source_id:submission.submitted_claims[0].source_id}],evidence_refs:[]})})).status;
  });
  expect(appended).toBe(202);
  await app.open('/en/reporting');
  await expect(screen.getByTestId('reporter-state')).toHaveAttribute('data-state','verified');
  await expect(screen.getByText('prototype-not-executable',{exact:true})).toBeVisible();
  await browser.locator('[data-testid="photo-files"]').setInputFiles([resolve('tests/fixtures/synthetic-green.png'),resolve('tests/fixtures/synthetic-blue.png')]);
  await screen.getByTestId('upload-files').click();
  await expect(screen.getByTestId('reporting-status')).toContainText('Files entered quarantine');
  expect(await browser.locator('img').count()).toBe(0);
  // Real scans are asynchronous and the UI polls every 5s; the default 5s matcher races that poll.
  // Require both actual clean derivatives within a bounded 30s worker budget; no test retry or bypass.
  await expect(screen.getByText('Sanitized review copy ready',{exact:true})).toHaveCount(2,{timeout:30_000});
  await screen.getByLabel('Message through NGO relay',{exact:true}).fill('Synthetic private relay statement');
  await screen.getByRole('button','Send safe message',{exact:true}).click();
  await expect(screen.getByTestId('reporting-status')).toContainText('Message received for review.');
  const boundary=await browser.evaluate(async()=>({staff:(await fetch('/v1/staff/cases?organization_id=10000000-0000-4000-8000-000000000001')).status,csrf:(await fetch('/v1/reporter/contact',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':'forged','Idempotency-Key':crypto.randomUUID()},body:JSON.stringify({message:'synthetic'})})).status,storage:localStorage.length+sessionStorage.length,overflow:document.documentElement.scrollWidth>innerWidth}));
  expect(boundary).toEqual({staff:401,csrf:403,storage:0,overflow:false});
  await browser.evaluate('() => {\n'+axeSource+'\n; return true;\n}');
  expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
  await screen.getByRole('button','العربية').click();
  expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  expect(await browser.evaluate(()=>{document.documentElement.style.fontSize='200%';return document.documentElement.scrollWidth<=innerWidth;})).toBe(true);
  await browser.evaluate('() => {\n'+axeSource+'\n; return true;\n}');
  expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
  await screen.getByRole('button','English').click();
  await screen.getByRole('button','End reporter session',{exact:true}).click();
  await expect(screen.getByTestId('reporter-state')).toHaveAttribute('data-state','unverified');
  expect(await browser.evaluate(async()=>(await fetch('/v1/reporter/submission')).status)).toBe(401);
 });
}

test('TC_RPT_BROWSER_NGO_MODERATION',async({app,screen,browser})=>{
 await app.open('/en/identity');await screen.getByRole('link','Sign in with MFA').click();
 const target=await browser.evaluate(()=>{const ua=navigator.userAgent;return `${ua.includes('Firefox')?'firefox':ua.includes('Chrome')?'chromium':'webkit'}-${navigator.language}-${innerWidth}`;});
 const username='synthetic-reporting-'+target;
 await browser.locator('#username').fill(username);await browser.locator('#password').fill(secrets.get('staff_password'));await browser.locator('#kc-login').click();await expect(browser.locator('#otp')).toBeVisible();await browser.locator('#otp').fill(secrets.get('staff_otp'));await browser.locator('#kc-login').click();
 await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','authenticated');
 await app.open('/en/reporting');await screen.getByRole('button','Load assigned cases').click();
 const fixtures=JSON.parse(readFileSync('.runtime/reporting-fixtures.json','utf8')) as {staff_cases:Record<string,string>};
 await screen.getByRole('button',fixtures.staff_cases[username],{exact:false}).click();
 await expect(screen.getByTestId('case-detail')).toBeVisible();
 // Label-based locators keep unrelated reporter/concern inputs outside staff mutations.
 await browser.locator('[data-testid="staff-reason"]').fill('Synthetic NGO intake review');
 await screen.getByRole('button','Review',{exact:true}).click();
 await expect(screen.getByTestId('case-detail')).toContainText('review');
 await expect(browser.locator('[data-testid="staff-reason"]')).toHaveValue('');
 await browser.locator('[data-testid="staff-reason"]').fill('Synthetic investigation note');
 await screen.getByRole('button','Append note',{exact:true}).click();
 await expect(screen.getByTestId('case-detail')).toContainText('Synthetic investigation note');
 const denied=await browser.evaluate(async()=>({cross:(await fetch('/v1/staff/cases/30000000-0000-4000-8000-000000000002?organization_id=10000000-0000-4000-8000-000000000002')).status,release:(await fetch('/v1/staff/reunification-plans/00000000-0000-4000-8000-000000000001/handover',{method:'POST'})).status,storage:localStorage.length+sessionStorage.length}));
 expect(denied).toEqual({cross:404,release:404,storage:0});
 await browser.evaluate('() => {\n'+axeSource+'\n; return true;\n}');
 expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
 expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await screen.getByRole('button','العربية').click();await expect(browser.locator('html')).toHaveAttribute('dir','rtl');
 expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
