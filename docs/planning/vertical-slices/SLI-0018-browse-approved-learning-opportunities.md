---
id: SLI-0018
kind: vertical-slice
planning_status: complete
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
| WRK-0046 | Qualify projection rebuild and the complete local browse path | WRK-0045 | none | complete |

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

SLI-0018 is complete through WRK-0043, WRK-0044, WRK-0045, and WRK-0046. The
delivered boundary is one Curriculum-owned, deterministic and rebuildable
discovery projection over exact public Content facts; a protected queryless API
and generated client; an all-or-nothing accessible `/learn` catalog; and an
explicit local fixture composition that qualifies the catalog-to-lesson path.
No new module, provider authority, ranking, personalization, enrollment, or
unsupported activity execution entered the slice.

Acceptance evidence covers every slice scenario:

- Contract and application vectors prove exact approved browse, stable source
  fingerprints/generation, deterministic ordering, replay, withdrawal,
  malformed input, oversized input, unavailable Content, and atomic failure.
- `curriculum_0002_discovery_projection` adds independently reversible
  Curriculum-owned classification and projection tables. PostgreSQL 18.4
  integration evidence proves checksum-locked up/down migration, idempotent
  registration, complete-generation replacement, interrupted rollback,
  corruption denial, empty projection, and preservation of the last complete
  generation.
- Identity/API evidence proves server-issued catalog permission, missing,
  malformed, expired, revoked, insufficient, and client-selected authority
  denial before records are disclosed, plus bounded unavailable responses.
- Web evidence proves whole-response schema and digest validation, exact lesson
  destinations, honest availability reasons, empty/denied/unavailable/invalid
  states, light/dark/system equivalence, keyboard/focus, narrow and
  200-percent-equivalent reflow, reduced motion, forced colors, and axe.
- The final empty-database live path passed 2 PostgreSQL/Python/Chromium
  scenarios for exact classification and provenance, catalog-to-lesson
  continuation, assessment/completion reopening, missing-session denial,
  security headers, opaque cookies, accessibility, and isolated cleanup.
  Composition tests separately prove flag-off isolation, exact seed/rebuild
  order, and no application readiness after registration or rebuild failure.

Focused and repository-level evidence includes 193 backend tests for the core
packet, 237 backend tests for the persistence/API packet, 48 current web
unit/component tests, 12 affected catalog/lesson Chromium tests, 11 current
architecture tests with 2 failure subtests, OpenAPI and generated-client
currency, TypeScript, lint, the 103-module static build, security, design,
documentation, planning, dependency and diff checks, and the 27-check aggregate
readiness gate. Every exact-candidate affected verification receipt qualified;
required independent dispositions closed their findings. The deterministic
completion structure gate passed for this slice and all four packets.

Canonical discovery, identity, module, migration, API, deployment, bootstrap,
web, architecture-assurance, known-gap, packet, slice, and register documents
are synchronized. No product contract or derived context pack became stale.
The migration pair supplies rollback for derived projection state; source
Content, placements, assessment evidence, completion history, and audit records
remain outside that rollback and are preserved.

Qualification is limited to exact approved lessons in the local
`single_profile` profile and Chromium. Search/filter/sort/pagination and stale
query states remain SLI-0019; detail/comparison and non-lesson limitation views
remain SLI-0020; cumulative multi-slice/provider-neutral qualification remains
SLI-0021. External search, managed-cloud tenancy, additional browsers,
production scheduling, and unsupported activity execution were not qualified.
These are accepted CAP boundaries rather than hidden completion claims.

The result conforms to the approved CAP-0004 package without material drift or
an unresolved decision. SLI-0019 is dependency-ready for just-in-time
refinement; SLI-0020 may also proceed from the stable SLI-0018 record in
parallel when separately claimed without overlapping files.

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
- 2026-10-15: Activated WRK-0046 after its dependency completed and its exact
  public-operation, static-build, live-test, documentation, and planning file
  set was claimed and exclusively leased.
- 2026-10-15: Submitted WRK-0046 candidate
  `2e7997801710db849cb58b58f4a6567421a393f2` after the isolated live
  catalog-to-lesson path and focused/aggregate checks passed.
- 2026-10-15: WRK-0046 completed on corrected candidate
  `7598516b885f43eca3a6d2ff32b7fada213e55eb` after its fresh qualifying receipt
  and accepted independent R02 disposition closed the composition and exact
  live-classification evidence findings. All four slice packets are complete,
  so SLI-0018 entered deterministic closure verification.
- 2026-10-15: Closed SLI-0018 after the four-packet completion gate, focused
  failure and denial review, live Docker qualification, current web/browser and
  architecture regressions, and 27-check aggregate readiness all passed. The
  slice remains within the approved CAP package and makes SLI-0019 and SLI-0020
  eligible for just-in-time refinement.
