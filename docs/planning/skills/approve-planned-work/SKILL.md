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

This skill may record an approval decision but can never originate one. Require an explicit authorized human decision in the current task context. Store every decision and reviewer statement only in the ignored `.local-codex/approvals/ledger.json`; never copy approval identity, date, decision, authority, scope, reviewer identity, reviewer status, or approval history into a tracked artifact or register.

## Six Approval Stages

| Stage | Subject | Local ledger stage | What it permits |
| --- | --- | --- | --- |
| Capability framing | `CAP-*` | `capability` | Slice candidates may be evaluated |
| Durable decision | `DEC-*` | `decision` | Canonical decision promotion may proceed |
| Slice selection | `SLI-*` | `selection` | Work packets may be authored |
| Plan readiness | `WRK-*` | `planning` | Packet is eligible for implementation approval |
| Implementation activation | `WRK-*` | `implementation` | Named work may start only with a current implementation instruction |
| Completion acceptance | `SLI-*` | `completion` | Verified slice may close |

An earlier approval never satisfies a later stage.

## Consolidated Decision Points

Keep the six stages separate, but reduce human approval interactions for homogeneous closed sets:

- one decision response may resolve an explicitly enumerated set of related `DEC-*` requests;
- one planning response may approve the complete, enumerated `WRK-*` packet set for one `SLI-*`;
- one implementation response may activate that same frozen packet set, with each record bound to the packet's exact current `write_scope`.

Record one local-ledger entry per artifact even when one response covers the bundle. Every bundle must identify all members and one stage. A response may state item-specific choices or exceptions; record only unambiguous outcomes. Never mix stages, silently add later artifacts, or treat a changed packet or scope as covered. A new member or material revision requires a new decision for the affected bundle.

## Workflow

1. Identify one subject or one homogeneous closed bundle and exactly one approval stage.
2. For a bundle, freeze and present the exact member list. Run every subject validator and review all applicable canonical authority, options, recommendations, decision gates, dependencies, ownership scopes, generated artifacts, failure scenarios, checks, and documentation impact.
3. Complete [the approval checklist](assets/approval-checklist.md). Present failures before asking for a decision.
4. Obtain one explicit human response for the subject or complete bundle: `approved`, `changes-requested`, `rejected`, or unambiguous per-item outcomes. If the decision, local actor label, scope, authority, bundle membership, or per-item choice is unclear, record nothing.
5. For one subject, use `python scripts/manage_approval.py record ...`. For a bundle, use `python scripts/manage_approval.py record-bundle --subjects <ID> <ID> ... --stage <decision|planning|implementation> --decision <decision> --actor-label <local-label> --decided-at <YYYY-MM-DD> --authority <local-reference> [--bundle-subject <CAP-or-SLI-ID>] --confirm-human-decision`. Implementation bundles require `--bundle-subject <SLI-ID> --scope-from-artifacts`. The command validates every member before atomically appending per-artifact records. Use separate single records only to preserve explicit item-specific exceptions from the same human response.
6. Confirm `write_scope`, generated artifacts, and parallel-safety claims are reviewable. Do not move or claim a packet as `active`; `implement-vertical-slice` performs that transition after a current implementation request.
7. Apply the deterministic public state transition below and update the planning register without adding an approval summary, identity, or decision evidence.
8. Run `python scripts/validate_approval.py <artifact> --stage <stage>` and the subject validator. Confirm `.local-codex/` is ignored and absent from Git status.
9. Report bundle membership, recorded outcomes, authority, state transitions, checks, and what approval or action comes next.

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

Stop when the agent would be approving its own work, the human response is not explicit, bundle membership is open-ended, readiness evidence is incomplete, decision gates are unresolved, approver authority is unknown, scope differs from the reviewed artifact, a member changed after review, or implementation/external authority would be inferred.
