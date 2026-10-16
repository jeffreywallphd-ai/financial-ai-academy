---
id: WRK-0062
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0023
capability: CAP-0005
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/adaptation/v1/", "contracts/compatibility/adaptation-navigation/v1/", "backend/src/financial_ai_academy/modules/adaptation/", "backend/tests/contract/adaptation_navigation/", "backend/tests/unit/adaptation/", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/modules/module-map.md", "docs/architecture/modules/module-dependency-rules.md", "docs/architecture/contracts/", "contracts/learning/README.md", "backend/src/financial_ai_academy/modules/README.md", "docs/planning/work-packets/WRK-0062-establish-deterministic-navigation-state-core.md", "docs/planning/vertical-slices/SLI-0023-explain-deterministic-curriculum-state.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: a36d2c7dab157f6a4e58fae931a4a561ec6269e1
claim_id: WRK-0062:af305e36-dae8-4ebc-a9b4-1ee036b3aa10
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T00:02:56Z
---

# Agent Work Packet: Establish the Deterministic Navigation-State Core

## Objective and Deliverable

Freeze and implement the transport-neutral `adaptation-navigation-state-v1`
contract, an Adaptation-owned pure deterministic eligibility policy, stable
public value types, and a public operation protocol. The accepted deliverable
can evaluate a validated exact Curriculum graph plus bounded activity-source
facts into one complete ordered navigation-state projection with orthogonal
completion, eligibility, requirement, and availability meaning, stable reason
codes, exact provenance, and a canonical digest. A direct conformance runner
and focused tests must prove both closed denials and flexible compatible graph
shapes before any host, persistence adapter, or browser work begins.

## Required Context

Before changing any file, the implementing agent must read and follow every
applicable `AGENTS.md` and the repository-root `docs/README.md`, then apply its
routing, impact, and decision-readiness instructions. Read the parent
CAP-0005 and SLI-0023 artifacts, ADR-0014, the adaptive-pathway architecture,
ADR-0005, the module map and dependency rules, the curriculum-graph contract
and executable schema/corpus, the Learner-model public completion surface and
nearest README, the contract architecture, the planning register, and the
affected architecture tests before editing.

## Decisions and Assumptions

- ADR-0014 and the accepted adaptive architecture make Adaptation the owner of
  deterministic eligibility and policy application. This packet reconciles the
  stale module-map row; it does not create a new decision.
- Curriculum remains authoritative for graph, prerequisite, activity, and
  required/optional branch meaning. The policy accepts a fully validated exact
  public graph and never changes, repairs, or persists it.
- Learner model remains authoritative for bounded completion. The initial pure
  policy consumes explicit typed source facts so a later adapter can map the
  public projection without importing Learner-model internals.
- Completion, eligibility, branch requirement, and source availability are
  orthogonal closed dimensions. An optional activity may independently be
  complete, eligible, locked, or unavailable.
- Activity prerequisite direction is the Curriculum contract's source-to-
  target direction: the target requires the source. Competency prerequisites
  do not silently become activity gates without an accepted mapping rule.
- Exact field names, enums, reason codes, ordering, canonicalization, digest
  bytes, timestamp profile, and bounded errors are fixed by the executable v1
  contract and compatibility corpus in this packet.
- The rule baseline uses no clock, random source, model, provider, repository,
  web framework, or database. If an evaluation timestamp is part of the
  response, it is an explicit validated input rather than an ambient clock.
- No learner/provider identifier, answer, score interpretation, recommendation,
  rank, mastery label, approval evidence, or free-form upstream error may enter
  the portable projection.

## In Scope

- JSON Schema and README for a complete v1 navigation-state projection and its
  constituent activity state, reason, source-fact, and provenance shapes.
- Compatibility fixtures for a canonical approved projection, optional/shared/
  unbranched/multiple-entry graph shapes, reason multiplicity, partial or absent
  presentation hints, and bounded invalid cases.
- A framework-free Adaptation domain policy that validates input closure,
  derives orthogonal state, evaluates activity prerequisites, retains graph
  order, produces stable reasons, and calculates canonical source and result
  digests.
- Stable Adaptation public request/result/error records and an operations
  protocol suitable for later application composition.
- A direct contract runner that validates and canonicalizes without importing
  API hosts, concrete adapters, or provider code.
- Architecture checks that recognize Adaptation as a module and forbid its
  domain from importing infrastructure or another module's internals.
- Canonical documentation reconciliation for the accepted Adaptation
  deterministic baseline and exact contract semantics.
- Unit, contract, boundary, negative, determinism, and excessive-rigidity tests.

## Out of Scope

- Curriculum or Learner-model gateway adapters, application composition from
  IDs, authentication, authorization, FastAPI, OpenAPI, generated TypeScript,
  browser behavior, or live PostgreSQL qualification.
- Persisting eligibility, recommendations, source facts, projections, or
  policy history; no migration belongs in this packet.
- Ranking, recommendations, mastery, competency publication, experiments,
  models, AI explanations, automatic action selection, or activity launch.
- Creating an assessment-completion semantic not already published by Learner
  model, or treating missing/unsupported evidence as completion.
- Manual waivers, overrides, organization rules, cross-curriculum transfer, or
  provider-specific availability behavior.
- Modifying `curriculum-graph-v1`, Curriculum persistence, Assessment evidence,
  Learner-model projections, API snapshots, generated clients, or web code.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Portable contracts | `contracts/learning/curriculum/v1/`, its compatibility corpus, `contracts/learning/README.md` | `contracts/learning/adaptation/v1/`, `contracts/compatibility/adaptation-navigation/v1/`, learning contract index | Define one provider-neutral navigation-state v1 family and direct fixtures |
| Adaptation module | Curriculum and Learner-model public surfaces and module layout | new `backend/src/financial_ai_academy/modules/adaptation/` files | Add framework-free domain policy and stable public values/protocol only |
| Verification | current graph contract/unit tests and module-boundary tests | new contract/unit suites and bounded updates to `test_module_boundaries.py` | Prove exact meaning, denials, determinism, and dependency direction |
| Canonical architecture | ADR-0014, adaptive architecture, module map/dependency rules, contract index | module map, dependency rules only if needed for the accepted module inventory, and an Adaptation navigation contract document/index entry | Reconcile later accepted ownership and document the executable seam |
| Planning evidence | CAP-0005, SLI-0023, register | this packet, the parent slice packet table/history, and register row | Keep lifecycle and bounded scope current |

No existing Curriculum, Learner-model, Assessment, host, adapter, migration,
OpenAPI, generated client, or browser file may be changed.

## Contracts and Interfaces

The executable contract must represent one exact evaluation input/output
family without duplicating the complete Curriculum graph schema. The Python
public seam may consume Curriculum's published `CurriculumGraph` type, while
portable fixtures bind graph identity/version/digest and explicit per-activity
source facts to the resulting projection.

At minimum, the projection identifies schema version, exact curriculum
identity/version/digest, deterministic policy identity/version, explicit
evaluation time, canonical source-set digest, projection digest, and an ordered
complete activity-state collection. Each activity state identifies the graph
activity and retains separate completion, eligibility, requirement, and
availability values plus zero or more ordered stable reasons. A reason contains
one closed code, bounded reviewed message or message key, and bounded public
activity/relationship references needed for explanation.

Canonical bytes use one documented JSON normalization shared by contract and
domain implementations. The contract runner and domain converter must agree on
timestamps, Unicode code-point bounds, optional fields, empty collections,
ordering, and digest exclusion. Validation errors return a closed code,
bounded message, and sanitized reference; they never expose payloads, paths,
tracebacks, or another module's error text.

The public operation protocol is transport- and adapter-neutral. A later
packet may implement an application service and gateways behind it, but must
not revise v1 state meaning merely to fit a host or database representation.

## Dependencies and Parallel Safety

SLI-0022 and all of its packets are complete. This packet has no within-slice
packet dependency, but it depends on the exact implemented graph and bounded
completion semantics supplied by CAP-0001/SLI-0022. Its write scope establishes
the contract and module seam consumed by every later SLI-0023 packet, so it is
not parallel-safe with them. No active claim may overlap its contract, module,
architecture-test, canonical-doc, or planning paths.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Entry and locked states | A valid graph with one entry activity and one source-to-target prerequisite, and no completions | The pure policy evaluates the exact inputs | The entry is eligible, the dependent activity is locked, and stable reasons identify entry and exact unmet prerequisite meaning | Contract fixture and unit test |
| Deterministic unlock | The prerequisite has exact accepted completion and all sources are available | The same policy/version evaluates | The prerequisite is complete and the dependent activity becomes eligible with a satisfied-prerequisite reason; no mastery claim appears | Unit and conformance test |
| Orthogonal optional meaning | An optional activity is independently locked, eligible, then complete across three inputs | Each input is evaluated | Optional requirement meaning remains unchanged while completion and eligibility vary independently | Anti-rigidity fixture/test |
| Flexible graph shapes | Multiple entry activities, partial or absent presentation hints, same-kind shared branches, unbranched activities, and reordered siblings are valid | The policy evaluates each compatible shape | Every graph activity appears exactly once in deterministic graph order without a schema or code change | Contract/domain anti-rigidity tests |
| Multiple prerequisites | One target has several prerequisite sources with mixed completion | The policy evaluates | The target is locked and emits deterministic bounded reasons for every unmet source rather than assuming one predecessor | Anti-rigidity unit test |
| Source unavailable | A typed source fact marks an exact activity unavailable | The policy evaluates | That activity is unavailable and not eligible with a bounded reason; no alternate version or upstream error text appears | Contract/domain test |
| Missing or conflicting source fact | A graph activity has no fact, an unknown activity has a fact, or duplicate facts disagree | Evaluation runs | The policy fails closed with the expected bounded error and produces no partial projection | Negative unit test |
| Exact replay | Identical graph, source facts, policy identity, and explicit time are evaluated repeatedly | Canonicalization runs | Ordered states, reasons, source-set digest, projection bytes, and projection digest are identical | Determinism test |
| Graph integrity | A malformed, digest-mismatched, or unsupported graph reaches the public policy boundary | Evaluation starts | Existing Curriculum validation fails before Adaptation emits any state | Boundary unit test |
| Bounded denial | Invalid schema, enum, identity, Unicode bound, timestamp, digest, reason reference, or CLI input is supplied | Contract/domain validation runs | A stable bounded denial is returned with no payload, path, traceback, or provider text | Contract CLI and negative tests |
| No model authority | Source and module trees are inspected | Architecture checks run | The Adaptation core imports no AI/model/provider/framework/database layer and contains no rank, score, recommendation, mastery, or engagement field | Architecture test |

## Verification Commands

Run from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/adaptation_navigation backend/tests/unit/adaptation backend/tests/architecture/test_module_boundaries.py
uv run --project backend pytest backend/tests/contract/curriculum_graph backend/tests/unit/curriculum/test_curriculum_graph.py backend/tests/unit/learner_model/test_completion_service.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/architecture/check_architecture.py
python .agents/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0062-establish-deterministic-navigation-state-core.md
python dev-tools/agent/check_ready.py
git diff --check
```

If a named aggregate script has a repository-specific replacement, use the
documented current command and record the exact substitution. The qualifying
candidate must pass the control-plane affected checks and independent review;
the focused commands do not replace the aggregate readiness gate.

## Documentation and Evidence Update

Update the learning-contract index and add the contract README; add the
Adaptation module README and module index entry; reconcile the module-map row
and related ADR references with ADR-0014; add or update the architecture
contract/index describing deterministic navigation state; and update the
parent slice packet table/history plus planning register lifecycle. Record the
contract profile, rule matrix, reason catalog, canonical digest rules,
anti-rigidity evidence, exact checks, assumptions, and known gaps. Do not add
approval or reviewer metadata to tracked artifacts.

## Stop Conditions

Stop for any unresolved meaning of prerequisite direction, completion,
availability, requirement, ordering, canonical digest, or reason semantics;
an unaccepted assessment-completion source; a need to change the Curriculum
graph or Learner-model public contract; model/ranking/recommendation/mastery
authority; persistence or migration; organization or waiver policy; cross-
module internal imports; provider-specific fields; active write-scope overlap;
material CAP drift; stale CAP approval; conflicting canonical sources; or an
external/destructive action not explicitly authorized.

## Required Handoff

Report the exact candidate revision; changed contract/module/doc/test paths;
the closed state, reason, error, ordering, timestamp, and digest profiles;
focused and aggregate check results; anti-rigidity and denial evidence;
documentation reconciliation; assumptions and known gaps; control-plane
receipt; independent review disposition; and confirmation that no API,
persistence, client, UI, model, recommendation, mastery, or external authority
was added. Leave the repository coherent with the packet complete and the next
packet dependency-ready, or return a bounded blocker with no partial claim.

## Planning History

- 2026-10-15: Authored just in time as the first SLI-0023 packet. It freezes
  the deterministic navigation-state contract and Adaptation core before any
  composition or presentation work, stays inside the approved CAP-0005
  outcome and non-goals, and requires direct flexibility tests for every
  compatible graph variation named by the slice.
- 2026-10-16: Submitted exact candidate 58947c0 after the focused contract,
  policy, and architecture suites, the complete backend suite, documentation
  and architecture checks, and all aggregate readiness gates passed. The
  packet is verifying pending exact-candidate control-plane evidence and
  independent review.
