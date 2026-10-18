---
id: WRK-0179
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0085
capability: CAP-0020
depends_on: [WRK-0178]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "backend/src/financial_ai_academy/modules/guidance/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/capabilities/CAP-0020-understand-platform-methods-and-limitations.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0085-qualify-platform-help-quality.md", "docs/planning/work-packets/WRK-0179-qualify-platform-help-cumulatively.md"]
generated_artifacts: []
base_revision: 230fcad08c129ce7334a89e6ed6445ee9e3d1ef6
claim_id: WRK-0179:7021f2cd-0bd0-4439-865a-8091b43cda2a
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T07:27:08Z
---

# Agent Work Packet: Qualify Platform Help Cumulatively

## Objective and Deliverable

Close SLI-0085 and CAP-0020 with reproducible cumulative evidence that the
delivered Platform Help, contextual Help, and feature guidance remain current,
exact, safe, accessible, deterministic, available offline in the local profile,
and equivalent for browser and ordinary headless clients. Run the existing
focused and complete local topology rather than adding a permanent heavyweight
gate to every contribution, reconcile direct architecture/runtime/contributor
claims, and record exact-candidate evidence and honest residual gaps.

This packet is evidence and documentation only. It must not add or change a
public operation, schema, Guidance record, search policy, browser behavior,
database, identity rule, provider/model behavior, or deployment topology.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered routed
Guidance, API/security/testing/deployment/interface and planning context; the
change-impact matrix and decision-readiness register; CAP-0020; completed
SLI-0082 through SLI-0084; active SLI-0085; completed WRK-0178; all Guidance
contracts, registries, API/client/browser consumers and tests; the quality gate;
the approved-lesson runner and replay suite; architecture verification,
residual gaps, direct consumer READMEs, and nearest contributor instructions.

CAP-0020 authority remains current, WRK-0178 is complete with no open technical
finding, and no durable decision applies. This is the final seam already
enumerated by SLI-0085 and requires no lower-level approval.

## Decisions and Assumptions

- The checked-in immutable Guidance registries, protected public operations,
  generated client, local single-profile identity, and disposable local
  topology are the accepted qualification surface.
- Offline local evidence means a normally restarted loopback-only host serves
  checked-in Guidance without non-loopback requests; it is not an operating-
  system firewall or production availability claim.
- Existing focused suites remain direct evidence for schema, safe rendering,
  owning-feature fallback, and accessibility. The complete topology supplies
  browser/headless equality, restart, read-only containment, and cleanup.
- Heavy browser/live qualification runs for this closure packet and remains
  available to affected work; the fast WRK-0178 command is the routine
  contributor gate so valid Help edits do not inherit an unnecessary full
  environment barrier.

## In Scope

- Run the Guidance quality command and its anti-rigidity tests, all Guidance
  unit/contract/source-binding checks, active-content/privacy/security checks,
  and exact generated-client/OpenAPI reproduction.
- Run Web unit/component/contract tests, TypeScript, zero-warning lint,
  production build, and focused Platform Help Chromium for safe rendering,
  keyboard/focus, themes, narrow/200-percent-text-equivalent reflow, forced
  colors, reduced motion, and automated accessibility.
- Run the complete isolated approved-lesson topology for every exact topic,
  context, and feature resolution through browser and fresh headless sessions;
  confidential denial; normal restart without reseeding; loopback-only GETs;
  non-Identity database containment; and success/failure cleanup.
- Confirm source-authority freshness, complete internal link graphs,
  deterministic search/pagination/filter behavior, varied valid additions,
  optional Guidance failure, and no fixed starter count/prose/layout contract.
- Run architecture, documentation, planning, design, dependency, compilation,
  whitespace, controller-selected exact-candidate, independent technical, and
  aggregate readiness checks.
- Reconcile only direct Guidance, Web, local-runtime, assurance, CAP/slice,
  packet, and register claims with executed evidence and residual gaps.

## Out of Scope

- Product, schema, API, generated-client, runtime Guidance, Web behavior,
  database, migration, dependency, identity, authorization, or topology edits.
- New Help topics, contexts, feature mappings, sources, learner conditions,
  search ranking, UI presentation, or provider/model behavior.
- Remote content, external link crawling, semantic retrieval, AI quality
  judgment, hosted support, public binding, managed cloud, production load,
  RPO/RTO, backup/recovery product claims, or non-Chromium certification.
- Styling and optional copy polish suitable for CAP-0031.
- New tenancy, licensing, queue, encryption, legal, commercial, external-
  execution, personalized-advice, or financial-policy decisions.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance/Web/runtime | implementation, contracts, generated client, focused and live tests | direct READMEs only | Reconcile usage and evidence without product change |
| Architecture assurance | verification matrix and known gaps | direct Guidance rows/gaps | Record qualified boundary and honest exclusions |
| Planning | CAP-0020, SLI-0085, this packet, register | lifecycle and evidence sections | Close the approved package deterministically |

No implementation, contract, resource, fixture, test, generated build,
dependency, migration, design token, or unrelated documentation path is
writable. A discovered functional defect must be routed to a bounded dependent
packet before this packet can close.

## Contracts and Interfaces

1. The routine quality result remains `guidance-quality-report-v1` over
   repository-only `source-authority-v1`, production adapters, and exact search
   cursors.
2. Public browser and headless clients continue to use only the reviewed
   Platform Help, contextual Help, and feature-guidance API operations and
   generated client.
3. Complete exact public documents, ordering, source/publication facts,
   canonical digests, denials, and safe failures must be equivalent before and
   after normal restart.
4. Browser Guidance traffic must be GET-only and loopback-only; the Guidance
   phase must leave every non-Identity database schema unchanged.
5. Rendering remains inert typed nodes with closed same-origin topic links and
   feature-owned safe actions. No active content, arbitrary URL/command, raw
   diagnostic, provider payload, or learner data is accepted.
6. Evidence may record safe counts, digests, command/check identities, result
   status, and bounded paths. It must not record cookies, credentials, learner
   identifiers, private payloads, absolute temporary paths, or approval/reviewer
   data in tracked artifacts.

## Dependencies and Parallel Safety

WRK-0178 is complete and supplies the fast source/graph/search gate and
affected-selection integration. This packet owns final Guidance assurance,
direct READMEs, CAP/slice closure, and the register, so it is not parallel-safe
with another writer on those files. It must begin from a clean base with one
exclusive exact-file lease.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Current complete graph | Checked-in canonical sources and all three registries | Focused quality and contract suites run | Every binding, digest, exact link, resolution, and full browse traversal qualifies | quality/unit/contract |
| Safe accessible rendering | Reviewed and malformed responses plus supported presentation states | Unit/component and focused Chromium suites run | Valid meaning/actions remain reachable; unsafe/partial/private content does not render | component/Chromium/security |
| Browser/headless parity | Equivalent authorized sessions | Complete local topology reads all Guidance | Ordered public documents, sources, digests, and failures are equivalent | live API/browser |
| Confidential denial | Session is missing or invalid | Clients request Guidance | Access fails without registry, key, source, digest, or rejected-input disclosure | API/live/security |
| Offline normal restart | The loopback local host restarts without reseeding | Browser and headless clients reread Guidance | Exact meaning is stable and no non-loopback request occurs | live/architecture |
| Read-only containment | Guidance-only phase runs | Database fingerprints are compared | Every non-Identity schema remains unchanged | live/PostgreSQL |
| Flexible integration | Corpus count/order/prose and valid references vary within contracts | Quality/property suites run | Valid extensions pass without fixed starter, prose, pixel, or incidental-order assumptions | anti-rigidity tests |
| Cleanup | Focused or full qualification succeeds or fails | Finally paths run | Only bounded snapshots, captures, browser output, containers, network, and test roots are removed | live/control plane |

## Verification Commands

- `python dev-tools/guidance/test_guidance_quality.py`
- `python dev-tools/guidance/check_guidance_quality.py --json`
- `python dev-tools/control-plane/check_feature_guidance.py --root . --mode feature-guidance`
- `python dev-tools/control-plane/check_platform_help.py --root . --mode platform-help-browser`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode unit`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode typecheck`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode lint`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode build`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode generated`
- `python tests/e2e/approved-lesson/test_replay_qualification.py`
- `python dev-tools/control-plane/check_approved_lesson.py --root . --mode live`
- `python dev-tools/architecture/check_architecture.py`
- `python tests/architecture/test_approved_lesson_boundaries.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Use the repository-pinned Node 24/npm 10.8.2, Python environment, Chromium, and
Docker composition for Web and live commands. Controller verification runs
against one clean exact candidate. No external production qualification is
authorized or claimed.

## Documentation and Evidence Update

Update the direct Guidance, Web, local-runtime, architecture-verification, and
known-gap sources with exact qualified meaning and explicit exclusions. Record
the exact candidate and receipt, focused and cumulative checks, parity,
accessibility, safe failure, restart, no-outbound observation, database
containment, cleanup, migration/rollback status, residual gaps, and CAP
conformance in this packet and SLI-0085. Move CAP-0020 to complete only after
the slice completion gate passes. Keep approval and technical-disposition data
only in ignored local ledgers.

## Stop Conditions

Before implementation, consume the reserved ID, commit this packet, claim it
from the clean commit, run `packet-start`, and acquire one exclusive lease for
the declared files.

Stop for a functional, security, accessibility, confidentiality, parity,
restart, containment, or cleanup failure that requires an implementation/test/
contract/resource change; conflicting canonical authority; a required public
contract break; external retrieval, provider/model authority, hosted support,
new identity/persistence/topology behavior; stale CAP authority; ownership
collision; or material CAP-0020 drift. Route a bounded defect to a dependent
packet inside SLI-0085; return to CAP shaping only for material package change.

Do not stop or reopen review solely for harmless whitespace, optional copy,
valid fixture count/order, nonfunctional styling, generated values, or another
inconsequential issue. Fix documentation locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0085.WRK-0179`; exact candidate and receipt; source/graph/
search qualification; safe rendering and accessibility; browser/headless and
restart equality; denial, loopback-only/read-only containment, and cleanup;
focused and cumulative checks; documentation impact; rollback/migration status;
assumptions; unsupported profiles; residual gaps; and any unresolved decision.
Confirm that CAP-0020 and SLI-0085 completion gates passed without changing
public Guidance, learner/feature state, identity, provider/model, external
action, or financial authority.

## Execution Evidence

- The repository-only quality result qualified 10 canonical sources, 8 topics,
  4 contexts, and 5 feature mappings/records. Its five anti-rigidity tests also
  qualified valid additions and failed stale, missing, absolute, escaped,
  duplicated, unknown, malformed, dangling, and reordered-invalid inputs.
- All 90 feature-guidance checks, 29 Web test files with 507 tests, TypeScript,
  zero-warning lint, production build, reviewed OpenAPI/generated-client drift,
  focused Platform Help Chromium, architecture, security, design, planning,
  documentation, and whitespace checks passed. Vite's informational chunk-size
  advisory does not change function or delivery evidence.
- The complete isolated topology passed all 87 replay tests and every focused
  Chromium journey. It reproduced all topics, four contexts, and five feature
  resolutions through authenticated browser and fresh ordinary HTTP sessions;
  preserved exact digests and confidential denial across normal restart;
  observed only loopback GET Guidance traffic; preserved every non-Identity
  schema; and completed disposable stopped-source backup/restore, populated-
  target refusal, restored-session revocation, source isolation, and cleanup.
- No product, contract, schema, client, runtime, state, identity, provider,
  model, migration, or external-action behavior changed in this packet. The
  exact controller candidate, qualifying receipt, independent technical
  disposition, aggregate readiness, and completion gates remain to be bound
  after this evidence reconciliation is committed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0178 completed. This final seam
  uses focused and existing full-topology evidence for CAP closure without
  adding a heavyweight routine gate, product behavior, or lower-level approval.
- 2026-10-18: Claimed from clean base `230fcad` with one bounded owner and the
  declared documentation/evidence scope after revalidating current CAP
  authority and completed dependencies.
- 2026-10-18: Cumulative focused and live qualification passed without a
  functional defect or decision gate; reconciled direct contributor, runtime,
  architecture-assurance, and residual-gap claims before exact-candidate
  submission.
