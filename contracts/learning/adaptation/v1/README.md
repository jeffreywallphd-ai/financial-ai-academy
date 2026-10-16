# Adaptation Navigation State v1

This contract defines the deterministic rule baseline that runs before any
adaptive ranking. Curriculum remains authoritative for the exact immutable
graph and prerequisite direction; Learner model remains authoritative for
bounded completion; Adaptation owns the resulting eligibility policy.

`source-facts.schema.json` is a closed transport-neutral input envelope for an
exact graph and one source fact per graph activity. `navigation-state.schema.json`
is the complete result. Completion, eligibility, required/optional membership,
and exact-source availability are deliberately separate dimensions. Optional
does not mean eligible, incomplete, or unavailable.

Activity prerequisite edges point from the prerequisite source activity to the
dependent target. The v1 baseline uses activity-prerequisite relationships
only. It does not infer activity gates from competency relationships. Every
graph activity must have exactly one source fact; missing, duplicate, unknown,
or malformed facts fail the whole evaluation rather than creating a partial or
positive result.

The result preserves graph activity order. Reasons preserve policy order, and
repeated prerequisite reasons preserve graph relationship order. Presentation
hints do not change policy. Multiple entries, multiple prerequisites, absent or
partial hints, same-kind shared branches, unbranched activities, and varied
sibling order require no schema change.

`source_set_digest` is SHA-256 over UTF-8 JSON containing schema version, exact
curriculum identity/version/digest, and source facts normalized into graph
activity order. `projection_digest` is SHA-256 over the complete result with
only `projection_digest` removed. Both use sorted object keys, compact
separators, unescaped Unicode, and uppercase-`Z` UTC timestamps. Timestamps use
the same explicit seconds and at-most-six-fractional-digit profile as the
curriculum graph.

This contract contains no learner identity, answer, score interpretation,
mastery or competency label, recommendation, rank, model, provider payload,
engagement signal, approval record, or durable-state mutation.

Run the direct evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/adaptation_navigation
```

Application gateways, protected API behavior, generated clients, browser
presentation, persistence, and model-influenced adaptation require separate
qualification.
