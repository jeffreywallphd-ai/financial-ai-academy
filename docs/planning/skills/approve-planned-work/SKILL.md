---
name: approve-planned-work
description: Review planning artifacts against deterministic readiness criteria and record an authorized human approve, changes-requested, or reject decision. Use for capability framing, durable decision, vertical-slice selection, work-packet planning, implementation activation, or completion acceptance gates; never self-approve or infer approval.
---

# Approve Planned Work

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions.
4. Read the planning guide/register, subject artifact, canonical sources, decision readiness, affected contracts, evidence, and nearest README.
5. Report completion of the gate. Stop on missing or conflicting authority.

This skill may record an approval decision but can never originate one. Require an explicit authorized human decision in the current task context.

## Six Approval Stages

| Stage | Subject | Metadata prefix | What it permits |
| --- | --- | --- | --- |
| Capability framing | `CAP-*` | `capability` | Slice candidates may be evaluated |
| Durable decision | `DEC-*` | `decision` | Canonical decision promotion may proceed |
| Slice selection | `SLI-*` | `selection` | Work packets may be authored |
| Plan readiness | `WRK-*` | `planning` | Packet is eligible for implementation approval |
| Implementation activation | `WRK-*` | `implementation` | Named work may start only with a current implementation instruction |
| Completion acceptance | `SLI-*` | `completion` | Verified slice may close |

An earlier approval never satisfies a later stage.

## Workflow

1. Identify exactly one subject and approval stage.
2. Run the subject skill's validator and review all applicable canonical authority, decision gates, dependencies, ownership scopes, generated artifacts, failure scenarios, checks, and documentation impact.
3. Complete [the approval checklist](assets/approval-checklist.md). Present failures before asking for a decision.
4. Obtain one explicit human decision: `approved`, `changes-requested`, or `rejected`. If the decision, approver identity/label, scope, or authority is unclear, do not edit.
5. Update the subject's stage-specific approval, approver, date, and Approval History in one change.
6. For implementation approval, also record `implementation_authority` as a task, conversation, roadmap, or other scoped authority reference. Confirm `write_scope`, generated artifacts, and parallel-safety claims are reviewable. Do not move or claim the packet as `active`; `implement-vertical-slice` performs that transition after a current implementation request.
7. Apply the deterministic state transition below and update the planning register.
8. Run `python scripts/validate_approval.py <artifact> --stage <stage>` and the subject validator.
9. Report the recorded decision, authority, state transition, checks, and what approval or action comes next.

## State Transitions

- Approved capability, selection, or planning gate: move to `ready` only when decision gates are resolved.
- Approved decision: move to `verifying` until canonical promotion is recorded; then `complete`.
- Approved implementation gate: remain `ready` until implementation actually starts.
- Approved completion gate: move the slice to `complete`.
- Changes requested for capability, decision, selection, or planning: move to `shaping`.
- Changes requested for completion: remain `verifying`.
- Rejected implementation: remain `ready` if the plan is still approved; do not start work.
- Any unresolved durable choice: use `decision-blocked` regardless of another approval.

## Stop Conditions

Stop when the agent would be approving its own work, the human decision is not explicit, readiness evidence is incomplete, decision gates are unresolved, approver authority is unknown, scope differs from the reviewed artifact, or implementation/external authority would be inferred.
