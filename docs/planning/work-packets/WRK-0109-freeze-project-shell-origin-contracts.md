---
id: WRK-0109
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: SLI-0030
capability: CAP-0007
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/project/README.md", "backend/src/financial_ai_academy/modules/project/__init__.py", "backend/src/financial_ai_academy/modules/project/adapters/project_contract.py", "backend/src/financial_ai_academy/modules/project/domain/project.py", "backend/src/financial_ai_academy/modules/project/ports/project_contract.py", "backend/tests/contract/project_workspace", "backend/tests/unit/project/test_project_contract.py", "contracts/compatibility/project-workspace/v1", "contracts/learning/README.md", "contracts/learning/project/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/project-workspace-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0030-create-independent-or-learning-project.md", "docs/planning/work-packets/WRK-0109-freeze-project-shell-origin-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Project Shell and Origin Contracts

## Objective and Deliverable

Freeze additive versioned contract families for an approved learning-project
brief and a learner-owned Project shell with a closed independent-or-learning
origin union. Deliver executable schemas, a synthetic compatibility corpus,
deterministic conformance evidence, immutable Project domain values, and a
transport-neutral parser/projector boundary. The result is the stable input to
the next persistence/API packet; it creates no Project row, learning evidence,
artifact, snapshot, domain-resource link, HTTP operation, or browser behavior.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, architecture-contracts,
security-risk, testing-quality, and delivery-planning context. Read the change-
impact matrix, decision readiness, CAP-0007, SLI-0030, ADR-0011, ADR-0012,
ADR-0005, the module map and dependency rules, contract architecture and
compatibility/versioning guidance, lesson-package and current learning-contract
families, Content/Curriculum/Assessment public seams, existing immutable domain
and contract-runner patterns, the nearest module/contract/test READMEs, and the
concurrent-work protocol.

## Decisions and Assumptions

- Create a separate additive `project/workspace/v1` contract family rather than
  widening lesson, practice, discovery, or portfolio contracts. Project owns
  shell identity, charter, origin, lifecycle, and revision meaning; Content
  owns the approved learning-project brief meaning.
- The learning-project brief is immutable versioned source material with stable
  brief ID/version, title, purpose, bounded milestone descriptions, approved
  source references, and a lowercase SHA-256 digest over compact sorted-key
  UTF-8 JSON for the canonical brief object. This packet does not admit it into
  a lesson package or persist a Curriculum placement.
- Project origin is exactly one closed variant:
  - `independent`, which has no Content/Curriculum fields and makes no learning-
    progress claim; or
  - `learning`, which retains exact package, brief, curriculum, placement,
    schema, version, and digest references plus an answer-safe brief summary.
- One Project shell has a stable project ID, server-owned learner ID, bounded
  title and charter, exactly one immutable origin, `active` lifecycle, positive
  revision, and server-owned timestamps. Initial contract limits use 1-120
  characters for title and 1-4000 for charter; later changes require normal
  version/compatibility treatment rather than fixture-specific assumptions.
- Identifiers and references use normalized bounded platform strings. Learner
  prose remains Unicode text after the repository's accepted JSON handling;
  canonical hashing specifies direct UTF-8 bytes without implicit Unicode
  normalization or ASCII escaping.
- The parser validates schema and semantic correlation and returns immutable
  typed values or bounded stable `project.contract.*` failures. It performs no
  persistence, clock, identity resolution, authorization, network, provider,
  artifact, execution, Assessment, Learner-model, or Audit action.

## In Scope

- Add Draft 2020-12 schemas for the Content-owned learning-project brief,
  closed Project origin union, Project shell, create intent, and learner-safe
  public representation under one versioned Project contract family.
- Add synthetic approved independent and learning-origin examples, fixed digest
  vectors including non-ASCII learner text, and table-driven denial cases for
  unsupported, malformed, contradictory, and private-field meaning.
- Add a dependency-light contract runner that validates schemas, versions,
  canonical digests, semantic invariants, origin correlation, round-trip-safe
  projection, and absence of storage/provider/execution fields.
- Introduce the Project module's initial immutable domain values plus a narrow
  parser/projector port and adapter. Keep domain code framework-free and point
  all dependencies inward.
- Add focused contract and unit tests covering both origin types, resource
  limits, closed-world denials, origin immutability, deterministic projection,
  privacy, Unicode hashing, and anti-rigidity across valid text, IDs, metadata,
  milestones, and source-reference counts.
- Add the Project workspace contract and module guidance and synchronize the
  contract catalog, module map, planning packet, parent slice, and register.

## Out of Scope

Lesson-package project-file admission; Content/Curriculum parsers or public
operations; project-brief placement; Project application services, repository
ports, persistence, migrations, clocks, idempotency storage, authorization,
session composition, HTTP/OpenAPI, generated client, browser UI, live fixtures,
artifacts, files, previews, downloads, snapshots, exports, domain-resource or
Portfolio links, Assessment submission/completion, Learner-model projections,
Audit events, deletion, restore, execution, providers, organizations, cloud
qualification, AI mode, recommendations, or financial advice.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing learning, lesson-package, Assessment, Curriculum, and compatibility families | new `project/v1` and compatibility directories plus learning catalog | Freeze additive brief, origin, create-intent, and shell meaning without widening another family |
| Contract evidence | current dependency-light runners and canonical digest vectors | new `project_workspace` runner/tests and corpus | Prove closed variants, digest rules, privacy, bounds, and anti-rigidity |
| Project domain | module conventions and immutable domain values | new Project README, package marker, domain, port, adapter, and unit test | Establish inward-pointing typed meaning without application or persistence behavior |
| Architecture guidance | module map and contract ownership | Project contract page plus bounded catalog/map updates | Record Content versus Project authority and future public-operation seam |
| Planning evidence | SLI-0030, WRK-0109, register | listed planning files | Keep just-in-time packet lifecycle and dependency seam synchronized |

No existing learning schema, compatibility fixture, Content/Curriculum/
Assessment implementation, OpenAPI/client, persistence, migration, UI,
dependency, generated artifact, provider, or deployment composition may change.

## Contracts and Interfaces

The Content-owned `learning-project-brief-v1` contains `schema_version`,
`brief_digest`, and one closed canonical `brief` object with stable identity and
version, learner-visible title/purpose, bounded ordered milestone descriptions,
and exact approved source references. It contains no learner, Project, score,
completion, executable, provider, market-data, or Portfolio state.

The Project-owned `project-create-intent-v1` carries an idempotency key, bounded
title/charter, and one origin variant. It has no learner ID, project ID,
revision, timestamp, permission, lifecycle, or completion field because the
future application supplies those authoritatively. An independent origin
contains only its discriminator. A learning origin contains exact immutable
Content/Curriculum references and a brief summary correlated to the approved
brief; unknown or partial variants fail closed.

The `project-shell-v1` public record adds server-owned project/learner identity,
active lifecycle, revision, timestamps, and the accepted immutable origin. It
forbids artifact content, host/storage paths, credentials, provider payloads,
execution controls, Assessment state, hidden source data, and copied domain
aggregate state.

The parser port accepts JSON-compatible bytes and returns immutable brief,
intent, and shell values or a bounded stable error with a safe code/reference.
The projector returns JSON-compatible learner-safe shapes. The next packet may
consume these values through Project public application operations but may not
reinterpret their origin or digest semantics.

## Dependencies and Parallel Safety

CAP-0005 and CAP-0006 are complete; CAP-0007 authority is current; SLI-0030 is
ready; and ADR-0011/ADR-0012 resolve the required execution and ownership
decisions. WRK-0109 has no WRK dependency. It owns the new contract family,
Project module entry point, shared architecture catalog/map, parent slice, and
planning register, so it is not parallel-safe with another packet changing
those paths. It must complete before persistence/API packet JIT-B is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Approved brief | One synthetic brief has bounded milestones and sources | Schema, semantic, and digest validation run | Immutable Content-owned meaning and an independently fixed digest match | schema/runner/unit |
| Independent intent | Bounded title/charter and independent origin are supplied | Intent parsing runs | Immutable typed intent contains no learning, learner, completion, artifact, or execution field | schema/runner/unit |
| Learning intent | Exact package/brief/curriculum/placement references and safe summary correlate | Intent parsing runs | Immutable learning origin preserves every exact reference without copying source content | schema/runner/unit |
| Public shell | Server-owned identity/revision/time values and one accepted intent are projected | Shell validation runs | One closed active Project record is reproducible and learner-safe | runner/unit |
| Closed origin | Both/neither variants, partial learning references, unknown fields/types, or independent learning fields appear | Validation runs | Stable bounded schema/semantic failure exposes no private input or hidden source fact | denial corpus/unit |
| Resource bounds | Title, charter, milestone, source, ID, and reference counts sit at accepted edges | Validation runs | Valid edges pass and zero/overflow/unsafe inputs fail for the specific invariant | parameterized tests |
| Canonical digest | ASCII and non-ASCII briefs differ only by documented meaning | Independent and production hashing run | Compact sorted direct UTF-8 bytes produce the fixed lowercase digest without implicit normalization | vectors/runner/unit |
| Origin immutability | Parsed values and projected records are reused or input objects mutate afterward | Results are inspected | Accepted origin and digest meaning remain immutable and deterministic | unit tests |
| Confidential shape | Shell and failures are recursively inspected | Forbidden keys/value patterns are scanned | No storage, host, credential, provider, execution, hidden learner, or copied domain state escapes | runner/security-focused unit |
| Anti-rigidity | Valid titles, charters, IDs, milestone/source counts and harmless metadata vary | Complete focused corpus runs | Meaningful invariants hold without one fixture's wording, counts, ordering beyond contract meaning, IDs, or timestamps | parameterized contract/unit |
| Side-effect freedom | Parsers/projectors run repeatedly | Repository and collaborators are inspected | No database, clock, network, provider, event, Assessment, Learner-model, artifact, or execution effect occurs | unit/architecture |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/project_workspace backend/tests/unit/project/test_project_contract.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0109-freeze-project-shell-origin-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run existing contract-catalog and architecture regressions selected by the
affected-check plan. Submit one exact candidate, create a fresh qualifying
receipt, and obtain one independent technical disposition. Add no dependency
or lockfile change.

## Documentation and Evidence Update

Document Project and Content ownership, the two origin variants, exact
references, canonical digest, supported limits, safe failures, privacy,
unchanged existing contract families, and deliberately unimplemented package,
persistence, API, UI, artifact, snapshot, submission, execution, provider, and
cloud boundaries. Keep Project module, contract architecture, module map,
contract catalog, SLI-0030, WRK-0109, and register state synchronized.

Completion evidence must record exact focused and affected checks, compatibility
and security meaning, changed files, assumptions, environment qualifications
not performed, and residual risks. Exact verification receipts and technical
review records remain only in ignored local control-plane storage; tracked
artifacts may record objective candidate and check results but no approval or
reviewer metadata/history.

## Stop Conditions

Stop for ambiguous Content-versus-Project ownership; a need to mutate an
existing contract family; learning origin without exact immutable references;
mutable origin; learner/client-selected authority; artifact/file/snapshot/
Portfolio/Assessment semantics; persistence/API/UI/migration change; active
rendering or execution; network/secrets/packages; external providers;
organization tenancy; cloud protection/recovery; AI-authoritative behavior;
personalized financial advice; new dependency; cross-module internals; private
data leakage; conflicting canonical sources; active scope collision; or
material CAP-0007/SLI-0030 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, one incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; contract identifiers and limits; canonical digest;
origin and shell invariants; confidentiality and denial evidence; focused,
architecture, security, affected, aggregate, and receipt results; changed
files; documentation impact; assumptions; environment checks not performed;
and residual gaps. Confirm no package admission, placement, persistence,
migration, public operation, HTTP/OpenAPI, client, UI, artifact, snapshot,
domain link, Assessment evidence, AI mode, provider, or execution changed, then
leave JIT-B dependency-ready.

## Planning History

- 2026-10-16: Authored just in time after SLI-0030 refinement. The packet
  freezes a separate additive Project workspace family and pure Project domain
  boundary for both accepted origin types while leaving package admission,
  persistence, API, UI, artifacts, snapshots, submissions, domain links, and
  execution to later packets or slices. No lower-level approval is required.
