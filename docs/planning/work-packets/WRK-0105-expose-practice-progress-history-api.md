---
id: WRK-0105
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: ["WRK-0104"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/generated/api-client/", "apps/web/tests/contract/generated-client.test.mjs", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_practice_progress_api.py", "backend/tests/integration/api/test_single_profile_practice_submission_api.py", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0105-expose-practice-progress-history-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 407f68f6587280a49a7da41537fc5dbbffde8bd3
claim_id: WRK-0105:4c4acab2-2651-4ddc-abb7-ce6d52ad3bf4
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T18:06:10Z
---

# Agent Work Packet: Expose Practice Progress and History API

## Objective and Deliverable

Expose the accepted practice draft, deterministic retry state, latest targeted
review destinations, and rebuildable attempt history through protected,
versioned HTTP operations and the reviewed OpenAPI/generated TypeScript client
seam. The same cookie-backed operations must remain directly usable by
non-browser and future headless clients; no browser-only policy or second core
is introduced.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the routed baseline, application-host,
identity, assessment, curriculum, learner-model, contract, security, and
testing context. Inspect CAP-0006, SLI-0028, WRK-0102 through WRK-0104,
ADR-0005, ADR-0007, ADR-0008, decision readiness, the change-impact matrix,
contract architecture, identity-provider contract, accepted draft/retry/
review/history schemas and corpora, public module facades, the API composition
root, models, routes, error mapping, OpenAPI generator, generated-client
pipeline, consumers, nearest READMEs, and established API tests.

## Decisions and Assumptions

- The existing opaque single-profile session remains the only learner selector;
  no request body, query, path, or generated client may select a learner.
- One protected progress read composes current Assessment draft and retry state,
  Learner-model history, and Curriculum review targets through public module
  operations. It never reads module persistence or recomputes scoring.
- Review actions are derived only from the latest immutable attempt. Scan its
  incorrect item summaries and their declared review-reference order, dedupe
  exact IDs stably, join them to the exact answer-safe practice presentation,
  and ask Curriculum to resolve those complete identities. Empty history or an
  all-correct latest attempt returns no targets. Missing mappings remain
  explicit unavailable targets; the host never ranks or substitutes them.
- Draft save is a complete replacement snapshot whose exact route placement
  must match the accepted body. Assessment remains authoritative for revision,
  save time, validation, concurrency conflict, and storage.
- Existing `curriculum.lesson.read` authorization and same-origin state-change
  policy apply to this private-host learning operation. Adding new role or
  tenancy policy is outside this CAP.

## In Scope

- Add a protected read operation for exact practice progress that returns a
  nullable answer-safe draft, deterministic retry state, bounded attempt
  history, and latest-attempt review targets in one closed response.
- Add a protected state-changing draft-save operation that accepts the exact
  versioned draft-save document, rejects route/body mismatch and caller-owned
  authority, and returns the server-owned draft document.
- Compose only Assessment, Curriculum, and Learner-model public operations;
  keep selection and wire mapping thin, deterministic, and transport-owned.
- Map attempt-limit, stale/version, conflict, absence, invalid, unauthorized,
  inconsistent, and unavailable failures to bounded established HTTP errors.
- Wire the existing practice-progress contract adapter into the production
  composition root so browser and headless clients receive the same behavior.
- Regenerate and review the OpenAPI 3.1 snapshot and TypeScript client, extend
  contract tests, and add focused protected API/headless tests for success,
  denial, confidentiality, variable counts, and exact mapping.
- Reconcile host, client, contract-architecture, module-map, assurance,
  slice, packet, and register documentation.

## Out of Scope

Browser components or routes; visual styling; live Chromium qualification;
new contract schemas or event bytes; submission scoring or persistence changes;
new identity permissions, roles, tenancy, or remote exposure; cross-version
draft migration; history deletion; adaptive ranking; mastery or competency
inference; Audit policy changes; queues, workers, external providers, cloud
recovery, or a separate AI/headless implementation.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API host | public facades, auth dependencies, error handlers, existing practice routes | closed response/request models, two protected operations, deterministic latest-review composition | Expose current accepted module meaning without persistence access |
| Composition | Assessment construction and practice contract adapters | inject the accepted progress contract adapter | Make the transport-neutral operations available in real local composition |
| Contract generation | OpenAPI generator/snapshot and generated TypeScript pipeline | deterministic model stubs, snapshot, client outputs, generation assertions | Preserve one reviewed browser/headless contract |
| Verification | established practice API and client tests | focused progress/history API suite and retry-error regression | Prove authority, confidentiality, failures, and variable cardinality |
| Documentation/planning | affected host/client/architecture guidance and SLI-0028 records | only implemented API ownership, evidence, and lifecycle | Keep public behavior and known remaining seams current |

No domain model, accepted JSON Schema, migration, repository, event, web
feature implementation, dependency, or lockfile may change in this packet.

## Contracts and Interfaces

Consume the accepted Assessment `draft`, `draft-save`, and `retry-state`,
Curriculum `practice-review-target`, and Learner-model `history` 1.0.0 shapes.
The API models must remain closed and serialize those public meanings without
learner identity, answers, evaluator declarations, raw event/result documents,
request fingerprints, private diagnostics, or storage rows.

Use exact placement-scoped operations under the existing practice resource.
The read response carries one nullable draft, one retry state, one complete
history view, and zero or more resolved targets. The save request carries only
the accepted draft-save body; the response is the accepted server-owned draft.
OpenAPI is generated from validated API models, and the TypeScript client is
generated only from that reviewed snapshot.

## Dependencies and Parallel Safety

WRK-0104 is complete and supplies all transport-neutral public operations and
persistence behavior. This packet owns shared API host, OpenAPI, generated
client, and composition files, so it is not parallel-safe with another host or
client packet. The browser packet depends on this exact reviewed client seam
and cannot start until this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Headless progress read | Authorized opaque session and exact practice state | Non-browser client reads progress | Response contains exact nullable draft, retry state, history, and latest-attempt targets with no learner or private fields | API/OpenAPI/client |
| Draft save and replay | Valid partial snapshot with current revision | Client saves or exactly retries it | Route/body identity is exact and Assessment returns server revision/time; replay is stable | API/application |
| Stale or mismatched save | Stale revision, malformed body, wrong placement, or unsupported version | Client saves | Bounded 400/409 result preserves current server draft and leaks no diagnostic payload | API/security |
| Authorization boundary | Missing/invalid session, missing permission, learner selector, or invalid origin | Client reads or writes | Request is denied before module mutation; no caller-selected identity is honored | API/security |
| Latest targeted review | Latest attempt has variable incorrect items and repeated declared references | Client reads progress | IDs dedupe in stable item/reference order and exact Curriculum mappings return available or explicit unavailable targets | API/unit |
| Empty or all-correct history | No attempt or latest attempt is all correct | Client reads progress | History remains complete and review targets are empty without fabricated guidance | API/unit |
| Retry exhaustion | Distinct attempts reached the accepted maximum | Client reads or submits | Retry state is exhausted and a further distinct submission maps to bounded 409 rather than an internal failure | API/regression |
| Confidentiality | Stored evidence includes responses, answer/rule material, and internal identifiers | Host serializes progress | Only accepted answer-safe public fields cross the boundary | API/OpenAPI/security |
| Reproduction | Reviewed snapshot and generated client exist | Generators run twice and check mode runs | Outputs are byte-stable and client exposes both operations with same-origin credentials | generation/contract |
| Anti-rigidity | Draft responses, attempts, items, and review targets vary within accepted bounds | Operations compose results | No fixture ID, one count, timestamp, or exact prose is required | API/unit |

## Verification Commands

Run the focused practice progress/history API suite and existing practice open,
submission, completion, and authorization regressions; the three accepted
draft/retry/review/history contract suites; OpenAPI generation/check and
snapshot assertions; generated-client generation/check, contract tests, and
TypeScript compile; architecture module-boundary checks; `python
dev-tools/planning/check_planning.py`; `python
dev-tools/documentation/check_docs.py`; `git diff --check`; exact-candidate
affected verification; independent technical review; and `python
dev-tools/agent/check_ready.py` when selected by packet start. Live PostgreSQL,
browser, restart, and accessibility composition remain the qualification
packet's responsibility unless a focused real-composition regression is needed
to prove the adapter wiring.

## Documentation and Evidence Update

Update the backend host and generated-client guidance, contract architecture,
module map, architecture verification, SLI-0028, this packet, and the planning
register. Record exact candidate/receipt evidence, route and operation IDs,
authorization and identity invariants, latest-review selection, response
confidentiality, deterministic generation, focused/aggregate results,
assumptions, and remaining browser/live seams. No ADR or decision-readiness
change is expected.

## Stop Conditions

Stop for a new permission/role/tenancy choice; changing accepted schema or
event bytes; placing scoring, retry, mastery, recommendation, or destination
authority in the host; reading module persistence from the host; exposing
learner IDs, answers, evaluator rules, raw evidence, or storage details;
requiring a browser-only core; arbitrary execution or external effects;
conflicting canonical authority; stale CAP binding; active scope overlap; or an
API shape that cannot represent the accepted contract without breaking change.

Do not stop or reopen review for harmless whitespace, optional wording, or
nonfunctional styling. Fix an inconsequential in-scope issue locally or defer
optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; route and operation inventory;
production adapter composition; opaque-session and same-origin enforcement;
draft/retry/history/review selection and confidentiality invariants; OpenAPI
and generated-client reproduction; focused, contract, architecture,
documentation, planning, aggregate, and independent acceptance results;
changed paths, assumptions, and residual gaps. Confirm direct browser and
headless use of the same API and that browser UI, live qualification, adaptive,
mastery, provider, cloud, and external-execution work remains later or outside
the CAP.

## Planning History

- 2026-10-16: Authored just in time after WRK-0104 completed. The packet keeps
  the accepted transport-neutral core unchanged and bounds one independently
  reviewable protected API/OpenAPI/generated-client result before browser work.
