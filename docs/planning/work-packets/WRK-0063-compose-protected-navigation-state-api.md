---
id: WRK-0063
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0023
capability: CAP-0005
depends_on: ["WRK-0062"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/adaptation/application/", "backend/src/financial_ai_academy/modules/adaptation/ports/", "backend/src/financial_ai_academy/modules/adaptation/adapters/", "backend/src/financial_ai_academy/modules/adaptation/public.py", "backend/src/financial_ai_academy/modules/adaptation/README.md", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/identity/README.md", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/tests/unit/adaptation/", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/integration/api/", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/README.md", "contracts/api/openapi.json", "apps/web/src/generated/api-client/", "apps/web/tests/contract/generated-client.test.mjs", "apps/web/README.md", "deployments/local/serve.py", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/architecture/contracts/identity-provider-contract.md", "docs/planning/work-packets/WRK-0063-compose-protected-navigation-state-api.md", "docs/planning/vertical-slices/SLI-0023-explain-deterministic-curriculum-state.md", "docs/planning/register.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 2698d088ca18e3af7dd5832a9b3e4553d6b13217
claim_id: WRK-0063:c391a755-a007-4ea1-a600-c03c37d756b2
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T00:34:38Z
---

# Agent Work Packet: Compose the Protected Navigation-State API

## Objective and Deliverable

Implement the provider-neutral Adaptation application composition that opens
one exact Curriculum graph, maps current Learner-model completion through
public gateways into the WRK-0062 source-fact contract, evaluates the pure
policy, and exposes the result through one protected exact-version GET and the
generated TypeScript client. The completed packet returns a closed complete
navigation-state projection for the authenticated learner context without a
client learner selector, persistence, model inference, browser-owned policy,
or a changed v1 meaning.

## Required Context

Before changing any file, the implementing agent must read and follow every
applicable `AGENTS.md` and the repository-root `docs/README.md`, then apply its
routing, impact, and decision-readiness instructions. Read the parent CAP-0005
and SLI-0023 artifacts; WRK-0062 and its executable Adaptation contracts;
ADR-0005, ADR-0006, ADR-0009, and ADR-0014; the adaptive-pathway architecture;
the module map, dependency rules, contract architecture, learner-context
contract, and adaptive-navigation contract; Curriculum, Learner-model,
Identity, Adaptation, bootstrap, host, API-contract, and web generated-client
READMEs; and the affected public surfaces, composition, consumers, and tests.

## Decisions and Assumptions

- Adaptation owns deterministic eligibility and the application orchestration
  that converts accepted public Curriculum and Learner-model meanings into the
  v1 projection. Cross-module adapters import public surfaces only.
- The request contains server-resolved `learner_id` plus exact curriculum ID
  and version. The HTTP operation accepts no learner, actor, permission,
  provider, latest-version, or policy selector.
- Curriculum graph reads retain their existing exact-version not-found and
  unavailable meaning. Every activity source is checked through Curriculum's
  public exact placement operations; a missing or mismatched exact activity
  source becomes an `unavailable` activity fact rather than an alternate
  version or partial projection.
- Existing Learner-model lesson completion maps only lesson activities to
  `completed` or `incomplete` with its exact source digest. An unavailable or
  inconsistent lesson-completion projection maps to `completion=unavailable`
  without copying its error text. Assessment activities remain
  `completion=unavailable` because no accepted assessment-activity completion
  projection exists; their exact public definition digest supplies the bounded
  source digest. This is a fail-closed mapping, not a new completion meaning.
- Source availability and completion remain orthogonal. A Curriculum source
  failure does not erase a valid completion fact, and a completion-source
  failure does not rewrite Curriculum availability.
- Evaluation time comes from an injected UTC clock. The application service,
  adapters, API host, and generated client do not change the WRK-0062 policy,
  state enums, reason order, or digest algorithms.
- Identity adds one application-issued `adaptation.navigation.read` permission
  for the existing single-profile context. This does not change provider,
  learner, tenancy, account, session, or authorization semantics.
- Local and future cloud compositions use the same ports and application
  service. This packet selects no cloud, model, provider, queue, migration, or
  persistence technology.

## In Scope

- An Adaptation public application request and bounded operation error for one
  exact learner-context navigation-state read.
- Adaptation-owned ports and adapters for Curriculum graph/activity-source
  reads, Learner-model lesson-completion mapping, and an injected UTC clock.
- A framework-free application service that validates context, obtains exact
  source closure, calls the WRK-0062 pure policy once, and returns no partial
  result.
- Bootstrap and local serving composition through public operations only.
- One protected exact-version GET, closed Pydantic response models, bounded
  error mapping, OpenAPI regeneration, and deterministic generated TypeScript
  client regeneration.
- The application-issued navigation-read permission and matching canonical
  identity/API documentation.
- Unit, adapter, API, generated-client, architecture, authorization, failure,
  determinism, and excessive-rigidity tests.

## Out of Scope

- Browser route calls, map/list annotations, visual labels, CSS, activity
  launch, return navigation, current-position history, or accessibility/visual
  qualification; those are JIT-C and later work.
- New Curriculum or Learner-model contracts, assessment-activity completion
  meaning, completion inference from graph presence, or mutation of source
  evidence.
- Adaptation persistence, cache, migration, durable eligibility history,
  recommendation, ranking, mastery, competency publication, experiment, model,
  AI explanation, manual override, or organization policy.
- Caller-selected identity, a new identity mode, tenancy, public registration,
  session changes, provider payloads, API policy selectors, or external action.
- Live browser/PostgreSQL end-to-end qualification, recovery, background jobs,
  managed-cloud composition, or production deployment.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Adaptation application | WRK-0062 public/domain seam and Curriculum/Learner-model public operations | Adaptation application, ports, adapters, public facade, README | Compose exact authoritative inputs without importing another module's internals |
| Identity authorization | learner-context contract, current read permissions and identity tests | single-profile permission tuple, Identity README, learner-context contract | Add one server-issued operation capability without accepting client authority |
| Host/bootstrap | current graph/completion routes, bootstrap and local serve composition | bootstrap, API app/models, host/bootstrap READMEs, local serve wiring | Expose one thin protected transport over the Adaptation public operation |
| Reviewed API/client | OpenAPI generator/snapshot, generated-client script and contract tests | API README/snapshot and generated TypeScript files/tests | Publish the exact additive GET shape reproducibly |
| Verification | current adaptation, identity, graph, completion, API, and architecture tests | focused Adaptation unit/adapter/API tests, bounded existing test updates | Prove mapping, authorization, failure, ordering, and dependency direction |
| Canonical architecture | adaptive navigation and identity contracts | those contract docs only as required | Record the implemented application/transport boundary and permission |
| Planning evidence | CAP-0005, SLI-0023, register | this packet, parent packet table/history, register | Keep lifecycle and bounded scope synchronized |

No persistence schema, migration, Curriculum implementation, Learner-model
implementation, Assessment implementation, web feature, design-system asset,
or deployment configuration may change.

## Contracts and Interfaces

The public application request is a frozen typed record with `learner_id`,
`curriculum_id`, and `curriculum_version`. It returns the existing
`NavigationStateProjection`. Its bounded operation errors distinguish invalid
context, exact graph not found, and unavailable source/composition state without
exposing another module's error, repository detail, learner identity, or
provider payload.

Adaptation-owned ports accept only provider-neutral values. The Curriculum
adapter may import `curriculum.public`; the Learner-model adapter may import
`learner_model.public`; neither application nor domain imports another module's
internals. The source-fact mapping preserves exact graph order and produces one
fact per activity. Lesson completion uses the exact public completion view;
assessment completion stays unavailable until a separate accepted public
meaning exists.

The additive endpoint is:
`GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state`.
It requires an opaque session and server-issued
`adaptation.navigation.read`, resolves `learner_id` only from the context, and
returns the exact v1 projection schema. The reviewed OpenAPI snapshot generates
`getCurriculumNavigationState`; the operation accepts only the two path values
and normal request options.

JIT-C may consume only that generated operation and the closed response. It
must not call the raw graph/completion endpoints to recompute state, infer
unsupported assessment completion, or duplicate policy.

## Dependencies and Parallel Safety

WRK-0062 is complete and supplies the accepted state, reason, error, ordering,
canonicalization, and digest contract. This packet is the sole JIT-B seam and
must finish before JIT-C because it owns the response and generated client that
the browser will consume. It overlaps host, generated API, Identity permission,
and planning files with later packets, so it is not parallel-safe with them.
No active packet may overlap its exact scope or generated artifacts.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Authorized exact state | A valid session, exact graph, available lesson sources, and current lesson-completion views | The protected operation runs | It returns one complete v1 projection in graph order with exact graph/policy/source/result provenance and no learner identifier | Application and API tests |
| Incomplete then complete lesson | The same lesson activity first has no accepted evidence and later exact retained completion | Each source set is evaluated | Completion changes from incomplete to completed and dependent eligibility follows the WRK-0062 policy without a mastery claim | Gateway/application test |
| Unsupported assessment completion | A valid assessment activity has no accepted activity-completion projection | The source mapper runs | Its activity source may remain available while completion and eligibility fail closed as unavailable with no inferred completion | Unit/API contract test |
| Orthogonal degradation | Curriculum activity availability and Learner-model completion independently succeed or fail | Composition runs | Each dimension retains its own meaning; every activity still appears exactly once and no upstream error text is exposed | Anti-rigidity parameterized test |
| Flexible graph | Activities are reordered, presentation hints are absent, optional branches are shared, activities are unbranched, or entry count varies | The same application/API operation runs | The output preserves complete graph order and compatible shapes without a route/model revision | Anti-rigidity API test |
| Exact graph missing or stale | The requested identity/version is absent or the stored graph is invalid | The operation runs | It returns bounded 404 or 503 and no partial/latest projection | Adapter/API test |
| Unauthorized or selected authority | The session is missing/insufficient or the client supplies learner/permission/policy selectors | The GET is attempted | Access fails before Adaptation and unsupported selectors are rejected; no learner or state data is returned | API integration test |
| Deterministic contract generation | The API models and operation are unchanged | OpenAPI and client generation rerun | Snapshot and generated TypeScript bytes remain clean and the operation has no learner selector | Generation/contract test |
| Boundary enforcement | Source imports and repository tree are inspected | Architecture tests run | Adaptation adapters import only public module surfaces; application/domain remain provider, framework, and persistence neutral | Architecture test |

## Verification Commands

Run from the repository root:

```powershell
uv run --project backend pytest backend/tests/unit/adaptation backend/tests/unit/identity/test_identity_service.py backend/tests/integration/api/test_single_profile_navigation_state_api.py backend/tests/architecture/test_module_boundaries.py
uv run --project backend pytest backend/tests/contract/adaptation_navigation backend/tests/contract/curriculum_graph backend/tests/unit/learner_model/test_completion_service.py backend/tests/integration/api/test_single_profile_curriculum_graph_api.py backend/tests/integration/api/test_single_profile_completion_api.py
python -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web test -- --run apps/web/tests/contract/generated-client.test.mjs
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/architecture/check_architecture.py
python .agents/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0063-compose-protected-navigation-state-api.md
python dev-tools/agent/check_ready.py
git diff --check
```

Run the complete backend suite against the qualified local PostgreSQL service
before submission. The packet's API integration uses in-process public fakes;
the real PostgreSQL/Python/static-browser path remains the final JIT-D boundary.

## Documentation and Evidence Update

Update the Adaptation, Identity, host, bootstrap, API-contract, and web
generated-client READMEs; reconcile the adaptive-navigation and learner-context
contracts with the implemented application/API seam; and update the parent
slice packet table/history plus planning register. Record the exact mapping
matrix, endpoint and permission, error profile, generated artifacts, focused
and aggregate checks, anti-rigidity evidence, assumptions, and known gaps. Do
not add approval or reviewer metadata to tracked files.

## Stop Conditions

Stop for a need to infer assessment-activity completion; change Curriculum or
Learner-model public meaning; change navigation-state v1 fields, rules, reasons,
ordering, canonicalization, or digests; persist Adaptation state; add a model,
rank, recommendation, mastery/competency claim, override, organization policy,
caller-selected identity, provider field, tenant behavior, new identity mode,
cloud/service choice, migration, browser policy, external action, or breaking
API/client change. Also stop for conflicting canonical authority, stale CAP
approval, material CAP drift, active scope/generated-artifact overlap, or a
failed exact generation or verification boundary.

## Required Handoff

Report the exact candidate revision; changed application/adapter/permission/
host/API/client/doc/test paths; the graph, availability, completion, assessment,
error, authorization, time, and provenance mappings; focused, full-backend,
generation, architecture, documentation, planning, readiness, and control-plane
results; anti-rigidity evidence; assumptions and known gaps; and confirmation
that no persistence, migration, UI policy, learner selector, model, ranking,
recommendation, mastery, or external authority was added. Leave JIT-C able to
consume one exact generated operation, or return a bounded blocker.

## Planning History

- 2026-10-16: Authored just in time after WRK-0062 completion. The packet
  composes the frozen navigation-state contract through existing public
  Curriculum, Learner-model, and Identity seams, adds the protected transport
  and generated client needed by JIT-C, and remains within the approved
  CAP-0005 outcome, ordering, non-goals, risk, and decision posture.
- 2026-10-16: Activated after the current CAP package binding, completed
  WRK-0062 dependency, implementation gate, exact generated artifacts, and
  bounded write scope were revalidated.
- 2026-10-16: Released to ready before implementation because an expired grouped
  file lease required a bounded correction to the reusable file-coordination
  control. No WRK-0063 implementation file was changed and its scope is stable.
