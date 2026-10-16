---
id: WRK-0118
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: SLI-0031
capability: CAP-0007
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/project/v1", "contracts/compatibility/project-workspace/v1", "backend/src/financial_ai_academy/modules/project/README.md", "backend/src/financial_ai_academy/modules/project/domain", "backend/src/financial_ai_academy/modules/project/ports/project_contract.py", "backend/src/financial_ai_academy/modules/project/adapters/project_contract.py", "backend/tests/contract/project_workspace", "backend/tests/unit/project/test_project_contract.py", "docs/architecture/contracts/project-workspace-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0118-freeze-project-workspace-snapshot-contracts.md"]
generated_artifacts: []
base_revision: 60d9add2da4ac723e512f2c6979e83c937d06707
claim_id: WRK-0118:61d67b63-06f8-4e0f-9920-8b3b89b406c1
claimed_by: codex-cap-0007
claimed_at: 2026-10-16T22:37:41Z
---

# Agent Work Packet: Freeze Project Workspace and Snapshot Contracts

## Objective and Deliverable

Define the additive Project workspace contract and pure policy foundation for
bounded notes and references, inert artifact manifests, typed domain-resource
links, immutable snapshots, and evidence exports. Hand back versioned executable
schemas, approved and denial compatibility cases, framework-free Project values
and canonical digest policy, and synchronized contract/module documentation.

The result must be independently useful to the next packet: application,
persistence, API, generated-client, and browser layers can consume one closed,
reviewed semantic boundary without inventing storage fields, execution effects,
Portfolio semantics, or Assessment meaning.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md`, the
repository-root `docs/README.md`, the planning guide/register/concurrent-work
protocol, and the current CAP-0007 package and SLI-0031 refinement. Route through
`docs/context/packs/index.pack.md` with `architecture-contracts` as the primary
pack and `security-risk` as the adjacent pack. Apply the change-impact matrix
and decision-readiness register.

Read ADR-0011, ADR-0012, the Project workspace contract, module map and
dependency rules, contract architecture and compatibility rules, security and
privacy standards, user-facing language standards, the existing Project v1 and
compatibility contract files, the Project module README/domain/contract port and
adapter, the focused contract/unit tests, and their nearest READMEs. Inspect the
current Project public/application/persistence/API/browser consumers so the new
types remain additive, but do not change those later layers in this packet.

## Decisions and Assumptions

- ADR-0011 is authoritative: every dataset, notebook, code, environment, result,
  reflection, and supporting file is inert untrusted data. Contract validation
  never claims code safety, result truth, or independent reproduction.
- ADR-0012 is authoritative: Project owns its mutable bounded workspace,
  artifact manifests, snapshots, and typed references. Owning domain modules
  retain their business state and Assessment retains submission/completion.
- Project shell v1 remains compatible. Workspace records are an additive
  contract seam that references one existing Project and never changes origin,
  learner ownership, or lifecycle meaning.
- Exact byte/count/text limits, closed media profiles, canonical serialization,
  and schema names are bounded implementation choices in executable contracts,
  not new durable product policy. Choose conservative limits that can be tested
  locally and changed only through ordinary additive contract versioning.
- A typed domain link records an owning module and public resource reference but
  never asserts target validity by itself. The next packet supplies gateway
  validation; no production Portfolio owner is assumed.
- Passive metadata inspection is always available. Preview content is permitted
  only for a narrowly allowlisted passive profile; unsupported content remains
  downloadable inert data. The contract contains no active-render instruction.
- Evidence export is a deterministic manifest contract. Packaging and streaming
  are later-layer concerns; import/restore and archive expansion are not implied.
- Browser and headless consumers will use the same later public API. This packet
  creates no browser-only or AI-specific representation.

## In Scope

- Extend the Project v1 contract family with closed schemas for workspace state,
  workspace mutation intent, learner notes, safe external-reference metadata,
  inert artifact manifest/version records, typed domain-resource links,
  snapshot close intent and immutable snapshot record, and evidence-export
  manifest.
- Define stable identifiers, canonical UTC time fields, positive live revision,
  expected-revision preconditions, idempotency keys, deterministic ordering,
  resource and artifact versioning, and exact digest fields.
- Define a closed artifact-kind union for dataset, notebook, code, environment,
  result, reflection, and supporting file plus a closed provenance/result-
  classification vocabulary that distinguishes observed, calculated, simulated,
  predicted, generated, and narrative evidence where applicable.
- Define normalized logical paths and file names without host paths, parent
  traversal, absolute paths, NULs, link targets, archive-expansion controls,
  executable controls, storage coordinates, credentials, or provider payloads.
- Define conservative text, count, and byte bounds; closed safe media metadata;
  lowercase SHA-256 content integrity; and explicit supplied source/license/use,
  environment, assumptions, and creator provenance where applicable.
- Define typed links with owning module, resource type, stable resource ID, link
  type, exact version and/or as-of evidence when applicable, provenance, and
  lifecycle. Do not define copied target state or Portfolio-specific fields.
- Define immutable snapshot canonicalization and digest rules over one exact
  Project shell/workspace revision and ordered accepted record set. Later live
  revision fields cannot mutate historical snapshot meaning.
- Define an export manifest that preserves snapshot and authorized artifact
  integrity while excluding secrets, credentials, private authorization facts,
  storage paths, and unauthorized source bytes.
- Add framework-free immutable Project domain values, parser/projector behavior,
  canonicalization/digest functions, and bounded error mapping for those
  contracts.
- Add approved, flexible-shape, boundary, malformed, unknown-union, traversal,
  digest-mismatch, over-limit, unsafe-media, active-effect, and private-field
  compatibility cases plus focused pure tests.
- Update Project contract and module documentation, SLI-0031 packet state, this
  packet, and the planning register with exact evidence.

## Out of Scope

- Repository ports, PostgreSQL migrations, object storage, transactions,
  application services, domain-owner gateway calls, authorization composition,
  HTTP endpoints, OpenAPI, generated clients, browser components, static builds,
  deployment composition, or live qualification.
- Reading or writing artifact bytes, download headers, export packaging,
  cleanup jobs, retained-data deletion, import/restore, or recovery policy.
- Live Portfolio or other domain adapters, target resolution, copied domain
  state, market data, provider data, financial calculations, or financial acts.
- Assessment submissions, completion, grading, Learner-model projections,
  instructor workflows, AI authority, or autonomous durable actions.
- Kernels, subprocesses, interpreters, package installation, runtime images,
  network or secret access, provider execution, callbacks, active previews, or
  archive expansion.
- General Workspace behavior, global files or notes, collaboration, public
  sharing, organization tenancy, managed-cloud storage/recovery, or unrelated
  refactoring and styling.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project executable contracts | Existing brief, intent, shell schemas and README | `contracts/learning/project/v1` | Add closed workspace/link/snapshot/export shapes without changing shell meaning |
| Compatibility corpus | Existing approved, denial, vector, runner behavior | `contracts/compatibility/project-workspace/v1`, `backend/tests/contract/project_workspace` | Prove portable success, flexibility, canonicalization, and fail-closed behavior |
| Project domain | Existing shell/origin values and package exports | `backend/src/financial_ai_academy/modules/project/domain` | Add framework-free immutable workspace and snapshot policy |
| Contract boundary | Existing Project contract port and adapter | `backend/src/financial_ai_academy/modules/project/ports/project_contract.py`, `backend/src/financial_ai_academy/modules/project/adapters/project_contract.py` | Parse/project the new portable records through the established seam |
| Focused unit tests | Current Project contract tests | `backend/tests/unit/project/test_project_contract.py` | Prove canonical digest, classifications, limits, and denials |
| Canonical documentation | Current Project semantic seam | `docs/architecture/contracts/project-workspace-contract.md` | Record additive versioned meaning and exclusions |
| Module documentation | Current implemented Project boundary | `backend/src/financial_ai_academy/modules/project/README.md` | State the delivered contract/domain surface and deferred layers |
| Planning | SLI-0031, packet, register | Exact declared planning files | Keep lifecycle and evidence synchronized |
| Later consumers | Public service, repository, API/OpenAPI/client, browser | inspect only | Prevent this contract packet from absorbing later-layer behavior |

The listed scope includes new files only under the exact contract, compatibility,
domain, and contract-test directories. It grants no authority to edit another
module, generated client, migration, host, or web file.

## Contracts and Interfaces

Consume the exact Project shell and origin contract delivered by SLI-0030. Do
not reinterpret its IDs, learner ownership, origin, lifecycle, revision, or UTC
time policy.

Produce for the next packet:

- validated immutable domain values and JSON-compatible projectors for a live
  workspace and bounded mutations;
- one closed artifact manifest/version model with normalized logical name/path,
  declared media profile, exact byte count, SHA-256 digest, classification,
  provenance, source/license/use, environment, assumptions, and created time;
- one closed typed domain-link model that carries references but no target state;
- one snapshot-close intent and immutable snapshot model with documented
  canonical serialization and lowercase SHA-256 digest;
- one evidence-export manifest derived from an accepted snapshot;
- stable contract failures that later application/API layers can map without
  leaking bytes, paths, credentials, learner identity, or persistence facts;
  and
- approved and denial fixtures reusable by persistence/API/browser qualification.

No storage or transport fact may enter these portable records. Contract readers
must reject unknown discriminators and executable/active-effect fields while
remaining tolerant of valid count, order, text, identifier, time, and digest
variation inside the exact schema.

## Dependencies and Parallel Safety

SLI-0030 and all of its packets are complete. This packet has no intra-slice
packet dependency because it establishes SLI-0031's first accepted seam.

It is not parallel-safe with later SLI-0031 packets: they consume these exact
schemas and domain values and would otherwise race on contract meaning, package
exports, compatibility fixtures, and Project documentation. It is also not safe
with another Project contract or Project-domain writer. Reads of unrelated files
remain permitted under the concurrent-work protocol.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete portable workspace | Valid varied notes, references, artifacts, links, and revisions | Records parse and project | Meaning and ordering round-trip without framework, storage, or provider data | schema compatibility + unit |
| Inert artifact classes | Each closed artifact and result classification with complete provenance | The manifest is validated | Exact safe metadata is accepted without an execution or correctness claim | contract/unit |
| Flexible valid shape | Boundary counts, Unicode names/text, different order, optional applicable provenance, IDs, times, versions, and digests | Fixtures are evaluated | Valid shapes pass without fixture-specific assumptions | compatibility anti-rigidity corpus |
| Path and active-effect denial | Absolute/traversal/NUL/link/archive controls, executable flags, callback/network/secret/runtime fields, or active media appear | The record is parsed | It fails closed with a bounded non-sensitive contract error | denial corpus + unit |
| Resource bounds | Text, count, nesting, logical-name, or byte limits are exceeded | Validation runs | It rejects the record before any later storage effect | boundary corpus |
| Integrity | Digest syntax or declared byte count is malformed or a supplied digest does not match tested bytes | Canonical helpers run | The mismatch fails without echoing artifact content | unit |
| Typed reference isolation | A link names an owner/type/id/version/as-of and provenance | It parses and projects | Only the reference is retained; target state, permissions, and storage facts are absent | schema/unit/architecture review |
| Snapshot immutability | One exact shell and workspace revision with varied records | Canonical snapshot material and digest are built repeatedly | Serialization and digest are deterministic; changing any material field changes the digest | vectors + unit |
| Snapshot continuation boundary | A later live revision exists | The earlier snapshot is parsed/projected again | Historical manifest, digest, and referenced versions remain unchanged | unit |
| Export manifest | One valid immutable snapshot and allowed artifact list | Export meaning is projected | Digests and provenance remain exact; secrets, host paths, credentials, authorization state, and unapproved source bytes are unrepresentable | schema/unit |
| Closed unions | An unknown artifact, provenance, result, link, lifecycle, media, or export member appears | Validation runs | It fails closed rather than guessing semantics | denial corpus |
| Existing shell compatibility | Current SLI-0030 brief, intent, and shell fixtures | The expanded suite runs | Existing bytes and meanings still pass unchanged | regression compatibility |

## Verification Commands

Run from the repository root using the pinned Python environment where shown:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/project_workspace backend/tests/unit/project/test_project_contract.py
python dev-tools/contracts/check_contracts.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_security.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

If an expected checker path has changed, inspect `dev-tools/README.md` and use
the repository-owned equivalent; do not invent a bypass. Run the affected-plan
and exact-candidate receipt flow selected by `packet-start` before completion.
No Docker, database, browser, external provider, network, or managed-cloud
qualification is required for this pure contract/domain packet.

## Documentation and Evidence Update

Update the canonical Project workspace contract and Project module README with
the exact new portable meaning, canonical digest rules, classifications,
bounds, compatibility posture, and deferred persistence/API/UI behavior. Update
the Project v1 contract README and compatibility README/corpus with executable
instructions. Reconcile derived context only if the canonical change makes it
stale; do not edit a pack merely to repeat unchanged ADR meaning.

Keep this packet, SLI-0031's packet table and planning history, and the register
synchronized through ready, active, verifying, and complete states. Record
exact candidate, qualifying receipt, checks, assumptions, and residual limits
without copying local reviewer or approval records into tracked files.

## Stop Conditions

Stop and return this packet to shaping for conflicting canonical meaning,
unknown Project ownership, inability to express a closed portable record,
breaking Project shell v1 semantics, a new origin/lifecycle, copied Portfolio or
other owner state, a provider-specific payload, unresolved license or data-use
policy, unbounded file semantics, a need for persistence/API/browser changes,
or scope that cannot be independently verified.

Stop at a durable decision boundary for execution, active rendering, archive
expansion, network, secrets, package installation, runtime images, provider
callbacks, live Portfolio integration, financial action/advice, Assessment or
Learner-model effects, general Workspace expansion, collaboration, organization
tenancy, managed-cloud protection/recovery, external providers, or a separate
local/cloud core. Stop for active overlapping file ownership or material
CAP-0007 drift.

Do not reopen review solely for harmless whitespace, optional wording,
nonfunctional styling outside this packet, or another inconsequential issue.
Fix it within scope or defer optional cleanup to CAP-0031.

## Required Handoff

Report the additive contract/domain outcome; exact schemas and classifications;
canonical snapshot/digest policy; resource bounds; approved and denial corpus;
existing-shell compatibility; files changed; exact focused and repository checks
with results; candidate and receipt; documentation impact; assumptions; residual
risks; and explicit confirmation that no storage, API, browser, execution,
Portfolio, Assessment, Learner-model, provider, or managed-cloud behavior was
added.

## Qualification Evidence

- Five additive Project v1 schemas now close live workspace state, revision-
  bound mutation intent, snapshot close intent, immutable snapshot material,
  and deterministic evidence-export manifests without changing Project shell
  v1 meaning.
- The synthetic compatibility corpus covers varied notes, references, dataset,
  notebook and simulated-result manifests, typed owner references, exact
  snapshot record versions, use-restricted export exclusions, and direct-UTF-8
  canonical digest vectors. It contains no personal or provider data and does
  not claim a live Portfolio adapter.
- Focused Project contract and domain verification passed 107 tests. The broader
  backend architecture, contract, and unit corpus passed 696 tests, including
  flexible zero/single/multiple workspace shapes and fail-closed traversal,
  cross-platform path aliases, credential-bearing URLs, incomplete export
  coverage, altered record meaning, active effects, incomplete provenance,
  unsafe inspection, stale digests, contradictory exports, and private fields.
- Repository evidence passed 16 architecture checks, ten security control
  groups, planning integrity for 202 artifacts, documentation integrity for 346
  Markdown files plus catalogs, Python compile checks, whitespace integrity,
  and all 29 aggregate readiness checks.
- A direct all-backend invocation reached database-backed API integration and
  waited for an unavailable isolated PostgreSQL environment, so it was stopped
  and is not counted as evidence. This pure packet changes no repository,
  migration, application, API, object-storage, browser, or deployment behavior;
  real PostgreSQL and live API/browser qualification belong to later packets.
- The same portable values and projectors are intended for the protected public
  API used by browser and non-browser/headless clients. No AI-specific
  transport, client-owned durable authority, execution surface, active preview,
  archive import, Assessment effect, Learner-model effect, external provider,
  managed-cloud profile, or financial action was introduced.

## Planning History

- 2026-10-16: Authored just in time as SLI-0031's first bounded packet after
  SLI-0030 completed and the workspace-to-snapshot slice was refined. It freezes
  additive portable contracts and pure policy only, preserves the public API as
  the future browser/headless boundary, and remains inside CAP-0007.
- 2026-10-16: Moved to verifying after the additive executable schemas,
  immutable domain values, parser/projector behavior, compatibility corpus, and
  synchronized contract/module documentation passed the focused and repository
  gates. Later persistence and presentation layers remain deliberately absent.
- 2026-10-16: Tightened the verifying candidate so logical paths have one NFC-
  normalized cross-platform representation, HTTPS metadata rejects embedded
  credentials, and each export embeds and digest-binds the exact snapshot and
  workspace records while accounting for every snapshot artifact. Focused and
  broad regression evidence passed without expanding packet scope.
