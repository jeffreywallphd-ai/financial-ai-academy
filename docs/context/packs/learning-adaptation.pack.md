# Context Pack: Learning and Adaptation

## Use When

Work affects curriculum, competencies, assessments, learner evidence/state, eligibility, ranking, policy, or recommendations.

## Preserve

- Evidence is retained separately from derived learner state.
- Content owns versioned resources; Curriculum owns placement and prerequisites.
- Published lessons preserve ADR-0007 package identity, version, digest, provenance, and safe-rendering semantics.
- Authoring follows ADR-0017: exact revision-bound human review and deterministic
  publication produce immutable native packages, while optional future external-
  standard adapters cannot bypass module ownership or native validation.
- Curriculum owns prerequisites; assessment owns attempts/evidence.
- Learner model owns derived completion/progress; Audit retains trace references without duplicating business truth.
- Project owns learning-initiated and independent project workspaces, inert-artifact manifests, and immutable snapshots under ADR-0012; Content/Curriculum retain learning definitions and requirements, while Assessment retains immutable submissions and source completion evidence by snapshot reference.
- Independent Project activity has no completion or mastery meaning until an authorized Assessment submission creates learning evidence.
- Applied-project artifacts remain inert untrusted evidence under ADR-0011; deterministic validation cannot claim code safety, result truth, mastery, certification, or investment performance.
- Adaptation applies deterministic eligibility and policy around ranking.
- Recommendations retain strategy, input-version, reason, and outcome evidence.
- Rule-based fallback remains available for essential flows.
- ADR-0014 separates versioned competency estimation from deterministic learner-
  facing publication, requires uncertainty and abstention, and phases research
  from rule baseline through offline/shadow qualification before any separately
  reviewed consented experiment.

## Canonical Sources

- `docs/architecture/learning/adaptive-pathway-architecture.md`
- `docs/adr/ADR-0014-governed-adaptive-learning-research-plane.md`
- `docs/adr/ADR-0005-first-learning-loop-module-ownership.md`
- `docs/adr/ADR-0011-inert-applied-project-artifacts.md`
- `docs/adr/ADR-0012-reusable-project-workspace.md`
- `docs/adr/ADR-0017-platform-native-human-reviewed-content-authoring.md`
- `docs/architecture/contracts/content-authoring-workflow-contract.md`
- `docs/domain/README.md`
- `docs/architecture/modules/module-map.md`
- `docs/architecture/contracts/content-package-contract.md`

## Stop When

Model output would bypass eligibility, policy, authorization, grading rules, or consent/experiment decisions.
