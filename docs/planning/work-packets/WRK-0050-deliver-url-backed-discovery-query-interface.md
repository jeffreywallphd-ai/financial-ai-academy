---
id: WRK-0050
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0019
capability: CAP-0004
depends_on: ["WRK-0049"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/src/features/learning-catalog/api.ts", "apps/web/src/features/learning-catalog/model.ts", "apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/src/features/learning-catalog/LearningCatalogRoute.tsx", "apps/web/src/styles/learning-catalog.css", "apps/web/tests/unit/learningCatalogModel.test.ts", "apps/web/tests/component/learningCatalogFixture.ts", "apps/web/tests/component/learningCatalog.test.tsx", "apps/web/tests/browser/learning-catalog/learning-catalog.spec.ts", "docs/architecture/contracts/discovery-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0019-query-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0050-deliver-url-backed-discovery-query-interface.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: 0bd13c1dcb872ee0eaee1dd0bc9326cc537a662e
claim_id: WRK-0050:9184881a-a641-4298-800a-a933d79df4c1
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T19:56:58Z
---

# Agent Work Packet: Deliver the URL-Backed Discovery Query Interface

## Objective and Deliverable

Replace the `/learn` route's queryless-only presentation with an accessible,
URL-backed interface over the completed protected query operation. Deliver
bounded search, prerequisite text, metadata and duration filters, closed sort,
page-size and continuation controls, exact result count, canonical applied
state, clear/empty states, and distinct bounded denial, invalid, stale, and
unavailable outcomes without duplicating Curriculum matching or ordering
policy in the browser.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; the
repository startup, planning, concurrency, change-impact, and
decision-readiness guidance; accepted
interface design system and standards; CAP-0004, SLI-0019, completed WRK-0048
and WRK-0049; discovery/query contracts; generated query client; current
catalog route/model/components/styles/tests; and nearest READMEs.

## Decisions and Assumptions

The browser URL uses the public operation's parameter names so refresh and
shared same-origin links reproduce the same first page. Repeated filters remain
repeated URL parameters. The loader performs only bounded shape parsing and
closed response validation; the server's echoed `applied_query`, ordering,
count, and cursor remain authoritative. A continuation cursor is preserved only
with its associated query. No learner/profile, recommendation, eligibility,
provider, storage, or ranking state enters the URL or interface.

## In Scope

- Parse bounded query URL state and call `queryLearningOpportunities` through
  the generated same-origin client, retaining one unauthorized-session retry.
- Validate the entire closed query-page envelope, canonical applied-query
  fields, exact records/source fingerprints, page/count coherence, and cursor
  shape before rendering; do not recompute a full-generation digest from a
  subset page.
- Add labeled GET-form controls for general/prerequisite text, topic, level,
  kind, availability, inclusive duration, sort, and page size using existing
  tokens and reviewed icons. Support clear/reset and keyboard submission.
- Present canonical active filters, exact total matches, current page records,
  and a continuation link that preserves the query and appends only the opaque
  cursor. Preserve exact lesson-opening rules and publication/provenance facts.
- Provide educational empty results plus distinct unauthorized, forbidden,
  invalid query/response, stale cursor, unavailable, loading, and unexpected
  states. Never render stale/partial records or silently retry stale cursors.
- Add focused unit, component, and mocked-browser coverage for URL mapping,
  response denial, controls, count/order, paging, clear, empty, and bounded
  error states in responsive/theme-neutral markup.
- Update only documentation made stale by the interface seam and packet
  lifecycle.

## Out of Scope

Query policy, ranking, record/query schemas, API/OpenAPI/generated-client
changes, backend or database work, migration, full live PostgreSQL/static-host
qualification, real-browser axe/theme/reflow matrices, provider/index/search
services, recommendation or prerequisite eligibility, enrollment, saved
searches, personalization, analytics, external navigation, and new dependencies
are excluded. WRK-0051 owns complete live topology and browser qualification.

## Expected File and Boundary Impact

| Area | Allowed change | Boundary |
| --- | --- | --- |
| Query loader and validation | `api.ts`, `model.ts` | URL/public-client mapping and fail-closed response checks only |
| Catalog interface | page, route, catalog stylesheet | Existing design tokens/icons and server-authoritative meaning |
| Evidence | listed unit/component/browser tests | Mocked deterministic query and bounded-state behavior |
| Documentation/lifecycle | listed README, contract, SLI, packet, register | Record delivered seam and remaining live qualification |

## Contracts and Interfaces

The loader calls only generated operation `queryLearningOpportunities`. URL
names match its public query parameters; repeated values remain repeated. A
validated success consumes `LearningOpportunityQueryPageResponseModel` and
renders the echoed `applied_query`, `total_matches`, ordered `records`, and
opaque `next_cursor` without interpreting query policy. Existing
`LearningOpportunityResponseModel` safety and exact lesson destinations remain
unchanged.

## Dependencies and Parallel Safety

WRK-0049 is complete and supplies the stable generated client. WRK-0051 depends
on this packet and shares route tests, documentation, and catalog files, so the
two packets are not parallel-safe. No other active edit lease may overlap the
declared scope.

## Acceptance Scenarios

| Scenario | Required outcome |
| --- | --- |
| Default URL | One protected default query runs and canonical count/order render |
| Bounded controls | GET submission writes reproducible URL parameters and server applied state renders |
| Combined filters/sort | Browser sends exact repeated/bounded values and preserves returned order without ranking |
| Continuation | Next link preserves query, adds opaque cursor, and renders the next validated page |
| Clear and empty | Clear returns to `/learn`; no matches explains absence without recommendations |
| Invalid or stale | Bounded distinct state offers correction or fresh first page without fallback records |
| Denied/unavailable | No records, counts, cursor, or stale content are disclosed |
| Accessibility/rigidity | Labels, native GET/form/link behavior, keyboard operation, responsive token-only CSS, and optional filters permit progress without forced input |

## Verification Commands

Run packet/planning/claim/start and lease controls; focused catalog unit,
component, and mocked-browser tests; generated-client currency; web typecheck,
lint, test, and build; design, architecture, security, documentation, planning,
and diff checks; affected control-plane verification; independent technical
review; and `python dev-tools/agent/check_ready.py`. Docker and live topology
are not required here because WRK-0051 owns that qualification.

## Documentation and Evidence Update

Record exact URL/public-client mapping, validation and confidentiality rules,
controls/states/paging, checks, theme/accessibility posture, absence of backend
or schema changes, residual live-browser/topology gaps, and WRK-0051 readiness.
Do not copy local approval or reviewer records into tracked files.

## Stop Conditions

Stop for changed query/discovery meaning; browser-owned matching, sorting,
ranking, cursor decoding, or eligibility; learner/permission/provider/storage
selectors; stale or partial fallback; raw HTML; new token/icon/dependency;
backend/schema/migration/external-service work; overlapping edit scope; an
unresolved durable decision; or material CAP/SLI outcome, order, risk, or
decision drift.

## Required Handoff

Report the URL and client mapping, validated response/state behavior,
accessibility and anti-rigidity evidence, affected interface/docs, all checks,
residual WRK-0051 qualification, lifecycle result, and dependency readiness.

## Planning History

- 2026-10-15: Authored just in time after WRK-0049 completion. The packet keeps
  the server authoritative for canonical query, count, order, and cursor;
  confines the browser to bounded URL mapping and fail-closed presentation;
  reuses existing tokens/icons; and introduces no durable decision or CAP drift.
