-- Contract 0001. Foundation only: runtime writes and all sensitive classification reads are denied.
CREATE ROLE foc_owner NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE foc_policy NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE foc_api LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE EXTENSION vector WITH SCHEMA public VERSION '0.8.7';
CREATE SCHEMA platform AUTHORIZATION foc_owner;
CREATE SCHEMA app AUTHORIZATION foc_owner;
REVOKE ALL ON SCHEMA platform, app FROM PUBLIC;
GRANT USAGE ON SCHEMA platform, app TO foc_api, foc_policy;
CREATE TABLE platform.environment (
 singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
 data_class text NOT NULL CHECK(data_class='synthetic'),
 schema_version text NOT NULL,
 instance_id uuid NOT NULL DEFAULT gen_random_uuid()
);
INSERT INTO platform.environment(data_class,schema_version) VALUES('synthetic','0001');
ALTER TABLE platform.environment OWNER TO foc_owner;
GRANT SELECT ON platform.environment TO foc_api;
CREATE TABLE platform.migrations(version text PRIMARY KEY, sha256 text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE platform.migrations OWNER TO foc_owner;
CREATE TABLE app.organizations(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), country_code char(2) NOT NULL, approved_status text NOT NULL CHECK(approved_status IN ('pending','approved','suspended')), policy_version text NOT NULL, suspended_at timestamptz);
CREATE TABLE app.staff_principals(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), oidc_issuer text NOT NULL, oidc_subject text NOT NULL, disabled_at timestamptz, UNIQUE(oidc_issuer,oidc_subject));

CREATE TABLE app.memberships (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 principal_id uuid NOT NULL REFERENCES app.staff_principals(id), role text NOT NULL CHECK(role IN ('reviewer','supervisor','safeguarding','authority','privacy','org_admin')), starts_at timestamptz NOT NULL DEFAULT now(), expires_at timestamptz NOT NULL, revoked_at timestamptz, CHECK(starts_at<expires_at), UNIQUE(organization_id,principal_id,role),
 PRIMARY KEY(organization_id,id)
);

CREATE TABLE app.cases (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 registry text NOT NULL CHECK(registry IN ('missing','found')), lifecycle text NOT NULL DEFAULT 'quarantined' CHECK(lifecycle IN ('quarantined','review','active','held','closed','deleted')), verification_status text NOT NULL DEFAULT 'unverified' CHECK(verification_status IN ('unverified','verified','disputed')), assigned_team_id uuid, revision bigint NOT NULL DEFAULT 1 CHECK(revision>0), opened_at timestamptz NOT NULL DEFAULT now(), closed_reason text, deleted_at timestamptz, deletion_generation bigint NOT NULL DEFAULT 0 CHECK(deletion_generation>=0),
 PRIMARY KEY(organization_id,id)
);

CREATE TABLE app.case_grants (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 principal_id uuid NOT NULL REFERENCES app.staff_principals(id), permission text NOT NULL CHECK(permission IN ('case.read','case.write','media.read','custody.read','matching.request','audit.read')), purpose text NOT NULL, granted_by uuid NOT NULL REFERENCES app.staff_principals(id), expires_at timestamptz NOT NULL, revoked_at timestamptz, UNIQUE(organization_id,case_id,principal_id,permission,purpose),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.report_access (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 capability_hash bytea NOT NULL CHECK(octet_length(capability_hash)=32), verified_contact_ref uuid, expires_at timestamptz NOT NULL, revoked_at timestamptz, UNIQUE(capability_hash),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.reporters (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 contact_ciphertext bytea NOT NULL, relationship_ciphertext bytea, verification_state text NOT NULL DEFAULT 'unverified', evidence_refs uuid[] NOT NULL DEFAULT '{}',
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.child_profiles (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 names_ciphertext bytea, birth_lower date, birth_upper date, birth_knowledge text NOT NULL CHECK(birth_knowledge IN ('unknown','estimated','known')), age_min_months integer CHECK(age_min_months>=0), age_max_months integer, age_reference_lower date, age_reference_upper date, description_ciphertext bytea, CHECK(birth_lower<=birth_upper), CHECK(age_min_months<=age_max_months), CHECK(age_reference_lower<=age_reference_upper), UNIQUE(organization_id,case_id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.name_variants (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 original_ciphertext bytea NOT NULL, normalized_search_ciphertext bytea NOT NULL, language text NOT NULL CHECK(language IN ('ar','en','other')), provenance uuid NOT NULL, normalization_version text NOT NULL,
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.assertions (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 field_name text NOT NULL, typed_value_ciphertext bytea NOT NULL, precision text NOT NULL, source_id uuid NOT NULL, state text NOT NULL CHECK(state IN ('claimed','verified','disputed')), verified_by uuid REFERENCES app.staff_principals(id), verified_at timestamptz, supersedes_id uuid, CHECK(state<>'verified' OR (verified_by IS NOT NULL AND verified_at IS NOT NULL)), FOREIGN KEY(organization_id,supersedes_id) REFERENCES app.assertions(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.registry_events (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 interval_lower timestamptz, interval_upper timestamptz, precision text NOT NULL, general_region_code text, original_timezone text NOT NULL, CHECK(interval_lower<=interval_upper),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.restricted_custody (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 location_ciphertext bytea NOT NULL, custody_authority_ref uuid NOT NULL, welfare_ciphertext bytea,
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.legal_bases (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 processing_purpose text NOT NULL, authority_type text NOT NULL, supporting_evidence_id uuid, approved_by uuid REFERENCES app.staff_principals(id), notice_version text NOT NULL, effective_from timestamptz NOT NULL, effective_until timestamptz NOT NULL, revoked_at timestamptz, CHECK(effective_from<effective_until),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.objects (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 bucket_class text NOT NULL CHECK(bucket_class IN ('quarantine','original','derivative')), opaque_key uuid NOT NULL, object_version text NOT NULL, content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32), bytes bigint NOT NULL CHECK(bytes>0 AND bytes<=20971520), detected_mime text NOT NULL, encryption_key_ref text NOT NULL, scan_status text NOT NULL DEFAULT 'pending' CHECK(scan_status IN ('pending','clean','infected','error')), expires_at timestamptz, UNIQUE(opaque_key,object_version),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.evidence_documents (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 object_id uuid NOT NULL, type text NOT NULL, claimed_origin text, verification text NOT NULL DEFAULT 'unverified', content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32), FOREIGN KEY(organization_id,object_id) REFERENCES app.objects(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
ALTER TABLE app.legal_bases ADD FOREIGN KEY(organization_id,supporting_evidence_id) REFERENCES app.evidence_documents(organization_id,id);

CREATE TABLE app.upload_intents (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 owner_access_id uuid NOT NULL, max_bytes bigint NOT NULL CHECK(max_bytes>0 AND max_bytes<=20971520), allowed_mime text[] NOT NULL, object_version text, nonce_hash bytea NOT NULL UNIQUE CHECK(octet_length(nonce_hash)=32), expires_at timestamptz NOT NULL, state text NOT NULL CHECK(state IN ('pending','uploaded','scanning','ready','rejected','expired')), FOREIGN KEY(organization_id,owner_access_id) REFERENCES app.report_access(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.photographs (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 original_object_id uuid NOT NULL, capture_lower date, capture_upper date, age_min_months integer CHECK(age_min_months>=0), age_max_months integer, age_reference_date date, source text NOT NULL, legal_basis_id uuid NOT NULL, submitted_at timestamptz NOT NULL DEFAULT now(), synthetic boolean NOT NULL DEFAULT false, CHECK(capture_lower<=capture_upper), CHECK(age_min_months<=age_max_months), FOREIGN KEY(organization_id,original_object_id) REFERENCES app.objects(organization_id,id), FOREIGN KEY(organization_id,legal_basis_id) REFERENCES app.legal_bases(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.photo_derivatives (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 photo_id uuid NOT NULL, object_id uuid NOT NULL, transform_version text NOT NULL, purpose text NOT NULL, exif_removed boolean NOT NULL CHECK(exif_removed), created_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(organization_id,photo_id) REFERENCES app.photographs(organization_id,id), FOREIGN KEY(organization_id,object_id) REFERENCES app.objects(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
CREATE TABLE app.model_manifests(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code_commit text NOT NULL CHECK(code_commit~'^[a-f0-9]{40}$'), weights_sha256 text NOT NULL CHECK(weights_sha256~'^[a-f0-9]{64}$'), weight_license_ref text NOT NULL, data_provenance_ref text NOT NULL, model_version text NOT NULL, dimension integer NOT NULL CHECK(dimension IN (128,512)), dtype text NOT NULL CHECK(dtype='float32'), metric text NOT NULL CHECK(metric IN ('cosine','l2')), detector_version text NOT NULL, alignment_version text NOT NULL, preprocessing_version text NOT NULL, validation_release text, status text NOT NULL CHECK(status IN ('research','validated','revoked')), UNIQUE(id,dimension));
CREATE TABLE app.embedding_spaces(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), model_manifest_id uuid NOT NULL, dimension integer NOT NULL CHECK(dimension IN (128,512)), metric text NOT NULL CHECK(metric IN ('cosine','l2')), normalization text NOT NULL, schema_version text NOT NULL, FOREIGN KEY(model_manifest_id,dimension) REFERENCES app.model_manifests(id,dimension), UNIQUE(id,dimension));

CREATE TABLE app.face_regions (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 photo_id uuid NOT NULL, detector_manifest_id uuid NOT NULL REFERENCES app.model_manifests(id), bounding_box double precision[] NOT NULL CHECK(array_length(bounding_box,1)=4), landmarks jsonb NOT NULL, subject_selection_status text NOT NULL CHECK(subject_selection_status IN ('pending','approved','rejected')), selected_by uuid REFERENCES app.staff_principals(id), selected_at timestamptz, quality_json jsonb NOT NULL, CHECK(subject_selection_status<>'approved' OR (selected_by IS NOT NULL AND selected_at IS NOT NULL)), FOREIGN KEY(organization_id,photo_id) REFERENCES app.photographs(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.embeddings (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 photo_id uuid NOT NULL, face_region_id uuid NOT NULL, space_id uuid NOT NULL, dimension integer NOT NULL CHECK(dimension IN (128,512)), vector public.vector NOT NULL, quality_json jsonb NOT NULL, processed_at timestamptz NOT NULL DEFAULT now(), preprocessing_version text NOT NULL, index_version text NOT NULL, source_revision bigint NOT NULL CHECK(source_revision>0), CHECK(public.vector_dims(vector)=dimension), FOREIGN KEY(space_id,dimension) REFERENCES app.embedding_spaces(id,dimension), FOREIGN KEY(organization_id,photo_id) REFERENCES app.photographs(organization_id,id), FOREIGN KEY(organization_id,face_region_id) REFERENCES app.face_regions(organization_id,id), UNIQUE(organization_id,photo_id,face_region_id,space_id,preprocessing_version,source_revision),
 PRIMARY KEY(organization_id,id,space_id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
) PARTITION BY LIST(space_id);

CREATE TABLE app.matching_runs (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 query_case_id uuid NOT NULL, revision_snapshot bigint NOT NULL CHECK(revision_snapshot>0), policy_version text NOT NULL, model_manifests uuid[] NOT NULL, search_version text NOT NULL, index_version text NOT NULL, requested_scope text NOT NULL, state text NOT NULL CHECK(state IN ('pending','running','held','completed','failed','cancelled')), completeness text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(organization_id,query_case_id) REFERENCES app.cases(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.candidate_leads (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 run_id uuid NOT NULL, query_case_id uuid NOT NULL, candidate_case_id uuid NOT NULL, rank integer NOT NULL CHECK(rank>0), model_scores_json jsonb NOT NULL, reasons_json jsonb NOT NULL, uncertainty_json jsonb NOT NULL, state text NOT NULL CHECK(state IN ('pending','held','rejected','escalated')), FOREIGN KEY(organization_id,run_id) REFERENCES app.matching_runs(organization_id,id), FOREIGN KEY(organization_id,query_case_id) REFERENCES app.cases(organization_id,id), FOREIGN KEY(organization_id,candidate_case_id) REFERENCES app.cases(organization_id,id), UNIQUE(organization_id,run_id,query_case_id,candidate_case_id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
CREATE TABLE app.federation_agreements(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_a uuid NOT NULL REFERENCES app.organizations(id), organization_b uuid NOT NULL REFERENCES app.organizations(id), purpose text NOT NULL, legal_basis_refs uuid[] NOT NULL, approvals uuid[] NOT NULL, valid_from timestamptz NOT NULL, valid_until timestamptz NOT NULL, revoked_at timestamptz, CHECK(organization_a<>organization_b AND valid_from<valid_until));
CREATE TABLE app.broker_candidate_edges(id uuid PRIMARY KEY DEFAULT gen_random_uuid(), agreement_id uuid NOT NULL REFERENCES app.federation_agreements(id), organization_a uuid NOT NULL, case_a uuid NOT NULL, organization_b uuid NOT NULL, case_b uuid NOT NULL, run_id uuid NOT NULL, restricted_evidence_refs uuid[] NOT NULL, disclosure_state text NOT NULL DEFAULT 'denied', FOREIGN KEY(organization_a,case_a) REFERENCES app.cases(organization_id,id), FOREIGN KEY(organization_b,case_b) REFERENCES app.cases(organization_id,id));

CREATE TABLE app.disclosure_grants (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 agreement_id uuid REFERENCES app.federation_agreements(id), recipient_ref uuid NOT NULL, field_mask text[] NOT NULL, purpose text NOT NULL, approver_ids uuid[] NOT NULL, snapshot_hash bytea NOT NULL CHECK(octet_length(snapshot_hash)=32), expires_at timestamptz NOT NULL, revoked_at timestamptz,
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.investigations (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 author uuid NOT NULL REFERENCES app.staff_principals(id), body_ciphertext bytea NOT NULL, evidence_refs uuid[] NOT NULL, revision bigint NOT NULL CHECK(revision>0), supersedes_id uuid,
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.notes (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 author uuid NOT NULL REFERENCES app.staff_principals(id), body_ciphertext bytea NOT NULL, evidence_refs uuid[] NOT NULL, revision bigint NOT NULL CHECK(revision>0), supersedes_id uuid,
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.duplicate_links (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 other_case_id uuid NOT NULL, state text NOT NULL CHECK(state IN ('proposed','confirmed','rejected')), reviewer uuid REFERENCES app.staff_principals(id), reason_ciphertext bytea NOT NULL, CHECK(case_id<>other_case_id), FOREIGN KEY(organization_id,other_case_id) REFERENCES app.cases(organization_id,id), UNIQUE(organization_id,case_id,other_case_id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.human_reviews (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 lead_id uuid NOT NULL, reviewer_id uuid NOT NULL REFERENCES app.staff_principals(id), outcome text NOT NULL CHECK(outcome IN ('hold','reject','escalate')), evidence_refs uuid[] NOT NULL, rationale_ciphertext bytea NOT NULL, reviewed_snapshot_hash bytea NOT NULL CHECK(octet_length(reviewed_snapshot_hash)=32), created_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(organization_id,lead_id) REFERENCES app.candidate_leads(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.reunification_plans (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 claimant_ref uuid NOT NULL, identity_decision_ref uuid NOT NULL, plan_revision bigint NOT NULL CHECK(plan_revision>0), snapshot_hash bytea NOT NULL CHECK(octet_length(snapshot_hash)=32), state text NOT NULL DEFAULT 'held' CHECK(state IN ('held','pending','approved','rejected','revoked','completed')),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.approvals (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 plan_id uuid, disclosure_id uuid, action text NOT NULL, scope text[] NOT NULL, signer uuid NOT NULL REFERENCES app.staff_principals(id), requested_by uuid NOT NULL REFERENCES app.staff_principals(id), authority_evidence_ref uuid NOT NULL, snapshot_hash bytea NOT NULL CHECK(octet_length(snapshot_hash)=32), expires_at timestamptz NOT NULL, revoked_at timestamptz, CHECK(signer<>requested_by), CHECK(num_nonnulls(plan_id,disclosure_id)=1), FOREIGN KEY(organization_id,plan_id) REFERENCES app.reunification_plans(organization_id,id), FOREIGN KEY(organization_id,disclosure_id) REFERENCES app.disclosure_grants(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
CREATE UNIQUE INDEX independent_plan_signer ON app.approvals(organization_id,plan_id,signer,action) WHERE revoked_at IS NULL;

CREATE TABLE app.handovers (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 plan_id uuid NOT NULL, witnessed_at timestamptz NOT NULL, witness_ids uuid[] NOT NULL CHECK(cardinality(witness_ids)>=2), authority_ref uuid NOT NULL, welfare_followup_ref uuid NOT NULL, FOREIGN KEY(organization_id,plan_id) REFERENCES app.reunification_plans(organization_id,id),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.outbox_events (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 type text NOT NULL, schema_version integer NOT NULL CHECK(schema_version=1), aggregate_id uuid NOT NULL, aggregate_revision bigint NOT NULL CHECK(aggregate_revision>0), dedup_key uuid NOT NULL, state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','leased','completed','dead','cancelled')), lease_until timestamptz, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5), next_attempt_at timestamptz NOT NULL DEFAULT now(), error_code text, deletion_generation bigint NOT NULL DEFAULT 0 CHECK(deletion_generation>=0), UNIQUE(organization_id,dedup_key),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.jobs (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 type text NOT NULL, schema_version integer NOT NULL CHECK(schema_version=1), aggregate_id uuid NOT NULL, aggregate_revision bigint NOT NULL CHECK(aggregate_revision>0), dedup_key uuid NOT NULL, state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','leased','completed','dead','cancelled')), lease_until timestamptz, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5), next_attempt_at timestamptz NOT NULL DEFAULT now(), error_code text, deletion_generation bigint NOT NULL DEFAULT 0 CHECK(deletion_generation>=0), UNIQUE(organization_id,dedup_key),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.notification_deliveries (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 event_id uuid NOT NULL, recipient_ref uuid NOT NULL, channel text NOT NULL CHECK(channel IN ('email','sms')), template_version text NOT NULL, attempt integer NOT NULL CHECK(attempt>0), provider_receipt text, status text NOT NULL CHECK(status IN ('pending','sent','failed')), FOREIGN KEY(organization_id,event_id) REFERENCES app.outbox_events(organization_id,id), UNIQUE(organization_id,event_id,recipient_ref,attempt),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.audit_events (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 sequence bigint GENERATED ALWAYS AS IDENTITY, event_id uuid NOT NULL UNIQUE, actor_ref uuid NOT NULL, action text NOT NULL, target_ref uuid NOT NULL, purpose text NOT NULL, outcome text NOT NULL, previous_hash bytea NOT NULL CHECK(octet_length(previous_hash)=32), event_hash bytea NOT NULL CHECK(octet_length(event_hash)=32), occurred_at timestamptz NOT NULL DEFAULT now(), UNIQUE(organization_id,sequence),
 PRIMARY KEY(organization_id,id)
);

CREATE TABLE app.deletion_requests (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 legal_hold_ref uuid, requested_at timestamptz NOT NULL DEFAULT now(), approved_at timestamptz, completed_at timestamptz, generation bigint NOT NULL CHECK(generation>0), purge_acknowledgments jsonb NOT NULL DEFAULT '{}', UNIQUE(organization_id,case_id,generation),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE TABLE app.tombstones (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 id uuid NOT NULL DEFAULT gen_random_uuid(),
 case_id uuid NOT NULL,
 legal_hold_ref uuid, requested_at timestamptz NOT NULL DEFAULT now(), approved_at timestamptz, completed_at timestamptz, generation bigint NOT NULL CHECK(generation>0), purge_acknowledgments jsonb NOT NULL DEFAULT '{}', UNIQUE(organization_id,case_id,generation),
 PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);

CREATE INDEX case_grants_lookup ON app.case_grants(organization_id,case_id,principal_id,permission,purpose);
CREATE INDEX cases_registry ON app.cases(organization_id,registry,lifecycle,opened_at);
CREATE INDEX jobs_claim ON app.jobs(state,next_attempt_at) WHERE state='pending';
-- Policy reader is NOLOGIN and never granted to runtime. Its only special access is ACL/identity metadata.
GRANT SELECT ON app.memberships, app.case_grants, app.staff_principals, app.organizations, app.cases TO foc_policy;
CREATE FUNCTION platform.case_permission(org uuid, cid uuid, required_permission text) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app
AS $$
 SELECT org::text = current_setting('foc.organization', true)
 AND EXISTS (SELECT 1 FROM app.organizations o WHERE o.id=org AND o.approved_status='approved' AND o.suspended_at IS NULL)
 AND EXISTS (SELECT 1 FROM app.staff_principals p WHERE p.id::text=current_setting('foc.principal',true) AND p.disabled_at IS NULL)
 AND EXISTS (SELECT 1 FROM app.memberships m WHERE m.organization_id=org AND m.principal_id::text=current_setting('foc.principal',true) AND m.starts_at<=now() AND m.expires_at>now() AND m.revoked_at IS NULL)
 AND EXISTS (SELECT 1 FROM app.case_grants g WHERE g.organization_id=org AND g.case_id=cid AND g.principal_id::text=current_setting('foc.principal',true) AND g.permission=required_permission AND g.purpose=current_setting('foc.purpose',true) AND g.expires_at>now() AND g.revoked_at IS NULL)
 AND EXISTS (SELECT 1 FROM app.cases c WHERE c.organization_id=org AND c.id=cid AND c.deleted_at IS NULL AND c.lifecycle<>'deleted')
$$;
ALTER FUNCTION platform.case_permission(uuid,uuid,text) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.case_permission(uuid,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.case_permission(uuid,uuid,text) TO foc_api;
DO $policies$
DECLARE t record;
BEGIN
 FOR t IN SELECT tablename FROM pg_tables WHERE schemaname='app' LOOP
  EXECUTE format('ALTER TABLE app.%I OWNER TO foc_owner',t.tablename);
  EXECUTE format('ALTER TABLE app.%I ENABLE ROW LEVEL SECURITY',t.tablename);
  EXECUTE format('ALTER TABLE app.%I FORCE ROW LEVEL SECURITY',t.tablename);
 END LOOP;
END $policies$;
CREATE POLICY policy_metadata ON app.memberships FOR SELECT TO foc_policy USING(true);
CREATE POLICY policy_metadata ON app.case_grants FOR SELECT TO foc_policy USING(true);
CREATE POLICY policy_metadata ON app.staff_principals FOR SELECT TO foc_policy USING(true);
CREATE POLICY policy_metadata ON app.organizations FOR SELECT TO foc_policy USING(true);
CREATE POLICY policy_metadata ON app.cases FOR SELECT TO foc_policy USING(true);
CREATE POLICY case_read ON app.cases FOR SELECT TO foc_api USING(platform.case_permission(organization_id,id,'case.read'));
GRANT SELECT ON app.cases TO foc_api;
-- All other tables have FORCE RLS but NO runtime policies or privileges in Phase 1A.
-- No writes, custody reads, media reads, biometrics, approvals, handovers, broker or admin bypass.
-- Phase 1B must add reviewed action-specific policies with negative tests; it cannot simply grant ALL.
ALTER DEFAULT PRIVILEGES FOR ROLE foc_owner IN SCHEMA app REVOKE ALL ON TABLES FROM PUBLIC;
