---
id: WRK-0090
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0025
capability: CAP-0005
depends_on: ["WRK-0089"]
decision_gates: []
parallel_safe_with: []
write_scope: ["deployments/local/README.md", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0025-qualify-complete-curriculum-navigation.md", "docs/planning/work-packets/WRK-0090-qualify-navigation-restart-and-replay.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: bb1ce700101058cf4e295c049840519b4ccceaee
claim_id: WRK-0090:b7bc6844-871f-46ca-b908-831537b2dd52
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T13:36:02Z
---

# Agent Work Packet: Qualify Navigation Restart and Replay

## Objective and Deliverable

Extend the existing isolated approved-lesson qualifier so a non-browser HTTP
client proves the complete public graph, Navigation-state, and activity-launch
path, then proves an application restart reconstructs derived Learner-model
completion state from unchanged Assessment evidence. The observable handoff is
one redacted live report that distinguishes API-only qualification, preserved
source evidence, rebuilt projections, and stable semantic navigation state.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, testing-quality, security-risk, and delivery-planning
context packs. Read the change-impact matrix, decision readiness, CAP-0005,
SLI-0025, WRK-0088 and WRK-0089, ADR-0004, ADR-0005, ADR-0014, the adaptive
Navigation-state contract, Learner-model completion service/repository and
Assessment replay adapter, session and protected API handlers, local
composition, approved-lesson runner, its browser consumers, relevant
integration tests, concurrent-work rules, and the deployment README.

## Decisions and Assumptions

- Existing versioned public APIs are the authoritative headless boundary. The
  browser remains one generated-client consumer and no AI-specific transport or
  authority is introduced.
- The live runner already owns an isolated database and data root. Test-only
  direct SQL may remove every row from the two rebuildable Learner-model
  completion tables only after the application is stopped; it may not expose a
  product reset route or mutate source evidence or Curriculum history.
- Assessment's append-only `outbox` plus completion evidence is the public
  replay source used by the Learner-model adapter. Source preservation is
  observed through counts before and after rebuild without printing private
  event payloads, learner IDs, answers, or credentials.
- First startup may seed the explicit fixture. Restart uses the same database
  and data root without reseeding so recovery depends on retained state and
  normal application composition, not fixture publication.
- Semantic replay compares exact graph identity/version/digest, policy
  identity/version, source-set digest, ordered activity states, and reason
  records. It does not demand byte identity for legitimate observation times or
  digests that include those times.

## In Scope

- Factor bounded start/stop helpers for the existing loopback Python process so
  the same isolated runner can restart it safely and retain diagnostics.
- Add a cookie-aware, same-origin HTTP client that establishes a fresh server-
  issued single-profile session and reads graph, Navigation-state, and an
  eligible activity launch using only public routes.
- Capture stable Navigation-state semantics and exact graph/launch correlation
  before the restart.
- Stop the host, inspect source/projection counts, clear only
  `learner_model.lesson_completion_history` and
  `learner_model.lesson_completion_projections`, and restart without fixture
  seeding.
- Re-establish a session, read current Navigation state, and prove stable
  semantics, unchanged Assessment evidence, and rebuilt projection/history
  rows.
- Add focused unit tests for semantic comparison, session/API behavior,
  process lifecycle, limited SQL reset scope, source-count preservation,
  failure cleanup, and redacted report construction.
- Update the Navigation-state contract and local qualification guidance with
  the exact API-first restart/replay evidence and remaining boundaries.

## Out of Scope

Any product domain/application/API/OpenAPI/generated-client/UI behavior or
schema; AI mode, agent protocol, model provider, recommendation, ranking,
mastery, or automatic selection; production reset/recovery operation;
Assessment event replay mutation; Curriculum mutation or reseeding on restart;
new migration, table, dependency, package or lockfile; cloud provider, tenancy,
managed recovery, remote binding, worker, external execution, or production
availability claim; and unrelated refactoring or styling.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live orchestrator | isolated PostgreSQL, Python host, public HTTP and browser flow | `tests/e2e/approved-lesson/run.py` | Add bounded restart, headless API, reset, rebuild, and report behavior |
| Focused evidence | runner helpers and failure paths | `tests/e2e/approved-lesson/test_replay_qualification.py` | Prove semantics without requiring Docker for every focused test |
| Contract guidance | replay and current launch boundary | adaptive Navigation-state contract | Record the observed recovery semantics without changing v1 |
| Operator guidance | automated clean qualification | deployment README | Document the API-first replay step and its safe limits |
| Planning evidence | packet, SLI-0025, register | listed planning files | Keep JIT packet and slice lifecycle synchronized |

No product source, public/executable schema, generated client, browser
specification, migration, dependency manifest, design-system asset, or fixture
meaning may change.

## Contracts and Interfaces

The headless client consumes `POST /api/v1/session/single-profile`, exact
Curriculum graph GET, exact Navigation-state GET, and exact activity-launch GET
with the server-issued HttpOnly session cookie. It supplies only the required
same-origin request metadata and accepted route selectors; it never supplies a
learner, permission, destination, state, completion, or policy result.

`stable_navigation_semantics` produces a private test value containing the
exact graph identity/version/digest, policy identity/version, source-set digest,
and complete graph-ordered activity-state/reason records. The runner may expose
only a concise pass/result summary. A test-only database helper returns bounded
counts and clears exactly the two Learner-model tables in one transaction. The
next packet consumes the completed live report and focused evidence; it receives
no new product interface.

## Dependencies and Parallel Safety

WRK-0089 is complete and makes the live runner select the prepared Python in a
clean host. This packet owns the shared approved-lesson orchestrator and the
active slice/register, so it is not parallel-safe with another packet touching
those paths. It preserves all browser scenarios and must complete before the
cumulative SLI/CAP closure packet is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| API-only path | The isolated app is ready and the browser has completed the approved lesson | A fresh cookie-aware HTTP client bootstraps and reads graph, Navigation state, and launch | Exact public facts correlate and no browser state or backend-internal import is required | focused mock and live HTTP |
| Restart and rebuild | Assessment evidence exists and current derived projection rows are present | The app stops, only derived rows are cleared, and the app restarts without seeding | A normal Navigation-state read rebuilds completion/history and returns the same semantic state | focused orchestration and live PostgreSQL/API |
| Source preservation | Assessment source rows are counted before reset | Rebuild completes | Assessment outbox/completion counts are unchanged and no source payload is logged | focused SQL assertions and live report |
| Bounded comparison | Evaluation time or a time-bound projection digest legitimately changes | Before/after results are compared | Stable owner facts, policy, source set, states, and reasons must match while irrelevant time variance does not cause failure | focused anti-rigidity test |
| Semantic drift | Graph, policy, source set, state, reason, or launch correlation differs | Replay comparison runs | Qualification fails with a bounded field-level diagnostic and no secret payload | focused failure tests |
| Restart failure | The second host exits or never becomes ready | Orchestration runs | Qualification fails, emits redacted log tail, and still removes only its exact process/container/data root | focused mock and existing live cleanup |
| External database | A caller supplies a DSN without isolation acknowledgement | Qualification starts | It refuses before any reset or source inspection | existing/focused safety test |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest tests/e2e/approved-lesson/test_replay_qualification.py
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/learner_model/test_postgres_completion_projection.py backend/tests/integration/api/test_single_profile_navigation_state_api.py backend/tests/integration/api/test_single_profile_activity_launch_api.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0090-qualify-navigation-restart-and-replay.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use the documented prepared Node/npm environment for the static build and live
Chromium run. Submit one exact candidate, generate a fresh affected-verification
receipt, and obtain one independent technical review. Docker/PostgreSQL and
Chromium are required only for the live check; focused tests must remain
deterministic without them.

## Documentation and Evidence Update

Update the contract and deployment guidance with the exact restart, API-only
client, projection reset/rebuild, source-preservation, isolation, comparison,
cleanup, and unqualified-boundary behavior. Record exact commands, counts,
candidate, receipt, review disposition, assumptions, and residual gaps in this
packet and SLI-0025. Preserve the explicit statement that APIs remain available
to UI and non-UI clients while a separate AI mode is not planned here. Keep all
approval and reviewer records only in the ignored local ledger.

## Stop Conditions

Stop for any product reset/recovery route, public contract/schema change,
source-evidence or Curriculum mutation, non-isolated database, caller-selected
learner/permission/state, browser-only authority, cross-module repository
access in product code, migration/dependency, provider/tenancy/cloud decision,
AI/model/recommendation authority, production availability claim, active scope
collision, conflicting canonical source, or material CAP-0005/SLI-0025 drift.

Do not stop or reopen review for harmless whitespace, nonfunctional styling,
report wording, or another inconsequential in-scope correction. Fix it locally
or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; headless API path; process restart; reset SQL scope;
before/after semantic, source, projection, and history evidence; all focused,
live, affected, aggregate, receipt, and independent-review results; changed
files; documentation impact; assumptions; and residual risks. Confirm that no
product API, generated client, UI behavior, source evidence, migration, model,
provider, cloud adapter, or separate AI-mode plan changed, then leave JIT-B
dependency-ready.

## Implementation Evidence

- The existing runner now starts and stops the loopback application through one
  bounded helper, cleans up a process that fails readiness, and restarts the
  normal host against the retained database and object root without fixture
  flags.
- A cookie-aware headless client uses only the public single-profile session,
  exact Curriculum graph, Navigation-state, and activity-launch endpoints. It
  correlates exact graph-owned identity, resource, destination, policy,
  source-set, ordered state, and reason semantics without importing product
  internals or trusting browser state.
- While the application is stopped, qualification executes exactly two fixed
  deletes against the rebuildable Learner-model history and projection tables.
  It observes Assessment evidence and outbox counts before and after, then
  requires normal API access to rebuild nonempty derived state.
- Nine focused orchestration tests pass. They cover seed-free restart command
  construction, headless public API routing, graph/launch drift denial,
  time/digest anti-rigidity, exact reset scope, source preservation, semantic
  replay, graceful/forced stop, and failed-readiness cleanup.
- The isolated PostgreSQL 18.4/Python/public-API/generated-client/Chromium run
  passes all eight browser scenarios plus the new replay phase. It preserves
  Assessment sources and rebuilds three projection rows and one history row
  with stable Navigation semantics after a seed-free restart.
- The focused contract/domain/application suite passes 189 tests; protected
  FastAPI integration passes 32; architecture passes 13 tests plus three
  subtests. Documentation and planning integrity, Git whitespace, and all 29
  aggregate readiness checks pass.
- No product domain, application, API, OpenAPI, generated client, UI, schema,
  migration, dependency, fixture meaning, source evidence, model authority,
  provider, cloud adapter, or separate AI-mode plan changed. Public APIs remain
  the authoritative UI and non-UI boundary.

## Planning History

- 2026-10-16: Authored just in time after SLI-0025 selection and WRK-0089
  completion. The packet reuses the isolated live harness, makes public API
  headless qualification and projection replay explicit, limits direct SQL to
  derived rows in the ephemeral database, and adds no decision or lower-level
  approval gate.
- 2026-10-16: Implemented the headless API observation, bounded host restart,
  isolated derived-state reset, source-preserving replay assertion, redacted
  report, focused tests, and synchronized contract/deployment guidance. The
  exact implementation candidate is ready for affected verification and
  independent review.
