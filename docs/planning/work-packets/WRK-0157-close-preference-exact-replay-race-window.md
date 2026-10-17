---
id: WRK-0157
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-17
parent: SLI-0075
capability: CAP-0018
depends_on: [WRK-0155]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/learner_model/application/service.py", "backend/tests/integration/learner_model/test_postgres_preferences.py", "backend/tests/integration/learner_model/test_postgres_presentation_preferences.py", "backend/tests/unit/learner_model/test_preference_service.py", "backend/tests/unit/learner_model/test_presentation_preference_service.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0075-set-accessible-display-preferences.md", "docs/planning/work-packets/WRK-0156-qualify-presentation-preferences-live-flow.md", "docs/planning/work-packets/WRK-0157-close-preference-exact-replay-race-window.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Close the Preference Exact-Replay Race Window

## Objective and Deliverable

Preserve exact idempotent replay for both learner-profile and presentation-
preference mutations when one duplicate request checks replay just before the
winning transaction commits and then reads the newer profile just after that
commit. The losing exact duplicate must return the already accepted profile,
not a stale-revision denial, while changed payloads and distinct stale keys
retain their current bounded denials and every schedule persists exactly one
revision, history row, and replay row.

This is a bounded correction to the already approved SLI-0075 semantics. It
does not change a public contract, endpoint, choice meaning, permission,
identity, persistence schema, or CAP outcome, and it needs no lower-level
approval.

## Required Context

Before editing, follow the repository `AGENTS.md` startup and routing rules and
read `docs/README.md`.
Inspect CAP-0018, SLI-0075, WRK-0154 through WRK-0156, ADR-0005 and ADR-0006,
the Learner-model public port, application service, preference repositories,
contract adapters, exact-replay and concurrency tests, protected API mapping,
approved-lesson live qualifier, module README, change-impact matrix, and
decision-readiness register.

No identity, tenancy, provider, model-authority, data-license, queue,
encryption, recovery, legal, commercial, or external-execution decision is
opened by restoring the documented exact-replay ordering.

## Decisions and Assumptions

- The documented same-key/same-payload behavior is authoritative: all exact
  retries converge on the originally accepted profile.
- The first replay lookup remains a fast path; the second lookup is required
  only after the separately read current revision proves that another commit
  became visible.
- A committed profile revision and its replay row are written in one existing
  PostgreSQL transaction, so a refreshed replay lookup after observing that
  revision is a deterministic classification boundary, not a retry loop.
- Existing repository transaction locking and uniqueness constraints remain
  the final write authority.
- The correction applies to both preference families because they expose the
  same public idempotency promise and share the same split-read pattern.

## Root Cause and Invariants

The application currently performs replay lookup and current-profile lookup as
separate repository reads before the atomic save. A duplicate request can see
no replay before the winner commits, then see the winner's newer revision and
return stale without reaching the repository transaction that rechecks replay
under the learner-scoped lock.

The correction must preserve these invariants:

- exact same-key/same-payload retries return the original accepted profile;
- same-key/changed-payload retries return immutable conflict once the accepted
  replay is visible;
- a distinct key for an old revision returns stale revision;
- replay always wins over revision comparison when a committed replay exists;
- no retry creates a second profile revision, history row, or mutation row;
- learner and presentation preferences retain equivalent ordering semantics;
- all denials remain bounded and confidential.

## In Scope

- Add one bounded second replay lookup when the separately read current
  revision no longer matches the request's expected revision.
- Reuse the original canonical request fingerprint and the same contract
  revalidation used by the initial replay path.
- Apply the ordering correction symmetrically to learner-profile and
  presentation-preference mutations.
- Add deterministic unit seams that insert a committed replay between the
  first replay lookup and current-profile lookup.
- Add real-PostgreSQL concurrency evidence for exact duplicates and retain
  changed-payload and distinct-key denial coverage.
- Resume WRK-0156 and require its complete browser/headless/PostgreSQL live
  workflow to pass on the corrected candidate.

## Out of Scope

Contract, schema, migration, endpoint, OpenAPI, generated-client, browser,
design-system, copy, identity, session, authorization, provider, model,
notification, analytics, recovery, managed-cloud, or financial behavior
changes; new retry loops; accepting changed payloads; weakening optimistic
revision checks; returning private storage details; or changing any preference
meaning.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Learner-model application | shared application service only | Recheck committed replay before final stale classification |
| Unit verification | learner and presentation service tests | Reproduce the split-read commit window deterministically |
| PostgreSQL verification | learner and presentation repository integration tests | Prove concurrent exact replay persists one durable change |
| Planning | this packet, WRK-0156, SLI-0075, register | Pause and resume the live qualifier through an explicit bounded correction |

No repository adapter, migration, public API, schema, generated client, or UI
file may change unless a new material defect is surfaced and routed separately.

## Contracts and Interfaces

No public shape changes. Both existing mutation operations retain their
current request and response contracts, error codes, generated-client methods,
and protected routes. The internal repository ports already expose the replay
lookup needed by the application correction, so no port or adapter expansion
is required.

The observable ordering remains:

```text
matching replay -> accepted original result
changed replay fingerprint -> immutable conflict
no replay + matching revision -> attempt one atomic save
no replay + changed revision -> stale revision
```

## Dependencies and Parallel Safety

WRK-0155 supplies the completed public preference paths. WRK-0157 temporarily
precedes resumption of WRK-0156 because the live qualifier is the evidence that
exposed and must close the race. The correction owns the shared Learner-model
application service and is not parallel-safe with another preference writer.
It does not overlap an active product-code lease.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Replay commits between reads | First replay lookup is empty; current lookup exposes the winner | Second replay lookup returns the accepted result instead of stale | deterministic unit |
| Changed same key | Newly visible replay has a different request fingerprint | Immutable conflict; no write | unit/integration |
| Distinct stale key | Current revision advanced and no replay exists for the key | Stale revision; no write | unit/integration |
| Exact concurrent learner mutation | Two clients send one identical learner-preference request | Both receive one accepted profile; one durable revision/change/replay row | PostgreSQL/live API |
| Exact concurrent presentation mutation | Two clients send one identical presentation request | Both receive one accepted profile; one durable revision/change/replay row | PostgreSQL/live API |
| Full regression | Browser and headless workflows run with restart and race schedules | All preference, privacy, isolation, accessibility, and cleanup evidence passes | WRK-0156 live qualifier |

## Verification Commands

Run focused learner and presentation service unit tests; real-PostgreSQL
preference integration tests; the approved-lesson qualifier tests; the full
isolated approved-lesson Chromium/headless/PostgreSQL workflow; architecture,
security, documentation, planning, compilation, and whitespace checks;
controller-selected exact-candidate verification; independent technical
review; and `python dev-tools/agent/check_ready.py`. Use the repository-pinned
Python, Node 24, npm 10.8.2, Playwright Chromium, and disposable PostgreSQL
topology.

## Documentation and Evidence Update

Update only the planning artifacts needed to record the bounded correction and
the dependency that returns WRK-0156 to verification. The module README already
states replay-before-revision semantics and therefore needs no product-guidance
change. Record exact candidates, receipts, deterministic race evidence, checks,
and remaining limitations without tracked approval or reviewer metadata.

## Stop Conditions

Stop for a public contract or migration change; a new identity, tenancy,
permission, provider, model, licensing, encryption, recovery, legal,
commercial, or external-action decision; acceptance of changed idempotency
meaning; more than one durable mutation; private denial content; unrelated
module change; stale CAP authority; or an active file-ownership collision.

Do not reopen CAP approval for the bounded ordering correction, harmless
formatting, optional wording, or nonfunctional styling.

## Required Handoff

Report `CAP-0018.SLI-0075.WRK-0157`; exact candidate and receipt; deterministic
split-read evidence; learner and presentation exact-replay concurrency results;
unchanged conflict/stale meaning; row-count invariants; full WRK-0156 live
qualification; checks and review; changed files; documentation impact;
assumptions; and residual gaps. Then return WRK-0156 to verification.

## Planning History

- 2026-10-17: Authored just in time after exact-candidate qualification exposed
  a split-read race shared by learner and presentation preferences. The packet
  restores already documented exact-replay ordering within SLI-0075 and does
  not change the approved CAP package or require lower-level approval.
