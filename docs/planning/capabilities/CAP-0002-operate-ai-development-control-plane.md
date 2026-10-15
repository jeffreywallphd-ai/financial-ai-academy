---
id: CAP-0002
kind: capability
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0003", "SLI-0004", "SLI-0005", "SLI-0006", "SLI-0007", "SLI-0008"]
---

# Capability: Operate the AI-Development Control Plane

## Outcome

A repository operator can start, interrupt, resume, submit, review, and qualify
AI-assisted development work through one deterministic local control plane that
preserves authority and evidence without turning routine progress into a chain
of redundant gates.

## Users and Value

Repository maintainers and authorized development agents need trustworthy state
transitions, recovery, verification, and review while work moves across planning
artifacts and Git commits. Today the repository has useful local approval,
reservation, claim, validation, and readiness tools, but each tool owns only a
portion of the lifecycle and does not yet provide one interruption-safe,
commit-bound operational path.

Value is observable when ordinary low-risk work follows a short happy path,
interrupted work resumes without manual metadata repair, unsafe or stale
transitions are refused with an exact remediation, and higher-risk work receives
stronger verification without imposing that cost on every change.

## Scope

### In Scope

- A versioned local lifecycle for capability, slice, packet, evidence, review,
  and completion projections governed by one complete CAP planning-package
  approval and deterministic lower-level transitions.
- Atomic, compare-and-swap state changes with repository-wide coordination,
  bounded packet leases, renewal, interruption recovery, and truthful stale-owner
  handling.
- Exact-commit submission evidence, deterministic affected-check selection,
  append-only verification receipts, and refusal of dirty, stale, incomplete, or
  mismatched evidence.
- Independent technical review with durable findings, closure evidence,
  resubmission lineage, and escalation when repeated adverse rounds expose a
  process or specification defect.
- Generated operator status and diagnostics, machine-readable outputs, retained
  CI reports, and policy checks that explain both the invariant and the narrowest
  safe next action.
- Packet-start acceptance closure, bounded correction of completed work, and a
  constrained maintenance route for defects in the control plane itself.
- Harness evaluations and telemetry that measure safety and friction, including
  recovery success, refusal quality, redundant work, verification duration, and
  control-plane failure modes.
- Capability-based confinement for paths and commands executed by repository
  automation, plus provenance for control-plane and verification outputs.
- Selective reuse of compatible, tested GPLv3 components and contracts from the
  Research Observatory project when their semantics fit this repository; copied
  behavior must be reduced to this repository's lifecycle and covered locally.

### Out of Scope

- A distributed or hosted scheduler, managed-cloud control plane, product job
  queue, or a decision about product queue and delivery guarantees.
- Automatic push, merge, publication, deployment, credential use, production
  mutation, destructive migration, or release approval.
- Replacement of Git, the repository's canonical documentation hierarchy, or
  human authority over the CAP package, durable decisions, and external actions.
- A new mandatory approval stage, compulsory full-suite execution for every
  work packet, or a generalized recovery bureaucracy for ordinary implementation bugs.
- Product-domain workflow orchestration, learner state, financial calculations,
  AI tutoring, model-provider selection, or other application behavior.
- A required graphical dashboard before the command and machine-output contracts
  are stable and independently useful.

## Canonical Context

- [Documentation Governance](../../README.md)
- [Automated Development Planning](../README.md)
- [Concurrent Automated Work](../concurrent-work.md)
- [Governed Planning Skill Suite](../skills/README.md)
- [AI-Agent Development Standards](../../standards/ai-agent-development-standards.md)
- [Testing and Verification Standards](../../standards/testing-and-verification-standards.md)
- [Change Impact Matrix](../../standards/change-impact-matrix.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [Agent Readiness](../../../dev-tools/agent/README.md)
- [Planning Automation](../../../dev-tools/planning/README.md)

## Decision Gates and Constraints

- The first delivery remains repository-local, provider-neutral, and
  dependency-light. It may coordinate local Git and repository commands but may
  not silently choose cloud infrastructure, product queue semantics, or remote
  execution authority.
- The single CAP planning approval and local-only approval storage remain
  authoritative. Control-plane convenience cannot infer approval, expand the
  governed package, or move reviewer records into tracked files.
- Controls are progressive and risk-proportional. The default path must be the
  smallest path that preserves the affected invariant; broader checks and deeper
  reviews require an explicit impact reason.
- Hard stops are reserved for authority gaps, integrity failures, destructive or
  external effects, active ownership conflicts, stale exact-commit evidence, and
  genuinely unresolved durable decisions. Other failures must prefer bounded
  recovery, correction, or maintenance with preserved history.
- Every refusal must identify the failed invariant, evidence observed, and an
  exact safe remediation. A tool may not require an operator to edit lifecycle
  metadata manually as its normal recovery path.
- Existing planning artifacts and ignored local records require an explicit,
  tested compatibility and migration strategy. Silent reinterpretation is not
  permitted.
- Any later multi-host coordinator, durable remote worker, or external execution
  integration requires a separate decision review and explicit authorization.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0003 | An operator safely resumes and submits one previously claimed packet after an interrupted process, with atomic state, an expiring renewable lease, exact base/candidate commits, and no manual metadata edits. | First; establishes the lifecycle and persistence contracts consumed by every later slice. | Multi-host or remote execution, a different lifecycle authority model, or removal of exact-commit binding changes the CAP package. | shaping |
| SLI-0004 | An operator receives a deterministic affected-check plan and fresh verification receipt bound to the exact candidate, inputs, environment, and check results; stale or mismatched evidence is rejected. | After SLI-0003; consumes its candidate and state contracts. | Non-deterministic check selection, evidence not bound to the exact candidate, or mandatory full-suite execution changes the CAP package. | captured |
| SLI-0005 | An independent reviewer records findings and dispositions against the submitted commit, and a corrected descendant preserves prior rounds and closure evidence without reopening unrelated gates. | After SLI-0004; requires accepted verification receipts. | Reviewer authority to mutate delivery state without deterministic disposition rules or erased review lineage changes the CAP package. | captured |
| SLI-0006 | Local and CI entry points enforce the same policy, retain machine-readable reports, and generate a concise operator view of claims, leases, evidence, reviews, blockers, and next legal actions. | After SLI-0003 through SLI-0005 have stable contracts; may integrate them without redefining them. | A hosted scheduler, remote control service, or CI-only source of truth changes the CAP package. | captured |
| SLI-0007 | Packet-start acceptance closure and bounded control maintenance let ordinary work proceed through a short risk-selected path while control defects and completed-work corrections use narrow, history-preserving routes. | After SLI-0006 exposes the full local/CI flow and diagnostics. | A new human approval layer, silent history rewrite, or unbounded bypass changes the CAP package. | captured |
| SLI-0008 | Multi-turn harness evaluations, telemetry, provenance, and capability confinement detect regressions in safety, recovery, refusal quality, and workflow friction before control-plane changes are promoted. | Last; qualifies the behavior delivered by SLI-0003 through SLI-0007. | Collection of prompts, personal data, secrets, or source payloads; remote enforcement; or a new product security boundary changes the CAP package. | captured |

### Initial Slice Contracts

| Slice | Required inputs | Stable outputs for later slices | Initial qualification target |
| --- | --- | --- | --- |
| SLI-0003 | Current planning artifacts, local ledger compatibility, Git identity, packet scope, and existing claim fields | Versioned lifecycle schema; pure transition kernel; atomic state-store/lock/CAS contract; renewable lease and recovery rules; exact base/candidate submission envelope; command result/refusal schema | Unit state table plus Windows multi-process, interruption, atomic-publication, path-confinement, and Git candidate fixtures |
| SLI-0004 | SLI-0003 lifecycle state, exact submitted candidate, declared inputs, repository impact rules, and check catalog | Deterministic affected-check plan; risk profile; exact input/environment fingerprints; append-only verification receipt; freshness and replay rules | Golden affected-selection cases, exact-candidate receipt checks, stale/mismatch denial, partial/failure evidence, and narrow-versus-broad profile tests |
| SLI-0005 | Submitted candidate and accepted SLI-0004 verification receipt | Review assignment/identity boundary; versioned finding and disposition records; blocking/non-blocking policy; corrected-descendant and resubmission lineage | Independent-review fixtures, open-finding completion refusal, descendant validation, repeated-round escalation, and append-only lineage tests |
| SLI-0006 | Stable lifecycle, receipt, and review projections from SLI-0003 through SLI-0005 | Shared local/CI policy evaluator; retained machine report; concise status/next-action projection; consistent exit-code and diagnostic contract | Local/CI parity fixtures, report retention, refusal remediation, projection rebuild, and supported-host command qualification |
| SLI-0007 | End-to-end policy and diagnostics from SLI-0006 plus observed recovery/friction cases | Packet-start acceptance closure; risk-selected default path; bounded correction route; constrained control-maintenance mode with durable audit evidence | Short-happy-path scenarios, completed-work correction, maintenance entry/exit, anti-bypass, history preservation, and recovery-without-metadata-edit tests |
| SLI-0008 | Completed operational flow, refusal taxonomy, receipts, findings, maintenance route, and supported-host results | Multi-turn workflow evaluation corpus; safety/friction metrics; privacy-minimized telemetry; provenance envelope; path/command capability confinement; regression thresholds | End-to-end interruption/recovery/review runs, safety invariants, friction budgets, provenance checks, confinement denial, privacy tests, and aggregate readiness integration |

The initial dependency order is serial because each slice stabilizes contracts
consumed by the next. Just-in-time slice planning may identify parallel-safe
packets inside one slice, but it may not reorder slices across an unmet stable
output above without returning CAP-0002 to shaping.

Detailed acceptance scenarios, packet seams, exact write scopes, and verification
commands are refined immediately before each slice or packet starts. Those
refinements require no approval while they remain within the outcome,
dependencies, constraints, and material-change boundaries above. Local
orchestration beyond one agent/process remains outside this package.

## Capability Acceptance

The capability is acceptable when evidence demonstrates that:

- two concurrent writers cannot both acquire or advance the same packet, and a
  failed or interrupted write cannot leave a partially published lifecycle;
- an expired or abandoned lease can be diagnosed and recovered safely while an
  active owner cannot be displaced silently;
- submission, verification, and review bind the exact Git candidate and complete
  declared input set, rejecting dirty, stale, forked, missing, or replayed data;
- verification selection is deterministic and risk-linked, with narrow checks as
  the routine default and broader profiles required only by credible impact;
- adverse review findings remain append-only and traceable through corrected
  descendants, and completion cannot erase or bypass an open blocking finding;
- routine claim, verify, submit, and disposition operations have concise command
  paths and machine-readable output; every denial includes a bounded remediation;
- interruption, lock contention, expired lease, malformed state, path escape,
  command mismatch, failed verification, stale candidate, and repeated-review
  scenarios have direct automated evidence;
- a control-plane defect has a bounded maintenance path that preserves authority
  and history without spawning a new permanent approval layer;
- telemetry and harness evaluations can detect increases in redundant commands,
  repeated context loading, unnecessary broad checks, recovery failures, and
  ambiguous refusals; and
- the aggregate readiness gate plus focused control-plane tests reproduce the
  supported lifecycle on Windows and remain portable to other supported hosts.

## Risks and Non-Goals

- The largest risk is procedural overfitting: adding a new artifact, approval, or
  controller for every exceptional case can make the safe path slower than manual
  work. Prefer stable primitives, derived projections, and bounded repair routes.
- Porting the Research Observatory controller wholesale would import foreign
  execution and governance semantics. Reuse atomic persistence,
  exact-commit evidence, receipt, lease, affected-selection, and review patterns
  only after adapting them to this repository's simpler CAP/SLI/WRK lifecycle.
- A single large controller could become difficult to audit. Keep a small pure
  state-transition kernel separate from filesystem/Git adapters and CLI
  presentation, with focused conformance tests at each boundary.
- Telemetry must not capture personal identifiers, secrets, prompts, source
  payloads, or approval/reviewer records. Prefer event types, durations, hashes,
  counters, and locally retained diagnostics.
- Optimization metrics must not reward agents for skipping required evidence or
  pressure operators to accept unsafe work. Safety invariants remain constraints,
  not score components that can be traded away.
- The capability does not promise autonomous delivery, zero human review, remote
  scheduling, or compatibility with every external agent framework.

## Documentation Impact

Expected slice delivery updates include the planning guide, concurrent-work
protocol, planning tools and their README, governed skill instructions and
evaluations, agent-readiness runner, testing standards, CI workflow, assurance
maps and gaps, and the delivery-planning/testing context guidance. Executable
schemas, compatibility fixtures, operator examples, and migration guidance must
change with the behavior they govern. Approval and reviewer records remain only
in ignored local storage.

## Completion Evidence

All six manifest slices and their six dependency-ordered packets are complete.
The delivered reusable core separates lifecycle transitions, storage, affected
verification, review, policy, operator status, packet-start/correction/
maintenance operations, capabilities, provenance, telemetry, and harness
evaluation from Financial AI Academy planning, risk, status, and Git adapters.

The final cross-slice run on 2026-10-15 passed 51 focused unit/integration tests,
all 7 deterministic multi-turn scenarios, the read-only CI workflow contract,
planning integrity for 26 artifacts, documentation validation for 146 Markdown
files, 18 local readiness checks, 17 CI-profile readiness checks, and
`git diff --check`. Evidence includes concurrency/atomic recovery, exact Git and
scope denials, narrow affected-check selection, immutable review lineage,
local/CI policy parity, one-command status, semantic start closure, bounded
correction/maintenance, capability confinement, payload-free provenance,
anonymous non-blocking telemetry, and explicit anti-rigidity budgets.

Remaining qualifications are deliberately outside CAP-0002: repository-host
required-status configuration and artifact availability, remote/multi-host
control and telemetry, external actions, and product-domain/model evaluation.
No commit, push, merge, release, deployment, credential use, or production
mutation was performed.

## Planning History

- 2026-10-15: Capability shaped from the requested full automation control-plane
  modernization, with workflow friction and safe progress treated as explicit
  acceptance constraints.
- 2026-10-15: CAP-0002 moved to `decision-blocked` while DEC-0006 resolves the
  requested CAP-only approval topology before further decomposition.
- 2026-10-15: Returned to `shaping` after DEC-0006 promoted one complete CAP
  planning-package approval with just-in-time slice and packet refinement.
- 2026-10-15: All manifest slices passed deterministic completion and cumulative
  qualification; CAP-0002 moved to `complete` without a lower-level or final
  approval stage.
