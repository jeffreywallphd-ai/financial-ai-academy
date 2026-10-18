---
id: WRK-0165
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0082
capability: CAP-0020
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/guidance", "backend/tests/contract/platform_help", "backend/tests/unit/guidance", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/platform-help/v1", "contracts/guidance", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0082-browse-search-approved-help.md", "docs/planning/work-packets/WRK-0165-freeze-platform-help-contracts.md"]
generated_artifacts: []
base_revision: a418a290ee28693d75659346e4401bc3994c32ab
claim_id: WRK-0165:ccd634b1-1c90-46ef-8414-b2e4d02ae74e
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T02:20:34Z
---

# Agent Work Packet: Freeze Platform Help Contracts

## Objective and Deliverable

Establish the additive `platform-help/v1` topic and search contracts, synthetic
compatibility evidence, and pure Guidance validation/search core that later API
and browser packets can compose without reinterpreting meaning.

The deliverable is a transport-neutral, immutable contract seam. It is not the
product corpus, a persistence adapter, an application service, an HTTP route,
generated client, or user interface.

## Required Context

Before implementation, read and follow `AGENTS.md`, `docs/README.md`, the
routed context sources, change-impact matrix, decision-readiness register,
CAP-0020, SLI-0082, contract and module architecture, risk and AI boundaries,
the nearest contract/module/test READMEs, and analogous versioned contract
implementations and consumers. Inspect affected contracts, implementation,
consumers, tests, and documentation before changing files.

The Required Startup has been performed and reported before this planning
change. Stop for a canonical conflict, stale CAP package, active write
collision, unresolved durable decision, or material scope drift.

## Decisions and Assumptions

- The approved CAP-0020 package and refined SLI-0082 remain current. No
  unresolved decision gate applies to a local read-only Guidance projection.
- Canonical product, domain, contract, risk, architecture, and method sources
  retain semantic authority. Guidance owns only the safe versioned projection
  and deterministic search policy.
- The new contract family has a semantic `guidance` owner rather than placing
  domain meaning in `contracts/common/`.
- Exact topic versions are immutable. Callers cannot request or infer `latest`.
- Search is deterministic literal matching over reviewed public fields. It
  does not use embeddings, models, learner history, popularity, analytics,
  provider calls, network retrieval, or hidden synonyms.
- Safe body content uses a closed tagged union. Raw markup, executable content,
  arbitrary URLs, file paths, repository locators, and private review data are
  invalid.
- Synthetic compatibility fixtures prove the contract. The reviewed starter
  product corpus is deferred to the dependent composition packet.
- Tests bind invariants and failure meaning, not fixed fixture counts, whole
  prose, incidental input order, harmless whitespace, or visual presentation.

## In Scope

- Add versioned schemas for an exact help topic, search request, and search
  page with closed topic kinds, publication and applicability facts,
  canonical-source summaries, exact related-topic references, and safe body
  nodes.
- Define compact sorted-key UTF-8 canonicalization and document digests without
  implicit Unicode rewriting.
- Add synthetic approved fixtures and denial cases for compatibility,
  confidentiality, canonicalization, safe content, and search meaning.
- Add pure immutable Guidance values, corpus validation, exact-version lookup,
  query normalization, filtering, ranking, cursor binding, and pagination.
- Reject duplicate exact keys, bad digests, unsafe nodes, broken exact
  references, invalid chronology, unknown fields, malformed cursors, and
  out-of-range requests atomically.
- Add focused contract and unit tests including Unicode, flexible valid topic
  counts and order, optional metadata, and additional safe topics.
- Reconcile direct contract, module, architecture, planning, and contribution
  documentation.

## Out of Scope

- Reviewed product help content, repository-document parsing, mutable
  authoring, editorial workflow, database schema, migration, corpus adapter,
  composition root, application service, authorization, HTTP API, OpenAPI,
  generated client, browser UI, live infrastructure, or deployment changes.
- AI-generated answers, semantic/vector search, recommendation,
  personalization, search telemetry, behavioral tracking, external content,
  arbitrary links, provider/model execution, or background jobs.
- Contextual feature links, troubleshooting flows, method/limitation expansion,
  managed-cloud operation, tenancy, recovery, licensing, legal/commercial
  policy, learner advice, grading, eligibility, or financial action.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Contracts | Existing versioning, canonicalization, and compatibility families | `contracts/guidance`, platform-help compatibility fixtures, direct indexes | Add the owned public data shapes and executable decisions |
| Guidance module | Analogous pure domain and contract adapters | New `modules/guidance` domain/ports/adapters only | Own validation, canonicalization, exact lookup, and search meaning |
| Tests | Existing contract and pure-domain suites | New platform-help contract and Guidance unit suites | Prove safe closed shapes and deterministic behavior |
| Architecture | Contract architecture and module map | Direct platform-help and Guidance documentation | Record ownership, dependency direction, and non-authority boundaries |
| Planning | SLI-0082 and register | WRK-0165, SLI-0082, register | Keep packet status and evidence synchronized |

No unlisted API, application, persistence, migration, generated-client, Web,
design-system, dependency, deployment, or product-content file may change.

## Contracts and Interfaces

`platform-help/v1` exposes three strict schemas: exact topic, search request,
and search page. Topic identity is `(topic_id, topic_version)`. A topic includes
a closed kind, title, summary, optional glossary term, bounded ordered keywords,
safe body nodes, applicability, publication facts, safe canonical-source facts,
exact related-topic references, and a canonical digest.

The body union is limited to headings, paragraphs, ordered or unordered lists,
educational/limitation/warning notes, and same-corpus exact topic references.
All text remains inert. Source facts use safe public source keys, titles, areas,
recorded versions, and content fingerprints; they never expose absolute paths,
Git metadata, accounts, approvals, reviewers, workstations, storage locators,
credentials, prompts, or learner data.

Search accepts bounded Unicode text, an optional closed topic-kind filter, a
bounded page size, and an optional opaque cursor. Normalization trims and
collapses whitespace and applies Unicode case folding for matching; canonical
document digests preserve admitted text exactly. Ranking is exact glossary/title
match, title prefix, title/glossary token coverage, summary/keyword coverage,
then stable topic ID and semantic version. Empty queries browse stable key
order. Cursors bind the normalized query, filter, corpus digest, and position;
cross-query or stale-corpus reuse fails closed.

The pure port accepts already parsed public documents and returns immutable
values. JSON parsing/projection is the only adapter in this packet. Neither the
domain nor port imports FastAPI, SQLAlchemy, filesystem, network, provider, or
Web code.

## Dependencies and Parallel Safety

The packet has no work-packet dependency and starts from the accepted
CAP-0020/SLI-0082 contracts. Its shared architecture, contract indexes, slice,
and register scope make it unsafe beside another writer on those paths.

Claim from a recorded base revision, acquire exact-file leases before edits,
and retain one owner through finalization. The dependent corpus/API packet must
wait for this packet to complete. Approval and reviewer records remain only in
ignored local control-plane storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Valid exact topic | Every allowed node and optional field is present | The topic is parsed and projected | One immutable value round-trips to the reviewed schema and exact digest | schema/contract/unit |
| Canonical digest | Key order and JSON whitespace vary | Documents are canonicalized | Equal admitted meaning produces the same digest without rewriting Unicode text | contract/unit |
| Safe content | Raw markup, active content, arbitrary URL, path, or unknown node is supplied | Admission runs | The complete topic is rejected before visibility | schema/unit |
| Corpus integrity | Duplicate keys, bad digests, broken relations, invalid chronology, or unknown fields exist | Corpus admission runs | The whole corpus is rejected atomically | unit/property |
| Exact lookup | A valid ID is paired with an absent version | Lookup runs | No different version is substituted | unit |
| Literal search | Case and harmless surrounding whitespace vary | Equivalent searches run | Results and query-bound cursor meaning remain deterministic | unit/property |
| Kind filter | One closed kind is selected | Search runs | Every result has that kind; clearing it restores normal browse | unit |
| Stable paging | Valid corpus insertion order changes | Search pages are requested | Ranking, tie order, and continuation remain stable | unit/property |
| Cursor containment | Query, filter, corpus, or cursor encoding is altered | Continuation is requested | Search fails closed without leaking private state | unit |
| Confidentiality | A source or topic attempts private review/runtime fields | Schema and parser run | The field is rejected | schema/contract |
| Flexible valid corpus | Counts, ordering, optional facts, Unicode, and safe body length vary in bounds | Admission and search run | Declared invariants hold without fixture-count assumptions | property/unit |
| No model/provider authority | The module imports and behavior are inspected | Architecture checks run | No model, provider, network, persistence, grading, eligibility, or financial-action seam exists | architecture/security |

## Verification Commands

Run the packet validator, planning-artifact checks, focused platform-help JSON
Schema compatibility tests, pure Guidance unit tests, Python compilation, and
architecture/import checks selected by the actual diff. Run documentation,
security, planning, whitespace, exact-candidate affected verification, one
independent technical review, and `python dev-tools/agent/check_ready.py`.

The expected focused command is:

`backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/platform_help backend/tests/unit/guidance`

Record only commands that pass. A harmless whitespace or prose correction may
be fixed in scope without reopening approval or a full review loop.

## Documentation and Evidence Update

Document the Guidance boundary, contract shapes and compatibility rules,
canonicalization and digest behavior, safe body/source constraints,
deterministic search/cursor rules, public confidentiality boundary, contribution
path, exact candidate and receipt, focused and aggregate checks, assumptions,
and remaining API/UI/corpus work. Keep packet, slice, and register status
synchronized. Do not place approval or reviewer records in tracked files.

## Stop Conditions

Stop for ambiguity in canonical source meaning; need for product help prose;
browser or headless contract divergence; serving repository Markdown or private
paths; arbitrary URLs or active content; mutable/user-authored help; semantic
search, model/provider execution, personalization, analytics, or external
retrieval; persistence/API/UI or dependency expansion; learner-specific advice,
grading, eligibility, or financial action; breaking public compatibility;
identity, tenancy, managed-cloud, recovery, licensing, legal, commercial, or
external-publication behavior; stale CAP authority; active write collision; or
material CAP-0020/SLI-0082 drift.

Do not stop for harmless whitespace, optional wording, fixture count/order,
nonfunctional styling, or another inconsequential issue. Fix it within bounded
scope or defer optional polish.

## Required Handoff

Report `CAP-0020.SLI-0082.WRK-0165`; exact candidate and receipt; contract and
safe-node shapes; canonicalization/digest and source-provenance rules;
deterministic search, cursor, exact-version, integrity, confidentiality,
Unicode, anti-rigidity, architecture, security, focused and aggregate checks;
changed files; documentation impact; assumptions; and remaining composition,
API, client, UI, and live gaps. Confirm that no product corpus, persistence,
API, browser, model/provider, external content, learner authority, or financial
behavior changed.

## Completion Evidence

- Exact candidate `f66efcf1f2666ded3e59661577d23064762e73b8`
  produced qualifying receipt
  `.local-codex/control-plane/receipts/WRK-0165/f66efcf1f2666ded3e59661577d23064762e73b8/20261018T022918Z-681dd4bc-127b-4261-898c-52ba94fb60f2.json`
  with digest
  `sha256:febff1b3a5ec517837401d512a79928f74b7e7556b222dede18fc5b1ea4294f9`.
- The executable v1 contract and pure Guidance core now expose exact immutable
  topics and deterministic search summaries with applicability, approved
  publication facts, bounded canonical-source facts, and no private source or
  runtime fields.
- Stable `major.minor.patch` identities, numeric version ordering, rank then
  exact-key tie ordering, corpus/query/filter/position/anchor-bound cursor
  integrity, safe Unicode shaping and emoji, unsafe-control rejection, exact
  date validation, canonical topic digests, and atomic corpus admission are
  covered by 43 focused contract and unit tests.
- Python compilation, architecture, security, documentation, planning,
  whitespace, all four selected exact-candidate checks, and all 29 aggregate
  readiness checks passed.
- No reviewed product corpus, persistence, API, OpenAPI, generated client,
  browser, model/provider execution, external content, learner-specific
  authority, or financial behavior changed. Those composition and delivery
  boundaries remain in the dependent SLI-0082 packets.

## Planning History

- 2026-10-18: Authored just in time as the first dependency seam of approved
  SLI-0082. The packet freezes a safe transport-neutral contract and pure
  deterministic core while deferring product content, composition, API, and UI
  to their enumerated dependent packets. No lower-level approval is required.
- 2026-10-18: Activated from recorded base `76afb52` after the implementation
  gate confirmed current CAP authority, refined slice membership, satisfied
  dependencies, and no overlapping active work.
- 2026-10-18: Rebased the claim to `a418a29` after the separately authorized
  roadmap-card correction was committed outside this packet. The platform-help
  scope and acceptance contract did not change; the new base keeps unrelated
  review-site files out of this packet's exact candidate.
- 2026-10-18: Completed the transport-neutral platform-help contract and pure
  deterministic Guidance core on corrected exact candidate `f66efcf`. Fresh
  receipt, focused contract/domain evidence, architecture, security,
  documentation, planning, whitespace, and aggregate readiness checks passed
  without expanding the approved CAP or introducing serving behavior.
