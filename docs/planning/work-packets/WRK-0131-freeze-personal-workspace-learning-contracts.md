---
id: WRK-0131
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0070
capability: CAP-0017
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/__init__.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/__init__.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/workspace_contract.py", "backend/src/financial_ai_academy/modules/personal_workspace/domain/__init__.py", "backend/src/financial_ai_academy/modules/personal_workspace/domain/workspace.py", "backend/src/financial_ai_academy/modules/personal_workspace/ports/__init__.py", "backend/src/financial_ai_academy/modules/personal_workspace/ports/workspace_contract.py", "backend/tests/contract/personal_workspace", "backend/tests/unit/personal_workspace", "contracts/compatibility/personal-workspace/v1", "contracts/learning/README.md", "contracts/learning/personal-workspace/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0070-save-learning-notes-bookmarks-collections.md", "docs/planning/work-packets/WRK-0131-freeze-personal-workspace-learning-contracts.md"]
generated_artifacts: []
base_revision: ad3caacfa925064ac1e5705a36ef894fe3b65ea2
claim_id: WRK-0131:81f47bea-6814-4247-8bda-366d54f7a34b
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T10:34:11Z
---

# Agent Work Packet: Freeze Personal Workspace Learning Contracts

## Objective and Deliverable

Freeze an additive versioned contract family and pure Personal-workspace core
for learner-owned notes, bookmarks, collections, and exact approved-learning
references. Deliver executable schemas, a synthetic compatibility corpus,
deterministic conformance evidence, immutable domain values, closed mutation
semantics, and a transport-neutral parser/projector port and adapter. The
result is the stable input to the next persistence/API packet; it creates no
database row, session, HTTP operation, generated client, browser route, target-
module mutation, Project resource, or execution surface.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, architecture-contracts,
security-risk, interface-design, testing-quality, and delivery-planning
context. Read the change-impact matrix, decision readiness, CAP-0017, SLI-0070,
ADR-0021, ADR-0011, ADR-0012, the module map and dependency rules, contract
architecture and compatibility/versioning guidance, current Curriculum and
Content public seams, existing Project contract/parser patterns, the nearest
module/contract/test READMEs, and the concurrent-work protocol.

## Decisions and Assumptions

- Create a separate additive `personal-workspace/v1` contract family rather
  than widening Curriculum, discovery, lesson-package, Project, Assessment, or
  Learner-model contracts. Personal workspace owns learner organization only.
- The initial learning-reference union has exactly two variants:
  - `learning_opportunity`, retaining exact Curriculum opportunity, placement,
    package, source-fingerprint, safe destination, availability, and
    publication provenance; and
  - `placed_lesson`, retaining exact Curriculum placement, package, safe
    destination, and publication provenance.
- A reference is an accepted safe snapshot of exact public identity and
  provenance facts. It is not the target body, permission, enrollment,
  eligibility, completion, evidence, or an instruction to fetch a URL.
- Workspace records are exactly `note` and `bookmark`. Notes own bounded title
  and body text plus one target. Bookmarks own one target and an optional
  bounded learner label. Collections own bounded titles and ordered unique
  member record IDs; they do not copy member or target state.
- One workspace has stable server-owned workspace and learner IDs, positive
  revision, ordered records and collections, canonical UTC creation/update
  times, and a deterministic digest. An empty workspace is a valid revision-one
  view for later side-effect-free reads.
- The mutation contract is a closed union for create/update note, create/update
  bookmark, create/rename/remove collection, set collection members, reorder
  records, archive/restore record, and remove record. It carries one
  idempotency key and exact expected revision. IDs, learner, canonical time,
  accepted source facts, next revision, and digest remain server authority.
- Initial semantic limits are 200 total records, 50 collections, 100 members
  per collection, 120 characters for learner titles/labels, and 8,000
  characters for note body text. Identifiers and destinations are normalized
  bounded platform strings; digests are lowercase SHA-256.
- The pure parser/projector validates closure, correlation, membership,
  ordering, timestamps, digest, bounds, and confidential shape. It performs no
  persistence, identity/session resolution, authorization, source lookup,
  clock, network, provider, event, target mutation, artifact, AI, or execution
  action.

## In Scope

- Add Draft 2020-12 schemas for exact learning references, note/bookmark
  records, collections, workspace document, and mutation intents under one
  versioned Personal-workspace contract family.
- Add synthetic approved examples, fixed digest vectors including non-ASCII
  learner text, compatibility fixtures, and table-driven denial cases for
  unsupported, malformed, contradictory, duplicate, dangling, private-field,
  and target-payload meaning.
- Add a dependency-light contract runner that validates schema versions,
  canonical digests, reference correlation, record/collection closure,
  membership/order uniqueness, chronology, learner-safe projection, and
  absence of storage/provider/execution/target-state fields.
- Introduce immutable framework-free Personal-workspace domain values,
  mutation application, canonical hashing, and a narrow parser/projector port
  and adapter with inward-pointing dependencies.
- Add focused contract and unit tests for both reference kinds, notes,
  bookmarks, collections, every mutation kind, exact replay-ready canonical
  projection, bounds, confidentiality, Unicode hashing, and anti-rigidity
  across valid text, IDs, generated times, record counts, collection counts,
  memberships, and orderings.
- Add Personal-workspace contract/module guidance and synchronize the learning
  contract catalog, contract architecture, module map, parent slice, packet,
  and planning register.

## Out of Scope

Curriculum or Content implementation changes; source-resolution adapters;
application service/repository ports; persistence; migrations; clocks;
idempotency storage; identity/session/permission composition; HTTP/OpenAPI;
generated clients; UI; browser storage; Project workspaces/snapshots/artifacts;
broader domain reference kinds; search/filter; export/import; deletion policy
outside workspace-owned records; restore; audit events; active rendering;
files; execution; network/provider calls; credentials; collaboration;
organizations; managed cloud; AI mode; recommendations; mastery; grading;
financial advice; dependency or lockfile changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing learning, discovery, lesson-package, Project, and compatibility families | new `personal-workspace/v1` and compatibility directories plus learning contract catalog | Freeze additive learner-organization meaning without widening a target owner |
| Contract evidence | current dependency-light runners, canonical digest vectors, and closed-union denials | new Personal-workspace runner, fixtures, and focused tests | Prove closure, correlation, hashing, privacy, bounds, and anti-rigidity |
| Personal-workspace core | module conventions and Project immutable contract patterns | new module README, package markers, domain, port, adapter, and unit tests | Establish inward-pointing typed meaning and pure mutation behavior without application/persistence |
| Architecture guidance | module map and contract ownership | new Personal-workspace contract page plus bounded catalog/map updates | Record Personal workspace versus Curriculum/Content/Project authority |
| Planning evidence | SLI-0070, WRK-0131, register | listed planning files | Keep packet lifecycle and next accepted seam synchronized |

No existing learning schema or fixture, Curriculum/Content/Project/Assessment/
Learner-model implementation, OpenAPI/client, persistence, migration, UI,
dependency, generated artifact, provider, or deployment composition may change.

## Contracts and Interfaces

`personal-workspace-learning-reference-v1` is a closed discriminated union. A
learning-opportunity variant retains exact opportunity/placement/package
identity, package version/digest, source fingerprint, safe title/destination,
availability, and publication provenance. A placed-lesson variant retains
exact placement/package identity, package version/digest, safe title/
destination, and publication provenance. Both identify `curriculum` as owner
and contain no body nodes, objectives, eligibility, completion, learner state,
permission, credential, provider payload, or arbitrary locator.

`personal-workspace-v1` contains server-owned workspace/learner identity,
positive revision, ordered closed note/bookmark records, ordered collections,
canonical UTC times, and one deterministic digest. Note and bookmark records
retain immutable record kind/ID/creation time, current learner content,
accepted target, archive state, and update time. Collection membership refers
only to existing record IDs, is unique and ordered, and never owns a record.

`personal-workspace-mutation-intent-v1` carries one idempotency key, exact
expected revision, and one closed operation. Create operations do not accept a
server record/collection ID or canonical time. Update/archive/remove/reorder
operations reference existing IDs and cannot change record kind, learner,
workspace, or target authority. Projecting and parsing the same accepted
workspace is deterministic; canonical JSON uses compact sorted-key direct
UTF-8 bytes with no implicit Unicode normalization or ASCII escaping.

The parser/projector port accepts JSON-compatible bytes and returns immutable
workspace/mutation values or a stable bounded `personal_workspace.contract.*`
error with a safe code/reference. The next packet may compose source resolution
and persistence around these values but may not reinterpret their ownership,
closed variants, digest, membership, revision, or server-authority semantics.

## Dependencies and Parallel Safety

CAP-0001 and CAP-0007 are complete; CAP-0017 authority is current; SLI-0070 is
ready; and ADR-0021 resolves Personal-workspace ownership. WRK-0131 has no WRK
dependency. It owns the new contract family, module entry point, shared
architecture catalog/map, parent slice, and register, so it is not parallel-
safe with another packet changing those paths. It must complete before JIT-B
is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Opportunity reference | Exact approved opportunity and publication facts are supplied | Reference parsing/projecting runs | Every exact safe identity/provenance fact round-trips without body, permission, or learner state | schema/runner/unit |
| Placed lesson reference | Exact approved placement/package/publication facts are supplied | Reference parsing/projecting runs | The placed-lesson variant round-trips without an opportunity-only field or source body | schema/runner/unit |
| Note and bookmark | Bounded learner text and one valid target are supplied | Record validation runs | Immutable typed records retain content, target, archive state, and server facts | schema/runner/unit |
| Collections and order | Multiple records and collections have valid unique ordered membership | Workspace validation runs | Order and membership round-trip without copying member records | runner/unit |
| Closed mutations | Each supported operation has complete current selectors and bounded learner input | Intent parsing and pure mutation run | One deterministic next aggregate is produced; unknown/partial operations fail closed | schema/unit |
| Canonical digest | ASCII and non-ASCII workspaces differ only by documented meaning | Independent and production hashing run | Compact sorted direct UTF-8 bytes produce fixed lowercase digests without implicit normalization | vectors/runner/unit |
| Bounds | Record, collection, membership, title/label, body, ID, destination, and provenance values sit at accepted edges | Validation runs | Valid edges pass; zero/overflow/unsafe or duplicate/dangling values fail on the specific invariant | parameterized tests |
| Confidential shape | Contracts, projections, and failures are recursively inspected | Forbidden keys/value patterns are scanned | No body node, score, eligibility, learner projection, storage, session, credential, provider, execution, Project payload, or hidden target state escapes | runner/security-focused unit |
| Anti-rigidity | Valid Unicode text, IDs, record/collection counts, memberships, orderings, generated times, and harmless compatible metadata vary | Complete focused corpus runs | Meaningful invariants hold without fixture wording, exact count, incidental order, generated value, or presentation assumptions | parameterized contract/unit |
| Side-effect freedom | Parsers, projectors, hashing, and mutation application run repeatedly | Collaborators and process capabilities are inspected | No database, clock, network, provider, event, target mutation, artifact, AI, or execution effect occurs | unit/architecture |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0131-freeze-personal-workspace-learning-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run affected contract-catalog and architecture regressions selected by the
affected-check plan. Submit one exact candidate, create a fresh qualifying
receipt, and obtain one independent technical disposition. Add no dependency
or lockfile change.

## Documentation and Evidence Update

Document Personal-workspace ownership, both learning-reference kinds, closed
record/mutation meaning, exact provenance, canonical digest, limits, safe
failures, privacy, and unchanged target owners. Keep module guidance, contract
architecture, module map, contract catalog, SLI-0070, WRK-0131, and register
state synchronized.

Completion evidence must record exact focused and affected checks, contract
compatibility, confidentiality and anti-rigidity meaning, changed files,
assumptions, environment qualifications not performed, and residual risks.
Verification receipts and technical review records remain only in ignored
local control-plane storage; tracked artifacts contain no approval or reviewer
metadata/history.

## Stop Conditions

Stop for ambiguous Personal-workspace versus target ownership; a need to widen
an existing contract family; client-selected learner/ID/time/source authority;
target payload copying or permission grants; source resolution, persistence,
migration, API, client, or UI change; Project/domain adapter behavior; artifact
or arbitrary-file semantics; execution; network/secrets/providers; Assessment
or Learner-model meaning; collaboration; tenancy; cloud policy; AI-authority;
financial advice; new dependency; cross-module internals; private-data leakage;
conflicting canonical sources; active scope collision; or material CAP-0017/
SLI-0070 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, an incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; contract identifiers and limits; reference,
record, collection, mutation, digest, confidentiality, and denial invariants;
focused, architecture, security, affected, aggregate, and receipt results;
changed files; documentation impact; assumptions; unqualified environment
checks; and residual gaps. Confirm no source-resolution adapter, persistence,
migration, public application operation, HTTP/OpenAPI, generated client, UI,
Project/domain link, Assessment/Learner-model state, provider, AI mode, or
execution behavior changed, then leave JIT-B dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0070 refinement. The packet
  freezes the separate additive Personal-workspace family and pure module core
  for the two accepted learning-reference variants while leaving resolution,
  persistence, API, UI, Project/domain adapters, and execution to later
  packets or slices. No lower-level approval is required.
