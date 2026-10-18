# Provenance and Lineage Contract

- Status: accepted for the learning-lineage v1 core and cross-domain v2
  owner-reference contract
- Canonical for: provider-neutral provenance references, bounded lineage graph
  meaning, canonicalization, and module ownership
- Executable shapes: `contracts/provenance/v1/` and `contracts/provenance/v2/`
- Compatibility evidence: `contracts/compatibility/provenance/v1/` and
  `contracts/compatibility/provenance/v2/`

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

## Closed Cross-Domain Version 2 References

Version 2 is additive and currently defines owner-issued references, not a new
lineage request or graph. Its executable catalog closes meaning to nine
profiles: Project snapshot; Market-data observation; Portfolio financial and
simulation results; AI-orchestration dataset snapshot, model version, and model
execution; Adaptation recommendation record; and Audit administrative action.
Project is the first implemented real-owner adapter. Other approved fixtures
are synthetic and do not claim a provider, dataset, model, run, calculation,
recommendation, administrator, or product record.

Each profile has one allowed owner/resource pair and closed exact identity
variants. Financial results explicitly discriminate an account from an analysis;
all other profiles have one variant. Market-observation resource IDs are derived
from the canonical digest of the exact identity tuple and cannot vary as an
independent identity field.
The common reference retains stable resource identity, lowercase SHA-256
integrity, aware recorded time, validation status, producer, origin label, and
zero to twenty typed sources. Labels are closed to observed, calculated,
simulated, predicted, generated, and administrative meaning and are constrained
per profile. They do not establish truth, quality, mastery, suitability,
permission, compliance, or authority. Relations are closed, descriptive, and
confer no causal or execution meaning.

V2 canonicalization projects aware times to UTC `Z`, sorts sources by relation
and canonical reference, and uses compact sorted-key UTF-8 JSON with unescaped
Unicode. The corpus fingerprints every v1 schema and approved document, covers
every v2 profile once, and rejects mismatched owner/profile/label/identity,
unsafe or private fields, ambiguous identity, conflicting duplicates, corpus
profile gaps or extras, and exceeded bounds. It adds no business payload,
actor/learner/tenant identity,
provider payload, market value, model input/output, Project content, storage,
secret, permission, external action, or financial advice.

Audit's separate pure v2 value and mapping core now implements the frozen
owner-reference meaning. It uses immutable profile-specific identities,
normalizes equivalent time and source order, matches the language-neutral
runner's canonical envelope digests, and contains failures to one validation
call without a dynamic registry. This is contract implementation only: it does
not make a future owner, adapter, graph, retained record, provider/model action,
authorization decision, public operation, or user history interface available.

Audit also owns a pure conformance port and application service for incremental
owner adoption. One adapter declares one exact profile and issues one typed
envelope. The service returns immutable profile-ordered cases, canonical digest
evidence on success, bounded code/reference evidence on failure, exact missing-
profile coverage, and a complete flag only when every closed profile validates
once. It retains no envelope, exception, registry, or result and performs no
I/O. Test-only synthetic adapters prove all catalog profiles and varied valid
values against the independent runner; they are not production owners.

The real Project adapter depends only on Project's public exact-snapshot
operation. It binds the existing learner/project/snapshot request for the read,
correlates the returned immutable identity, and issues only project and snapshot
IDs, project/workspace revisions, snapshot digest, close time, and fixed
producer facts. It supports learning-started and independent Projects because
the public snapshot shape is origin-neutral. Learner identity, origin payload,
workspace content, resource details, paths, URLs, bytes, and storage coordinates
are neither copied nor retained. Project failures and mismatches collapse to
bounded conformance results.

Cumulative qualification replaces the synthetic Project fixture with the real
adapter while leaving the other eight forecasts explicitly test-only. The
mixed complete suite validates one case per frozen profile; empty and varied
partial suites remain valid incremental adoption states, report exact missing
coverage, and produce the same ordered cases under input reordering. One Project
failure remains local and cannot disable unrelated profiles. No dynamic runtime
registry or all-or-nothing owner count is introduced.

## Accountable History Version 1 Contract

The additive `accountable-history/v1` family defines a purpose-limited read
model over one already authorized learning-lineage root. It leaves provenance
v1/v2 meaning and fingerprints unchanged. A request contains only the same
closed lesson or knowledge-check completion selector; server identity,
permission, and operation purpose remain outside caller control.

An inspection binds `learner_review`; a portable evidence operation binds
`portable_evidence`. Both use one disclosed-content document containing ordered
history entries, existing transformation relations, explicit gaps, closed safe
diagnostics, reviewed plain-English display fields, bounded exact technical
facts, redaction category counts, the source lineage digest, and a separate
disclosed-content digest. Entry roles and owner/kind combinations remain closed
to the existing Content, Assessment, and Audit learning chain.

Diagnostics distinguish missing reference, unavailable owner, unsupported
version, integrity mismatch, invalid relation, identity conflict, and redacted
detail. They describe validation results and do not claim malicious activity,
compliance failure, or tamper-proof storage. Diagnostic text cannot expose the
rejected value, payload, path, stack trace, credential, or internal exception.
Redaction summaries expose only one closed category and count.

Canonical documents normalize source times to UTC `Z`, sort semantic arrays,
and use compact sorted-key UTF-8 JSON with unescaped Unicode. The history digest
binds the complete disclosed document without its own digest field. The export
wrapper uses that same digest and derives export time from the latest disclosed
source time; it contains no file path, storage locator, retained download, or
runtime-clock claim.

The frozen contract now has a shared production composer, protected inspection
and export operations, reviewed OpenAPI, and a generated client. It still
contains no browser view, export retention, migration, provider/model action,
tenant or administrator policy, legal conclusion, or history mutation.

## Safety and Non-Authority

The contract contains no lesson body, assessment response, answer, feedback,
raw learner identity, provider payload, storage locator, secret, arbitrary URL,
path, executable content, or permission. Diagnostics expose a stable bounded
code and field reference, not rejected values or storage details. The pure
contract core performs no persistence, network, filesystem, provider, model,
identity, authorization, API, browser, or external action.

The shared Python core implements the first owner-adapter and composition seam.
Content issues exact lesson/source envelopes through its public operation;
Assessment completion events enter through its public replay surface; and
Audit reconciles then reads only its append-only assessment-completion record.
One exact completion occurrence correlates evidence, event, retained Audit
reference, definition, lesson, and zero-to-many educational sources without
copying body, answer, feedback, learner, locator, or provider payloads.

The protected `POST /api/v1/audit/learning-lineage` operation exposes that same
core to generated and direct/headless clients. Its closed union selects one
exact lesson or completion occurrence, completion learner identity comes only
from the server session, and the host requires both Audit-lineage and lesson-
read permissions before invoking Audit. The response is the canonical bounded
view and cannot grant authorization or disclose owner payloads. Browser
presentation, export, and retention policy remain separate delivery seams. The
disposable local host now directly qualifies both roots through the generated
client and ordinary HTTP, exact replay across a normal restart, confidential
denials, and steady-state database/file containment after deterministic Audit
reconciliation; it does not claim public hosting or managed-cloud behavior.

The protected `POST /api/v1/audit/accountable-history` and
`POST /api/v1/audit/accountable-history/export` operations reuse those exact
roots. Inspection and export require separate Audit permissions while both
preserve lesson-read authority. Completion learner identity and operation
purpose are server-bound. The application obtains the accepted lineage through
Audit public methods and delegates all disclosed meaning, redaction, diagnostics,
ordering, and digests to the pure core. The export is an ephemeral response and
does not introduce a retained record, path, signing, encryption, or recovery
policy. The learner browser consumes the same generated operations and the
disposable local topology now directly qualifies generated-client and ordinary
HTTP equality for both roots and purposes, exact replay across a normal
restart, confidential denial, and accountable-history-only non-Identity
database and bounded-file containment. A selector-only public phase may refresh
the existing rebuildable Learner-model projection. The runner freezes its
containment baseline after that phase and before the first history or export
call; no accountable-history operation creates a retained record.

Cumulative qualification keeps v1 and v2 source limits aligned and keeps the
history entry, transformation, and missing-link limits no wider than their v1
lineage node, edge, and incomplete-link inputs. Every public object schema stays
closed. The portable wrapper remains exactly schema version, media type,
filename stem, export time, document digest, and document; retention class,
expiry, deletion, legal hold, tenant, provider payload, and storage location are
not provenance or export identity. The shared provenance/history core also
remains free of host, database, cloud, network, and provider-framework imports.
This proves a policy-neutral adapter seam and local/shared-core behavior, not a
retention duration, legal policy, immutable store, tenant policy, recovery
posture, or managed-cloud deployment.
