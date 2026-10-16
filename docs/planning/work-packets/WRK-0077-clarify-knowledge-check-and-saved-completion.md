---
id: WRK-0077
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0124
capability: CAP-0030
depends_on: ["WRK-0076"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/lesson-reading/KnowledgeCheck.tsx", "apps/web/tests/component/knowledgeCheck.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0077-clarify-knowledge-check-and-saved-completion.md", "docs/planning/vertical-slices/SLI-0124-understand-lesson-check-and-completion.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 71f119456985eec6601e41b6eb50e26f072c2b87
claim_id: WRK-0077:2d2b96a5-f196-4f7e-b076-4887c7002cec
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:41:48Z
---

# Agent Work Packet: Clarify Knowledge Check and Saved Completion

## Objective and Deliverable

Apply the accepted learner-facing language contract to the knowledge-check
load, answer result, retry/conflict states, and saved completion. The learner
can understand what was checked or saved, what the score means, what was not
recorded, and what to do next without projection, replay, retained-evidence, or
exact-contract language. Exact result and completion provenance remains
complete under accessible `Technical record` disclosures.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`,
`learning-adaptation`, `testing-quality`, and relevant context packs. Read
CAP-0030, SLI-0124, WRK-0068, WRK-0076, the language/content standards,
Assessment and content-package contracts, ADR-0005/0006/0007, learner-model and
completion-history architecture, risk guidance, `KnowledgeCheck`, generated
response types, focused tests, and `apps/web/README.md` before editing.

## Decisions and Assumptions

- Assessment remains the sole answer, grading, feedback, attempt, and evidence
  authority; Learner model remains the completion-view owner. The browser
  changes no validation, request, score, retry identity, or load order.
- Score, completion time, and the non-mastery/non-advice limitation remain in
  the main flow. IDs, versions, digests, policy, source, rebuild, attempt,
  evidence, event, submission, and exact timestamps belong in `Technical
  record` unless required to interpret the result directly.
- The just-submitted result and reopened saved completion both retain every
  exact fact already delivered to the browser. The private answer, selected
  option, learner identity, and Audit record remain unavailable.
- Error copy follows result, recording/protection fact, and existing recovery.
  No new mutation, retake, or navigation action is introduced.
- Tests protect semantic meaning, all exact facts, answer secrecy, flexible
  history, and safe retry identity rather than exact paragraphs or styling.

## In Scope

- Plain completion-check loading, unavailable, denied, and invalid messages.
- Knowledge-check result, score limitation, conflict, denial, unavailable, and
  safe retry language.
- Saved-completion heading, explanation, primary score/time summary, limitation,
  and native technical disclosures for projection/source and per-event facts.
- A technical disclosure for the just-submitted result's exact package,
  assessment, item, policy, attempt, evidence, submission, and timestamp facts.
- Focused component evidence for unchanged load order, request body, no answer
  key/client learner, retry identity, flexible saved history, technical fact
  completeness, limitations, and fail-closed states.
- Minimal web README and planning/evidence reconciliation.

## Out of Scope

- Lesson route/page work completed by WRK-0076; complete Chromium/live evidence
  and slice closure assigned to JIT-C.
- Scoring, feedback, answer, assessment definition, request/response, event,
  learner-model, identity/session, API, generated-client, persistence, retry,
  or completion semantics; new retake/navigation actions; CSS, tokens, icons,
  visual polish, localization, external services, or disclosure rewrites.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Canonical/runtime boundary | Assessment/content/identity contracts, learner-model architecture, generated types | none | Confirm exact grading, evidence, completion, and secrecy semantics |
| Assessment presentation | `KnowledgeCheck` | named component only | Clarify load/result/recovery and add accessible exact technical records |
| Focused evidence | knowledge-check component tests | named test only | Protect requests, retries, facts, limitations, flexible history, and failures |
| Documentation/planning | web README, packet, parent slice, register | named files | Reconcile delivered result and evidence |

## Contracts and Interfaces

The packet consumes the unchanged generated `KnowledgeCheckPresentation`,
`KnowledgeCheckResult`, and `LessonCompletion` response types and sends the
same exact submission request. It produces no public schema, API, generated
client, domain, event, session, persistence, or grading change.

JIT-C receives stable learner-facing headings/actions and native technical
disclosures for mocked and live Chromium assertions. The browser still requests
completion before a presentation and never requests a presentation after a
valid completed response.

## Dependencies and Parallel Safety

WRK-0076 is complete. This packet serially establishes assessment/completion
presentation consumed by JIT-C and is not parallel-safe with another SLI-0124
packet. Its exact lease does not block unrelated work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Load incomplete state | No saved completion exists | Component loads | It checks for a saved completion, then shows the answer-safe prompt without answer or client learner authority | Component test |
| Correct/incorrect result | Server returns reviewed deterministic feedback | Result renders | It shows feedback, exact score, and bounded non-mastery meaning in direct language | Component test |
| Inspect submitted result | A result is returned | Technical record opens | Every returned exact ID/version/digest/policy/time fact remains labeled and selectable without answer exposure | Component test |
| Retry unchanged answer | The first request is unavailable | Learner retries | The same submission identity is reused and plain copy says no duplicate result is created | Component test |
| Conflict or denial | Exact references changed or access is denied | Failure renders | It states that no new result was recorded and gives the existing reload/retry guidance without internals | Component test |
| Reopen saved completion | Completion history is present | Lesson loads | It shows saved completion, score/time, and limitation without another presentation request | Component test |
| Inspect saved evidence | One or more completion entries exist | Technical records open | Projection/source and every event/package/assessment/item/policy/attempt/evidence fact remain complete | Component test |
| Invalid/unavailable completion | Completion is denied, malformed, unavailable, or offline | Failure renders | It fails closed, shows no radio choices or protected facts, and explains safe reload behavior | Component test |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/component/knowledgeCheck.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0077`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Chromium and approved-lesson live qualification are owned by JIT-C. Backend,
database, generated-client, and live suites are not required unless affected
routing selects them.

## Documentation and Evidence Update

Update `apps/web/README.md` only where the check/completion presentation is
described. Update this packet, SLI-0124, and the register together. Store
approval and reviewer records only in ignored local control storage.

## Stop Conditions

Stop for changed grading, feedback, answer secrecy, completion/mastery meaning,
submission identity/retry, request/load order, session/authorization, evidence,
event/provenance, exact versions, educational-use/advice meaning, public
contracts, persistence, a new action, canonical conflict, CAP drift, or a
colliding lease. Do not stop or reopen review for whitespace, copy fit, or
nonfunctional visual polish; fix it locally when trivial or defer to CAP-0031.

## Required Handoff

Report revised assessment/completion meaning, preserved grading/evidence/
secrecy/retry boundaries, focused and affected verification, aggregate
readiness, assumptions, JIT-C work, and any cosmetic issue deferred to CAP-0031.

## Planning History

- 2026-10-16: Refined SLI-0124 JIT-B around knowledge-check result/recovery,
  saved completion, accessible complete technical records, flexible semantic
  evidence, and unchanged Assessment/Learner-model authority.
- 2026-10-16: Submitted exact implementation candidate
  `9eedd397616dcc93ae3eedd821b14fb20e684cca` after focused component,
  typecheck, lint, design, planning, documentation, whitespace, and aggregate-
  readiness checks passed.
