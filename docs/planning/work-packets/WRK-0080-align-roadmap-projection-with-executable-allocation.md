---
id: WRK-0080
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-order-correction
updated: 2026-10-16
parent: SLI-0034
capability: CAP-0008
depends_on: ["WRK-0024"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/financial_academy_roadmap_review.py", "dev-tools/control-plane/roadmap_review.py", "dev-tools/control-plane/test_roadmap_review.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0034-project-dynamic-roadmap-review-data.md", "docs/planning/work-packets/WRK-0080-align-roadmap-projection-with-executable-allocation.md"]
generated_artifacts: []
base_revision: 8d72372ceb4314cf2b7221db257ed75c88ed8ab2
claim_id: WRK-0080:2b136fdf-f893-4dcd-ba82-fd67782a7402
claimed_by: codex-roadmap-order-correction
claimed_at: 2026-10-16T11:19:51Z
---

# Agent Work Packet: Align Roadmap Projection with Executable Allocation

## Objective and Deliverable

Correct `roadmap-review-v1` so its current capability execution order and
parallel groups come from the same deterministic `portfolio-allocation-v1`
composition used by the control-plane workflow. Preserve the broader
dependency-aware ordering result as advisory future context, and expose only a
privacy-minimized allocation view suitable for a read-only review client.

## Required Context

Read and follow repository `AGENTS.md`, `docs/README.md`, the routed delivery,
testing, and interface context, CAP-0008, SLI-0034, WRK-0024, CAP-0003's
allocation/order/compatibility cores, the correction route, control-plane
README, affected implementation and tests before changing files.

## Decisions and Assumptions

- `portfolio_allocation.allocate` remains the single reusable composition for
  active plus dependency-ready lanes and their conflict-free groups.
- `portfolio_ordering.plan` remains useful advisory evidence for blocked and
  future work; a future position does not become an execution lock.
- The public projection omits branch, claim, lease path, and coordination
  details that are unnecessary for roadmap review.
- The additive contract requires no migration or durable architecture choice.

## In Scope

- Compose the default capability allocation in the repository adapter.
- Validate and project a safe current-allocation subset with lane order,
  allocation/lifecycle state, parallel groups, unresolved pair summaries, and
  non-authority constraints.
- Prove exact parity with the control-plane allocator, including a future
  dependency-blocked capability omitted from current executable lanes.
- Document the distinction between current executable allocation and advisory
  future order.

## Out of Scope

Ordering or compatibility algorithm changes, accepted priority capture,
planning mutation, agent creation, claims, file leases, remote scheduling,
provider selection, or UI rendering changes owned by WRK-0081.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable projection | roadmap contract and validation | `roadmap_review.py` | Publish a bounded allocator-derived view |
| Repository adapter | graph/order/compatibility/allocation composition | `financial_academy_roadmap_review.py` | Use the canonical current execution composition |
| Contract tests | generic and repository projection scenarios | `test_roadmap_review.py` | Prove exact order/group parity and anti-rigidity |
| Operator guide | dynamic roadmap data guidance | control-plane README | Explain current versus future ordering |
| Planning lineage | parent slice, packet, register | exact named planning files | Retain bounded correction evidence |

## Contracts and Interfaces

Add a backward-compatible `current_allocation` member to `roadmap-review-v1`,
derived from `portfolio-allocation-v1`. Keep existing `ordering` and
`compatibility` members unchanged for future blockers, ties, and diagnostic
evidence.

## Dependencies and Parallel Safety

WRK-0024 is complete. Correction route
`sha256:e8b80bef2e5e09f2ab831bcc15241c1732034922e676dc891b3c3823bcac5b95`
bounds the affected implementation paths. This packet is serial with WRK-0081,
which consumes the additive projection contract.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Current execution parity | Default capability allocation contains active and dependency-ready lanes | Roadmap data is projected | Current allocation lane order and parallel groups exactly match the allocator | Repository integration test |
| Future advisory order | The dependency plan includes a future blocked capability | Roadmap data is projected | The capability remains in ordering/blocker evidence but is absent from current executable lanes | Anti-rigidity regression |
| Parallel-safe work | Two current lanes are mutually compatible | The generic projection is built | Both appear in one current parallel group in deterministic order | Generic contract test |
| Privacy | Allocation contains local branch and coordination details | The public roadmap is serialized | Unnecessary branch, claim, lease, and coordination details are absent | Privacy regression |
| Malformed allocation | Groups do not partition the projected lanes | Projection is attempted | The input is refused with bounded remediation | Contract validation test |

## Verification Commands

- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/control-plane/test_portfolio_allocation.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- Packet-start selected checks and `git diff --check`

## Documentation and Evidence Update

Update the operator explanation and planning records with exact checks and the
current-versus-future distinction. Do not record local reviewer or approval
metadata and do not commit a generated roadmap projection.

## Stop Conditions

Stop for changed allocation semantics, a second ordering engine, disclosure of
local coordination details, a global priority lock, planning mutation, a path
outside the correction route, an unresolved durable decision, or an active
edit collision.

## Required Handoff

Report the canonical source used, projected contract shape, exact parity and
anti-rigidity evidence, privacy posture, documentation impact, and remaining UI
consumption work for WRK-0081.

## Implementation Evidence

- `roadmap-review-v1.current_allocation` now projects the canonical allocator's
  ordered capability lanes, parallel groups, unresolved pair summaries, and
  non-authority constraints without branch or coordination detail.
- The repository adapter composes `portfolio_allocation.allocate` with the same
  graph, current CAP authority, empty explicit priority, and empty accepted
  sequence as the default workflow. Existing broader `ordering` and
  `compatibility` evidence remains available for blockers and future context.
- The current repository projection and allocator both produce lanes
  `CAP-0005`, `CAP-0006`, and `CAP-0030`; dependency-blocked `CAP-0007` remains
  in future ordering evidence but is not presented as currently executable.
- The roadmap projection suite passed 13 tests, the allocator suite passed 9
  tests outside the Windows sandbox for its temporary-directory fixture,
  planning validated 156 artifacts, documentation validated 299 Markdown files
  plus catalogs, and diff checks passed.


## Planning History

- 2026-10-16: Authored from the bounded WRK-0024 correction route after the
  roadmap order card was found to bypass the allocator and include a
  dependency-blocked future capability as if it were executable.
- 2026-10-16: Implemented and verified the additive, privacy-minimized current
  allocation projection with exact default-allocator parity and explicit
  anti-rigidity coverage.
