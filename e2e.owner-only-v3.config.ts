// Separate official suite; original 360 executions and config remain intact.
import baseline from './e2e.config';
import type {E2EConfig} from 'e2e';
export default {...baseline,projectId:'find-our-child-owner-v3',
  tests:['tests/owner_only_v3_browser/*.e2e.ts'],output:'.e2e-owner-only-v3',
} satisfies E2EConfig;
