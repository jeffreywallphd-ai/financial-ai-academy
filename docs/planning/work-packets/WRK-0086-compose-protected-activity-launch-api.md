---
id: WRK-0086
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0024
capability: CAP-0005
depends_on: ["WRK-0085"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/adaptation/application/service.py", "backend/src/financial_ai_academy/modules/adaptation/public.py", "backend/src/financial_ai_academy/modules/adaptation/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/tests/unit/adaptation/test_activity_launch_application.py", "backend/tests/integration/api/test_single_profile_activity_launch_api.py", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/README.md", "contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/README.md", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/planning/work-packets/WRK-0086-compose-protected-activity-launch-api.md", "docs/planning/vertical-slices/SLI-0024-open-and-return-to-an-eligible-activity.md", "docs/planning/register.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 6842d92c1c538f995bcce6345b4450bf63922311
claim_id: WRK-0086:880f791c-f972-48f4-a37c-dfbb8706bf08
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T12:28:56Z
---

# Agent Work Packet: Compose the Protected Activity-Launch API

## Objective and Deliverable

Compose the accepted WRK-0085 activity-launch decision through the existing
provider-neutral Adaptation application service and expose one protected,
bodyless, exact-version GET through the reviewed OpenAPI contract and generated
TypeScript client. One request must open the current exact graph and completion
facts, evaluate navigation state once, resolve the requested lesson against
that same graph/projection pair, and return only the closed v1 launch value.

The endpoint resolves learner identity from the server session and requires
both existing `adaptation.navigation.read` and `curriculum.lesson.read`
permissions. It accepts no learner, destination, placement, package,
eligibility, state, policy, or fallback-version selector.

## Required Context

Read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, learning-adaptation,
architecture-contracts, security-risk, testing-quality, and delivery-planning
context. Read CAP-0005, SLI-0024, WRK-0085, SLI-0023 and WRK-0063; decision
readiness; ADR-0005, ADR-0006, ADR-0007, ADR-0009, and ADR-0014; the Curriculum
graph, Navigation-state, learner-context, and activity-launch contracts; the
Adaptation application/public surface; API models/host and reviewed snapshot;
generated-client tooling and consumers; affected tests; and nearest READMEs.

## Decisions and Assumptions

- Adaptation continues to own deterministic launch authorization. The host
  resolves identity and checks existing permissions but does not duplicate
  activity or eligibility policy.
- The application request contains the server-resolved learner ID plus exact
  curriculum ID, version, and activity ID. The public operation returns the
  existing `ActivityLaunchResolution` and does not persist a launch grant.
- One private application composition produces the exact graph and its current
  projection together. Navigation-state reads and launch reads share that
  composition so the resolver cannot combine different graph snapshots.
- The launch resolver is invoked only after all current Curriculum and
  Learner-model sources have been evaluated. WRK-0085 remains authoritative
  for success shape, destination derivation, and denial precedence.
- Invalid path context maps to a bounded 400, absent activity or curriculum to
  404, locked/unsupported activity to 409, and unavailable source/composition
  state to 503. Permission failures retain the existing 401/403 envelopes.
- The endpoint is a current read/decision and uses GET with no body or query.
  It creates no evidence, recommendation, history, completion, or external
  action.

## In Scope

- `OpenActivityLaunchRequest` and `AdaptationOperations.open_activity_launch`
  on the public application boundary.
- Refactoring the existing application composition so graph loading, source
  observation, UTC evaluation, and launch resolution use one fresh exact
  context without changing Navigation-state v1 behavior.
- Closed API response modeling from `activity_launch_payload`, bounded domain
  error mapping, a launch-specific dependency requiring both current
  permissions, and exact path/query/body rejection.
- One additive exact-version route:
  `GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch`.
- Deterministic OpenAPI snapshot and TypeScript client regeneration plus one
  compile-time client usage proving only the three path identifiers are
  accepted.
- Focused application, authorization, error, flexible-graph, OpenAPI, client,
  architecture, documentation, and excessive-rigidity tests.

## Out of Scope

Learner-facing buttons, routing, return context, current-position presentation,
lesson-page changes, component/browser tests, CSS, design tokens, persistence,
migrations, events, durable launch grants, ranking, recommendation, automatic
selection, model inference, mastery, assessment execution, new permissions,
identity/tenancy changes, providers, queues, or live-stack qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Adaptation application | Current graph/source composition and WRK-0085 resolver | service, public protocol, focused tests, README | Compose one fresh exact launch without duplicating policy |
| API host | Current protected graph/navigation/lesson routes and error envelopes | app, models, focused integration test, host README | Add the bodyless dual-permission operation and bounded mappings |
| Reviewed API/client | OpenAPI generator/snapshot and deterministic client generator | snapshot, generated files, contract usage, API/web README | Publish an additive reproducible public operation |
| Architecture evidence | Public-boundary fitness tests and adaptive-navigation contract | bounded assertions/documentation | Preserve module ownership and generated-client direction |
| Planning evidence | SLI-0024 and register | this packet, parent slice, register | Keep JIT-B lifecycle and evidence synchronized |

No Curriculum, Learner-model, Identity, Assessment, persistence, bootstrap,
deployment, browser-feature, or design-system implementation may change.

## Contracts and Interfaces

The application request is a frozen value with `learner_id`, `curriculum_id`,
`curriculum_version`, and `activity_id`. It validates the same learner and
exact curriculum context as `OpenNavigationStateRequest`, validates the
activity identifier through the accepted launch resolver, and returns the
existing immutable `ActivityLaunchResolution`. `open_navigation_state` remains
compatible and delegates to the same graph/projection composition.

The HTTP success response is the closed activity-launch v1 payload already
defined by WRK-0085. It includes exact graph/projection/lesson-package
provenance and the derived same-origin lesson path, but no learner/session,
permission, source payload, answer, score, provider, or arbitrary URL. Every
denial returns the standard error envelope and no destination.

The reviewed OpenAPI operation ID is `getCurriculumActivityLaunch`. It has
exactly three required path parameters, no query/header/cookie authority
selectors beyond the existing opaque session security scheme, and no request
body. The generated client must expose that exact operation without hand-edited
types.

## Dependencies and Parallel Safety

WRK-0085 is complete and freezes the launch v1 contract, resolver, denials, and
compatibility corpus. WRK-0086 is serial with JIT-C because it owns the
generated operation JIT-C will consume. It is not parallel-safe with other
work touching Adaptation, the API snapshot/client, architecture evidence, or
SLI-0024 planning files. No active edit lease may overlap its scope.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Eligible or completed lesson | Current exact graph/projection says the requested lesson is eligible | Protected launch GET runs | Closed v1 response returns the exact derived lesson destination and provenance | application + API |
| One fresh context | Graph/source observations are instrumented | Launch operation runs | The graph is opened once, facts are evaluated once, and resolver receives that matching pair | application unit |
| Locked lesson | Current prerequisite evidence leaves the lesson locked | Direct endpoint call runs | 409 uses the stable launch code and contains no destination | application + API |
| Unavailable source | Graph, lesson, completion, or current evaluation is unavailable | Endpoint runs | 503 is bounded and no stale or partial launch is returned | application + API |
| Missing or unsupported activity | Activity is absent or is an assessment | Endpoint runs | 404 or 409 is stable and no lesson behavior is inferred | application + API |
| Unauthorized request | Session is absent or lacks either existing permission | Endpoint runs | 401/403 occurs before Adaptation and no graph/state/destination leaks | API integration |
| Selected authority | Client adds learner, destination, state, placement, package, policy, or query inputs | Endpoint runs | Contract validation rejects the request and Adaptation is not called | API/OpenAPI |
| Flexible graph | Optional, unbranched, reordered, multiple-entry, or shared same-kind branches are used | Same service/endpoint runs | Only exact activity/state meaning controls launch; no shape special case is added | anti-rigidity unit/API |
| Deterministic generation | Source models and route are unchanged | Snapshot/client regenerate | Bytes stay current and compile-time usage accepts only exact path inputs | generation + TypeScript |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/adaptation/test_activity_launch_application.py backend/tests/unit/adaptation/test_navigation_application.py backend/tests/integration/api/test_single_profile_activity_launch_api.py backend/tests/architecture/test_module_boundaries.py`
- `backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/adaptation_activity_launch backend/tests/contract/adaptation_navigation backend/tests/integration/api/test_single_profile_navigation_state_api.py`
- `backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check`
- `npm --prefix apps/web run generate:api -- --check`
- `npm --prefix apps/web test -- --run apps/web/tests/contract/generated-client.test.mjs`
- `npm --prefix apps/web run typecheck`
- `backend/.venv/Scripts/python.exe dev-tools/architecture/check_architecture.py`
- `backend/.venv/Scripts/python.exe dev-tools/planning/check_planning.py`
- `backend/.venv/Scripts/python.exe dev-tools/documentation/check_docs.py`
- `backend/.venv/Scripts/python.exe dev-tools/agent/check_ready.py`
- `git diff --check`

The complete backend and live browser/PostgreSQL qualification remain JIT-D;
this packet uses in-process application/API collaborators and exact generation
checks at the boundary it changes.

## Documentation and Evidence Update

Update the Adaptation and host READMEs, API contract catalog, generated-client
README, adaptive-navigation/activity-launch contract, this packet, SLI-0024,
and register. Record exact endpoint/permission/error mappings, one-context
composition, generated artifacts, focused and aggregate checks,
anti-rigidity evidence, assumptions, known gaps, and migration
non-applicability. Tracked files must not contain approval or reviewer data.

## Implementation Evidence

- `AdaptationService.open_activity_launch` now composes one exact graph and
  current Navigation-state projection through the same private application
  path, then invokes the accepted WRK-0085 resolver with that matching pair.
  Instrumented tests prove one graph open and one source-evaluation pass.
- The public protocol exposes the composed operation without moving policy to
  the host. The protected bodyless GET resolves learner context from the opaque
  session, requires both existing navigation-read and lesson-read permissions,
  rejects every query and request body before Adaptation, and accepts only the
  three exact path identifiers.
- The host maps invalid context to 400, missing activity or graph to 404,
  locked/unsupported activity to 409, and unavailable current sources to 503.
  Every error uses the standard bounded envelope and returns no destination.
- The reviewed OpenAPI snapshot and deterministic TypeScript client publish
  `getCurriculumActivityLaunch` with the closed activity-launch response and no
  request body or caller-selected authority fields.
- Focused application/API/architecture verification passed 49 tests. Adjacent
  launch/navigation contract and navigation API regression passed 42 tests.
  Compilation, architecture fitness functions (15 tests), OpenAPI/client
  determinism, generated-client contract use, TypeScript typecheck, planning,
  documentation, whitespace, and all 29 aggregate readiness checks passed.
- Flexible optional and newly prerequisite-constrained lesson shapes, direct
  locked/unavailable/missing/assessment requests, absent permissions, selected
  query authority, and body input are covered without graph-shape branches or
  a lower-level approval loop. No migration, persistence, event, UI policy,
  new permission, identity/tenancy behavior, model/ranking/mastery authority,
  provider coupling, queue, cloud choice, or external action was added.

## Stop Conditions

Stop for a need to change activity-launch or Navigation-state v1 meaning;
caller-selected learner/destination/state/placement/package/policy; inferred
assessment completion; a new permission or identity/tenancy model; persistence,
migration, recommendation, model, mastery, provider, queue, cloud, external
action, breaking API behavior, active file overlap, stale CAP authority,
canonical conflict, or material CAP/SLI drift.

Do not stop or request another approval for bounded implementation/test
corrections, exact generated bytes, harmless formatting, advisory prose, or
nonfunctional style. Correct those within this accepted packet or defer
optional polish to CAP-0031.

## Required Handoff

Report the application operation, single-context composition, dual-permission
boundary, endpoint and generated-client surface, error/status mapping, exact
candidate, focused/adjacent/generation/architecture/planning/documentation/
readiness results, anti-rigidity evidence, assumptions, known gaps, and absence
of persistence, migration, UI policy, new identity authority, model/ranking/
mastery behavior, provider coupling, or external action. Leave JIT-C able to
consume one generated launch operation or return one bounded blocker.

## Planning History

- 2026-10-16: Authored just in time after WRK-0085 completion. The packet
  composes the frozen launch decision through the existing fresh
  graph/navigation application path, protects it with both accepted read
  permissions, and publishes only the additive exact operation needed by
  JIT-C. It remains within the approved CAP-0005 package and introduces no
  decision or lower-level approval gate.
- 2026-10-16: Activated from base
  `6842d92c1c538f995bcce6345b4450bf63922311` after the implementation gate
  prerequisites confirmed current CAP authority, completed dependency, exact
  bounded scope, reproducible generated artifacts, and no unresolved decision
  or active ownership collision.
- 2026-10-16: Implemented the single-context application composition,
  dual-permission bodyless endpoint, bounded denials, reviewed OpenAPI, and
  generated client. Focused, adjacent, architecture, generation, TypeScript,
  planning, documentation, whitespace, and aggregate-readiness evidence passed;
  the exact candidate entered verification and independent review.
