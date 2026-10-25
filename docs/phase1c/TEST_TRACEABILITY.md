# Phase 1C feature and execution traceability

Current status: **passed**. New cases remain pending until the full current-source hosted artifact passes and is independently verified. The Phase 0 151-feature/630-test snapshot and all accepted Phase 1A–1B entries are preserved.

Master registry: 178 features, 972 logical cases; 346 passed, 626 pending. Logical mappings are not browser execution counts.

Phase 1C inventory: 109 reporting cases, 1 real scanner-outage case, 6 actual TLS/BFF cases and 3 browser titles ×24 targets. Together with preserved 158 baseline/58 identity and four prior browser titles, full required execution is 332 Python and 168 TesterArmy cases.

Identity-boundary doubles in test_cases.py are explicitly scoped API/SQL tests; actual MFA/HTTP/browser lanes remain independently mandatory.

## RPTC-01 — Intake, uncertain claims, contact verification, private drafts, receipt/session scope and relay

Related requirements: FR-01, FR-02, FR-03, FR-04, FR-13, API-01, API-02, API-03, API-04, API-05, API-06, API-07, API-08, API-09. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_01_001 | `tests/reporting/test_intake.py::test_abuse_report_does_not_lookup_receipt` | passed |
| TC_RPTC_01_002 | `tests/reporting/test_intake.py::test_access_request_replay_keeps_original_verification_code` | passed |
| TC_RPTC_01_003 | `tests/reporting/test_intake.py::test_bilingual_safety_has_no_unapproved_emergency_numbers[ar]` | passed |
| TC_RPTC_01_004 | `tests/reporting/test_intake.py::test_bilingual_safety_has_no_unapproved_emergency_numbers[en]` | passed |
| TC_RPTC_01_005 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[cross_site]` | passed |
| TC_RPTC_01_006 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[expired]` | passed |
| TC_RPTC_01_007 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[missing_challenge]` | passed |
| TC_RPTC_01_008 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[other_browser]` | passed |
| TC_RPTC_01_009 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[oversized]` | passed |
| TC_RPTC_01_010 | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[wrong_origin]` | passed |
| TC_RPTC_01_011 | `tests/reporting/test_intake.py::test_code_one_use_contact_possession_not_guardianship` | passed |
| TC_RPTC_01_012 | `tests/reporting/test_intake.py::test_contact_verified_claimants_never_gain_staff_or_custody_authority[guardian]` | passed |
| TC_RPTC_01_013 | `tests/reporting/test_intake.py::test_contact_verified_claimants_never_gain_staff_or_custody_authority[parent]` | passed |
| TC_RPTC_01_014 | `tests/reporting/test_intake.py::test_expired_private_draft_is_not_recovered` | passed |
| TC_RPTC_01_015 | `tests/reporting/test_intake.py::test_idempotency_exact_replay_and_conflict` | passed |
| TC_RPTC_01_016 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[bad_timezone]` | passed |
| TC_RPTC_01_017 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[fabricated_unknown]` | passed |
| TC_RPTC_01_018 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[invalid_range]` | passed |
| TC_RPTC_01_019 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[missing_purpose]` | passed |
| TC_RPTC_01_020 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[production_contact]` | passed |
| TC_RPTC_01_021 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unapproved_notice]` | passed |
| TC_RPTC_01_022 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_field]` | passed |
| TC_RPTC_01_023 | `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_registry]` | passed |
| TC_RPTC_01_024 | `tests/reporting/test_intake.py::test_interval_validation_rejects_half_unknown` | passed |
| TC_RPTC_01_025 | `tests/reporting/test_intake.py::test_journal_quota_rejects_growth_without_destroying_original_claims` | passed |
| TC_RPTC_01_026 | `tests/reporting/test_intake.py::test_local_event_dates_preserve_original_timezone_and_calendar_interval` | passed |
| TC_RPTC_01_027 | `tests/reporting/test_intake.py::test_long_literal_and_structured_claims_match_closed_response_contracts` | passed |
| TC_RPTC_01_028 | `tests/reporting/test_intake.py::test_neutral_access_request_for_unknown_and_wrong_contact` | passed |
| TC_RPTC_01_029 | `tests/reporting/test_intake.py::test_private_server_draft_scope_revision_expiry_and_removal` | passed |
| TC_RPTC_01_030 | `tests/reporting/test_intake.py::test_public_command_replay_cannot_change_contact_or_duplicate_concern` | passed |
| TC_RPTC_01_031 | `tests/reporting/test_intake.py::test_reporter_csrf_and_arbitrary_evidence_denied` | passed |
| TC_RPTC_01_032 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[case_deleted]` | passed |
| TC_RPTC_01_033 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_code]` | passed |
| TC_RPTC_01_034 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_session]` | passed |
| TC_RPTC_01_035 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[five_attempts]` | passed |
| TC_RPTC_01_036 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[org_suspended]` | passed |
| TC_RPTC_01_037 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[paused_claimant]` | passed |
| TC_RPTC_01_038 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_access]` | passed |
| TC_RPTC_01_039 | `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_session]` | passed |
| TC_RPTC_01_040 | `tests/reporting/test_intake.py::test_reporter_logout_revokes_replayed_session` | passed |
| TC_RPTC_01_041 | `tests/reporting/test_intake.py::test_restricted_custody_never_in_receipt_submission_or_staff_projection` | passed |
| TC_RPTC_01_042 | `tests/reporting/test_intake.py::test_signed_anonymous_browser_limits_isolate_reporters_and_bound_peer_admission` | passed |
| TC_RPTC_01_043 | `tests/reporting/test_intake.py::test_supplement_immutable_original_and_replay` | passed |
| TC_RPTC_01_044 | `tests/reporting/test_intake.py::test_temporal_uncertainty_and_offset_ordering_are_not_fabricated[known_without_date]` | passed |
| TC_RPTC_01_045 | `tests/reporting/test_intake.py::test_temporal_uncertainty_and_offset_ordering_are_not_fabricated[reversed_actual_instants]` | passed |
| TC_RPTC_01_046 | `tests/reporting/test_intake.py::test_temporal_uncertainty_and_offset_ordering_are_not_fabricated[unknown_precision_with_date]` | passed |
| TC_RPTC_01_047 | `tests/reporting/test_intake.py::test_unknown_attributes_without_photo_create_independent_quarantined_reports[found]` | passed |
| TC_RPTC_01_048 | `tests/reporting/test_intake.py::test_unknown_attributes_without_photo_create_independent_quarantined_reports[missing]` | passed |
| TC_RPTC_01_049 | `tests/reporting/test_intake.py::test_untrusted_supplement_keys_and_values_remain_literal_unverified_claims` | passed |

## RPTC-02 — NGO moderation, scoped case access, assignments, evidence assertions, revisions and audit/outbox atomicity

Related requirements: FR-03, FR-06, FR-12, FR-13, API-12, API-13, API-14, API-15, API-16, API-18, API-22. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_02_001 | `tests/reporting/test_cases.py::test_assignment_bounded_to_active_same_org_staff` | passed |
| TC_RPTC_02_002 | `tests/reporting/test_cases.py::test_audit_failure_rolls_back_case_note_revision_and_outbox` | passed |
| TC_RPTC_02_003 | `tests/reporting/test_cases.py::test_case_projection_is_closed_and_has_no_custody_or_contacts` | passed |
| TC_RPTC_02_004 | `tests/reporting/test_cases.py::test_close_revokes_reporter_and_reopen_requires_supervisor` | passed |
| TC_RPTC_02_005 | `tests/reporting/test_cases.py::test_concurrent_case_writes_allow_one_revision_and_one_audit` | passed |
| TC_RPTC_02_006 | `tests/reporting/test_cases.py::test_evidence_assertions_require_same_case_clean_object_and_supervisor` | passed |
| TC_RPTC_02_007 | `tests/reporting/test_cases.py::test_fraudulent_parent_claim_pauses_contact_without_establishing_identity` | passed |
| TC_RPTC_02_008 | `tests/reporting/test_cases.py::test_media_gateway_reauthorizes_and_never_serves_original` | passed |
| TC_RPTC_02_009 | `tests/reporting/test_cases.py::test_moderation_notes_revision_and_idempotency` | passed |
| TC_RPTC_02_010 | `tests/reporting/test_cases.py::test_runtime_cannot_mutate_claims_sessions_or_worker_results` | passed |
| TC_RPTC_02_011 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[custody_target]` | passed |
| TC_RPTC_02_012 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[forged_csrf]` | passed |
| TC_RPTC_02_013 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[identity_target]` | passed |
| TC_RPTC_02_014 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[missing_evidence]` | passed |
| TC_RPTC_02_015 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[reunited_target]` | passed |
| TC_RPTC_02_016 | `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[self_approval]` | passed |
| TC_RPTC_02_017 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[expired_grant]` | passed |
| TC_RPTC_02_018 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[membership_expired]` | passed |
| TC_RPTC_02_019 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[org_admin_without_grant]` | passed |
| TC_RPTC_02_020 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[other_org]` | passed |
| TC_RPTC_02_021 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[principal_disabled]` | passed |
| TC_RPTC_02_022 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[revoked_grant]` | passed |
| TC_RPTC_02_023 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[unknown_case]` | passed |
| TC_RPTC_02_024 | `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[wrong_purpose]` | passed |
| TC_RPTC_02_025 | `tests/reporting/test_cases.py::test_verification_or_scanning_incomplete_blocks_active_transition` | passed |

## RPTC-03 — Actual ClamAV/S3 intake, encrypted versions, sanitization, publication authorization and crash/fencing recovery

Related requirements: FR-05, FR-11, API-10, API-11, API-18, T05, T06, T07, T10. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_03_001 | `tests/reporting/test_media.py::test_actual_worker_process_crash_recovers_lease_without_duplicate_publication[after_derivative]` | passed |
| TC_RPTC_03_002 | `tests/reporting/test_media.py::test_actual_worker_process_crash_recovers_lease_without_duplicate_publication[after_original]` | passed |
| TC_RPTC_03_003 | `tests/reporting/test_media.py::test_actual_worker_process_crash_recovers_lease_without_duplicate_publication[before_scan]` | passed |
| TC_RPTC_03_004 | `tests/reporting/test_media.py::test_bad_media_never_becomes_ready[animation]` | passed |
| TC_RPTC_03_005 | `tests/reporting/test_media.py::test_bad_media_never_becomes_ready[decompression_bomb]` | passed |
| TC_RPTC_03_006 | `tests/reporting/test_media.py::test_bad_media_never_becomes_ready[invalid_bytes]` | passed |
| TC_RPTC_03_007 | `tests/reporting/test_media.py::test_bad_media_never_becomes_ready[mime_mismatch]` | passed |
| TC_RPTC_03_008 | `tests/reporting/test_media.py::test_clamav_detects_controlled_eicar_test_signature_without_serving` | passed |
| TC_RPTC_03_009 | `tests/reporting/test_media.py::test_duplicate_completion_creates_only_one_scan_job` | passed |
| TC_RPTC_03_010 | `tests/reporting/test_media.py::test_lease_fencing_and_worker_database_least_privilege` | passed |
| TC_RPTC_03_011 | `tests/reporting/test_media.py::test_metadata_removed_at_byte_level_and_envelope_authentication` | passed |
| TC_RPTC_03_012 | `tests/reporting/test_media.py::test_multiple_photos_keep_individual_intents_and_no_automatic_identity` | passed |
| TC_RPTC_03_013 | `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/jpeg-JPEG]` | passed |
| TC_RPTC_03_014 | `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/png-PNG]` | passed |
| TC_RPTC_03_015 | `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/webp-WEBP]` | passed |
| TC_RPTC_03_016 | `tests/reporting/test_media.py::test_stale_worker_cannot_erase_versions_adopted_by_newer_lease` | passed |
| TC_RPTC_03_017 | `tests/reporting/test_media.py::test_storage_role_permissions_and_no_anonymous_access` | passed |
| TC_RPTC_03_018 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[checksum]` | passed |
| TC_RPTC_03_019 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_hash]` | passed |
| TC_RPTC_03_020 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_version]` | passed |
| TC_RPTC_03_021 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[expired_intent]` | passed |
| TC_RPTC_03_022 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[foreign_intent]` | passed |
| TC_RPTC_03_023 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[mime]` | passed |
| TC_RPTC_03_024 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[overwrite]` | passed |
| TC_RPTC_03_025 | `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[size]` | passed |
| TC_RPTC_03_026 | `tests/reporting/test_media.py::test_upload_quota_and_oversize_rejected_before_storage` | passed |
| TC_RPTC_03_027 | `tests/reporting/test_media.py::test_worker_publish_rechecks_current_authority_and_deletion_generation[case_deleted]` | passed |
| TC_RPTC_03_028 | `tests/reporting/test_media.py::test_worker_publish_rechecks_current_authority_and_deletion_generation[generation]` | passed |
| TC_RPTC_03_029 | `tests/reporting/test_media.py::test_worker_publish_rechecks_current_authority_and_deletion_generation[org_suspended]` | passed |
| TC_RPTC_03_030 | `tests/reporting/test_media.py::test_worker_publish_rechecks_current_authority_and_deletion_generation[report_access]` | passed |

## RPTC-04 — Orphan erasure acknowledgments, outbox recipient reauthorization, neutral notification dedup and dead letters

Related requirements: FR-09, FR-11, T10, T11, T13. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_04_001 | `tests/reporting/test_workers.py::test_exhausted_worker_leases_dead_letter_without_unsafe_publication` | passed |
| TC_RPTC_04_002 | `tests/reporting/test_workers.py::test_expired_orphan_version_is_erased_before_acknowledgment` | passed |
| TC_RPTC_04_003 | `tests/reporting/test_workers.py::test_neutral_notification_sink_deduplicates_and_has_no_child_payload` | passed |
| TC_RPTC_04_004 | `tests/reporting/test_workers.py::test_revoked_notification_recipient_is_excluded_at_send_time` | passed |
| TC_RPTC_04_005 | `tests/reporting/test_workers.py::test_unbound_storage_write_is_erased_before_orphan_acknowledgment` | passed |

## RPTC-05 — Actual scanner service outage fails closed with bounded retries/dead letters

Related requirements: T05, T10, T17. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_05_001 | `tests/resilience/test_scanner_outage.py::test_actual_scanner_outage_keeps_media_quarantined_and_retries_bounded` | passed |

## RPTC-06 — Actual TLS Next/Keycloak/API/PG/S3/ClamAV/background-worker workflows

Related requirements: FR-02, FR-04, FR-06, FR-12, T01, T02, T04, T05, T07. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_06_001 | `tests/reporting_http/test_live.py::test_real_bff_verified_reporter_has_only_own_submission_and_one_time_code` | passed |
| TC_RPTC_06_002 | `tests/reporting_http/test_live.py::test_real_mfa_case_projection_and_tenant_denials` | passed |
| TC_RPTC_06_003 | `tests/reporting_http/test_live.py::test_real_two_photo_uploads_complete_through_background_worker` | passed |
| TC_RPTC_06_004 | `tests/reporting_http/test_live.py::test_real_media_gateway_serves_derivative_and_denies_original` | passed |
| TC_RPTC_06_005 | `tests/reporting_http/test_live.py::test_real_moderation_notes_and_stale_revision_are_atomic` | passed |
| TC_RPTC_06_006 | `tests/reporting_http/test_live.py::test_real_suspicious_claim_pause_revokes_reporter_without_identity_or_release` | passed |

## RPTC-07 — Official TesterArmy missing/found/reporter/moderation journeys, ar/en a11y, RTL, keyboard/zoom and all 24 targets

Related requirements: FR-01, FR-02, FR-04, FR-14, T01, T02, T04, T05, T15. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: [verified sanitized results](../../artifacts/phase1c-sanitized/results.json).

| Case ID | Executable selector | Status |
|---|---|---|
| TC_RPTC_07_001 | `TC_RPT_BROWSER_MISSING_INTAKE` | passed |
| TC_RPTC_07_002 | `TC_RPT_BROWSER_FOUND_INTAKE` | passed |
| TC_RPTC_07_003 | `TC_RPT_BROWSER_NGO_MODERATION` | passed |

## API, jobs, database and safeguarding crosswalk

| Boundary | Executable coverage / status |
|---|---|
| `POST /v1/public/reports/missing` (api_01) | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[cross_site]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[expired]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[missing_challenge]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[other_browser]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[oversized]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[wrong_origin]`; `tests/reporting/test_intake.py::test_idempotency_exact_replay_and_conflict`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[bad_timezone]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[fabricated_unknown]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[invalid_range]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[missing_purpose]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[production_contact]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unapproved_notice]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_field]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_registry]`; `tests/reporting/test_intake.py::test_unknown_attributes_without_photo_create_independent_quarantined_reports[missing]`; **passed** |
| `POST /v1/public/reports/found` (api_02) | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[cross_site]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[expired]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[missing_challenge]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[other_browser]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[oversized]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[wrong_origin]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[bad_timezone]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[fabricated_unknown]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[invalid_range]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[missing_purpose]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[production_contact]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unapproved_notice]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_field]`; `tests/reporting/test_intake.py::test_intake_rejects_invalid_or_unapproved_payload[unknown_registry]`; `tests/reporting/test_intake.py::test_restricted_custody_never_in_receipt_submission_or_staff_projection`; `tests/reporting/test_intake.py::test_unknown_attributes_without_photo_create_independent_quarantined_reports[found]`; **passed** |
| `POST /v1/public/access-requests` (api_03) | `tests/reporting/test_intake.py::test_access_request_replay_keeps_original_verification_code`; `tests/reporting/test_intake.py::test_neutral_access_request_for_unknown_and_wrong_contact`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[case_deleted]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_code]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_session]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[five_attempts]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[org_suspended]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[paused_claimant]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_access]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_session]`; **passed** |
| `POST /v1/public/access-exchanges` (api_04) | `tests/reporting/test_intake.py::test_code_one_use_contact_possession_not_guardianship`; `tests/reporting/test_intake.py::test_contact_verified_claimants_never_gain_staff_or_custody_authority[guardian]`; `tests/reporting/test_intake.py::test_contact_verified_claimants_never_gain_staff_or_custody_authority[parent]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[case_deleted]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_code]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_session]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[five_attempts]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[org_suspended]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[paused_claimant]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_access]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_session]`; **passed** |
| `GET /v1/reporter/submission` (api_05) | `tests/reporting/test_intake.py::test_code_one_use_contact_possession_not_guardianship`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[case_deleted]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_code]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[expired_session]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[five_attempts]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[org_suspended]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[paused_claimant]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_access]`; `tests/reporting/test_intake.py::test_reporter_expiry_revocation_and_verification_fail_safely[revoked_session]`; `tests/reporting/test_intake.py::test_restricted_custody_never_in_receipt_submission_or_staff_projection`; **passed** |
| `POST /v1/reporter/supplements` (api_06) | `tests/reporting/test_intake.py::test_reporter_csrf_and_arbitrary_evidence_denied`; `tests/reporting/test_intake.py::test_supplement_immutable_original_and_replay`; `tests/reporting/test_intake.py::test_untrusted_supplement_keys_and_values_remain_literal_unverified_claims`; **passed** |
| `POST /v1/reporter/contact` (api_07) | `tests/reporting/test_intake.py::test_public_command_replay_cannot_change_contact_or_duplicate_concern`; `tests/reporting/test_intake.py::test_reporter_csrf_and_arbitrary_evidence_denied`; **passed** |
| `POST /v1/public/abuse-reports` (api_08) | `tests/reporting/test_intake.py::test_abuse_report_does_not_lookup_receipt`; `tests/reporting/test_intake.py::test_public_command_replay_cannot_change_contact_or_duplicate_concern`; **passed** |
| `GET /v1/public/safety` (api_09) | `tests/reporting/test_intake.py::test_bilingual_safety_has_no_unapproved_emergency_numbers[ar]`; `tests/reporting/test_intake.py::test_bilingual_safety_has_no_unapproved_emergency_numbers[en]`; **passed** |
| `POST /v1/reporter/upload-intents` (api_10) | `tests/reporting/test_media.py::test_multiple_photos_keep_individual_intents_and_no_automatic_identity`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[checksum]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_hash]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_version]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[expired_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[foreign_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[mime]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[overwrite]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[size]`; `tests/reporting/test_media.py::test_upload_quota_and_oversize_rejected_before_storage`; **passed** |
| `POST /v1/reporter/upload-intents/{id}/complete` (api_11) | `tests/reporting/test_media.py::test_duplicate_completion_creates_only_one_scan_job`; `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/jpeg-JPEG]`; `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/png-PNG]`; `tests/reporting/test_media.py::test_real_clamav_versioned_storage_and_sanitized_derivative[image/webp-WEBP]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[checksum]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_hash]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_version]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[expired_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[foreign_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[mime]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[overwrite]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[size]`; **passed** |
| `GET /v1/staff/cases` (api_12) | `tests/reporting/test_cases.py::test_case_projection_is_closed_and_has_no_custody_or_contacts`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[expired_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[membership_expired]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[org_admin_without_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[other_org]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[principal_disabled]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[revoked_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[unknown_case]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[wrong_purpose]`; **passed** |
| `GET /v1/staff/cases/{id}` (api_13) | `tests/reporting/test_cases.py::test_case_projection_is_closed_and_has_no_custody_or_contacts`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[expired_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[membership_expired]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[org_admin_without_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[other_org]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[principal_disabled]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[revoked_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[unknown_case]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[wrong_purpose]`; **passed** |
| `POST /v1/staff/cases/{id}/transitions` (api_14) | `tests/reporting/test_cases.py::test_close_revokes_reporter_and_reopen_requires_supervisor`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[custody_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[forged_csrf]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[identity_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[missing_evidence]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[reunited_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[self_approval]`; `tests/reporting/test_cases.py::test_verification_or_scanning_incomplete_blocks_active_transition`; **passed** |
| `POST /v1/staff/cases/{id}/assignments` (api_15) | `tests/reporting/test_cases.py::test_assignment_bounded_to_active_same_org_staff`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[expired_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[membership_expired]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[org_admin_without_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[other_org]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[principal_disabled]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[revoked_grant]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[unknown_case]`; `tests/reporting/test_cases.py::test_staff_case_scope_denies_existence_and_cross_organization_exposure[wrong_purpose]`; **passed** |
| `POST /v1/staff/cases/{id}/assertions` (api_16) | `tests/reporting/test_cases.py::test_evidence_assertions_require_same_case_clean_object_and_supervisor`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[custody_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[forged_csrf]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[identity_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[missing_evidence]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[reunited_target]`; `tests/reporting/test_cases.py::test_sensitive_workflow_bypasses_have_no_effect[self_approval]`; **passed** |
| `POST /v1/staff/photos/{id}/subject-selection` (api_17) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `GET /v1/staff/media/{id}/content` (api_18) | `tests/reporting/test_cases.py::test_media_gateway_reauthorizes_and_never_serves_original`; `tests/reporting/test_media.py::test_storage_role_permissions_and_no_anonymous_access`; `tests/reporting_http/test_live.py::test_real_media_gateway_serves_derivative_and_denies_original`; **passed** |
| `POST /v1/staff/cases/{id}/matching-runs` (api_19) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `GET /v1/staff/cases/{id}/leads` (api_20) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/leads/{id}/reviews` (api_21) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/cases/{id}/notes` (api_22) | `tests/reporting/test_cases.py::test_audit_failure_rolls_back_case_note_revision_and_outbox`; `tests/reporting/test_cases.py::test_concurrent_case_writes_allow_one_revision_and_one_audit`; `tests/reporting/test_cases.py::test_moderation_notes_revision_and_idempotency`; **passed** |
| `POST /v1/staff/duplicate-links` (api_23) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/disclosure-requests` (api_24) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/disclosure-requests/{id}/approvals` (api_25) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/reunification-plans` (api_26) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/reunification-plans/{id}/approvals` (api_27) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/reunification-plans/{id}/handover` (api_28) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/cases/{id}/deletion-requests` (api_29) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `GET /v1/staff/audit-events` (api_30) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `GET /v1/staff/analytics` (api_31) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `POST /v1/staff/organizations/{id}/memberships` (api_32) | Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending |
| `GET /health/live` (foundation_liveness) | Preserved baseline API/contract/readiness suite |
| `GET /health/ready` (foundation_readiness) | Preserved baseline API/contract/readiness suite |
| `GET /openapi.json` (foundation_contract) | Preserved baseline API/contract/readiness suite |
| `GET /identity/login` (login_identity_login_get) | Preserved 58-case identity inventory and MFA browser regression |
| `GET /identity/callback` (callback_identity_callback_get) | Preserved 58-case identity inventory and MFA browser regression |
| `GET /identity/me` (me_identity_me_get) | Preserved 58-case identity inventory and MFA browser regression |
| `POST /identity/logout` (logout_identity_logout_post) | Preserved 58-case identity inventory and MFA browser regression |
| `POST /identity/organizations/{org}/memberships` (membership_identity_organizations__org__memberships_post) | Preserved 58-case identity inventory and MFA browser regression |
| `GET /identity/organizations/{org}/cases/{case}/permission` (permission_identity_organizations__org__cases__case__permission_get) | Preserved 58-case identity inventory and MFA browser regression |
| `GET /identity/organizations/{org}/audit` (audit_identity_organizations__org__audit_get) | Preserved 58-case identity inventory and MFA browser regression |
| `POST /v1/public/intake-challenges` (reporting_intake_challenge) | `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[cross_site]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[expired]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[missing_challenge]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[other_browser]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[oversized]`; `tests/reporting/test_intake.py::test_challenge_and_transport_boundaries[wrong_origin]`; `tests/reporting/test_intake.py::test_signed_anonymous_browser_limits_isolate_reporters_and_bound_peer_admission`; **passed** |
| `PUT /v1/reporter/upload-intents/{id}/content` (reporting_upload_content) | `tests/reporting/test_media.py::test_multiple_photos_keep_individual_intents_and_no_automatic_identity`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[checksum]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_hash]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[complete_version]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[expired_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[foreign_intent]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[mime]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[overwrite]`; `tests/reporting/test_media.py::test_upload_binding_rejects_tampering_and_replay[size]`; `tests/reporting/test_media.py::test_upload_quota_and_oversize_rejected_before_storage`; **passed** |
| `POST /v1/staff/cases/{id}/moderation` (reporting_moderation) | `tests/reporting/test_cases.py::test_fraudulent_parent_claim_pauses_contact_without_establishing_identity`; `tests/reporting/test_cases.py::test_moderation_notes_revision_and_idempotency`; `tests/reporting_http/test_live.py::test_real_suspicious_claim_pause_revokes_reporter_without_identity_or_release`; **passed** |
| `GET /v1/public/drafts` (reporting_draft_get) | `tests/reporting/test_intake.py::test_expired_private_draft_is_not_recovered`; `tests/reporting/test_intake.py::test_private_server_draft_scope_revision_expiry_and_removal`; **passed** |
| `POST /v1/public/drafts` (reporting_draft_post) | `tests/reporting/test_intake.py::test_private_server_draft_scope_revision_expiry_and_removal`; **passed** |
| `POST /v1/reporter/logout` (reporting_reporter_logout) | `tests/reporting/test_intake.py::test_reporter_logout_revokes_replayed_session`; **passed** |
| media.scan, lease/retry/dead-letter/publication | RPTC-03/05: actual scanner, worker roles, crash checkpoints, fences and deletion-generation negatives |
| outbox/notification delivery | RPTC-04: neutral payload, current grants, idempotent private sink, exhausted lease |
| quarantine/orphan/draft expiry | RPTC-01/04: expiry, actual immutable version erasure and acknowledgment; whole-case/backup erasure remains pending |
| cases/grants/memberships/org/principal | Preserved DB/RLS/identity regression plus RPTC-02 current grant/tenant/role/transaction tests |
| claims/codes/sessions/commands/restricted intake/journals | RPTC-01/02: hashed capabilities, replay/expiry, no direct runtime reads/writes, closed projections, custody exclusion |
| objects/intents/photos/derivatives/evidence | RPTC-03: immutable key/version/hash, quota, MIME/bomb/EICAR, metadata stripping, exact-owner scope and current media grants |
| audit/outbox | RPTC-02/04: same-transaction rollback, non-sensitive envelopes, role separation; operational WORM export remains a release gate |
| fraudulent parent/guardian, found location, original media, tenant leaks | RPTC-01/02/06/07 and permanent security guards; exact denials/no-effects |
| biometric search, self-approval, release/custody bypass | Existing permanent disabled-route guards plus RPTC-02/06/07; no positive production capability implemented |
| model accuracy, federation, operational custody/reunion/deletion/legal hold | Original future cases remain pending; browser tests cannot validate those unimplemented capabilities |
