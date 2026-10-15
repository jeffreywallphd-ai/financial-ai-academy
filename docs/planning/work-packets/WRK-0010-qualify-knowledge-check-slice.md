---
id: WRK-0010
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-08-05
parent: SLI-0002
capability: CAP-0001
depends_on: [WRK-0009]
decision_gates: []
parallel_safe_with: []
write_scope: [backend/tests, apps/web/package.json, apps/web/package-lock.json, apps/web/tests/browser/knowledge-check, apps/web/tests/browser/approved-lesson, tests/e2e/knowledge-check, deployments/local, .github/workflows/deterministic-knowledge-check-slice.yml, dev-tools/architecture, dev-tools/security, backend/README.md, apps/web/README.md, deployments/local/README.md, docs/domain/README.md, docs/architecture/modules/module-map.md, docs/architecture/contracts/assessment-contract.md, docs/architecture/contracts/content-package-contract.md, docs/architecture/assurance/architecture-verification.md, docs/architecture/assurance/known-architecture-gaps.md, docs/assurance/known-verification-gaps.md, docs/architecture/deployment/local-open-source-profile.md, docs/security/local-identity-architecture.md, docs/security/community-learner-evidence-protection.md, docs/context/packs/architecture-contracts.pack.md, docs/context/packs/learning-adaptation.pack.md, docs/context/packs/security-risk.pack.md, docs/context/packs/deployment-operations.pack.md, docs/context/packs/interface-design.pack.md, docs/context/packs/testing-quality.pack.md, docs/context/pack-catalog.json]
generated_artifacts: [apps/web/package-lock.json, apps/web/tests/browser/knowledge-check/**/*-snapshots/*.png]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Deterministic Knowledge-Check Slice

## Objective and Deliverable

Add the aggregate cross-boundary, architecture, security, accessibility,
static-runtime, and local-composition evidence needed to verify SLI-0002 as one
complete vertical slice. The observable deliverable is a reproducible private
loopback qualification path that starts disposable PostgreSQL, seeds the exact
successor package and placement, serves the Python API/static client, submits
the knowledge check through the generated client, and verifies the durable
Assessment evidence/outbox plus every named denial and failure boundary.

## Required Context

Before any file change, prominently read and follow every applicable
`AGENTS.md` and the repository-root `docs/README.md`. Route through the
baseline pack with `testing-quality` as primary and `security-risk` as
adjacent. Read SLI-0002 and WRK-0006 through WRK-0009 handoffs, SLI-0001's
qualification topology, ADR-0005 through ADR-0009, module/data/contract rules,
Assessment and content-package contracts, community evidence protection,
local/cloud parity, local profile, identity security, education-versus-advice,
interface/testing standards, architecture verification, current local runner
and server, CI workflows, dependency locks, all affected executable tests,
generated artifacts, and nearest READMEs.

## Decisions and Assumptions

- Qualification targets only the private-host community `single_profile`
  profile with loopback exposure, PostgreSQL, local filesystem content
  objects, Python API/static serving, and the exact static web build. It does
  not generalize to built-in/OIDC, multiple learners, remote/public hosting,
  managed cloud, production, or provider services.
- Correct and incorrect live scenarios use isolated databases/learner contexts
  so the one-completion rule remains authoritative. Tests never weaken or
  bypass production uniqueness/idempotency behavior.
- The live path seeds only committed synthetic fixtures through controlled
  local setup/public application seams. It contains no personal data,
  credential, provider payload, restricted dataset, or investment advice.
- Qualification inspects durable Assessment evidence and the pending outbox
  record directly only from test-owned adapters/fixtures. No production API
  exposes raw evidence, responses, correct answers, or event payloads.
- No outbox dispatcher, queue, worker, consumer, backup, or restore claim is
  required. The evidence is limited to atomic durable event creation suitable
  for later consumers.
- Existing one-command Git Bash/PowerShell development tooling remains the
  supported entry point. It must add the new checks and fixture without
  introducing a Node production server or unsafe cleanup of user-owned
  containers, processes, databases, or data roots.
- Automated accessibility supports but does not replace documented manual
  assistive-technology, actual zoom, non-Chromium, and non-Windows
  qualification.

## In Scope

- Cross-system correct and incorrect submissions from package admission,
  placement/definition resolution, single-profile session, API/OpenAPI,
  generated client, accessible UI, deterministic result, PostgreSQL evidence,
  and transactional outbox inspection.
- Live idempotent replay and bounded conflict/already-completed behavior with
  exact row/event-count assertions.
- Cross-boundary denials for missing/tampered/expired/revoked context,
  cross-origin mutation, malformed/unknown option, stale/mismatched versions,
  conflicting submission, database failure, private-answer leakage, unsafe
  feedback, and sentinel redaction.
- Architecture fitness functions for module public surfaces/direction, owned
  Assessment/Curriculum/Content tables, event ownership, generated-client-only
  browser access, no browser evidence storage, no backend imports from web,
  and no Node production/server entry point.
- Security checks for request authority, private definition/correct-answer
  separation, response/evidence redaction, no-store/cookie/Origin/Host policy,
  append-oriented mutation bounds, and synthetic fixture hygiene.
- Reproducible local seed/start/health/readiness/test/teardown integration with
  unique Compose project, unused ports, isolated database, and bounded ignored
  data root.
- Focused and live browser qualification across light/dark/system,
  keyboard/focus/status, narrow and 200-percent-equivalent reflow, reduced
  motion, forced colors, correct/incorrect/denial/failure states, advice copy,
  and zero automated accessibility violations.
- Deterministic CI orchestration and one-command local runner updates covering
  all predecessor checks plus slice-specific contract/backend/API/web/live,
  architecture, security, advisory, documentation, planning, design, and
  readiness gates.
- Canonical and derived documentation/evidence reconciliation based only on
  checks that directly pass.

## Out of Scope

- New product behavior, contract meaning, scoring rules, migrations, public
  APIs, UI patterns, tokens/icons, or broad refactoring of earlier packets.
- Event delivery/consumption, Learner-model/Audit implementation, history,
  resume, retakes, progress/mastery, recovery tools, remote/public operation,
  managed cloud, production publication, provider access, or external CI
  execution.
- RPO/RTO, high availability, recovery, cloud parity, compliance, mastery,
  certification, suitability, performance, or personalized-advice claims.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Aggregate backend evidence | All predecessor tests and migrations | `backend/tests/` | Add only missing cross-boundary and regression assertions |
| Browser/live evidence | Focused browser tests and SLI-0001 live pattern | Named browser roots and `tests/e2e/knowledge-check/` | Complete generated-client/browser/PostgreSQL path |
| Local qualification | Existing server, seed, runner, compose, cleanup | `deployments/local/` | Reproducible new fixture and exact teardown without Node production server |
| Architecture/security | Existing executable rules | Named dev-tool roots | Enforce ownership, answer secrecy, redaction, and runtime boundaries |
| CI | Existing slice/readiness workflows | New deterministic workflow only | Remote-ready orchestration without weakening required jobs |
| Documentation/context | Canonical and derived sources made stale | Exact named documents/packs/catalog | Reconcile direct, representative, and gap classifications |

## Contracts and Interfaces

This packet consumes every accepted output from WRK-0006 through WRK-0009
without changing public meaning. The local qualification interface must expose
documented commands for exact dependency installation, PostgreSQL startup,
migration from empty/current state, successor fixture admission/placement,
Python API/static startup, correct/incorrect live browser runs, evidence/outbox
inspection, shutdown, exact Compose removal, and bounded data-root cleanup.

Failure injection and direct evidence/outbox inspection remain test-only.
Architecture/security runners return nonzero on drift and print bounded
redacted diagnostics. CI cannot silently skip a required slice job after its
prerequisites are present.

## Dependencies and Parallel Safety

WRK-0009 and all preceding SLI-0002 packets must complete first. This packet
touches shared test roots, npm orchestration, local composition, assurance
sources, and derived context, so it has no parallel-safe peer. If qualification
finds a focused product defect, return the owning packet to an appropriate
lifecycle state within its approved scope rather than redesigning that seam in
this packet.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete correct path | Clean local composition and exact successor fixture | Learner opens, selects correct option, and submits | UI shows `1/1` reviewed feedback and exactly one matching evidence/outbox set exists | Live Chromium plus PostgreSQL inspection |
| Complete incorrect path | Isolated clean learner/database and exact fixture | Learner selects another declared option and submits | UI shows `0/1` corrective feedback and exactly one matching evidence/outbox set exists | Live Chromium plus PostgreSQL inspection |
| Replay/conflict/completion | Accepted evidence exists | Exact replay, conflicting reuse, and a new post-completion submission run | Replay is stable; conflict/completion are bounded; counts remain one | Live/API/PostgreSQL assertions |
| Unauthorized/cross-origin | Session or request-origin context is invalid | GET/POST is attempted | Access fails closed before response/evidence leakage or mutation | Live denial and security tests |
| Malformed/stale submission | Option or exact version/digest/policy token is wrong | POST runs | No evidence/outbox is created and no newer version is substituted | Cross-system denial test |
| Private-answer boundary | GET, errors, generated client, logs, and browser state are inspected | Success and failure paths run | Correct answer/private definition never appears before authorized result behavior and never enters diagnostics/storage | Schema, browser, log, and static scan |
| Transaction failure | Controlled database/outbox commit failure occurs | Submission runs | No partial evidence/event remains and UI/API expose bounded retry-safe failure | Failure-injection test |
| Accessibility/theme matrix | All major states run across supported settings | Automated qualification runs | Equivalent content/actions, focus/status/reflow/contrast, and zero axe violations pass | Focused/live browser report and baselines |
| Static production boundary | Clean build and local server start | Processes/artifacts are inspected | Python plus PostgreSQL/filesystem are present; no Node app server, SSR, BFF, or server action exists | Build/composition inspection |
| Architecture/security boundaries | Completed repository is scanned | Fitness/control runners execute | Forbidden dependencies, persistence access, model duplication, browser evidence storage, answer leakage, and unsafe runtime entries fail | Architecture/security runners |
| Educational claim boundary | Fixture and UI result copy are reviewed | Both outcomes render | No mastery, certification, suitability, performance, or buy/sell/hold claim appears | Fixture and browser assertions |

## Verification Commands

```powershell
py -m uv sync --project backend --frozen
backend/.venv/Scripts/python.exe -m pytest backend/tests
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run
npm --prefix apps/web run build
npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading apps/web/tests/browser/knowledge-check
backend/.venv/Scripts/python.exe tests/e2e/knowledge-check/run.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
npm --prefix apps/web audit
git diff --check
```

The final handoff must distinguish direct focused/live evidence from previous
historical runs and must identify browser engine, operating system, container,
manual assistive-technology, dependency-advisory, CI-host, and external
qualification not performed.

## Documentation and Evidence Update

Update domain/module/Assessment/content-package/local-deployment/identity/
community-protection sources only where executable behavior makes them stale.
Update architecture verification and known gaps at invariant granularity:
direct for the exact private-loopback single-profile slice, representative for
provider-neutral shared semantics, and gap for delivery/consumption,
history/projection, recovery, managed cloud, and broader identity/browser
profiles. Rebuild derived packs only from reconciled canonical sources and do
not broaden claims.

SLI-0002 moves to `verifying` only after WRK-0006 through WRK-0010 are complete
and evidence is reconciled. Slice completion still requires the separate
verification workflow and explicit completion acceptance stored locally only.

## Stop Conditions

- Aggregate failure requires changing accepted contract, scoring, evidence,
  identity, security, risk, interface, or compatibility meaning.
- Required evidence can pass only by skipping/weakening a guardrail, using an
  in-memory/SQLite substitute for PostgreSQL, exposing private answer/evidence,
  or bypassing production idempotency/authorization.
- Local tooling would bind publicly, access credentials/providers, require a
  Node production server, or clean up a user-owned process/container/database/
  data root.
- Event qualification requires a queue/worker/consumer decision, or delivery
  is implied from durable outbox creation alone.
- Accessibility, redaction, append-only evidence, atomic outbox, exact
  versioning, generated-client authority, or advice boundaries cannot be
  proven.
- Canonical sources conflict, another active scope overlaps, or required
  external/destructive authority is absent.

## Required Handoff

Report exact local topology and commands, fixture/package/contract hashes,
contract-to-Assessment-to-database-to-API-to-generated-client-to-browser path,
evidence/outbox row semantics, correct/incorrect/idempotency/conflict/failure
results, architecture/security runner results, browser/theme/accessibility
matrix, static runtime inspection, dependency/advisory evidence,
documentation/evidence classifications, raw and normalized failures,
unperformed external qualification, cleanup result, residual risks, and
whether SLI-0002 is ready for separate completion verification.

## Planning History

- 2026-08-05: Shaped from SLI-0002 boundary seam 6 after WRK-0009; planning approval and implementation activation remain separate local-only stages.
