---
id: WRK-0154
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0075
capability: CAP-0018
depends_on: [WRK-0153]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "backend/migrations/learner_model/learner_model_0005_presentation_preferences.down.sql", "backend/migrations/learner_model/learner_model_0005_presentation_preferences.up.sql", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/learner_model/adapters/system.py", "backend/src/financial_ai_academy/modules/learner_model/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/ports/repositories.py", "backend/src/financial_ai_academy/modules/learner_model/ports/system.py", "backend/src/financial_ai_academy/modules/learner_model/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_learner_preferences_api.py", "backend/tests/integration/api/test_single_profile_presentation_preferences_api.py", "backend/tests/integration/learner_model/test_postgres_completion_projection.py", "backend/tests/integration/learner_model/test_postgres_preferences.py", "backend/tests/integration/learner_model/test_postgres_presentation_preferences.py", "backend/tests/integration/learner_model/test_postgres_project_completion.py", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/unit/learner_model/test_presentation_preference_service.py", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api/README.md", "contracts/api/openapi.json", "deployments/local/serve.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/learner-presentation-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0075-set-accessible-display-preferences.md", "docs/planning/work-packets/WRK-0154-compose-presentation-preference-persistence-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 0eef6f8e65675ae9d564b7de01241e0a832d164b
claim_id: WRK-0154:3f0d58a2-6a21-4ecb-9088-1704ff8f2681
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T21:25:15Z
---

# Agent Work Packet: Compose Presentation Preference Persistence and Public API

## Objective and Deliverable

Compose the completed learner-presentation-preferences v1 contract and pure
core into Learner-model application operations, additive module-owned
PostgreSQL storage, and a protected public JSON API. The same reviewed OpenAPI
contract and generated TypeScript client must serve browser, command-line,
service, and future headless-AI callers under identical identity, permission,
validation, replay, concurrency, and privacy rules.

Deliver side-effect-free default reads; complete replacement and reset;
bounded history; portable export; exact retry; stale-write and changed-key
denial; learner isolation; restart durability; and closed public errors. Do not
add browser feature UI, runtime presentation attributes/tokens, theme storage,
adaptive policy, inference, evidence, recommendation, provider, or external
action.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md` and
perform their Required Startup. Revalidate CAP-0018, SLI-0075, WRK-0153,
ADR-0005, ADR-0006, the learner-presentation-preference, learner-preference,
identity, API, migration, and application/repository contracts, module map,
privacy guidance, generated-client conventions, testing standards, nearest
READMEs, and concurrent-work protocol. Inspect affected contracts,
implementations, consumers, migrations, and tests.

No unresolved identity, tenancy, data-license, provider, model-authority,
encryption, recovery, legal, commercial, or external-execution decision is
needed. Stop if implementation would change one of those durable choices.

## Decisions and Assumptions

- Learner model owns the profile, replay records, and bounded change summaries
  in its existing schema. No cross-module foreign key or repository read is
  introduced.
- Existing single-profile identity gains narrow
  `learner_presentation_preferences.read` and
  `learner_presentation_preferences.write` permissions. The server session is
  the only learner selector; request bodies and query strings cannot choose it.
- Public routes are `GET /api/v1/learner-presentation-preferences`, `POST
  /api/v1/learner-presentation-preferences/mutations`, `GET
  /api/v1/learner-presentation-preferences/history`, and `GET
  /api/v1/learner-presentation-preferences/export`.
- An absent row projects a deterministic revision-one safe default profile
  without writing. A deterministic profile ID binds to the server learner; the
  first accepted replacement persists revision two atomically.
- The server clock supplies canonical time. This family has no entry identity
  generator because it contains one learner-bound complete value.
- PostgreSQL serializes each learner with a transaction-scoped advisory lock,
  checks exact replay before revision, writes profile/replay/change together,
  and retains at most 100 newest summaries.
- Exact idempotency-key reuse returns the accepted profile. Changed reuse and
  stale expected revision fail without a profile, replay, or history write.
- The API uses the frozen profile, intent, history, export, and bounded error
  meaning exactly. OpenAPI is the source for generated TypeScript types and
  operations; no browser-only or agent-only path is introduced.
- Browser-local `system|light|dark` theme remains outside the API. Headless
  clients receive only learner-owned presentation choices and their limits.

## In Scope

- Add framework-free public requests and service operations for open, mutate,
  history, and export with safe contract-to-public error mapping.
- Add repository/system ports, deterministic default-profile seed, contract
  revalidation, and application fingerprinting.
- Add forward, reapply, and retained-data development-down migration for
  current profiles, accepted mutation replays, and bounded summaries.
- Add PostgreSQL reads and one atomic optimistic/idempotent save; prove
  isolation, retry, conflict, atomicity, history truncation, and reconstruction.
- Add four protected API routes and two module-specific permissions; reject
  missing/wrong permission, caller-selected learner identity, unknown fields,
  arbitrary style/theme values, malformed input, stale revision, and changed
  key reuse.
- Regenerate and review OpenAPI and generated TypeScript files; prove direct
  generated-client availability for browser and ordinary headless consumers.
- Wire application composition, local serving, migration settings,
  module-boundary checks, and focused unit/integration tests.
- Synchronize API, module, architecture, slice, packet, and register docs.

## Out of Scope

Browser pages or controls; preview; semantic root attributes; design tokens;
browser-local theme storage; AI-assistance or notification preferences;
arbitrary CSS/fonts/scales; inferred needs or medical traits; Assessment
evidence; competency/mastery; Adaptation policy; providers or models;
collaboration/organizations/tenancy; external notifications; managed-cloud
recovery; account erasure/import; separate agent authority; financial advice or
action; dependency changes; or styling-only work.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Learner-model core | Public/application/repository/system seams | One shared framework-free core; no other-module state |
| Persistence | Additive `learner_model_0005` tables and focused adapter | Atomic replay/revision/history; no destructive or cross-schema behavior |
| Identity/API | Two scoped permissions and four protected routes | Server-owned learner/time; closed inputs and safe errors |
| OpenAPI/client | Reproduced snapshot and generated files | Browser/headless parity; no handwritten divergence |
| Composition | Settings, service assembly, and local host wiring | Local/cloud semantics remain portable |
| Tests/docs | Focused unit, PostgreSQL, API, architecture, and contract evidence | Privacy, theme exclusion, isolation, anti-rigidity, and exact cleanup |

No path outside `write_scope` may change. Stop if another migration family,
module repository, UI source, design-system runtime, provider, dependency,
deployment policy, or unlisted shared boundary becomes necessary.

## Contracts and Interfaces

Expose transport-neutral operations equivalent to:

```text
open_presentation_preferences(learner_id) -> PresentationPreferenceProfile
mutate_presentation_preferences(learner_id, PresentationPreferenceMutationIntent) -> PresentationPreferenceProfile
read_presentation_preference_history(learner_id) -> PresentationPreferenceHistory
export_presentation_preferences(learner_id) -> PresentationPreferenceExport
```

The API request uses the frozen complete replacement/reset intent. Responses
use the frozen v1 profile, history, and export fields exactly. Export purpose
and limitations use stable plain language and contain no storage, session,
permission, replay, provider, inference, evidence, score, policy, medical, CSS,
or browser-local theme fields.

Public failures distinguish invalid request, immutable conflict, stale
revision, integrity failure, and temporary unavailability. Messages are safe
and actionable; they never echo private data, database detail, credentials, or
provider payloads.

## Dependencies and Parallel Safety

WRK-0153 is complete and fixes all consumed contract/domain semantics.
WRK-0154 owns shared Learner-model, Identity, host API, OpenAPI, generated-
client, composition, migration, test, documentation, slice, and register paths.
It is not parallel-safe with another SLI-0075 packet and must complete before
the browser/runtime-presentation packet is reserved or authored.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Default open | Authorized read returns deterministic revision-one safe choices and performs no database write | unit/PostgreSQL/API |
| Replace and reopen | Every valid complete choice combination reopens with exact revision, times, and digest | unit/PostgreSQL/API |
| Retry/conflict | Exact retry returns accepted result; changed-key and stale revision write nothing | unit/PostgreSQL/API |
| History bound | More than 100 accepted changes retain the newest 100 valid summaries and current revision | PostgreSQL/anti-rigidity |
| Reset/export | Reset creates a new safe-default revision; history/export remain correlated and omit prior choices | contract/PostgreSQL/API |
| Authorization/isolation | Missing or wrong permission, caller identity, theme, arbitrary CSS, and cross-learner access fail closed | API/security/PostgreSQL |
| Atomic interruption | Simulated failure rolls back profile, replay, and summary together | PostgreSQL |
| Restart reconstruction | Accepted state and replay remain exact after ordinary service reconstruction | PostgreSQL/API |
| Headless parity | A non-browser generated-client consumer can read and mutate through reviewed public operations | OpenAPI/client contract |
| No policy leakage | No diagnosis, inference, evidence, mastery, eligibility, recommendation, provider, financial, theme, or external-action state is created | architecture/security |
| Anti-rigidity | All valid combinations, varied revisions, IDs, times, history lengths, and technical metadata share invariant behavior | parameterized tests |

## Verification Commands

Run focused presentation-preference contract, service, real-PostgreSQL,
protected API, identity, composition, and module-boundary tests; migration
forward/reapply/development-down/rollback/reconstruction/cleanup evidence;
OpenAPI currency and generated-client reproduction/usage checks; security,
architecture, planning, documentation, Python compilation, web typecheck and
zero-warning lint where affected, whitespace, exact-candidate affected
verification, and `python dev-tools/agent/check_ready.py`.

## Documentation and Evidence Update

Document exact routes, permissions, public shapes/errors, learner/time
authority, side-effect-free default reads, replay/concurrency/history behavior,
reset/export privacy, migration and reconstruction evidence, theme exclusion,
OpenAPI/headless parity, checks, assumptions, and remaining runtime/UI/live
qualification gaps. Keep approval and technical-review records and receipts
only in ignored local control-plane storage.

## Stop Conditions

Stop for inferred or medical profiling; preferences used as evidence, mastery,
eligibility, permission, recommendation, suitability, or irreversible action;
theme entering learner-owned API state; runtime design changes; arbitrary style
input; new identity model or tenancy; cross-module database access;
provider/model/network/credential use; external notification; breaking public
contract; destructive migration; import/account erasure/cloud recovery;
private-data leakage; dependency change; active collision; conflicting sources;
stale authority; or material CAP-0018/SLI-0075 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or an inconsequential
generated diff. Fix it within scope or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0075.WRK-0154`; exact candidate and receipt; routes,
permissions, shapes/errors, persistence/replay/revision/history behavior,
migration/reconstruction/rollback results, learner isolation, export privacy,
theme exclusion, headless client parity, focused/affected/security/
architecture/aggregate checks, documentation impact, assumptions, and residual
runtime/UI/live gaps. Confirm no UI, runtime token/theme behavior, diagnosis,
inferred trait, evidence/competency, recommendation, provider, external action,
or financial behavior changed. Leave the browser packet dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0153 completed. The packet
  consumes its fixed contract and pure core, reuses established single-profile
  PostgreSQL/API/client patterns, preserves API/headless parity and local theme
  separation, and requires no lower-level approval within CAP-0018.
- 2026-10-17: Refined the active scope to include the existing learner-
  preference PostgreSQL and API regression files whose migration-order and
  shared-host assertions must remain current after the additive migration.
- 2026-10-17: Corrected history and export to consume one coherent PostgreSQL
  profile-and-history snapshot, then added deterministic concurrent-mutation,
  mixed-choice, reset, replay, and protected-API regression evidence within the
  existing packet scope.
