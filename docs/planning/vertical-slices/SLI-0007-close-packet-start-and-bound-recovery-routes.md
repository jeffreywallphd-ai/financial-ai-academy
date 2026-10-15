---
id: SLI-0007
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: CAP-0002
depends_on: ["SLI-0006"]
decision_gates: []
---

# Vertical Slice: Close Packet Start and Bound Recovery Routes

## Outcome and User Scenario

At packet start, one command freezes a claim-bound acceptance manifest and the
smallest risk-selected delivery route. Ordinary work receives no new approval,
full-suite, or recovery ceremony. A completed-work defect receives a bounded
corrective-packet route, while a defect in the controller itself can enter,
execute, and exit an allowlisted maintenance session with preserved evidence.

## Scope Boundaries

### In Scope

- A reusable packet-start service that binds the claim, canonical planning
  inputs, acceptance identifiers, risk tier, required evidence, and manifest
  digest in ignored append-only state.
- Idempotent replay for the same claim and deterministic refusal when tracked
  planning inputs drift after start.
- Risk routes whose ordinary path uses affected checks and one independent
  review; aggregate readiness is added only for explicit shared/control impact.
- A completed-work correction router that confines changed paths to the
  completed packet scope and directs a bounded descendant WRK under the same
  slice without another approval.
- A reusable maintenance-session core with allowlisted action IDs, one active
  session, mutation blocking, append-only events, success-required exit, and no
  arbitrary shell, approval, review, Git, or tracked-planning mutation.
- Financial AI Academy acceptance/risk/correction and maintenance-action
  adapters, CLI surfaces, operator diagnostics, documentation, and tests.
- Anti-rigidity tests for the shortest low-risk route, idempotent start, no
  speculative recovery artifacts, one-command correction routing, bounded
  maintenance, and exact narrow remediation.

### Out of Scope

- Silent reopening or rewriting of completed planning artifacts; automatic
  generation or implementation of a corrective packet; arbitrary state edits;
  deletion of evidence; bypass of authority, verification, review, or scope.
- Remote repair, hosted operators, arbitrary command execution, commit, push,
  merge, release, deploy, credentials, or production mutation.
- Telemetry, evaluation corpus, provenance envelopes, and capability tokens,
  which are delivered by SLI-0008.

## Canonical Context and Decisions

CAP-0002; SLI-0003 through SLI-0006 contracts; planning/concurrency/testing
standards; ignored-state and local-only reviewer rules; and the reusable
control-plane boundary govern this slice. No durable decision gate is open.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Start manifest, corrective router, and allowlisted maintenance session | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add approval gates for each start/correction/repair | no — violates CAP-only authority and short path | — | — | — | — | — | — | — | — |
| C. General shell-based repair mode | no — unbounded bypass violates CAP | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A closes the explicit CAP contracts while keeping policy decisions in
adapters and reusable orchestration in dependency-free cores. Its local records
are derived/recoverable and its public corrective route remains governed by the
existing just-in-time WRK process.

## Contracts, Data, and Provenance

`packet-start-manifest-v1` contains stable IDs, digests, counts, risk, and
required evidence, not approval/reviewer data or source text. `correction-route-v1`
binds a completed WRK, path set, original scope digest, and route steps.
`maintenance-session-v1` records a defect code, allowed action IDs, status, and
append-only action outcomes under ignored state. It never carries shell text.

## Boundary Path

The project adapter extracts tracked acceptance and scope facts; reusable start
and correction services validate and persist confined manifests; maintenance
accepts only registered action handlers, blocks normal mutating CLI operations
while active, preserves each event, and exits only after a successful action and
health validation.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Low-risk packet start | One command freezes the manifest and requires affected verification plus one review, with no full readiness or approval |
| Shared/control impact | The same rules add aggregate readiness with an explicit risk reason |
| Replay | Repeating start for the same unchanged claim returns the existing manifest without another record |
| Planning drift | Changed acceptance or scope after start is refused with one re-plan remediation |
| Completed correction | In-scope paths return a bounded corrective-WRK route under the same slice and preserve completed history |
| Correction escape | An out-of-scope path is refused as CAP/scope review rather than silently broadened |
| Maintenance | One allowlisted session blocks normal mutations, records actions, validates health, and exits without editing tracked planning metadata |
| Anti-bypass | Unknown actions, concurrent sessions, exit without success, arbitrary commands, and approval/review mutation are impossible |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0014 | Deliver packet-start closure, correction routing, bounded maintenance, adapters, CLI, docs, and anti-rigidity tests | WRK-0013 | none | ready |

## Verification and Qualification

Run operations tests, every prior control-plane suite, workflow/readiness,
planning, documentation, and deterministic completion gates. Tests must inspect
history preservation and prove the low-risk route excludes unrelated controls.

## Rollback and Migration

Start, correction, and maintenance records are ignored derived/audit evidence.
Removing their CLI routes does not reinterpret public planning or approval
records. Existing packets without start manifests remain readable and receive a
manifest only when explicitly started.

## Stop Conditions

Stop for a new approval, arbitrary command/path repair, erased evidence,
completed-history rewrite, unbounded scope expansion, external action, or any
material CAP change.

## Documentation Impact and Completion Evidence

Control-plane and planning references now describe semantic packet-start
closure, short risk routes, completed-work correction without history reopening,
and allowlisted maintenance. Concurrency, delivery/testing context, and testing
standards distinguish semantic drift from harmless prose churn and require
anti-bypass evidence. The fixed readiness allowlist includes operations tests.

Focused results on 2026-10-15: operations 8 passed, policy/status 8 passed,
review 6 passed, verification 10 passed, lifecycle 10 passed, planning integrity
passed for 24 artifacts, documentation validation passed for 144 Markdown files,
local readiness passed 16 checks, and CI-profile readiness passed 15 checks. A
real high-risk packet start, confined completed-work correction route, and
validate-only maintenance entry/action/health/exit cycle also succeeded.

## Planning History

- 2026-10-15: Refined just in time after SLI-0006 completion; Candidate A
  scored 14/14 and preserves the approved short-path and anti-bypass boundaries.
- 2026-10-15: Deterministic completion structure and exact focused/local/CI
  evidence passed; the slice closed without a lower-level approval.
