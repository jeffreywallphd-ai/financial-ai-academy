---
id: SLI-0004
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: CAP-0002
depends_on: ["SLI-0003"]
decision_gates: []
---

# Vertical Slice: Select Affected Checks and Record Verification Receipts

## Outcome and User Scenario

Given an exact submitted WRK candidate, an operator receives one deterministic,
risk-explained affected-check plan, runs only those allowlisted checks by
default, and obtains an append-only receipt bound to the candidate, selected
commands, declared inputs, environment, outputs, timing, and dispositions.
Stale, mismatched, partial, or failed evidence never qualifies the candidate.

## Scope Boundaries

### In Scope

- A tracked, versioned check catalog and deterministic path/risk selector.
- Stable plan and receipt schemas with canonical digests and append-only local
  storage under ignored control-plane state.
- An allowlisted executor that records each attempt, including failures and
  output digests, without interpreting repository output as instructions.
- Exact candidate, submission, selected-check, input, environment, and freshness
  validation before a receipt is accepted.
- JSON and concise operator output with invariant-specific remediation.
- Tests for narrow documentation, planning-tool, control-plane, interface, and
  shared-foundation changes plus stale/replay/failure/partial evidence.
- Anti-rigidity assertions that narrow changes do not select the full suite,
  repeated checks require a concrete invalidation, and risk escalation includes
  its triggering reason.

### Out of Scope

- Independent reviewer findings and resubmission lineage (SLI-0005).
- CI retention/parity and consolidated operator status (SLI-0006).
- Cross-project automatic discovery of arbitrary test runners, remote caches,
  signing services, or execution of commands absent from the tracked catalog.
- Treating a receipt as approval, criterion judgment, or authorization.

## Canonical Context and Decisions

CAP-0002, SLI-0003, the planning and concurrent-work guides, testing standards,
the agent-readiness allowlist, current CI workflow, and the reusable
`dev-tools/control-plane/` contracts govern this slice. No unresolved durable
decision applies because execution stays local, repository-owned, allowlisted,
and free of credentials or external effects.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Path/risk selector plus fresh receipt executor | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. General build-system or remote result cache | no — outside CAP and input-closure authority | — | — | — | — | — | — | — | — |
| C. Full-suite-only verifier | no — violates risk-proportional CAP constraint | — | — | — | — | — | — | — | — |

Candidate A is the exact next manifest increment and consumes SLI-0003's stable
submission envelope without redefining it.

## Selection Rationale

Candidate A scores 14/14 because it delivers the full local operator outcome,
uses resolved repository-owned contracts, depends only on completed SLI-0003,
has directly observable success and denial evidence, and remains reversible
additive local tooling. Candidates B and C fail eligibility before scoring.

## Contracts, Data, and Provenance

The reusable core gains check definitions, deterministic selection, environment
and input fingerprinting, execution results, receipt validation, and an
append-only receipt port. The Financial AI Academy adapter supplies its tracked
catalog and path/risk rules. A plan records candidate, changed paths, catalog
digest, selected command IDs, reasons, risk tier, and deferred profiles. A
receipt records that plan plus exact inputs/environment, attempts, exit codes,
durations, stdout/stderr digests, freshness, producer, and prior receipt digest.

## Boundary Path

The submitted-candidate envelope enters the reusable selector, the repository
adapter maps changed paths to catalog command IDs and risk, the executor runs
only those IDs, the receipt store appends observed results, and the validator
returns one qualifying or actionable non-qualifying disposition to the CLI.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Narrow docs change | Documentation/planning checks are selected; unrelated product/full suites are deferred with reason |
| Control-plane change | Focused control-plane and planning checks are selected; aggregate readiness is selected only when shared support inputs require it |
| Shared foundation change | Full readiness is selected with the matching shared-impact reason |
| Determinism | Identical candidate, paths, catalog, and inputs yield the same plan digest |
| Fresh verification | All selected checks run and an append-only exact-candidate receipt is accepted |
| Failure or partial run | Failure attempts remain recorded and the receipt is non-qualifying with a rerun remediation |
| Stale or mismatched data | Candidate, plan, catalog, input, or environment mismatch is rejected without replay acceptance |
| Minimal path | A low-risk candidate runs only its selected narrow checks with no new approval or full-suite prerequisite |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0011 | Deliver deterministic affected-check selection, exact verification receipts, adapters, commands, docs, and anti-rigidity tests | WRK-0010 | none | ready |

## Verification and Qualification

- Focused selector, fingerprint, executor, receipt-chain, replay, failure, and
  anti-rigidity unit/integration tests.
- Existing control-plane and planning-tool suites.
- Planning, documentation, skill, and aggregate readiness gates.
- Real allowlisted subprocess execution on Windows; other hosts remain an
  explicit environment qualification gap.

## Rollback and Migration

Receipts are additive local evidence. A failed run remains append-only and does
not advance acceptance. A catalog change creates a new digest and invalidates
reuse; it never rewrites prior receipts. The SLI-0003 lifecycle remains usable
if verification commands are rolled back, but submitted work cannot qualify
without a fresh valid receipt.

## Stop Conditions

Stop for arbitrary untracked command execution, external cache/service or
credential requirements, optimistic evidence reuse with unknown inputs,
mandatory full-suite selection without a shared-impact reason, or material CAP
drift.

## Documentation Impact and Completion Evidence

Update the reusable control-plane reference, testing and planning guidance,
SLI/WRK artifacts, and register. Completion evidence must name selected versus
deferred checks, exact focused commands/results, failure and anti-rigidity
coverage, environment limits, and CAP conformance without copying local approval
or reviewer records into tracked files.

Delivered evidence is recorded in WRK-0011. The slice provides deterministic
path/risk selection, a tracked allowlisted catalog, exact-candidate stability
checks before and after execution, privacy-minimized attempts, append-only
receipt chaining, freshness validation, and explicit non-qualification for
failure, timeout, drift, partial coverage, stale inputs, or digest mismatch.
The focused verification and lifecycle suites, planning behavior/integrity,
artifact validators, documentation validation, and aggregate readiness all
passed. Cross-host execution and result reuse remain unqualified; reuse is
therefore disabled rather than inferred.

## Planning History

- 2026-10-15: Refined just in time after SLI-0003 completed; Candidate A scored
  14/14 and remains within the approved CAP-0002 manifest and risk posture.
