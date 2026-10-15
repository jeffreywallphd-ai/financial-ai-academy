---
id: WRK-0055
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: SLI-0020
capability: CAP-0004
depends_on: ["WRK-0054"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityComparisonPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityComparisonRoute.tsx", "apps/web/src/styles/learning-catalog.css", "apps/web/tests/component/learningCatalog.test.tsx", "apps/web/tests/component/learningOpportunityComparison.test.tsx", "apps/web/tests/browser/learning-catalog/learning-catalog.spec.ts", "apps/web/dist", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0020-inspect-and-compare-learning-opportunities.md", "docs/planning/work-packets/WRK-0055-deliver-opportunity-comparison.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver Opportunity Comparison

## Objective and Deliverable

Deliver an accessible, query-coherent way to select two through four current
catalog opportunities and compare their exact educational facts in user
selection order. Consume WRK-0053's protected current-snapshot comparison
loader, preserve a cursor-free return to the originating catalog, never rank or
recommend a winner, and expose only each available lesson's exact validated
destination.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through interface, API/security, testing-quality, and delivery-planning
context; read the change-impact matrix, decision readiness,
planning/concurrency guidance, interface design system, style guide, interface
standard, executable tokens, icon rules, CAP-0004, SLI-0020, completed
WRK-0053 and WRK-0054, discovery-v1 and its architecture contract, the app
router/shell, catalog/detail routes, status-panel conventions, catalog styles,
component and Chromium tests, and the web README.

## Decisions and Assumptions

Comparison is transient navigation state over the current catalog generation,
not saved learner data, a score, ranking, eligibility result, or suitability
recommendation. Selection is limited to records visible on the current result
page and retains the learner's checkbox selection order. The protected
queryless snapshot remains authoritative; URL values carry identities only.

## In Scope

- Add accessible per-card comparison controls and a catalog comparison action
  that permits two through four distinct current-page identities, states the
  bound, prevents excess selection, and requires no saved state or service.
- Register `/learn/opportunities/compare` before the parameterized detail route
  and compose it with the existing protected comparison loader.
- Present selected records in input order with exact identity, kind, topics,
  objectives, level, duration, prerequisites, availability/reason, package
  identity/version/digest, publication review facts, source fingerprint, and
  projection generation/time/schema.
- Preserve a canonical cursor-free `/learn` return reference. Provide a detail
  link for each record and the exact existing placement destination only for an
  available lesson; never fabricate an executable destination for other kinds.
- Provide bounded loading, malformed, changed/missing, unauthorized,
  forbidden, unavailable, invalid-response, unexpected, and invalid-ready-shape
  states without partial records or confidential implementation facts.
- Add token-only responsive styles and component/mocked-Chromium evidence for
  selection bounds/order, exact facts/actions, return continuity, denial and
  invalid response, themes, keyboard/focus, narrow reflow, 200-percent text
  scale, reduced motion, forced colors, and axe behavior.
- Regenerate the tracked static client and synchronize web and planning docs.

## Out of Scope

Saved comparisons, bookmarks, browser storage, cross-page selection,
recommendation, ranking, winner or score, enrollment, eligibility,
prerequisite completion, learner progress, behavioral tracking, new backend or
schema operations, direct detail endpoints, provider integration, migrations,
background work, or real PostgreSQL/live qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Route composition | router and WRK-0053 loader | router, new comparison route | Compose the protected current-snapshot comparison state |
| Catalog selection | current query page and card actions | catalog page | Offer bounded transient selection and preserve return state |
| Comparison presentation | discovery contract, detail vocabulary, tokens/icons | new comparison page and catalog stylesheet | Present exact facts and limitations without ranking |
| Interface evidence | catalog fixtures and component/Chromium suites | listed tests | Prove bounds, order, confidentiality, parity, reflow, and axe |
| Generated static client | current Vite output | `apps/web/dist` | Keep the Python-served artifact synchronized |
| Documentation/lifecycle | web README, slice, packet, register | listed docs | Keep delivered behavior and packet state synchronized |

## Contracts and Interfaces

The route consumes `createLearningOpportunityComparisonLoader` and
`LearningOpportunitySelectionRouteState` unchanged. It accepts two through
four repeated `opportunity` parameters plus the existing bounded `return_to`.
A ready state must be comparison-kind, contain two through four records, and
match identity count and order. Displayed facts and destinations come only
from those fully validated current records.

## Dependencies and Parallel Safety

WRK-0054 is complete. WRK-0056 will qualify and may reconcile the same route,
styles, browser suite, static output, documentation, and planning lifecycle, so
the packets are intentionally serial and not parallel-safe.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Select comparison | Two through four current-page cards are selected | Compare is activated | The repeated-ID URL retains selection order and a cursor-free return path | component/browser |
| Bound selection | Fewer than two or four selected records exist | Controls are used | Compare remains unavailable below two and unchecked records cannot exceed four | component/browser |
| Exact comparison | A valid current selection resolves | Comparison renders | Every selected record and exact provenance fact appears in input order with no ranking | component/browser |
| Exact actions | Selected records include available and planned kinds | Actions render | Detail is available for each; only available lessons expose exact placement | component/browser |
| Changed selection | Any selected identity is absent from the current generation | Loading resolves | The whole comparison fails closed with no partial record | component/browser |
| Visibility denial | Session is denied before browse | Comparison is requested | No selected ID, record, count, provenance, provider, storage, or technical detail appears | component/browser |
| Invalid response | Complete browse validation fails | Loading resolves | No partial facts or client-owned fallback appears | component/browser |
| Interface equivalence | Themes, keyboard, narrow reflow, 200-percent text scale, reduced motion, forced colors, and axe run | Comparison is used | Equivalent facts, actions, focus, order, and readable long values remain available | Chromium/design |
| Anti-rigidity | Ordinary unfiltered catalog records are selected | Comparison and return are used | The flow works without filters, saved state, cross-page state, or extra services | component/browser |

## Verification Commands

Run the packet validator; focused catalog/comparison component tests; focused
mocked Chromium catalog/comparison tests with axe; complete web unit/component
suite; TypeScript typecheck, lint, generated-client currency, and production
build; design-system, documentation, and planning validation; Git diff check;
packet-start selected controls; independent technical review; and any
additional affected control-plane checks. Real PostgreSQL/static/live
qualification remains WRK-0056.

## Documentation and Evidence Update

Record the bounded selection, ordered comparison, exact facts/actions,
cursor-free return, failure/confidentiality behavior, interface evidence, and
remaining live work in the web README, this packet, SLI-0020, and the planning
register. Never place local approval or reviewer records in tracked files.

## Stop Conditions

Stop for saved or cross-page state, a new backend operation or discovery
meaning, client-owned or cached record authority, partial comparison, ranking
or recommendation, enrollment, eligibility, prerequisite completion, learner
progress, new execution, a shared visual contract requiring approval, external
provider, dependency, migration, queue, background job, remote profile,
managed-cloud policy, overlapping active scope, unresolved durable choice, or
material CAP-0004/SLI-0020 outcome, manifest, order, risk, or decision drift.

## Required Handoff

Report selection bounds/order, compared facts, exact action policy,
return-path behavior, bounded failure/confidentiality results, theme and
accessibility checks, all verification, documentation impact, residual live
work, and CAP/SLI conformance.

## Planning History

- 2026-10-15: Authored just in time after WRK-0054 completion. The packet
  consumes the verified comparison-selection seam and existing design system,
  adds no backend contract or durable state, and retains comparison as bounded
  current-generation educational inspection within the approved CAP package.
