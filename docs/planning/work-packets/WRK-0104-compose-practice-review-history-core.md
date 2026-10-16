---
id: WRK-0104
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: ["WRK-0103"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/curriculum/", "backend/migrations/learner_model/", "backend/src/financial_ai_academy/modules/assessment/", "backend/src/financial_ai_academy/modules/curriculum/", "backend/src/financial_ai_academy/modules/learner_model/", "backend/tests/integration/assessment/", "backend/tests/integration/curriculum/", "backend/tests/integration/learner_model/", "backend/tests/unit/assessment/", "backend/tests/unit/curriculum/", "backend/tests/unit/learner_model/", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/curriculum-graph-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0104-compose-practice-review-history-core.md"]
generated_artifacts: []
base_revision: 25e0ce0aa469d8ffe02ec8ad826262fd8f357709
claim_id: WRK-0104:35352888-dcc3-4860-a5eb-2a67b3b77ebe
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T17:47:54Z
---

# Agent Work Packet: Compose Practice Review and History Core

## Objective and Deliverable

Implement the transport-neutral application and persistence core that turns
Assessment-owned practice evidence into a rebuildable Learner-model attempt
history and resolves incorrect-item review references through exact
Curriculum-owned mappings. The delivered operations must be directly reusable
by the next protected HTTP/OpenAPI/generated-client packet and by future
non-browser or headless consumers without creating another domain core.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the routed baseline, assessment,
curriculum, learner-model, contract, database, and application-host context;
then inspect CAP-0006, SLI-0028, WRK-0102, WRK-0103, ADR-0005, ADR-0007,
ADR-0008, decision readiness, the change-impact matrix, module map, Assessment
and Curriculum contracts, accepted practice completion/review/history schemas
and corpora, the three affected module READMEs, public facades, application
services, repository ports/adapters, migrations, consumers, and nearest tests.

## Decisions and Assumptions

- Assessment remains authoritative for retained result/event evidence and must
  validate and correlate any safe history source it exposes. The accepted
  completion-event bytes remain unchanged and are not retrofitted with fields.
- The Learner-model history contract requires item correctness and selected
  review-reference IDs that the completion-event envelope deliberately omits.
  Assessment may therefore expose a typed, answer-safe application replay view
  derived from its already retained result plus the validated event envelope;
  this is not a new event or a second evidence store.
- Curriculum owns exact mappings from one practice placement and complete
  review-resource identity/version/digest to an available or unavailable safe
  learning destination. It never reads Assessment or Content persistence.
- Learner model owns only the replaceable derived history projection and source
  digest. It consumes Assessment through a public port and never treats retries
  as mastery, competency, eligibility, certification, or recommendation.
- Missing review mappings degrade to an explicit unavailable target; they do
  not hide an attempt, invent a destination, or block history rebuild.

## In Scope

- Extend the Assessment public/application replay seam with a typed safe source
  that correlates the validated event to retained result identity, score,
  ordered item correctness, and selected review-reference IDs while excluding
  submitted values, feedback text, answers, evaluator rules, and raw rows.
- Add Curriculum domain/public/application/repository behavior and an additive
  migration for idempotent exact review-target registration and deterministic
  declaration-ordered resolution, including explicit unavailable mappings.
- Add Learner-model domain/public/application/repository behavior and an
  additive migration for deterministic zero-through-ten-attempt history
  projection, stable source digest, exact replay deduplication, atomic complete
  replacement, and read-after-restart.
- Add Assessment, Curriculum, and Learner-model unit plus real-PostgreSQL
  evidence for provenance correlation, exact mapping, rebuild, replay,
  interruption rollback, isolation, confidentiality, and anti-rigidity.
- Reconcile the affected module, contract, architecture-verification,
  module-map, migration, slice, packet, and register documentation.

## Out of Scope

HTTP routes or API models; authorization-host composition; OpenAPI or generated
clients; browser work; Audit reconciliation beyond existing trace boundaries;
event schema changes; event dispatch, queues, workers, or checkpoints; adaptive
ranking; mastery or competency inference; cross-version draft/history merge;
history deletion; provider, tenancy, cloud-recovery, or external-execution
choices; and styling-only polish.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment | completion event/result persistence, public replay, contracts/tests | typed safe source replay and its owned query/tests/docs | Supply history facts omitted intentionally from the event without changing event bytes |
| Curriculum | placement core, repository conventions, review-target contract/tests | exact mapping types, operations, migration, repository, tests/docs | Own deterministic safe review destinations |
| Learner model | completion projection precedent, practice-history contract/tests | practice projection types, rebuild operation, migration, repository, tests/docs | Own rebuildable attempt history without copying Assessment authority |
| Shared architecture | module map, contract guidance, verification map | only listed ownership and evidence guidance | Keep dependency direction and known gaps current |
| Planning | SLI-0028, this packet, register | lifecycle and exact completion evidence | Keep the governed packet chain synchronized |

No API host, OpenAPI snapshot, TypeScript generated client, web application,
design-system, dependency, or lockfile may change in this packet.

## Contracts and Interfaces

Consume the accepted `assessment.practice.completed@1.0.0`,
`practice-review-target@1.0.0`, and Learner-model `history@1.0.0` meanings
without changing their schemas or approved bytes. The Assessment public source
view must contain only the exact identities, scope, stable order, aggregate
score/outcome, per-item identity/policy/score/correctness, selected review IDs,
and completion time required to construct the accepted history record.

Curriculum accepts an exact review-target record and returns declaration-ordered
unique targets for exact declared review references. Learner model accepts a
server-bound learner plus exact practice scope through its Assessment gateway,
validates uniqueness and contiguous order, computes the canonical source
digest, atomically replaces its projection, and returns the closed typed
history. These public application operations are the stable input for the next
API packet.

## Dependencies and Parallel Safety

WRK-0103 is complete and supplies durable drafts, retry ordering, correlated
completion replay, and exact-scope persistence. This packet owns Assessment,
Curriculum, and Learner-model core files and migrations, so it is not
parallel-safe with another packet in those boundaries. The protected API and
generated-client packet depends on these exact public operations and is not
eligible until this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe source replay | Valid correlated result and event evidence exists | Assessment replays history sources after restart | Ordered typed facts include correctness/review IDs but no response, answer, feedback text, evaluator, or raw-row data | unit/PostgreSQL/security |
| Corrupt source | Result/event identities, item signatures, totals, or review IDs conflict | Assessment prepares a source view | The operation fails closed with a bounded diagnostic and leaks no stored value | unit/PostgreSQL |
| Exact review mapping | Declared references include available and unavailable exact mappings | Curriculum resolves incorrect-item IDs | Unique targets follow declaration order and exact identity/version/digest; unavailable mappings remain explicit | unit/PostgreSQL |
| Mapping conflict | One exact mapping identity is reused for different meaning | Registration or read occurs | Curriculum refuses the conflict without replacement or fall-forward | unit/PostgreSQL |
| History rebuild | Zero through ten valid ordered Assessment sources exist | Learner model rebuilds | One closed history with the canonical source digest is atomically stored and returned | unit/PostgreSQL/restart |
| Replay and interruption | Duplicate exact events or an injected replacement failure occurs | Learner model rebuilds | Exact replay is idempotent and interrupted replacement preserves the prior complete projection | unit/PostgreSQL/fault injection |
| Isolation and provenance | Another learner or exact practice version is queried | History or targets are read | No cross-learner/version state is returned and every retained identity remains exact | unit/PostgreSQL/security |
| Anti-rigidity | Item, attempt, incorrect-reference, and mapping counts vary within accepted bounds | Rebuild and resolution run | Behavior depends on contract meaning, not fixture IDs, one count, or fixed prose | unit/PostgreSQL |

## Verification Commands

Run the focused Assessment, Curriculum, and Learner-model unit suites; the
three accepted contract conformance suites; real-PostgreSQL migration,
reapply/teardown, mapping, history rebuild, replay, restart, rollback,
isolation, and confidentiality tests; existing lesson-completion, practice
submission/progress, and curriculum placement regressions; module-boundary
architecture checks; `python dev-tools/planning/check_planning.py`; `python
dev-tools/documentation/check_docs.py`; `git diff --check`; the control-plane
affected verification route and independent technical review for the exact
candidate; and `python dev-tools/agent/check_ready.py` when selected by packet
start. Use an isolated PostgreSQL qualification database for real-store checks.

## Documentation and Evidence Update

Update the affected module READMEs, Assessment/Curriculum contract guidance,
module map, architecture verification, migration index, SLI-0028, this packet,
and the planning register. Record exact candidate/receipt evidence, migration
IDs, safe source fields, mapping/rebuild invariants, focused and aggregate
results, database/restart/rollback/confidentiality evidence, assumptions,
known gaps, and the API/browser seams deliberately left for later packets. No
ADR or decision-readiness change is expected.

## Stop Conditions

Stop for a breaking accepted schema or event change; copying raw result/event
documents into Learner model; Curriculum or Learner model reading Assessment
persistence; Assessment selecting a learning destination; mutable or deleted
source evidence; adaptive ranking, mastery, competency, grade, credential,
financial-advice, provider, queue, tenancy, cloud-recovery, or external-action
authority; conflicting canonical sources; stale CAP binding; overlapping live
write scope; or a migration that cannot preserve existing evidence meaning.

Do not stop or reopen review for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; new public operation and migration
inventory; Assessment source-correlation, Curriculum mapping, and Learner-model
rebuild invariants; contract compatibility and confidentiality evidence;
focused, PostgreSQL, rollback, restart, architecture, documentation, planning,
aggregate, and independent-review results; changed paths; assumptions and
residual gaps. Confirm that the core remains directly reusable by browser and
non-browser/headless API composition and that HTTP, clients, browser, adaptive,
mastery, provider, cloud, and external-execution work remains later or outside
the CAP.

## Planning History

- 2026-10-16: Authored just in time after WRK-0103 completed. This refines the
  former combined JIT-C seam into a core packet followed by a protected
  API/OpenAPI/generated-client packet, reducing review and write scope without
  changing SLI-0028 or CAP-0006 outcome, dependencies, or acceptance.
