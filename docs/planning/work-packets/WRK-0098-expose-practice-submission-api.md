---
id: WRK-0098
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0027
capability: CAP-0006
depends_on: ["WRK-0097"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/scripts/generate-api-client.mjs", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "backend/README.md", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_assessment_api.py", "backend/tests/integration/api/test_single_profile_practice_submission_api.py", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/assessment-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0027-submit-and-score-practice-attempt.md", "docs/planning/work-packets/WRK-0098-expose-practice-submission-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 34ef4a92d196d3270d4009cd26efa2c335a07f34
claim_id: WRK-0098:989c719d-adfa-420e-9721-70e66fe58719
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T16:08:14Z
---

# Agent Work Packet: Expose the Practice Submission API

## Objective and Deliverable

Expose the completed WRK-0097 practice-submission application operation through
one protected, versioned public POST; reproduce the reviewed OpenAPI snapshot
and generated TypeScript client; and prove that a direct non-browser consumer
can submit and receive the same learner-safe result later used by the browser.
The public API remains the primary product boundary. This packet does not build
browser behavior or plan a distinct AI mode, agent protocol, or autonomous
authority.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository-
root `docs/README.md`; route through the baseline, architecture-contract,
security-risk, testing-quality, and delivery-planning context. Read the change-
impact matrix, decision readiness, CAP-0006, SLI-0027, WRK-0096, WRK-0097,
ADR-0005, ADR-0007, ADR-0009, the Assessment and REST contract guidance, API
host and bootstrap READMEs, accepted practice submission/result schemas,
current protected knowledge-check submission route, OpenAPI/client generators,
API tests, web contract tests, and concurrent-work rules.

## Decisions and Assumptions

- The FastAPI host is a thin adapter over `AssessmentOperations`; it does not
  score, read Assessment persistence, or reinterpret the accepted contracts.
- Cookie-backed learner context and same-origin request policy remain the
  current protected local profile. The caller cannot select learner identity,
  server IDs, time, score, completion, or feedback.
- The route-bound placement ID must equal the closed request body's placement
  ID. The complete JSON document is passed to the WRK-0097 operation as bytes
  after transport validation; accepted canonical meaning remains Assessment's
  authority.
- The response exposes the accepted learner-safe result and technical
  provenance needed by clients, but omits learner identity and the internal
  request fingerprint. It never exposes answer keys or private evaluator data.
- The reviewed OpenAPI snapshot is the sole source for the generated
  TypeScript client. Browser code will consume that client in WRK-0099; it may
  not import backend internals or hand-author a competing transport type.
- Direct HTTP use by a non-browser program is a supported API use case. A
  future headless AI client may reuse it, but no AI-specific mode, endpoint,
  credentials, tools, or action policy are introduced here.

## In Scope

- Add closed Pydantic request and discriminated learner-safe response models
  corresponding to the accepted three practice response types and result
  outcomes.
- Add one protected POST at
  `/api/v1/curriculum/placements/{placement_id}/practice/submissions` with a
  stable operation ID and existing bounded error envelope/status mapping.
- Serialize the validated transport body deterministically and invoke only
  `AssessmentOperations.submit_placed_practice` with server-resolved learner
  context and route placement.
- Compose the production submission adapter so the live API uses the accepted
  schemas and deterministic scorer from WRK-0096/WRK-0097.
- Regenerate and verify the reviewed OpenAPI snapshot and TypeScript client.
- Test success for all supported response shapes, direct/headless use, exact
  replay, route/body mismatch, caller-selected identity, missing session,
  malformed/extra input, bounded Assessment denials, unconfigured service,
  learner/private-answer confidentiality, and response validation.
- Update boundary and verification documentation plus planning evidence.

## Out of Scope

Browser form state, rendering, submission, result or focus behavior; styling;
retry/resume/history/review navigation; new Assessment schemas, scoring,
persistence, migrations, or event meaning; Learner-model/Audit consumers;
command-line product UX; API tokens, remote/cloud identity, tenancy, managed-
cloud recovery, external execution, model/manual grading, mastery/adaptation,
AI planning, AI-specific protocol or tool calling; dependencies and lockfiles.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API transport | protected knowledge-check POST, practice GET, error mapping | closed practice request/result models and one POST adapter | Publish the existing application operation without moving authority into HTTP |
| Production composition | Assessment parser/scorer wiring | add accepted submission adapter injection | Make the public endpoint functional in local and future cloud compositions |
| Public contract | OpenAPI generator and snapshot | additive operation and schemas | Keep the API reviewable and client-language neutral |
| Generated client | deterministic generator and contract tests | reproduced TypeScript types/client exports | Give browser and other TypeScript callers the reviewed public seam |
| Tests | Assessment/practice API and generated-client suites | direct API/headless success, denial, confidentiality, and anti-rigidity coverage | Prove API availability independently of UI |
| Documentation/planning | Assessment/API/web boundary guidance, SLI/register | listed files | Record API-first scope and evidence |

No accepted practice JSON schema, domain/application scoring, persistence,
migration, existing route meaning, browser feature file, dependency, or
lockfile may change.

## Contracts and Interfaces

The request model is the closed `assessment-practice-submission-v1` document:
versioned exact placement/package/definition/practice/policy selectors, one
client-stable submission UUID, and one discriminated response per item. It has
no learner, server ID, timestamp, score, feedback, or evaluator field. Extra
properties fail at the transport boundary.

The route authenticates through the existing learner-context dependency,
rejects route/body placement mismatch as a stale reference, encodes the
validated body to JSON bytes, and calls `SubmitPlacedPracticeRequest` with the
server learner UUID. Assessment remains authoritative for exact-schema parsing,
canonical request identity, scoring, replay, conflict, attempt limits, and
persistence.

The response is one closed, ordered result envelope containing server attempt
and evidence UUIDs, the client submission UUID, exact public provenance,
score/max/outcome, review references, submitted response value, applicable
feedback, and UTC timestamp. It excludes `learner_id`, `request_fingerprint`,
correct-answer values, private evaluator declarations, database detail, and
provider payloads.

## Dependencies and Parallel Safety

WRK-0097 is complete and supplies the transport-neutral operation, accepted
result, atomic evidence, replay, conflict, and completion-limit behavior.
WRK-0098 owns shared API models/routes, bootstrap composition, the reviewed
OpenAPI snapshot, generated client, and SLI/register files. It is not parallel-
safe with the later browser or slice-qualification packet and must complete
before WRK-0099 is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Direct API submission | An authenticated non-browser caller sends a valid complete three-type document | It POSTs to the public route | The caller receives the persisted learner-safe result without any browser dependency | API integration |
| Browser-ready client | The reviewed snapshot contains the operation | Generation runs | The checked-in TypeScript client exposes the exact request/result and route parameter | generation/contract/typecheck |
| Server authority | A caller omits or attempts to add learner/server/scoring fields | Transport resolution runs | Omitted server fields are supplied internally; extra caller fields fail before Assessment | API security |
| Route correlation | The body placement differs from the route | The request is handled | A bounded stale-reference denial occurs and no submission call runs | API integration |
| Replay and denials | Assessment returns replay, conflict, already-completed, unavailable, or invalid/stale errors | The route maps the result | Stable public status/error envelopes are returned without private diagnostics | API integration |
| Closed varied shapes | Valid documents vary item count/order and supported response variants within accepted bounds | Models and generated types process them | No fixture-specific item count or incidental ordering is imposed by the host/client | parameterized API/contract |
| Confidentiality | Service output contains learner identity/internal fingerprint and private state exists behind Assessment | The route returns success or failure | Neither learner identity, fingerprint, answer keys, evaluator declarations, nor diagnostics appear | API security |
| Existing behavior | Current practice-open and knowledge-check routes run | The new operation is installed | Existing contracts and status behavior remain unchanged | regression |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/api/test_single_profile_practice_submission_api.py backend/tests/integration/api/test_single_profile_practice_api.py backend/tests/integration/api/test_single_profile_assessment_api.py
backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check
node apps/web/scripts/generate-api-client.mjs --check
npm --prefix apps/web run test
npm --prefix apps/web run typecheck
python dev-tools/architecture/check_architecture.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0098-expose-practice-submission-api.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Submit one exact candidate, generate a fresh affected-verification receipt, and
obtain one independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document the protected POST, response confidentiality, server-owned identity,
thin-host/application boundary, production adapter composition, reviewed
OpenAPI/generated-client flow, direct non-browser availability, and deferred
browser/AI-specific work. Record exact checks, candidate/receipt, review
disposition, assumptions, and residual gaps in this packet and SLI-0027. Keep
approval and reviewer records only in the ignored local ledger.

## Stop Conditions

Stop for a breaking accepted schema or existing endpoint; ambiguity in public
response confidentiality or error meaning; caller-selected identity/time/
scoring authority; private answer or evaluator leakage; transport-owned domain
policy; browser-only or AI-specific API divergence; remote identity, tenancy,
managed-cloud recovery, external execution, model/manual grading, new provider
or dependency; active scope collision; conflicting canonical source; or
material CAP-0006/SLI-0027 drift.

Do not stop or reopen review solely for harmless whitespace, generated-file
ordering with unchanged meaning, nonfunctional styling, optional copy polish,
or another inconsequential in-scope correction. Fix it locally or defer
optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; route and operation ID; request/result boundary;
server-owned fields; production composition; direct/headless, replay, denial,
confidentiality, anti-rigidity, regression, OpenAPI/client reproduction,
typecheck, architecture, aggregate, receipt, and review results; documentation
impact; assumptions; and residual gaps. Confirm that browser behavior,
accepted schema/domain/persistence meaning, dependencies, separate AI-mode
planning, autonomous authority, and external execution did not change, then
leave WRK-0099 dependency-ready.

## Implementation Evidence

- Added protected `submitPlacedPractice` at
  `/api/v1/curriculum/placements/{placement_id}/practice/submissions` as a thin
  adapter over the WRK-0097 public operation. The host supplies the learner
  from the opaque session, rejects route/body mismatch and query authority,
  serializes the closed validated document, and owns no scoring, replay, or
  persistence policy.
- Added closed discriminated request/result API models for single-select,
  multiple-select, and canonical fixed-decimal responses. The response retains
  submitted values, ordered outcomes, applicable reviewed feedback, review
  references, exact public provenance, evidence IDs, and UTC time while
  deliberately omitting learner identity, the internal request fingerprint,
  answer keys, private evaluators, and diagnostics.
- Production composition now supplies the accepted
  `ContractPracticeSubmissionAdapter`. The reviewed OpenAPI snapshot and
  deterministic TypeScript client expose the exact operation for direct,
  browser, command-line, service, and future headless consumers; no second
  protocol or browser-only contract exists.
- Sixteen new direct API tests cover success, all three response shapes,
  server-owned identity, confidentiality, exact operation shape, route/body
  mismatch, query and extra-field denial, duplicate selection, every bounded
  Assessment error class, unconfigured service, invalid service output, and
  varied valid item counts. The focused practice/knowledge-check group passes
  27 tests; the complete backend API integration directory passes 79 with six
  environment-gated PostgreSQL tests skipped; Assessment unit/practice-
  contract regression passes 115.
- Generated-client tests plus the full web suite pass 181 tests. OpenAPI and
  client reproduction, TypeScript typecheck, web lint, all 15 architecture
  fitness tests, packet/planning/documentation validation, and whitespace
  integrity pass. Browser submission/rendering and live PostgreSQL HTTP
  qualification remain intentionally deferred to the dependent packets.

## Planning History

- 2026-10-16: Authored just in time after WRK-0097 completed. The packet
  deliberately proves the public API and generated-client boundary before
  browser integration so browser and future headless clients share one stable
  interface without creating a separate AI mode.
- 2026-10-16: Claimed from base revision `34ef4a9` after the implementation
  gate confirmed current CAP authority, completed dependencies, decision
  readiness, exact generated-artifact scope, and no active ownership collision.
- 2026-10-16: Implemented and focused-qualified the protected public POST,
  reviewed OpenAPI, generated TypeScript client, production adapter
  composition, and direct non-browser result contract. The API remains the
  primary boundary; browser use is dependency-ready and separate AI-mode
  planning remains out of scope.
