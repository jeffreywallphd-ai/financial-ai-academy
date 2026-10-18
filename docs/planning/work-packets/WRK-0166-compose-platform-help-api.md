---
id: WRK-0166
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0082
capability: CAP-0020
depends_on: [WRK-0165]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/guidance", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/tests/integration/api/test_single_profile_guidance_api.py", "backend/tests/unit/guidance", "backend/tests/unit/identity/test_identity_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0082-browse-search-approved-help.md", "docs/planning/work-packets/WRK-0166-compose-platform-help-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 9fd11b3f13fd7e36839ed665cf43c47fca567fae
claim_id: WRK-0166:b2dbf125-2742-451c-b8c1-3d8b0eba23a7
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T02:34:09Z
---

# Agent Work Packet: Compose the Platform Help API

## Objective and Deliverable

Compose the completed `platform-help/v1` contract and pure Guidance core into
one checked-in immutable starter corpus, a Guidance-owned application/public
seam, and two protected read-only FastAPI operations for deterministic search
and exact-version topic reads. Regenerate the reviewed OpenAPI snapshot and the
shared TypeScript client so browser, command-line, service, and future headless
AI callers receive the same validated public documents.

The deliverable is an API-first local composition seam. It is not a browser
feature, mutable help authoring system, database, network retrieval path,
provider/model feature, or live end-to-end qualification.

## Required Context

Before implementation, read and follow `AGENTS.md`, `docs/README.md`, the
routed context sources, change-impact matrix, decision-readiness register,
CAP-0020, SLI-0082, WRK-0165, platform-help contract architecture, module map,
identity-provider contract, API contract README, content and language
standards, risk/AI boundaries, and the nearest Guidance/API/client/test
READMEs. Inspect the completed Guidance contracts/domain/adapters/ports, the
composition root, identity permissions, FastAPI host and models, OpenAPI
generator, generated-client script/output, analogous protected exact reads,
and their tests before changing files.

The Required Startup has been performed and reported before this planning
change. Stop for a canonical conflict, stale CAP package, active write
collision, unresolved durable decision, or material scope drift.

## Decisions and Assumptions

- The approved CAP-0020 package and active SLI-0082 remain current; WRK-0165 is
  complete and supplies the exact contract, validation, search, cursor,
  provenance, and failure rules consumed here.
- The starter corpus is immutable checked-in product data derived from current
  canonical repository sources. Runtime code loads only its versioned JSON
  resources at composition time and never parses or serves repository Markdown.
- Guidance owns corpus admission and application reads. Identity owns the
  opaque session and grants one additive `guidance.platform_help.read`
  permission; the API checks it before any corpus operation.
- Search and exact reads remain learner-independent and read-only. The server
  session authorizes access but does not personalize, rerank, track, or mutate
  results.
- The public routes are `GET /api/v1/guidance/platform-help` and
  `GET /api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}`.
  The exact path has no `latest` alias.
- OpenAPI and the generated TypeScript client are generated artifacts. Their
  generators, not hand edits, remain authoritative.

## In Scope

- Add a bounded immutable-corpus adapter that loads sorted versioned JSON
  resources, parses every record through the existing strict contract adapter,
  validates the complete corpus atomically, and exposes only the Guidance port.
- Add a small reviewed starter corpus with plain-language help, method,
  limitation, and glossary topics bound to safe canonical-source fingerprints.
- Add Guidance application operations and a stable public module for
  deterministic browse/search and exact-version reads.
- Compose Guidance once at application startup and fail startup when any corpus
  record is missing, malformed, unsafe, duplicated, stale, or internally
  inconsistent.
- Add the server-owned read permission and protected search/exact-read API
  operations with strict path/query bounds, bounded public errors, no client
  identity/permission selector, and no private corpus-count disclosure before
  authorization.
- Add closed Pydantic response models that preserve the v1 contract's safe body,
  applicability, publication, source, relation, digest, and cursor meaning.
- Regenerate reviewed OpenAPI and generated TypeScript types; prove browser and
  non-browser callers share the same operations.
- Add focused corpus/application/API/identity tests for success, authorization,
  exact-version absence, cursor/query errors, startup failure, source binding,
  flexible valid topic counts/order, and confidentiality.
- Reconcile direct Guidance, API, contract, module, architecture assurance,
  planning, and contribution documentation.

## Out of Scope

- Browser routes, components, local browser adapters, navigation, styling,
  accessibility behavior, or browser query-state composition; WRK-0167 owns
  that dependent increment.
- Live PostgreSQL/browser/restart/offline/no-outbound qualification and final
  cleanup; WRK-0168 owns that dependent increment.
- Persistence, migrations, mutable corpus/editorial workflow, database-backed
  search, remote content, arbitrary links, source refresh jobs, analytics, or
  user-contributed content.
- Semantic/vector search, generated answers, personalization, recommendations,
  learner evidence, grading, eligibility, provider/model execution, external
  action, or financial conclusions.
- Contextual feature links, expanded methodology, troubleshooting flows, and
  final corpus-wide qualification owned by later CAP-0020 slices.
- Managed-cloud operation, organization tenancy, recovery, licensing,
  legal/commercial policy, or public/external publication.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance | Completed domain, adapter, port, and module README | Application/public seam, immutable corpus adapter/resources, direct exports/docs | Compose one validated read-only owner |
| Identity | Session context and established permission grant | Add one read permission and focused expectation | Authorize before corpus access |
| API | Host, models, error mapping, OpenAPI generator | Guidance dependency, models, handlers, routes, schema stub | Expose the same safe public documents |
| Contracts/client | v1 schemas, API snapshot, generator output | OpenAPI snapshot, generated TypeScript types, API README | Keep headless/browser contracts identical |
| Tests | Guidance unit and analogous protected API suites | New corpus/service/API tests and direct identity expectation | Prove atomic startup and protected reads |
| Architecture | Platform help, module map, assurance table | Direct implementation-status and verification rows | Record ownership and non-authority |
| Planning | SLI-0082, WRK-0166, register | Status and neutral evidence only | Keep governed state synchronized |

No migration, persistence repository, deployment topology, Web feature,
design-system, provider, model, or unrelated module file may change.

## Contracts and Interfaces

WRK-0165's `PlatformHelpCorpusPort`, immutable domain values, strict mapping
adapter, exact topic/search payloads, schemas, and failure codes are binding
inputs. This packet adds a public `GuidanceOperations` seam with an exact-topic
request and the existing transport-neutral `SearchRequest`/`SearchPage` values.

The HTTP search operation accepts only `query`, optional `topic_kind`,
`page_size`, and optional opaque `cursor`. The exact operation accepts only the
validated `topic_id` and stable `major.minor.patch` `topic_version`. Responses
contain no learner/session identity, repository path, Git metadata, approval or
review data, authoring locator, provider payload, prompt, model output, or raw
markup. Error mapping never echoes rejected payloads or corpus internals.

The generated client must reproduce both operation IDs and all closed response
models from `contracts/api/openapi.json`; no handwritten browser API shape is
introduced.

## Dependencies and Parallel Safety

WRK-0165 is complete. This packet changes the shared composition root, identity
grant, API host/models, OpenAPI snapshot, generated client, architecture, slice,
and register, so it is not parallel-safe with another writer on those paths.
WRK-0167 must wait for this packet's exact generated client and operation IDs.

Claim from a recorded base revision, run `packet-start`, acquire exact-file
leases immediately before edits, retain one owner through verification, and
keep approval/reviewer records only in ignored local storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Atomic starter corpus | All checked-in topics are valid | Composition starts | One immutable corpus is admitted with stable source/topic/corpus digests | unit/application |
| Startup containment | Any record is malformed, duplicated, unsafe, or broken | Adapter/composition starts | Startup fails before a partial corpus or API becomes available | unit/architecture |
| Protected search | A session has `guidance.platform_help.read` | Search/browse is called | The deterministic v1 page preserves exact order, facts, and cursor meaning | application/API |
| Exact topic | A valid ID and version exist | Exact read is called | The complete safe topic document is returned without reinterpretation | API/contract |
| No substitution | A valid ID names an absent version | Exact read is called | A bounded 404 is returned and no other version is substituted | application/API |
| Authorization confidentiality | Session is missing or lacks exact permission | Either route is called | 401/403 occurs before Guidance is invoked or corpus facts/counts are exposed | API/security |
| Invalid query/cursor | Bounds or cursor binding are invalid | Search is called | A bounded 400/409 occurs without payload or internal-state disclosure | API/security |
| Headless parity | OpenAPI and generated client are inspected | Artifacts regenerate | The same two protected operations and exact shapes serve all clients | OpenAPI/client |
| Flexible valid corpus | Order, counts, Unicode, optional fields, and extra safe topics vary | Admission/search runs | Invariants hold without fixed-count or whole-prose assertions | unit/anti-rigidity |
| No new authority | Imports, outputs, and calls are inspected | Checks run | No persistence, network, model/provider, learner-policy, grading, eligibility, or financial seam exists | architecture/security |

## Verification Commands

Run focused tests first:

`backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/guidance backend/tests/unit/identity/test_identity_service.py backend/tests/integration/api/test_single_profile_guidance_api.py`

Regenerate, then check the OpenAPI snapshot and TypeScript client with the
repository's pinned Python/Node workflows. Run generated-client contract tests,
Python compilation, architecture, security, documentation, planning,
learner-language, whitespace, exact-candidate affected verification, one
independent technical review, and `python dev-tools/agent/check_ready.py`.

Record only commands that pass. Harmless whitespace, optional copy, or generated
formatting correction may be fixed in scope without a new approval or a full
review loop.

## Documentation and Evidence Update

Document the embedded corpus contribution and source-fingerprint rules,
Guidance application/public boundary, startup failure behavior, permission,
routes, Pydantic/OpenAPI/client shapes, headless parity, exact-version and cursor
errors, confidentiality, generated-artifact commands, assumptions, and
remaining browser/live work. Update packet, slice, and register together; never
copy local approval or reviewer records into tracked files.

## Stop Conditions

Stop for ambiguous canonical help meaning; request-time repository Markdown;
mutable or remote content; arbitrary URL/active content; browser-only ranking;
semantic/vector search; model/provider execution; personalization/analytics;
learner-specific advice, grading, eligibility, or financial action; persistence
or migration need; breaking v1 compatibility; client-selected identity or
permission; managed-cloud/tenancy/recovery/licensing/legal/commercial/external-
publication behavior; stale CAP authority; active collision; or material
CAP-0020/SLI-0082 drift.

Do not stop for harmless whitespace, optional wording, generated ordering,
nonfunctional styling, or fixture count. Fix bounded inconsequential issues or
defer optional polish.

## Required Handoff

Report `CAP-0020.SLI-0082.WRK-0166`; exact candidate and receipt; corpus and
source fingerprints; application/public/API operations; permission and failure
mapping; OpenAPI/client reproduction; headless parity; confidentiality and
anti-rigidity evidence; exact checks; docs; assumptions; and remaining browser
and live gaps. Confirm no persistence, migration, browser feature, provider,
model, external content, learner authority, or financial behavior changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0165 completed. The packet
  composes its transport-neutral contracts and deterministic core into one
  immutable starter corpus and protected API-first seam while deferring browser
  and live qualification to their dependency-ordered packets. It preserves the
  approved CAP package and requires no lower-level approval.
