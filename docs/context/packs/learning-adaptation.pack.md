# Context Pack: Learning and Adaptation

## Use When

Work affects curriculum, competencies, assessments, learner evidence/state, eligibility, ranking, policy, or recommendations.

## Preserve

- Evidence is retained separately from derived learner state.
- Content owns versioned resources; Curriculum owns placement and prerequisites.
- Published lessons preserve ADR-0007 package identity, version, digest, provenance, and safe-rendering semantics.
- Curriculum owns prerequisites; assessment owns attempts/evidence.
- Learner model owns derived completion/progress; Audit retains trace references without duplicating business truth.
- Adaptation applies deterministic eligibility and policy around ranking.
- Recommendations retain strategy, input-version, reason, and outcome evidence.
- Rule-based fallback remains available for essential flows.

## Canonical Sources

- `docs/architecture/learning/adaptive-pathway-architecture.md`
- `docs/adr/ADR-0005-first-learning-loop-module-ownership.md`
- `docs/domain/README.md`
- `docs/architecture/modules/module-map.md`
- `docs/architecture/contracts/content-package-contract.md`

## Stop When

Model output would bypass eligibility, policy, authorization, grading rules, or consent/experiment decisions.
