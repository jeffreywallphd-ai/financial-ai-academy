---
id: SLI-0016
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: CAP-0001
depends_on: ["SLI-0015"]
decision_gates: []
---

# Vertical Slice: Reopen Retained Lesson Completion

## Outcome and User Scenario

After completing the exact knowledge check, the authorized learner can close
and reopen the lesson and see a reproducible completion state and evidence
history rebuilt from retained Assessment events. The view identifies the exact
lesson and assessment versions, score, time, attempt, and source evidence while
making no mastery or certification claim.

## Scope Boundaries

### In Scope

- A typed Assessment public query over its retained versioned completion events;
  it is a replay source, not a queue or delivery-guarantee choice.
- A Learner-model-owned, rebuildable PostgreSQL completion projection and
  evidence history retaining source event, attempt, and evidence references.
- Audit-owned append-oriented event references with actor/action, canonical
  event digest, source evidence, exact-version provenance, and idempotency.
- A protected history API/generated client and an accessible reopened-lesson
  state that cannot select another learner or silently substitute versions.
- Duplicate, tampered, stale-version, unsupported-event, missing-context,
  interrupted-rebuild, empty-history, and unavailable-storage behavior.

### Out of Scope

- A background worker, queue, broker, polling schedule, delivery SLA, or
  managed-cloud event infrastructure.
- Mastery, competency, certification, recommendations, adaptive ranking,
  retakes, overrides, or mutation of Assessment evidence.
- Cross-learner history, bulk export, recovery automation, retention policy,
  built-in/OIDC qualification, or cloud deployment claims.

## Canonical Context and Decisions

ADR-0005 assigns immutable evidence to Assessment, derived completion and
progress to Learner model, and integrity/provenance references to Audit.
ADR-0006 supplies server-resolved learner context; ADR-0008 constrains local
evidence protection and recovery claims. The modular-monolith dependency rules
permit consumers to use Assessment's public operation and versioned event, but
forbid cross-schema reads. The decision-readiness register leaves job queues and
delivery guarantees unresolved, so this slice uses explicit synchronous replay
on the history query and makes no asynchronous-delivery claim.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Replay Assessment public events into Learner model and Audit when history is opened | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add a mutable completion flag to Assessment | no | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 4 |
| C. Introduce a background queue projector | no | 2 | 2 | 0 | 1 | 0 | 1 | 1 | 7 |
| D. Reconstruct history only from browser submission state | no | 1 | 0 | 2 | 0 | 1 | 1 | 2 | 7 |

## Selection Rationale

Candidate A is the only eligible cut. It delivers the reopen scenario through
the accepted module boundaries, proves deterministic replay and idempotency,
and stays independent of the unresolved queue decision. Candidate B violates
Assessment/Learner-model ownership, C crosses a decision gate, and D loses
durable server authority after interruption.

## Boundary Path

`reopened lesson UI -> generated client -> protected API host -> Audit public
reconcile operation -> Learner-model public completion query -> Assessment
public event query -> module-owned PostgreSQL repositories`. Both consumers use
only the typed Assessment public surface. The API returns a view only after
Audit reconciliation and an atomic Learner-model rebuild succeed.

## Contracts, Data, and Provenance

Assessment exposes validated `assessment.knowledge-check.completed@1.0.0`
events from its append-only outbox with learner/placement filters and stable
ordering. Learner model atomically replaces only its derived projection/history
for that learner and placement from the complete validated event set, retaining
event, attempt, evidence, package, assessment, item, policy, score, and time.
Audit appends one integrity record per event ID and rejects conflicting replay
of the same event identity. Neither consumer reads Assessment tables directly.

The public history response carries exact provenance and bounded completion
meaning. It omits provider bindings, answer selections, answer keys, feedback
internals, database identifiers, and any mastery or advice interpretation.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Reopen after completion | Exact completion and evidence history reappear after a fresh browser load | API/browser/live E2E |
| Empty history | The exact lesson remains usable and clearly incomplete without fabricating evidence | application/API/browser |
| Duplicate replay | Projection and Audit retain one source record for one event | repository integration |
| Interrupted rebuild | No partial or false completion becomes visible; the next query rebuilds successfully | real-PostgreSQL integration |
| Tampered or unsupported event | Reconciliation fails closed and preserves the last valid projection | contract/application/integration |
| Missing or forged learner context | Request is denied before history or event data is disclosed | host/security integration |
| Stale lesson/assessment identity | No newer or different version is substituted | application/API/browser |
| Audit reconciliation failure | The endpoint returns unavailable and does not present un-audited new completion state | workflow integration |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0035 | Expose the validated replay-safe Assessment event source | none | none | complete |
| WRK-0036 | Deliver the rebuildable Learner-model completion projection | WRK-0035 | none | complete |
| WRK-0037 | Deliver append-oriented Audit event references | WRK-0035, WRK-0036 | none | complete |
| WRK-0038 | Expose the protected completion-history API and generated client | WRK-0037 | none | complete |
| WRK-0039 | Deliver the accessible reopened-lesson completion view | WRK-0038 | none | complete |
| WRK-0040 | Qualify and close the complete replay/history slice | WRK-0039 | none | complete |

## Verification and Qualification

Run event-contract conformance, unit tests, real PostgreSQL migration/replay/
rollback/tamper tests, architecture and security checks, OpenAPI/client
generation, web component and Chromium accessibility/state tests, live
close/reopen qualification, docs/planning/design gates, dependency audit, and
`python dev-tools/agent/check_ready.py`.

## Rollback and Migration

Learner-model data is rebuildable from Assessment evidence and may be dropped
and recreated after consumers are disabled. Audit records are append-oriented;
rollback must not claim their removal is harmless and requires confirming the
local evidence-retention boundary. Assessment event-source additions are
read-only and do not alter existing evidence.

## Stop Conditions

Stop for a renewed decision or CAP package if delivery requires a queue,
delivery guarantee, worker topology, cross-module SQL, mutable Assessment
evidence, mastery inference, cross-learner access, managed-cloud/recovery
claims, or a different event/version meaning. Bounded implementation defects
and packet refinements remain inside this slice.

## Documentation Impact and Completion Evidence

### Delivered Outcome and Boundaries

All six packets are complete. Assessment publishes a typed validated
placement/learner-filtered replay query; Learner model atomically rebuilds
bounded completion/history with stable source-set identity; Audit appends one
canonical integrity reference per source event; the protected API reconciles
Audit before returning the server-learner-bound projection; and the static
browser presents exact retained provenance before it can offer another answer.
No module reads another module's persistence and no browser request selects a
learner or receives private answers, feedback internals, or Audit rows.

The required repository startup, routed canonical sources, impact matrix,
decision readiness, interface standards, affected contracts/consumers/tests,
and nearest README files were read and followed before changes. The delivered
path remains synchronous by design and stays inside the accepted first-loop,
single-profile, private-host boundary.

### Acceptance and Failure Evidence

- Live close/reopen passed through PostgreSQL 18.4, the module-first Python
  composition, one same-origin static host, generated client, and pinned
  Chromium. Two consecutive post-submission reloads showed the same source-set
  digest and one exact evidence chain with no replacement answer form.
- Empty source history, exact replay, duplicate and conflicting event identity,
  interrupted projection replacement, malformed/unsupported/tampered event,
  Audit conflict/failure, projection failure, and unavailable services are
  covered at contract, application, real-PostgreSQL, and API layers.
- Missing session and client-supplied authority are denied before consumer
  access. Nonexistent/stale placement does not substitute a newer version.
  Browser responses that are denied, incoherent, or unavailable stop without a
  false completion or evidence mutation.
- The completed browser state exposes score, time, exact package/Assessment/
  item/policy versions and digests, and source event/attempt/evidence references
  while explicitly rejecting mastery, certification, advice, suitability, and
  performance meaning. Light/dark axe scans, keyboard/focus, narrow reflow,
  reduced motion, forced colors, and existing lesson visual parity passed.

### Exact Verification Results

- `backend/.venv/Scripts/python.exe -m pytest backend/tests` with an isolated
  PostgreSQL 18.4 DSN: 196 passed on Python 3.14.3; the exact temporary
  container and volume were removed.
- `npm --prefix apps/web test -- --run`: 26 passed across six files under Node
  24.14.0. `npm --prefix apps/web run test:browser --
  apps/web/tests/browser/lesson-reading`: eight Chromium scenarios passed.
- `backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py`: two live
  Chromium scenarios passed; the runner removed its exact database container
  and temporary data root.
- OpenAPI and generated-client currency, web typecheck, lint, and production
  build passed. The Python-served static index digest was
  `15ea50af1f57d2b0c6dee25277e49d80440c6b6ba7796be8a2a5e42dd60164ef`.
- Architecture passed eight fitness functions; security passed ten control
  groups; design validation verified 125 tokens and 56 icons; documentation
  verified 194 Markdown files plus catalogs; planning verified 70 artifacts;
  the JavaScript dependency audit found zero vulnerabilities; and the diff
  check passed with line-ending warnings only in generated/installed files.
- `python dev-tools/agent/check_ready.py --base-ref
  515c2e16e4458b1305a89acd594085c828fe49ec` passed all 27 fixed checks outside
  the Windows app sandbox used only for temporary-fixture-hostile commands.

### Contracts, Documentation, and Migration

Assessment v1 and `assessment.knowledge-check.completed@1.0.0` remain backward
compatible and unchanged. The reviewed OpenAPI snapshot/generated client are
byte-current. Separate Assessment, Learner-model, and Audit migrations apply,
reapply, tear down in focused tests, and compose from an empty live database.
Projection replacement rollback preserves the last valid state; Audit rollback
cannot treat append-oriented evidence as disposable. No backup or restore
operation was implemented or claimed.

Module, Assessment-contract, assurance, security, web, migration, API, and
planning documentation now reflects the delivered path. Derived context did
not require a semantic update because the canonical ownership and synchronous
replay constraints were already represented.

### Qualification Limits, Assumptions, and Residual Gaps

Qualification assumes the accepted private loopback host and setup-selected
`single_profile` identity. Background delivery and guarantees, production
database roles, backup/restore and retention automation, built-in/OIDC and
multi-user isolation, non-Chromium browsers, managed-cloud adapters/recovery,
additional Assessment families, mastery, and adaptation remain unqualified.
Manual screen-reader operation and actual browser zoom controls remain later
controlled checks; automated axe and zoom-equivalent reflow are direct.

The slice conforms to the current CAP-0001 package and its exact manifest. No
material drift or new decision gate was found, and deterministic closure needs
no lower-level completion approval.

## Planning History

- 2026-10-15: Refined from the approved CAP-0001 manifest after SLI-0015
  completed. Explicit synchronous replay was selected to avoid the unresolved
  queue/delivery-guarantee boundary; no material CAP drift or new decision gate
  was found.
- 2026-10-15: WRK-0035 delivered the validated, filtered Assessment event
  replay source; Learner-model projection is the next dependency-ready packet.
- 2026-10-15: WRK-0036 delivered the rebuildable Learner-model completion
  projection; append-oriented Audit references are next.
- 2026-10-15: WRK-0037 delivered append-only Audit integrity/provenance
  references; protected API and generated-client integration are next.
- 2026-10-15: WRK-0038 delivered the Audit-first protected completion-history
  API and generated client; reopened-lesson browser presentation is next.
- 2026-10-15: WRK-0039 refined the completion-first browser state, exact
  retained-history presentation, and focused accessibility/failure evidence;
  it remains inside the approved CAP package with no new decision gate.
- 2026-10-15: WRK-0039 delivered completion-first reload behavior with exact
  retained provenance, bounded failure states, and passing component plus
  light/dark/accessibility/reflow browser evidence; final slice qualification
  is next.
- 2026-10-15: WRK-0040 refined the live close/reopen, repeated replay, static
  artifact, cumulative verification, and documentation-reconciliation route;
  no material CAP change or unresolved decision was found.
- 2026-10-15: WRK-0040 completed cumulative qualification with 196 backend, 26
  web, eight focused Chromium, two live same-origin Chromium, and 27 aggregate
  readiness checks passing; SLI-0016 entered deterministic closure.
- 2026-10-15: Completion structure, documentation, planning integrity, and all
  acceptance evidence reconciled; SLI-0016 closed complete with no unresolved
  decision, material CAP drift, or lower-level approval.
