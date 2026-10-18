---
id: SLI-0082
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: CAP-0020
depends_on: []
decision_gates: []
---

# Vertical Slice: Browse and Search Approved Help

## Outcome and User Scenario

An authorized learner can browse and search a versioned collection of approved
help and glossary topics, open one exact topic version, understand what it
applies to and when it was updated, and follow related concepts without leaving
the local application. Browser and headless clients receive the same safe public
representation. The help system presents reviewed explanations but never
silently replaces the product, domain, contract, risk, security, or architecture
sources that own their meaning.

## Scope Boundaries

### In Scope

- An additive, read-only `platform-help/v1` contract family for an exact topic,
  deterministic browse/search page, query, stable topic kinds, applicability,
  publication facts, canonical-source references, and related-topic links.
- A bounded Guidance module that owns the safe product projection and search
  policy only. Canonical repository sources retain glossary, product, domain,
  method, risk, AI-authority, and limitation meaning.
- A checked-in, immutable, versioned starter corpus derived from current
  canonical sources and admitted through a closed validator at composition
  time. No repository Markdown is served or parsed at request time.
- Deterministic case-insensitive literal search and kind filtering with closed
  normalization, ranking, cursor, and tie behavior. Search uses reviewed title,
  summary, keywords, and glossary term only; it performs no embedding, model,
  personalization, behavioral tracking, or external retrieval.
- Protected same-origin read operations, reviewed OpenAPI, and a generated
  TypeScript client suitable for browser, command-line, service, and future
  headless-AI callers under the same validation and authorization policy.
- Accessible browser routes for browsing, searching, clearing filters, opening
  an exact topic version, following related topics, and reaching publication
  details and a progressive `Technical record`.
- Safe typed content nodes and same-origin topic links. Raw HTML, scripts,
  styles, executable content, arbitrary protocols, repository paths, storage
  locators, and unreviewed external instructions are rejected.
- Focused and live evidence for exact-version reads, stable search order,
  malformed/stale/missing topic containment, source binding, browser/headless
  parity, local offline use, restart, accessibility, privacy, and cleanup.
- Anti-rigidity evidence for empty and populated results, varied valid topic
  counts and order, Unicode, optional metadata, additional safe topics, and copy
  improvements that preserve required meaning and accessible actions.

### Out of Scope

- Contextual feature links, detailed methodology/provenance explanations, and
  feature-specific unavailable or troubleshooting guidance; SLI-0083 and
  SLI-0084 own those increments.
- Final corpus-wide freshness, broken-link, search-quality, offline, and
  cumulative accessibility qualification; SLI-0085 owns closure evidence.
- Mutable authoring, editorial workflow, external learning standards, public
  publishing, user-contributed help, comments, ratings, support tickets, or
  hosted support integration.
- AI-generated canonical help, semantic/vector search, recommendations,
  personalization, experimentation, inferred needs, model/provider execution,
  or collection of search analytics.
- Serving repository Markdown, exposing local paths or Git metadata, fetching
  remote content, following redirects, rendering arbitrary URLs, or executing
  active content.
- Legal, tax, regulatory, accreditation, suitability, support, or outcome
  guarantees; learner-specific financial conclusions; or any change to the
  education-versus-advice boundary.
- Organization tenancy, enterprise policy, managed-cloud operation, external
  source refresh jobs, notifications, commercial licensing, or recovery policy.
- Nonfunctional visual polish that does not impair comprehension,
  accessibility, responsive use, or required hierarchy; optional polish remains
  CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0020](../capabilities/CAP-0020-understand-platform-methods-and-limitations.md)
  defines the approved four-slice outcome and this first corpus/search
  increment.
- [Documentation Governance](../../README.md), the
  [Domain Glossary](../../domain/glossary.md), and each referenced canonical
  source retain semantic authority. Guidance is a versioned product projection,
  not a second source of truth.
- The [Module Map](../../architecture/modules/module-map.md) and
  [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  require one bounded owner, public module seams, additive versioned contracts,
  no cross-module persistence access, and identical browser/non-browser meaning.
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
  and [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
  prevent help from becoming personalized advice, model authority, grading,
  eligibility, or external execution.
- [Interface Design](../../design/README.md), the
  [Content Style Guide](../../design/content-style-guide.md),
  [Interface Design Standards](../../standards/interface-design-standards.md),
  and [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern task-first copy, progressive technical detail, accessibility, themes,
  and responsive presentation.
- [Decision Readiness](../../adr/decision-readiness.md) has no unresolved choice
  for this read-only local shared-core boundary. Identity remains server-owned;
  managed-cloud, external-provider, tenancy, recovery, legal, and commercial
  choices are not exercised.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver a platform-owned Guidance projection, public API, generated client, and accessible browser browse/search flow over an immutable reviewed corpus | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Bundle the corpus only in the browser and search it client-side | yes, but omits API/headless parity and duplicates search authority | 1 | 1 | 2 | 1 | 1 | 2 | 2 | 10 |
| C. Expose or parse repository Markdown directly at request time | no; it leaks repository structure, couples runtime to authoring files, and admits unsafe or stale presentation shapes | - | - | - | - | - | - | - |
| D. Encode help as lesson packages inside Content | yes, but conflates learner activities with product guidance and creates unnecessary placement/publication coupling | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 9 |
| E. Use semantic search or generated answers for the initial corpus | no; provider/model authority, evaluation, privacy, grounding, and fallback decisions are outside this slice | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the smallest complete SLI-0082 outcome and scores 14 of 14. It
keeps one transport-neutral source for browser and headless clients, separates
the Guidance projection from canonical source authority, works without network
access, and establishes stable topic keys that later contextual links can use.
Candidate B would make the browser authoritative and force future headless or
feature consumers to reimplement search. Candidate D reuses storage machinery
at the cost of incorrect domain meaning and dependence on lesson publication.
Candidates C and E cross explicit security and decision boundaries.

The bounded Guidance module is an immutable read projection, not a new policy
owner. This refinement preserves CAP-0020's outcome, four-slice manifest,
sequence, material-change boundaries, and no-AI/no-external-content constraints.
It requires no slice-level approval.

## Boundary Path

1. Closed `platform-help/v1` schemas define an exact safe topic, browse/search
   request and page, applicability, source/publication facts, related-topic
   references, and a typed body-node union.
2. Pure Guidance values validate topic and version identity, closed kinds,
   Unicode text bounds, safe nodes, canonical-source fingerprints, unique
   relations, chronology, applicability, and a canonical document digest.
3. A deterministic search operation normalizes the closed query, filters by
   kind, ranks reviewed fields with documented rules, applies a query-bound
   cursor, and returns exact-version links in stable order.
4. A checked-in corpus adapter loads only declared versioned JSON resources at
   composition time, validates the complete set, and exposes immutable reads
   behind a Guidance-owned port. Invalid corpus data fails startup rather than
   becoming partially visible.
5. Protected FastAPI reads accept only the closed query/path shapes, derive
   permission from the server session, map bounded public failures, publish
   reviewed OpenAPI, and regenerate the shared TypeScript client.
6. The generated client powers accessible `Help` browse/search and exact-topic
   routes. URL-backed filters support reload and sharing inside the same
   authorized application; the browser does not rank or reinterpret results.
7. Focused and isolated live qualification compares browser and ordinary
   headless results, restarts the host without network access, checks source
   and topic integrity, exercises safe failures and accessibility, and removes
   only its bounded runtime artifacts.

## Contracts, Data, and Provenance

The additive `platform-help/v1` family contains closed schemas for a topic,
search request, and result page. A topic has stable `topic_id`, semantic
`topic_version`, `topic_kind`, title, summary, optional glossary term, ordered
keywords, safe typed body nodes, applicability records, publication facts,
canonical-source references, ordered related-topic references, and a canonical
digest. Exact reads always require both ID and version; no caller-selected
`latest` substitution exists.

The initial body union supports only headings, paragraphs, unordered or ordered
lists, notes with a closed educational/limitation/warning kind, and same-origin
references to an exact help topic. Text is inert. There is no raw Markdown,
HTML, SVG, script, style, form, iframe, object, data URL, file path, external
URL, executable extension, or dynamic component declaration.

A canonical-source reference contains a safe source key, learner-readable
source title, source area, source version or recorded revision, and a content
fingerprint. It does not expose an absolute path, account identity, approval
ledger, reviewer identity, workstation, or Git remote. The topic projection
records when its meaning was reviewed and updated but never claims external
legal or standards authority.

Search accepts a bounded Unicode query, optional closed topic kind, positive
page size within a fixed maximum, and an optional opaque cursor bound to the
normalized query, filter, corpus version, and result position. Empty search
browses the stable corpus order. Non-empty search is literal and deterministic:
exact term/title, title prefix, title/term token coverage, then summary/keyword
coverage, followed by stable ID and semantic version. It does not use learner
history, popularity, engagement, embeddings, models, network calls, or hidden
synonyms. Cursor mismatch, unknown fields, malformed Unicode/control content,
and out-of-range limits fail before reading private state.

The starter corpus is checked-in immutable product data. It is loaded through
the same validator used by contract tests and retains exact source fingerprints
and topic digests. Later editorial tooling may produce the same contract but
cannot bypass its validation or silently rewrite canonical meaning.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Browse approved topics | An authorized browser or headless caller receives a stable first page with exact topic/version links, kinds, summaries, applicability, and publication facts | contract/application/API/live |
| Literal search | Case and harmless surrounding whitespace vary | The same normalized query returns deterministic ranked results with a query-bound cursor | domain/application/API/browser |
| Kind filter | A learner selects one supported topic kind | Every returned result has that kind and stable ordering; clearing it restores ordinary browse | application/API/browser |
| Exact topic open | A result's exact ID and version are opened | Both clients receive the same validated safe nodes, source facts, digest, and related-topic links | contract/API/browser/headless |
| No latest substitution | A valid ID is paired with an absent version | The request reports that exact version unavailable and does not substitute another version | application/API/browser |
| Safe rendering | Topic nodes include every allowed kind and Unicode text | The browser renders semantic elements without raw markup, active content, or unsafe protocols | contract/component/Chromium |
| Source authority | A topic is inspected | It identifies its canonical owner/source fingerprint and clearly states that help summarizes rather than replaces that source | contract/content/browser |
| Malformed corpus | A duplicate, bad digest, unsafe node, broken exact relation, invalid chronology, or unknown field is loaded | The complete corpus is rejected before any partial topic becomes visible | contract/domain/composition |
| Missing or stale topic | A URL points to a removed, unknown, or changed exact version | No unrelated content is disclosed; the learner can return to Help and search again | API/browser |
| Authorization | Session or required read permission is absent | The API fails closed without exposing topic content, corpus counts, or internal identifiers | API/security |
| Browser/headless parity | Equivalent queries and exact reads use the generated browser client and ordinary HTTP | Both observe equivalent ordered public documents and failure meaning | client/live |
| Offline local use | External network access is unavailable and the local host restarts | The checked-in corpus remains browseable and searchable with no outbound request | architecture/live |
| Flexible valid corpus | Topic counts, order, optional metadata, valid Unicode, extra safe topics, and body length vary within bounds | Invariants hold without fixed snapshots or fixture-count assumptions | property/contract/UI anti-rigidity |
| Accessible use | A learner searches, filters, opens, follows, and returns using keyboard and assistive technology across narrow, zoomed, forced-color, reduced-motion, and supported theme states | component/Chromium/design |
| Exact cleanup | Qualification succeeds or fails | Only its named disposable application, browser, and temporary artifacts are removed | live runner/finally |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0165](../work-packets/WRK-0165-freeze-platform-help-contracts.md) | Freeze the `platform-help/v1` topic/search contracts, compatibility corpus, safe body union, pure validation/search core, and source-provenance rules | none | none | complete |
| [WRK-0166](../work-packets/WRK-0166-compose-platform-help-api.md) | Compose the immutable corpus adapter, Guidance application/public seam, protected API, reviewed OpenAPI, and generated client | WRK-0165 | none | complete |
| [WRK-0167](../work-packets/WRK-0167-deliver-platform-help-browser-flow.md) | Deliver the URL-backed accessible Help browse/search and exact-topic browser routes only through the generated client | WRK-0166 | none | complete |
| [WRK-0169](../work-packets/WRK-0169-preserve-required-platform-help-null-fields.md) | Preserve the contract-required nullable continuation member discovered by live qualification | WRK-0166 | none | complete |
| [WRK-0168](../work-packets/WRK-0168-qualify-platform-help-live-flow.md) | Qualify contract, browser/headless parity, deterministic search, offline restart, source integrity, safe rendering, accessibility, containment, and cleanup | WRK-0167, WRK-0169 | none | ready |

Dependent packets are not reserved, authored, or claimed until their concrete
predecessor is complete. The sequential default avoids shared contract,
generated-client, API, routing, corpus, and live-runner collisions. A bounded
correction may add a dependent packet without renewed approval when it remains
inside this slice and the approved CAP package.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; pure Guidance validation,
canonical-digest, normalization, ranking, pagination/cursor, safe-node,
relation, chronology, and anti-rigidity tests; composition failure tests;
protected API authorization and failure suites; reviewed OpenAPI and generated-
client reproduction; TypeScript boundary tests; Web model/component tests;
focused Chromium accessibility; and one disposable browser plus ordinary
headless HTTP journey with outbound-network observation and normal restart.

Also run architecture/import and source-authority checks; security, privacy,
active-content, private-path, advice-language, and AI-authority checks;
documentation, planning, learner-language, design-system, dependency, Python,
TypeScript, zero-warning lint, build, whitespace, exact-candidate affected
verification, one independent technical review, deterministic completion
structure, and `python dev-tools/agent/check_ready.py`.

Tests protect contract meaning, ranking invariants, safe actions, required risk
language, and accessible behavior. They do not freeze whole prose, topic counts,
incidental order outside the declared ranking, layout pixels, optional styling,
or repository-document wording. Harmless whitespace, optional copy, or visual
polish does not create a full correction/review loop.

## Rollback and Migration

The slice adds versioned read-only contracts and an immutable checked-in corpus;
it requires no database migration or mutable learner data. A code rollback may
remove an unreferenced v1 API and browser route, but an exposed contract or
stable topic key follows compatibility governance rather than silent reuse.

Corpus updates create a new exact topic version and refreshed corpus version.
They never rewrite an already published exact version. Startup validation is
atomic: a malformed successor corpus leaves the prior deployable artifact
unchanged. Local qualification data and browser artifacts are disposable only
inside their exact isolated topology.

## Stop Conditions

Stop for ambiguity over canonical source meaning; help becoming product,
domain, risk, contract, authorization, grading, eligibility, or financial-policy
authority; raw repository Markdown or paths served at runtime; mutable or user-
authored help; unreviewed external retrieval; arbitrary links or active content;
semantic/vector search; model/provider execution; personalization or search
tracking; learner-specific advice or suitability; breaking public contract;
identity or tenancy expansion; managed-cloud, recovery, legal, commercial, or
external-publication behavior; stale CAP authority; active write collision; or
material CAP-0020 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, fixture count/order, or another inconsequential issue.
Fix a bounded issue in scope or defer optional visual polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will reconcile the Guidance module boundary, versioned help/search
contract, corpus contribution and source-binding rules, public API/OpenAPI and
generated client, browser Help route, local runtime, architecture assurance,
known gaps, this slice, its packets, the CAP, and the planning register.

Completion evidence must name exact candidates and receipts; scenario-to-test
coverage; corpus and source fingerprints; deterministic ranking/cursor facts;
safe body and relation validation; browser/headless equivalence; authorization;
no-outbound-network observation; restart/local-offline behavior; accessibility,
privacy, containment, cleanup; compatibility and migration impact; assumptions;
unqualified deployment profiles; residual gaps; and CAP-package conformance.
Local approval and reviewer records remain ignored.

## Planning History

- 2026-10-18: Refined immediately before delivery from the approved CAP-0020
  manifest. Candidate A scores 14 of 14 and establishes a safe versioned
  Guidance projection plus one API-first browse/search path without making the
  browser, repository Markdown, lesson packages, external content, or AI a new
  source of authority. The four-slice CAP package remains unchanged and no
  lower-level approval is required.
