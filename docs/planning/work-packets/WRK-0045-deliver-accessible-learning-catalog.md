---
id: WRK-0045
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0018
capability: CAP-0004
depends_on: ["WRK-0044"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/components/Icon.tsx", "apps/web/src/features/learning-catalog/api.ts", "apps/web/src/features/learning-catalog/model.ts", "apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/src/features/learning-catalog/LearningCatalogRoute.tsx", "apps/web/src/styles/learning-catalog.css", "apps/web/tests/unit/learningCatalogModel.test.ts", "apps/web/tests/component/learningCatalogFixture.ts", "apps/web/tests/component/learningCatalog.test.tsx", "apps/web/tests/browser/learning-catalog/learning-catalog.spec.ts", "apps/web/README.md", "docs/architecture/contracts/discovery-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0018-browse-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0045-deliver-accessible-learning-catalog.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Accessible Learning Catalog

## Objective and Deliverable

Deliver the protected `/learn` catalog route that consumes only the WRK-0044
generated discovery client, validates the closed response before presentation,
and shows the authorized learner a stable set of approved opportunities. The
observable result is an accessible, responsive catalog with exact lesson links,
bounded empty/denied/unavailable/invalid states, publication context, and
equivalent light, dark, and system-theme meaning.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the interface-design and
testing-quality context packs; read the change-impact matrix, decision
readiness, CAP-0004, SLI-0018, WRK-0044, ADR-0006, ADR-0007, ADR-0009, the
discovery and identity contracts, discovery v1 schemas, education-versus-advice
boundary, interface standards, design README and style guide, executable token
and icon documentation, web README, generated client, session controller,
router and shell, lesson-route patterns, affected tests, and nearest READMEs.

## Decisions and Assumptions

The accepted static React/Vite architecture, single-profile Identity context,
and protected queryless discovery operation are fixed. The generated client is
the only data seam; browser code cannot select identity, permission, ordering,
or visibility and must treat successful JSON as untrusted. The API's existing
order is presentation order, not a ranking or recommendation. Existing semantic
tokens and reviewed SVG icons are sufficient. Only an `available` `lesson`
record may expose its exact same-origin `destination`; unsupported, planned, or
unavailable records remain descriptive and non-navigable.

## In Scope

- Add a `/learn` data route that establishes the existing single-profile
  session, calls the generated protected browse operation, permits one bounded
  renewal after a 401, and maps failures to non-disclosing route states.
- Validate the complete closed discovery v1 envelope and every record before
  displaying any record, including identifiers, destination, enums, bounds,
  dates, digests, uniqueness, ordering, and generation coherence.
- Render the API-provided order without search, filtering, sorting, pagination,
  personalization, substitution, or hard-coded opportunity identity.
- Present title, kind, summary, objectives, topics, level, duration,
  prerequisite summary, availability/reason, exact package version, and
  publication/review context without implying suitability or recommendation.
- Provide exact lesson navigation only for contract-valid available lessons,
  plus explicit educational empty, unauthorized, forbidden, unavailable,
  invalid-response, and unexpected states with safe retry guidance.
- Make `/` and the application brand resolve to `/learn` while retaining exact
  lesson URLs and the shared application shell.
- Qualify semantic hierarchy, keyboard/focus, narrow reflow, 200-percent
  equivalent zoom, reduced motion, forced colors, light/dark/system parity,
  axe results, safe errors, and flexible valid record sets in unit, component,
  and Chromium browser tests.

## Out of Scope

Search, filters, alternate sorts, cursors, pagination, comparison, detail
routes, enrollment, prerequisite evaluation, recommendations, learner progress,
new activity kinds or execution, backend/schema/generated-client changes,
automatic projection rebuild, seed orchestration, static/API co-serving, new
tokens or icons, SSR, analytics, tenancy, managed cloud, or external search.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Route and session composition | Generated client, session controller, lesson loader | Listed app and learning-catalog feature files | Add one protected catalog route without a second data protocol |
| Presentation | Interface standards, tokens, icon manifest, shared status panel | Listed catalog component, icon type, and stylesheet | Present exact facts and bounded states with shared visual semantics |
| Verification | Existing unit/component/Playwright patterns | Listed focused tests and fixtures | Prove fail-closed validation, flexibility, themes, access, and reflow |
| Documentation and lifecycle | Discovery/web docs, slice, packet, register | Listed documentation and planning files | Record the delivered browser boundary and remaining live qualification |

The packet may inspect but may not change the design-token or SVG assets. If an
existing semantic role cannot express an accessible state, stop for a shared
design review rather than adding a feature-local primitive.

## Contracts and Interfaces

WRK-0045 consumes `GET /api/v1/curriculum/opportunities` through
`FinancialAcademyApiClient`, the `1.0.0` closed browse and opportunity shapes,
the existing opaque session bootstrap, fixed record ordering, 500-record bound,
and bounded API errors. It produces a local route-state union and rendering
model only; neither is a new public contract.

Successful response validation is all-or-nothing. Unknown fields, unsafe or
non-exact destinations, malformed dates/digests/identifiers, duplicate values,
unsorted records, incoherent projection timestamps, or unsupported schema
versions produce the invalid-response state without partial cards. Valid empty
and variable-length record sets are accepted, ensuring the route does not
encode the current fixture or require a particular opportunity.

## Dependencies and Parallel Safety

WRK-0044 is complete and supplies the protected operation and generated client.
This packet owns the route and UI consumed by WRK-0046, so it is not
parallel-safe with that final composition/qualification packet. No active
packet owns its declared files or generated artifacts.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Approved browse | One or more exact approved records are returned | `/learn` loads | Cards retain API order and show exact classification, version, and provenance | unit/component/browser |
| Exact lesson action | A valid available lesson record is shown | Its action is activated | Navigation uses that record's exact destination without substitution | component/browser |
| Non-executable record | A record is unavailable, planned, or not a lesson | It is displayed | Availability meaning is visible and no destination action is exposed | unit/component |
| Flexible catalog | A valid empty set or different valid IDs/titles is returned | Validation and rendering run | Empty guidance or all supplied cards render without hard-coded fixture assumptions | unit/component |
| Whole-response denial | Any record, order, timestamp, or generation field is malformed | The response resolves | No partial catalog appears; a bounded invalid-response state is shown | unit/component/browser |
| Session denial | Session is missing, expired, revoked, or lacks permission | Catalog loading runs | One bounded renewal is allowed for 401; final denial exposes no records | unit/component/browser |
| Service failure | Network, conflict, or unavailable response occurs | Catalog loading runs | A safe unavailable state offers retry and leaks no internal detail | component/browser |
| Interface equivalence | Catalog and failure states use supported themes/settings | Keyboard, narrow, zoom, reduced-motion, forced-color, and axe checks run | Meaning, hierarchy, focus, actions, and content remain equivalent | component/Chromium |
| Static boundary | Production web build is inspected | Build and boundary checks run | UI uses only generated client/static React seams and no backend/provider imports | unit/build |

## Verification Commands

Run the packet validator and claim/start checks; focused catalog model, loader,
component, and browser tests; the complete web unit/component suite; TypeScript,
lint, static-boundary, design-system, production-build, documentation,
architecture, security, planning, and diff checks; affected control-plane
verification; and `python dev-tools/agent/check_ready.py`. Browser qualification
must include axe, keyboard/focus, theme parity, narrow and 200-percent-equivalent
reflow, reduced motion, forced colors, denial, invalid response, and safe retry.

## Documentation and Evidence Update

Update the web README and discovery contract only for actual delivered route,
validation, action, and remaining composition behavior. Update this packet,
SLI-0018, and the planning register together. Record exact route states,
operation consumed, validation boundary, interface/browser evidence, build
result, unsupported behavior, and the inputs handed to WRK-0046. Do not modify
canonical product meaning or derived packs unless a source change makes them
stale.

## Stop Conditions

Stop if implementation requires changing discovery v1, generated API output,
session/provider authority, fixed ordering, visibility policy, design tokens or
assets; permits partial rendering of an invalid response; requires a new
framework/data protocol; introduces personalized ranking, enrollment,
eligibility, tenancy, external search, unsupported execution, or automatic
rebuild; overlaps an active file lease; cannot automate the required browser
evidence; or materially changes the approved CAP/SLI outcome or risk posture.

## Required Handoff

Report the `/learn` route and state model; exact generated operation consumed;
validation and navigation constraints; ready, empty, denial, failure, theme,
accessibility, reflow, and static-build evidence; checks and results;
documentation impact; unsupported behavior and residual gaps; packet lifecycle
result; and whether WRK-0046 is dependency-eligible.

## Planning History

- 2026-10-15: Authored just in time after WRK-0044 completion. The packet stays
  within the approved protected catalog outcome, adds no durable decision, and
  reserves live projection composition and full local-path qualification for
  WRK-0046.
