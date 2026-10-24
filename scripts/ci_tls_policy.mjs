// Supported Playwright Firefox policy path; only disposable GitHub-hosted Linux runners.
// https://playwright.dev/docs/api/class-browsertype#browser-type-launch-option-firefox-user-prefs
// No binary/package patch, verification bypass, or persistent user trust change.
import {join,resolve} from 'node:path';
import {mkdirSync,writeFileSync,existsSync,appendFileSync} from 'node:fs';
if(process.platform!=='linux'||process.env.GITHUB_ACTIONS!=='true'||process.env.RUNNER_ENVIRONMENT!=='github-hosted'||!process.env.GITHUB_ENV){
  throw new Error('This trust policy is restricted to disposable GitHub-hosted Linux runners');
}
const directory=resolve('.runtime');
const target=join(directory,'firefox-policies.json');
if(existsSync(target))throw new Error('Refusing to overwrite existing browser policy');
mkdirSync(directory,{recursive:true});
writeFileSync(target,JSON.stringify({policies:{Certificates:{Install:[resolve('.runtime/tls/cert.pem')]}}}));
appendFileSync(process.env.GITHUB_ENV,`PLAYWRIGHT_FIREFOX_POLICIES_JSON=${target}\n`);
