---
id: WRK-0048
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0019
capability: CAP-0004
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/README.md", "contracts/learning/discovery/query/v1", "contracts/compatibility/README.md", "contracts/compatibility/discovery/query/v1", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/src/financial_ai_academy/modules/curriculum/application/service.py", "backend/tests/contract/discovery_query", "backend/tests/unit/curriculum/test_discovery_service.py", "docs/architecture/contracts/discovery-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0019-query-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0048-deliver-discovery-query-core.md"]
generated_artifacts: []
base_revision: 6b9cc0886b6ef7af358f290b8b6446455c29938e
claim_id: WRK-0048:c99fbd22-94aa-44af-84f1-f12b93c27de1
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T19:01:19Z
---

# Agent Work Packet: Deliver the Discovery Query Core

## Objective and Deliverable

Add a versioned, provider-neutral discovery-query contract and one
deterministic Curriculum application operation over the validated SLI-0018
projection. The operation returns a bounded, generation-bound page with exact
applied-query facts, total matches, stable records, and an opaque next cursor,
while the existing queryless browse contract and operation remain unchanged.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the baseline, API-contract, and
testing-quality context packs; read the change-impact matrix, decision
readiness, planning/concurrency guidance, CAP-0004, completed SLI-0018, ready
SLI-0019, discovery architecture contract, discovery-v1 schemas/corpus,
Curriculum public/application/repository boundaries and README, contract and
Curriculum discovery tests, and the nearest contract READMEs. Revalidate the
accepted CAP package and current SLI before implementation.

## Decisions and Assumptions

Discovery remains a Curriculum-owned derived read projection over exact public
Content facts. ADR-0002 authorizes a platform-owned versioned contract, ADR-0004
requires one shared local/cloud core, and the approved CAP forbids personalized
or model-ranked results. The current validated projection is capped at 500
records, so deterministic in-core matching, filtering, sorting, and pagination
is bounded and requires no second index, migration, external provider, queue,
or scheduler. Query cursors carry no authority and bind only a version,
canonical query fingerprint, projection generation, and continuation position.

## In Scope

- Add closed JSON Schemas and documentation for discovery-query v1 request and
  result values that reference the unchanged discovery-v1 opportunity record.
- Add approved, boundary, malformed, normalization, sort-tie, pagination,
  cursor replay/tamper/query-mismatch/generation-mismatch, and denial vectors
  plus a dependency-free contract runner.
- Add public Curriculum request, applied-query, sort, result-page, and bounded
  error types and a `query_learning_opportunities` operation.
- Validate every request before repository access: bounded text and filter
  cardinality, known enum values, sorted/deduplicated canonical filters,
  inclusive duration range, page size 1 through 50, and a bounded cursor.
- Normalize query/prerequisite text using contract-fixed Unicode NFKC,
  whitespace collapse, and case-fold semantics. Match all query terms across
  title, summary, objectives, topics, and prerequisite summary; match the
  prerequisite-only terms only against prerequisite summary.
- Apply OR within repeated topic/level/kind/availability filters and AND across
  different dimensions. Preserve default projection order or apply title,
  shortest-duration, or longest-duration order with opportunity ID as the final
  tie-break.
- Compute a stable canonical query fingerprint and deterministic opaque cursor;
  continue without omission or duplication only when query and projection
  generation match. Reject malformed, tampered, mismatched, or stale cursors
  without returning records.
- Preserve record fingerprints/provenance, validate the complete projection
  through the existing browse path, and return no ranking, learner, provider,
  storage, eligibility, recommendation, or cursor-secret fields.

## Out of Scope

- FastAPI routes, HTTP status mapping, OpenAPI, generated clients, browser/UI
  behavior, live end-to-end qualification, or any change to discovery-v1 browse
  schemas or meanings; these belong to WRK-0049 through WRK-0051.
- PostgreSQL schema/query optimization, another projection, migration, durable
  cursor storage, cache, background indexing, external search, provider
  admission, tenancy, or managed-cloud operations.
- Fuzzy, stemmed, synonym, semantic/vector, relevance-scored, personalized, or
  behavior-ranked search; prerequisite parsing; eligibility; enrollment;
  recommendation; detail/comparison; or activity execution.
- Unrelated refactoring, dependency upgrades, design-system changes, remote
  publication, or destructive/external action.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | Discovery v1 schemas/corpus and contract architecture | Listed query schema/corpus directories and contract catalog READMEs | Fix portable request/result, normalization, cursor, and denial meaning without changing browse v1 |
| Curriculum public seam | Existing discovery public types and operations | `public.py` | Expose closed query inputs/outputs with no provider or learner authority |
| Application policy | Projection validation, browse behavior, hashing/canonicalization helpers | `application/service.py` | Own deterministic matching, filters, sort, count, and continuation in the shared core |
| Focused verification | Existing discovery contract and service tests | Listed query contract directory and discovery service test | Prove conformance, bounds, replay, stale/tampered denial, order, and confidentiality |
| Canonical documentation | Curriculum and discovery contracts | Listed READMEs and discovery contract | Record exact semantics and remaining HTTP/UI/live work |
| Lifecycle | Parent slice, packet, register | Listed planning files | Keep status, dependency, evidence, and next packet synchronized |

## Contracts and Interfaces

WRK-0048 consumes `LearningOpportunityBrowse` only through the existing
validated Curriculum browse operation. It produces `LearningOpportunityQuery`
and `LearningOpportunityQueryPage` public types and the query-v1 executable
schemas/corpus for WRK-0049. The default request is semantically equivalent to
the full queryless browse up to its bounded page size, but the browse operation
and closed envelope remain byte-for-byte compatible.

The applied-query representation is canonical and safe to echo. Cursors are
opaque transport values, not evidence or authorization. Their decoded form and
hashing algorithm are implementation details only where the contract does not
need cross-adapter compatibility; externally observable accept/reject and
continuation semantics are fixed by vectors.

## Dependencies and Parallel Safety

SLI-0018 is complete and supplies the validated record/projection contract.
This is the first SLI-0019 packet and has no packet dependency. WRK-0049 depends
on its final public types and schemas; WRK-0050 depends on the generated client
from WRK-0049; WRK-0051 depends on all prior query behavior. No SLI-0019 packet
is parallel-safe with this work because contracts, generated artifacts, catalog
semantics, and final fixtures are sequential inputs.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Default query | A valid complete projection exists | Empty query requests a page | Records retain projection order, applied query is canonical, total is exact, and browse v1 is unchanged | application/contract |
| Normalized text | Records contain Unicode, mixed case, and repeated whitespace across allowed fields | Multiple query and prerequisite-only terms run | NFKC/case-fold/whitespace vectors match; every term uses the documented field and AND semantics | compatibility/unit |
| Combined filters | Topic, level, kind, availability, and duration values are supplied | Query executes | Values within dimensions use OR, dimensions use AND, and filters are canonicalized without inventing eligibility | application/unit |
| Stable sorts | Titles/durations tie | Each closed sort runs | Default, title, shortest, and longest orders use the documented keys and opportunity-ID final tie-break | compatibility/unit |
| Page continuation | Matches exceed a bounded page | First and subsequent cursor requests run | Total is stable and each record appears exactly once in deterministic order | contract/unit |
| Cursor replay or mismatch | A cursor is reused with the same or changed query/generation | Continuation runs | Exact replay is deterministic; query mismatch, tamper, malformed shape, or changed generation fails boundedly with no records | contract/unit |
| Malformed request | Text, enum, filter count, duration, size, or cursor is invalid | Query is invoked | Validation rejects before repository read and exposes no raw input, record, or internal detail | unit/security |
| Projection unavailable | Browse reports absent/corrupt/unavailable projection | Query is invoked | Existing bounded discovery error propagates without stale/partial results | unit |
| Confidentiality | Public query types and cursor are inspected | Contract checks run | No learner/provider/storage/rank/score/eligibility/recommendation/secret field exists | contract/architecture |

## Verification Commands

Run the packet validator, planning checks, claim/start controls, dependency-free
query contract runner, query contract tests, existing discovery-v1 contract
tests, and focused Curriculum discovery service tests. Also run backend unit,
contract, and architecture suites; architecture and security checks;
documentation and planning checks; dependency checks; `git diff --check`;
affected control-plane verification; and
`python dev-tools/agent/check_ready.py`. This packet requires no Docker,
browser, network, provider, or managed-cloud qualification because it changes
no adapter, host, interface, migration, or external integration.

## Documentation and Evidence Update

Update the contract catalogs, Curriculum README, discovery architecture
contract, packet, slice, and register. Completion evidence must record exact
query/filter/sort/page/cursor semantics; schema and corpus results; browse-v1
compatibility; bounds and denial behavior; focused and aggregate checks; no
migration; unsupported HTTP/UI/provider profiles; residual risks; and
CAP/SLI conformance. Update a derived context pack only if a changed canonical
source makes it stale.

## Stop Conditions

Stop if implementation requires changing discovery-v1 record/browse semantics;
a PostgreSQL migration or second authoritative index; client-side or
provider-owned policy; prerequisite/eligibility inference; relevance,
personalization, learner behavior, recommendation, enrollment, or execution;
an external provider, queue, scheduler, crawler, tenancy, credential, or secret
cursor authority; responses above the existing projection bound; stale or
partial fallback; overlapping live write scope; non-executable verification; or
material CAP-0004/SLI-0019 outcome, order, risk, or decision drift.

## Required Handoff

Report the query contract and public operation; exact normalization, matching,
filter, sort, count, page, and cursor behavior; browse-v1 compatibility; changed
files and boundaries; success, malformed, replay, tamper, mismatch, stale,
unavailable, and confidentiality evidence; checks/results; documentation
impact; absence of migration/external qualification; residual gaps; packet
lifecycle result; and whether WRK-0049 is dependency-ready.

## Planning History

- 2026-10-15: Authored just in time as the first SLI-0019 packet after SLI-0018
  completion. It preserves the queryless contract, confines deterministic query
  policy to the shared Curriculum core, adds no migration or provider, and
  introduces no durable decision or material CAP drift.
- 2026-10-15: Claimed on base
  `6b9cc0886b6ef7af358f290b8b6446455c29938e` after deterministic readiness,
  CAP authority, dependency, decision, and scope-overlap gates passed.
