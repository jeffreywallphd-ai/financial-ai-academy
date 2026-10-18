---
id: WRK-0195
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0009
updated: 2026-10-18
parent: SLI-0038
capability: CAP-0009
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment/public.py", "backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/domain/progress.py", "backend/src/financial_ai_academy/modules/learner_model/ports/progress_sources.py", "backend/tests/contract/learner_progress", "backend/tests/unit/learner_model/test_progress.py", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/learner-progress/v1", "contracts/learning/README.md", "contracts/learning/learner-progress/v1", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/learning/adaptive-pathway-architecture.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0038-review-rebuildable-learning-progress.md", "docs/planning/work-packets/WRK-0195-freeze-learning-progress-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Learning Progress Contracts

## Objective and Deliverable

Freeze the additive `learner-progress/v1` external contract and the pure,
dependency-light normalization rules for one learner's rebuildable evidence-
only progress timeline. Deliver executable schemas, approved and denial corpus,
canonicalization vectors, source-family DTO boundaries, stable ordering and
digest behavior, exact-duplicate replay, immutable-identity conflict handling,
and anti-rigidity evidence over all three current Assessment evidence families.

The completed packet is a coherent contract and pure-core result. It does not
query Assessment persistence, persist a Learner-model projection, expose HTTP,
generate a client, render a browser view, publish competency meaning, or select
adaptive learning activity. Those results remain in dependent packets.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. Review covered routed learning-
adaptation and AI/ML context, change impact, decision readiness, CAP-0009,
SLI-0038, ADR-0014, adaptive-pathway ownership, Assessment and Learner-model
public/domain/application/adapter seams, current evidence contracts and tests,
contract architecture, interface and learner-language standards, consumers,
and nearest READMEs.

Before implementation changes, report the startup gate again, validate current
CAP authority and this packet, then inspect the exact Assessment public events,
Learner-model source projections, contract/compatibility conventions, module
boundaries, canonicalization tests, and every direct consumer of a changed
public type. No product, architecture, risk, or approval choice is delegated to
the implementing agent.

## Decisions and Assumptions

- CAP-0009 authority is current, SLI-0038 is the first enumerated slice, and
  DEC-0009 is complete through ADR-0014. No unresolved model, provider,
  identity, tenancy, license, recovery, or experiment decision applies.
- Assessment remains source of truth. Learner model owns only derived values
  and source-reader ports; the pure core never imports Assessment internals.
- The three closed families are `knowledge_check`, `practice`, and
  `learning_project`. Completion and scores are observable evidence, never a
  competency, mastery, credential, eligibility, or financial claim.
- This packet may extend stable Assessment public DTO and protocol surfaces so
  later adapters can enumerate learner-scoped evidence. It does not implement
  their database-backed methods or authorize caller-selected learners.
- Equivalent facts produce identical canonical meaning independent of input
  order. Exact duplicates are idempotent; changed reuse of an immutable source
  identity fails only that family and never invents replacement evidence.

## In Scope

- Add `contracts/learning/learner-progress/v1` schemas and README for a
  projection root, ordered source-family checkpoints, closed typed entries,
  page query/response, opaque revision-bound continuation, and bounded errors.
- Add compatibility fixtures and vectors covering valid empty/mixed timelines,
  all family combinations, equal timestamps, Unicode-safe context, optional
  score meaning, exact replay, input-order equivalence, continuation binding,
  and denial of private or competency-bearing fields.
- Add an isolated dependency-light contract runner that imports only its
  contract/corpus helpers and validates schema, semantic correlations,
  canonicalization, digest, bounds, privacy, and approved/denial behavior.
- Extend Assessment's stable public boundary with typed learner-scoped replay
  requests/results for each family. The DTOs contain only safe source facts and
  retain exact event/evidence, version, policy, score, occurrence, and owner
  references required by the contract; no answer, feedback text, project file,
  workspace, storage, session, or provider data is exposed.
- Add Learner-model source-reader protocols and a pure progress domain module
  that validates/canonicalizes the three source DTO families without importing
  Assessment, computes family and total source digests, orders entries newest-
  first with deterministic tie breakers, and reports exact conflict references.
- Prove flexible valid shapes rather than fixture-specific IDs, counts, times,
  scores, or prose. Keep all validation closed enough to reject unknown private
  data without limiting legitimate additional evidence.
- Update exact contract catalogs and architecture/learning ownership guidance,
  plus packet/slice/register lifecycle evidence.

## Out of Scope

- Assessment repository queries, service implementations, PostgreSQL changes,
  source adapter wiring, learner projection repository, migrations, transaction
  or concurrency behavior, family carry-forward, or runtime rebuild operations.
- FastAPI, authorization policy, Identity permissions, OpenAPI, generated
  clients, Web models/components, browser routes, styling, or live topology.
- Competency labels/estimates, uncertainty, applicability, review due state,
  adaptive ranking, recommendations, experiments, analytics, credentials,
  comparison, filters, or Curriculum-wide percentages.
- AI/ML models, training data, model/provider calls, financial calculations,
  personalized advice, organization tenancy, managed-cloud recovery,
  external execution, destructive repair, notifications, or public sharing.
- Raw learner answers, correct answers, feedback text, project files, workspace
  state, private owner payloads, storage locators, secrets, sessions, or another
  module's mutable record.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | adjacent learning and evidence families | new learner-progress schemas/README and catalog links | freeze external meaning |
| Compatibility | current assessment and learner-model corpora | new learner-progress corpus/vectors and catalog | bind accepted, rejected, and canonical behavior |
| Assessment public boundary | current event DTOs and operations | additive safe replay request/result DTOs and protocol operations only | declare owner-supported source surface |
| Learner-model pure core | existing source projections and validation rules | new progress domain values/functions and source-reader ports | own deterministic derived meaning without foreign imports |
| Verification | contract and unit conventions | isolated learner-progress contract and pure-core tests | execute contract, privacy, replay, ordering, and anti-rigidity evidence |
| Architecture/docs | adaptive pathway, contracts, verification, module README | exact ownership/maturity sections | describe delivered boundary honestly |
| Planning | SLI-0038, this packet, register | lifecycle/evidence sections only | maintain governed state |

No repository, migration, host, generated client, browser, deployment, provider,
model, Identity, or unrelated documentation path is writable.

## Contracts and Interfaces

1. `LearnerProgressV1` identifies schema version `1.0.0`, a positive revision,
   lowercase SHA-256 source digest, rebuild time, evidence cutoff, exactly one
   checkpoint per closed source family, a bounded entry count/page, and opaque
   continuation. Learner identity is never returned or accepted as a query.
2. Checkpoints identify their source contract/version and state (`current`,
   `stale`, or `unavailable`). Non-current states use closed learner-safe reason
   codes; last-success cutoff/digest are correlated and never fabricated.
3. Entries are a closed discriminated union. Common facts are family/kind,
   immutable event/evidence identity, occurrence time, family state, source
   contract/policy versions, and exact replay owner references. Scores are
   bounded optional completion/attempt facts and never percent mastery.
4. Knowledge-check entries retain placement, package, assessment, definition,
   item, and scoring-policy facts. Practice entries retain placement, package,
   practice, attempt policy, attempt/submission facts, and bounded score.
   Project entries retain project, accepted submission, snapshot, brief,
   placement, and closure-policy facts without qualitative grading.
5. Public Assessment replay requests accept only server-supplied `learner_id`.
   Results are immutable safe DTOs. Later infrastructure implements them; this
   packet only makes the required stable source contract explicit and tested.
6. Learner-model ports define one reader per family. Pure domain inputs are
   Learner-model values, not Assessment types. Domain code imports no adapter,
   framework, database, host, provider, model, filesystem, network, or clock.
7. Canonicalization normalizes aware timestamps to UTC `Z`, sorts by newest
   occurrence then family/kind/event/evidence stable keys, and hashes compact
   sorted-key UTF-8 JSON. Equivalent order is identical; changed meaning is not.
8. Continuation is opaque and binds schema version, projection revision,
   source digest, offset, and page size. Malformed, guessed, out-of-bounds, or
   stale-revision tokens fail without exposing their raw content.

## Dependencies and Parallel Safety

This first SLI-0038 packet has no work-packet dependency. It owns the contract
and pure meaning consumed by the later runtime/persistence packet. It is not
parallel-safe with another SLI-0038 packet because dependent implementation
must consume its frozen schemas, DTOs, ports, canonicalization, and planning
artifacts; later packet IDs remain intentionally unreserved.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty current progress | Three successful empty families | Contract/domain normalization runs | One valid empty projection has three current checkpoints and no competency claim | approved corpus/unit |
| Mixed evidence | Valid facts from all three families | Inputs are normalized | Typed entries retain exact safe owner/version facts in stable newest-first order | approved corpus/unit |
| Equivalent order | The same valid facts arrive in different family/input order | Canonicalization runs | Entries, family digests, total digest, and bytes are identical | vector/property |
| Exact duplicate | One immutable fact appears twice unchanged | Normalization runs | One entry is produced and no conflict is invented | unit/property |
| Changed identity reuse | One event/evidence identity is reused with changed meaning | Normalization runs | The affected family fails closed with a bounded reference | denial/unit |
| Flexible valid bounds | Zero through many events, equal times, varied scores, Unicode-safe references, and all family combinations | Validation runs | Legitimate shapes pass without fixture-count or exact-prose assumptions | property/anti-rigidity |
| Private expansion | Answer, feedback, learner/tenant/session, file/workspace, storage/provider/secret, arbitrary text, or unknown field appears | Validation runs | The entire input fails before private content is returned | denial/security |
| Misleading meaning | A fixture labels evidence as mastery, competency, eligibility, credential, advice, or suitability | Validation runs | The contract rejects the claim | denial/language |
| Opaque continuation | Valid and changed projection bindings are exercised | Tokens are decoded/validated | Exact binding resumes; malformed/guessed/stale binding yields a safe restart error | vector/unit |
| Layer isolation | Contract runner and pure-core imports are inspected | Architecture checks run | No persistence, framework, host, Web, provider/model, or foreign implementation import exists | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/contract/learner_progress backend/tests/unit/learner_model/test_progress.py backend/tests/unit/assessment -q`
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the tracked affected-check plan and exact-candidate verification after the
candidate is frozen, followed by an independent technical disposition. Docker,
PostgreSQL, API, generated-client, and browser checks are not routine for this
contract/pure-core packet.

## Documentation and Evidence Update

Record exact families, types, bounds, canonical order/digest/token rules,
approved and denial corpus, replay/conflict and anti-rigidity results, public
source DTO maturity, layer isolation, focused and affected checks, candidate
and receipt, technical disposition, rollback impact, residual gaps, and CAP/
slice conformance. Approval/reviewer records remain only in ignored local state.

## Stop Conditions

Stop for stale CAP authority; evidence ownership conflict; competency,
recommendation, experiment, model/provider, identity/tenancy, licensing,
recovery, legal/commercial, financial, or external-action choice; direct
Assessment storage access by Learner model; private source data; breaking
public change; persistence/migration behavior; active scope collision; or
material CAP/SLI drift.

Do not stop or reopen broad review solely for harmless whitespace, optional
wording, valid fixture count/order, nonfunctional styling, or another
inconsequential issue. Correct bounded functional/evidence defects locally or
defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0009.SLI-0038.WRK-0195`; exact candidate and receipt; contract and
compatibility catalogs; safe Assessment replay DTOs; pure Learner-model
normalization, digest/order/token behavior; replay/conflict/privacy and anti-
rigidity results; architecture/security isolation; documentation impact;
rollback status; assumptions; residual gaps; CAP conformance; and unresolved
decisions. Confirm no persistence, migration, API/client, UI, authorization,
provider/model, competency, tenant, financial, or external-action behavior was
implemented.

## Planning History

- 2026-10-18: Authored just in time after SLI-0038 refinement. The packet
  freezes one additive evidence-only progress contract, safe owner replay DTO
  seam, and pure normalization core for all three delivered evidence families.
  It leaves runtime source queries, persistence, protected API/client, browser,
  and live qualification to dependency-ordered packets without adding a lower-
  level approval gate.
