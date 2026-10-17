---
id: WRK-0143
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0073
capability: CAP-0017
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/personal-workspace/v1/workspace-export.schema.json", "contracts/learning/personal-workspace/v1/README.md", "contracts/learning/README.md", "contracts/compatibility/personal-workspace/v1/valid-workspace-export.json", "contracts/compatibility/personal-workspace/v1/workspace-export-denials.json", "contracts/compatibility/personal-workspace/v1/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/domain/workspace.py", "backend/src/financial_ai_academy/modules/personal_workspace/ports/workspace_contract.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/workspace_contract.py", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/tests/contract/personal_workspace/test_personal_workspace_contract.py", "backend/tests/unit/personal_workspace/test_workspace_contract.py", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/contracts/personal-workspace-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0073-qualify-personal-workspace-durability-boundaries.md", "docs/planning/work-packets/WRK-0143-freeze-personal-workspace-export-quota-contracts.md"]
generated_artifacts: []
base_revision: 75dccce2b9938fed304386b6ec2e81bf2b25ec32
claim_id: WRK-0143:5860fa87-9352-4224-83dd-817dcbefc9af
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T16:42:17Z
---

# Agent Work Packet: Freeze Personal Workspace Export and Quota Contracts

## Objective and Deliverable

Deliver the first independently reviewable CAP-0017.SLI-0073 seam: a closed v1
Personal-workspace owner export envelope with canonical digest semantics,
explicit pure-contract quota outcomes for every accepted workspace limit, and
focused proof that existing record and collection removal cleans only
workspace-owned organization.

The completed packet leaves a transport-neutral contract and pure adapter that
the next packet can compose into application, PostgreSQL, protected API,
OpenAPI, and generated-client behavior. It changes no host, persistence,
browser, backup tool, target-domain state, or multi-module export workflow.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply its context routing, change-impact,
decision-readiness, contract, planning, exact-scope, and verification rules.

Read the current CAP-0017 package, SLI-0073, ADR-0021, ADR-0008, the Personal
Workspace contract and module README, the v1 schemas and compatibility corpus,
the pure contract port/adapter/domain implementation, focused contract/unit
tests, module-boundary tests, and the CAP-0019 boundary before editing. Stop if
those sources conflict or a managed-cloud, retention, erasure, or cross-module
portable-export choice becomes necessary.

## Decisions and Assumptions

- ADR-0021 authorizes one explicit versioned owner export view, bounded quotas,
  module-owned PostgreSQL state, removal semantics, and recovery participation.
- The export view is a complete authorized Personal-workspace projection for
  later composition. It is not a cross-module manifest, background job,
  downloadable archive, import, restore, credential, or permission grant.
- The envelope is closed over `schema_version`, `workspace_digest`,
  `generated_at`, and `workspace`. The digest is SHA-256 over the canonical
  compact sorted-key UTF-8 JSON workspace document.
- Exact quota codes distinguish record, collection, and collection-membership
  capacity from malformed input. Exact names may follow the module's existing
  bounded error convention, but their meanings must remain closed and
  independently testable.
- Existing `remove_record` and `remove_collection` operations are the selected
  deletion boundary. No whole-workspace physical purge, account erasure,
  retention interval, or recovery-copy deletion is inferred.
- The existing workspace JSON aggregate remains the persistence source of
  truth. This packet requires no migration or data rewrite.

## In Scope

- Add `workspace-export.schema.json` in the Personal-workspace v1 family with
  closed fields, full embedded workspace validation, canonical digest, and UTC
  generation time.
- Add an immutable domain value and contract-port parse/project operation for
  the export envelope. Keep identity, clock, and authorization outside the
  pure adapter; the caller supplies an already-authorized workspace and a
  server-owned generation time.
- Load and validate the new schema through the existing contract adapter and
  resource registry. Round-trip one canonical synthetic compatibility fixture.
- Reject digest substitution, workspace substitution, unknown fields, invalid
  time/version, omitted required fields, over-limit embedded data, and any
  attempt to add credentials, storage keys, mutation replay, target content,
  artifact bytes, or provider payloads.
- Emit distinct bounded pure-contract quota failures for a 201st record, 51st
  collection, and 101st unique collection member while accepting exact maxima.
- Preserve existing mutation error precedence: malformed shapes, stale
  revision, missing records/collections, duplicate IDs, and invalid membership
  remain distinct from capacity exhaustion.
- Prove `remove_record` cleans record order and every collection membership,
  while `remove_collection` changes no record or target reference. Exact replay
  behavior remains for the later application/persistence packet.
- Add anti-rigidity evidence for empty, sparse, full, reordered, mixed
  Curriculum/Project reference, Unicode, optional-label, and varied valid-count
  workspaces without hard-coding one fixture's incidental order or count.
- Update contract/module guidance, SLI packet mapping, packet history, and the
  planning register with the exact delivered semantics and evidence.

## Out of Scope

- Application service operations, repository methods, SQL/migrations, host
  composition, authorization, API models/routes/errors, OpenAPI, generated
  TypeScript clients, web code, browser tests, or live topology changes.
- User-triggered file download, combined learning-record export, background
  generation, object storage, artifact inclusion, import, populated-target
  merge, or restore; these remain later seams or CAP-0019.
- Whole-workspace deletion, physical purge, retention, audit deletion,
  recovery-copy deletion, legal guarantees, or managed-cloud policy.
- Curriculum or Project mutation, direct owner persistence access, target
  content copying, provider calls, artifact bytes, active preview/execution,
  external network access, financial behavior, or AI authority.
- New reference kinds, source lifecycle events, quota configuration UI, quota
  increases, schema-version changes beyond the additive export envelope, or a
  migration of accepted workspace aggregates.
- Styling-only cleanup or unrelated documentation changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contract | all Personal-workspace v1 schemas and compatibility fixtures | new export schema/fixtures and family README | Freeze exact owner export meaning and denials |
| Domain and port | workspace immutable values and contract protocol | export-envelope value and pure parse/project signatures | Provide transport-neutral accepted input/output for JIT-B |
| Contract adapter | schema registry, canonical digest, workspace parse/project, mutation validation | export parse/project and explicit capacity classification | Reuse one canonical implementation without host logic |
| Focused tests | contract corpus, pure mutation/query/refresh suite | export, quota, removal, and anti-rigidity evidence | Prove the packet result at its owning layer |
| Architecture | Personal-workspace import boundary | only a focused assertion if the new type exposes a missing boundary test | Prevent dependency reversal or target coupling |
| Documentation/planning | contract/module docs, SLI-0073, packet, register | exact changed boundary and lifecycle evidence | Keep implementation and public coordination aligned |

No file outside `write_scope` may change. Generated output is not owned by this
packet. If implementation requires application, persistence, API, OpenAPI,
client, browser, deployment, recovery-tool, or unrelated architecture files,
stop and leave that work for the appropriate later packet.

## Contracts and Interfaces

The accepted output between WRK-0143 and JIT-B is:

- one `WorkspaceExportView`-equivalent immutable value containing v1 schema
  version, canonical workspace digest, generated UTC time, and one complete
  `PersonalWorkspace` value;
- contract-port operations to construct/project and parse/validate that value;
- one exact valid JSON compatibility fixture plus bounded denial fixtures;
- distinct contract failure meanings for record, collection, and membership
  capacity; and
- unchanged `PersonalWorkspace`, mutation-intent, query/result, reference, and
  public owner contracts outside those additive seams.

The export document is safe only after ordinary learner authorization in a
later layer. The pure adapter does not accept a learner override, authorize a
caller, sign a download, access persistence, contact an owner adapter, or
decide retention. Its digest detects changed meaning but is not a signature.

Quota classification is deterministic and data-minimizing. Failures may name
the public limit category and bound, but never include note text, target title,
learner ID, database data, or a private reference selector.

## Dependencies and Parallel Safety

SLI-0070, SLI-0071, and SLI-0072 are complete and provide the accepted
workspace, Project-reference, query, refresh, browser/headless, and live parity
inputs. WRK-0143 has no packet dependency because it is the first SLI-0073
packet, but it depends semantically on those completed slices.

The packet is not parallel-safe with another SLI-0073 packet. JIT-B consumes
its exact export and quota outputs and therefore cannot start until WRK-0143 is
complete. The contract, adapter, tests, documentation, SLI, and register scopes
also overlap the later delivery seam.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Canonical export | an authorized complete empty or populated workspace and server time | the pure contract constructs and parses an export view | the closed document round-trips and its digest equals the canonical workspace digest | schema/compatibility/unit |
| Changed meaning | a sealed export fixture | any workspace fact is substituted without the matching digest | parsing fails with the bounded digest-mismatch meaning | contract/unit |
| Closed privacy | a valid export view | a credential, replay row, storage key, target payload, artifact bytes, provider field, or unknown property is added | validation fails without returning the added value | schema/security fixture |
| Exact record bound | a workspace with 199 or 200 records | a create would produce the 200th or 201st record | 200 is accepted and 201 fails with the record-capacity meaning without changing the input | pure contract/unit |
| Exact collection bound | a workspace with 49 or 50 collections | a create would produce the 50th or 51st collection | 50 is accepted and 51 fails with the collection-capacity meaning without changing the input | pure contract/unit |
| Exact membership bound | a collection with 99 or 100 unique members | membership is set to 100 or 101 valid record IDs | 100 is accepted and 101 fails with the membership-capacity meaning without replacing prior membership | schema/pure contract/unit |
| Removal cleanup | one record belongs to multiple collections and appears in the order | the record is removed | only the record, order entry, and workspace-owned memberships disappear | pure contract/unit |
| Collection removal | a collection holds mixed reference records | the collection is removed | all records and target references remain byte-equivalent | pure contract/unit |
| Failure precedence | capacity, stale revision, missing item, duplicate ID, and invalid membership inputs | each invalid mutation is applied | every case retains its specific bounded meaning instead of collapsing to generic capacity | unit/parameterized |
| Anti-rigidity | varied empty/sparse/full, Unicode, reordered, mixed-kind, and optional-field workspaces | export, valid mutations, and removals run | invariants hold without requiring one fixture count, order, label, or source kind | compatibility/property-style unit |

## Verification Commands

Run from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace/test_workspace_contract.py
uv run --project backend pytest backend/tests/architecture/test_module_boundaries.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
```

After claim, run the controller-selected exact-candidate affected checks and
the independent technical review route. Run `python dev-tools/agent/check_ready.py`
when selected by shared contract impact and before handoff. Do not substitute
aggregate readiness for the focused contract and pure-core commands.

## Documentation and Evidence Update

Update the Personal-workspace executable-family README, compatibility-corpus
README, module README, architecture contract, SLI packet table/history, this
packet, and planning register. Record the exact contract fields, digest rule,
quota meanings, removal cleanup, compatibility posture, checks and results,
assumptions, and later application/API/recovery gaps.

Approval and reviewer records remain only in ignored local storage. Tracked
files contain public lifecycle and technical evidence only.

## Stop Conditions

Stop for an unresolved export container or cross-module manifest choice;
whole-account erasure, physical purge, retention, recovery-copy deletion, or
legal guarantee; managed-cloud policy; application/API/browser/recovery-tool
scope; migration of accepted rows; caller-selected learner identity; target
content or permission inclusion; replay-row, secret, session, credential,
storage, artifact-byte, or provider-payload export; direct owner persistence or
object-storage access; new reference kinds; active artifact behavior; external
action; breaking contract change; stale CAP package; active write collision;
conflicting canonical authority; or material CAP-0017/SLI-0073 drift.

Do not stop for harmless whitespace, incidental fixture order/count, optional
wording, or nonfunctional styling. Fix in-scope inconsequential issues locally
or defer optional cleanup without creating another approval or review gate.

## Required Handoff

Report `CAP-0017.SLI-0073.WRK-0143`; exact candidate and qualifying receipt;
contract and fixture additions; export fields and digest rule; quota codes and
exact-limit evidence; removal/membership behavior; focused contract/unit and
architecture results; affected and aggregate results when selected;
documentation impact; compatibility/migration posture; assumptions; and
remaining JIT-B application/API work. Confirm no persistence, API/OpenAPI,
generated client, browser, recovery tool, target mutation, managed-cloud,
provider, execution, AI, financial, or external-action behavior changed.

## Planning History

- 2026-10-17: Authored just in time after SLI-0073 refinement and completion of
  its three predecessor slices. The packet isolates the export/quota/removal
  contract seam from later application, API/client, browser, and live recovery
  work, stays inside the current CAP manifest and decisions, and requires no
  lower-level approval.
- 2026-10-17: Activated from recorded base `75dccce` after confirming current
  CAP binding, resolved decision posture, exact contract-only write scope,
  completed predecessor slices, and no active coordination collision.
- 2026-10-17: Moved to evidence verification after the closed export envelope,
  privacy denials, exact capacity classifications, removal isolation, focused
  contract/core/architecture checks, documentation, planning, security, and
  whitespace validation passed within the contract-only boundary.
- 2026-10-17: Completed after quota classification was constrained to the
  workspace and export contexts, malformed or duplicate membership overflow
  retained its non-capacity meaning, and query-result overflow retained its
  existing non-quota failure.

## Completion Evidence

- Candidate `3106cae` is a strict descendant of the original contract
  candidate and stays within the declared contract, adapter, focused-test,
  documentation, and planning scope.
- The versioned export envelope is closed over `schema_version`,
  `workspace_digest`, `generated_at`, and `workspace`; the outer digest must
  match the canonical embedded workspace and generation cannot predate the
  workspace update.
- Exact maxima remain 200 records, 50 collections, and 100 unique canonical
  members per collection. Valid overflow has distinct bounded capacity meaning;
  malformed, duplicate, query-result, and unrelated schema failures do not.
- Record removal changes only workspace records, order, and membership;
  collection removal preserves records and target references.
- The focused Personal-workspace contract, pure-core, and module-boundary suite
  passed 185 tests. Controller-selected planning, documentation, and
  architecture checks produced a fresh, stable, qualifying exact-candidate
  receipt with digest
  `sha256:2a2de2ee4a614aa2d959223ecf9f1d0a7c0c9f96b0de8e22a38ee42c740f01d5`.
- No persistence, application service, protected API, OpenAPI, generated
  client, browser, recovery tool, target-domain mutation, managed-cloud,
  provider, execution, AI, financial, or external-action behavior changed.
  Those selected SLI-0073 seams remain for the dependent packets.
