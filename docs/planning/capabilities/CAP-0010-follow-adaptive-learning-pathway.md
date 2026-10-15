---
id: CAP-0010
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0004", "CAP-0005", "CAP-0009", "CAP-0018"]
decision_gates: ["DEC-0009", "DEC-0010"]
approval_model: cap-package-v1
slice_ids: ["SLI-0042", "SLI-0043", "SLI-0044", "SLI-0045"]
---

# Capability: Follow an Adaptive Learning Pathway

## Outcome

An individual learner can receive eligible next-activity recommendations based
on current evidence, goals, prerequisites, and deterministic policy, understand
why each option was offered, choose an alternative, and inspect the recorded
decision and later outcome.

## Users and Value

Learners benefit from guidance that reduces navigation effort without becoming
a mandate or obscuring prerequisites. Value is observable when identical inputs
and policy produce reproducible eligibility, recommendations remain explainable,
and the learner can choose any eligible path.

## Scope

### In Scope

- Adaptation-owned candidate assembly, deterministic eligibility and policy,
  versioned ranking strategy, recommendation record, explanation, expiration,
  alternatives, and outcome linkage.
- A rule-based safe baseline and the ranking/experiment posture accepted by
  DEC-0010.
- Learner goals/preferences and exact Curriculum/Learner-model versions as
  inputs, with explicit stale and degraded behavior.
- Accessible recommendations that preserve learner choice and explain why an
  option is eligible, ranked, constrained, or unavailable.

### Out of Scope

- Prerequisite bypass, automatic enrollment, coercive nudging, financial advice,
  or autonomous durable action.
- Model authority over eligibility, grades, mastery, permissions, or learner
  evidence.
- Cohort optimization, advertising, certification, or engagement-only success
  metrics.

## Canonical Context

- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0004](CAP-0004-discover-learning-opportunities.md)
- [CAP-0005](CAP-0005-navigate-competency-based-curriculum.md)
- [CAP-0009](CAP-0009-track-progress-and-competency-evidence.md)
- [CAP-0018](CAP-0018-set-learning-goals-and-preferences.md)

## Decision Gates and Constraints

- Curriculum and Learner model supply approved projections; Adaptation owns
  eligibility, ranking orchestration, deterministic policy, and recommendation
  records without mutating those sources.
- DEC-0009 establishes usable competency evidence. DEC-0010 establishes the
  initial ranking, experimentation, consent, evaluation, and fallback posture.
- Deterministic prerequisites, permissions, exclusions, and accessibility
  constraints always run before ranking and after any advisory model output.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0042 | A learner requests guidance and receives the complete deterministically eligible candidate set with exact prerequisite, goal, and evidence inputs. | First after dependencies and DEC-0009; establishes eligibility and denial contracts. | Model-controlled eligibility or hidden exclusions changes the CAP package. | captured |
| SLI-0043 | Eligible candidates are ordered by the versioned DEC-0010 strategy with a rule-based fallback, constraints, alternatives, and reproducible explanation data. | After SLI-0042 and DEC-0010. | Unvalidated ranking, engagement-only optimization, or no safe fallback changes the CAP package. | captured |
| SLI-0044 | The learner compares recommendations, chooses any eligible activity, and the recommendation and later outcome are retained without becoming source evidence. | After SLI-0043; integrates existing destinations. | Automatic enrollment, coercive UI, or mutation of curriculum/evidence changes the CAP package. | captured |
| SLI-0045 | The pathway is qualified for deterministic gates, ranking replay, stale inputs, consent/experiment isolation, fairness and harm measures, accessibility, and degraded operation. | Last; depends on SLI-0042 through SLI-0044. | Production experimentation outside DEC-0010 or authoritative AI changes the CAP package. | captured |

## Capability Acceptance

- Every recommendation identifies exact candidate, learner-state, curriculum,
  policy, and strategy versions and provides bounded reasons and alternatives.
- Ineligible items never reach ranking; stale or unauthorized inputs fail
  closed; model failure uses the accepted deterministic fallback.
- Learner choice is preserved, recommendation outcomes are recorded separately
  from source learning evidence, and evaluation includes learning and exclusion
  measures rather than engagement alone.
- The interface exposes equivalent information in accessible list and visual
  forms across supported themes and screen sizes.

- Every slice includes focused failure and anti-rigidity tests; adding an
  optional strategy or candidate source cannot become a prerequisite for the
  deterministic baseline.

## Risks and Non-Goals

Adaptive systems can entrench noisy projections or optimize engagement at the
expense of learning. This CAP does not permit hidden experimentation, automatic
advancement, prerequisite bypass, or model-owned durable decisions.

## Documentation Impact

Delivery will add recommendation and outcome contracts, Adaptation boundaries,
ranking/evaluation records, consent and fallback guidance, UI explanations,
architecture verification, and known-gap evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 7 with manifest SLI-0042 through
  SLI-0045. DEC-0009 and DEC-0010 must be promoted before CAP approval.

