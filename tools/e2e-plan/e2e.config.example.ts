// Phase 0 configuration specimen only; application services/tests do not exist yet.
import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';

if (process.env.E2E_TELEMETRY_DISABLED !== '1' || process.env.DO_NOT_TRACK !== '1') {
  throw new Error('Testing requires both telemetry opt-out flags');
}
if (process.env.FOC_E2E_DATA_CLASS !== 'synthetic' || process.env.FOC_E2E_ISOLATED !== '1') {
  throw new Error('This specimen only permits an isolated synthetic environment');
}
const url = new URL(process.env.FOC_E2E_BASE_URL ?? 'http://127.0.0.1:3000');
if (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || url.username || url.password) {
  throw new Error('This specimen only permits a loopback application URL without embedded credentials');
}
const browsers = ['chromium', 'firefox', 'webkit'] as const;
const locales = ['ar-EG', 'en-GB'] as const;
const widths = [320, 360, 390, 1280] as const;

export default {
  projectId: 'find-our-child',
  tests: ['tests/browser/**/*.e2e.ts'],
  targets: browsers.flatMap((browser) => locales.flatMap((locale) => widths.map((width) => ({
    name: `${browser}-${locale}-${width}`,
    engine: web({ browser, locale, viewport: { width, height: 844 }, timezoneId: 'Africa/Cairo' }),
    app: { url: url.toString() },
  })))),
  workers: 1,
  retries: 0,
  failOnSkippedFailure: true,
  cache: 'off',
  trace: 'on',
  video: 'off',
  reporters: ['list', 'junit'],
  output: '.e2e',
  // Deliberately no model/provider, remote browser, API key or AI filter.
} satisfies E2EConfig;
