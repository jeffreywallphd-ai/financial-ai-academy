---
id: WRK-0059
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-15
parent: SLI-0022
capability: CAP-0005
depends_on: ["WRK-0058"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/curriculum/curriculum_0003_curriculum_graphs.up.sql", "backend/migrations/curriculum/curriculum_0003_curriculum_graphs.down.sql", "backend/src/financial_ai_academy/modules/curriculum/domain/models.py", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/src/financial_ai_academy/modules/curriculum/ports/repositories.py", "backend/src/financial_ai_academy/modules/curriculum/ports/__init__.py", "backend/src/financial_ai_academy/modules/curriculum/application/service.py", "backend/src/financial_ai_academy/modules/curriculum/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/identity/README.md", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/tests/unit/curriculum/test_curriculum_graph_service.py", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/integration/curriculum/test_postgres_curriculum_graph.py", "backend/tests/integration/curriculum/test_postgres_discovery.py", "backend/tests/integration/api/test_single_profile_curriculum_graph_api.py", "backend/tests/integration/assessment/test_postgres_assessment.py", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/README.md", "contracts/api/openapi.json", "apps/web/README.md", "apps/web/src/generated/api-client", "apps/web/tests/contract/generated-client.test.mjs", "apps/web/tests/contract/client-usage.ts", "docs/architecture/contracts/curriculum-graph-contract.md", "docs/architecture/contracts/identity-provider-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0022-open-versioned-curriculum-graph.md", "docs/planning/work-packets/WRK-0059-persist-and-expose-curriculum-graph.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: d20a9d25946fb52055d3a09b4aef3bc03f93f257
claim_id: WRK-0059:e94b53fc-962e-40c2-9c70-2ab3bee8e81a
claimed_by: codex-cap-0005
claimed_at: 2026-10-15T23:16:03Z
---

# Agent Work Packet: Persist and Expose the Curriculum Graph

## Objective and Deliverable

Persist validated, immutable approved curriculum-graph versions in
Curriculum-owned PostgreSQL storage and expose one exact-version protected read
operation through the reviewed OpenAPI snapshot and generated TypeScript
client. The application admission operation must prove exact lesson and
assessment placement references before storage, and reads must revalidate
stored meaning without falling forward to another version. This packet ends at
the generated client seam; learner-facing rendering remains in WRK-0060.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through the baseline, curriculum/learning architecture, contracts, security,
testing-quality, and planning context packs. Read the change-impact matrix,
decision readiness, CAP-0005, SLI-0022, WRK-0058, ADR-0005, ADR-0006, ADR-0007,
the adaptive-pathway, contract, identity-provider, migration, and module-map
architecture; the Curriculum, Identity, host, API, migration, and web READMEs;
the graph schema/corpus and public types; existing placement/discovery ports,
service, PostgreSQL adapter, protected routes, OpenAPI/client generators; every
affected consumer; and the nearest unit, PostgreSQL, API, generated-client, and
architecture tests.

## Decisions and Assumptions

CAP-0005 and ADR-0005 assign graph admission, persistence, and read semantics to
Curriculum. PostgreSQL remains an adapter behind the shared application port,
and there is no cross-module SQL or foreign key. ADR-0006 authorizes opaque
server-resolved learner sessions and least-privilege permissions; the new GET
requires a server-issued `curriculum.graph.read` permission and accepts no
learner, actor, permission, or fallback-version selector. The approved graph
contract is already frozen by WRK-0058. A single JSONB aggregate row preserves
that complete contract without forcing table changes for optional branches or
presentation hints, while root identity, version, digest, state, and timestamp
constraints plus adapter revalidation prevent storage from becoming authority.

## In Scope

- Add checksum-locked up/down migrations for `curriculum.curriculum_graph_versions`
  keyed by curriculum ID and semantic version, containing the exact validated
  graph aggregate plus root digest and publication timestamp.
- Add database constraints matching root identity/version/digest/approved-state
  invariants and an append-only trigger that rejects ordinary update/delete;
  rollback removes only the new trigger/function/table.
- Extend the Curriculum repository port and PostgreSQL adapter with idempotent
  immutable save and exact read operations. Identical replay succeeds; reuse of
  an ID/version with different meaning returns a bounded conflict.
- Add provider-neutral publish/admit and exact-open application operations.
  Admission revalidates the graph and verifies every lesson/assessment
  activity against the existing exact Curriculum placement records before the
  graph becomes readable.
- Revalidate reconstructed rows and fail closed on malformed JSON, root-column
  mismatch, stale digest, unknown version, missing placement, repository
  failure, or an unknown exact graph. Never fall forward to a later version.
- Add a separate server-issued `curriculum.graph.read` permission and enforce
  it before Curriculum invocation at
  `GET /api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}`.
- Add closed Pydantic response models that mirror graph v1 without storage,
  provider, learner, eligibility, mastery, recommendation, or approval-ledger
  fields; map bounded graph errors without exposing SQL or source payloads.
- Regenerate and verify OpenAPI and the generated TypeScript client, including
  compile-time contract use of the exact-version path.
- Prove anti-rigidity by round-tripping absent/partial presentation hints,
  multiple optional branches, unbranched activities, and same-kind branch
  sharing through application, PostgreSQL, API, and generated types without a
  storage-schema or route change.

## Out of Scope

Browser map/list rendering, CSS, route composition, static fixture seeding,
live browser qualification, graph authoring/drafts, public mutation endpoints,
automatic publication, completion or prerequisite satisfaction, eligibility,
advancement explanations, activity launch, recommendations, mastery, learner
state, enrollment, cross-curriculum credit, external standards, tenancy,
provider execution, background jobs, or a current-version/fallback alias.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Curriculum application | WRK-0058 graph types, placements, repository port, service consumers | listed Curriculum domain/public/port/service files and focused unit tests | Add validated admission and exact read without provider coupling |
| PostgreSQL adapter | existing immutable placement/discovery patterns and migration inventory | listed migration pair, adapter, migration README, PostgreSQL tests | Persist the full graph aggregate atomically and append-only |
| Identity/API | opaque-session policy, protected route patterns, API models/errors | listed Identity, host/API files and integration tests | Enforce least privilege before graph disclosure |
| Generated public client | OpenAPI generator, snapshot, client generator and consumers | listed snapshot, generated artifacts, web docs and contract tests | Provide WRK-0060 one reviewed typed read seam |
| Architecture/planning | module map, identity and graph contracts, boundary tests, slice/register | listed architecture docs/tests and planning artifacts | Preserve ownership, lifecycle, and explicit remaining work |

## Contracts and Interfaces

Public application additions are `PublishCurriculumGraphRequest(graph)` and
`OpenCurriculumGraphRequest(curriculum_id, curriculum_version)` with matching
`CurriculumOperations` methods. Repository additions are an immutable
`save_graph_if_absent` and `get_graph_exact`; only the port may mention their
storage behavior. Graph admission confirms each lesson reference against
`LessonPlacement` and each assessment reference against `AssessmentPlacement`
using exact IDs, versions, and digests already owned by Curriculum.

The HTTP GET returns graph v1 exactly and requires
`curriculum.graph.read`. Path identifiers are bounded to the existing graph
identifier and semantic-version profiles. Missing or insufficient context is
denied before graph access; an unknown ID/version is 404; immutable conflict is
409; corrupt, stale-reference, digest, or storage failure is a bounded 503. No
version alias, query, learner selector, or client-selected permission exists.
The generated operation is named `getCurriculumGraphVersion`.

## Dependencies and Parallel Safety

WRK-0058 is complete and fixes graph shape, canonical timestamp/digest rules,
bounded errors, and anti-rigidity semantics. WRK-0060 consumes this packet's
exact generated read client, so the packets are sequential. No other active
packet may overlap the declared migration, Curriculum, Identity, host, API,
generated artifact, documentation, test, or planning paths.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact approved graph | Valid graph and exact lesson/assessment placements exist | Admission, persistence, and protected GET run | Application, PostgreSQL, HTTP, and generated contract preserve the same version and digest | unit/PostgreSQL/API/client |
| Replay and conflict | The same ID/version is admitted again with equal or changed meaning | Save runs | Equal replay is idempotent; changed meaning is a bounded immutable conflict and original row remains | unit/PostgreSQL |
| Exact reference mismatch | A placement is missing or any exact ID/version/digest differs | Admission runs | Publication fails before storage with a bounded stale-reference error | unit/PostgreSQL |
| Exact-version read | Versions 1.0.0 and 1.1.0 both exist | 1.0.0 is requested | Only 1.0.0 is returned; no latest/fallback substitution occurs | repository/API |
| Stored corruption | JSON, root columns, timestamp, or digest is malformed or mismatched | Exact read runs | The request fails closed with no row, SQL, or payload disclosure | PostgreSQL/API |
| Append-only storage | An ordinary update or delete is attempted | PostgreSQL executes it | The database rejects mutation and the original approved version remains | PostgreSQL migration |
| Unauthorized read | Cookie is absent/invalid or resolved context lacks graph permission | GET runs | Identity denies before Curriculum is invoked and reveals no graph existence | API security |
| Client-selected authority | Request sends identity/permission headers | GET runs | Request is rejected or ignored per existing policy; no authority is granted | API security |
| Flexible valid shape | Graph omits presentation order or adds valid optional/shared/unbranched structures | Round trip and GET run | Meaning survives without schema/table/route specialization | unit/PostgreSQL/API anti-rigidity |
| Generated seam | OpenAPI and client generation run twice | Checks and TypeScript compile run | Artifacts are stable and expose only the exact typed GET | snapshot/client/typecheck |

## Verification Commands

Run the work-packet validator, packet-start controls, migration checks, focused
graph/service/Identity unit tests, graph contract tests, real PostgreSQL
migration/replay/corruption/append-only tests, protected API tests, OpenAPI
generation twice plus `--check`, generated-client generation plus `--check`,
client contract tests, TypeScript typecheck and lint, complete backend
unit/contract/integration suites where the environment permits, architecture,
security, documentation, planning, and diff checks, affected exact-candidate
verification, independent technical review, and
`python dev-tools/agent/check_ready.py`. Docker/PostgreSQL evidence is required
for completion; an unavailable environment is a blocker, not inferred proof.

## Documentation and Evidence Update

Update migration, Curriculum, Identity, host, API, web, module-map,
identity-provider, and curriculum-graph contract documentation plus this
packet, SLI-0022, and the planning register. Completion evidence records exact
migration objects, immutable replay/conflict/rollback behavior, reference
checks, permission and denial behavior, endpoint and generated-operation shape,
focused and aggregate checks, PostgreSQL/Docker evidence, assumptions, known
gaps, and the client seam handed to WRK-0060. Never place local approval or
review records in tracked files.

## Stop Conditions

Stop for cross-module SQL/foreign keys, mutable graph replacement, a public
unaudited mutation, client-selected identity or permission, version fallback,
provider or learner state in the graph row/response, a graph contract meaning
change, a new identity/session model, tenancy/entitlement policy, publication
authoring workflow, external-standard semantics, inability to run mandatory
PostgreSQL evidence, overlapping file ownership, or any material CAP/SLI scope,
order, risk, or decision-posture change.

## Required Handoff

Report migration/table/trigger and rollback behavior; repository/application
operations; exact-reference, replay/conflict, corruption, and anti-rigidity
evidence; permission and HTTP contract; generated artifact currency; checks and
results; documentation impact; unsupported profiles and residual risks;
CAP/SLI conformance; packet lifecycle result; and whether WRK-0060 is eligible.

## Completion Evidence

- Added checksum-locked `curriculum_0003_curriculum_graphs` up/down migrations.
  The Curriculum-owned table stores one validated graph aggregate per exact
  curriculum ID and semantic version, constrains root identity, digest,
  approved state, and publication time, and rejects ordinary update/delete
  through an append-only trigger. The down path removes only that trigger,
  function, and table.
- Added provider-neutral repository and application seams for immutable
  idempotent admission and exact-version reads. Admission revalidates every
  graph and exact lesson/assessment placement reference before persistence;
  identity reuse with changed meaning, missing references, unavailable
  storage, corrupt payloads, and unknown exact versions fail with bounded
  errors. Reads never select a current or later version.
- Added the protected exact-version graph GET, closed response models, and the
  server-issued `curriculum.graph.read` permission. The OpenAPI snapshot and
  generated TypeScript client are current and expose
  `getCurriculumGraphVersion` without a learner, permission, provider,
  storage, or fallback-version selector.
- Anti-rigidity coverage round-trips a graph without presentation order and
  retains the complete flexible graph aggregate behind one JSONB port/adapter
  boundary. Optional/shared/unbranched graph structures remain governed by
  the WRK-0058 contract rather than by storage columns or route variants.
- A real PostgreSQL 18.4 qualification container passed migration, replay,
  conflict, exact-read, corruption, and append-only checks. The complete
  backend suite passed all 335 tests against that database. The web suite
  passed all 93 tests; generated-client currency, TypeScript typecheck, lint,
  and production build passed. OpenAPI currency, architecture, documentation,
  planning, and diff checks passed, and aggregate readiness passed all 27
  checks. Sandbox-only temporary-file and loopback restrictions were
  reproduced, isolated, and rerun successfully through the established
  workspace-temp and unsandboxed qualification routes.
- Updated Curriculum, Identity, API host, migration, generated-client, module
  map, graph-contract, and identity-provider documentation. This packet adds
  no browser route, learner state, eligibility, mastery, recommendation,
  authoring, tenancy, provider execution, or durable decision. WRK-0060 retains
  the accessible learner-facing map/list.

## Planning History

- 2026-10-15: Authored just in time after WRK-0058 completion. The packet keeps
  the frozen graph meaning in Curriculum, chooses a flexible validated JSONB
  aggregate behind a reusable repository port, and introduces no new decision
  or approval gate.
- 2026-10-15: Refined the exact write scope to include the existing discovery
  migration-inventory test after the new migration made that consumer
  materially affected; the prior claim and leases were released and replaced
  before implementation continued.
- 2026-10-15: Implemented and qualified immutable graph persistence,
  exact-reference admission, protected exact-version transport, generated
  client output, and cross-layer anti-rigidity behavior without changing the
  approved slice outcome or decision posture.
