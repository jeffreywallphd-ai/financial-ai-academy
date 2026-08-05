---
id: WRK-0002
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0001
capability: CAP-0001
depends_on: ["WRK-0001"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/pyproject.toml", "backend/uv.lock", "backend/src/financial_ai_academy/modules/content", "backend/src/financial_ai_academy/modules/curriculum", "backend/src/financial_ai_academy/platform/database", "backend/src/financial_ai_academy/platform/object_storage", "backend/migrations", "backend/tests/unit/content", "backend/tests/unit/curriculum", "backend/tests/integration/lesson_read", "backend/tests/architecture", "docs/architecture/modules/module-map.md", "docs/domain/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md"]
generated_artifacts: ["backend/uv.lock", "backend/migrations"]
base_revision: a9503220007fedb9b67113a1b3f1e6e498fc6205
claim_id: WRK-0002:62727714-6522-4926-a21b-c0188679a670
claimed_by: codex-agent
claimed_at: 2026-08-05T00:26:09Z
---

# Agent Work Packet: Deliver the Approved-Lesson Read Core

## Objective and Deliverable

Implement the backend domain, application, port, PostgreSQL metadata, and local-filesystem object-storage behavior required to admit one WRK-0001-conformant package, place its exact immutable version in Curriculum, and open a safe lesson-reading result through public Content and Curriculum operations. The observable deliverable is a repeatable application-level read path that returns objectives, constrained body nodes, sources, version, digest, and provenance without an API host or browser.

## Required Context

Before changing files, prominently read and follow every applicable `AGENTS.md` and repository-root `docs/README.md`. Route through the baseline pack with `architecture-contracts` as primary and `testing-quality` as adjacent. Read SLI-0001, WRK-0001 and its accepted outputs, ADR-0001, ADR-0003, ADR-0005, ADR-0007, the module map and dependency rules, contract architecture, content-package contract, data architecture, testing standards, backend/module/platform READMEs, affected contracts, migrations, consumers, and tests.

## Decisions and Assumptions

- Content exclusively owns package admission, immutable publication metadata, constrained lesson body, educational-source provenance, and object-storage references.
- Curriculum exclusively owns placement and retains only exact Content identifiers: package ID, semantic version, and digest. It calls the public Content facade and never reads Content tables or object keys.
- Package parsing and safe intermediate-representation creation occur at Content admission. The public read result contains only allowed typed nodes; later API and web packets never receive raw CommonMark or use an unsafe HTML sink.
- PostgreSQL is the transactional metadata store. SQLite or in-memory persistence cannot substitute for integration evidence. Each module owns its tables and migration objects.
- Local package bytes use a filesystem adapter behind a Content-owned object-storage port. Public results expose no host path, storage key, database identifier, or provider payload.
- Admission becomes visible only after validation and durable object finalization succeed. Database failure may leave a quarantined/orphan object for bounded cleanup, but it must never create a published partial package or overwrite immutable bytes.
- SQL, migration, and CommonMark implementation libraries are replaceable dependencies pinned through `backend/uv.lock`; the implementing agent may select compatible exact patches but may not alter the accepted ownership, persistence, or safe-rendering boundaries.

## In Scope

- Module-first Content and Curriculum packages with domain, application, ports, adapters, public facades, and focused tests.
- Immutable package identity/version/digest values, publication state, source provenance, placement identity, and typed safe lesson-reading result.
- Atomic admission orchestration, idempotent re-admission of identical bytes, immutable-conflict denial, exact-version resolution, and no `latest` fallback.
- PostgreSQL migrations and repositories for Content metadata/publication and Curriculum placement, without cross-module table access.
- Local filesystem object storage with normalized opaque keys, restrictive root behavior, staged writes, integrity verification, bounded reads, and safe cleanup.
- The minimum controlled seed/test operation needed to admit the reviewed package and create one placement; no general import or authoring interface.

## Out of Scope

- Identity sessions, HTTP/API operations, OpenAPI, generated clients, web application behavior, or deployment composition.
- Knowledge-check interpretation, response validation, scoring, attempts, completion evidence, Learner-model projections, Audit event delivery, or workers.
- Mutable publication UI, arbitrary imports, archive extraction, removal of referenced published packages, backup/restore, managed object storage, or cloud qualification.
- New domain meaning beyond the exact read-only slice.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Content module | WRK-0001 contracts and ADR-0007 | `backend/src/financial_ai_academy/modules/content/` | Own admission, publication, safe body, provenance, and storage port |
| Curriculum module | ADR-0005 and module map | `backend/src/financial_ai_academy/modules/curriculum/` | Own exact-version placement and public read composition |
| Persistence | Data architecture and module ownership | `backend/src/financial_ai_academy/platform/database/`, `backend/migrations/` | PostgreSQL runtime and module-owned migrations |
| Object storage | Content storage port and local profile | `backend/src/financial_ai_academy/platform/object_storage/` | Local filesystem adapter without path leakage |
| Verification | Existing backend test layout | Named unit and integration roots in `write_scope` | Focused domain/application/adapter evidence |
| Documentation | Module/domain and assurance maps | Named documents in `write_scope` | Record delivered public operations and direct evidence only |

## Contracts and Interfaces

WRK-0002 consumes the exact schemas, diagnostic codes, digest rules, limits, and fixture corpus from WRK-0001.

It produces public typed operations equivalent to:

- Content `AdmitLessonPackage(request) -> AcceptedPackageVersion` and `GetPublishedLessonVersion(request) -> PublishedLesson`;
- Curriculum `CreateLessonPlacement(request) -> LessonPlacement` and `OpenPlacedLesson(request) -> LessonReadingResult`.

`LessonReadingResult` carries placement ID, package ID/version/digest, title, objectives, a closed typed body-node union, approved HTTPS sources with reviewed provenance fields, passive asset references through application-controlled identifiers, and publication/provenance metadata. Error results distinguish unavailable, not found, unsupported version, invalid package, immutable conflict, and integrity failure without leaking internals.

## Dependencies and Parallel Safety

WRK-0001 must complete first because its contract family, digest bytes, fixtures, and limits are accepted inputs. This packet shares Python metadata and establishes public results consumed by every later packet, so it has no parallel-safe peer. WRK-0003 starts only after public operations, migrations, and integration behavior are stable.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Admit and open | The approved fixture and an exact Curriculum placement | Content admits it and Curriculum opens the placement | The result contains the expected safe body, objectives, sources, version, digest, and provenance | Application plus PostgreSQL/filesystem integration test |
| Identical retry | The same package identity/version/digest was already admitted | Admission repeats | The operation is idempotent and does not duplicate or replace state | Content domain/repository test |
| Immutable conflict | The identity/version exists with different bytes or digest | Admission runs | The conflict is rejected and accepted bytes/metadata remain unchanged | Domain and adapter integration test |
| Missing or stale version | A placement references an absent or unsupported exact version | The read operation runs | A bounded unavailable/not-found result is returned; no newer version is substituted | Curriculum application test |
| Malformed or unsafe package | A WRK-0001 negative fixture is submitted | Admission runs | Validation fails before publication or placement visibility | Contract/application integration test |
| Storage or database failure | Staging, finalization, transaction, or read fails | Admission or open runs | No partial publication appears, diagnostics are redacted, and cleanup is bounded | Failure-injection integration tests |
| Module isolation | Curriculum resolves a placement | The operation needs Content data | It calls the public Content facade and never imports Content internals or queries Content tables | Architecture/public-surface test |
| Provider-neutral result | Filesystem storage fulfills the request | The public result is inspected | No filesystem path, storage key, database row, or driver type crosses the facade | Contract/type assertion |

## Verification Commands

```powershell
uv sync --project backend --frozen
uv run --project backend pytest backend/tests/unit/content backend/tests/unit/curriculum
uv run --project backend pytest backend/tests/integration/lesson_read
uv run --project backend pytest backend/tests/architecture
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

PostgreSQL integration must run against a supported real server with migrations applied from an empty database. Report any container/runtime qualification that could not run locally.

## Documentation and Evidence Update

Document the implemented public module operations, owned data, migration boundary, storage port, and exact direct/remaining-gap evidence in the module map, domain guide, architecture verification map, and known verification gaps. Do not claim API, browser, managed-cloud adapter, backup/recovery, or end-to-end delivery.

## Stop Conditions

- Curriculum would import Content internals, use Content persistence, or treat a storage key as a public contract.
- Admission cannot remain fail-closed and non-visible across validation, object finalization, and metadata persistence.
- Implementation needs to change WRK-0001 compatibility-sensitive schema or digest rules.
- A safe closed body-node representation cannot be produced without raw HTML, active content, or implicit access.
- Work expands into Assessment execution, learner evidence, identity, API, UI, general imports, removal policy, recovery, or cloud storage.
- A migration lacks an upgrade plus downgrade or forward-fix strategy, canonical sources conflict, or active write scope overlaps.

## Required Handoff

Report public operation signatures, owned tables and migrations, object-key and staging rules, transaction/failure behavior, focused and PostgreSQL integration results, architecture checks, documentation updates, residual cleanup limitations, and exact inputs handed to WRK-0003.

## Planning History

- 2026-08-04: Shaped from SLI-0001 boundary seams 2 through 4 after WRK-0001; planning approval and implementation activation remain separate local-only stages.
