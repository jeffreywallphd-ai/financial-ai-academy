---
id: WRK-0132
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0070
capability: CAP-0017
depends_on: [WRK-0131]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/scripts/generate-api-client.mjs", "apps/web/src/generated/api-client", "apps/web/tests/contract", "backend/migrations/personal_workspace", "backend/migrations/README.md", "backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/hosts/api", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/personal_workspace", "backend/tests/architecture", "backend/tests/integration/api", "backend/tests/integration/personal_workspace", "backend/tests/unit/identity", "backend/tests/unit/personal_workspace", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api", "deployments/local", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/modules/module-map.md", "docs/assurance/known-verification-gaps.md", "docs/operations/local-development.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0070-save-learning-notes-bookmarks-collections.md", "docs/planning/work-packets/WRK-0132-deliver-personal-workspace-persistence-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 7102251488f164cee414a9b2711965b344b4dba9
claim_id: WRK-0132:a0bbe1e5-39f4-42e3-aa85-d4d31851281a
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T11:03:26Z
---

# Agent Work Packet: Deliver Personal Workspace Persistence and Public API

## Objective and Deliverable

Compose the accepted WRK-0131 contracts into one Personal-workspace-owned,
server-authoritative persistence and public API seam. A learner can open the
single Personal workspace and apply one revision-bound note, bookmark,
collection, ordering, archive, restore, or removal command. Exact retries
return the accepted workspace, stale or changed requests fail without
overwrite, and create commands resolve current learning references through
Curriculum public operations before persistence.

The protected API is the primary product boundary. Browser, command-line,
service, and future headless AI consumers use the same operations and receive
the same identity, permission, provenance, revision, idempotency, and
containment behavior. This packet creates no browser workspace interface.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through architecture contracts, security/risk, testing, API versioning, and
delivery planning; apply the change-impact matrix and decision-readiness
register; and inspect CAP-0017, SLI-0070, WRK-0131, ADR-0006, ADR-0021, the
Personal-workspace contracts and pure core, Curriculum public learning reads,
Identity permissions, PostgreSQL/migration conventions, API/OpenAPI/client
generation, bootstrap composition, relevant tests, and nearest READMEs.

Revalidate that collaboration, organizations, tenancy, managed cloud,
provider selection, external execution, Assessment/Learner-model effects,
recommendations, financial actions, and separate AI-mode planning remain
outside the packet.

## Decisions and Assumptions

- WRK-0131's schemas and immutable values are fixed inputs. Persistence and
  transport cannot weaken reference correlation, chronology, digest, bounds,
  collection closure, or confidentiality.
- Personal workspace owns its PostgreSQL schema and aggregate. It retains no
  cross-schema foreign key and reads no other module's repository or tables.
- Public create-note and create-bookmark requests carry a closed Curriculum
  selector, not caller-authored title, destination, package, publication, or
  validation provenance. A gateway resolves the current safe reference only
  through Curriculum public operations and constructs the accepted WRK-0131
  target. Other mutations carry only learner-owned text and workspace-owned
  identifiers.
- The source gateway may compose the existing bounded learning-opportunity
  browse and placed-lesson read operations. Missing, unavailable, mismatched,
  or malformed targets fail before a workspace write. Persistence never stores
  a permission grant or copied lesson body.
- One authenticated learner has one logical workspace. An absent row projects
  a stable revision-one empty aggregate without writing on read. Its opaque
  workspace ID and logical inception are deterministically derived by a
  server-owned seed adapter; they are not client inputs. The first accepted
  mutation atomically materializes revision two.
- Mutation persistence is one learner-scoped transaction. It checks exact
  replay before source resolution, binds a canonical request fingerprint,
  locks the current revision or absent aggregate, and records the accepted
  complete workspace. Exact replay is stable even if the source later changes;
  changed key reuse or concurrent stale work does not overwrite state.
- Identity grants explicit `personal_workspace.read` and
  `personal_workspace.write` permissions in the accepted single-profile mode.
  The API derives learner identity and permissions from the opaque server
  session; requests never select a learner or server-owned ID/time/digest.
- API paths are `/api/v1/personal-workspace` and
  `/api/v1/personal-workspace/mutations`. Transport models remain closed and
  bounded. OpenAPI is the sole generated TypeScript source.

## In Scope

- Add transport-neutral Personal-workspace requests, results, bounded error
  codes, application service, repository/source/system ports, and adapters.
- Resolve opportunity and placed-lesson selectors through public Curriculum
  operations, construct exact accepted reference snapshots, and deny stale or
  unavailable sources without writing.
- Add one deterministic virtual-empty seed, UTC clock, and opaque identifier
  adapter without persisting on reads or exposing derivation details.
- Add Personal-workspace PostgreSQL tables for current aggregate and mutation
  replay, exact revision locking, atomic first materialization, deterministic
  reads, canonical JSON, and contract revalidation on read.
- Add additive up/down migration behavior. Fresh up and empty development down
  are supported; retained workspace or replay rows refuse a claim of harmless
  destructive rollback.
- Compose the contract, repository, gateway, clock, identifiers, and service
  through bootstrap while preserving one local/cloud application core.
- Add protected FastAPI/Pydantic GET and POST operations, bounded error
  mapping, server identity/permission checks, safe correlation, and no private
  storage/source details.
- Regenerate and review OpenAPI and the TypeScript client; extend generated-
  client usage evidence so authenticated non-browser callers can execute the
  complete seam without a UI model.
- Add focused unit, real-PostgreSQL, API, architecture, migration, restart,
  concurrency, interruption, authorization, privacy, and anti-rigidity tests.
- Synchronize Personal-workspace, API, operations, assurance, module,
  migration, slice, packet, and register documentation.

## Out of Scope

Browser routes, forms, styling, browser storage, or offline synchronization;
Project resources/snapshots/artifacts; arbitrary files; active rendering;
kernels, subprocesses, packages, network/provider calls, credentials, or
execution; full-text/semantic search; import/export; sharing, collaboration,
organizations, tenancy, managed-cloud recovery; Assessment, Learner-model,
completion, mastery, adaptation, or recommendation changes; autonomous AI
authority; financial calculations, advice, transactions, or external action;
and breaking WRK-0131 contract meaning.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Personal-workspace public/application | Requests, errors, policy, owned ports, service | One transport-neutral core; domain remains framework-free |
| Adapters/persistence | Curriculum public gateway, system adapters, PostgreSQL repository | No cross-module repository/table access; stored documents revalidate |
| Migration/composition/identity | Additive module migration, bootstrap wiring, two explicit permissions | One shared core; server-owned learner identity; retained-data down refusal |
| API/OpenAPI/client | Closed protected models/routes and generated outputs | Selector-only source input, bounded errors, browser/headless parity |
| Tests | Unit/PostgreSQL/API/client/architecture/security evidence | Flexible valid shapes plus stale/replay/privacy/source denials |
| Documentation/planning | Exact delivered contract, operations, limitations, lifecycle | Claims match qualified local behavior and explicit omissions |

## Contracts and Interfaces

Expose transport-neutral operations equivalent to:

```text
open_personal_workspace(learner_id) -> PersonalWorkspace
mutate_personal_workspace(learner_id, command) -> PersonalWorkspace
```

The closed public command includes schema version, idempotency key, expected
revision, and one operation. Create note/bookmark operations use either an
exact `learning_opportunity` selector (`opportunity_id`, `placement_id`) or an
exact `placed_lesson` selector (`placement_id`); the server resolves and stamps
all remaining reference facts. Update, collection, reorder, archive, restore,
and remove operations use the WRK-0131 learner/workspace fields only.

The service constructs a WRK-0131 mutation intent after source resolution,
uses the pure mutation core, and persists only the complete revalidated result.
Responses use `personal-workspace-v1` and contain no request fingerprint,
replay row, session, permission, database, source body, provider, or execution
fact. Stable public errors distinguish invalid request, stale revision,
immutable idempotency conflict, source unavailable, integrity failure, not
found, and service unavailable without leaking private state.

## Dependencies and Parallel Safety

WRK-0131 is complete and fixes every contract/core invariant consumed here.
This packet owns shared bootstrap, Identity permission, API/OpenAPI/client, and
Personal-workspace persistence surfaces, so it is not parallel-safe with
another writer in those areas. It must complete before the browser packet is
authored.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Empty/open | An authenticated learner receives the same revision-one empty workspace repeatedly without a database write | unit/PostgreSQL/API |
| First materialization | The first valid mutation atomically creates revision two and survives normal restart | PostgreSQL/API |
| Opportunity note | Exact available opportunity selector becomes one note with server-resolved identity, destination, package, publication, and validation provenance | unit/API/PostgreSQL |
| Lesson bookmark | Exact placed-lesson selector becomes one bookmark without copied body or caller-authored source facts | unit/API/PostgreSQL |
| Source denial | Missing, unavailable, mismatched, or malformed Curriculum source fails before any workspace/replay row is written | unit/PostgreSQL/API |
| Closed mutations | Update, collection, membership, order, archive, restore, and removal retain WRK-0131 meaning and bounds | unit/PostgreSQL/API |
| Revision/idempotency | Exact retry returns the accepted workspace; changed key reuse and stale/concurrent revision fail without overwrite | unit/PostgreSQL/API |
| Restart/read integrity | Stored order, Unicode, times, provenance, digest, and collection closure survive restart; invalid stored meaning fails unavailable | PostgreSQL/API |
| Headless parity | An authenticated non-browser client reads and mutates through reviewed OpenAPI/generated types | API/client contract |
| Authorization/privacy | Missing session/permission, caller-selected learner/server fields, cross-learner guesses, private fields, and unsafe diagnostics fail closed | API/security |
| No target/evidence effect | Mutations write no Curriculum/Content/Project/Assessment/Learner-model/provider state | architecture/PostgreSQL |
| Anti-rigidity | Valid Unicode, zero/many records/collections, optional labels, generated values, IDs, times, ordering, and operation variants work without fixture assumptions | parameterized unit/PostgreSQL/API |
| Migration bounds | Fresh up and empty down/up pass; retained Personal-workspace data refuses destructive down | PostgreSQL/migration docs |

## Verification Commands

Run focused Personal-workspace core/application, real-PostgreSQL, protected API,
migration up/down, restart, and concurrency suites; existing Curriculum and
Identity regressions; OpenAPI currency; generated-client reproduction and
usage typecheck; backend architecture and schema-ownership checks; security;
packet, planning, documentation, Python compilation, whitespace, exact-
candidate affected verification, independent technical review, and `python
dev-tools/agent/check_ready.py`. Use the repository-local Windows temporary
root where necessary. Browser qualification belongs to the next packet.

## Documentation and Evidence Update

Record public operations and permissions; selector/source-resolution rules;
virtual-empty and first-materialization behavior; tables and rollback limits;
revision/idempotency/concurrency/restart behavior; OpenAPI/client parity;
authorization/privacy; no-target-effect boundaries; exact checks; qualified
environment; assumptions; unperformed checks; and residual gaps. Receipts and
technical-review records remain only in ignored local control-plane storage.

## Stop Conditions

Stop for conflicting Personal-workspace/Curriculum ownership; a need to change
WRK-0131 meaning; copied target body or permission state; caller-selected
learner/ID/time/provenance/digest; cross-module repository/table access;
destructive retained-data migration; execution, arbitrary files, network,
provider, secret, Project/Assessment/Learner-model effect, collaboration,
tenancy, managed cloud, external action, autonomous AI authority, financial
advice/action, irreproducible generated output, active write collision, or
material CAP-0017 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it within scope or defer optional cleanup to
CAP-0031.

## Required Handoff

Report exact candidate; public operations and permissions; reference
resolution; persistence/migration behavior; API paths and generated-client
headless parity; revision/idempotency/concurrency/restart results;
authorization/privacy and target-effect containment; focused, PostgreSQL, API,
client, architecture, security, affected, and aggregate checks; changed files;
documentation impact; assumptions; unqualified environment checks; and
residual gaps. Confirm no browser interface, arbitrary file, execution,
Project/Assessment/Learner-model effect, provider, managed-cloud profile,
separate AI mode, autonomous authority, or financial action was added.

## Planning History

- 2026-10-17: Authored just in time after WRK-0131 completed. This packet
  composes the accepted Personal-workspace contracts into the smallest
  complete persistence and public-API seam, keeps source facts server-resolved,
  and preserves equal generated-client access for headless use. No lower-level
  approval is required.
- 2026-10-17: Activated after validating the completed dependency, current CAP
  package binding, decision readiness, selector-based source authority, exact
  file ownership, and generated-client/headless contract.
- 2026-10-17: Incrementally included local deployment composition after the
  protected API seam required the already composed Personal-workspace service
  to be passed into the local host. Product scope and public contracts are
  unchanged.
- 2026-10-17: Released the unsubmitted claim to ready so one new claim can bind
  the refined deployment-composition scope. Implemented work remains on the
  same CAP branch; no review or lower-level approval is required.
