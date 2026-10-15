# AI and ML Governance

- Status: proposed
- Canonical for: AI/ML governance routing

AI/ML governance covers model and prompt identity, dataset/feature provenance, evaluation, promotion, monitoring, rollback, learner impact, cost, and provider data use.

Before implementing an AI/ML feature, define:

- owning product/domain outcome,
- model authority and deterministic policy envelope,
- input and output data classes,
- grounding or evidence requirements,
- model/provider/template versions,
- offline and online evaluation,
- promotion and rollback thresholds,
- fallback and degraded behavior,
- retention, redaction, consent, and cost controls.

Architecture authority is defined in `docs/architecture/ai-ml/ai-ml-system-boundaries.md`. Detailed model, prompt, dataset, evaluation, and experiment documents should be added only when their first real use case is approved.

## Accepted Adaptive-Learning Profile

[ADR-0014](../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
accepts a phased champion-challenger portfolio for competency inference, active
assessment, and eligible-action ranking. It requires calibrated uncertainty,
selective prediction and abstention, leakage-resistant offline evaluation,
shadow qualification, deterministic eligibility and publication, and permanent
evidence-only and rule fallbacks. A concrete dataset, provider, model promotion,
or online experiment still requires its applicable evidence and review.

