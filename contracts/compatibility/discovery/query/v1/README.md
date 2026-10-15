# Discovery Query v1 Compatibility Corpus

This corpus fixes one tolerant raw request, its canonical applied query, and a
result page over the approved synthetic discovery-v1 lesson. Multi-record
vectors cover every closed sort, identity tie-breaking, OR-within and
AND-across filtering, prerequisite-only search, two-page continuity and replay,
and checksum-, query-, and generation-mismatch cursor outcomes. Normalization
and bounded raw-input denials are fixed separately.

Raw requests may contain repeated or noncanonical filter order and
normalizable text; the server canonicalizes them. The raw request remains
bounded before canonicalization, and the applied-query contract alone requires
canonical text plus sorted unique filters. No vector contains personal learner
data, provider payloads, ranking scores, eligibility meaning, or durable cursor
state.

The corpus proves portable request/result meaning. It does not by itself
qualify HTTP authorization, generated clients, browser controls, PostgreSQL, or
an external search provider.
