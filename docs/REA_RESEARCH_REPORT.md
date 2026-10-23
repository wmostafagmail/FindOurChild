# REA research report

Phase 0 research conducted 23 October 2026. Findings concern selected public repository snapshots, not a deployed Find Our Child application. All fourteen required repositories, including REA itself, have exact reviewed commits in [repository-lock.json](research/repository-lock.json). See [capability matrix](OPEN_SOURCE_CAPABILITY_MATRIX.md) for all ten requested assessment dimensions per repository.

## Method and authority

Used the connected GitHub plugin to resolve repository commit heads, enumerate source trees and read selected README/license/manifests/source/tests at those immutable SHAs. Retained examined text in [source-evidence.json](research/source-evidence.json). A repository's documentation establishes what upstream describes; inspected source establishes syntax/implementation within that file; only observed execution establishes runtime outcomes. No upstream application or test suite was installed/executed, and no production/child data was accessed.

Reviewed public targets only, without authentication bypass, commercial tool activation, surveillance capture or model downloads. All architectural recommendations are inference/design decisions with limits, not REA-generated proof of correctness.

Confidence convention: **high** = direct source/config observation within stated scope; **medium** = documentation/indexed-paper evidence or a supported design inference; **unverified** = untested runtime, licensing entitlement, benchmark transfer or security assertion.

## Official REA and installation verification

Official repository: [morluto/rea](https://github.com/morluto/rea), reviewed commit `9fd78a74f84a8e924bd58e7deaf5934bfb24f53c`. README, installation, client configuration, CLI, JavaScript workflow and package manifest inspected. REA-authored code uses MIT; third-party tools retain independent licenses.

Official docs support `npx rea-agents setup`, exact `--client codex`, dry run, `--skill=false`, reviewed `--yes` apply and scoped `doctor --client codex`. They require a client restart after registration. The package registry identifies rea-agents 6.7.0 with the official repository and integrity:
`sha512-yhIx2ioJYYT1C/tONfYeitC6LhnKmCh+ZwRUOgYuhSc733lGhkkt73zhug9WmLgxoMdKuqIYGCoBfD4fXkOhFw==`.

Important discrepancy: reviewed main's package manifest requires Node ^22.23.4 / ^24.22.1 / >=26.12.1, while the **published** 6.7.0 package registry permits ^22.19.0 / ^24.11.0 / >=26.0.0. Local Node is 24.18.0, npm 11.16.0. Used the exact published package, which passed version/doctor/static analysis here; did not claim execution of reviewed main or equivalence between its bytes and npm. Source main and published package are separate evidence identities.

Installed research-only tooling in `tools/rea/node_modules`, package and transitive versions/integrities pinned by package-lock. Lifecycle install scripts disabled; this does not establish optional native-provider functionality. A fresh temporary `npm ci --ignore-scripts` completed, installed 174 packages and `rea --version` returned 6.7.0. npm's reported vulnerability count is only the point-in-time registry audit, not an independent security audit.

Initial sandboxed setup preview failed because a macOS ownership helper attempted compiler-cache writes outside the workspace. Retained diagnosis, then ran the documented preview/apply with the required filesystem permission. No installer rejection or application workaround was used.

Codex setup result: ready, configured_codex. Configuration: `/Users/waleedmostafa/.codex/config.toml`, backup `/Users/waleedmostafa/.codex/config.toml.rea.backup`. The final configured command is `/Users/waleedmostafa/.codex/tools/find-our-child-rea-6.7.0/node_modules/.bin/rea mcp`, using a byte-identical copy of the verified clean installation. The first workspace-path registration was refreshed through reviewed setup, with a recovery backup. Unrelated settings were managed by REA's documented backup-preserving setup. Only Codex was selected, no native provider or bundled skill installed.

Scoped doctor: healthy=true, Node and Codex registration checks pass. Environment-wide healthy=false because optional native providers/skill/other client registrations are absent. This is not an application defect. The current chat has not reloaded the new MCP server; **restart Codex for live tool discovery**. CLI execution below is independently observed and sufficient for these static investigations. Live MCP invocation remains unverified.

## Investigation 1: FindTrace original HTML

Final evidence refresh: integrity checks found one extra trailing newline introduced by snapshot publication. Saved targets were corrected to byte-exact fetched text, verified against source-evidence.json. A clean-tool probe on the workspace target then failed with `Directory entry changed during read: index.html`; the typed failure is retained in [workspace-integrity-failure.json](research/rea/workspace-integrity-failure.json). Its underlying filesystem cause is not established. Three workspace refresh processes stalled and were stopped; they are not successful evidence. Final successful outputs below were collected sequentially from byte-identical copies under `/private/tmp/foc-rea-exact-targets` using the independently clean-installed 6.7.0 runtime. Their Evidence subjects retain those actual temporary paths. No integrity policy was weakened or failure reclassified as success. The final Codex runtime was copied with its exact lockfile to the durable Codex tools directory and setup/doctor refreshed there.

Target: pinned `raigaurav26/FindTrace` index.html snapshot. Full five-path tree contained README.md, index.html, docs/ieee_paper.tex, docs directory and .gitignore; no LICENSE file identified.

Command: `rea analyze-javascript-application <absolute-target-directory> --format json`.

Evidence: [original HTML result](research/rea/findtrace-analysis.json); exit 0. Evidence ID `ev_53589939030f4c9ee9652e4840da8d6d808c5e67cb422c1c7e0991036c797f9f`. Inventory reads one HTML file. REA identifies the external face-api.js 0.22.2 script reference. **Coverage is partial**: the tool explicitly says one inline JavaScript body beginning at original line 2797 was not analyzed. Therefore absence of endpoint/storage findings here is not evidence of their absence.

No browser opened and no remote script fetched. REA's “electron-renderer” graph classification of HTML is a static graph role, not evidence FindTrace is an Electron application.

## Investigation 2: FindTrace exact derived JavaScript

To address inline coverage, extracted the exact nonempty inline script body as inert text with a line map and original SHA-256. [Extraction provenance](research/targets/findtrace-extracted/extraction-provenance.json) distinguishes derived artifact identity from original HTML. This is research preparation, not modifying or building the target.

[Derived result](research/rea/findtrace-extracted-analysis.json), exit 0; evidence ID `ev_da4842f3cb5e492ef7fa7e30896c7d892a84aeb1b0424460d7fd42a4bf589048`. One JavaScript file parsed, 9,271 AST nodes visited, zero parse failures, graph coverage still **partial**. Findings include localStorage and literal fetch endpoint candidates. Exact source inspection confirms:

| Observation | Direct source location | Confidence / boundary |
|---|---|---|
| Local case/settings storage | index.html around lines 2849–2873 | High syntax evidence; not runtime persistence test |
| Match label converts Euclidean distance to a percentage | around 3373–3382 | High; source uses 100 − distance×100, differing from README's threshold-based confidence formula; neither is a calibrated identity probability |
| IP geolocation fallback | around 3428–3434 | High literal request/geolocation source evidence; request never sent here |
| Procedural image aging | generateAgedImage at about 3513 onward | High canvas/source evidence; no longitudinal recognition validation |
| External descriptive prediction API request | around 3675–3681 | High: prompt includes case descriptors/name/marks/notes and fetch targets api.anthropic.com/v1/messages; no request made and no evidence it succeeds |
| README local-only privacy and publication claims | README | Advertised claims not established by source or publication evidence |

The external request contradicts a blanket claim that data never leaves the browser as a source-level privacy guarantee. It does **not** prove the call succeeds or that any real child data was transmitted. Reuse license not identified; production base rejected independently on architecture/safeguarding grounds. Source snapshot is inspection evidence, not a licensed reusable module.

## Investigation 3: selected Immich interfaces

Selected two commit-pinned TypeScript files: FaceController and MachineLearningRepository, with paths and hashes in the manifest. [REA result](research/rea/immich-selected-analysis.json), exit 0; evidence ID `ev_f473af83436bd6d19a0fa2277ad26cf1880f9bb0c13f80b153c8230812b095e9`. Two parsed source files, zero parse failures, 1,636 AST nodes visited.

Graph reports complete coverage **for the two supplied files only**; imports/dependency implementations were not supplied, so this is not whole-application coverage. Direct source confirms guarded face CRUD/reassignment and an ML boundary using multipart predict requests with model-task options. Separate Python recognition-source inspection shows the detection dependency, alignment and serialized embedding output.

No running server, auth session, JavaScript facade execution, HTTP contract, photo processing or integration test was exercised. REA observations aid architecture/interface study; auth guards in source do not prove effective multi-tenant safeguarding at runtime.

## Cross-repository source and test evidence

The capability matrix links inspected implementation contracts: CompreFace architecture/REST/plugin, InsightFace FaceAnalysis, DeepFace facade/setup, AdaFace inference/channel conversion, PhotoPrism model-provenance guards/license gates, pgvector SQL/control, Qdrant manifest/startup, FastAPI application/manifest, Keycloak pom, Temporal architecture/go.mod and MinIO object interface/go.mod.

Sample test source was read for CompreFace embedding comparison, DeepFace SFace self-retrieval/verification consistency, Immich Playwright face editing, PhotoPrism model-license gates, pgvector HNSW vector operators, Qdrant search aggregation and FastAPI TestClient behavior. These demonstrate available testing patterns only; **none was run**. No standalone automated test suite identified in FindTrace's small tree; AdaFace has validation scripts rather than evidence of child-protection acceptance tests.

## Conclusions and gaps

Recommended modular FastAPI domain backend + bilingual Next.js client, PostgreSQL/pgvector, private media adapter, Keycloak staff identity and isolated versioned workers. Use PostgreSQL outbox/leases initially, defer Temporal/Qdrant until measured justification. Source reviews support these design choices; they do not measure our workload.

No required repository provides the entire safeguarding/authority workflow. No pretrained recognition artifact is cleared operationally. No longitudinal Egyptian child benchmark, production threshold, hardware sizing or model accuracy is established. Legal/privacy source review is scoped in PRIVACY_AND_RETENTION; qualified counsel remains necessary.

REA was useful for static integration boundaries and explicit limitations; reverse-engineering a live third-party application was unnecessary with available source and no authorized runtime target. Later, inspect only our synthetic staging application and approved runtime captures to verify actual integration behavior. Do not infer it now.

Stop at this package for Phase 0 review. Remaining blockers/approvals are consolidated in [PHASE_0_REVIEW](PHASE_0_REVIEW.md).
