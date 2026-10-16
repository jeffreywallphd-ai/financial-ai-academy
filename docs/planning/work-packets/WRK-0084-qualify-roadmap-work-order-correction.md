---
id: WRK-0084
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-roadmap-order-qualification
updated: 2026-10-16
parent: SLI-0037
capability: CAP-0008
depends_on: ["WRK-0080", "WRK-0081", "WRK-0083"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/financial_academy_roadmap_review.py", "dev-tools/control-plane/portfolio_allocation.py", "dev-tools/control-plane/roadmap_review.py", "dev-tools/control-plane/test_portfolio_allocation.py", "dev-tools/control-plane/test_roadmap_review.py", "dev-tools/roadmap-review-site/README.md", "dev-tools/roadmap-review-site/src/app.ts", "dev-tools/roadmap-review-site/src/model.ts", "dev-tools/roadmap-review-site/tests/app.test.ts", "dev-tools/roadmap-review-site/tests/model.test.ts", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0013-propose-hierarchy-aware-agent-allocations.md", "docs/planning/vertical-slices/SLI-0034-project-dynamic-roadmap-review-data.md", "docs/planning/vertical-slices/SLI-0035-review-capability-order-and-parallelism.md", "docs/planning/vertical-slices/SLI-0037-qualify-dynamic-roadmap-review.md", "docs/planning/work-packets/WRK-0080-align-roadmap-projection-with-executable-allocation.md", "docs/planning/work-packets/WRK-0081-render-executable-roadmap-lanes.md", "docs/planning/work-packets/WRK-0083-promote-active-descendant-allocation-lanes.md", "docs/planning/work-packets/WRK-0084-qualify-roadmap-work-order-correction.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js"]
base_revision: 8d72372ceb4314cf2b7221db257ed75c88ed8ab2
claim_id: WRK-0084:98e13f76-5cba-45c5-a537-32c1eb5d42c3
claimed_by: codex-roadmap-order-qualification
claimed_at: 2026-10-16T11:33:16Z
---

# Agent Work Packet: Qualify the Roadmap Work-Order Correction

## Objective and Deliverable

Qualify the integrated allocator, roadmap projection, and review-site correction
as one exact candidate. Prove that the proposed capability order card shows the
same active and dependency-ready lanes as the control plane, promotes current
descendant work ahead of proposals, and preserves conservative parallel-work
evidence without creating authority or a global scheduling lock.

## Required Context

Read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md` before changing files. Use the index, delivery-planning,
testing-quality, and interface-design packs. Inspect CAP-0003 allocation
contracts, CAP-0008 and SLI-0034 through SLI-0037, WRK-0080, WRK-0081,
WRK-0083, the allocator/projector/site implementation and tests, concurrency
guidance, interface standards, and the nearest control-plane and site READMEs.

## Decisions and Assumptions

- The portfolio allocator remains the reusable source for current executable
  lane proposals; the roadmap projector publishes only a privacy-minimized
  view of that result.
- Active or verifying descendant work is current-execution evidence and may
  promote a lifecycle-ready ancestor ahead of proposals without mutating its
  lifecycle or accepting future priority.
- Unknown or incompatible lane evidence remains conservative and local to the
  affected pair. It never becomes permission to run lanes in parallel.
- This packet performs integrated qualification only. The three dependency
  packets own the implementation changes and were executed sequentially under
  non-overlapping exact-file leases.

## In Scope

- Bind the combined correction to one exact candidate and affected-check plan.
- Verify allocator promotion, deterministic remaining order, dependency
  blocking, projection partition validation, privacy minimization, site model
  validation, and rendered sequential/parallel labels.
- Run focused Python, TypeScript, DOM, loopback, design, planning,
  documentation, diff, and aggregate readiness evidence.
- Record exact outcomes and known environmental limits without copying local
  reviewer or approval records into tracked files.

## Out of Scope

- New capability priority, automatic agent creation, lifecycle mutation,
  approval, packet claims for product delivery, global order locks, hosted
  review access, product application behavior, static roadmap generation,
  styling polish, deployment, publication, or pushing to a remote.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Allocation core | Portfolio ordering, compatibility, allocation and tests | Exact allocator/test files in `write_scope` | Prove active-descendant promotion and conservative lane grouping |
| Roadmap projection | Repository adapter, neutral projection and tests | Exact projector/test files in `write_scope` | Prove the public order uses the executable allocation population |
| Review client | Model, DOM rendering, tests, site README | Exact site files in `write_scope` | Prove displayed order and labels match the projection |
| Planning and guidance | Concurrent-work guide, owning slices, dependency packets, register | Exact planning files in `write_scope` | Keep correction lineage and evidence coherent |

No product runtime, backend module, public application API, generated client,
database, migration, provider, learner record, or design token changes.

## Contracts and Interfaces

Consumes `portfolio-allocation-v1` and publishes its bounded
`roadmap-current-allocation-v1` projection inside `roadmap-review-v1`. The
public projection exposes ordered lane ID, allocation state, lifecycle status,
parallel groups, bounded unresolved-pair summaries, and explicit non-authority
constraints. It omits branches, claims, paths, coordination records, and local
ledger data.

## Dependencies and Parallel Safety

WRK-0080, WRK-0081, and WRK-0083 are complete. This cumulative packet is
serial because it binds their shared exact candidate, planning register, and
cross-boundary evidence. It is not parallel-safe with other roadmap,
allocation, control-plane, or SLI-0037 writes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Current work first | CAP-0030 has active SLI-0125 while CAP-0005 and CAP-0006 are ready proposals | Capability allocation and roadmap projection run | CAP-0030 is first and `in-progress`; CAP-0005 and CAP-0006 follow as proposals | Allocation and roadmap projection tests plus live JSON inspection |
| Conservative grouping | Current lane pairs are incompatible or lack complete evidence | Parallel groups are built | Each affected lane remains sequential and no unknown pair is labeled safe | Allocation/projection and DOM tests |
| Blocked future work | CAP-0007 still depends on incomplete CAPs | Current lanes are projected | CAP-0007 remains advisory blocker context and is absent from current lanes | Allocation and projection tests |
| Exact partition | A malformed allocation duplicates, omits, or invents a lane/group member | Projection/model validation runs | The payload is rejected with bounded remediation | Python projection and TypeScript model tests |
| No authority expansion | The card renders current lanes | A user reviews it | Copy and contract state that the result grants no authority, lease, agent, branch mutation, or global lock | DOM/source qualification |
| Proportionate workflow | Optional styling or unrelated browser setup is unavailable | Qualification runs | Functional checks remain focused; nonfunctional polish does not reopen delivery | Site qualification and aggregate readiness |

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_allocation.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/roadmap-review-site/test_qualification.py`
- `python dev-tools/roadmap-review-site/test_server.py`
- `node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests/app.test.ts dev-tools/roadmap-review-site/tests/model.test.ts`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `python -m compileall -q dev-tools/control-plane dev-tools/roadmap-review-site`
- `git diff --check`

The isolated Chromium check is affected-interface evidence when its prepared
browser can start without taking over an operator-owned server. An occupied
interactive review port is an environment condition, not permission to stop or
replace the operator's process; the isolated verification wrapper remains the
preferred candidate-bound browser path.

## Documentation and Evidence Update

Keep allocator and roadmap READMEs, concurrent-work behavior, SLI-0013,
SLI-0034, SLI-0035, SLI-0037, all four correction packets, and the register
synchronized. Completion evidence records check names, counts, exact candidate
binding, assumptions, and known gaps only. Approval and reviewer identity,
disposition, scope, and history remain exclusively in the ignored local ledger.

## Stop Conditions

Stop for a mismatched allocator/site order, failure to promote current work,
false parallel safety, blocked-future work entering current lanes, malformed
partition acceptance, private coordination disclosure, authority expansion,
breaking contract, unresolved durable decision, active scope collision, or
material CAP-0008 drift. Do not stop for whitespace, advisory copy/style
observations, an occupied operator review port, or nonfunctional visual polish.

## Required Handoff

Report the exact projected lane order and states, affected boundaries, focused
and aggregate checks, documentation impact, assumptions, known gaps, and any
decision still requiring approval. Identify Chromium as performed or bounded by
the operator-owned-server condition without overstating evidence.

## Planning History

- 2026-10-16: Authored just in time as the cumulative qualification seam for
  the three completed bounded corrections. It adds no implementation outcome,
  decision, lower-level approval, global lock, or unrelated full-suite gate.
- 2026-10-16: Marked ready after packet validation and planning integrity
  confirmed exact scope, completed dependencies, executable checks, and
  conformance to the existing CAP-0008 qualification boundary.
- 2026-10-16: Activated from base
  `8d72372ceb4314cf2b7221db257ed75c88ed8ab2` with a three-file documentation
  lease for qualification evidence and lifecycle reconciliation. No product or
  implementation edit is authorized by this packet.
- 2026-10-16: Submitted the integrated exact candidate after current allocation
  reported CAP-0030 first as in progress, followed by CAP-0005 and CAP-0006 as
  proposals, and every required focused and aggregate check passed.
