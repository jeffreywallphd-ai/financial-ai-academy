---
id: SLI-0023
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: CAP-0005
depends_on: ["SLI-0022"]
decision_gates: []
---

# Vertical Slice: Explain Deterministic Curriculum State

## Outcome and User Scenario

An authorized learner opens one exact curriculum version and sees current
completion, eligibility, requirement, and availability meaning for every
visible activity. The learner can tell which work is complete, which available
work can be chosen now, which prerequisite is still unmet, which branch is
optional, and why an exact activity is unavailable. Every result and
explanation is reproducible from the exact Curriculum graph and current
Learner-model completion projections; no model score, ranking, engagement
signal, browser state, or hidden provider payload participates.

## Scope Boundaries

### In Scope

- A deployment-neutral Adaptation public operation that composes one exact
  Curriculum graph with authorized, exact Learner-model completion views.
- A versioned closed navigation-state response that keeps completion,
  eligibility, required-versus-optional meaning, and availability as separate
  dimensions instead of collapsing them into one brittle status enum.
- Deterministic prerequisite evaluation over the graph's typed activity
  relationships and branch semantics, including multiple entry activities,
  same-kind shared branches, and unbranched activities.
- Stable bounded reason codes and reviewed learner-facing explanations that
  identify exact unmet or satisfied activity references without claiming
  mastery, competence, suitability, or advice.
- A protected learner-context API and generated TypeScript client that never
  accepts a caller-selected learner identity or trusts client-calculated state.
- Accessible map/list annotations that preserve all SLI-0022 graph content and
  provide equivalent non-color state and explanation text in both views.
- Exact-version provenance, source-set digests, fail-closed invalid or stale
  inputs, focused anti-rigidity evidence, and shared local/cloud core semantics.

### Out of Scope

- Recommendation ordering, automatic next-step selection, model inference,
  mastery or competency labels, experiments, engagement optimization, or AI-
  generated explanations.
- Opening or executing an activity, return-to-curriculum behavior, current-
  position history, or curriculum-version change presentation; those belong to
  SLI-0024.
- Manual waivers, instructor overrides, organization policy, cross-curriculum
  credit, enrollment, authoring, certification, or external standards.
- A new completion meaning for assessment-only activity placements. The slice
  may report bounded unavailable or incomplete state until an accepted public
  completion source exists; it may not infer completion from graph presence.
- Durable recommendation records, eligibility history, provider-specific
  state, background delivery, or a managed-cloud adapter.

## Canonical Context and Decisions

- [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
  and the [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  accept deterministic eligibility as Adaptation-owned policy that runs before
  any ranking. They require the rule baseline and prohibit model authority.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) and the
  [Module Map](../../architecture/modules/module-map.md) keep prerequisite and
  pathway meaning in Curriculum, completion projections in Learner model, and
  source evidence in Assessment. The module-map summary must be reconciled with
  the later accepted ADR-0014 ownership before this slice closes.
- [Curriculum Graph Contract](../../architecture/contracts/curriculum-graph-contract.md)
  keeps graph meaning separate from learner-specific state. Adaptation consumes
  the exact public graph; it does not extend or mutate the immutable graph.
- [Decision Readiness](../../adr/decision-readiness.md) classifies adaptive-
  learning authority as constrained: deterministic eligibility and rule
  fallback are allowed, while a concrete model, promotion, ranking influence,
  or online experiment remains outside this slice.
- CAP-0001 supplies the bounded Learner-model lesson-completion projection.
  Completion is not mastery and missing evidence never becomes a positive
  completion or eligibility claim.
- The current CAP-0005 outcome, manifest, ordering, risk posture, and non-goals
  remain unchanged. Later canonical authority resolves the implementation
  owner without activating ranking, recommendations, or model influence.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Adaptation-owned deterministic state projection through protected API and existing map/list | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Server state projection without learner-visible annotations | no - no complete observable learner increment | - | - | - | - | - | - | - | - |
| C. Browser joins graph and completion responses and calculates eligibility | no - makes protected policy client-authoritative | - | - | - | - | - | - | - | - |
| D. Persist a mutable eligibility cache before exposing behavior | no - adds stale derived state without a current durability requirement | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the only eligible vertical increment. It follows the accepted
owner boundaries, delivers the approved learner-visible outcome, and remains
independent of ranking and model infrastructure. Its public operation and
closed transport contract make deterministic replay directly testable, while
the existing SLI-0022 map/list provides the smallest complete UI path. The
projection is computed from authoritative inputs and therefore remains
reversible without a data migration. SLI-0024 depends on this authoritative
state before it can open an eligible destination, and SLI-0025 remains the
final CAP qualification.

## Boundary Path

1. Curriculum returns one validated immutable graph through its public exact-
   version operation; it remains the sole owner of activities, branches,
   prerequisite relationships, and their meaning.
2. An Adaptation-owned gateway obtains current completion for each supported
   exact activity placement through the Learner-model public operation. It does
   not read another module's repository or database schema.
3. A pure deterministic Adaptation policy validates input closure, evaluates
   prerequisite relationships, preserves required/optional meaning as a
   separate dimension, emits bounded reasons, and derives a canonical source-
   set digest. Missing, cross-context, stale, or malformed inputs fail closed.
4. The API host resolves the authenticated learner context, invokes the public
   Adaptation operation, maps only public values into a protected exact-version
   response, and regenerates the TypeScript client.
5. The web route consumes that generated client and annotates the existing
   semantic list and map with equivalent text, labels, and explanation
   relationships. It never recomputes eligibility.
6. Contract, unit, architecture, API, component, and composed-browser checks
   prove deterministic replay, authorization, provenance, accessibility,
   failure behavior, and tolerance for compatible graph shapes.

## Contracts, Data, and Provenance

The slice adds a versioned learner navigation-state response while leaving the
immutable `curriculum-graph-v1` shape unchanged. Each response identifies the
curriculum ID/version/digest, learner-context-bound projection identity,
evaluation-policy ID/version, evaluated time, canonical source-set digest, and
one state record for every visible activity in graph order.

Each activity record keeps orthogonal fields for bounded completion,
eligibility, branch requirement, and availability meaning plus zero or more
stable reason records. Reasons carry closed codes and public graph activity
references, not free-form model output, private answers, raw provider errors,
database identifiers, or learner identifiers. Exact field names, whether
evaluation time is supplied or derived, supported activity-completion sources,
and unavailable-source semantics are frozen in the first work packet before
implementation.

The initial projection is computed on read and adds no durable Adaptation
tables. Learner-model source evidence and Curriculum history remain unchanged.
If later research needs durable recommendation or decision records, that is a
separate accepted slice and migration rather than an implicit cache introduced
here.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Fresh entry activities | With no completion evidence, every available entry activity is eligible and has a stable entry reason; later required activities identify exact unmet prerequisites | Policy/API/browser |
| Completed prerequisite | Accepted exact completion makes the activity complete and deterministically unlocks each dependent activity without claiming mastery | Learner-model gateway/policy/browser |
| Optional branch | Optional work remains visibly optional whether locked, eligible, or complete; completing it does not become a hidden requirement for an unrelated required path | Policy/component/browser anti-rigidity |
| Multiple and shared shapes | Multiple entry activities, same-kind shared branches, unbranched activities, and differently ordered siblings evaluate without a code or contract revision | Policy/contract anti-rigidity |
| Unavailable exact source | An exact activity whose required public source cannot be validated is not eligible and has a bounded unavailable reason; no alternate version is substituted | Gateway/policy/API |
| Missing or stale completion | Missing evidence means incomplete, while malformed, cross-context, stale, or unavailable projection input fails closed without a false positive or hidden-data leak | Gateway/policy/API |
| Exact replay | The same graph, completion source set, policy version, and evaluation input reproduce the same ordered states, reasons, and source-set digest | Unit/integration |
| Unauthorized request | Missing or insufficient server-issued permission returns the standard protected denial without graph, learner, completion, or reason data | API integration |
| Client tampering | Changing browser state, query values, or disabled controls cannot create an eligible server result | API/browser |
| Accessible explanations | List and map expose equivalent non-color text, reason relationships, focus order, zoom/reflow, reduced-motion, forced-color, and light/dark behavior | Component/browser/design-system |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0062 | Freeze the navigation-state contract, pure Adaptation policy, public operation, reason semantics, and focused anti-rigidity corpus | none | none | complete |
| WRK-0063 | Compose Curriculum and Learner-model public gateways, expose the protected API, and regenerate the client | WRK-0062 | none | ready |
| JIT-C | Annotate the existing accessible map/list through the generated client without client-side policy | JIT-B | none | refine after JIT-B completes |
| JIT-D | Qualify the live projection, failure paths, accessibility, provenance, module ownership, and documentation | JIT-C | none | refine after JIT-C completes |

Exact `WRK-*` identifiers replace these seam labels as each bounded packet is
authored. This preserves just-in-time planning and prevents later packets from
freezing implementation detail before earlier contracts have evidence.

## Verification and Qualification

Run navigation-state contract and compatibility checks; Adaptation policy and
gateway unit tests; cross-module import and repository-boundary architecture
tests; protected API and OpenAPI regeneration checks; generated-client usage
checks; web model, component, accessibility, and browser tests; design-system,
documentation, planning, architecture, and diff checks; and
`python dev-tools/agent/check_ready.py`. The final packet must exercise a real
PostgreSQL/Python/web-host/browser path and prove that the browser receives the
server-evaluated state.

Every packet includes at least one excessive-rigidity test appropriate to its
layer. Compatible additions or variations in entry count, sibling order,
optional branches, same-kind sharing, unbranched activities, absent
presentation hints, and reason multiplicity must remain usable without
weakening closed identity, relationship, authorization, or provenance rules.

## Rollback and Migration

The initial policy module, public operation, API response, generated client,
and UI annotations are additive. No new durable table is planned. Rollback
removes the learner-state endpoint and annotations before removing the
Adaptation composition; the SLI-0022 graph route remains fully usable and no
Curriculum, Assessment, or Learner-model evidence is rewritten.

## Stop Conditions

Stop and return to decision review or CAP reshaping if implementation requires
model ranking or inference, a mastery or competency claim, a durable
recommendation record, manual waiver authority, organization policy, a caller-
selected learner identity, client-authoritative eligibility, a new Assessment
evidence meaning, cross-module repository access, provider-specific state,
curriculum graph mutation, a managed-cloud dependency, or an unaccepted
activity-completion source. Also stop for conflicting canonical authority,
material CAP drift, stale CAP approval, active file-scope overlap, or an
external action not covered by current authority.

## Documentation Impact and Completion Evidence

Reconcile the module map with ADR-0014; document the new Adaptation public
boundary and deterministic rule baseline; update Curriculum, Learner-model,
host, API/client, web-feature, architecture-verification, and known-gap
guidance where affected. Completion evidence must state exact tested inputs,
the reason and state matrix, provenance and replay results, authorization and
failure paths, live-browser qualification, accessibility and theme results,
anti-rigidity coverage, assumptions, known gaps, and confirmation that no
model, ranking, mastery, recommendation, provider, or durable state authority
was introduced.

## Planning History

- 2026-10-15: Refined just in time after SLI-0022 completion. Candidate A
  scored 14/14 and remained within the approved CAP-0005 outcome, manifest,
  order, scope, risk, and decision posture. ADR-0014 and the accepted adaptive
  architecture resolve Adaptation ownership for deterministic eligibility;
  ranking, model influence, and recommendations remain excluded. No decision
  or lower-level approval gate was added.
- 2026-10-15: Refined the first packet seam as WRK-0062 around the executable
  navigation-state v1 contract, Adaptation pure rule baseline, public types,
  compatibility corpus, architecture boundary, and direct anti-rigidity tests.
- 2026-10-16: Activated WRK-0062 after the current CAP package, completed
  dependencies, accepted decision posture, exact scope, and implementation gate
  were revalidated and the control plane issued its durable claim.
- 2026-10-16: Completed WRK-0062 with the transport-neutral navigation-state v1
  contract, pure Adaptation policy, stable reason and digest semantics, bounded
  denials, and durable anti-rigidity coverage. JIT-B is now dependency-ready for
  refinement and must consume the published public seams without revising v1
  meaning.
- 2026-10-16: Refined JIT-B as WRK-0063 around the Adaptation application
  composition, public Curriculum and Learner-model gateways, server-issued
  navigation permission, protected exact-version API, reviewed OpenAPI, and
  generated TypeScript client. Assessment-activity completion remains explicitly
  unavailable rather than inferred.
