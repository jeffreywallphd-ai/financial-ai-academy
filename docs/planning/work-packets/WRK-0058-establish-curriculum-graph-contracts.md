---
id: WRK-0058
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-15
parent: SLI-0022
capability: CAP-0005
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/curriculum/v1", "contracts/compatibility/curriculum-graph/v1", "contracts/learning/README.md", "backend/src/financial_ai_academy/modules/curriculum/domain/models.py", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/tests/contract/curriculum_graph", "backend/tests/unit/curriculum/test_curriculum_graph.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0022-open-versioned-curriculum-graph.md", "docs/planning/work-packets/WRK-0058-establish-curriculum-graph-contracts.md"]
generated_artifacts: []
base_revision: aa05d51ea9da6f0eee262db1548628929f52f77b
claim_id: WRK-0058:46aa95c3-9c03-4749-a189-4b3546a412c3
claimed_by: codex-cap-0005
claimed_at: 2026-10-15T22:49:24Z
---

# Agent Work Packet: Establish Curriculum Graph Contracts

## Objective and Deliverable

Deliver the executable `curriculum-graph-v1` contract and a matching
Curriculum-owned, dependency-light validation core. One synthetic approved graph
must validate through both the JSON-schema conformance runner and public domain
types, while malformed references, disallowed topology, digest drift, and
unsupported versions fail closed with bounded stable codes. The packet ends at
the validated in-memory contract; it does not persist, publish, serve, or render
a graph.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through the baseline, curriculum/learning architecture, contract, security,
testing-quality, and planning context packs. Read the change-impact matrix,
decision readiness, CAP-0005, SLI-0022, ADR-0005, ADR-0007, adaptive-pathway and
contract architecture, the learning-contract index, Curriculum public/domain
surface and README, existing lesson and assessment placement contracts,
discovery and assessment compatibility runners, their tests, and the closest
test READMEs. Reinspect consumers before changing either public Curriculum file.

## Decisions and Assumptions

CAP-0005 and ADR-0005 assign graph identity, structure, branch meaning, and
validation to Curriculum. Content and Assessment continue to own resource
payloads; graph activities retain exact public placement and resource identity,
version, and digest without importing either module's internals. This profile
represents approved immutable graphs only. Presentation order is an optional
bounded hint, not prerequisite or advancement meaning. The first profile may
support `lesson` and `assessment` activities while keeping relationship and
branch vocabularies closed and versionable.

## In Scope

- Add Draft 2020-12 schemas under `contracts/learning/curriculum/v1/` for one
  graph and its objective, competency, activity, branch, relationship, and
  provenance records.
- Freeze `schema_version` `1.0.0`; bounded identifier, semantic-version, digest,
  title, description, collection-size, and source-reference rules; and
  `publication_state: approved`.
- Define activity kinds `lesson` and `assessment`; branch kinds `required` and
  `optional`; and typed relationships for objective-to-competency,
  activity-to-competency development/assessment, competency prerequisites, and
  activity prerequisites with endpoint-type enforcement.
- Require lesson activities to carry the exact lesson placement plus package
  ID/version/digest, and assessment activities to carry the exact assessment
  placement plus assessment ID/version/definition digest.
- Canonicalize graph meaning excluding `graph_digest`, compute SHA-256, and
  reject digest mismatch, duplicate identities, dangling references, invalid
  relationship endpoints, invalid/empty branch membership, ambiguous
  required/optional membership, prerequisite self-loops, and prerequisite
  cycles. Activities shared by branches of the same kind remain valid.
- Add a compatibility corpus with one valid multi-objective graph containing a
  required branch and more than one optional branch, stable digest vector, and
  table-driven bounded denials.
- Add stable public immutable Curriculum graph types, error codes, and a pure
  validator/converter seam that later application and persistence work can
  consume without JSON-schema or filesystem coupling.
- Prove anti-rigidity by accepting valid sibling reordering, multiple entry
  activities, optional branches, and an unbranched activity without making
  layout or a single linear path authoritative.

## Out of Scope

Repository ports, migrations, PostgreSQL, graph admission/publication commands,
graph read operations, API or OpenAPI changes, generated clients, permissions,
composition, UI, CSS, browser qualification, learner completion, eligibility,
advancement explanations, activity launch, mastery, recommendation, authoring,
external standards, tenancy, jobs, providers, or remote execution.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public contract | lesson-package, assessment, discovery schemas and contract architecture | `contracts/learning/curriculum/v1/`, `contracts/learning/README.md` | Define the portable immutable graph shape and its limits |
| Compatibility evidence | existing assessment/discovery corpora and runners | `contracts/compatibility/curriculum-graph/v1/`, `backend/tests/contract/curriculum_graph/` | Fix one approved graph, digest, denials, and dependency-light CLI behavior |
| Curriculum domain/public surface | current public types, domain digest rules, placement consumers | `backend/src/financial_ai_academy/modules/curriculum/domain/models.py`, `backend/src/financial_ai_academy/modules/curriculum/public.py` | Expose stable graph records and pure validation without leaking contract tooling |
| Focused domain evidence | Curriculum unit tests and graph consumers | `backend/tests/unit/curriculum/test_curriculum_graph.py` | Prove topology, exact references, bounded errors, and anti-rigidity |
| Module documentation | Curriculum ownership and public-operation guidance | `backend/src/financial_ai_academy/modules/curriculum/README.md` | Document the new validated contract and its current in-memory limit |
| Lifecycle | slice, packet, planning register | listed planning files | Keep packet state, boundary, and evidence synchronized |

## Contracts and Interfaces

The JSON root is `curriculum-graph-v1` and carries `schema_version`,
`curriculum_id`, `curriculum_version`, `title`, `summary`,
`publication_state`, `published_at`, `source_references`, optional bounded
`presentation_order`, `objectives`, `competencies`, `activities`, `branches`,
`relationships`, and `graph_digest`. Records have globally unique IDs within
the graph. Relationships have unique IDs, a closed kind, and typed source and
target IDs. Branches name a closed kind and one or more distinct activity IDs.
An activity may be unbranched or shared by branches of the same kind; only
conflicting required-versus-optional meaning is rejected.

Canonical graph bytes omit `graph_digest`, normalize `published_at` to UTC with
a trailing `Z`, omit empty arrays within an explicitly present
`presentation_order` object, retain that object even when empty, preserve every
other array order and value, then encode sorted-key compact JSON as UTF-8.

The packet produces immutable public tuples/dataclasses for the same meaning,
`CurriculumGraphError` with bounded error codes/references, and a pure
`validate_curriculum_graph` seam returning a validated graph. WRK-0059 may
consume only those public values and canonical graph bytes/digest behavior; it
must not depend on the contract runner, compatibility fixture paths, JSON
Schema implementation, or private Content/Assessment models.

## Dependencies and Parallel Safety

CAP-0001 and CAP-0004 are complete; neither is an active packet dependency.
This is the first SLI-0022 packet. WRK-0059 requires its exact public graph and
digest contract, so the packets are deliberately sequential and not
parallel-safe. No active packet may overlap the declared Curriculum public,
domain, contract, or planning files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Approved graph | A valid graph with exact lesson and assessment resources, one required branch, and multiple optional branches | Both validators run | The same immutable graph meaning and independently computed digest are accepted | contract/unit |
| Duplicate or dangling identity | Any node, relationship, branch, or referenced endpoint is duplicated or missing | Validation runs | Publication readiness fails with a stable bounded code and no payload echo | contract/unit |
| Flexible branch reuse | An activity is shared by multiple branches of the same kind | Validation runs | The graph remains valid without duplicating the activity; required-versus-optional ambiguity still fails closed | contract/unit anti-rigidity |
| Wrong endpoint type | A typed relationship connects valid IDs of incompatible node kinds | Validation runs | The relationship fails closed rather than being treated as a generic edge | contract/unit |
| Invalid prerequisite topology | A competency or activity prerequisite is a self-loop or cycle | Validation runs | The graph fails with the relevant bounded topology code | contract/unit |
| Exact-resource mismatch | Activity kind and exact placement/resource fields disagree or a version/digest is malformed | Validation runs | The graph is rejected before any persistence or consumer access | schema/unit |
| Digest drift | Any semantic graph field changes without recomputing `graph_digest` | Validation runs | The graph fails with `graph_digest_mismatch` | contract/unit |
| Unsupported version | `schema_version` is not `1.0.0` | Validation runs | The graph fails with `unsupported_version` before interpretation | contract/unit |
| Anti-rigidity | Valid siblings are reordered, entry activities are plural, an activity is unbranched, or optional branches are added within bounds | Validation runs | The graph remains valid and no visual layout or single linear path is required | contract/unit |
| Safe CLI failure | A denial fixture is supplied | The conformance runner executes | Output is bounded JSON with no source payload, local path, or stack trace | contract CLI |

## Verification Commands

Run:

```powershell
python .agents/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0058-establish-curriculum-graph-contracts.md
uv run --project backend pytest backend/tests/contract/curriculum_graph backend/tests/unit/curriculum/test_curriculum_graph.py
uv run --project backend python -m compileall -q backend/src backend/tests
python dev-tools/architecture/check_architecture.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
git diff --check
```

Run the packet-start selected controls and independent technical review. Run
`python dev-tools/agent/check_ready.py` if packet-start classifies the public
contract/module surface as shared impact or if focused evidence exposes broader
drift.

## Documentation and Evidence Update

Update the learning-contract index and Curriculum README without changing
canonical ownership or decision records. Keep this packet, SLI-0022, and the
planning register synchronized. At completion record exact contract fields,
allowed vocabularies, digest behavior, denial coverage, focused checks,
anti-rigidity evidence, and the persistence/API/UI work left to WRK-0059 through
WRK-0061. Never put local approval or reviewer evidence in tracked files.

## Stop Conditions

Stop for a need to change CAP-0005 outcome, slice manifest, module ownership,
Content or Assessment authority, an accepted ADR, external-standard semantics,
mutable authoring, eligibility or mastery meaning, provider payloads, tenancy,
manual override policy, generated content authority, a breaking existing
contract, an overlapping active scope, or a public interface that cannot be
made exact without a durable decision. Also stop if valid graph flexibility
would require accepting untyped edges, arbitrary executable expressions, or
client-authoritative validation.

## Required Handoff

Report the schema and public-type contract, accepted relationship/branch
vocabularies, digest and topology rules, denial and anti-rigidity evidence,
affected boundaries, exact checks/results, documentation changes, assumptions,
residual risks, and the concrete inputs handed to WRK-0059.

## Completion Evidence

- Added the Draft 2020-12 `curriculum-graph-v1` contract, an approved synthetic
  graph, canonical SHA-256 vector, and ten bounded denial cases. The contract
  retains exact lesson package and assessment definition references without
  embedding provider, storage, learner, eligibility, mastery, or recommendation
  state.
- Added immutable Curriculum graph records plus a strict mapping converter,
  canonical serializer/digest, typed-edge enforcement, branch policy, cycle
  detection, and bounded public errors. Equivalent RFC 3339 offsets and empty
  presentation hints share one canonical representation; unknown client-owned
  fields, malformed public values, and stale digests fail closed.
- Anti-rigidity coverage accepts missing/partial presentation hints, sibling
  reordering, multiple entry activities, unbranched activities, new optional
  branches, and reuse of one activity across branches of the same kind. An activity
  cannot silently acquire conflicting required and optional meaning.
- The focused graph suite passed all 26 tests, including a bounded sanitized
  CLI denial. The complete backend unit and contract suite passed all 249
  tests; Python 3.14 compilation passed; all 13
  architecture checks passed; work-packet, planning, documentation, and diff
  checks passed; and aggregate readiness passed all 27 checks. The architecture
  check used its established unsandboxed route after the Windows sandbox denied
  temporary-directory cleanup.
- Updated the learning-contract index and Curriculum README. No migration,
  repository operation, API, generated client, permission, UI, dependency,
  external service, or durable learner state changed. WRK-0059 retains
  persistence and protected transport; WRK-0060 retains the interface; and
  WRK-0061 retains live end-to-end qualification.

## Planning History

- 2026-10-15: Authored just in time as the first SLI-0022 packet. It establishes
  the immutable graph and validation seam required by all later packets without
  adding persistence, transport, interface behavior, or a new decision gate.
- 2026-10-15: Implemented and qualified the versioned graph contract and pure
  Curriculum validation core with explicit flexible-shape evidence and no
  material CAP or slice drift.
- 2026-10-15: Unified contract/domain canonicalization, bounded direct public
  validation failures, allowed same-kind branch reuse, and directly qualified
  the sanitized CLI denial path.
