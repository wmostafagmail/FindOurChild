import type {E2EConfig} from 'e2e';
import original from './e2e.config';
import {execFileSync} from 'node:child_process';
if(process.env.GITHUB_ACTIONS!=='true')throw Error('Generated deployment fixture workflow required');
export default {...original,projectId:'find-our-child-deployment-readiness',
  tests:['tests/demo_deployment_browser/**/*.e2e.ts'],output:'.e2e-deployment-readiness',
  secrets:{fixture_password:()=>execFileSync('.venv/bin/python',['-m','scripts.deployment_credentials','password'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim(),
    fixture_otp:()=>execFileSync('.venv/bin/python',['-m','scripts.deployment_credentials','otp'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim()},
  targets:original.targets.map(t=>({...t,app:{url:'https://127.0.0.1:9443'}})),
  retries:0,cache:'off',failOnSkippedFailure:true,
} satisfies E2EConfig;
