---
id: SLI-0015
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: CAP-0001
depends_on: ["SLI-0001"]
decision_gates: []
---

# Vertical Slice: Submit a Deterministic Knowledge Check

## Outcome and User Scenario

An authorized learner answers the single bounded knowledge check attached to
the exact lesson placement and receives reproducible feedback. One retry-safe
attempt, response, score, and completion-evidence chain is retained against the
exact lesson package and Assessment-owned definition.

## Scope Boundaries

### In Scope

- One versioned, single-choice Assessment definition carried as an opaque
  lesson-package resource and interpreted only by Assessment.
- Exact placement, package, definition, and learner binding; deterministic
  validation and scoring; stable explanatory feedback.
- Append-oriented attempt, response, score, completion, and versioned event
  evidence in PostgreSQL with an idempotent learner-submission key.
- Protected API/generated-client operations and an accessible knowledge-check
  panel on the existing lesson route.
- Denial, stale-definition, malformed-definition, duplicate, unauthorized,
  cross-learner, partial-write, and unavailable-storage evidence.

### Out of Scope

- Multiple questions, open-ended or executable responses, manual or model
  grading, mutable scores, overrides, mastery, credentials, and adaptive paths.
- Learner-model projection and historical reopening, which belong to SLI-0016.
- New identity modes, cloud/recovery claims, content authoring, or package UI.

## Canonical Context and Decisions

ADR-0005 through ADR-0009 and the accepted module, contract, testing, interface,
identity, content-package, and evidence-protection documents govern this slice.
Content owns immutable bytes, Curriculum owns exact placement, Assessment owns
definition meaning and scoring, and Identity supplies server-resolved learner
context. No unresolved durable decision is crossed.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| One single-choice check with complete evidence chain | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| Definition and scoring core without learner submission | no | 1 | 0 | 2 | 2 | 2 | 2 | 2 | 11 |
| General multi-item assessment engine | no | 2 | 2 | 0 | 0 | 0 | 1 | 0 | 5 |

## Selection Rationale

The first candidate is the smallest observable path that satisfies the CAP
outcome. It proves ownership and evidence semantics without prematurely
generalizing the assessment engine.

## Boundary Path

`lesson UI -> generated client -> API host -> Assessment public facade ->
Assessment domain/ports -> PostgreSQL`, with adapters calling Curriculum and
Content public facades only. Content returns the exact declared opaque resource;
Assessment validates and interprets it.

## Contracts, Data, and Provenance

Executable JSON Schemas own the single-choice definition and scored-evidence
event shapes. An attempt binds learner, placement, package ID/version/digest,
assessment ID/schema/digest, submission key, response, deterministic score,
feedback, timestamps, and event identity. Evidence is append-oriented and no
`latest` lookup or provider payload enters a domain model.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Correct or incorrect answer | Stable score and bounded feedback are returned and retained | domain/application/API/browser |
| Same submission retried | The original result is returned with no duplicate evidence | application/adapter integration |
| Same key with different response | Conflict; original evidence remains unchanged | application/adapter integration |
| Missing context or permission | Request fails before evidence is written | host/security integration |
| Stale or malformed definition | Safe conflict/invalid-definition response and no attempt | contract/application |
| Persistence failure | No partial attempt, score, completion, or event chain is visible | adapter integration |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0031 | Deliver definition, scoring, evidence, and persistence core | none | none | complete |
| WRK-0032 | Expose protected submission and definition API/client contracts | WRK-0031 | none | complete |
| WRK-0033 | Deliver the accessible lesson knowledge-check interaction | WRK-0032 | none | complete |
| WRK-0034 | Qualify and close the complete slice | WRK-0033 | none | complete |

## Verification and Qualification

Run schema conformance, domain/application units, real PostgreSQL transaction
and migration tests, architecture/security checks, OpenAPI/client generation,
web unit and Chromium accessibility/state tests, design/doc checks, full setup
qualification, and `python dev-tools/agent/check_ready.py`.

## Rollback and Migration

Migrations are additive and have explicit down scripts. Rollback removes only
the new Assessment schema after verifying no retained evidence is required.
Published package identity changes when its definition resource changes; an
existing immutable version is never rewritten.

## Stop Conditions

Stop for CAP reshaping if implementation requires model/manual grading, mutable
evidence, a new identity or tenancy model, cross-module persistence access,
external execution, or recovery guarantees. A bounded implementation defect or
packet refinement is not a new approval gate.

## Documentation Impact and Completion Evidence

Update Assessment and affected Content/API/web READMEs, executable contracts,
module-map evidence when needed, slice/register lifecycle, and exact checks.
Retain limitations: completion is not mastery, advice, certification, or
investment-performance evidence.

- **Delivered outcome and boundaries:** all four packets are complete. An
  authorized local learner can load one exact single-choice definition, submit
  it through the generated client, receive deterministic feedback, and retain
  an append-oriented attempt/response/score/completion/event chain. Content,
  Curriculum, Identity, Assessment, API-host, PostgreSQL, and web boundaries
  remain separately owned and communicate only through public surfaces.
- **Scenario evidence:** contract, domain, application, real-PostgreSQL, API,
  component, focused-browser, and live same-origin tests cover correct and
  incorrect scoring, idempotent retry, conflicting reuse, absent/forged
  authority, stale or malformed input, persistence rollback, provenance,
  accessibility, theme parity, reflow, and safe denial. The full backend suite
  passed 162 tests, the web suite passed 21 tests, focused Chromium passed seven
  scenarios, and the live PostgreSQL/Chromium path passed two scenarios.
- **Contracts and compatibility:** assessment definition/event JSON Schemas,
  compatibility fixtures, OpenAPI, and the generated TypeScript client are
  current. The successor immutable lesson package is
  `intro-risk-return@1.1.0`; the prior package remains unchanged.
- **Repository gates:** the production build transformed 98 modules;
  architecture passed eight tests, security passed ten control groups, design
  verified 125 tokens and 56 icons, documentation verified 187 Markdown files
  and catalogs, planning verified 63 artifacts, readiness passed 27 checks,
  and npm audit reported zero vulnerabilities. `git diff --check` passed with
  line-ending warnings only.
- **Documentation and data lifecycle:** Assessment, Content, Curriculum, API,
  web, local deployment, contract, module-map, assurance, security, and domain
  documentation are reconciled. Additive Assessment and Curriculum migrations
  have down scripts; rollback must first establish that retained evidence is
  no longer required. The disposable PostgreSQL container, network, and data
  root were removed after qualification.
- **Assumptions and gaps:** only loopback single-profile identity, PostgreSQL
  18.4, filesystem objects, same-origin Python static serving, and pinned
  Chromium are qualified. Cloud identity, hosted recovery, projection/history,
  multiple assessments, mastery, credentials, and model/manual grading remain
  unqualified and outside the approved slice. No material CAP drift or
  unresolved decision gate was found; lower-level completion approval is not
  required.

## Planning History

- 2026-10-15: Refined from the approved CAP-0001 manifest. The complete
  single-choice evidence path was selected; no material CAP drift or unresolved
  decision gate was found.
- 2026-10-15: WRK-0031 completed after 151 backend tests on PostgreSQL 18.4;
  protected API/client delivery is the next dependency-ready packet.
- 2026-10-15: WRK-0032 completed with current generated contracts and 162
  backend tests; the accessible lesson interaction is next.
- 2026-10-15: WRK-0033 completed with 21 web tests and 7 Chromium scenarios;
  live same-origin and whole-slice qualification is next.
- 2026-10-15: WRK-0034 completed after the Docker-backed aggregate workflow
  passed and removed its disposable state; the slice entered completion
  verification.
- 2026-10-15: Completion structure, exact verification evidence, documentation,
  migrations, limitations, and approved CAP conformance were reconciled; the
  slice closed without a lower-level approval gate.
