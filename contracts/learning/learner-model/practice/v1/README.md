# Learner-model Practice History Contract v1

This contract defines a bounded, rebuildable view of immutable practice
attempts. Learner model owns the projection; Assessment remains authoritative
for retained attempts and completion events. The view is ordered by
`attempt_order` and correlates each summary to exact event, attempt, evidence,
submission, package, definition, practice, policy, and completion-time
provenance.

The history excludes learner identity, submitted answers, feedback text,
correct-answer declarations, private evaluator rules, drafts, mastery,
competency, suitability, advice, and adaptive recommendations. Item correctness
and approved review-reference IDs are bounded derived facts used only to help a
learner compare attempts and return to approved study material.

`source_digest` is lowercase SHA-256 over the compact, sorted-key UTF-8 JSON
array of canonical source records in attempt order. Exact duplicate source
events are idempotent. Reuse of an event, attempt, evidence, submission, or
attempt order for different meaning fails closed.

Run the dependency-light evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/learner_model_practice_history
```

This contract does not implement replay persistence, API exposure, browser
comparison, mastery, adaptation, or a separate AI mode.
