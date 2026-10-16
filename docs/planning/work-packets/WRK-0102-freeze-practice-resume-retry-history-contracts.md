---
id: WRK-0102
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/tests/contract/assessment_practice/", "backend/tests/contract/curriculum_practice_review/", "backend/tests/contract/learner_model_practice_history/", "contracts/compatibility/README.md", "contracts/compatibility/assessment-practice/v1/", "contracts/compatibility/curriculum-practice-review/v1/", "contracts/compatibility/learner-model-practice-history/v1/", "contracts/learning/README.md", "contracts/learning/assessment/practice/v1/", "contracts/learning/curriculum/v1/", "contracts/learning/learner-model/practice/v1/", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/curriculum-graph-contract.md", "docs/contracts/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0102-freeze-practice-resume-retry-history-contracts.md"]
generated_artifacts: []
base_revision: 9eb7ea6c1d383df298102778611790d706ccad3a
claim_id: WRK-0102:7e8ea83b-c464-4eaa-8293-9397b588829e
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T17:09:15Z
---

# Agent Work Packet: Freeze Practice Resume, Retry, and History Contracts

## Objective and Deliverable

Freeze the additive transport-neutral contract families and dependency-light
conformance evidence needed for SLI-0028: conditional partial-draft save/read,
deterministic retry state, exact Curriculum review targets, and rebuildable
Learner-model practice-attempt history. Define complete positive, boundary,
flexible-shape, and confidential denial corpora without implementing public
facades, persistence, migrations, HTTP/OpenAPI, generated clients, browser
behavior, or live composition.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository-
root `docs/README.md`; route through the baseline, delivery-planning, learning-
adaptation, architecture-contract, security-risk, and testing-quality guidance.
Read the change-impact matrix, decision readiness, CAP-0006, completed SLI-0027,
SLI-0028, ADR-0005, ADR-0007, ADR-0008, the Assessment and Curriculum contracts,
contract architecture/versioning rules, practice-v1 schemas and corpus, current
Assessment result/event meaning, Learner-model completion-history precedent,
contract runners, module boundaries, and concurrent-work protocol.

## Decisions and Assumptions

- Extend existing contract namespaces additively. Do not change the meaning or
  required fields of accepted practice submission, result, presentation,
  definition, or completion-event v1 documents.
- Treat a partial draft as mutable learner work state, not an attempt,
  completion, score, event, recommendation, or evidence. It carries a closed
  subset of the existing response union and exact immutable selectors.
- Define conditional save semantics around server revision 0 for creation and a
  positive monotonic revision thereafter. Exact same-content replay may return
  the current representation; different stale input conflicts. Identity,
  revision, and save time are never client authority.
- Define retry state from the exact `formative-retry@1.0.0` policy and immutable
  accepted-attempt count. Support every valid `max_attempts` from 1 through 10;
  do not specialize semantics to the approved fixture's value 3.
- Preserve the existing completion event as the Learner-model replay input. A
  new history view is derived, bounded, and source-referenced; it never contains
  submitted values, feedback text, correct answers, evaluator declarations,
  mastery, competency, or advice.
- Define Curriculum review targets as exact mappings from practice placement
  plus review-resource identity/version/digest to a safe lesson placement.
  Selection is a separate deterministic rule over incorrect item results;
  Curriculum never reads Assessment persistence or feedback internals.
- Keep schemas closed and versioned while anti-rigidity fixtures vary valid
  counts, order, identifiers, timestamps, scores, references, and policy limits.

## In Scope

- Add Assessment practice draft-save request and server draft representation
  schemas using the existing closed response union and exact version selectors.
- Add deterministic retry-state schema semantics for attempt count, remaining
  attempts, can-retry status, policy provenance, and bounded denial reasons.
- Add a Curriculum practice-review-target contract family with exact resource
  and safe destination provenance plus available/unavailable meaning that does
  not hide the underlying result.
- Add a Learner-model practice-history contract family with a source digest,
  stable attempt order, score/outcome/item-correctness summary, review-reference
  IDs, completion time, and exact event/attempt/evidence/package/definition/
  practice/policy provenance.
- Add approved, minimum/maximum, empty/partial, variable-shape, order, duplicate,
  stale, unsupported, overflow, inconsistent-provenance, private-field, and
  malformed examples with stable bounded diagnostic codes.
- Extend or add dependency-light contract runners that validate JSON Schema and
  cross-record semantics independently of database, framework, API, or UI code.
- Reconcile contract catalogs and architecture guidance made stale by the new
  accepted shapes, plus packet/slice/register evidence.

## Out of Scope

Production domain/application/public-facade code; draft, retry, review-target,
or history repositories; PostgreSQL migrations; transaction locks; event replay
queries; API routes/models/OpenAPI; generated clients; browser components; live
qualification; a new practice package; changing the existing result/event
shape; cross-version draft conversion; deletion/retention schedules; queues or
workers; adaptive ranking; mastery; manual/model grading; external providers;
tenancy; managed-cloud recovery; separate AI/headless mode; or styling.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment practice contracts | accepted v1 definition/presentation/submission/result/event and corpus | additive draft/retry schemas, corpus, runner, README | Freeze mutable-work and retry meaning without changing evidence bytes |
| Curriculum contracts | graph/activity identity and placement ownership | additive exact review-target schema/corpus/runner and bounded catalog guidance | Keep resource-to-placement routing Curriculum-owned |
| Learner-model contracts | completion projection/history precedent and Assessment event | additive practice-history schema/corpus/runner | Freeze rebuildable evidence-only summaries |
| Architecture/catalog docs | contract ownership/versioning and module boundaries | listed contract guidance only | Record semantic ownership and compatibility |
| Planning | SLI-0028, this packet, register | listed artifacts | Record bounded packet evidence and lifecycle |

No production module, database, migration, API snapshot, generated client,
package fixture, dependency, lockfile, design token, icon, or browser file may
change.

## Contracts and Interfaces

Produce additive Draft 2020-12 JSON Schemas and compatibility documents with
stable `1.0.0` family versions. Reuse existing identifier, semantic-version,
digest, canonical-decimal, response, policy, and UTC timestamp profiles rather
than inventing equivalent shapes. Draft requests carry `expected_revision` and
the exact public selectors plus zero through all defined responses; server
drafts add positive revision and server save time but no learner ID.

Retry state carries `attempts_used`, `max_attempts`, `attempts_remaining`, and
`can_retry` with exact policy/version provenance and invariants that prevent
negative, overflow, or contradictory values. History carries no draft and no
submitted answers. Its ordered entries correlate one source event, attempt, and
evidence ID to exact definition/policy versions and bounded item-score facts.
Review targets bind the exact review resource to one safe lesson placement and
must not contain a raw URL, HTML, filesystem path, provider payload, or client-
selected route.

## Dependencies and Parallel Safety

SLI-0027 is complete and supplies immutable evidence plus the existing event.
This first SLI-0028 packet has no packet dependency. It owns shared practice,
Curriculum, and contract catalog sources and therefore is not parallel-safe with
another packet editing those paths. Later persistence/API/UI packets depend on
these exact accepted shapes but may refine implementation detail without
changing their meaning.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Partial draft | Any valid subset from zero through all definition items | Request and server draft validate | Exact selectors/responses round-trip; server fields cannot be supplied as client authority | schema/semantic corpus |
| Flexible shape | Valid definitions with variable item/reference counts and all three response types | Drafts and histories validate | No fixture-specific count, order, ID, score, or timestamp becomes a rule | anti-rigidity corpus |
| Draft denial | Duplicate, unknown, wrong-type, private, noncanonical, stale-selector, or overflow input | Contract runner evaluates it | Stable bounded denial contains no answer, learner, path, or raw payload | negative corpus |
| Retry boundaries | Attempt counts span zero, one below, exactly at, and inconsistent with policy limits 1 through 10 | Retry state validates | Remaining/can-retry meaning is exact and contradictions fail closed | semantic corpus |
| History reconstruction | Valid events arrive in varied order with exact provenance | History view is derived | Stable attempt order/source digest and bounded summaries are reproducible | history runner |
| Replay and duplication | The same event appears repeatedly or IDs conflict | History semantics evaluate it | Exact duplicates are idempotent; inconsistent duplicates fail closed | history runner |
| Targeted review | Incorrect item references contain repeats and varied declaration order | Selection semantics run | Unique declaration-ordered IDs map only to exact approved targets | review runner |
| Unavailable target | An approved reference lacks a current exact mapping | Target state validates | Result/history remain usable and target reports unavailable without substitution | review corpus |
| Confidentiality | Documents are serialized and denial cases run | Public fields are inspected | No submitted answers in history, no correct answer/evaluator, no learner ID in client shapes, and no raw route/provider data appear | contract/security tests |
| Compatibility | Existing accepted practice documents run unchanged | New runner suite is added | Existing schemas, digests, fingerprints, result/event bytes, and knowledge-check corpus remain accepted | regression corpus |

## Verification Commands

Run the Assessment practice, Curriculum review-target, and Learner-model
practice-history contract suites; existing Assessment, curriculum-graph,
lesson-package, and learner-completion contract/unit regressions; JSON Schema
closure and semantic denial checks; architecture contract ownership;
work-packet validation; documentation, planning, whitespace, affected
verification, one independent technical review, and the fixed aggregate
readiness gate. Add no database, API, web, browser, or live checks unless the
implementation crosses those excluded boundaries.

## Documentation and Evidence Update

Record every added schema/corpus version, ownership boundary, canonicalization
and ordering rule, variable-shape evidence, compatibility result, confidentiality
result, exact candidate and receipt, review disposition, commands/results,
assumptions, residual gaps, and CAP/SLI conformance. State that these contracts
do not yet implement persistence, retries, resume, history, review routing,
public APIs, browser behavior, mastery, adaptation, or AI authority.

## Stop Conditions

Stop for a breaking change to an accepted practice/result/event document; a new
item, scoring, policy, or event family; ambiguity about draft versus evidence
ownership; a client-authoritative learner/revision/time/attempt decision;
history containing submitted values or private feedback/answer data; raw URLs
or provider routes as Curriculum meaning; adaptive/mastery interpretation;
cross-version draft conversion; retention/deletion policy; persistence/API/UI
implementation; provider, queue, tenancy, cloud, recovery, external execution,
or AI authority; conflicting canonical sources; stale CAP binding; or active
write-scope collision.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate; schema and corpus inventory; draft/retry/history/
review-target invariants; flexible-shape and denial coverage; unchanged existing
contract bytes; ownership and confidentiality evidence; focused, affected,
aggregate, documentation and planning checks; changed paths; assumptions and
gaps. Confirm that no persistence, migration, public API, client, browser,
mastery, adaptation, separate AI mode, provider, cloud, or external execution
was implemented. Leave the next SLI-0028 persistence packet dependency-ready.

## Planning History

- 2026-10-16: Submitted exact candidate
  `297e8a51d29f5fdf07ea27ddbc1cbc8ad256aef6` for affected verification and
  independent technical review. The candidate adds only the frozen contract,
  compatibility, conformance, and documentation boundaries; production
  persistence, APIs, clients, and UI remain deferred.
- 2026-10-16: Claimed from base revision `9eb7ea6c1d383df298102778611790d706ccad3a`
  and activated for bounded contract implementation under the repository control
  plane. No lower-level approval was required by the current CAP authorization.
- 2026-10-16: Authored just in time as the first SLI-0028 seam after SLI-0027
  completed. The packet freezes additive, transport-neutral contracts and
  anti-rigidity evidence before persistence or API work, preserving Assessment,
  Curriculum, and Learner-model ownership without opening a durable decision.

