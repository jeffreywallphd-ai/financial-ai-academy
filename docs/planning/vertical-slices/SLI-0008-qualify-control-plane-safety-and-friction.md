---
id: SLI-0008
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: CAP-0002
depends_on: ["SLI-0007"]
decision_gates: []
---

# Vertical Slice: Qualify Control-Plane Safety and Friction

## Outcome and User Scenario

An operator can run a deterministic multi-turn harness corpus and inspect
privacy-minimized friction/safety metrics before promoting a control-plane
change. Every executable command and repository path effect is checked against
an explicit capability grant, and machine outputs carry reusable provenance.
Metrics inform maintenance; they do not grant authority or block ordinary work
outside explicit regression thresholds in the committed evaluation corpus.

## Scope Boundaries

### In Scope

- Reusable capability grants with exact command IDs, normalized path scopes,
  effect classes, deterministic digests, stable denials, and no arbitrary argv.
- Confinement of affected-check execution plus reusable APIs for future adapters;
  existing candidate, report, review-request, and maintenance confinement stays
  intact and is covered by cross-boundary tests.
- A reusable provenance envelope attached to CLI results and verification
  receipts, binding producer/version, command or operation ID, revision/input,
  capability digest where applicable, and output digest without raw payloads.
- Append-only privacy-minimized command telemetry with event IDs, command IDs,
  result codes, outcome, duration, remediation count, and no prompts, arguments,
  paths, work IDs, people, review data, source, or command output.
- Deterministic aggregate metrics for refusal quality, replay/redundancy,
  recovery success, verification duration, maintenance failure, and command
  count, with locally configurable observation windows but committed regression
  thresholds only in the evaluation corpus.
- A tracked multi-turn scenario corpus and evaluator covering happy path,
  interruption/recovery, verification failure, review correction, correction
  routing, maintenance, confinement denial, and minimal-friction budgets.
- Readiness integration, reusable/project adapter documentation, assurance
  updates, final CAP evidence, and anti-rigidity/privacy/confinement tests.

### Out of Scope

- Collection of prompts, model text, source payloads, command argv/output,
  personal data, approval/reviewer records, credentials, or production facts.
- Remote telemetry, hosted enforcement, network upload, dashboards, model-based
  graders, autonomous optimization, or metrics that waive safety invariants.
- New product security boundaries, remote workers, commit/push/merge/release,
  deployment, or external/destructive authority.

## Canonical Context and Decisions

CAP-0002 and every predecessor slice; AI-agent, testing, planning, security, and
documentation standards; local-only authority/review rules; and the fixed
readiness workflow govern. No durable decision is required for local anonymous
events and deterministic repository fixtures.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Capability grants, provenance, local metrics, and deterministic scenario corpus | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Remote observability/enforcement service | no — outside local CAP and unresolved provider boundary | — | — | — | — | — | — | — | — |
| C. Model-graded free-form transcripts | no — nondeterministic authority and privacy risk | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A qualifies all delivered behavior with portable, dependency-free
contracts while preserving local control and deterministic safety constraints.
It measures friction without converting optimization into authority.

## Contracts, Data, and Provenance

`capability-grant-v1` contains effect, command IDs, normalized scope, subject,
expiry when supplied, and digest. `control-provenance-v1` contains producer,
operation, revision/input/capability/output digests, and time. `control-event-v1`
contains only categorical IDs, duration, count, and outcome.
`harness-evaluation-report-v1` contains scenario/assertion results and aggregate
threshold status; fixtures contain no prompts or source payloads.

## Boundary Path

Tracked catalog/scenarios enter pure confinement and evaluation cores; project
adapters issue bounded grants; execution refuses command/path mismatch before
subprocess start; CLI outputs receive provenance; a best-effort local sink emits
minimal events; reports aggregate or evaluate without mutating lifecycle state;
readiness executes the deterministic corpus.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Allowed affected check | Exact catalog command ID and matched paths execute under one digest-bound grant and receipt provenance records it |
| Command/path escape | Unknown command, effect, absolute/traversal/out-of-scope path is refused before execution with one narrow remediation |
| Provenance | CLI and receipt outputs bind producer, operation, revision/input/output and capability when applicable without embedding payloads |
| Telemetry privacy | Events exclude arguments, prompts, paths, work IDs, source/output, people, approvals, and reviews; sink failure cannot invalidate the underlying command |
| Friction metrics | Aggregate command/refusal/replay/recovery/verification/maintenance metrics are deterministic and read-only |
| Multi-turn regressions | Corpus catches extra approval, full-suite, metadata-edit, retry, ambiguous refusal, missing recovery, unsafe maintenance, and confinement regressions |
| Threshold policy | Safety assertions are hard constraints; friction budgets may fail evaluation but cannot waive a safety assertion |
| Portability | Generic tests use synthetic vocabulary/adapters and Financial AI Academy mappings remain separate |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0015 | Deliver confinement, provenance, telemetry, deterministic harness evaluation, readiness/docs/final CAP evidence, and anti-rigidity tests | WRK-0014 | none | ready |

## Verification and Qualification

Run qualification/evaluation tests, committed corpus evaluator, all predecessor
control suites, workflow/local/CI readiness, planning, docs, diff checks, and the
slice/CAP deterministic completion gates. Inspect reports for forbidden fields.

## Rollback and Migration

Telemetry and reports are ignored derived evidence. Disabling emission leaves
authoritative lifecycle unchanged. Capability enforcement is additive around
the already allowlisted check catalog; rollback removes the wrapper without
changing command definitions. Provenance fields are additive versioned data.

## Stop Conditions

Stop for raw or identifying telemetry, remote transmission, arbitrary command
or path grants, nondeterministic grading, a metric that weakens safety, external
effects, or material CAP drift.

## Documentation Impact and Completion Evidence

Control-plane, agent, and planning guides now map reusable capability,
provenance, telemetry, and evaluation cores and their adapter boundaries.
AI-agent/testing standards, testing architecture, AI/delivery/testing context,
and assurance gaps now define local privacy, non-blocking metrics, hard safety
constraints, deterministic friction budgets, and the remaining remote/hosted
qualification boundary.

Final focused results on 2026-10-15: qualification 9 passed; all 7 multi-turn
scenarios passed; operations 8 passed; policy/status 8 passed; review 6 passed;
verification 10 passed; lifecycle 10 passed; CI workflow contract passed;
planning integrity passed for 26 artifacts; documentation validation passed for
146 Markdown files; local readiness passed 18 checks; CI-profile readiness
passed 17 checks; and `git diff --check` passed. Generated readiness, harness,
policy, and telemetry reports remained under ignored `artifacts/control-plane/`.

## Planning History

- 2026-10-15: Refined just in time after SLI-0007 completion; Candidate A
  scored 14/14 and remains within CAP-0002's local qualification boundary.
- 2026-10-15: Deterministic completion structure and the full cross-slice
  qualification passed; the final slice closed without lower-level approval.
