---
id: WRK-0119
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: SLI-0031
capability: CAP-0007
depends_on: [WRK-0118]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/scripts/generate-api-client.mjs", "apps/web/src/generated/api-client", "apps/web/tests/contract", "backend/migrations/project", "backend/migrations/README.md", "backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/hosts", "backend/src/financial_ai_academy/modules/identity", "backend/src/financial_ai_academy/modules/project", "backend/tests/architecture", "backend/tests/integration/api", "backend/tests/integration/project", "backend/tests/unit/project", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api", "deployments/local", "docs/architecture/contracts/project-workspace-contract.md", "docs/architecture/modules/module-map.md", "docs/assurance/known-verification-gaps.md", "docs/operations/local-development.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0119-deliver-project-workspace-persistence-public-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 7403e3d5f4624cf3e6c706d7240994a56c5b710b
claim_id: WRK-0119:c3f655b1-e7f7-4513-9dcf-93de2f1c7403
claimed_by: codex-cap-0007
claimed_at: 2026-10-16T23:12:08Z
---

# Agent Work Packet: Deliver Project Workspace Persistence and Public API

## Objective and Deliverable

Compose the accepted WRK-0118 workspace contracts into one Project-owned,
server-authoritative backend and public API seam. Persist revision-bound notes,
references, inert artifact manifests and bytes, typed reference records, and
immutable snapshots; then expose protected workspace, mutation, artifact,
snapshot, download, and evidence-export operations through reviewed OpenAPI and
the generated TypeScript client.

The public API is the primary product boundary. Browser, command-line, service,
and future headless AI consumers must use the same operations and receive the
same authorization, revision, idempotency, provenance, and execution-denial
behavior. This packet creates no browser workspace interface.

## Required Context

Before editing, read every applicable `AGENTS.md`, `docs/README.md`, the routed
architecture-contracts and security-risk context, the change-impact matrix,
decision-readiness register, CAP-0007, SLI-0031, WRK-0118, ADR-0011, ADR-0012,
the Project workspace contract, module map and dependency rules, contract and
API versioning guidance, single-profile identity/security contract, current
Project public/application/repository/composition/API/client implementation,
Project and object-storage tests, migration guidance, and nearest READMEs.

Revalidate that external execution, active rendering, live Portfolio behavior,
Assessment submission, Learner-model effects, tenancy, managed-cloud storage,
and provider selection remain outside the packet.

## Decisions and Assumptions

- WRK-0118's executable schemas and pure values are fixed inputs. Transport and
  persistence may not weaken their bounds, classifications, canonical ordering,
  snapshot digests, or credential/path denials.
- Project owns workspace and snapshot metadata. PostgreSQL tables remain in the
  `project` schema with no cross-schema foreign keys and every stored portable
  record is revalidated on read.
- Artifact bytes remain opaque, inert, content-addressed data behind a
  Project-owned object port. A Project adapter may reuse the qualified local
  filesystem object-store implementation through composition, but Project
  application code may not import Content or platform infrastructure.
- Artifact admission verifies exact byte count and SHA-256 before metadata is
  accepted. Finalized but unreferenced content may remain for bounded later
  reconciliation after a metadata failure; no partial manifest becomes live.
- Workspace mutation is one transaction guarded by learner, Project,
  expected-revision, and idempotency fingerprint. Exact replay returns the
  accepted workspace; changed reuse, stale revision, missing record, or
  version conflict fails without overwrite.
- Domain-link mutation is supported only through an explicit allowlisted owner
  gateway. With no live Portfolio or other domain gateway admitted yet,
  attempts fail as unavailable/invalid rather than inventing a dangling link.
- Snapshot closure reads one exact Project shell and workspace revision under a
  transaction lock, freezes canonical version references, and stores an
  immutable digest-bound record. Exact replay returns the original snapshot;
  later workspace mutations never update it.
- Evidence export is a deterministic JSON-compatible manifest plus only the
  learner-authorized inert bytes admitted by the export policy. Use-restricted
  or unavailable source content remains an explicit exclusion. Export is not
  import, restore, archive expansion, or execution.
- Binary upload/download may use a thin transport envelope distinct from the
  portable Project schemas. It must remain bounded, deterministic, generated-
  client visible, safe to use headlessly, and unable to carry identity,
  storage keys, host paths, authorization facts, or execution controls.
- The API host derives learner identity and `project.read`/`project.write`
  permission from the server session. State-changing operations keep the
  existing same-origin policy; learner IDs and server-owned versions/times are
  never accepted as authority.

## In Scope

- Extend the Project public facade with transport-neutral requests/results for
  reading a workspace, applying one reviewed mutation, uploading one inert
  artifact, downloading exact bytes, closing/listing/reading snapshots, and
  building one evidence export.
- Add Project-owned repository and object-storage ports plus application policy
  for learner validation, exact Project ownership, contract revalidation,
  canonical request fingerprints, optimistic revisions, idempotent replay,
  server IDs/times, artifact integrity, domain-gateway denial, snapshot closure,
  continued live work, download lookup, and export inclusion/exclusion.
- Add a Project object adapter over the restrictive local content-addressed
  filesystem implementation without importing another module's internals into
  Project application or domain code.
- Extend Project PostgreSQL persistence additively for live workspaces,
  mutation idempotency, opaque artifact object references, immutable snapshots,
  and snapshot-close idempotency. Preserve exact record order and transaction
  semantics; reject ordinary snapshot update/delete.
- Add exact up/down migration behavior. Empty development rollback may succeed;
  retained workspace, artifact, idempotency, or snapshot rows must refuse a
  claim of harmless destructive rollback.
- Compose storage, repository, contract, clock, IDs, and admitted empty domain-
  gateway registry through bootstrap while preserving one local/cloud core.
- Add protected FastAPI/Pydantic operations and bounded error mapping for the
  complete backend seam. Safe download responses use attachment headers,
  `nosniff`, exact media/length/digest metadata, and never active inline HTML.
- Regenerate and review OpenAPI and the TypeScript client. Extend generated-
  client usage evidence so non-browser/headless callers can reach every
  operation without a UI-only model or hand-maintained duplicate type.
- Add focused unit, PostgreSQL, API, architecture, security, migration,
  restart, concurrency, interruption, privacy, and anti-rigidity evidence.
- Synchronize Project, API, operations, assurance, module, migration, slice,
  packet, and register documentation with the exact delivered boundary.

## Out of Scope

- Browser pages, forms, styling, route state, previews, or visual export flows;
  those belong to the next packet.
- Active rendering, notebook/code/model execution, kernels, subprocesses,
  package installation, runtime images, network, secrets, callbacks, malware
  service selection, archive expansion, or a provider execution port.
- A live Portfolio or other domain-resource adapter; copied target state;
  market data; financial calculations, transactions, recommendations, advice,
  or real financial actions.
- Assessment submission, completion, grading, review, Learner-model projection,
  instructor workflow, AI authority, autonomous mutation, collaboration,
  sharing, organizations, tenancy, managed-cloud protection/recovery, jobs,
  import/restore, deletion/retention automation, or production recovery claims.
- Breaking Project shell or WRK-0118 portable contract meaning.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Project public/application | Requests, results, errors, policy, and owned ports | Same operations serve browser and headless clients; domain stays framework-free |
| Project adapters | PostgreSQL workspace/snapshot persistence and restrictive object adapter | Project schema ownership, no cross-module internals, bytes remain inert |
| Migration/composition | Additive Project migration, settings/composition wiring | One shared core, deterministic order, retained-data down refusal |
| API/OpenAPI/client | Protected models/routes, reviewed snapshot, generated TypeScript | Server learner authority, bounded transport, generated-client parity |
| Tests | Project unit/PostgreSQL/API/client/architecture evidence | Flexible valid shapes plus stale/replay/privacy/execution denials |
| Documentation/planning | Project/API/operations/assurance and exact lifecycle artifacts | Claims match qualified local behavior and explicit omissions |

## Contracts and Interfaces

Expose transport-neutral operations equivalent to:

```text
open_workspace(learner_id, project_id) -> ProjectWorkspace
mutate_workspace(learner_id, project_id, intent) -> ProjectWorkspace
upload_artifact(learner_id, project_id, intent, content) -> ProjectWorkspace
download_artifact(learner_id, project_id, artifact_id, artifact_version) -> bytes + safe metadata
close_snapshot(learner_id, project_id, intent) -> ProjectSnapshot
list_snapshots(learner_id, project_id) -> tuple[ProjectSnapshot, ...]
open_snapshot(learner_id, project_id, snapshot_id) -> ProjectSnapshot
export_snapshot(learner_id, project_id, snapshot_id) -> manifest + authorized inert bytes
```

The ordinary mutation operation accepts notes, references, and admitted domain
link intents. Artifact admission uses a distinct request carrying one validated
`add_artifact` intent and exact bounded bytes so portable records never embed
content. The service verifies supplied byte count/digest before object storage.

An empty workspace is created lazily and deterministically for an existing
owned Project at revision one. Its Project shell revision remains distinct from
its workspace revision. Public responses contain no request fingerprint,
idempotency row, object key, stage ID, host path, permission, session, database,
or provider fact.

HTTP paths remain under `/api/v1/projects/{project_id}` and use explicit
operation IDs. OpenAPI is the sole source for generated TypeScript. Download or
export byte responses must declare safe content handling and be callable by the
generated client; no browser wrapper may become authoritative.

## Dependencies and Parallel Safety

WRK-0118 is complete and fixes the contract/domain seam consumed here. This
packet owns shared Project persistence, composition, API/OpenAPI/client output,
and related qualification surfaces, so it is not parallel-safe with another
writer in those areas. It must complete before the browser packet begins.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Empty/open/resume | Existing owned Project opens revision-one empty workspace; accepted work reopens identically after restart | unit/PostgreSQL/API |
| Notes and references | Add/replace operations preserve order, exact versions, provenance, and Unicode within contract bounds | unit/PostgreSQL/API |
| Inert artifact | Matching bounded bytes and complete manifest finalize by digest and become one live record | unit/object/PostgreSQL/API |
| Artifact denial | Digest/length mismatch, unsafe path/media/effect, over-limit input, stale revision, or partial storage failure creates no accepted manifest | unit/object/PostgreSQL/API/security |
| Safe download | Authorized exact artifact bytes return with attachment, `nosniff`, bounded length, media, and digest; guessed/cross-learner IDs disclose nothing | API/security |
| Domain owner unavailable | A syntactically valid link to an unadmitted owner is rejected without a stored dangling link or copied state | unit/API |
| Revision/idempotency | Exact retry returns accepted state; changed key reuse or stale concurrent revision conflicts without overwrite | unit/PostgreSQL/API |
| Snapshot closure | Exact shell/workspace revision closes once to the canonical digest and exact retry returns the same snapshot | unit/PostgreSQL/API |
| Continue after close | A later live mutation advances only workspace state; historical snapshot record/digest stays byte-identical | PostgreSQL/API |
| Evidence export | Exact snapshot yields the reviewed manifest and allowed bytes; restricted/unavailable source bytes are explicit exclusions | unit/object/API |
| Headless parity | An authenticated non-browser client performs every supported read/write/download/snapshot/export operation from OpenAPI/generated types | API/client contract |
| Authorization/privacy | Missing session/permission, caller-selected learner, cross-learner guesses, private fields, storage paths, and unsafe errors fail closed | API/security |
| No execution/evidence effects | Composition exposes no execution dependency and writes no Assessment, Learner-model, Portfolio, provider, or financial state | architecture/PostgreSQL |
| Anti-rigidity | Zero/many records, varied Unicode, valid optional metadata, classifications, ordering, digests, revisions, IDs, and times work without fixture-specific assumptions | parameterized unit/PostgreSQL/API |
| Migration bounds | Fresh up and empty down/up pass; retained Project data refuses destructive down | PostgreSQL/migration docs |

## Verification Commands

Run the focused Project contract/domain/application/object tests, real
PostgreSQL Project integration, protected API integration, migration up/down and
restart checks, OpenAPI currency, generated-client reproduction and usage
typecheck, backend architecture and contract/unit regression, security,
planning, documentation, Python compilation, whitespace, affected-candidate
verification, one independent technical review, and `python
dev-tools/agent/check_ready.py`. Use a repository-local temp root on Windows
when the sandbox denies its default temporary directory. Browser qualification
is not required unless a generated-client contract explicitly invokes it.

## Documentation and Evidence Update

Record exact operations and permissions; PostgreSQL tables and rollback
limits; object admission/failure semantics; revision and idempotency behavior;
download headers; snapshot canonicalization and immutability; export contents
and exclusions; OpenAPI/client parity; authorization/privacy; no-execution and
no-learning-effect boundaries; exact checks and candidate receipt; qualified
local environments; assumptions; and residual gaps. Reviewer and approval
records remain only in ignored local control-plane storage.

## Stop Conditions

Stop for conflicting Project ownership or contract meaning; a need to alter
WRK-0118 semantics; execution, active rendering, archive expansion, network,
secrets, packages, runtime images, provider callbacks, live Portfolio behavior,
copied domain state, financial action/advice, Assessment or Learner-model
effects, cross-module internals/tables, client-selected identity/authorization,
unbounded bytes, destructive retained-data migration, tenancy, managed cloud,
provider selection, a separate AI mode or autonomous authority, irreproducible
generated output, active write-scope overlap, or material CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture order/count, or another
inconsequential issue. Fix it within scope or defer optional cleanup to
CAP-0031.

## Required Handoff

Report the exact candidate and receipt; public operations; persistence and
object-storage behavior; API paths and permissions; generated-client/headless
parity; revision/idempotency/concurrency/restart results; artifact integrity and
safe-download evidence; snapshot/export results; authorization/privacy;
migration behavior; focused, PostgreSQL, API, client, architecture, security,
affected, and aggregate checks; changed files; documentation impact;
assumptions; environment checks not performed; and residual gaps. Confirm that
no browser workspace, execution, active rendering, live Portfolio behavior,
Assessment submission, Learner-model effect, provider, managed-cloud profile,
separate AI mode, or autonomous authority was added.

## Planning History

- 2026-10-16: Authored just in time after WRK-0118 completed. The packet
  composes the accepted portable contracts into the smallest complete
  Project-owned persistence and public API seam, keeping the browser interface
  separate while preserving equal generated-client access for headless use.
- 2026-10-16: Activated after confirming the WRK-0118 dependency, current CAP
  package binding, decision readiness, API-first headless parity, and exact
  file ownership. Packet-start selected the affected evidence route.
