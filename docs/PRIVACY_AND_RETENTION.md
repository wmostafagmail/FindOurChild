# Privacy and retention — proposed

Prepared 23 October 2026. Legal interpretation, controller/processor allocation, notices and retention schedules require qualified Egyptian counsel and NGO approval. No operational legal basis is established by this research package.

## Egypt legal evidence and uncertainty

Egypt's Personal Data Protection Law No. 151/2020 is available as an [official-gazette text hosted by ILO NATLEX](https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/111246/EGY111246%20Ara.pdf). Its machine-extracted Arabic is corrupted in the research tool; no detailed article interpretation is asserted from that extraction.

The Egyptian Ministry of Social Solidarity describes the law, the PDPC's licensing/permit role and executive regulations issued in November 2025 with a one-year adjustment period ending in November 2026 in its [official workshop notice](https://www.moss.gov.eg/المركز-الإعلامي/الأخبار/التضامن-الاجتماعي-تنظم-ورشة-عمل-حول-قانون-حماية-البيانات-الشخصية-بالتعاون-وزارة-الاتصالات-وتكنولوجيا-المعلومات/). Counsel must confirm the exact applicable deadline, Decree 816/2025 text, regulator guidance and required authorizations before any real-data pilot. The [PDPC site](https://pdpc.gov.eg/) returned no extractable content in this review; current portal procedures were not independently verified.

The [Egyptian State Information Service child-law description](https://hrightsstudies.sis.gov.eg/en/right-to-decent-life/rights-of-the-child/child/) and [ILO amendment record](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/details?p3_isn=45791) identify the Child Law and amendments. A 2008 translation is not a complete current consolidated statute. Counsel must review subsequent amendments, custody/disclosure rules and child-protection duties.

These sources justify a current legal review, not a claim of compliance or an assumed exception for missing children. Do not assume charitable/non-commercial status clears face-model restrictions or permits biometric processing.

## Questions counsel must decide

- Which NGO/entity is controller, joint controller or processor for each registry, federation match and disclosure?
- What lawful basis/authority permits each collection, biometric comparison and sharing purpose, particularly a found child without a verified guardian?
- What current licensing, sensitive-data/children's-data requirements, guardian authority, child assent and documentation apply?
- What data-residency, cross-border transfer and subcontractor requirements apply to storage, IdP, messages, diagnostics and backups?
- What regulator/data-subject breach notifications, deadlines and procedures apply?
- How should access/correction/withdrawal/deletion requests be verified without empowering an abusive claimant?
- Which police/custody/NGO record-retention or legal-hold duties limit erasure?
- What approvals are required for research, independently verified evaluation data, later model training and foreign model providers?

## Purpose limitation and minimization

Record purpose, legal authority/evidence, policy/notice version, approver, dates and withdrawal/review status for reporting, storage, matching, investigation, disclosure and research separately. A consent checkbox alone cannot establish lawful guardian authority. Intake must route uncertain legal basis to restricted review and prohibit biometric processing until resolved.

Arabic/English notices explain who receives data, uncertainty of matching, contact options, retention, rights and transfer arrangements in plain language. Collect only needed facts; exact custody is separate from general reported locations. No ad trackers, external image analysis APIs or production telemetry containing child data.

## Provisional engineering TTLs — not legal retention decisions

| Data class | Proposed default for design/testing | Approval/exception |
|---|---|---|
| Unsubmitted server draft | Expire after 7 days inactivity | NGO to approve accessibility/recovery balance |
| Expired upload intent/orphan object | Intent 10 minutes; orphan purge within 24 hours | Bound quota; successful evidence not orphaned |
| Malicious/invalid quarantine | Restricted review up to 7 days, then purge | Scoped incident evidence hold only |
| Active case originals/claims | No fixed automatic purge until lawful case schedule approved | Periodic purpose review every 90 days proposed; real-data launch blocked without maximum retention |
| Closed case media/embeddings | Proposed purge 90 days after closure and final authority review | Counsel may require a different period or lawful hold |
| Model evaluation artifacts | Approved protocol expiry only | No production dataset reuse |
| Reporter verification codes | Proposed 10-minute expiry, one-time use | Never retain plaintext codes |
| Neutral notification metadata | Proposed 90 days | Provider agreement and legal audit needs |
| Operational logs | Proposed 30 days, minimized | Security incidents held separately |
| Audit/approval evidence | Period unresolved | Signed legal schedule required; no “keep forever” default |
| Encrypted backups | Proposed rolling 35 days | Tombstone replay and restore isolation mandatory |

No production ingestion is allowed with an unresolved active/closed case or audit retention schedule. Erasure timelines are measured from authorized approval and validated for every store, not assumed from a database DELETE.

## Erasure and access requests

Authenticate requesters through safe staff procedures without revealing child existence. Record scope and lawful holds, seek child-protection advice if a claimant threatens welfare, and respond through a verified channel.

Purge workflow: tombstone/revoke first; stop pending processing/disclosure; remove source/derivative objects and historical versions, vectors/index rows, caches, export packages and provider copies; obtain per-store acknowledgments; verify negative retrieval. Retain minimum pseudonymous audit proof only under approved legal basis. Key destruction counts as erasure only where key scope makes all intended copies unrecoverable without erasing unrelated records.

Backups are segregated, encrypted and expire on schedule; no claim of immediate deletion from immutable copies. Restore applies the independently maintained deletion ledger before access. Legal holds have scope, authority, owner, expiry/review dates and restricted access; they do not justify indefinite operational reuse.

## Assessments and release evidence

Complete a child-focused privacy/data-protection impact assessment, processing inventory, data flow/vendor register, disclosure agreement, lawful basis/notice review, rights procedures, incident plan and retention sign-off. Obtain actual approved hosting region and processor contracts. Any later training protocol is a separate decision; no training on production child photographs by default.

