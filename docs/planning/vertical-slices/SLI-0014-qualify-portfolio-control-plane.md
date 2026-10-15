---
id: SLI-0014
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: ["SLI-0009", "SLI-0010", "SLI-0011", "SLI-0012", "SLI-0013"]
decision_gates: []
---

# Vertical Slice: Qualify the Portfolio Control Plane

## Outcome and User Scenario

An operator and repository maintainer receive fixed, deterministic evidence that
the complete CAP-0003 portfolio and communication plane preserves hierarchy,
dependency order, useful parallelism, single-writer file safety, provenance,
privacy, bounded recovery, and low-friction behavior. Future repositories can
run the generic harness with their own adapter and vocabulary.

## Scope Boundaries

### In Scope

- A project-neutral, tracked scenario corpus that executes the real generic
  graph/order/conflict/allocation pipeline and enforces hard safety separately
  from anti-rigidity budgets.
- Cumulative tests for the current 26-candidate catalog, mixed shaped/unshaped
  work, CAP/SLI/WRK-equivalent hierarchy levels, dependency/cycle/stale inputs,
  conflicts, single-writer races, recovery, replanning, provenance, and privacy.
- Adapter-independence evidence using non-CAP/SLI/WRK identifiers plus a concise
  adapter contract for future repositories.
- Portfolio/edit telemetry aggregates containing categorical counts only, with
  sink failure remaining non-blocking.
- Fixed local/CI readiness integration and synchronized testing, assurance,
  context, concurrent-work, and control-plane documentation.

### Out of Scope

- Hosted/multi-host enforcement, remote telemetry, automatic agent startup,
  production effects, branch-protection configuration, performance guarantees
  across unrelated hardware, or closing unrelated repository assurance gaps.

## Canonical Context and Decisions

CAP-0003 and all preceding slices, CAP-0002 qualification contracts, testing and
AI-agent standards, architecture verification, known verification gaps, CI
readiness wiring, and privacy/locality rules govern. No unresolved durable
decision applies to local deterministic qualification.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Real-core scenario harness plus cumulative safety/friction, telemetry, provenance, adapter, and readiness qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Rely only on focused unit suites and prose claims | no — misses cumulative behavior and friction budgets | — | — | — | — | — | — | — | — |
| C. Require hosted multi-agent execution before local completion | no — crosses approved provider/execution boundary | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A directly exercises the reusable implementation and makes both false
safety and excessive serialization visible without extending authority or
depending on a hosted scheduler.

## Boundary Path

Tracked synthetic scenarios feed the generic pipeline through its public
contracts; the evaluator emits digest/count-only reports and applies hard safety
assertions before friction budgets; repository qualification adds catalog,
adapter, CLI provenance/privacy, telemetry, lease-race, and readiness evidence;
documentation maps each claim to its owning check.

## Contracts, Data, and Provenance

`portfolio-harness-corpus-v1` and `portfolio-harness-report-v1` use synthetic
project-neutral IDs and scopes. Reports retain scenario IDs, digests, categorical
metrics, and violation codes, not node payloads, source contents, prompts,
credentials, approval/reviewer metadata, or personal identifiers. Existing
control provenance binds CLI results and existing anonymous telemetry records
categorical command outcomes only.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Useful concurrency | Independent complete-scope work reaches the minimum parallel-lane budget without an avoidable global lock | Real-core corpus |
| Safe serialization | Dependencies, overlaps, and live single-file ownership prevent only unsafe pairs and never allow two live file owners | Corpus/core/process race |
| Unknown evidence | Only affected lanes remain unresolved, with bounded refinement and false-positive serialization budgets | Corpus/anti-rigidity |
| Hierarchy/order | CAP/SLI/WRK-equivalent runs preserve parent authority, dependency order, explicit priority, and no ancestor/descendant double allocation | Cumulative tests |
| Replanning/recovery | Lifecycle, scope, priority, branch, and lease changes create durable rationale changes; expired leases recover without live preemption | Cumulative tests |
| Current repository | All 26 catalog candidates project beside governed work without implying approval | Adapter test |
| Reuse | Generic modules and corpus run with `PROGRAM`/`INCREMENT`/`TASK` vocabulary and no repository adapter imports | Conformance test |
| Privacy/provenance | CLI output validates provenance and reports/events contain no forbidden payload or identity fields | Contract test |
| Fixed gates | Local and CI readiness run every portfolio/communication suite and evaluator | Readiness contract test |
| Known limits | Multi-host enforcement and hosted qualification remain explicit gaps rather than fabricated passes | Documentation check |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0022 | Deliver cumulative real-core evaluation, telemetry/readiness integration, adapter/reuse evidence, and synchronized assurance documentation | WRK-0017, WRK-0018, WRK-0019, WRK-0020, WRK-0021 | none | complete |

## Verification and Qualification

Run every portfolio, lease, lifecycle, qualification, and evaluator suite;
evaluate both local and CI readiness profiles; run planning/docs/design, ignored-
state, privacy/provenance, and diff checks. Keep external hosted qualification as
an explicit gap.

## Rollback and Migration

Qualification additions are tracked tests, corpus, allowlisted gates, metrics,
and docs. No product or state migration occurs. Rollback removes those additive
artifacts without changing operational portfolio or lease state.

## Stop Conditions

Stop if throughput can offset a safety failure, tests require sensitive data,
telemetry becomes blocking or payload-bearing, generic harness code imports the
repository adapter, gates add authority, a remote effect is required, an
unresolved decision appears, or CAP scope materially drifts.

## Documentation Impact and Completion Evidence

`portfolio-harness-report-v1` now executes seven tracked scenarios through the
real generic pipeline: all 7 passed with 9 parallel lanes, 4 intentional
singletons, 3 explained unresolved/conflict pairs, and 1 dependency block. The
13-scenario command corpus passed 13/13. Cumulative qualification passed 8
tests; CAP-0002 qualification passed 9; file coordination passed 11; allocation,
compatibility, ordering, and graph suites each passed 7; lifecycle passed 10.
Planning passed for 39 artifacts, documentation for 159 Markdown files, design
for 125 tokens/56 icons, local readiness for 25 checks, CI readiness for 24,
ignored-state and diff checks passed, and the generated digest/count-only report
remains ignored. Synthetic `PROGRAM`/`INCREMENT`/`TASK` fixtures and import
checks prove the generic layer does not depend on Financial AI Academy or its
CAP/SLI/WRK identifiers. Windows process/temp tests used the approved
unsandboxed route. Multi-host leases, hosted agent startup, remote telemetry,
and hosted evaluation remain explicit external gaps; no safety claim covers
them. The slice conforms to CAP-0003.

## Planning History

- 2026-10-15: Refined as the final cumulative CAP-0003 slice after SLI-0013;
  Candidate A scored 14/14 and remains within the approved local boundary.
- 2026-10-15: Delivered and verified real-core safety/friction evaluation,
  cumulative reuse/privacy/provenance evidence, fixed readiness gates,
  telemetry aggregates, and synchronized assurance documentation.
