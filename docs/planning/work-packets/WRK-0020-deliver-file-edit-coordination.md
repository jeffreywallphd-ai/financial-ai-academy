---
id: WRK-0020
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0012
capability: CAP-0003
depends_on: ["WRK-0019"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/file_leases.py", "dev-tools/control-plane/financial_academy_editing.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_file_leases.py", "dev-tools/control-plane/test_portfolio_ordering.py", "dev-tools/control-plane/README.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0012-coordinate-exclusive-file-edits.md", "docs/planning/work-packets/WRK-0020-deliver-file-edit-coordination.md"]
generated_artifacts: [".local-codex/control-plane/file-leases.json"]
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0020:88cae2d9-e084-4ad4-8606-94fa4768da1d
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:07:09Z
---

# Agent Work Packet: Deliver File-Edit Coordination

## Objective and Deliverable

Deliver a reusable exact-file communication/lease core, Financial AI Academy
ancestry/claim/scope adapter, commands/status, documentation, and focused
single-writer plus anti-rigidity tests.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/testing context,
CAP-0003, SLI-0011/0012, WRK-0019, concurrent-work rules, existing state/lease/
path confinement code, packet claim metadata, CLI, tests, and nearest README.

## Decisions and Assumptions

- Logical CAP/SLI coordination is always backed by one active descendant WRK
  claim for write authority; a lease never broadens that claim.
- Intent is visible but non-blocking; only a live exact-file lease excludes a
  second editor.
- One short transaction lock protects state transitions, not edit duration.
- Recovery is explicit after expiry and never displaces a live owner.

## In Scope

Versioned state/contracts, canonical paths, atomic intent/acquire/renew/release/
recover/status, ignored persistence/events, repository authorization adapter,
CLI/docs, and race/denial/privacy/anti-rigidity tests.

## Out of Scope

Read locks, directories, repo mutexes, cross-host consensus, chat, editor hooks,
automatic edits, agent/claim creation, Git mutation, or remote effects.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | Store/state/contracts | `file_leases.py`, tests | Add exact-file local coordination kernel |
| Repository adapter | Planning artifacts/claims/scopes | `financial_academy_editing.py` | Prove ancestry and bounded write authority |
| CLI/docs | Parser/dispatch/guidance | Named files | Expose safe coordination workflow |
| Planning | SLI/WRK/register | Named artifacts | Synchronize lifecycle/evidence |

## Contracts and Interfaces

Versioned state/intent/lease/event contracts; exact normalized file keys;
lease ID, unit/work/claim references; expected revision; stable refusal codes;
existing `ControlError`, atomic write, confined path, and short lock primitives.

## Dependencies and Parallel Safety

WRK-0019 is complete. This packet changes shared CLI/concurrency guidance and
is serial in the current branch. Its delivered lease plane enables later
parallel agents.

## Acceptance Scenarios

The SLI-0012 table is normative. Tests also cover malformed state, duplicate
paths, zero/excessive duration, wrong owner/claim, stale revision, idempotent
status, intent expiry, release cleanup, recovery lineage, and event ordering.

## Verification Commands

- `python dev-tools/control-plane/test_file_leases.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git check-ignore -v .local-codex/control-plane/file-leases.json`
- `git diff --check`

## Documentation and Evidence Update

Document commands, single-writer invariant, intent versus ownership, path
identity, expiry/recovery, local storage, and anti-rigidity rules.

## Stop Conditions

Stop for broad/read locks, non-atomic acquisition, live preemption, authority or
scope expansion, remote state, sensitive payloads, unresolved decision, or
scope outside this packet.

## Required Handoff

Report state/contracts, path/transaction behavior, adapter authority, commands,
tests, docs, environment limits, residual risk, and CAP conformance.

## Planning History

- 2026-10-15: Authored just in time for conforming SLI-0012 delivery.
- 2026-10-15: Added the ordering regression test to scope after it exposed a
  hard-coded prior active-slice expectation; no contract or CAP scope changed.
- 2026-10-15: Delivered generic state/lease contracts, repository authorization,
  CLI/docs, and 11 focused race, denial, recovery, privacy, and anti-rigidity
  tests; all packet verification commands passed.
