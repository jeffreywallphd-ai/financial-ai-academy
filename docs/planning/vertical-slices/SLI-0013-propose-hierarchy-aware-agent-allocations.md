---
id: SLI-0013
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: ["SLI-0010", "SLI-0011", "SLI-0012"]
decision_gates: []
---

# Vertical Slice: Propose Hierarchy-Aware Agent Allocations

## Outcome and User Scenario

An operator can request a deterministic proposed allocation at capability,
slice, or work granularity and see dependency-ready lanes, pairwise-safe groups,
active descendants, current branch facts, and live edit coordination. A later
run explains what changed without creating agents, claims, branches, or work.

## Scope Boundaries

### In Scope

- A project-neutral allocation and replan contract composed from the existing
  graph, ordering, compatibility, and coordination contracts.
- One explicit granularity per allocation, so an ancestor container and its
  descendant can never become independent editing owners in the same plan.
- Deterministic lanes and parallel groups for ready and in-progress work,
  preserving explicit priority, authority, dependencies, compatibility, active
  descendants, branch facts, intent, and live/expired file-lease observations.
- Stable input/plan digests and categorical change records when a prior plan is
  supplied, including additions, removals, state changes, and rationale changes.
- A Financial AI Academy adapter, read-only CLI/JSON, documentation, and safety
  plus anti-rigidity tests at CAP, SLI, and WRK levels.

### Out of Scope

- Agent/thread creation, assignment commands, claim or lease acquisition,
  branch creation/switching, commits, merges, pushes, priority invention,
  accepted-roadmap mutation, distributed scheduling, or remote execution.

## Canonical Context and Decisions

CAP-0003, SLI-0010 through SLI-0012, CAP-0002 local state/provenance rules,
concurrent-work guidance, current CAP authority, and testing standards govern.
No unresolved decision gate applies because this remains a local advisory view.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deterministic single-granularity lanes composed from ready, compatibility, branch, and edit evidence | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Automatically create and assign agents from each safe set | no — crosses explicit execution and authority boundaries | — | — | — | — | — | — | — | — |
| C. Persist one static allocation that ignores live state changes | no — cannot satisfy replanning or stale-evidence safety | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A produces an immediately useful proposed control view while keeping
all mutations in existing governed paths. It reuses stable generic contracts
and asks for refinement only where compatibility evidence is actually unknown.

## Boundary Path

The project adapter supplies the generic hierarchy, current CAP authority,
checkout branch, and privacy-minimized file coordination; the generic allocator
composes readiness and compatibility at one requested level, derives lanes and
parallel sets, binds active descendant facts, and compares an optional prior
plan; the CLI returns the proposal without changing any source of truth.

## Contracts, Data, and Provenance

`portfolio-allocation-v1` contains level, input and plan digests, lanes,
parallel-safe groups, unresolved items, change records, and explicit
`creates_agents: false`/`grants_authority: false` constraints. It carries IDs,
categorical state, repository-relative branch/coordination counts, and reason
codes, but no prompts, file contents, credentials, personal identity, or local
approval/reviewer records.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Ready compatible work | Independent ready units appear in one pairwise-safe proposed group with stable lane order | Core test |
| Dependency/conflict | Blocked, incompatible, or unknown units are excluded or isolated with existing reason codes and narrow remediation | Core test |
| Hierarchy safety | One run contains exactly one granularity and never assigns a container plus descendant as separate writers | Core/property test |
| Active descendants | A CAP or SLI lane reports active descendant IDs and current `codex/*` branch evidence without duplicating their ownership | Adapter/core test |
| File coordination | Intent and live/expired leases change lane observations but do not grant authority or reserve unrelated files | Adapter/anti-rigidity test |
| Replanning | Changed lifecycle, priority, decision, conflict, branch, or lease evidence yields deterministic added/removed/state/rationale changes and a new digest | Core test |
| No mutation | CLI does not create agents, claims, branches, commits, leases, or tracked changes | CLI test |
| Reuse | A synthetic project with non-CAP/SLI/WRK identifiers uses the generic allocator unchanged | Adapter-independence test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0021 | Deliver project-neutral allocation/replanning, the Financial AI Academy adapter/CLI, docs, and focused tests | WRK-0018, WRK-0019, WRK-0020 | none | complete |
| WRK-0052 | Ignore the compatibility-only branch sentinel while preserving genuine and current-checkout branch facts | WRK-0021 | none | active |

## Verification and Qualification

Run allocation, ordering, compatibility, graph, file-lease, lifecycle, planning,
documentation, aggregate readiness, no-mutation, and diff checks. Verify that
unknown evidence narrows the plan instead of globally serializing all work.

## Rollback and Migration

The allocation view is additive and read-only with no tracked persistence or
migration. Rollback removes the module, adapter entry point, command, tests, and
docs while leaving graph, order, compatibility, and lease state unchanged.

## Stop Conditions

Stop for automatic agent/claim/branch mutation, inferred approval or priority,
cross-level double allocation, hidden rationale loss, remote effects,
identity/content leakage, unresolved decision, or material CAP drift.

## Documentation Impact and Completion Evidence

`portfolio-allocation-v1` now composes readiness, compatibility, branch,
descendant, and file-coordination facts at exactly one requested hierarchy
level, with stable plan/input/lane digests and prior-plan change evidence. Seven
focused tests passed using generic `PROGRAM`/`INCREMENT`/`TASK` identifiers,
including dependency blocking, narrow unknown isolation, branch/edit context,
replanning, refusal, and no-mutation CLI behavior. Compatibility, ordering, and
graph suites each passed 7; file leases passed 11; lifecycle passed 10;
planning passed for 37 artifacts; docs passed for 157 Markdown files; aggregate
readiness passed 18 checks; and diff checking passed. Windows temporary and
multi-process tests used the approved unsandboxed route. Allocation remains
advisory and repository-local; automatic agent startup and distributed
scheduling remain intentionally out of scope. The slice conforms to CAP-0003.

## Planning History

- 2026-10-15: Refined just in time after SLI-0012; Candidate A scored 14/14
  and conforms to the approved CAP-0003 allocation join point.
- 2026-10-15: Delivered and verified generic allocation/replanning, repository
  live-fact projection, CLI/docs, reuse proof, and anti-rigidity coverage.
- 2026-10-15: Added WRK-0052 through the bounded completed-work correction
  route after a historical `legacy-unrecorded` compatibility marker was
  projected as a real branch and falsely blocked current Codex-branch readiness.
  Completed SLI-0013 and WRK-0021 history remains terminal.
