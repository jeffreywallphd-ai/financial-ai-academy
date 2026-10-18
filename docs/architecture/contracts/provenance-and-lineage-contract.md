# Provenance and Lineage Contract

- Status: accepted for the learning-lineage v1 contract core
- Canonical for: provider-neutral provenance references, bounded lineage graph
  meaning, canonicalization, and module ownership
- Executable shape: `contracts/provenance/v1/`
- Compatibility evidence: `contracts/compatibility/provenance/v1/`

## Purpose

The provenance envelope identifies one exact owned resource and its exact
source references without copying the resource payload. A bounded lineage view
correlates admitted envelopes into one deterministic directed graph for an
exact root. The contract describes evidence and integrity relationships; it
does not grant permission to read a referenced resource or make a grading,
mastery, causal, legal, compliance, or financial claim.

Version 1 admits two root kinds: an exact Content-owned published lesson and an
Assessment-owned knowledge-check completion. Content remains authoritative for
published packages and educational sources. Assessment remains authoritative
for definitions, events, and completion evidence. Audit owns append-oriented
integrity references and the later composed lineage read, not a copy of either
owner's business records.

## Closed Version 1 Meaning

Each reference contains a closed owner and resource kind, a stable resource ID,
the one applicable exact-identity field, a lowercase SHA-256 integrity digest,
an aware recorded time, and a validation status. Educational sources,
published lessons, and assessment definitions require `resource_version` and
forbid `occurrence`. Knowledge-check events, completion evidence, and Audit
references require `occurrence` and forbid `resource_version`. Recorded times
use an RFC 3339 offset with zero to six fractional digits; unsupported precision
is rejected instead of truncated. Owner-kind combinations are closed:

- Content: `educational_source`, `published_lesson`
- Assessment: `assessment_definition`, `knowledge_check_event`,
  `completion_evidence`
- Audit: `audit_reference`

Relations are closed to `published_from`, `defined_by`, `produced`, and
`recorded_as`. Every source reference is represented exactly once: a
`validated` source by one exact edge and an `incomplete` source by one matching
bounded incomplete link. Every edge and incomplete link must correlate back to
that declared source. A missing optional target is therefore retained as an
exact incomplete reference plus the bounded reason link, never as an invented
node or relationship.

The graph admits at most 64 nodes, 128 edges, 32 incomplete links, 20 sources
per envelope, and 12 edges from the root. IDs are bounded to 128 Unicode
characters, start with an alphanumeric character, and exclude whitespace,
Unicode control and format characters, paths, query or fragment syntax.
Language-neutral schemas provide the portable structural prefilter; Audit's
pure semantic validator is authoritative for the Unicode alphanumeric-first and
character-category rules. Versions are bounded ASCII tokens. Duplicate
node IDs, duplicate exact references, changed same-identity digests,
uncorrelated roots, dangling or disconnected nodes, unmatched edges, cycles,
unsafe owner-kind combinations, and exceeded bounds fail the whole view.

## Canonicalization and Compatibility

Canonical bytes are UTF-8 JSON with sorted object keys, compact separators,
unescaped Unicode, and UTC `Z` timestamps. Envelope sources are sorted by
relation and exact reference. View nodes are sorted by root distance then exact
reference and node ID; edges and incomplete links are sorted by their root
distance and closed identities. `view_digest` is lowercase SHA-256 over the
complete canonical view without the digest field itself.

Meaning changes require an additive contract version. Valid changes inside v1
include different bounded counts, Unicode IDs, input order, versions,
occurrences, timestamps, digests, and explicit incomplete links. Fixtures test
meaning and bounds rather than a fixed production graph size.

## Safety and Non-Authority

The contract contains no lesson body, assessment response, answer, feedback,
raw learner identity, provider payload, storage locator, secret, arbitrary URL,
path, executable content, or permission. Diagnostics expose a stable bounded
code and field reference, not rejected values or storage details. The pure
contract core performs no persistence, network, filesystem, provider, model,
identity, authorization, API, browser, or external action.

Owner adapters, Audit composition and persistence reads, protected HTTP,
generated clients, browser presentation, export, retention, and live
qualification are separate delivery seams. Their absence does not weaken the
frozen v1 contract or imply that those runtime capabilities already exist.
