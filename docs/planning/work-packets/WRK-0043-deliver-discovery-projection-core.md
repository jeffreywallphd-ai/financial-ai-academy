---
id: WRK-0043
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0018
capability: CAP-0004
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/README.md", "contracts/learning/discovery/v1", "contracts/compatibility/README.md", "contracts/compatibility/discovery/v1", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/src/financial_ai_academy/modules/curriculum/domain/models.py", "backend/src/financial_ai_academy/modules/curriculum/application/service.py", "backend/src/financial_ai_academy/modules/curriculum/ports/content_gateway.py", "backend/src/financial_ai_academy/modules/curriculum/ports/repositories.py", "backend/src/financial_ai_academy/modules/curriculum/adapters/content_gateway.py", "backend/tests/contract/discovery", "backend/tests/unit/curriculum/test_discovery_service.py", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/contracts/discovery-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0018-browse-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0043-deliver-discovery-projection-core.md"]
generated_artifacts: []
base_revision: 419f40c69f56be6b9a5464ef0e86f3383d21e2f0
claim_id: WRK-0043:72251e82-7103-40c1-ad61-e9d6cab49b5c
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T17:33:10Z
---

# Agent Work Packet: Deliver the Discovery Projection Core

## Objective and Deliverable

Deliver the versioned learning-opportunity record and a deterministic
Curriculum application core that rebuilds and browses an approved-lesson
discovery projection from exact public Content facts plus Curriculum-owned
classification, with conformance and denial evidence independent of storage,
HTTP, or browser concerns.

## Required Context

Before changing any file, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the delivery-planning and
architecture-contracts context, CAP-0004, SLI-0018, decision readiness,
ADR-0005, ADR-0007, contract/versioning standards, Content/Curriculum public
operations and module READMEs, the exact lesson-package contract, Curriculum
service/ports/tests, module-boundary tests, and the nearest contract and backend
README files.

## Decisions and Assumptions

Discovery remains inside the accepted Curriculum owner: it projects exact
Content publication facts and Curriculum placement/classification facts but
does not become a new business module. Content remains authoritative for title,
objectives, package version/digest, publication state, and provenance.
Curriculum owns catalog summary, topic, level, estimated duration,
prerequisite summary, opportunity kind, availability, and exact placement
destination. The initial implementation admits only `lesson` records backed by
an exact existing placement and published Content version; other enum values
are contract vocabulary, not a claim that their execution is delivered.

## In Scope

- Add additive discovery v1 JSON Schemas, approved/denied compatibility
  fixtures, canonical serialization/digest rules, and a dependency-free
  conformance runner.
- Add closed Curriculum public value types and operations for registering exact
  lesson discovery classification, rebuilding one atomic projection generation,
  and browsing its stable approved records.
- Add repository ports that keep source classification and replaceable
  projection state owned by Curriculum, with no cross-module persistence
  references.
- Extend the Content gateway only through Content's existing public exact-read
  operation; no Content internals, raw package bytes, paths, or object keys.
- Enforce bounded identifiers/text, closed enums, exact placement/package
  agreement, deterministic ordering and source fingerprints, idempotent
  registration, conflict denial, no silent version substitution, all-or-nothing
  rebuild semantics, and bounded unavailable errors.
- Add focused contract, application, architecture, replay, conflict, missing
  source, malformed input, and failure tests plus the core contract/module docs.

## Out of Scope

PostgreSQL migrations/adapters, bootstrap composition, API/OpenAPI/generated
client, browser UI, search/filter/sort options beyond the fixed browse order,
pagination, stale-index serving, background indexing, external search, new
modules, Content package changes, Identity transport authorization, non-lesson
destinations, enrollment, eligibility, recommendations, and CAP completion.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Portable discovery contract | Contract/versioning policy and existing learning families | Listed discovery schemas, fixtures, runner, READMEs | Fix exact record and browse semantics before adapters |
| Curriculum public/application core | Existing placement operations, ports, service, fakes | Listed Curriculum files | Own classification, deterministic projection/rebuild, and stable browse policy |
| Content seam | Exact public read and Curriculum adapter | Listed Curriculum gateway files only | Map authoritative Content facts without changing Content |
| Architecture evidence | Current module/public/persistence rules | Listed architecture test and docs | Prove projection ownership and public-only dependency |
| Planning | Parent slice, packet, register | Listed planning artifacts | Preserve bounded lifecycle and evidence |

## Contracts and Interfaces

Discovery v1 uses `schema_version: 1.0.0`, stable opportunity/placement IDs, an
exact `/learn/placements/{placement_id}` destination, closed kind/level/
availability values, bounded display fields, exact package version and SHA-256
digest, normalized UTC publication/projection times, publication provenance,
and a SHA-256 source fingerprint over canonical owner facts. Browse output is a
stable ordered tuple and one projection generation identifier; it contains no
learner/provider identity, package body, answers, drafts, storage keys, table
details, eligibility, recommendation score, or execution promise.

Registration is idempotent for identical Curriculum classification and rejects
identity reuse with different facts. Rebuild reads exact lesson placements and
Content through owned ports, validates every record before atomic replacement,
and publishes no partial generation if any source is missing, stale,
conflicting, or unavailable. Browse orders by normalized title then stable
opportunity ID; later query semantics may consume but not redefine this record.

## Dependencies and Parallel Safety

CAP-0001 is complete and supplies accepted exact Content/Curriculum seams.
WRK-0043 has no SLI-local predecessor. It is not parallel-safe because it owns
the record contract and public application inputs required by every later
SLI-0018 packet.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Contract conformance | Approved lesson discovery fixture | Schemas and runner validate it | Exact canonical record/browse bytes and digest are stable | contract tests |
| Exact projection | Registered classification matches an exact placement and published Content version | Rebuild runs | One record contains only mapped owner facts and a stable source fingerprint | application tests |
| Repeat rebuild | Authoritative inputs are unchanged | Rebuild runs twice | Semantic records/order/fingerprint are identical and generation replacement is idempotent | application tests |
| Classification conflict | Existing opportunity identity is reused with different Curriculum facts | Registration runs | Conflict is rejected without replacing source facts | application tests |
| Missing or stale source | Placement or exact Content version/digest is absent or mismatched | Rebuild runs | It fails closed and publishes no partial/new generation | application tests |
| Unsupported kind | A non-lesson registration lacks an accepted owned destination | Validation runs | It is denied rather than presented as executable | contract/application tests |
| Repository failure | Source read or atomic replace fails | Rebuild/browse runs | Bounded unavailable result exposes no storage detail and retains last complete generation | application tests |
| Stable browse | Multiple valid records exist | Browse runs | Records use deterministic title/ID ordering with no ranking or personalization | application tests |
| Boundary integrity | Architecture tests inspect Curriculum | Tests run | Only Content public surface is imported and repository ports contain no cross-module access | architecture tests |

## Verification Commands

Run the work-packet validator and implementation gate; discovery contract tests;
focused Curriculum unit tests; backend architecture tests; full backend unit
and contract tests that do not require the later persistence adapter; contract,
documentation, planning, and security checks; and `git diff --check`. Use the
repository-managed Python 3.14 environment.

## Documentation and Evidence Update

Update the learning/compatibility contract indexes, Curriculum README,
discovery contract, module map, packet, slice, and register. Record exact
contract vectors, focused test counts, compatibility classification, failure
coverage, unchanged Content/package behavior, unsupported kinds/profiles,
residual persistence/API/UI work, and CAP-package conformance.

## Stop Conditions

Stop if implementation requires a new module, Content-internal or cross-schema
access, a package-format or breaking existing contract change, an authoritative
copy of Content publication facts, non-lesson execution claims, personalized or
model ranking, external provider/tenancy/commercial policy, partial projection
publication, mutable source history, or any material CAP/SLI change.

## Required Handoff

Return the record/application result, exact files and boundaries affected,
contract and focused test evidence, failure/denial coverage, documentation and
migration impact, unsupported profiles and kinds, residual risks, CAP
conformance, packet lifecycle result, and whether WRK-0044 is eligible.

## Verification Progress

- Discovery v1 now has closed opportunity and browse schemas, approved and
  denial fixtures, canonical source/generation digest vectors, and a
  dependency-free runner. The committed vector produced source fingerprint
  `6206218a3a49b2439ec3d46054f2c96f004cc680021b8b25e0f62b1f211894f5`
  and generation
  `746b3442477c7e3d70b0886cee11a0e1a439b58b7fcc4b660d790ce3cf92f3d8`.
- Curriculum owns registration, exact public Content/placement validation,
  deterministic rebuild, all-in-memory validation before atomic replace,
  stable title/ID ordering, and bounded fail-closed browse behavior. No
  persistence, HTTP, browser, non-lesson execution, ranking, or personalization
  was introduced.
- Backend unit, contract, and architecture qualification passed 193 tests.
  Architecture fitness passed eight checks, security passed ten control groups,
  documentation validated 201 Markdown files plus both catalogs, planning
  integrity passed 76 artifacts, and aggregate readiness passed all 27 checks
  against base `419f40c69f56be6b9a5464ef0e86f3383d21e2f0`.
- Bounded correctness corrections now reject malformed or oversized stored
  classification sets before replacement, validate every persisted record and
  one coherent projection timestamp before browse, translate unexpected
  Content-gateway failures to a redacted unavailable result, and reject
  malformed registration runtime types without leaking raw exceptions.
- Exact-candidate affected verification passed the selected planning-tool,
  planning-integrity, documentation-integrity, and architecture-integrity
  checks for corrected commit `f39c297416b8a480894cc3e5ddf09a54110106e9`;
  all bounded correctness defects were closed and no packet-level gap remains.

## Planning History

- 2026-10-15: Authored as the first dependency-defining SLI-0018 packet. It
  keeps discovery in Curriculum, preserves exact Content authority, and adds no
  decision gate or material CAP change.
- 2026-10-15: Reclaimed on the repaired control-plane base after a bounded
  submit-CLI correction; implementation and pre-submission qualification passed
  and the packet moved to `verifying`.
- 2026-10-15: Tightened stored-source, projection-coherence, gateway-failure,
  and runtime-type validation within the approved packet after technical
  verification identified bounded correctness defects.
- 2026-10-15: Completed after exact-candidate affected verification, 193
  backend tests, all aggregate readiness checks, and closure of the bounded
  correctness defects. WRK-0044 is now dependency-eligible.
