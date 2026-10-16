---
id: WRK-0093
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: SLI-0026
capability: CAP-0006
depends_on: [WRK-0092]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client", "backend/migrations/curriculum/curriculum_0004_practice_placements.down.sql", "backend/migrations/curriculum/curriculum_0004_practice_placements.up.sql", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/content_gateway.py", "backend/src/financial_ai_academy/modules/assessment/adapters/curriculum_gateway.py", "backend/src/financial_ai_academy/modules/assessment/application/service.py", "backend/src/financial_ai_academy/modules/assessment/ports/gateways.py", "backend/src/financial_ai_academy/modules/assessment/public.py", "backend/src/financial_ai_academy/modules/content/README.md", "backend/src/financial_ai_academy/modules/content/adapters/lesson_package.py", "backend/src/financial_ai_academy/modules/content/application/service.py", "backend/src/financial_ai_academy/modules/content/public.py", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/curriculum/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/curriculum/application/service.py", "backend/src/financial_ai_academy/modules/curriculum/ports/repositories.py", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/tests/contract/lesson_package", "backend/tests/integration/api/test_single_profile_practice_api.py", "backend/tests/integration/curriculum/test_postgres_practice.py", "backend/tests/unit/assessment/test_practice_service.py", "backend/tests/unit/content/test_content_service.py", "backend/tests/unit/content/test_lesson_package_adapter.py", "backend/tests/unit/curriculum/test_curriculum_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "contracts/compatibility/lesson-package/v1", "contracts/learning/lesson-package/v1", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/content-package-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0026-open-versioned-practice-activity.md", "docs/planning/work-packets/WRK-0093-compose-protected-practice-opening-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Compose Protected Practice Opening API

## Objective and Deliverable

Compose the frozen practice-v1 contract through Content, Curriculum,
Assessment, and the single-profile API so an authorized browser or non-browser
client can open one exact placed practice activity without receiving answers or
creating learner evidence. Deliver additive package admission, immutable
practice placement, a transport-neutral Assessment public operation, protected
HTTP/OpenAPI, and mechanically regenerated TypeScript client contracts. Do not
deliver the browser route, response submission, scoring, or a separate AI mode.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, security-risk, testing-quality, interface, and delivery-
planning context. Read the change-impact matrix, decision readiness, CAP-0006,
SLI-0026, WRK-0092, ADR-0005, ADR-0007, the content-package and Assessment
contracts, contract/versioning and API standards, Content/Curriculum/Assessment
module READMEs, current lesson-package validator and corpus, placement services
and migrations, Assessment gateways/service/public facade, API models/routes,
OpenAPI generator and generated-client workflow, affected tests, and concurrent-
work rules.

## Decisions and Assumptions

- Keep the shared domain/application core authoritative. The browser, a command-
  line client, and a future headless AI consumer must call the same protected
  public API; no UI-only state or AI-specific transport is introduced.
- Extend lesson-package v1 additively with an optional `practices` declaration
  and closed `assessment.practice.v1` capability. Existing packages without
  that member retain identical bytes, digests, admission, and public reads.
- Content validates declared practice files against the frozen private schema,
  canonical digest, ID/version correlation, semantic invariants, exact file
  closure, and package limits before publication. Content transports exact
  private bytes but does not interpret answers at runtime or expose them to a
  learner client.
- Add a Curriculum-owned immutable practice-placement record rather than
  overloading the knowledge-check placement's singular item/policy fields. The
  record carries exact placement, package, practice version, and definition
  digest and may reference the same parent lesson placement without creating a
  cross-module database relationship.
- Assessment resolves Content and Curriculum only through their public facades,
  parses with the WRK-0092 adapter, correlates all exact tokens, and returns a
  public answer-safe presentation. Opening is read-only and creates no attempt,
  response, score, completion, event, projection, or history row.
- The API uses server-resolved identity and existing permission policy. It
  accepts only the placement selector, never learner identity or private
  definition input, and maps missing, malformed, stale, unauthorized, and
  unavailable states to bounded responses without answer facts.
- Update the reviewed OpenAPI snapshot and mechanically generated client in the
  same packet to keep API consumers available. JIT-C will consume that client
  in the browser and does not redefine the operation.

## In Scope

- Add the closed practice-file declaration/capability to lesson-package v1,
  update independent and production admission paths, and add a versioned
  synthetic package/corpus fixture that preserves existing digest vectors.
- Add exact Content public retrieval for one declared practice definition with
  full stored-byte revalidation and no storage/provider identifiers.
- Add a forward/down Curriculum migration, repository port/adapter, public
  create/resolve operations, immutable conflict behavior, exact parent-package
  correlation, and real-PostgreSQL integration coverage.
- Add Assessment public presentation types and `open_placed_practice`, plus
  public-only Curriculum/Content gateways, exact token correlation, bounded
  error mapping, deterministic safe projection, and side-effect-free unit tests.
- Add the authenticated GET route, closed response models, answer-confidential
  OpenAPI schema, authorization/unconfigured/error integration tests, reviewed
  snapshot, and generated TypeScript client.
- Update affected architecture/module/contract documentation and prove existing
  knowledge-check, lesson-package, placement, API, and generated-client behavior
  remains compatible.

## Out of Scope

Browser page, form controls, styling, navigation link, or client-side practice
state; response submission; attempt creation; scoring; feedback selection;
retry/resume/history enforcement; completion evidence or events; Curriculum
graph successor or adaptive navigation changes; live local fixture seeding;
AI-authored items, agent protocols, autonomous actions, model/manual grading,
adaptive selection, mastery inference, external providers, arbitrary execution,
organization tenancy, managed cloud, production recovery, or financial advice.

## Expected File and Boundary Impact

| Area | Allowed impact | Boundary reason |
| --- | --- | --- |
| Lesson package | additive schema/capability, validator, corpus, contract/unit tests | Content must admit exact practice bytes without changing old package meaning |
| Content | public request/result and exact service read | Assessment receives private bytes only through a Content-owned facade |
| Curriculum | additive placement model, migration, repository/service/public operations, tests | Multi-item practice identity cannot truthfully reuse singular knowledge-check fields |
| Assessment | public safe types, service operation, public-only gateways, composition, tests | Assessment remains answer and projection authority |
| API | protected GET, closed models, OpenAPI snapshot, generated client, integration tests | Browser and headless clients share one versioned operation |
| Documentation/planning | listed contracts, READMEs, slice/packet/register | Keep ownership, compatibility, evidence, and gaps explicit |

## Contracts and Interfaces

- Lesson-package v1 gains optional `practices` declarations with exact
  `practice_id`, schema version, safe logical path, JSON media type, byte count,
  and SHA-256; the closed capability is `assessment.practice.v1`.
- Content gains exact practice-definition request/result types and one facade
  operation. Curriculum gains exact practice-placement create/resolve types and
  operations backed by its own additive table.
- Assessment gains answer-safe public practice presentation types and
  `open_placed_practice`; private domain values and definition bytes remain
  internal. The HTTP GET response maps only the public type.
- OpenAPI and generated TypeScript preserve one source of transport truth. No
  client or host imports backend internals, and no provider payload enters a
  public model.

## Dependencies and Parallel Safety

WRK-0092 is complete and freezes every private/safe practice meaning consumed
here. This packet is sequential because package admission, placement,
Assessment correlation, API shape, OpenAPI, and generated client form one
compatibility chain. It is not parallel-safe with another packet changing any
of those files. No external service, model, provider, or unresolved DEC is a
dependency.

## Acceptance Scenarios

| Criterion | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Additive admission | Existing package v1 fixtures and a declared practice package | Admission runs | Old digests/behavior remain exact; valid practice bytes publish; undeclared, stale, malformed, unknown-capability, or answer-schema drift fails closed | contract/unit |
| Exact Content read | A published package declares one practice | Assessment asks through the public facade with exact package/digest/practice tokens | Exact revalidated bytes and file digest return; mismatch/not-found returns bounded failure | unit |
| Immutable placement | A parent lesson placement and exact practice reference exist | Practice placement is created/repeated/conflicted/resolved | Exact replay is idempotent; conflicting meaning fails; PostgreSQL forward/down behavior is proven | unit/PostgreSQL |
| Safe Assessment open | Exact placement and private definition correlate | `open_placed_practice` runs repeatedly | Same immutable answer-safe presentation returns with no correct IDs, numeric answers/ranges, feedback, or side effects | unit |
| Stale/malformed closure | Any package/practice/version/digest token or private definition is inconsistent | Assessment resolves | A stable bounded error returns and no private value is echoed | unit/API |
| Protected API | Supported session calls the route using only a placement | Host resolves identity and Assessment operation | Closed v1 presentation returns; missing session, extra learner input, absent service, not-found, stale, and unavailable cases fail safely | API |
| Headless parity | A non-browser HTTP client has the supported session | It calls the documented GET operation | It receives the same schema and provenance with no browser state or alternate core | API/OpenAPI |
| Side-effect-free open | Repeated API calls occur | State is inspected | No Assessment evidence/event and no learner state are created | unit/API |
| Generated compatibility | OpenAPI is regenerated | Generated client check runs | Snapshot and TypeScript client reproduce exactly and retain existing methods | contract/typecheck |
| Anti-rigidity | Compatible package path/order, 1-20 items, and valid reference counts vary | Admission/opening runs | Behavior follows contract bounds rather than fixture-specific counts or browser assumptions | contract/unit |

## Verification Commands

Run focused lesson-package, Content, Curriculum, Assessment, API, migration,
OpenAPI, and generated-client suites plus their existing regressions. Run the
real PostgreSQL migration qualifier, API snapshot reproduction, client
generation/check, TypeScript typecheck, architecture, security, documentation,
planning, whitespace, and aggregate readiness checks. Use the repository's
prepared Python/Node/npm environment and isolated workspace temp directory.

Submit one exact candidate, generate a fresh affected-verification receipt, and
obtain one independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Record exact package, placement, public-operation, API, OpenAPI/client,
confidentiality, side-effect, compatibility, PostgreSQL, affected, aggregate,
and review results. Document the same-API browser/headless boundary and the
deliberately unimplemented submission/UI/AI/live-fixture scope. Store approval
and reviewer records only in the ignored local ledger.

## Stop Conditions

Stop for a breaking existing package, knowledge-check, placement, or API
contract; private-answer leakage; a need to overload singular knowledge-check
meaning; client-owned identity; scoring/evidence state on open; a new identity,
tenancy, model-authority, provider, execution, recovery, legal, or commercial
decision; cross-module persistence access; dependency addition; active scope
collision; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional UI
styling, optional prose polish, or another inconsequential in-scope correction.
Fix it locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; package and placement contracts; public operation
and protected route; headless parity; answer secrecy and side-effect evidence;
OpenAPI/generated-client result; PostgreSQL migration result; old-family
regressions; focused, architecture, affected, aggregate, receipt, and technical
review results; changed files; documentation impact; assumptions; and gaps.
Confirm that browser UI, submission, scoring, feedback, attempts, evidence,
events, live fixture seeding, graph/adaptation, AI mode, model authority, cloud,
and external execution did not change, then leave JIT-C dependency-ready.

## Planning History

- 2026-10-16: Authored just in time after WRK-0092 completed. The packet keeps
  the same protected API authoritative for browser and non-browser clients,
  uses additive Content and Curriculum contracts instead of overloading the
  knowledge-check family, and defers a separate AI mode without closing future
  headless consumption.
