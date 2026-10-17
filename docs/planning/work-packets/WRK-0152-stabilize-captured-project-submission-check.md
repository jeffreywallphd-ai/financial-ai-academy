---
id: WRK-0152
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: [WRK-0129]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/project-learning-submission.e2e.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0150-qualify-learning-preferences-live-flow.md", "docs/planning/work-packets/WRK-0152-stabilize-captured-project-submission-check.md"]
generated_artifacts: []
base_revision: d5ae96182d0b9060ba7c3d82ea131ff871598c75
claim_id: WRK-0152:aa0f9424-12f9-4814-94a8-91a59e76617b
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T20:40:47Z
---

# Agent Work Packet: Stabilize the Captured Project Submission Check

## Objective and Deliverable

Remove one reproduced timing sensitivity in the existing approved-lesson
Project-submission browser check so the same functional assertion passes when
the control plane captures subprocess output. Preserve the accepted Project
submission behavior and the exact `Submitted checkpoint` assertion.

## Required Context

Read and follow every applicable `AGENTS.md`, `docs/README.md`, the planning
guide/register, CAP-0018, SLI-0074, WRK-0150, completed WRK-0128 and WRK-0129,
the Project-submission browser test, its UI implementation, the live runner,
and the nearest web README before changing a file. The required repository
startup and routed context were completed before this packet was authored.

## Decisions and Assumptions

- The same exact candidate repeatedly passes the full wrapper with inherited
  console output and fails at the same 5-second Project UI assertion when
  stdout/stderr are captured; learner-preference checks have already passed.
- A bounded wait-policy correction in the existing Playwright check requires
  no product, contract, design, identity, provider, or durable decision.
- The functional assertion must remain; the packet may not skip, soften, or
  replace accepted-submission UI evidence with an API-only assertion.

## In Scope

- Give the accepted-submission UI assertion a named timeout appropriate to the
  cumulative captured-output qualification topology.
- Prove the focused Project-submission browser journey and captured-output live
  wrapper pass without changing product code or semantic expectations.
- Record the corrective dependency and neutral completion evidence.

## Out of Scope

Project product behavior, contracts, API, generated client, fixtures, learner-
preference behavior, arbitrary sleep, retry loops, assertion removal, styling,
new dependencies, and any change to unrelated browser checks.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Browser qualification | Project-submission route and assertion | one approved-lesson Playwright file | Make the existing UI assertion timing-robust under captured output |
| Planning | SLI-0074, WRK-0150, this packet, register | listed planning files | Preserve bounded correction provenance and dependency order |
| Product/contract | Project and learner-preference sources | none | No runtime meaning changes |

## Contracts and Interfaces

No interface changes. The browser must still observe the accepted POST response
and the learner-visible `Submitted checkpoint` heading before continuing.

## Dependencies and Parallel Safety

Completed WRK-0129 supplies the qualified browser flow. WRK-0150 depends on this bounded
correction because its controller-selected live receipt captures subprocess
output. This packet is not parallel-safe with WRK-0150 planning closure.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Captured output | Exact candidate runs through a parent process with captured stdout/stderr | First checkpoint is accepted | The named submitted-state heading appears within the bounded qualification timeout | captured wrapper |
| Functional integrity | Accepted submission response | Browser waits for rendered state | The assertion remains present and no API-only substitution or fixed sleep is introduced | diff/review |
| Failure integrity | UI never reaches submitted state | Bounded timeout expires | The test still fails with the named missing state | Playwright semantics |

## Verification Commands

Run TypeScript typecheck and zero-warning lint; the focused Project learning-
submission Chromium journey through the isolated live topology; the exact
captured-output wrapper; planning, documentation, whitespace, controller exact-
candidate verification, proportionate independent review, and aggregate agent
readiness. Use Node 24, npm 10.8.2, pinned Chromium, and disposable PostgreSQL.

## Documentation and Evidence Update

Record the exact candidate, qualifying receipt, captured-output reproduction,
focused/live results, unchanged functional assertion, scope, cleanup, and any
remaining gap. Keep review records only in the ignored local ledger.

## Stop Conditions

Stop for a product-code change, assertion removal, arbitrary delay, fixture or
contract change, unresolved decision, active file collision, failure outside
the reproduced timing boundary, or material CAP/slice drift.

## Required Handoff

Report `CAP-0018.SLI-0074.WRK-0152`, the exact timing correction, focused and
captured-output results, candidate/receipt, review outcome, unchanged product
and contract boundaries, and cleanup.

## Planning History

- 2026-10-17: Authored just in time after WRK-0150 reproduced the same late
  Project-submission UI timeout under captured subprocess output while the exact
  wrapper passed with inherited output. The correction remains test-only and
  inside SLI-0074 qualification; no lower-level approval is required.
- 2026-10-17: Activated from `d5ae961` after confirming completed WRK-0128,
  current CAP authority, exact test-only scope, and exclusive file ownership.
- 2026-10-17: Entered verification after packet/planning/documentation checks,
  TypeScript, zero-warning lint, whitespace, and all 29 aggregate readiness
  checks passed with the functional submitted-state assertions preserved.
- 2026-10-17: Corrected the direct dependency to WRK-0129, which introduced
  and qualified the changed browser check. Implementation and acceptance are
  unchanged.
