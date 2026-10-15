---
name: approve-planned-work
description: Review and record the one CAP planning-package approval used for delivery, or an explicit durable DEC choice. Never create SLI-, WRK-, implementation-, or completion-level approvals; never self-approve or infer authority.
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

## Allowed Human Decisions

| Decision | Subject | Local ledger stage | What it permits |
| --- | --- | --- | --- |
| CAP planning package | `CAP-*` | `capability` | Delivery of the exact governed CAP package and enumerated slice manifest may proceed |
| Durable decision | `DEC-*` | `decision` | Canonical decision promotion may proceed |

Durable decisions remain separately explicit because a planning package cannot invent architecture, policy, legal, commercial, or product authority. They are not delivery-stage approvals.

## CAP Package Contract

Before requesting CAP approval, confirm the tracked CAP artifact contains:

- one bounded outcome, acceptance contract, scope, non-goals, constraints, and decision posture;
- a complete `slice_ids` manifest and coarse outcome/dependency row for every intended slice;
- no unresolved decision gate; and
- enough sequencing and stop boundaries to distinguish conforming incremental refinement from material CAP drift.

The recorder binds approval to a semantic digest of the governed CAP sections and exact slice manifest. Detailed SLI and WRK plans may change without approval when they remain within that binding. A changed CAP outcome, boundary, slice membership or ordering constraint, risk posture, or decision posture requires a renewed CAP approval.

One response may still resolve an explicitly enumerated homogeneous set of related `DEC-*` requests. Record one local-ledger entry per decision and never mix CAP approval with a decision bundle.

## Workflow

1. Identify one `CAP-*` package or one homogeneous closed `DEC-*` set.
2. For a CAP, present the complete slice manifest and governed package. For a decision set, freeze and present the exact members and choices. Run every applicable validator and review canonical authority, decision gates, boundaries, failure scenarios, checks, and documentation impact.
3. Complete [the approval checklist](assets/approval-checklist.md). Present failures before asking for a decision.
4. Obtain one explicit human response for the subject or complete bundle: `approved`, `changes-requested`, `rejected`, or unambiguous per-item outcomes. If the decision, local actor label, scope, authority, bundle membership, or per-item choice is unclear, record nothing.
5. For one subject, use `python scripts/manage_approval.py record ...`. For a decision bundle, use `python scripts/manage_approval.py record-bundle --subjects <DEC-ID> <DEC-ID> ... --stage decision --decision <decision> --actor-label <local-label> --decided-at <YYYY-MM-DD> --authority <local-reference> [--bundle-subject <CAP-ID>] --confirm-human-decision`. CAP recording automatically captures the current package digest and slice manifest.
6. Never create a selection, planning, implementation, or completion approval record. Those legacy stages remain readable only for historical compatibility.
7. Apply the deterministic public state transition below and update the planning register without adding an approval summary, identity, or decision evidence.
8. Run `python scripts/validate_approval.py <artifact> --stage <stage>` and the subject validator. Confirm `.local-codex/` is ignored and absent from Git status.
9. Report the recorded outcome, public state transition, checks, and next deterministic action without copying local authority metadata into tracked files.

## State Transitions

- Approved CAP package: move the capability to `ready` only when decision gates are resolved; included slices may then be refined and delivered deterministically.
- Approved decision: move to `verifying` until canonical promotion is recorded; then `complete`.
- Changes requested for a CAP package or decision: move to `shaping`.
- Any unresolved durable choice: use `decision-blocked` regardless of another approval.

## Stop Conditions

Stop when the agent would be approving its own work, the human response is not explicit, the CAP slice manifest is open-ended, readiness evidence is incomplete, decision gates are unresolved, authority is unknown, governed CAP content changed after review, or external authority would be inferred.
