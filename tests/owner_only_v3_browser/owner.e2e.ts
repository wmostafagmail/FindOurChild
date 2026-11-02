import {test} from '@e2e-dev/web';
import {expect,secrets} from 'e2e';
import {createRequire} from 'node:module';
const {source:axeSource}=createRequire(import.meta.url)('axe-core') as {source:string};

for(let journey=1;journey<=6;journey++) {
  test(`OD3-B${String(journey).padStart(2,'0')}`,async({app,screen,browser})=>{
    await app.open('/en/demo-authorization');
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','denied');
    expect(await browser.evaluate(async()=>(await fetch('/demo-authorization/status')).status)).toBe(401);
    const target=await browser.evaluate(()=>{const ua=navigator.userAgent;return `${ua.includes('Firefox')?'firefox':ua.includes('Chrome')?'chromium':'webkit'}-${navigator.language}-${innerWidth}`;});
    await screen.getByRole('link','Sign in with fresh MFA').click();
    await browser.locator('#username').fill(`synthetic-owner-v3-${target}-${String(journey).padStart(2,'0')}`);
    await browser.locator('#password').fill(secrets.get('staff_password'));
    await browser.locator('#kc-login').click();
    await expect(browser.locator('#otp')).toBeVisible();
    await browser.locator('#otp').fill(secrets.get('staff_otp'));
    await browser.locator('#kc-login').click();
    await expect(browser).toHaveURL('/en/identity');
    const ar=target.includes('-ar-EG-');
    await app.open(ar?'/ar/demo-authorization':'/en/demo-authorization');
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','ready');
    await expect(browser.locator('html')).toHaveAttribute('dir',ar?'rtl':'ltr');
    await expect(screen.getByTestId('fixture-count')).toHaveText('48 / 24');
    expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    await browser.evaluate('() => {\n'+axeSource+'\n;return true;\n}');
    expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
    const invalid=await browser.evaluate(async()=>{
      const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';
      return {claim:(await fetch('/demo-authorization/status?owner=true')).status,
        csrf:(await fetch('/demo-authorization/prepare',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':'wrong'},body:'{}'})).status,
        policy:(await fetch('/demo-authorization/prepare',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:'{"policy":"V2"}'})).status,
        get:(await fetch('/demo-authorization/confirm')).status};
    });
    expect(invalid).toEqual({claim:404,csrf:403,policy:403,get:405});
    await screen.getByTestId('prepare').click();
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','prepared');
    const record=await browser.evaluate(()=>JSON.parse(document.querySelector('[data-testid="scope-record"]')!.textContent!));
    const shown=await browser.evaluate(()=>document.querySelector('[data-testid="draft-digest"]')!.textContent);
    expect(record.confirmation.reviewed_draft_sha256).toBe(shown);
    expect(record.scope.image_count).toBe(48);expect(record.scope.fictional_pair_count).toBe(24);
    expect(record.domain).toBe('FOC-PHASE2E-DEMO-OWNER-AUTHORIZATION-V3');
    expect(record.time.lifetime_seconds).toBe(14400);
    expect(record.exceptions.database_p95_target_ms).toBe(1000);
    expect(record.prohibitions.no_public_biometric_search).toBe(true);
    expect(record.prohibitions.no_custody_disclosure_or_release).toBe(true);
    if(journey===3) {
      const wrong=await browser.evaluate(async()=>{
        const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';
        const record=JSON.parse(document.querySelector('[data-testid="scope-record"]')!.textContent!);
        return (await fetch('/demo-authorization/confirm',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},
          body:JSON.stringify({nonce:'wrong',record_id:record.record_id,reviewed_draft_sha256:'0'.repeat(64)})})).status;
      });expect(wrong).toBe(403);
    }
    if(journey===4) {
      const plan=await browser.evaluate(()=>JSON.parse(document.querySelector('[data-testid="fixture-json"]')!.textContent!));
      expect(plan.images.length).toBe(48);expect(plan.pairings.length).toBe(24);
      expect(plan.images.every((p:{capture_age_months:{lower:unknown};capture_date:{lower:unknown}})=>p.capture_age_months.lower===null&&p.capture_date.lower===null)).toBe(true);
      expect(plan.failure_policy).toBe('retain_all_selected_outcomes_no_substitution');
      expect(plan.freeze_before).toBe('any_model_image_call');
    }
    await screen.getByTestId('confirm-check').click();
    await screen.getByTestId('confirm').click();
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','confirmed');
    expect(await browser.evaluate(async()=>{const v=await(await fetch('/demo-authorization/status')).json();return {
      source:v.source_only,execution:v.execution_available,assets:v.actual_assets,inference:v.actual_inference,owner:v.provisioned_real_owner};})).toEqual({source:true,execution:false,assets:0,inference:false,owner:false});
    if(journey===6) {
      const isolation=await browser.evaluate(async()=>({
        foreign:(await fetch('/identity/organizations/10000000-0000-4000-8000-000000000002/cases/30000000-0000-4000-8000-000000000002/permission')).status,
        publicSearch:(await fetch('/v1/public/biometric-search',{method:'POST'})).status,
        custody:(await fetch('/v1/child-release',{method:'POST'})).status,
        storage:localStorage.length+sessionStorage.length,
      }));expect(isolation.foreign).toBe(404);expect(isolation.publicSearch>=400).toBe(true);
      expect(isolation.custody>=400).toBe(true);expect(isolation.storage).toBe(0);
    }
    await screen.getByTestId('revoke').click();
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','revoked');
    expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    await browser.evaluate('() => {\n'+axeSource+'\n;return true;\n}');
    expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
    // Only the signed-out static shell is eligible for screenshot publication.
    expect(await browser.evaluate(async()=>{const csrf=document.cookie.split('; ').find(v=>v.startsWith('__Host-foc-csrf='))?.split('=')[1]??'';
      return (await fetch('/identity/logout',{method:'POST',headers:{'X-CSRF-Token':csrf}})).status;})).toBe(200);
    await app.open(ar?'/ar/demo-authorization':'/en/demo-authorization');
    await expect(screen.getByTestId('owner-panel')).toHaveAttribute('data-state','denied');
    await expect(screen.getByTestId('scope-record')).toHaveCount(0);
    await expect(screen.getByTestId('fixture-json')).toHaveCount(0);
    await app.screenshot('owner-v3-signed-out-shell');
  });
}
