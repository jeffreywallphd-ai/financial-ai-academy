---
id: SLI-0005
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: CAP-0002
depends_on: ["SLI-0004"]
decision_gates: []
---

# Vertical Slice: Record Review Findings and Corrected Descendants

## Outcome and User Scenario

An independent technical reviewer can inspect one exact submitted and verified
candidate, append a consolidated finding/disposition round to the existing
ignored local ledger, and require a corrected strict descendant. Later rounds
preserve adverse history, explicit finding closure, verification lineage, and
root-cause escalation without reopening unrelated planning gates.

## Scope Boundaries

### In Scope

- Reusable finding, closure, disposition, open-finding, and resubmission-lineage
  contracts with deterministic validation.
- A Financial AI Academy review-ledger adapter that stores all reviewer labels,
  status, notes, findings, closures, candidate/evidence bindings, and history
  only in `.local-codex/approvals/ledger.json`.
- Reviewer independence from the current work owner.
- Accepted, changes-requested, and rejected technical dispositions; acceptance
  is refused while a blocking finding remains open.
- Corrected strict-descendant resubmission, fresh-verification requirement, and
  replay of unresolved findings.
- Root-cause evidence before a third candidate after two adverse rounds.
- Commands, machine results, concise remediation, and append-only concurrency
  tests.
- Anti-rigidity tests proving a clean accepted candidate needs one review round,
  remediation replays only open findings plus incremental risk, and review does
  not create a new planning approval stage or rerun unrelated checks.

### Out of Scope

- Storing reviewer records or identities in tracked artifacts, registers,
  fixtures, histories, or summaries.
- A human planning approval at review or slice completion.
- Reviewer authority to mutate delivery state without validated disposition.
- Hosted review assignment, pull-request publication, merge, or release action.
- CI retention and consolidated operator projections (SLI-0006).

## Canonical Context and Decisions

CAP-0002; SLI-0003 and SLI-0004 contracts; the local-only approval/reviewer
ledger rule; planning, concurrent-work, testing, and agent standards; and the
reusable control-plane ports govern this slice. No unresolved durable decision
applies because review remains local technical evidence and cannot authorize
external or product actions.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Append-only local review rounds and strict descendants | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Pull-request or hosted reviewer orchestration | no — external action and service are outside CAP | — | — | — | — | — | — | — | — |
| C. Tracked Markdown review reports | no — violates local-only reviewer-record authority | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the only eligible next manifest increment. It uses the exact
candidate and qualifying receipt from completed predecessors, keeps reviewer
records in the required local ledger, and exposes every safety and friction
property to deterministic tests.

## Contracts, Data, and Provenance

Each round binds the work ID, round ID, candidate, verification-receipt digest,
reviewer label, disposition, findings, closures, notes, optional root cause, and
recorded time. Findings have stable round-local IDs, severity, blocking status,
criterion/invariant, and evidence. Resubmission state binds parent and child
candidates and preserves earlier attempts. Reviewer data never enters tracked
planning files.

## Boundary Path

The current submitted state and qualifying receipt enter the reusable review
service; the repository adapter supplies owner identity and the ignored ledger;
the validator computes open findings and independence; the append-only store
records one round. An adverse latest round unlocks corrected-descendant
resubmission through the existing state/projection transaction, after which
SLI-0004 verification must run fresh before another review.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Clean independent acceptance | One bound round is appended; no lower-level approval or extra review artifact is created |
| Self review | Reviewer matching the current owner is refused with independence remediation |
| Blocking finding | Acceptance is refused and the finding remains open until a later explicit closure |
| Corrected descendant | A clean strict descendant is accepted as a new submission with parent lineage and requires fresh verification |
| Fork, same candidate, stale receipt | Resubmission or review is refused without mutating prior rounds |
| Closure replay | Later review names exact prior finding IDs and evidence; unrelated closed findings stay closed |
| Repeated adverse rounds | Third candidate requires root-cause evidence while preserving all prior attempts |
| Minimal path | A clean candidate completes one verification plus one independent review without a full audit restart or new planning gate |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0013 | Deliver append-only review rounds, open-finding closure, corrected-descendant lineage, commands, docs, and anti-rigidity tests | WRK-0012 | none | complete |
| WRK-0070 | Correct review proportionality so mechanically proven terminal-blank-line descendants receive fresh verification without redundant re-review | WRK-0013 | none | complete |
| WRK-0112 | Allow a strict corrected descendant after the latest exact-candidate verification fails or times out, without fabricating a review | WRK-0013, WRK-0070 | none | complete |
| WRK-0113 | Preserve failed-verification correction across an unrelated catalog revision only when the affected route remains semantically identical | WRK-0112 | none | ready |

## Verification and Qualification

Run focused review/store/resubmission tests, both existing control-plane suites,
planning tools/integrity, documentation validation, and aggregate readiness.
Use synthetic local reviewer labels and Git fixtures; never commit personal
identifiers or local ledger contents.

## Rollback and Migration

Review rounds are append-only local evidence. A tool rollback may read earlier
rounds but may not erase them or synthesize closure. New fields remain optional
for legacy review entries. Corrected candidates never replace ancestral
candidate or receipt identity.

## Stop Conditions

Stop for tracked reviewer data, self-review authority, erased findings, a
non-descendant correction, stale/non-qualifying receipt, remote service or
publication needs, or material CAP drift.

## Documentation Impact and Completion Evidence

Update reusable review/adaptation guidance, local-ledger semantics, planning and
testing guidance, artifacts, and register. Tracked completion evidence may
describe behaviors and check results but must not copy any reviewer label,
status, date, authority, finding ledger, or local review history.

Delivered evidence is recorded in WRK-0013. The slice supplies append-only local
technical review rounds, deterministic independence checks, binding to exact
candidate receipts, blocking/open-finding enforcement, explicit closure,
strict-descendant lineage, fresh verification between rounds, and repeated-round
root-cause escalation. Focused review, verification, and lifecycle suites plus
planning, documentation, artifact, and aggregate readiness checks passed. No
hosted review, identity-provider proof, publication, or external action was
performed; stronger reviewer authentication remains a future adapter decision.

WRK-0112 closes the remaining failed-verification correction dead end. A clean
strict descendant is now permitted only when the latest exact-candidate receipt
is structurally complete and fails solely because a selected check failed or
timed out. Receipt-chain integrity, current submission binding, locked-state
authorization, descendant identity, fresh verification, and the ordinary
technical-review path remain intact. Focused review, verification, and lifecycle
suites, planning and documentation integrity, aggregate readiness, whitespace,
and exact affected verification passed. The change adds no approval stage,
external action, migration, or stored personal data.

## Planning History

- 2026-10-15: Refined just in time after SLI-0004 completed; Candidate A scored
  14/14 and remains within CAP-0002's review-lineage slice boundary.
- 2026-10-16: Added bounded descendant WRK-0070 through the completed-work
  correction route. It preserves substantive review controls while removing a
  redundant review loop for verified cleanup-only descendants.
- 2026-10-16: Reopened through a bounded WRK-0013 correction after a real
  non-qualifying first verification exposed a lifecycle dead end. WRK-0112
  permits only a strict descendant backed by the latest structurally valid
  exact-candidate failed-execution receipt; fresh verification and ordinary
  independent review remain required.
- 2026-10-16: WRK-0112 completed the bounded correction and SLI-0005 returned
  to complete without changing CAP-0002 scope or adding a lower-level gate.
- 2026-10-16: Reopened through WRK-0112's bounded correction route after an
  unrelated global catalog revision blocked a product packet whose selected
  checks and commands were unchanged. WRK-0113 adds exact route-equivalence
  proof rather than weakening stale-evidence protection.
