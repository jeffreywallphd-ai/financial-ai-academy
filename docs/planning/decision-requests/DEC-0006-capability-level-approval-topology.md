---
id: DEC-0006
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: docs/planning/README.md#authority-model
---

# Decision Request: Choose the Capability-Level Approval Topology

## Decision Needed

Choose whether a complete `CAP-*` planning package receives one approval before
delivery, or receives that initial approval plus a final capability-acceptance
approval after all included `SLI-*` evidence is complete.

The planning package is prepared at the beginning of the capability and includes
the capability outcome, boundaries, constraints, decisions, and the complete
enumerated and sequenced set of planned `SLI-*` increments. Both options remove
approval requests at `SLI-*` and `WRK-*` levels. The choice must be made by the
repository authority that owns the automated-development workflow.

## Why Now

[CAP-0002](../capabilities/CAP-0002-operate-ai-development-control-plane.md)
and [SLI-0003](../vertical-slices/SLI-0003-resume-submit-interrupted-work-packet.md)
are ready to decompose into work packets, but the current canonical planning
model requires separate capability, slice-selection, packet-planning,
implementation-activation, and slice-completion approvals. Continuing under
that model would directly contradict the requested policy that approvals be
sought only at the capability level.

Deferring this choice would either halt control-plane delivery or accumulate
more slice and packet approval machinery that the revised control plane is
expected to remove.

## Current Authority and Constraints

- [Automated Development Planning](../README.md), [Concurrent Automated
  Work](../concurrent-work.md), the [Governed Planning Skill Suite](../skills/README.md),
  root `AGENTS.md`, and [AI-Agent Development Standards](../../standards/ai-agent-development-standards.md)
  currently define six separate approval stages.
- Approval and reviewer evidence must remain only in the ignored local ledger;
  tracked artifacts may retain public lifecycle and evidence state but no human
  approval metadata.
- `SLI-*` and `WRK-*` artifacts remain required for decomposition, ownership,
  claims, dependencies, verification, review, and recoverable execution. Removing
  their approval gates does not remove their deterministic readiness checks.
- New or materially expanded CAP scope must never inherit authority silently.
  It requires a revised CAP and renewed CAP-level approval.
- External, destructive, credentialed, production, publication, commercial,
  and substantial-spend actions retain separate action authority regardless of
  planning approval topology.
- Independent technical review is evidence and disposition, not a planning
  approval. Blocking findings must still prevent completion.
- Agents may not self-approve, weaken acceptance, or close a CAP without the
  evidence required by the selected option.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| CAP-level approval topology | decision-required | A. Single CAP planning-package approval; B. CAP planning-package approval plus final CAP acceptance | A. Single CAP planning-package approval | DEC-0006 |

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Single CAP planning-package approval | Lowest human-interaction burden; all slices are visible before authority is granted; one approved package authorizes deterministic packet shaping, claims, implementation, verification, correction, and closure until the CAP is complete or materially revised | Capability closure becomes an automated evidence conclusion without a final human acceptance point; the initial package must keep each slice bounded and observable so a broad CAP cannot hide indefinite execution | Replace delivery approvals below the CAP and final acceptance with deterministic lifecycle controls; bind approval to the exact CAP revision and complete SLI manifest; permit WRK refinement only when it conforms to that approved package | Reversible only through a governed migration because existing local records and skill behavior must remain interpretable |
| B. CAP planning-package approval plus final CAP acceptance | Removes all SLI/WRK approval interruptions while retaining one human decision before work and one human acceptance after complete capability evidence; materially revised scope still returns to CAP planning | Adds one final interaction per CAP and conflicts with the stated requirement for a single approval | Use the same complete initial package and deterministic lower-level controls as Option A, then add one CAP completion decision | Reversible through the same versioned policy migration; existing lower-level records remain historical evidence |

The current six-stage model is not a viable option for this decision because it
conflicts with the explicit constraint that approvals be sought only at the CAP
level.

## Recommendation

Choose **Option A: single CAP planning-package approval**.

Verified facts: this repository already separates planning state from approval
evidence, has deterministic validators for `SLI-*` and `WRK-*`, and requires
independent verification before completion. Those mechanisms can support
autonomous delivery below the CAP without turning lower-level state changes into
human approvals.

Inference: binding the one approval to a complete CAP and SLI manifest preserves
meaningful human control over the intended outcome while eliminating the
repeated gates that created the reported barrier to progress. Deterministic
completion evidence can still present cumulative results, residual risks, and
deliberately omitted work without turning that report into another approval.

## Evidence Required

- Deterministic tests showing that SLI selection, WRK readiness, scoped claims,
  implementation, technical review, correction, and completion cannot exceed the
  exact approved CAP outcome, constraints, and exclusions.
- Compatibility fixtures proving that existing capability, selection, planning,
  implementation, and completion ledger records remain readable as historical
  evidence and are never rewritten or fabricated.
- Prompt evaluations showing that agents request one complete CAP
  planning-package approval only, while still stopping for material package
  drift, unresolved decisions, external/destructive authority, integrity
  failures, and blocking findings.
- Operator-flow evidence that ordinary SLI/WRK transitions proceed without human
  approval requests and provide actionable diagnostics when deterministic gates
  fail.

No legal, provider-term, privacy, financial, or external infrastructure review
is required for this repository-local process decision.

## Required Authority

The human repository owner or delegated planning-governance authority must choose
Option A or Option B. The local approval ledger is the only location for the
corresponding authority and review record; this tracked request records only the
durable policy after canonical promotion.

## Decision Record and Promotion

Option A is promoted in the [Authority Model](../README.md#authority-model).
The canonical contract uses one complete CAP planning-package approval, then
deterministic just-in-time slice and packet planning with renewed CAP approval
only for material package change. Root guidance, documentation governance,
concurrent-work rules, AI-agent standards, planning skills and scripts,
templates, routing evaluations, prompt evaluations, and decision readiness use
the same model.

## Dependent Planning Updates

- CAP-0002 and SLI-0003 remain `decision-blocked` until the choice is promoted.
- Existing local selection evidence for SLI-0003 remains historical and is not
  deleted, copied into tracked files, or treated as the future policy.
- The complete CAP-0002 slice set must be shaped before its replacement CAP
  planning-package approval is requested. Its work packets may be refined after
  approval only within the approved slice contracts.
- Future CAP-0002 slices must use the selected CAP-level topology and this
  repository's native planning vocabulary.

## Planning History

- 2026-10-15: Created when the requested CAP-only approval policy conflicted
  with the repository's canonical six-stage approval model. CAP-0002 and
  SLI-0003 moved to `decision-blocked` pending a CAP-level topology choice.
