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

