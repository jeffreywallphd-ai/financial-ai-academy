---
id: WRK-0060
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-15
parent: SLI-0022
capability: CAP-0005
depends_on: ["WRK-0059"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/curriculum-graph/api.ts", "apps/web/src/features/curriculum-graph/model.ts", "apps/web/src/features/curriculum-graph/CurriculumGraphPage.tsx", "apps/web/src/features/curriculum-graph/CurriculumGraphRoute.tsx", "apps/web/src/styles/curriculum-graph.css", "apps/web/tests/component/curriculumGraphFixture.ts", "apps/web/tests/component/curriculumGraph.test.tsx", "apps/web/tests/unit/curriculumGraphModel.test.ts", "apps/web/tests/browser/curriculum-graph/curriculum-graph.spec.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0022-open-versioned-curriculum-graph.md", "docs/planning/work-packets/WRK-0060-deliver-curriculum-graph-map-list.md"]
generated_artifacts: []
base_revision: 7b7d4fab58ab5e7e0d3632cc6706a8ba957bc00a
claim_id: WRK-0060:7229c075-e594-43ac-aa45-3f71a3d8fc56
claimed_by: codex-cap-0005
claimed_at: 2026-10-15T23:34:23Z
---

# Agent Work Packet: Deliver the Curriculum Graph Map and List

## Objective and Deliverable

Deliver an authenticated learner route for one exact approved curriculum graph
version using the WRK-0059 generated client. The route must fail closed on
invalid or unavailable data and present the complete graph through two peer
views: a semantic list that is the robust default and a responsive visual map
that does not encode graph meaning in fixed coordinates, color, or motion.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, interface-design,
curriculum/learning architecture, contracts, security, testing-quality, and
planning context packs. Read the change-impact matrix, decision readiness,
CAP-0005, SLI-0022, WRK-0058, WRK-0059, ADR-0005 through ADR-0007, the adaptive
pathway and curriculum-graph contracts, interface design system, style guide,
interface standards, executable token and icon documentation, web README,
generated graph client, application router/session patterns, current learner
routes, shared status/icon components, and nearest unit/component/browser
tests.

## Decisions and Assumptions

The exact graph response remains Curriculum authority; the browser validates
the closed transport shape and relationships before presentation but does not
become publication, eligibility, or graph-digest authority. The route identity
is explicit and versioned at
`/learn/curricula/:curriculumId/versions/:curriculumVersion`; there is no
current/latest alias or hard-coded curriculum count. List and map are peer
presentation modes over one validated in-memory graph. The list is the default
and complete accessible representation. The map is a fluid CSS/semantic-HTML
projection, not canvas geometry, executable graph expressions, or a new layout
contract.

## In Scope

- Add a generated-client loader that validates exact path identifiers,
  establishes the opaque single-profile session, calls only the exact graph
  endpoint, retries one unauthorized response through the existing session
  renewal seam, and maps denials/failures to bounded route states.
- Add a strict runtime graph-response validator for closed keys, scalar bounds,
  enums, timestamp/digest profiles, identity uniqueness, typed references,
  branch memberships, presentation hints, and relationship endpoints. Reject
  the entire response on any unknown, malformed, duplicate, or dangling value.
- Add one exact-version route with loading, unauthorized, forbidden, not-found,
  unavailable, invalid-response, and unexpected states that disclose no
  private or technical payload.
- Render title, summary, exact version/digest, publication time, source
  references, objectives, competencies, activities, required/optional
  branches, and typed relationships in both semantic list and responsive map
  modes. Label graph concepts and relationship meaning in text in addition to
  visual grouping.
- Use accessible peer-view controls with persistent visible focus. Preserve
  logical reading order, theme parity, 200-percent reflow, reduced motion,
  forced colors, keyboard use, and a complete no-script-independent semantic
  DOM; add no activity launch or advancement action.
- Reuse semantic `--faa-*` variables and reviewed `learning-path`, `target`,
  `learn`, `assessment`, and provenance/status icons. Add no feature palette,
  token scale, icon asset, dependency, visual baseline, or shared design rule.
- Add direct anti-rigidity coverage for absent/partial presentation hints,
  plural objectives and entries, variable node and branch counts, same-kind
  shared activity membership, unbranched activities, alternate sibling order,
  and unknown future-looking values that must fail closed.

## Out of Scope

Eligibility, completion state, prerequisite satisfaction, locked/unavailable
activity states, advancement explanations, activity launch, return context,
current-position markers, saved view preference, graph editing, drafts,
publication, adaptive ranking, recommendations, mastery, learner evidence,
enrollment, cross-curriculum credit, current/latest aliases, external learning
standards, provider payloads, canvas/SVG edge routing, a graph-layout library,
or live cross-system qualification retained by WRK-0061.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated-client boundary | graph operation/types, session and loader patterns | listed curriculum-graph `api.ts` and `model.ts` | Validate one exact response without duplicating backend authority |
| Learner interface | router, shell, shared components, tokens/icons, current feature patterns | listed route/page, router/main, and feature stylesheet | Add accessible list/map presentation using the existing design contract |
| Verification | current unit, component, and Playwright patterns | listed fixture and focused tests | Prove denials, complete semantics, themes, accessibility, and flexible shapes |
| Documentation/planning | web README, SLI-0022, register | listed documentation and packet files | Keep delivered route, packet state, and remaining live qualification explicit |

## Contracts and Interfaces

`CurriculumGraphView` is a browser-internal, deeply readonly alias of the
generated `CurriculumGraphResponseModel`; no handwritten transport contract is
introduced. `curriculumGraphIsSafe(value, expectedIdentity)` validates an
unknown response as a whole and returns no partial projection.
`parseCurriculumGraphSelection(params, url)` accepts only the exact bounded ID
and semantic version path with no query or fragment authority.
`createCurriculumGraphLoader(client, session)` returns a closed
`CurriculumGraphRouteState` union. The page accepts only the validated graph and
local `list | map` presentation state. Both presentations expose identical
graph facts; neither computes eligibility, progression, rank, or a substitute
graph version.

## Dependencies and Parallel Safety

WRK-0059 is complete and supplies the reviewed exact endpoint, generated types,
permission behavior, and flexible graph semantics. This packet owns shared web
router/style/test surfaces and therefore has no parallel-safe peer. WRK-0061
depends on this route and retains composed PostgreSQL/API/static-host/browser
qualification.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact approved graph | A valid exact-version response and established session | Route loads | Complete graph facts, version, digest, publication time, and sources appear without fallback | loader/component/browser |
| List/map parity | The learner switches peer views | Either view renders | Both expose the same objectives, competencies, activities, branches, and relationships in text | component/browser |
| Flexible graph shape | Presentation hints are absent/partial and graph counts/order/sharing vary | Validation and rendering run | Valid meaning renders without fixed counts, coordinates, or branch specialization | unit/component anti-rigidity |
| Invalid graph | Unknown fields/enums, duplicates, dangling links, mismatched identity, or malformed values arrive | Loader validates | Entire response becomes a bounded invalid-response state with no partial facts | unit/loader/component |
| Exact selection | A different or malformed ID/version/query is requested | Loader parses path | Malformed selection is rejected and a valid older version is never replaced by another | unit/browser |
| Protected access | Session is absent/expired, permission is denied, or graph is missing | Loader runs | One bounded state appears and no stale graph is displayed | loader/browser |
| Theme and assistive parity | Light/dark/system, keyboard, narrow/200-percent, reduced-motion, or forced-color mode is active | Learner uses both views | Content/action parity, focus, reading order, reflow, and axe checks remain valid | browser/design |
| Non-authority | Graph contains prerequisite relationships and activities | Page renders | No complete/eligible/locked/mastered/recommended state or launch action is inferred | component/browser |

## Verification Commands

Run the work-packet and implementation-gate validators; focused graph model,
loader, component, and browser tests; generated-client currency; TypeScript
typecheck, lint, complete Vitest suite, and production build; design-system,
architecture, documentation, planning, and diff checks; the packet-start
selected exact-candidate verification; independent technical review; and
`python dev-tools/agent/check_ready.py`. Browser evidence must exercise both
views, three themes, axe, keyboard/focus, narrow and 200-percent reflow,
reduced motion, forced colors, flexible shape, denials, and malformed response.

## Documentation and Evidence Update

Update the web README, this packet, SLI-0022, and the planning register.
Completion evidence records route/loader contracts, runtime validation,
list/map semantic parity, anti-rigidity shapes, denial behavior, exact focused
and aggregate checks, design-system reuse, assumptions, known gaps, and the
live path retained by WRK-0061. Never copy local approval or reviewer records
into tracked files.

## Stop Conditions

Stop for a graph-contract or endpoint meaning change, a current/latest alias,
client-authoritative digest/publication/eligibility policy, activity launch,
learner evidence or adaptation, hard-coded node/branch counts, fixed visual
coordinates required for correctness, a new design token/icon/dependency,
inaccessible map-only meaning, tenancy/entitlement changes, external-standard
semantics, active scope overlap, or any material CAP/SLI outcome, order, risk,
or decision-posture change.

## Required Handoff

Report exact route and loader behavior; runtime validation and bounded states;
list/map semantic parity; flexible-shape and excessive-rigidity evidence;
theme/accessibility/responsive checks; affected files and boundaries;
documentation impact; residual browser/manual gaps; packet lifecycle result;
and whether WRK-0061 is eligible.

## Completion Evidence

- Delivered the protected exact-version route at
  `/learn/curricula/:curriculumId/versions/:curriculumVersion` through the
  generated client and the existing opaque single-profile session seam, with
  one bounded unauthorized renewal and closed denied, missing, unavailable,
  malformed-selection, invalid-response, and unexpected states.
- Added whole-response validation for closed keys and bounds, global graph
  identities, typed activity references, same-kind shared branch membership,
  mixed-kind ambiguity denial, typed relationship endpoints, assessment-only
  assessor sources, optional presentation hints, and Unicode code-point text
  and source-reference limits. The browser does not recompute publication,
  eligibility, completion, mastery, or graph-digest authority.
- Delivered a complete semantic list default and fluid CSS/HTML map peer over
  the same validated graph facts. Both modes expose objectives, competencies,
  required and optional branches, shared and unbranched activities,
  relationships, exact version/digest, publication time, and sources without
  activity launch or learner-state inference.
- Focused evidence passed with 21 model, loader, and component tests plus four
  Chromium tests. Final aggregate web evidence passed with 114 Vitest tests and
  26 Chromium tests. TypeScript typecheck, lint, generated-client check,
  production build, design-system, architecture, documentation, planning,
  diff, and all 27 readiness checks passed on the closure candidate.
- Independent technical review accepted the third exact candidate after
  corrections aligned global graph semantics and all browser text/provenance
  limits with the canonical Curriculum contract. Local immutable review and
  verification records remain under ignored `.local-codex` only.
- WRK-0061 retains live PostgreSQL/API/static-host/browser qualification and is
  now dependency-ready. No decision gate, dependency, token, icon, or shared
  design rule was added.

## Planning History

- 2026-10-15: Authored just in time after WRK-0059 completion. The packet uses
  the reviewed exact graph client and existing design system to deliver one
  flexible accessible presentation increment without adding domain authority,
  activity execution, a dependency, or a new decision gate.
- 2026-10-15: Completed after exact-candidate verification and independent
  review. Review corrections added global identity and relationship meaning
  checks while removing noncanonical Unicode and whitespace rigidity.
