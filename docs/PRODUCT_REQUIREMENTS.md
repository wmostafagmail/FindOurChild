# Product requirements

Status: proposed specification, Phase 0, 23 October 2026. Policy statements describe required future behavior, not existing controls.

## Purpose and boundaries

Arabic-first, mobile-first reporting and NGO case management in Egypt. Two independently maintained registries hold missing and found reports; a case represents a report, not a globally established child identity. Multiple reports may describe one child, but merging them requires a reviewed duplicate decision. AI produces investigative leads only. Neither a high score nor a family resemblance proves identity or lawful custody.

Public users can report either case type, securely access their own submission, add information, contact the NGO through a relay and read safety guidance. There is no public directory, face search, claimant-facing candidate list, current shelter lookup or automatic reunion.

## Actors

| Actor | Permitted responsibility |
|---|---|
| Reporter / guardian / individual finder | Submit claims and evidence; view redacted own-report receipt after secure verification |
| Verified organizational reporter | Report within an approved organization and custody scope |
| Intake moderator | Review submissions, verify source and assign restricted cases |
| Caseworker | Investigate granted cases and proposed leads |
| Safeguarding approver | Assess disclosure, claimant risks and reunion readiness |
| Organization administrator | Manage membership; no implicit access to every sensitive case |
| Independent auditor | Read minimized audit records under mandate |
| Infrastructure administrator | Operate systems without default access to child records or media |

## Missing report fields

Case ID (server-generated UUID plus random receipt), original name and Arabic/English aliases with language and source, birth-date interval or estimated-age interval with reference date, optionally reliably reported sex, missing-time interval and precision/timezone, last known general location, description, distinguishing marks, clothing, multiple photographs, capture-date/age intervals for each, reporter relationship and encrypted contact, police reference where applicable, supporting documents, legal-basis record and source verification state.

Name, birth date, sex, photographs and police reference may be unknown. A missing field never becomes a fabricated value. Use explicit unknown, approximate, disputed and not-collected states; distinguish absent data from contradictory evidence. Date precision can be day/month/year/interval. Exact contact and location are separately restricted.

## Found report fields

Discovery-time interval and approximate public-report location, estimated age with reference date, known names/statements with provenance, current photos subject to welfare policy, distinguishing marks, reporting organization when known, custody authority and evidence, welfare status, safe-contact channel. Individual finders need an intake route even without a verified organization; their reports remain quarantined for organizational triage.

Current shelter, exact location and custody arrangements reside in a separate restricted record and never appear in reporter receipts or candidate notifications.

## Acceptance criteria

| ID | Requirement and observable acceptance |
|---|---|
| FR-01 | Separate missing/found forms in Arabic RTL and English LTR; switch preserves entered values |
| FR-02 | Submit with uncertain/unknown child attributes and without a photo; staff receive a triage task |
| FR-03 | Store original and submitted claims immutably by revision; verified facts cite evidence and verifier |
| FR-04 | Reporter receipt authorizes only own-submission updates after verification, never staff data |
| FR-05 | Multiple historical images retain capture-age uncertainty and explicit subject selection |
| FR-06 | Moderation, assignment, case grants and every lifecycle transition are audited |
| FR-07 | Duplicate cases can be linked without destructive merging or loss of provenance |
| FR-08 | Candidate reviews can be rejected, held or escalated with reason and independent review |
| FR-09 | Notifications target authorized staff and carry only a neutral task link |
| FR-10 | Identifying disclosure and safe reunion require separate, scoped approvals and authority evidence |
| FR-11 | Revocation and deletion cancel stale media links, jobs, indexes and queued notifications |
| FR-12 | No route exposes private child records across tenants without an explicit federation agreement and grant |
| FR-13 | Evidence addition, investigation notes, abuse reports and event history retain authorship/version |
| FR-14 | Screen-reader flow, keyboard use and narrow-screen RTL are verified before pilot |

## Lifecycle

`draft → submitted → triage → active → investigation → identity_confirmed → reunification_pending → reunited → closed`.
Triage may reject or quarantine abusive reports. Active/investigation may close as withdrawn, duplicate, unresolved or referred, with a reason; closure is not an identity determination. Reopening requires a supervisor decision. A lead has its own lifecycle and cannot change case status automatically.

Fraud suspicion pauses claimant contact without denying the child's care. Identity confirmation is distinct from custody authorization. A confirmed family relationship can still lead to a decision not to reunite when unsafe.

## Proposed service targets

Initial pilot sizing hypothesis: 50,000 cases, five photos per case, 30 concurrent staff, 100 report submissions/hour. Measure and revise before capacity commitments. Public shell ≤200 KB compressed initial JS; staff metadata reads p95 ≤500 ms at pilot load, excluding uploads/inference and external identity-provider login. Matching completion target ≤15 minutes under normal pilot load is provisional, not measured. No persistent browser cache of child media, forms or tokens; low-bandwidth resumability uses server-side drafts and safe retry.

Out of scope: surveillance feeds, live location tracking, inferred race/emotion/gender attributes, automated custody, production-data training and synthetic age progression in production.

