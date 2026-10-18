---
id: SLI-0084
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: CAP-0020
depends_on: [SLI-0083]
decision_gates: []
---

# Vertical Slice: Understand Feature Limits and Safe Recovery

## Outcome and User Scenario

When a delivered feature is limited, unavailable, degraded, or uncertain, an
authorized learner sees a plain explanation of what could not be completed,
what was protected or may already have happened, and the next safe action. The
explanation is bound to one reviewed versioned Guidance record and the public
condition already reported by the owning feature. Browser and headless clients
can read the same record without exposing secrets, raw diagnostics, internal
selectors, unsupported guarantees, or executable troubleshooting commands.

## Scope Boundaries

### In Scope

- An additive `feature-guidance/v1` contract for one exact reviewed limitation
  or recovery record and one exact surface-condition mapping. Records contain
  learner-facing status, reason, protected or uncertain outcome, closed safe
  next-action kinds, exact Help references, applicability, source/publication
  facts, and a canonical digest.
- Pure Guidance validation, canonicalization, complete-registry admission, and
  exact lookup. Duplicate mappings, dangling topics, unsafe text, arbitrary
  destinations, commands, guarantees, private fields, stale source bindings,
  and changed same-version meaning fail before partial guidance is visible.
- A protected exact Guidance operation, reviewed OpenAPI snapshot, and
  generated client so browser, command-line, service, and future headless
  clients use the same safe record. The operation accepts a closed surface key,
  condition key, and exact mapping version; it never accepts a learner ID,
  stack trace, provider payload, raw exception, or caller-written message.
- Bounded integration with already-delivered conditions where more than generic
  retry copy materially helps: an absent exact lesson version, an uncertain
  practice save or submission, a stale or unavailable Saved-learning source,
  an inert Project artifact that cannot run in the platform, and an AI-help
  choice whose provider/model execution is not enabled by that choice.
- A reusable accessible explanation that preserves the owning feature's
  primary status and action, renders only server-returned safe meaning, and
  opens exact same-origin Help topics. Guidance cannot make a feature available,
  decide whether a write occurred, select a provider, or execute a recovery.
- Safe fallback when Guidance is missing, denied, stale, malformed, or
  unavailable: the feature's existing learner-safe status and action remain
  usable and no substitute record is invented.
- Focused and isolated evidence for exact condition correlation,
  browser/headless parity, confidentiality, unchanged-request retry meaning,
  read-only containment, local restart, accessibility, offline local use,
  varied valid records/actions, and bounded cleanup.

### Out of Scope

- Changing feature availability, error/status codes, write or retry semantics,
  idempotency, version selection, provider/model enablement, artifact execution,
  source validation, feature authorization, or durable feature state.
- Raw exception, log, trace, database, object key, filesystem path, account,
  credential, request payload, answer, learner identifier, provider response,
  secret, or private diagnostic disclosure.
- Arbitrary shell, Docker, package, database, network, support, remediation, or
  provider commands; automatic repair; operational runbooks in learner UI;
  external URLs/content; hosted support; ticket creation; chat escalation; or
  claims that retry, availability, recovery, performance, compliance, or a
  provider outcome is guaranteed.
- Cross-feature health aggregation, monitoring, incident management, status
  pages, telemetry/analytics, personalization, semantic retrieval, AI-generated
  troubleshooting, or model/provider calls.
- New identity, tenancy, managed-cloud, queue, encryption, backup/recovery,
  legal, commercial, or public-hosting behavior; a separate headless-AI mode;
  or nonfunctional visual polish suitable for CAP-0031.

## Canonical Context and Decisions

- [CAP-0020](../capabilities/CAP-0020-understand-platform-methods-and-limitations.md)
  enumerates this third slice after contextual Help and requires safe limitation
  and troubleshooting guidance without command execution or guarantee claims.
- [SLI-0083](SLI-0083-open-contextual-method-and-limitation-help.md) supplies
  immutable exact Help topics, contextual mappings, protected Guidance APIs,
  generated-client rendering, and live browser/headless qualification.
- [Module Map](../../architecture/modules/module-map.md) assigns safe versioned
  explanations to Guidance while feature owners retain status, state,
  authorization, write, retry, and availability authority.
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  and [Compatibility and Versioning](../../architecture/contracts/compatibility-and-versioning.md)
  require additive closed contracts and generated public clients.
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
  keeps provider/model use explicitly admitted and disabled by default; an
  AI-help preference is intent, not execution authority.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) keeps Project
  artifacts inert and learner-executed outside the platform.
- [User-Facing Language Standards](../../standards/user-facing-language-standards.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [Interface Design Standards](../../standards/interface-design-standards.md)
  require learner-first status, protected outcome, safe next action, accessible
  technical detail, theme parity, and no implementation-language leakage.
- [Decision Readiness](../../adr/decision-readiness.md) is ready for this
  read-only shared-core Guidance boundary. Organization tenancy, managed-cloud
  controls, external execution, providers, recovery guarantees, and commercial
  policy are not exercised.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Guidance-owned exact feature-condition registry, protected API, generated client, and bounded recovery explanations | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add optional limitation text and actions independently to each feature error response | yes, but duplicates cross-feature safety meaning and expands several feature contracts | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 11 |
| C. Map feature errors to Help topics and recovery copy only in the browser | no; the browser becomes guidance authority and headless clients cannot discover the same meaning | - | - | - | - | - | - | - |
| D. Build a live health/diagnostic service that inspects modules and executes remediation commands | no; it crosses ownership, secret, operational-command, managed-cloud, and guarantee boundaries | - | - | - | - | - | - | - |
| E. Generate troubleshooting with an AI model from errors or logs | no; provider, private-data, grounding, evaluation, authority, and fallback decisions are outside this CAP | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14 of 14 and is the smallest complete SLI-0084 outcome. It
centralizes reviewed safe explanatory meaning without centralizing runtime
state or feature policy, reuses the immutable Guidance and generated-client
architecture from SLI-0082/0083, and keeps the same API available headlessly.
Candidate B can show similar copy but distributes one safety contract across
feature owners and would require coordinated feature-version churn for an
editorial explanation. Candidates C through E are ineligible because they make
the browser, operational introspection, or an AI model an unaccepted authority.

This refinement preserves the CAP-0020 outcome, four-slice manifest, ordering,
risk posture, and material-change boundaries. It adds no slice, external
effect, durable decision, provider/model call, remediation command, or lower-
level approval.

## Boundary Path

1. Existing feature/domain/application code remains authoritative for exact
   status, version, authorization, retry, idempotency, availability, and state.
2. Additive `feature-guidance/v1` schemas define an exact safe Guidance record
   and exact surface-condition mapping with closed action kinds and exact
   platform-Help references.
3. Pure Guidance values validate records and mappings, bind canonical source
   fingerprints and exact Help topic identities, compute canonical digests, and
   atomically admit one immutable checked-in registry.
4. A Guidance application operation reads one exact mapping and record. The
   protected API authorizes before access, accepts only closed public condition
   facts, and maps bounded unavailable/not-found failures without revealing the
   registry or rejected input.
5. Reviewed OpenAPI generates the shared TypeScript client. Feature adapters
   request only their closed surface/condition/version after the owning public
   result is already known; they do not send exception text or private state.
6. A reusable optional explanation renders server-owned status/reason/protected
   outcome and closed next actions beside the owning feature status. It can
   open exact Help but cannot invoke a feature write or operational command.
7. Focused and isolated qualification compares browser and ordinary headless
   records, exact condition/source/topic correlation, denial, restart,
   read-only containment, accessibility, no outbound access, and cleanup.

## Contracts, Data, and Provenance

`feature-guidance/v1` is additive, immutable, and read-only. An exact record has
a stable `guidance_id` and semantic `guidance_version`; a closed status class;
learner-readable heading, reason, protected-or-uncertain outcome; zero or more
bounded safe action descriptors; exact Help topic references; applicability;
publication facts; canonical-source references; and a canonical digest.

A mapping has one safe `surface_key`, public `condition_key`, semantic
`mapping_version`, and exact record identity. It contains no HTTP status, route,
URL, exception, internal enum, component, repository path, learner identity,
request body, provider/model payload, command, or mutable feature state.
Mapping changes publish a new exact version; exact reads never choose `latest`
or substitute a different condition.

Action kinds are closed presentation intentions such as retry the unchanged
feature request, reload current feature state, return to a safe owning page,
open one exact Help topic, or download an inert artifact for learner-managed
use. The record supplies no arbitrary destination, command string, promise of
success, automatic side effect, or credential requirement. The owning feature
remains responsible for whether an action is currently safe and available.

The starter registry is checked-in immutable product data correlated to the
already admitted Help corpus. It persists no learner or runtime data. Browser
and headless consumers use the same protected operation, while all feature
records, error envelopes, databases, and write/retry contracts remain
unchanged.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Exact reviewed guidance | An authorized client reads a supported surface, condition, and exact mapping version | One closed record returns with exact identity, safe actions, source facts, topic references, and digest | contract/domain/API |
| Missing exact version | A known surface/condition uses an absent mapping version | No newer or different condition is substituted; the feature's existing safe status remains usable | domain/API/component |
| Lesson version unavailable | An exact lesson version cannot be opened | The learner sees that no other version was substituted and can return safely without a record change | component/Chromium |
| Uncertain practice write | A save or submission response is unavailable after dispatch | Guidance preserves the existing same-request retry/reload rule and never claims whether the write committed | component/browser/live |
| Saved source stale or unavailable | A retained note/bookmark points to changed or absent source content | Learner-owned work remains visible; guidance explains that source access, not saved content, is unavailable | component/browser |
| Inert Project artifact | A learner views an admitted notebook, code, data, or result artifact | Guidance states that the platform does not execute or actively render it and offers only safe download/external-use meaning | contract/component/browser |
| AI-help execution boundary | A learner enables `on_request` or sees AI help unavailable | Guidance states that the choice alone enables no provider/model call or data egress and never substitutes a provider | contract/component/browser |
| Authorization confidentiality | Session or Guidance permission is missing | Access fails closed without record counts, conditions, topics, sources, private input, or rejected-key disclosure | API/security |
| Malformed registry | A duplicate, dangling, stale, command-bearing, arbitrary-destination, guarantee-bearing, unsafe, unknown-field, or digest-mismatched record is loaded | Complete admission fails before any partial guidance becomes visible | schema/domain/composition |
| Browser/headless parity | Equivalent authorized clients request each integrated exact condition | Both receive equivalent ordered public records and safe failure meaning | generated client/API/live |
| Optional Guidance failure | Guidance is missing, denied, stale, malformed, or unavailable | The owning feature retains its original status and safe action; no substitute guidance or blocked primary task appears | component/Chromium |
| Flexible valid registry | Record/action/topic counts and ordering, safe copy, added valid mappings, feature data, themes, viewport, zoom, forced colors, and motion vary | Required meaning and actions remain reachable without fixed prose, fixture count, pixel, or incidental-layout assumptions | property/component/Chromium |
| Restart, containment, and cleanup | Browser and headless reads run before and after normal local restart | Meaning is stable, requests stay loopback-only and read-only, feature state does not change, and only bounded artifacts are removed | live/architecture |

## Agent Work Packets

Packet identifiers are reserved and packets are authored one at a time
immediately before each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0174](../work-packets/WRK-0174-freeze-feature-guidance-contracts-and-registry.md) | Freeze `feature-guidance/v1`, pure validation/digests, reviewed starter records/mappings, exact Help correlation, compatibility fixtures, and focused anti-rigidity tests | SLI-0083 | none | complete |
| [WRK-0175](../work-packets/WRK-0175-compose-feature-guidance-api.md) | Compose the immutable registry, Guidance application/public operation, authorization, reviewed OpenAPI, generated client, and failure tests | WRK-0174 | none | complete |
| [WRK-0176](../work-packets/WRK-0176-deliver-bounded-feature-explanations.md) | Add the optional generated-client explanation to the five named feature conditions with plain language, safe actions, fallback, accessibility, and anti-rigidity evidence | WRK-0175 | none | active |
| Live qualification | Prove browser/headless parity, condition/source/topic integrity, denial, restart, loopback-only reads, feature-state containment, and exact cleanup | bounded feature explanations | none | planned |

Sequential delivery is required because all seams share Guidance contract,
registry, generated-client, feature integration, and live-runner surfaces. A
bounded correction may add a dependent packet inside this slice without renewed
CAP authority.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; pure record/mapping identity,
validation, canonical-digest, exact-topic correlation, whole-registry
admission, and varied-valid-shape tests; Guidance composition and protected API
success/not-found/denial tests; reviewed OpenAPI and generated-client
reproduction; focused feature model/component tests; and Chromium keyboard,
axe, light/dark, narrow, 200-percent-text, forced-color, reduced-motion,
optional-failure, and unchanged-request retry checks.

Also run one isolated browser plus ordinary headless flow with normal restart,
non-loopback observation, read-only feature-state comparison, and cleanup;
architecture/import, source-authority, active-content, privacy, advice-language,
AI-authority, learner-language, design-system, documentation, planning,
dependency, Python/TypeScript, zero-warning lint, build, whitespace,
controller-selected exact-candidate verification, and aggregate readiness.

Tests protect status meaning, uncertainty, safe actions, confidentiality,
exact identity, accessibility, and ownership. They do not freeze whole prose,
record/action counts, incidental ordering outside the contract, layout pixels,
or optional styling.

## Rollback and Migration

No database, learner-state, or feature-state migration is required. An
unexposed registry/API/UI change can roll back together. Once a public record
or mapping identity is exposed, successors follow additive compatibility and
exact-version rules. Feature status remains usable when Guidance is absent, so
removing an optional explanation does not block the owning task or change its
write/retry behavior.

## Stop Conditions

Stop for ambiguity in a feature's public status, retry/idempotency or exact-
version semantics; Help becoming feature, operational, support, provider, AI,
security, or policy authority; a breaking feature/public contract; raw/private
diagnostics; arbitrary destinations or commands; automatic remediation;
provider/model execution or substitution; external content/support;
availability, recovery, performance, legal, regulatory, tax, or financial
guarantees; personalized advice; active artifact rendering/execution; new
identity, tenancy, managed-cloud, queue, encryption, recovery, commercial, or
public-hosting behavior; stale CAP authority; ownership collision; or material
CAP-0020 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix it in bounded scope or route optional presentation polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will reconcile the Guidance resource/contribution rules, feature-
guidance contract and compatibility guidance, protected API/OpenAPI/generated
client, affected Web feature behavior, local runtime and architecture
assurance, known gaps, this slice, its packets, CAP-0020, and the planning
register.

Completion evidence must identify exact candidates and receipts; record,
mapping, source, and topic identities; browser/headless parity; authorization
and confidentiality; each integrated condition and fallback; uncertain-write
meaning; restart/offline-local behavior; loopback-only observation; read-only
containment; accessibility; anti-rigidity; cleanup; compatibility impact;
unsupported profiles; residual gaps; and CAP-package conformance. Local
authority and technical-disposition records remain ignored.

## Planning History

- 2026-10-18: Refined just in time after SLI-0083 completed. Candidate A scores
  14 of 14 and establishes one Guidance-owned, exact, transport-neutral
  limitation/recovery projection over existing public feature conditions. The
  CAP-0020 outcome, four-slice manifest, ordering, risk posture, and material-
  change boundaries remain unchanged; no slice-level approval is required.
- 2026-10-18: Activated WRK-0174 from clean base `85fa074` after confirming the
  completed SLI-0083 dependency, current CAP authority, bounded contract/core
  scope, and no unresolved decision or coordination collision.
