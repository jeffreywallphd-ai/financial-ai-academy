---
id: WRK-0158
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0076
capability: CAP-0018
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/platform/reminders/localReminderPreference.ts", "apps/web/tests/unit/localReminderPreference.test.ts", "backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/assistance_preference_contract.py", "backend/src/financial_ai_academy/modules/learner_model/domain/assistance_preferences.py", "backend/src/financial_ai_academy/modules/learner_model/ports/assistance_preference_contract.py", "backend/tests/contract/learner_assistance_preferences", "backend/tests/unit/learner_model/test_assistance_preference_contract.py", "backend/tests/unit/learner_model/test_assistance_preferences.py", "contracts/compatibility/learner-assistance-preferences/v1", "contracts/learning/README.md", "contracts/learning/learner-assistance-preferences/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/learner-assistance-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0158-freeze-ai-help-and-local-reminder-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze AI Help and Local Reminder Contracts

## Objective and Deliverable

Freeze the additive `learner-assistance-preferences/v1` contract family and
pure Learner-model core for an explicit `off|on_request` AI-help choice. Also
deliver one dependency-free browser-local reminder adapter for the separately
owned versioned `off|in_app_when_available` choice. The adapter must validate,
replace, reset, retain bounded non-content history, export, and safely recover
from malformed or unavailable storage without a network or notification side
effect.

The result is the stable input to the later persistence/API and browser-route
packets. It creates no database row, session, permission, HTTP operation,
OpenAPI/client output, browser route, model/provider call, notification prompt,
worker, timer, schedule, queue, or external delivery.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contracts, AI/ML, interface-design, security-risk,
testing-quality, and delivery-planning context. Read the change-impact matrix,
decision readiness, CAP-0018, SLI-0076, SLI-0074, ADR-0005, ADR-0006,
ADR-0013, AI/ML system boundaries, Learner-model README and current preference
implementations, contract/versioning guidance, user-facing language standards,
the theme adapter, nearest contract and test READMEs, and concurrent-work
protocol.

## Decisions and Assumptions

- Add a separate `learner-assistance-preferences/v1` family rather than widen
  the closed general or presentation preference documents.
- `assistance_mode` is exactly `off` or `on_request`; `off` is the default.
  `on_request` means a future governed feature may offer a learner-started
  action. It does not enable or select a provider, authorize a data class,
  grant egress, call a model, create output, or promise availability.
- Learner model owns the portable learner-bound AI-help choice. A profile has
  server-owned identity, positive revision, canonical times, and a canonical
  SHA-256 digest. Empty persistence later projects revision one `off` without
  a read-side write.
- Mutation intents carry one idempotency key, exact expected revision, and a
  complete replacement or `reset_profile`. They cannot carry learner,
  provider, model, credential, prompt, content, tool, destination, permission,
  evidence, policy, time, identity, or digest facts.
- History retains at most 100 non-content summaries. Export binds the exact
  profile and history to purpose and limitations. Neither is proof that AI
  help exists or authority to perform it.
- The platform-owned reminder setting is a separate browser-local v1 envelope
  with exactly `off` and `in_app_when_available`; `off` is the default.
  `in_app_when_available` records only future local intent and sends nothing.
- The local envelope has no learner identity or headless meaning. It contains
  a positive revision, canonical update time, bounded non-content history,
  and a deterministic integrity code over canonical JSON. One allowlisted
  storage key contains the complete envelope so accepted replacement is one
  storage operation.
- An absent local value projects revision one `off` without writing. Invalid,
  unknown, corrupt, or inaccessible storage also returns a safe in-memory
  `off` projection and never overwrites the stored bytes during read.
- The pure Python core and TypeScript adapter issue no identity or time on
  their own. Explicit caller facts make fixed vectors and tests deterministic.

## In Scope

- Add Draft 2020-12 profile, mutation-intent, history, and export schemas for
  learner assistance preferences.
- Add synthetic valid examples, fixed canonical digest vectors,
  compatibility fixtures, and table-driven denials for unknown versions,
  operations, fields, values, malformed identity/time/digest, history/export
  mismatch, provider/model/data-permission/execution fields, and confidential
  internal data.
- Add a dependency-light conformance runner for closed shapes, canonical
  digest, history/export correlation, bounds, and confidentiality.
- Introduce immutable framework-free Learner-model values, canonical
  serialization/hashing, deterministic default, complete replacement, reset,
  history/export validation, and bounded errors.
- Add a narrow transport-neutral parser/projector port and JSON Schema adapter
  with no FastAPI, Pydantic, PostgreSQL, provider, or browser dependency.
- Add the versioned TypeScript local-reminder adapter with pure validation,
  canonical integrity calculation, read, replacement, reset, history, export,
  and explicit injected storage/clock/identifier inputs.
- Add focused Python and TypeScript tests for every valid value, default,
  replacement, reset, fixed digests, newest-100 history, malformed and
  unavailable storage, confidentiality, no side effects, and anti-rigidity
  across IDs, times, revisions, history lengths, and fixture order.
- Document ownership, meaning, defaults, unavailable-capability limitations,
  provider/permission separation, local-only storage, history/export
  limitations, and consumer obligations.

## Out of Scope

Application services; repositories; PostgreSQL; migrations; idempotency replay
persistence; public facades; session or permission composition; HTTP/FastAPI/
Pydantic; OpenAPI; generated clients; React routes or components; navigation;
styles; model/provider admission, selection, credentials, prompts, grounding,
generation, tools, or data egress; browser/OS notification permission; service
workers; timers; schedules; queues; reminder creation; delivery; email, SMS,
push, or external action; inferred traits; Assessment evidence; competency;
Adaptation; organization/guardian/marketing policy; dependency or lockfile
changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing general and presentation preference families and compatibility corpus | new `learner-assistance-preferences/v1` and compatibility directories plus the learning contract catalog | Freeze an additive portable AI-help choice without widening closed contracts |
| Learner-model core | current preference domains and parser/projector conventions | new assistance domain, port/adapter, tests, and bounded module README update | Establish inward-pointing typed meaning with no application or persistence effect |
| Local platform adapter | current theme adapter and browser unit-test conventions | new local-reminder adapter and focused unit test | Freeze local-only validation, retention, reset/export, safe fallback, and no-delivery semantics |
| Architecture guidance | contract ownership, provider opt-in, AI/ML boundaries, local-setting distinction | new assistance preference contract page plus bounded contract-architecture update | Record authority, privacy, and unavailable-capability limits |
| Planning evidence | SLI-0076, WRK-0158, register | listed planning files | Keep lifecycle and next seam synchronized |

No existing learner/presentation-preference, completion, practice, project,
Curriculum, Assessment, Adaptation, Identity, Personal-workspace, provider, or
notification schema or runtime; public facade; OpenAPI/client; persistence;
migration; React route; theme adapter; dependency; lockfile; or deployment
composition may change.

## Contracts and Interfaces

`learner-assistance-preference-profile-v1` is one closed document with exact
server identity, revision, `assistance_mode`, time, and digest facts.
`learner-assistance-preference-mutation-intent-v1` contains one idempotency key,
expected revision, and `replace_preferences` with one complete mode or
`reset_profile` with no replacement body. The pure mutation operation receives
validated current state plus explicit canonical time and returns the next
profile and summary or a bounded `learner_assistance_preferences.*` error.
Replay remains the application/repository packet's responsibility.

`learner-assistance-preference-history-v1` contains ordered summaries with
unique increasing revisions no newer than the current profile.
`learner-assistance-preference-export-v1` binds the exact current profile and
history to explicit purpose, limitations, schema version, and export time.
History and export contain no prior choice, session, permission, provider,
model, prompt, content, evidence, recommendation, financial meaning, or local
reminder setting.

`local-learning-reminder-preference-v1` is a TypeScript-owned closed envelope
with no learner ID. The adapter accepts a narrow `getItem/setItem/removeItem`
storage interface and explicit time/operation inputs. Read returns a validated
envelope or a safe virtual default plus a bounded local status; replacement
and reset create one complete next envelope and retain only the newest 100
summaries. Export returns JSON-compatible values only after the exact envelope
validates. No method prompts for permission, registers a worker or timer, uses
fetch, imports an API client, or claims delivery.

Canonical JSON for both boundaries uses compact sorted-key direct UTF-8 data,
excludes the integrity field itself, performs no implicit Unicode
normalization, and yields lowercase SHA-256. Synthetic fixed ASCII and Unicode
vectors prevent implementation-specific drift.

## Dependencies and Parallel Safety

CAP-0001, CAP-0017, SLI-0074, and SLI-0075 are complete; CAP-0018 authority is
current; SLI-0076 is ready; and no durable decision gate remains in this
boundary. WRK-0158 has no WRK dependency. It owns new shared contract,
Learner-model, platform-adapter, architecture, and planning paths, so it is not
parallel-safe with another packet changing those paths. It must complete
before the persistence/API packet is reserved or authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe assistance default | Valid server identity and time | Default projection runs | One deterministic revision-one `off` profile round-trips with its exact digest and no write | schema/runner/unit |
| Closed assistance values | `off` and `on_request` profiles and replacements | Validation, projection, hashing, and mutation run | Both values retain exact explicit meaning and no other value is accepted | parameterized contract/unit |
| Assistance reset | A valid `on_request` profile receives `reset_profile` | Pure mutation runs | The next revision is `off` with one non-content summary | unit/contract |
| No AI authority | Provider, model, credential, data-permission, prompt, tool, output, or execution fields are supplied | Parsing or validation runs | Input fails closed and no external or cross-module effect occurs | schema/runner/unit/architecture |
| Assistance history/export | A current profile and zero through 100 correlated summaries are supplied | Validation and projection run | Exact revisions, digest, purpose, limitations, and export time correlate without private prior values | schema/runner/unit |
| Safe local default | Browser storage has no reminder key | Read runs | Revision-one `off` is returned without a storage write | TypeScript unit |
| Local replacement and reset | Valid explicit caller facts and storage are supplied | Replace then reset runs | Each operation writes one complete validated envelope and advances exactly one revision | TypeScript unit |
| Bounded local history | More than 100 valid replacements occur | The latest envelope is read/exported | Only the newest 100 ordered non-content summaries remain | parameterized TypeScript unit |
| Corrupt or unavailable storage | Stored bytes are malformed, unknown, digest-invalid, or storage throws | Read runs | A bounded status and safe `off` projection return without overwriting data or blocking callers | TypeScript unit |
| No notification action | Every local adapter method runs | Collaborators and process capabilities are inspected | No permission, worker, timer, queue, network, subscription, or delivery effect exists | unit/architecture |
| Canonical integrity | Independent and production implementations hash fixed ASCII and Unicode vectors | Hashing runs | Compact sorted direct UTF-8 bytes produce the expected lowercase digest | vectors/runner/Python/TypeScript unit |
| Anti-rigidity | IDs, revisions, canonical times, history lengths, fixture order, and valid surrounding data vary | Focused suites run | Semantic invariants hold without frozen counts, generated values, or interface copy | parameterized contract/unit |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_assistance_preferences backend/tests/unit/learner_model/test_assistance_preference_contract.py backend/tests/unit/learner_model/test_assistance_preferences.py
npm --prefix apps/web test -- apps/web/tests/unit/localReminderPreference.test.ts
npm --prefix apps/web run typecheck
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0158-freeze-ai-help-and-local-reminder-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run the selected affected-check route, submit one exact candidate, create a
fresh qualifying receipt, and obtain one independent technical disposition.
Add no dependency or lockfile change.

## Documentation and Evidence Update

Document explicit-versus-inferred meaning, Learner-model ownership, closed
assistance values, conservative defaults, provider/model/data-permission
separation, complete replacement/reset, history/export limitations, canonical
hashing, the local-only reminder envelope and download, unavailable-capability
meaning, and unchanged evidence/policy owners. Keep the module README,
contract architecture, learning contract catalog, SLI-0076, WRK-0158, and
register synchronized.

Completion evidence records exact focused and affected checks, compatibility,
confidentiality, containment, and anti-rigidity meaning, changed files,
assumptions, environment qualifications not performed, and residual risks.
Verification receipts and technical review records remain in ignored local
control-plane storage; tracked files contain no approval or reviewer record.

## Stop Conditions

Stop for provider/model admission, credentials, selection, data permission,
prompt/tool/model execution, output, background or autonomous action;
notification permission, worker, timer, schedule, queue, subscription, or
delivery; caller-selected learner identity; browser state used as server
authority; inferred traits; preferences used as Assessment evidence,
competency, mastery, eligibility, authorization, grading, recommendation,
financial suitability, or irreversible instruction; widening an existing
closed preference family; persistence/API/OpenAPI/client/React route change;
cross-module storage; breaking contract; destructive migration;
identity/tenancy/managed-cloud/licensing/recovery/commercial expansion; new
dependency; confidential-data leakage; conflicting canonical sources; active
scope collision; stale authority; or material CAP-0018/SLI-0076 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count or order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; assistance and local-reminder contract identifiers
and closed values; default, replacement, reset, history/export, canonical
digest, confidentiality, provider/permission separation, safe local fallback,
and no-execution/no-delivery invariants; focused, architecture, security,
affected, aggregate, receipt, and independent-review results; changed files;
documentation impact; assumptions; unqualified environment checks; and
residual gaps. Confirm that no persistence, migration, public application or
HTTP operation, OpenAPI/generated client, React route, provider/model call,
notification permission or delivery, evidence/competency state,
recommendation, inferred trait, or external action changed. Leave the
persistence/API packet dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0076 refinement. The packet
  freezes the additive portable AI-help contract/pure core and the separately
  owned browser-local reminder contract/adapter while leaving persistence,
  API, interface composition, and live qualification to dependency-ordered
  packets. It remains inside CAP-0018 and needs no lower-level approval.
