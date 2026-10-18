---
id: WRK-0175
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0084
capability: CAP-0020
depends_on: [WRK-0174]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client/schema.d.ts", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/guidance/README.md", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_feature_guidance_registry.py", "backend/src/financial_ai_academy/modules/guidance/application/service.py", "backend/src/financial_ai_academy/modules/guidance/domain/__init__.py", "backend/src/financial_ai_academy/modules/guidance/domain/feature_guidance.py", "backend/src/financial_ai_academy/modules/guidance/ports/__init__.py", "backend/src/financial_ai_academy/modules/guidance/ports/feature_guidance.py", "backend/src/financial_ai_academy/modules/guidance/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_guidance_api.py", "backend/tests/unit/guidance/test_feature_guidance.py", "backend/tests/unit/guidance/test_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0084-understand-feature-limits-and-safe-recovery.md", "docs/planning/work-packets/WRK-0175-compose-feature-guidance-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 518b07b5b4cefb55603454abc9e9f6dd85a790b2
claim_id: WRK-0175:c70026a3-887d-453a-afd8-8c5c06644ed9
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T06:08:28Z
---

# Agent Work Packet: Compose the Feature-Guidance API

## Objective and Deliverable

Compose the completed `feature-guidance/v1` registry into one Guidance-owned,
transport-neutral exact resolution operation and one protected read-only
FastAPI route. Regenerate the reviewed OpenAPI snapshot and shared TypeScript
client so browser, command-line, service, and future headless AI callers use
the same admitted mapping and reviewed guidance record.

The deliverable is an API-first local composition seam. It does not add a
browser explanation, change an owning feature's status or action, execute a
recovery, persist learner data, call a provider or model, or perform live end-
to-end qualification.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate routed architecture-contract,
security-risk, testing-quality, delivery-planning, API, and generated-artifact
context; the change-impact matrix; decision readiness; CAP-0020; SLI-0084;
completed WRK-0174; the current Guidance application/API/client seams;
identity permission behavior; affected consumers and tests; and nearest
Guidance, API, contract, and client READMEs.

The Required Startup was performed and reported before this planning change.
Stop for conflicting canonical authority, stale CAP binding, an unresolved
durable decision, ownership collision, or material slice drift.

## Decisions and Assumptions

- WRK-0174 remains authoritative for exact mapping and record identity,
  validation, source/topic correlation, canonical digests, and atomic registry
  admission.
- Guidance owns only exact resolution of already admitted explanatory meaning.
  The owning feature remains authoritative for its status, authorization,
  availability, state, write uncertainty, retry safety, and offered action.
- The route is
  `GET /api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}`.
  It exposes no `latest` alias, browse operation, arbitrary message, or
  exception-to-guidance inference.
- The operation uses the existing server-issued
  `guidance.platform_help.read` permission because the response is a reviewed
  projection over the same approved Help corpus. No learner identifier,
  permission selector, or caller-written explanation is accepted.
- A transport-neutral resolution preserves the requested exact mapping
  identity and digest together with its exact record. It does not reinterpret
  either document or embed Help topic bodies.
- OpenAPI and TypeScript client outputs are generated artifacts. Generators,
  admitted Python values, and executable contracts remain authoritative.

## In Scope

- Add a minimal feature-guidance registry port and extend the Guidance service
  and public protocol with an exact resolution request and response.
- Preserve the admitted mapping plus record in one immutable resolution so the
  response includes exact surface, condition, mapping version/digest, guidance
  identity/version/digest, safe actions, exact Help references, applicability,
  publication, and source facts.
- Compose the immutable feature-guidance registry from the already admitted
  Help corpus and fail startup atomically on malformed, stale, duplicate, or
  dangling data.
- Add closed Pydantic response models, the protected exact route, strict path
  bounds, bounded not-found/validation errors, no-query behavior, and
  authorization-before-registry-access behavior.
- Regenerate the reviewed OpenAPI snapshot and TypeScript client and prove the
  operation is usable by non-browser callers without backend imports.
- Add focused domain, service, composition, API, generation, permission,
  exact-version absence, malformed-path, flexible-valid-registry,
  confidentiality, and module-boundary tests.
- Reconcile direct Guidance, API, contract, architecture assurance, module,
  planning, and generated-artifact documentation.

## Out of Scope

- Browser components, feature adapters, learner-facing placement, retry or
  reload controls, styling, accessibility, and optional-failure rendering;
  the dependent bounded-explanations packet owns those changes.
- Browser/headless live parity, restart, loopback observation, feature-state
  containment, and final cleanup; the last SLI-0084 packet owns qualification.
- Feature-state inspection, error/exception inference, automatic fallback or
  substitution, health aggregation, diagnostics, incident response, support
  workflow, arbitrary URL/command, automatic remediation, or guarantees.
- Persistence, migration, mutable/user-authored Guidance, remote content,
  provider/model execution, personalization, analytics, grading, eligibility,
  mastery, competency, recommendation authority, financial advice, suitability,
  or external action.
- Identity, tenancy, managed-cloud, queue, recovery, licensing,
  legal/commercial, or public-hosting expansion.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance | completed feature registry, current Help ports/service/public protocol | exact resolution value, port, request, service operation, exports, README | expose one transport-neutral exact read |
| Composition | local bootstrap and admitted Help corpus | compose one feature registry beside contextual Help | fail startup atomically |
| API | Guidance permission, models, routes, error mapping, OpenAPI generator | closed response model and protected exact route | serve headless and browser clients identically |
| Contracts/client | reviewed API snapshot and generation output | OpenAPI snapshot, generated TypeScript schema, API README | preserve one public shape |
| Tests | feature core, service, protected API, generation, architecture | focused success, denial, absence, variation, startup, and boundary tests | prove fail-closed behavior without brittle fixtures |
| Architecture/planning | Help contract, module map, assurance, SLI-0084 | direct implementation/evidence and governed status | keep ownership and evidence synchronized |

No browser feature, owning feature module, persistence, migration, deployment,
provider/model, design-system, or unrelated domain file may change.

## Contracts and Interfaces

The request is exactly `(surface_key, condition_key, mapping_version)` using
the bounded identifiers and semantic-version grammar already enforced by
`feature-guidance/v1`. The result preserves the exact admitted mapping and its
exact record; no version or condition substitution is allowed.

The API route accepts only bounded canonical path values and no query or body.
The closed response contains no learner/session identity, rejected input, raw
exception, HTTP status interpretation, feature state, request payload,
repository path, prompt, provider/model payload, arbitrary URL, command,
credential, or private diagnostic. Errors do not disclose registry contents,
record counts, alternative versions, or rejected keys.

The generated client must reproduce operation ID `getFeatureGuidanceVersion`
and all closed response types from `contracts/api/openapi.json`; consumers may
not add a handwritten backend shape.

## Dependencies and Parallel Safety

WRK-0174 is complete. This packet changes shared Guidance composition, API
host/models, OpenAPI, generated client, architecture, slice, and register
surfaces, so it is not parallel-safe with another writer on those paths. The
bounded feature-explanations packet waits for this exact generated operation.

Claim from a clean recorded base, run packet-start, acquire exact-file leases
immediately before edits, keep one owner through verification, and store local
authority/disposition records only in ignored local state.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact resolution | A permitted session names an admitted surface, condition, and mapping version | The route is called | The exact mapping and reviewed record return with stable digests and no reinterpretation | domain/service/API |
| No substitution | A known surface/condition names an absent mapping version | Resolution runs | A bounded not-found result returns; no other mapping or record is substituted | service/API |
| Protected read | A session is missing or lacks Help read permission | The route is called | 401/403 occurs before registry access or guidance facts are exposed | API/security |
| Invalid identity | A path value violates bounded identifier/version grammar | The route is called | A bounded validation response returns without echoing unsafe input | API/security |
| Atomic composition | A record, mapping, source, digest, or topic binding is invalid | Local composition starts | Startup fails before a partial Guidance operation becomes available | composition/unit |
| Mapping-record correlation | A valid mapping targets one admitted record | Resolution runs | Mapping identity/digest and record identity/digest remain exact and correlated | domain/API |
| Flexible valid registry | Safe record/action/reference counts, ordering, wording, and additional valid mappings vary | Service/API reads run | Contract invariants hold without fixed starter counts or prose | unit/anti-rigidity |
| Headless contract | OpenAPI and generated client regenerate | Artifacts are inspected | Browser and non-browser callers share one protected operation and closed shape | OpenAPI/client |
| No new authority | Imports, response fields, and calls are inspected | Architecture/security checks run | No feature-policy, persistence, provider/model, learner-policy, or financial seam enters Guidance | architecture/security |

## Verification Commands

Run focused Guidance domain/service and protected API tests plus module-boundary
tests with the prepared Python environment. Regenerate and verify the reviewed
OpenAPI snapshot and TypeScript client using the pinned repository workflows;
run generated-client contract tests, Python compilation, TypeScript checking,
zero-warning lint, architecture, security, documentation, planning,
learner-language, whitespace, controller-selected exact-candidate verification,
independent technical review, and `python dev-tools/agent/check_ready.py`.

Record only passing evidence. Fix bounded whitespace, generated formatting,
optional wording, or another inconsequential correction in scope without a new
approval or unrelated full-review loop.

## Documentation and Evidence Update

Document the feature-guidance resolution port and application/public operation,
startup composition, shared permission, route and bounded error semantics,
closed Pydantic/OpenAPI/client shape, mapping-record correlation, headless
availability, confidentiality, generated-artifact commands, assumptions, and
remaining browser/live work. Update packet, slice, and register together and
keep all local authority/disposition metadata out of tracked files.

## Stop Conditions

Stop for ambiguous owning-feature status, retry/idempotency, exact-version, or
provider/model meaning; required change to an owning feature contract; runtime
state or exception inference; mutable/remote/arbitrary content; browser-only
mapping; model/provider execution; arbitrary destinations or commands;
automatic remediation; persistence/migration; breaking v1 compatibility; new
permission, identity, tenancy, managed-cloud, queue, recovery, licensing,
legal/commercial, or external-publication behavior; stale CAP authority;
ownership collision; or material CAP-0020/SLI-0084 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
generated ordering, fixture count, nonfunctional styling, or another
inconsequential issue. Fix it in bounded scope or route optional polish to
CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0084.WRK-0175`; exact candidate and receipt; domain, port,
service, composition, API, OpenAPI, and generated-client seams; mapping-record
correlation; permission and failure mapping; browser/headless contract parity;
confidentiality and anti-rigidity evidence; focused and repository checks;
changed files; documentation impact; assumptions; and remaining feature-
explanation and live-qualification gaps. Confirm no persistence, browser
feature, provider/model, external content/action, learner authority, owning-
feature behavior, or financial behavior changed.

## Verification Evidence

- Guidance now resolves one exact admitted mapping and reviewed record through
  a transport-neutral request, port, service operation, and immutable
  resolution value. Local composition admits the feature registry against the
  same complete Help corpus as the contextual registry.
- The protected exact route uses the existing Help-read permission, validates
  authorization before registry access, accepts no query or body, returns a
  closed mapping-and-record response, and preserves bounded not-found behavior
  without version or condition substitution.
- The reviewed OpenAPI snapshot and generated TypeScript client reproduce the
  `getFeatureGuidanceVersion` operation. Browser and ordinary headless clients
  therefore share one public shape without importing backend internals.
- The focused Guidance, API, and module-boundary suite passes 94 tests; Web and
  generated-client qualification passes 499 tests. OpenAPI reproduction,
  TypeScript checking, zero-warning lint, Python compilation, architecture,
  security, documentation, planning, whitespace, and all 29 aggregate
  readiness checks pass.
- Varied-valid-registry evidence derives counts from the admitted baseline,
  changes wording and ordered action/reference shapes, adds a mapping, and
  preserves schema validity, exact digests, mapping-record correlation, and
  ordering through the real service and protected API projection.
- No owning-feature behavior, browser explanation, persistence, migration,
  provider/model call, arbitrary command or destination, recovery execution,
  external action, learner authority, or financial behavior changed.
- Exact candidate `1a722abcefe9f8efc02604feb9120e3f4f463fc9` has a qualifying
  receipt at `.local-codex/control-plane/receipts/WRK-0175/1a722abcefe9f8efc02604feb9120e3f4f463fc9/20261018T062306Z-a1c5233c-76bf-40ca-afbc-5c0805735690.json`.
  Its 12 selected checks cover focused feature Guidance, architecture,
  security, reviewed contracts/client, the full Web unit/build gates, and all
  29 aggregate readiness checks.

## Planning History

- 2026-10-18: Authored just in time after WRK-0174 completed. This packet
  composes its exact source-bound registry into one protected API-first
  resolution shared by browser and future headless callers while deferring
  feature placement and live qualification to dependent packets. It remains
  inside the approved CAP-0020 package and requires no lower-level approval.
- 2026-10-18: Activated from clean base `518b07b` after confirming the current
  CAP binding, completed WRK-0174 dependency, API-first exact-resolution scope,
  executable checks, and no unresolved decision or ownership collision.
- 2026-10-18: Entered verification after implementing the exact mapping-and-
  record resolution, protected API, reviewed OpenAPI, generated client, and
  focused failure/anti-rigidity evidence within the bounded packet scope.
- 2026-10-18: Corrected one bounded anti-rigidity evidence gap so valid added
  mappings and varied record shapes pass through the real service and API
  without fixed starter counts or prose.
- 2026-10-18: Completed on corrected exact candidate `1a722ab` after all 12
  affected checks produced a qualifying receipt. The API-first resolution is
  ready for the dependent feature-explanation packet.
