---
id: WRK-0081
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-order-correction
updated: 2026-10-16
parent: SLI-0035
capability: CAP-0008
depends_on: ["WRK-0025", "WRK-0080"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/roadmap-review-site/README.md", "dev-tools/roadmap-review-site/src/app.ts", "dev-tools/roadmap-review-site/src/model.ts", "dev-tools/roadmap-review-site/tests/app.test.ts", "dev-tools/roadmap-review-site/tests/model.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0035-review-capability-order-and-parallelism.md", "docs/planning/work-packets/WRK-0081-render-executable-roadmap-lanes.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js"]
base_revision: 8d72372ceb4314cf2b7221db257ed75c88ed8ab2
claim_id: WRK-0081:9c17fd59-ccab-4986-8370-68b6809ab3a3
claimed_by: codex-roadmap-order-correction
claimed_at: 2026-10-16T11:21:39Z
---

# Agent Work Packet: Render Executable Roadmap Lanes

## Objective and Deliverable

Correct the roadmap review site's “Proposed capability order” and parallel-work
sections to render the allocator-derived current capability lanes delivered by
WRK-0080. Make sequential singleton lanes and multi-capability parallel-safe
groups explicit while retaining blockers, ties, and future order as advisory
context rather than a repository-wide lock.

## Required Context

Read and follow repository `AGENTS.md`, `docs/README.md`, routed delivery,
testing, and interface context, CAP-0008, SLI-0035, WRK-0025, WRK-0080,
`roadmap-review-v1`, site README, design and content standards, current client
model/rendering, and focused DOM/model tests before changing files.

## Decisions and Assumptions

- `current_allocation.lanes` is the canonical source for the card's current
  order; the client does not recompute readiness or compatibility.
- `current_allocation.parallel_groups` is the canonical source for displayed
  current parallel lanes, including singleton sequential lanes.
- `ordering` remains visible for blockers and unresolved future prioritization
  only. It neither grants authority nor blocks work globally.
- Existing design-system primitives are sufficient; no token or icon change is
  required.

## In Scope

- Add strict client typing and envelope validation for current allocation.
- Render current executable lanes in exact allocator order.
- Label every lane with its sequential or evidence-backed parallel group.
- Use current allocation groups in the parallel-work summary while preserving
  full compatibility diagnostics separately.
- Add DOM/model regressions covering a blocked future capability, deterministic
  lane order, singleton sequential lanes, and one multi-capability parallel
  group.
- Update operator guidance and planning evidence.

## Out of Scope

Allocation/order/compatibility algorithm changes, planning writes from the
site, accepted priority input, graphical scheduling, claims, agent creation,
file leases, hosted access, or product-application integration.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Client contract | roadmap envelope types and guard | `src/model.ts` | Require the allocator-derived projection |
| Overview rendering | order and parallel evidence sections | `src/app.ts` | Show exact current sequential/parallel lanes |
| Focused evidence | view-model and DOM fixtures/assertions | named site tests | Prove parity and anti-rigidity |
| Operator guide | overview meaning and focused commands | site README | Explain current versus future evidence |
| Planning lineage | parent slice, packet, register | exact named planning files | Retain bounded correction evidence |

## Contracts and Interfaces

Consume the additive `roadmap-review-v1.current_allocation` contract from
WRK-0080. Do not derive a second client-side order or compatibility model.

## Dependencies and Parallel Safety

WRK-0025 and WRK-0080 are complete. Correction route
`sha256:8f653455025289683ada965f8fd485a92c632b501497c6d3897e684a2bf85a55`
bounds the affected site paths. This packet is serial because it consumes the
new projection member and overlaps the completed overview boundary.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact order | Current allocation order differs from broader future order | Overview renders | The card follows current allocation lane order exactly | DOM regression |
| Future advisory work | A dependency-blocked capability remains in ordering evidence | Overview renders | It appears in blockers but not the current executable lane list | Anti-rigidity DOM regression |
| Sequential lane | A current allocation group contains one capability | Overview renders | The capability is labeled as a sequential lane, not parallel-safe work | DOM regression |
| Parallel-safe lane | A current allocation group contains multiple capabilities | Overview renders | The grouped capabilities are shown together and each order item identifies the same parallel group | DOM/model regression |
| Malformed response | Current allocation is missing or internally inconsistent | Client loads the envelope | The response is rejected as incompatible instead of inventing order | Model regression |

## Verification Commands

- `node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/roadmap-review-site/test_server.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- Packet-start selected checks and `git diff --check`

## Documentation and Evidence Update

Update the site guide and planning records with the allocator-derived display
semantics, focused results, and explicit non-authority boundary. Do not commit
compiled client output or generated roadmap data.

## Stop Conditions

Stop for client-side scheduling logic, a second order engine, treating unknown
evidence as safe, hiding blockers, turning advisory future order into a global
lock, planning mutation, a new shared visual primitive, hosted exposure, a path
outside the correction route, or an active edit collision.

## Required Handoff

Report exact rendered ordering/group behavior, anti-rigidity evidence, focused
checks, accessibility/theme impact, documentation impact, and any qualification
not performed.

## Implementation Evidence

- The “Proposed capability order” card now iterates
  `current_allocation.lanes` in allocator order. Each entry identifies its
  current lifecycle state and either its singleton sequential lane or shared
  evidence-backed parallel-safe group.
- The parallel-work section now renders allocator groups, while the existing
  full compatibility pairs remain available as diagnostic evidence. Blocked
  and future capabilities remain in the blocker/tie context and never enter the
  current lane list unless the allocator makes them active or dependency-ready.
- The client rejects a missing or internally inconsistent current allocation;
  it does not recompute order or treat unknown compatibility as safe. Authority,
  claims, agents, branches, and leases remain outside the site boundary.
- TypeScript checking passed; 12 focused DOM/model tests passed outside the
  Windows sandbox; the projection suite passed 13 tests; the loopback server
  suite passed 8 tests outside the socket sandbox; and the site qualification
  suite passed 6 tests. Design validation reported 125 tokens and 56 icons,
  planning validated 157 artifacts, documentation validated 300 Markdown files
  plus catalogs, diff checks passed, and aggregate readiness passed all 27
  checks outside the Windows temporary-directory sandbox.
- Focused Chromium qualification was attempted but did not start because the
  operator's existing review server already owned `127.0.0.1:8765` and the
  Playwright config intentionally refuses reuse. No process was displaced;
  DOM, type, server, accessibility-source, and aggregate evidence cover this
  bounded rendering correction.

## Planning History

- 2026-10-16: Authored after WRK-0080 established allocator-derived current
  lanes and the existing overview was confirmed to render broader future order
  and all-eligible compatibility groups instead.
- 2026-10-16: Implemented and verified exact allocator-order rendering,
  sequential and parallel lane labels, strict client validation, and explicit
  non-authority language without adding a client-side scheduler.
