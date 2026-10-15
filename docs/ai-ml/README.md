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

## Accepted Financial Experiment Execution Profile

[ADR-0016](../adr/ADR-0016-learner-managed-experiment-execution.md)
keeps financial AI/ML code and runs learner-managed. The platform defines
versioned plans, exports integrity-bound run bundles, validates normalized
imported result bundles, and labels them learner-supplied rather than
independently reproduced. Provider-neutral run/result semantics preserve a
future optional analytics interface or sandbox adapter, but no executable
adapter is currently authorized.

