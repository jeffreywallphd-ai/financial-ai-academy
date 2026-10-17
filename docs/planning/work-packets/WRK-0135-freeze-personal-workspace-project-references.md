---
id: WRK-0135
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0071
capability: CAP-0017
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope:
  - contracts/learning/personal-workspace/v1/learning-reference.schema.json
  - contracts/learning/personal-workspace/v1/README.md
  - contracts/compatibility/personal-workspace/v1/README.md
  - contracts/compatibility/personal-workspace/v1/valid-project-workspace-note.json
  - contracts/compatibility/personal-workspace/v1/valid-project-snapshot-bookmark.json
  - contracts/compatibility/personal-workspace/v1/valid-project-artifact-bookmark.json
  - backend/src/financial_ai_academy/modules/personal_workspace/README.md
  - backend/src/financial_ai_academy/modules/personal_workspace/domain/workspace.py
  - backend/src/financial_ai_academy/modules/personal_workspace/public.py
  - backend/src/financial_ai_academy/modules/personal_workspace/ports/learning_reference.py
  - backend/src/financial_ai_academy/modules/personal_workspace/adapters/workspace_contract.py
  - backend/src/financial_ai_academy/modules/personal_workspace/adapters/project_reference.py
  - backend/tests/contract/personal_workspace/test_personal_workspace_contract.py
  - backend/tests/unit/personal_workspace/test_workspace_contract.py
  - backend/tests/unit/personal_workspace/test_project_reference_gateway.py
  - docs/architecture/contracts/personal-workspace-contract.md
  - docs/architecture/contracts/project-workspace-contract.md
  - docs/architecture/modules/module-map.md
  - docs/planning/vertical-slices/SLI-0071-organize-project-workspaces-snapshots-resources.md
  - docs/planning/work-packets/WRK-0135-freeze-personal-workspace-project-references.md
  - docs/planning/register.md
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Personal-Workspace Project References

## Objective and Deliverable

Deliver the additive, closed contract and reusable adapter seam that lets the
Personal workspace accept safe typed references to an authorized Project
workspace, immutable snapshot, or inert artifact manifest. Reuse Project's
existing public operations, retain only bounded safe facts, and prove that no
Project content, permission, artifact bytes, storage locator, or execution
authority enters the Personal-workspace core.

This packet leaves persistence, HTTP/OpenAPI, generated-client, browser, and
live qualification work to its dependent packets.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed architecture/contracts and
delivery-planning context, change-impact matrix, decision-readiness register,
ADR-0011, ADR-0012, ADR-0021, CAP-0017, SLI-0071, both affected module READMEs,
the current Personal-workspace schemas/core/tests, and Project's public
operations and contract guidance.

## Decisions and Assumptions

- Project remains authoritative for its shell, mutable workspace, immutable
  snapshots, inert artifact manifests, access, and lifecycle.
- Existing public `open_project`, `open_workspace`, and `open_snapshot`
  operations provide the accepted source facts. A dedicated new Project
  operation is unnecessary unless implementation proves those public outputs
  cannot support safe exact resolution without internal imports or ambiguity.
- The Personal workspace owns organization and an accepted safe reference
  snapshot only. A stored reference is not a permission grant and never makes
  Project content available.
- Add exactly three reference kinds: `project_workspace`, `project_snapshot`,
  and `project_artifact`. Each is versioned and closed under the existing v1
  additive union.
- The artifact reference identifies the inert manifest by Project, artifact ID
  and version, kind, logical path, media type, inspection mode, byte count, and
  content digest. It excludes provenance URLs, artifact bytes, object keys,
  download locators, environments, assumptions, and execution controls.
- Safe destinations are application-relative Project routes derived by the
  adapter, not arbitrary URLs supplied by Project records or learners.

## In Scope

- Extend the executable Personal-workspace learning-reference schema and pure
  immutable domain union for the three Project reference kinds.
- Add public typed selectors that contain only exact Project, snapshot, and
  artifact identity; learner identity remains server-owned.
- Add a Personal-workspace Project adapter that depends only on
  `financial_ai_academy.modules.project.public.ProjectOperations`, calls the
  minimum public reads for each selector, correlates all returned identities,
  and maps bounded failures to `PersonalWorkspaceSourceUnavailable`.
- Extend Personal-workspace parsing/projection so existing note and bookmark
  mutations accept and round-trip the new closed variants without changing
  collection, revision, digest, quota, or mutation semantics.
- Add compatibility examples and focused contract/unit evidence for each
  variant, mixed-reference workspaces, exact safe-field sets, missing and
  cross-learner denial, mismatched identities, unavailable Project operations,
  no byte/download call, confidential failures, and varied valid manifests.
- Update affected module/contract architecture guidance, SLI-0071, this
  packet, and the planning register.

## Out of Scope

Personal-workspace application-service composition; source-adapter dispatch;
PostgreSQL changes or migrations; API models/routes; reviewed OpenAPI;
generated clients; browser UI or Project contextual save links; live Docker,
PostgreSQL, browser, headless, restart, or cleanup qualification; Project
mutation, snapshot close, artifact upload/download/export; artifact bytes;
active preview or rendering; network/subprocess/package/provider execution;
Portfolio or other domain resources; search/filter; collaboration; cloud or
organization policy; AI authority; financial advice; dependency or lockfile
changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contract | Current reference/workspace/mutation schemas and compatibility examples | Personal-workspace learning-reference schema, README, and three new compatibility examples | Add the closed Project variants without widening existing record/mutation meaning |
| Pure core | Personal-workspace immutable values and contract adapter | Domain union, public selectors, parser/projector, port typing, focused tests | Admit safe typed targets while retaining existing deterministic mutation policy |
| Public source adapter | Project public protocol and safe Project domain values | New Personal-workspace-owned `project_reference.py` and focused adapter tests | Translate public Project facts without importing internals or copying target authority |
| Architecture guidance | Current Personal-workspace and Project contract/module descriptions | Listed module and architecture Markdown files | Make ownership, safe fields, and inert boundaries explicit |
| Planning evidence | SLI-0071, WRK-0135, register | Listed planning files | Keep packet lifecycle and next seam synchronized |

No Project implementation, Project contract/schema, Personal-workspace
persistence/application/API/client/UI, migration, dependency, provider, or
deployment file may change.

## Contracts and Interfaces

`project_workspace` retains `project_id`, safe Project title/lifecycle,
`project_revision`, `workspace_revision`, application-relative destination,
`target_status=available`, validation time, and owner/kind discriminators.

`project_snapshot` retains those Project facts plus `snapshot_id`, exact
snapshot `workspace_revision`, `snapshot_digest`, and `closed_at`.

`project_artifact` retains safe Project title/revision plus exact current
workspace revision and artifact ID/version, artifact kind, logical path, media
type, inspection mode, byte count, content digest, creation time, safe route,
availability, and owner/kind discriminators. It is a reference to an inert
manifest, not a download or execution handle.

The adapter accepts one public selector and a server canonical validation time,
uses learner-bound Project operations supplied by the application layer, and
returns a Personal-workspace `LearningReference`. It rejects malformed IDs,
missing Project/snapshot/artifact, cross-result correlation failures, and every
Project public failure through one bounded source-unavailable error that does
not echo private Project, learner, path, or storage data.

Existing learning-opportunity and placed-lesson documents remain compatible.
Workspace digests remain compact sorted-key direct-UTF-8 canonical hashes, and
existing note/bookmark/collection mutation semantics are unchanged.

## Dependencies and Parallel Safety

CAP-0007 and SLI-0070 are complete. SLI-0071 is ready in the current CAP-0017
package with no decision gate. WRK-0135 has no WRK dependency. It owns the
shared reference schema/core and therefore is not parallel-safe with another
packet touching Personal-workspace reference meaning. It must complete before
the persistence/API packet is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Workspace reference | One learner-owned Project shell and workspace are returned through public operations | The Project selector resolves and round-trips | Exact safe Project/workspace revisions and route are retained without charter, origin payload, notes, sources, artifacts, links, or permission state | schema/adapter/unit |
| Snapshot reference | One authorized immutable snapshot correlates to the selected Project | The snapshot selector resolves | Exact snapshot ID, digest, workspace revision, and close time round-trip without snapshot material | schema/adapter/unit |
| Artifact reference | One authorized current inert artifact manifest correlates to the selector | The artifact selector resolves | Safe manifest facts round-trip without bytes, source URL, environment, assumptions, object key, download locator, preview, or execution control | schema/adapter/security-focused unit |
| Mixed workspace | Learning and Project reference variants appear in notes/bookmarks and ordered collections | Existing pure mutation and projection run | All variants coexist without changing record, collection, revision, quota, or digest policy | contract/unit anti-rigidity |
| Missing or denied target | Public Project reads return not-found, unavailable, mismatched, or cross-learner meaning | Resolution runs | One bounded source-unavailable failure is returned and no protected value is echoed | adapter/unit |
| Public-only boundary | The adapter resolves every selector | Dependencies and calls are inspected | Only Project public operations are imported/called; no repository, database, object storage, download, export, mutation, or internal module seam is reachable | architecture/unit |
| Closed shape | Extra private, target-content, storage, provider, permission, or execution fields are injected | Contract validation runs | The document fails closed while existing valid variants remain compatible | schema/contract |
| Flexible manifests | Project titles, revisions, artifact kinds, paths, media types, sizes, digests, optional source state, and generated times vary within bounds | Complete focused corpus runs | Meaningful invariants hold without exact fixture wording/count/order or presentation assumptions | parameterized contract/unit |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace backend/tests/unit/project/test_project_service.py backend/tests/unit/project/test_project_workspace_service.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0135-freeze-personal-workspace-project-references.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run the affected-check plan for the exact changed paths. Submit one exact
candidate, create a fresh qualifying receipt, and obtain one independent
technical disposition. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document all three Project reference variants, the retained and prohibited
fields, public-only resolution, revalidation/denial meaning, inert behavior,
unchanged target authority, and the next persistence/API seam. Keep the module
READMEs, contract architecture, module map, SLI-0071, WRK-0135, and register
synchronized.

Completion evidence must record exact focused/affected checks, compatibility,
confidentiality, public-only call evidence, no-download/no-execution evidence,
anti-rigidity variations, changed files, assumptions, unqualified environment
checks, and residual risks. Receipts and reviewer records stay only in ignored
local control-plane storage.

## Stop Conditions

Stop for ambiguous Project/Personal-workspace ownership; need to copy target
content or permission; need for a dedicated Project operation that changes
Project contract meaning; source URL or storage locator exposure; Project
mutation or download; persistence/API/client/UI/migration change; artifact
bytes or execution; Portfolio/domain expansion; cross-module internals; new
dependency; private-data leakage; unresolved decision; conflicting canonical
sources; active scope collision; or material CAP-0017/SLI-0071 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report the exact candidate; the three reference contracts and safe-field sets;
public Project calls used; compatibility, confidentiality, denial, mixed-
reference, anti-rigidity, architecture, security, affected, aggregate, receipt,
and independent-review results; changed files; documentation impact;
assumptions; unqualified environment checks; and residual gaps. Confirm no
Project mutation, persistence, migration, public API/OpenAPI, generated client,
browser, artifact download/content, provider, AI, or execution behavior changed,
then leave the persistence/API seam dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0071 refinement. The packet
  freezes the additive Project-reference union and reusable public-operation
  adapter without widening Project authority or starting persistence, API,
  client, UI, or live qualification work. No lower-level approval is required.
