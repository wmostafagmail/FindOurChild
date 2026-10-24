-- Contract release 0001, second forward migration. No domain runtime permissions are enabled.
CREATE TABLE app.idempotency_records(
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 principal_scope_hash bytea NOT NULL CHECK(octet_length(principal_scope_hash)=32),
 operation text NOT NULL CHECK(length(operation) BETWEEN 1 AND 128),
 idempotency_key uuid NOT NULL,
 request_sha256 bytea NOT NULL CHECK(octet_length(request_sha256)=32),
 state text NOT NULL CHECK(state IN ('pending','completed')),
 response_status integer CHECK(response_status BETWEEN 200 AND 599),
 response_ciphertext bytea,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 PRIMARY KEY(organization_id,id),
 UNIQUE(organization_id,principal_scope_hash,operation,idempotency_key),
 CHECK(created_at<expires_at),
 CHECK((state='pending' AND response_status IS NULL AND response_ciphertext IS NULL)
 OR (state='completed' AND response_status IS NOT NULL AND response_ciphertext IS NOT NULL))
);
ALTER TABLE app.idempotency_records OWNER TO foc_owner;
ALTER TABLE app.idempotency_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.idempotency_records FORCE ROW LEVEL SECURITY;
-- Default deny: scoped replay, reauthorization and expiration processing require Phase 1C implementation.

ALTER TABLE app.outbox_events
 ADD COLUMN aggregate_type text NOT NULL DEFAULT 'case' CHECK(aggregate_type IN ('case','photograph','face_region','embedding','matching_run','lead','disclosure','approval','reunification_plan','deletion_request','notification')),
 ADD COLUMN occurred_at timestamptz NOT NULL DEFAULT now(),
 ADD COLUMN correlation_id uuid NOT NULL DEFAULT gen_random_uuid(),
 ADD COLUMN policy_version text NOT NULL DEFAULT 'synthetic-foundation-v1' CHECK(length(policy_version) BETWEEN 1 AND 128),
 ADD CONSTRAINT closed_event_type CHECK(type IN ('report.submitted','media.uploaded','media.ready','media.quarantined','subject.selected','embedding.ready','matching.requested','matching.completed','lead.reviewed','disclosure.approved','approval.revoked','reunification.recorded','deletion.requested','deletion.completed','notification.requested'));
-- id is the envelope event_id, and type is event_type; no child payload column is permitted.
ALTER TABLE app.matching_runs ADD CONSTRAINT query_owns_run CHECK(case_id=query_case_id);
ALTER TABLE app.candidate_leads ADD CONSTRAINT query_owns_lead CHECK(case_id=query_case_id AND query_case_id<>candidate_case_id);

-- Tenant identity alone is insufficient when a child-owned object belongs to another case in the same tenant.
-- Add case-consistent object/plan/event foreign keys before any such runtime policies are activated.
DO $scope$
DECLARE t record; f record;
BEGIN
 FOR t IN SELECT c.oid,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='app' AND c.relkind='r'
  AND EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=c.oid AND a.attname='case_id' AND NOT a.attisdropped)
 LOOP
  EXECUTE format('ALTER TABLE app.%I ADD CONSTRAINT %I UNIQUE(organization_id,case_id,id)',t.relname,'case_identity_'||t.relname);
 END LOOP;
 FOR f IN SELECT con.oid,child.relname AS child,parent.relname AS parent,
  (SELECT a.attname FROM pg_attribute a WHERE a.attrelid=con.conrelid AND a.attnum=con.conkey[2]) AS field
  FROM pg_constraint con JOIN pg_class child ON child.oid=con.conrelid JOIN pg_class parent ON parent.oid=con.confrelid
  JOIN pg_namespace n ON n.oid=child.relnamespace
  WHERE con.contype='f' AND n.nspname='app' AND array_length(con.conkey,1)=2 AND parent.relkind='r'
  AND EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=child.oid AND a.attname='case_id' AND NOT a.attisdropped)
  AND EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=parent.oid AND a.attname='case_id' AND NOT a.attisdropped)
 LOOP
  EXECUTE format('ALTER TABLE app.%I ADD CONSTRAINT %I FOREIGN KEY(organization_id,case_id,%I) REFERENCES app.%I(organization_id,case_id,id)',f.child,'same_case_'||f.child||'_'||f.field,f.field,f.parent);
 END LOOP;
END $scope$;
GRANT SELECT ON platform.migrations TO foc_api;
