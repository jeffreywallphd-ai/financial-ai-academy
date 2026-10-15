---
id: WRK-0054
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: SLI-0020
capability: CAP-0004
depends_on: ["WRK-0053"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityDetailPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityDetailRoute.tsx", "apps/web/src/styles/learning-catalog.css", "apps/web/tests/component/learningCatalog.test.tsx", "apps/web/tests/component/learningOpportunityDetail.test.tsx", "apps/web/tests/browser/learning-catalog/learning-catalog.spec.ts", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0020-inspect-and-compare-learning-opportunities.md", "docs/planning/work-packets/WRK-0054-deliver-opportunity-detail-route.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Opportunity Detail Route

## Objective and Deliverable

Deliver an accessible route for inspecting one current learning opportunity
from the catalog. The route must consume WRK-0053's protected current-snapshot
loader, present exact educational facts, limitations, provenance, and
generation context, preserve a bounded return to the originating catalog, and
offer the exact lesson destination only when the validated record is an
available lesson.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through interface, API/security, testing-quality, and delivery-planning
context; read the change-impact matrix, decision readiness,
planning/concurrency guidance, interface design system, style guide, interface
standard, executable tokens, icon rules, CAP-0004, SLI-0020, completed WRK-0053,
discovery-v1 and its architecture contract, the app router/shell, current
catalog and lesson routes, status-panel conventions, catalog styles, component
and Chromium tests, and the web README.

## Decisions and Assumptions

WRK-0053's validated loader state is authoritative for browser presentation;
the detail route does not refetch by a new operation or accept URL-owned record
facts. Detail is educational inspection, not enrollment, eligibility,
prerequisite completion, suitability, or recommendation. Existing semantic
tokens, status panels, and reviewed icons are sufficient; no shared visual
contract or new asset is required.

## In Scope

- Register `/learn/opportunities/:opportunityId` with the generated queryless
  detail loader, loading fallback, and bounded route view.
- Add a visible `View details` action to every validated catalog card. Build
  its return reference from the canonical applied query without carrying the
  current page cursor or any record data.
- Present exact identity, kind, topics, objectives, level, duration,
  prerequisite summary, availability and reason, package identity/version and
  digest, publication/review facts and educational notice, source fingerprint,
  projection generation, and projection time with semantic headings and lists.
- Keep the exact available-lesson destination as the only executable activity
  action. Planned, unavailable, and non-lesson records retain an explicit
  limitation and no fabricated activity link.
- Provide bounded loading, malformed selection, changed/missing selection,
  unauthorized, forbidden, unavailable, invalid-response, and unexpected
  states with retry or catalog-return behavior appropriate to the state.
- Add token-only responsive detail/rail styling with light, dark, system,
  reduced-motion, forced-color, keyboard/focus, reflow, text-scaling, and long
  digest handling.
- Add component and mocked Chromium evidence for facts, exact actions,
  return-path continuity, denial/failure confidentiality, theme parity,
  keyboard focus, narrow reflow, forced colors, and axe behavior.
- Update the web README and synchronized planning lifecycle evidence.

## Out of Scope

Comparison selection or UI, saved/bookmarked details, browser storage, new
tokens or icons, backend/API/schema/generated-client changes, direct record
endpoint, enrollment, entitlement, prerequisite completion, recommendation,
ranking, learner progress, activity execution beyond the existing exact lesson
destination, production static generation, real PostgreSQL/live qualification,
provider integration, or background work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Route composition | app shell/router and WRK-0053 loaders | `apps/web/src/app/router.tsx`, new detail route | Compose the current protected loader and bounded route states |
| Catalog navigation | catalog page and query href model | `LearningCatalogPage.tsx` | Add a detail action with canonical cursor-free return state |
| Detail presentation | discovery contract, existing card/lesson semantics, tokens/icons | new detail page and catalog stylesheet | Present exact current facts, provenance, limitations, and actions accessibly |
| Component/browser evidence | catalog fixtures, component and Chromium catalog suites | listed tests | Prove success, failure, continuity, confidentiality, themes, focus, reflow, and axe |
| Documentation/lifecycle | web README, slice, packet, register | listed documentation files | Keep behavior and delivery state synchronized |

## Contracts and Interfaces

The route consumes `createLearningOpportunityDetailLoader` and
`LearningOpportunitySelectionRouteState` unchanged. Its parameter name is
`opportunityId`; ready state must be a detail selection containing exactly one
record. The catalog builds only the selected ID plus an encoded canonical
`/learn` return path. Activity continuation reuses the already validated
record destination and `opportunityCanOpen`; display never reconstructs a
placement path or substitutes another version.

## Dependencies and Parallel Safety

WRK-0053 is complete and supplies the exact parser, protected loader,
projection metadata, and closed states. WRK-0055 will edit the same catalog,
router, stylesheet, browser suite, and documentation to add comparison, so the
packets are intentionally serial and not parallel-safe.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Inspect current opportunity | A valid selected ID occurs in the current projection | The detail route opens | Exact facts, provenance, generation, educational notice, and limitations are visible | component/browser |
| Return continuity | Detail is opened from a filtered catalog page | The learner returns | Canonical query/filter state is retained without a cursor or client-owned record data | component/browser |
| Exact lesson action | The current record is an available lesson | The action is inspected | Only its validated exact placement destination can be opened | component/browser |
| Unavailable kind | The current record is planned or non-lesson | Detail renders | Availability reason remains visible and no activity action exists | component/browser |
| Malformed or changed selection | The ID is malformed or absent from the current projection | Loading resolves | No record or partial fallback appears; bounded catalog recovery is offered | component/browser |
| Visibility denial | Session is denied before browse | Detail is requested | No record, ID, count, provenance, provider, storage, or technical detail is disclosed | component/browser |
| Invalid response | The complete browse response fails validation | Loading resolves | No partial facts or cached fallback appear | component/browser |
| Interface equivalence | Themes, keyboard, narrow reflow, text scaling, reduced motion, forced colors, and axe run | Detail is used | Equivalent content, hierarchy, actions, focus, and readable long values remain available | Chromium/design |
| Anti-rigidity | The learner opens detail from ordinary `/learn` | Return is used | The route works without filters, comparison selection, saved state, or extra services | component/browser |

## Verification Commands

Run the packet validator; focused detail/catalog component tests; focused
mocked Chromium catalog/detail tests with axe; complete web unit/component
suite; TypeScript typecheck, lint, generated-client currency, and production
build; design-system and documentation validation; planning integrity; Git
diff check; packet-start selected controls; independent technical review; and
any additional affected control-plane checks. Real PostgreSQL/static/live
qualification remains WRK-0056.

## Documentation and Evidence Update

Record the new route, exact displayed facts/actions, cursor-free return
behavior, bounded failures, interface verification, and remaining comparison
and live work in the web README, this packet, SLI-0020, and the planning
register. Do not place local approval or reviewer records in tracked files.

## Stop Conditions

Stop for a new backend operation or discovery meaning; client-owned or cached
record authority; a new shared token/icon/pattern requiring design approval;
partial or substituted records; enrollment, eligibility, prerequisite
completion, recommendation, ranking, learner progress, saved state, or new
execution; an external provider, dependency, migration, queue, background job,
remote profile, or managed-cloud policy; overlapping active scope; unresolved
durable choice; or material CAP-0004/SLI-0020 outcome, manifest, order, risk, or
decision drift.

## Required Handoff

Report route composition, displayed facts, exact activity policy, return-path
behavior, bounded failure/confidentiality results, theme/accessibility checks,
all other verification, documentation impact, residual comparison/live work,
and CAP/SLI conformance.

## Planning History

- 2026-10-15: Authored just in time after WRK-0053 completion. The packet
  consumes the verified protected selection seam and existing design system to
  deliver detail inspection without new public contract, durable state, shared
  visual decision, or material CAP drift.
