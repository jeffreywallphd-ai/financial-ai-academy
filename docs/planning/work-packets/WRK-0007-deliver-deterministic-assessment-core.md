---
id: WRK-0007
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0002
capability: CAP-0001
depends_on: [WRK-0006]
decision_gates: []
parallel_safe_with: []
write_scope: [backend/pyproject.toml, backend/uv.lock, backend/src/financial_ai_academy/modules/assessment, backend/src/financial_ai_academy/modules/content, backend/src/financial_ai_academy/modules/curriculum, backend/src/financial_ai_academy/platform/database, backend/migrations, backend/tests/unit/assessment, backend/tests/unit/content, backend/tests/unit/curriculum, backend/tests/integration/assessment, backend/tests/architecture, backend/README.md, backend/src/financial_ai_academy/modules/README.md, docs/domain/README.md, docs/architecture/modules/module-map.md, docs/architecture/contracts/assessment-contract.md, docs/architecture/contracts/content-package-contract.md, docs/security/community-learner-evidence-protection.md, docs/architecture/assurance/architecture-verification.md, docs/architecture/assurance/known-architecture-gaps.md, docs/assurance/known-verification-gaps.md]
generated_artifacts: [backend/uv.lock, backend/migrations]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0007:14e920d5-e593-41a2-a35a-4437cd4a224b
claimed_by: codex-agent
claimed_at: 2026-08-05T13:24:32Z
---

# Agent Work Packet: Deliver the Deterministic Assessment Core

## Objective and Deliverable

Implement the Assessment-owned domain, application, ports, PostgreSQL
evidence/outbox persistence, and public Content/Curriculum gateways needed to
open and submit WRK-0006's exact knowledge check. The observable technical
result is a repeatable application-level operation that presents no private
answer material, scores one authorized response deterministically, and commits
one immutable attempt/evidence/event set atomically without an HTTP host or
browser.

## Required Context

Before any file change, prominently read and follow every applicable
`AGENTS.md` and the repository-root `docs/README.md`. Route through the
baseline pack with `learning-adaptation` as primary and `security-risk` as
adjacent. Read SLI-0002, WRK-0006 and its exact contract outputs, SLI-0001's
Content/Curriculum handoffs, ADR-0001 through ADR-0005, ADR-0007, ADR-0008,
module dependency and data rules, assessment/content contracts, community
evidence protection, migration and testing standards, backend/module/platform
READMEs, all affected public facades, repositories, migrations, tests, and
current dependency metadata.

## Decisions and Assumptions

- Assessment owns definition interpretation, learner-safe presentation,
  response validation, attempts, deterministic scoring, feedback selection,
  completion evidence, and the completion event. Content owns immutable
  package bytes and verifies the Assessment-owned executable contract at its
  untrusted admission boundary without becoming scoring authority.
- Content adds one internal public query that returns the exact opaque
  assessment-definition bytes plus package/definition identity and digest. It
  never exposes those private bytes through the learner API. Assessment calls
  this public operation through an owned gateway; it never reads Content
  persistence or object keys.
- Curriculum adds an exact placed-assessment reference containing package,
  assessment, version, and digest tokens. Existing read-only placements remain
  compatible. Assessment resolves the reference through a Curriculum public
  operation and never reads Curriculum tables.
- Assessment exposes public application operations equivalent to
  `OpenPlacedKnowledgeCheck` and `SubmitPlacedKnowledgeCheck`. The first returns
  only WRK-0006's safe presentation. The second receives server-resolved
  learner context plus the exact submission and returns deterministic evidence
  result data.
- One learner may complete this exact placed assessment once in this slice.
  An exact replay of the same submission ID/payload returns the original
  result; conflicting reuse fails closed; a different submission after
  completion returns a bounded already-completed result and creates no retake.
- PostgreSQL is authoritative for append-oriented attempt, response, score,
  knowledge-check completion evidence, and a versioned outbox record. All are
  inserted in one transaction. No update/delete operation mutates accepted
  evidence, and no publishable event exists without its source evidence.
- Opaque ID generation and the UTC server clock are ports. Browser timestamps,
  actor/learner claims, scores, correctness, feedback selection, or evidence
  IDs are never authoritative input.
- The outbox is durable evidence for later delivery. This packet selects no
  queue, broker, worker, polling interval, delivery guarantee, consumer, or
  managed-cloud mechanism.

## In Scope

- A module-first Assessment package with domain values/errors, application
  services, owned ports, public facade, contract parser/mapper, PostgreSQL
  repository, Curriculum/Content gateways, clock/ID ports, and focused tests.
- Closed parsing of the exact WRK-0006 definition and generation of the safe
  presentation; unsupported types/policies/versions and unknown fields fail
  closed.
- Pure one-point exact-match scoring and reviewed feedback selection with
  independently expected correct/incorrect fixtures.
- Exact submission idempotency, conflicting reuse, one-completion uniqueness,
  and deterministic concurrent-request behavior.
- Append-oriented PostgreSQL records for attempt, response, score evidence,
  completion evidence, and transactional outbox, with owning migration stream,
  constraints, indexes, and bounded public repository results.
- Content admission validation for the new definition contract and a public
  exact private-definition query with no path/object-key leakage.
- Curriculum placement/reference evolution and a public exact assessment
  resolution operation that preserves existing lesson-read behavior.
- Empty-database upgrade, reapply, downgrade or forward-fix, corruption,
  rollback, database failure, and cross-module architecture evidence.
- Domain, module, contract, community-protection, backend, architecture-gap,
  and verification documentation made stale by the delivered core.

## Out of Scope

- FastAPI routes/models, Identity host composition, OpenAPI, generated
  TypeScript, web components, browser behavior, static build, local server, or
  cross-system qualification.
- Outbox delivery, retries to consumers, Learner-model/Audit consumers,
  projection, history, resume, retakes, manual review, overrides, recovery
  tooling, or managed-cloud persistence.
- New item/scoring types, mutable authoring/import endpoints, remote package
  access, event infrastructure, or changes to SLI-0001's public meaning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment module | WRK-0006 contracts and accepted ownership | `backend/src/financial_ai_academy/modules/assessment/` | Own definition meaning, scoring, evidence, outbox, and public operations |
| Content seam | Current immutable admission/read operations | Named Content module root | Validate exact definition contract and expose private bytes only to internal public consumers |
| Curriculum seam | Current exact lesson placement | Named Curriculum module root | Retain and resolve exact Assessment reference without owning its meaning |
| Persistence | Data architecture and current migrations | `backend/migrations/` and platform database root | Module-owned evidence/outbox tables and compatible placement evolution |
| Verification | Existing module/integration/architecture suites | Named backend test roots | Domain, PostgreSQL, failure, concurrency, and dependency evidence |
| Canonical docs | Domain/module/contract/security/assurance sources | Exact documents in `write_scope` | Record delivered semantics and honest gaps |

## Contracts and Interfaces

WRK-0007 consumes WRK-0006's schema IDs, definition/presentation split,
submission tokens, expected score vectors, evidence shape, event type, and
diagnostic codes without reinterpretation.

The public module chain is fixed as follows:

- Curriculum resolves one placement to exact Content and Assessment identity,
  versions, and digests.
- Content returns the exact opaque private definition for that accepted tuple
  through its public facade; Assessment's adapter performs the call.
- Assessment validates and maps the definition, emits only the safe
  presentation for reads, and remains the sole scorer for submissions.
- Assessment returns stable success, malformed, unsupported, stale/mismatch,
  unknown-option, unauthorized-context input, duplicate, already-completed,
  conflict, and unavailable results without leaking private definition data.
- The outbox payload is the exact versioned WRK-0006 event and refers to the
  committed evidence IDs. Later consumers can process by event ID and source
  evidence ID without querying Assessment internals.

Repository ports expose owned records rather than SQL/driver values. Content,
Curriculum, and Assessment may import only each other's published facade where
the direction above requires it; no module reads another schema or imports
another module's domain/adapters.

## Dependencies and Parallel Safety

WRK-0006 must complete first because its schemas, fixtures, versions, digests,
expected results, and event semantics are immutable inputs. This packet changes
shared Python metadata, three public module seams, migrations, and architecture
tests, so it has no parallel-safe peer. WRK-0008 begins only after the public
Assessment operations, safe presentation, evidence transaction, migrations,
and error taxonomy are stable and this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Open exact check | A placement references the accepted package and Assessment tuple | Assessment opens it | Safe prompt/options and exact public tokens are returned without correct answer/scoring internals | Application plus gateway integration test |
| Correct submission | Valid learner context and the declared correct option | Submit runs | Score `1/1`, correct feedback, and exactly one immutable evidence/event set commit | Domain and PostgreSQL test |
| Incorrect submission | Valid context and a declared incorrect option | Submit runs | Score `0/1`, corrective feedback, and exactly one immutable evidence/event set commit | Domain and PostgreSQL test |
| Exact replay | The same learner, submission ID, exact tokens, and option repeat | Submit runs again | Original result is returned and row/event counts do not change | Idempotency integration test |
| Conflicting reuse | A submission ID is reused with different option or version tokens | Submit runs | Conflict is returned and accepted evidence is unchanged | Domain/repository test |
| Already completed | The learner submits a different ID after one accepted completion | Submit runs | A bounded already-completed result appears and no retake evidence is created | Application/PostgreSQL test |
| Concurrent duplicate | Equivalent or conflicting requests race | Transactions resolve | One accepted evidence set exists; every other result is deterministic and bounded | Real PostgreSQL concurrency test |
| Malformed or stale input | Definition, option, package, assessment, item, policy, or digest is invalid/mismatched | Open or submit runs | Operation fails closed with no evidence/outbox and no `latest` substitution | Contract/application integration test |
| Persistence/outbox failure | A controlled insert or commit failure occurs | Submit runs | Neither partial evidence nor a publishable event remains; diagnostics are redacted | Failure-injection transaction test |
| Cross-module isolation | Assessment resolves placement and definition | Architecture scan and integration run | Only Curriculum/Content public facades are used; no foreign tables, paths, keys, or internals cross | Architecture and type assertions |
| Migration compatibility | Current SLI-0001 database upgrades and rolls back/forward | Migration commands run | Existing lesson path remains usable and Assessment state is never silently lost or reinterpreted | Empty/current database migration tests |
| Evidence confidentiality | Sentinel learner, response, definition, and path values trigger errors | Diagnostics are captured | Raw response, correct answer, session, SQL, path, and event payload material are absent | Redaction test |

## Verification Commands

```powershell
py -m uv sync --project backend --frozen
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment backend/tests/unit/content backend/tests/unit/curriculum
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment backend/tests/integration/lesson_read
backend/.venv/Scripts/python.exe -m pytest backend/tests/architecture
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

PostgreSQL integration must use a supported real disposable server with
migrations applied from empty and from the current SLI-0001 state. Report any
environment path that could not run.

## Documentation and Evidence Update

Document Assessment vocabulary, public operations, module dependencies, owned
tables/migrations, exact placement/definition references, scoring and
idempotency invariants, evidence/outbox meaning, private-host treatment,
migration behavior, direct tests, and residual gaps. Do not claim HTTP/UI,
event delivery/consumption, projection, backup/restore, remote/public hosting,
managed-cloud adapters, or end-to-end delivery. Derived context follows
canonical updates and cannot broaden them.

## Stop Conditions

- Content or Curriculum must interpret/scoring the definition, or Assessment
  must import their internals/read their tables or object keys.
- A safe presentation cannot exclude private answer/scoring fields.
- Evidence and outbox cannot commit atomically or accepted evidence can be
  updated/deleted through ordinary application behavior.
- Idempotent, conflicting, already-completed, or concurrent requests cannot be
  distinguished without duplicate/ambiguous evidence.
- Exact learner, package, assessment, item, policy, submission, or source-event
  provenance cannot be retained.
- Implementation requires a queue/broker, consumer delivery policy, retake,
  projection, recovery, cloud/tenancy, AI, or another unresolved decision.
- Existing package/API behavior breaks, a migration lacks a safe path,
  sensitive diagnostics cannot be redacted, canonical sources conflict, or an
  active write scope overlaps.

## Required Handoff

Implementation evidence recorded 2026-08-05:

- Added `open_placed_knowledge_check(OpenPlacedKnowledgeCheckRequest) ->
  KnowledgeCheckPresentation` and
  `submit_placed_knowledge_check(SubmitPlacedKnowledgeCheckRequest) ->
  KnowledgeCheckResult`. The first returns exact public tokens/prompt/options
  only; the second accepts server-resolved learner identity, scores in
  Assessment, and returns retained evidence meaning.
- Dependency direction is Assessment adapter -> Curriculum public facade and
  Assessment adapter -> Content public facade. Curriculum owns an exact
  Assessment placement record; Content validates and returns exact private
  bytes without paths/object keys; architecture tests reject module internals,
  cross-schema reads, and non-Assessment completion-event ownership.
- Added `curriculum.assessment_placements` and Assessment-owned `attempts`,
  `responses`, `scores`, `completion_evidence`, and `outbox` tables through
  separate globally named migration streams. One transaction appends all
  Assessment rows; unique learner/submission and placed-completion constraints
  distinguish replay, conflicting reuse, and already-completed input.
  Accepted rows reject ordinary update/delete.
- Correct and incorrect fixture inputs independently yield `1/1` plus
  `risk-return-correct` and `0/1` plus `risk-return-review`. Exact replay
  returns the original IDs/time/result; conflict and a different post-
  completion submission create no additional evidence.
- Against an isolated `postgres:18.4` service,
  `backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment -q`
  passed `7` tests and the existing lesson-read regression passed `5` tests.
  Evidence covered concurrent duplicate resolution, atomic outbox rollback,
  append-only rejection, event confidentiality, stream reapply, reverse
  teardown, and shared Content object storage. The uniquely named container
  and network were removed after the run.
- The aggregate backend result was `133 passed, 18 skipped` after the direct
  database run. Focused contract/unit/architecture suites, architecture and
  security runners, documentation, planning, whitespace, and deterministic
  agent readiness all passed.
- No dependency metadata changed; existing locked standard-library,
  `jsonschema==4.26.0`, and `psycopg[binary]==3.3.4` capabilities were used.
  No external registry, license service, or advisory lookup was performed.
- Canonical module, domain, Assessment/content contract, community-protection,
  and assurance sources now describe only the delivered core. HTTP identity
  authorization/composition, API/OpenAPI/client, UI, outbox delivery/
  consumption, learner projection/history, recovery, managed cloud, retakes,
  and additional item/policy types remain residual gaps handed forward.

Report public operation signatures, exact module dependency direction,
definition retrieval/presentation behavior, table/migration/constraint layout,
scoring vectors, submission and completion uniqueness, transaction/outbox
semantics, failure/concurrency/redaction results, dependency review,
documentation changes, residual risks, and the exact error/result interface
handed to WRK-0008.

## Planning History

- 2026-08-05: Shaped from SLI-0002 boundary seams 2 and 3 after WRK-0006; planning approval and implementation activation remain separate local-only stages.
