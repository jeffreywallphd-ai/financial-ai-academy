---
id: WRK-0094
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0026
capability: CAP-0006
depends_on: [WRK-0093]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/practice-activity", "apps/web/src/styles/practice-activity.css", "apps/web/tests/browser/practice-activity", "apps/web/tests/component/practiceActivity.test.tsx", "apps/web/tests/component/practiceFixture.ts", "apps/web/tests/unit/practiceActivityModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0026-open-versioned-practice-activity.md", "docs/planning/work-packets/WRK-0094-deliver-practice-opening-browser-route.md"]
generated_artifacts: []
base_revision: 93882c1025db65f483b3b867afa75381d7dabbdc
claim_id: WRK-0094:6c66f0cf-a9b2-4239-90fb-113fb0596eaf
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T14:53:50Z
---

# Agent Work Packet: Deliver Practice Opening Browser Route

## Objective and Deliverable

Deliver an accessible browser route for opening one exact versioned practice
activity through the generated public API client. The page must validate the
complete answer-safe response before rendering, explain the activity and its
attempt policy in plain learner language, render all three supported response
shapes without submitting or scoring them, preserve exact technical evidence,
and fail closed without partial content. The public API remains authoritative
for browser and non-browser consumers; this packet adds no alternate browser
contract or separate AI mode.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository-
root `docs/README.md`. Route through the baseline, interface-design, and
testing-quality context packs. Read the change-impact matrix, decision
readiness, CAP-0006, SLI-0026, WRK-0093, ADR-0005, ADR-0007, Assessment
contract, interface design system, style and content guides, user-facing
language standard, web/design-system READMEs, generated practice API types,
session adapter, router, lesson route patterns, affected components and styles,
component/browser fixtures, and concurrent-work protocol before editing.

## Decisions and Assumptions

- Use the generated `getPlacedPractice` operation exactly as delivered by
  WRK-0093. The loader supplies only `placement_id`; session, learner identity,
  authorization, exact definition resolution, and answer safety stay server-
  owned.
- Add `/learn/placements/:placementId/practice` as the browser location. Do not
  add an unconditional lesson link because the current lesson contract does
  not state whether a practice placement exists. JIT-D may qualify a truthful
  entry path from live seeded data without inventing browser authority.
- Validate the entire closed response before showing any activity facts. The
  browser may be stricter only where the published API contract is explicit;
  it must accept variable valid item, option, and reference counts and preserve
  server order.
- Render native radio, checkbox, and fixed-decimal number/text controls as an
  accessible preview of the required response shape. Learner choices remain
  ephemeral DOM state and are explicitly described as neither checked nor
  saved. No submit control, answer key, scoring rule payload, feedback branch,
  attempt record, completion meaning, or local persistence is introduced.
- Put title, purpose, instructions, response requirements, attempt limit,
  resume/history meaning, and review material in the primary flow. Put exact
  IDs, versions, digests, schema and policy facts in an accessible `Technical
  record`. Do not expose raw enum text as learner-facing labels.
- Reuse existing semantic tokens and native controls. This packet introduces
  no shared token, icon, component, theme, or visual-system decision.

## In Scope

- Add a typed practice presentation model and exhaustive closed validator for
  root, attempt-policy, resource-reference, item-union, option, decimal-scale,
  identifier, semantic-version, digest, cardinality, uniqueness, and exact-key
  invariants represented by the public contract.
- Add a session-aware route loader using the generated client, one bounded
  unauthorized retry, and learner-safe denied, missing, unavailable, malformed,
  loading, and unexpected states with no partial presentation.
- Add the practice-opening route/page and item renderers for single select,
  multiple select, and fixed-decimal numeric entry; preserve item and option
  order, labels, descriptions, field groups, and keyboard semantics.
- Present purpose, instructions, attempt-policy summary, source and review
  references, educational limitations, and complete exact technical evidence
  with light/dark/system and responsive parity.
- Add flexible-shape unit and component coverage plus focused Chromium coverage
  for success, all response types, confidentiality, malformed/denied paths,
  keyboard order, focus, narrow/zoom reflow, reduced motion, forced colors,
  theme parity, and automated accessibility.
- Update the web README and planning evidence for the new browser route.

## Out of Scope

Submitting responses; scoring; correct-answer, accepted-range, or private
feedback disclosure; attempt creation; idempotency; retry enforcement;
resume/history state; completion evidence; lesson/curriculum navigation changes;
live fixture seeding; API/OpenAPI/generated-client changes; backend changes;
new shared tokens or icons; cosmetic redesign; AI-specific transport, agent
protocols, autonomous action, model grading, adaptive selection, mastery,
financial advice, cloud, tenancy, recovery, or external execution.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public API client | generated schema/client and WRK-0093 tests | none | Browser consumes the existing headless-capable contract without redefining it |
| Browser model and loader | session, lesson model/API, router | new practice feature and router only | Fail closed and preserve server-owned identity and meaning |
| Interface | design tokens, lesson patterns, style/language guides | practice components and semantic-token CSS | Render the three safe response shapes accessibly without a new design system |
| Tests | model/component/browser patterns and fixtures | bounded practice test files | Prove shape flexibility, confidentiality, states, themes, reflow, and accessibility |
| Documentation/planning | web README, parent slice, register | listed files only | Keep route behavior, evidence, and packet lifecycle current |

## Contracts and Interfaces

Consume the generated `PracticePresentationResponseModel` and protected
`GET /api/v1/curriculum/placements/{placement_id}/practice` operation from
WRK-0093. Produce one validated browser `PracticePresentation`, a closed loader
state union, and a route whose visible content is derived only from that public
response. JIT-D may depend on the route path, component semantics, fixtures,
and failure-state contract; it may not treat browser state as submission or
scoring authority.

## Dependencies and Parallel Safety

WRK-0093 is complete and owns the public API contract. This packet is not
parallel-safe with JIT-D because both will touch browser-route tests, web
documentation, and SLI-0026 evidence. No active packet owns the declared paths,
and no generated artifact is written.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact opening | A supported session and valid answer-safe presentation | The route opens one placement | The title, purpose, instructions, attempt meaning, references, ordered items, and exact technical record render from the public API | unit/component/browser |
| Headless contract parity | The generated client represents the same public operation available to non-browser callers | The browser loader reads practice data | It supplies only the placement path and adds no alternate contract, learner selector, or browser-owned authority | unit/contract inspection |
| Response shapes | Valid single-select, multiple-select, and numeric items with variable option/item counts | The page renders | Native labeled controls preserve order and required shape without answers, scores, feedback, submission, or persistence | component/browser |
| Flexible shape | Valid arrays vary within published bounds and records arrive in non-fixture order | Validation and rendering run | All records remain accepted and ordered by the response rather than hard-coded counts | unit/component |
| Confidentiality | Presentation or unexpected payload contains private answer/scoring/feedback keys or an unknown union member | Validation runs | The whole response fails closed and no partial activity facts appear | unit/component/browser |
| Session and failures | Session start or practice read is denied, missing, malformed, unavailable, or fails unexpectedly | The route loads | A bounded learner-focused state explains the result and safe next action without technical/private detail | unit/component/browser |
| Accessibility and parity | The route is used by keyboard at desktop, narrow, and zoom-equivalent widths in every theme and relevant media mode | Learner reviews the activity | Content/actions remain equivalent, focus is visible, field groups are named, no horizontal overflow occurs, and automated accessibility reports no violation | browser/design |

## Verification Commands

Run the generated-client check before and after implementation to prove the
contract remains unchanged. Run focused Vitest model/component tests and the
practice-activity Chromium directory; then web typecheck, lint, full unit,
build, learner-language changed/full checks, design-system, documentation,
planning, whitespace, affected verification with an exact candidate, one
independent technical review, and the fixed aggregate readiness gate when
selected by the packet-start risk plan. Do not add backend or live database
qualification unless implementation crosses those boundaries.

## Documentation and Evidence Update

Update the web README with the route, public-API dependency, answer-safe
rendering, no-submit behavior, error states, and verification ownership. Update
SLI-0026 and the planning register with packet state and technical completion
evidence only. Keep all approval and reviewer records in the ignored local
ledger.

## Stop Conditions

Stop for a required API/OpenAPI/generated-client or backend change; an answer
or private scoring fact in the public response; a need to infer practice
availability from lesson/browser state; submission, scoring, persistence,
completion, or adaptive behavior; a new shared design-system rule; a breaking
route or session contract; an unresolved identity, tenancy, model-authority,
provider, execution, recovery, legal, commercial, or financial-advice choice;
active path overlap; canonical conflict; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional copy
polish, nonfunctional styling, or another inconsequential in-scope correction.
Fix it locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; route and generated-client boundary; complete
validation and failure-state behavior; all supported item shapes; answer and
side-effect confidentiality; plain-language and technical-record hierarchy;
theme, responsive, keyboard, media, and accessibility results; focused,
affected, aggregate, design, documentation, planning, and generated-client
checks; files changed; assumptions and gaps. Confirm that backend/API,
submission, scoring, feedback, evidence, history, live seeding, AI mode, model
authority, cloud, and external execution did not change, leaving JIT-D ready
for live qualification.

## Planning History

- 2026-10-16: Authored just in time after WRK-0093 completed. The packet keeps
  the existing protected public API authoritative for browser and future
  headless consumers, adds only answer-safe rendering, and defers submission,
  persistence, scoring, live seeding, and any separate AI mode.
- 2026-10-16: Claimed from base revision `93882c1` after dependency,
  authority, decision, branch, exact-scope, and collision checks passed.
