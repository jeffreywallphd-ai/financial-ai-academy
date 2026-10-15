---
id: WRK-0044
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0018
capability: CAP-0004
depends_on: ["WRK-0043"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/curriculum/curriculum_0002_discovery_projection.up.sql", "backend/migrations/curriculum/curriculum_0002_discovery_projection.down.sql", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/curriculum/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/identity/README.md", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/tests/integration/curriculum/test_postgres_discovery.py", "backend/tests/integration/api/test_single_profile_discovery_api.py", "backend/tests/integration/assessment/test_postgres_assessment.py", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/README.md", "apps/web/README.md", "apps/web/tests/contract/generated-client.test.mjs", "apps/web/tests/contract/client-usage.ts", "docs/architecture/contracts/discovery-contract.md", "docs/architecture/contracts/identity-provider-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0018-browse-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0044-persist-and-expose-protected-discovery-catalog.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 7aadfee6d95312bf5cbd12629f2a49780861b366
claim_id: WRK-0044:a54944c5-5e2f-4073-866b-da0fbc71d2d8
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T17:44:43Z
---

# Agent Work Packet: Persist and Expose the Protected Discovery Catalog

## Objective and Deliverable

Persist the accepted discovery classification and complete projection in
Curriculum-owned PostgreSQL tables, then expose the exact deterministic browse
response through one server-authorized FastAPI operation and the reproducible
generated TypeScript client. The result gives WRK-0045 a stable protected
`GET /api/v1/curriculum/opportunities` seam without adding browser presentation
or query semantics.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the index, delivery-planning, and
architecture-contracts context packs; the change-impact matrix; decision
readiness; planning/concurrency guidance; CAP-0004; SLI-0018; WRK-0043;
ADR-0005, ADR-0006, ADR-0007, and ADR-0009; the discovery, identity-provider,
contract-architecture, and migration contracts; the Curriculum, Identity,
bootstrap, host, API, migration, and web READMEs; the discovery schemas and
compatibility corpus; existing PostgreSQL repositories/migrations; API models,
OpenAPI generation, generated-client tooling and consumers; and the nearest
integration, contract, architecture, and Identity tests.

## Decisions and Assumptions

The accepted PostgreSQL split and module-first architecture authorize
Curriculum-owned tables and a provider-neutral repository port; no cross-module
foreign key or SQL read is permitted. ADR-0006 authorizes server-resolved
permissions and opaque sessions. Add the least-privilege
`curriculum.discovery.read` permission to the current single-profile context
and require it independently at the catalog operation; clients cannot supply
identity or permissions. The API response mirrors discovery v1, while JSON
Schema remains authoritative for the portable shape and generated OpenAPI is
authoritative for the HTTP/client shape. The browse operation is fixed-order,
bounded, and queryless until SLI-0019.

## In Scope

- Add checksum-locked up/down migrations for Curriculum-owned immutable lesson
  classifications and one replaceable discovery generation with at most 500
  ordered records and database-level identifier, enum, digest, duration, and
  timestamp constraints.
- Implement every discovery method already present on
  `CurriculumRepositoryPort`, including idempotent classification insertion,
  immutable-conflict detection, deterministic listing, one-transaction
  generation replacement, consistent reconstruction, and bounded adapter
  failure through the WRK-0043 application contract.
- Prove that an interrupted replacement preserves the prior complete
  generation and that malformed stored rows cannot escape as partial or raw
  provider data.
- Issue and enforce the separate `curriculum.discovery.read` permission from
  server-owned Identity context, including missing, malformed, expired,
  revoked, client-selected, and insufficient-permission denial.
- Add closed Pydantic response models, discovery error mapping, and the
  protected queryless `GET /api/v1/curriculum/opportunities` operation.
- Regenerate and verify the reviewed OpenAPI snapshot and generated TypeScript
  client, including a compile-time consumer of the new operation.
- Update the affected module, host, API, migration, architecture, and planning
  documentation with exact persistence/API behavior and remaining UI/live
  work.

## Out of Scope

Browser route, catalog card or layout, design tokens, visual/accessibility
qualification, static-host integration, live end-to-end qualification,
search/filter/sort parameters, cursors, pagination, stale-index serving,
background jobs, automatic rebuild scheduling, external search, new modules,
non-lesson records, destination navigation, enrollment, eligibility,
personalization, managed-cloud tenancy, or exposing registration/rebuild as a
public HTTP mutation.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Curriculum persistence | Accepted port, service invariants, migration patterns, PostgreSQL adapters | Listed Curriculum adapter, migration pair, integration test, and READMEs | Persist source classification and replaceable projection without duplicating authority |
| Identity authorization | ADR-0006 contract, service-issued permissions, denial tests | Listed Identity service, README, unit tests, and identity contract doc | Add one server-issued least-privilege browse permission |
| API transport | Current thin FastAPI host, response models, protected operation patterns | Listed host/API files and focused API integration test | Serialize discovery v1 and deny before disclosure |
| Public generated client | OpenAPI snapshot, deterministic generator, current client consumer | Listed generated artifacts, client contract tests, consumer, API/web docs | Provide WRK-0045 a reviewed typed seam |
| Architecture and planning | Module map, boundary tests, slice/packet/register | Listed architecture test/docs and planning artifacts | Prove owner boundaries and retain lifecycle evidence |

## Contracts and Interfaces

WRK-0044 consumes the exact WRK-0043 public dataclasses, error codes, digest
rules, repository port, fixed ordering, 500-record maximum, and discovery v1
schemas without changing their meaning. PostgreSQL reconstructs those exact
types and commits classification or projection replacement atomically; rows do
not reference Content tables or contain package bodies, provider payloads,
storage keys, learner identity, ranking, or eligibility.

The HTTP operation returns the discovery browse envelope with
`schema_version`, one generation digest, one coherent projection timestamp, and
closed opportunity records. It accepts no learner selector and no query
parameters. Authentication uses only the HttpOnly opaque session and requires
`curriculum.discovery.read`; unavailable, stale, or invalid internal projection
states return bounded non-disclosing errors. The generated client operation
`browseLearningOpportunities` is the sole accepted browser input for WRK-0045.

## Dependencies and Parallel Safety

WRK-0043 is complete and fixes the consumed discovery record and application
contract. WRK-0044 owns the migration, HTTP operation, Identity permission, and
generated client required by WRK-0045, so it is not parallel-safe with later
SLI-0018 packets. No other active work owns its declared files or generated
artifacts.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Persisted approved browse | Exact placement, Content version, and valid classification exist | Projection rebuild and protected GET run | PostgreSQL and HTTP return the same stable generation and owner facts in fixed order | PostgreSQL/API/contract tests |
| Registration replay/conflict | Classification identity is repeated or reused with changed facts | Adapter saves it | Identical input is idempotent; changed input is an immutable conflict with no replacement | PostgreSQL test |
| Atomic replacement | A complete prior generation exists | A later replacement is interrupted after record mutation begins | Transaction rollback preserves the prior generation byte-for-byte | PostgreSQL failure test |
| Empty projection | No classifications exist and rebuild succeeds | Authorized browse runs | A valid empty generation is returned without invented recommendations | PostgreSQL/API test |
| Stored corruption | Projection metadata or a stored record is malformed, mixed-generation, or incomplete | Adapter/application reads it | Browse fails closed with a bounded response and leaks no SQL or row detail | PostgreSQL/API failure test |
| Missing or invalid session | Cookie is absent, malformed, expired, or revoked | Catalog GET runs | Identity denies before Curriculum is invoked | API integration test |
| Insufficient or client-selected authority | Resolved context lacks catalog permission or request supplies identity/permission headers | Catalog GET runs | It returns a bounded forbidden response and no records | API/security test |
| Projection unavailable | Repository raises or no complete generation exists | Authorized catalog GET runs | It returns bounded `503` without stale records or provider detail | API integration test |
| Generated seam | Reviewed OpenAPI is regenerated twice | Client generation and TypeScript checks run | Output is stable and exposes only the typed queryless browse operation | snapshot/client/typecheck tests |
| Boundary integrity | Architecture checks inspect persistence and host imports | Checks run | Curriculum owns its schema, host uses public operations, and web imports only generated client types | architecture tests |

## Verification Commands

Run the packet validator and claim/start checks; discovery contract and focused
Curriculum/Identity tests; real PostgreSQL migration, replay, corruption, and
transaction-interruption tests against the disposable PostgreSQL 18.4 profile;
focused protected API tests; OpenAPI generation twice plus `--check`; generated
client generation plus `--check`, contract test, TypeScript typecheck, and
lint; backend unit/contract/architecture suites; migration, architecture,
security, documentation, and planning checks; `git diff --check`; affected
control-plane verification; and `python dev-tools/agent/check_ready.py`. Docker
qualification is mandatory for packet completion; a host failure is an
environmental blocker, not permission to claim PostgreSQL behavior.

## Documentation and Evidence Update

Update the migration, Curriculum, Identity, host, API, and web READMEs; discovery
and identity-provider contracts; module map; packet, slice, and register. Record
the exact migration IDs/tables, transaction/rollback evidence, permission and
denial behavior, API operation, OpenAPI/client regeneration results, focused
and aggregate checks, unsupported profiles, and remaining WRK-0045/WRK-0046
work. Update a derived context pack only if a changed canonical source makes it
stale.

Completion evidence establishes `curriculum_0002_discovery_projection`,
idempotent immutable classification, atomic complete-generation replacement,
the independent discovery permission, the protected queryless browse
operation, and current OpenAPI/TypeScript output. PostgreSQL 18.4 qualification
passed 5 focused migration/repository/HTTP scenarios, including interrupted
replacement rollback and corrupted-row denial. The complete backend suite
passed 237 tests; focused discovery/API/Identity checks passed; the generated
client check, TypeScript compilation, lint, 26 web tests, and static build
passed; architecture, security, documentation, planning, and diff checks
passed; and the aggregate readiness gate passed all 27 checks. The exact
submitted candidate also produced a qualifying affected-verification receipt.

No external search, provider, learner identity, ranking, eligibility, or
Content persistence entered the projection or response. Automatic rebuild
composition, browser presentation, and complete live catalog qualification
remain assigned to WRK-0045 and WRK-0046.

## Stop Conditions

Stop if implementation requires cross-module SQL or foreign keys, makes the
projection authoritative, changes discovery v1 meaning or its fixed ordering,
accepts client-selected identity/permission, exposes registration or rebuild as
an unaudited public mutation, requires a job queue or external index, serves a
known stale/partial generation, changes the session/provider model, adds
tenancy/entitlement/personalization, edits an applied migration, cannot execute
transactional PostgreSQL evidence, overlaps another live file lease, or
materially changes CAP-0004/SLI-0018 outcome, order, risk, or decision posture.

## Required Handoff

Return the migration and repository result; exact persisted fields and rollback
behavior; permission and HTTP contract; generated artifact digests/currency;
success, replay, corruption, interruption, denial, and unavailable evidence;
checks and results; documentation impact; unsupported profiles; residual risks;
CAP/SLI conformance; packet lifecycle result; and whether WRK-0045 is eligible.

## Planning History

- 2026-10-15: Authored just in time after WRK-0043 completion. The packet
  preserves the approved PostgreSQL, Identity, API, generated-client, and
  discovery boundaries and introduces no decision gate or material CAP change.
- 2026-10-15: Claimed on base
  `7aadfee6d95312bf5cbd12629f2a49780861b366`; the high-risk evidence route
  requires affected verification, aggregate readiness, and independent
  technical review.
- 2026-10-15: Added the existing Assessment PostgreSQL integration fixture to
  the bounded write scope after the complete backend run exposed its exact
  migration-inventory assertion. This is a compatibility update for the new
  Curriculum migration and does not change behavior or CAP scope.
- 2026-10-15: Completed the persisted protected browse seam with live
  PostgreSQL rollback/corruption evidence, stable generated contracts, bounded
  authorization and failure behavior, affected verification, and aggregate
  readiness. WRK-0045 is now dependency-eligible.
