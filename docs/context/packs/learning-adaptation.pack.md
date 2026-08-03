# Context Pack: Learning and Adaptation

## Use When

Work affects curriculum, competencies, assessments, learner evidence/state, eligibility, ranking, policy, or recommendations.

## Preserve

- Evidence is retained separately from derived learner state.
- Curriculum owns prerequisites; assessment owns attempts/evidence.
- Adaptation applies deterministic eligibility and policy around ranking.
- Recommendations retain strategy, input-version, reason, and outcome evidence.
- Rule-based fallback remains available for essential flows.

## Canonical Sources

- `docs/architecture/learning/adaptive-pathway-architecture.md`
- `docs/domain/README.md`
- `docs/architecture/modules/module-map.md`

## Stop When

Model output would bypass eligibility, policy, authorization, grading rules, or consent/experiment decisions.

