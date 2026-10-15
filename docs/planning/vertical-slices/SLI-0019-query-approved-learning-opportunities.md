---
id: SLI-0019
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: CAP-0004
depends_on: ["SLI-0018"]
decision_gates: []
---

# Vertical Slice: Query Approved Learning Opportunities

## Outcome and User Scenario

An authorized private-host learner searches and narrows the approved learning
catalog by explicit metadata, changes a deterministic sort, and moves through a
bounded result set while the URL, visible controls, result count, and server
response describe the same query. Empty, malformed, stale-page, unavailable,
and unauthorized states remain bounded and never fall back to personalized
ranking, stale records, or an unfiltered disclosure.

## Scope Boundaries

### In Scope

- Add a versioned discovery-query contract that reuses the exact SLI-0018
  opportunity record without changing the existing queryless browse contract.
- Define bounded query text over title, summary, objectives, topics, and
  prerequisite summary; a prerequisite-only text filter; repeatable topic,
  level, kind, and availability filters; inclusive duration bounds; closed sort
  choices; page size; and an opaque continuation cursor.
- Normalize server-side text matching with versioned Unicode NFKC, whitespace
  collapse, and case-fold semantics fixed by cross-runtime compatibility
  vectors. All search terms are conjunctive; repeated values within one filter
  dimension are disjunctive; different filter dimensions are conjunctive.
- Preserve projection order as the default and provide title-ascending,
  duration-ascending, and duration-descending sorts with opportunity identity as
  the final deterministic tie-breaker. No relevance score or learner signal is
  produced.
- Execute the bounded query in the shared Curriculum application core over the
  validated projection, whose existing maximum is 500 records. The local
  profile requires no external search service; provider-specific optimization
  remains behind future platform-owned ports and the same conformance corpus.
- Add a protected generated-client operation with an applied-query echo, total
  match count, bounded page, next cursor, projection generation, and projection
  time. A cursor binds its query fingerprint and projection generation.
- Extend `/learn` with accessible, responsive, theme-equivalent controls and
  canonical URL state, including clear-all, explicit active filters, stable
  result counts, and bounded empty, malformed, stale-page, denied, unavailable,
  and invalid-response states.

### Out of Scope

- Relevance scoring, fuzzy matching, stemming, synonyms, semantic/vector/model
  search, recommendations, behavior-based ranking, sponsored placement, or
  learner-specific defaults.
- Parsing prerequisite prose into eligibility or claiming that prerequisites
  are satisfied. The prerequisite filter performs normalized text matching only
  against the Curriculum-owned summary and is labeled accordingly.
- External search infrastructure, crawlers, provider selection, background
  scheduling, incremental indexing, managed-cloud tenancy, or cross-tenant
  visibility.
- Detail or comparison views, selection trays, enrollment, entitlement,
  eligibility, activity execution, or changing the exact destination; those
  remain SLI-0020 or later capability work.
- Changing discovery-v1 record meaning, loosening SLI-0018 authorization and
  integrity checks, or silently returning the full catalog after query failure.

## Canonical Context and Decisions

CAP-0004 explicitly enumerates SLI-0019 after the now-complete SLI-0018 and
requires documented deterministic query, filter, sort, pagination, malformed,
stale, degraded, and provider-neutral local semantics. The current CAP package
approval includes SLI-0019. ADR-0002 keeps the contract platform-owned;
ADR-0004 keeps one shared local/cloud core; ADR-0005 keeps discovery in
Curriculum; ADR-0006 keeps authorization server-resolved; ADR-0009 keeps the
static TypeScript client on generated public contracts. Decision readiness is
`ready` for these boundaries. External search, tenancy, personalized ranking,
and provider admission remain explicit stop boundaries rather than hidden
implementation choices.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Add a separate deterministic query operation over the accepted projection and retain queryless browse compatibility | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Download the whole projection and query only in the browser | yes | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 12 |
| C. Add query metadata directly to the closed discovery-v1 browse envelope | no | 2 | 2 | 2 | 0 | 1 | 2 | 1 | 10 |
| D. Adopt an external full-text or vector search provider | no | 1 | 2 | 0 | 1 | 0 | 1 | 1 | 6 |

## Selection Rationale

Candidate A wins on every criterion. It produces the complete learner-visible
increment, keeps deterministic policy in the shared core, adds an explicit
portable contract, preserves the accepted queryless consumer, and is reversible
without migrating authoritative data. Candidate B would duplicate product
semantics in the browser and make a future cloud adapter unable to prove the
same query boundary. Candidate C breaks the deliberately closed SLI-0018
envelope and existing fail-closed consumers. Candidate D crosses unresolved
provider, data-use, tenancy, cost, and operational decisions and is outside the
approved CAP.

No tie-break was required. SLI-0018 is the only hard predecessor. SLI-0020 may
use the stable SLI-0018 record in parallel at the CAP level, but SLI-0019's
packets remain sequential because they share contracts, generated clients, the
catalog route, and final live evidence.

## Boundary Path

`validated Curriculum discovery projection -> versioned query request and
deterministic application policy -> bounded query page and generation-bound
cursor -> protected FastAPI/OpenAPI operation -> generated TypeScript client ->
URL-backed accessible /learn controls -> isolated PostgreSQL/Python/Chromium
qualification`. Identity continues to authorize discovery reads before query
execution. The browser displays applied server facts and does not re-rank or
recompute matches.

## Contracts, Data, and Provenance

Create a discovery-query v1 request/result contract while referencing the
unchanged discovery-v1 record. The request bounds query and prerequisite text,
filter cardinality, duration range, sort, page size, and cursor exclusivity. The
result includes schema version, exact projection generation/time, a canonical
applied-query representation, total matches, records, and nullable next cursor.
Records retain their exact source fingerprint and Content/Curriculum provenance.

Default catalog order remains the authoritative SLI-0018 order. Alternative
sorts are deterministic metadata ordering with opportunity ID as the final
tie-break. The cursor is opaque to clients, versioned and bounded, and binds the
canonical query fingerprint, sort position, and projection generation. A
changed generation fails as a stale cursor, while a mismatched query fails as
an invalid query;
it never resumes against different records. Because cursors grant no authority
and contain only already-public ordering facts, they require validation and
integrity checks but no new credential or durable secret.

No authoritative migration is expected. The accepted projection remains
derived and capped at 500 records, so the shared core may query one validated
snapshot without a second index. If measured evidence later requires an
optimized or external adapter, that is a separately decided implementation
behind the same public semantics and compatibility corpus.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Text query | Learner enters multiple terms | Every returned record matches every normalized term in an allowed field; projection order is retained unless an explicit sort is selected | contract/application/API/browser/live |
| Metadata filters | Learner combines topics, levels, kinds, availability, duration bounds, and prerequisite-summary text | Values within one dimension use OR, dimensions use AND, active controls and URL show the exact applied query | contract/application/component/browser |
| Stable sorts | Learner selects catalog, title, shortest, or longest order | Results use the documented order and opportunity-ID tie-break without relevance or learner signals | application/compatibility/browser |
| Bounded pagination | More matches exist than the page size | Result count is stable, next cursor continues without duplicate/omitted records, and refresh preserves URL state | contract/application/API/browser/live |
| Empty result | A valid query matches nothing | A bounded educational empty state shows the applied filters and clear action without invented recommendations | API/component/browser |
| Malformed query | Text, enum, range, cardinality, size, or cursor shape is invalid | Request is rejected before query execution with bounded error fields and no records | contract/API/security/browser |
| Stale or mismatched cursor | Projection generation changes or cursor query differs | Continuation is rejected without records; generation drift offers a fresh start, while query mismatch offers clear-query recovery | application/API/browser/live |
| Projection unavailable or corrupt | The current complete projection cannot be read or validated | Query returns bounded unavailable output and UI retains controls without stale or partial records | application/API/browser |
| Visibility denial | Session is absent, expired, revoked, insufficient, or client-selected | Request is denied before query records or counts are disclosed | identity/API/security/live |
| Interface equivalence | Query controls are used across themes, keyboard, focus, reflow, reduced motion, forced colors, and axe | Equivalent labels, active state, count, ordering, paging, errors, and clear actions remain perceivable and operable | component/Chromium |
| Local portability | Local query runs without external search | PostgreSQL, shared Python core, static client, and filesystem qualify the same public query semantics | architecture/live |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0048 | Deliver the discovery-query contract, canonical normalization/cursor rules, deterministic shared-core query policy, and compatibility vectors | SLI-0018 | none | complete |
| WRK-0049 | Expose the protected query API and reproducible OpenAPI/generated-client seam with bounded error mapping | WRK-0048 | none | complete |
| WRK-0050 | Deliver URL-backed accessible search, filter, sort, count, paging, empty, denial, stale, unavailable, and invalid states on `/learn` | WRK-0049 | none | complete |
| WRK-0051 | Qualify the complete local query path, pagination continuity, query-bound cursor denial, security/accessibility, and cleanup | WRK-0050 | none | active |

## Verification and Qualification

Require query schema/corpus vectors; normalization, conjunction/disjunction,
sort tie, cursor replay/mismatch/generation, boundary, and denial unit tests;
Curriculum application and PostgreSQL projection regressions; protected API and
Identity denial tests; stable OpenAPI and generated-client regeneration;
component/browser tests for URL state, content safety, active filters, count,
ordering, paging, clear/empty/malformed/stale/unavailable behavior, themes,
keyboard/focus, reflow, reduced motion, forced colors, and axe; and one isolated
PostgreSQL 18.4/Python/static/Chromium qualification with enough deterministic
fixtures to cross a page boundary. Also run architecture, security, design,
documentation, planning, dependency, build, diff, affected control-plane, and
aggregate readiness gates.

## Rollback and Migration

No authoritative migration is planned. The new protected operation and browser
controls are additive; the queryless browse operation remains compatible and
available during rollback. Reverting the generated client and route controls
removes query exposure without changing the accepted projection or source
facts. Query cursors are short-lived transport state rather than durable user
evidence and may be invalidated by rollback or projection rebuild with an
explicit bounded response.

## Stop Conditions

Stop if work requires changing discovery-v1 record or browse meaning; parsing
prerequisite prose into eligibility; client-side ranking authority; relevance,
personalization, learner behavior, recommendation, entitlement, or enrollment;
an external search/index provider, background queue/scheduler, crawler, tenant,
credential, secret cursor authority, or managed-cloud policy; unbounded scans or
responses; stale/partial fallback; new activity execution; overlap with another
active lease; or a material change to CAP-0004 outcome, slice manifest,
ordering, risk, or decision posture.

## Documentation Impact and Completion Evidence

Update the discovery/query executable contracts and compatibility corpus;
Curriculum/API/web READMEs; discovery, identity, module, architecture-assurance,
security, and known-gap documents; generated OpenAPI/client artifacts; this
slice, its packets, and the register. Completion evidence must identify exact
normalization/filter/sort/cursor semantics, compatibility preservation, denial
and failure paths, interface qualification, live topology and fixtures, checks,
unsupported profiles/providers, residual gaps, and CAP-package conformance.

## Planning History

- 2026-10-15: Refined as the dependency-ready second CAP-0004 slice after
  SLI-0018 completion. Candidate A scored 14/14 by adding a separate
  deterministic query operation over the accepted projection, preserving the
  queryless contract and introducing no durable decision or material CAP drift.
- 2026-10-15: Authored WRK-0048 with the executable query-v1 contract,
  shared-core deterministic policy, compatibility corpus, bounded denial, and
  focused verification seams. HTTP, generated-client, interface, and live
  qualification remain assigned to WRK-0049 through WRK-0051.
- 2026-10-15: Activated WRK-0048 after its exact contract, Curriculum,
  verification, documentation, and planning scope was claimed against the
  current CAP branch with no overlapping active work.
- 2026-10-15: Completed WRK-0048 with the additive query-v1 contract, bounded
  tolerant raw-input and canonical applied-query rules, deterministic shared
  core, multi-record filter/sort/page/cursor vectors, unchanged queryless
  browse, and fresh qualifying verification. WRK-0049 is dependency-ready.
- 2026-10-15: Authored WRK-0049 with the protected GET query operation,
  bounded transport/error mapping, deterministic OpenAPI/generated-client seam,
  queryless compatibility, and focused authorization/confidentiality evidence.
  Browser behavior remains assigned to WRK-0050.
- 2026-10-15: Completed WRK-0049 with the protected additive query operation,
  exact bounded parameter and topic-item contracts, canonical page mapping,
  bounded 400/409/503 failures, unchanged queryless browse, reproducible
  OpenAPI/generated-client outputs, and fresh qualifying verification. WRK-0050
  is dependency-ready.
- 2026-10-15: Authored WRK-0050 with bounded URL/public-client mapping,
  fail-closed query-page validation, accessible optional controls, exact count
  and continuation behavior, and explicit empty/invalid/stale/denied states.
  Full live topology and browser qualification remain WRK-0051.
- 2026-10-15: Completed WRK-0050 with URL-backed optional query controls,
  canonical server-applied state, exact count and opaque-cursor paging,
  request-aware first/continuation page validation, bounded failure states,
  and responsive theme-equivalent interface evidence. WRK-0051 is
  dependency-ready for live topology qualification.
- 2026-10-15: Authored WRK-0051 to qualify an explicit bounded query corpus
  through the existing PostgreSQL/Python/static/Chromium topology, including
  combined filters, multi-page continuity, query-bound cursor denial,
  confidentiality, accessibility, cleanup, and ordinary-startup anti-rigidity.
- 2026-10-15: Activated WRK-0051 on the current CAP branch after its exact
  composition, live-browser, architecture, generated-artifact,
  documentation, and lifecycle scope was claimed with no overlapping edits.
