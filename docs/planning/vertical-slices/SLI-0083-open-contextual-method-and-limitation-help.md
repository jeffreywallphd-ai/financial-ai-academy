---
id: SLI-0083
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: CAP-0020
depends_on: [SLI-0082]
decision_gates: []
---

# Vertical Slice: Open Contextual Method and Limitation Help

## Outcome and User Scenario

While using an existing lesson, practice, Project, or AI-assistance feature, an
authorized learner can open reviewed explanations for the method, source and
history, data distinction, AI boundary, or education-versus-advice limit that
applies at that point. The link names the learner question, resolves to one
exact approved topic version, and returns to the originating feature. Browser
and headless clients use the same protected Guidance context contract; feature
code does not invent or reinterpret help policy.

## Scope Boundaries

### In Scope

- An additive versioned contextual-help contract owned by Guidance. One exact
  feature context and version maps to an ordered bounded set of exact approved
  platform-help topic references with learner-readable labels and purposes.
- Pure validation, canonical digest, and a checked-in immutable context registry
  that rejects duplicates, unknown or dangling topic versions, unsafe labels,
  unknown fields, inconsistent applicability, and changed same-version meaning.
- A protected exact-context read operation composed through the existing
  Guidance public seam, OpenAPI snapshot, and generated TypeScript client so
  browser, command-line, service, and future headless clients see the same map.
- Reviewed starter explanations for source and history plus the distinctions
  among observed, calculated, simulated, predicted, and generated information.
  Existing exact method, AI-control, and education-not-advice topics remain the
  owned destinations when their current meaning is sufficient.
- Contextual links from a bounded set of already-delivered lesson/publication,
  practice-result, Project artifact/result, and AI-assistance preference
  surfaces. Each feature requests its closed context key and renders only the
  server-returned safe label and exact same-origin topic destination.
- Preserved return context, plain language, keyboard/focus behavior, narrow and
  zoomed layouts, supported themes, forced colors, reduced motion, and safe
  failure that leaves the underlying feature usable when contextual Help is
  missing, stale, denied, malformed, or unavailable.
- Focused and isolated evidence for exact topic correlation, browser/headless
  parity, source binding, authorization confidentiality, read-only containment,
  offline local use, normal restart, accessibility, and bounded cleanup.
- Anti-rigidity coverage for additional valid contexts/topics, varied ordering,
  optional or unavailable Help, copy improvements, and feature data shapes that
  preserve the declared contract rather than a fixed fixture count or layout.

### Out of Scope

- Feature limitation/unavailable/degraded-state guidance and troubleshooting;
  SLI-0084 owns those flows. Corpus-wide freshness, broken-link, search-quality,
  offline, and cumulative accessibility closure remains SLI-0085 work.
- Changing lesson, practice, Project, preference, method, provenance, result,
  identity, authorization, grading, eligibility, learner-state, or financial
  behavior. Contextual Help explains accepted meaning but does not own it.
- Arbitrary caller-selected topic IDs, browser-owned mappings, feature-specific
  duplicate Help content, direct repository-document links, external URLs,
  mutable authoring, search analytics, personalization, or behavioral tracking.
- AI-generated canonical help, semantic/vector retrieval, model/provider calls,
  learner-specific financial conclusions, suitability, advice, execution,
  hosted support, managed-cloud operation, or a separate headless-AI mode.
- Nonfunctional visual polish that does not impair meaning, required actions,
  accessibility, or responsive use; optional polish remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0020](../capabilities/CAP-0020-understand-platform-methods-and-limitations.md)
  defines this approved contextual-help increment after SLI-0082.
- [SLI-0082](SLI-0082-browse-search-approved-help.md) supplies immutable exact
  topics, literal search, protected APIs, generated client, safe rendering, and
  live browser/headless qualification.
- [Module Map](../../architecture/modules/module-map.md) assigns safe versioned
  product projections and contextual links to Guidance while each feature and
  canonical source retains semantic authority.
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  and [Compatibility and Versioning](../../architecture/contracts/compatibility-and-versioning.md)
  require additive exact public shapes and generated clients.
- [Financial Method and Simulation Architecture](../../architecture/finance/financial-method-and-simulation-architecture.md),
  [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md),
  and [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
  own the method, data-classification, AI-authority, and advice boundaries that
  Help may explain but not redefine.
- [User-Facing Language Standards](../../standards/user-facing-language-standards.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [Interface Design Standards](../../standards/interface-design-standards.md)
  govern task-first labels, progressive detail, and accessible presentation.
- [Decision Readiness](../../adr/decision-readiness.md) is ready for the shared
  modular-monolith, public contract, local identity, and checked-in read-only
  Guidance boundary. Tenancy, managed cloud, provider/model use, external
  execution, recovery, and commercial policy are not exercised.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Guidance-owned exact contextual-help registry, protected API, generated client, and bounded feature links | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add exact Help references separately to each owning feature's public response | yes, but duplicates one cross-feature mapping across several contracts and releases | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 11 |
| C. Keep a browser-only constant map from feature routes to Help topics | no; browser becomes policy authority and headless clients cannot discover the same links | - | - | - | - | - | - | - |
| D. Search Help text from each feature and choose the first result | no; literal ranking is not an exact applicability contract and content wording could silently redirect meaning | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14 of 14. It preserves one Guidance-owned, exact,
transport-neutral map while feature owners retain their own behavior and source
meaning. It is independently verifiable, additive, read-only, reversible, and
uses the exact topics already delivered by SLI-0082. Candidate B produces the
same visible outcome but would distribute Guidance identity across multiple
feature contracts, requiring coordinated version churn for an editorial link
change. Candidates C and D are ineligible because they create browser-only or
search-derived authority and break headless parity.

This refinement keeps the approved SLI-0083 outcome, dependency, stop boundary,
and CAP acceptance unchanged. It adds no slice, external effect, durable
decision, provider/model behavior, or lower-level approval.

## Boundary Path

1. Canonical method, data, AI, provenance, and risk sources remain authoritative;
   Guidance records only reviewed safe projections and exact source bindings.
2. An additive `contextual-help/v1` schema defines one exact context identity,
   version, feature applicability, ordered exact topic references, publication
   facts, and canonical digest.
3. Pure Guidance validation admits an immutable checked-in registry only when
   every exact topic exists in the admitted platform-help corpus and every
   context identity, label, relationship, source, and digest is closed.
4. A Guidance application operation reads one exact context. The protected API
   authorizes first, accepts no learner selector, and maps bounded public
   unavailable/not-found failures without disclosing registry contents.
5. Reviewed OpenAPI generates the shared TypeScript client. Bounded delivered
   feature loaders request a closed context key/version and never import
   Guidance internals or rank, substitute, or construct topic destinations.
6. Feature pages show concise learner-question links, open the exact Help topic,
   preserve a safe same-origin return target, and leave the feature usable when
   optional contextual Help cannot be shown.
7. Focused and isolated qualification compares browser and ordinary headless
   context/topic reads, source and digest meaning, authorization, restart,
   containment, accessibility, and exact cleanup.

## Contracts, Data, and Provenance

`contextual-help/v1` is additive and read-only. A context has a stable
`context_key`, semantic `context_version`, learner-readable feature label,
applicability facts, ordered exact topic references, publication facts, source
references, and a canonical digest. Each reference contains only exact
`topic_id`, `topic_version`, a closed relationship/purpose, and safe link text.
It contains no route, URL, repository path, browser component, learner identity,
permission, prompt, provider/model payload, arbitrary command, or mutable state.

The initial registry is checked-in immutable product data admitted at startup
with the topic corpus. A same-version context cannot change meaning; a mapping
change publishes a new exact context version. The server derives same-origin
topic destinations from contract identity. Browser return targets are parsed
through the already-closed Help selection and never enter canonical Guidance
records.

No persistence schema, migration, analytical store, event, provider, job, or
external data source is added. Browser and headless consumers use the same
protected public operation; feature APIs and domain records remain unchanged.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Contextual method explanation | A learner opens Help beside a supported calculation/result surface and reaches the exact reviewed method topic, then returns to the unchanged feature | contract/API/component/Chromium |
| Source and history explanation | A lesson or Project surface offers plain contextual Help for publication/provenance meaning without replacing its exact technical record | corpus/component/browser |
| Data distinction | A result-classification surface links to reviewed observed/calculated/simulated/predicted/generated distinctions without relabeling the source record | corpus/API/browser |
| Education and advice boundary | A supported financial-learning surface opens the exact educational-use limitation and retains the originating learner task on return | component/Chromium |
| AI authority boundary | The assistance-preference surface opens the exact approved AI-control topic without enabling a provider or implying model authority | component/API/browser |
| Browser/headless parity | Equivalent authorized clients read one exact context and its referenced topics | Both receive the same ordered versioned public documents and digests | API/live |
| Missing or stale mapping | A feature requests an absent context/version or a referenced topic is unavailable | The feature stays usable, offers ordinary Help/search recovery when safe, and does not substitute another topic | domain/API/component |
| Malformed registry | A duplicate, dangling reference, unknown field, unsafe label, bad chronology, or digest mismatch is loaded | The complete registry is rejected before partial contextual links become visible | contract/domain/composition |
| Authorization confidentiality | Context or exact-topic access lacks a valid server session/permission | Access fails closed without revealing context counts, labels, topic identities, source facts, or rejected input | API/security |
| Flexible valid registry | Contexts, reference count/order, feature data, safe copy, and optional Help availability vary within contract bounds | Required meaning and actions hold without fixed fixture counts, prose, or layout snapshots | property/component anti-rigidity |
| Accessible return | Links are used by keyboard in supported themes, narrow/zoomed/forced-color/reduced-motion states | Exact Help and the safe return action remain perceivable and operable | Chromium/axe |
| Local restart and containment | Browser and headless reads run before and after normal restart | Identical checked-in context/topic meaning remains available with no non-loopback request or durable feature-state mutation | live/architecture |

## Agent Work Packets

Packet IDs are reserved and packets authored one at a time immediately before
start. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0170](../work-packets/WRK-0170-freeze-contextual-help-contracts-and-registry.md) | Add the exact context contract, pure validation/digest behavior, reviewed source-bound starter topics, immutable registry, compatibility fixtures, and focused anti-rigidity tests | SLI-0082 | none | complete |
| [WRK-0171](../work-packets/WRK-0171-compose-contextual-help-api.md) | Add the Guidance application/public exact-context read, protected API, reviewed OpenAPI, generated client, and authorization/failure tests | WRK-0170 | none | complete |
| [WRK-0172](../work-packets/WRK-0172-deliver-contextual-help-links.md) | Add generated-client contextual links and safe return behavior to the bounded lesson, practice, Project, and AI-assistance surfaces with focused component/browser accessibility evidence | WRK-0171 | none | complete |
| [WRK-0173](../work-packets/WRK-0173-qualify-contextual-help-live-flow.md) | Prove exact browser/headless parity, source/digest correlation, denial, restart, no-outbound behavior, read-only containment, accessibility, anti-rigidity, and cleanup | WRK-0172 | none | ready |

Sequential delivery is the default because the seams share Guidance contracts,
corpus/registry admission, generated client, Web routing, and live-runner
surfaces. A bounded correction may add a dependent packet inside this slice
without renewed CAP approval.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; pure context identity, validation,
canonical-digest, exact-topic correlation, registry atomicity, and varied-valid-
shape tests; Guidance composition and protected API success/not-found/denial
tests; reviewed OpenAPI and generated-client reproduction; TypeScript boundary,
loader, model, and component tests; focused Chromium keyboard, axe, light/dark,
narrow, 200-percent-text, forced-color, and reduced-motion checks; and one
isolated browser plus ordinary headless HTTP flow with normal restart,
non-loopback observation, state-containment comparison, and bounded cleanup.

Also run architecture/import, source-authority, active-content, privacy,
advice-language, AI-authority, learner-language, design-system, documentation,
planning, dependency, Python/TypeScript, zero-warning lint, build, whitespace,
controller-selected exact-candidate verification, independent technical review,
deterministic slice closure, and `python dev-tools/agent/check_ready.py`.

Tests protect exact identity, safe destinations, learner meaning, failure
recovery, and accessibility. They do not freeze whole prose, topic/context
counts, incidental ordering outside the declared record, layout pixels, or
optional styling.

## Rollback and Migration

No database or learner-state migration is required. A code rollback may remove
unreferenced context API and feature links, but an exposed public context schema
or identity follows additive compatibility rules. Registry/topic publication is
atomic; an invalid successor leaves the prior deployable artifact unchanged.
Feature behavior remains useful when contextual Help is absent, so optional link
rollback does not block the owning learner task.

## Stop Conditions

Stop for ambiguity in canonical method, provenance, data-classification, AI, or
advice meaning; Help becoming feature/product/domain/risk authority; a breaking
public contract; feature API/domain record reinterpretation; arbitrary routes,
external content, raw repository documents, active content, model/provider use,
semantic search, personalization, tracking, financial advice/suitability/action,
identity or tenancy expansion, managed-cloud/recovery/commercial policy, stale
CAP authority, active ownership collision, or material CAP-0020 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
fixture count/order, nonfunctional styling, or another inconsequential issue.
Fix a bounded issue in scope or route optional presentation polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will reconcile the Guidance boundary and resource contribution rules,
context/topic contracts and compatibility guidance, protected API/OpenAPI and
generated client, bounded feature README and user-facing behavior, local
runtime/architecture assurance, known gaps, this slice, its packets, the CAP,
and the planning register.

Completion evidence must name exact candidates and receipts; context/topic
identities and source fingerprints; browser/headless parity; authorization and
safe failures; return behavior; restart/offline-local results; non-loopback
observation; read-only containment; accessibility; anti-rigidity; cleanup;
compatibility impact; unsupported deployment profiles; residual gaps; and
CAP-package conformance. Approval and reviewer records remain ignored.

## Planning History

- 2026-10-18: Refined just in time after SLI-0082 completed. Candidate A scores
  14 of 14 and establishes one Guidance-owned exact contextual-help contract
  for browser and headless consumers without making feature code, text search,
  external content, or AI a new authority. The approved CAP outcome, four-slice
  manifest, ordering, risk posture, and material-change boundaries are unchanged;
  no slice-level approval is required.
- 2026-10-18: Activated WRK-0170 from clean base `547fbe0` after confirming the
  current CAP binding, completed SLI-0082 dependency, exact contract/core scope,
  and no unresolved decision or active coordination collision.
