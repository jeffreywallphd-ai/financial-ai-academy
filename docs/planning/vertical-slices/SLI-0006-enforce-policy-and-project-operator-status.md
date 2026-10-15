---
id: SLI-0006
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: CAP-0002
depends_on: ["SLI-0003", "SLI-0004", "SLI-0005"]
decision_gates: []
---

# Vertical Slice: Enforce Policy and Project Operator Status

## Outcome and User Scenario

Local operators and read-only CI evaluate the same versioned control-plane rule
set, emit privacy-minimized machine reports, and retain CI evidence. A single
operator command projects every packet's public state, lease, submission,
verification, review blockers, and next legal action without requiring manual
ledger or JSON inspection.

## Scope Boundaries

### In Scope

- A reusable deterministic policy evaluator with stable rule IDs, dispositions,
  evidence digests, severity, and remediation.
- Identical rule inventory and semantics in local and CI profiles; unavailable
  ignored-local evidence is explicitly `not-evaluated`, never silently passed.
- Atomic privacy-minimized JSON reports and consistent exit codes.
- A derived operator projection over tracked planning artifacts and available
  ignored state, receipts, and reviews, without becoming a new source of truth.
- Reconciliation in the projection when legacy public terminal state is newer
  than optional local controller state.
- Integration of all focused control-plane suites into the fixed readiness
  allowlist and read-only CI, with always-retained machine reports.
- Tests for local/CI parity, report retention contract, malformed/stale state,
  next actions, no local-reviewer disclosure, and supported Windows commands.
- Anti-rigidity tests proving status is read-only/one command, unavailable local
  evidence does not block public CI, and failures name one narrow next action
  instead of demanding every check or another approval.

### Out of Scope

- Hosted scheduling, a remote control service, CI as lifecycle source of truth,
  branch-protection configuration mutation, push, merge, release, or deployment.
- A graphical dashboard or product UI.
- Packet-start acceptance closure and maintenance/correction routes (SLI-0007).
- Telemetry, multi-turn harness evaluation, and capability confinement
  qualification (SLI-0008).

## Canonical Context and Decisions

CAP-0002, SLI-0003 through SLI-0005 contracts, agent-readiness and CI workflow
authority, planning/testing standards, local-only ledger rules, and the reusable
control-plane interfaces govern the slice. No external or cloud authority is
introduced.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Shared policy/report core plus derived operator projection | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. CI-only policy source of truth | no — violates local/CI parity and CAP boundary | — | — | — | — | — | — | — | — |
| C. Hosted dashboard/controller | no — hosted control is outside CAP | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the next manifest slice, consumes all stable predecessor
projections, is directly testable locally and in workflow contract fixtures, and
keeps reports/projections derived and reversible.

## Contracts, Data, and Provenance

`control-policy-report-v1` records tool/schema version, profile, repository
revision when available, stable rule results, evidence digests/counts, start/end
times, and overall disposition without raw command output, reviewer labels,
notes, findings, prompts, secrets, or source payloads. `operator-status-v1`
derives work IDs, public/operational states, anonymous counts, blocker IDs, and
next actions. CI retains reports as workflow artifacts but never mutates
lifecycle state.

## Boundary Path

Tracked artifacts and available ignored evidence enter project-neutral rule and
projection services; the Financial AI Academy adapter maps planning/receipt/
review contracts; the same command writes a report locally and in CI; the
readiness runner invokes focused control tests; the workflow uploads the report
even on failure.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Local/CI parity | Both profiles expose identical rule IDs and dispositions for identical available facts |
| CI lacks ignored evidence | Local-only rules are `not-evaluated` with reason; public rules still decide CI success |
| Operator happy path | One command identifies the next legal action for ready, active, submitted, reviewed, and complete work |
| Stale optional local state | A newer tracked terminal projection is shown truthfully and the stale local fact is diagnosed, not promoted as source of truth |
| Failed policy | Report is retained, exit is nonzero, and the failed rule includes one bounded remediation |
| Privacy | Machine reports and operator output contain no reviewer labels, notes, raw findings, command output, prompts, or local absolute paths |
| CI retention | Workflow contract runs the same policy/readiness path and uploads the machine report with read-only permissions |
| Minimal status | Read-only status performs no check suite, mutation, or approval request |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0013 | Deliver shared policy reports, operator projection, readiness/CI integration, retained artifacts, docs, and anti-rigidity tests | WRK-0012 | none | ready |

## Verification and Qualification

Run policy/operator tests, all prior control-plane suites, readiness-runner and
CI-workflow tests, planning tools/integrity, documentation validation, and the
aggregate readiness command in local and CI profiles where executable.

## Rollback and Migration

Reports and projections are derived. Removing the new command does not change
canonical lifecycle state. Workflow artifact retention can be rolled back
without deleting historical local evidence. Legacy readiness output remains
human-readable while the new report path is additive.

## Stop Conditions

Stop for CI lifecycle mutation, raw sensitive output retention, reviewer-data
disclosure, different local/CI rule semantics, a hosted dependency, or material
CAP drift.

## Documentation Impact and Completion Evidence

The reusable control-plane and planning references now distinguish the generic
policy/status cores from Financial AI Academy adapters. Agent guidance documents
sanitized report retention; testing context and standards document profile
parity, explicit unavailable evidence, and read-only status. The assurance gap
retains hosted artifact availability and branch protection as external
qualifications.

Focused results on 2026-10-15: policy/status 8 passed, review 6 passed,
verification 10 passed, lifecycle 10 passed, CI workflow contract passed,
planning integrity passed for 22 artifacts, documentation validation passed for
142 Markdown files, local readiness passed 15 checks, and CI-profile readiness
passed 14 checks. Generated JSON reports were written under the ignored
`artifacts/control-plane/` boundary and inspected through privacy assertions.

## Planning History

- 2026-10-15: Refined just in time after SLI-0005 completed; Candidate A scored
  14/14 and remains inside CAP-0002's local/CI reporting boundary.
- 2026-10-15: Deterministic completion structure and exact focused/local/CI
  verification passed; the slice closed without a lower-level approval gate.
