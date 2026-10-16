---
id: WRK-0071
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0122
capability: CAP-0030
depends_on: ["WRK-0069"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/learning-catalog/LearningOpportunityDetailPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityDetailRoute.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityComparisonPage.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityComparisonRoute.tsx", "apps/web/src/styles/learning-catalog.css", "apps/web/tests/component/learningOpportunityDetail.test.tsx", "apps/web/tests/component/learningOpportunityComparison.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0071-clarify-opportunity-detail-comparison-and-errors.md", "docs/planning/vertical-slices/SLI-0122-choose-learning-opportunities-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 5f43bce7a658ad45808b9cf72fc5e44a53a98d58
claim_id: WRK-0071:45182ee8-5477-4948-ac42-77637b2c19dc
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T09:36:53Z
---

# Agent Work Packet: Clarify Opportunity Detail, Comparison, and Errors

## Objective and Deliverable

Apply the accepted learner-facing language contract to the complete learning-
opportunity detail and comparison presentation. A learner can understand what
each page shows, compare unchanged educational facts, open an available lesson,
return to the learning library, and recover from bounded failures without
software, projection, schema, or pipeline vocabulary in the primary flow.

Exact identifiers, versions, digests, fingerprints, generation, and schema
facts remain complete under keyboard-operable `Technical record` disclosures.
The packet changes presentation and focused component evidence only.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`, and
`testing-quality` packs. Read CAP-0030, SLI-0122, WRK-0068, WRK-0069, the
interface design and content style guides, user-facing language and interface
standards, testing standards, product/domain/risk meaning for discovery, all
four affected components, their component tests, the generated-client boundary,
the learning-catalog model/fixture, shared `StatusPanel`, catalog CSS, and
`apps/web/README.md` before editing.

## Decisions and Assumptions

- CAP-0030 and SLI-0122 authorize presentation-only clarification. Catalog,
  selection, session, availability, exact-placement, provenance, and fail-
  closed behavior remain unchanged.
- The shared language standard requires task meaning in the primary flow and
  permits exact support facts in an accessible `Technical record`.
- Publication facts, review date, educational-use notice, availability reason,
  prerequisites, topics, objectives, level, and duration remain visible without
  opening the technical disclosure.
- Version labels remain kind-sensitive where necessary; package identity and
  cryptographic/projection details belong in the technical record.
- Non-functional styling preferences discovered during this packet are
  nonblocking and deferred to CAP-0031 unless they impair function,
  comprehension, accessibility, contrast, hierarchy, responsive use, safety,
  or this packet's acceptance scenarios.
- Tests protect actions, required facts, accessible names, safe recovery, and
  technical-record reachability rather than freezing full prose.

## In Scope

- Task-focused detail and comparison headings, explanatory copy, fact labels,
  action labels, loading messages, error titles, descriptions, and safe next
  actions.
- `Lesson version`/kind-appropriate version presentation and `Open lesson` for
  the unchanged available-lesson destination.
- Accessible `Technical record` disclosures for opportunity identity, package
  identity/digest, source fingerprint, projection generation, and schema.
- Plain `Publication details` language while retaining publisher, publication
  date, review date, and educational-use notice.
- Component tests for required meaning, technical evidence, flexible kinds,
  ordering, non-ranking language, safe failure/denial, accessible actions, and
  anti-jargon/anti-rigidity behavior in the regions owned by this packet.
- Minimal reuse of existing catalog styles for the disclosure only when needed
  for accessibility and hierarchy; no discretionary visual redesign.
- Reconciliation of the delivered-route documentation and planning evidence.

## Out of Scope

- Catalog list/filter/card work completed by WRK-0069; Chromium/live
  qualification reserved for JIT-D; curriculum, lesson/completion, or changed-
  copy checker work reserved for later CAP-0030 slices.
- Changes to URL parsing, query behavior, selection order, API calls, generated
  clients, model validation, fingerprints, generation verification, sessions,
  authorization, availability, destinations, or error-state selection.
- New design tokens, icons, component libraries, layout redesign, persisted
  comparisons, ranking, recommendations, eligibility inference, localization,
  or external content services.
- Rewriting the educational-use notice or other financial/risk disclosure.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public/domain contracts | generated client, catalog model, query/selection semantics | none | Confirm exact facts and behavior remain unchanged |
| Detail presentation | detail page and route, shared status panel | two named detail components | Clarify primary content, technical disclosure, loading, and bounded errors |
| Comparison presentation | comparison page and route | two named comparison components | Clarify comparison facts/actions without ranking or reordering |
| Styling | shared catalog stylesheet and tokens | named catalog stylesheet only if disclosure accessibility requires it | Reuse existing semantic tokens and avoid visual redesign |
| Focused evidence | detail/comparison fixtures and component suites | two named component tests | Protect meaning, actions, evidence reachability, and anti-rigidity |
| Documentation/planning | web README, packet, parent slice, register | named files | Reconcile delivered terminology, packet state, and evidence |

## Contracts and Interfaces

The packet consumes the unchanged `LearningOpportunity`,
`LearningOpportunityProjectionIdentity`, selection-route state, generated
discovery client, session boundary, and exact destination contracts. It
produces no public schema, client, model, persistence, API, or event change.

JIT-D receives the same routes and runtime behavior with stable learner-facing
names, accessible technical disclosures, and focused component expectations to
qualify in Chromium. Required exact evidence remains selectable text and is not
shortened, reformatted, or recomputed.

## Dependencies and Parallel Safety

WRK-0069 is complete and supplies the shared discovery wording/disclosure
pattern. This packet is serial within SLI-0122 because it changes the remaining
detail/comparison presentation and establishes the browser assertions consumed
by JIT-D. It is not declared parallel-safe with another packet; exact-file
leasing must still allow unrelated repository work to proceed.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Inspect an opportunity | A validated current record | The detail page renders | The learner sees task-focused facts, kind-appropriate version wording, publication details, availability reason, and `Open lesson` only for an available lesson | Detail component tests |
| Reach technical evidence | A validated record and projection | The learner opens `Technical record` | Opportunity/package identity, digest, source fingerprint, generation, and schema remain labeled, complete, keyboard reachable, and selectable | Detail accessibility assertions |
| Compare selections | Two through four validated records in learner order | The comparison renders | The page preserves order and facts, uses the same plain terms, and states it does not rank, recommend, or decide eligibility | Comparison component tests |
| Non-openable item | A planned, unavailable, or non-lesson item | Detail/comparison actions render | Details remain available, but no lesson-opening action is invented | Detail/comparison component tests |
| Loading | Navigation or revalidation is pending | A loading state renders | The message names the learner task without session-establishment, projection, or catalog-generation jargon | Route component tests |
| Changed selection | The selected ID is absent from the validated current catalog | The bounded state renders | The message says the item is no longer in the current learning library and offers the existing safe return action without partial facts | Route component tests |
| Session or response failure | The existing unauthorized, forbidden, unavailable, invalid, or unexpected state occurs | The bounded state renders | The message leads with what could not be done, protects private/partial facts, and offers only the existing safe action | Parameterized route tests |
| Flexible kinds and prose | Lesson and project records plus future harmless wording changes | Components are tested | Labels stay kind-sensitive and assertions protect roles/phrases rather than whole paragraphs or one fixture count | Anti-rigidity component tests |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/component/learningOpportunityDetail.test.tsx apps/web/tests/component/learningOpportunityComparison.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0071`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

JIT-D owns the full learning-catalog Chromium and live-boundary qualification.
This packet does not require Docker, backend, database, generated-client, or
live tests unless an actual changed path or discovered behavior crosses those
boundaries.

## Documentation and Evidence Update

Update `apps/web/README.md` only where the delivered detail/comparison language
or technical-record presentation is named. Update this packet, SLI-0122, and
the planning register together. Do not change canonical domain/contract/risk
sources because their meaning is unchanged. Completion evidence records focused
checks, affected-verification selection, assumptions, and known gaps without
tracked approval or reviewer information.

## Stop Conditions

Stop for changed domain/API/query/selection/session/authorization/availability/
destination/provenance meaning; missing required facts; disclosure of private
details; removal of technical evidence; changed risk language; a new token,
icon, or visual system; a universal prose/readability gate; a required browser
behavior change; unresolved canonical conflict; material CAP-0030 drift; or an
overlapping active file lease.

## Required Handoff

Report the revised learner actions and states, retained exact facts, unchanged
behavioral boundaries, component/type/lint/design/documentation/planning/
readiness and affected-verification results, assumptions, residual browser
qualification left to JIT-D, and any non-functional styling item deferred to
CAP-0031.

## Completion Evidence

- Delivered task-focused detail, comparison, loading, bounded-error, and safe-
  action language while preserving the existing routes and fail-closed state
  selection.
- Retained kind-sensitive versions, publication and educational-use facts, and
  complete opportunity/package identifiers, digests, source fingerprint,
  generation, and schema values in native keyboard-operable `Technical record`
  disclosures.
- Verified 24 focused component scenarios, TypeScript type checking, lint, the
  design-system, planning and documentation integrity, production build, Git
  whitespace, and all 27 aggregate readiness checks. Fresh affected
  verification passed every selected planning, documentation, type, lint,
  unit, and build check for the exact corrected candidate.
- Closed the comprehension defect found during review by removing session-
  establishment wording from loading states and testing only those status
  regions. The distinct unauthorized state retains its canonical learner-
  session explanation.
- No public contract, generated client, query, ordering, selection,
  authorization, availability, provenance, persistence, or migration changed.
  Full learning-library Chromium qualification remains assigned to JIT-D.

## Planning History

- 2026-10-16: Refined JIT-C after WRK-0069 completed. The packet applies the
  accepted language and technical-record pattern to detail, comparison,
  loading, and bounded failure presentation without changing discovery or
  selection behavior.
- 2026-10-16: Completed WRK-0071 after exact-candidate affected verification,
  focused and aggregate checks, and correction of loading copy that still used
  session-establishment language. JIT-D is now dependency-ready.
