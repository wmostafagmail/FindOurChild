# Owner-only demonstration governance — decision packet

Date: **31 October 2026 (Africa/Cairo)**. Status: **proposed policy design; owner approval and implementation pending**.

The owner authorized preparation and documentation-only publication of this amendment as a draft PR, not its implementation, deployment, an execution authorization, acquisition, parsing or inference. No runtime, validator, trust registry, existing required-test inventory or configuration is changed by this packet. No actual authorization record, reviewer signature or model/image byte-verification hash is issued here.

The accepted governance milestone is main `2bc7c555291b6e21920fed9be58e195aaafb4c9c`, containing approved implementation `9075f77b62b879c2910ad0a9042193fb054309eb`. Full Phase 2E remains incomplete. [PR #12](https://github.com/wmostafagmail/FindOurChild/pull/12) records exact-main CI, artifact identities and milestone limitations. That evidence does not validate this proposed V3 design or future implementation.

| Review item | Document |
|---|---|
| Exact substitutions, retained controls and alternatives | [Policy amendment](POLICY_AMENDMENT.md) |
| Single owner action, scope, receipts and lifecycle | [Authorization contract](AUTHORIZATION_CONTRACT.md) |
| Draft closed record shape; not an installed verifier | [JSON Schema](authorization-record.schema.json) |
| Per-photo uncertain metadata and fictional pair selection shape | [Fixture-plan schema](fixture-plan.schema.json) |
| Threats, loss of independence and residual risks | [Threat assessment](THREAT_ASSESSMENT.md) |
| All 64 existing families mapped; new negative, positive and browser designs | [Test matrix](TEST_MATRIX.md), [machine inventory](TEST_MATRIX.json) |
| Implementation, provisioning and owner decision boundaries | [Implementation plan](IMPLEMENTATION_PLAN.md) |
| Source preservation and documentation-check evidence | [Design status](DESIGN_STATUS.json) |

The five primary review documents are the policy amendment, authorization contract, threat assessment, test matrix and implementation plan. This index, two draft schemas, machine-readable matrix and status evidence are supporting files in the same documentation-only commit. The policy includes all 12 V2 record kinds plus enrollment/role/lifecycle substitutions; the matrix explicitly maps all 96 V3 scenarios to the 17 planned or retained implementation boundaries.

## Decision requested

Approve or revise the **new, isolated owner-only policy**, proposed domain `FOC-PHASE2E-DEMO-OWNER-AUTHORIZATION-V3`, single MFA-backed authorization, immutable pre-run selection and stage-receipt state machine. The sole human approval authority would be the actual authenticated project owner. No technical verifier or fixture reviewer appointment, human application signing key, multi-person permit chain or external consultancy would be required by this new demo policy.

The accepted V2 implementation, its two-person requirements, the original v1/research/operational requirements and all historical findings remain unchanged. A future V3 deployment must be explicitly selected by protected deployment configuration and separately implemented and reviewed; V2 failures must never trigger fallback to V3.

The original independent human A1b assessment remains **unmet under the existing demo waiver**. Removing independent technical/fixture approval is an additional proposed exception, not proof that those reviews occurred. Existing NGO case-purpose authorization and safeguarding reviewer separation are outside this exception.

Approval of this design alone would not authorize implementation, registry deployment, assets or neural execution. The next instruction must state its authorized engineering/provisioning scope. This packet ends at owner review; no merge or Phase 2F/3 work is authorized.

## Reproducible documentation checks

Using the existing locked Python environment with `jsonschema` installed, from the repository root:

```sh
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
p = Path('docs/phase2e/owner-only-demo')
for name in ['authorization-record.schema.json', 'fixture-plan.schema.json']:
    Draft202012Validator.check_schema(json.loads((p / name).read_text()))
m = json.loads((p / 'TEST_MATRIX.json').read_text())
b = json.loads(Path('docs/phase2e/governance-required-tests.json').read_text())
assert m['legacy_selectors_preserved'] == b['selectors']
assert m['legacy_scenarios_preserved'] == b['scenarios']
assert {r['legacy_case'] for r in m['cases'] if r['legacy_case']} == set(b['scenarios'])
assert len(m['cases']) == 96 and len({r['case_id'] for r in m['cases']}) == 96
assert all(r['validation_status'] == 'pending_implementation_and_execution'
           and not r['selectors'] and not r['execution_evidence'] for r in m['cases'])
assert len(m['component_catalog']) == 17
assert all(r['affected_components'] and r['component_obligation']
           and set(r['affected_components']) <= set(m['component_catalog'])
           for r in m['cases'])
print('Schema/traceability documentation checks passed; no V3 application test executed.')
PY
```

The status file also records relative-link/JSON checks, exact proposal-file hashes and selected accepted security/source/config preservation checks. These are documentation checks only. No V3 authentication, database, browser, model-loading or inference result is passed by this packet; the accepted main evidence keeps its original scope.
