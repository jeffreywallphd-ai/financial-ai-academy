---
id: SLI-0012
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: CAP-0003
depends_on: ["SLI-0011"]
decision_gates: []
---

# Vertical Slice: Coordinate Exclusive File Edits

## Outcome and User Scenario

Agents working in parallel CAP, SLI, or WRK lanes can announce bounded edit
intent and atomically acquire, inspect, renew, release, or recover exclusive
leases on canonical repository files. At most one live owner can edit a file,
while reads and edits to unrelated files remain concurrent.

## Scope Boundaries

### In Scope

- Project-neutral intent, file-lease, event, refusal, expiry, recovery, and
  status contracts with confined atomic local persistence.
- Canonical path identity across separators, case variants, relative aliases,
  and in-repository symlink resolution; absolute, traversal, outside-root, and
  directory targets are refused.
- Atomic all-or-nothing bounded multi-file acquisition, renewable short leases,
  non-preemptable live ownership, explicit release, and post-expiry recovery.
- Financial AI Academy authorization binding from CAP/SLI logical lane through
  an active WRK claim and declared write/generated scope.
- CLI/JSON, communication status, docs, and concurrency/anti-rigidity tests.

### Out of Scope

- Read locks, default directory/repository locks, cross-host consensus,
  peer-to-peer chat, automatic file modification, editor integration, agent
  startup, claim creation, branch mutation, merge, push, or remote service.

## Canonical Context and Decisions

CAP-0003, SLI-0011, CAP-0002 lease/store contracts, concurrent-work rules,
packet authority and scope, local-only state/privacy, and testing standards
govern. Cross-host enforcement remains outside the approved boundary.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Repository-local exact-file intent and renewable exclusive leases | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Repository-wide mutex for an agent session | no — excessive serialization | — | — | — | — | — | — | — | — |
| C. Distributed cross-host lease service | no — outside accepted provider/execution boundary | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A enforces the requested single-writer invariant at the smallest
practical boundary and builds on the local control-plane transaction model
without turning reads or unrelated work into blockers.

## Boundary Path

An agent supplies logical CAP/SLI/WRK lane, active WRK claim, and exact file
paths; the repository adapter proves authority/scope/ancestry; the generic core
canonicalizes every path, atomically transitions local lease state, and emits
append-only categorical events; status exposes current intent/leases without
tracked or remote effects.

## Contracts, Data, and Provenance

`file-edit-state-v1`, `file-edit-lease-v1`, `file-edit-intent-v1`, and
`file-edit-event-v1` remain under ignored `.local-codex/control-plane/`. Records
contain local owner/claim and planning IDs, canonical repository-relative paths,
timestamps, lease IDs, event types, and recovery lineage but no file contents,
prompts, credentials, approval/reviewer data, or personal identity requirements.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Single file race | Exactly one concurrent owner acquires; the other receives current expiry and narrow remediation | Multi-process/core test |
| Different files | Different owners acquire and work concurrently without waiting on edit duration | Anti-rigidity test |
| Alias collision | Case, separator, relative, and resolved in-repository aliases map to one lease key | Path/core test |
| Multi-file conflict | Any one conflict refuses the entire set and leaves no partial/orphaned lease | Transaction test |
| Live preemption | Recovery refuses an unexpired owner | Core test |
| Expiry recovery | Explicit recovery after expiry creates lineage and preserves prior events | Core test |
| Authority/scope | Lease cannot expand WRK scope; CAP/SLI lane must be an ancestor of the active WRK claim | Adapter test |
| Reads/no broad locks | Status/read use needs no file lease; directories and repository-wide targets cannot be leased | Anti-rigidity test |
| Privacy/locality | State is ignored/local and contains no source contents, prompts, credentials, or approval/reviewer records | Contract test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0020 | Deliver the local edit-intent and exclusive file-lease plane, repository authority adapter, CLI/docs, and tests | WRK-0019 | none | complete |
| WRK-0023 | Revalidate active WRK authority on lease renewal while preserving post-completion release | WRK-0020 | none | complete |
| WRK-0029 | Stabilize independent-process same-file races while preserving disjoint-file and read concurrency | WRK-0023 | none | complete |

## Verification and Qualification

Run file-lease tests including multi-process and expiry paths, all portfolio and
control-plane suites, planning/docs, aggregate readiness, ignored-state, and
diff checks.

## Rollback and Migration

The new ignored state has its own version and no tracked migration. Normal
rollback stops using the command and preserves local state/events for diagnosis;
bounded maintenance may archive stale ignored state. Existing packet leases are
unchanged.

## Stop Conditions

Stop for cross-host claims, read locks, broad default locks, live-owner
preemption, non-atomic multi-file behavior, scope expansion, sensitive payloads,
unresolved decision, or material CAP drift.

## Documentation Impact and Completion Evidence

The reusable `file-edit-state-v1` core and repository adapter now provide
exact-file intent, all-or-nothing acquisition, renewal, release, status, and
complete-set expiry recovery for CAP/SLI/WRK lanes backed by an active WRK.
Focused tests passed 11 scenarios, including a real two-process race, path
aliases, nonblocking intent, disjoint-file concurrency, scope confinement,
privacy minimization, and recovery lineage. Portfolio graph, ordering, and
compatibility tests each passed 7; lifecycle tests passed 10; planning passed
for 35 artifacts; docs passed for 155 Markdown files; aggregate readiness
passed all 18 checks; ignored-state and diff checks passed. Windows sandboxed
temporary directories required the approved unsandboxed test route. Cross-host
consensus remains intentionally out of scope; local exact-file enforcement
conforms to CAP-0003 without adding read or broad locks.

A bounded descendant correction now revalidates the backing active WRK claim
and declared paths before lease renewal. Focused tests prove active renewal still
succeeds, post-completion renewal is refused, and the recorded owner/claim can
release after completion so cleanup never requires reactivation.

WRK-0029 additionally normalizes equivalent Windows device paths and safely
revalidates a short-lived lock pathname that resolves through NTFS
`$Extend\$Deleted` after a concurrent release. The correction preserves stable
symlink/junction escape refusal and adds diagnostic worker evidence. Twelve
focused scenarios, 500 consecutive fresh-state two-process races, all 109
control-plane tests, and all 27 aggregate readiness checks passed. Disjoint
files and reads remain concurrent, so the correction strengthens single-writer
safety without adding a broad coordination barrier.

## Planning History

- 2026-10-15: Refined just in time after SLI-0011; Candidate A scored 14/14
  and conforms to CAP-0003.
- 2026-10-15: Delivered and verified reusable exact-file coordination, the
  Financial AI Academy authority adapter, CLI/docs, and anti-rigidity coverage.
- 2026-10-15: Closed WRK-0023 as a bounded descendant correction enforcing
  active packet authority on renewal while preserving post-completion release.
- 2026-10-15: Added WRK-0029 through the completed-work correction route after
  aggregate readiness reproduced intermittent non-contention classification in
  the independent-process same-file race; CAP-0003 scope and semantics are
  unchanged.
- 2026-10-15: WRK-0029 completed after Windows path normalization, deleted-lock
  revalidation, 500 consecutive race passes, and full control-plane and
  aggregate readiness qualification; the slice returned to its complete state.
