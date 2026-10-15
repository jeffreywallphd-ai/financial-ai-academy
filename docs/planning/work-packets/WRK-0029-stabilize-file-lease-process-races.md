---
id: WRK-0029
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0012
capability: CAP-0003
depends_on: ["WRK-0023"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/file_leases.py", "dev-tools/control-plane/store.py", "dev-tools/control-plane/test_file_leases.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0012-coordinate-exclusive-file-edits.md", "docs/planning/work-packets/WRK-0029-stabilize-file-lease-process-races.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0029:5f3d9a09-3e67-4339-943c-699a010d2bb6
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:09:26Z
---

# Agent Work Packet: Stabilize File-Lease Process Races

## Objective and Deliverable

Correct the completed exact-file coordination path so two independent local
processes racing for the same canonical file always produce one successful
lease and one bounded `edit.lease-contended` result. The reusable lock/store
primitive must remain atomic without introducing repository-wide, directory,
read, or unrelated-file serialization.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read CAP-0003, SLI-0012, WRK-0020,
WRK-0023, concurrent-work rules, the project-neutral state store and file-lease
core, the Financial AI Academy adapter, focused race tests, testing standards,
and the completed-work correction route.

## Decisions and Assumptions

- This is a bounded defect in completed CAP-0003 behavior discovered by the
  SLI-0001 aggregate gate. It does not change CAP-0003's outcome, public
  commands, local-only coordination boundary, or single-writer policy.
- The losing same-file racer must be classified at the lease contract as
  contention. Internal lock contention, partial state visibility, or a stale
  lock artifact must not leak as an ordinary same-file outcome.
- Reads and edits to different exact files remain concurrent. A fix that makes
  a broad lock a user-visible prerequisite is not acceptable.

## In Scope

- Capture the exact intermittent loser outcome and add deterministic regression
  diagnostics.
- Correct the project-neutral lock/state transition responsible for the race
  while retaining atomic state publication and bounded failure handling.
- Stress same-file acquisition across independent processes and retain existing
  alias, multi-file, expiry, recovery, privacy, scope, and anti-rigidity tests.
- Re-run control-plane, planning, documentation, and aggregate readiness gates,
  then resume WRK-0028 and SLI-0001 verification.

## Out of Scope

- Cross-host consensus, remote coordination, read locks, directory or
  repository locks, automatic retries that hide an active owner, longer lease
  duration, new user approvals, lifecycle-policy changes, or product behavior.
- Web dependency changes, lesson behavior, CAP-0001 contracts, external
  publication, branch integration, or production mutation.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generic store | Exclusive lock and atomic publication | `store.py` only if root cause is shared | Preserve process-safe atomic mutation |
| File-lease core | Acquisition and state classification | `file_leases.py` only if root cause is lease-specific | Guarantee one owner and bounded contention |
| Regression | Core, process race, expiry, disjoint-file tests | `test_file_leases.py` | Prove safety and non-rigidity repeatedly |
| Planning | Owning slice, packet, register | Named artifacts | Preserve correction lineage and evidence |

## Contracts and Interfaces

Preserve `file-edit-state-v1`, `file-edit-lease-v1`, `file-edit-intent-v1`,
existing CLI/JSON result shapes, `edit.lease-contended`, explicit expiry
recovery, and the ignored local storage boundary. No product, API, event,
database, browser, or external contract changes.

## Dependencies and Parallel Safety

WRK-0023 is complete and the controller accepted a bounded correction route
from WRK-0020 for `file_leases.py` and `test_file_leases.py`. The packet is
serial because it changes the shared reusable lock/lease core and qualification
evidence. It has no parallel-safe peer.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Same-file race | Two independent processes request the same canonical file | Acquisitions overlap repeatedly | Exactly one succeeds and exactly one returns `edit.lease-contended` every run | Focused stress test with actionable failure output |
| Disjoint files | Two owners request different files | Acquisitions overlap | Both may proceed; no broad user-visible lock blocks either lane | Existing anti-rigidity test |
| Reads remain free | A live lease exists | Another actor inspects status or reads repository data | No read lease is required | Status/core test |
| Atomic multi-file refusal | One requested file is already owned | A multi-file request runs | Nothing is partially acquired | Existing transaction test |
| Recovery semantics | A live or expired owner exists | Recovery is attempted | Live preemption is refused and expired complete-set recovery retains lineage | Existing expiry tests |
| Aggregate stability | The corrected focused suite is green under stress | Repository readiness runs | File-edit coordination and all other gates pass without relaxing assertions | `check_ready.py` and full local qualification |

## Verification Commands

```powershell
python dev-tools/control-plane/test_file_leases.py
python dev-tools/control-plane/test_qualification.py
python dev-tools/control-plane/test_portfolio_qualification.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
npm --prefix apps/web run setup:dev -- --verify-only
git diff --check
```

Run the same-file process race repeatedly enough to reproduce the prior
intermittent path while keeping the ordinary suite fast and deterministic.

## Documentation and Evidence Update

Update SLI-0012 with the bounded correction and exact safety/non-rigidity
evidence. Resume WRK-0028/SLI-0001 closure after aggregate readiness passes.
No canonical product, domain, architecture, interface, or external behavior is
expected to change.

## Stop Conditions

- The fix requires cross-host consensus, broad/default locks, read locks,
  weakened contention assertions, live-owner preemption, or hidden retries.
- State compatibility or public command/result semantics must change.
- The defect requires a durable architecture decision or material CAP-0003
  reshaping rather than a local atomicity correction.
- Another active packet owns an overlapping path or exact evidence cannot be
  reproduced after bounded stress.

## Required Handoff

Report the captured loser outcome, root cause, correction, same-file stress
count, disjoint/read anti-rigidity evidence, focused and aggregate results,
contract/documentation impact, assumptions, residual risk, and the exact
SLI-0001 resumption action.

## Completion Evidence

- The captured loser was first `path.outside-repository` for an equivalent
  Windows `\\?\` path and then, under deeper stress, for an NTFS
  `C:\$Extend\$Deleted\...` path created when the winning process removed the
  short-lived lock between the loser's `exists()` and `resolve()` calls.
- `normalize_resolved_path` now collapses equivalent Windows device prefixes.
  `confined_path` revalidates the current exact pathname once only after a
  failed target containment check, allowing a vanished lock to resolve through
  its still-confined parent while continuing to refuse a stable symlink or
  junction escape. Lease retry, duration, ownership, and recovery policy did
  not change.
- Worker return code/stdout/stderr and result payloads are now retained in race
  assertion failures. A Windows-specific regression proves equivalent device
  prefixes share one resolved path.
- `python dev-tools/control-plane/test_file_leases.py` passed 12 scenarios.
  The same-file process race then passed 500 consecutive fresh-state runs;
  exactly one owner succeeded and the other returned `edit.lease-contended`.
- Full control-plane discovery passed 109 tests. Planning integrity passed for
  57 artifacts, documentation passed for 180 Markdown files, `git diff
  --check` reported no whitespace error, and aggregate readiness passed all 27
  checks including file-edit coordination.
- Existing disjoint-file concurrency, lease-free reads, alias collision,
  all-or-nothing multi-file acquisition, live-owner refusal, expiry recovery,
  scope confinement, and local payload-minimization assertions remain green.
  No public schema, CLI result shape, product behavior, external action, or
  durable decision changed.

## Planning History

- 2026-10-15: Authored as a bounded descendant correction after SLI-0001
  aggregate readiness reproduced the completed file-lease race defect on
  stress iteration 18 of 25.
- 2026-10-15: Deterministic packet validation and planning integrity passed;
  the packet is ready for a bounded claim without a lower-level approval.
- 2026-10-15: Corrected the Windows path-resolution race and passed focused,
  500-run stress, full control-plane, planning, documentation, diff, and
  aggregate readiness qualification.
