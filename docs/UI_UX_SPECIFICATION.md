# UI/UX specification

Proposed Arabic-first mobile experience; no UI implemented in Phase 0.

## Information architecture

Public home presents distinct “report missing”, “report found”, “access my report”, “add information”, “contact NGO” and safety guidance actions. No child gallery, public search, map of found children or match-percentage display. If users enter through an assisted channel, authorized intake staff create the same attributed claims and give a safe receipt.

Staff workspace: assigned case queue, triage, case detail/evidence, lead review, investigation notes, approvals, safeguarding alerts and scoped activity. Organization administration and independent audit are separate permission-controlled sections. Empty lists do not reveal inaccessible case totals.

## Form flows

Missing report steps: relationship/safe contact → known child details → missing circumstances → optional historical photos/documents → purpose notice and review → neutral receipt. Found flow: immediate safety guidance → discovery circumstances and approximate location → known description/estimated age → organizational/custody information where known → safe optional photos → review/receipt. Exact custody details use a restricted staff follow-up.

Every uncertain field has “unknown” and where appropriate “approximate” controls; dates support ranges and capture precision. Each photo asks about capture date or age at capture, with uncertainty. Forms clearly distinguish reporter claims from later staff verification. No field forces invention of a birthday/name or police report.

Upload states: pending, uploading, awaiting scan, held/quarantined, ready and failed. Do not preview an unsafe original; a local pre-upload preview must disappear when navigating away and never persist in browser storage. After intake scan, multiple-face selection is performed by staff with explicit subject confirmation.

Server-side draft capability supports interrupted connections; no sensitive localStorage/IndexedDB/offline cache. Plain-language retries preserve safe in-memory values and avoid duplicate reports using idempotency keys. Warn before session expiry and provide a safe continuation route.

## Arabic/English and accessibility

Default locale ar-EG, html lang=ar and dir=rtl. English uses lang=en and dir=ltr. CSS uses logical properties; directional icons mirror only when meaning is directional. Telephone numbers, case IDs and Latin names use bdi or explicit LTR isolation inside RTL. Keep Arabic text in logical reading order rather than visually reversing strings.

Locale switch retains in-memory/server draft, returns focus to a meaningful heading and announces the change. Arabic and Western digit input is normalized for validation while preserving original submitted names. Initial calendar is clearly labeled Gregorian; optional calendar conversions require user confirmation and preserve source/precision. Time display follows user locale; storage UTC with original timezone (Egypt initially Africa/Cairo).

Target WCAG 2.2 AA as an engineering acceptance goal: keyboard-only operation, meaningful labels, focus visibility, inline+summary errors linked to fields, screen-reader status announcements, contrast, text scaling, reduced motion, 44px target design goal and no color-only status. Anti-bot challenges require an accessible alternative. NGO-approved Arabic wording must be checked by a fluent reviewer, not only automated translation.

Test narrow widths 320/360/390px, 200% zoom and desktop staff tables; compare RTL/LTR focus/reading order, mixed names, long Arabic labels and no horizontal overflow. No identifying names in document titles, browser history URLs or analytics events.

## Lead review screen

Display provenance and side-by-side authorized sanitized photos with recorded capture dates/uncertainty. Show “possible investigative lead” / “تطابق محتمل يحتاج إلى مراجعة بشرية” with supporting, contradictory and missing evidence, model/version and quality warnings. Do not show a percentage of identity. Reviewer can hold, reject or investigate with evidence/reason, and can request an independent review.

Separate identity evidence, claimant verification and custody authority into distinct review sections. Cross-NGO coordination initially reveals only a neutral task; counterpart identity/location stays withheld until field-scoped bilateral approval. Every sensitive image open is authorized/audited.

## Suggested bilingual microcopy — pending safeguarding review

| Context | Arabic | English |
|---|---|---|
| Missing report | الإبلاغ عن طفل مفقود | Report a missing child |
| Found report | الإبلاغ عن العثور على طفل | Report a found child |
| Unknown | غير معروف | Unknown |
| Approximate information | معلومات تقريبية | Approximate information |
| AI caution | هذه نتيجة أولية للمراجعة وليست إثباتًا للهوية | This is a lead for review, not proof of identity |
| Safe receipt | تم استلام البلاغ للمراجعة | Your report has been received for review |
| Contact | التواصل الآمن مع المؤسسة | Contact the NGO safely |

A receipt conveys intake status only, not that a child has been located. Notification wording must remain neutral even on a phone lock screen. Emergency guidance, contact numbers and claims about response times need NGO-approved maintained sources before publication.

