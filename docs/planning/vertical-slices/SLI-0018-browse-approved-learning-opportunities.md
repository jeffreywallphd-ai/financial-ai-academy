---
id: SLI-0018
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: CAP-0004
depends_on: []
decision_gates: []
---

# Vertical Slice: Browse Approved Learning Opportunities

## Outcome and User Scenario

An authorized private-host learner opens the learning catalog and sees a stable,
deterministically ordered set of approved lesson opportunities with exact
identity, kind, topic, level, estimated duration, availability, version, and
publication provenance. Drafts, invalid versions, inaccessible placements, and
unowned or unsupported activity claims are absent or fail closed.

## Scope Boundaries

### In Scope

- Define the versioned, provider-neutral discovery record and deterministic
  browse response for exact approved lesson opportunities.
- Keep title, objectives, package identity, publication state, and provenance
  sourced from Content's exact public operation; keep placement, topic, level,
  duration, prerequisite summary, kind, availability, and destination
  classification as Curriculum-owned facts.
- Build and rebuild a Curriculum-owned PostgreSQL projection using only public
  Content facts and exact Curriculum records, with stable ordering and source
  fingerprints that make stale or conflicting input fail closed.
- Expose a protected bounded browse API and generated client without learner,
  provider, object-storage, database, or draft details.
- Deliver an accessible `/learn` catalog route for the private-host
  `single_profile` profile with explicit empty, denied, unavailable, and invalid
  response states in light, dark, and system themes.

### Out of Scope

- Free-text search, filters, alternative sorts, cursors, pagination, or
  stale-index degradation policy beyond a fail-closed browse response; those
  belong to SLI-0019.
- Detail/comparison views, multi-select comparison state, or destination
  navigation beyond presenting an exact non-substitutable lesson link; those
  belong to SLI-0020.
- Claiming executable courses, labs, or projects before their owning facts and
  destinations exist; the record contract may enumerate kinds but this slice
  qualifies only exact approved lessons.
- Personalized/adaptive ranking, enrollment, eligibility, entitlement,
  organization visibility, behavioral ranking, external search providers,
  crawlers, managed-cloud tenancy, or commercial placement.
- Content authoring, mutable drafts, package-format expansion, provider
  ingestion, background indexing, or a new application module.

## Canonical Context and Decisions

CAP-0004 is currently approved and enumerates SLI-0018 first after completed
CAP-0001. ADR-0005 keeps Content and Curriculum ownership distinct; ADR-0007
keeps published lesson identity, version, digest, safe content, and provenance
inside the exact package contract. Curriculum already owns exact placement and
structure facts. The discovery read model therefore remains a Curriculum-owned
projection over public Content operations rather than a new business owner.
Decision readiness has no unresolved gate for this local deterministic
projection; external indexing, tenancy, personalized ranking, or unsupported
activity execution would cross explicit stop boundaries.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver one exact approved-lesson browse path from projection through accessible catalog | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Deliver only the discovery record and projection core without a learner-visible path | yes | 1 | 0 | 2 | 2 | 2 | 2 | 2 | 11 |
| C. Seed lesson, lab, course, and project cards before every owning destination exists | no | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 4 |
| D. Adopt an external search service for the first browse projection | no | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 5 |

## Selection Rationale

Candidate A is the highest-scoring eligible cut and matches the approved
manifest outcome. It crosses the minimum complete path, produces immediate
learner value, reuses accepted Content/Curriculum/Identity/API/browser seams,
and can be independently qualified with one exact approved lesson. Candidate B
would establish useful internals but no observable learner outcome. Candidates
C and D require unowned execution facts or explicitly excluded provider and
decision authority.

## Boundary Path

`exact approved Content version + Curriculum placement/classification ->
Curriculum discovery projection/rebuild -> deterministic visibility and stable
browse operation -> server-resolved Identity permission -> FastAPI/OpenAPI ->
generated TypeScript client -> accessible static catalog route`. Content and
Curriculum remain semantic authorities; the projection is disposable,
rebuildable query state and the host/browser add no ranking or availability
policy.

## Contracts, Data, and Provenance

Add a closed discovery v1 record/browse contract with stable opportunity and
placement identity, exact destination, kind, title, summary, objectives, topic,
level, estimated minutes, prerequisite summary, availability code and reason,
package version/digest, publication timestamp/reviewer context, source
fingerprint, and projection timestamp. Curriculum classification inputs are
validated closed enums/bounded text; Content-derived fields are copied only
from an exact public read. The PostgreSQL projection belongs to Curriculum,
contains no provider payload or Content storage key, and is deterministically
replaceable from authoritative inputs.

The browser consumes only the generated client, treats the response as
untrusted, and links an available lesson to its exact placement route. The
record must not imply enrollment, prerequisite satisfaction, suitability,
mastery, recommendation, execution support, certification, employment, or
investment performance.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Approved browse | Authorized learner opens `/learn` | Stable approved lesson card shows exact Curriculum classification and Content version/provenance | contract/application/PostgreSQL/API/component/browser/live |
| Exact source trace | Projection is rebuilt from the same authoritative inputs | Record and source fingerprint are byte-for-byte semantically stable | application/PostgreSQL |
| Withdrawn or changed input | Placement disappears, exact Content is missing, or source facts conflict | Record is omitted or rebuild fails closed; no newer version is substituted | application/PostgreSQL/API |
| Visibility denial | Session is missing, expired, revoked, client-selected, or lacks catalog permission | Browse is denied before records are disclosed | identity/API/browser/live |
| Draft or unsupported item | Input is unpublished, invalid, or lacks an owned destination | It never appears as an available opportunity | contract/application/PostgreSQL |
| Empty catalog | No authorized approved records exist | Bounded educational empty state appears without invented recommendations | API/component/browser |
| Projection unavailable | Storage/rebuild or response validation fails | Bounded unavailable/invalid state appears without stale or partial records | application/API/browser |
| Interface equivalence | Catalog is used across themes, keyboard, focus, reflow, reduced motion, forced colors, and axe checks | Same content, availability meaning, provenance, and exact action remain accessible | component/Chromium |
| Local portability | Private-host composition runs without an external search dependency | Public contract/port remains provider-neutral and local qualification passes | architecture/live E2E |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0043 | Deliver the discovery record, Curriculum projection core, rebuild policy, and focused conformance tests | none | none | complete |
| WRK-0044 | Persist the projection and expose the protected browse API plus generated client | WRK-0043 | none | complete |
| WRK-0045 | Deliver the accessible approved-opportunity catalog route | WRK-0044 | none | complete |
| WRK-0046 | Qualify projection rebuild and the complete local browse path | WRK-0045 | none | ready |

## Verification and Qualification

Require discovery contract vectors; Curriculum domain/application denial and
rebuild tests; real PostgreSQL migration/adapter tests; Identity permission and
protected API tests; OpenAPI and generated-client currency; component/browser
tests for content safety, empty/denied/unavailable states, both themes,
keyboard/focus, reflow, reduced motion, forced colors, and axe; a live static
same-origin private-host path; architecture, security, design, documentation,
planning, dependency, build, and aggregate readiness checks.

## Rollback and Migration

The discovery projection is derived, not evidence. Its migration must be
additive and independently reversible, and rollback may drop and rebuild only
the projection while preserving Content packages, Curriculum placements,
Assessment evidence, completion history, and Audit records. A failed rebuild
must retain no partially published projection and must not silently serve a
mixed generation.

## Stop Conditions

Stop if implementation requires a new module or authoritative duplicate of
Content/Curriculum facts; a package-format or breaking public-contract change;
draft/provider payload exposure; external indexing or crawler authority;
personalized/model-ranked results; organization tenancy, entitlement, or
commercial policy; unsupported lab/project/course execution; cross-module SQL;
mutable source evidence; or a materially different CAP outcome, manifest,
ordering, risk, or decision posture.

## Documentation Impact and Completion Evidence

Update the discovery contract catalog, Curriculum/API/web READMEs, module and
dependency maps, security/assurance evidence, local composition and migration
instructions, this slice and its packets, and the planning register. Completion
must record exact schemas/migrations, supported record kinds, rebuild and
failure evidence, generated artifacts, interface qualification, live runtime,
cleanup, unsupported profiles, residual gaps, and CAP-package conformance.

## Planning History

- 2026-10-15: Refined as the first approved CAP-0004 manifest slice. The exact
  approved-lesson end-to-end browse cut scored 14/14, uses existing module
  ownership, and introduces no new decision gate or material CAP change.
- 2026-10-15: WRK-0043 completed the deterministic discovery contract and
  Curriculum projection core with fail-closed source and persisted-projection
  validation. The dependent persistence and API packet is now eligible.
- 2026-10-15: Refined WRK-0044 with exact Curriculum PostgreSQL, server-issued
  catalog permission, protected API, OpenAPI, and generated-client boundaries;
  it remains within the approved slice and adds no durable decision.
- 2026-10-15: Activated WRK-0044 after its dependency completed and its exact
  write scope, generated artifacts, candidate base, and file lease were bound.
- 2026-10-15: WRK-0044 completed the Curriculum-owned PostgreSQL projection,
  server-issued discovery permission, protected queryless API, and reproducible
  OpenAPI/generated-client seam. WRK-0045 is the next dependency-ready packet.
- 2026-10-15: Authored WRK-0045 with the exact generated-client, fail-closed
  validation, accessible catalog, exact-link, and browser evidence boundaries;
  it remains within the approved slice and introduces no durable decision.
- 2026-10-15: Activated WRK-0045 on its reserved generated-client and browser
  boundary after its dependency completed and its exact file set was leased.
- 2026-10-15: Submitted WRK-0045 candidate
  `a01c057d9060186c0481ac7ee578324c3ba3e745` for affected verification after
  focused and aggregate checks passed.
- 2026-10-15: Verification required corrections for valid shared
  placements, digest/order coherence, calendar-valid timestamps, and visible
  availability reasons. The bounded corrections preserve the approved slice
  and add no durable decision.
- 2026-10-15: WRK-0045 completed the protected `/learn` catalog with
  all-or-nothing response integrity, exact available-lesson navigation,
  flexible catalog cardinality, and responsive accessibility evidence.
  WRK-0046 is now the dependency-ready completion packet.
- 2026-10-15: Authored WRK-0046 with explicit public-operation fixture seeding,
  final static artifacts, isolated PostgreSQL/Python/Chromium qualification,
  catalog-to-lesson continuation, authorization denial, and cleanup evidence.
