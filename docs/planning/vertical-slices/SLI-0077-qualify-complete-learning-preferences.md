---
id: SLI-0077
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-18
parent: CAP-0018
depends_on: [SLI-0074, SLI-0075, SLI-0076]
decision_gates: []
---

# Vertical Slice: Qualify Complete Learning Preferences

## Outcome and User Scenario

An authorized learner can use the complete delivered preference system through
browser or headless clients and can trust each preference family to keep its
own meaning, ownership, failure behavior, history, reset, and download. A
failure or malformed record in one family does not grant authority, change
learning evidence, or prevent the other valid preference families and ordinary
learning from working.

## Scope Boundaries

### In Scope

- Cumulative qualification of the learner goals, experience, and interests;
  accessible display preferences; AI-help preference; browser theme; and
  browser-local reminder preference delivered by SLI-0074 through SLI-0076.
- Browser and ordinary headless use of the three existing protected generated
  public API families without backend-internal imports or browser-only meaning
  in the headless contract.
- Cross-family isolation for save, exact retry, conflict, bounded history,
  reset, download, malformed data, service unavailability, persistence
  restart, and unrelated learner state.
- Evidence that explicit preferences remain advisory learner input and never
  become identity, authorization, Assessment evidence, competency, grading,
  deterministic eligibility, financial suitability, provider admission,
  model-execution permission, or notification authority.
- Cumulative privacy, accessibility, plain-language, light/dark, responsive,
  provenance, replay, persistence, cleanup, and anti-rigidity evidence.
- Deployment-neutral contract and shared-core semantics suitable for local and
  future cloud profiles; operational managed-cloud qualification is excluded.

### Out of Scope

- A new combined profile, settings endpoint, aggregate export/import format,
  synchronization protocol, or compatibility manifest. CAP-0019 owns portable
  composition across modules.
- New preference fields, inferred traits, behavioral profiling, recommendation
  logic, adaptive-learning policy, model/provider execution, notification
  delivery, queues, schedules, or autonomous actions.
- Managed-cloud deployment, organization tenancy, enterprise identity,
  recovery objectives, cloud-provider selection, or production operation.
- Replacing the separate learner-owned, platform-owned, and browser-local
  authorities with one persistence model or atomic cross-authority mutation.
- Optional visual polish, copy churn that does not change meaning, or another
  human approval stage for slice, packet, review, or completion work.

## Canonical Context and Decisions

- [CAP-0018](../capabilities/CAP-0018-set-learning-goals-and-preferences.md)
  defines the approved four-slice outcome and makes this the cumulative final
  increment.
- [SLI-0074](SLI-0074-record-learning-goals-experience-interests.md),
  [SLI-0075](SLI-0075-set-accessible-display-preferences.md), and
  [SLI-0076](SLI-0076-control-ai-help-and-local-reminders.md) define the
  delivered contracts, ownership boundaries, clients, interfaces, and focused
  evidence this slice qualifies together.
- The [Learner Preferences Contract](../../architecture/contracts/learner-preferences-contract.md),
  [Learner Presentation Preferences Contract](../../architecture/contracts/learner-presentation-preferences-contract.md),
  and [Learner Assistance Preferences Contract](../../architecture/contracts/learner-assistance-preferences-contract.md)
  govern the three separate public API families.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  owns explicit learner choices in Learner model and keeps platform and local
  display settings outside that module.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md)
  supplies the opaque current learner context; preference requests cannot
  select another learner.
- [ADR-0013](../../adr/ADR-0013-explicit-model-provider-opt-in.md) keeps model
  providers disabled until separate provider, model, permission, and execution
  controls are satisfied.
- [Local and Cloud Deployment Parity](../../architecture/deployment/local-cloud-capability-parity.md)
  requires one shared core and adapter-owned deployment differences.
- [Decision Readiness](../../adr/decision-readiness.md) permits qualification
  inside the accepted local shared-core boundary. Managed-cloud, tenancy, and
  provider operations remain outside this slice.
- [Interface Design Standards](../../standards/interface-design-standards.md)
  and [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern the cumulative browser journey without turning style heuristics into
  brittle functional gates.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cumulative cross-family qualification of existing APIs and local adapters | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| Add a combined settings API and aggregate export | yes, but overlaps CAP-0019 and adds avoidable compatibility surface | 1 | 1 | 2 | 0 | 1 | 1 | 1 | 7 |
| Qualify a managed-cloud deployment | no; cloud, tenancy, security, and recovery decisions remain outside CAP-0018 | - | - | - | - | - | - | - | - |
| Close from prose and isolated unit suites only | no; omits cumulative live, restart, headless, and cross-family isolation evidence | - | - | - | - | - | - | - | - |

## Selection Rationale

The cumulative qualification candidate is the only complete and decision-ready
final increment. It exposes no new product contract and instead proves that the
three public API families and two browser-local settings coexist without
authority leakage, shared-failure coupling, hidden execution, or browser-only
assumptions. It preserves API-first use for a future headless AI mode while
keeping the local-only meanings out of that API.

The combined-endpoint candidate would duplicate existing generated clients and
preempt CAP-0019's portable-record composition. Managed-cloud qualification
would cross unresolved operational decisions. Isolated evidence alone would
not satisfy the CAP's cumulative acceptance. SLI-0074 through SLI-0076 are now
complete, so SLI-0077 is dependency-eligible and scores 14 of 14.

This refinement preserves the approved CAP-0018 outcome, four-slice manifest,
sequence, non-goals, and decision posture. It needs no slice-level approval.

## Boundary Path

1. The authorized learner establishes the current opaque learner session.
2. An ordinary headless client independently reads and changes the three
   protected learner preference families through their generated public API
   contracts.
3. The browser uses those same generated clients and separately reads theme
   and local-reminder settings through their platform-owned local adapters.
4. Changing or resetting one preference family advances only that family's
   revision, history, digest, and export; the other families remain unchanged.
5. Exact retries converge, while stale revisions, changed-key reuse, unknown
   fields or values, and caller-selected identity fail closed without partial
   cross-family writes.
6. Malformed or unavailable data in one family produces its conservative
   fallback or bounded error without making another family unavailable and
   without blocking ordinary learning.
7. Restart and reload demonstrate the documented durability boundary for each
   server-owned or browser-local setting.
8. Cumulative evidence confirms that no preference mutates evidence,
   competency, grading, eligibility, financial state, model execution,
   notification delivery, or another module's owned persistence.

## Contracts, Data, and Provenance

No new public product schema is introduced. The three existing learner-owned
contract families retain independent profile IDs, revisions, canonical times,
digests, mutation intents, bounded histories, resets, and exports. Their
records share only the opaque authorized learner context; they do not form an
atomic aggregate and one family cannot carry fields belonging to another.

Theme and local reminder records remain browser-local, versioned envelopes
behind platform-owned adapters. They contain no learner identity, server
revision, provider permission, evidence, or headless meaning. Downloads remain
separate and accurately identify whether a record is portable learner data or
state from the current browser.

Qualification evidence records the exact candidate revision, selected checks,
runtime topology, contract versions, and pass/fail result without copying
private learner content into tracked artifacts. Existing versioned schemas and
provenance remain authoritative; this slice creates no aggregate source of
truth.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Headless API parity | An ordinary non-browser client can read, mutate, inspect history, reset, and export each learner-owned family through protected public APIs | contract/API/live runner |
| Browser parity | Browser routes perform the same learner-owned operations through generated clients while local settings stay behind local adapters | generated client/component/Chromium |
| Cross-family save isolation | Saving one family changes only its own profile, history, digest, and persistence rows | application/PostgreSQL/live runner |
| Cross-family reset isolation | Resetting one family restores only its documented default and does not reset another family or either local setting | application/local adapter/Chromium |
| Exact retry and conflict isolation | Exact retry converges; stale revision and changed-key reuse write nothing in any family | application/API/PostgreSQL |
| Malformed-family containment | An invalid server response or local envelope falls back or reports unavailability for that family while valid families and ordinary learning remain usable | unit/component/Chromium |
| Service-family containment | An unavailable preference request does not manufacture defaults as saved state, grant authority, or block unrelated learning and local settings | component/live network isolation |
| Local boundary | Theme and reminder choices never appear in public learner APIs, headless output, learner persistence, or Assessment evidence | schema/architecture/security |
| No policy authority | Preferences do not change identity, authorization, evidence, competency, grading, eligibility, financial suitability, provider admission, model execution, or notification delivery | architecture/integration/live state fingerprint |
| Restart and reload | Server-owned preferences survive host restart; browser-local settings survive page reload only in the same browser storage boundary | PostgreSQL/Chromium/live runner |
| Privacy and portability | Separate exports contain their exact documented data and no credentials, prompts, financial account data, hidden traits, or unrelated family values | contract/security/component |
| Flexible valid data | Closed values, generated identifiers and times, bounded zero-through-100 histories, and varied surrounding learner content work without fixed fixture counts or ordering | contract/unit/live anti-rigidity |
| Accessible cumulative journey | All settings remain understandable and operable with keyboard, focus, narrow reflow, zoom, forced colors, reduced motion, and light/dark/device themes | component/Chromium/design |
| Exact cleanup | Qualification removes only its isolated database, browser, server, and generated runtime artifacts | live runner/operations |

## Agent Work Packets

Packet identifiers are reserved and authored immediately before work starts.
The expected dependency-ordered seam is:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0164 | Add only the minimum cross-family assertions or harness support needed, run cumulative browser/headless/live qualification, reconcile evidence, and close CAP-0018 | WRK-0150, WRK-0156, WRK-0161 | none | complete |

The packet may reuse existing complete qualification runners and tests. It must
not duplicate them merely to create new files. Detailed file scope, generated
artifacts, selected checks, and stop conditions are frozen at packet start.

## Verification and Qualification

Run the existing preference contract, compatibility, domain, application,
PostgreSQL, API, generated-client, local-adapter, component, Chromium,
architecture, security, privacy, and migration checks selected from the actual
affected files. Extend them only where cumulative cross-family behavior lacks
observable evidence.

The final live journey must exercise browser and ordinary headless paths in one
isolated production-like topology, include all three public preference
families and both local settings, capture source-state noninterference before
and after mutations, verify exact replay and conflicts, restart the server,
reload the browser, and clean up exactly. Run documentation, planning,
dependency, Python, TypeScript, zero-warning lint, build, exact-candidate
affected verification, one independent technical review, deterministic slice
and CAP completion structure, and `python dev-tools/agent/check_ready.py`.

Tests should assert contracts, ownership, behavior, and required language—not
incidental whitespace, fixture counts, full-copy snapshots, styling details,
or internal implementation order. A bounded inconsequential correction does
not reopen a full review cycle.

## Rollback and Migration

This slice adds no public schema, migration, or aggregate durable state by
default. Any minimal harness or test correction is removable without changing
learner data. Existing additive preference migrations and versioned local
envelopes retain the rollback rules established by their delivering slices.

If qualification exposes a functional defect, route the smallest correction
to a descendant packet under the owning slice when it remains within CAP-0018.
Do not delete or reinterpret retained preferences to make qualification pass.
Material new behavior or a breaking contract returns the CAP to shaping.

## Stop Conditions

Stop for a new combined API or export; breaking preference schema; caller-
selected learner identity; direct cross-module storage; browser state used as
server authority; hidden or inferred profiling; preference values used as
evidence, authorization, grading, eligibility, financial suitability, provider
permission, model instruction, notification permission, or irreversible
action; managed-cloud or tenancy implementation; provider/model execution;
external notification delivery; destructive migration; stale CAP approval;
active write collision; or material CAP-0018 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count or order, or an advisory readability
signal. Fix bounded inconsequential issues locally or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will reconcile the CAP, this slice, its packet, the planning register,
known verification gaps, and any affected preference or deployment-parity
documentation. It will not create a redundant combined contract.

Completion evidence must name the exact candidate, affected boundaries, checks
and live topology; confirm browser/headless public-API parity and independent
local adapters; show cross-family failure and state isolation; report restart,
cleanup, privacy, accessibility, and readiness results; and list residual gaps.
The CAP closes only when the four approved slices cumulatively satisfy the
CAP-0018 acceptance scenarios.

### Completion Evidence

- WRK-0164 completed on exact candidate
  `5f19dc72b8e9c7529bd76dbf927d65c10dcd17de` with qualifying receipt digest
  `sha256:13336f2f84c056a16825239ad00259e2343b49a2700b6c899f84a85b91a2e43b`.
- One live isolated topology exercised all three protected learner-preference
  API families through browser and headless clients plus both browser-local
  adapters. Named-family changes left both non-target families exact, all
  server-owned state survived restart, and subsequent headless reads were
  zero-write.
- The final three profiles share one opaque learner context and retain distinct
  identities, schemas, revisions, histories, and exports. Theme and reminders
  remain local to the browser and do not appear in public learner data.
- Failure, replay, conflict, concurrency, privacy, accessibility, unrelated-
  state containment, and exact cleanup passed without adding a combined API or
  changing product contracts. The complete focused and aggregate check set is
  recorded in WRK-0164.
- Managed-cloud operation, organization tenancy, multi-module portable
  import/export, and a future headless AI mode remain explicit later work. No
  material CAP-0018 drift or unresolved decision gate remains.

## Planning History

- 2026-10-18: Refined the final approved manifest increment after SLI-0074,
  SLI-0075, and SLI-0076 completed. Deterministic selection found cumulative
  cross-family qualification eligible at 14 of 14. A combined API would overlap
  CAP-0019, managed-cloud work remains outside current decisions, and isolated
  evidence alone is insufficient. The refinement preserves CAP-0018 and
  requires no slice-level approval.
- 2026-10-18: Authored WRK-0164 just in time as the single cumulative
  qualification seam. It reuses the existing complete topology and adds only
  missing cross-family isolation evidence before deterministic CAP closure.
- 2026-10-18: Completed SLI-0077 after its one packet proved cumulative
  browser/headless API parity, local-adapter separation, cross-family isolation,
  restart durability, containment, accessibility, and cleanup on a qualifying
  exact candidate. No product or contract expansion was required.
