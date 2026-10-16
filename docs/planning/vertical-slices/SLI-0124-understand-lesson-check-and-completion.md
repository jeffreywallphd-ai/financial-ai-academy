---
id: SLI-0124
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: CAP-0030
depends_on: ["SLI-0122"]
decision_gates: []
---

# Vertical Slice: Understand Lesson, Check, and Completion

## Outcome and User Scenario

A learner opens an approved lesson, understands what is loading or unavailable,
checks one answer, interprets the result, and later recognizes the saved
completion without needing to understand packages, projections, replay, or
storage. The main flow states what happened, what was protected or recorded,
and what the learner can do next. Exact lesson, assessment, score, evidence,
event, version, digest, and publication facts remain available through
accessible `Technical record` disclosures.

## Scope Boundaries

### In Scope

- Task-focused lesson loading, publication, source, and recovery language.
- Direct knowledge-check loading, result, retry, conflict, session, unavailable,
  and safety-check messages with an existing safe next action where one exists.
- A plain saved-completion summary that preserves the distinction among one
  completed knowledge check, lesson completion, mastery, certification,
  suitability, performance, and investment advice.
- Progressive disclosure for package, assessment, item, policy, attempt,
  evidence, event, source, version, digest, and rebuild facts.
- Focused component and Chromium evidence for unchanged answer secrecy,
  deterministic grading, retained-evidence completeness, safe retry identity,
  fail-closed behavior, accessibility, themes, and flexible evidence history.
- Anti-rigidity assertions based on roles, actions, required facts, and semantic
  limitations rather than complete prose, fixed record counts, or styling.

### Out of Scope

- Assessment definition, scoring, feedback selection, attempt, completion-event,
  learner-model, session, authorization, exact-version, or persistence changes.
- New retake, mastery, competency, certification, recommendation, or lesson-
  completion policy.
- Correct-answer exposure, client-side grading, learner-selected identity, or
  removal of retained provenance.
- Changes to the educational-use or investment-advice limitation, visual tokens,
  icons, layout polish, localization, or public/generated contracts.

## Canonical Context and Decisions

- CAP-0030 owns the approved plain-language outcome, progressive-disclosure
  boundary, four-slice manifest, and proportionate non-rigid verification model.
- SLI-0122 established the user-facing language standard, content style guide,
  error order, and `Technical record` pattern used here.
- ADR-0005 and the Assessment contract keep Assessment authoritative for
  definitions, deterministic scoring, feedback, attempts, evidence, and the
  bounded completion event. Learner model owns the derived completion view.
- ADR-0006 and the identity contract keep sessions server-owned and opaque;
  learner copy may explain failure but cannot change session or permission
  behavior.
- The content-package contract keeps exact published lesson identity, version,
  digest, sources, and safe rendering authoritative. A newer lesson is never
  substituted silently.
- Education-versus-advice guidance requires the completion limitation to remain
  accurate and prominent enough to prevent mastery, suitability, performance,
  or investment-advice inference.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Clarify the complete lesson-to-check-to-saved-completion experience | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Clarify lesson loading and errors only | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Clarify assessment and completion only | yes | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 13 |
| D. Simplify evidence by removing exact identifiers and limitation language | no - weakens accepted evidence and risk boundaries | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the highest-scoring eligible cut because it gives one coherent
learner journey from opening the lesson through interpreting a saved result.
It receives full value and end-to-end scores because every learner-facing state
in the delivered lesson loop is covered; full decision and contract scores
because accepted contracts settle all semantics; full independence because it
changes only this feature's presentation and tests; full verification because
component, mocked Chromium, and live evidence already exercise the seam; and
full reversibility because no data or contract migration exists. Candidate B
has lower value and completeness because assessment jargon would remain.
Candidate C has high value but loses end-to-end completeness because route and
session messages would remain inconsistent. Candidate D is ineligible.

## Boundary Path

1. The existing protected route establishes the same server-owned learner
   session and resolves the same exact lesson placement.
2. The lesson page presents its purpose, objectives, body, sources, and
   educational-use limitation while publication facts move into task-focused
   context and an accessible technical record.
3. The knowledge-check component first reads the same derived completion view;
   incomplete state loads the same answer-safe presentation and completed state
   opens the same saved evidence without requesting another assessment.
4. The learner submits the same exact-version tokens and selected option; the
   server remains the sole grading authority and returns reviewed feedback.
5. Primary result and recovery copy explains the learner-visible outcome,
   record protection, and next action. Exact provenance stays selectable under
   `Technical record`.
6. Focused and live browser checks verify the complete journey, protected facts,
   safe retry identity, no answer leak, access parity, and unchanged contracts.

## Contracts, Data, and Provenance

No public schema, API, generated client, domain, persistence, event, identity,
or grading change is permitted. Exact placement, package, assessment, item,
policy, attempt, evidence, submission, and event identities; semantic versions;
digests; score and maximum score; feedback; timestamps; source-set identity;
publication facts; and educational-use limitations retain their current meaning.

The main flow may say `Saved completion`, `Progress updated`, or `Safety checks`
when that wording preserves the exact contract. `Technical record` disclosures
retain every required package/assessment/evidence field in labeled groups on
the same authorized page. The browser never derives correctness, changes
feedback, treats completion as mastery, or exposes the private answer.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Open the lesson | Loading and ready states describe the learner task; publication and source facts remain available without package terminology dominating the page | Component/browser |
| Recover from lesson failure | Session, permission, missing-version, unavailable, invalid-content, and unexpected states state what failed, what was protected, and the existing next action | Component/browser |
| Take the check | The answer-safe prompt and choices remain unchanged in meaning; `Check answer` submits the exact contract with no client learner or grading authority | Component/browser/live |
| Interpret the result | Correct and incorrect results show reviewed feedback, score meaning, and the bounded non-mastery limitation in direct language | Component/browser/live |
| Retry safely | Network retry reuses the same submission identity, conflict asks for reload, and denial/unavailable messages do not imply a recorded result | Component/browser |
| Reopen saved completion | The learner sees one saved completion summary and limitation while no new assessment presentation or answer is requested | Component/browser/live |
| Inspect technical evidence | Every exact lesson, assessment, item, policy, source, score, timestamp, attempt, evidence, event, version, and digest fact remains keyboard reachable under `Technical record` | Component/browser/live |
| Preserve flexible access | Empty/incomplete, single/multiple history, light/dark/system, keyboard, forced-color, reduced-motion, narrow, and scaled-text modes keep equivalent meaning and actions | Component/browser/design |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The planned dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| JIT-A | Clarify lesson loading, publication context, and bounded route recovery with focused component evidence | none | none | planned |
| JIT-B | Clarify knowledge-check result, retry, saved-completion summary, and technical records with focused component evidence | JIT-A | none | planned |
| JIT-C | Qualify the complete lesson and saved-completion experience in Chromium, reconcile documentation, and close the slice | JIT-B | none | planned |

## Verification and Qualification

Run focused lesson-reading and knowledge-check component tests after their
owned presentation seams, followed by the pinned lesson-reading Chromium suite
and the existing approved-lesson live path for the complete flow. Run TypeScript
typecheck and lint, production build when browser evidence needs it, design-
system, planning, documentation, Git whitespace, affected verification, and
`python dev-tools/agent/check_ready.py` before closure.

Verification is proportionate. Presentation work does not select unrelated
backend/database suites unless affected routing requires them; the existing live
suite is used only for the end-to-end grading/evidence seam. Whitespace-only,
cosmetic, and nonfunctional styling findings are fixed locally when trivial or
deferred to CAP-0031 and do not trigger full correction/re-review. Tests assert
meaning, actions, limitations, and required facts rather than exact paragraphs,
pixel styling, or one fixture's record count.

## Rollback and Migration

Changes are presentation, documentation, and verification only. No schema or
data migration exists. Rollback restores prior copy and tests together while
leaving lesson, assessment, learner-model, identity, session, evidence, and
publication records unchanged.

## Stop Conditions

Stop for changed scoring, feedback selection, completion or mastery meaning,
answer exposure, session/authorization behavior, exact-version resolution,
evidence/event/provenance retention, educational-use or investment-advice
meaning, public contracts, persistence, new visual-system decisions, conflicting
canonical language, active scope collision, or material CAP-0030 drift. Do not
stop or reopen approval for whitespace, copy fit, or nonfunctional visual polish;
fix it locally when trivial or defer it to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery updates the lesson feature documentation where necessary and records
focused component, browser, live-seam, design, planning, documentation, affected-
verification, and readiness results. Completion evidence must identify changed
presentation boundaries, preserved contracts and evidence fields, tested safe
failures, assumptions, known gaps, and any residual decision gate.

## Planning History

- 2026-10-16: Refined as the third CAP-0030 increment after the shared language
  standard. Candidate A scored 14/14 because it provides one coherent lesson,
  answer-check, saved-completion, and recovery experience while leaving all
  content, assessment, learner-model, identity, evidence, and risk authority
  unchanged. Three just-in-time packet seams keep changes independently
  reviewable without creating packet- or slice-level approval gates.
