---
id: WRK-0087
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0024
capability: CAP-0005
depends_on: ["WRK-0086"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/features/curriculum-graph/model.ts", "apps/web/src/features/curriculum-graph/api.ts", "apps/web/src/features/curriculum-graph/CurriculumGraphRoute.tsx", "apps/web/src/features/curriculum-graph/CurriculumGraphPage.tsx", "apps/web/src/features/lesson-reading/model.ts", "apps/web/src/features/lesson-reading/api.ts", "apps/web/src/features/lesson-reading/LessonRoute.tsx", "apps/web/src/features/lesson-reading/LessonReadingPage.tsx", "apps/web/src/styles/curriculum-graph.css", "apps/web/src/styles/lesson-reading.css", "apps/web/tests/unit/curriculumGraphModel.test.ts", "apps/web/tests/unit/lessonModel.test.ts", "apps/web/tests/component/curriculumGraph.test.tsx", "apps/web/tests/component/lessonReadingPage.test.tsx", "apps/web/dist", "apps/web/README.md", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/planning/work-packets/WRK-0087-deliver-curriculum-launch-and-return-ui.md", "docs/planning/vertical-slices/SLI-0024-open-and-return-to-an-eligible-activity.md", "docs/planning/register.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: 7bfb3a7a61ae715d2c82fe3ca6c7a6d726ecbc38
claim_id: WRK-0087:cf174cae-825f-4540-a63b-fe044386abb6
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T12:55:14Z
---

# Agent Work Packet: Deliver Curriculum Launch and Return UI

## Objective and Deliverable

Let a learner start or review an openable lesson from either learning-path
presentation by calling the generated protected launch operation, navigating
only to its validated same-origin destination, and carrying bounded exact
curriculum return context. The lesson exposes a clear return action. Returning
reloads the graph and current navigation state and marks the selected activity
in text and non-color semantics without treating browser state as authority.

## Required Context

Follow the repository startup, interface-design contract, planning workflow,
and concurrent-work protocol. Read CAP-0005, SLI-0024, WRK-0085 and WRK-0086;
the curriculum graph, navigation-state, activity-launch, and lesson package
contracts; the generated launch client; current graph and lesson models,
loaders, routes, pages, styles, tests, and nearest README; design tokens and
reviewed icons; content-language guidance; and decision readiness.

## Decisions and Assumptions

- The browser sends only the exact curriculum ID, version, and activity ID to
  the generated launch operation. It never constructs a lesson placement from
  graph data or treats displayed eligibility as permission.
- The returned launch value must match the requested graph, activity, current
  graph digest, exact lesson placement/package, and fixed same-origin lesson
  path before navigation. Its evaluation time and projection digest are newly
  produced by the server and are validated as bounded provenance rather than
  compared with the necessarily earlier screen projection.
- One client-side route action owns session renewal, launch transport, bounded
  failures, and navigation data. Activity cards remain presentation-only.
- Structured query values carry curriculum ID, version, and activity ID to the
  lesson for return presentation. All three are required together and strictly
  validated. They never authorize a lesson or graph read.
- The returning graph route accepts only its one selected-activity query,
  ignores a syntactically valid ID absent from the freshly loaded graph, and
  rejects unrelated query or fragment inputs.
- Existing semantic variables and controls are sufficient. Styling is limited
  to functional focus, current-position, feedback, and responsive behavior.

## In Scope

- Closed runtime validation for the activity-launch response and its exact
  correlation with the currently requested graph/activity state.
- A generated-client route action with one unauthorized renewal, bounded
  learner-facing failure states, and no caller-supplied destination.
- `Start lesson` for incomplete eligible lessons and `Review lesson` for
  completed eligible lessons in both equivalent list and map presentations;
  no launch control for locked, unavailable, or assessment activities.
- Pending and bounded failure feedback that retains all learning-path facts.
- Strict all-or-none lesson return-context parsing and a same-origin return
  link derived from identifiers rather than an arbitrary URL.
- A refreshed graph current-position marker using visible text plus
  `aria-current`, with identical facts and actions after view switching.
- Unit and component coverage for success, renewal, stale/tampered responses,
  denials, flexible graph shapes, action visibility, keyboard activation,
  return parsing/linking, and current-position parity.

## Out of Scope

Backend/API/OpenAPI/generated-client changes; new permissions; automatic next
selection; ranking or recommendation; mastery; assessment launch; persistence;
navigation history; browser-authoritative eligibility; arbitrary return URLs;
evidence mutation; live PostgreSQL/host/Chromium qualification; screenshots;
new design tokens or icons; and broad visual polish.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Graph feature | closed graph/navigation models and route | model, API action, route, page, focused tests | Validate launch and expose equivalent learner actions |
| Lesson feature | protected lesson loader and reading page | model, loader, route, page, focused tests | Carry non-authoritative exact return context |
| Router | existing graph loader and lesson route | route action wiring only | Compose generated client/session without global feature coupling |
| Interface | current graph/lesson CSS, tracked static build, and design contract | functional selectors using existing tokens plus deterministic `apps/web/dist` output | Show pending/current/return meaning accessibly and keep the Python-served bundle current |
| Evidence | web README and adaptive-navigation contract | bounded notes plus packet/slice/register | Keep UI and planning behavior discoverable |

No backend, contract snapshot, generated API source, design token, icon source,
fixture database, or deployment file may change.

## Contracts and Interfaces

The route action accepts exactly one `activity_id` form value plus the exact
curriculum path parameters. It calls `getCurriculumActivityLaunch` and returns
a local action result: ready with an internally constructed lesson URL, or a
bounded unavailable/forbidden/not-found/blocked/invalid result associated with
the requested activity. Raw server details and arbitrary destinations never
reach rendered feedback.

The launch validator closes every response field and correlates graph,
activity, placement, package, and destination while validating the fresh
projection provenance. The return context
has exactly `curriculum_id`, `curriculum_version`, and `activity_id`; malformed,
partial, duplicate, extra, cross-origin, or fragmented forms are ignored on the
lesson and cannot change authorization. The graph accepts only
`activity=<identifier>` and uses it as current-position presentation after the
fresh graph confirms membership.

## Dependencies and Parallel Safety

WRK-0086 is complete and supplies the generated launch operation. This packet
is serial with JIT-D because JIT-D qualifies these exact interactions in the
live stack. It is not parallel-safe with changes to the graph/lesson features,
their styles/tests, router, adaptive-navigation contract, or SLI-0024 planning
files. No overlapping file lease may be active.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Eligible lesson | Lesson is available, eligible, and incomplete | Learner chooses `Start lesson` | Generated launch runs and only a correlated same-origin lesson destination opens | unit + component |
| Completed lesson | Lesson is available, eligible, and complete | Learner chooses `Review lesson` | Same server check runs; completion is not mutated | component |
| Non-openable activity | Activity is locked, unavailable, or an assessment | Path renders in list or map | Facts remain visible and no launch control exists | component anti-rigidity |
| Tampered/stale launch | Response mismatches graph, activity, placement, package, graph digest, path, or has malformed fresh projection provenance | Action resolves | Browser fails closed and does not navigate | unit |
| Session expiry | First launch is unauthorized | Session renews once | Exact launch retries once; a second denial stays bounded | unit |
| Return | Lesson has complete valid return context | Learner returns | Exact graph route reloads with the activity visibly current | unit + component |
| Invalid return | Return context is partial, extra, malformed, or absent from graph | Page renders | It grants nothing, creates no external link, and no false marker appears | unit + component |
| Flexible graph | Optional, unbranched, reordered, or shared same-kind activity appears | Actions render and view switches | Behavior derives per activity without graph-shape branches | component anti-rigidity |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/unit/curriculumGraphModel.test.ts apps/web/tests/unit/lessonModel.test.ts apps/web/tests/component/curriculumGraph.test.tsx apps/web/tests/component/lessonReadingPage.test.tsx`
- `npm --prefix apps/web test -- --run apps/web/tests/contract/generated-client.test.mjs`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `npm --prefix apps/web run build`
- `backend/.venv/Scripts/python.exe dev-tools/design/check_design_system.py`
- `backend/.venv/Scripts/python.exe dev-tools/planning/check_planning.py`
- `backend/.venv/Scripts/python.exe dev-tools/documentation/check_docs.py`
- `backend/.venv/Scripts/python.exe dev-tools/agent/check_ready.py`
- `git diff --check`

Live browser/PostgreSQL qualification remains JIT-D. Nonfunctional styling and
harmless formatting never require a correction or re-review loop.

## Documentation and Evidence Update

Update the web README, adaptive-navigation contract, this packet, SLI-0024,
and the planning register with launch/return/current-position behavior, exact
checks, anti-rigidity coverage, assumptions, known gaps, and migration
non-applicability. Do not store reviewer or approval metadata in tracked files.

## Implementation Evidence

- The graph route now uses the generated `getCurriculumActivityLaunch`
  operation through the existing session boundary. It retries one expired
  session once, maps denials to bounded learner-facing states, and navigates
  only after the closed response matches the exact graph, activity, lesson
  placement/package, graph digest, and derived same-origin lesson path.
- Eligible incomplete and completed lessons expose `Start lesson` and `Review
  lesson` respectively. Locked, unavailable, and assessment activities retain
  all facts without a launch control. List and map reuse the same activity
  component and action logic without graph-shape branches.
- The lesson accepts only a complete exact curriculum/version/activity return
  set and derives its local path. Returning reloads graph and Navigation state;
  only a selected identifier present in the fresh graph receives visible
  `Current activity` text and `aria-current="step"`.
- The graph route owns launch cancellation: a later learner action or route
  unmount aborts the superseded request without leaking an unhandled rejection,
  while unexpected failures remain bounded. Route-level coverage exercises the
  superseding-action path through the real router.
- Focused model/component verification passed 57 tests and the complete web
  unit/component regression passed 151 tests. Generated-client contract use,
  TypeScript typecheck, lint, production build, design-system validation,
  planning, documentation, and whitespace checks passed. The tracked static
  production bundle was regenerated from the verified source.
- Flexible unbranched, optional, shared same-kind, and reordered graph behavior
  remains data-driven. Fresh server launch evaluation time/projection provenance
  is accepted without stale equality, while malformed or mismatched graph,
  activity, resource, digest, and destination data fails closed.
- No backend, API, OpenAPI, generated API source, permission, persistence,
  evidence, ranking, recommendation, mastery, provider, queue, cloud, or
  external-action boundary changed. Live composed-system qualification remains
  JIT-D.

## Stop Conditions

Stop for a backend or launch-contract change; caller-selected destination,
learner, eligibility, placement, or package; arbitrary/open redirect; browser
authorization; persistent current-position/history; new evidence meaning;
ranking, recommendation, mastery, model authority, assessment execution, new
permission, identity/tenancy, provider, queue, cloud, external action, active
scope collision, canonical conflict, stale CAP authority, or material CAP/SLI
drift.

Do not stop for bounded component/model corrections, copy, exact functional
CSS using existing tokens, harmless whitespace, or optional polish. Fix those
locally or defer optional polish to CAP-0031 without another approval.

## Required Handoff

Report generated-client launch usage, response correlation, action visibility,
session renewal, bounded failures, return-context validation, refreshed current
position, list/map parity, focused and aggregate checks, exact candidate,
anti-rigidity evidence, assumptions, known gaps, and absence of backend,
contract, generated-source, persistence, evidence, model, provider, or external
authority changes. Leave JIT-D able to qualify one deterministic browser flow.

## Planning History

- 2026-10-16: Authored just in time after WRK-0086 completion. This packet
  consumes the generated protected launch operation at the browser boundary,
  adds only validated non-authoritative return presentation, and keeps live
  composed-system qualification in JIT-D. It remains within the approved
  CAP-0005 package and introduces no decision or lower-level approval gate.
- 2026-10-16: Activated from base
  `87c0455bef3c0dfa1a7336064b48d4201dd804eb` after revalidating current CAP
  authority, the completed dependency, exact browser-only scope, reproducible
  checks, and no decision or active ownership collision.
- 2026-10-16: Expanded the active packet by one generated-artifact boundary
  after the production build confirmed that `apps/web/dist` is tracked and
  Python-served. The packet was released and re-claimed from the same source
  base so a fresh start manifest and exclusive lease cover the exact static
  files; no product behavior, decision, or approval boundary changed.
