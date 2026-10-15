---
id: WRK-0049
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0019
capability: CAP-0004
depends_on: ["WRK-0048"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/identity/README.md", "backend/tests/integration/api/test_single_profile_discovery_api.py", "contracts/api/README.md", "contracts/api/openapi.json", "apps/web/README.md", "apps/web/src/generated/api-client", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "docs/architecture/contracts/discovery-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0019-query-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0049-expose-protected-discovery-query-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 057baa81533d0a2eb778664b76a818c37b08bad2
claim_id: WRK-0049:8f4359dc-62e3-47d6-9ef8-cc7c420c225e
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T19:42:24Z
---

# Agent Work Packet: Expose the Protected Discovery Query API

## Objective and Deliverable

Expose the completed discovery-query core as one protected, read-only FastAPI
operation with closed query parameters, bounded safe error mapping, a
reproducible OpenAPI snapshot, and the generated TypeScript client seam needed
by WRK-0050. Preserve the existing queryless browse operation exactly and add
no browser behavior, learner-selected authority, provider, or persistence.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the baseline, API-contract,
security/privacy, and testing-quality context packs; read the change-impact
matrix, decision readiness, planning/concurrency guidance, CAP-0004, SLI-0019,
completed WRK-0048, discovery-query schemas/corpus, discovery architecture
contract, Curriculum public/query behavior and README, Identity context and
permission contract, FastAPI host/models/OpenAPI generator, current discovery
API tests, TypeScript client generator/tests, and the nearest READMEs.

## Decisions and Assumptions

The additive operation is `GET /api/v1/curriculum/opportunities/query`. It uses
URL-compatible query parameters because it is side-effect free and WRK-0050
must keep visible controls, browser URL, and applied server query aligned. The
path remains separate from queryless `GET /api/v1/curriculum/opportunities`, so
its response and parameter contract do not change. Existing
`curriculum.discovery.read` authority applies to both operations and is resolved
only from the opaque server session. No unresolved identity, provider, search,
queue, tenancy, persistence, or external-execution decision is introduced.

## In Scope

- Add closed FastAPI request-parameter and response models for the query-v1
  operation, mapping repeated topic/level/kind/availability parameters,
  duration bounds, closed sort, page size, and opaque cursor to the existing
  Curriculum public request.
- Echo only the core's canonical applied query; return exact total matches,
  bounded records, nullable next cursor, projection generation, and projection
  time without recomputing or reordering in the host.
- Require the server-resolved `curriculum.discovery.read` permission before the
  Curriculum query operation can disclose records, totals, generations, or
  cursor facts. Reject absent, expired, revoked, insufficient, or
  client-selected authority through existing Identity/request-policy paths.
- Map `invalid_query` and FastAPI shape errors to bounded 400 responses,
  `stale_cursor` and immutable conflict to bounded 409 responses, and invalid,
  stale, or unavailable projection state to bounded 503 responses. Do not copy
  raw input, decoded cursor payload, storage/provider detail, or record content
  into errors.
- Extend the deterministic OpenAPI generator's Curriculum schema double,
  regenerate the reviewed OpenAPI snapshot and all generated client outputs,
  and prove regeneration is byte-stable.
- Add API integration, security-denial, error-mapping, OpenAPI, generated-client,
  and typed client-usage coverage while retaining queryless compatibility.
- Update only documentation made stale by the new protected operation and
  generated-client seam.

## Out of Scope

- `/learn` controls, browser URL parsing, result rendering, paging behavior,
  accessibility, CSS, or client-side response validation; these belong to
  WRK-0050.
- Query matching, normalization, filtering, sorting, pagination, cursor
  construction, or projection policy changes; those are completed WRK-0048
  core responsibilities.
- Changing discovery-v1 records or queryless browse semantics, migration,
  another projection/index, durable cursor storage, external search, provider
  admission, queue/scheduler, crawler, cache, tenancy, or managed-cloud policy.
- Personalized/relevance/model ranking, prerequisite eligibility, enrollment,
  recommendation, detail/comparison, destination execution, dependency changes,
  remote publication, deployment, push, or unrelated refactoring.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API composition | Existing permission dependency, browse route, error handler | `app.py` | Add a protected thin query route and complete bounded discovery error mapping |
| Transport models | Discovery response models and domain-to-API converters | `models.py` | Express query parameters/applied query/page without host policy |
| OpenAPI generation | Curriculum schema double and snapshot generator | `generate_openapi.py`, OpenAPI snapshot | Keep the reviewed public contract reproducible |
| Generated client | Current deterministic generator outputs and contract tests | Generated client directory and listed tests | Expose one typed read operation without backend imports |
| Verification | Existing single-profile discovery API suite | Listed integration test | Prove authorization, mapping, stability, compatibility, and confidentiality |
| Canonical documentation | Host, Curriculum, Identity, API, web, discovery contract | Listed READMEs/contract | Record exact public boundary and deferred interface work |
| Lifecycle | Parent slice, packet, register | Listed planning files | Synchronize packet state and evidence |

## Contracts and Interfaces

The public operation is `queryLearningOpportunities` at
`GET /api/v1/curriculum/opportunities/query`. Its query parameters use the
contract names `query`, `prerequisite_query`, repeated `topic`, repeated
`level`, repeated `kind`, repeated `availability`, `minimum_minutes`,
`maximum_minutes`, `sort`, `page_size`, and `cursor`. Absence selects the core's
documented defaults. Parameter shape remains bounded in OpenAPI, while the
Curriculum core remains authoritative for canonicalization and cross-adapter
semantics.

The response maps `LearningOpportunityQueryPage` one-for-one into a closed API
model that references the unchanged `LearningOpportunityResponseModel` shape.
The generated TypeScript `paths`/`operations` types are the only web-facing
dependency. The browser sends the opaque session cookie through the existing
same-origin generated client and cannot send a learner ID, permission, decoded
cursor, provider, or database selector.

## Dependencies and Parallel Safety

WRK-0048 is complete and fixes the query request/page/error types consumed
here. WRK-0050 depends on this packet's final generated client; WRK-0051 depends
on both. This packet is not parallel-safe with those successors because they
share the OpenAPI/client seam, API contract documentation, and final fixtures.
The completed WRK-0052 correction has released all edit leases.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Authorized default query | A valid session has discovery-read permission | The query path is called without parameters | Core defaults execute once and the closed canonical page is returned | API integration |
| Full parameter mapping | Repeated filters, duration bounds, sort, page size, and cursor are supplied | The query path is called | The public Curriculum request receives the exact bounded values and response order is preserved | API integration |
| Unauthorized or insufficient context | Session is absent/invalid or lacks discovery-read permission | Query is requested, including with client-selected permission headers | Identity/request policy denies before Curriculum invocation or disclosure | API/security |
| Invalid query | Shape or core semantic validation fails | Query is requested | A bounded 400 envelope is returned with no records, counts, raw query, or cursor internals | API/security |
| Stale cursor | Query/generation binding fails | Continuation is requested | A bounded 409 envelope is returned with no fallback page | API integration |
| Projection failure | Projection is invalid, stale, conflicted, or unavailable | Query is requested | Existing bounded 409/503 mapping applies without stale or partial results | API integration |
| Queryless compatibility | Existing browse route and snapshot fragment are exercised | New operation is added | Browse still accepts no parameters and returns the unchanged browse model | API/OpenAPI regression |
| Reproducible client | OpenAPI/client generation runs twice | Generated outputs are compared | Snapshot and TypeScript outputs are byte-stable and expose the typed query operation | generator/contract |
| Confidentiality | OpenAPI, responses, and generated types are inspected | Contract checks run | No learner, actor, session, permission, provider, storage, score, ranking, eligibility, recommendation, secret, or decoded cursor field exists | contract/security |

## Verification Commands

Run the packet validator, planning checks, claim/start controls, focused query
and queryless API integration tests, OpenAPI generation in write and check mode,
generated-client generation/check, TypeScript client-usage and generated-client
contract tests, backend unit/contract/integration/architecture suites,
architecture and security checks, web typecheck and lint where required by the
generated seam, documentation and planning checks, dependency checks, `git diff
--check`, affected control-plane verification, and `python
dev-tools/agent/check_ready.py`. This packet requires no Docker or live browser
qualification because it changes no database, migration, static interface, or
external service; those full local query checks remain WRK-0051.

## Documentation and Evidence Update

Update the API, host, Curriculum, Identity, web, and discovery-contract sources
listed in scope plus packet/slice/register lifecycle. Completion evidence must
record the exact path/parameters/response, permission boundary, bounded status
mapping, queryless compatibility, reproducible OpenAPI/client results, focused
and aggregate checks, absence of persistence/external effects, residual gaps,
and WRK-0050 dependency readiness. Do not copy approval or reviewer records
from ignored local storage into tracked files.

## Stop Conditions

Stop if implementation requires changing query-v1 or discovery-v1 meaning;
duplicating query policy in the host/client; accepting learner, permission,
provider, or storage selectors; returning raw input/cursor internals; weakening
authorization or fail-closed behavior; an external provider/index, queue,
scheduler, crawler, migration, tenant, credential, or secret cursor authority;
browser/UI work; overlapping live write scope; non-reproducible generated
artifacts; a new dependency; an unresolved durable decision; or material
CAP-0004/SLI-0019 outcome, order, risk, or decision drift.

## Required Handoff

Report the protected operation, exact parameter-to-core mapping, response and
error behavior, authorization and confidentiality evidence, queryless
compatibility, OpenAPI/client reproducibility, changed files/boundaries,
commands and results, documentation impact, absence of migration/external
qualification, residual gaps, packet lifecycle result, and whether WRK-0050 is
dependency-ready.

## Planning History

- 2026-10-15: Authored just in time after WRK-0048 completion and the bounded
  compatibility-branch correction. The packet confines HTTP, OpenAPI, and
  generated-client work to the existing protected host/client seams, preserves
  queryless browse, adds no durable decision, and leaves all browser behavior to
  WRK-0050.
