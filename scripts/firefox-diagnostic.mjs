// Launch diagnostics only; these are not TesterArmy application acceptance tests.
import { firefox } from 'playwright-core';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir, release } from 'node:os';
import { join } from 'node:path';

mkdirSync('artifacts/raw', { recursive: true });
const executable = firefox.executablePath();
const report = {
  platform: process.platform, release: release(),
  executable_sha256: createHash('sha256').update(readFileSync(executable)).digest('hex'),
  diagnostics_only: true, results: [],
};
for (const mode of ['default', 'isolated-app-data']) {
  const directory = mkdtempSync(join(tmpdir(), 'foc-firefox-diagnostic-'));
  mkdirSync(join(directory, 'Library', 'Application Support'), { recursive: true });
  mkdirSync(join(directory, 'Downloads'), { mode: 0o700 });
  let browser;
  try {
    const env = { ...process.env };
    delete env.CFFIXED_USER_HOME;
    if (mode === 'isolated-app-data') env.CFFIXED_USER_HOME = directory;
    browser = await firefox.launch({ headless: true, timeout: 15000, env });
    const page = await browser.newPage();
    await page.setContent('<title>Synthetic launch diagnostic</title>');
    const title = await page.title();
    if (title !== 'Synthetic launch diagnostic') throw new Error('Unexpected diagnostic page');
    report.results.push({ mode, status: 'passed', version: browser.version() });
  } catch (error) {
    report.results.push({ mode, status: 'failed', error: error.message });
  } finally {
    if (browser) await browser.close();
    rmSync(directory, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
  }
}
writeFileSync('artifacts/raw/firefox-diagnostic.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ ...report, results: report.results.map(({error, ...result}) => result) }, null, 2));
if (report.results[1].status !== 'passed') process.exitCode = 1;
