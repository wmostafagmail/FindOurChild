import {test} from '@e2e-dev/web';
import {expect,secrets} from 'e2e';
import {createRequire} from 'node:module';
const {source:axeSource}=createRequire(import.meta.url)('axe-core') as {source:string};
test('DR-B01-real-private-readiness-without-campaign',async({app,browser,screen})=>{
 const ar=await browser.evaluate(()=>navigator.language==='ar-EG');
 const locale=ar?'ar':'en';
 await app.open('/owner/'+locale);
 await expect(browser.locator('html')).toHaveAttribute('dir',ar?'rtl':'ltr');
 await screen.getByRole('link',ar?'تسجيل الدخول بخطوتين':'Sign in with fresh MFA').click();
 await browser.locator('#username').fill('generated-readiness-owner');
 await browser.locator('#password').fill(secrets.get('fixture_password'));
 await browser.locator('#kc-login').click();
 await expect(browser.locator('#otp')).toBeVisible();
 await browser.locator('#otp').fill(secrets.get('fixture_otp'));
 await browser.locator('#kc-login').click();
 await expect(browser).toHaveURL('/owner/en');
 await app.open('/owner/'+locale);
 await expect(browser.locator('#proof')).toBeEnabled();
 const status=await browser.evaluate(async()=>{const r=await fetch('/owner/status');return {status:r.status,body:await r.json()};});
 expect(status.status).toBe(200);
 expect((status.body as {campaign_authorizations:number}).campaign_authorizations).toBe(0);
 expect((status.body as {inference_enabled:boolean}).inference_enabled).toBe(false);
 expect((status.body as {model_parsing_enabled:boolean}).model_parsing_enabled).toBe(false);
 expect(await browser.evaluate(async()=>({claim:(await fetch('/owner/session?owner=true')).status,
  csrf:(await fetch('/owner/enrollment-proof',{method:'POST',headers:{'Origin':location.origin,'X-CSRF-Token':'wrong'},body:'{}'})).status,
  campaign:(await fetch('/demo-authorization/prepare',{method:'POST',body:'{}'})).status,
  inference:(await fetch('/model/infer',{method:'POST',body:'{}'})).status})))
  .toEqual({claim:403,csrf:403,campaign:404,inference:404});
 await browser.locator('#proof').click();
 await expect(browser.locator('#code')).toHaveText(/^[a-f0-9]{64}$/);
 // The displayed code is for an isolated generated fixture, not a human or campaign approval.
 expect(await browser.evaluate(()=>localStorage.length+sessionStorage.length)).toBe(0);
 expect(await browser.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await browser.evaluate('() => {\n'+axeSource+'\n;return true;\n}');
 expect(await browser.evaluate(`async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>v.id)`)).toEqual([]);
 await browser.locator('#logout').click();
 await expect(browser.locator('#proof')).toBeDisabled();
 await expect(browser.locator('#code')).toHaveText('');
 expect(await browser.evaluate(async()=>(await fetch('/owner/status')).status)).toBe(403);
 await app.open('/owner/'+locale);
 await expect(browser.locator('#code')).toHaveText('');
 await expect(browser.locator('#proof')).toBeDisabled();
 await app.screenshot('deployment-readiness-signed-out-shell');
});
