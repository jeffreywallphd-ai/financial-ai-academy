---
id: CAP-0001
kind: capability
planning_status: verifying
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0001", "SLI-0015", "SLI-0016", "SLI-0017"]
---

# Capability: Complete a Structured Introductory Lesson

## Outcome

An individual learner can complete one approved, versioned introductory
financial-learning lesson, receive deterministic feedback on its bounded
knowledge check, return after interruption, and review retained attempt and
completion evidence tied to the exact lesson and assessment versions.

## Users and Value

The primary user is an individual learner beginning a structured financial
learning pathway. The capability establishes the first complete learning loop:
read source-backed educational material, demonstrate bounded understanding,
and return later without losing the evidence needed to explain the resulting
completion state.

Value is observable when the same authorized learner can reopen the exact
lesson and see a reproducible completion view derived from append-oriented
evidence rather than a mutable flag or model inference.

## Scope

### In Scope

- Open one approved lesson placement bound to an immutable package ID, semantic
  version, digest, assessment definition, and publication provenance.
- Present the lesson's objectives, constrained educational content, sources,
  examples, declared passive assets, and one bounded deterministic knowledge
  check through platform-owned public contracts.
- Accept one authorized learner response, validate it against the exact
  assessment version, score it deterministically, and return understandable
  feedback without AI or manual grading authority.
- Record append-oriented attempt, response, score, and bounded completion
  evidence with learner context, timestamps, idempotency, and content and
  assessment provenance.
- Derive a minimal completion projection from retained evidence without making
  a mastery, competency, certification, or investment-performance claim.
- Resume or reopen the lesson and review the retained attempt and completion
  history without silently substituting a newer content or assessment version.
- Preserve shared domain, application, contract, and evidence semantics across
  community and managed-cloud profiles while qualifying only deployment
  adapters that have accepted authority and an available environment.
- Provide equivalent accessible learner behavior in light, dark, and system
  themes, including denial, stale-version, duplicate, and unavailable states.

### Out of Scope

- Catalog search, enrollment, broad prerequisite navigation, or individualized
  next-activity recommendations.
- Content authoring, mutable drafts, publication workflow, package import/export
  UI, localization, or external learning-standard interoperability.
- Multi-item examinations, open-ended exercises, instructor review, manual
  grading, overrides, credentials, or certification.
- Mastery estimation, competency projection, adaptive ranking, experiments, or
  engagement optimization.
- AI tutoring, generated lesson content, model-provider selection, or AI-authored
  grading or feedback.
- Market data, valuation, portfolio simulation, backtesting, financial AI/ML
  labs, or investment recommendations.
- Organization tenancy, cohort administration, enterprise identity, billing,
  managed-cloud operations, or managed-cloud recovery objectives.
- Built-in-credential and OIDC delivery beyond the accepted provider-neutral
  identity contract; the currently implemented path remains `single_profile`.
- A comprehensive learner-record export product, automated backup service, or
  recovery guarantee beyond ADR-0008's community boundary.

## Canonical Context

- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Product Capability Catalog](../../product/capability-catalog.md)
- [Initial Glossary](../../domain/glossary.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Setup-Selectable Learner Identity](../../adr/ADR-0006-setup-selectable-learner-identity.md)
- [Versioned Lesson Package](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Community Evidence Protection and Recovery](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
- [Initial Runtime Baseline](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md)
- [Module Map](../../architecture/modules/module-map.md)
- [Content-Package Contract](../../architecture/contracts/content-package-contract.md)
- [Identity Provider Contract](../../architecture/contracts/identity-provider-contract.md)
- [Interface Design System](../../design/README.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [Backend Modules](../../../backend/src/financial_ai_academy/modules/README.md)
- [Web Application](../../../apps/web/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)

## Decision Gates and Constraints

- ADR-0005 fixes Content, Curriculum, Assessment, Learner model, and Audit as
  distinct owners for this loop. Modules communicate through public application
  operations or registered versioned events and never another module's internals
  or persistence.
- ADR-0006 fixes provider-neutral learner context and exactly one setup-selected
  identity mode. The existing executable seam qualifies only the private-host
  `single_profile` adapter and must not imply built-in, OIDC, remote, or managed
  identity qualification.
- ADR-0007 fixes immutable lesson-package identity, safe rendering, declared
  assets, source provenance, and Assessment ownership of runtime scoring.
- ADR-0008 fixes append-oriented evidence protection and the community
  private-host recovery boundary. Delivery may not claim an RPO, RTO, automatic
  backup, populated-target restore, or managed-cloud recovery posture.
- ADR-0009 fixes the Python/FastAPI/Pydantic backend and static
  TypeScript/React/React Router/Vite client boundary with generated public API
  clients and no Node production server.
- Eligibility, authorization, scoring, idempotency, completion derivation, and
  durable state changes remain deterministic. AI output cannot supply or
  override them.
- Learning evidence is append-oriented. Learner-model completion is a
  rebuildable projection that retains source-evidence references and never
  replaces Assessment evidence.
- No unresolved durable decision is required for this bounded CAP package.
  Crossing any out-of-scope identity, tenancy, recovery, AI, external-execution,
  or commercial boundary requires a separate decision before CAP reshaping.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0001 | A learner opens one approved, versioned lesson placement and can identify its objectives, sources, exact package version and digest, and publication provenance through the protected generated-client route. | First foundation; its existing completed packets establish Content, Curriculum, Identity, API, generated-client, renderer, and local qualification seams. | Broadening the package trust profile, identity modes, storage authority, or browser rendering contract changes the CAP package. | complete |
| SLI-0015 | The authorized learner submits the lesson's bounded knowledge check and receives deterministic, reproducible feedback while one idempotent attempt and score evidence chain is retained against the exact assessment and lesson versions. | After SLI-0001; introduces Assessment public operations, evidence contracts, persistence, API/client behavior, and focused denial paths without reopening the lesson-read contract. | Adding model or manual grading, open-ended/executable responses, unrelated assessment families, or mutable score history changes the CAP package. | complete |
| SLI-0016 | The learner closes and reopens the lesson and sees the correct completion state and evidence history rebuilt from retained Assessment evidence, including safe duplicate, stale-version, missing-context, and replay handling. | After SLI-0015; introduces the Learner-model projection and Audit references after the evidence source is stable. | Inferring mastery, replacing source evidence, adding adaptive recommendations, or expanding recovery and retention claims changes the CAP package. | complete |
| SLI-0017 | The complete lesson loop is qualified across domain, event, persistence, API, generated-client, accessible browser, security, provenance, interruption, and community protection boundaries, with unsupported deployment profiles reported rather than fabricated as passing. | Last; depends on SLI-0001, SLI-0015, and SLI-0016 and closes only after their exact contracts and evidence are current. | Qualifying built-in/OIDC identity, managed-cloud operations or recovery, unrelated curricula, or a broader browser/content profile changes the CAP package. | complete |

## Capability Acceptance

The capability is complete only when evidence demonstrates that:

- an authorized learner opens the intended immutable lesson placement and sees
  its objectives, approved educational sources, version, digest, and provenance;
- the exact assessment definition is resolved without a silent `latest`
  substitution and malformed or unsupported definitions fail before an attempt
  or completion record is created;
- one valid response produces deterministic scoring and bounded feedback while
  retry and idempotency behavior prevents duplicate business evidence;
- attempt, response, score, and completion evidence retain learner context,
  content and assessment versions, event identity, time, and provenance without
  exposing identity-provider or storage internals;
- a learner-model projection can be rebuilt from evidence and reopening the
  lesson reproduces the correct history and completion state without claiming
  mastery;
- missing, expired, revoked, tampered, or client-selected learner context;
  unauthorized or cross-learner access; stale versions; replay; partial storage
  failure; and projection interruption fail safely and leave no false completion;
- Content, Curriculum, Assessment, Learner model, Identity, and Audit ownership
  and dependency direction are enforced by focused architecture checks;
- the same domain and contract semantics are reusable by local and cloud
  adapters, while qualification reports unavailable profiles explicitly;
- delivered interfaces preserve content and actions in light and dark modes and
  meet applicable keyboard, focus, contrast, zoom/reflow, reduced-motion,
  forced-color, and assistive-technology expectations; and
- educational completion and feedback are never presented as mastery,
  certification, personalized financial advice, suitability, or expected
  investment performance.

## Risks and Non-Goals

- Assessment implementation may accidentally treat package transport as grading
  authority or collapse attempts, score evidence, and completion projection into
  one mutable record.
- Event delivery and projection replay can create duplicate or out-of-order
  evidence unless event identity, idempotency, and rebuild rules are explicit.
- Extending the delivered `single_profile` path to remote or multi-user use would
  exceed its accepted private-host security boundary.
- Recovery language can overstate ADR-0008 unless backup freshness, host
  protection, empty-target restore, and no-RPO/RTO limitations remain explicit.
- Example financial material must remain sourceable education and cannot contain
  personalized buy, sell, hold, allocation, or suitability recommendations.
- CAP-0001 is not a general assessment engine, curriculum browser, adaptive
  pathway, instructor workflow, or credentialing product.

## Documentation Impact

Delivery is expected to refine Assessment and Learner-model domain rules, public
operations, evidence/event contracts, persistence ownership, API and generated
client contracts, security and recovery evidence, interface behavior, module
README files, architecture verification, and known verification gaps. Derived
context packs change only after their canonical sources change.

## Capability Completion Evidence

- All four approved manifest slices are complete. SLI-0001 delivers and
  qualifies the protected exact lesson-read path; SLI-0015 delivers and
  qualifies deterministic knowledge-check evidence; SLI-0016 delivers and
  qualifies Audit reconciliation plus rebuildable retained completion; and
  SLI-0017 traces the whole loop to every capability acceptance criterion.
- The completed candidate passed 196 backend tests under Python 3.14.3 with
  disposable PostgreSQL 18.4, 26 web tests, eight focused Chromium scenarios,
  and two live same-origin scenarios. The live learner submitted the exact
  approved check and reopened twice with an unchanged completion source-set.
- OpenAPI and the generated client were current. Node 24 typecheck, lint, and
  production build passed; dependency audit reported zero vulnerabilities.
  Eight architecture fitness functions, ten security control groups, and the
  125-token/56-icon design-system validation passed. The fixed aggregate
  readiness gate passed all 27 checks against the capability base revision.
- Assessment evidence remains append-oriented; Learner-model state is a
  rebuildable projection; identity, content, assessment, audit, provider, and
  persistence internals remain behind owned seams. No contract, migration, or
  compatibility gap is concealed by capability closure.
- Qualification is deliberately limited to the private-host `single_profile`,
  synchronous replay, PostgreSQL/Python same-origin, and reviewed Chromium
  profile. Built-in/OIDC, multi-user and managed-cloud identity, background
  delivery, production database roles, automated backup/restore and RPO/RTO,
  non-Chromium/manual screen-reader coverage, broader assessment families,
  mastery, adaptation, advice, suitability, and performance remain outside the
  completed capability rather than being represented as passing.
- All disposable containers and temporary build output were removed. Closure
  required no new decision gate, approval stage, material CAP-package change,
  or product behavior beyond the approved manifest.

## Planning History

- 2026-08-04: The initial capability was shaped and its four durable decisions
  were promoted through ADR-0005 through ADR-0008.
- 2026-08-05: SLI-0001 delivered the approved lesson-read seam and entered
  verification under the earlier planning topology.
- 2026-10-15: The capability returned to `shaping` for the `cap-package-v1`
  workflow. The complete manifest now retains SLI-0001 and reserves SLI-0015
  through SLI-0017 for deterministic knowledge-check evidence, resumable
  completion projection, and whole-capability qualification. This material
  package revision requires one current CAP-level approval before delivery
  resumes; no slice- or packet-level approval is introduced.
- 2026-10-15: Completed all four approved manifest slices. Direct cumulative
  evidence satisfies every capability criterion and preserves explicit limits
  for identity, recovery, cloud, queue, browser, mastery, and advice profiles.
