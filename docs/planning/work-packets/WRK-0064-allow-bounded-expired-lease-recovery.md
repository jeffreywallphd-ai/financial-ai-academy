---
id: WRK-0064
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0003-correction
updated: 2026-10-16
parent: SLI-0012
capability: CAP-0003
depends_on: ["WRK-0029"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/file_leases.py", "dev-tools/control-plane/financial_academy_editing.py", "dev-tools/control-plane/test_file_leases.py", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0012-coordinate-exclusive-file-edits.md", "docs/planning/work-packets/WRK-0064-allow-bounded-expired-lease-recovery.md"]
generated_artifacts: []
base_revision: b72f1834f5754914bc554db0a70b51873e45bafa
claim_id: WRK-0064:f3b07f25-cde3-4b83-b8a6-98dac37bb27a
claimed_by: codex-cap-0003-correction
claimed_at: 2026-10-16T00:23:40Z
---

# Agent Work Packet: Allow Bounded Expired-Lease Recovery

## Objective and Deliverable

Correct exact-file coordination so a successor packet can explicitly recover
only the requested, in-scope paths from an expired multi-file lease. Preserve
the unrecovered paths as expired ownership, retain recovery lineage, and keep
live-owner exclusion, atomic acquisition, and packet-scope authorization
unchanged. This removes a control-plane deadlock that otherwise requires a
successor to expand its scope to unrelated historical files.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`, then apply its context routing, impact, and
decision-readiness instructions. Read CAP-0003, SLI-0012, WRK-0020, WRK-0023,
WRK-0029, the completed-work correction route, concurrent-work rules, the
project-neutral lease core, the Financial AI Academy authorization adapter,
focused lease tests, and the nearest control-plane documentation.

## Decisions and Assumptions

- This is a bounded defect in completed CAP-0003 behavior reproduced while
  starting CAP-0005 work. It does not change CAP-0003's single-live-writer
  invariant, local-only boundary, command surface, or project authorization.
- Recovery authority is path-scoped. A successor must name every exact path it
  takes, and every requested path must remain inside its active WRK scope, but
  it must not acquire unrelated paths merely because a prior lease grouped
  them in one operation.
- A partial recovery removes only the requested path keys from the expired
  lease. The residual expired lease remains visible and independently
  recoverable under the original lease ID; the new lease records that ID in
  `recovered_from`.
- Recovery remains explicit and atomic. It never displaces a live owner,
  silently turns into ordinary acquisition, or grants a directory/repository
  lock.

## In Scope

- Split expired lease ownership by exact requested path during an explicit
  recovery transaction while preserving residual expired ownership and
  lineage.
- Retain full-set recovery behavior when every path is requested.
- Add deterministic regression coverage for subset recovery, residual
  recovery, multi-lease recovery, live-owner refusal, scope confinement,
  all-or-nothing acquisition, and unrelated-file concurrency.
- Align concurrent-work guidance, SLI-0012 evidence, and the planning register
  with the corrected bounded-recovery semantics.

## Out of Scope

- Live-owner preemption, implicit expiry cleanup, recovery outside an active
  packet's declared scope, cross-host consensus, read locks, directory or
  repository locks, remote state, new commands, schema-version migration, or
  product behavior.
- Reopening or rewriting completed WRK history, altering the CAP-level approval
  model, bypassing the repository adapter, editing ignored state by hand, or
  broadening CAP-0005 feature scope.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generic lease core | expired ownership lookup, recovery transaction, events, status | `file_leases.py` | Transfer only requested expired path keys and retain residual ownership |
| Repository adapter | active packet scope authorization around recovery | `financial_academy_editing.py` only if required | Preserve project-specific authorization without core coupling |
| Regression | expiry, recovery, contention, scope, and anti-rigidity tests | `test_file_leases.py` | Prove subset recovery removes the deadlock without weakening exclusion |
| Operator guidance | exact-file recovery rules | `concurrent-work.md` | Replace obsolete complete-historical-set requirement |
| Planning | parent slice, packet, register | named artifacts | Preserve bounded correction lifecycle and evidence |

## Contracts and Interfaces

Preserve `file-edit-state-v1`, `file-edit-lease-v1`, `file-edit-intent-v1`,
existing commands, response codes, and ignored local storage. On recovery, the
new lease's `recovered_from` remains the sorted set of expired lease IDs that
owned requested paths. For each such prior lease, requested paths are removed
from its `paths` and private `keys`; the lease is deleted only when no paths
remain. Every residual key continues to map to that prior lease in
`path_owners`. The recovery event continues to record the new lease and prior
IDs without source contents, approvals, credentials, or personal data.

## Dependencies and Parallel Safety

WRK-0029 is complete. The controller routed the reproduced defect from
WRK-0020 to one bounded descendant correction covering the lease core, adapter,
and focused tests. WRK-0063 was safely released before feature implementation
and will be reclaimed only after this correction qualifies. This packet is
serial because it changes reusable coordination behavior and its canonical
guidance.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Bounded subset recovery | An expired lease owns `a` and `b`, while the successor WRK is authorized only for `a` | The successor explicitly recovers `a` | A live successor lease owns only `a`; the expired original still owns only `b`; lineage names the original lease | Core and adapter anti-rigidity tests |
| Residual recovery | The original lease retains expired `b` after `a` was recovered | An authorized later packet recovers `b` | Recovery succeeds once, removes the residual lease, and retains the same lineage ID | Core test |
| Full-set compatibility | An expired lease owns exactly the requested set | Recovery runs | Existing full-set behavior and result shape remain valid | Core regression |
| Multiple expired owners | Requested paths are split across expired leases | One authorized atomic recovery runs | The new lease names all prior IDs and no unrelated residual path moves | Core transaction test |
| Live owner protection | Any requested path has an unexpired lease | Recovery runs | The whole operation is refused as `edit.lease-contended`; no ownership changes | Core regression |
| Scope confinement | A successor requests a path outside its active WRK scope | Adapter authorization runs | Recovery is refused before lease state changes | Adapter regression |
| Unrelated progress | Other expired or live leases own files not requested | A bounded recovery runs | Those files and status/read concurrency are unchanged | Anti-rigidity regression |

## Verification Commands

```powershell
python dev-tools/control-plane/test_file_leases.py
python dev-tools/control-plane/test_qualification.py
python dev-tools/control-plane/test_portfolio_qualification.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python .agents/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0064-allow-bounded-expired-lease-recovery.md
python dev-tools/agent/check_ready.py
git diff --check
```

After qualification, use the corrected command against the actual expired
WRK-0062 lease overlap before reclaiming WRK-0063. Do not modify ignored lease
state manually.

## Documentation and Evidence Update

Update concurrent-work rules and SLI-0012 with the corrected path-level
recovery contract, exact regression coverage, focused and aggregate results,
independent technical review, assumptions, and residual risk. Keep all
approval and reviewer records in ignored local control state only.

## Stop Conditions

Stop if the correction requires live-owner preemption, scope expansion,
implicit recovery, broad/default locks, read locks, remote consensus, a public
schema-version change, destructive ignored-state maintenance, history rewrite,
an unresolved durable decision, or paths outside the accepted correction
route.

## Required Handoff

Report the reproduced deadlock, root cause, exact ownership transition,
lineage and residual-lease behavior, focused/full control-plane and aggregate
results, independent review outcome, anti-rigidity evidence, documentation
impact, assumptions, residual risk, and the exact WRK-0063 resumption action.

## Planning History

- 2026-10-16: Authored from the bounded completed-work correction route after
  WRK-0063 could not recover its in-scope files from an expired grouped
  WRK-0062 lease without also requesting unrelated files outside its scope.
  The packet preserves exact-file exclusion and replaces only the rigid
  complete-historical-set recovery requirement.
