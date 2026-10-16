# Learner-model Practice History Compatibility Corpus v1

The approved history fixes a rebuildable evidence-only projection for one
exact placed practice. Each ordered summary correlates server-issued event,
attempt, evidence, and submission identities to bounded scores, outcome,
item correctness, approved review-reference IDs, and canonical completion
time. The root retains exact package, definition, practice, and retry-policy
provenance.

The denial corpus prevents private answers, feedback, learner identity,
noncanonical time, contradictory scores/correctness, review references on
correct items, order gaps, and source-digest drift. Exact duplicate input is
idempotent; inconsistent identity reuse fails closed. Valid histories may be
empty and may contain 1 through 10 attempts without fixture-specific IDs,
timestamps, scores, or item counts.

```powershell
uv run --project backend pytest backend/tests/contract/learner_model_practice_history
```

This corpus does not implement Assessment replay, Learner-model persistence,
public APIs, browser comparison, mastery, adaptation, or AI authority.
