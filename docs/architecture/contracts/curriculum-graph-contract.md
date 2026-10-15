# Curriculum Graph Persistence and Read Contract

- Status: implemented for the first deterministic navigation slice
- Canonical for: Curriculum graph admission, immutable persistence, and exact-version read boundaries
- Related ADR: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)

## Ownership and Shape

Curriculum owns graph identity, objectives, competencies, activity placement,
branches, and typed relationships. The portable `curriculum-graph-v1` schema
remains authoritative for graph shape and digest meaning. Content and
Assessment retain their resources; Curriculum stores only their exact public
placement and version/digest references and never reads their tables.

## Admission

Graph admission is an internal application operation, not a public browser
mutation. It revalidates the complete graph and confirms every lesson and
assessment activity against the exact placement record already owned by
Curriculum. A missing or mismatched placement fails before persistence. Exact
replay is idempotent; reusing one curriculum ID/version for different meaning
is an immutable conflict.

## Persistence

`curriculum.curriculum_graph_versions` stores one validated JSONB aggregate per
curriculum ID and semantic version. Root identity, version, digest, approved
state, and publication timestamp are duplicated only as constrained database
columns for exact lookup and integrity checks. The adapter reconstructs public
types and repeats full validation on every read. Database rows reject ordinary
update/delete, and there are no cross-module foreign keys.

Keeping constituents inside one validated aggregate is deliberate. Optional
branches, presentation hints, unbranched activities, and same-kind branch
sharing do not require a persistence migration or specialized tables. The
aggregate does not contain learner state, eligibility, mastery,
recommendations, provider payloads, storage keys, or approval records.

## Protected Exact Read

`GET /api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}`
requires the server-issued `curriculum.graph.read` capability after resolving
the opaque session. The client cannot select identity, permission, or a
fallback version. Unknown exact versions return a bounded not-found response;
corrupt, stale-reference, digest, or storage failures return bounded
unavailable responses without row or SQL detail. The operation returns only
the closed graph v1 response through the reviewed OpenAPI snapshot and
generated TypeScript client.

## Compatibility

The current seam supports immutable approved versions only. Mutable drafts,
authoring, current/latest aliases, completion and eligibility projections,
adaptive ranking, external learning standards, organization tenancy, and
cross-curriculum credit require separate governed work. Later storage adapters
must pass the same admission, replay/conflict, exact-version, corruption,
authorization, and flexible-shape scenarios.
