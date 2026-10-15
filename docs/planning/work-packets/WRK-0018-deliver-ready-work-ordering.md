---
id: WRK-0018
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0010
capability: CAP-0003
depends_on: ["WRK-0017"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/portfolio_ordering.py", "dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_portfolio_ordering.py", "dev-tools/control-plane/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0010-explain-ready-work-and-order.md", "docs/planning/work-packets/WRK-0018-deliver-ready-work-ordering.md"]
generated_artifacts: []
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0018:045aa98a-c80e-4069-ae46-f7f4ae59ca90
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:01:19Z
---

# Agent Work Packet: Deliver Ready-Work Ordering

## Objective and Deliverable

Deliver project-neutral readiness and ordering logic, Financial AI Academy
authority/parent adapters, read-only CLI output, documentation, and focused
tests for CAP, SLI, and WRK levels.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, CAP-0003, SLI-0009/0010,
WRK-0017, routed context, roadmap/planning/concurrency guidance, decision
readiness, current local CAP-binding helpers, portfolio contracts/tests, CLI,
and the nearest README.

## Decisions and Assumptions

- Only hard dependencies and explicit priority/accepted sequence constrain
  order; stable IDs are presentation tie-breakers only.
- Current CAP-package validity is projected as a boolean, never ledger content.
- Completed nodes satisfy dependencies but are omitted from proposed new work.
- A missing future artifact remains unavailable, not a global ordering failure.

## In Scope

Ready/blocked evaluation, proposed order, tie groups, explicit priority
validation, repository authority facts, CLI, docs, and success/denial/
anti-rigidity tests.

## Out of Scope

Compatibility, allocation, leases, mutation, roadmap writing, business scoring,
agent execution, or external effects.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | Portfolio contract | `portfolio_ordering.py`, ordering tests | Add generic readiness/order contract |
| Adapter | Approval binding/planning hierarchy | `financial_academy_portfolio.py` | Supply current authority and parent facts |
| CLI/docs | Parser/dispatch/README | Named files | Expose documented read-only plan command |
| Planning | SLI/WRK/register | Named artifacts | Synchronize lifecycle/evidence |

## Contracts and Interfaces

`portfolio-plan-v1`, level values `capability`, `slice`, `work`, stable reason
codes, explicit priority list, tie groups, and existing result envelopes.

## Dependencies and Parallel Safety

WRK-0017 is complete. This packet changes shared portfolio adapter/CLI files and
is serial with later portfolio slices.

## Acceptance Scenarios

The SLI-0010 table is normative. Tests also cover empty levels, invalid levels,
duplicate priority IDs, priority IDs outside the selected level, decision gates,
active/ineligible states, and deterministic repeatability.

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document readiness/order semantics and the command. Record exact verification
without copying local authority metadata.

## Stop Conditions

Stop for inferred priority, stale authority pass, mutation, hidden ties,
unbounded output, unresolved decision, or scope outside the packet.

## Required Handoff

Report ordering contracts, authority adapter behavior, command/tests,
documentation, assumptions, residual risks, and CAP conformance.

## Planning History

- 2026-10-15: Authored just in time for conforming SLI-0010 delivery.
- 2026-10-15: Delivered `portfolio-plan-v1`, CAP/SLI/WRK readiness, explicit
  priority and tie behavior, current-authority adapter facts, CLI/docs, and
  seven focused tests; all named repository gates passed.
