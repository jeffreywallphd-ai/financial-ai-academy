---
id: SLI-0123
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: CAP-0030
depends_on: ["SLI-0122"]
decision_gates: []
---

# Vertical Slice: Understand Learning Path State in Plain Language

## Outcome and User Scenario

A learner opens an exact approved learning path, understands how its activities
connect, sees what is complete, required, optional, available, or blocked, and
knows what to do when the path cannot be shown. Primary copy uses task-focused
language rather than graph, projection, policy, or pipeline terminology. Exact
identifiers, versions, digests, source references, evaluation facts, and reason
codes remain available in accessible `Technical record` disclosures.

## Scope Boundaries

### In Scope

- Learner-facing headings, view labels, activity groupings, relationship text,
  state labels, reason explanations, and informational notices on the delivered
  curriculum route.
- Plain bounded loading, invalid-link, session, permission, missing-version,
  unavailable, invalid-response, and unexpected-error language with an existing
  safe next action where one is available.
- Progressive disclosure for graph identity, navigation-policy identity,
  schema, digests, evaluation time, reason codes, reason references, source
  references, and exact curriculum/activity identifiers.
- Focused component and Chromium evidence for unchanged state meaning, complete
  technical facts, safe failures, list/map parity, themes, keyboard operation,
  forced colors, reduced motion, narrow layouts, and scaled text.
- Anti-rigidity checks that use roles, actions, state meaning, and required facts
  without freezing full prose, fixture counts, or cosmetic presentation.

### Out of Scope

- Contract, API, generated-client, graph, navigation-policy, reason-code,
  eligibility, completion, requirement, availability, authorization, or
  activity-launch behavior.
- Recommendation, ranking, mastery, competency, grading, retained-evidence, or
  lesson-content changes.
- Domain or transport renaming, new persistence, localization, visual tokens,
  icon changes, layout polish, or formal readability/conformance claims.
- Removing or weakening exact-version, provenance, fail-closed, privacy, or
  educational-safety boundaries.

## Canonical Context and Decisions

- CAP-0030 owns the approved plain-language outcome, progressive-disclosure
  boundary, four-slice manifest, and proportionate non-rigid verification model.
- SLI-0122 established the learner-facing language standard, content style
  guide, preferred terms, and `Technical record` pattern used here.
- CAP-0005 and completed SLI-0023 own the exact curriculum graph and
  server-evaluated navigation-state semantics. This slice changes presentation
  only and does not reproduce or reinterpret Adaptation policy in the browser.
- The graph and navigation-state contracts retain exact external shapes.
  Completion remains distinct from mastery; separate completion, eligibility,
  requirement, and availability dimensions remain authoritative.
- Interface guidance requires the learner's task to remain primary while exact
  supporting evidence stays reachable and equivalent across access modes.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Clarify the complete learning-path page, activity state, bounded failures, and technical records | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Publish guidance without changing the delivered learning path | no - no observable learner increment | - | - | - | - | - | - | - | - |
| C. Replace graph terms in headings but leave state and recovery language unchanged | yes | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 11 |
| D. Rename graph, projection, policy, and state fields in public contracts | no - changes authoritative contracts and domain-facing vocabulary outside CAP scope | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the highest-scoring eligible increment. It gives the learner one
coherent path from orientation through activity status and recovery while
preserving exact server-owned facts. Candidate C would leave the most important
status and error language inconsistent. The selected cut is independently
verifiable and reversible because it changes presentation and presentation
tests only.

## Boundary Path

1. The protected route establishes the existing private learner session and
   loads the same exact graph and navigation-state pair.
2. Existing validators require the complete closed graph, matching identity and
   digest, and one server-owned state record for every activity.
3. The page presents the curriculum as a learning path with familiar view,
   grouping, connection, activity, and state language.
4. Each activity preserves the four separate state dimensions and explanations
   while exact reason codes and references move to accessible technical detail.
5. Exact graph, policy, schema, source, digest, identity, and evaluation facts
   remain available under `Technical record` disclosures.
6. Existing fail-closed states continue to hide protected or partial facts and
   explain the learner's safe next step without internal pipeline vocabulary.
7. Component and Chromium checks verify meaning, actions, evidence, access
   modes, and flexible shapes rather than exact prose or cosmetic layout.

## Contracts, Data, and Provenance

No public transport, domain, generated-client, persistence, or navigation
contract changes. Exact curriculum ID/version, graph digest, schema, publication
facts, source references, navigation policy ID/version, evaluation time,
source-set digest, projection digest, activity IDs, state dimensions, reason
codes, and reason references remain authoritative and unchanged.

Primary copy explains what the learner can understand or do. `Technical record`
disclosures retain the exact diagnostic and provenance facts, remain keyboard
reachable and screen-reader understandable, and require no separate permission
or route. The browser does not infer eligibility, completion, mastery, or a
recommended path.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Understand the path | The page describes an approved learning path and its activities without making graph/projection language primary | Component/browser |
| Compare views | List and map controls expose equivalent facts with learner-focused accessible names | Component/browser |
| Understand activity status | Every activity keeps separate completion, requirement, availability, and readiness meaning plus its explanations | Component/browser |
| Inspect connections | Prerequisite, membership, and sequence connections use direct relationship descriptions and support empty/variable sets | Component/unit |
| Inspect technical evidence | Exact IDs, versions, source references, schema, policy, evaluation time, digests, reason codes, and references remain reachable under `Technical record` | Component/browser |
| Avoid false authority | The page does not claim mastery, competency, recommendation, ranking, or browser-owned eligibility | Component/browser |
| Recover safely | Invalid links, missing versions, denied access, unavailable data, and invalid responses stay bounded and give a plain safe next step where one exists | Component/browser |
| Preserve access parity | Light, dark, system, keyboard, forced-color, reduced-motion, narrow, and scaled-text modes retain equivalent content, actions, and hierarchy | Browser/design |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The planned dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0073 | Clarify the learning-path page, connections, activity-state presentation, and technical records | none | none | ready |
| JIT-B | Clarify loading and bounded recovery states while preserving fail-closed behavior | JIT-A | none | captured |
| JIT-C | Qualify the complete learning-path experience in Chromium, reconcile documentation, and close the slice | JIT-B | none | captured |

## Verification and Qualification

Run focused curriculum component tests after each presentation seam, then the
pinned Chromium curriculum suite for the complete flow. Run TypeScript
typecheck and lint, the production build when browser evidence needs it,
design-system, planning, documentation, Git whitespace, affected verification,
and `python dev-tools/agent/check_ready.py` before handoff.

Verification is proportionate: presentation packets do not select unrelated
backend, database, or live suites unless affected-file routing requires them.
Whitespace-only, cosmetic, and nonfunctional styling findings do not trigger a
full correction/re-review loop. Tests assert semantic roles, actions, separate
state meaning, required technical facts, and safe boundaries rather than exact
sentences, card counts tied to one fixture, or pixel styling.

## Rollback and Migration

The changes are presentation-only and require no data or schema migration.
Rollback restores prior learner-visible labels, error copy, documentation, and
tests together while leaving graph, state, session, authorization, provenance,
and persistence records untouched.

## Stop Conditions

Stop for changed eligibility, completion, requirement, availability, graph,
reason-code, authorization, exact-version, activity-launch, recommendation,
mastery, grading, or provenance semantics; removal of technical evidence; new
public contracts or persistence; legal/risk disclosure changes; conflicting
canonical language; scope collision; or material CAP-0030 drift. Do not stop or
re-open approval for whitespace, copy-fit, or nonfunctional visual-polish
findings; fix them locally when trivial or defer them to CAP-0031.

## Documentation Impact and Completion Evidence

Update the web feature README for the revised learner-facing terminology and
progressive-disclosure boundary. On completion, record focused component and
Chromium results, affected and aggregate readiness receipts, unchanged
contracts/semantics, assumptions, residual gaps, and any decision gate.

## Planning History

- 2026-10-16: Refined as the second CAP-0030 increment after SLI-0122.
  Candidate A scored 14/14 because it delivers one coherent learning-path,
  activity-state, recovery, and technical-record experience while leaving all
  graph and navigation authority unchanged. Three just-in-time work seams keep
  implementation bounded without creating lower-level approval gates.
- 2026-10-16: Refined JIT-A as WRK-0073 around the ready learning-path
  presentation, separate activity-state meaning, accessible complete technical
  records, focused component evidence, and presentation-only documentation.
