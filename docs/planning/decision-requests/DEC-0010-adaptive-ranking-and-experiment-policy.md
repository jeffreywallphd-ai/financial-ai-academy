---
id: DEC-0010
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["DEC-0009"]
decision_gates: []
decision_record: null
---

# Decision Request: Choose the Initial Adaptive Ranking and Experiment Policy

## Decision Needed

Choose the initial recommendation-ranking strategy and whether online learner
experiments are permitted, including consent, evaluation, fallback, and
promotion rules.

## Why Now

CAP-0010 can implement deterministic eligibility now, but ranking and
experimentation materially affect learner opportunity and data use. An implicit
engagement optimizer would violate the accepted adaptive boundary.

## Current Authority and Constraints

Prerequisites, permissions, exclusions, accessibility constraints, and course
requirements are deterministic gates. Model output is advisory. Evaluation must
measure learning and harm/exclusion, not engagement alone, and a rule baseline
must remain available.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Rule-based ranking without online experiments | Deterministic, explainable, low data risk, and easy to audit; establishes a stable baseline. | Less personalization and slower empirical improvement. | Recommendation policy/record, explanation UI, offline evaluation, fallback. | High; later strategies can be versioned against the baseline. |
| B. Validated model ranking with consented experiments | Can learn from richer signals and compare outcomes under controlled assignment. | Requires consent, experiment governance, fairness/harm monitoring, rollback, and model/provider decisions. | Model gateway, experiment assignment, recommendation record, monitoring, privacy and retention. | Medium; experiment effects and consent records remain durable. |

## Recommendation

Option A for the first delivered capability. Preserve the contracts needed to
evaluate Option B offline, but require a new promoted decision before online
assignment.

## Evidence Required

- Rule-baseline specification and explanation examples.
- Offline outcome and exclusion metrics with representative fixtures.
- If Option B remains viable, consent/privacy review, experiment threat model,
  model evaluation thresholds, monitoring, and rollback design.

## Required Authority

Product learning authority with learner-model, adaptation, privacy, AI/ML,
security, accessibility, and education-risk review.

## Decision Record and Promotion

Promote the selected strategy/experiment posture to an ADR and adaptive
architecture/evaluation guidance; update decision readiness.

## Dependent Planning Updates

Reconcile CAP-0010 and any later model-provider or learner-consent planning.

## Planning History

- 2026-10-15: Captured while shaping CAP-0010.

