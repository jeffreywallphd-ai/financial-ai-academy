---
id: WRK-0126
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: ["WRK-0125"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_project_submission_api.py", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/project-submission-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0126-expose-project-submission-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: d3646497667e578811034a6bfc1f958980e0156c
claim_id: WRK-0126:1e546432-cd39-4733-a752-c800408d0037
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T03:49:42Z
---

# Agent Work Packet: Expose the Project Submission API

## Objective and Deliverable

Compose the completed WRK-0125 project-submission core in the local application
and expose its candidate, submit/validation, exact-evidence, and ordered-history
operations as one protected, reviewed HTTP boundary. Regenerate the committed
OpenAPI snapshot and TypeScript client so browser and authenticated headless
clients consume the same server-owned behavior. This packet stops before
Learner-model/Audit consumption and before any browser feature is added.

## Required Context

Follow the repository-root `AGENTS.md` and `docs/README.md` startup and route through the baseline,
architecture-contracts, learning-adaptation, testing-quality, and delivery-
planning packs. Read CAP-0007, SLI-0032, WRK-0124, WRK-0125, ADR-0005,
ADR-0011, ADR-0012, the Assessment and Project submission contracts, executable
Assessment Project schemas, application composition, API host/models,
OpenAPI/client generators, nearest READMEs, analogous practice routes, affected
tests, change-impact guidance, decision readiness, and concurrent-work rules.

## Decisions and Assumptions

- The API is a thin transport over Assessment public operations. It does not
  duplicate candidate assembly, validation, replay, persistence, or history
  policy.
- Learner identity and permission come only from the opaque server session.
  Candidate/evidence/history reads require the existing `project.read` grant;
  submission requires the existing `project.write` grant. No new permission or
  identity model is invented.
- Routes bind one exact Project and snapshot. A request body cannot override
  route selectors, learner identity, evidence metadata, occurrence,
  supersession, or time.
- Exact evidence may return the current session learner identifier, consistent
  with the existing protected Project shell/snapshot boundary. Safe ordered
  history continues to omit learner identity and artifact bytes.
- The existing v1 Project-submission schemas remain canonical. HTTP models are
  closed projections of those shapes and cannot add provider, execution,
  grading, mastery, or advice meaning.

## In Scope

- Add the Assessment Project schema-directory setting and compose
  `ContractProjectSubmissionAdapter`, `PublicProjectSubmissionSource`, the
  Project service, Assessment repository, and Assessment service in dependency
  order at the application root.
- Add closed API request/response models and deterministic domain-to-transport
  projectors for candidate, submission, validation outcome, accepted evidence,
  and ordered safe history.
- Expose protected operations under one Project resource hierarchy: exact
  snapshot candidate read, exact snapshot submission, Project submission
  collection/history read, and exact submission evidence read.
- Reject query authority, route/body source mismatch, missing session,
  insufficient permission, cross-learner guesses, malformed closed documents,
  conflicts, limits, and unavailable sources through bounded existing error
  envelopes.
- Regenerate and verify reviewed OpenAPI and generated TypeScript types, and
  prove representative client usage for all four operations.
- Add real-composition PostgreSQL API tests for accepted/refused submission,
  replay, exact/history reads, cross-source denial, permission and privacy,
  malformed input, and headless OpenAPI parity.
- Update host/API/architecture guidance and planning evidence.

## Out of Scope

Learner-model projection; Audit consumption; browser pages/components; worker
dispatch; Project/Assessment schema or migration changes; qualitative,
instructor, peer, or AI grading; mastery/competency; live Portfolio behavior;
artifact execution or active rendering; provider calls; organization tenancy;
managed-cloud behavior; new dependencies or lockfiles; remote push or deploy.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Composition/settings | additive project-submission contract/source wiring | Make the completed transport-neutral core reachable in the real host |
| API models/host | four protected operations and closed projectors | Supply one browser/headless boundary without policy duplication |
| OpenAPI/client | regenerate reviewed artifacts and client-usage proof | Keep generated consumers exact and reproducible |
| API verification | new focused real-composition test | Prove authorization, persistence, replay, privacy, and denial behavior |
| Guidance/planning | listed host, API, architecture, slice, packet, and register files | Record the delivered boundary and remaining consumer/UI work |

No executable Assessment Project schema, compatibility fixture, migration,
repository, domain policy, Project persistence, UI feature, dependency, or
lockfile may change.

## Contracts and Interfaces

The HTTP boundary exposes:

- `GET /api/v1/projects/{project_id}/snapshots/{snapshot_id}/submission-candidate`;
- `POST /api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions`;
- `GET /api/v1/projects/{project_id}/submissions`;
- `GET /api/v1/projects/{project_id}/submissions/{submission_id}`.

The candidate is a closed learner-safe projection of exact Project, origin,
milestone, policy, and snapshot-resource facts. The POST body is the canonical
v1 submission intent and returns a validation result plus nullable accepted
evidence; a deterministic refusal is a successful bounded response with no
write. Exact evidence is learner-bound and immutable. History is occurrence-
ordered and learner-safe. Every operation accepts only bounded path/body facts,
never a learner or permission selector.

## Dependencies and Parallel Safety

WRK-0125 is complete and supplies the public operations, source adapter,
contract adapter, immutable PostgreSQL evidence, exact replay, and bounded
history. This packet owns shared composition, host, OpenAPI, generated-client,
SLI, and register files, so it is not parallel-safe with the dependent
projection/Audit, browser, or qualification packets.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Exact candidate | authorized learning Project/snapshot returns exact safe facts only | API/PostgreSQL |
| Refused mapping | missing, unknown, duplicate, or stale evidence returns ordered issues and no retained evidence | API/PostgreSQL |
| Accepted and replay | valid input returns immutable evidence; exact replay returns original metadata | API/PostgreSQL |
| Exact/history reads | accepted evidence reopens exactly and history remains ordered, safe, and complete | API/PostgreSQL |
| Route/body mismatch | a body cannot select another Project or snapshot | API security |
| Identity/permission | no session, read-only submit, caller-selected learner/query, and cross-learner guesses fail boundedly | API security |
| Source denial | independent Project or stale/unavailable exact source fails without fallback or partial evidence | API integration |
| Shape flexibility | varied milestone/resource counts, resource kinds/order, Unicode labels, and optional exact-version forms remain valid | API anti-rigidity |
| Generated parity | reviewed OpenAPI reproduces byte-for-byte and TypeScript compiles representative calls to all four operations | OpenAPI/client |
| No execution/advice | payloads contain no bytes, path, active rendering, provider, grading, mastery, suitability, or advice authority | architecture/security |

## Verification Commands

Run the focused API test with the isolated PostgreSQL DSN, then:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/api/test_single_profile_project_submission_api.py backend/tests/integration/api/test_single_profile_project_api.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment/test_project_submission_service.py backend/tests/contract/assessment_project
backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web run generate:api -- test
npm --prefix apps/web run typecheck
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0126-expose-project-submission-api.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Generate the OpenAPI snapshot before `--check` and regenerate the TypeScript
client from that reviewed snapshot. Submit one exact affected candidate,
produce a fresh verification receipt, and obtain one independent technical
review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document route shapes, session-owned identity and permission, side-effect-free
validation refusal, replay and history meaning, safe response fields,
composition order, reviewed generated artifacts, headless parity, tests,
candidate/receipt, review disposition, assumptions, and remaining JIT-C/JIT-D/
JIT-E work. Keep approval and reviewer records only in ignored local storage.

## Stop Conditions

Stop for a breaking WRK-0124/WRK-0125 contract, a new permission/identity
model, cross-module persistence access, mutable accepted evidence, client-
selected authority, private data or bytes in safe output, qualitative/AI/
mastery authority, execution/provider/tenancy/commercial expansion, a new
dependency, active scope collision, conflicting canonical source, or material
CAP-0007/SLI-0032 drift.

Do not stop or reopen review for harmless whitespace, optional prose, generated
ordering with unchanged meaning, or nonfunctional styling. Correct such items
locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0126`; exact candidate and receipt; composed
public seams; route and permission contracts; refusal, replay, exact/history,
privacy, cross-source, anti-rigidity, and generated-client evidence; focused,
architecture, security, planning, documentation, aggregate, and independent-
review results; documentation impact; assumptions; and residual gaps. Confirm
that Project/Assessment schema meaning, browser behavior, Learner-model/Audit,
dependencies, AI authority, and external execution did not change, then leave
JIT-C ready for just-in-time refinement.

## Planning History

- 2026-10-17: Authored and validated the just-in-time API/client packet after
  WRK-0125 completed. The boundary remains inside the approved CAP-0007 and
  SLI-0032 package and introduces no new decision gate.
- 2026-10-17: Claimed the packet from base `d364649` after the implementation
  gate passed for the current approved CAP package.
- 2026-10-17: Expanded the test-only scope to keep the bootstrap settings
  directory-resolution fixture synchronized with the new required Assessment
  Project schema directory. No runtime or approval boundary changed.
