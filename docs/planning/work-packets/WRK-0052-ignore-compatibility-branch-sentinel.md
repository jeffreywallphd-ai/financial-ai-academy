---
id: WRK-0052
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0003-correction
updated: 2026-10-15
parent: SLI-0013
capability: CAP-0003
depends_on: ["WRK-0021"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/test_portfolio_allocation.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0013-propose-hierarchy-aware-agent-allocations.md", "docs/planning/work-packets/WRK-0052-ignore-compatibility-branch-sentinel.md"]
generated_artifacts: []
base_revision: 2b86cfe4552ab3bf0c6ca2c6707bbdb723aa6d88
claim_id: WRK-0052:8eddc425-b560-45ef-b550-e6fcdb33cdfd
claimed_by: codex-cap-0003-correction
claimed_at: 2026-10-15T19:32:40Z
---

# Agent Work Packet: Ignore the Compatibility Branch Sentinel

## Objective and Deliverable

Prevent a completed work packet's compatibility-only `legacy-unrecorded`
sentinel from being projected as a real Git branch. Preserve the current
checkout's valid `codex/*` branch for active slice and capability allocation
lanes, so historical compatibility state cannot create a false readiness
failure or serialize unrelated progress.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the baseline and delivery-planning
context packs, CAP-0003, SLI-0013, WRK-0021, the bounded correction route for
`compatibility-branch-projection`, the planning/concurrency guidance, the
portfolio adapter and allocator, the local lifecycle-state compatibility
behavior, and the focused allocation tests.

## Decisions and Assumptions

The correction route confines the observed defect to the Financial AI Academy
portfolio adapter and its focused regression tests. `legacy-unrecorded` is a
compatibility marker created when historical work lacks a recorded branch; it
is not a Git branch observation. Treating that sentinel as absent preserves the
existing rule that an active or verifying artifact can use the current checkout
branch. This is a projection repair, not a lifecycle, authority, approval,
branching, provider, or product decision.

## In Scope

- Exclude the exact `legacy-unrecorded` compatibility sentinel from projected
  branch facts.
- Preserve all genuine recorded branches and the current-checkout fallback for
  active or verifying artifacts.
- Add a regression showing completed compatibility state cannot contaminate an
  active container's branch classification.
- Run focused allocation, planning, documentation, and aggregate readiness
  checks required for a shared control-plane correction.

## Out of Scope

Lifecycle-state migration, claim rewriting, deletion of historical state,
branch creation or switching, changes to branch policy, allocation contract
changes, approval changes, product implementation, remote execution,
publication, deployment, push, or unrelated cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project adapter | Lifecycle facts, checkout fallback, container roll-up | `financial_academy_portfolio.py` | Keep compatibility metadata from masquerading as a branch |
| Regression evidence | Repository allocation and no-mutation coverage | `test_portfolio_allocation.py` | Prove active lanes retain the current Codex branch |
| Planning lineage | Completed parent slice, descendant packet, register | Listed planning files | Preserve a bounded correction without reopening terminal history |

## Contracts and Interfaces

`portfolio-allocation-v1` and lifecycle-state schemas remain unchanged. Genuine
claim branches are projected exactly as before. The adapter interprets only the
existing `legacy-unrecorded` sentinel as missing branch evidence; active or
verifying artifacts without genuine branch evidence continue to use the
current checkout branch. Allocation remains read-only and grants no authority.

## Dependencies and Parallel Safety

WRK-0021 is complete. The correction route digest
`sha256:29c161353b9375e3cded0c2f7fa4721a2560fea71a3eddcaecaae11c70651bcc`
confines implementation to the two control-plane files. This packet runs
serially because the adapter and aggregate readiness evidence are shared by
the active CAP-0004 workflow.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Compatibility sentinel | A completed work item records `legacy-unrecorded` | Planning nodes are projected | The sentinel is absent from branch facts | focused unit regression |
| Active container | A sibling/descendant keeps active slice delivery on a `codex/*` checkout | Allocation rolls branch facts to the slice | The in-progress lane reports branch state `codex` | repository CLI regression |
| Genuine branch | A work claim records a real branch | Planning nodes are projected | The recorded branch remains present | focused regression/existing coverage |
| Read-only behavior | The repository allocation CLI runs | Before and after state is compared | No register, claim, lease, or Git branch is mutated | existing CLI regression |
| Bounded correction | The candidate diff is inspected | Qualification completes | No path outside routed implementation and planning lineage changed | scope/diff checks |

## Verification Commands

Run `python dev-tools/control-plane/test_portfolio_allocation.py`, the portfolio
ordering/compatibility/graph suites, `python dev-tools/planning/check_planning.py`,
`python dev-tools/documentation/check_docs.py`, `python
dev-tools/agent/check_ready.py --base-ref <packet-base>`, and `git diff
--check`. Submit and verify the exact committed candidate through the control
plane and obtain independent technical review before deterministic completion.

## Documentation and Evidence Update

Update only this packet, the SLI-0013 correction history, and the planning
register unless the implementation makes another canonical source stale. Keep
all approval and reviewer records only in ignored local storage.

## Stop Conditions

Stop if the correction changes a public allocation or lifecycle schema, ignores
a genuine branch, rewrites historical state, weakens Codex-branch policy,
expands outside the routed paths, conflicts with another live file lease,
introduces a durable decision, or cannot be qualified through a clean exact
candidate.

## Required Handoff

Report the sentinel interpretation, genuine-branch preservation, regression
coverage, focused and aggregate results, independent review disposition,
documentation impact, and whether CAP-0004 delivery can proceed without the
false readiness block.

## Verification Progress

- The Financial AI Academy adapter now treats only the exact
  `legacy-unrecorded` compatibility marker as absent branch evidence. Genuine
  branch values remain unchanged, and active or verifying artifacts without a
  genuine recorded branch continue to use the current checkout.
- Eight focused allocation tests passed, including a direct sentinel/genuine
  branch regression and the read-only repository CLI assertion that in-progress
  lanes report the current Codex branch. Portfolio ordering, compatibility, and
  graph suites each passed seven tests.
- Planning integrity passed for 115 artifacts, documentation validation passed
  for 240 Markdown files plus both catalogs, diff hygiene passed, and the
  aggregate readiness gate passed all 27 checks outside the Windows sandbox
  required by its temporary Git/filesystem fixtures.
- No lifecycle state, claim, branch, public schema, allocation authority, or
  product behavior changed. Exact-candidate affected verification and
  independent technical review remain before completion.

## Planning History

- 2026-10-15: Authored from the bounded completed-work correction route after
  aggregate readiness showed a compatibility-only `legacy-unrecorded` marker
  overriding the current valid Codex checkout. No CAP package, decision, or
  authority change is required.
- 2026-10-15: Implemented the bounded adapter repair and regression; focused,
  planning, documentation, diff, and aggregate readiness checks passed, so the
  packet moved to exact-candidate verification.
