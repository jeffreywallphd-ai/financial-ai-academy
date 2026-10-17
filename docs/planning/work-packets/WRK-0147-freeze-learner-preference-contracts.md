---
id: WRK-0147
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/preference_contract.py", "backend/src/financial_ai_academy/modules/learner_model/domain/preferences.py", "backend/src/financial_ai_academy/modules/learner_model/ports/preference_contract.py", "backend/tests/contract/learner_preferences", "backend/tests/unit/learner_model/test_preference_contract.py", "backend/tests/unit/learner_model/test_preferences.py", "contracts/compatibility/learner-preferences/v1", "contracts/learning/README.md", "contracts/learning/learner-preferences/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/learner-preferences-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0147-freeze-learner-preference-contracts.md"]
generated_artifacts: []
base_revision: 3aa5454cdb579faaceb0b281b3c6775e46853d54
claim_id: WRK-0147:71878a44-391f-4e67-a17a-470aa8866608
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T18:20:51Z
---

# Agent Work Packet: Freeze Learner Preference Contracts

## Objective and Deliverable

Freeze an additive `learner-preferences/v1` contract family and pure Learner-
model core for explicit learning goals, self-described experience, interests,
bounded change summaries, reset, and export. Deliver executable JSON Schemas,
a synthetic compatibility corpus, deterministic conformance evidence,
immutable framework-free domain values, closed mutation semantics, canonical
hashing, and a transport-neutral parser/projector port and adapter.

The result is the stable input to the later persistence/API packet. It creates
no database row, learner session, permission, HTTP operation, generated client,
browser route, recommendation, evidence, inferred trait, provider call, or
external action.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contracts, interface-design, security-risk, testing-quality, and
delivery-planning context. Read the change-impact matrix, decision readiness,
CAP-0018, SLI-0074, ADR-0005, the adaptive-pathway architecture, module map,
contract architecture and compatibility/versioning guidance, identity-provider
contract, current Learner-model domain and public seams, nearest module/
contract/test READMEs, and the concurrent-work protocol.

## Decisions and Assumptions

- Add a separate `learner-preferences/v1` family inside Learner model rather
  than widening completion, practice-history, project-completion, Curriculum,
  Assessment, Adaptation, Identity, or Personal-workspace contracts.
- All stored semantic values are explicit learner input. No activity,
  assessment, browser, model, provider, or third-party data is used to infer a
  goal, experience level, interest, demographic, health condition, disability,
  financial situation, competency, or protected trait.
- A current profile contains server-owned profile/learner identity, positive
  revision, ordered goals, ordered experience entries, ordered interests,
  canonical creation/update times, and one lowercase SHA-256 digest.
- A goal has server-owned identity, a learner title of at most 160 characters,
  optional detail of at most 2,000 characters, active/archived state, and
  canonical times. It is an intention, not a requirement, commitment, evidence,
  recommendation, or competency claim.
- An experience entry has server-owned identity, a learner-named subject of at
  most 120 characters, one explicit self-description (`new`,
  `some_experience`, or `experienced`), optional detail of at most 1,000
  characters, and canonical times. The label is not a score or verified level.
- An interest has server-owned identity, one learner label of at most 120
  characters, and canonical times. Labels are preserved as entered after
  bounded whitespace validation; no taxonomy or semantic classification is
  inferred.
- Initial quotas are 20 goals, 20 experience entries, and 50 interests. They
  bound local storage and review while allowing empty and varied valid shapes.
- A mutation intent contains one idempotency key, exact expected revision, and
  a closed operation. Create operations omit server IDs/times. Update,
  archive/restore, remove, and reorder operations reference exact existing
  profile-owned IDs. Reset accepts no replacement profile and clears only this
  preference profile in the next revision.
- Change history contains at most 100 append-oriented summaries with revision,
  operation kind, affected object kind/ID where applicable, canonical time,
  and resulting digest. It never copies previous private text or becomes Audit,
  Assessment evidence, or an immutable legal-consent ledger.
- Export contains the current profile, bounded change summaries, schema and
  purpose/limitation metadata. It excludes session, permission, storage,
  provider, hidden profile, evidence, scoring, recommendation, experiment,
  financial, and inferred fields.
- Canonical JSON hashing uses compact sorted-key direct UTF-8 bytes, excludes
  the digest field itself, and performs no implicit Unicode normalization or
  ASCII escaping. Synthetic fixed vectors cover ASCII and non-ASCII input.
- Pure parsing, projection, hashing, and mutation application have no database,
  identity/session, authorization, clock, network, provider, event, AI,
  filesystem, random, Curriculum, Assessment, Adaptation, or target mutation.

## In Scope

- Add Draft 2020-12 schemas for profile values, mutation intents, change-
  history results, and portable export under one versioned contract family.
- Add synthetic valid examples, fixed canonical-digest vectors, compatibility
  fixtures, and table-driven denial cases for unsupported versions/operations,
  extra private fields, malformed or duplicate IDs, invalid ordering,
  chronology, quota overflow, stale/dangling selectors, contradictory state,
  hidden inference/evidence/policy meaning, and forbidden implementation data.
- Add a dependency-light contract runner that validates schema versions,
  closed object shapes, canonical digest, profile closure, order uniqueness,
  lifecycle, history correlation, export correlation, bounds, and confidential
  shape without requiring the application host or database.
- Introduce immutable framework-free Learner-model preference values,
  canonical serialization/hashing, deterministic profile projection, and pure
  mutation application with explicit server-fact input.
- Add a narrow parser/projector port and adapter that maps JSON-compatible
  bytes and values to the pure domain contract without FastAPI/Pydantic/
  PostgreSQL dependencies.
- Add focused contract and unit tests for empty/populated profiles, every
  operation, reset, export, history bounds, exact replay-ready projections,
  quotas, chronology, confidentiality, Unicode hashing, and anti-rigidity
  across wording, optional detail, counts, order, IDs, and times.
- Document Learner-model ownership, explicit-versus-inferred meaning, contract
  invariants, privacy/authority limits, canonical hashing, and later consumer
  obligations. Synchronize module guidance, contract catalog, architecture
  map, parent slice, packet, and planning register.

## Out of Scope

Application services; learner-context or permission composition; repositories;
PostgreSQL; migrations; idempotency persistence; clocks/ID generators; public
facade operations; HTTP/FastAPI/Pydantic; OpenAPI; generated clients; browser
UI/storage; theme/accessibility/AI/notification preferences; Curriculum
references; Assessment evidence; competency/mastery projections; Adaptation or
recommendations; model/provider calls; inferred traits; collaboration;
organizations/tenancy; consent ledgers; external notifications; files/uploads;
managed cloud; export transport/download; backup/restore; audit events;
dependency or lockfile changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing learning, Personal-workspace, project, and compatibility families | new `learner-preferences/v1` and compatibility directories plus learning contract catalog | Freeze additive explicit learner preference meaning without widening evidence or target owners |
| Contract evidence | dependency-light runners, canonical digest vectors, closed-union and confidentiality denials | new learner-preference runner, fixtures, and focused tests | Prove closure, correlation, hashing, privacy, bounds, and anti-rigidity |
| Learner-model core | current completion/practice/project domain conventions and public direction | new `preferences.py`, preference contract port/adapter, focused unit tests, bounded README update | Establish inward-pointing typed meaning without application/persistence |
| Architecture guidance | module map and contract ownership | new learner-preference contract page plus bounded catalog/map updates | Record explicit preference ownership and prohibited evidence/policy authority |
| Planning evidence | SLI-0074, WRK-0147, register | listed planning files | Keep lifecycle and next accepted seam synchronized |

No existing completion, practice, project, Curriculum, Assessment, Adaptation,
Identity, or Personal-workspace schema/fixture/implementation; public facade;
OpenAPI/client; persistence/migration; UI; dependency; provider; or deployment
composition may change.

## Contracts and Interfaces

`learner-preference-profile-v1` is one closed document containing exact server
identity/revision/time facts and ordered closed values. Profile identity and
learner identity are distinct bounded identifiers. Goal, experience, and
goal, experience, and interest IDs are unique across the complete profile so
generic change references remain unambiguous; every order list is complete
and duplicate-free. Archived goals remain in goal order until removed. Empty
sections are valid.

`learner-preference-mutation-intent-v1` contains an idempotency key, exact
expected revision, and one closed operation. Supported goal operations create,
update, archive, restore, remove, and reorder. Experience supports create,
update, remove, and reorder. Interest supports create, rename, remove, and
reorder. `reset_profile` has no replacement payload. Create operations accept
learner text but no ID, learner, revision, time, history, or digest. Mutations
cannot change object kind or another module's state.

`learner-preference-history-v1` contains ordered change summaries whose
revisions are positive, unique, increasing, and no newer than the current
profile. `learner-preference-export-v1` binds the exact current profile and
history to explicit purpose, limitations, export schema version, and canonical
export time. A history record identifies the resulting profile digest; it does
not contain prior private values.

The pure mutation function receives a validated current profile, validated
intent, and an explicit server-fact bundle containing canonical time and any
required new object ID. It returns the next profile plus its change summary or
a stable bounded `learner_preferences.*` error. Reapplying an accepted intent
is an application/repository responsibility in the next packet; the pure core
is deterministic for identical accepted inputs and never manufactures time or
identity.

The parser/projector port accepts JSON-compatible bytes/values and returns
immutable preference values or stable safe contract errors. The later packet
may persist and expose these values but may not reinterpret explicit input as
evidence, inference, eligibility, permission, recommendation, or consent.

## Dependencies and Parallel Safety

CAP-0001 and CAP-0017 are complete; CAP-0018 authority is current; SLI-0074 is
ready; and accepted Learner-model ownership resolves this bounded seam.
WRK-0147 has no WRK dependency. It owns the new contract family and shared
Learner-model/architecture/planning files, so it is not parallel-safe with
another packet changing those paths. It must complete before JIT-B is reserved
or authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty profile | Valid server identity, revision, and times with empty sections | Profile parsing/projecting runs | One deterministic empty profile round-trips with exact digest and no write | schema/runner/unit |
| Explicit values | Varied valid Unicode goals, experience entries, interests, optional detail, ordering, and archive state | Validation and projection run | Learner wording and exact explicit meaning round-trip without classification or evidence | schema/runner/unit |
| Closed mutations | Each supported operation has complete learner input/selectors plus explicit server facts | Intent parsing and pure mutation run | One deterministic next profile and change summary result; unknown/partial operations fail closed | schema/unit |
| Reset | A populated profile receives `reset_profile` | Pure mutation runs | Only profile-owned sections become empty in the next revision; a non-content history summary records reset | unit/contract |
| History and export | Current profile and bounded correlated summaries are supplied | History/export projection runs | Revisions, result digests, purpose, limitations, and export time correlate without prior private text or internal data | schema/runner/unit |
| Canonical digest | ASCII and non-ASCII profiles differ only by documented meaning | Independent and production hashing run | Compact sorted direct UTF-8 bytes produce fixed lowercase digests without implicit normalization | vectors/runner/unit |
| Bounds and closure | Values sit at valid edges and just beyond them | Validation runs | Valid edges pass; overflow, duplicate, dangling, incomplete order, chronology, and contradictory lifecycle fail specifically | parameterized tests |
| Confidential shape | Schemas, projections, exports, failures, and all nested values are scanned | Forbidden keys and meanings are inspected | No session, permission, storage, provider, inferred trait, score, evidence, mastery, eligibility, recommendation, consent, or financial field escapes | runner/security-focused unit |
| No side effects | Parser, projector, hashing, and mutation functions run repeatedly | Collaborators and process capabilities are inspected | No database, clock, random ID, network, filesystem, provider, event, AI, or other-module effect occurs | unit/architecture |
| Anti-rigidity | Valid wording, Unicode, optional detail, empty/populated sections, counts, order, IDs, times, and compatible technical metadata vary | Complete focused corpus runs | Meaningful invariants hold without exact prose, fixture count, incidental ordering, generated-value, or UI assumptions | parameterized contract/unit |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_preferences backend/tests/unit/learner_model/test_preference_contract.py backend/tests/unit/learner_model/test_preferences.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0147-freeze-learner-preference-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run the affected-check plan and any focused contract-catalog or architecture
regression it selects. Submit one exact candidate, create a fresh qualifying
receipt, and obtain one independent technical disposition. Add no dependency
or lockfile change.

## Documentation and Evidence Update

Document explicit-versus-inferred meaning, Learner-model ownership, profile and
mutation shapes, history/export limitations, canonical hashing, quotas, safe
failures, confidentiality, and unchanged evidence/policy owners. Keep the
module README, contract architecture, module map, contract catalog, SLI-0074,
WRK-0147, and register synchronized.

Completion evidence records exact focused and affected checks, compatibility,
confidentiality and anti-rigidity meaning, changed files, assumptions,
environment qualifications not performed, and residual risks. Verification
receipts and technical review records remain only in ignored local control-
plane storage; tracked files contain no approval or reviewer metadata/history.

## Stop Conditions

Stop for ambiguous Learner-model ownership; widening an existing contract
family; inferred/hidden profiling; medical/protected-trait meaning; preferences
as evidence, competency, mastery, eligibility, permission, grade, credential,
recommendation, experiment consent, financial suitability, or irreversible
action; persistence/API/UI change; server identity/time generated inside the
pure core; another module's internal state; collaboration/tenancy; provider,
network, secret, model, or external-notification use; file/execution semantics;
new dependency; private-data leakage; conflicting canonical sources; active
scope collision; or material CAP-0018/SLI-0074 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; contract identifiers and limits; profile, goal,
experience, interest, mutation, reset, history/export, digest,
confidentiality, and denial invariants; focused, architecture, security,
affected, aggregate, receipt, and independent-review results; changed files;
documentation impact; assumptions; unqualified environment checks; and
residual gaps. Confirm that no persistence, migration, public application or
HTTP operation, OpenAPI/generated client, browser UI, theme/accessibility/AI/
notification preference, evidence/competency state, recommendation, inferred
trait, provider, external action, or execution behavior changed. Leave JIT-B
dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0074 refinement. The packet
  freezes the additive explicit learner-preference contract and pure Learner-
  model core while leaving persistence/API, UI, and live qualification to
  dependency-ordered packets. It conforms to the current CAP-0018 package and
  requires no lower-level approval.
- 2026-10-17: Moved to exact-candidate verification after 73 focused Learner-
  model tests, 17 architecture checks, 10 security control groups, planning,
  documentation, whitespace, and all 29 aggregate readiness checks passed.
