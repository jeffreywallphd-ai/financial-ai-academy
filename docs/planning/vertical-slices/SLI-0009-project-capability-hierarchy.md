---
id: SLI-0009
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: []
decision_gates: []
---

# Vertical Slice: Project the Capability Delivery Hierarchy

## Outcome and User Scenario

An operator can request one deterministic, read-only inventory of catalog
candidates and governed CAP, SLI, and WRK artifacts. The result preserves
ancestry and dependencies and reports missing references, dependency cycles,
stale manifest bindings, invalid parent relationships, and dependencies on
superseded work without treating catalog presence or planning status as
authority.

## Scope Boundaries

### In Scope

- Project-neutral node, hierarchy, dependency-edge, issue, and graph-result
  contracts with stable ordering and reason codes.
- Validation of duplicate IDs, missing references, cycles, invalid ancestry,
  CAP-to-SLI manifest drift, stale child bindings, and superseded dependencies.
- A Financial AI Academy adapter for the product capability catalog and current
  planning artifacts.
- Read-only CLI and JSON output, documentation, focused tests, and malformed or
  partial-input behavior.

### Out of Scope

- Readiness or priority recommendations, conflict scoring, allocations, file
  leases, lifecycle mutation, roadmap generation, or agent activation.
- Invented candidate dependencies or promotion of catalog rows into CAP
  authority.

## Canonical Context and Decisions

CAP-0003, the planning guide/register, capability catalog, concurrent-work
protocol, decision-readiness register, CAP-0002 control-plane contracts, and
testing standards govern. The current CAP package has no unresolved decision
gate, and this read-only projection remains repository-local.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Versioned hierarchy graph plus repository adapter and read-only CLI | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. CAP-only graph without SLI/WRK ancestry | no — does not satisfy the approved hierarchy outcome | — | — | — | — | — | — | — | — |
| C. Mutable roadmap generator | no — sequencing and mutation belong to later slices | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the smallest end-to-end increment that makes current planning
state explainable and supplies stable inputs to ordering, compatibility, lease,
and allocation slices. It is deterministic, read-only, and reversible.

## Boundary Path

Canonical catalog and planning artifacts enter the Financial AI Academy
adapter; the adapter emits project-neutral nodes; the reusable graph core
normalizes and validates nodes and edges; the CLI emits one stable success or
actionable-refusal envelope without modifying planning or lifecycle state.

## Contracts, Data, and Provenance

`portfolio-graph-v1` contains sorted nodes, dependency edges, ancestry,
topological order where possible, and sorted diagnostic issues. Source
references are repository-relative paths and row-derived candidate keys; no
approval, reviewer, prompt, file content, or personal data is copied. Catalog
nodes are explicitly `candidate`, never approved delivery work.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Current repository | Catalog candidates and CAP/SLI/WRK artifacts appear once with stable ancestry and source references | Adapter integration test |
| Missing dependency | Result reports the exact source and missing target without fabricating a node | Core unit test |
| Dependency cycle | Every involved node is reported deterministically and no false topological order is claimed | Core unit test |
| Manifest drift | Missing, extra, or mis-parented SLI bindings receive distinct reason codes | Adapter/core test |
| Superseded dependency | Dependency on a superseded node is diagnosed with bounded remediation | Core unit test |
| Partial future detail | A CAP with declared slices but no refined SLI file remains visible as an expected binding, not a repository-wide blocker | Anti-rigidity test |
| Authority separation | Candidate presence and `ready` status never appear as approval evidence or executable authority | Contract test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0017 | Deliver the reusable portfolio hierarchy graph, Financial AI Academy adapter, CLI, documentation, and focused tests | none | none | complete |

## Verification and Qualification

Run the portfolio tests, existing control-plane tests, planning validation,
documentation validation, aggregate readiness, and diff checks. Inspect output
for deterministic ordering and forbidden authority or identity fields.

## Rollback and Migration

The slice adds read-only code and commands. It creates no tracked or durable
state migration. Rollback removes the command, adapter, core, and tests without
altering existing lifecycle data.

## Stop Conditions

Stop for invented dependencies, approval inference, mutable roadmap behavior,
raw document payloads in output, an unresolved durable decision, or material
CAP drift.

## Documentation Impact and Completion Evidence

The reusable control-plane README now documents the portfolio core, repository
adapter, and read-only command. `portfolio-graph-v1` is additive and does not
change lifecycle state or existing result envelopes. Focused portfolio tests
passed 7 scenarios; the existing control-plane lifecycle suite passed 10 tests;
planning integrity passed for 29 artifacts; documentation validation passed for
149 Markdown files; aggregate readiness passed all 18 checks; and diff checking
passed. The Windows temporary-repository suite required execution outside the
restricted temp sandbox and then passed. No migration, external qualification,
or generated tracked artifact was required. The delivered boundary conforms to
CAP-0003 and leaves ordering, compatibility, leases, and allocation to later
slices.

## Planning History

- 2026-10-15: Refined just in time as the first enumerated CAP-0003 slice.
  Candidate A scored 14/14 and conforms to the approved package.
- 2026-10-15: Delivered the project-neutral hierarchy graph, repository
  projection, read-only CLI, documentation, and focused authority-separation
  and anti-rigidity tests.
