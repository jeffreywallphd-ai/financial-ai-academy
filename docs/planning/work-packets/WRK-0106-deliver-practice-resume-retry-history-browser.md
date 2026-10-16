---
id: WRK-0106
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: ["WRK-0105"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/router.tsx", "apps/web/src/features/practice-activity/api.ts", "apps/web/src/features/practice-activity/model.ts", "apps/web/src/features/practice-activity/PracticeActivityPage.tsx", "apps/web/src/features/practice-activity/PracticeActivityRoute.tsx", "apps/web/src/styles/practice-activity.css", "apps/web/tests/browser/practice-activity/practice-activity.spec.ts", "apps/web/tests/component/practiceActivity.test.tsx", "apps/web/tests/component/practiceFixture.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0106-deliver-practice-resume-retry-history-browser.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver Practice Resume, Retry, and History Browser Flow

## Objective and Deliverable

Deliver one accessible learner-facing practice flow that reads the public
progress API, restores and conditionally saves partial answers, shows targeted
review destinations, permits another attempt only while the deterministic retry
state allows it, and compares every retained attempt summary without replacing
or hiding earlier evidence. The browser remains a generated-client consumer of
the same public API available to non-browser and future headless clients.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the routed baseline, web-interface,
practice, contract, security, learner-language, and testing context. Inspect
CAP-0006, SLI-0028, WRK-0102 through WRK-0105, ADR-0005, ADR-0007, ADR-0008,
decision readiness, the change-impact matrix, interface and user-facing
language standards, content style guide, design-system tokens and icons, the
generated progress/draft client types, current practice route/model/API/page,
consumers, focused fixtures and tests, and nearest README before editing.

## Decisions and Assumptions

The public API and generated client produced by WRK-0105 remain authoritative.
The browser must not infer retry eligibility, attempt order, review routing,
scores, completion, or evidence meaning. An explicit `Save progress` action is
the initial bounded resume interaction; it saves the current valid partial
snapshot with the last server revision and gives an observable saved/conflict
result. The browser does not claim background or offline synchronization.

Learner-facing copy follows the three-layer information model: task, status and
next action in the main flow; concise evidence limitations nearby; exact IDs,
versions, digests, policy values, and source references in a keyboard-operable
technical record. Styling uses only shared semantic variables and the reviewed
icon pack. Tests protect behavior and meaning without freezing incidental
wording, timestamps, fixture counts, or one exact visual arrangement.

## In Scope

- Load the exact practice presentation and practice progress through generated
  clients after one opaque-session establishment, including one bounded session
  renewal for unauthorized reads and writes.
- Validate progress, draft, retry, review-target, history, and item-summary
  response shapes fail-closed before rendering; reject extra/private fields and
  mismatched placement/package/definition/practice/policy chains.
- Restore each supported saved response into its matching control, show when it
  was saved, and conditionally save any valid empty or partial response set with
  the last server revision. Keep stale, denied, malformed, unavailable, and
  uncertain-save states explicit without overwriting newer work.
- Continue to submit only complete attempts through the existing generated
  operation and stable retry-safe request. Refresh progress after a confirmed
  result, keep the result readable, and prepare a new attempt only when the
  server-owned retry state says another attempt is available.
- Show remaining attempts, latest targeted review destinations, explicit
  unavailable review resources, and every bounded immutable history summary.
  Compare attempt order, score, outcome, item correctness, completion time, and
  evidence source without showing submitted answers or answer keys.
- Link available review targets only to the exact internal lesson placement;
  preserve an optional section fragment only when it is safe and supported by
  the existing lesson route. Do not accept a server-supplied arbitrary URL.
- Preserve keyboard focus, live status, narrow reflow, zoom, forced colors,
  reduced motion, and equivalent light/dark/system-theme content and actions.
- Update focused component/browser fixtures, tests, and web guidance plus this
  packet, parent slice, and planning register.

## Out of Scope

- API, OpenAPI, generated-client, backend, schema, event, migration, scoring,
  projection, or persistence changes; a second browser-only domain core; or
  browser calculation of retry, review, history, or completion authority.
- Autosave, offline work, multi-device merge, cross-version draft migration,
  draft expiry/reset, reminders, notifications, or a general sync protocol.
- Answers, answer keys, private evaluator declarations, raw response/evidence/
  event documents, learner identifiers, storage fields, or diagnostic payloads
  in the progress/history presentation.
- Mastery, competency, ranking, adaptive recommendation, personalized next
  activity, investment suitability, advice, certification, proctoring, or AI/
  model authority.
- New response types, question authoring, external links/providers, arbitrary
  execution, cloud/tenancy/recovery choices, or styling-only polish beyond what
  is needed for operation, accessibility, hierarchy, and theme parity.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public client seam | Generated progress/draft/submission types and operation IDs | none | Consume the reviewed headless-compatible API without editing generated output |
| Web API adapter | Practice API and session helper | `apps/web/src/features/practice-activity/api.ts` | Compose reads and bounded writes through generated clients with one renewal |
| Browser model | Practice types, validators, form/draft preparation | `apps/web/src/features/practice-activity/model.ts` | Fail closed and translate controls to accepted public request types |
| Route composition | Router and practice route | listed router/route files | Inject the generated-client operations and render only one complete validated state |
| Learner interface | Practice page and feature stylesheet | listed page/CSS files | Resume, save, retry, review, compare, status, technical record, and accessibility behavior |
| Evidence | Feature fixtures, component and Chromium tests | listed test files | Protect flexible shapes, confidentiality, failure recovery, accessibility, and theme parity |
| Guidance and planning | Web README, parent slice, packet, register | listed documentation files | Keep consumer and delivery status current |

## Contracts and Interfaces

Consume `PracticePresentationResponseModel`, `PracticeProgressResponseModel`,
`PracticeDraftSaveRequestModel`, `PracticeDraftResponseModel`, and the existing
practice submission request/result from the generated TypeScript client. The
route-ready value is one exact presentation plus one exact progress response;
no partial successful state is rendered. Draft writes contain only the exact
scope, expected revision, and accepted response union. A save result replaces
only the browser's current draft revision after exact validation.

Use the existing placement route for an available review destination and a
bounded application-owned fragment encoding for an optional safe section ID;
unavailable targets remain non-links with learner-readable status. Attempt
history remains an answer-free read model. The browser may refresh it after a
confirmed submission but may not synthesize an attempt while waiting.

## Dependencies and Parallel Safety

WRK-0105 is complete and supplies the exact public API, generated types, and
production composition. This packet owns the shared practice route, feature,
styles, and focused tests and therefore is not parallel-safe with another
practice-browser packet. The final SLI-0028 qualification packet depends on
this packet's accepted browser behavior and fixtures.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Resume saved answers | Exact progress contains a partial draft across supported response types | Learner opens or reloads the activity | Matching controls restore exactly, saved time/status is visible, and unanswered controls stay empty | model/component/Chromium |
| Save partial progress | Learner has zero or more valid answers and the current revision | Learner chooses `Save progress` | Exact conditional snapshot is sent once and the returned server revision/time replaces local status | unit/component/browser |
| Stale or uncertain save | Server reports conflict, denial, malformed state, or unavailable result | Save finishes | Newer server work is not overwritten; protected status explains what happened and offers only a safe reload/retry action | component/browser |
| Confirmed submission | All questions are answered | Learner checks answers | Existing stable submission path returns its result, the server clears its draft, and refreshed progress shows authoritative retry/history state | component/browser |
| Retry available | Progress says another attempt is allowed | Learner chooses `Try another attempt` | Controls reset for a distinct submission while earlier result and history remain readable | component/browser |
| Retry exhausted | Progress says no attempts remain | Learner reviews the page | No mutation control promises another attempt; exhaustion and retained history remain visible | component/browser |
| Targeted review | Latest attempt supplies repeated available and unavailable targets | Learner views review guidance | Targets keep stable deduplicated order; internal destinations are links and unavailable resources are explained without substitute ranking | unit/component/browser |
| Compare attempts | History contains zero, one, or many variable-shaped attempts | Learner opens history | Every summary retains order, score, outcome, item correctness, time, evidence reference, and technical provenance without answers or mastery claims | component/browser |
| Confidentiality failure | A progress/draft result has an extra private field or mismatched exact chain | Route or save validates it | The whole affected state fails closed; no partial/private value is rendered or copied into a request | unit/component/browser |
| Accessible recovery | Loading, saved, saving, conflict, unavailable, review, retry, empty-history, and exhausted states occur | Learner uses keyboard, narrow view, themes, forced colors, or reduced motion | Equivalent meaning/actions remain labeled, focus and live status are useful, and no horizontal overflow or color-only state is introduced | component/Chromium/axe |
| Anti-rigidity | Item, response, target, history, and attempt counts vary within accepted bounds | Flow renders and mutates | Behavior follows IDs and contracts without fixed fixture counts, exact timestamps, or whole-paragraph/style assertions | unit/component/browser |

## Verification Commands

Run focused practice model/component tests; the focused Chromium practice suite
with axe, keyboard, reflow, forced-color, reduced-motion, and theme evidence;
all web unit/component tests; TypeScript typecheck, lint, and production build;
generated-client check mode; user-facing language changed/full checks; design-
system integrity; `python dev-tools/planning/check_planning.py`; `python
dev-tools/documentation/check_docs.py`; `git diff --check`; exact-candidate
affected verification; independent technical review; and `python
dev-tools/agent/check_ready.py` when selected by packet start. Backend,
PostgreSQL, restart, and direct headless composition remain the final
qualification packet except where a focused browser-contract regression needs
the existing API fixture.

## Documentation and Evidence Update

Update the web README, SLI-0028, this packet, and the planning register. Record
the exact candidate/receipt, generated-client-only boundary, resume/save/retry/
review/history behavior, validation and confidentiality results, accessibility
and theme results, focused/aggregate checks, assumptions, and remaining live
qualification. No ADR, public contract, architecture, design-token, icon, or
decision-readiness change is expected.

## Stop Conditions

Stop for a required API/schema/generated-client change; new response or policy
meaning; browser-owned retry, score, review, attempt, evidence, or identity
authority; arbitrary or server-supplied external navigation; answer/private
field exposure; autosave/offline/sync requirements; adaptive ranking, mastery,
AI/model, provider, cloud, tenancy, queue, recovery, or external-execution
choice; conflicting canonical authority; stale CAP binding; or active write-
scope overlap.

Do not stop or reopen review for harmless whitespace, optional wording, or
nonfunctional styling. Fix an inconsequential in-scope issue locally or defer
optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; route/client operations; validation,
confidentiality, save revision, retry, review-link, history, focus, accessibility,
and theme behavior; focused, language, design, generated-client, documentation,
planning, aggregate, and independent results; changed paths, assumptions, and
residual gaps. Confirm the browser consumes the same public API as non-browser
and future headless clients and that final real PostgreSQL/restart/headless/live
qualification remains the dependent SLI-0028 seam.

## Planning History

- 2026-10-16: Authored just in time after WRK-0105 completed. The packet keeps
  the public API authoritative, chooses one explicit conditional save action,
  and bounds browser resume, retry, review, and comparison into one observable
  learner flow before final live qualification.
