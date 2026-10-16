---
id: WRK-0083
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-order-correction
updated: 2026-10-16
parent: SLI-0013
capability: CAP-0003
depends_on: ["WRK-0021", "WRK-0052"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/portfolio_allocation.py", "dev-tools/control-plane/test_portfolio_allocation.py", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0013-propose-hierarchy-aware-agent-allocations.md", "docs/planning/work-packets/WRK-0083-promote-active-descendant-allocation-lanes.md"]
generated_artifacts: []
base_revision: 8d72372ceb4314cf2b7221db257ed75c88ed8ab2
claim_id: WRK-0083:695e6320-7087-485e-a6af-103bd515b050
claimed_by: codex-roadmap-order-correction
claimed_at: 2026-10-16T11:26:37Z
---

# Agent Work Packet: Promote Active-Descendant Allocation Lanes

## Objective and Deliverable

Correct `portfolio-allocation-v1` so a lifecycle-ready container at the
requested hierarchy level is presented as in-progress, ahead of proposed lanes,
when descendant work is active or verifying even if the container's own
lifecycle field has not been advanced. Preserve the deterministic order of
remaining proposals and the proposal-only, non-authorizing control boundary.

## Required Context

Read and follow repository `AGENTS.md`, `docs/README.md`, routed delivery and
testing context, CAP-0003, SLI-0013, WRK-0021, WRK-0052, the correction route,
portfolio graph/order/compatibility/allocation contracts, concurrent-work
guidance, control-plane README, affected implementation, and focused tests
before changing files.

## Decisions and Assumptions

- Active or verifying descendant lifecycle and active-claim evidence is current
  execution evidence, not product priority or new authority.
- Direct in-progress lanes retain precedence; descendant-promoted lanes follow
  in deterministic proposed-order or stable-ID order; remaining proposals keep
  their existing relative order.
- The lane retains its container lifecycle status while
  `allocation_state: in-progress`, `active_descendants`, and rationale explain
  the promotion.
- Work-level allocation is unchanged because work items have no governed
  descendants at a lower planning level.

## In Scope

- Derive active descendants before assembling candidate lane order.
- Promote containers with active/verifying descendants into the in-progress
  prefix without duplicating them.
- Preserve proposed-lane relative order, compatibility grouping, read-only
  behavior, and existing contract shape.
- Add generic focused tests for promotion, order, lifecycle/rationale clarity,
  blocked future work, and anti-rigidity.
- Document the execution-evidence precedence rule.

## Out of Scope

Lifecycle mutation, CAP priority acceptance, dependency rewrites, automatic
agent creation, claims, leases, branches, remote scheduling, roadmap-specific
ordering logic, schema-version changes, or product behavior.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Allocation core | order, descendant, grouping, replan composition | `portfolio_allocation.py` | Promote observed active descendant work |
| Focused evidence | generic allocator and repository CLI tests | `test_portfolio_allocation.py` | Prove order, state, and anti-rigidity |
| Operator guidance | allocation and concurrency semantics | named README and concurrent-work guide | Explain evidence precedence without authority drift |
| Planning lineage | parent slice, packet, register | exact named planning files | Retain bounded correction evidence |

## Contracts and Interfaces

`portfolio-allocation-v1` remains unchanged. Existing lane fields express the
correction: `allocation_state` becomes `in-progress`, `lifecycle_status`
retains the container's actual status, `active_descendants` names the evidence,
and `rationale` adds `lifecycle.descendant-in-progress`.

## Dependencies and Parallel Safety

WRK-0021 and WRK-0052 are complete. Correction route
`sha256:c26bd2029154d752b0eca06fadbe3396d657f75a5d3d36b2ed319e03bbb157eb`
bounds the affected core, focused test, and operator-documentation paths. The
packet is serial with the uncommitted roadmap projection correction because the
roadmap consumes this allocator result.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Descendant promotion | A ready container has active or verifying descendants | Allocation runs at the container level | Its lane is first-class in-progress with exact descendants and rationale | Generic core regression |
| Proposal preservation | Ready proposals have deterministic priority order | One later proposal is descendant-promoted | The promoted lane precedes proposals and remaining proposals keep relative order | Order regression |
| Future blocker | Another container is dependency-blocked | Descendant promotion occurs | The blocker remains excluded from lanes without globally locking unrelated proposals | Anti-rigidity regression |
| No duplication | A container is already directly in progress and has active descendants | Allocation runs | It appears once with direct lifecycle rationale | Generic core regression |
| Roadmap composition | The repository has active CAP-0030 descendants | Capability allocation and roadmap projection run | CAP-0030 is first and in-progress, followed by CAP-0005 and CAP-0006 proposals | Repository command evidence |

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_allocation.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Update allocation/operator guidance and planning evidence with descendant
promotion semantics, focused results, and the exact repository lane order. Do
not record local approval/reviewer metadata or generated projections.

## Stop Conditions

Stop for lifecycle or authority mutation, accepted priority invention,
cross-level duplicate ownership, a new schema, client-specific scheduling in
the core, broad unknown-as-lock behavior, remote effects, an unresolved durable
decision, a path outside the correction route, or an active edit collision.

## Required Handoff

Report promotion semantics, exact current CAP lane order, focused and aggregate
checks, unchanged contract/authority boundaries, documentation impact, and any
qualification not performed.

## Implementation Evidence

- The generic allocator now derives descendant activity before lane assembly.
  A lifecycle-ready container with active/verifying descendants moves into the
  in-progress prefix, retains its actual lifecycle status, names the descendants,
  and carries `lifecycle.descendant-in-progress` rationale. Direct in-progress
  lanes remain first, completed containers remain terminal, and remaining
  proposals preserve deterministic relative order.
- A generic regression promotes `PROGRAM-C` ahead of explicitly prioritized
  `PROGRAM-B` and `PROGRAM-A`, leaves both proposals ordered, keeps blocked
  `PROGRAM-FUTURE` out of lanes, and proves a directly active container is not
  duplicated or given descendant-only rationale.
- The current capability allocation and roadmap projection both emit
  `CAP-0030` first as `in-progress` with `SLI-0125` evidence, followed by
  `CAP-0005` and `CAP-0006` as `proposed`. CAP-0007 remains dependency-blocked.
- The allocation contract and schema version are unchanged; the proposal still
  creates no agents, grants no authority, mutates no branches, and acquires no
  leases.
- The allocation suite passed 10 tests outside the Windows sandbox; ordering
  and compatibility passed 7 tests each; roadmap projection passed 13 tests;
  planning validated 158 artifacts; documentation validated 301 Markdown files
  plus catalogs; diff checks passed; and aggregate readiness passed all 27
  checks outside the Windows temporary-directory sandbox.

## Planning History

- 2026-10-16: Authored from the bounded WRK-0021 correction route after roadmap
  parity work exposed that active descendant work was reported on a proposed
  ancestor lane and therefore ordered behind not-yet-started proposals.
- 2026-10-16: Implemented and verified lifecycle-ready ancestor promotion with
  exact current CAP-0030/CAP-0005/CAP-0006 parity through the roadmap consumer.
