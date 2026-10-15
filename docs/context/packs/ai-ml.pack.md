# Context Pack: AI and ML

## Use When

Work affects model providers, prompts, tutoring, retrieval, embeddings, adaptive models, datasets, features, experiments, evaluations, or promotion.

## Preserve

- Model access uses platform-owned ports.
- Model output is validated input, not authoritative protected-state mutation.
- Executions retain model/policy/template/source/version evidence.
- Essential workflows have deterministic policy and fallback.
- Evaluation distinguishes task quality, grounding, safety, learning outcomes, and operational cost.
- Adaptive-learning models follow ADR-0014's champion-challenger, calibration,
  abstention, leakage-control, shadow, deterministic-fallback, and separately
  reviewed online-experiment envelope.
- Automation-harness evaluations use deterministic fixtures and privacy-minimized
  operational metrics; they do not collect prompts/model output or become model
  promotion authority.

## Canonical Sources

- `docs/ai-ml/README.md`
- `docs/architecture/ai-ml/ai-ml-system-boundaries.md`
- `docs/architecture/learning/adaptive-pathway-architecture.md`
- `docs/adr/ADR-0014-governed-adaptive-learning-research-plane.md`

## Stop When

Data use, model authority, evaluation criteria, learner consent, provider egress, or promotion threshold is unresolved.

