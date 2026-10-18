# Platform Help Contract

- Status: accepted for the platform-help v1 projection and pure search core
- Canonical for: Guidance ownership, exact topic meaning, safe body/source
  boundaries, canonicalization, and deterministic literal search
- Executable shapes: `contracts/guidance/platform-help/v1/`
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

Search uses no embeddings, models, learner history, popularity, hidden
synonyms, behavioral analytics, provider call, network retrieval, or generated
answer. A later search algorithm requires a new version or compatible reviewed
contract change, not an undocumented ranking adjustment.

## Compatibility and Clients

Additive optional fields may be introduced only when older consumers retain
the same safe meaning. Removing or reinterpreting a required field, admitted
node kind, digest input, exact identity, ranking tier, or cursor binding is a
breaking change and requires versioning.

Browser, command-line, service, and future headless-AI clients must consume the
same protected public API once it exists. The browser cannot become a separate
ranking authority or bypass exact-version and authorization rules. The current
seam qualifies contract and pure domain behavior only; reviewed product corpus,
API, generated client, browser, deployment, authorization, and live operation
remain subsequent SLI-0082 packets.
