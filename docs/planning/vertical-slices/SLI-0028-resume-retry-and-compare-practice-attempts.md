---
id: SLI-0028
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: CAP-0006
depends_on: ["SLI-0027"]
decision_gates: []
---

# Vertical Slice: Resume, Retry, and Compare Practice Attempts

## Outcome and User Scenario

An authorized learner can leave a partially answered practice activity, return
to the same exact version, and continue from the saved draft. After submitting,
the learner can open the approved review resources selected by deterministic
item feedback, try again while attempts remain under the visible formative
policy, and compare immutable attempt summaries without losing or replacing
earlier evidence. Browser and non-browser clients use the same versioned public
API. The flow does not infer mastery, rank resources adaptively, or personalize
financial guidance.

## Scope Boundaries

### In Scope

- Preserve at most one mutable Assessment-owned draft for one learner and exact
  placed-practice version. A draft may contain any valid subset of the defined
  responses, retains exact package/definition/item/policy provenance, and is
  separate from attempts, scores, completion evidence, and outbox records.
- Read and conditionally replace the complete draft through a server-revisioned
  public contract. An exact retried save returns the current draft; a different
  stale revision conflicts without overwriting newer work. Learner identity,
  revision, and save time remain server-authoritative.
- Resume the draft after page reload, process restart, and another supported
  client session. Clear the matching draft atomically only after a successful
  submission; failed, malformed, stale, or unauthorized submissions do not
  destroy it.
- Enforce the exact immutable definition's `formative-retry@1.0.0` policy and
  variable `max_attempts` value atomically. Exact submission replay never
  consumes another attempt; distinct accepted submissions receive stable
  attempt order; concurrent contenders cannot exceed the declared limit.
- Preserve every accepted attempt and completion event append-only. Expose a
  bounded Assessment replay operation and rebuildable Learner-model history
  projection with exact source references, attempt order, score, maximum,
  outcome, item-correctness summary, review-reference IDs, and time. It is not
  a mastery, competency, grade, suitability, or recommendation record.
- Resolve selected review-reference IDs through an exact Curriculum-owned
  mapping to an approved learning placement. The deterministic selection rule
  uses references attached to incorrect item feedback, deduplicates them in
  declaration order, and never ranks or generates a recommendation.
- Expose draft, retry availability, review destinations, and attempt history
  through reviewed public API/OpenAPI and generated-client seams that remain
  directly usable without the browser.
- Deliver accessible learner controls for saved progress, targeted review,
  another attempt, and bounded attempt comparison using plain learner language
  with exact versions and evidence IDs in a technical record.
- Prove replay/rebuild, restart durability, confidentiality, local cleanup,
  responsive/theme parity, and anti-rigidity across valid item, reference,
  draft-response, history, and attempt-limit counts.

### Out of Scope

- Mastery or competency inference, adaptive ranking, personalized learning
  recommendations, model/manual grading, AI-authored feedback, instructor
  override, credentialing, certification, proctoring, or financial advice.
- Unlimited retries, answer-key display, hiding or deleting prior attempts,
  changing a published policy in place, cross-version draft migration, merging
  multiple drafts, collaborative editing, offline conflict resolution, or a
  general document-sync protocol.
- Draft expiration, retention schedules, background cleanup, reminders,
  notifications, event dispatch, queues, brokers, checkpoints, managed-cloud
  recovery, organization tenancy, or a separate browser/AI/headless core.
- New item types, partial credit, response weighting, randomized questions,
  free text, files, notebooks, executable expressions, or external item banks.
- Styling-only polish that does not impair meaning, operation, accessibility,
  responsive behavior, or theme parity; optional polish may remain for
  CAP-0031.

## Canonical Context and Decisions

- [CAP-0006](../capabilities/CAP-0006-practice-and-demonstrate-understanding.md)
  enumerates this third observable increment after deterministic submission.
- [SLI-0027](SLI-0027-submit-and-score-practice-attempt.md) supplies the exact
  request/result/event contracts, append-only aggregate, protected POST,
  generated client, browser result, and live browser/headless evidence.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  assigns drafts, attempt policy, results, and source evidence to Assessment;
  rebuildable history to Learner model; review placement to Curriculum; and
  trace-only integrity evidence to Audit.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
  keeps the immutable package and exact private practice definition authoritative
  without making package transport a runtime policy owner.
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
  bounds local retained-data claims to a private host and forbids managed-cloud
  recovery claims.
- [Assessment contract](../../architecture/contracts/assessment-contract.md)
  keeps validation, scoring, policy enforcement, replay, and evidence
  deterministic and server-owned. Drafts are mutable work state, not evidence.
- The accepted practice-v1 definition already exposes
  `formative-retry@1.0.0`, variable `max_attempts` from 1 through 10,
  `resume_allowed: true`, and `history_visible: true`. This slice implements
  those accepted meanings without changing item or scoring semantics.
- Decision readiness is sufficient. Identity, tenancy, managed-cloud recovery,
  AI authority, providers, queues, external execution, and adaptive learning
  remain outside this slice.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver server-resumable drafts, exact retry enforcement, approved review routing, rebuildable history, public API, generated client, and accessible comparison | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add retry enforcement but defer resume, review routing, history rebuild, and comparison to a new slice | no - it redefines the approved SLI-0028 manifest instead of refining it | - | - | - | - | - | - | - |
| C. Keep drafts and attempt history only in browser storage | no - it cannot provide durable server-authoritative resume, headless parity, or rebuild evidence | - | - | - | - | - | - | - |
| D. Rank review resources or infer mastery from retry performance | no - adaptive and mastery authority are explicit material-change boundaries | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the only eligible complete refinement and scores 14/14. It
delivers the approved learner outcome across exact contracts, module-owned
state, public APIs, generated clients, browser behavior, replay/rebuild, and
live qualification. Its behavior is independently observable, uses already
accepted attempt-policy metadata, and remains reversible while preserving any
accepted evidence. Candidate B would silently split or defer manifest meaning.
Candidate C makes an untrusted browser the only source of resumable state.
Candidate D crosses the CAP's adaptive/mastery boundary. No tie-break is
required.

## Boundary Path

1. A protected public read resolves the exact practice presentation through
   Curriculum, Content, and Assessment public facades, then composes the
   learner's current Assessment draft, deterministic retry state, resolved
   Curriculum review targets, and Learner-model attempt-history projection.
2. A client saves a complete replacement snapshot of its current partial
   responses with the last server revision. Assessment validates exact
   selectors and response shapes without scoring, then conditionally creates or
   replaces its one draft and returns the server revision and save time.
3. On reopening, any supported client receives only its server-bound draft for
   the same exact placement/package/definition/practice/policy chain. A stale,
   malformed, unauthorized, or different-version request fails without
   exposing or overwriting the draft.
4. The existing submission operation scores a complete request through the
   SLI-0027 rules. Inside one Assessment transaction, the repository resolves
   exact replays first, locks the learner/practice policy scope, assigns the
   next stable attempt order only when below `max_attempts`, appends the whole
   evidence/event aggregate, and clears only the matching draft.
5. Assessment exposes a typed, read-only replay of validated practice
   completion events. Learner model deterministically orders, deduplicates, and
   replaces its own bounded history projection while retaining every source
   event/attempt/evidence/version reference and never mutating Assessment.
6. Incorrect item outcomes yield a declaration-ordered unique set of approved
   review-reference IDs. Curriculum resolves only exact registered mappings to
   safe learning placements; an unavailable mapping degrades the link without
   hiding the saved result or inventing another resource.
7. The browser uses only generated public clients to show saved progress,
   remaining attempts, review actions, and a comparison of immutable summaries.
   Exact technical evidence remains available through progressive disclosure;
   the same APIs remain usable directly by non-browser and future headless
   consumers.

## Contracts, Data, and Provenance

Introduce additive versioned contracts for a partial practice draft, conditional
draft save/read result, retry state, resolved review target, and bounded attempt-
history view. A draft carries exact public selectors and a closed subset of the
existing response union. It excludes learner identity, scores, feedback,
correct answers, private evaluator rules, storage details, and client-supplied
time or revision authority. Empty and partial response sets are valid; unknown,
duplicate, wrong-type, or noncanonical responses fail closed.

Keep the existing whole-attempt submission/result contract compatible. Add a
stable server-owned attempt order to Assessment persistence and to the new
history view rather than reinterpreting earlier result bytes. Migrate existing
accepted practice attempts as order 1, replace the one-completion uniqueness
rule with exact-scope attempt-order uniqueness, and enforce the definition's
bounded `max_attempts` under one transaction/lock. Submission-ID idempotency is
checked before the attempt limit so exact replay remains valid after the limit.

Add one mutable Assessment draft table keyed by learner and exact placed-
practice version, with a monotonic revision, canonical response snapshot,
definition/policy provenance, and server save time. The row is replaced only by
conditional save and removed only by successful matching submission or an
explicit learner reset if that reset is included in a bounded packet. It is not
completion evidence, does not emit an event, and is never projected as an
attempt.

Add an Assessment practice-completion replay query over validated existing
outbox events. Add Learner-model practice-history projection/history tables that
are transactionally replaceable from those events and retain stable source
digests plus exact event, attempt, evidence, placement, package, definition,
practice, policy, item-score, outcome, and time provenance. Add a
Curriculum-owned exact mapping from a practice placement and review resource
identity/version/digest to a safe lesson placement; do not store Content bytes
or Assessment feedback there.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Save and resume | A valid partial snapshot saves once and reopens with the same responses, exact versions, higher server revision, and save time after reload, restart, and a fresh supported session | contract/application/PostgreSQL/API/browser/live |
| Save replay and conflict | Retrying the same save returns the current draft; a different stale-revision save conflicts and preserves the newer snapshot | application/PostgreSQL/API/concurrency |
| Draft isolation | Another learner, placement, package/definition version, or unauthorized caller cannot observe or alter the draft | application/API/security/PostgreSQL |
| Submission transition | A valid complete submission appends one immutable aggregate/event and clears only its matching draft atomically; a rejected submission preserves the draft | application/PostgreSQL/fault injection |
| Retry policy | Distinct valid attempts are accepted only through the definition's variable maximum, receive stable order, and preserve every earlier result; the next attempt is refused confidentially | domain/application/PostgreSQL/API/browser |
| Exact replay at limit | Replaying any accepted submission returns its original result and does not consume an attempt even after the limit is reached | application/PostgreSQL/API/live |
| Concurrent boundary | Concurrent final-slot submissions produce at most one new accepted attempt, no skipped/duplicate order, and no partial aggregate | PostgreSQL/concurrency |
| Targeted review | Incorrect items produce declaration-ordered deduplicated approved review actions; correct-only references do not create a retry recommendation, and unavailable mappings degrade safely | domain/Curriculum/API/browser |
| History rebuild | Learner model rebuilds the same ordered summaries and source digest from Assessment replay; duplicate replay is idempotent and interrupted rebuild preserves the prior complete projection | domain/application/PostgreSQL/replay |
| Attempt comparison | The learner can compare bounded score, outcome, item-correctness, time, and evidence source for every attempt without answer keys, mastery language, hidden prior results, or exact-copy rigidity | component/Chromium/accessibility |
| Headless parity | A cookie-backed non-browser client reads/saves/resumes the same draft and reads the same retry/history/review contract as the generated browser client | API/live |
| Accessible recovery | Pending, saved, stale, unavailable, limit-reached, empty-history, review-return, and comparison states preserve labels, focus, live status, keyboard use, reflow, forced colors, reduced motion, and both themes | component/Chromium/design |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0102 | Freeze draft/retry/history/review-target contracts, deterministic policy and projection rules, and anti-rigidity corpora | SLI-0027 | none | complete |
| WRK-0103 | Implement Assessment conditional drafts, atomic retry enforcement, attempt ordering, compatible migration, and practice-event replay | WRK-0102 | none | complete |
| WRK-0104 | Implement an Assessment-safe history source, Curriculum review-target resolution, and Learner-model history rebuild/persistence | WRK-0103 | none | complete |
| WRK-0105 | Expose the composed progress, review, and history operations through protected API, OpenAPI, and generated clients | WRK-0104 | none | complete |
| WRK-0106 | Deliver accessible browser resume, saved-progress, targeted-review, retry, and attempt-comparison behavior through generated clients | WRK-0105 | none | complete |
| WRK-0107 | Qualify contracts, real PostgreSQL concurrency/rollback/rebuild, API/headless and browser parity, restart durability, confidentiality, accessibility, and live local composition | WRK-0106 | none | ready |

Exact `WRK-*` identifiers replace these seam labels as each bounded packet is
authored. This preserves incremental planning and avoids freezing later file
scope before earlier contracts have executable evidence.

## Verification and Qualification

Run schema and semantic conformance for empty through full valid draft subsets,
all supported response shapes, variable item/reference/history counts, attempt
limits 1 through 10, ordering equivalence, exact save/submission replay, stale
revision, wrong-version, private-field, and malformed corpora. Run pure retry,
review-selection, history-ordering, source-digest, and projection-rebuild tests.

Run application and real-PostgreSQL tests for conditional saves, learner/version
isolation, successful-submit draft clearing, failure preservation, exact replay,
attempt-order uniqueness, concurrent final slots, transaction rollback,
append-only evidence, migration/reapply/teardown, replay/rebuild idempotency,
interrupted rebuild, and normal restart. Prove existing one-attempt rows migrate
to order 1 without result/event reinterpretation and existing knowledge-check
and lesson-completion paths remain unchanged.

Run protected API success/denial and direct non-browser tests; reviewed OpenAPI
and generated-client reproduction; web model/component tests; keyboard, focus,
live-region, zoom/reflow, forced-color, reduced-motion, light/dark, and axe
checks; and the isolated live PostgreSQL/Python/headless/Chromium workflow. Run
architecture ownership, security, learner-language, design-system,
documentation, planning, whitespace, exact-candidate affected verification,
independent technical review, and aggregate readiness. Tests must protect
meaning and invariants without fixing incidental copy, style, fixture counts,
timestamps, IDs, or one exact history length.

## Rollback and Migration

Use additive draft, attempt-order, review-target, and history-projection changes.
Forward migration assigns order 1 to existing attempts before replacing the
one-completion constraint; retained result and event documents remain unchanged.
Before accepted retry/draft state exists, development rollback may remove the
new structures. After use, preserve immutable attempts and completion events;
disable new exposure or use a later governed forward migration rather than a
destructive down-migration. Drafts and Learner-model tables are rebuildable or
mutable work state, but rollback must not delete Assessment evidence. No
managed-cloud backup/restore or RPO/RTO claim is made.

## Stop Conditions

Stop for a change to the CAP slice manifest; a new item/scoring or policy family;
cross-version draft migration; deleting, hiding, or rewriting prior attempts;
client-owned learner, revision, order, score, time, or eligibility authority;
Curriculum or Learner model reading Assessment persistence; answer/private-rule
leakage; adaptive ranking, mastery, instructor override, credentialing,
proctoring, external providers, arbitrary execution, queue/broker selection,
tenancy, managed-cloud recovery, or a separate AI/browser core. Also stop for
conflicting canonical authority, stale CAP binding, active write-scope overlap,
or a migration that cannot preserve existing evidence meaning.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or defer optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Update Assessment, Curriculum, Learner model, API, web, local deployment,
contract/event, persistence/migration, architecture-verification, recovery,
module-map, and known-gap guidance made stale by delivery. Completion evidence
must identify exact candidates and retained contract versions; draft/retry/
history/review-target invariants; focused and aggregate checks; real-database,
concurrency, rollback, migration, rebuild, restart, API/headless, browser,
accessibility, security, confidentiality, cleanup, and live results; assumptions
and residual gaps; and CAP-conformance assessment. State explicitly that retry
history is evidence-only and no mastery, adaptive recommendation, separate AI
mode, autonomous authority, provider, cloud, or external execution was added.

## Planning History

- 2026-10-16: Refined the third CAP-0006 manifest increment after SLI-0027
  completed. Candidate A scores 14/14 and implements the already declared
  formative retry, resume, targeted review, and visible-history meanings
  through one API-first browser/headless boundary. Drafts remain mutable work
  state, accepted attempts remain append-only evidence, Learner-model history
  remains rebuildable, and adaptive/mastery authority remains excluded.
- 2026-10-16: Refined JIT-A as WRK-0102 for additive draft, retry-state,
  Curriculum review-target, and Learner-model history contracts plus
  dependency-light anti-rigidity evidence. Persistence, APIs, clients, and UI
  remain dependent seams.
- 2026-10-16: Completed WRK-0102 at exact candidate
  `5d869b8df0896dd1ddb248559bde5d233ee0ddba`; additive contracts and
  dependency-light evidence now make the Assessment persistence/retry seam
  eligible for just-in-time packet authoring.
- 2026-10-16: Completed WRK-0103 at exact candidate
  `0745422d1e742937a0c97fde817bf1d0e2d62235`; Assessment now owns durable
  conditional drafts, exact retry enforcement, stable attempt order, and
  provenance-correlated typed replay. The composed Curriculum, Learner-model,
  API, OpenAPI, and generated-client seam is dependency-ready for refinement.
- 2026-10-16: Refined the former combined JIT-C seam as WRK-0104 for the
  Assessment-safe history source, Curriculum exact review mapping, and
  Learner-model rebuildable projection. Protected API/OpenAPI/generated-client
  composition follows as its own packet so the core can be reviewed and reused
  independently without changing the approved slice outcome.
- 2026-10-16: Completed WRK-0104 at exact implementation candidate
  `7e2213f52a1516a442175e045e47ff8f8c7785c9`. The answer-safe Assessment
  source, exact Curriculum mapping, and rebuildable Learner-model projection
  passed affected unit, contract, real-PostgreSQL, architecture, documentation,
  planning, whitespace, aggregate-readiness, and exact-candidate acceptance
  checks. JIT-D is now dependency-ready for protected API/OpenAPI/generated-
  client refinement, and the transport-neutral core remains reusable by
  browser and headless clients.
- 2026-10-16: Refined JIT-D as WRK-0105 for one protected practice-progress
  read, conditional draft save, reviewed OpenAPI snapshot, and generated client
  seam. Browser behavior and live qualification remain dependent packets.
- 2026-10-16: Completed WRK-0106 at exact candidate
  `067e04b6088891b43d215f81c822ee5758de4308`. The accessible browser now
  resumes and conditionally saves contract-order-insensitive drafts, follows
  server-owned retry and targeted-review state, and compares immutable
  answer-free attempt history through the same public API available to
  headless clients. JIT-F remains for cumulative live qualification.
- 2026-10-16: Refined JIT-F as WRK-0107 for one qualification-only extension
  of the existing approved-lesson harness. It combines browser save/resume and
  submission evidence, fresh-session headless parity, normal restart, and the
  established PostgreSQL concurrency/rollback/migration/rebuild suites without
  changing product contracts or implementation.

