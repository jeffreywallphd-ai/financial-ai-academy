# Curriculum Practice Review Compatibility Corpus v1

This synthetic corpus fixes Curriculum-owned exact mapping from an approved
practice review resource to a safe lesson placement. `available.json` carries
only exact resource and package provenance plus stable placement/section IDs.
`unavailable.json` preserves the requested resource while reporting a bounded
reason; consumers must keep the underlying Assessment result and history
usable.

The dependency-light runner validates closed shapes and the deterministic
selection rule: review references attached to incorrect items are deduplicated
in the definition's declaration order. Missing mappings do not cause ranking,
fallback, or substitution. Raw URLs, HTML, filesystem paths, client-selected
routes, provider payloads, and credentials are rejected.

```powershell
uv run --project backend pytest backend/tests/contract/curriculum_practice_review
```

This corpus does not implement Curriculum persistence, public APIs, browser
navigation, adaptive recommendations, or Content retrieval.
