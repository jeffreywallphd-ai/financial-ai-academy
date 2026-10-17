---
id: WRK-0139
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0072
capability: CAP-0017
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/personal-workspace/v1/learning-reference.schema.json", "contracts/learning/personal-workspace/v1/workspace.schema.json", "contracts/learning/personal-workspace/v1/mutation-intent.schema.json", "contracts/learning/personal-workspace/v1/workspace-query.schema.json", "contracts/learning/personal-workspace/v1/workspace-query-result.schema.json", "contracts/learning/personal-workspace/v1/README.md", "contracts/compatibility/personal-workspace/v1", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/domain/workspace.py", "backend/src/financial_ai_academy/modules/personal_workspace/public.py", "backend/src/financial_ai_academy/modules/personal_workspace/ports/workspace_contract.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/workspace_contract.py", "backend/tests/contract/personal_workspace/test_personal_workspace_contract.py", "backend/tests/unit/personal_workspace/test_workspace_contract.py", "docs/architecture/contracts/personal-workspace-contract.md", "docs/planning/vertical-slices/SLI-0072-search-and-refresh-saved-references.md", "docs/planning/work-packets/WRK-0139-freeze-saved-reference-query-refresh-contracts.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 43528ad1aa6e31a058389ab600ec6b72532b4b59
claim_id: WRK-0139:464525e1-58f1-4345-b2ed-bdbaf1ffa04a
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T14:48:45Z
---

# Agent Work Packet: Freeze Saved-Reference Query and Refresh Contracts

## Objective and Deliverable

Deliver the transport-neutral contract and pure-core seam for SLI-0072. Extend
the versioned Personal-workspace family with closed reference status,
deterministic record-query/result, continuation, and server-enriched
`refresh_reference` intent shapes; implement pure search/filter/sort/page and
status-transition behavior; and prove compatibility, confidentiality,
provenance, and anti-rigidity without adding persistence, host API, generated
client, browser, owner-gateway orchestration, or live topology behavior.

The result must leave one exact typed input/output contract for WRK-0140 to
compose through public owner adapters, PostgreSQL, and the protected API.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed baseline, architecture-
contracts, API/security, testing-quality, and delivery-planning context;
change-impact matrix; decision-readiness register; ADR-0012 and ADR-0021;
CAP-0017; SLI-0072; completed SLI-0071; the Personal-workspace executable
schemas, compatibility fixtures, domain/public/contract ports and adapter,
focused tests, contract guidance, and nearest READMEs.

## Decisions and Assumptions

- Existing Curriculum and Project reference kinds are the complete source union
  for this packet. A later domain adapter requires its own accepted owner
  contract and additive packet; no generic untyped reference is introduced.
- `target_status` admits exactly `available`, `stale`, and `unavailable`.
  Missing, removed, denied, adapter-absent, and source-outage causes are never
  encoded separately in the public/stored reference.
- Querying is pure over one already-authorized learner workspace. It never
  calls a source owner and cannot mutate status, validation time, order, or
  revision.
- Search normalization is deterministic, locale-independent, Unicode-safe, and
  bounded. It covers learner-authored title/body/label plus already-retained
  safe target title/path/identifier facts; it never indexes external content.
- `refresh_reference` carries only the record ID at the contract/core seam.
  The application layer in WRK-0140 will derive the selector and owner result;
  caller-supplied replacement facts or statuses remain impossible.
- Continuation material is opaque outside the module and bound to workspace
  revision plus canonical query digest. The pure core may use an encoded stable
  position, but must validate it as untrusted input and disclose no learner or
  target data.
- Existing `1.0.0` workspace and reference documents remain valid. Additive
  status values and new query schemas do not require eager rewrite or a
  persistence migration.

## In Scope

- Extend learning-reference, workspace, and mutation-intent schemas and Python
  values for the closed status enum and server-enriched refresh operation.
- Add closed versioned query and result schemas with bounded normalized text,
  enum filters, collection membership, stable sort, page size, opaque
  continuation, workspace revision, canonical query digest, records, and next
  continuation.
- Define immutable Python query, result, filter, sort, continuation, refresh,
  and status-transition values at the domain/public boundary needed by the next
  packet, without wiring them to a host or repository.
- Implement pure query behavior in the Personal-workspace contract adapter:
  exact normalization, AND-composed filters, deterministic sort, record-ID
  tie-break, bounded page, query digest, and continuation validation.
- Implement pure refresh-result application that accepts only a trusted
  application-supplied exact replacement or confidential status outcome,
  preserves record kind/ID and learner-authored fields, retains historical safe
  facts on non-available outcomes, updates validation time, increments the
  workspace revision once, and leaves collections/order intact.
- Define immutable-identity comparison rules for both Curriculum reference
  kinds and all three Project reference kinds. Mutable Project-workspace safe
  facts may refresh; package/snapshot/artifact identity or digest drift becomes
  stale and never silently replaces historical meaning.
- Add valid and invalid compatibility fixtures for legacy available documents,
  stale/unavailable references, queries, results, continuations, refresh
  intents, private fields, unsupported enums, unsafe text, and shape/bound
  violations.
- Add parameterized/property-style coverage for empty/full workspaces, Unicode,
  mixed record/source/reference/status/archive/collection filters, varied
  counts/order/ties, cursor tampering/revision/query mismatch, exact status
  transitions, no-op versus accepted changes, and additive safe fields.
- Update direct executable-contract and module documentation plus this packet,
  SLI-0072, and the planning register.

## Out of Scope

Application service orchestration; deriving selectors from stored references;
Curriculum/Project public calls; gateway changes; PostgreSQL adapter or
migration; replay repository; FastAPI route/model/authorization; OpenAPI;
generated TypeScript client; browser search/filter/status/refresh; live
browser/headless/restart evidence; new domain adapter; target event subscriber;
background refresh; external search service; learner identity/auth changes;
artifact content/preview/download/execution; export/deletion; backup/recovery;
managed cloud; provider/model; dependency or lockfile change; styling.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | Current v1 reference/workspace/mutation schemas and fixtures | listed schemas, two new query schemas, compatibility fixtures and README | Freeze additive status, query/result, and refresh shapes |
| Pure model | Existing immutable references, records, workspace, and mutations | domain workspace and public values | Represent exact query, refresh, and status outcomes without framework/provider coupling |
| Contract port/adapter | Current parser/projector/mutation core | listed port and adapter | Implement deterministic query and trusted refresh-result application |
| Focused evidence | Current contract and pure-core suites | two listed test files | Prove compatibility, invariants, denial, confidentiality, and anti-rigidity |
| Guidance | Current Personal-workspace contract/module docs | listed Markdown | Record frozen meanings and next-packet boundary |
| Planning | SLI-0072, WRK-0139, register | listed planning files | Keep JIT packet lifecycle and handoff synchronized |

No application service, source gateway, repository, migration, host, API,
OpenAPI, generated client, web, deployment, provider, or control-plane file may
change.

## Contracts and Interfaces

The query request is closed over optional normalized `text`, zero-or-more
closed filters for `record_kind`, `owner_module`, `reference_kind`,
`target_status`, archive state, and collection ID, one stable sort, `limit`
bounded to 1-100, and an optional opaque continuation. Missing filters mean all
values; empty arrays, duplicate values, unknown values/fields, unsafe text,
over-limit values, and invalid collection identities fail closed.

The result carries schema version, workspace revision, canonical query digest,
the normalized applied query, at most the requested number of complete
workspace-owned records, and an optional continuation. It cannot carry learner
identity, session, permission, source content, private target fields, storage
locations, credentials, or provider material. Stable order always includes
record ID as the final tie-break.

`refresh_reference` in the mutation intent contains only `operation` and
`record_id`. The external command in WRK-0140 will add only existing request
envelope fields: schema version, idempotency key, and expected workspace
revision. The trusted pure operation receives one of:

- an exact resolved reference whose selector identity matches the retained
  reference;
- `stale` when immutable meaning differs; or
- `unavailable` for every confidential source failure.

Available refresh may update safe mutable Project-workspace facts and
validation time. Immutable Curriculum publication/package, Project snapshot,
and Project artifact meaning must match exactly; otherwise the original facts
remain and status becomes stale. Non-available outcomes retain all historical
safe facts, change only status and validation time, and never expose a source
route as actionable presentation authority.

## Dependencies and Parallel Safety

SLI-0071 is complete and supplies the accepted five-kind reference union,
versioned aggregate, public-owner adapter pattern, and live containment
evidence. WRK-0139 owns shared schemas, domain values, contract adapter, and
their tests, so it is not parallel-safe with another Personal-workspace packet.
WRK-0140 cannot start until this packet freezes the exact seam.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Legacy compatibility | Existing `1.0.0` available workspace/reference fixtures | New parsers project and parse them | They remain byte-canonical without eager rewrite | contract fixtures |
| Mixed deterministic query | A varied workspace with notes/bookmarks and Curriculum/Project targets | Text, filters, collection, sort, and limit compose | Only matching records appear in stable order with an exact digest | unit/contract |
| Safe continuation | More matches exist than the page bound | A valid continuation is used | The next stable records appear with no duplicate or omission | unit/property |
| Tampered continuation | Learner/query/revision/position material is invalid or changed | The continuation is parsed | The query fails generically without partial or old records | contract/unit |
| Current mutable Project | An exact Project workspace replacement preserves identity | Trusted refresh is applied | Safe mutable facts and validation time update and status stays available | unit |
| Changed immutable source | Package, snapshot, or artifact immutable meaning differs | Trusted refresh compares it | Historical facts remain and status becomes stale | unit/property |
| Confidential failure | A source is missing, denied, removed, absent, or unavailable | The trusted application supplies unavailable | Only unavailable and validation time change; no cause is stored | unit/contract |
| Recovery | A stale/unavailable reference later resolves to the exact immutable target | Refresh is applied | It becomes available without losing record/collection/order/provenance | unit |
| Refresh containment | A record belongs to notes and multiple collections | Any status transition runs | Learner text, record ID, membership, order, other records, and source state do not change | unit/property |
| Invalid caller shape | A refresh includes selector, status, timestamp, replacement fact, learner, or private field | Schema parsing runs | The request is rejected before pure mutation | contract/security |
| Anti-rigidity | Valid Unicode, varied IDs/titles/statuses/counts/order and additive safe data are used | Contract and query suites run | Invariants hold without one fixture, count, order, wording, or future adapter | parameterized/property |

## Verification Commands

Run:

```text
python -m pytest backend/tests/contract/personal_workspace/test_personal_workspace_contract.py backend/tests/unit/personal_workspace/test_workspace_contract.py -q
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0139-freeze-saved-reference-query-refresh-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python -m compileall -q backend/src backend/tests
git diff --check
python dev-tools/agent/check_ready.py
```

Run a clean exact-candidate affected-check plan and obtain a fresh qualifying
receipt plus one independent technical disposition. Use a repository-local
writable temp root when the Windows sandbox temp location rejects fixture
creation. Do not escalate this pure packet to a live database/browser suite
without a concrete shared-impact reason.

## Documentation and Evidence Update

Document the exact status meanings, searchable fields, normalization, filters,
stable sorts, page/cursor semantics, query digest, refresh input, immutable-
identity rules, historical-fact retention, non-actionable unavailable/stale
destination, confidentiality collapse, optional-adapter isolation, compatibility,
and the frozen WRK-0140 handoff.

Completion evidence records the exact candidate and receipt, schema/fixture
counts, focused tests, negative/private-field cases, anti-rigidity corpus,
architecture/security/affected/aggregate results, changed files, migration
impact, assumptions, checks not run, and residual gaps. Approval and reviewer
records remain ignored local state.

## Stop Conditions

Stop for a new source kind or live domain adapter; unresolved target ownership;
generic untyped reference; differentiated missing/denied/removed state;
caller-controlled status, owner, selector, timestamp, replacement, learner, or
permission; silent immutable-source advance; source content or private facts;
cross-module persistence; repository/migration/API/client/UI change; external
search dependency; background polling/events; artifact execution; managed-
cloud/provider/model decision; dependency change; active scope collision;
canonical conflict; stale CAP package; or material SLI/CAP drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish.

## Required Handoff

Report `CAP-0017.SLI-0072.WRK-0139`; exact candidate and receipt; status/query/
result/continuation/refresh shapes; searchable safe fields; normalization and
stable-order rules; immutable identity and confidential status transitions;
legacy compatibility; anti-rigidity, architecture, security, affected,
aggregate, and independent-review results; changed files; documentation and
migration impact; assumptions; unqualified checks; and residual gaps. Confirm
no application/gateway/persistence/API/OpenAPI/client/browser/live/new-adapter/
execution/provider behavior changed, then leave WRK-0140 dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0072 refinement. The packet
  freezes the additive query, continuation, status, and refresh pure-core seam
  while preserving legacy documents and leaving owner orchestration,
  persistence/API/client, browser, and live qualification to later packets. No
  lower-level approval is required.
- 2026-10-17: Activated from recorded base `43528ad` after validating the
  approved parent package, completed dependency, bounded contract/core scope,
  resolved decisions, and no active coordination overlap.
