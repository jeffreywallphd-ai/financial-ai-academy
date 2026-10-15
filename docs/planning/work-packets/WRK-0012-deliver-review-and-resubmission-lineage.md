---
id: WRK-0012
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0005
capability: CAP-0002
depends_on: ["WRK-0011"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane", "dev-tools/planning/README.md", "docs/context/packs/delivery-planning.pack.md", "docs/context/packs/testing-quality.pack.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0005-record-review-findings-and-corrected-descendants.md", "docs/planning/work-packets/WRK-0012-deliver-review-and-resubmission-lineage.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: []
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0012:e7452417-7d6d-464a-8ed0-1db1e35f18d0
claimed_by: codex-control-plane
claimed_at: 2026-10-15T12:46:18Z
---

# Agent Work Packet: Deliver Review and Resubmission Lineage

## Objective and Deliverable

Add reusable append-only technical-review and corrected-descendant primitives,
the Financial AI Academy ignored-ledger adapter, CLI operations, documentation,
and focused independence, finding-closure, lineage, escalation, concurrency, and
anti-rigidity evidence.

## Required Context

Read applicable `AGENTS.md`, `docs/README.md`, CAP-0002, SLI-0005, predecessor
slice/packet contracts, planning/concurrent-work/testing guidance, the complete
local approval-store contract, affected control-plane code/tests, and nearest
READMEs before editing.

## Decisions and Assumptions

- Technical review evidence uses the ledger's `reviews` array, not approval
  records and never tracked files.
- Reviewer independence is deterministic label inequality against the active
  work owner; deployments needing stronger identity proof require a future
  separately decided adapter.
- Review acceptance is a technical disposition, not planning, release, merge,
  or external-action authority.
- Corrections must be clean strict descendants and receive fresh affected
  verification before the next review.

## In Scope

Review/finding/closure validation, ignored append-only store with locking,
receipt binding, independent reviewer enforcement, corrected-descendant state
transition, repeated-round escalation, CLI, docs, and tests.

## Out of Scope

Hosted review assignment, identity provider choice, tracked review summaries,
PR/push/merge/release actions, CI reporting, or another approval layer.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | State, ports, receipts, engine, CLI, tests | `dev-tools/control-plane/` | Add project-neutral review and resubmission behavior |
| Repository adapter | Approval-store reviewer contract | Control-plane adapter files | Append validated rounds only to ignored ledger |
| Guidance/planning | Named docs and artifacts | Exact `write_scope` | Synchronize review, privacy, and anti-rigidity semantics |

## Contracts and Interfaces

Stable `technical-review-round-v1`, finding, closure, open-finding, and
corrected-submission lineage objects; stable refusal codes; ledger append with
exclusive lock and atomic save; CLI review input restricted to ignored local
paths.

## Dependencies and Parallel Safety

WRK-0011 is complete. This packet is serial and extends its exact receipt and
the lifecycle state established by WRK-0010.

## Acceptance Scenarios

The SLI-0005 scenarios are normative. Tests also assert that no review data
appears in Git status, prior rounds remain byte-equivalent after later rounds,
one clean accepted round is sufficient, and a corrected round reuses closed
history rather than restarting unrelated checks.

## Verification Commands

- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/test_planning_tools.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update reusable extension guidance, local review-ledger behavior, planning and
testing rules, packet/slice evidence, and register. Never copy local reviewer
records or identifiers into tracked content.

## Stop Conditions

Stop for self-review, tracked review records, stale/non-qualifying evidence,
history rewrite, non-descendant correction, unresolved identity authority,
external publication, or material CAP drift.

## Required Handoff

Report contracts and commands, exact focused/aggregate results, independence,
finding, closure, lineage, adverse-round and anti-rigidity evidence, environment
limits, documentation impact, and the next slice action without reviewer data.

## Completion Evidence

- Added reusable review/finding/closure/open-finding and corrected-resubmission
  services, a locked append-only Financial AI Academy reviewer-ledger adapter,
  ignored-local review request parsing, and review status/record/resubmit CLI
  operations.
- `python dev-tools/control-plane/test_review.py` passed 6 tests covering the
  one-round clean path, self-review and duplicate-candidate denial, blocking
  findings, strict descendants, stale receipt rejection, explicit closure,
  immutable prior rounds, fresh-verification requirement, third-candidate
  root-cause escalation, append-only ledger behavior, and confinement of review
  requests to ignored local storage.
- The verification and lifecycle suites each passed 10 tests. Planning-tool
  behavior, public planning integrity for 20 artifacts, SLI/WRK validators,
  documentation validation for 140 Markdown files/context catalog, and all 10
  aggregate readiness checks passed.
- Review evidence is bound to an exact candidate and qualifying receipt.
  Corrected candidates preserve parent lineage and cannot be the same commit or
  a fork. Accepted dispositions cannot leave a blocking finding open.
- Tracked files contain behavior and test evidence only; no local reviewer
  label, disposition, date, candidate record, finding, closure, note, or review
  history was copied from the ignored ledger.
- The ordinary clean path needs one qualifying receipt and one independent
  technical disposition. It adds no planning approval, full-audit restart,
  remote service, publication, commit, push, merge, or product-state mutation.

## Planning History

- 2026-10-15: Authored just in time as the single SLI-0005 packet after SLI-0004
  and WRK-0011 completed.
