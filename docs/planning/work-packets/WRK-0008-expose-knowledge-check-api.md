---
id: WRK-0008
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0002
capability: CAP-0001
depends_on: [WRK-0007]
decision_gates: []
parallel_safe_with: []
write_scope: [backend/src/financial_ai_academy/hosts/api, backend/src/financial_ai_academy/bootstrap, backend/src/financial_ai_academy/platform/security, backend/tests/integration/api, backend/tests/unit/identity, contracts/api/openapi.json, apps/web/package.json, apps/web/package-lock.json, apps/web/scripts/generate-api-client.mjs, apps/web/src/generated/api-client, apps/web/tests/contract, backend/README.md, apps/web/README.md, docs/security/local-identity-architecture.md, docs/architecture/assurance/architecture-verification.md, docs/assurance/known-verification-gaps.md]
generated_artifacts: [contracts/api/openapi.json, apps/web/package-lock.json, apps/web/src/generated/api-client]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0008:6e43cbc5-5a1c-42cc-8540-354ad9a3540a
claimed_by: codex-agent
claimed_at: 2026-08-05T13:47:13Z
---

# Agent Work Packet: Expose the Knowledge-Check API

## Objective and Deliverable

Compose WRK-0007's public Assessment operations behind the existing
provider-neutral learner context, thin FastAPI host, reviewed OpenAPI snapshot,
and generated TypeScript client. The observable technical result is an
authenticated browser contract that retrieves one safe knowledge-check
presentation and submits one exact idempotent response without exposing
correct-answer internals or accepting client-selected learner/scoring data.

## Required Context

Before any file change, prominently read and follow every applicable
`AGENTS.md` and the repository-root `docs/README.md`. Route through the
baseline pack with `architecture-contracts` as primary and `security-risk` as
adjacent. Read SLI-0002, WRK-0007's public operations/error taxonomy, SLI-0001
Identity/API/generated-client handoffs, ADR-0001, ADR-0002, ADR-0005,
ADR-0006, ADR-0008, ADR-0009, the identity-provider and Assessment contracts,
local identity security architecture, contract compatibility rules, module
dependency rules, API/bootstrap/web READMEs, current OpenAPI generator and
snapshot, generated-client tooling, consumers, API/client tests, dependency
metadata, and redaction guidance.

## Decisions and Assumptions

- Preserve the existing opaque HttpOnly `SameSite=Strict` session and
  provider-neutral `LearnerContext`. Path/body/header fields never select an
  actor, learner, identity provider, score, correctness, feedback, evidence
  identifier, or server timestamp.
- Add a safe presentation operation equivalent to
  `GET /api/v1/curriculum/placements/{placement_id}/knowledge-check` and one
  state-changing operation equivalent to
  `POST /api/v1/curriculum/placements/{placement_id}/knowledge-check/submissions`.
  Exact route names become reviewed OpenAPI compatibility commitments.
- GET returns only the WRK-0006 safe presentation and exact public version
  tokens. It never returns the correct option, scoring internals, private
  definition, database/storage values, or prior evidence history.
- POST accepts one opaque submission ID, exact tokens returned by GET, and one
  selected option ID. Assessment remains authoritative for validation,
  scoring, feedback selection, idempotency, and evidence creation.
- All state-changing requests enforce the existing allowed Host/Origin,
  same-origin fetch metadata when present, cookie, permission, correlation,
  and no-store controls. Loopback-development exceptions cannot broaden the
  private-host boundary.
- Exact replay returns the original success response. Conflicting submission
  reuse and a different submission after completion receive distinct bounded
  conflict results; clients cannot infer private correct-answer material from
  denial differences.
- OpenAPI generated from reviewed FastAPI/Pydantic models remains the sole
  browser data authority. Generated client files are never hand-edited, and no
  Node production server or alternative protocol is introduced.

## In Scope

- Thin API models and route handlers for safe knowledge-check presentation and
  deterministic submission through the WRK-0007 facade.
- Bootstrap/composition changes that select concrete Assessment gateways,
  repository, clock/ID sources, and existing Identity policy without placing
  feature policy in the host.
- Permission enforcement, same-origin mutation controls, content/security
  headers, safe no-store behavior, correlation IDs, stable error mappings, and
  sentinel redaction for the new routes.
- Reviewed OpenAPI request/response/error/security shapes and byte-stable
  deterministic regeneration.
- Generated TypeScript client operations/models and contract tests proving the
  browser uses them rather than handwritten duplicates.
- API success, incorrect-result, replay, conflict, already-completed,
  malformed, stale-version, missing/tampered/expired/revoked context,
  client-selected identity/scoring, Host/Origin, database failure, and
  redaction integration evidence against real PostgreSQL.
- Backend/web/identity-security/assurance documentation made stale by the new
  public operations and direct evidence.

## Out of Scope

- Changes to WRK-0006 contract meaning or WRK-0007 scoring/evidence semantics,
  new migrations, UI components/styles, browser flows, static build changes,
  local seeding/composition, outbox delivery, consumers, history, projection,
  retakes, built-in/OIDC delivery, remote/public hosting, managed cloud, or
  recovery tooling.
- Returning private definition bytes, correct option, raw learner evidence,
  SQL/storage identifiers, session values, stack traces, or provider payloads.
- A handwritten API client/model, GraphQL, WebSocket, BFF, SSR, server action,
  React framework server, or Node production process.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API host/models | Existing session and lesson routes | `backend/src/financial_ai_academy/hosts/api/` | Thin presentation/submission transport and safe mappings |
| Composition/security | Current bootstrap and same-origin policy | Named bootstrap/security roots | Select WRK-0007 adapters and enforce existing request boundary |
| API verification | Current PostgreSQL API suite | `backend/tests/integration/api/` and focused Identity tests | Authorized, denial, idempotency, failure, and redaction evidence |
| Public API | OpenAPI governance | `contracts/api/openapi.json` | Reviewed exact HTTP contract |
| Generated client | Existing generator and client | Named web metadata/script/generated/test roots | Deterministic TypeScript consumer seam |
| Documentation | Backend/web/security/assurance sources | Exact documents in `write_scope` | Record direct API/client evidence and residual gaps |

## Contracts and Interfaces

The GET response carries placement ID, package ID/version/digest, assessment
ID/version/definition digest, item ID/version, scoring-policy version, bounded
prompt, and ordered option ID/label pairs. It excludes every private definition
field and learner-evidence record.

The POST request carries `submission_id`, the exact GET version tokens, and
`selected_option_id`. The success response carries opaque attempt/evidence
identifiers, score/max score, correctness, bounded reviewed feedback, exact
provenance, and server occurrence time. It does not return the private
definition or make a mastery/lesson-completion claim.

Use the existing versioned safe error envelope. Map unauthorized/forbidden,
not found, unsupported/stale/malformed, conflicting submission,
already-completed, unavailable/integrity, and unexpected failures explicitly.
Error messages are platform-authored and cannot echo raw learner responses,
correct answers, private feedback, cookies, paths, SQL, event payloads, or
stack traces.

## Dependencies and Parallel Safety

WRK-0007 must complete first because the host consumes its stable public
operations, exact models, migrations, and error taxonomy. This packet owns the
shared API host, OpenAPI snapshot, npm lock, generator, and generated client,
so it has no parallel-safe peer. WRK-0009 begins only after snapshot/client
regeneration is byte-stable, every authorization/error path is fixed, and this
packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe presentation | Valid local session and exact placed assessment | GET runs | Prompt/options and exact public tokens return with no private answer/scoring fields | API/PostgreSQL integration plus schema assertion |
| Correct or incorrect submit | Valid exact request and learner context | POST runs | WRK-0007's deterministic result maps exactly and one evidence set is created | API integration test for both scores |
| Exact replay | Same submission ID and body repeat | POST runs | Original success payload returns and evidence/event counts remain one | API idempotency integration test |
| Conflict or already complete | Same ID changes or a new submission follows completion | POST runs | Stable distinct conflict response appears with no new evidence and no private-answer oracle | API conflict tests |
| Malformed or stale request | Option, ID, version, digest, or policy is invalid/mismatched | POST runs | Bounded client error returns and no evidence exists; `latest` is never substituted | API/schema tests |
| Missing/invalid context | Cookie/session is absent, tampered, expired, or revoked | GET or POST runs | Access fails closed without presentation internals, feedback, or evidence | Identity/API denial tests |
| Client-selected authority | Actor/learner/score/correctness/time/evidence headers or fields are supplied | Request runs | Input is rejected or ignored by exact contract; server values remain authoritative | Security contract test |
| Cross-origin mutation | Host, Origin, fetch metadata, or configured exposure is unsafe | POST runs | Request is denied before application mutation | Same-origin/Host tests |
| Infrastructure failure | Repository/transaction fails | POST runs | Safe unavailable/internal envelope returns with correlation and no sensitive values | Controlled failure/redaction test |
| Generation stability | OpenAPI and client generation run twice | Outputs are compared | Snapshot and generated files are byte-stable with no handwritten model drift | Generation checks |
| Runtime boundary | Client/import graph is scanned | Web contract code is built/typechecked | Only generated client crosses the API seam; no backend/database/Node server code appears | Contract and architecture tests |

## Verification Commands

```powershell
py -m uv sync --project backend --frozen
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/identity backend/tests/integration/api
backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web test -- --run apps/web/tests/contract
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

Use a supported real disposable PostgreSQL server for API integration. Inspect
exact dependency advisories/licenses if the lock changes and report any
external qualification not performed.

## Documentation and Evidence Update

Document the two new operations, exact cookie/permission/same-origin boundary,
safe request/result/error fields, generated-client commands, direct denial and
redaction evidence, and unimplemented UI/runtime/identity/cloud/recovery paths.
Do not promote browser, static runtime, outbox delivery, projection, retake,
built-in/OIDC, remote hosting, or managed-cloud coverage.

## Stop Conditions

- A route/model must duplicate scoring, idempotency, evidence, or feedback
  policy instead of mapping WRK-0007.
- GET or an error reveals the correct option, private definition, raw response,
  prior evidence, session/provider material, SQL/storage values, or stack.
- Browser-supplied identity, time, score, correctness, feedback, or evidence ID
  becomes authoritative.
- Existing same-origin/private-host controls cannot protect the mutation.
- OpenAPI/client generation is nondeterministic, handwritten models are
  required, or a Node production/BFF/server boundary is introduced.
- Work requires built-in/OIDC, tenancy, remote hosting, history/projection,
  recovery, event delivery, or another unresolved decision; canonical sources
  conflict; or active scope overlaps.

## Required Handoff

Report route names, permissions/security behavior, request/response/error
models, answer-secrecy assertions, OpenAPI and generated-client hashes,
generation commands, API/PostgreSQL success/denial/failure results, dependency
review, documentation impact, residual loopback limitations, and the exact
generated interface handed to WRK-0009.

## Planning History

- 2026-08-05: Shaped from SLI-0002 boundary seam 4 after WRK-0007; planning approval and implementation activation remain separate local-only stages.
