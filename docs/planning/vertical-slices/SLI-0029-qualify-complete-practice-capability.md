---
id: SLI-0029
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: CAP-0006
depends_on: ["SLI-0026", "SLI-0027", "SLI-0028"]
decision_gates: []
---

# Vertical Slice: Qualify the Complete Practice Capability

## Outcome and User Scenario

An authorized learner can open one exact versioned practice activity, answer
its supported structured items, save and resume partial work, submit and receive
deterministic source-backed feedback, follow approved review material, retry
within the visible formative policy, and inspect immutable attempt evidence
after interruption or restart. Browser and non-browser clients use the same
protected public API and the same domain/application core.

This final CAP-0006 increment produces cumulative release evidence for that
complete journey and closes only gaps discovered by the qualification. It does
not create a second product workflow, duplicate earlier tests mechanically, or
turn optional wording, styling, fixture counts, timestamps, IDs, or response
ordering into new functional requirements.

## Scope Boundaries

### In Scope

- Map every CAP-0006 acceptance statement to direct contract, domain,
  application, real-PostgreSQL, API, generated-client, browser, live,
  architecture, security, accessibility, or recovery evidence.
- Run the complete practice-focused matrix from immutable definition and
  answer-safe presentation through submission, draft/retry/history/review,
  normal restart, projection rebuild, and browser/headless parity.
- Reproduce reviewed OpenAPI and generated-client artifacts and prove that the
  browser consumes the generated public client while an ordinary supported
  non-browser session consumes the same operations without UI internals.
- Inspect success, malformed, unauthorized, stale, replay, conflict, attempt-
  limit, concurrency, rollback, interrupted-rebuild, unavailable-review,
  accessibility, and cleanup paths with privacy-minimized evidence.
- Verify exact provenance, immutable attempt/event history, server-owned
  identity/time/revision/order/eligibility, deterministic grading, answer
  confidentiality, and shared-core module ownership.
- Keep anti-rigidity evidence explicit: valid item, option, reference, response,
  history, and attempt-limit variation remains supported; semantically
  unordered responses and selections remain order-insensitive; harmless copy
  and nonfunctional style differences do not block capability closure.
- Reconcile only documentation, verification maps, known gaps, planning state,
  and bounded qualification controls made stale by the cumulative result.
- Close SLI-0029 and CAP-0006 deterministically when all acceptance evidence is
  current, with no new human approval below the CAP package.

### Out of Scope

- New item or scoring families, partial credit, weighting, free text, files,
  notebooks, code, arbitrary expressions, external item banks, or proctoring.
- AI-authored questions, model/manual grading, mastery or competency inference,
  adaptive ranking, personalized recommendations, engagement optimization, or
  personalized financial guidance.
- A separate AI endpoint, browser-specific backend, agent protocol, tool-
  calling surface, autonomous authority, or duplicate headless application
  core. Future AI clients may reuse the public API qualified here.
- Organization tenancy, built-in/OIDC qualification, managed-cloud deployment
  or recovery, queue/broker selection, provider execution, notifications,
  background outbox delivery, or a cloud-specific domain fork.
- Styling-only polish that does not impair function, meaning, accessibility,
  responsive behavior, or theme parity. Optional cleanup remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0006](../capabilities/CAP-0006-practice-and-demonstrate-understanding.md)
  defines the complete practice outcome, acceptance contract, and final
  qualification increment.
- [SLI-0026](SLI-0026-open-versioned-practice-activity.md),
  [SLI-0027](SLI-0027-submit-and-score-practice-attempt.md), and
  [SLI-0028](SLI-0028-resume-retry-and-compare-practice-attempts.md) supply the
  complete implemented behavior and their focused evidence.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md) requires one shared
  domain/application core across deployment profiles.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  separates Content, Curriculum, Assessment, Learner model, and Audit authority.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
  governs immutable package and structured assessment-definition meaning.
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
  bounds community evidence and recovery claims to the private host.
- [Assessment contract](../../architecture/contracts/assessment-contract.md)
  keeps authorization, validation, grading, evidence, retry, and replay
  deterministic and server-owned.
- Decision readiness is sufficient for cumulative provider-neutral private-host
  qualification. Tenancy, managed-cloud controls, external providers, model
  authority, and adaptive learning remain constrained or decision-required and
  are not activated.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Reuse focused evidence, run one cumulative API-first matrix, close only material gaps, and record a CAP acceptance map | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add a new meta-runner that reruns every repository check without acceptance mapping or gap ownership | yes | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 10 |
| C. Build a separate headless or AI practice API to prove non-UI operation | no - it duplicates the accepted public API and crosses the CAP boundary | - | - | - | - | - | - | - |
| D. Qualify one managed-cloud deployment and recovery profile | no - provider, tenancy, encryption, and recovery decisions remain unresolved | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the only complete conforming refinement and scores 14/14. It
produces the approved observable outcome, uses current contracts and evidence,
and keeps any correction tied to a concrete acceptance gap. Candidate B is
eligible but duplicates work, consumes more time, and provides weaker evidence
meaning because an undifferentiated green suite does not show which capability
claim it owns. Candidate C would create the duplicate core the user explicitly
wants avoided. Candidate D crosses unresolved cloud authority. Candidate A
wins without a tie-break and does not materially change the CAP package.

## Boundary Path

1. The qualifier starts from the immutable approved practice definition and
   exact Curriculum placement already delivered by SLI-0026.
2. Contract and application suites validate every supported response shape,
   deterministic grading, exact version resolution, denials, provenance,
   idempotency, retry rules, review selection, and replay/rebuild semantics.
3. Real PostgreSQL suites validate atomic evidence, conditional drafts,
   migration, concurrency, rollback, attempt ordering, source preservation,
   and interrupted projection replacement.
4. The reviewed OpenAPI snapshot and generated TypeScript client reproduce
   exactly. Browser and ordinary cookie-backed clients traverse the same
   protected presentation, submission, progress, and draft operations.
5. The isolated local live workflow exercises save/reload, submission,
   feedback, targeted review, retry/history, exact replay, stale conflict,
   restart without reseeding, accessibility, confinement, and cleanup.
6. Architecture, security, language, design, documentation, planning, build,
   and readiness gates verify shared-core and user-interface boundaries.
7. A cumulative evidence map records direct, representative, and intentionally
   unqualified claims. Only a concrete material gap returns to a new bounded
   packet; inconsequential cleanup is fixed locally or deferred to CAP-0031.
8. When the map satisfies CAP acceptance, SLI-0029 and CAP-0006 close
   deterministically and the completed CAP branch is fast-forwarded to main.

## Contracts, Data, and Provenance

No new product contract, table, event, route, provider port, migration, or
generated-client shape is planned. Qualification consumes the accepted
practice-definition, submission/result, completion-event, draft-save,
retry-state, review-target, history, session, and error contracts. It treats
response-array and multiple-selection order according to their canonical
semantics rather than byte order.

Evidence must retain exact package, definition, practice, item, scoring,
attempt-policy, result, event, projection-source, review-resource, schema, and
tool versions or digests. Reports remain categorical and privacy-minimized;
they do not retain learner identity, cookies, credentials, responses, answer
keys, private evaluator declarations, storage details, or raw diagnostics.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Complete learner journey | The authorized learner opens, saves, resumes, submits, reviews, retries, and inspects retained attempts through exact public versions | live Chromium/API/PostgreSQL |
| Structured contract closure | Every supported item/response type has versioned compatible schemas, deterministic scoring, and malformed/unsupported denials | contract/domain/application |
| Deterministic evidence | Valid submission produces reproducible ordered feedback and one atomic append-only aggregate; failed or stale work creates no contradictory evidence | application/PostgreSQL/API |
| Replay and interruption | Exact save/submission replay is stable; stale replacement conflicts; restart and projection rebuild preserve accepted meaning and prior complete state | PostgreSQL/API/live |
| Retry and history | Variable immutable limits, final-slot concurrency, gap-free order, answer-free history, and retained prior attempts remain server-authoritative | domain/PostgreSQL/browser |
| Targeted review | Latest incorrect-item references resolve in declaration order, unavailable mappings degrade safely, and no ranking/mastery/advice claim is introduced | Curriculum/API/browser |
| Confidential denial | Unauthorized, malformed, stale, conflict, unavailable, and exhausted paths expose only the closed public error contract | API/security/live |
| API/headless parity | Generated browser and supported non-browser clients use the same presentation, submission, progress, and draft operations with no private imports | OpenAPI/client/architecture/live |
| Accessible equivalent views | Purpose, instructions, responses, saved state, feedback, review, retry, and history retain keyboard/focus/live-region/reflow/theme/forced-color/reduced-motion meaning | component/Chromium/design |
| Shared-core and recovery bounds | Module ownership and deployment-neutral core remain intact; private-host restart is direct evidence while managed-cloud recovery stays explicitly unqualified | architecture/live/documentation |
| Anti-rigidity | Compatible counts, ordering, metadata, timestamps, generated IDs, plain wording, and nonfunctional styles do not become accidental acceptance constraints | focused mutation tests/review |
| Containment and cleanup | Qualification uses one isolated topology, leaves no unbounded process/container/artifact, and reports no secret or personal identifier | runner/architecture/live |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0108 | Run the cumulative capability matrix, close only directly observed acceptance gaps, reconcile the evidence map and known gaps, and deterministically close SLI-0029 and CAP-0006 | SLI-0028 | none | active |

The packet is authored immediately before activation. If qualification finds a
material product defect, WRK-0108 stops and a new bounded correction packet is
reserved inside this slice rather than hiding product work in the evidence map.

## Verification and Qualification

Run the complete practice contract/domain/application/API and real-PostgreSQL
suites; migration, concurrency, rollback, replay/rebuild, and module-boundary
checks; OpenAPI and generated-client reproduction; all web unit/component tests;
TypeScript typecheck, lint, and build; focused mocked and live Chromium practice
flows; and the isolated approved-lesson PostgreSQL/Python/headless/Chromium
workflow. Run focused harness anti-rigidity and containment tests, security,
learner-language, design-system, documentation, planning, whitespace, exact-
candidate affected verification, independent technical review, completion
structure, and the fixed aggregate readiness gate.

Reuse current exact evidence when its candidate and affected boundary remain
unchanged. Rerun a check when the qualification packet changes that boundary or
when freshness is necessary to close a claim. Do not force an unrelated full
rerun merely to produce a newer timestamp.

## Rollback and Migration

The selected work is qualification and documentation unless it finds a bounded
defect. It adds no planned migration or public contract. Rollback removes only
new qualification assertions and evidence documentation; delivered practice
behavior remains intact. Any discovered persistence correction must preserve
accepted attempts/events and follow a separately bounded forward-compatible
packet rather than destructive rollback. Ephemeral test state is deleted only
inside the isolated qualifier.

## Stop Conditions

Stop for a new item/scoring/policy family; changed CAP outcome, slice manifest,
or acceptance boundary; model/manual grading; adaptive/mastery authority;
external or arbitrary execution; provider, queue, tenancy, encryption, cloud,
or managed-recovery choice; breaking public contract; destructive evidence
handling; cross-module persistence access; duplicate browser/headless core;
private answer or learner leakage; stale CAP binding; active write collision;
or inability to prove qualification isolation.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, one incidental fixture count/order, or another
inconsequential correction. Fix it locally within scope or defer optional
polish to CAP-0031.

## Documentation Impact and Completion Evidence

Reconcile CAP-0006, the architecture-verification map, known verification gaps,
affected module and deployment guidance, SLI-0029, WRK-0108, and the planning
register. Completion evidence must map every CAP acceptance statement to an
owning exact check; identify changed paths and boundaries; record contract and
migration compatibility; distinguish direct local evidence from unqualified
cloud/provider behavior; state checks not performed; and identify assumptions,
residual risks, and follow-up work.

The final evidence must state that public APIs remain directly usable by future
headless and AI consumers while no separate AI mode, agent protocol, autonomous
authority, provider, cloud profile, or external execution was planned or added.

### Qualification Result

Every SLI-0029 acceptance scenario has direct passing evidence. The cumulative
focused backend matrix passes 218 contract, deterministic-core, and protected-
API checks. The unchanged WRK-0107 real-PostgreSQL matrix passes 220 checks, and
its isolated live PostgreSQL/Python/public-API/headless/Chromium qualification
passes ten scenarios at exact candidate `5706f9a94df400e2858bd524a1557062d9e01d41`.
The approved-lesson harness passes 39 tests plus four parameterized subtests.

The web matrix passes 210 tests across 15 files; TypeScript typecheck, lint,
reviewed generated-client reproduction, production build, and 11 focused
Chromium practice journeys pass. Architecture passes 16 tests, security passes
10 control groups, and learner-language, design, documentation, planning,
whitespace, and all 29 aggregate readiness checks pass. The exact supported
practice API remains authoritative for both generated browser traffic and
ordinary authenticated non-browser HTTP; no duplicate headless core exists.

No product source, contract, API, schema, migration, generated client, UI,
provider, deployment composition, or harness changed in this qualification
packet. The architecture-verification and known-gap maps remain truthful as
written. Managed-cloud behavior, tenancy, providers, background delivery,
model grading, adaptive/mastery authority, arbitrary execution, a separate AI
mode, and autonomous action remain explicitly unqualified.

## Planning History

- 2026-10-16: Refined the final CAP-0006 manifest increment after SLI-0026
  through SLI-0028 completed. Candidate A scores 14/14 and uses an evidence-
  first cumulative matrix with one bounded packet. It preserves the shared
  API-first browser/headless core, reuses still-current exact evidence, and
  avoids duplicate meta-infrastructure or inconsequential acceptance gates.
- 2026-10-16: Activated WRK-0108 after validating current CAP membership,
  completed dependencies, decision readiness, the documentation-only write
  scope, implementation gate, and collision-free ownership.
- 2026-10-16: The cumulative SLI-0029 matrix passed with no product or harness
  defect. The slice has one documentation-only exact candidate ready for
  submission before deterministic completion.
