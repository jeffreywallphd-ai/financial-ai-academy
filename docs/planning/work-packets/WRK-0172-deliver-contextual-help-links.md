---
id: WRK-0172
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0083
capability: CAP-0020
depends_on: [WRK-0171]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/router.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesPage.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesRoute.tsx", "apps/web/src/features/lesson-reading/LessonReadingPage.tsx", "apps/web/src/features/lesson-reading/LessonRoute.tsx", "apps/web/src/features/platform-help/ContextualHelpLinks.tsx", "apps/web/src/features/platform-help/PlatformHelpPage.tsx", "apps/web/src/features/platform-help/PlatformHelpRoute.tsx", "apps/web/src/features/platform-help/api.ts", "apps/web/src/features/platform-help/model.ts", "apps/web/src/features/practice-activity/PracticeActivityPage.tsx", "apps/web/src/features/practice-activity/PracticeActivityRoute.tsx", "apps/web/src/features/project-workspace/ProjectDetailPage.tsx", "apps/web/src/features/project-workspace/ProjectRoutes.tsx", "apps/web/src/styles/platform-help.css", "apps/web/tests/browser/assistance-preferences/assistance-preferences.spec.ts", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts", "apps/web/tests/browser/platform-help/platform-help.spec.ts", "apps/web/tests/browser/practice-activity/practice-activity.spec.ts", "apps/web/tests/browser/project-workspace/project-workspace.spec.ts", "apps/web/tests/component/assistancePreferences.test.tsx", "apps/web/tests/component/lessonReadingPage.test.tsx", "apps/web/tests/component/platformHelp.test.tsx", "apps/web/tests/component/platformHelpFixture.ts", "apps/web/tests/component/practiceActivity.test.tsx", "apps/web/tests/component/projectWorkspace.test.tsx", "apps/web/tests/unit/platformHelpModel.test.ts", "docs/architecture/contracts/platform-help-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0083-open-contextual-method-and-limitation-help.md", "docs/planning/work-packets/WRK-0172-deliver-contextual-help-links.md"]
generated_artifacts: []
base_revision: 693c936aa2d5e3eda919d76b0f3899810098c089
claim_id: WRK-0172:b8fc54d6-52e6-40ab-98b5-7764aca9d281
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T04:40:34Z
---

# Agent Work Packet: Deliver Contextual Help Links

## Objective and Deliverable

Use the generated public client to read one exact Guidance context and show its
server-owned learner labels beside the delivered lesson-publication,
practice-result, Project artifact/result, and AI-assistance surfaces. Each link
opens its exact reviewed topic and returns through a closed same-origin target
to the unchanged originating feature. Missing, denied, stale, malformed, or
unavailable optional Help must leave the feature fully usable.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md`,
`docs/README.md`, the context-pack index/routing/catalog, change-impact matrix,
decision readiness, planning guide/register, CAP-0020, SLI-0083, WRK-0171,
platform-help contract, executable contextual-help schema, Guidance/Web
READMEs, generated client, affected feature consumers and tests, design guide,
content style guide, user-facing language standard, icon rules, and nearest
styles. Inspect the complete contract-to-reader-to-route-to-feature path.

## Decisions and Assumptions

- The approved CAP selects a Guidance-owned exact context registry and public
  API; feature code supplies only its closed context key/version.
- The existing `guidance.platform_help.read` permission and generated
  `getContextualHelpVersion` operation are authoritative.
- Contextual Help is optional enhancement. Its absence does not disable,
  reinterpret, or mutate the owning feature.
- Feature return locations are a closed Web navigation concern. They are not
  added to canonical Guidance records and are never accepted as arbitrary
  cross-origin, credentialed, hashed, or unrelated destinations.
- Presentation reuses existing semantic tokens and link/card patterns. Optional
  styling polish is nonblocking and may remain for CAP-0031.

## In Scope

- Close and validate the complete generated `ContextualHelpResponseModel` in
  the Web boundary, including exact requested identity, references, source and
  publication facts, duplicate rejection, bounds, and varied valid ordering.
- Add a reusable generated-client reader with one bounded 401 renewal and an
  optional, abortable feature link group that renders only server-returned
  labels and exact topic identities.
- Add contextual links to the four approved surfaces without changing their
  feature APIs, domain meaning, mutation behavior, or primary task flow.
- Extend exact topic return navigation only for closed lesson, practice,
  Project-detail, AI-assistance, and platform-guide destinations. Preserve the
  complete allowed lesson return query and derive plain return labels locally.
- Add focused model, component, and Chromium accessibility/failure/anti-
  rigidity evidence and reconcile Web/contract/planning documentation.

## Out of Scope

- New backend, OpenAPI, generated-client, schema, persistence, migration,
  permission, identity, provider/model, analytics, personalization, search,
  feature behavior, external action, advice, grading, mastery, or competency
  behavior.
- Contextual troubleshooting for unavailable feature states (SLI-0084), live
  browser/headless/restart containment qualification (later SLI-0083 packet),
  or corpus-wide closure (SLI-0085).
- Arbitrary return URLs, browser-owned topic mapping, static duplicate Help
  copy, route data in Guidance records, visual redesign, or pixel snapshots.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance API/client | contextual v1 schema, OpenAPI, generated client, WRK-0171 evidence | no generated/backend change | Consume the already reviewed exact operation |
| Web Help boundary | model, API, Help routes/pages, shared styles | yes | Validate, read, render exact links, and close return destinations |
| Feature consumers | lesson, practice, Project detail, AI-assistance pages/routes | yes | Supply only the approved context key/version and reader |
| Feature contracts/state | feature models, APIs, backend modules, storage | inspect only | Contextual Help cannot reinterpret or gate feature behavior |
| Verification | focused unit/component/browser suites | yes | Prove exactness, safe return, optional failure, accessibility, and flexibility |
| Documentation/planning | Web README, Help contract, packet/slice/register | yes | Keep public behavior and governed state synchronized |

## Contracts and Interfaces

Consume WRK-0171's protected exact
`GET /api/v1/guidance/contextual-help/{context_key}/versions/{context_version}`
operation and the generated `ContextualHelpResponseModel`. Produce a reusable
reader outcome that is either one fully validated exact context or an optional
unavailable result; never expose partial records. Feature link groups accept a
closed context key/version and derive their return from the current supported
route. Topic links retain the existing exact identity contract.

## Dependencies and Parallel Safety

WRK-0171 is complete. This packet is sequential and not parallel-safe because
it owns the shared Help model/API/routes and four feature consumer/test seams.
No active lease may overlap its exact scope.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Four bounded surfaces | An authorized feature has an admitted context | Optional Help loads | Server labels open exact topics and return to that feature | component/Chromium |
| Optional failure | Context read is denied, absent, malformed, stale, or unavailable | Feature renders | Primary feature data and actions remain usable; no partial Help appears | API/component |
| Safe return | A topic link contains a supported return or an arbitrary destination | Topic selection parses | Closed destination is retained; unrelated/cross-origin/extended input fails | unit/component |
| Flexible context | A valid context has a different bounded reference count/order/copy | Link group renders | Every valid reference is available without fixture-count or prose assumptions | unit/component |
| Accessibility | Keyboard, narrow/zoomed, themes, forced colors, reduced motion | Learner opens and returns | Links and return action remain named, visible, ordered, and operable | Chromium/axe |

## Verification Commands

```powershell
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0172-deliver-contextual-help-links.md
python dev-tools/planning/check_planning.py
<pinned npm> --prefix apps/web test -- --run apps/web/tests/unit/platformHelpModel.test.ts apps/web/tests/component/platformHelp.test.tsx apps/web/tests/component/lessonReadingPage.test.tsx apps/web/tests/component/practiceActivity.test.tsx apps/web/tests/component/projectWorkspace.test.tsx apps/web/tests/component/assistancePreferences.test.tsx
<pinned npm> --prefix apps/web run test:browser -- tests/browser/platform-help tests/browser/lesson-reading tests/browser/practice-activity tests/browser/project-workspace tests/browser/assistance-preferences
<pinned npm> --prefix apps/web run typecheck
<pinned npm> --prefix apps/web run lint
<pinned npm> --prefix apps/web run build
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
python dev-tools/learner-language/check_learner_language.py
git diff --check
python dev-tools/agent/check_ready.py
```

Then run controller-selected exact-candidate verification and independent
technical review. Live headless/browser restart and containment evidence is
deliberately deferred to the final SLI-0083 qualification packet.

## Documentation and Evidence Update

Document the optional generated-client link group, exact context/topic
correlation, closed return destinations, safe failure, headless contract
continuity, affected learner surfaces, assumptions, and remaining live gap.
Update packet, slice, and register together. Store local claims, receipts,
reviews, and approvals only under ignored `.local-codex` paths.

## Stop Conditions

Stop for a required feature-domain or public-contract change; browser-owned
topic authority; arbitrary or external return navigation; partial/malformed
context rendering; Help gating a primary task; persistence or migration;
provider/model execution; personalization or tracking; new identity,
permission, tenancy, managed-cloud, recovery, legal/commercial, or external-
action policy; stale CAP authority; active scope collision; or material
CAP-0020/SLI-0083 drift.

Do not stop or reopen review solely for whitespace, optional copy, valid
reference count/order, nonfunctional styling, or another inconsequential issue.
Fix it within scope or defer optional presentation polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0083.WRK-0172`; exact candidate and receipt; generated-
client/context validation; all four feature surfaces; topic/return exactness;
optional failure behavior; accessibility and anti-rigidity evidence; checks;
changed files; documentation; assumptions; and the remaining live
qualification gap. Confirm no backend, generated artifact, feature contract,
persistence, identity, provider/model, learner authority, or financial
behavior changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0171 completed. The packet adds
  only generated-client contextual links and closed return behavior to the four
  surfaces already enumerated by approved SLI-0083; no lower-level approval is
  required.
- 2026-10-18: Activated from clean recorded base `693c936` after confirming the
  current CAP binding, completed WRK-0171 dependency, bounded generated-client
  consumer scope, executable checks, and no unresolved decision or collision.
- 2026-10-18: Refined the focused test scope to include its shared contextual-
  help fixture. This bounded test-support addition does not change the outcome,
  CAP boundary, or approval posture.
