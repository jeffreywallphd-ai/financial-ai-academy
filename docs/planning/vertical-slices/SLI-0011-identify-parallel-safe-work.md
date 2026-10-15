---
id: SLI-0011
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: ["SLI-0009"]
decision_gates: []
---

# Vertical Slice: Identify Parallel-Safe Work

## Outcome and User Scenario

An operator can request pairwise compatibility and parallel-safe sets for CAPs,
SLIs, or WRKs. Each result explains dependency, scope, generated-output,
contract, exclusive-resource, claim, branch, ancestry, and evidence-confidence
factors and offers narrow remediation when safety is unknown.

## Scope Boundaries

### In Scope

- Project-neutral compatibility facts, pairwise decisions, reason codes,
  confidence, and deterministic safe-set construction.
- Repository projection and aggregation of write scopes, generated artifacts,
  contract paths, exclusive resources, reciprocal packet declarations, active
  claims, branch facts, and refinement completeness.
- Read-only CLI/JSON, documentation, and false-positive/false-negative/
  anti-rigidity tests at CAP, SLI, and WRK levels.

### Out of Scope

- File-edit leases, agent allocation or startup, lifecycle mutation, branch
  creation, merge prediction guarantees, or inferred safety with missing
  high-impact evidence.

## Canonical Context and Decisions

CAP-0003, SLI-0009, concurrent-work rules, existing scope-overlap semantics,
CAP-0002 claim state, and testing standards govern. This slice remains
read-only and repository-local.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Evidence-classified compatibility matrices and safe sets at all three levels | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Treat all unknown scope as conflicting | no — recreates global serialization | — | — | — | — | — | — | — | — |
| C. Treat missing evidence as safe | no — creates false-negative collision risk | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A distinguishes incompatible from unknown, enabling proven parallel
work while asking only for the missing evidence needed to decide uncertain
pairs.

## Boundary Path

Portfolio graph nodes receive repository-owned coordination facts; the generic
compatibility core calculates dependency reachability and pairwise evidence;
deterministic grouping produces safe sets; CLI output remains advisory and
read-only.

## Contracts, Data, and Provenance

`portfolio-compatibility-v1` contains level, considered IDs, pair decisions,
reason codes, confidence/evidence fields, safe sets, and exclusions. It exposes
work IDs and repository-relative declared paths but no file contents, ledger
metadata, owner identity, prompts, or credentials.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Dependency path | Direct or transitive dependencies are incompatible | Core test |
| Scope/output overlap | Exact or ancestor overlap is incompatible with precise reason codes | Core test |
| Disjoint evidence | Independent, fully scoped units form a parallel-safe set | Core test |
| Packet declaration | WRKs require reciprocal `parallel_safe_with` plus disjoint evidence | Adapter/core test |
| Missing detail | Result is `unknown` with narrow refinement remediation, not global conflict or safe | Anti-rigidity test |
| Active claim/branch/resource | Exclusive collisions are incompatible without exposing owner identity | Adapter/core test |
| Set-level conflict | Every pair in a returned safe set is compatible | Property-style test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0019 | Deliver compatibility matrices, safe sets, repository evidence projection, CLI/docs, and tests | WRK-0017 | none | complete |

## Verification and Qualification

Run compatibility, ordering, graph, lifecycle, planning, docs, aggregate, and
diff checks. Verify safe-set pair closure and unknown-evidence anti-rigidity.

## Rollback and Migration

Additive read-only code with no migration. Rollback removes the compatibility
module/adapter fields/command/tests without changing planning state.

## Stop Conditions

Stop for fabricated safety, default global locks, identity leakage, automatic
activation, unresolved decision, or material CAP drift.

## Documentation Impact and Completion Evidence

The control-plane and concurrent-work guides now document the three-state
compatibility model and reciprocal WRK rule. `portfolio-compatibility-v1` is
additive and read-only. Conflict tests passed 7 scenarios; ordering tests passed
7; graph tests passed 7; the lifecycle suite passed 10; planning integrity
passed for 33 artifacts; documentation validation passed for 153 Markdown
files; aggregate readiness passed 18 checks; and diff checking passed. Scope
completeness is conservative: unrefined descendants produce `unknown`, not a
safe or global-conflict result. No migration or external qualification was
required, and the slice conforms to CAP-0003.

## Planning History

- 2026-10-15: Refined just in time after SLI-0009; Candidate A scored 14/14
  and remains independently deliverable alongside completed SLI-0010.
- 2026-10-15: Delivered multi-level compatibility matrices, pairwise-safe sets,
  repository evidence aggregation, CLI/docs, and safety plus anti-rigidity tests.
