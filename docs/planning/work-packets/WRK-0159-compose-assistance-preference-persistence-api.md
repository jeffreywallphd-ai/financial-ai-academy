---
id: WRK-0159
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0076
capability: CAP-0018
depends_on: [WRK-0158]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "backend/migrations/learner_model/learner_model_0006_assistance_preferences.down.sql", "backend/migrations/learner_model/learner_model_0006_assistance_preferences.up.sql", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/learner_model/adapters/system.py", "backend/src/financial_ai_academy/modules/learner_model/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/ports/repositories.py", "backend/src/financial_ai_academy/modules/learner_model/ports/system.py", "backend/src/financial_ai_academy/modules/learner_model/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_assistance_preferences_api.py", "backend/tests/integration/api/test_single_profile_learner_preferences_api.py", "backend/tests/integration/api/test_single_profile_presentation_preferences_api.py", "backend/tests/integration/learner_model/test_postgres_assistance_preferences.py", "backend/tests/integration/learner_model/test_postgres_completion_projection.py", "backend/tests/integration/learner_model/test_postgres_preferences.py", "backend/tests/integration/learner_model/test_postgres_presentation_preferences.py", "backend/tests/integration/learner_model/test_postgres_project_completion.py", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/unit/learner_model/test_assistance_preference_service.py", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api/README.md", "contracts/api/openapi.json", "deployments/local/serve.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/learner-assistance-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0159-compose-assistance-preference-persistence-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 9459290be9704952a91231d7941709b764170072
claim_id: WRK-0159:c07084f8-8410-45f7-9f26-0303e65e5f71
claimed_by: codex-cap-0018
claimed_at: 2026-10-18T00:09:59Z
---

# Agent Work Packet: Compose Assistance Preference Persistence and Public API

## Objective and Deliverable

Compose the completed `learner-assistance-preferences/v1` contract and pure
core into Learner-model application operations, additive module-owned
PostgreSQL storage, and a protected public JSON API. The same reviewed OpenAPI
contract and generated TypeScript client must serve browser, command-line,
service, and future headless-AI callers under identical identity, permission,
validation, replay, concurrency, and privacy rules.

Deliver side-effect-free default reads; complete `off|on_request` replacement
and reset; bounded non-content history; portable export; exact retry;
stale-write and changed-key denial; learner isolation; restart durability; and
closed public errors. The API records learner intent only. It must not admit or
select a model provider, grant data permission, call a model, produce AI
output, or expose the separate browser-local reminder choice.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md` and
perform their Required Startup. Revalidate CAP-0018, SLI-0076, WRK-0158,
ADR-0005, ADR-0006, ADR-0013, the learner-assistance, learner-preference,
presentation-preference, identity, API, migration, application/repository, and
AI/ML contracts, module map, privacy and security guidance, generated-client
conventions, testing standards, nearest READMEs, and concurrent-work protocol.
Inspect affected contracts, implementations, consumers, migrations, and tests.

No unresolved identity, tenancy, licensing, provider, model-authority,
encryption, recovery, legal, commercial, queue, or external-execution decision
is needed because this packet records a closed preference and performs no AI
or reminder action. Stop if implementation would change one of those choices.

## Decisions and Assumptions

- Learner model owns the portable assistance profile, replay records, and
  bounded summaries in its existing schema. No other module or browser-local
  repository becomes authoritative.
- Existing single-profile identity gains narrow
  `learner_assistance_preferences.read` and
  `learner_assistance_preferences.write` permissions. The server session is
  the only learner selector; bodies and query strings cannot choose identity.
- Public routes are `GET /api/v1/learner-assistance-preferences`, `POST
  /api/v1/learner-assistance-preferences/mutations`, `GET
  /api/v1/learner-assistance-preferences/history`, and `GET
  /api/v1/learner-assistance-preferences/export`.
- Absent storage projects one deterministic revision-one `off` profile without
  writing. The first accepted mutation persists revision two atomically.
- Server clock and identifier ports supply canonical time and profile facts.
  The request supplies only its idempotency key, expected revision, and closed
  operation from the frozen mutation contract.
- PostgreSQL serializes each learner with the established transaction-scoped
  advisory lock, checks exact replay before revision, writes profile/replay/
  summary together, and retains exactly the newest 100 summaries.
- Exact reuse of an idempotency key returns the accepted profile. Changed reuse
  and stale revision fail without profile, replay, or history writes.
- History and export contain no prompts, content, provider, model, data class,
  permission, output, evidence, score, recommendation, or local-reminder fact.
- OpenAPI is the source for generated TypeScript types and operations. Browser
  and supported headless callers use the same API; no agent-only shortcut or
  browser-only copy of learner-owned state is introduced.

## In Scope

- Add transport-neutral public requests, responses, bounded errors, and
  application operations for open, mutate, history, and export.
- Add repository/system ports, deterministic default identity, contract
  revalidation, and safe domain-to-public error mapping.
- Add forward, reapply, retained-data down-refusal, and development-down
  migration behavior for profiles, accepted replay, and bounded summaries.
- Add PostgreSQL coherent reads and one atomic optimistic/idempotent save;
  prove isolation, retry, conflict, rollback, exact history retention, and
  restart reconstruction.
- Add protected API models/routes and two module-specific permissions; reject
  missing/wrong permission, caller-selected learner identity, unknown fields,
  malformed input, stale revision, and changed-key reuse.
- Regenerate and review OpenAPI and generated TypeScript files; prove direct
  generated-client use from a non-browser consumer without backend imports.
- Wire application composition, local serving, schema settings, migrations,
  module-boundary checks, and focused unit/integration tests.
- Synchronize API, module, architecture, slice, packet, and register docs.

## Out of Scope

Browser pages or controls; browser-local reminder persistence, export, or
headless meaning; provider admission, credentials, provider/model selection,
data-class permission, prompts, tools, grounding, generation, AI output, cost
policy, autonomous/background action, or network egress; notification
permission, worker, timer, schedule, queue, subscription, or delivery;
inferred assistance need or engagement profiling; preferences used as
Assessment evidence, competency, mastery, eligibility, grading,
recommendation, financial suitability, or instruction; organizations,
tenancy, import, erasure, managed-cloud recovery, dependency changes, or
styling-only work.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Learner-model core | Public/application/repository/system seams | One shared framework-free core; no other-module state |
| Persistence | Additive `learner_model_0006` tables and focused adapter | Atomic replay/revision/history; no destructive or cross-schema behavior |
| Identity/API | Two scoped permissions and four protected routes | Server-owned learner/time/IDs; closed requests and confidential errors |
| OpenAPI/client | Reproduced snapshot and generated files | Browser/headless parity; no handwritten divergence |
| Composition | Settings, service assembly, and local host wiring | Local/cloud semantics remain portable |
| Tests/docs | Focused unit, PostgreSQL, API, architecture, and contract evidence | Privacy, containment, anti-rigidity, and exact cleanup |

No path outside `write_scope` may change. Stop if another migration family,
module repository, browser feature source, provider adapter, dependency,
deployment policy, or unlisted shared boundary becomes necessary.

## Contracts and Interfaces

Expose transport-neutral operations equivalent to:

```text
open_assistance_preferences(learner_id) -> AssistancePreferenceProfile
mutate_assistance_preferences(learner_id, AssistancePreferenceMutationIntent) -> AssistancePreferenceProfile
read_assistance_preference_history(learner_id) -> AssistancePreferenceHistory
export_assistance_preferences(learner_id) -> AssistancePreferenceExport
```

The API request uses the frozen mutation-intent shape. Responses use the
frozen v1 profile, history, and export fields exactly. `on_request` means only
that a later governed feature may offer a learner-started action; it is not
provider/model enablement, data permission, proof of availability, or standing
execution authority. Export purpose and limitations make that boundary
explicit and contain no storage, session, permission, replay, provider,
inference, evidence, notification, or policy fields.

Public failures distinguish invalid request, immutable idempotency conflict,
stale revision, profile/history integrity failure, and temporary
unavailability. Messages are actionable and safe; they never echo learner
identity, database detail, secret, provider payload, prompt, or content.

## Dependencies and Parallel Safety

WRK-0158 is complete and fixes all consumed contract/domain semantics.
WRK-0159 owns shared Learner-model, Identity, host API, OpenAPI,
generated-client, composition, migration, test, documentation, slice, and
register paths. It is not parallel-safe with another SLI-0076 packet and must
complete before the browser packet is reserved or authored.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Safe default open | Authorized read returns deterministic revision-one `off` and performs no database write | unit/PostgreSQL/API |
| Closed replacement/reset | Either valid choice advances exactly one revision; reset returns `off` | unit/PostgreSQL/API |
| No AI authority | `on_request` changes only the profile; no provider, permission, model, prompt, output, evidence, or network state changes | architecture/security/integration |
| Retry/conflict | Exact retry returns the accepted profile; changed-key reuse and stale revision write nothing | unit/PostgreSQL/API |
| Coherent newest-100 history | More than 100 accepted mutations retain exactly the newest 100 correlated summaries and current revision | PostgreSQL/anti-rigidity |
| Export privacy | Export binds the current profile and history while omitting prior values and confidential or execution facts | contract/PostgreSQL/API |
| Authorization/isolation | Missing or wrong permission, caller identity fields, and cross-learner access fail closed | API/security/PostgreSQL |
| Atomic interruption | Simulated failure rolls back profile, replay, and summary together | PostgreSQL |
| Restart | Accepted state and replay remain exact after ordinary service reconstruction | PostgreSQL/API |
| Headless parity | A non-browser generated-client consumer can read and mutate through reviewed public operations | OpenAPI/client contract |
| Local reminder separation | API, profile, history, export, database, and generated client contain no local-reminder value | contract/API/architecture |
| Flexible valid inputs | Both choices, generated IDs/times, zero through 100 summaries, and varied unrelated state share invariant behavior | parameterized tests |

## Verification Commands

Run focused Learner-model assistance-preference unit, contract, real-
PostgreSQL, protected API, identity, composition, and module-boundary tests;
migration forward, reapply, retained-data down-refusal, development-down,
rollback, restart, and cleanup evidence; OpenAPI currency and generated-client
reproduction/usage checks; security, architecture, planning, documentation,
typecheck/lint where affected, Python compilation, and whitespace checks;
controller-selected exact-candidate verification; one independent technical
disposition; and `python dev-tools/agent/check_ready.py`.

## Documentation and Evidence Update

Record exact routes, permissions, public fields/errors, learner/time/ID
authority, default-read behavior, replay and concurrency rules, history bound,
export privacy, provider/model/data-permission separation, local-reminder
exclusion, migration/restart evidence, OpenAPI/headless parity, qualified
checks, assumptions, and remaining browser/live-qualification gaps. Keep
approval, technical disposition, and verification-receipt records only in
ignored local control-plane storage.

## Stop Conditions

Stop for provider/model admission, credentials, selection, data-class
permission, prompt/tool/model execution, output, background/autonomous action,
or network egress; notification permission or delivery; queue, schedule,
service worker, or timer; inferred profiling; preference used as evidence,
mastery, eligibility, permission, recommendation, suitability, or irreversible
action; new identity/tenancy model; caller-selected learner identity;
cross-module database access; local reminder entering the API; breaking public
contract; destructive migration; import/erasure/managed-cloud recovery;
private-data leakage; dependency change; active write collision; conflicting
canonical sources; or material CAP-0018/SLI-0076 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or an inconsequential
generated diff. Fix it within scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0076.WRK-0159`; exact candidate and qualifying receipt;
routes, permissions, public shapes/errors, default/replay/revision/history
behavior, migration/restart/rollback results, learner isolation, export
privacy, no-AI/no-reminder containment, headless-client parity, focused/
affected/security/architecture/aggregate checks, documentation impact,
assumptions, and residual browser/live gaps. Confirm no browser UI, local
reminder authority, provider/model/data permission, AI output, inferred trait,
evidence/competency, recommendation, notification, external action, or
financial behavior changed. Leave the browser packet dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0158 completed. The packet
  consumes its fixed learner-assistance contract and pure core, reuses the
  established single-profile PostgreSQL/API/client patterns, preserves API/
  headless parity and browser-local reminder separation, and requires no
  lower-level approval within the current CAP-0018 package.
- 2026-10-17: Activated from recorded base `9459290` after confirming the
  current CAP package, completed WRK-0158 dependency, resolved decision
  posture, bounded scope, and no active coordination collision.
