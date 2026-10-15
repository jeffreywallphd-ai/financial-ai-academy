---
id: WRK-0040
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: ["WRK-0039"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/README.md", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/modules/module-map.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/security/community-learner-evidence-protection.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0040-qualify-replay-and-completion-history.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0040:996ada4f-0fcd-4e86-9bda-5f7ff8c3eaf2
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T17:03:40Z
---

# Agent Work Packet: Qualify Replay and Completion History

## Objective and Deliverable

Qualify SLI-0016 cumulatively by proving a real private-host learner can submit
the approved knowledge check, close/reopen the statically built lesson, and see
the same retained completion reconstructed through Assessment, Audit, and
Learner model on PostgreSQL 18.4.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the planning, learning, interface,
testing, security, and operations context; CAP-0001; SLI-0016; WRK-0035 through
WRK-0039; ADR-0005, ADR-0006, ADR-0008, and ADR-0009; Assessment and lesson
contracts; first-loop module/public seams; local composition and live E2E
runner; existing architecture/security/assurance maps; production build; and
the nearest backend, web, deployment, and design-system README files.

## Decisions and Assumptions

Qualification uses the accepted private-host `single_profile` path,
synchronous replay, the reviewed static client, and disposable PostgreSQL 18.4.
It makes no queue, background delivery, recovery, non-Chromium, built-in/OIDC,
managed-cloud, or production-role claim. Static output is regenerated from the
reviewed source and generated API client; exact changed artifact files receive
leases before the tracked build runs.

## In Scope

- Extend the live approved-lesson browser scenario to reload after submission,
  verify exact retained provenance and no replacement form, reload again, and
  prove the source-set identity remains stable.
- Run focused and cumulative contract, backend, web, browser, architecture,
  security, design, documentation, planning, dependency, build, and aggregate
  readiness checks, including disposable Docker/PostgreSQL qualification.
- Regenerate tracked production assets and verify the Python same-origin static
  host serves the exact built application without a Node production server.
- Reconcile canonical module, Assessment, assurance, security, web, slice, and
  register statements with the delivered evidence and preserve every genuine
  unsupported-profile or recovery gap.

## Out of Scope

Background workers or delivery guarantees, backup/restore implementation,
retention automation, production database roles, built-in/OIDC or cross-user
identity, non-Chromium browsers, managed-cloud deployment, multi-item or retake
assessment behavior, mastery/adaptation, and any production deployment or push.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser qualification | Approved lesson success/denial scenarios and runner | Listed E2E spec | Prove close/reopen against real composition and stores |
| Static build | Vite inputs and current tracked artifacts | `apps/web/dist` generated files | Publish source-current reviewed browser assets |
| Canonical architecture/contracts | Assessment consumption and module map | Listed documents | Remove delivered gaps without changing domain meaning |
| Assurance/security | Direct evidence and retained limitations | Listed maps/posture | State exactly what ran and what remains unqualified |
| Web documentation | Route and verification boundary | Web README | Record live completion-history ownership |
| Planning | Packet, slice, and register | Listed artifacts | Record exact cumulative evidence and deterministic closure |

## Contracts and Interfaces

Consume the unchanged Assessment v1 completion event, Learner-model projection,
Audit reconciliation, completion HTTP/OpenAPI client, and lesson browser
contracts. The live assertion must show package and definition digests, score,
bounded meaning, source event/attempt/evidence references, and a stable
source-set digest after repeat reopen. It must not expose learner/provider IDs,
answers, feedback internals, Audit rows, storage details, mastery, advice, or
performance meaning.

## Dependencies and Parallel Safety

WRK-0039 and every earlier SLI-0016 packet are complete. This cumulative packet
owns the shared generated bundle and final slice evidence, so it is not
parallel-safe with any other work on this slice.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live close/reopen | Approved fixture and private learner complete the exact check | Browser reloads | Retained bounded completion and exact provenance replace the answer form | Docker/PostgreSQL/Python/Chromium E2E |
| Repeat reopen | Projection and Audit have already reconciled the event | Browser reloads again | Same source-set digest and one evidence chain remain visible | live E2E |
| Missing/stale context | Sessionless API or nonexistent placement is requested | Live route/API runs | It fails closed without lesson or completion disclosure/substitution | live E2E/API |
| Replay/idempotency | Source event is read repeatedly | Unit/integration suites run | Learner projection and Audit remain deterministic and duplicate-free | backend/PostgreSQL |
| Tamper/interruption | Invalid event, conflicting event, or rebuild failure occurs | Focused suites run | Last valid truth is preserved and false completion is not returned | contract/application/PostgreSQL/API |
| Static artifact | Source and generated client are current | Production build runs | Tracked bundle is reproducible and served by the Python same-origin host | build/architecture/live E2E |
| Complete verification | All slice boundaries are checked | Aggregate gates run | Exact results are recorded and genuine gaps remain explicit | packet/slice evidence |

## Verification Commands

Run packet validation and the implementation/completion gates; Assessment,
Learner-model, Audit, completion API, migration, and architecture tests; full
backend tests; OpenAPI/client currency; full web unit/component tests;
lesson-reading Chromium and live approved-lesson E2E; web typecheck, lint, and
production build; dependency audit; architecture, security, design-system,
documentation, planning, aggregate readiness, and `git diff --check`. Use the
supported Node 24 runtime and disposable Docker PostgreSQL 18.4 environment.

## Documentation and Evidence Update

Reconcile the listed canonical/assurance/security/web sources, SLI-0016, this
packet, and the register. Record exact counts, environments, the generated
artifact transition, failures and bounded fixes, cleanup, unsupported profiles,
recovery gaps, assumptions, residual risks, and CAP-package conformance.

## Stop Conditions

Stop if qualification requires a queue/delivery guarantee, new identity or
tenancy model, production credentials or deployment, recovery/support claim,
cross-module SQL, mutable evidence, mastery/advice interpretation, breaking
contract, unowned generated file, or material CAP change. A bounded test or
documentation defect remains local to this packet.

## Required Handoff

Return a slice closure decision with exact live and cumulative evidence,
artifact/docs impact, environment cleanup, supported and unsupported profiles,
residual gaps, CAP conformance, and the next manifest slice.

## Verification Progress

- The live same-origin success scenario now submits the approved
  `intro-risk-return@1.1.0` check, reloads into retained completion, verifies the
  exact package and definition digests plus source references, reloads again,
  and observes the same source-set digest with no second answer form. The
  missing-context/stale-placement scenario remains fail-closed. Both live
  Chromium tests passed against a disposable PostgreSQL 18.4 container, a
  restrictive temporary object root, and one Python same-origin process.
- The first live invocation used the shell's unprovisioned Python and stopped
  before application readiness on missing `psycopg`; the repository-managed
  Python 3.14 environment was selected. Its first test run then exposed an
  ambiguous digest selector because the same exact digest correctly appears in
  publication and completion provenance. Scoping the assertion to the
  completion-event article produced a clean two-scenario rerun without changing
  product behavior.
- The complete backend suite passed 196 tests under Python 3.14.3 against a
  separately isolated PostgreSQL 18.4 container, including every migration,
  contract, module, API, replay, tamper, interruption, and architecture test.
  The exact container was inspected and removed with its temporary volume after
  the run. The complete web suite passed 26 tests in six files; the focused
  lesson Chromium suite passed eight scenarios, including light/dark axe and
  retained-history reflow evidence.
- The reviewed OpenAPI snapshot and generated client were current. Node 24 web
  typecheck, lint, and the Vite production build passed. The tracked build now
  contains `index-DRKu1gri.css` and `index-DvdEp4wh.js` plus its source map and
  reviewed icon asset; the live Python host reported static index SHA-256
  `15ea50af1f57d2b0c6dee25277e49d80440c6b6ba7796be8a2a5e42dd60164ef`.
- Architecture passed eight fitness functions, security passed ten control
  groups, design validation verified 125 tokens and 56 icons, documentation
  verified 194 Markdown files plus catalogs, planning verified 70 artifacts,
  the dependency audit found zero vulnerabilities, and `git diff --check`
  exited successfully with line-ending warnings only in generated or installed
  files.
- The fixed aggregate readiness gate passed all 27 checks against base revision
  `515c2e16e4458b1305a89acd594085c828fe49ec`. Its sandboxed attempt had failed
  only because Windows denied temporary fixture repositories; the identical
  supported run outside that sandbox passed every planning, anti-rigidity,
  control-plane, portfolio, roadmap, documentation, and design check.
- Canonical module, Assessment, assurance, security, and web documentation now
  records the delivered synchronous replay/history path. Background delivery,
  recovery, production database roles, built-in/OIDC, non-Chromium browsers,
  managed cloud, broader Assessment families, mastery, and adaptation remain
  explicitly unqualified. No decision gate or CAP drift was found.

## Planning History

- 2026-10-15: Authored after WRK-0039 completed. The cumulative path uses the
  accepted synchronous replay and private-host runtime and introduces no new
  decision, contract meaning, or material CAP drift.
- 2026-10-15: Qualified the complete synchronous replay and retained-history
  slice across real PostgreSQL, Python same-origin serving, generated client,
  static build, Chromium, accessibility, security, architecture, documentation,
  planning, dependency, and aggregate readiness boundaries.
