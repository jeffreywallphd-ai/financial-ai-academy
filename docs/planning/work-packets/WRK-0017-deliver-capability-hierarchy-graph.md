---
id: WRK-0017
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0009
capability: CAP-0003
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/portfolio.py", "dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_portfolio.py", "dev-tools/control-plane/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0009-project-capability-hierarchy.md", "docs/planning/work-packets/WRK-0017-deliver-capability-hierarchy-graph.md"]
generated_artifacts: []
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0017:83628652-3923-4a06-a9d3-11190c6cc0dc
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T13:58:02Z
---

# Agent Work Packet: Deliver the Capability Hierarchy Graph

## Objective and Deliverable

Deliver a dependency-free reusable hierarchy/graph core, a Financial AI
Academy catalog/planning adapter, a read-only CLI result, documentation, and
focused tests for the SLI-0009 acceptance scenarios.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed delivery-planning and
testing context, CAP-0003, SLI-0009, planning/concurrency guidance, the product
capability catalog, decision readiness, CAP-0002 reusable contracts, affected
control-plane implementation/tests, and the nearest README before editing.

## Decisions and Assumptions

- The reusable core owns graph semantics; the repository adapter owns CAP/SLI/
  WRK vocabulary and catalog parsing.
- Catalog rows are stable candidate keys derived from normalized names and are
  never treated as governed artifact IDs.
- Missing future SLI files named by an approved CAP manifest are diagnostics,
  not global blockers and not fabricated artifacts.
- Output is read-only and privacy-minimized.

## In Scope

Versioned node/result contracts, deterministic validation and topological
ordering, catalog/planning projection, CLI integration, focused success/failure/
partial-state/anti-rigidity tests, and README command/architecture guidance.

## Out of Scope

Priority/readiness ordering, compatibility, scheduling, file leases, mutable
state, roadmap creation, agents, Git mutation, or external effects.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | Current control-plane contracts/store/tests | `dev-tools/control-plane/portfolio.py`, `test_portfolio.py` | Add project-neutral graph contracts and tests |
| Repository adapter | Planning model, catalog, artifacts | `financial_academy_portfolio.py` | Map canonical repository sources into generic nodes |
| CLI | Existing parser/dispatch/result envelope | `control_plane.py` | Expose one read-only command |
| Documentation/planning | README, slice, packet, register | Exact declared files | Keep operator and lifecycle guidance synchronized |

## Contracts and Interfaces

`portfolio-graph-v1`; stable node kinds, edge types, issue codes, ordering, and
repository-relative sources; existing `ControlError` and success envelope;
adapter function returning generic node dictionaries.

## Dependencies and Parallel Safety

CAP-0002 is complete and the CAP-0003 package is current. The packet is serial
because it establishes shared contracts used by every successor slice.

## Acceptance Scenarios

The SLI-0009 scenario table is normative. Tests also cover duplicate IDs,
self-dependencies, invalid kinds, malformed catalog tables, deterministic
repeatability, empty input, and absence of approval/reviewer metadata.

## Verification Commands

- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Update the control-plane architecture/command guide and record exact slice/
packet evidence without approval metadata. No migration or generated artifact
is expected.

## Stop Conditions

Stop for canonical-source conflict, invented product dependency, authority
inference, mutable behavior, sensitive payload output, non-deterministic graph
results, unresolved decision, or scope outside the declared files.

## Required Handoff

Report graph contracts, adapter behavior, CLI surface, tests and results,
documentation impact, assumptions, residual risks, and CAP conformance.

## Planning History

- 2026-10-15: Authored just in time for the first conforming CAP-0003 slice.
- 2026-10-15: Delivered `portfolio-graph-v1`, catalog/planning adapters,
  read-only CLI projection, README guidance, and seven focused tests; existing
  lifecycle, planning, documentation, readiness, and diff gates passed.
