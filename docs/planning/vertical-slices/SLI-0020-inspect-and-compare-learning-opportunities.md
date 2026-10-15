---
id: SLI-0020
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: CAP-0004
depends_on: ["SLI-0018"]
decision_gates: []
---

# Vertical Slice: Inspect and Compare Learning Opportunities

## Outcome and User Scenario

From the approved learning catalog, an individual learner can open a stable
detail view for one current opportunity or compare two through four current
opportunities. The learner sees exact version, provenance, kind, topics,
objectives, level, duration, prerequisite summary, availability limitations,
and the exact approved destination where one is executable. The experience
helps the learner make an informed educational choice without granting
enrollment, asserting prerequisite completion, deciding eligibility, ranking
suitability, or making a personalized recommendation.

## Scope Boundaries

### In Scope

- Define a bounded browser URL contract for one opportunity detail identity and
  two through four repeated comparison identities, using only validated
  `opportunity_id` values from the current discovery projection.
- Resolve detail and comparison records from the protected queryless discovery
  snapshot through the existing generated client. Validate the complete
  current projection before selecting records; never accept record fields,
  destinations, provenance, or availability from URL or browser storage.
- Add a catalog detail action and a comparison-selection form that preserve a
  bounded return path to the originating `/learn` query without copying an
  opaque cursor into a durable record.
- Present consistent per-opportunity facts and limitations, including honest
  unavailable/planned states and a clear distinction among lesson, lab,
  project, and course vocabulary even though the current local projection
  admits only exact approved lessons.
- Permit an exact destination action only when the already validated discovery
  record is an available lesson with its contract-valid same-origin placement
  path. Preserve the existing exact-version lesson-open behavior.
- Provide bounded missing, changed-selection, malformed, denied, unavailable,
  and invalid-response states with no partial comparison or fallback records.
- Qualify keyboard, focus, headings, table or list semantics, light/dark/system
  parity, reflow, text scaling, reduced motion, forced colors, and axe behavior
  using the existing design system and reviewed icon pack.

### Out of Scope

- Enrollment, entitlement, cohort assignment, prerequisite completion,
  eligibility, learner suitability, adaptive ranking, recommendation, ratings,
  reviews, bookmarking, saved comparisons, or behavioral tracking.
- Executing a lab, project, course, notebook, provider job, or any unavailable
  opportunity; creating fictional destinations for closed kind values.
- New backend detail or comparison endpoints, a new discovery record version,
  mutable catalog state, a second index, external search, provider payloads,
  background rebuilds, or managed-cloud tenancy.
- Comparing lesson body content, assessment answers, learner progress, prices,
  financial products, market performance, certifications, or employment
  outcomes.

## Canonical Context and Decisions

- [CAP-0004](../capabilities/CAP-0004-discover-learning-opportunities.md)
- [Learning Discovery Contract](../../architecture/contracts/discovery-contract.md)
- [Discovery v1](../../../contracts/learning/discovery/v1/README.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Initial Glossary](../../domain/glossary.md)
- [Module Map](../../architecture/modules/module-map.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Versioned Lesson Package](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Interface Design System](../../design/README.md)
- [Interface Style Guide](../../design/style-guide.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [SLI-0018](SLI-0018-browse-approved-learning-opportunities.md)
- [SLI-0019](SLI-0019-query-approved-learning-opportunities.md)

The accepted Content/Curriculum ownership, discovery-v1 record, queryless
browse authorization, exact lesson destination, generated-client boundary,
single-profile context, and static React application are sufficient. No
identity, tenancy, provider, data-license, AI authority, queue, encryption,
recovery, commercial, or external-execution choice is introduced. Extending
comparison into eligibility, recommendation, learner progress, enrollment, or
undelivered activity execution would cross a decision or CAP boundary.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Resolve detail and bounded comparison from the existing protected, fully validated queryless projection | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add dedicated server detail and comparison operations over the same projection | yes | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 13 |
| C. Carry complete records in URL or browser storage and compare without rereading the projection | no | 2 | 1 | 2 | 0 | 2 | 1 | 1 | 9 |
| D. Deliver detail only and defer comparison to another CAP slice | no | 1 | 0 | 2 | 2 | 2 | 2 | 2 | 11 |

## Selection Rationale

Candidate A is selected. It produces the complete manifest outcome while
reusing the accepted protected browse seam and its 500-record bound. It keeps
Curriculum authoritative, revalidates the current complete generation before
record selection, exposes no new public backend meaning, and is reversible as
static-client behavior. Candidate B is viable but adds redundant transport and
schema surface without a measured need. Candidate C could display stale or
tampered owner facts and is ineligible. Candidate D omits the comparison value
explicitly bound into SLI-0020 and would materially redefine the slice.

## Boundary Path

`/learn query or browse page -> bounded opportunity identity selection ->
detail or compare URL -> generated protected browse client -> complete
discovery-v1 validation -> current record resolution -> accessible fact and
limitation presentation -> exact available-lesson destination or explicit
non-executable state`.

SLI-0019 is complete and supplies the query-origin state and validated card
model. SLI-0020 may technically depend only on SLI-0018's stable record and
browse contract, but delivery now consumes the completed SLI-0019 interface so
return navigation and comparison selection remain coherent with active query
state. SLI-0021 remains the final cumulative qualification slice.

## Contracts, Data, and Provenance

No public backend schema changes. Detail accepts exactly one bounded
`opportunity_id`. Comparison accepts two through four repeated, distinct
bounded IDs; order follows the user's validated selection and is not a ranking.
Malformed, duplicate-only, excessive, missing, or no-longer-current selection
fails to a bounded state. A return reference may preserve only a same-origin
`/learn` query URL within a conservative length bound and must exclude an
opaque continuation cursor so transient paging is not mistaken for durable
state.

Both routes fetch the protected queryless browse operation, validate the full
closed envelope and generation, then select current records. Every displayed
fact comes from the discovery-v1 record and retains its exact package identity,
version, digest, source fingerprint, projection generation/time, publication
provenance, availability reason, and exact destination. No learner identity,
provider/storage reference, lesson body, Assessment data, ranking score,
eligibility result, or suitability inference enters the view.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Open detail | Learner follows a catalog record's detail action | One current record is shown with exact identity, version, provenance, classification, prerequisites, availability, and limitations | component/browser/live |
| Select comparison | Learner selects two through four current catalog records | Comparison opens in selection order with the same labeled fields and no winner, score, or recommendation | model/component/browser |
| Query-origin continuity | Learner starts from a filtered or sorted catalog | Detail/compare can return to the bounded originating query without retaining a transient cursor or mutating filters | model/browser |
| Exact destination | Current record is an available lesson | Only its exact contract-valid placement action is executable; no latest-version or alternate substitution occurs | contract/component/browser/live |
| Honest unavailable kind | Record is planned, unavailable, or a non-executable closed kind | Limitations remain visible and no activity action is fabricated | compatibility/component/browser |
| Malformed selection | IDs are invalid, duplicate-only, too numerous, or supplied record facts are attempted | Request fails before rendering records, without accepting client-owned content | model/security/browser |
| Changed or missing selection | A selected identity is absent from the current complete generation | Entire detail/comparison fails closed with a bounded refresh/return path and no partial table | model/component/browser |
| Visibility denial | Session is absent, expired, revoked, insufficient, or client-selected | No opportunity facts, counts, selected identities, provenance, cursor, learner, provider, or storage detail is disclosed | identity/API/browser/live |
| Invalid or unavailable projection | Browse envelope fails integrity checks or the host is unavailable | No partial comparison or cached fallback appears; learner gets a bounded recovery state | model/component/browser |
| Education boundary | Learner compares prerequisites, effort, kind, and availability | Copy remains educational and does not claim eligibility, suitability, financial performance, certification, or employment outcome | content/component/browser |
| Interface equivalence | Detail and comparison run across themes, keyboard, reflow, text scaling, reduced motion, forced colors, and axe | Equivalent facts, limitations, actions, focus, labels, and table/list alternatives remain perceivable and operable | component/Chromium |
| Local portability | Complete path runs in the accepted local topology | PostgreSQL, shared Python core, static client, and filesystem serve the same public facts without external search or a Node production server | architecture/live |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0053 | Define the bounded detail/comparison URL, record-resolution, validation, and return-path model over the existing generated browse client | SLI-0018, SLI-0019 | none | complete |
| WRK-0054 | Deliver the accessible current-opportunity detail route with provenance, limitations, and exact available-lesson continuation | WRK-0053 | none | active |
| WRK-0055 | Deliver query-coherent two-to-four selection and accessible comparison without ranking, partial fallback, or saved browser authority | WRK-0054 | none | captured |
| WRK-0056 | Qualify the complete detail/comparison path, denial/failure states, accessibility, exact continuation, portability, and cleanup | WRK-0055 | none | captured |

## Verification and Qualification

Require bounded URL/selection/return-path model tests; complete discovery-page
validation and current-generation resolution; malformed, duplicate, excessive,
missing, changed, denied, unavailable, and invalid-response tests; available
and unavailable kind/action evidence; exact package/destination provenance;
component and pinned-Chromium light/dark/system, keyboard/focus, table/list,
reflow/text-scaling, reduced-motion, forced-color, and axe checks; live
PostgreSQL/Python/static/Chromium detail, comparison, denial, and exact lesson
continuation; generated-client/OpenAPI currency; static-browser and no-Node
production boundaries; architecture, security, design, documentation,
planning, dependency, build, diff, affected control-plane, independent-review,
and aggregate readiness gates.

## Rollback and Migration

No authoritative migration or public backend contract change is planned.
Detail and comparison routes, card controls, and static output are additive.
Rollback removes those client routes and controls while retaining discovery-v1,
query-v1, browse/query operations, projections, and exact lesson destinations.
Comparison URLs are transport/navigation state, not durable learner evidence,
and may fail explicitly when their identities no longer occur in the current
generation.

## Stop Conditions

Stop for a new discovery record meaning; a server endpoint without demonstrated
need; client-owned or cached record authority; partial comparison after missing
or corrupt input; enrollment, eligibility, entitlement, prerequisite
completion, recommendation, learner suitability, progress/mastery, saved work,
or behavioral tracking; undelivered activity execution; external search,
provider payload, managed-cloud/tenancy policy, remote binding, dependency,
migration, or background scheduling; raw lesson/Assessment data; a financial
performance or certification claim; overlapping active scope; unresolved
durable decision; or material CAP-0004 outcome, manifest, order, risk, or
decision drift.

## Documentation Impact and Completion Evidence

Update the web and Curriculum/application READMEs only where behavior changes;
add browser detail/comparison navigation guidance, acceptance evidence,
architecture verification, known-gap reconciliation, generated static output,
this slice, its packets, and the register. Completion evidence must identify
the exact URL/selection bounds, current-generation resolution, displayed facts,
available/unavailable action policy, query-return behavior, denial/failure
paths, education boundary, interface qualification, live topology, checks,
unsupported kinds/profiles/providers, residual gaps, and CAP conformance.

## Planning History

- 2026-10-15: Refined as the dependency-ready third CAP-0004 slice after
  SLI-0019 completion. Candidate A scored 14/14 by resolving detail and bounded
  comparison from the existing protected, fully validated queryless projection.
  The selection preserves exact owner facts and current-generation provenance,
  introduces no backend contract or durable decision, and remains within the
  approved CAP outcome and four-slice manifest.
- 2026-10-15: Refined WRK-0053 just in time as the bounded selection,
  return-path, complete-snapshot validation, and protected-loader seam consumed
  by the detail and comparison interface packets.
- 2026-10-15: Completed WRK-0053 with strict detail/comparison and return-path
  bounds, complete current-snapshot resolution, one-renewal protected loading,
  closed failure states, and focused verification. WRK-0054 is dependency-ready.
- 2026-10-15: Refined WRK-0054 just in time as the accessible detail route,
  catalog navigation, exact fact/provenance/limitation presentation, bounded
  failures, and mocked interface-evidence increment.
