"""Check documentary coverage/config evidence; never marks application tests passed."""
from pathlib import Path
import hashlib
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
checks = []


def check(ok, message):
    if not ok:
        raise AssertionError(message)
    checks.append(message)


def data(path):
    return json.loads((ROOT/path).read_text())


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


for name in ['TEST_MATRIX','E2E_FRAMEWORK_INTEGRATION','CI_CD_TEST_GATES','SECURITY_TEST_CATALOG']:
    check((ROOT/'docs'/f'{name}.md').is_file(), 'Correction document exists: '+name)
for item in data('docs/research/e2e/protected-baseline.json')['files']:
    check(digest(item['path']) == item['sha256'], 'Original approved/design evidence preserved: '+item['path'])

matrix = data('docs/testing/test-matrix.json')
features = matrix['features']
check(matrix['application_test_status'] == 'pending', 'Application validation remains pending')
ids = [f['feature_id'] for f in features]
check(len(ids) == len(set(ids)), 'Feature IDs unique')
fr = re.findall(r'^\| (FR-\d+) \|', (ROOT/'docs/PRODUCT_REQUIREMENTS.md').read_text(), re.M)
check(set(fr) == {f['feature_id'] for f in features if f['category']=='functional'}, 'Every functional requirement mapped')
ops = re.findall(r'^\| ((?:GET|POST|PUT|PATCH|DELETE) /[^|]+?) \|', (ROOT/'docs/API_CONTRACTS.md').read_text(),re.M)
check(set(ops) == {f['title'] for f in features if f['category']=='api_operation'}, 'Every declared API operation mapped')
relations = re.findall(r'^\| ([a-z_]+(?: / [a-z_]+)?) \|', (ROOT/'docs/DATABASE_SCHEMA.md').read_text(),re.M)
check(set(relations) == {f['title'] for f in features if f['category']=='database_boundary'}, 'Every database relation boundary mapped')
events = data('docs/contracts/event-envelope.schema.json')['properties']['event_type']['enum']
check(set(events) == {f['title'] for f in features if f['category']=='background_event'}, 'Every event/consumer contract mapped')
threats = re.findall(r'^\| (T\d+) \|', (ROOT/'docs/SECURITY_THREAT_MODEL.md').read_text(),re.M)
check({'SEC-'+t for t in threats} == {f['feature_id'] for f in features if f['category']=='security_threat'}, 'All original threats mapped')
check(len([f for f in features if f['category']=='background_job']) == 6, 'Additional timer/worker job inventory present')
check(len([f for f in features if f['category']=='transaction']) == 6, 'Transaction/race inventory present')
all_cases = []
rendered_matrix = (ROOT/'docs/TEST_MATRIX.md').read_text()
for f in features:
    for key in ['source','title','suite','positive_scenarios','negative_scenarios','security_authorization_scenarios','edge_cases','fixture_ids','expected_outcomes','test_cases']:
        check(bool(f[key]), f['feature_id']+' has '+key)
    check(f['current_validation_status']=='pending' and f['execution_evidence'] is None, f['feature_id']+' has no fabricated result')
    check({'positive','negative','security_authorization','edge'} <= {c['kind'] for c in f['test_cases']}, f['feature_id']+' has four scenario classes')
    check(all(fx in matrix['fixture_catalog'] for fx in f['fixture_ids']), f['feature_id']+' fixtures resolve')
    check(f['feature_id'] in rendered_matrix, f['feature_id']+' rendered in Markdown')
    for case in f['test_cases']:
        all_cases.append(case)
        check(case['status']=='pending' and case['execution_evidence'] is None, case['test_case_id']+' remains pending')
        check(isinstance(case['required_from_phase'], int) and 1 <= case['required_from_phase'] <= 5, case['test_case_id']+' has explicit phase applicability')
        check(bool(case['planned_file']) and bool(case['planned_selector']) and bool(case['planned_command']), case['test_case_id']+' planned executable specified')
        check(not (ROOT/case['planned_file']).exists(), case['test_case_id']+' not misrepresented as implemented')
        if case['planned_file'].endswith('.e2e.ts'):
            check('node_modules/.bin/e2e run' in case['planned_command'], case['test_case_id']+' uses principal browser runner')
check(len(all_cases)==len({c['test_case_id'] for c in all_cases}), 'All test case IDs unique')
for n in range(1,12):
    f=next(f for f in features if f['feature_id']==f'SAF-{n:02}')
    check({'companion_browser','companion_state'} <= {c['kind'] for c in f['test_cases']}, f['feature_id']+' browser/state companion mapping')
    check(any(c['required_from_phase']==1 for c in f['test_cases']), f['feature_id']+' has mandatory Phase 1 protection or disabled-capability guard')

policy=data('docs/testing/ci-gates.json')
check(policy['kind']=='planned_policy_not_active_ci' and policy['gate_implementation_status']=='pending', 'CI policy not claimed deployed')
check(policy['phase_applicability_field']=='required_from_phase', 'Gate policy consumes per-case phase applicability')
check(len(policy['required_suite_groups'])==11, 'Eleven coordinated suite groups')
check(set(policy['always_required_critical_features']) == {f'SAF-{i:02}' for i in range(1,12)}, 'All safeguarding cases in permanent critical gate')
check({'skipped','missing','pending','flaky','interrupted','blocked','failed'} <= set(policy['acceptance']['reject_statuses']), 'No skipped/missing/pending result accepted')
check(policy['acceptance']['critical_security_safeguarding_failure_blocks_progression'], 'Critical failures block progression')
for key in ['allow_successful_rerun_to_hide_failure','allow_mandatory_ai_filter','allow_pass_with_no_tests','allow_continue_on_error']:
    check(policy['acceptance'][key] is False, 'Unsafe gate bypass disabled: '+key)
check(policy['all_affected_and_transitive_tests_per_pr'] is True, 'Affected/transitive regression policy')
check(set(policy['full_accepted_regression_at']) == {'main','merge_queue','phase_exit','release_candidate'}, 'Full regression points')
check(policy['browser']['actual_application_services'] and policy['browser']['isolated_real_database'] and policy['browser']['independent_database_identity_preflight'], 'Real service/DB/preflight required')
check(not policy['browser']['mocked_application_backend_accepted'], 'Mock backend cannot satisfy browser E2E')
check(policy['browser']['deterministic_outcome_assertions'] and not policy['browser']['mandatory_model_configured'] and not policy['browser']['external_testing_model_may_receive_real_child_data'], 'Deterministic outcomes and external-model boundary')
check(policy['artifact_policy']['sanitize_before_publication'] and not policy['artifact_policy']['raw_e2e_upload_allowed'] and policy['artifact_policy']['publication_and_acceptance_block_on_sanitizer_failure'], 'Sanitized publication/acceptance enforced by plan')
check({'test_results','logs','sanitized_screenshots','sanitized_traces','migration_results','coverage','versioned_checksum_manifest'} <= set(policy['artifact_policy']['required']), 'All required artifact classes specified')

pin=data('docs/research/e2e/framework-lock.json')
source=data('docs/research/e2e/source-evidence.json')
check(pin['reviewed_commit']==source['reviewed_commit']=='69e123b17e04ed624df16d32f3b1ef95ce22c083', 'Selected official repository commit pinned')
for item in pin['source_files']:
    f=next(f for f in source['files'] if f['path']==item['path'])
    check(hashlib.sha256(f['content'].encode()).hexdigest()==item['utf8_sha256'], 'Framework fetched-text integrity: '+item['path'])
    check('/'+pin['reviewed_commit']+'/' in item['url'], 'Immutable framework source URL: '+item['path'])
required_sources={'README.md','LICENSE','packages/e2e/package.json','packages/web/package.json','docs/quickstart.mdx','docs/coding-agents.mdx','docs/mcp-server.mdx','docs/ci.mdx','docs/ci/github-actions.mdx','.github/workflows/examples.yml','docs/telemetry.mdx','docs/security.mdx','examples/with-next/tests/deterministic.e2e.ts','packages/e2e/src/telemetry/telemetry.ts','plugins/e2e/.codex-plugin/plugin.json'}
check(required_sources <= {f['path'] for f in source['files']}, 'All requested upstream research categories evidenced')
package=data('tools/e2e-plan/package.json');lock=data('tools/e2e-plan/package-lock.json')
for name,version in {'e2e':'0.21.3','@e2e-dev/web':'0.15.3','typescript':'7.0.2','@types/node':'26.6.2'}.items():
    check(package['devDependencies'][name]==version and lock['packages']['node_modules/'+name]['version']==version, 'Exact declared/locked version: '+name)
check(lock['packages']['node_modules/playwright-core']['version']=='1.64.1', 'Exact web engine Playwright pin')
check(lock['packages']['node_modules/@e2e-dev/web']['dependencies']['playwright-core']=='1.64.1', 'No second floating Playwright engine')
config=(ROOT/'tools/e2e-plan/e2e.config.example.ts').read_text()
for snippet in ['E2E_TELEMETRY_DISABLED','DO_NOT_TRACK',"cache: 'off'",'retries: 0','failOnSkippedFailure: true',"video: 'off'",'FOC_E2E_DATA_CLASS','FOC_E2E_ISOLATED',"'chromium', 'firefox', 'webkit'","'ar-EG', 'en-GB'",'[320, 360, 390, 1280]']:
    check(snippet in config, 'Configuration specimen safety/target property: '+snippet)
check(not re.search(r'\bmodel\s*:|\bagents\s*:',config), 'No model/provider configured in mandatory specimen')
toml=tomllib.loads((ROOT/'docs/testing/codex-e2e.example.toml').read_text())
check('/ABSOLUTE/TEST-PROJECT/' in toml['mcp_servers']['e2e']['command'], 'Codex specimen intentionally inert')
for flag in ['E2E_TELEMETRY_DISABLED','DO_NOT_TRACK']:
    check(toml['mcp_servers']['e2e']['env'][flag]=='1' and policy['environment'][flag]=='1', 'Telemetry opt-out in MCP and CI: '+flag)
tooling=data('docs/research/e2e/tooling-checks.json')
for path, sha in tooling['checked_file_sha256'].items():
    check(digest(path)==sha, 'Tooling evidence matches exact specimen/lock: '+path)
check(tooling['all_tooling_expectations_met'] and all(c['matched_expected_behavior'] for c in tooling['checks']), 'Actual tooling diagnostics match expectations')
check(tooling['application_tests_executed']==0 and tooling['application_validation']=='pending' and not tooling['no_test_discovery_is_application_success'], 'Tool checks never counted as app passes')
empty=next(c for c in tooling['checks'] if c['check']=='empty_discovery')
check(empty['exit_code']!=0 and empty['expected_exit_code']!=0, 'NO_TESTS remains non-success')
for c in tooling['checks']:
    check((ROOT/'docs/research/e2e'/c['log']).is_file(), 'Reviewable tooling log: '+c['check'])
check(not pin['browser_binaries_installed_or_launched'], 'Browser runtime validation not overstated')

for path in [ROOT/'README.md', *list((ROOT/'docs').rglob('*.md'))]:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if link.startswith(('https:','http:','#','mailto:')):continue
        target=link.split('#')[0].strip('<>')
        if target:check((path.parent/target).exists(), 'Local document link: '+str(path.relative_to(ROOT))+' -> '+target)
print(json.dumps({'status':'passed','scope':'documentation/configuration/traceability consistency only',
    'checks':len(checks),'required_documents':20,'original_repositories_preserved':14,
    'additional_framework_repositories':1,'framework_source_files':len(source['files']),
    'mapped_features':len(features),'planned_test_cases':len(all_cases),
    'declared_api_operations':len(ops),'database_relation_boundaries':len(relations),
    'declared_events':len(events),'application_tests_executed':0,
    'application_validation_status':'pending','ci_enforcement_status':'pending',
    'limits':['No application/browser/database/ML tests run','No active CI/MCP/plugin integration installed',
              'Other suite tool/release image compatibility pending','Full API/DDL contracts still pending']},indent=2))
