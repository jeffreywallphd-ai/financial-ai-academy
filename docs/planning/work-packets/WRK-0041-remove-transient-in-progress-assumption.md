---
id: WRK-0041
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0010
capability: CAP-0003
depends_on: ["WRK-0018"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/test_portfolio_ordering.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0010-explain-ready-work-and-order.md", "docs/planning/work-packets/WRK-0041-remove-transient-in-progress-assumption.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0041:3a9dca97-77c5-43e7-84fc-7c935ab47d5b
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T17:10:48Z
---

# Agent Work Packet: Remove the Transient In-Progress Assumption

## Objective and Deliverable

Correct the repository-adapter ordering test so a safe handoff between slices
does not fail aggregate readiness merely because no slice is momentarily
`active` or `verifying`, while preserving current CAP-authority confinement.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the planning and testing context,
CAP-0003, SLI-0010, WRK-0018, concurrent-work correction protocol, portfolio
ordering/adapter implementation and tests, the bounded correction route for
reason `portfolio.repository-state-assumption`, and the nearest control-plane
and planning README files.

## Decisions and Assumptions

An interval with no in-progress unit is valid after one slice closes and before
the next slice is refined or claimed. Authority confinement—not perpetual
activity—is the safety invariant. Completed histories remain terminal and this
correction adds one descendant packet without reopening WRK-0018 or SLI-0010.

## In Scope

- Replace the repository-state-dependent nonempty `in_progress` assertion with
  checks that every in-progress, ready, or otherwise lifecycle-eligible slice
  belongs to a CAP in the current authority set.
- Assert that slices outside current authority remain explicitly blocked by the
  authority reason.
- Run the focused portfolio-ordering test and aggregate readiness gate.

## Out of Scope

Ordering algorithm changes, graph or adapter semantics, authority-ledger
changes, lifecycle mutation, new approval behavior, portfolio allocation,
production feature work, and reopening any completed artifact.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Ordering behavior | Project-neutral planner and repository adapter | none | Existing behavior is correct in an empty handoff interval |
| Anti-rigidity test | Repository-adapter test | Listed test file | Test the invariant without requiring artificial activity |
| Planning | Completed parent slice, new descendant, register | Listed artifacts | Preserve correction lineage without reopening history |

## Contracts and Interfaces

The `portfolio-plan-v1` result remains unchanged. The test evaluates
`in_progress`, `ready`, and `blocked` categories and the stable
`authority.cap-package-not-current` reason; no public or local-state schema
changes.

## Dependencies and Parallel Safety

WRK-0018 is complete and the control-plane correction router classified this
exact test path as a bounded descendant of SLI-0010. The packet is not declared
parallel-safe because it touches shared ordering qualification evidence.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty handoff interval | A current CAP has no active/verifying slice for an instant | Repository adapter test runs | Readiness does not fail solely because `in_progress` is empty | focused test/aggregate gate |
| Current delivery candidate | A slice is in progress, ready, or lifecycle-eligible | Plan is projected | Its capability ancestor is in the current authority set | focused test |
| Noncurrent slice | A slice belongs to a CAP outside current authority | Plan is projected | It retains `authority.cap-package-not-current` in its reasons | focused test |
| No semantic drift | Test correction is applied | Ordering suite runs | All project-neutral ordering behavior remains unchanged | full ordering suite |

## Verification Commands

Run the work-packet validator, implementation gate, focused portfolio-ordering
test, planning integrity, aggregate readiness against the current base, docs
check, and `git diff --check`.

## Documentation and Evidence Update

Update only this descendant packet, the parent slice history, and the planning
register. No canonical control-plane behavior or context changes because the
implementation contract remains unchanged.

## Stop Conditions

Stop if the correction would permit noncurrent authority, change ordering or
allocation semantics, mutate local approval evidence, reopen completed history,
expand beyond the routed test path, or require a durable decision.

## Required Handoff

Report the removed rigidity assumption, preserved authority invariant, focused
and aggregate results, documentation impact, and whether CAP-0001 routing can
resume.

## Verification Progress

- The repository-adapter test no longer requires a globally nonempty
  `in_progress` list. It now checks every in-progress, ready, or
  lifecycle-eligible blocked slice against the current CAP authority set and
  separately proves that every noncurrent slice retains the explicit
  `authority.cap-package-not-current` reason.
- The focused portfolio-ordering suite passed seven tests, including
  dependency ordering, authority denial, priority validation, and read-only CLI
  behavior. No planner, graph, adapter, allocation, or schema code changed.
- The fixed aggregate readiness gate passed all 27 checks against base revision
  `515c2e16e4458b1305a89acd594085c828fe49ec`, including anti-rigidity,
  portfolio ordering, compatibility, allocation, file-edit coordination,
  qualification, and real-core corpus evidence.
- The correction remained confined to the router-approved test path plus
  planning lineage. It reopened no terminal artifact and introduced no
  decision, approval, or authority change. CAP-0001 routing can resume.

## Planning History

- 2026-10-15: Authored from the bounded completed-work correction route after
  SLI-0016 closure exposed a valid no-in-progress handoff interval. No behavior,
  authority, decision, or CAP-package change is required.
- 2026-10-15: Corrected the transient global-state assumption; focused and
  aggregate evidence passed while the authority-confinement invariant remained
  explicit.
