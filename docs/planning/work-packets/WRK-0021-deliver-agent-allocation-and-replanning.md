---
id: WRK-0021
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0013
capability: CAP-0003
depends_on: ["WRK-0018", "WRK-0019", "WRK-0020"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/portfolio_allocation.py", "dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_portfolio_allocation.py", "dev-tools/control-plane/test_portfolio_ordering.py", "dev-tools/control-plane/test_file_leases.py", "dev-tools/control-plane/README.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0013-propose-hierarchy-aware-agent-allocations.md", "docs/planning/work-packets/WRK-0021-deliver-agent-allocation-and-replanning.md"]
generated_artifacts: []
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0021:28c6d6d6-a61b-45be-9f48-1dcc0fa10124
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:12:34Z
---

# Agent Work Packet: Deliver Agent Allocation and Replanning

## Objective and Deliverable

Deliver a reusable single-granularity allocation/replan core, Financial AI
Academy live-fact adapter, read-only CLI/JSON, documentation, and focused safety,
reuse, change-explanation, and anti-rigidity tests.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/testing context,
CAP-0003, SLI-0010 through SLI-0013, WRK-0018 through WRK-0020, current graph/
order/compatibility/file-lease contracts, control-plane CLI/tests, concurrent-
work rules, planning claims, Git branch facts, and the nearest README.

## Decisions and Assumptions

- Each allocation selects one explicit hierarchy level; ancestors are context,
  not duplicate agents or edit owners.
- Ready and in-progress work may be displayed, but only current authority and
  existing claims establish permission; proposal output grants nothing.
- Previous plans are optional input evidence. Change records never overwrite or
  mutate the previous plan.
- Unknown compatibility isolates only the affected unit and preserves unrelated
  compatible opportunities.

## In Scope

Versioned allocation/replan contracts, stable digests, lane/group derivation,
active descendant and branch observations, coordination summaries, prior-plan
comparison, repository adapter, CLI/docs, and focused tests.

## Out of Scope

Agent/thread startup, claim/lease/branch mutation, accepted-roadmap writes,
commit/merge/push, automatic product priority, remote scheduling, or telemetry
and final cumulative qualification owned by SLI-0014.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | Graph/order/conflict contracts | `portfolio_allocation.py`, focused tests | Compose generic proposed lanes and replan changes |
| Repository adapter | Planning, Git, file-lease status | `financial_academy_portfolio.py` | Project current authority and live local facts |
| CLI/docs | Parser/dispatch/guidance | Named files | Expose read-only allocation workflow |
| Planning | SLI/WRK/register | Named artifacts | Synchronize lifecycle and evidence |

## Contracts and Interfaces

`portfolio-allocation-v1`; stable canonical input/plan digests; lane records;
parallel and unresolved groups; categorical change records; existing
`portfolio-graph-v1`, `portfolio-plan-v1`, `portfolio-compatibility-v1`, and
file-edit status inputs; stable `ControlError` refusal envelope.

## Dependencies and Parallel Safety

WRK-0018, WRK-0019, and WRK-0020 are complete. This packet joins their shared
adapter/CLI surfaces and runs serially in the current branch.

## Acceptance Scenarios

The SLI-0013 table is normative. Tests also cover invalid levels/contracts,
deterministic repeatability, priority reorder, active/ready mixing, pairwise set
closure, unknown isolation, no ancestor duplication, lease/intention changes,
prior-plan incompatibility, empty candidates, privacy, and read-only CLI use.

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_allocation.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_file_leases.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document proposal-only semantics, single-level hierarchy safety, branches,
coordination observations, prior-plan comparison, narrow unknown handling, and
the project-adapter seam.

## Stop Conditions

Stop for mutation, inferred authority/priority, cross-level duplicate owners,
opaque rationale erasure, broad unknown-as-conflict behavior, remote effects,
sensitive payloads, unresolved decision, or scope outside this packet.

## Required Handoff

Report contracts, composition, adapter facts, replan behavior, commands, tests,
docs, environment limits, residual risk, and CAP conformance.

## Planning History

- 2026-10-15: Authored just in time for conforming SLI-0013 delivery.
- 2026-10-15: Added the file-lease regression test to scope after normal packet
  progression made its repository-active-lane fixture stale; no contract or CAP
  boundary changed.
- 2026-10-15: Delivered `portfolio-allocation-v1`, repository branch/edit-fact
  projection, CLI/docs, and seven focused generic-vocabulary allocation tests;
  all packet verification commands passed.
