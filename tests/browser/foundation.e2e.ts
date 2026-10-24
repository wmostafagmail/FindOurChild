import { test } from '@e2e-dev/web';
import { expect } from 'e2e';
import { createRequire } from 'node:module';
const { source: axeSource } = createRequire(import.meta.url)('axe-core') as {source:string};

for (const [locale,heading,status,notice] of [
  ['ar','معًا من أجل سلامة كل طفل','الخدمات الأساسية جاهزة','بيانات اصطناعية فقط. لا تُدخل معلومات أو صور أطفال حقيقيين.'],
  ['en','Together for every child’s safety','Foundation services ready','Synthetic data only. Do not enter information or photographs of real children.'],
]) {
  test(`TC_FND_BROWSER_${locale.toUpperCase()}_READY`, async ({app,screen,browser}) => {
    await app.open(`/${locale}`);
    await expect(screen.getByRole('heading',heading)).toBeVisible();
    await expect(screen.getByTestId('readiness')).toHaveText(status);
    await expect(screen.getByTestId('readiness')).toHaveAttribute('data-ready','true');
    await expect(screen.getByText(notice)).toBeVisible();
    await expect(browser.locator('html')).toHaveAttribute('lang',locale);
    await expect(browser.locator('html')).toHaveAttribute('dir',locale==='ar'?'rtl':'ltr');
    await expect(screen.getByRole('textbox')).toHaveCount(0);
    await expect(screen.getByRole('button')).toHaveCount(0);
    await expect(browser).toHaveTitle('Find Our Child');
    const fits = await browser.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
    expect(fits).toBe(true);
    await browser.evaluate('() => {\n' + axeSource + '\n; return true;\n}');
    const violations = await browser.evaluate(`async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v => v.id)`);
    expect(violations).toEqual([]);
    await app.screenshot(`foundation-${locale}`);
    // Safari on macOS uses Option+Tab for links when full keyboard access is off.
    const safari = await browser.evaluate(() => navigator.userAgent.includes('Safari') && !navigator.userAgent.includes('Chrome'));
    await browser.keyboard.press(process.platform === 'darwin' && safari ? 'Alt+Tab' : 'Tab');
    await expect(screen.getByRole('link',locale==='ar'?'انتقل إلى المحتوى':'Skip to content')).toBeFocused();
    await browser.keyboard.press('Enter');
    await expect(screen.getByRole('main')).toBeFocused();
  });
}
test('TC_FND_BROWSER_LANGUAGE_SWITCH', async ({app,screen,browser}) => {
  await app.open('/ar');
  await screen.getByRole('link','English').click();
  await expect(browser).toHaveURL('/en');
  await expect(browser.locator('html')).toHaveAttribute('lang','en');
  await expect(screen.getByRole('heading','Together for every child’s safety')).toBeVisible();
  await screen.getByRole('link','العربية').click();
  await expect(browser).toHaveURL('/ar');
  await expect(browser.locator('html')).toHaveAttribute('lang','ar');
});
