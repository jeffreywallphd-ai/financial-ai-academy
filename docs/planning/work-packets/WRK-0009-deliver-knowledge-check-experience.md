---
id: WRK-0009
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-08-05
parent: SLI-0002
capability: CAP-0001
depends_on: [WRK-0008]
decision_gates: []
parallel_safe_with: []
write_scope: [apps/web/package.json, apps/web/package-lock.json, apps/web/src/app, apps/web/src/components/Icon.tsx, apps/web/src/features/knowledge-check, apps/web/src/features/lesson-reading, apps/web/src/styles/knowledge-check.css, apps/web/src/styles/lesson-reading.css, apps/web/tests/unit, apps/web/tests/component, apps/web/tests/browser/knowledge-check, apps/web/tests/browser/lesson-reading, apps/web/README.md, docs/architecture/assurance/architecture-verification.md, docs/assurance/known-verification-gaps.md]
generated_artifacts: [apps/web/package-lock.json, apps/web/tests/browser/knowledge-check/**/*-snapshots/*.png, apps/web/tests/browser/lesson-reading/**/*-snapshots/*.png]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Knowledge-Check Experience

## Objective and Deliverable

Add the accessible learner-facing knowledge-check and feedback experience to
the existing lesson workspace using only WRK-0008's generated client. The
observable deliverable is a learner who can select one option, submit once,
receive deterministic correct or corrective feedback, and understand bounded
validation/denial/failure states with equivalent light, dark, and system-theme
behavior.

## Required Context

Before any file change, prominently read and follow every applicable
`AGENTS.md` and the repository-root `docs/README.md`. Route through the
baseline pack with `interface-design` as primary and `testing-quality` as
adjacent. Read SLI-0002, WRK-0008 and the generated client, SLI-0001's lesson
route/shell handoff, ADR-0007 through ADR-0009, education-versus-advice rules,
interface design README, style guide, interface standards, executable token
and icon documentation, web README, existing lesson components/styles/tests,
browser boundary rules, package metadata, and nearest READMEs. Mockups remain
directional only.

## Decisions and Assumptions

- The existing `/learn/placements/:placementId` route remains the learner
  workspace. The knowledge check appears after the lesson's instructional
  content and before secondary provenance so the learning task remains primary.
- UI code consumes only generated GET/POST operations and generated types. It
  never reconstructs the private definition, infers a correct option, scores a
  response, selects feedback, chooses learner identity, or creates durable
  evidence.
- Use a native `form`, `fieldset`, `legend`, and radio controls with no
  preselected answer. Labels remain fully clickable and the selected state is
  not communicated by color alone.
- Create one opaque submission ID per mounted, uncompleted form instance and
  reuse it for bounded retry after an ambiguous network failure. Do not persist
  the ID, selected option, response, score, or evidence in local/session
  storage. A page reload/history view is outside this slice.
- Client validation requires one option before POST but never substitutes for
  server validation. The submit control prevents accidental double activation
  while a request is in flight; server idempotency remains authoritative.
- After success, lock the form, present score `0|1` of `1`, correctness and
  reviewed feedback, announce the result, and provide no retake action.
  Language says knowledge-check result, not mastery, certification, learner
  completion, suitability, or performance.
- Reuse existing semantic tokens, card/control/status patterns, and the
  reviewed Assessment icon if useful. If a genuinely new shared visual role is
  necessary, stop for synchronized design-system review rather than adding a
  feature-local palette, spacing scale, shadow, radius, theme map, or icon.

## In Scope

- Generated-client adapter and feature model that map safe presentation,
  submission, success, validation, conflict/already-completed, denial,
  unavailable, and unexpected responses into a closed UI state union.
- Accessible question/options form, required-selection validation, pending
  state, deterministic result/feedback panel, and bounded retry for ambiguous
  transient failure using the same submission ID.
- Integration with the existing lesson-loading/session/route path without
  weakening title, content, source, provenance, theme, sidebar, skip-link, or
  safe-error behavior.
- Focus movement/announcement after validation and result, logical keyboard
  order, visible focus, target sizing, semantic status/error relationships,
  narrow/200-percent-equivalent reflow, reduced motion, and forced colors.
- Equivalent correct, incorrect, loading, validation, denial, conflict,
  already-completed, retry, and generic safe-error presentation in light,
  dark, and system themes.
- Unit/component tests for model/API mapping, no scoring logic, form semantics,
  one-selection behavior, submission-ID reuse, double-submit prevention,
  result locking, focus/status, safe error copy, and no browser-local evidence.
- Focused Playwright/axe/visual tests for both deterministic outcomes,
  keyboard-only submission, themes, narrow reflow, reduced motion, forced
  colors, denial/failure, answer secrecy, and education-only wording.
- Web/assurance documentation made stale by the delivered feature and direct
  browser evidence.

## Out of Scope

- Hand edits to generated API files, backend/contract/migration changes,
  scoring/feedback/idempotency policy, evidence persistence, or local server
  composition.
- Retakes, reset/change-answer after success, history/reopen/resume, learner
  completion/progress/mastery, recommendations, review/override, notes,
  analytics, or browser persistence of protected state.
- New route destinations, changes to planned sidebar areas, broad dashboard or
  practice pages, shared token/icon redesign, new component library, charts,
  animation system, or exact mockup reproduction.
- SSR, server components/actions, Node production server, BFF, direct backend
  imports, raw HTML, unsafe sinks, implicit network calls, or provider access.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Feature model/API | Generated operations and lesson feature pattern | `apps/web/src/features/knowledge-check/` | Closed browser state and generated-client adapter |
| Lesson composition | Current reading route/page/body | Named lesson feature root and app composition | Place the bounded task in the delivered workspace |
| Presentation | Existing tokens/card/form/status rules | New knowledge-check stylesheet and narrowly affected lesson stylesheet | Accessible responsive states without a parallel design system |
| Icon use | Reviewed sprite and typed icon wrapper | `Icon.tsx` only if the existing Assessment icon is consumed | Keep icon name union aligned with reviewed assets |
| Verification | Existing unit/component/Playwright patterns | Named test roots and baselines | Deterministic outcomes, denial, themes, accessibility, and regressions |
| Documentation | Web and assurance guidance | Exact documents in `write_scope` | Record delivered interaction and honest qualification gaps |

## Contracts and Interfaces

The feature consumes exactly the generated safe-presentation and submission
operations from WRK-0008. The UI state must distinguish:

- loading the presentation;
- ready with no selection or one selected option;
- client validation error;
- submission pending with the same retained in-memory submission ID;
- completed correct or incorrect result;
- conflicting/already-completed response with no new submission action;
- authorization denial;
- stale/invalid/unavailable presentation; and
- ambiguous retryable versus terminal safe failure.

No UI type may contain a correct option, private definition, provider payload,
cookie/session value, database/storage identifier, or handwritten duplicate of
the API model. Diagnostic rendering is allowlisted and never displays raw
response bodies, stack traces, request headers, or learner response values.

## Dependencies and Parallel Safety

WRK-0008 must complete first because its reviewed OpenAPI, generated models,
operations, errors, and answer-secrecy contract are fixed inputs. This packet
touches shared application composition, lesson feature code, npm metadata, and
browser baselines, so it has no parallel-safe peer. WRK-0010 begins only after
all focused unit/component/browser checks, accessibility scans, and baseline
review complete and this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Present check | Exact safe presentation loads | Lesson workspace renders | One fieldset shows prompt and ordered labeled radios with no preselection/private answer | Component and browser semantic assertion |
| Missing selection | No radio is selected | Learner submits | No POST occurs; bounded validation is associated, announced, and focused appropriately | Component/keyboard test |
| Correct submission | Learner selects the correct option from the fixture | POST succeeds | Form locks and announces `1/1` plus reviewed correct feedback without a mastery claim | Component/browser test |
| Incorrect submission | Learner selects another declared option | POST succeeds | Form locks and announces `0/1` plus reviewed corrective feedback with no client scoring | Component/browser test |
| Double activation | Submit is activated repeatedly while pending | Request is in flight | One logical request/submission ID is used and controls expose pending state | Unit/component request-count test |
| Ambiguous retry | Network fails before a terminal response | Learner invokes bounded retry | The same in-memory submission ID/payload is reused and a later exact replay can show the original result | API-adapter/component test |
| Conflict/already complete | Server reports conflicting reuse or completed check | Response maps | Bounded terminal state appears without retake or private-answer clues | Component/browser safe-state test |
| Denial/stale/unavailable | Session or exact version is invalid/missing | Load or submit resolves | Safe bounded state appears with no question/feedback/evidence internals | Browser denial/failure test |
| Keyboard/focus/status | Learner uses only keyboard | Selection, validation, submit, and result occur | Order, focus visibility, associations, and announcements remain usable | Playwright keyboard plus axe |
| Theme/reflow parity | Every key state runs across themes/settings/widths | Visual/accessibility checks run | Identical content/actions and readable contrast/reflow persist without horizontal loss | Theme, screenshot, axe, forced-color tests |
| Browser boundary | Storage/import/network use is inspected | Feature executes | No learner evidence in web storage, no handwritten models/scoring, and only generated API requests occur | Unit/architecture assertions |
| Educational wording | Result and error copy are reviewed | Correct and incorrect states render | No mastery, certification, suitability, performance, or buy/sell/hold claim appears | Copy fixture and browser assertion |

## Verification Commands

```powershell
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run apps/web/tests/unit apps/web/tests/component
npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading apps/web/tests/browser/knowledge-check
npm --prefix apps/web run build
python dev-tools/design/check_design_system.py
python dev-tools/architecture/check_architecture.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

Regenerate and review light/dark baselines only after semantic behavior and axe
checks pass. Report manual screen-reader, actual browser zoom, non-Chromium,
and non-Windows baseline qualification if not performed.

## Documentation and Evidence Update

Update the web README with the delivered form/result states, generated-client
boundary, no-browser-evidence rule, focused commands, and known gaps. Update
assurance coverage only for directly passing component/Chromium evidence.
Do not claim live PostgreSQL/Python, history/resume, manual assistive
technology, multi-browser, recovery, cloud, or production qualification. If no
shared visual decision changes, do not edit canonical tokens/icons/style
guidance merely because a feature was added.

## Stop Conditions

- UI code needs to infer the correct option, calculate score, choose feedback,
  create evidence, or duplicate a generated API model.
- The generated presentation exposes answer/scoring internals or unsafe
  feedback content.
- Protected response/result/evidence state would be persisted in browser
  storage, analytics, logs, URL, or diagnostic text.
- Retry cannot reuse the exact submission ID safely, double activation can
  create multiple logical requests, or terminal completion offers an implicit
  retake.
- Accessibility, theme, contrast, focus, reflow, forced-color, or advice
  boundaries cannot pass without weakening accepted standards.
- A new shared token/icon/component-library decision, backend change,
  history/projection, public hosting, AI, recovery, or other non-scope is
  required; canonical sources conflict; or active scope overlaps.

## Required Handoff

Report the generated operations consumed, UI state union, submission-ID and
retry behavior, form/result semantics, focus/announcement behavior, safe-error
mapping, theme/accessibility/browser results, baseline hashes, build output,
dependency review, documentation changes, manual/external gaps, residual UI
risks, and the exact cross-system behaviors handed to WRK-0010.

## Planning History

- 2026-08-05: Shaped from SLI-0002 boundary seam 5 after WRK-0008; planning approval and implementation activation remain separate local-only stages.
