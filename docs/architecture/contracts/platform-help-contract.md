# Platform Help Contract

- Status: accepted and implemented through the protected platform-help and contextual-help v1 APIs
- Canonical for: Guidance ownership, exact topic meaning, safe body/source
  boundaries, canonicalization, and deterministic literal search
- Executable shapes: `contracts/guidance/platform-help/v1/`, `contracts/guidance/contextual-help/v1/`, and `contracts/guidance/feature-guidance/v1/`
- Compatibility evidence: `contracts/compatibility/platform-help/v1/`
- Related docs: `contract-architecture.md`,
  `../modules/module-map.md`, `../../domain/glossary.md`,
  `../../risk-compliance/education-versus-financial-advice.md`

## Ownership and Authority

Guidance owns a safe product projection and its deterministic search policy.
It does not own or replace the meaning summarized from canonical product,
domain, architecture, contract, risk, or method sources. Each topic carries
safe source facts and a content fingerprint so consumers can identify that
authority without receiving a repository path or storage locator.

Platform help is explanatory content. It cannot authorize, grade, determine
eligibility, establish mastery, personalize financial conclusions, select a
provider, permit model execution, or cause an external or durable action.

## Exact Topic and Integrity

The immutable identity is `(topic_id, topic_version)`. Reads must name both;
there is no latest-version substitution. A topic has one closed kind, bounded
learner-readable title and summary, optional glossary term, reviewed keywords,
inert body nodes, applicability, publication facts, safe source facts, exact
related-topic references, and `topic_digest`.

Version `1.0.0` admits only the stable SemVer core form
`major.minor.patch`. Prerelease and build suffixes are outside this contract
version so exact-version ordering does not depend on partially implemented
SemVer rules.

The body union is limited to headings, paragraphs, ordered/unordered lists,
educational/limitation/warning notes, and exact same-corpus topic references.
Raw Markdown or HTML, scripts, styles, components, forms, embedded objects,
arbitrary protocols, external URLs, file paths, repository locators, prompts,
approval/reviewer data, learner identity, and provider payloads are invalid.

Canonical topic bytes are compact sorted-key UTF-8 JSON with only
`topic_digest` excluded. Admitted Unicode text is preserved exactly; no
implicit Unicode normalization changes its meaning. A corpus digest covers the
stable exact topic set including each topic digest. Duplicate identities, bad
digests, broken exact references, invalid chronology, unknown fields, or unsafe
nodes reject the whole corpus before any topic becomes visible.

## Search Meaning

Search accepts a bounded query, optional closed topic kind, bounded page size,
and optional opaque cursor. Query matching trims/collapses whitespace and uses
Unicode case folding. It never rewrites topic content.

Nonempty results rank by exact glossary/title match, title prefix,
title/glossary token coverage, then summary/keyword coverage. Stable topic ID
and semantic version keys break ties. Empty search browses the same
stable key order. The public projection includes applicability, approved
publication facts, and bounded canonical-source summaries for every result.
The cursor binds the normalized query, kind filter, corpus digest, position,
and prior exact result key; a deterministic integrity digest detects altered
encodings. It is an integrity check rather than an authorization boundary.
Altered, cross-query, cross-filter, or stale-corpus cursors fail closed.
Every successful search page serializes the required `next_cursor` member:
continued pages carry a nonempty opaque string and terminal pages carry an
explicit JSON `null`. Clients therefore receive the reviewed shape directly;
route-level omission of null fields cannot narrow the public contract. Other
optional search metadata remains absent when it has no value, matching the
executable schema rather than introducing undeclared nullable members.

Search uses no embeddings, models, learner history, popularity, hidden
synonyms, behavioral analytics, provider call, network retrieval, or generated
answer. A later search algorithm requires a new version or compatible reviewed
contract change, not an undocumented ranking adjustment.

## Compatibility and Clients

Additive optional fields may be introduced only when older consumers retain
the same safe meaning. Removing or reinterpreting a required field, admitted
node kind, digest input, exact identity, ranking tier, or cursor binding is a
breaking change and requires versioning.

Browser, command-line, service, and future headless-AI clients consume the same
protected public operations: deterministic search at
`GET /api/v1/guidance/platform-help` and exact-version read at
`GET /api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}`.
Both require the server-issued `guidance.platform_help.read` permission before
Guidance is invoked. They accept no learner or permission selector, preserve the
closed v1 documents, and map absent versions and invalid cursors to bounded
errors without corpus internals.

The immutable starter corpus is checked-in JSON admitted atomically at
composition time through the strict mapping and domain rules. Runtime code does
not parse canonical repository Markdown. OpenAPI and generated TypeScript types
reproduce the same headless contract. The browser cannot become a separate
ranking authority or bypass exact-version and authorization rules; browser
presentation consumes only those generated operations.

The implemented browser routes are `/help` and
`/help/topics/{topic_id}/versions/{topic_version}`. URL search admits only the
public bounded query, kind, page-size, and opaque-cursor fields. Closed browser
validation rejects malformed or extended documents before rendering; the
typed body union becomes inert semantic elements and exact same-guide links,
never raw markup or arbitrary URLs. Primary pages use learner-readable labels,
while publication and complete identity, digest, source-version, and source-
fingerprint facts remain keyboard-accessible under `Technical record`.

Live restart, offline/no-outbound observation, and browser/headless parity are
qualification concerns. They do not give the browser another content, search,
policy, or authorization path.

## Exact Contextual Help

The additive `contextual-help/v1` record maps one exact feature context and
version to an ordered set of exact approved topic identities. Guidance owns the
safe mapping only. The feature and each referenced canonical source retain
behavior and semantic authority.

A context carries a learner-readable feature label, applicability, exact Help
references with closed purposes and safe labels, publication facts, source
facts, and a canonical digest. It carries no route, URL, component, repository
path, learner identity, permission, prompt, provider/model payload, mutable
feature state, command, or external action. Exact reads never substitute a
different context or topic version.

The checked-in registry is admitted atomically after the platform-help corpus.
Every reference must resolve to an admitted exact topic. Duplicate identities,
unknown fields, stale source fingerprints, invalid chronology or digest, unsafe
text, and dangling topics reject the whole registry.

The protected exact read is
`GET /api/v1/guidance/contextual-help/{context_key}/versions/{context_version}`.
It uses the same server-issued Help-read permission as topic reads, authorizes
before registry access, accepts no query or body, and transports the exact
record without feature or host reinterpretation. The reviewed OpenAPI snapshot
and generated client expose the same operation to browser and headless callers.
The Web client closes the complete response before it shows any link. The
delivered lesson-publication, practice-result, Project artifact/result, and
AI-assistance surfaces request only their fixed context key and version, then
render the server-owned feature and reference labels in declared order. Missing,
denied, stale, malformed, or unavailable contextual Help leaves every owning
feature usable and reveals no partial context.

Each reference opens its exact same-origin topic identity. Browser return state
is separate from Guidance content and accepts only closed platform-guide,
lesson, practice, Project-detail, or AI-assistance destinations; cross-origin,
credentialed, hashed, extended, duplicate, or unrelated destinations fail
closed. Live browser/headless parity, restart, no-outbound, and read-only
containment qualification remain dependent SLI-0083 work.

## Exact Feature Guidance

The additive `feature-guidance/v1` contract owns reviewed explanatory meaning
for one exact public feature condition. A mapping identifies
`(surface_key, condition_key, mapping_version)` and one exact record version.
A record carries a closed `limited`, `unavailable`, or `degraded` status;
learner-readable reason and protected or uncertain outcome; closed
presentation actions; exact Help references; applicability; publication;
source facts; and a canonical digest.

Only an `open_help_topic` action has a destination, and it must match an exact
topic in the same atomically admitted Help corpus. Retry, reload, return,
download-inert-artifact, and Help actions describe presentation intent only.
They contain no arbitrary route, URL, command, credential, mutable request, or
promise. The owning feature remains authoritative for state, availability,
authorization, idempotency, retry, download, provider/model enablement, and
artifact execution.

The starter registry covers absent exact lesson content, an uncertain practice
write response, an unavailable Saved-learning source, an inert Project
artifact, and an AI-help preference that does not enable provider/model
execution. Exact lookup never substitutes another condition or version.
Duplicate identities, stale source facts, invalid chronology or digest,
unsafe text, arbitrary destinations, guarantee language, dangling records, or
dangling topics reject the complete registry before any record is visible.

The protected exact resolution is
`GET /api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}`.
It uses the existing server-issued Help-read permission, authorizes before
registry access, accepts no query or body, and returns the admitted mapping and
its exact reviewed record without feature or host reinterpretation. The
reviewed OpenAPI snapshot and generated client expose the same closed operation
to browser and headless callers. Missing or invalid exact identities return
bounded errors without registry facts or substitute guidance. The browser
validates both digests and exact mapping/record identity before it optionally
places the reviewed explanation beside the five owning public conditions.
Only exact same-application Help references receive a destination; every
retry, reload, return, or inert-file action remains unavailable unless the
owning feature supplies the matching safe handler. Denied, missing, malformed,
stale, or unavailable Guidance renders nothing and leaves the original feature
status and action usable. Final live browser/headless restart, no-outbound,
read-only-containment, and cleanup qualification remains SLI-0084 work; this
operation and its presentation have no persistence or execution effect.
