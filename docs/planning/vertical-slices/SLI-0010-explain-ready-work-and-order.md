---
id: SLI-0010
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: ["SLI-0009"]
decision_gates: []
---

# Vertical Slice: Explain Ready Work and Proposed Order

## Outcome and User Scenario

An operator can request an explainable ready set and dependency-respecting
proposed order at CAP, SLI, or WRK granularity. The result preserves current CAP
authority, parent lifecycle, hard dependencies, explicit operator priority, and
accepted roadmap constraints while leaving equal-priority choices visibly tied.

## Scope Boundaries

### In Scope

- Project-neutral readiness, block-reason, ordering-constraint, tie-group, and
  proposed-order contracts over `portfolio-graph-v1`.
- Deterministic CAP, SLI, and WRK readiness rules with completed dependency,
  decision-gate, parent, and current CAP-package authority checks.
- Explicit priority/sequence inputs and stable tie reporting without inferred
  product value.
- Repository adapter, read-only CLI/JSON output, documentation, and tests.

### Out of Scope

- Conflict compatibility, agent allocation, file leases, roadmap mutation,
  autonomous priority scoring, lifecycle mutation, or agent startup.

## Canonical Context and Decisions

CAP-0003, SLI-0009, the roadmap and planning authority guides, decision
readiness, local approval binding, and control-plane result contracts govern.
No accepted active roadmap currently adds repository sequence constraints.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deterministic multi-level ready sets with explicit priority and visible ties | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Numeric model-generated business ranking | no — invents product authority | — | — | — | — | — | — | — | — |
| C. Automatically rewrite accepted roadmaps | no — mutation is outside this slice | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A provides useful sequencing without turning a deterministic
presentation order into product strategy. It consumes the graph contract and is
independently testable before compatibility analysis.

## Boundary Path

The repository graph and local current-authority facts enter the reusable
ordering core with an explicit level and optional priority sequence. The core
returns readiness explanations, blocked items, tie groups, and a proposed order;
the CLI publishes the result without modifying any source.

## Contracts, Data, and Provenance

`portfolio-plan-v1` contains granularity, ready/blocked entries with reason
codes, explicit constraints, unresolved tie groups, and proposed order. It may
contain a boolean current-authority fact but never local ledger metadata,
identity, decision history, or inferred priority.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Ready CAP | Current approved CAP with completed dependencies and no decision gate appears ready with reasons | Adapter/core test |
| Slice/WRK readiness | Parent authority and lifecycle plus same-level dependencies are enforced at the requested granularity | Core test |
| Missing authority | Work is blocked with one bounded remediation and no ledger detail | Adapter test |
| Explicit priority | Operator order breaks otherwise equal choices and is labeled explicit | Core/CLI test |
| Equal choices | Stable display order is accompanied by an unresolved tie group | Anti-rigidity/authority test |
| Completed work | Completed items satisfy dependencies but are not proposed as new work | Core test |
| Unknown priority ID | Request is refused precisely rather than silently ignored | Core test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0018 | Deliver hierarchy-aware readiness and proposed ordering with explicit priority, CLI, docs, and tests | WRK-0017 | none | complete |

## Verification and Qualification

Run ordering and portfolio tests, existing control-plane tests, planning/docs,
aggregate readiness, and diff checks. Verify no output includes ledger metadata
or treats stable tie display as authority.

## Rollback and Migration

Read-only additive code; no state migration. Rollback removes the ordering
module/command/tests without changing graph or lifecycle data.

## Stop Conditions

Stop for inferred business priority, mutation, hidden ties, stale authority
treated as current, unresolved durable decisions, or material CAP drift.

## Documentation Impact and Completion Evidence

The control-plane guide documents the new ordering core and read-only command.
`portfolio-plan-v1` is additive to the graph and existing result envelopes.
Ordering tests passed 7 scenarios; graph tests passed 7; the lifecycle suite
passed 10; planning integrity passed for 31 artifacts; documentation validation
passed for 151 Markdown files; aggregate readiness passed 18 checks; and diff
checking passed. Temporary Git tests ran outside the restricted Windows sandbox.
No roadmap is currently active, so accepted-sequence ingestion is covered by
the reusable contract rather than a live repository fixture. No migration or
external qualification was required. The slice conforms to CAP-0003.

## Planning History

- 2026-10-15: Refined just in time after SLI-0009 completed; Candidate A scored
  14/14 and conforms to CAP-0003.
- 2026-10-15: Delivered multi-level ready sets, dependency-respecting order,
  explicit priority, visible ties, current-authority projection, CLI/docs, and
  focused anti-rigidity and authority tests.
