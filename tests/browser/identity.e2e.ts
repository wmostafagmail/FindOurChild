import {test} from '@e2e-dev/web';
import {expect,secrets} from 'e2e';
import {readFileSync} from 'node:fs';
// Secrets are synthetic, generated privately; no screenshots or raw traces from this flow are published.
test('TC_ID_BROWSER_MFA_TENANT_LOGOUT',async({app,screen,browser})=>{
  const fixture=JSON.parse(readFileSync('.runtime/identity.json','utf8')) as {password:string,otp:string,users:Record<string,string>};
  await app.open('/en/identity');
  await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','signed_out');
  await screen.getByRole('link','Sign in with MFA').click();
  const target=await browser.evaluate(()=>{const ua=navigator.userAgent;const b=ua.includes('Firefox')?'firefox':ua.includes('Chrome')?'chromium':'webkit';return `${b}-${navigator.language}-${innerWidth}`;});
  const username=`synthetic-${target}`;
  await browser.locator('#username').fill(username);
  await browser.locator('#password').fill(secrets.get('staff_password'));
  await browser.locator('#kc-login').click();
  await expect(browser.locator('#otp')).toBeVisible();
  await browser.locator('#otp').fill(secrets.get('staff_otp'));
  await browser.locator('#kc-login').click();
  await expect(browser).toHaveURL('/en/identity');
  await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','authenticated');
  await expect(screen.getByTestId('principal')).toHaveText(fixture.users[username]);
  const cookies=await browser.cookies();
  const session=cookies.find(c=>c.name==='__Host-foc-session');
  expect(Boolean(session?.httpOnly && session.secure && session.path==='/')).toBe(true);
  const access=await browser.evaluate(async()=>{
    const own=await fetch('/identity/organizations/10000000-0000-4000-8000-000000000001/cases/30000000-0000-4000-8000-000000000001/permission');
    const other=await fetch('/identity/organizations/10000000-0000-4000-8000-000000000002/cases/30000000-0000-4000-8000-000000000002/permission');
    const forged=await fetch('/identity/logout',{method:'POST',headers:{'X-CSRF-Token':'forged'}});
    return {own:own.status,other:other.status,forged:forged.status,storage:localStorage.length+sessionStorage.length};
  });
  expect(access).toEqual({own:200,other:404,forged:403,storage:0});
  await screen.getByRole('link','العربية').click();
  await expect(browser.locator('html')).toHaveAttribute('dir','rtl');
  await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','authenticated');
  await screen.getByRole('button','تسجيل الخروج').click();
  await expect(screen.getByTestId('identity-state')).toHaveAttribute('data-state','signed_out');
  const denied=await browser.evaluate(async()=>(await fetch('/identity/me')).status);
  expect(denied).toBe(401);
});
