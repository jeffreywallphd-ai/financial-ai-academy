# Module Map

- Status: partially accepted
- Canonical for: accepted first learning-loop ownership and remaining module hypotheses
- Related ADRs: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md), [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md), [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md), [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md), [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md), [ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md), [ADR-0019](../../adr/ADR-0019-append-only-bounded-projection-overrides.md)
- Decision gate: use accepted first-loop boundaries; refine every still-proposed boundary before implementation

| Module | Status | Primary responsibility | Publishes |
| --- | --- | --- | --- |
| Identity | accepted for first learner context | Provider-neutral actors and learners, provider bindings, authentication context, sessions, and application permission inputs | Identity, binding, and session changes |
| Content | accepted; lesson read core implemented | Versioned learning resources, provenance, publication state, safe body nodes, and private content storage references | Content-version events remain future work |
| Curriculum | accepted; lesson, exact Assessment/practice placement, review-target mapping, protected discovery, and immutable graph read implemented | Competencies, prerequisites, pathways, course structure, exact activity placement, review routing, and rebuildable discovery views | Curriculum-version events remain future work |
| Assessment | accepted; deterministic knowledge-check/practice core, retry evidence, and safe history source implemented | Items, attempts, responses, deterministic scoring evidence, review state, and bounded completion evidence | Assessment knowledge-check and practice completion evidence |
| Learner model | accepted; bounded lesson completion and practice-history projections implemented | Derived mastery, preferences, accommodations, completion, and progress projections | Learner-state changes remain future work |
| Adaptation | accepted; deterministic navigation-state core implemented | Eligibility, ranking orchestration, deterministic policy, recommendations | Deterministic navigation-state projections; durable recommendation decisions and outcomes remain future work |
| Market data | accepted for initial financial lane; implementation pending | Canonical instruments, observations, calendars, corporate actions, coverage, quality, normalization, and provider provenance | Canonical market-data events |
| Portfolio | accepted for initial financial lane; implementation pending | Simulated accounts, cash/transactions, positions, valuation, benchmarks, performance/risk, scenarios, backtests, and simulation results | Portfolio and simulation results |
| Project | accepted; shell/origin contract core implemented | Learner Project identity, charter, immutable accepted origin, lifecycle, mutable workspace, snapshots, and typed references without taking authority from referenced modules | Project lifecycle and snapshot records remain future work |
| AI orchestration | proposed | Model-provider gateway, prompt/model policy, grounded generation, evaluation hooks | AI execution records |
| Audit | accepted; Assessment completion references implemented | Append-oriented decision, provenance, administrative evidence, and source-event integrity references | Exportable audit records remain future work |

## Boundary Notes

- Assessment evidence is an input to the learner model; assessment does not directly decide mastery.
- Evidence-owning modules retain immutable review inputs and feedback/revision
  records through their public operations. Under ADR-0019, Learner model owns
  the append-only projection-override ledger and effective overlay while Audit
  retains integrity references without becoming projection authority.
- Curriculum may retain immutable Content and Assessment version identifiers but cannot access those modules' internals or persistence.
- Learner-model completion and progress are projections that retain source-evidence references and never replace Assessment evidence.
- Adaptation reads approved learner and curriculum projections; it does not mutate curriculum or assessment history.
- AI orchestration supplies bounded capabilities. It does not own learning, grading, market, or portfolio rules.
- Market data normalizes provider observations. Portfolio behavior consumes canonical market data, never raw provider responses.
- ADR-0015 adds no Analysis module. Reusable pure calculations are registered by
  stable ID/version with one semantic owner and no persistence, provider,
  network, clock, random, AI, host, or adapter dependency. Owning modules retain
  workflow, authorization, persistence, and result meaning.
- Audit captures references and integrity evidence from owning modules without becoming a second business database.
- Content owns ADR-0007 package identity, publication, lesson body, educational-source provenance, and storage references. Assessment owns the meaning and runtime use of packaged assessment definitions.
- Content owns approved learning-project brief meaning and Curriculum owns its
  exact learning placement. Project accepts exact public references and owns
  the learner's continuing Project shell. Assessment later owns only a
  submitted immutable Project snapshot and its evidence.

ADR-0005 accepts the Content, Curriculum, Assessment, Learner model, and Audit
boundaries only for the first learning loop. Rows still marked `proposed`
remain hypotheses until their own discovery and decisions establish
implementation authority; later ADRs may accept additional bounded ownership.

ADR-0006 additionally accepts Identity ownership for the first learner context. Organization membership, tenancy, enterprise administration, and other Identity responsibilities remain proposed.

ADR-0007 additionally accepts the portable versioned lesson-package boundary.
Executable version 1 schemas, admission validation, PostgreSQL Content metadata,
and local filesystem objects now exist for the approved lesson-read seam.
Archive transport, managed object storage, removal policy, and broader content
operations remain subject to later approved delivery planning.

ADR-0015 accepts Market data and Portfolio ownership for the initial financial
analysis and simulation lane plus the platform method-registry seam. Exact
methods, schemas, accounting policies, and provider admissions remain bounded
CAP and contract work.

ADR-0014 accepts Adaptation ownership for deterministic eligibility, ranking
orchestration, policy application, and recommendation records while keeping
models advisory. The currently implemented baseline stops at a pure,
provider-neutral navigation-state projection over an exact Curriculum graph
and typed source facts. Gateway composition, durable recommendation records,
model influence, and experiments remain separately governed work.

ADR-0012 accepts Project ownership for both learning-started and independent
Projects. The implemented deterministic baseline parses and projects the
closed origin union plus a learner-safe active shell. It has no persistence,
public application operation, API, artifact, snapshot, Assessment submission,
Portfolio link, execution, provider, or AI-authoritative behavior.

## Implemented Adaptation Deterministic Baseline

- `adaptation-navigation-state-v1` keeps completion, eligibility,
  required/optional membership, and exact-source availability as orthogonal
  closed dimensions with stable bounded reasons.
- The framework-free policy validates one exact Curriculum graph and one source
  fact per activity, evaluates source-to-target activity prerequisites, and
  emits canonical source/projection digests for replay.
- Optionality is not eligibility. Multiple entries and prerequisites, absent
  presentation hints, same-kind shared branches, unbranched activities, and
  sibling reordering remain compatible.
- The core imports only Curriculum's public surface, has no repository or
  migration, and exposes no learner identity, answer, score interpretation,
  provider payload, model, rank, recommendation, mastery, approval, or advice
  field.

## Implemented Lesson-Read Seams

- Content exposes package admission and exact published-version reads through
  `backend/src/financial_ai_academy/modules/content/public.py`.
- Curriculum exposes exact placement creation and safe placed-lesson reads
  through `backend/src/financial_ai_academy/modules/curriculum/public.py`.
- Curriculum uses its Content gateway and imports only the Content public
  surface. Automated architecture tests reject Content-internal imports and
  cross-module repository access.
- Content owns `content.lesson_package_versions` and its private object key.
  Curriculum owns `curriculum.lesson_placements` and stores only package ID,
  semantic version, and digest. There is deliberately no cross-module database
  foreign key.
- Admission creates a closed safe body-node union before publication. API and
  browser layers must consume that union and cannot request raw CommonMark or
  an HTML fragment.

The deterministic Assessment seam is described separately below. Audit
consumption, background event delivery, managed-cloud adapters, and broader
completion-history API behavior remain outside the lesson-read seam.

## Implemented Discovery Projection Core

- Curriculum owns the discovery record classification, exact destination,
  availability, deterministic fixed browse order, and projection rebuild; it
  remains a read model over owning facts rather than a new business module.
- Content title, objectives, immutable package identity/version/digest, and
  publication provenance enter only through Content's exact public operation.
  Discovery code imports no Content internals and reads no Content persistence.
- Discovery v1 fixes closed provider-neutral record and browse shapes plus
  SHA-256 source/generation fingerprints. The initial profile admits only exact
  approved lessons; other kind values do not imply delivered execution.
- The application builds and validates a complete generation before requesting
  one atomic Curriculum repository replacement. Missing, stale, conflicting,
  unavailable, unsorted, or digest-mismatched state fails closed without
  replacing the last valid generation.
- `curriculum_0002_discovery_projection` stores immutable classification and
  one complete ordered generation without a Content foreign key. Transactional
  replacement preserves the prior generation when a rebuild is interrupted.
- The protected queryless discovery GET requires the server-issued
  `curriculum.discovery.read` permission and is represented in the reviewed
  OpenAPI snapshot and generated TypeScript client.
- Contract, unit, PostgreSQL, and API tests cover schema/semantic denials, immutable source
  registration, repeat rebuild, stable ordering, exact-source failure,
  replacement interruption, projection tamper, and absence of private/ranking
  fields. Browser presentation, automatic rebuild composition, and full live
  qualification are later SLI-0018 packet boundaries.

## Implemented Curriculum Graph Persistence and API Seam

- Curriculum admits only fully validated approved graph versions and confirms
  every activity against its exact Curriculum-owned lesson or assessment
  placement before storage.
- `curriculum_0003_curriculum_graphs` stores one constrained append-only JSONB
  aggregate per Curriculum ID/version without cross-module foreign keys. The
  repository adapter reconstructs and revalidates the full public graph on
  every read.
- Exact replay is idempotent; changed meaning for an existing ID/version is an
  immutable conflict. Reads require an exact semantic version and never choose
  a current/latest replacement.
- The protected graph GET requires server-issued `curriculum.graph.read` and is
  represented in the reviewed OpenAPI snapshot and generated TypeScript client.
  Browser map/list rendering, eligibility, completion context, and activity
  launch remain later CAP-0005 boundaries.

## Implemented Deterministic Assessment Seams

- Curriculum separately owns `curriculum.assessment_placements`, retaining the
  exact package, definition, item, and scoring-policy identities/versions for
  an existing lesson placement. It does not interpret Assessment meaning.
- Content validates complete Assessment v1 bytes at package admission and
  exposes an exact private-definition query through its public module facade.
  It does not expose paths/object keys or become a scorer.
- Assessment calls only the Curriculum and Content public facades through
  owned gateways. Architecture tests reject imports of their internals and
  cross-schema persistence access.
- Assessment owns answer-safe presentation, option validation, exact-match
  scoring, reviewed feedback selection, and the public application operations
  for opening/submitting one placed knowledge check.
- Assessment owns `assessment.attempts`, `responses`, `scores`,
  `completion_evidence`, and `outbox`. One PostgreSQL transaction appends one
  evidence/event set; unique constraints distinguish exact replay, conflicting
  submission reuse, and already-completed submissions. Accepted rows reject
  ordinary update/delete.
- Assessment separately owns one mutable `practice_drafts` row and one
  transaction-lock row for each learner/exact-practice scope. Drafts are work
  state, not evidence. Stable attempt order and immutable-definition limits are
  enforced inside the same transaction that appends practice evidence and
  clears only the matching draft.
- Assessment exposes transport-neutral typed operations to read/save the exact
  draft, derive retry state, and replay validated ordered practice completion
  events. These operations contain no HTTP, browser, AI-specific, or cross-
  module persistence behavior. The protected API host composes them through
  public operations and never reads Assessment persistence.
- Assessment's safe practice-history source correlates immutable events with
  retained results and the exact definition inside Assessment, then exposes
  only provenance, scores, correctness, and incorrect-item review references.
  Event bytes remain unchanged and private responses/feedback are not copied.
- Curriculum owns append-only exact review-target mappings and resolves them in
  declaration order. Missing mappings remain explicit; Curriculum does not
  inspect Assessment evidence or rank destinations.
- The protected practice-progress GET composes the nullable Assessment draft,
  deterministic retry state, complete Learner-model history, and exact
  Curriculum targets selected from the latest attempt's incorrect items. The
  conditional draft PUT accepts only the reviewed versioned snapshot and binds
  learner identity on the server. OpenAPI and the generated TypeScript client
  expose both operations equally to browser and headless consumers.
- `assessment.knowledge-check.completed@1.0.0` refers to its durable evidence
  and excludes private answers, selected responses, and feedback. A synchronous
  validated replay source now feeds the implemented Learner-model and Audit
  consumers; background delivery remains unimplemented.

The protected completion-history FastAPI/generated-client seam and accessible
completion-first browser presentation are implemented. A fresh lesson load
shows exact retained provenance without requesting another Assessment
presentation; empty history continues to the answer-safe form. Background
event delivery, recovery, managed-cloud adapters, and additional item or
scoring types remain outside this implemented core.

## Implemented Learner-model Completion Seam

- Assessment exposes a typed, validated, learner/placement-filtered completion
  event query. The Learner-model adapter imports only that public surface and
  maps events into owned domain values.
- Learner model derives `completed` only from accepted bounded Assessment
  evidence. It retains exact event, attempt, evidence, package, Assessment,
  item, policy, score, and time references and makes no mastery claim.
- `learner_model.lesson_completion_projections` and
  `learner_model.lesson_completion_history` are transactionally replaceable,
  rebuildable tables with a stable source-set digest. They have no
  cross-schema foreign keys and never mutate Assessment evidence.
- Unit, architecture, and real PostgreSQL 18.4 tests cover empty and exact
  evidence, repeated replay, invalid source data, and interrupted rebuild.
  Audit-first HTTP/client/browser delivery and private-host close/reopen are
  directly covered. Recovery and background event transport remain outside
  this seam.
- The same public-only dependency direction now supports rebuildable practice
  history. Learner model validates zero through ten contiguous attempts,
  deduplicates only exact event replay, retains stable item signatures and
  exact source identities, and atomically replaces its own exact-scope rows.
  Its canonical digest matches the accepted history contract; the projection
  carries no response, feedback text, answer, mastery, or recommendation.

## Implemented Audit Completion Seam

- Audit imports only Assessment's public completion-event query and maps the
  validated event into an owned integrity/provenance value.
- A deterministic Audit record ID and SHA-256 over the canonical event bind
  the source event, evidence, attempt, actor/action, exact package/Assessment
  versions and digests, and occurrence time.
- `audit.assessment_completion_records` is append-only and has no cross-schema
  foreign keys. Exact replay is idempotent; the same event identity with
  different content is rejected without replacing the original.
- Audit remains evidence about the event, not a second source for attempt,
  score, completion, or learner-state facts. HTTP exposure, exports, retention
  automation, recovery, background delivery, and managed-cloud posture remain
  outside this seam.

## Implemented Completion-History API Seam

- The local composition applies separate Assessment, Learner-model, Audit, and
  Identity migration streams and constructs each module through its owned
  adapters.
- The protected exact-placement endpoint accepts no learner selector. It
  resolves Identity context, reconciles Audit first, atomically rebuilds
  Learner-model state, and returns only bounded completion/history provenance.
- OpenAPI and the generated TypeScript client carry the exact response shape;
  the host owns only operation ordering and transport error mapping, not
  scoring, evidence, completion, or integrity policy.

## Implemented Completion-History Browser Seam

- The lesson route calls the protected completion operation before requesting
  another answer-safe Assessment presentation.
- Completed history shows only bounded meaning, score, time, exact package and
  Assessment provenance, and source event/attempt/evidence references. It
  exposes no learner/provider identity, answer, feedback, Audit row, mastery,
  advice, suitability, or performance interpretation.
- Component and Chromium checks cover empty, completed, denied, malformed, and
  unavailable states plus light/dark accessibility and narrow reflow. The live
  private-host path submits once and reproduces the same source-set identity on
  repeated reopen through PostgreSQL and the Python same-origin host.
