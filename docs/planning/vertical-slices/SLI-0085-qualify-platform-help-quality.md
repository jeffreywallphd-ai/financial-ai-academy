---
id: SLI-0085
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: CAP-0020
depends_on: [SLI-0082, SLI-0083, SLI-0084]
decision_gates: []
---

# Vertical Slice: Qualify Platform Help Quality

## Outcome and User Scenario

When a contributor changes reviewed Platform Help or one of its canonical
sources, one deterministic repository gate identifies stale source bindings,
broken exact links, unsafe records, search regressions, or incomplete
integration before the change can be delivered. Learners and ordinary
headless clients receive the same reviewed Help through the local application,
with accessible safe rendering, deterministic discovery, offline operation,
normal-restart stability, and no fixed-corpus assumptions that block valid
future topics or feature explanations.

## Scope Boundaries

### In Scope

- A repository-owned Guidance quality command that binds safe source keys to
  current canonical files and checks exact fingerprints without putting
  repository paths in runtime records or public responses.
- Atomic admission of the Platform Help corpus, contextual registry, and
  feature-guidance registry as one exact link graph, including required starter
  identities, canonical digests, exact topic references, and source bindings.
- Deterministic search and pagination quality checks across varied valid
  topics, ordering, filters, query forms, result counts, and continuation
  boundaries without freezing the starter corpus size or whole prose.
- Safe-serialization and browser-rendering evidence that malformed, private,
  active, stale, or unknown content fails closed before partial display.
- Contributor instructions and control-plane selection so the focused quality
  gate runs when Guidance resources, their canonical sources, shared client
  rendering, or the quality tooling changes.
- Cumulative browser and ordinary headless qualification for exact parity,
  accessibility, local/offline operation, normal restart, loopback-only reads,
  read-only containment, flexible valid additions, and bounded cleanup.
- Bounded corrections discovered by the qualification when they preserve the
  approved CAP outcome and public contracts.

### Out of Scope

- New learner features, API operations, public schemas, database state,
  telemetry, personalization, analytics, semantic retrieval, or authoring UI.
- External link crawling, remote content ingestion, hosted support, public
  deployment, production uptime, load, backup, recovery, or non-Chromium
  certification.
- AI-generated or AI-scored content, search, explanations, troubleshooting, or
  quality judgments; provider/model selection or execution; embeddings or
  vector search.
- Replacing canonical product, architecture, contract, risk, or design sources
  with Help content, or exposing repository paths and internal diagnostics to
  clients.
- New identity, tenancy, data licensing, queue, encryption, cloud-provider,
  legal, commercial, financial-advice, or external-execution behavior.
- Nonfunctional visual polish that belongs in CAP-0031.

## Canonical Context and Decisions

- [CAP-0020](../capabilities/CAP-0020-understand-platform-methods-and-limitations.md)
  enumerates this final slice for freshness, link integrity, safe rendering,
  search quality, accessibility, offline local use, and anti-rigidity closure.
- [SLI-0082](SLI-0082-browse-search-approved-help.md),
  [SLI-0083](SLI-0083-open-contextual-method-and-limitation-help.md), and
  [SLI-0084](SLI-0084-understand-feature-limits-and-safe-recovery.md) supply the
  complete read-only Guidance boundary and focused evidence this slice
  qualifies cumulatively.
- [Guidance resources](../../../backend/src/financial_ai_academy/modules/guidance/resources/README.md)
  define immutable contribution, exact-version, source-binding, and safe-action
  rules for all three registries.
- [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  [Compatibility and Versioning](../../architecture/contracts/compatibility-and-versioning.md),
  and the [Module Map](../../architecture/modules/module-map.md) keep exact
  contracts and runtime ownership authoritative.
- [Testing Architecture](../../architecture/assurance/testing-architecture.md),
  [Architecture Verification](../../architecture/assurance/architecture-verification.md),
  and [Known Verification Gaps](../../assurance/known-verification-gaps.md)
  govern direct evidence and honest residual gaps.
- [User-Facing Language Standards](../../standards/user-facing-language-standards.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [Interface Design Standards](../../standards/interface-design-standards.md)
  govern plain language, safe detail, accessibility, and theme parity.
- [Decision Readiness](../../adr/decision-readiness.md) is ready for this
  deterministic repository and local-runtime qualification. External retrieval,
  AI authority, managed-cloud operation, and hosted support are not exercised.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. One deterministic Guidance quality gate plus cumulative local browser/headless qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Rely only on the existing separate unit, browser, security, and live checks | yes, but contribution failures remain fragmented and source selection stays implicit | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 12 |
| C. Crawl remote links and hosted support content as part of delivery | no; it adds external retrieval, availability, licensing, and hosted-support decisions | - | - | - | - | - | - | - | - |
| D. Use an AI model or semantic grader to judge Help quality and search relevance | no; model/provider authority, grounding, evaluation, and failure policy are outside this CAP | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14 of 14 because it turns already-delivered exact contracts
and focused tests into one contributor-facing result while retaining direct
browser and headless evidence. It makes freshness and cross-registry link
ownership explicit, is locally reproducible, and can roll back without public
or stored-data migration. Candidate B is bounded but scores lower because a
contributor must infer which scattered commands and source files establish the
complete quality result. Candidates C and D are ineligible because they add
unapproved external or model authority.

The refinement preserves CAP-0020's outcome, four-slice manifest, dependency
order, safety posture, and material-change boundaries. It adds no slice,
durable decision, public operation, provider call, or lower-level approval.

## Boundary Path

1. Canonical product, architecture, contract, risk, and language files remain
   the authoritative source meaning.
2. Repository-only quality metadata maps safe source keys to those canonical
   files and compares current file digests with the runtime manifest bindings.
3. The quality command loads the Platform Help, contextual, and feature
   registries through their public adapters so exact identities, digests,
   links, and whole-registry admission use production validation rather than a
   second parser.
4. Focused contract/domain tests exercise deterministic search, varied valid
   extensions, malformed/stale/private/active content, and fail-closed
   serialization.
5. The existing protected Guidance API and generated TypeScript client serve
   the same read-only records to browser and headless clients.
6. Component and Chromium evidence verifies safe accessible presentation; the
   isolated local topology verifies parity, restart, loopback-only reads,
   read-only containment, and cleanup.
7. Control-plane affected selection and aggregate readiness make the focused
   quality result repeatable for later contributions.

## Contracts, Data, and Provenance

No public contract or stored learner data changes. Repository-only source
authority metadata identifies canonical file locations for build-time
freshness checks; these paths never enter runtime Guidance values, generated
clients, logs, or responses. Runtime `platform-help/v1`, `contextual-help/v1`,
and `feature-guidance/v1` identities, canonical digests, source references,
exact topic links, closed action kinds, and safe failure meaning remain
unchanged.

The focused gate must use the shipped adapters and contract validators. It may
summarize safe source keys and failing quality dimensions for contributors but
must not print learner data, credentials, private payloads, rejected record
contents, or deployment-specific paths. Valid additional topics, contexts, and
feature records remain supported when they satisfy the same exact contracts.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Current reviewed sources | A contributor runs the focused Guidance quality command | Every safe source key resolves to one canonical file whose digest matches the runtime source binding | repository quality gate |
| Stale canonical source | A bound canonical file changes without a reviewed Guidance update | The focused command identifies the stale safe source key and fails before delivery | repository quality gate |
| Broken exact link | A context, related topic, feature record, or mapping refers to missing exact meaning | Complete registry admission fails without exposing a partial graph | domain/quality gate |
| Deterministic search | Valid topics, queries, filters, result counts, and file order vary | Results, pagination, and exact reads remain stable by contract rather than fixture count or incidental order | property/unit/contract |
| Unsafe or malformed content | A record contains active markup, private fields, unknown keys, stale digest, or invalid text | Validation fails closed and the browser renders no partial record or leaked value | schema/security/component/Chromium |
| Accessible Help | A learner uses keyboard, narrow layout, 200-percent text-equivalent reflow, themes, forced colors, or reduced motion | Equivalent content and actions remain reachable with no serious automated accessibility violation | component/Chromium |
| Browser/headless parity | Equivalent authorized clients read and search Guidance | Both receive equivalent ordered public meaning and safe denial/failure behavior | API/live |
| Offline local restart | The isolated local application is read before and after a normal restart without external connectivity | Guidance remains available from checked-in resources, requests stay loopback-only, and meaning is stable | live/architecture |
| Flexible valid extension | An additional valid topic or mapping changes corpus size, prose, references, or file order | The quality gate accepts the extension without weakening exact links or source provenance | property/quality gate |
| Containment and cleanup | Qualification succeeds or fails | No learner/feature state changes and only bounded test artifacts are removed | live/control plane |

## Agent Work Packets

Packet identifiers are reserved and detailed packets are authored one at a
time immediately before work starts. The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0178](../work-packets/WRK-0178-build-guidance-quality-gate.md) | Build the deterministic contributor-facing Guidance quality gate, source-authority binding, flexible valid-extension fixtures, and affected-check integration | SLI-0082 through SLI-0084 | none | active |
| reserved just in time | Run and close cumulative browser/headless, accessibility, offline-local, restart, containment, anti-rigidity, documentation, and control-plane qualification | prior packet | none | captured |

Sequential delivery is required because both packets share the quality command,
Guidance resources, affected-check catalog, and cumulative evidence. A bounded
correction may add a dependent packet without changing the approved CAP.

## Verification and Qualification

Run focused source-freshness, whole-registry, exact-link, schema, compatibility,
digest, search-property, varied-extension, unsafe-content, active-content,
privacy, and source-authority checks. Run the affected-check catalog tests and
prove the focused Guidance quality command is selected for canonical sources,
resources, adapters, public Guidance surfaces, generated-client rendering, and
its own tooling.

Run component and focused Chromium accessibility and safe-rendering checks,
then the complete isolated approved-lesson topology with browser/headless
parity, normal restart, loopback-only observation, database containment, and
bounded cleanup. Finish with reviewed OpenAPI/client reproduction, Python and
TypeScript checks, zero-warning lint, build, architecture, security, design,
documentation, planning, whitespace, controller-selected exact-candidate
verification, and aggregate readiness.

Evidence protects exact meaning, freshness, link integrity, deterministic
search, confidentiality, accessibility, offline availability, and ownership.
It must not freeze whole prose, valid corpus size, incidental file order,
layout pixels, or optional styling.

## Rollback and Migration

No database, learner-state, public-contract, or feature-state migration is
required. Repository quality tooling and its control-plane registration can
roll back together. Existing Guidance resources and clients remain compatible;
published exact records still require additive successors if meaning changes.

## Stop Conditions

Stop for conflicting canonical meaning; a stale or missing CAP package;
ambiguous runtime ownership; a required public-contract break; repository paths
or private data entering a runtime response; external content retrieval or
hosted support; AI/model authority; automatic remediation; a new identity,
tenancy, licensing, cloud, queue, encryption, recovery, legal, commercial, or
external-execution decision; an active ownership collision; or material
CAP-0020 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
valid fixture count/order, nonfunctional styling, or an equivalent
inconsequential issue. Fix it within bounded scope or route optional visual
polish to CAP-0031.

## Documentation Impact and Completion Evidence

Update Guidance contributor instructions, control-plane check documentation,
architecture verification and residual gaps, direct consumer READMEs, the
packet artifacts, this slice, and the planning register. Completion evidence
must record the exact candidate and qualifying receipt, selected checks and
results, focused and cumulative test results, browser/headless parity,
accessibility, restart and no-outbound observations, state containment,
cleanup, residual gaps, rollback/migration status, and CAP conformance.

## Planning History

- 2026-10-18: Refined immediately after SLI-0084 completed. Candidate A scores
  14 of 14 and selects one deterministic contributor-facing quality result plus
  cumulative local qualification. The refinement preserves the approved
  CAP-0020 outcome, four-slice manifest, ordering, risks, and non-goals; no
  slice-level approval exists or is required.
- 2026-10-18: Activated WRK-0178 from clean base `be5e38f` after confirming
  current CAP authority, completed dependencies, bounded quality-tool scope,
  and no decision or ownership collision.
