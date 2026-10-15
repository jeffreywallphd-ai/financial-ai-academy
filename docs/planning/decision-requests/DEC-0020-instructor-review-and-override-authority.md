---
id: DEC-0020
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["DEC-0009", "DEC-0016"]
decision_gates: []
decision_record: ../../adr/ADR-0019-append-only-bounded-projection-overrides.md
---

# Decision Request: Choose Instructor Review and Override Authority

## Decision Needed

Choose which learner projections, if any, an authorized instructor may override
and define review states, reasons, evidence, dual control, notification,
expiration, reversal, and audit behavior without mutating source evidence.

## Why Now

CAP-0022 includes approved overrides, but current Assessment scoring and evidence
are deterministic and append-oriented. An undefined override could become a
hidden grade change or privilege bypass.

## Current Authority and Constraints

Assessment owns attempts/scores/evidence; Learner model owns derived projections;
source evidence is append-oriented; AI cannot grade or override; authorization
and audit are deterministic; credentials and high-stakes certification are out
of scope.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Feedback and revision requests only | Safest initial boundary; instructors cannot alter any score, completion, or competency projection. | Does not support exceptional correction of a derived state and narrows the catalog's override outcome. | Review/feedback records, learner notifications and audit. | High; bounded overrides can be added later. |
| B. Append-only bounded projection override | Permits correction or waiver of named derived completion/competency states while preserving source evidence and requiring reason, scope, evidence, authorization, notification, expiry/reversal and audit. | Higher privacy, consistency, abuse, conflict, and support burden; requires precise policy and UI. | Instructor action contract, Learner-model projection, authorization, audit, notification, history and export. | Medium-high; overrides are append-only and reversible by new action. |

## Recommendation

Option B limited to explicitly enumerated derived projection fields; never permit
attempt, response, deterministic score, Project snapshot, or source evidence
mutation. Require a stronger permission and learner-visible reason/history.

## Evidence Required

- Concrete correction/waiver use cases and excluded high-stakes cases.
- Authorization and abuse threat model, conflict/reversal state table, and audit review.
- Learner/instructor explanation and notification prototype.
- Privacy, fairness, appeal/support, retention, and export analysis.

## Required Authority

Product learning authority with Assessment/Learner-model domain, identity,
privacy/security, education-risk, accessibility, and support review.

## Decision Record and Promotion

[ADR-0019](../../adr/ADR-0019-append-only-bounded-projection-overrides.md)
selects the Option B recommendation: append-only bounded overrides of explicit
derived projection fields with two-person activation, learner-visible history,
expiration, and reversal. Source evidence and base projections remain immutable;
DEC-0016 still controls tenancy, membership, and exact permission mapping.

## Dependent Planning Updates

Reconcile CAP-0022 and any CAP-0009 projection policy affected by overrides.

## Planning History

- 2026-10-15: Captured while shaping CAP-0022.
- 2026-10-15: The Option B recommendation was promoted to ADR-0019 while the
  organization/authorization dependency remains deferred to DEC-0016.
