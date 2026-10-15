---
id: WRK-0023
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0012
capability: CAP-0003
depends_on: ["WRK-0020"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/financial_academy_editing.py", "dev-tools/control-plane/test_file_leases.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0012-coordinate-exclusive-file-edits.md", "docs/planning/work-packets/WRK-0023-enforce-active-authority-on-lease-renewal.md"]
generated_artifacts: []
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0023:9814e4cd-b7e2-41fc-8155-d8e17b7d2513
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:22:56Z
---

# Agent Work Packet: Enforce Active Authority on Lease Renewal

## Objective and Deliverable

Correct the completed file-edit coordination path so renewal revalidates the
lease's backing active WRK claim and declared paths, while owner-authorized
release remains available after work closes for prompt cleanup.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/testing context,
CAP-0003, SLI-0012, WRK-0020, the bounded completed-work correction route,
file-lease core and Financial AI Academy adapter, planning authority/scopes,
focused tests, concurrent-work rules, and the nearest README.

## Decisions and Assumptions

- Renewal extends exclusive ownership and therefore requires current active
  packet authority; ownership and claim equality alone are insufficient.
- Release reduces authority and contention, so the recorded owner/claim may
  release an expired or post-completion lease without reactivating work.
- The generic lease core remains project-neutral; repository authority belongs
  in the Financial AI Academy adapter.

## In Scope

Adapter-side renewal lookup and authority/scope revalidation, terminal-state-
independent regression coverage, planning/register reconciliation, and focused
plus aggregate verification.

## Out of Scope

Core lease-contract changes, new commands, read locks, broader scopes, live
preemption, cross-host behavior, agent startup, or changes to completed history.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Repository adapter | Lease/status and planning authority | `financial_academy_editing.py` | Revalidate active WRK before renewal |
| Regression | File coordination suite | `test_file_leases.py` | Prove post-completion renewal denial and release cleanup |
| Planning | Parent slice/new packet/register | Named artifacts | Record bounded descendant correction |

## Contracts and Interfaces

Existing `file-edit-lease-v1`, edit-status, `edit.work-claim-mismatch`, owner/
claim checks, and active WRK scope authority. No public schema changes.

## Dependencies and Parallel Safety

WRK-0020 is complete. The bounded correction uses its original adapter/test
scope and has no concurrent active packet.

## Acceptance Scenarios

- A live lease renews while its exact backing WRK claim remains active.
- After the packet projection becomes complete, renewal is refused by current
  work authority even when owner and claim still match.
- The same recorded owner/claim can release that lease after completion.
- Wrong owner/claim, expired lease, scope escape, and normal active paths retain
  their existing behavior.

## Verification Commands

- `python dev-tools/control-plane/test_file_leases.py`
- `python dev-tools/control-plane/test_portfolio_qualification.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py --profile local`
- `python dev-tools/agent/check_ready.py --profile ci`
- `git diff --check`

## Documentation and Evidence Update

Update SLI-0012 completion evidence with the bounded renewal-authority
correction. No public command or reusable-core documentation changes.

## Stop Conditions

Stop for generic-core repository coupling, release becoming blocked after work
completion, authority expansion, schema drift, external effects, unresolved
decision, or paths outside the correction route.

## Required Handoff

Report renewal/release semantics, focused and aggregate checks, documentation
impact, assumptions, residual risk, and continued CAP conformance.

## Planning History

- 2026-10-15: Authored as a bounded descendant correction after final audit
  found renewal did not revalidate active packet authority.
- 2026-10-15: Delivered adapter-side renewal revalidation and terminal-state-
  independent regression evidence; focused qualification, planning, and docs
  checks passed before completion.
