# Database schema specification

Design contract v0.1, not an executed migration. PostgreSQL with pgvector; UUID keys, UTC timestamptz for instants, original timezone/precision retained, optimistic integer revisions, explicit organization ownership. All case-owned foreign keys use composite `(organization_id, id)` references to prevent accidental tenant mixing.

## Relations

| Table | Principal columns and constraints |
|---|---|
| organizations | id, country_code, approved_status, policy_version, suspended_at |
| staff_principals | id, oidc_issuer, oidc_subject unique pair, disabled_at |
| memberships | organization_id, principal_id, role, starts_at, expires_at; no global tenant role |
| cases | organization_id, id, registry missing/found, lifecycle, verification_status, assigned_team_id, revision, opened_at, closed_reason, deleted_at |
| case_grants | organization_id, case_id, principal/team, permission, purpose, granted_by, expires_at, revoked_at |
| report_access | id, case_id, capability_hash, verified_contact_ref, expires_at, revoked_at; never raw token |
| reporters | organization_id, id, encrypted contact and relationship, verification state and evidence |
| child_profiles | organization_id, case_id, original names, birth interval, age interval/reference date, description; claimed view only |
| name_variants | organization_id, case_id, original_text, normalized_search_text, language, provenance, normalization_version |
| assertions | organization_id, id, case_id, field_name, typed_value, precision, source_id, state claimed/verified/disputed, verified_by/at, supersedes_id |
| registry_events | organization_id, case_id, missing/discovery interval, precision, general_region_code, original_timezone |
| restricted_custody | organization_id, case_id, encrypted exact location, custody authority, welfare flags; separate grants/table |
| legal_bases | organization_id, id, case_id, processing_purpose, authority_type, supporting_evidence_id, approved_by, notice_version, effective interval, revoked_at |
| evidence_documents | organization_id, id, case_id, object_id, type, claimed_origin, verification, content_sha256 |
| upload_intents | organization_id, id, case_id, owner_access_id, expected media constraints, object_version, nonce_hash, expires_at, state |
| photographs | organization_id, id, case_id, original_object_id, capture interval, age interval/reference date, source, legal_basis_id, submitted_at, synthetic boolean default false |
| objects | organization_id, id, case_id, bucket_class, opaque_key, object_version, hash, bytes, detected_mime, encryption_key_ref, scan_status, expires_at |
| photo_derivatives | organization_id, id, photo_id, object_id, transform_version, purpose, exif_removed, created_at |
| face_regions | organization_id, id, photo_id, detector_manifest_id, bounding_box, landmarks, subject_selection_status, selected_by/at, quality_json |
| model_manifests | id, code_commit, weights_sha256, weight_license_ref, data_provenance_ref, model_version, dimension, dtype, metric, detector_version, alignment_version, preprocessing_version, validation_release, status |
| embedding_spaces | id, model_manifest_id, dimension, metric, normalization, schema_version; immutable compatibility identity |
| embeddings | organization_id, id, case_id, photo_id, face_region_id, space_id, dimension, vector, quality_json, processed_at, preprocessing_version, index_version, source_revision |
| matching_runs | organization_id, id, query_case_id, revision_snapshot, policy_version, model_manifests, search/index versions, requested_scope, state, completeness, created_at |
| candidate_leads | organization_id, id, run_id, query_case_id, candidate_case_id, rank, model_scores_json, reasons_json, uncertainty_json, state; unique run/query/candidate |
| federation_agreements | id, approved organization pair, purpose, legal_basis_refs, validity, approvals, revoked_at |
| broker_candidate_edges | broker-only id, agreement_id, opaque case endpoints, run_id, restricted evidence refs, disclosure_state |
| disclosure_grants | agreement_id, both case refs, recipient, exact field mask, purpose, approver IDs, snapshot_hash, expires_at, revoked_at |
| investigations / notes | organization_id, id, case_id, author, body encrypted, evidence_refs, revision, supersedes_id |
| duplicate_links | owning organization, two case IDs, proposed/confirmed/rejected, reviewer, reason; no destructive merge |
| human_reviews | organization_id, id, lead_id, reviewer_id, outcome, evidence_refs, rationale, reviewed_snapshot_hash, created_at |
| reunification_plans | organization_id, id, case_id, claimant_ref, identity_decision_ref, plan_revision, snapshot_hash, state |
| approvals | organization_id, id, plan/disclosure target, action, scope, independent signer, authority_evidence_ref, snapshot_hash, expires_at, revoked_at |
| handovers | organization_id, id, plan_id, witnessed_at, witness IDs, authority_ref, welfare_followup_ref |
| jobs / outbox_events | organization_id, id, type, schema_version, aggregate_id/revision, dedup_key, state, lease_until, attempts, next_attempt_at, error_code |
| notification_deliveries | organization_id, id, event_id, recipient_ref, channel, template_version, attempt, provider_receipt, status; no message body in audit |
| audit_events | organization_id, monotonic sequence, event_id, actor_ref, action, opaque target refs, purpose, outcome, previous_hash, event_hash, timestamp |
| deletion_requests / tombstones | organization_id, case_id, legal_hold_ref, requested/approved/completed timestamps, generation, store-specific purge acknowledgments |

## Type and integrity rules

Unknown values are NULL plus an explicit knowledge/precision state where needed. An age estimate is a nonnegative closed interval in months, anchored to a date interval. Min ≤ max for all intervals; no default “0 years.” Verified assertions require verifier, timestamp and evidence; originals remain retained under policy. Photograph capture dates inconsistent with stated birth dates create review flags, not silent correction.

Each photo may have many detected faces but only approved subject selections are embedded. Multiple children require separate cases and selected regions; the original evidence object may be access-controlled through explicit references rather than copying a shared public URL. No arbitrary `child_id` deduplication from model scores.

Use one physical vector partition/table per immutable embedding space/dimension; dimension CHECK and foreign key must match its manifest. An illustrative 512-dimension partition uses `vector(512)`; 128-dimension models use a different partition. Match query must include the same space, metric, preprocessing compatibility, active legal basis and authorization scope on both sides. Unique processing key: photo + region + manifest + preprocessing + source revision. Inference outputs cannot overwrite older provenance.

## RLS design

Enable and FORCE RLS on every tenant-owned table. API role is non-owner and has no BYPASSRLS. Each transaction sets a trusted, transaction-local principal and organization context after server-side token/membership validation; user input cannot set it. Missing context denies access. Pool reuse must not retain a tenant setting.

Policies combine organization membership, non-expired grants, purpose and object classification. Separate restricted-custody and broker policies; organization administrator alone cannot read them. The broker service role only executes tightly scoped matching routines; it does not inherit arbitrary tenant reads. Maintenance/migrations use separately controlled credentials.

Conceptual policy predicate, to translate into reviewed SQL:
`row.organization_id = authorized_org AND active_case_permission(principal, row.case_id, requested_action) AND not_deleted(row)`.
Functions must avoid recursive RLS, use fixed search paths and audited security-definer scope where unavoidable. Acceptance requires database-level tenant tests, not only API filters.

## Indexing and search

B-tree on organization/lifecycle/update time and grants; normalized name index and region/date indexes for independent metadata retrieval. Start exact vector scans within the authorized opposite registry. Introduce HNSW per space only after comparing Recall@K against exact search under realistic tenant/grant filters; iterative scans and post-filter shortfalls must be reported. A vector index never replaces authorization.

## Migrations and erasure

Expand-contract migrations, separate data backfills, resumable processing, migration ledger and verified restore before destructive steps. Keep model migrations side by side; switch alias only after shadow validation. No mixed-space fallback.

A deletion transaction first tombstones the case, revokes grants/receipts and increments deletion generation, then cancels work. Purge originals, derivatives, embeddings, indexes, caches, exports and provider artifacts; retain only legally approved minimized audit references. Legal holds block only scoped erasure with documented authority and periodic review. Restores replay the tombstone ledger before any application access resumes.

