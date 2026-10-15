---
id: WRK-0042
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0017
capability: CAP-0001
depends_on: ["WRK-0005", "WRK-0034", "WRK-0040"]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/planning/capabilities/CAP-0001-complete-structured-introductory-lesson.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0017-qualify-complete-introductory-lesson-loop.md", "docs/planning/work-packets/WRK-0042-reconcile-capability-acceptance.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0042:80dd570e-22c3-484e-8c98-3403965f7d00
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T17:13:46Z
---

# Agent Work Packet: Reconcile Capability Acceptance

## Objective and Deliverable

Reconcile every CAP-0001 acceptance criterion against the delivered first-loop
evidence, record an exact cumulative qualification trace with honest limits,
and close SLI-0017 and CAP-0001 without changing runtime behavior.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the planning, testing, assurance,
security, operations, learning, and interface context; CAP-0001; SLI-0001,
SLI-0015, SLI-0016, and SLI-0017; their completed qualification packets;
ADR-0005 through ADR-0009; the Assessment, Content, Curriculum, Identity,
Learner-model, and Audit contracts and module maps; the current API/client,
browser, static-build, and live-composition evidence; and the nearest README
for every inspected boundary.

## Decisions and Assumptions

This is a cumulative evidence and lifecycle packet. It consumes the unchanged
approved CAP package and already delivered private-host `single_profile`,
synchronous replay, PostgreSQL, generated-client, and static-browser behavior.
Fresh qualification may reuse current evidence while the corresponding product
candidate remains unchanged. It adds no decision, contract, schema, runtime,
dependency, recovery, or deployment claim.

## In Scope

- Trace each CAP-0001 acceptance criterion to direct contract, application,
  PostgreSQL, API, generated-client, browser, live, architecture, security,
  design, documentation, and readiness evidence.
- Re-run the fixed aggregate and planning/documentation checks after lifecycle
  reconciliation, and repeat narrower checks only if the qualified candidate or
  its evidence sources changed.
- Record supported and unsupported profiles, assumptions, residual risks,
  cleanup, and exact cumulative results.
- Close SLI-0017 and CAP-0001 only after every manifest slice and this packet
  are complete and their terminal planning state is internally consistent.

## Out of Scope

Product code, contracts, schemas, migrations, generated clients or assets,
dependencies, new test behavior, built-in/OIDC or multi-user identity,
organization tenancy, queue guarantees, background delivery, backup/restore
automation, managed cloud, production roles, non-Chromium claims, mastery,
adaptation, recommendations, credentials, or financial advice.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Acceptance trace | CAP criteria and completed slice/packet evidence | CAP-0001 | Record exact cumulative evidence and limitations |
| Slice closure | SLI-0017 scenarios and verification route | SLI-0017 | Record packet result and deterministic closure |
| Packet evidence | Current qualification results | This packet | Preserve an auditable final handoff |
| Planning index | CAP, slice, and packet lifecycle | Register | Keep terminal state discoverable and consistent |

## Contracts and Interfaces

No contract or interface changes. Acceptance consumes the immutable lesson
package, protected placement, deterministic Assessment v1 definition and
evidence chain, versioned completion event, Audit references, rebuildable
Learner-model projection, protected completion response, generated client, and
accessible lesson route exactly as delivered.

## Dependencies and Parallel Safety

WRK-0005 qualifies the exact lesson-read path, WRK-0034 qualifies deterministic
knowledge-check evidence, and WRK-0040 qualifies replay and retained completion.
All manifest slices are complete except this cumulative slice. The packet owns
the shared CAP lifecycle and is not parallel-safe with other CAP-0001 work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact lesson open | Approved package and authorized learner context | Protected route opens | Exact objectives, sources, version, digest, and publication provenance are visible | SLI-0001 evidence |
| Deterministic check | Exact definition and one valid response | Submission completes | Stable score, bounded feedback, and one provenance-rich attempt chain result | SLI-0015 evidence |
| Retained completion | Completed learner closes and reopens | Completion source replays | Same bounded history and source-set identity return without mastery meaning | SLI-0016 evidence |
| Failure safety | Identity, version, replay, tamper, storage, or projection input is invalid | Focused and cumulative checks run | Access or mutation fails closed without false completion or disclosure | backend/API/security evidence |
| Boundary integrity | Module and adapter checks run | Ownership is evaluated | Public seams and shared core remain intact | architecture/static-build evidence |
| Accessible education | Reviewed browser flow runs | Themes, reflow, keyboard, focus, forced colors, and axe are checked | Equivalent educational content and action remain available without advice claims | component/Chromium/live evidence |
| Honest closure | All exact evidence is reconciled | CAP lifecycle closes | Only qualified private-host behavior is claimed and every unsupported profile remains explicit | CAP/SLI/register plus readiness gate |

## Verification Commands

Run the packet and slice planning validators, completion gate, planning and
documentation checks, aggregate readiness against the CAP base revision, and
`git diff --check`. Reuse unchanged fresh backend, web, Chromium, live Docker/
PostgreSQL/Python, architecture, security, design, build, client, OpenAPI, and
dependency evidence; rerun any layer whose candidate changed.

## Documentation and Evidence Update

Update only this packet, SLI-0017, CAP-0001, and the planning register. Record
exact counts and environments, candidate stability, cleanup, supported and
unsupported profiles, residual gaps, and absence of product or contract drift.

## Stop Conditions

Stop if a CAP acceptance criterion lacks direct evidence; any current fixed
gate fails for a product or control defect; the candidate changed without its
narrow verification being repeated; closure would overstate identity,
tenancy, recovery, queue, cloud, browser, production-role, mastery, advice, or
performance coverage; or a durable decision or material CAP revision appears.

## Required Handoff

Return the criterion-by-criterion CAP acceptance trace, exact cumulative check
results, candidate and documentation impact, supported and unsupported
profiles, residual gaps, lifecycle closure, commit identifier, local
fast-forward result, and next workflow-routed CAP.

## Capability Acceptance Trace

| CAP-0001 criterion | Direct evidence | Result |
| --- | --- | --- |
| Exact approved lesson and provenance | Content/Curriculum contract and API tests, generated-client currency, component and live lesson-open scenarios | Passed for `intro-risk-return@1.1.0`; objectives, sources, semantic version, digest, and publication provenance remain exact |
| Exact deterministic assessment resolution | Assessment contract/application/PostgreSQL/API tests and live submission | Passed without `latest` substitution; malformed and unsupported definitions fail before evidence creation |
| Stable score, feedback, and idempotency | Assessment domain/application/PostgreSQL tests and browser submission | Passed with one deterministic attempt/evidence chain and conflict-safe retries |
| Provenance-rich retained evidence | Assessment event, Audit reference, Learner-model projection, completion API, and live reopen evidence | Passed with learner context, version/digest, event, attempt, evidence, score, source-set, and time references; provider/storage internals remain excluded |
| Rebuildable non-mastery completion | Learner-model replay/rebuild tests and two consecutive live reloads | Passed with stable source-set identity and no second response form, mastery, competency, or certification claim |
| Safe denial and failure handling | Identity, version, tamper, replay, partial-store, and interrupted-rebuild tests plus live missing-context/stale-placement scenario | Passed fail closed with no false completion, silent substitution, cross-learner disclosure, or invalid last-known-state replacement |
| Module ownership and dependency direction | Eight architecture fitness functions and module contract tests | Passed across Content, Curriculum, Assessment, Learner model, Identity, Audit, adapters, and generated-client boundaries |
| Shared core and explicit adapter qualification | Static production build, Python same-origin host, PostgreSQL stores, architecture checks, and assurance documentation | Passed for private-host `single_profile`; built-in/OIDC, multi-user, managed-cloud, background delivery, production roles, and recovery guarantees remain unqualified |
| Accessible equivalent interface | Component and eight-scenario Chromium suite covering light/dark axe, keyboard/focus, reflow, reduced motion, and forced colors, plus live browser flow | Passed for reviewed Chromium profile; manual screen-reader and non-Chromium qualification remain open |
| Educational—not advice—meaning | Contract/UI assertions, copy review, security and assurance checks | Passed without mastery, certification, personalized advice, suitability, or investment-performance meaning |

## Verification Progress

- The cumulative candidate is unchanged after WRK-0040: no product source,
  contract, schema, migration, generated client, static asset, dependency, or
  executable test changed in this packet. Fresh results therefore remain
  directly applicable to the same Git candidate.
- The complete backend suite passed 196 tests under Python 3.14.3 against an
  isolated PostgreSQL 18.4 container. The complete web suite passed 26 tests in
  six files, the focused Chromium lesson suite passed eight scenarios, and the
  live same-origin flow passed two scenarios against disposable PostgreSQL and
  the repository-managed Python environment, including two consecutive
  completion reloads with the same source-set digest.
- OpenAPI and the generated TypeScript client were current. Node 24 typecheck,
  lint, and production build passed; npm audit reported zero vulnerabilities.
  The live host served static index SHA-256
  `15ea50af1f57d2b0c6dee25277e49d80440c6b6ba7796be8a2a5e42dd60164ef`.
- Architecture passed eight fitness functions, security passed ten control
  groups, and design validation verified 125 tokens and 56 icons. The fixed
  readiness gate passed all 27 checks after the bounded WRK-0041 anti-rigidity
  correction; the exact disposable test containers and temporary build output
  were removed.
- Every CAP criterion above has direct evidence and all four manifest slices
  are terminal or closing through this packet. No decision, contract, runtime,
  recovery, identity, tenancy, cloud, queue, commercial, or external-execution
  gate appeared. Residual limits remain the explicitly excluded profiles and
  community-host recovery posture, not incomplete approved scope.

## Planning History

- 2026-10-15: Authored as the single evidence-only packet for the final
  approved CAP-0001 manifest slice. It adds no runtime behavior, decision, or
  material package change.
- 2026-10-15: Reconciled all ten CAP acceptance criteria to unchanged direct
  evidence and found no missing approved scope or new decision gate.
- 2026-10-15: Completed after planning, documentation, and diff checks passed;
  the terminal slice gate remains responsible for SLI and CAP closure.
