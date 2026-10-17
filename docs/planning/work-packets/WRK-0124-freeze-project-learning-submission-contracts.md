---
id: WRK-0124
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/project_submission_contract.py", "backend/src/financial_ai_academy/modules/assessment/domain/project_submission.py", "backend/src/financial_ai_academy/modules/assessment/ports/project_submission.py", "backend/tests/contract/assessment_project/**", "backend/tests/unit/assessment/test_project_submission_contract.py", "contracts/compatibility/assessment-project/v1/**", "contracts/learning/README.md", "contracts/learning/assessment/project/v1/**", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/project-submission-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0124-freeze-project-learning-submission-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Project Learning-Submission Contracts

## Objective and Deliverable

Deliver the additive transport-neutral Assessment contract and pure
deterministic policy for submitting one exact learning-started Project snapshot.
The accepted result must close snapshot-candidate, submission, validation,
immutable evidence, safe event, and ordered-history meaning before persistence,
HTTP, generated clients, projections, or browser behavior begin.

The packet leaves the repository coherent with executable schemas,
compatibility fixtures, a dependency-light conformance runner, immutable domain
values, a contract adapter, and focused tests. It does not create learner state
or expose a new runtime operation.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the delivery-planning, architecture-contracts,
testing-quality, security-risk, and Project/Assessment context; apply the
change-impact matrix and decision readiness; and inspect CAP-0007, SLI-0032,
ADR-0005, ADR-0011, ADR-0012, the Project workspace and deterministic
Assessment contracts, current Project snapshot shapes and public projectors,
Assessment practice schemas/adapters/runners, Content brief and Curriculum
placement shapes, exact consumers/tests, and the nearest READMEs.

## Decisions and Assumptions

- Project remains the sole owner of mutable workspace and immutable snapshot
  meaning. This packet consumes a closed learner-safe snapshot candidate and
  never imports Project internals or copies artifact bytes.
- Content owns the approved brief and ordered milestone definitions; Curriculum
  owns their exact placement. Assessment owns only the immutable submission,
  deterministic closure validation, evidence, and safe completion event.
- A valid submission maps every exact milestone exactly once to one or more
  versioned resource references already included in the submitted snapshot.
  Validation proves structural closure, not quality, truth, mastery,
  competency, result reproduction, code safety, or financial performance.
- Exact replay identity is learner-independent contract meaning over the closed
  submission document. Server learner/time/IDs, persistence sequencing,
  supersession, and authorization remain for later packets.
- Every artifact stays inert under ADR-0011. No schema field can request
  execution, active rendering, network, secrets, packages, callbacks, or a
  provider.
- Existing knowledge-check and practice contract families remain byte-for-byte
  and semantically unchanged.

## In Scope

- Add versioned closed JSON Schemas for a snapshot candidate, submission
  intent, validation result/issues, immutable evidence, safe completion event,
  and ordered history envelope under an additive Assessment Project family.
- Define exact Project/snapshot, origin, Content brief, Curriculum placement,
  milestone, snapshot-resource, policy, digest, revision, occurrence,
  supersession, and canonical UTC fields with conservative count/text bounds.
- Define a closed snapshot-resource union for note, safe source, inert artifact
  version, and admitted domain-resource link references without content bytes,
  private owner payloads, storage locations, or execution controls.
- Canonicalize submission request identity so JSON object order is irrelevant,
  milestone mappings follow exact brief order, and evidence references have one
  stable contract-defined order and uniqueness rule.
- Implement immutable Assessment domain values and pure policy that validates
  exact source agreement, learning origin, milestone closure, snapshot
  membership, resource version/digest identity, duplicate/unknown/missing
  references, and bounded server metadata for accepted evidence/event/history.
- Produce stable safe denial codes and ordered learner-actionable issue records
  that never echo artifact content, credentials, paths, private identifiers,
  stack traces, provider data, or another learner's facts.
- Add approved, boundary, reordered, Unicode, flexible-count, stale, expanded,
  malicious, and cross-record fixtures plus contract and unit tests.
- Document ownership, canonicalization, compatibility, non-authority, and
  downstream packet interfaces in the Assessment and contract architecture.

## Out of Scope

Any repository, database migration, transaction, application service,
Project/Content/Curriculum gateway, protected API, OpenAPI shape, generated
client, host composition, learner session, authorization, retry lock,
occurrence allocation, durable supersession, outbox persistence, Learner-model
projection, Audit append, browser, production bundle, live qualifier, external
provider, Portfolio behavior, execution, active preview, qualitative grading,
mastery/competency inference, instructor review, managed cloud, recovery,
external queue, notification, or separate AI mode.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | Project snapshot, Assessment practice, Content brief, Curriculum placement families | new Assessment Project schemas and compatibility corpus; learning contract index | Freeze additive external meaning and compatibility |
| Assessment core | domain values, contract adapters and ports | one new dependency-light domain module, parser/projector adapter, and port | Implement pure deterministic policy without runtime effects |
| Verification | existing conformance runners and Assessment unit suites | new focused contract runner/tests and pure-policy unit tests | Prove closure, flexibility, canonical identity, and safe denial |
| Architecture documentation | Assessment, Project submission, contract architecture | named contract documents and Assessment README | Record exact owners, limits, and later-packet seams |
| Planning | SLI-0032, WRK-0124, register | named planning artifacts | Retain current state and evidence |
| Runtime/API/UI | application, repositories, migrations, hosts, OpenAPI, client, browser | none | Remain later packet boundaries |

## Contracts and Interfaces

The snapshot-candidate document is a closed learner-safe input assembled later
from public Project, Content, and Curriculum facts. It binds one exact learner-
authorized Project and immutable snapshot to its learning origin, approved brief
and placement, ordered milestones, validation-policy version, and complete
closed resource-reference set. It contains neither artifact bytes nor mutable
workspace state.

The submission intent carries a public schema version, opaque submission ID,
the exact Project/snapshot and source selectors, and one mapping for every
milestone. Each mapping contains one or more exact candidate resource
references. It carries no learner ID, accepted sequence, evidence/event ID,
server time, authorization, score, completion, supersession, or mutable
revision authority.

Pure validation returns either ordered bounded issues or an accepted immutable
candidate with a canonical request fingerprint. Later server metadata produces
one evidence record and one safe `assessment.project.completed@1.0.0` event.
The event/history shapes expose source and closure provenance but omit artifact
bytes, environment secrets, private authorization, host/storage facts, and
qualitative claims. A later occurrence may reference a prior submission ID;
this contract never authorizes mutation of the prior record.

The adapter consumes bytes or JSON-compatible documents and returns immutable
domain values. It performs no clock, UUID, persistence, network, Project,
Content, Curriculum, Learner-model, Audit, host, or filesystem operation.
Later packets depend only on these values and the port, never on fixtures or
the conformance runner.

## Dependencies and Parallel Safety

SLI-0031 supplies the accepted immutable Project snapshot and public Project
boundary. This packet has no active packet dependency inside SLI-0032. It owns
the new schemas, policy, fixtures, and shared Assessment/contract documentation,
so it is not parallel-safe with later persistence, event-consumer, API, or
browser work until the exact contract is accepted and complete.

Downstream JIT-B must consume the accepted candidate/evidence/event values and
cannot redefine validation. JIT-C consumes only the safe event/replay meaning.
JIT-D consumes only the reviewed generated client. JIT-E qualifies all of them.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete closure | one learning snapshot candidate with every exact milestone and closed resource set | a submission maps each milestone to included evidence | pure validation accepts one immutable candidate and stable fingerprint | contract/unit |
| Flexible valid shape | 1-20 milestones, varied resource kinds/counts/order, Unicode safe text, optional provenance, IDs, and canonical times | schemas and policy parse/project records | valid meaning is preserved without fixture-count or ASCII assumptions | compatibility/unit |
| Canonical identity | equivalent object order and permitted mapping/reference order variants | fingerprints are calculated | contract-defined equivalents share one fingerprint and changed meaning does not | vector/unit |
| Missing or duplicate milestone | a milestone is omitted, repeated, or unknown | validation runs | ordered safe issues identify only bounded milestone references and nothing is accepted | denial/unit |
| Invalid resource | evidence is absent from the snapshot, duplicated, stale, wrong kind/version/digest, live-only, or cross-project | validation runs | the exact safe issue is returned without content or private facts | denial/unit |
| Source mismatch | Project origin, brief, placement, package, curriculum, or snapshot selectors disagree | validation runs | stale-source failure is bounded and no fall-forward occurs | compatibility/unit |
| Independent origin | the candidate is not learning-started | parsing or validation runs | submission is refused without inventing learning meaning | denial/unit |
| Private/active expansion | a document adds learner authority, private payload, content bytes, paths, execution, provider, network, secret, score, mastery, or advice fields | schema/policy runs | the record fails closed | malicious corpus |
| Evidence/event correlation | accepted validation plus valid bounded server metadata exists | evidence and event projectors run | exact source, snapshot, mapping, fingerprint, IDs, occurrence, and time agree and private fields remain absent | contract/unit |
| Supersession representation | a later occurrence names a prior submission | history validation runs | both immutable records remain ordered and the forward reference cannot rewrite earlier evidence | contract/unit |
| Existing compatibility | accepted knowledge-check, practice, and Project workspace corpora run | the additive family is present | all existing records and digests remain unchanged | regression |

## Verification Commands

Run the new Assessment Project conformance suite and pure-policy unit tests;
existing Assessment knowledge-check and practice contract/unit suites; Project
workspace contract/domain tests; schema validation and canonical digest/vector
checks; backend architecture and compile checks; security and dependency checks;
documentation, planning, and whitespace integrity; exact-candidate affected
verification; `python dev-tools/agent/check_ready.py`; and one independent
technical review.

Use the prepared Python runtime. Do not claim PostgreSQL, API, browser, or live
qualification in this packet because those boundaries are explicitly deferred.

## Documentation and Evidence Update

Record the exact additive schemas, supported bounds and unions, canonical
fingerprint rule, deterministic validation matrix, denial codes, event/history
privacy, inherited Project/Content/Curriculum facts, unchanged existing
contract families, checks, exact candidate receipt, independent review, and
residual downstream work. Reconcile only the named Assessment and contract
documents; do not claim runtime delivery.

## Stop Conditions

Stop for ambiguous milestone or resource ownership; need to change an accepted
Project snapshot, brief, or placement contract incompatibly; qualitative or
AI/instructor grading; mastery/competency or advice meaning; artifact bytes or
execution controls in Assessment; client-owned learner/time/authorization/
occurrence/completion/supersession; cross-module imports or persistence access;
provider, Portfolio, tenancy, cloud, recovery, queue, external-action, legal,
or commercial choice; unbounded record size; active scope collision; stale CAP
package; or material CAP-0007/SLI-0032 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
or nonfunctional styling. Fix it locally when in scope or defer optional
cleanup to CAP-0031.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0124`; exact candidate and receipt; contract
family and stable denial codes; deterministic policy and canonical identity;
flexible-shape and malicious-denial evidence; unchanged existing contract
digests; architecture/security results; changed files; documentation impact;
assumptions; and residual JIT-B through JIT-E work. Confirm that no persistence,
API, browser, projection, provider, execution, qualitative grading, mastery,
advice, cloud profile, external action, or AI-specific authority was added.

## Planning History

- 2026-10-17: Authored just in time as the first SLI-0032 packet. It freezes
  the additive Assessment Project submission and evidence language plus pure
  deterministic closure policy before any stateful or user-interface layer can
  invent requirement, completion, or supersession meaning. The scope conforms
  to CAP-0007 and exposes no new decision gate.
