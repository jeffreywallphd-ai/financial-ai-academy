---
id: WRK-0173
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0083
capability: CAP-0020
depends_on: [WRK-0172]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/assistance-preferences.e2e.ts", "apps/web/tests/browser/approved-lesson/platform-help.e2e.ts", "backend/src/financial_ai_academy/modules/guidance/README.md", "deployments/local/README.md", "dev-tools/control-plane/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0083-open-contextual-method-and-limitation-help.md", "docs/planning/work-packets/WRK-0173-qualify-contextual-help-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: 5fcd3f170bf6b3cd367696871d9d8ef943695766
claim_id: WRK-0173:f702184a-1eea-4c51-a37e-f47be1e60717
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T05:18:59Z
---

# Agent Work Packet: Qualify the Contextual Help Live Flow

## Objective and Deliverable

Close SLI-0083 with reproducible evidence that the exact contextual Help map
works through the same protected Guidance API for generated-browser and
ordinary headless HTTP clients. Exercise the four delivered feature contexts,
their ordered exact topic references, safe return behavior, source and digest
correlation, authorization, normal restart, offline-local operation,
accessibility, read-only containment, anti-rigidity, and cleanup through the
existing disposable PostgreSQL, Python host, static build, and pinned Chromium
topology.

This packet adds qualification evidence only. It does not change product
behavior, public contracts, context/topic meaning, feature authority, identity,
persistence, provider/model behavior, or financial authority.

## Required Context

Before implementation, revalidate every applicable `AGENTS.md`,
`docs/README.md`, the routed architecture-contract, API/security,
testing-quality, deployment-operations, interface-design, and delivery-planning
context, the change-impact matrix, decision readiness, CAP-0020, SLI-0083,
completed WRK-0170 through WRK-0172, contextual/platform Help contracts and
Guidance sources, generated client and feature links, the approved-lesson
runner and pure replay tests, assurance sources, and nearest READMEs.

The Required Startup was performed and reported before this planning change.
The CAP package remains approved, WRK-0172 is complete, and no unresolved
durable decision applies. Stop for conflicting authority, stale CAP authority,
an ownership collision, or material CAP/slice drift.

## In Scope

- Extend the approved-lesson Help journey so its authenticated browser context
  reads all four exact maps and referenced topics through the public API, then
  correlate that cumulative evidence with WRK-0172's focused feature-link and
  safe-return browser evidence.
- Record one closed contextual capture containing only public context and topic
  documents, exact ordered identities, versions, digests, safe purposes, and
  expected source/publication facts.
- Extend the Python runner with strict capture validation, fresh cookie-backed
  headless exact-context and exact-topic reads, confidential denial,
  browser/headless equivalence, read-only containment, normal restart equality,
  non-loopback request observation, and finally-path cleanup.
- Add pure qualification tests for closed capture shape, topic/context digest
  correlation, varied valid reference counts and order, safe return paths,
  denial, restart equality, containment, non-loopback refusal, and bounded-path
  cleanup.
- Regenerate the static browser artifact and reconcile direct Web, Guidance,
  local-runtime, architecture-assurance, known-gap, and planning documentation.

## Out of Scope

- Product, contract, schema, context registry, corpus, application, API,
  OpenAPI, generated-client, identity, permission, session, dependency,
  migration, persistence, deployment-composition, or design-system changes.
- New Help contexts or meanings, browser-owned mappings, fallback substitution,
  external links/content, semantic search, personalization, analytics,
  authoring, AI generation, learner evidence, grading, eligibility,
  recommendation, suitability, or financial action.
- A substantive product correction discovered by qualification; route it to a
  separately bounded dependent packet without weakening evidence.
- Operating-system firewall isolation, public hosting, managed cloud,
  production load or availability, recovery guarantees, multi-browser
  certification, or a separate headless-AI mode.

## Expected File and Boundary Impact

| Boundary | Allowed change | Evidence target |
| --- | --- | --- |
| Live Chromium | approved-lesson Help journey | Four exact feature contexts and topics through the browser session, correlated with focused link/return evidence, keyboard/accessibility, and no non-loopback Help traffic |
| Existing assistance containment | approved-lesson assistance assertion only | Permit the optional exact contextual GET while retaining the no-unapproved-write rule |
| Live orchestration | approved-lesson runner | Browser/headless parity, denial, restart, containment, cleanup |
| Pure qualification | approved-lesson replay tests | Closed capture, varied-valid references/order, restart and path safety |
| Static browser | `apps/web/dist` generated output | Qualify the exact accepted candidate |
| Direct guidance | listed Web, Guidance, runtime, assurance, and known-gap Markdown | Match claims to executed evidence and exclusions |
| Planning | this packet, SLI-0083, and register | Deterministic completion projection |

No unlisted product, contract, registry, corpus, schema, migration, generated-
client, dependency, shared-design, deployment-composition, or planning file is
writable.

## Contracts and Interfaces

Browser and headless qualification consume only the established local session,
exact contextual Help, and exact platform topic reads:

```text
POST /api/v1/session/single-profile
GET  /api/v1/guidance/contextual-help/{context_key}/versions/{context_version}
GET  /api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}
```

The session bootstrap establishes only server-owned context. Help operations
remain GET-only. The capture excludes cookies, credentials, learner IDs,
permissions, local paths, Git metadata, approval/review data, repository bytes,
arbitrary diagnostics, model/provider data, and feature state. Complete response
equality is required for identical inputs, with semantic equality across normal
restart.

## Dependencies and Parallel Safety

WRK-0172 is complete and supplies the generated-client feature links. This
packet owns the shared approved-lesson journey, runner, static build, assurance
sources, and SLI-0083 closure paths, so it is not parallel-safe with another
writer on those surfaces. Claim from a clean recorded base, acquire one-owner
leases for every write-scope path, complete it before dependent work, and keep
approval/reviewer records only in ignored local control-plane storage.

## Decisions and Assumptions

- The accepted local identity, deterministic Guidance, checked-in immutable
  corpus/registry, and provider-disabled boundaries are sufficient.
- Contextual Help remains optional, read-only explanation. Missing Help cannot
  block the underlying feature or reinterpret its state.
- Offline-local evidence means the checked-in data remains available through a
  normally restarted loopback host while Help observation reports no
  non-loopback request; it is not an operating-system isolation claim.
- Existing focused feature/browser suites remain the reusable affected checks;
  the live runner provides cumulative integration evidence.

## Acceptance Scenarios

| Scenario | When | Then | Evidence |
| --- | --- | --- | --- |
| Four feature contexts | Authenticated browser context reads every delivered exact map and topic while focused suites exercise each link | Server label, purpose, exact topic identity/version, and safe same-origin return evidence remain correlated | Chromium/capture/focused suites |
| Browser/headless parity | Fresh HTTP client repeats each exact read | Ordered public context/topic meaning and digests match without browser imports | runner/public HTTP |
| Source and digest integrity | Contexts and referenced topics are compared | Context digest, topic digest, publication facts, and source fingerprints are internally exact | runner/focused tests |
| Authorization confidentiality | Session is missing or invalid | Exact context and topic reads deny without labels, counts, identities, sources, or rejected input | HTTP/security |
| Optional failure isolation | Contextual Help is unavailable or absent | Underlying learner feature remains usable and no substitute topic is invented | focused/live evidence |
| Restart and offline-local | Host restarts normally after initial parity | Identical checked-in meaning remains available and Help made no non-loopback request | restart/network observation |
| Read-only containment | Browser and headless Help phases finish | No feature, evidence, preference, permission, provider/model, or financial state changes | runner/architecture |
| Accessible flexibility | Context counts/order, feature state, themes, viewport, zoom, forced colors, and motion vary | Required meaning/actions remain reachable without fixed prose, count, pixel, or incidental-layout assumptions | Chromium/axe/pure tests |
| Closed evidence | Capture is missing, extra, private, stale, inconsistent, or path-escaping | Verification fails before comparison or mutation | pure pytest |
| Cleanup | Qualification succeeds or fails | Only named topology, capture, browser artifacts, build, and bounded temporary root are removed | runner/finally |

## Verification Commands

Run packet and planning validation; pure capture/restart tests; contextual and
platform Help contract, Guidance domain/application/API/source-binding suites;
OpenAPI and generated-client reproduction; full Web unit/component/contract
tests, typecheck, zero-warning lint, build, and focused feature Chromium checks;
the existing platform-Help focused Chromium wrapper; and the complete isolated
approved-lesson workflow.

Also run architecture/import/source-authority, security/privacy/active-content,
advice-language and AI-authority, learner-language and design-system,
documentation, planning, dependency, Python compilation, whitespace,
controller-selected exact-candidate verification, independent technical review,
deterministic slice closure, and `python dev-tools/agent/check_ready.py`. Record
only passing evidence and always execute exact cleanup.

## Documentation and Evidence Update

Record the exact candidate and receipt; four feature contexts; focused and live
browser/headless parity; source/publication/digest integrity; denial; safe
returns and optional-failure isolation; non-loopback observation; restart;
read-only containment; accessibility; anti-rigidity; cleanup; checks;
assumptions; unsupported profiles; and residual gaps. Update only the direct
sources in `write_scope`, and keep approval/reviewer records untracked.

## Stop Conditions

Stop for a required product, contract, schema, registry/corpus, OpenAPI,
generated-client, identity, dependency, feature, or deployment-composition
change; inconsistent browser/headless meaning; source/digest mismatch; unsafe
return or non-loopback Help request; durable feature-state mutation; private or
repository-path disclosure; provider/model execution; semantic search,
personalization, analytics, grading, eligibility, recommendation, financial
action, or unsupported guarantee; unisolated infrastructure; managed-cloud,
tenancy, recovery, licensing, legal, or commercial expansion; stale CAP
authority; collision; or material CAP-0020/SLI-0083 drift.

Do not stop or reopen review solely for whitespace, optional wording,
nonfunctional styling, generated values, fixture count/order, or another
inconsequential qualification correction. Fix it in bounded scope or defer
optional polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0083.WRK-0173`; exact candidate and receipt; four context
links; browser/headless parity; source and digest integrity; authorization;
safe returns and optional failure; non-loopback observation; restart;
read-only containment; accessibility; anti-rigidity; cleanup; focused/live/
security/architecture/aggregate checks; changed files; documentation impact;
assumptions; unsupported profiles; and residual gaps. Confirm no product,
contract, registry/corpus meaning, generated client, identity, persistence,
provider/model, external content/action, learner policy, or financial behavior
changed, then leave SLI-0083 closure-ready.

## Planning History

- 2026-10-18: Authored just in time after WRK-0172 completed. This is the
  smallest final qualification seam for SLI-0083 and reuses the established
  disposable Help topology without a new product decision or lower-level
  approval.
- 2026-10-18: The first isolated live pass reached contextual qualification and
  exposed one stale assistance-harness assertion that froze an exact GET count.
  Scope now includes only that assertion so optional exact Help rereads are
  admitted while every unapproved write remains forbidden.
- 2026-10-18: Whole-database diagnostics identified `learner_model` mutation
  when the live Help test revisited owning learner features. The live journey
  now keeps its containment window Guidance-only and correlates browser-session
  public reads with WRK-0172's focused feature-link evidence rather than
  weakening the read-only fingerprint or treating feature side effects as Help.
- 2026-10-18: Exact-candidate verification audit found that the controller
  selected the live topology but did not execute the packet's pure replay
  module. The bounded live runner now executes that module before starting
  infrastructure, so the already-selected exact-candidate check must prove
  replay and live qualification together without widening product scope.
