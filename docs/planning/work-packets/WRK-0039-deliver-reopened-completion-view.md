---
id: WRK-0039
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: ["WRK-0038"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/lesson-reading/KnowledgeCheck.tsx", "apps/web/src/styles/lesson-reading.css", "apps/web/tests/component/knowledgeCheck.test.tsx", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0039-deliver-reopened-completion-view.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0039:4290da20-5188-4203-9c66-b77662a6f571
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:58:27Z
---

# Agent Work Packet: Deliver the Reopened Completion View

## Objective and Deliverable

Make the lesson knowledge-check region completion-aware so a fresh browser load
shows the authorized learner's retained bounded completion and exact evidence
history before offering another response.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the routed learning, interface, testing,
and planning context; CAP-0001; SLI-0016; WRK-0038; ADR-0005, ADR-0006,
ADR-0008, and ADR-0009; the Assessment contract; generated completion client
shape; current lesson/knowledge-check components, styles, browser and component
tests; and the nearest web and design-system README files.

## Decisions and Assumptions

The browser consumes only the protected generated-client endpoint and does not
derive completion from local state. It queries retained completion before the
answer-safe presentation. A completed response suppresses another submission
form; an incomplete response preserves the existing knowledge-check flow. Any
denied, malformed, or unavailable completion response fails closed rather than
showing an unverified completion or bypassing the history check.

## In Scope

- Load and validate the exact-placement completion response before loading the
  knowledge-check presentation.
- Render a semantic, accessible retained-completion summary with ordered source
  history, exact lesson/Assessment versions and digests, score, time, attempt,
  event, and evidence references.
- State explicitly that the retained result is a bounded knowledge check and
  not mastery, certification, advice, suitability, or performance evidence.
- Preserve the existing deterministic submission behavior when history is
  empty and add focused component/browser evidence for reload, denial,
  malformed response, unavailable service, theme/accessibility, and reflow.
- Reuse existing semantic tokens and component patterns without introducing a
  shared visual-system decision.

## Out of Scope

Background delivery, client caching, learner selection, history mutation,
retakes, mastery or recommendation meaning, Audit-row display, answer or
feedback disclosure from history, generated-client changes, recovery,
managed-cloud qualification, and production bundle regeneration.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated client | Protected completion and knowledge-check operations | none | Consume the reviewed exact response shape without duplicating it |
| Lesson interface | Knowledge-check state machine and existing tokenized styles | Listed component and stylesheet | Present retained state or the existing form, never both |
| Component verification | Current presentation/submission fixtures | Listed component test | Prove request order, exact history, and fail-closed states |
| Browser verification | Existing route mocks and interface matrix | Listed browser spec | Prove fresh-load history, accessibility, theme parity, and reflow |
| Documentation | Delivered web route and remaining limits | Web README | Record browser behavior without broadening support claims |
| Planning | Packet, slice, and register | Listed planning artifacts | Keep incremental lifecycle state synchronized |

## Contracts and Interfaces

Consume `LessonCompletionResponseModel` from
`GET /api/v1/curriculum/placements/{placement_id}/completion`. Accept only the
closed projection version, bounded completion meaning, digest-shaped source
and package/definition values, finite bounded score, nonempty exact-version
identities, valid server timestamps, and a coherent completed/history state.
Do not send or render a learner selector. When `completed` is false, history
must be empty and the existing generated knowledge-check presentation and
submission contracts remain unchanged.

## Dependencies and Parallel Safety

WRK-0038 is complete and supplies the protected generated-client operation.
This packet is not parallel-safe with WRK-0040 because qualification will
consume this interface, regenerate the production bundle, and reconcile final
slice evidence.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Fresh reopen after completion | Protected history returns one retained event | Lesson loads in a fresh page | Exact completion history is shown and no presentation/submission request is made | component/browser |
| No completion | Protected history is coherent and empty | Lesson loads | Existing answer-safe form opens and submission behavior is unchanged | component/browser |
| Exact provenance | Retained event contains fixed versions, digests, IDs, score, and time | History renders | Values are visible with clear labels and no private answer, feedback, or learner identifier | component/browser |
| Bounded meaning | Completed history is visible | Learner reads the result | Copy rejects mastery, certification, advice, suitability, and performance interpretation | component/browser |
| Denied history | Completion request is unauthorized or forbidden | Lesson loads | A bounded unavailable state appears and no presentation data is requested | component |
| Malformed history | Response has an incoherent state, invalid digest, score, or timestamp | Lesson loads | It fails closed without a completion claim or answer form | component |
| Unavailable history | Request fails or returns a nonaccepted status | Lesson loads | It fails closed without fabricating or erasing completion | component |
| Accessible parity | Retained history is rendered in themes and narrow view | Browser checks run | Content, hierarchy, axe result, forced-color behavior, and reflow remain sound | browser/design |

## Verification Commands

Run the work-packet validator and implementation gate; focused Vitest for the
knowledge-check component; the lesson-reading Playwright Chromium suite; web
typecheck and lint; design-system, documentation, and planning checks; and
`git diff --check`. Production build, live close/reopen, full suites, dependency
audit, aggregate readiness, and generated `apps/web/dist` reconciliation belong
to WRK-0040.

## Documentation and Evidence Update

Update the web README, this packet, SLI-0016, and the planning register with
exact focused results. No canonical domain, contract, design-token, icon, ADR,
or context-pack change is expected because the packet exposes already accepted
meaning through the existing visual system.

## Stop Conditions

Stop if the browser must choose a learner, infer completion from submission
state, accept incoherent or version-substituted history, expose private answer
or Audit data, add mastery/advice meaning, select background delivery or cache
policy, change the generated API contract, or introduce a shared visual-system
decision. Those are not bounded implementation details for this packet.

## Required Handoff

Report request ordering, history validation and presentation, unchanged empty
flow, denial/failure behavior, accessibility/theme/reflow evidence,
documentation impact, residual gaps, and WRK-0040 readiness.

## Verification Progress

- The knowledge-check region now calls the protected completion operation
  first. A coherent empty result continues to the existing answer-safe form; a
  completed result renders ordered exact-version provenance and makes no second
  presentation or submission request. Denied, malformed, unavailable, and
  transport-failure responses stop at a bounded no-mutation state.
- Eight focused component tests passed under the supported Node 24 runtime,
  covering request order, unchanged submission/idempotent retry, exact retained
  provenance, no answer or learner authority, and all completion failure
  classes. The initial sandboxed invocation failed before test collection on a
  Windows temporary-cache rename; the same command completed outside that
  sandbox rather than weakening the test.
- Eight focused Chromium scenarios passed. The retained state preserved light
  and dark content parity, returned zero axe violations in both themes,
  suppressed another Assessment request, and reflowed without horizontal
  overflow at 375 pixels. Its first run exposed 4.21:1 muted-label contrast;
  switching those caption labels to the existing secondary-text token produced
  a clean rerun while design-system validation still passed.
- Web typecheck and lint passed. Design-system validation verified 125 tokens
  and 56 icons, documentation verified 193 Markdown files plus catalogs,
  planning verified 69 artifacts, the implementation gate remained current,
  and `git diff --check` exited successfully with line-ending warnings only in
  installed dependency files.
- No contract, token, icon, domain, or ADR meaning changed. Production bundle
  regeneration, live Docker close/reopen, full-suite execution, dependency
  audit, and aggregate readiness remain intentionally grouped in WRK-0040.

## Planning History

- 2026-10-15: Authored after WRK-0038 completed. The generated completion
  contract and existing design system are sufficient; no unresolved decision or
  material CAP drift was found.
- 2026-10-15: Delivered completion-first reload behavior, retained evidence
  presentation, fail-closed states, and focused accessibility/theme/reflow
  evidence without changing the generated contract or shared visual system.
