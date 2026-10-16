---
id: WRK-0076
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0124
capability: CAP-0030
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/lesson-reading/LessonRoute.tsx", "apps/web/src/features/lesson-reading/LessonReadingPage.tsx", "apps/web/tests/component/lessonReadingPage.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0076-clarify-lesson-context-and-recovery.md", "docs/planning/vertical-slices/SLI-0124-understand-lesson-check-and-completion.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 6d6478927f6bd64d7e89745c642e19bbaa5cc487
claim_id: WRK-0076:0167f10b-d260-40d6-92f8-399ae9c4d694
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:36:21Z
---

# Agent Work Packet: Clarify Lesson Context and Recovery

## Objective and Deliverable

Apply the accepted learner-facing language contract to lesson loading, ready-
page publication context, and bounded route failures. A learner understands
what is opening, where the lesson came from, what could not be shown, and the
existing safe next action without package, exact-version, private-session, or
validator wording dominating the task. Exact lesson publication and integrity
facts remain complete in an accessible `Technical record` disclosure.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`,
`testing-quality`, and relevant learning/context packs. Read CAP-0030,
SLI-0124, WRK-0068, the user-facing language and content-style standards, the
content-package and identity contracts, ADR-0006/0007, the risk limitation,
lesson route/page/model/API, shared `StatusPanel`, focused component tests, and
`apps/web/README.md` before editing.

## Decisions and Assumptions

- Route-state selection, server-owned session establishment, authorization,
  exact placement/version resolution, content validation, and retry wiring are
  unchanged; only presentation and focused evidence change.
- Publication dates and publisher are useful supporting facts in the ordinary
  flow. Package ID/version/digest are exact technical facts and remain labeled,
  selectable, and reachable under `Technical record` on the same page.
- Educational-use and investment-advice language keeps its current meaning and
  prominence; this packet does not rewrite that disclosure.
- Tests protect semantic roles, state/action meaning, protected-fact absence,
  and technical-record completeness rather than entire prose or styling.
- Whitespace, copy fit, and nonfunctional styling do not trigger re-review.

## In Scope

- Lesson loading eyebrow, heading, description, and accessible status copy.
- Ready-page orientation and publication-context terminology, including an
  accessible native `Technical record` disclosure for exact package facts.
- Plain titles, descriptions, and existing action labels for unauthorized,
  forbidden, not-found, unavailable, invalid-content, and unexpected states.
- Focused component evidence for ready-page hierarchy, publication facts,
  technical-record reachability, all bounded states/actions, and absence of
  avoidable technical language in route-owned messages.
- Minimal web README and planning/evidence reconciliation.

## Out of Scope

- Knowledge-check and saved-completion presentation, which is JIT-B; complete
  Chromium/live qualification and slice closure, which is JIT-C.
- Route parsing, model/API/session/authorization/content-validation behavior;
  public/generated contracts; sources or lesson body; new actions; CSS, tokens,
  icons, layout polish, localization, persistence, or external services.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Canonical/runtime boundary | content/identity contracts, lesson model/API/session behavior | none | Confirm exact lesson and safe session semantics remain unchanged |
| Lesson presentation | lesson route and reading page | named route/page only | Clarify task, publication context, technical record, and bounded failures |
| Focused evidence | lesson component tests | named lesson test only | Protect facts, actions, accessibility, and non-rigid language outcomes |
| Documentation/planning | web README, packet, parent slice, register | named files | Reconcile delivered result and evidence |

## Contracts and Interfaces

The packet consumes the unchanged closed `LessonRouteState` union and exact
validated `Lesson` model. It produces no API, schema, generated-client, route,
domain, persistence, event, or session change. `LessonReadingPage` keeps every
title, objective, body node, source, publication date, publisher, review date,
package ID/version/digest, and educational-use fact.

JIT-B receives the unchanged knowledge-check insertion point. JIT-C receives
stable learner-facing headings/actions and a native `Technical record`
disclosure for browser assertions.

## Dependencies and Parallel Safety

The completed SLI-0122 language contract is the only implementation dependency.
This packet is serial within SLI-0124 because later packets share the lesson
feature and browser flow. Its bounded lease does not block unrelated work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Loading | The route is establishing context and opening the lesson | Loading state renders | It says the lesson is opening without exact/private/session-establishment wording | Component test |
| Ready lesson | A validated exact lesson is available | Page renders | The learner sees purpose, objectives, body, sources, publication details, and educational-use limitation | Component test |
| Technical record | The ready lesson has exact package facts | Disclosure opens | Package ID, version, and digest remain labeled, selectable, keyboard reachable, and screen-reader understandable | Component test |
| Session failure | Session establishment fails | State renders | It says the learner session could not start, no private details were shown, and offers the existing retry | Component test |
| Permission or missing lesson | Access is denied or the exact placement is absent | State renders | It states the result without leaking lesson facts or implying another version was substituted | Component test |
| Temporary or invalid content | Loading fails or content is rejected | State renders | It states that the lesson could not be shown, preserves the learning record, and offers only the existing safe action | Component test |
| Unexpected failure | The request fails unexpectedly | State renders | It gives the existing retry and exposes no technical/private detail | Component test |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/component/lessonReadingPage.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0076`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Chromium and approved-lesson live qualification are owned by JIT-C. Backend,
database, generated-client, and live suites are not required unless affected
routing selects them.

## Documentation and Evidence Update

Update `apps/web/README.md` only where lesson presentation is described. Update
this packet, SLI-0124, and the register together. Store approval and reviewer
records only in the ignored local ledger/control state.

## Stop Conditions

Stop for changed route-state selection, session, authorization, exact-version,
retry, content validation, safe rendering, privacy, publication, provenance,
educational-use, or advice meaning; removal of a technical fact; a new action;
contract/model/API changes; canonical conflict; CAP drift; or a colliding lease.
Do not stop or reopen review for whitespace, copy fit, or nonfunctional visual
polish; fix it locally when trivial or defer it to CAP-0031.

## Required Handoff

Report revised lesson/loading/recovery meaning, preserved exact-version/session/
publication boundaries, focused and affected verification, aggregate readiness,
assumptions, work left to JIT-B/JIT-C, and any cosmetic issue deferred to
CAP-0031.

## Planning History

- 2026-10-16: Refined SLI-0124 JIT-A around lesson loading, publication context,
  accessible exact technical facts, bounded route failures, focused semantic
  evidence, and explicit exclusion of assessment behavior and visual polish.
