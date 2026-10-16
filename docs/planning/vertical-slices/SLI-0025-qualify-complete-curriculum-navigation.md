---
id: SLI-0025
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: CAP-0005
depends_on: ["SLI-0024"]
decision_gates: []
---

# Vertical Slice: Qualify Complete Curriculum Navigation

## Outcome and User Scenario

An authorized learner can complete the full exact-version curriculum journey
from graph inspection through deterministic eligibility, lesson launch,
completion, and return. After the application restarts and the rebuildable
Learner-model projection is reconstructed from retained Assessment evidence,
the same public API reports the same semantic navigation state. A headless
client can perform and verify this journey without depending on browser-only
state or UI implementation details.

This final capability slice assembles evidence for the complete CAP-0005
contract. It does not add recommendation ranking, model inference, a cloud
adapter, or a separate AI execution mode.

## Scope Boundaries

### In Scope

- Extend the isolated composed qualification path with an API-driven
  application restart and deterministic projection-rebuild scenario.
- Use the public session, Curriculum graph, Navigation-state, and activity-
  launch APIs as the authoritative workflow; browser checks remain an
  additional generated-client consumer of those same contracts.
- Retain Assessment source evidence and immutable Curriculum history while
  clearing only rebuildable Learner-model projection rows in the isolated test
  database, then prove reconstruction through normal application operations.
- Compare stable semantic navigation fields before and after rebuild while
  treating bounded observation time and derived digest changes according to
  their public contract rather than brittle byte identity.
- Qualify graph validation, authorization and denial confidentiality,
  interruption, exact-version behavior, provenance, accessibility,
  responsive/theme parity, and flexible compatible graph shapes across the
  completed slices.
- Demonstrate that local and future cloud profiles can reuse the same domain,
  application, contract, and provider-port semantics without claiming that a
  particular cloud adapter has been qualified.
- Record a concise cumulative capability evidence map and close CAP-0005 when
  every acceptance statement has direct evidence.

### Out of Scope

- A separate headless AI mode, agent protocol, model provider, tool-calling
  interface, recommendation service, or AI-authored curriculum operation.
- A specific managed-cloud adapter, tenancy model, cloud recovery profile, or
  provider-specific deployment claim.
- New Curriculum, Assessment, Learner-model, Navigation-state, activity-launch,
  session, or generated-client contract fields.
- Mastery or competency estimation, adaptive ranking, automatic next-step
  selection, experimentation, nudging, or engagement optimization.
- Mutation or replay of Assessment evidence, mutation of immutable Curriculum
  history, production recovery tooling, or a general administrative reset API.
- Styling-only cleanup that does not impair function, accessibility, or
  equivalent information; such work remains eligible for the final cleanup
  capability.

## Canonical Context and Decisions

- [CAP-0005](../capabilities/CAP-0005-navigate-competency-based-curriculum.md)
  defines this final qualification increment and its complete acceptance set.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  separates Curriculum meaning, Assessment evidence, Learner-model
  projections, and host composition.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md)
  requires one shared core rather than local and cloud product forks.
- [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
  keeps deterministic eligibility authoritative and model influence outside
  this capability.
- [Navigation-state Contract](../../architecture/contracts/adaptive-navigation-state-contract.md)
  defines the replayable public state and activity-launch boundaries used by
  both headless and browser consumers.
- SLI-0022 through SLI-0024 supply the validated graph, protected deterministic
  Navigation-state API, protected launch API, generated client, browser
  presentation, exact-version behavior, and live composed-system baseline.
- Decision readiness permits this provider-neutral qualification. Organization
  tenancy, managed-cloud controls, and concrete model/provider behavior remain
  decision-required or constrained and are not activated here.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Extend the isolated API-first live path with application restart, projection rebuild, and cumulative qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add only a meta-runner that aggregates existing checks without a new replay observation | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Implement and qualify one specific managed-cloud adapter | no - provider, tenancy, and managed-cloud protection choices remain unresolved | - | - | - | - | - | - | - |
| D. Add a durable recommendation or navigation-history service for headless agents | no - it changes the capability outcome and activates deferred adaptive authority | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it produces a directly observable recovery
and replay outcome, crosses the complete authoritative path, requires no new
durable decision, reuses stable public contracts, and remains isolated and
reversible. It closes the largest remaining evidence gap: proving that retained
source evidence can reconstruct current navigation meaning after process loss,
including for non-browser clients.

Candidate B is decision-ready and easy to reverse, but it mostly restates
earlier evidence and does not independently observe restart/rebuild behavior,
so its value and end-to-end completeness score one point each. Candidate C
crosses unresolved cloud and tenancy decisions. Candidate D adds state and
adaptive authority that CAP-0005 deliberately excludes. Candidate A therefore
wins without a tie-break and remains conformant to the enumerated SLI-0025
increment.

## Boundary Path

1. The isolated qualification environment starts PostgreSQL and the normal
   local application composition with the approved explicit learning fixtures.
2. A headless HTTP client establishes the server-issued single-profile session
   and reads the exact Curriculum graph, Navigation-state projection, and
   eligible activity launch through versioned public API routes.
3. The generated browser client exercises the same contracts for the complete
   learner-visible journey, including exact lesson opening, completion, and
   return.
4. The qualifier captures stable semantic Navigation-state fields and retained
   Assessment source-evidence counts, then stops the application host.
5. Test-only orchestration deletes only rebuildable Learner-model completion
   projection and history rows inside the isolated database. There is no
   product reset route and no source-evidence or Curriculum mutation.
6. The normal application host restarts against the same database and data
   root. A fresh server-issued session reads the exact public Navigation-state
   API, which reconstructs completion from Assessment public evidence through
   the existing Learner-model operation.
7. The qualifier proves semantic equality, complete provenance, unchanged
   Assessment evidence, and rebuilt projection rows. It then runs the
   cumulative contract, policy, API, generated-client, browser, architecture,
   security, documentation, and readiness checks.
8. Completion evidence maps every CAP acceptance statement to a passing check
   without claiming a particular cloud deployment or AI runtime.

## Contracts, Data, and Provenance

No public contract change is planned. The existing versioned session,
`curriculum-graph-v1`, `adaptation-navigation-state-v1`, and
`activity-launch-v1` operations remain the API-first boundary for browser,
command-line, service, and future headless AI consumers. The TypeScript browser
continues to depend on the generated public client rather than backend
internals.

The replay scenario retains immutable Curriculum rows and Assessment events.
It removes only derived Learner-model completion history/projection rows from
an isolated ephemeral database while the application is stopped. The normal
Learner-model service then rebuilds those rows from Assessment's public replay
source. Evidence records the exact graph and policy versions, source-set and
projection provenance, stable activity-state semantics, source-evidence count,
and rebuilt projection count. Observation timestamps and derived digests are
compared according to their documented meaning rather than assumed to be
identical when a legitimate replay time changes.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Headless complete path | An HTTP-only client establishes an authorized session, reads the exact graph and Navigation state, and resolves an eligible exact lesson launch without browser state | Live API qualification |
| Restart and replay | After stopping the app and clearing only derived Learner-model rows, restart plus a normal API read rebuilds them from unchanged Assessment evidence and returns the same semantic activity states | Live PostgreSQL/application/API qualification |
| Source preservation | Assessment event count and exact source references remain unchanged across replay; Curriculum graph identity/version/digest remain exact | Live database/API provenance checks |
| Invalid graph | Missing references, duplicates, unsupported versions, forbidden cycles, and ambiguous rules remain rejected before learner visibility | Contract/domain/integration tests |
| Authorization and tampering | Missing capability, caller-selected context, stale browser state, or direct locked launch fails closed without protected graph, learner, state, or destination disclosure | API/browser/security tests |
| Exact versions | Coexisting versions retain distinct graph and placement meaning; completion is reused only for intentionally identical exact source references | Integration/live browser tests |
| Interruption | Failed projection replacement or interrupted/superseded client work preserves the last complete state and creates no partial evidence | Persistence/application/component tests |
| Flexible shapes | Compatible additions and ordering variations, optional branches, shared prerequisites, and multiple reasons remain usable without count-specific code changes | Contract/policy/UI anti-rigidity tests |
| Accessible equivalent views | List and map retain equivalent labels, reasons, keyboard order, focus, non-color state, zoom/reflow, reduced motion, forced colors, and theme behavior | Component/browser/design checks |
| Shared-core semantics | Core and public contract tests are deployment-neutral and contain no cloud-provider or local-edition domain fork | Architecture and import-boundary tests |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0090 | Add API-first application restart and isolated Learner-model projection-replay qualification with focused orchestration tests | WRK-0089 | none | complete |
| WRK-0091 | Run cumulative capability qualification, reconcile evidence and documentation, and close SLI-0025 and CAP-0005 | WRK-0090 | none | active |

## Verification and Qualification

Run focused tests for replay comparison, process restart, isolated row reset,
source preservation, teardown, and report shape; the complete live
PostgreSQL/Python/public-API/generated-client/Chromium journey; Curriculum,
Learner-model, Adaptation, Assessment, API, and architecture suites; reviewed
OpenAPI and generated-client checks; web unit/component/browser tests;
accessibility, design-system, security, documentation, planning, whitespace,
and build checks; and `python dev-tools/agent/check_ready.py`.

The live qualifier must use an isolated database and data root, fail closed if
isolation cannot be proved, and clean up its own process, container, and data.
The replay test must prove its delete scope is limited to rebuildable
Learner-model rows. Direct anti-rigidity tests must ensure semantically
irrelevant timestamps, compatible graph growth, sibling ordering, and reason
multiplicity do not cause brittle false failures.

## Rollback and Migration

The planned change is test and documentation infrastructure only. It adds no
public schema, product table, production route, or migration. Rollback removes
the replay phase and its focused tests; the already delivered API and browser
behavior remain intact. Ephemeral database changes occur only inside the
qualifier and are discarded with its isolated environment.

## Stop Conditions

Stop and return to decision review or CAP shaping if qualification requires a
specific cloud provider, organization tenancy, managed-cloud recovery target,
model provider, AI authority, recommendation record, new public product
contract, production projection-reset operation, Assessment evidence mutation,
Curriculum history mutation, client-authoritative eligibility, cross-module
repository access, or a separate local/cloud domain fork. Also stop for
conflicting canonical authority, stale CAP conformance, active write-scope
overlap, inability to prove database isolation, or an external action outside
current authority.

## Documentation Impact and Completion Evidence

Reconcile the Navigation-state contract and local live-qualification guidance
with the explicit restart/replay evidence; preserve generated-client and API-
first guidance; and update this slice, CAP-0005, and the planning register with
public lifecycle state. Completion evidence must map every capability
acceptance statement to exact passing checks and record boundaries, cleanup,
assumptions, and known gaps. It must explicitly state that headless API access
remains available while a separate AI mode, cloud adapter, and adaptive model
plan remain out of scope.

## Planning History

- 2026-10-16: Refined the final CAP-0005 manifest increment after SLI-0022
  through SLI-0024 completed. Candidate A scored 14/14 and adds the missing
  API-first restart/rebuild observation plus cumulative capability evidence
  without changing product contracts, durable decisions, or the CAP package.
- 2026-10-16: Confirmed that public APIs remain the authoritative interface for
  browser and future headless consumers. Planning a separate AI mode remains
  explicitly deferred.
- 2026-10-16: Refined JIT-A as WRK-0090 around a headless public-API client,
  bounded application restart, isolated derived-projection reset, normal
  Learner-model replay, source preservation, and focused orchestration tests.
- 2026-10-16: Activated WRK-0090 after revalidating CAP membership, completed
  dependencies, decision readiness, exact write scope, and collision-free
  ownership.
- 2026-10-16: WRK-0090 implemented a public-API-only headless observation,
  seed-free host restart, isolated derived-projection reset, source-preserving
  replay proof, and direct anti-rigidity coverage without changing product
  contracts or planning a separate AI mode.
- 2026-10-16: Submitted WRK-0090 exact candidate `03f55a5` for affected
  verification and independent review after focused, live, documentation,
  planning, whitespace, and aggregate readiness checks passed.
- 2026-10-16: Independent R01 found one bounded failure-containment gap in
  multi-stage harness teardown. WRK-0090 now attempts all exact cleanup stages
  and preserves primary plus aggregated cleanup diagnostics; CAP scope and
  public API behavior remain unchanged.
- 2026-10-16: Completed WRK-0090 at corrected exact candidate `bb6285e` after
  fresh affected verification passed all six selected checks and independent
  R02 closed R01-F001 with no new findings. JIT-B is dependency-ready.
- 2026-10-16: Refined JIT-B as WRK-0091 for cumulative capability evidence and
  deterministic closure. Public API availability for browser and non-browser
  consumers is a first-class acceptance condition; a separate AI mode remains
  explicitly deferred.
- 2026-10-16: Activated WRK-0091 after validating its dependency, exact
  documentation-only write scope, current CAP package, and collision-free
  claim. Packet-start froze the cumulative acceptance and evidence route.
