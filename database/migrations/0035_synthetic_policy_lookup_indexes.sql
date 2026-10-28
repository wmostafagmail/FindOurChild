-- Support the existing exact text-context predicates without changing any
-- authorization function, row policy, grant, audit lock or approval condition.
CREATE INDEX synthetic_principal_context_lookup ON app.staff_principals((id::text));
CREATE INDEX synthetic_membership_context_lookup ON app.memberships(organization_id,(principal_id::text));
CREATE INDEX synthetic_case_grant_context_lookup ON app.case_grants(organization_id,case_id,(principal_id::text),permission,purpose);
CREATE INDEX synthetic_workflow_context_lookup ON platform.synthetic_workflow_grants(organization_id,scenario_id,(principal_id::text));
CREATE INDEX synthetic_report_integrity_lookup ON platform.report_versions(organization_id,case_id,id);
