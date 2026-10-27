# Phase 2D specification review and validation

Prepared 2026-10-27. This package contains **proposed documentation only**. No Phase 2D application, API, schema, permission, fixture, model, runtime dependency, worker or test implementation has started. No additional implementation phase is authorized by the strategic clarification.

## Delivered proposal

- [Implementation specification](IMPLEMENTATION_SPEC.md): synthetic-only scope, paired staff access, evidence comparison, uncertainty/explanations, decisions, collaboration, independent review, audit, failure behavior, Arabic/English UX, proposed ADRs and implementation/exit sequence.
- [Proposed contracts/data](PROPOSED_CONTRACTS_AND_DATA.md): 14 closed operations in a distinct synthetic namespace, eight proposed relations, purpose/tenant/case/media/action boundaries, optimistic/idempotent transactions, worker/recovery and disabled operational routes.
- [Proposed test matrix](PROPOSED_TEST_MATRIX.md): 20 features / 80 logical scenarios, eight proposed official TesterArmy journeys / 192 additional browser executions; every new case pending.
- [Revised development roadmap](../DEMONSTRATION_ROADMAP.md): production-representative demonstration first; licensed working recognition, fictional longitudinal multi-photo retrieval, NGO workflow and complete stakeholder journey before institutional operating approval processes. Explicit authorization and asset rights still gate future work; institutional approvals do not block synthetic development.

This package is separate from the Phase 2C PR. The original `aca8a2a3c9aa2fd04840caacf53086fe9bc45a76` was pushed unchanged, without force/history rewriting, to `codex/phase-2c-readiness-assessment`. [Draft PR #7](https://github.com/wmostafagmail/FindOurChild/pull/7) contains exactly its original six documentation paths, including the Phase 2B engineering-acceptance/evidence records. No Phase 2D file is added to that PR.

## Hosted Phase 2C verification

Every step passed on exact documentation head `aca8a2a3c9aa2fd04840caacf53086fe9bc45a76` in [push run 40474607704](https://github.com/wmostafagmail/FindOurChild/actions/runs/40474607704) and [required PR run 40474700684](https://github.com/wmostafagmail/FindOurChild/actions/runs/40474700684). The synthetic PR merge checkout `e0c32be7d9b832afe9efa557a5abd3fa62e9e0ba` has an identical tree to the review head. PR #7 remains draft/unmerged; these are not future merged-main results.

Each full workflow passed **554 Python executions, 168 official TesterArmy browser executions (56 each Chromium/Firefox/WebKit), 24 application migrations, real PostgreSQL/RLS, API/security/authorization, worker/integration and both application and isolated-lab recovery checks**. Coverage: **1305/1384 = 94.29%**. No mandatory skip, test retry, external-model step or ordinary Playwright-only acceptance test is counted as success. The original required inventories and pinned runner/web/Playwright dependency 0.21.3/0.15.3/1.64.1 are unchanged.

Independently downloaded archives matched GitHub SHA-256 and were verified read-only against 191 committed execution-source blobs, all 53 payload hashes, required test/target IDs, migration/coverage/isolation fields, 48 input-free PNGs and 168 minimized traces:

| Run | Artifact | Archive SHA-256 |
|---|---|---|
| Push 40474607704 | 12720274274 | `7958501ec52e96d29eff7ed34f9726a13e60b4061a1aa1e50ea27727765e2ee6` |
| PR 40474700684 | 12720154787 | `a20d7fe0f700aa7c86db99825a190153b22cae26067a7c2162b37d3c83ccb0b5` |

[Machine-readable verification](phase2c-hosted-verification.json) preserves the sanitized proof. Source fingerprint for both is `2513f3776af7a360d7c22acc864bd537435ecf7b959c7e2f33f031787baf27fa`. The existing independent verifier was invoked with `--no-copy`, so checked-in historical artifacts were not overwritten:

```sh
GIT_DIR=/private/tmp/foc-phase1a-hosted-git python3 tools/verify_phase2b_evidence.py \
  artifacts/raw/phase2b-hosted-history/40474700684-artifact.json \
  artifacts/raw/phase2b-hosted-history/40474700684.zip \
  aca8a2a3c9aa2fd04840caacf53086fe9bc45a76 --no-copy
```

Push archive verification used the analogous push-run paths. Original diagnostics/dumps remain private and ignored. No real child images, weights, embeddings or sensitive browser content are published by this task.

## Documentary/source validation

The proposal was checked against an exact Git archive of `aca8a2a`, avoiding the existing cloud-backed filesystem issue. Relative Markdown links resolve; the new verification JSON parses; the proposed inventory has 20 distinct feature IDs, 80 logical case IDs, 14 proposed HTTP operations and eight browser journeys. No proposed test is marked passed. Executable sources match all 191 previously verified hashes; seven accepted locks, 24 applied migrations and the 190-feature / 1,216-case central registry remain unchanged. Existing 572 passed engineering cases and 644 pending future cases retain their statuses.

The existing pinned Python environment ran `FOC_GIT_DIR=/private/tmp/foc-phase1a-hosted-git /private/tmp/foc-phase1a-runtime/.venv/bin/python -m scripts.check_foundation` against the archived tree plus proposal. Result: **180 foundation structural/configuration checks and both historical Phase 0 validators passed**. These documentary/configuration checks do not execute new Phase 2D features. Phase 2D application tests executed: **zero**. Proposed biometric demonstration/model tests executed: **zero**.

The six Phase 2C PR files are frozen. New proposal files are documentation only on a separate local specification branch; their later documentation commit is not the head of the hosted runs above. No hosted pass is claimed for a nonexistent Phase 2D implementation. The pre-existing global cloud-backed working-tree read limitation is not claimed fixed; scoped files/index/source preservation are checked without replacing old evidence.

## Assumptions, limits and review decisions

The proposed synthetic org/people/cases are fixtures, not institutional approval or independently verified real humans. Existing geometric images are not faces. Scenario ranks, fictional age intervals and synthetic grants do not establish model accuracy, real longitudinal robustness, lawful authority, identity or custody. All eight real profiles remain blocked; no new model/image is selected or acquired.

The dedicated namespace/relations, closed narrative templates, paired write requirement, distinct canonical person binding, eight browser journeys and planning performance budgets are **proposals for owner review**. Actual migration IDs, final DTO/schema identifiers, dependency needs, implementation selector counts, reference-machine capacity and manual Arabic/accessibility results are not yet verified. Index/worker/restore details require real synthetic integration testing after explicit implementation authorization.

Rights-cleared demonstration model/image work can proceed in a separately authorized development scope without waiting for institutional operating approval. It must still resolve exact artifact/purpose rights, safe loading and input provenance; it cannot reclassify an uncleared existing model or use real missing-child data. Real-child evaluation and operational recognition retain their separate legal/safeguarding/scientific gates. No publisher, NGO, government body, custodian or external model was contacted by this specification work.

Stop here for owner review. No Phase 2D code, model acquisition, actual child-data processing, public search, identity decision, disclosure or production matching has begun.
