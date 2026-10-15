---
id: SLI-0003
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: CAP-0002
depends_on: []
decision_gates: []
---

# Vertical Slice: Resume and Submit an Interrupted Work Packet

## Outcome and User Scenario

An authorized repository operator can claim one ready `WRK-*` packet, survive an
interrupted agent process, resume the same packet safely, and submit an exact Git
candidate for independent verification without editing lifecycle metadata by
hand or repeating an approval stage.

The operator receives a short happy path for ordinary work and precise refusal
guidance for stale ownership, concurrent mutation, dirty candidates, invalid
state, or authority gaps. The slice establishes the minimum trustworthy
lifecycle on which later verification receipts, review lineage, operator views,
and harness evaluations can depend.

## Scope Boundaries

### In Scope

- One versioned, repository-local lifecycle for claim, lease renewal,
  interruption diagnosis, resume, submission, and safe release of a `WRK-*`
  packet.
- Atomic, compare-and-swap mutation across the public packet projection and its
  ignored local operational state, with no partially published successor.
- A bounded renewable lease that distinguishes an active owner from an expired
  or abandoned process without treating a conversation or branch name as proof
  of ownership.
- Exact base and candidate Git bindings for submission, including clean-worktree,
  ancestry, branch, packet-scope, and complete declared-input checks.
- Compatibility with the single CAP package binding, historical local-ledger
  records, packet `write_scope`, generated artifacts, claim fields, planning
  register, and serial dependency rules.
- Machine-readable results plus concise operator messages that name the failed
  invariant, observed evidence, and narrowest safe next action.
- Direct concurrency, interruption, stale-lease, malformed-state, path-boundary,
  stale-candidate, and happy-path tests on Windows, with portable semantics for
  other supported hosts.
- Reuse of small compatible Research Observatory primitives only where they fit
  this repository's `CAP-*`, `SLI-*`, `WRK-*`, and `DEC-*` lifecycle.

### Out of Scope

- A new approval stage or any inference of CAP, durable-decision, review, or
  external-action authority.
- Deterministic affected-check selection and reusable verification receipts,
  which remain CAP-0002 Candidate B.
- Durable independent finding and resubmission lineage, which remains Candidate C.
- Generated operator dashboards, retained CI reporting, packet-start acceptance
  closure, control maintenance, telemetry, or multi-turn harness evaluation.
- Concurrent execution of multiple work packets, distributed scheduling, remote
  workers, product queue semantics, or hosted coordination.
- Automatic commit, merge, push, publication, deployment, credential use,
  production mutation, destructive migration, or release approval.
- Changes to learner, financial, identity, provider, or other product-domain
  behavior.

## Canonical Context and Decisions

- [CAP-0002](../capabilities/CAP-0002-operate-ai-development-control-plane.md)
  defines the approved operator outcome, progressive-control constraint, and
  Candidate A.
- [Automated Development Planning](../README.md) defines the public lifecycle,
  one CAP planning-package approval, incremental lower-level planning, and
  deterministic packet execution.
- [Concurrent Automated Work](../concurrent-work.md) defines reservation,
  ownership, write-scope, claim, release, and finalization semantics.
- [Governed Planning Skill Suite](../skills/README.md) defines skill
  compatibility and the local-ledger boundary.
- [AI-Agent Development Standards](../../standards/ai-agent-development-standards.md)
  requires bounded ownership, deterministic validation, failure evidence, and
  no inferred authority.
- [Testing and Verification Standards](../../standards/testing-and-verification-standards.md)
  requires focused failure and denial evidence plus the aggregate readiness gate.
- [Change Impact Matrix](../../standards/change-impact-matrix.md) governs
  coordinated updates to planning automation, skills, tests, CI, context, and
  assurance evidence.
- [Decision Readiness](../../adr/decision-readiness.md) permits repository-local,
  provider-neutral tooling. Product queue, cloud platform, and remote execution
  decisions remain outside this slice.

No unresolved durable decision applies while the slice remains a local
development control with no remote scheduler, product queue, external effect, or
new approval authority.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Resume and submit an interrupted work packet | yes | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 13 |
| B. Select affected checks and issue verification receipts | no — requires a stable exact-candidate lifecycle from A | — | — | — | — | — | — | — | — |
| C. Record independent findings and corrected descendants | no — requires A and B submission evidence | — | — | — | — | — | — | — | — |
| D. Generate operator views and enforce matching CI policy | no — requires the lifecycle, evidence, and review projections from A through C | — | — | — | — | — | — | — | — |
| E. Add packet-start closure and bounded control maintenance | no — requires the stable operational policy established through D | — | — | — | — | — | — | — | — |
| F. Evaluate harness safety, friction, provenance, and confinement | no — requires the completed observable lifecycle through E | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the only currently eligible increment.

- **Observable value — 2:** an operator can recover real interrupted work and
  submit it without unsafe manual metadata repair.
- **End-to-end completeness — 2:** the slice crosses lifecycle policy, pure
  transition logic, local atomic persistence, Git provenance, command behavior,
  documentation, and executable qualification.
- **Decision readiness — 2:** the repository already fixes CAP authority,
  local-only records, write-scope ownership, and serial packet execution. No
  cloud, queue, tenancy, provider, or external-execution decision is selected.
- **Contract clarity — 1:** the existing claim and approval contracts are clear,
  but the lease, versioned operational state, compare-and-swap token, and exact
  submission envelope require executable schemas during packet planning.
- **Dependency independence — 2:** Candidate A depends only on accepted planning
  contracts and can be valuable before broader evidence or review automation.
- **Verification observability — 2:** races, process interruption, expired and
  active leases, stale commits, dirty worktrees, malformed state, and recovery
  can all be exercised deterministically.
- **Reversibility and bounded risk — 2:** the work is repository-local and can
  retain compatibility with the current tools; it performs no external or
  product-state mutation.

Candidates B through F are deferred rather than rejected. Selecting any of them
first would either depend on an unstable candidate identity or introduce a
horizontal subsystem without a trustworthy lifecycle consumer.

## Boundary Path

1. **Accepted authority and lifecycle meaning:** preserve the approved CAP
   package plus deterministic slice, packet, verification, and completion boundaries; preserve current packet
   dependencies, scope, and owner semantics.
2. **Executable control contracts:** define exact versioned shapes and invariants
   for operational state, leases, transition requests/results, Git bindings, and
   submission envelopes, including compatibility fixtures.
3. **Pure transition behavior:** implement deterministic legal-transition,
   compare-and-swap, lease, expiry, renewal, resume, release, and submission
   decisions without filesystem or command side effects.
4. **Local adapters:** bind atomic confined-file publication, cross-platform
   mutual exclusion, monotonic version checks, safe recovery, and read-only Git
   inspection behind narrow interfaces.
5. **Command composition:** expose concise claim, status, renew, resume, submit,
   and release operations while retaining compatible existing entry points or a
   documented migration path.
6. **Repository integration:** keep planning artifacts, register checks, governed
   skills, context guidance, CI policy, and aggregate readiness synchronized.
7. **Qualification:** prove happy, denial, concurrency, interruption, replay,
   malformed, stale, path-confined, and compatibility behavior.

No product domain, browser interface, database, network provider, worker, remote
scheduler, or deployment layer participates in this slice.

## Contracts, Data, and Provenance

- Public `CAP-*`, `SLI-*`, `WRK-*`, `DEC-*`, and register files remain tracked
  reviewable projections, not approval evidence or volatile lease storage.
- Approval and reviewer decisions remain only in the ignored local ledger. The
  new lifecycle may validate those decisions but may not rewrite or infer them.
- Operational state is versioned and confined under the ignored repository-local
  control root. Its contract must include a monotonic revision or digest used for
  compare-and-swap and must reject unknown incompatible versions.
- A lease identifies the packet, opaque claim identity, local owner label,
  acquisition/renewal/expiry times, base revision, and transition revision. It
  must not contain credentials, prompts, personal identifiers, or source payloads.
- A submission binds packet identity, claim identity, base revision, exact
  candidate commit, branch observation, declared scope/input closure, and
  evidence references. Candidate B will later define qualifying verification
  receipts; this slice must not imply that submission alone proves correctness.
- State publication uses canonical serialization and atomic replacement with
  explicit durability behavior. Lock or process failure cannot make a partial
  successor authoritative.
- Paths are repository-relative, normalized, confined, and revalidated at use;
  traversal, symlink/junction escape, absolute paths, and unexpected replacements
  fail closed.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Claim ready packet | One eligible packet receives one opaque claim and renewable lease bound to the current base revision and exact approved scope | Transition-kernel unit and command integration tests |
| Resume after interruption | A successor process proves the same live claim or safely recovers an expired claim, resumes without a new approval, and preserves prior history | Adapter/command integration tests |
| Concurrent claim or update | Exactly one competing writer succeeds; the loser observes a version conflict and receives a retry/status remediation without overwrite | Multi-process integration tests |
| Active-owner displacement | A non-owner cannot resume, release, or replace an unexpired lease without separately authorized recovery | Transition and command denial tests |
| Lease renewal and expiry | The owner renews within bounds; expired state is diagnosed deterministically and cannot be renewed as if still active | Time-controlled unit and integration tests |
| Interrupted publication | Failure before atomic publication leaves the prior valid state authoritative and recoverable; no partial successor is accepted | Filesystem fault-injection tests |
| Exact-candidate submission | A clean descendant candidate inside the packet scope is recorded with exact Git identity and declared inputs | Git-adapter and command integration tests |
| Dirty, stale, forked, or out-of-scope candidate | Submission is refused without lifecycle advancement and names the exact mismatch and remediation | Git-adapter denial tests |
| Malformed or incompatible local state | The command fails closed, preserves the bytes for diagnosis, and does not ask for routine hand editing | Schema/compatibility and command tests |
| Path escape or replacement | Absolute, traversal, symlink/junction, or replaced-path access is refused before reading or publishing state | Security-focused adapter tests |
| Minimal happy path | An ordinary authorized packet proceeds through claim, optional renew/resume, submit, and release/status with no repeated approval and no mandatory repository-wide test run | Command conformance scenario |

## Agent Work Packets

The slice is delivered through one bounded packet because the lifecycle kernel,
persistence, command composition, and qualification share one atomic contract
and can be accepted or rejected as one observable result.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0011 | Deliver lifecycle contracts, atomic state, leases, recovery, exact-candidate commands, documentation, and qualification | none | none | ready |

Later CAP-0002 slices consume the stable outputs of WRK-0011 and remain serial.
Anti-rigidity evidence is required alongside safety evidence: the common path
must not repeat approvals, require manual metadata repair, or run unrelated
repository-wide checks.

## Verification and Qualification

- Focused planning-tool unit tests for transition legality, compare-and-swap,
  lease bounds, renewal, expiry, recovery, and exact submission rules.
- Multi-process local integration tests for mutual exclusion, conflicting
  versions, process termination, atomic publication, and retry behavior.
- Git fixture tests covering clean descendants, dirty worktrees, stale bases,
  forked history, wrong branch observation, incomplete inputs, and scope escape.
- Compatibility fixtures for current unclaimed, active, verifying, and complete
  packet metadata plus current ignored approval records.
- `python dev-tools/planning/check_planning.py` and focused planning-tool tests.
- Governed skill validation, behavior tests, and prompt-level evaluations for
  interruption, resume, stale ownership, authority denial, and minimal progress.
- Documentation and CI-workflow checks plus
  `python dev-tools/agent/check_ready.py`.
- Windows qualification is required for the delivered local path. Portable lock
  and atomic-publication behavior must have executable coverage where supported;
  unavailable host qualification remains an explicit gap.

## Rollback and Migration

The delivery must recognize existing packets and claim metadata without silently
reinterpreting completed history. Migration is additive and versioned: preview
and validate current state, write a new confined successor atomically, and retain
enough prior bytes or derivation evidence for diagnosis and bounded rollback.

If migration or compatibility validation fails, the existing public artifact and
local record remain unchanged and the operator receives an exact repair path.
Rollback may return command routing to the prior compatible tool only while no
new-only transition has been accepted. Once new lifecycle evidence exists,
rollback must preserve it and use a forward compatibility repair rather than
discarding history.

## Stop Conditions

- A proposed implementation would introduce foreign planning vocabulary or
  replace this repository's `CAP-*`, `SLI-*`, `WRK-*`, or `DEC-*` meanings.
- The slice would add an approval stage, infer CAP or decision authority, track
  approval/reviewer records, or require new approval for ordinary interruption
  recovery.
- Safe coordination requires a remote service, cloud provider, product queue,
  durable external worker, credential, or other unresolved decision.
- Existing claim or approval records cannot be migrated without silent semantic
  change, evidence loss, or routine manual metadata editing.
- Locking, compare-and-swap, atomic publication, or exact Git binding cannot be
  demonstrated on the supported Windows path.
- Work expands into affected verification receipts, independent review lineage,
  dashboards, telemetry, multi-packet orchestration, or another CAP-0002 candidate.
- Canonical sources conflict, the active worktree has overlapping ownership, or
  the proposed write scope would include unrelated product implementation.

## Documentation Impact and Completion Evidence

Delivery is expected to update the planning guide, concurrent-work protocol,
planning automation README and tools, applicable governed skills and evaluations,
agent-readiness support, testing standards, context routing, CI workflow, and
architecture/verification assurance entries. Only sources made stale by the
implemented contracts should change.

Completion evidence must record the exact supported lifecycle and migration,
focused and aggregate commands with results, Windows concurrency/interruption
evidence, compatibility fixtures, known platform gaps, affected documentation,
and confirmation that no approval, external action, commit, push, deployment, or
product-state authority was added.

Delivered evidence is recorded in WRK-0011. The slice supplies a reusable core
with repository adapters, direct Windows multi-process exclusion, recoverable
state/projection publication, lease expiry and owner-protection scenarios,
exact-candidate and scope denials, and a two-command happy-path assertion that
does not add lower-level approval prompts or unrelated full-suite execution.
All focused lifecycle, planning-tool, planning-integrity, documentation, WRK,
SLI, and aggregate readiness checks passed. Cross-platform execution beyond
Windows remains unperformed; the implementation uses portable standard-library
semantics and records that qualification gap without weakening Windows evidence.

## Planning History

- 2026-10-15: Shaped from CAP-0002 Candidate A after deterministic eligibility
  and scoring. Candidates B through F remain deferred dependencies.
- 2026-10-15: SLI-0003 moved to `decision-blocked` while DEC-0006 resolves the
  CAP-only approval topology; no work packets were authored.
- 2026-10-15: Returned to `shaping` under the promoted single-CAP authority
  model. Detailed packet planning remains just in time and approval-free while
  it conforms to CAP-0002.
