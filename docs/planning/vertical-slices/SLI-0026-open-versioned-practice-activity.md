---
id: SLI-0026
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: CAP-0006
depends_on: []
decision_gates: []
---

# Vertical Slice: Open a Versioned Practice Activity

## Outcome and User Scenario

An authorized learner opens one exact published practice activity and sees its
purpose, instructions, attempt policy, approved source and review references,
and an answer-safe ordered set of structured items before responding. The
initial response set is deliberately closed: single select, multiple select,
and fixed-decimal numeric entry. The same versioned public API is usable by the
generated browser client and a non-browser/headless client; no browser-only
state, answer key, scoring authority, or AI-specific transport is introduced.

## Scope Boundaries

### In Scope

- Define a private versioned practice-activity definition for a bounded ordered
  item set with stable activity/item IDs, exact source/review references,
  purpose, instructions, attempt-policy summary, and private deterministic
  scoring declarations.
- Admit exactly three initial response types: single-select exact match,
  multiple-select exact set, and fixed-decimal numeric entry with an explicit
  exact-value or inclusive-range rule. Numeric values use canonical decimal
  strings, never binary floating-point interpretation.
- Preserve Content ownership of immutable package bytes and provenance,
  Curriculum ownership of exact placement, and Assessment ownership of item
  meaning, answer-safe presentation, response validation, and future scoring.
- Add exact-version Assessment application and protected API operations that
  return only learner-safe presentation, attempt-policy meaning, and approved
  source/review references after server-side identity and authorization.
- Expose the reviewed API through the generated TypeScript client and an
  accessible responsive browser route that renders every supported item shape
  without embedding correct answers or scoring rules.
- Keep the operation suitable for command-line, service, and future headless AI
  consumers through the same public application API. A separate AI mode,
  agent protocol, or autonomous action authority remains out of scope.
- Prove malformed, unknown-type, unsafe-reference, stale-version,
  unauthorized, unavailable, and answer-leakage failures are closed and
  create no attempt or completion evidence.

### Out of Scope

- Submitting responses, scoring an attempt, selecting feedback, creating
  completion evidence, retries, resume state, history, replay, or projection
  rebuild; those remain SLI-0027 through SLI-0029.
- Free text, essays, code, files, notebooks, spreadsheets, executable
  expressions, plugins, arbitrary precision rules, unit conversion, randomized
  items, or externally supplied item types.
- AI-authored items, model/manual grading, generative feedback, adaptive item
  selection, mastery inference, recommendation ranking, or financial advice.
- Instructor review, certification, proctoring, provider item banks,
  organization tenancy, managed-cloud recovery, or a separate local/cloud
  domain fork.
- Styling-only cleanup that does not impair meaning, operation, accessibility,
  or theme parity; optional polish may remain for CAP-0031.

## Canonical Context and Decisions

- [CAP-0006](../capabilities/CAP-0006-practice-and-demonstrate-understanding.md)
  defines this first observable increment and the full four-slice boundary.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  assigns practice definitions, presentations, attempts, and scoring to
  Assessment while Content and Curriculum retain their distinct authority.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
  permits structured versioned assessment definitions inside immutable
  platform packages but never makes package transport a grader.
- [Assessment Contract](../../architecture/contracts/assessment-contract.md)
  and the existing Assessment module establish answer-safe presentation,
  exact-version resolution, deterministic authority, and append-only evidence
  boundaries that this slice extends without rewriting CAP-0001 history.
- The content-package contract owns immutable bytes, digests, safe references,
  and admission. Curriculum retains exact placement references and imports no
  Assessment internals. The API host composes only public operations.
- Decision readiness is sufficient for closed structured response types and
  deterministic Assessment authority. Model grading, arbitrary execution,
  external providers, tenancy, and managed-cloud recovery remain outside this
  selection.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver a closed three-response-type definition, protected presentation API, generated client, and accessible browser opening flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Define contracts and backend presentation only, deferring the learner-visible route | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Mock a browser practice form from local fixtures before owning contracts and server operations | no - it makes UI fixtures accidental authority and produces no protected end-to-end value | - | - | - | - | - | - | - |
| D. Add open text, code, notebook, or generated item support in the first slice | no - arbitrary execution, model authority, and unbounded response semantics are outside the CAP | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it gives the learner a complete observable
opening experience, uses accepted module ownership, exposes a stable API-first
boundary, can be qualified without submission or scoring evidence, and remains
reversible through additive contracts and bounded placement/presentation
state. It also prevents the browser from becoming the only usable client.

Candidate B is decision-ready and useful to later work but does not deliver the
approved learner scenario, so observable value and end-to-end completeness each
score one. Candidate C bypasses authoritative contracts and server policy.
Candidate D materially changes the accepted safety and execution boundary.
Candidate A wins without a tie-break and conforms to the enumerated SLI-0026
increment.

## Boundary Path

1. Content admits an immutable exact package whose declared practice-definition
   bytes pass schema, semantic, reference, resource, digest, and capability
   validation before publication.
2. Curriculum records an exact practice placement that retains stable activity,
   package, definition, and version/digest references without reading Content
   or Assessment persistence.
3. Assessment resolves the placement and private definition only through the
   Curriculum and Content public facades, validates its closed item union and
   policy declarations, and returns a new answer-safe presentation value.
4. A protected host operation resolves server-issued learner context and
   permission, accepts exact placement/version selectors, and maps bounded
   missing, stale, malformed, unavailable, and unauthorized failures without
   disclosing private answers or hidden activity facts.
5. The reviewed OpenAPI operation generates the TypeScript client. The browser
   route uses that client to render purpose, instructions, policy, provenance,
   review references, and every supported input shape accessibly.
6. Contract and live qualification call the same operation from a non-browser
   HTTP client, proving the practice presentation remains available headlessly
   without implying submission, grading, completion, or autonomous AI action.

## Contracts, Data, and Provenance

Introduce or extend one versioned private practice-definition family, one
answer-safe public presentation family, and one exact protected HTTP operation.
The private definition uses a closed discriminated item union:

- single select declares stable ordered options and one private correct option;
- multiple select declares stable ordered options and one private exact correct
  set, with duplicate or unknown option IDs rejected;
- numeric entry declares canonical fixed-decimal syntax plus one private exact
  value or inclusive range at an explicit scale. NaN, infinity, exponent text,
  locale separators, implicit unit conversion, and binary floats are rejected.

The public presentation includes no correct values, score weights, private
feedback branch, or evaluator object. It retains exact activity, placement,
package, definition, schema, item, attempt-policy, source, review-reference,
and digest/version provenance needed by later submissions. Attempt policy is
descriptive in this slice; Assessment remains the future enforcement owner.

No attempt or response rows are created by open. If additive persistence is
needed for exact placement or immutable metadata, it remains module-owned,
migration-backed, append-oriented, and free of cross-module foreign keys. Both
browser and headless consumers use the public API rather than backend internals.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Exact opening | An authorized learner opens one exact placed activity and sees purpose, instructions, policy, provenance, review references, and every ordered item | application/API/browser/live |
| Headless opening | A non-browser HTTP client establishes the supported session and reads the same exact answer-safe presentation without UI state | API/live qualification |
| Single select | Stable ordered choices render with one required selection and no correct-answer signal | contract/component/browser |
| Multiple select | Stable choices permit a bounded set response without leaking the private exact set | contract/component/browser |
| Numeric entry | Fixed-decimal syntax, scale, and learner-visible unit/range instructions render without exposing the private accepted value or range | contract/component/browser |
| Version and provenance | Exact package, definition, item, policy, source, and review-reference versions/digests correlate; no latest substitution occurs | contract/application/API |
| Closed definitions | Unknown item types, policies, fields, capabilities, unsafe references, duplicate IDs/options, invalid decimal/range rules, and resource-limit breaches fail before visibility | schema/semantic compatibility corpus |
| Authorization and confidentiality | Missing permission/session, caller-selected learner context, stale selector, or unavailable placement fails closed without hidden activity or answer facts | API/security/browser |
| Flexible shape | Valid item counts, item order, option counts, and compatible optional presentation metadata do not trigger count-specific failure | contract/model/UI anti-rigidity tests |
| Accessible parity | Labels, instructions, field groups, error associations, keyboard order, focus, zoom/reflow, reduced motion, forced colors, and light/dark/system themes remain equivalent | component/Chromium/design checks |
| Side-effect-free open | Repeated presentation reads create no attempt, score, completion, or learner projection evidence | application/PostgreSQL/live |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0092 | Freeze practice-definition and answer-safe presentation contracts, closed response semantics, compatibility fixtures, and Assessment domain values | none | none | complete |
| JIT-B | Compose exact Content/Curriculum/Assessment storage and public operations plus the protected API | JIT-A | none | captured |
| JIT-C | Generate the public client and deliver the accessible practice-opening browser route | JIT-B | none | captured |
| JIT-D | Qualify contracts, API/headless access, browser behavior, denial confidentiality, side-effect-free open, accessibility, and live local composition | JIT-C | none | captured |

## Verification and Qualification

Run schema and semantic conformance over approved and malicious definitions;
domain and application tests for each closed response type and answer-safe
projection; immutable package/placement and PostgreSQL adapter integration;
protected API success, denial, stale/malformed, and confidentiality tests;
reviewed OpenAPI/generated-client reproduction; web model, component, mocked
Chromium, and isolated live browser/headless qualification; architecture import
and schema-ownership checks; security, learner-language, accessibility, design,
documentation, planning, whitespace, build, and aggregate readiness checks.

Anti-rigidity tests must vary valid item and option counts, item ordering,
source/review-reference counts, compatible optional presentation fields, and
all three supported response types. They must not require one fixture's exact
count, sibling order beyond contract meaning, incidental timestamps, or visual
styling for functional success.

## Rollback and Migration

Contract and data changes must be additive and versioned. A rollback may remove
the unreferenced practice route and UI while retaining already admitted exact
package/placement metadata. Any new database migration requires a tested
forward application and development rollback or documented restore boundary;
it may not rewrite CAP-0001 evidence. Public contract removal or meaning change
requires normal compatibility governance rather than an in-place rollback.

## Stop Conditions

Stop for model/manual grading, AI-authored items, arbitrary or external
execution, free text or files, personalized financial advice, external item-
bank authority, client-owned identity/authorization/answer/scoring state,
cross-module persistence access, private answer leakage, a breaking existing
Assessment contract, organization tenancy, managed-cloud recovery, a separate
local/cloud core, active write-scope overlap, conflicting canonical sources,
or material CAP-0006 package drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional copy polish, or another inconsequential issue. Fix it locally
or defer optional cleanup to CAP-0031.

## Documentation Impact and Completion Evidence

Expected updates include the Assessment and content-package contracts, module
READMEs, compatibility catalog, domain vocabulary, API/generated-client
guidance, interface behavior, architecture verification, and local live
qualification. Completion evidence must identify exact supported response
types, API/headless and browser outcomes, denial/confidentiality paths,
side-effect-free open behavior, contracts and migrations, checks and results,
assumptions, residual risks, and deliberately unqualified submission, AI,
cloud, and recovery behavior.

## Planning History

- 2026-10-16: Refined the first approved CAP-0006 manifest increment after the
  allocator selected CAP-0006 as the only ready capability lane. Candidate A
  scores 14/14 and delivers a closed three-response-type, API-first opening
  flow without activating submission, model authority, execution, or another
  decision gate. The refinement conforms to the current CAP package.
- 2026-10-16: Confirmed the public API remains authoritative for browser and
  non-browser consumers. A separate headless AI mode remains explicitly
  deferred.
- 2026-10-16: Refined JIT-A as WRK-0092 around a separate additive practice
  contract family, closed three-type semantics, answer-safe projection,
  canonical decimal/digest rules, compatibility fixtures, and pure Assessment
  parser/domain values. Existing knowledge-check v1 behavior remains frozen.
- 2026-10-16: Activated WRK-0092 after revalidating current CAP authority,
  manifest membership, decision readiness, exact write scope, and collision-
  free ownership. Packet-start froze the contract/domain acceptance set.
- 2026-10-16: Completed WRK-0092 at exact candidate `7d2f921` with the additive
  practice-v1 schemas, compatibility corpus, immutable Assessment values, and
  transport-neutral answer-safe parser/projector. The protected API remains
  the next packet's boundary; no separate AI mode was introduced.
