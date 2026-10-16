---
id: SLI-0122
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: CAP-0030
depends_on: []
decision_gates: []
---

# Vertical Slice: Choose Learning Opportunities in Plain Language

## Outcome and User Scenario

A learner opens the learning catalog, filters the available opportunities,
inspects or compares selections, and opens an available lesson using familiar,
task-focused words. The learner sees publication and educational-use facts in
the normal flow while versions, identifiers, digests, and source records remain
available in an accessible `Technical record` disclosure.

The same increment establishes the repository language standard and initial
term map so later interface work applies the pattern consistently rather than
making isolated copy substitutions.

## Scope Boundaries

### In Scope

- A normative learner-facing language standard covering audience, task-first
  structure, familiar words, active/direct explanations, actionable errors,
  progressive disclosure, specialist-term exceptions, and content review.
- A design content style guide with voice, preferred terms, reviewed examples,
  error and status patterns, and the boundary between primary learner copy and
  intentionally technical records.
- Workflow links from agent, interface, context-routing, change-impact, and
  planning guidance where they materially route learner-facing copy changes.
- Catalog, filter, detail, and comparison language, including `Topic`, `Show
  results`, `Lesson version`, `Open lesson`, and `Technical record`.
- Plain descriptions for session establishment, current-catalog mismatch,
  invalid response, loading, empty, denied, and retry states without changing
  their safe fail-closed behavior.
- Focused component and Chromium checks for the revised accessible names,
  preserved facts/actions, progressive disclosure, errors, themes, responsive
  behavior, and flexible catalog shapes.

### Out of Scope

- Contract, API, generated-client, query, selection, authorization,
  availability, exact-version, provenance, or catalog-generation semantics.
- Curriculum graph/navigation copy, lesson and retained-completion copy, or the
  reusable changed-copy checker; those remain SLI-0123 through SLI-0125.
- Domain renaming, localization, external grammar or AI services, visual token
  changes, icon changes, legal/risk disclosure changes, and formal standards
  compliance claims.
- Removing package versions, digests, publication sources, educational-use
  notices, or any current safe-error boundary.

## Canonical Context and Decisions

- CAP-0030 owns the accepted plain-language outcome, progressive-disclosure
  boundary, four-slice manifest, and non-rigid verification posture.
- The product vision, domain glossary, and risk guidance retain semantic
  authority. Presentation may clarify those meanings but not redefine them.
- Interface design guidance requires the learner's next task to remain primary,
  supporting evidence to remain available, and equivalent content and actions
  across themes, responsive layouts, and assistive technology.
- CAP-0004 and its completed slices own discovery ordering, filtering,
  selection, exact placement, provenance, failure behavior, and live evidence.
  This slice changes presentation only.
- ASD-STE100 and other external sources inform principles. Their proprietary
  text, controlled vocabulary, and conformance marks are not repository assets.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Shared language contract plus complete catalog/detail/comparison application | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Publish guidance without changing the learner experience | no - no observable learner increment | - | - | - | - | - | - | - | - |
| C. Replace visible strings without a shared content contract | yes | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 13 |
| D. Rename API and generated-client fields to match display copy | no - changes public contracts and domain-facing technical vocabulary outside CAP scope | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the highest-scoring eligible increment. It improves the complete
delivered discovery flow while creating the reusable language contract needed
by later CAP-0030 slices. Candidate C is reversible but would encourage local
synonyms and repeat the same judgment in every feature. The selected cut keeps
runtime behavior, identifiers, and external contracts unchanged, so it is
independently verifiable and low risk.

## Boundary Path

1. Canonical product, domain, risk, and interface sources define the meaning
   that learner-facing words must preserve.
2. The language standard defines required clarity outcomes, specialist-term
   exceptions, progressive disclosure, and proportionate verification.
3. The content style guide maps those rules to the application's voice,
   preferred terms, controls, statuses, errors, and technical-record pattern.
4. Catalog list, detail, and comparison components update presentation only;
   they continue consuming the same validated generated-client facts and route
   state.
5. Component and browser checks verify the new accessible names and wording,
   complete evidence visibility, safe failure states, and unchanged actions.
6. Documentation and workflow routes point future interface changes to the
   standard without adding a new human approval stage.

## Contracts, Data, and Provenance

No public transport or domain contract changes. Query parameter names, URL
shape, generated types, exact package identity, opportunity identity,
availability, publication facts, source fingerprints, projection generation,
and educational-use notice remain authoritative and unchanged.

The presentation contract distinguishes primary learner copy from a technical
record. Primary copy answers what the learner can do or understand now.
Technical disclosure retains exact versions, digests, identifiers, source
fingerprints, generation/evaluation data, and other diagnostic facts with
semantic headings and definition lists. Moving a fact into disclosure is valid
only when it remains keyboard reachable, screen-reader understandable, and
available without a separate permission or route.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Find by topic | The first topic field is labeled `Topic`, additional fields remain distinguishable, and `Show results` applies the unchanged query | Component/browser |
| Inspect a lesson | Package information is introduced as `Lesson version`; an available lesson exposes `Open lesson` and unavailable kinds remain non-actionable | Component/browser |
| Inspect supporting evidence | Publication facts and educational-use notice remain visible; exact technical facts remain complete under `Technical record` | Component/accessibility/browser |
| Compare opportunities | Every comparison preserves current facts and learner order with the same plain terms and without ranking or recommending a winner | Component/browser |
| Current selection changed | The page explains that the opportunity is no longer in the current catalog and offers the existing safe return/retry action without pipeline terminology | Component/browser |
| Session unavailable | The page says it could not start the learner session, exposes no protected facts, and provides the existing safe retry action | Component/browser |
| Flexible catalog | Empty, one-item, repeated-classification, variable-topic, planned, unavailable, and available records remain usable without copy tied to one fixture | Unit/component anti-rigidity |
| Theme and access parity | Light, dark, system, keyboard, forced-color, reduced-motion, narrow, and scaled-text modes retain equivalent words, facts, actions, and hierarchy | Browser/design |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The planned dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0068 | Establish the normative language standard, content style guide, initial term map, and workflow routing | none | none | complete |
| WRK-0069 | Apply the standard to catalog list/filter/card presentation and focused component evidence | WRK-0068 | none | complete |
| WRK-0071 | Apply the standard to detail/comparison/loading/error presentation and focused component evidence | WRK-0069 | none | complete |
| WRK-0072 | Qualify the complete revised discovery flow in Chromium, reconcile documentation, and close the slice | WRK-0071 | none | ready |

## Verification and Qualification

Run the language and documentation checks introduced by the slice; focused
learning-catalog component and browser suites; TypeScript typecheck and lint;
the production build when browser evidence needs it; design-system,
documentation, and planning checks; Git whitespace; affected verification;
and `python dev-tools/agent/check_ready.py` before handoff. Preserve the
existing live CAP-0004 evidence unless a changed path selects the live runner.

Every packet includes an anti-rigidity check appropriate to its layer. Guidance
must permit necessary specialist terms when immediately explained; tests must
prefer roles, actions, and required meaning over freezing whole prose passages;
and a copy-only change must not automatically require unrelated backend or live
database suites.

## Rollback and Migration

The standard, documentation links, copy, and tests are additive or
presentation-only. No data migration exists. Rollback restores prior labels and
documentation together; it does not touch catalog, selection, learner,
publication, or provenance records. Technical evidence remains available
throughout both directions.

## Stop Conditions

Stop for a domain or API rename; changed query, ordering, selection,
availability, authorization, exact-version, publication, provenance, or
educational-use meaning; a financial/risk/legal disclosure rewrite; removal of
technical evidence; localization or translation; external content processing;
new visual tokens or icons; formal standards claims; a mandatory universal
readability score; conflicting canonical language; scope collision; or
material CAP-0030 drift.

## Documentation Impact and Completion Evidence

Create the learner-facing language standard and content style guide, link them
from the relevant agent, interface, context-routing, change-impact, and
planning guidance, and update web-feature documentation where delivered terms
are named. Completion evidence records each revised interaction, retained
technical fact, unchanged behavior boundary, focused test result, accessibility
and theme result, anti-rigidity evidence, assumptions, and known gaps without
copying approval or reviewer records into tracked files.

## Planning History

- 2026-10-16: Refined as the first CAP-0030 increment. Candidate A scored
  14/14 because it couples the reusable content contract to an observable
  complete discovery-flow improvement while leaving public contracts, domain
  meaning, risk language, and runtime policy unchanged.
- 2026-10-16: Refined JIT-A as WRK-0068 around the normative learner-facing
  language standard, design content guide, initial preferred-term map,
  informative external-source posture, and minimum routing needed for future
  interface work.
- 2026-10-16: Activated WRK-0068 after validating the current CAP binding,
  slice membership, resolved decision posture, exact write scope, packet-start
  acceptance set, and collision-free file lease.
- 2026-10-16: Completed WRK-0068 with the normative language standard,
  content guide, initial term map, informative source posture, discoverable
  workflow routing, and proportionate anti-rigidity safeguards. JIT-B is now
  dependency-ready.
- 2026-10-16: Refined JIT-B as WRK-0069 around the learning-library result
  list, filters, cards, current-page comparison controls, focused semantic
  component evidence, and unchanged discovery/query behavior.
- 2026-10-16: Activated WRK-0069 after validating its dependency, current CAP
  authority, exact write scope, acceptance manifest, and collision-free file
  lease.
- 2026-10-16: Completed WRK-0069 with task-focused learning-library labels,
  kind-sensitive version/package descriptions, persistent topic-format help,
  accessible progressive disclosure, and anti-rigidity tests scoped only to
  their owned learner-facing regions. JIT-C is now dependency-ready.
- 2026-10-16: Refined and activated JIT-C as WRK-0071 after validating the
  current CAP binding, dependency, exact presentation/test/documentation
  scope, packet-start acceptance set, and absence of a decision gate.
- 2026-10-16: Completed WRK-0071 with plain detail, comparison, loading, and
  bounded-error presentation; accessible complete technical records; flexible
  kind labels; and exact-candidate component, build, readiness, and affected-
  verification evidence. JIT-D is ready for just-in-time refinement.
- 2026-10-16: Refined JIT-D as WRK-0072 around the existing pinned-Chromium
  learning-library suite, complete technical-record reachability, access and
  theme parity, anti-rigid assertions, and deterministic slice closure.
