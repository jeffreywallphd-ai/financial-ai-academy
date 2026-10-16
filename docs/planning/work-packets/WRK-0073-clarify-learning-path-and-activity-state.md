---
id: WRK-0073
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0123
capability: CAP-0030
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/curriculum-graph/CurriculumGraphPage.tsx", "apps/web/tests/component/curriculumGraph.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0073-clarify-learning-path-and-activity-state.md", "docs/planning/vertical-slices/SLI-0123-understand-learning-path-state-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 13491dcb293bee5cb6b611c605e9cb3131e9c13f
claim_id: WRK-0073:f4512c22-b67f-452f-bfe9-b3d282e45b9c
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:01:14Z
---

# Agent Work Packet: Clarify Learning Path and Activity State

## Objective and Deliverable

Apply the accepted learner-facing language contract to the ready curriculum
page. A learner can understand the learning path, its groups and connections,
and each activity's separate completion, requirement, availability, and
readiness meaning without graph, projection, policy, identifier, or reason-code
terminology competing with the primary task.

Exact curriculum/activity identities, resource references, relationship IDs,
source references, schema, policy, evaluation time, digests, reason codes, and
reason references remain complete in keyboard-operable `Technical record`
disclosures. The packet changes presentation and focused component evidence
only.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`,
`learning-adaptation`, and `testing-quality` packs. Read CAP-0030, SLI-0123,
WRK-0068, the interface and content style guides, user-facing language and
interface standards, CAP-0005/SLI-0023, the graph and navigation-state
contracts, the curriculum page/model/fixture/component test, and
`apps/web/README.md` before editing.

## Decisions and Assumptions

- CAP-0030 and SLI-0123 authorize presentation-only clarification. Exact graph,
  state, session, authorization, provenance, and fail-closed behavior remain
  unchanged.
- The four state dimensions remain separate. Learner-facing `Ready to start`
  can label the existing eligibility dimension, but it does not change or infer
  eligibility.
- Completion remains explicitly distinct from mastery or competency judgment.
- Exact IDs, versions, codes, references, policies, and digests stay available
  in accessible `Technical record` disclosures rather than being deleted.
- No activity-opening action exists in the current route, so this packet does
  not add one.
- Tests protect roles, actions, state meaning, prohibited authority claims, and
  required technical facts rather than full prose, one fixture cardinality, or
  cosmetic styling.
- Whitespace-only and nonfunctional visual-polish findings are nonblocking;
  fix them locally when trivial or defer them to CAP-0031 without re-review.

## In Scope

- Learner-focused page, view, objective, competency, grouping, ungrouped-
  activity, connection, publication, source, and return labels.
- Plain labels and explanations for the unchanged completion, requirement,
  availability, and eligibility/readiness values; the exact recorded reason
  wording remains in the technical record with its code and references.
- `Technical record` disclosures for each activity's exact identity/resource
  and reason codes/references, relationship IDs/types, and complete page-level
  graph/navigation provenance.
- Focused component tests for the revised semantic names, separate state
  meaning, complete technical records, flexible path shapes, view parity, no
  invented launch action, and no mastery/recommendation claim.
- Reconciliation of the delivered-route README and planning evidence.

## Out of Scope

- Route loading/error/recovery copy, reserved for the next SLI-0123 packet.
- Chromium/live qualification and slice closure, reserved for the final packet.
- Changes to URL parsing, API calls, validators, generated clients, models,
  contracts, server policies, graph ordering, state values, reasons,
  authorization, sessions, or activity destinations.
- New design tokens, icons, layout redesign, animations, visual polish,
  localization, recommendation/ranking, mastery, grading, or external services.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Contracts/domain | graph/navigation contracts, generated client, model | none | Confirm exact facts and authority remain unchanged |
| Learning-path presentation | curriculum page and shared icons | named page only | Clarify primary language and progressive disclosure |
| Focused evidence | fixture and component suite | named component test only | Protect semantics and exact evidence without prose rigidity |
| Documentation/planning | web README, packet, parent slice, register | named files | Reconcile terminology, scope, state, and evidence |

## Contracts and Interfaces

The packet consumes the unchanged `CurriculumGraph`, `NavigationState`,
`ActivityNavigationState`, presentation-order helper, exact protected route,
and server-provided reason explanations. It produces no public schema, model,
client, persistence, route, or API change.

The next packet receives the same ready-state component with stable
learner-facing names and complete technical disclosures; it only owns the
route-level loading and bounded failure presentation.

## Dependencies and Parallel Safety

SLI-0122 is complete and supplies the language and progressive-disclosure
contract. This is the first serial packet in SLI-0123. It is not declared
parallel-safe with another packet because later work consumes its accessible
names and evidence pattern. Exact-file leasing still permits unrelated work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Understand the path | A validated exact graph/state pair | The page renders | Primary headings describe a learning path, activities, groups, and connections without graph/projection vocabulary | Component tests |
| Understand activity status | Any activity state | The activity renders | Completion, requirement, availability, and readiness remain separate and server-provided explanations stay visible | Component tests |
| Inspect activity evidence | An activity with reasons and references | The learner opens its `Technical record` | Exact activity/resource identity plus reason codes and references remain complete and labeled | Component disclosure tests |
| Inspect path evidence | An exact graph/state pair | The learner opens the page `Technical record` | Version, publication, source, schema, policy, evaluation time, and all digests remain complete and labeled | Component disclosure tests |
| Inspect connections | Variable or empty relationships | The page renders | Direct connection descriptions remain understandable; exact relationship IDs/types are available technically | Component flexible-shape tests |
| Preserve authority | Any ready page | Learner-visible copy is inspected | No ranking, recommendation, eligibility inference, launch action, or mastery/competency claim is introduced | Component negative assertions |
| Compare views | The learner switches list/map view | Both views render | Equivalent facts and learner-focused accessible names remain available | Component tests |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/component/curriculumGraph.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0073`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

The packet does not require Docker, backend, database, generated-client, or live
tests unless affected-file routing selects them. Full Chromium qualification is
owned by the final SLI-0123 packet.

## Documentation and Evidence Update

Update `apps/web/README.md` only where this delivered ready-state terminology or
technical-record presentation is described. Update this packet, SLI-0123, and
the planning register together. Completion evidence records focused checks,
affected-verification selection, assumptions, and gaps without tracked approval
or reviewer information.

## Stop Conditions

Stop for changed graph/state/reason/session/authorization/exact-version/
provenance semantics; a new learner action; removed technical evidence; domain
or API renaming; recommendation, ranking, mastery, or grading meaning; new
design tokens/icons; unresolved canonical conflict; CAP-0030 drift; or a
colliding active file lease. Do not stop or reopen review for whitespace,
copy-fit, or nonfunctional visual polish.

## Required Handoff

Report the revised learner-facing path and state language, retained exact facts,
unchanged behavioral boundaries, focused/type/lint/design/documentation/
planning/readiness and affected-verification results, assumptions, recovery-
copy work left to the next packet, browser work left to the final packet, and
any cosmetic item deferred to CAP-0031.

## Completion Evidence

- Delivered an approved learning-path presentation with learner-focused group,
  connection, progress, readiness, requirement, availability, and reason
  language. The list and map views retain equivalent facts, and no launch,
  recommendation, ranking, mastery, or browser-owned state inference was added.
- Preserved exact curriculum/activity/resource identity, resource digests,
  graph and navigation schemas, graph/policy identity, exact evaluation time,
  source references, graph/source-set/projection digests, state values, reason
  codes, recorded explanations, reason references, and relationship identity
  in keyboard-operable `Technical record` disclosures.
- Focused component qualification passed all 11 curriculum scenarios, including
  flexible graph shapes and computed fixture cardinality. TypeScript typecheck,
  lint, design-system, planning, documentation, Git whitespace, and aggregate
  readiness checks passed.
- Exact corrected candidate
  `8a81dcbba3b875c6e395829f5dfb0d43faa8a2ef` received a qualifying affected-
  verification receipt at `.local-codex/control-plane/receipts/WRK-0073/`
  `8a81dcbba3b875c6e395829f5dfb0d43faa8a2ef/`
  `20261016T100903Z-55cbe5c4-c6a1-4671-813e-29bfab59181b.json`.
- Independent R01 identified that `unassigned` had collapsed into unavailable
  and that exact navigation schema/time evidence was incomplete. The corrected
  descendant gives `unassigned` its distinct `Not in a group` label and exposes
  the complete exact provenance set; R02 accepted both closures with no new
  substantive finding.
- Public contracts, generated clients, graph/state/reason semantics, sessions,
  authorization, ordering, activity actions, persistence, and migrations are
  unchanged. Route recovery language remains JIT-B; Chromium qualification
  remains JIT-C. No cosmetic issue blocked delivery or required re-review.

## Planning History

- 2026-10-16: Refined SLI-0123 JIT-A around the ready learning-path page,
  separate activity-state meaning, complete technical records, focused
  component evidence, and presentation-only documentation boundaries.
- 2026-10-16: Submitted implementation candidate
  `6fd652ba0e7029550568416a9c8058558bbb8d7a` after focused component,
  typecheck, lint, planning, documentation, design-system, whitespace, and
  aggregate-readiness checks passed.
- 2026-10-16: Completed WRK-0073 on corrected exact candidate
  `8a81dcbba3b875c6e395829f5dfb0d43faa8a2ef` after fresh affected verification
  qualified and independent R02 closed the two R01 state/provenance findings.
