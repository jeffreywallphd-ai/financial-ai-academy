---
id: WRK-0148
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: [WRK-0147]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/learner_model/learner_model_0004_preferences.up.sql", "backend/migrations/learner_model/learner_model_0004_preferences.down.sql", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/learner_model/adapters/system.py", "backend/src/financial_ai_academy/modules/learner_model/application/service.py", "backend/src/financial_ai_academy/modules/learner_model/ports/repositories.py", "backend/src/financial_ai_academy/modules/learner_model/ports/system.py", "backend/src/financial_ai_academy/modules/learner_model/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_learner_preferences_api.py", "backend/tests/integration/learner_model/test_postgres_completion_projection.py", "backend/tests/integration/learner_model/test_postgres_preferences.py", "backend/tests/integration/learner_model/test_postgres_project_completion.py", "backend/tests/unit/identity/test_identity_service.py", "backend/tests/unit/learner_model/test_preference_service.py", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api/README.md", "contracts/api/openapi.json", "apps/web/README.md", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "deployments/local/serve.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/learner-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0148-compose-learner-preference-persistence-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 69b78b8130593c4337f3537061c651aa8a0d4d2d
claim_id: WRK-0148:72a5d452-187a-4dc0-940c-a3dc9d5a837e
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T18:39:20Z
---

# Agent Work Packet: Compose Learner Preference Persistence and Public API

## Objective and Deliverable

Compose the completed learner-preference v1 contract and pure core into a
Learner-model application service, additive module-owned PostgreSQL storage,
and protected public JSON API. The same reviewed OpenAPI contract and generated
TypeScript client must serve the browser, command-line, service, and future
headless-AI callers under identical identity, permission, validation,
idempotency, concurrency, and privacy rules.

Deliver side-effect-free empty reads; deterministic create, revise, archive,
restore, reorder, remove, and reset mutations; bounded history; portable export;
exact retry; stale-write and changed-key denial; learner isolation; restart
durability; and closed public errors. Do not add browser feature UI, adaptive
ranking, inference, evidence, recommendation, provider, or external action.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`.
Revalidate CAP-0018, SLI-0074, WRK-0147, ADR-0005, the learner-preference and
identity contracts, module map, application/repository direction, migration
rules, API/OpenAPI/client generation conventions, privacy guidance, testing
standards, and nearest READMEs. Inspect all affected contracts,
implementations, consumers, migrations, and tests.

No unresolved identity, tenancy, data-license, provider, model-authority,
encryption, recovery, legal, commercial, or external-execution decision is
needed. Stop if implementation would change one of those durable choices.

## Decisions and Assumptions

- Learner model owns the profile, replay records, and bounded change summaries
  in its existing schema. No cross-module foreign key or repository read is
  introduced.
- Existing single-profile identity gains narrow `learner_preferences.read` and
  `learner_preferences.write` permissions. The server session is the only
  learner selector; request bodies and query strings cannot choose identity.
- Public routes are `GET /api/v1/learner-preferences`, `POST
  /api/v1/learner-preferences/mutations`, `GET
  /api/v1/learner-preferences/history`, and `GET
  /api/v1/learner-preferences/export`.
- An absent stored row projects a deterministic revision-one empty profile
  without writing. The deterministic profile ID binds to the server learner;
  the first accepted mutation persists revision two atomically.
- Server clock and identifier ports supply canonical time and operation-
  appropriate IDs. Generic entry IDs remain globally unique across the
  profile as frozen in WRK-0147.
- PostgreSQL serializes each learner with a transaction-scoped advisory lock,
  checks exact replay before revision, writes profile/replay/change together,
  and retains at most 100 newest change summaries.
- Exact reuse of an idempotency key returns the accepted profile. Changed reuse
  fails as immutable conflict. A stale expected revision fails without a
  profile, replay, or history write.
- OpenAPI is the source for generated TypeScript types and client operations;
  no handwritten browser-only or agent-only API is introduced.

## In Scope

- Add framework-free public requests, responses, error vocabulary, and service
  operations for open, mutate, history, and export.
- Add repository/system ports, UUID-backed identifiers, deterministic empty
  profile seed, contract revalidation, and safe domain-to-public error mapping.
- Add forward, reapply, and development-down Learner-model migration for
  current profiles, accepted mutation replay, and bounded summaries.
- Add PostgreSQL repository reads and one atomic optimistic/idempotent save;
  prove isolation, retry, conflict, atomicity, history truncation, and restart.
- Add protected API models/routes and the two module-specific permissions;
  reject missing/wrong permission, caller-selected learner identity, unknown
  query/body fields, malformed input, stale revision, and changed-key reuse.
- Regenerate and review OpenAPI and generated TypeScript files; prove direct
  generated-client usage without importing backend internals.
- Wire application composition, local serving, schema settings, migrations,
  module-boundary checks, and focused unit/integration tests.
- Synchronize API, module, architecture, slice, packet, and register docs.

## Out of Scope

Browser screens or controls; theme/accessibility/AI/notification preferences;
automatic goal creation; inferred traits; behavioral profiling; semantic
classification; embeddings; recommendations; Curriculum prerequisites;
Assessment evidence; competency/mastery changes; Adaptation policy; provider
or model calls; collaboration/organizations/tenancy; files or arbitrary URLs;
external notifications; managed-cloud retention/recovery; account erasure;
import; separate agent authority; financial advice/action; dependency changes;
or styling-only work.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Learner-model core | Public/application/repository/system seams | One shared framework-free core; no other-module state |
| Persistence | Additive `learner_model_0004` tables and focused adapter | Atomic replay/revision/history; no destructive or cross-schema behavior |
| Identity/API | Two scoped permissions and four protected routes | Server-owned learner/time/IDs; closed inputs and safe errors |
| OpenAPI/client | Reproduced snapshot and generated files | Browser/headless parity; no handwritten divergence |
| Composition | Settings, service assembly, and local host wiring | Local/cloud semantics remain portable |
| Tests/docs | Focused unit, PostgreSQL, API, architecture, and contract evidence | Privacy, isolation, anti-rigidity, and exact cleanup |

No path outside `write_scope` may change. Stop if another migration family,
module repository, UI source, provider, dependency, deployment policy, or
unlisted shared boundary becomes necessary.

## Contracts and Interfaces

Expose transport-neutral operations equivalent to:

```text
open_preferences(learner_id) -> LearnerPreferenceProfile
mutate_preferences(learner_id, PreferenceMutationIntent) -> LearnerPreferenceProfile
read_preference_history(learner_id) -> PreferenceHistory
export_preferences(learner_id) -> PreferenceExport
```

The API request uses the frozen mutation-intent shape. All response shapes use
the frozen v1 profile, history, and export fields exactly. Export purpose and
limitations use stable plain language and contain no storage, session,
permission, replay, provider, inference, evidence, score, or policy fields.

Public failure codes distinguish invalid request, immutable conflict, stale
revision, not found, profile/history integrity failure, quota failure, and
temporary unavailability. Messages are actionable and safe; they never echo
learner text, database details, secrets, or provider payloads.

## Dependencies and Parallel Safety

WRK-0147 is complete and fixes all consumed contract/domain semantics.
WRK-0148 owns shared Learner-model, Identity, host API, OpenAPI, generated-
client, composition, migration, test, documentation, slice, and register paths.
It is not parallel-safe with another SLI-0074 packet and must complete before
the browser packet is reserved or authored.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Empty open | Authorized read returns deterministic revision-one empty profile and performs no database write | unit/PostgreSQL/API |
| Record and reopen | Varied Unicode goals, experience, and interests reopen with exact wording, order, revision, times, and digest | unit/PostgreSQL/API |
| Complete operations | Every frozen operation produces one atomic next revision and correlated summary | unit/PostgreSQL/API |
| Retry/conflict | Exact retry returns accepted result; changed-key and stale-revision requests write nothing | unit/PostgreSQL/API |
| History bound | More than 100 accepted changes retain the newest 100 valid summaries and current revision | PostgreSQL/anti-rigidity |
| Reset/export | Reset creates a new empty revision; history/export remain correlated and omit prior private content | contract/PostgreSQL/API |
| Authorization/isolation | Missing or wrong permission, caller identity fields, and cross-learner access fail closed | API/security/PostgreSQL |
| Atomic interruption | Simulated failure rolls back profile, replay, and summary together | PostgreSQL |
| Restart | Accepted state and replay remain exact after ordinary service reconstruction | PostgreSQL/API |
| Headless parity | A non-browser generated-client consumer can read and mutate through reviewed public operations | OpenAPI/client contract |
| No policy leakage | No inference, evidence, mastery, eligibility, recommendation, provider, financial, or external-action state is created | architecture/security |
| Anti-rigidity | Empty/populated profiles, varied valid text, optional detail, counts, order, IDs, and times share invariant behavior | parameterized tests |

## Verification Commands

Run focused Learner-model preference unit, contract, real-PostgreSQL, protected
API, identity, composition, and module-boundary tests; migration forward,
reapply, development-down, rollback, restart, and cleanup evidence; OpenAPI
currency and generated-client reproduction/usage checks; security, architecture,
planning, documentation, typecheck/lint where affected, Python compilation,
and whitespace checks; controller-selected exact-candidate verification; an
independent technical disposition; and `python dev-tools/agent/check_ready.py`.

## Documentation and Evidence Update

Record exact routes, permissions, public fields/errors, learner/time/ID
authority, empty-read behavior, replay and concurrency rules, history bound,
reset/export privacy, migration/restart evidence, OpenAPI/headless parity,
qualified checks, assumptions, and remaining browser/live-qualification gaps.
Keep approvals, technical-review records, and verification receipts only in
ignored local control-plane storage.

## Stop Conditions

Stop for inferred or hidden profiling; preferences used as evidence, mastery,
eligibility, permission, recommendation, suitability, or irreversible action;
new identity model or organization tenancy; cross-module database access;
provider/model/network/credential use; external notification; breaking public
contract; destructive migration; import/account erasure/managed-cloud recovery;
private-data leakage; dependency change; active write collision; conflicting
canonical sources; or material CAP-0018/SLI-0074 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or an inconsequential
generated diff. Fix it within scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0074.WRK-0148`; exact candidate and qualifying receipt;
routes, permissions, public shapes/errors, persistence/replay/revision/history
behavior, migration/restart/rollback results, learner isolation, export privacy,
headless client parity, focused/affected/security/architecture/aggregate checks,
documentation impact, assumptions, and residual browser/live gaps. Confirm no
UI, inferred trait, evidence/competency, recommendation, provider, external
action, or financial behavior changed. Leave the browser packet dependency-
ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0147 completed. The packet
  consumes its fixed contract and pure core, uses the established single-
  profile identity and PostgreSQL/API patterns, preserves API/headless parity,
  and requires no lower-level approval within the current CAP-0018 package.
- 2026-10-17: Activated from recorded base `69b78b8` after confirming the
  current CAP package, completed WRK-0147 dependency, resolved decision
  posture, exact bounded scope, and no active coordination collision.
