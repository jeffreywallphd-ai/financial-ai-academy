---
id: CAP-0003
kind: capability
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: null
depends_on: ["CAP-0002"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0009", "SLI-0010", "SLI-0011", "SLI-0012", "SLI-0013", "SLI-0014"]
---

# Capability: Plan and Orchestrate Capability Portfolios

## Outcome

A repository operator can turn candidate and shaped capabilities into an
explainable, dependency-aware portfolio plan, track the order in which CAPs,
SLIs, and WRKs are eligible to proceed, and identify governed work at each level
that multiple agents can deliver concurrently without creating excessive write,
contract, decision, or ownership conflicts. When parallel delivery begins,
agents can publish their edit intent and coordinate through exclusive,
renewable leases so that only one agent can edit a repository file at a time
across concurrent CAP, SLI, or WRK work.

The control plane distinguishes hard dependency constraints from explicit
human priority, reports why a CAP is ready, blocked, ordered, or incompatible
with another CAP, exposes who has an active file-edit lease and how to recover
it safely, and recomputes the plan as decisions and delivery state change. It
does not invent product priority, approve a CAP, or start an agent.

## Users and Value

Repository maintainers need to move from a catalog of candidate outcomes to a
coherent delivery portfolio without serializing every capability, slice, and
packet or allowing agents to collide in shared contracts, generated artifacts,
planning state, or implementation boundaries. Development agents need a stable
ready set, dependency rationale, and conflict evidence at the granularity they
are authorized to work before accepting it.

Value is observable when the operator can see the minimum dependency-respecting
CAP order, the current parallel-safe CAP sets, the reason for every exclusion,
and a bounded remediation for missing or stale planning data. Independent CAPs
can proceed on separate `codex/*` branches while dependent or overlapping CAPs
remain safely ordered. Agents working at CAP, SLI, or WRK granularity can
discover pending and active edits before touching a file, while unrelated files
and all read-only work remain concurrent.

## In Scope

- A versioned portfolio model for catalog candidates and `CAP-*` artifacts,
  including source, lifecycle status, manifest status, decision posture,
  dependencies, explicit priority constraints, and current delivery state.
- A hierarchy-aware projection of each CAP's declared `SLI-*` manifest and each
  refined slice's `WRK-*` dependency graph, so readiness and concurrency can be
  computed independently at capability, slice, and work-packet granularity
  without treating an ancestor container as a second editing owner.
- Explicit dependency types that distinguish hard outcome, contract, decision,
  and evidence prerequisites from human-selected priority preferences.
- Deterministic validation of missing references, cycles, contradictory order
  constraints, stale CAP bindings, and dependencies on superseded work.
- Explainable ready sets and dependency-respecting proposed sequences at CAP,
  SLI, and WRK granularity that honor parent authority, accepted roadmap order,
  and explicit operator priority without manufacturing business priority for
  otherwise equivalent work.
- Cross-CAP, cross-slice, and cross-packet conflict analysis over declared and
  projected write scopes, generated artifacts, shared contracts, decision
  gates, exclusive resources, active claims, branch state, ancestry, and other
  evidence that can make concurrent work unsafe.
- Pairwise and set-level parallel-safety results with machine-readable reason
  codes, confidence/evidence classification, and the narrowest remediation for
  each exclusion.
- A repository-local agent communication plane that publishes normalized
  repository-relative edit intent, active file leases, owning CAP/SLI/WRK and
  agent/claim references, lease expiry, heartbeat, release, recovery, refusal,
  and append-only transition evidence through machine-readable status and
  event contracts.
- Atomic, exclusive file-edit lease acquisition that permits many readers but
  guarantees at most one live editing owner for each canonical file path,
  rejects path aliases and case variants, supports deadlock-safe all-or-nothing
  acquisition for bounded multi-file edits, and refuses displacement of a live
  owner.
- A proposed hierarchy-aware multi-agent allocation view that can form
  conflict-free lanes from dependency-ready CAPs, SLIs within an approved CAP,
  or WRKs within an active slice; prevents duplicate allocation of a container
  and its descendant as independent editing owners; tracks `codex/*` branches
  and active descendants; incorporates file-edit intent and leases; and
  recomputes after lifecycle, scope, decision, priority, or lease changes.
- Read-only and proposed-plan CLI/JSON outputs suitable for operator review and
  later accepted-roadmap generation; mutations remain governed by existing CAP,
  slice, packet, claim, and Git controls.
- Deterministic evaluations, provenance, and privacy-minimized telemetry for
  ordering accuracy, conflict false positives and false negatives, replanning,
  lease contention and recovery, and avoidable serialization or operator
  friction.
- Project-neutral graph, ordering, conflict, allocation, event, and file-lease
  primitives behind adapters for this repository's capability catalog, CAP
  packages, roadmaps, decision register, filesystem path rules, Git branches,
  and control-plane state.

## Out of Scope

- Automatically choosing product value, commercial priority, funding, staffing,
  deadlines, or release commitments when no authoritative priority exists.
- Automatically shaping or approving a CAP, resolving a durable decision,
  changing an accepted roadmap, or treating a recommendation as authority.
- Automatically creating agent conversations, assigning human identities,
  starting implementation, merging branches, pushing commits, publishing,
  deploying, using credentials, or performing production or destructive actions.
- A hosted or distributed scheduler, cross-host lease service, peer-to-peer chat
  or arbitrary agent messaging, cloud resource planner, or replacement for a
  future accepted job queue and delivery-guarantee decision. The communication
  plane is repository-local machine-readable coordination state and events.
- Replacing the planning register, CAP package, accepted roadmap, decision
  readiness register, work-packet claims, or Git as their respective sources of
  truth.
- Requiring every CAP to declare speculative file-level scope before its slices
  and packets are refined, or blocking all concurrency merely because some
  future detail remains unknown.
- Flattening CAP, SLI, and WRK authority into one generic job state, bypassing
  parent approval or dependency rules, or interpreting a parallel-safe result
  as permission to activate unapproved work.
- Locking directories or the whole repository for an ordinary edit, requiring
  a lease for reads, retaining a file lease after its bounded edit finishes, or
  using the communication plane as an additional approval gate.
- Planning all candidate product capabilities inside this CAP. This capability
  delivers the mechanism; each product outcome still requires its own complete
  CAP package and approval.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Automated Development Planning](../README.md)
- [Planning Register](../register.md)
- [Concurrent Automated Work](../concurrent-work.md)
- [Implementation Roadmaps](../../roadmaps/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [AI-Agent Development Standards](../../standards/ai-agent-development-standards.md)
- [Testing and Verification Standards](../../standards/testing-and-verification-standards.md)
- [Change Impact Matrix](../../standards/change-impact-matrix.md)
- [Reusable Local Control Plane](../../../dev-tools/control-plane/README.md)
- [CAP-0002: Operate the AI-Development Control Plane](CAP-0002-operate-ai-development-control-plane.md)

## Decision Gates and Constraints

- DEC-0006 and the current planning authority model remain controlling: only a
  complete CAP package receives human delivery approval, and portfolio output
  cannot create or infer that approval.
- CAP-0002 supplies the completed repository-local lifecycle, verification,
  review, policy, status, maintenance, telemetry, provenance, and confinement
  foundation. CAP-0003 extends it without reopening completed CAP-0002 history.
- Accepted roadmaps remain the sequencing authority. Before roadmap acceptance,
  portfolio order is a proposed plan; afterward the control plane validates and
  projects the accepted order rather than silently changing it.
- Product priority remains explicit human or accepted product/roadmap authority.
  The deterministic default may derive only hard dependency readiness and
  stable tie reporting; it may not convert estimated value, novelty, or model
  preference into authority.
- Parallel safety is evidence-based and progressive. Known independent CAPs may
  proceed without repository-wide serialization; an unknown high-impact shared
  boundary must produce an actionable request for narrower scope or additional
  evidence rather than a fabricated safe result.
- File-edit exclusivity is enforced at the narrowest practical boundary: a
  canonical repository file path. An agent acquires the lease immediately
  before its first write, renews it only while the edit is active, and releases
  it promptly after the bounded edit. Reading, planning, testing that does not
  write the file, and work on unrelated files do not require or wait on that
  lease.
- File leases are subordinate to approved CAP authority, WRK write scope, and
  active packet claims. Holding a lease communicates and arbitrates an edit; it
  never expands scope, grants approval, establishes product priority, or
  replaces branch and claim controls.
- Lease acquisition and state transitions must be atomic, compare-and-swap
  safe, path-normalized for the host filesystem, and recoverable only after
  release or expiry. A live lease cannot be preempted silently, and abandoned
  leases retain provenance without becoming permanent blockers.
- Detailed scopes may become more precise as slices and packets are refined.
  Replanning must preserve prior rationale and detect material CAP drift without
  turning ordinary conforming refinement into another approval gate.
- Parallelism is computed at the narrowest currently planned unit. CAPs may run
  together when their packages are approved and compatible; slices within a CAP
  may run together when their manifest dependencies and refined boundaries
  permit; packets within a slice may run together when their WRK dependencies,
  reciprocal safety declarations, claims, and write scopes permit. A parent is
  a governance and aggregation context, not a duplicate file-edit lease owner.
- Actual remote or multi-host orchestration, automatic agent startup, or a
  durable distributed scheduler requires separate decision review and explicit
  authority. This CAP only identifies and tracks safe parallel opportunities.

No unresolved durable decision blocks shaping this repository-local advisory
capability. Any later expansion into remote execution, autonomous prioritization,
or automatic agent startup crosses the boundaries above and returns the CAP to
shaping or requires a separate CAP and decision review.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0009 | An operator receives one validated portfolio inventory and hierarchical dependency graph covering catalog candidates, CAP artifacts, declared SLI manifests, and refined WRK graphs, with missing references, cycles, stale bindings, invalid ancestry, and superseded dependencies reported precisely. | First; establishes the project-neutral portfolio, hierarchy, and graph contracts consumed by every later slice. | Treating a catalog entry or descendant as approved work, inventing missing product dependencies, flattening authority levels, or replacing canonical planning sources changes the CAP package. | shaping |
| SLI-0010 | An operator receives explainable ready sets and dependency-respecting proposed order at CAP, SLI, and WRK granularity that honor explicit priority, parent authority, manifest/packet dependencies, and accepted roadmap constraints while reporting unresolved ties. | After SLI-0009. May be refined in parallel with SLI-0011 once the portfolio contract is stable because ordering and conflict analysis have independent outputs. | Autonomous product prioritization, activation of unapproved work, opaque model ranking, or mutation of accepted roadmap order changes the CAP package. | captured |
| SLI-0011 | An operator receives pairwise compatibility matrices and parallel-safe sets for CAPs, SLIs, and WRKs derived from dependency, ancestry, scope, generated-artifact, contract, decision, resource, claim, and branch evidence, with actionable reasons for every exclusion. | After SLI-0009. May be refined in parallel with SLI-0010; it consumes the shared portfolio contract but does not depend on a chosen priority among equally ready work. | Declaring safety without evidence, requiring speculative file-level scope for every future CAP, bypassing lower-level collision checks, or assigning a container and descendant as independent writers changes the CAP package. | captured |
| SLI-0012 | Agents working on parallel CAPs, slices, or packets can publish edit intent and atomically acquire, inspect, renew, release, or recover exclusive leases on normalized repository file paths, so no two live owners can edit the same file at once while reads and unrelated edits remain concurrent. | After SLI-0011 defines the conflict and evidence contracts. It extends CAP-0002 claim/lease primitives with project-neutral file-edit coordination and repository path adapters. | Directory/repository-wide default locks, read locks, scope expansion through a lease, live-owner preemption, unbounded lease retention, cross-host enforcement, or arbitrary messaging changes the CAP package. | captured |
| SLI-0013 | An operator sees proposed hierarchy-aware multi-agent allocations at CAP, SLI, or WRK granularity, `codex/*` branch and descendant-work tracking, active file-edit coordination, and deterministic replanning when status, priority, decision, conflict, or lease evidence changes. | After SLI-0010, SLI-0011, and SLI-0012; combines order, compatibility, and live coordination outputs. It proposes and tracks lanes but does not create or command agents, and never double-allocates an ancestor container and its descendant as independent writers. | Automatic agent startup, distributed scheduling, silent reassignment, inferred authority, parent-rule bypass, or automatic merge/push changes the CAP package. | captured |
| SLI-0014 | The portfolio planner and communication plane are qualified against realistic concurrent CAP, SLI, and WRK scenarios for dependency and hierarchy accuracy, cycles, stale state, conflict false positives/negatives, exclusive-file safety, lease contention/recovery, parallel utilization, provenance, privacy, and anti-rigidity budgets. | Last; qualifies SLI-0009 through SLI-0013 and integrates supported CLI/JSON, documentation, readiness, and evaluation evidence. | Safety traded for throughput, telemetry containing source or identity payloads, remote enforcement, or a mandatory broad gate for every portfolio or edit operation changes the CAP package. | captured |

The stable portfolio contract from SLI-0009 is the only shared prerequisite for
SLI-0010 and SLI-0011. Their detailed packet plans may proceed concurrently only
when their refined write scopes are reciprocal and disjoint. SLI-0012 adds the
live file-edit coordination needed when approved work actually runs in
parallel. SLI-0013 is the allocation join point, and SLI-0014 remains the final
cumulative qualification.

## Capability Acceptance

The capability is acceptable when evidence demonstrates that:

- every catalog candidate and CAP artifact can be projected without implying
  that catalog inclusion, file presence, or `ready` status grants approval;
- CAP manifests and refined SLI/WRK graphs preserve their hierarchy, authority,
  dependencies, and lifecycle state, and an ancestor container is never treated
  as a competing writer merely because an authorized descendant is active;
- hard dependencies, explicit priority constraints, accepted roadmap order,
  decision posture, parent authority, and lifecycle state produce deterministic
  ready sets and explainable proposed order at CAP, SLI, and WRK granularity,
  with cycles and contradictions refused;
- equivalent inputs produce equivalent graph, order, conflict, and allocation
  results across supported local environments;
- every ordering edge and parallel-safety decision identifies its evidence and
  reason codes, while missing evidence produces a bounded remediation rather
  than a fabricated dependency or safe result;
- CAPs, sibling slices, or sibling packets with no dependency path and no
  credible scope, contract, generated-output, decision, exclusive-resource,
  ownership, ancestry, or branch conflict can be grouped for parallel work by
  multiple agents at the applicable authority level;
- a pair or set with a direct/transitive dependency, overlapping owned boundary,
  active claim conflict, incompatible decision posture, or exclusive resource
  is excluded from the parallel-safe set;
- every attempted edit is preceded by atomic acquisition of the canonical file
  path, and concurrent acquisition attempts prove that no more than one live
  agent/claim owner can hold the edit lease for that file at any instant;
- path normalization prevents case variants, separator variants, relative
  traversal, symlink or equivalent aliases from creating two leases for the
  same repository file, while paths outside the repository are refused;
- an agent can inspect pending intent and active ownership with CAP, SLI, WRK,
  branch, claim, expiry, and bounded remediation context before editing, without
  exposing prompts, file contents, credentials, or personal identifiers;
- bounded multi-file acquisition is atomic or uses a deterministic ordering
  that cannot deadlock, partial failure leaves no orphaned acquisition, live
  owners cannot be preempted, and expired or explicitly released leases can be
  recovered without rewriting history;
- read-only access and edits to different canonical files proceed concurrently,
  leases are obtained just in time and released promptly, and neither a broad
  declared write scope nor uncertain future work reserves every possible file;
- file leases never expand approved scope or replace WRK claims, and status
  distinguishes authorization, projected conflicts, edit intent, and actual
  exclusive ownership rather than collapsing them into one lock concept;
- progressively refined SLI and WRK scopes improve conflict precision without
  invalidating a CAP package for nonmaterial detail or requiring another human
  approval;
- accepted roadmap and explicit operator priority are preserved, unresolved
  equal-priority choices remain visible, and the control plane never substitutes
  model preference for product authority;
- allocation output tracks proposed CAP/SLI/WRK-to-agent/branch relationships,
  current ancestor and descendant work, edit intent, and file leases without
  creating agents, packet claims, commits, merges, or remote effects;
- replanning after completion, blockage, decision change, scope refinement, or
  branch conflict preserves provenance and cannot silently erase earlier
  rationale;
- qualification covers the current 26-candidate catalog, mixed planned and
  unplanned capabilities, concurrent independent CAPs, concurrent compatible
  slices within a CAP, concurrent compatible packets within a slice, cycle and
  stale-state recovery, pairwise and set-level conflicts, and both useful
  concurrency and safe serialization; and
- anti-rigidity evidence sets budgets for avoidable blockers, redundant full
  scans, unnecessary operator steps, excessive false-positive conflicts, stale
  leases, and lock wait time without weakening dependency, authority, or
  single-writer safeguards.

## Risks and Non-Goals

- False-negative conflict analysis could authorize agents to collide in shared
  contracts or generated outputs. Conservative evidence classification,
  packet-level revalidation, and active claims remain mandatory safeguards.
- False-positive conflict analysis could recreate the excessive rigidity this
  capability is intended to remove. Evaluations must measure avoidable
  serialization and offer narrow remediation rather than defaulting to one
  repository-wide lock.
- Capability dependencies can become speculative when a candidate has not yet
  been shaped. The planner must distinguish asserted canonical dependencies,
  shaped CAP dependencies, inferred diagnostic hints, and unknowns; only the
  first two may constrain authoritative order.
- A numeric score can masquerade as product strategy. The control plane may
  display explicit operator-supplied priority and deterministic readiness, but
  it cannot invent value, urgency, or commercial importance.
- Multiple agents increase integration and review pressure even when write
  scopes are disjoint. Branch, exact-candidate, verification, and merge controls
  remain in force and are not replaced by a portfolio-level safe result.
- Hierarchy-aware scheduling can accidentally double-count a CAP and its active
  descendants or bypass a parent dependency. Explicit scheduling granularity,
  ancestor aggregation, and authority-preserving readiness tests prevent that
  ambiguity.
- A crashed agent could leave a stale file lease, while an overly long default
  could halt useful work. Short renewable leases, visible expiry, prompt
  release, safe post-expiry recovery, and contention metrics limit that risk.
- Canonical-path mistakes could allow two names for one file or block an
  unrelated file. Repository-root confinement, host-aware normalization,
  alias tests, and exact-file diagnostics are part of the safety contract.
- A strict single-writer invariant can still become rigid if agents reserve
  files too early or in broad batches. Just-in-time acquisition, bounded atomic
  sets, no read leases, no default directory locks, and measured wait budgets
  preserve progress without weakening exclusivity.
- The capability does not promise optimal scheduling, automatic staffing,
  deadline prediction, remote execution, zero merge conflicts, or autonomous
  product management.

## Documentation Impact

Expected delivery updates include the planning guide, planning register,
concurrent-work protocol, capability and roadmap guidance, control-plane README,
project-neutral graph/order/conflict/allocation/event/file-lease contracts,
Financial AI Academy catalog/planning/path/Git adapters, operator status,
CLI/JSON contracts, tests, evaluation corpus, readiness checks, assurance gaps,
standards, and delivery-planning/testing context packs. Product capability
definitions change only when their canonical product sources change.

Approval and reviewer evidence remains in ignored local storage. Portfolio
reports and accepted roadmaps may retain public dependency and sequencing facts,
but they must not copy approval identities, reviewer data, prompts, source
payloads, credentials, or local operational history.

## Completion Evidence

All six manifest slices and their seven dependency-ordered packets, including
one bounded descendant correction, are complete.
The delivered abstraction separates project-neutral graph, ordering, conflict,
exact-file lease, allocation/replanning, and real-core evaluation modules from
the Financial AI Academy catalog/planning/Git/authority/filesystem adapters.
Synthetic `PROGRAM`/`INCREMENT`/`TASK` fixtures and generic-module import checks
demonstrate that future repositories can keep their own vocabulary and policy.

The final cross-slice run on 2026-10-15 passed 47 focused portfolio/file/
qualification tests, 10 lifecycle regression tests, all 7 real-core portfolio
scenarios, all 13 multi-turn scenarios, planning integrity for 40 artifacts,
documentation validation for 160 Markdown files, design validation for 125
tokens and 56 icons, 25 local readiness checks, 24 CI-profile readiness checks,
ignored-state checks, and `git diff --check`. The real-core corpus produced 9
parallel lanes while preserving 4 intentional singletons, 3 explained
conflict/unknown pairs, and 1 dependency block. Direct evidence covers the
26-candidate catalog, hierarchy/authority separation, deterministic order,
unknown-vs-incompatible conflict handling, useful CAP/SLI/WRK-equivalent
parallelism, exact-file process races and recovery, proposal-only allocation,
replanning lineage, provenance, privacy-minimized telemetry, and friction
budgets that cannot offset safety failures.
The descendant correction additionally proves that lease renewal revalidates
active WRK authority while post-completion release remains available.

Remaining qualifications are deliberately outside CAP-0003: multi-host or
remote coordination, distributed file leases, automatic agent startup, hosted
telemetry/evaluation, branch-protection configuration, merge/push, and other
external actions. No commit, merge, push, publication, deployment, credential
use, or production mutation was performed.

## Planning History

- 2026-10-15: Shaped from the requested control-plane ability to plan and order
  capabilities and identify conflict-aware parallel CAP work for multiple agents.
  An initial five-slice manifest was prepared but not submitted for approval;
  detailed slice and packet planning remained just in time.
- 2026-10-15: Expanded before approval with a repository-local communication
  plane and exclusive, renewable file-edit leases for concurrent CAP, SLI, and
  WRK agents. The revised complete six-slice manifest is proposed for one
  CAP-level approval; no lower-level approval is introduced.
- 2026-10-15: Clarified before approval that readiness, compatibility, agent
  allocation, and parallel execution apply independently at CAP, SLI, and WRK
  levels while preserving hierarchy, parent authority, and single-writer file
  leases.
- 2026-10-15: All six manifest slices passed deterministic completion and
  cumulative qualification; CAP-0003 moved to `complete` without a lower-level
  or final approval stage.
