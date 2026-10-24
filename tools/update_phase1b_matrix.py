"""Append identity executables without changing the immutable Phase 0/1A evidence or future pending cases."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'docs/testing/test-matrix.json'
    matrix=json.loads(path.read_text())
    matrix['features']=[f for f in matrix['features'] if not f['feature_id'].startswith('IDN-')]
    identity=json.loads((ROOT/'docs/phase1b/required-tests.json').read_text())['python']
    baseline=json.loads((ROOT/'docs/phase1a/required-tests.json').read_text())['python']
    groups=[('IDN-01','JWT issuer/audience/signature/MFA/time/nonce and IdP failure boundaries',[t for t in identity if '/test_tokens.py::' in t]),('IDN-02','Anonymous, forged, callback state and Secure-cookie boundaries',[t for t in identity if '/test_boundaries.py::' in t and 'test_real_' not in t and 'test_live_revocation' not in t]),('IDN-03','Real Keycloak MFA, BFF/API, organizations, case grants, CSRF, audit and live revocation',[t for t in identity if 'test_real_' in t or 'test_live_revocation' in t]),('IDN-04','Real PostgreSQL session ACLs, role elevation denial, context isolation and audit integrity',[t for t in baseline if '/test_identity.py::' in t]),('IDN-05','TesterArmy real TLS MFA/tenant/CSRF/logout, Arabic switch, every configured browser',['TC_ID_BROWSER_MFA_TENANT_LOGOUT'])]
    evidence_path=ROOT/'artifacts/phase1b-sanitized/results.json'
    evidence=json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
    if evidence.get("gate",{}).get("status")=="passed":
        sys.path.insert(0,str(ROOT))
        from scripts.fingerprint import fingerprint
        if evidence["gate"]["source_digest"] != fingerprint():
            raise SystemExit("Stale evidence cannot mark current identity cases passed")
    executed={t['id'] for key in ['python','identity','browser'] for t in evidence.get(key,[]) if t.get('status')=='passed'} if evidence.get('gate',{}).get('status')=='passed' else set()
    for fid,title,tests in groups:
        feature={'feature_id':fid,'category':'identity_security','source':'phase1b/ARCHITECTURE.md','title':title,'suite':'browser' if fid=='IDN-05' else 'coordinated_python_api_database_security','phase_introduced':'1B','positive_scenarios':'Explicitly provisioned active synthetic staff completes MFA and only its scoped permitted operations','negative_scenarios':'Malformed/expired/forged/revoked credentials, unavailable verifier, unknown IDs and invalid mutations deny safely','security_authorization_scenarios':'Cross-tenant and self-elevation denied; org role alone grants no case data; Secure cookies and exact Origin/CSRF; append-only minimized audit','edge_cases':'Expiry/idle/revocation, missing context, nonce mismatch, algorithm confusion, token audience and MFA evidence, missing mandatory test results','fixture_ids':['FX-IDP','FX-BASE'],'expected_outcomes':'Allowed operations match exact DTO/status; denied operations reveal no child/location/token data or unauthorized state; all mandatory targets execute','test_cases':[]}
        for number,node in enumerate(tests,1):
            feature['test_cases'].append({'test_case_id':f'TC_{fid.replace("-","_")}_{number:03d}','kind':'positive_negative_security_edge','scenario':node,'planned_file':'tests/browser/identity.e2e.ts' if fid=='IDN-05' else node.split('::')[0],'planned_selector':node,'planned_command':'.venv/bin/python -m scripts.dev browser' if fid=='IDN-05' else '.venv/bin/python -m scripts.identity_test' if '/identity/' in node else '.venv/bin/python -m scripts.dev test','expected_outcome':feature['expected_outcomes'],'required_from_phase':'1B','phase1b_required':True,'status':'passed' if node in executed else 'pending','execution_evidence':{'artifact':'artifacts/phase1b-sanitized/results.json','source_digest':evidence['gate']['source_digest']} if node in executed else None})
        matrix['features'].append(feature)
    matrix['scope']='Preserved Phase 0/1A baseline plus explicitly scoped Phase 1B identity executables; no Phase 1C'
    matrix['application_test_status']='phase1b_hosted_validation_passed_awaiting_review' if executed else 'phase1b_hosted_validation_pending; prior passing evidence is historical Phase 1A'
    path.write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    output=['# Phase 1B executable traceability','','The immutable 151-feature/630-test Phase 0 baseline and existing 1A mappings remain preserved in the master matrix. Original future operations remain pending; the new identity routes do not activate the 32 Phase 1C/domain endpoints. Each IDN entry in the JSON matrix records positive/negative/security/edge scenarios, fixture IDs, outcomes, exact executable selectors, evidence and current status. Browser count is 24 executions for each logical title.','','| Feature | Executable cases | Current evidence |','|---|---:|---|']
    for fid,title,tests in groups:
        output.append(f'| {fid}: {title} | {len(tests)} | '+('verified artifact' if all(t in executed for t in tests) else 'pending final hosted gate')+' |')
    output+=['','| API operation | Executable coverage |','|---|---|','| GET /identity/login, GET /identity/callback, GET /identity/me | IDN-02, IDN-03, IDN-05 |','| POST /identity/logout | IDN-03, IDN-05; CSRF and revoked-session negatives |','| POST /identity/organizations/{org}/memberships | IDN-03 admin flow; IDN-04 sensitive-role/self-elevation negatives |','| GET /identity/organizations/{org}/cases/{case}/permission | IDN-03 cross-org/unknown/grant/membership expiry and revocation; IDN-04 context |','| GET /identity/organizations/{org}/audit | IDN-03 role/tenant/token-leak negatives; IDN-04 chain and mutation denial |','','Platform sessions and all new SQL functions: IDN-04 plus IDN-03 real API/session flows. No background worker is delivered in 1B; worker/event/safeguarding cases remain pending in the master matrix. Separate unit doubles in IDN-01 do not count as real IdP/browser/database execution.','']
    (ROOT/'docs/phase1b/TEST_TRACEABILITY.md').write_text('\n'.join(output))


if __name__=='__main__':main()
