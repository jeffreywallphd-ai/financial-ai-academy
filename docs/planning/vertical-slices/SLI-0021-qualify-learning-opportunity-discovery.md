---
id: SLI-0021
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: CAP-0004
depends_on: ["SLI-0019", "SLI-0020"]
decision_gates: []
---

# Vertical Slice: Qualify Learning Opportunity Discovery

## Outcome and User Scenario

The complete approved learning-discovery capability is demonstrably coherent:
an authorized local learner can browse, query, inspect, compare, and continue
to an exact available lesson using one versioned, rebuildable, provenance-rich
projection. Operators can distinguish directly qualified behavior from future
external-search, cloud, broader-identity, and unsupported activity profiles.

## Scope Boundaries

### In Scope

- Reconcile every CAP-0004 acceptance criterion against the completed
  SLI-0018, SLI-0019, and SLI-0020 evidence.
- Re-run the minimum cumulative checks whose freshness is required after the
  final interface slice, including live isolated discovery behavior and the
  fixed aggregate readiness gate.
- Prove that browse, query, detail, comparison, projection replay, denial,
  exact destination, accessibility, portability, and cleanup evidence all
  describe the same public discovery semantics.
- Record an acceptance trace and close SLI-0021 and CAP-0004 only when every
  manifest slice and capability criterion has current direct evidence.

### Out of Scope

- New product behavior, contract, schema, migration, fixture authority,
  dependency, interface pattern, or runtime service.
- External search providers, cloud/organization tenancy, commercial placement,
  personalization, recommendation, behavioral ranking, enrollment,
  eligibility, mastery, or execution of unavailable/non-lesson activities.
- Non-Chromium or manual assistive-technology qualification, production roles,
  backup/restore tooling, or managed-cloud operations.

## Canonical Context and Decisions

[CAP-0004](../capabilities/CAP-0004-discover-learning-opportunities.md),
[SLI-0018](SLI-0018-browse-approved-learning-opportunities.md),
[SLI-0019](SLI-0019-query-approved-learning-opportunities.md), and
[SLI-0020](SLI-0020-inspect-and-compare-learning-opportunities.md) define the
delivered capability. ADR-0005 and ADR-0007 retain Content/Curriculum ownership
and exact immutable lesson-package identity. Decision readiness still blocks
external providers, managed-cloud tenancy, broader identity, and commercial or
personalized policy, none of which is required for cumulative local acceptance.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Reconcile and qualify the delivered local discovery capability | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add an external search adapter before closing the CAP | no | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 5 |
| C. Expand qualification to managed-cloud tenancy and broader identity | no | 1 | 2 | 0 | 1 | 0 | 1 | 1 | 6 |
| D. Add personalized ranking and recommendation evidence | no | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 4 |

## Selection Rationale

Candidate A is the only eligible final slice and scores 14/14. It closes the
exact approved capability with direct evidence and honest limits. Candidates B
through D cross explicit CAP boundaries and unresolved provider, tenancy,
identity, commercial, or model-authority decisions.

## Boundary Path

`approved Content and Curriculum facts -> deterministic projection/rebuild ->
protected browse/query operations -> generated public client -> accessible
catalog/detail/comparison routes -> exact available-lesson destination ->
isolated PostgreSQL/Python/static/Chromium qualification`. No new runtime layer
is introduced; the slice verifies the complete accepted path.

## Contracts, Data, and Provenance

Discovery-v1, query-v1, protected operations, generated client, projection
generation, package digest, source fingerprint, publication/review timestamps,
and exact placement destination remain unchanged. Acceptance requires complete
generation validation and direct traceability to owning facts without treating
the projection, URL, browser storage, or provider payload as authority.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Approved browse | Only authorized current records appear with exact identity, version, provenance, and availability | contract/application/PostgreSQL/API/browser/live |
| Deterministic query | Filters, stable order, pagination, cursor binding, empty, and malformed states preserve query-v1 semantics | contract/application/API/browser/live |
| Exact inspection | Detail and ordered comparison display complete current-generation facts without ranking or partial substitution | model/component/browser/live |
| Exact continuation | Only an available lesson opens its reviewed exact-version destination | API/browser/live |
| Rebuild and stale state | Replay is deterministic and stale, withdrawn, changed, invalid, or unavailable state fails closed | application/PostgreSQL/API/browser |
| Authorization denial | Missing or insufficient context discloses no records, counts, identities, provenance, provider, or storage facts | identity/security/API/live |
| Accessibility and portability | Themes, focus, keyboard, reflow, 200-percent text, forced colors, axe, local startup, and cleanup remain qualified | component/Chromium/live/architecture |
| Honest qualification | External-search, managed-cloud, broader-identity, non-lesson execution, and manual/non-Chromium limits remain explicit | assurance/operations/planning docs |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0057 | Reconcile cumulative CAP acceptance and close learning-opportunity discovery | SLI-0018, SLI-0019, SLI-0020 | none | verifying |

## Verification and Qualification

Validate the exact manifest and all packet evidence; run current contract,
backend, web, focused Chromium/live, architecture, security, design,
documentation, planning, dependency, build, diff, affected-verification,
independent-review, and aggregate readiness checks only where evidence
freshness requires them. Retain unsupported profiles as explicit gaps.

## Rollback and Migration

No runtime, contract, schema, or authoritative data change is planned.
Qualification-document updates can be reverted without affecting the
rebuildable discovery projection or learner evidence.

## Stop Conditions

Stop if any manifest slice or CAP criterion lacks direct evidence, a fixed check
fails for a product/control defect, documentation overstates a profile, or
closure requires new identity, tenancy, provider, licensing, model-authority,
commercial, recovery, or external-execution authority. Bounded evidence defects
route through correction without weakening acceptance.

## Documentation Impact and Completion Evidence

Update this slice, WRK-0057, CAP-0004, the planning register, and only assurance
or operational sources made stale by reconciliation. Completion must identify
exact checks, environments, cleanup, unchanged contracts and migrations,
unsupported profiles, residual risks, and conformance to the approved package.

## Acceptance Trace

| CAP-0004 criterion | Direct current evidence |
| --- | --- |
| Approved and authorized exact versions with owning provenance | SLI-0018 discovery-v1 contract, deterministic Curriculum projection, protected browse API, generated client, browser cards, and live baseline |
| Deterministic replay/rebuild and safe stale or withdrawn behavior | SLI-0018 atomic rebuild, replay/stale/conflict tests, PostgreSQL integration, and bounded API/browser states |
| Deterministic topic, level, duration, prerequisite, kind, availability, ordering, tie, and pagination semantics | SLI-0019 query-v1 compatibility corpus, shared-core policy, protected query operation, URL-backed interface, and live multi-page/filter/cursor evidence |
| Bounded malformed, invalid-cursor, unsupported, stale, missing-destination, and unavailable responses | SLI-0018 through SLI-0020 contract, application, API, component, Chromium, and live denial/failure scenarios |
| Honest lesson, lab, project, and course inspection without fabricated execution | SLI-0020 closed-kind detail/comparison model and exact available-lesson-only action evidence |
| Exact approved destination without version substitution | SLI-0018 catalog and SLI-0020 detail/comparison continuation into the reviewed placement and retained lesson path |
| Local operation without external search and reusable provider-neutral boundary | PostgreSQL 18.4, shared Python core, local filesystem, same-origin static client, architecture checks, and explicit future-adapter gap |
| Keyboard, focus, labels, filter state, counts, failures, reflow/text scale, themes, forced colors, and assistive evidence | Component tests, focused mocked/live Chromium with axe, design-system validation, and retained manual/non-Chromium limits |

All eight criteria have direct evidence. The final qualification candidate
changes planning evidence only; runtime files are identical to the corrected
WRK-0056 live candidate. That ancestor passed five isolated live scenarios and
exact resource cleanup with static-index SHA256
`e802f7885cc0394b3c864300ba8a2620921aa26c1b71db3160a0e28334de72ec`.
The current candidate passed 13 architecture tests, 93 web tests, generated
client currency, TypeScript typecheck and lint, ten security control groups,
125-token/56-icon design validation, planning and documentation integrity, Git
whitespace checks, and all 27 aggregate readiness checks. No assurance source
was stale: the verification map already records direct discovery detail and
comparison evidence, while known gaps retain external search, managed cloud,
non-lesson destinations, production rebuild scheduling, non-Chromium/manual
assistive technology, and broader identity limits.

## Planning History

- 2026-10-15: Refined as the final approved CAP-0004 manifest slice after
  SLI-0019 and SLI-0020 completed. The evidence-only cumulative qualification
  cut scored 14/14 and introduces no decision, runtime behavior, or material
  capability change.
- 2026-10-15: Authored WRK-0057 as one bounded cumulative acceptance packet;
  no new product boundary or decision gate was introduced.
- 2026-10-15: Activated WRK-0057 after restoring the approved CAP artifact
  byte-for-byte and claiming the exact evidence-only scope against the current
  branch with no overlap.
- 2026-10-15: Reconciled all eight capability criteria to direct completed-slice
  evidence and moved WRK-0057 to verification after focused and aggregate gates
  passed without runtime or approved-package changes.
