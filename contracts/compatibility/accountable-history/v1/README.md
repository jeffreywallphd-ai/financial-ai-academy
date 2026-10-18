# Accountable History v1 Compatibility

The approved corpus fixes the two closed learning roots, both operation-bound
purposes, plain-English display fields, exact technical facts, incomplete-link
and safe-diagnostic behavior, redaction summaries, canonical disclosed-content
digests, and the ephemeral portable export wrapper.

The denial corpus prevents callers from selecting a purpose, learner, tenant,
role, policy, field list, or redaction behavior and rejects protected payloads,
active content, raw errors, paths, URLs, secrets, unknown vocabulary, changed
identity, broken correlation, digest mismatch, duplicate semantics, and exceeded
bounds. Valid fixtures vary count, order, Unicode, missing-link, diagnostic, and
redaction combinations; production code must not assume one fixture size.

`vectors/provenance-fingerprints.json` binds the existing provenance v1/v2
schemas and approved records so this additive family cannot reinterpret them.
