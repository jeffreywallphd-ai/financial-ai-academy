---
id: WRK-0033
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0015
capability: CAP-0001
depends_on: ["WRK-0032"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/lesson-reading", "apps/web/src/styles/lesson-reading.css", "apps/web/tests", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0015-submit-deterministic-knowledge-check.md", "docs/planning/work-packets/WRK-0033-deliver-lesson-knowledge-check-ui.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0033:14e0befa-e769-4f6f-9344-4c9d499bbdd1
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:34:18Z
---

# Agent Work Packet: Deliver the Lesson Knowledge-Check UI

## Objective and Deliverable

Add an accessible, token-based single-choice check to the existing lesson page
with clear pending, correct, incorrect, duplicate, conflict, unauthorized,
stale, and unavailable states and no mastery/advice claim.

## Required Context

Read AGENTS.md, routed interface/testing context, CAP-0001, SLI-0015,
WRK-0032, the generated client, lesson route/page/model/styles, design-system
tokens and icon rules, component/browser fixtures, and nearest README.

## Decisions and Assumptions

The server remains the only scorer and learner authority. The browser retains
one submission UUID across a retry of unchanged input, creates a new UUID only
after the answer changes, and never derives correctness locally.

## In Scope

Use the generated client, semantic tokens, native form controls, stable focus
and live-region behavior. Test light/dark parity, keyboard flow, zoom/reflow,
reduced motion, forced colors, retry behavior, and failure recovery. Do not add
new visual primitives unless existing tokens cannot express the interaction.

## Out of Scope

History/projection, mastery, celebrations, multiple questions, answer-key
inspection, offline persistence, and any new design token or icon.

## Contracts and Interfaces

Read the exact presentation after the lesson is available. Submit the complete
immutable reference tuple through generated types. Map errors to bounded
learner language without exposing correlation or storage details.

## Acceptance Scenarios

- Keyboard and pointer users can choose one answer and submit it once.
- Correct and incorrect results show server feedback and bounded completion
  meaning without advice/mastery language.
- Pending state prevents duplicate clicks; unchanged network retry reuses the
  submission identity; changing the answer creates a new identity.
- Unauthorized, stale/conflict, malformed, and unavailable states fail safely
  without grading in the client.

## Verification

Run generated-client currency, typecheck, lint, component tests, focused
Chromium tests in light/dark/keyboard/reflow/reduced-motion/forced-color states,
design, docs, planning, and security checks.

## Stop Conditions

Stop on contract drift, client-side grading, hidden identity selection, or a
shared visual decision requiring broader synchronized design work.

## Required Handoff

Report interaction states, retry semantics, accessibility evidence, checks,
documentation impact, and readiness of WRK-0034.

## Verification Progress

- Added a generated-client-only single-choice interaction to the existing
  lesson page. The server remains the sole scorer; no learner identifier or
  answer key is present in the browser request/presentation.
- The browser retains one submission UUID for an unchanged failed retry and
  resets it only when the selected option changes. Pending, success, review,
  conflict, denied, malformed, and unavailable states use native controls,
  live regions, and bounded non-mastery language.
- Generated-client contract tests and 21 Vitest tests passed. Seven focused
  Chromium scenarios passed across light/dark/system parity, axe analysis,
  keyboard use, exact submission, narrow/zoom-equivalent reflow, reduced
  motion, forced colors, denial, and unsafe-content refusal. The two reviewed
  theme snapshots were regenerated for the intentional panel.
- Typecheck, lint, 98-module production build, design-system validation (125
  tokens and 56 icons), security (10 control groups), documentation, planning,
  and diff checks passed.

## Planning History

- 2026-10-15: Captured as the third serial packet for SLI-0015.
- 2026-10-15: Refined immediately before start after WRK-0032 completed; the
  existing design system can express the interaction without shared changes.
- 2026-10-15: Added the tracked static build directory to generated output
  after the first production build proved that the repository retains it.
- 2026-10-15: Accessible interaction and focused browser qualification
  completed without adding design tokens, icons, or client-side grading.
