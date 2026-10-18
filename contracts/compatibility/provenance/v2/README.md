# Cross-Domain Provenance v2 Compatibility Corpus

`approved/` contains exactly one deterministic synthetic document for every
closed v2 profile. The Project document mirrors the public snapshot identity
shape but is still a contract fixture; the real Project adapter is delivered by
a later packet. The other records do not claim an implemented owner, provider,
model, dataset, calculation, recommendation, or administrative action.

`cases/denials.json` mutates approved documents to exercise structural and
semantic failures. `vectors/canonicalization.json` binds canonical catalog and
envelope digests, including source-order equivalence.
`vectors/v1-fingerprints.json` protects the pre-existing v1 schemas and approved
corpus from accidental reinterpretation during v2 work.

Fixture identifiers and source counts are examples, not product constants.
Conformance tests vary valid Unicode, time offsets, ordering, counts, versions,
and occurrences inside the contract bounds.
