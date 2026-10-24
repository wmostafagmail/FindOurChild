// Mozilla's supported certificate-install policy, only for disposable GitHub-hosted Linux runners.
// No binary/package patch, verification bypass, or persistent user trust change.
import {firefox} from 'playwright-core';
import {dirname,join,resolve} from 'node:path';
import {mkdirSync,writeFileSync,existsSync} from 'node:fs';
if(process.platform!=='linux'||process.env.GITHUB_ACTIONS!=='true'||process.env.RUNNER_ENVIRONMENT!=='github-hosted'){
  throw new Error('This trust policy is restricted to disposable GitHub-hosted Linux runners');
}
const directory=join(dirname(firefox.executablePath()),'distribution');
const target=join(directory,'policies.json');
if(existsSync(target))throw new Error('Refusing to overwrite existing browser policy');
mkdirSync(directory,{recursive:true});
writeFileSync(target,JSON.stringify({policies:{Certificates:{Install:[resolve('.runtime/tls/cert.pem')]}}}));
