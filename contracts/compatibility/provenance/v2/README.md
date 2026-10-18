# Cross-Domain Provenance v2 Compatibility Corpus

`approved/` contains exactly one deterministic synthetic document for every
closed v2 profile. The Project document mirrors the public snapshot identity
shape but is still a contract fixture; cumulative qualification replaces it
with the real public-only Project adapter. The other records do not claim an
implemented owner, provider,
model, dataset, calculation, recommendation, or administrative action.

`cases/denials.json` mutates approved documents to exercise structural and
semantic failures. `vectors/canonicalization.json` binds canonical catalog and
envelope digests, including source-order equivalence.
`vectors/v1-fingerprints.json` protects the pre-existing v1 schemas and approved
corpus from accidental reinterpretation during v2 work.

Fixture identifiers and source counts are examples, not product constants.
Conformance tests vary valid Unicode, time offsets, ordering, counts, versions,
and occurrences inside the contract bounds.

`backend/tests/contract/provenance_v2/synthetic_adapters.py` maps fresh copies
of these deterministic records through the production v2 mapper. The reusable
Audit conformance kit must return the same canonical digest as the independent
language-neutral runner for every profile. Reverse adapter order, partial
profile sets, varied valid values, one failing adapter, malformed output, and
duplicate declarations are tested without treating fixture count or order as
product behavior. These adapters are test-only and confer no owner maturity.

Slice qualification also runs empty and varied partial profile sets, reordered
inputs, and an isolated Project failure. Missing profiles are coverage evidence,
not implementation failures; the eight remaining synthetic adapters do not
claim a live provider, model, calculation, recommendation, or administrator.
