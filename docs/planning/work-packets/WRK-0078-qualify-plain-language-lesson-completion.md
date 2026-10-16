---
id: WRK-0078
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0124
capability: CAP-0030
depends_on: ["WRK-0076", "WRK-0077"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/styles/lesson-reading.css", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts-snapshots/lesson-light-chromium-win32.png", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts-snapshots/lesson-dark-chromium-win32.png", "apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/README.md", "docs/planning/work-packets/WRK-0078-qualify-plain-language-lesson-completion.md", "docs/planning/vertical-slices/SLI-0124-understand-lesson-check-and-completion.md", "docs/planning/register.md"]
generated_artifacts: ["apps/web/dist", "artifacts/playwright/wrk0004/**", "artifacts/playwright/wrk0005/**"]
base_revision: 5612ab9c085d08633899e0b412a3115ce7a866d2
claim_id: WRK-0078:9506ffa8-1648-4028-84bd-272495b07aa9
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:50:10Z
---

# Agent Work Packet: Qualify Plain-Language Lesson Completion

## Objective and Deliverable

Qualify the complete SLI-0124 lesson, knowledge-check, and saved-completion
journey in pinned Chromium. Update stale browser expectations and visual
baselines only where the already-delivered learner language changed. Prove that
task-focused meaning, bounded failures, exact technical evidence, answer
secrecy, completion persistence, accessibility, and theme/responsive behavior
remain intact, then reconcile evidence for slice closure.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`, and
`testing-quality` packs. Read CAP-0030, SLI-0124, WRK-0068, WRK-0076,
WRK-0077, the interface and user-facing-language standards, content style
guide, lesson/completion component tests, browser configuration and support,
isolated approved-lesson runner, affected browser/live specifications, and
`apps/web/README.md`.

## Decisions and Assumptions

- WRK-0076 and WRK-0077 own the delivered runtime behavior. This packet
  qualifies that behavior and does not create a new product or visual pattern.
- Browser evidence opens native `Technical record` disclosures before
  asserting exact facts. Primary assertions protect learner meaning, actions,
  limitations, privacy, and failures rather than exact full paragraphs.
- The existing light/dark screenshots may be refreshed because their content
  and hierarchy changed. Pixel-only variation inside the accepted tolerance is
  cosmetic and does not trigger a correction/re-review cycle.
- Pinned Chromium and the existing isolated live approved-lesson harness remain
  the accepted local qualification boundary. No cross-browser promise is made.
- Cosmetic styling observations are nonblocking and belong in CAP-0031 unless
  they impair function, comprehension, accessibility, safety, required
  evidence, or an SLI-0124 acceptance scenario.

## In Scope

- Align mocked Chromium expectations with the delivered lesson loading,
  recovery, publication-detail, result, and saved-completion language.
- Open lesson, checked-answer, saved-completion, and saved-result technical
  disclosures before verifying exact IDs, versions, digests, policy, times,
  attempts, evidence, event, submission, and source facts.
- Preserve checks for no client learner authority, no answer disclosure, exact
  submission behavior, no duplicate presentation after completion, and
  stable saved evidence across reload.
- Retain axe, keyboard, light/dark/system, reduced-motion, forced-color,
  narrow-layout, and 200-percent-equivalent evidence.
- Refresh only the two tracked lesson light/dark baselines when the semantic
  browser state is correct.
- Correct only responsive wrapping that prevents an open required technical
  record from fitting the supported narrow viewport.
- Run focused mocked Chromium, isolated live approved-lesson, component,
  typecheck, lint, build, design, planning, documentation, affected-
  verification, readiness, whitespace, and deterministic slice-completion
  checks.
- Reconcile this packet, SLI-0124, and the planning register.

## Out of Scope

- Product behavior, backend, contract, generated-client, fixture, grading,
  feedback, answer, completion, navigation, persistence, session,
  authorization, retry, browser configuration, runner, container, token, icon,
  nonfunctional styling, layout redesign, or shared visual-system changes.
- New actions, browser engines, formal readability conformance, localization,
  external services, or unrelated test cleanup.
- Re-review or CAP interruption for blank lines, snapshot noise, copy fit, or
  nonfunctional styling; fix trivial issues locally or defer them to CAP-0031.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Runtime and contracts | lesson route/page, knowledge check, generated types, session and exact-version APIs | narrow lesson technical-record wrapping only | Keep required evidence usable at supported narrow widths without changing behavior |
| Mocked browser evidence | lesson fixture, Chromium spec/config/support | named specification and two tracked baselines | Align accessible names and qualify browser modes |
| Live journey evidence | approved-lesson spec and isolated runner | named specification only | Preserve API/UI evidence and saved completion through the shared live flow |
| Documentation and planning | web README, completed packets, parent slice, register | named README and planning files | Record exact qualification and close the slice |
| Generated evidence | web build and Playwright output | generated only | Support live execution and retain bounded diagnostics |

## Contracts and Interfaces

The browser suites consume the unchanged loopback application, generated API
client, exact-version lesson and knowledge-check endpoints, completion history,
single-profile session, and accessible native disclosure names. No public,
domain, API, event, generated-client, persistence, or runtime interface changes.

Completion hands the slice verifier three closed packets and exact focused,
live, accessibility, and affected-verification evidence.

## Dependencies and Parallel Safety

WRK-0076 and WRK-0077 are complete and provide the stable learner-facing
lesson and assessment/completion states. This packet serially qualifies their
combined outcome and closes SLI-0124, so it is not parallel-safe with another
SLI-0124 packet. Its exact file lease leaves unrelated work available.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Open and read | An exact reviewed lesson | The learner opens it | Task-focused lesson content, sources, publication details, and educational limit render; exact package facts remain reachable | Mocked/live Chromium |
| Complete the check | An incomplete lesson | The learner submits an answer | Server-reviewed feedback and score appear without client learner/grading authority or mastery claims | Mocked/live Chromium/API |
| Inspect checked evidence | A result is returned | The checked-answer technical record opens | Every returned exact result and submission fact is visible without answer-key exposure | Mocked Chromium |
| Reopen completion | A completion is saved | The lesson reloads | Saved result, score/time, limitation, and stable exact evidence render without another presentation request | Mocked/live Chromium/API |
| Recover safely | Session, lesson, completion, presentation, or submission fails | A bounded state renders | Partial/private facts stay hidden, no false result is claimed, and existing safe recovery remains clear | Mocked/live Chromium |
| Access parity | Theme, keyboard, narrow/scaled layout, reduced motion, or forced colors change | The journey is used | Equivalent content/actions remain accessible, axe-clean, and non-overflowing | Mocked/live Chromium |
| Anti-rigidity | Harmless prose, fixture history size, or pixel noise changes | Tests evaluate the page | Assertions depend on roles, actions, required facts, flexible records, and bounded visual tolerance | Test review |

## Verification Commands

- `npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading`
- `python tests/e2e/approved-lesson/run.py`
- `npm --prefix apps/web test -- --run apps/web/tests/component/lessonReadingPage.test.tsx apps/web/tests/component/knowledgeCheck.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `npm --prefix apps/web run build`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0078`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`
- `python docs/planning/skills/verify-and-close-slice/scripts/check_completion_gate.py docs/planning/vertical-slices/SLI-0124-understand-lesson-check-and-completion.md docs/planning/work-packets/WRK-0076-clarify-lesson-context-and-recovery.md docs/planning/work-packets/WRK-0077-clarify-knowledge-check-and-saved-completion.md docs/planning/work-packets/WRK-0078-qualify-plain-language-lesson-completion.md`

Use the repository-pinned Node/npm/Chromium runtime and a short isolated temp
root. Run the live harness through its existing disposable PostgreSQL path and
exact cleanup. An environmental Docker failure is diagnosed separately from a
product defect and does not authorize scope expansion.

## Documentation and Evidence Update

Update `apps/web/README.md` only if the qualification description is stale.
Record exact mocked/live scenario counts, accessible technical-fact coverage,
session/privacy/answer behavior, supported modes, visual-baseline disposition,
containment cleanup, affected receipt, independent review, assumptions, gaps,
and slice closure in this packet and SLI-0124. Keep approval and reviewer
records only in ignored local state.

## Stop Conditions

Stop for a runtime/product defect; missing or inaccessible required fact;
changed grading, feedback, answer secrecy, completion, retry, authorization,
session, persistence, provenance, or exact-version meaning; failed live
containment; a required path outside scope; canonical conflict; colliding
lease; or material CAP-0030 drift. Do not stop or reopen review for whitespace,
copy fit, baseline noise, or nonfunctional visual polish.

## Required Handoff

Report exact candidate, mocked/live scenario counts, result/completion evidence,
privacy/secrecy/recovery behavior, accessibility/theme/responsive outcomes,
snapshot disposition, containment cleanup, focused/affected/aggregate checks,
review, deterministic completion result, unchanged boundaries, assumptions,
gaps, and the next CAP-manifest action. Do not request slice approval.

## Planning History

- 2026-10-16: Refined SLI-0124 JIT-C as the serial qualification seam after
  WRK-0076 and WRK-0077 completed, with semantic browser/live evidence,
  bounded baseline refresh, explicit anti-rigidity rules, and no runtime or
  contract change.
- 2026-10-16: Browser qualification found that an open saved-result technical
  record expanded the 375-pixel viewport to 669 pixels. Refined the packet to
  allow one functional wrapping correction while leaving cosmetic styling and
  layout redesign out of scope.
