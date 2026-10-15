# Module Map

- Status: partially accepted
- Canonical for: accepted first learning-loop ownership and remaining module hypotheses
- Related ADRs: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md), [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md), [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- Decision gate: use accepted first-loop boundaries; refine every still-proposed boundary before implementation

| Module | Status | Primary responsibility | Publishes |
| --- | --- | --- | --- |
| Identity | accepted for first learner context | Provider-neutral actors and learners, provider bindings, authentication context, sessions, and application permission inputs | Identity, binding, and session changes |
| Content | accepted; lesson read core implemented | Versioned learning resources, provenance, publication state, safe body nodes, and private content storage references | Content-version events remain future work |
| Curriculum | accepted; lesson, initial Assessment placement/read, and persisted protected discovery browse implemented | Competencies, prerequisites, pathways, course structure, exact versioned activity placement, and rebuildable discovery views | Curriculum-version events remain future work |
| Assessment | accepted; deterministic single-select core implemented | Items, attempts, responses, deterministic scoring evidence, review state, and bounded completion evidence | Assessment knowledge-check completion evidence |
| Learner model | accepted; bounded completion projection implemented | Derived mastery, preferences, accommodations, completion, and progress projections | Learner-state changes remain future work |
| Adaptation | proposed | Eligibility, ranking, deterministic policy, recommendations | Recommendation decisions and outcomes |
| Market data | proposed | Instruments, observations, calendars, corporate actions, provider provenance | Canonical market-data events |
| Portfolio | proposed | Simulated accounts, positions, transactions, valuation, backtests | Portfolio and simulation results |
| AI orchestration | proposed | Model-provider gateway, prompt/model policy, grounded generation, evaluation hooks | AI execution records |
| Audit | accepted; Assessment completion references implemented | Append-oriented decision, provenance, administrative evidence, and source-event integrity references | Exportable audit records remain future work |

## Boundary Notes

- Assessment evidence is an input to the learner model; assessment does not directly decide mastery.
- Curriculum may retain immutable Content and Assessment version identifiers but cannot access those modules' internals or persistence.
- Learner-model completion and progress are projections that retain source-evidence references and never replace Assessment evidence.
- Adaptation reads approved learner and curriculum projections; it does not mutate curriculum or assessment history.
- AI orchestration supplies bounded capabilities. It does not own learning, grading, market, or portfolio rules.
- Market data normalizes provider observations. Portfolio behavior consumes canonical market data, never raw provider responses.
- Audit captures references and integrity evidence from owning modules without becoming a second business database.
- Content owns ADR-0007 package identity, publication, lesson body, educational-source provenance, and storage references. Assessment owns the meaning and runtime use of packaged assessment definitions.

ADR-0005 accepts the Content, Curriculum, Assessment, Learner model, and Audit boundaries only for the first learning loop. Other rows remain hypotheses until their own discovery and decisions establish implementation authority.

ADR-0006 additionally accepts Identity ownership for the first learner context. Organization membership, tenancy, enterprise administration, and other Identity responsibilities remain proposed.

ADR-0007 additionally accepts the portable versioned lesson-package boundary.
Executable version 1 schemas, admission validation, PostgreSQL Content metadata,
and local filesystem objects now exist for the approved lesson-read seam.
Archive transport, managed object storage, removal policy, and broader content
operations remain subject to later approved delivery planning.

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
