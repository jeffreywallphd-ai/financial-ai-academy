---
id: SLI-0002
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: CAP-0001
depends_on: [SLI-0001]
decision_gates: []
---

# Vertical Slice: Submit a Deterministic Knowledge Check

## Outcome and User Scenario

An authorized individual learner using the private-host community
`single_profile` profile can open the approved introductory lesson, answer one
bounded single-select knowledge-check item, submit it once, and receive
deterministic, author-reviewed feedback. The platform retains append-oriented
Assessment-owned attempt, response, score, and knowledge-check completion
evidence tied to the exact lesson package, assessment definition, scoring
policy, learner context, and submission.

The learner receives observable practice and feedback without a mastery,
certification, suitability, investment-performance, or personalized-advice
claim. Lesson-completion projection, history after restart, retakes, adaptive
recommendations, and recovery tooling remain later work.

## Scope Boundaries

### In Scope

- One immutable successor version of `intro-risk-return` containing one
  Assessment-owned, versioned single-select definition with a fixed correct
  option and reviewed correct/incorrect feedback.
- Versioned executable Assessment contracts for the definition, submitted
  response, deterministic score, retained evidence, and the evidence event
  needed by later Learner-model and Audit consumers.
- Assessment-owned validation, one-point exact-match scoring, safe feedback,
  attempt lifecycle, submission idempotency, and append-oriented evidence.
- PostgreSQL Assessment tables and an owned transactional outbox or equivalent
  atomic event-publication boundary; no cross-module database access.
- Exact references to learner, placement, package ID/version/digest,
  assessment ID/version, item ID/version, scoring-policy version, server time,
  and opaque submission/attempt/evidence identifiers.
- One authenticated submission operation in the reviewed OpenAPI contract and
  generated TypeScript client, composed through the existing provider-neutral
  learner context.
- An accessible knowledge-check form and deterministic feedback state in the
  lesson workspace with equivalent light, dark, and system-theme behavior.
- Focused contract, domain, application, persistence, authorization, API,
  generated-client, component, browser, architecture, security, and live
  local-runtime evidence.

### Out of Scope

- Multiple items, free text, numeric answers, partial credit, randomized
  options, time limits, hints, manual review, overrides, retakes, attempt
  limits, question banks, or complex scoring policies.
- Learner-model completion or mastery projection, progress display, resume or
  history after restart, recommendation eligibility, adaptation, experiments,
  or credentials.
- Audit consumption or export beyond the versioned Assessment evidence event
  and integrity/trace fields needed for later consumers.
- Mutation of the published `intro-risk-return@1.0.0` package, silent `latest`
  resolution, general authoring/import workflows, or broader lesson-package
  capabilities.
- Built-in credentials, OIDC, multiple learners, organization tenancy,
  managed-cloud composition, remote/public exposure, backup/restore delivery,
  provider calls, external publication, or production deployment.
- AI grading, AI feedback, tutoring, market data, portfolios, brokerage
  behavior, or personalized financial recommendations.

## Canonical Context and Decisions

- [CAP-0001](../capabilities/CAP-0001-complete-structured-introductory-lesson.md)
  defines Candidate B and the first deterministic learning-loop outcome.
- [SLI-0001](SLI-0001-open-approved-versioned-lesson.md) supplies the completed
  exact-version lesson, Identity, API/generated-client, accessible web, and
  local-runtime path on which this slice depends.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  assigns definitions, attempts, responses, deterministic scores, review
  state, and bounded completion evidence to Assessment; Learner model and
  Audit remain separate consumers.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and
  the [content-package contract](../../architecture/contracts/content-package-contract.md)
  require a new immutable package version for assessment-definition changes
  and preserve Assessment as the sole runtime scoring authority.
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
  and the [community evidence boundary](../../security/community-learner-evidence-protection.md)
  govern retained responses and scores. This slice preserves their data
  meaning and private-host controls but makes no backup or recovery claim.
- [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md)
  preserves the Python modular application, PostgreSQL transaction boundary,
  static React/TypeScript client, generated API models, and no Node production
  server.
- The [adaptive pathway architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  keeps deterministic grading authoritative and evidence distinct from later
  projections or recommendations.
- The education-versus-advice and interface authorities continue to govern
  learner-visible wording, sources, themes, accessibility, and layout.

Decision readiness is sufficient within this boundary. The accepted ADRs fix
ownership, deterministic authority, identity, immutable content versioning,
evidence protection, and runtime shape. Exact schema fields, identifier
formats, PostgreSQL models, event-envelope fields, API models, and compatible
library patches are reviewable delivery details; changing the single-select,
one-point, one-submission boundary requires renewed planning or a durable
decision review.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B. Submit and score one knowledge check with retained evidence | yes | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 12 |
| C. Reopen and review derived completion and evidence history | no — requires Candidate B evidence and event contracts | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate B is the only eligible next CAP-0001 increment.

- **Observable value — 2:** the learner answers a real question and receives
  reproducible feedback, extending the completed read-only lesson into active
  practice.
- **End-to-end completeness — 2:** the path crosses immutable package input,
  Assessment contracts and policy, transactional evidence, authenticated API,
  generated client, accessible UI, and live local qualification.
- **Decision readiness — 2:** ADR-0005, ADR-0007, ADR-0008, and ADR-0009 resolve
  the durable ownership, authority, protection, versioning, and runtime choices.
- **Contract clarity — 1:** semantic ownership and the bounded item/scoring
  profile are clear, while exact executable definition, response, evidence,
  event, and HTTP shapes must be established during packet planning.
- **Dependency independence — 2:** SLI-0001 is complete, and this slice does
  not require Learner-model projections, Audit consumption, recovery tooling,
  adaptive behavior, AI, or an external provider.
- **Verification observability — 2:** correct, incorrect, malformed,
  unauthorized, stale-version, duplicate, concurrent, persistence-failure,
  accessibility, and advice-boundary results are independently observable.
- **Reversibility and bounded risk — 1:** exposure can be withdrawn, but
  accepted Assessment contracts, migrations, and append-oriented evidence
  cannot be silently deleted or reinterpreted.

Candidate C is deferred rather than rejected. It requires the exact evidence
and event outputs created by Candidate B and will separately introduce
Learner-model projection, replay/rebuild, restart/history presentation, and
their recovery implications.

## Boundary Path

1. Extend the approved fixture through a new immutable package version and
   define one versioned Assessment-owned single-select contract family.
2. Register and resolve the exact assessment definition through Assessment,
   without giving Content or Curriculum scoring authority or persistence
   access.
3. Validate one response and atomically append the attempt, response, score,
   feedback reference, completion evidence, and versioned outbox event in
   Assessment-owned PostgreSQL tables.
4. Expose one authenticated, idempotent submission operation through the thin
   Python host, reviewed OpenAPI snapshot, and generated TypeScript client.
5. Render the question, selection, submission, result, and safe retry/failure
   states inside the existing lesson workspace using the shared design system.
6. Qualify the exact local path plus denial, stale/malformed input, duplicate
   submission, transactional failure, redaction, accessibility, theme, and
   education-only scenarios.

Learner-model projection and Audit consumption begin only in a later slice and
must consume the public evidence event without reading Assessment persistence.

## Contracts, Data, and Provenance

- Add a platform-owned, versioned Assessment contract family for the initial
  single-select definition, response command, deterministic result/evidence,
  and evidence event. Unknown item or scoring-policy versions fail closed.
- Preserve the existing lesson-package manifest's opaque Assessment file
  closure. Content validates bytes and delegates Assessment semantics; it does
  not learn correct answers or grade responses.
- Publish the assessment through a new immutable lesson package version.
  Existing `intro-risk-return@1.0.0` bytes, digest, placement behavior, and
  evidence remain unchanged and resolvable.
- Retain append-oriented Assessment evidence with stable opaque IDs, exact
  content and assessment provenance, normalized learner context, server time,
  deterministic scoring-policy version, and a response representation bounded
  to the selected option ID. Never log raw responses or place them in ordinary
  diagnostics.
- Treat an opaque client submission ID as an idempotency boundary: an exact
  replay returns the original result without duplicate evidence; conflicting
  reuse fails closed. A new attempt or retake is outside this slice.
- Commit the evidence and its versioned outbox record atomically. Later
  consumers must be able to process the event idempotently and retain its
  source-evidence reference without making Assessment a projection store.
- Extend the reviewed OpenAPI and regenerate the client. Handwritten browser
  models, backend imports, provider payloads, storage keys, database IDs, and
  unbounded feedback markup cannot cross the public seam.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Present exact knowledge check | The authorized learner sees the one single-select item and reviewed options tied to the exact lesson and assessment versions | Assessment/content integration plus component/browser test |
| Correct response | Submission yields a deterministic score of one and reviewed correct feedback; one append-oriented evidence set and event are retained | Assessment domain/application and PostgreSQL integration tests |
| Incorrect response | Submission yields a deterministic score of zero and reviewed corrective feedback without changing the scoring rule | Assessment domain/application plus API/browser test |
| Missing or malformed response | No option, multiple options, unknown option, unsupported schema, oversized value, or malformed identifier is rejected without evidence | Contract, application, and API denial tests |
| Missing or invalid learner context | Absent, tampered, expired, or revoked context fails closed without question answers, feedback internals, or learner evidence | Identity/API/browser denial tests |
| Stale or mismatched versions | A response for another package, assessment, item, or scoring-policy version is refused; no `latest` substitution or evidence occurs | Assessment application and API contract tests |
| Idempotent retry | Repeating the same submission ID and payload returns the original result and creates no duplicate evidence or event | PostgreSQL concurrency/idempotency integration test |
| Conflicting or concurrent submission | Conflicting reuse or simultaneous duplicate requests resolves deterministically to one accepted evidence set and bounded failure/original result | Transaction and API concurrency test |
| Persistence or outbox failure | Database failure leaves neither partial learner evidence nor a publishable event and exposes only redacted diagnostics | Failure-injection integration test |
| Safe feedback rendering | Authored feedback renders through a closed representation with no HTML injection, implicit fetch, or unsafe link behavior | Contract and renderer-security tests |
| Theme, keyboard, and reflow parity | The form, validation, submitted state, feedback, and errors retain equivalent content/actions across themes and supported widths | Component, Playwright, axe, keyboard, focus, and visual checks |
| Educational claim boundary | Feedback explains the concept but makes no mastery, certification, suitability, performance, or buy/sell/hold claim | Fixture review and browser assertion |
| Provider-neutral meaning | Public contracts and evidence contain platform identifiers and versions rather than local paths, drivers, or identity-provider payloads | Architecture and contract tests |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0006](../work-packets/WRK-0006-establish-assessment-contracts.md) | Establish executable Assessment definition, presentation, submission, evidence, event contracts, and the immutable successor fixture | none | none | complete |
| [WRK-0007](../work-packets/WRK-0007-deliver-deterministic-assessment-core.md) | Deliver Assessment scoring, append-oriented PostgreSQL evidence/outbox, and exact Content/Curriculum public seams | WRK-0006 | none | complete |
| [WRK-0008](../work-packets/WRK-0008-expose-knowledge-check-api.md) | Expose authenticated presentation/submission through FastAPI/OpenAPI and the generated TypeScript client | WRK-0007 | none | active |
| [WRK-0009](../work-packets/WRK-0009-deliver-knowledge-check-experience.md) | Deliver the accessible knowledge-check and deterministic feedback experience in the lesson workspace | WRK-0008 | none | ready |
| [WRK-0010](../work-packets/WRK-0010-qualify-knowledge-check-slice.md) | Qualify the complete local cross-system, security, architecture, accessibility, and runtime path | WRK-0009 | none | ready |

## Verification and Qualification

- Executable Assessment schema, semantic, version, scoring, feedback,
  response, evidence, and event fixtures, including unsupported and malicious
  cases.
- Domain tests that independently establish the exact expected score and
  feedback for correct and incorrect option IDs.
- Real PostgreSQL migration, append-only, atomic outbox, rollback,
  idempotency, conflict, concurrency, and failure-injection evidence.
- Module architecture tests for public-only Content/Curriculum/Assessment
  coordination, owned persistence, event ownership, and no reverse dependency.
- Identity authorization, bounded error, sentinel redaction, OpenAPI snapshot,
  and deterministic generated-client checks.
- Component and browser evidence for selection, validation, submission,
  feedback, loading, retry, denial, safe error, light/dark/system themes,
  keyboard/focus, status announcements, reflow, reduced motion, forced colors,
  and zero automated accessibility violations.
- A live same-origin local test through PostgreSQL, Python API/static serving,
  generated client, and Chromium, with no Node production server.
- Dependency/advisory review plus architecture, security, design,
  documentation, planning, readiness, and whitespace gates.

## Rollback and Migration

Assessment migrations require tested upgrade and downgrade or forward-fix
behavior from the current empty Assessment schema. The existing lesson read
path and `intro-risk-return@1.0.0` remain compatible throughout.

Once evidence is accepted, rollback may disable new submissions but must not
delete, rewrite, renumber, or reinterpret attempts, responses, scores, events,
or their exact version references. A rolled-back application must either read
the accepted contract safely or fail closed while preserving the records for a
forward fix. No backup, restore, retention, RPO, or RTO support claim is made.

## Stop Conditions

- Content, Curriculum, API, or UI would become a second scoring authority or
  read Assessment tables directly.
- The selected item cannot be represented by a bounded, versioned,
  deterministic single-select contract and independently expected fixtures.
- A retry, conflict, concurrent request, or database failure can create
  duplicate, partial, mutable, or unpaired evidence/outbox state.
- Exact package, assessment, item, scoring-policy, learner, or submission
  provenance would be lost or silently resolved to a newer version.
- Learner responses, session material, correct-answer internals, raw feedback,
  database/storage paths, or stack traces would enter logs or safe errors.
- Delivery requires a retake policy, manual grading, completion/mastery
  projection, Audit consumer, recovery support, managed-cloud protection,
  public exposure, AI authority, or another out-of-scope durable choice.
- A migration cannot preserve accepted evidence, a contract change breaks the
  completed SLI-0001 path, canonical sources conflict, or implementation scope
  overlaps active work.

## Documentation Impact and Completion Evidence

Packet planning should identify coordinated changes to Assessment domain and
contract documentation, the module map, content-package semantics, evidence
protection, API/generated-client references, interface behavior, migrations,
architecture verification, known gaps, local deployment guidance, and derived
learning/security/testing/interface context. Update only sources made stale by
executable behavior and classify local evidence as direct, shared semantics as
representative, and unimplemented recovery or managed-cloud behavior as gaps.

Completion evidence must identify exact contract versions and fixture hashes,
Assessment tables and migration behavior, scoring results, idempotency and
failure outcomes, event/outbox semantics, API/client drift results,
accessibility/theme evidence, live topology, advisories, documentation impact,
unperformed external qualification, residual risks, and the separate
completion-acceptance stage.

## Planning History

- 2026-08-05: Candidate B became eligible after SLI-0001 completed and was selected provisionally by deterministic scoring for explicit slice-selection review.
- 2026-08-05: Decomposed the selected boundary into the closed serial WRK-0006 through WRK-0010 packet set for plan-readiness review.
