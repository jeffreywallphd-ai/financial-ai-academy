---
id: WRK-0128
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: ["WRK-0127"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/router.tsx", "apps/web/src/features/project-workspace/ProjectDetailPage.tsx", "apps/web/src/features/project-workspace/ProjectRoutes.tsx", "apps/web/src/features/project-workspace/ProjectSubmissionPage.tsx", "apps/web/src/features/project-workspace/api.ts", "apps/web/src/features/project-workspace/model.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/styles/project-workspace.css", "apps/web/tests/browser/project-workspace/project-workspace.spec.ts", "apps/web/tests/component/projectWorkspace.test.tsx", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/unit/projectWorkspaceModel.test.ts", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_project_submission_api.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/contracts/project-submission-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0128-deliver-project-learning-submission-browser-flow.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Project Learning-Submission Browser Flow

## Objective and Deliverable

Deliver one accessible, generated-client Project snapshot learning-submission
flow. A learner opens an eligible immutable checkpoint, reviews the exact
learning milestones and safe checkpoint records, associates each milestone
with retained evidence, corrects bounded server validation problems, submits,
and reopens the immutable evidence history and server-derived Project activity
completion. Add the missing protected Project-completion read route as a thin
Learner-model/Audit composition so browser, command-line, service, and future
headless clients use the same server-owned completion meaning.

## Required Context

Before any file change, follow the repository-root `AGENTS.md` and
`docs/README.md` startup. Route through the baseline, architecture-contracts,
learning-adaptation, interface-design, testing-quality, and delivery-planning
packs. Read CAP-0007, SLI-0032, WRK-0124 through WRK-0127, ADR-0005, ADR-0011,
ADR-0012, the Project submission and Assessment contracts, executable Project
submission schemas, Learner-model and Audit public operations, API host/models
and generators, generated client, Project browser routes/model/tests, nearest
READMEs, interface and learner-language standards, change-impact guidance,
decision readiness, and concurrent-work rules. Inspect implementation,
consumers, and tests before editing.

## Decisions and Assumptions

- Assessment remains the sole authority for candidate facts, deterministic
  validation, accepted evidence, replay, history, and supersession. The browser
  assembles an intent only from the current safe candidate and does not decide
  completion, grading, eligibility, authorization, or persistence.
- The new completion GET composes the existing Learner-model Project operation
  and Audit reconciliation exactly as the accepted lesson-completion route does.
  It is additive, session-owned, Project-scoped, and independently headless.
- One dedicated route under the existing Project area may show the selected
  checkpoint form and the full retained Project submission history. No separate
  browser-only store or API contract is introduced.
- All records are closed and validated before display. Private artifact bytes,
  paths, persistence facts, stack traces, learner selectors, answer/quality
  judgments, mastery claims, and Audit internals never enter the page model.
- Existing semantic tokens, reviewed SVG icons, Project styles, and plain learner
  language are reused. Nonfunctional styling defects do not reopen functional
  review and may be deferred to CAP-0031.

## In Scope

- Add a protected `GET /api/v1/projects/{project_id}/completion` operation that
  reconciles existing public Audit facts, rebuilds/opens the current
  Learner-model Project completion view, and returns its bounded completion
  meaning, exact source digest, rebuild time, and safe ordered source references.
- Regenerate the reviewed OpenAPI snapshot and TypeScript client and extend the
  generated-client contract-usage check for the new route.
- Add closed TypeScript guards and route state for candidate, validation result,
  immutable evidence/history, and Project completion responses. Reject extra,
  missing, malformed, uncorrelated, unsafe, or private fields before rendering.
- Add a generated-client loader/action and route for one exact Project/checkpoint.
  The action reopens the authoritative candidate, admits only expected form
  fields and candidate-owned milestone/resource identities, creates or reuses
  one stable submission identity for retry, and posts the canonical v1 intent.
- Present plain-English checkpoint, milestone, safe evidence, validation issue,
  retained history, supersession, and completion meaning. Preserve learner
  selections after bounded refusal and provide explicit retry/reload recovery.
- Link only learning-started eligible checkpoints from the Project detail page;
  independent Projects remain ordinary Projects with no Assessment meaning.
- Cover keyboard order and focus after invalid input, landmarks/headings, field
  labels and descriptions, validation summaries, zoom/reflow, reduced motion,
  forced colors, light/dark parity, and accessible technical-record disclosures.
- Add unit, component, protected API, generated-client, and focused Chromium
  coverage, including anti-rigidity over one and many milestones/resources,
  Unicode labels, optional provenance, multiple retained submissions, and valid
  identifier boundaries.
- Reconcile affected API, browser, architecture-contract, and planning docs.

## Out of Scope

- Changing Project or Assessment v1 schema meaning, persistence, validation
  policy, accepted evidence, replay, supersession, or authorization.
- New Learner-model or Audit domain rules, migrations, tables, event shapes, or
  authority; the host only exposes already completed public operations.
- Instructor, peer, AI, rubric, quality, truth, reproducibility, mastery,
  competency, suitability, advice, or performance judgments.
- Submitting an independent Project, mutating or copying a checkpoint, changing
  the live workspace, executing or actively rendering artifacts, scanning via a
  provider, expanding archives, installing packages, or using network/secrets.
- Live Portfolio/provider integration, organization tenancy, collaboration,
  public sharing, managed cloud, external queues/notifications, production
  recovery, analytics, or a separate AI/headless mode.
- Slice-wide PostgreSQL/restart/live-browser qualification and closure; JIT-E
  owns that cumulative boundary after this focused browser packet completes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public host | Learner-model/Audit operations, lesson completion precedent, Project permissions | API app, models, schema generator, host README | Expose one thin protected Project-completion read |
| Reviewed client | OpenAPI snapshot/generator and generated TypeScript | OpenAPI snapshot, generated schema, usage check | Keep browser and headless clients on one contract |
| Browser model/API | Existing Project closed guards, loaders, actions, session renewal | Project model and API files | Validate and compose authoritative safe responses |
| Browser interface | Project detail, routes, router, shared Project styles | New submission page and bounded existing consumers | Deliver the learner-observable submission/reopen flow |
| Verification | API, model, component, contract, Chromium suites | Named focused tests only | Prove security, accessibility, anti-rigidity, replay, and denial |
| Documentation | API/Project browser behavior and planning lifecycle | Named READMEs, architecture contract, SLI/register/packet | Keep public and delivery evidence current |

No token, icon, dependency, lockfile, backend domain, migration, or unrelated
route change is authorized.

## Contracts and Interfaces

- Preserve the completed Assessment Project candidate, submission outcome,
  exact evidence, and history schemas byte-for-byte. Generated types are inputs,
  not substitutes for runtime closure and correlation checks.
- The completion response is a transport projection of
  `ProjectCompletionView`: schema/versioned safe identifiers, `completed`, exact
  bounded non-mastery meaning, source digest, UTC rebuild time, and ordered
  history references. It includes no learner selector, evidence mapping bytes,
  Audit identifier, database fact, or mutable Project state.
- Every request derives learner identity and permission from the server session.
  Project/checkpoint/submission path identities must correlate with the returned
  documents; extra query input and caller-selected learner facts fail closed.
- The browser action must reconstruct source selectors from the freshly opened
  candidate, not trust hidden source digests or origin facts. One or more safe
  candidate resources may be associated with each exact milestone; missing,
  duplicate, unknown, cross-candidate, or stale selections reach bounded local
  input guidance or the authoritative server refusal without side effects.
- A retry after an uncertain outcome reuses the identical submission identity
  and prepared selections. A deliberate corrected attempt may create a new
  identity; the browser never rewrites accepted evidence.

## Dependencies and Parallel Safety

WRK-0127 must remain complete. This packet is not parallel-safe with another
SLI-0032 packet because it owns the shared Project routes, API schema, generated
client, and focused browser tests. JIT-E depends on this exact browser/public-
completion contract. No lower-level approval is required because the packet is
inside the current approved CAP-0007 package and SLI-0032 boundary.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Eligible checkpoint | A learning-started Project has one closed checkpoint | The learner opens its submission route | Exact milestones and safe checkpoint records appear; origin/checkpoint facts correlate | API/component/Chromium |
| Independent denial | A Project has independent origin | Its checkpoint is viewed | No learning-submit action is offered and direct route opening fails safely | component/API/Chromium |
| Complete submit | Every milestone has admitted retained evidence | The learner submits | The generated client posts one exact intent and immutable evidence/history/completion appear | API/component/Chromium |
| Correct refusal | A mapping is missing, duplicate, unknown, or stale | Submit returns bounded issues | The summary and fields identify safe corrections, preserve admissible choices, focus the first problem, and create no accepted completion | unit/component/API |
| Exact retry | The first response is uncertain | The learner retries unchanged data | The same submission identity/document is reused and only one accepted occurrence exists | unit/component |
| Retained history | Multiple accepted checkpoints exist | The route reloads | Ordered immutable entries, exact provenance, mappings, and supersession remain reopenable | model/component |
| Derived completion | Accepted evidence exists | The completion route is read | Audit reconciliation and Learner-model rebuild produce bounded activity completion without mastery | API/generated client |
| Authorization/privacy | Session or ownership is absent or identities are guessed | Routes are called | Confidential bounded failure occurs without partial Project/Assessment facts | API/browser/security |
| Unsafe response | A success body has an extra/private/malformed/uncorrelated field | Loader validates it | The page fails closed and renders no partial record | unit/component |
| Flexible shape | Valid candidate/history shapes vary in counts, order, Unicode, optional provenance, IDs, and timestamps | They are rendered and submitted | No fixture-specific limit or styling assumption blocks valid work | unit/component/Chromium |
| Accessible parity | The flow is used by keyboard, narrow viewport, zoom/reflow, forced colors, reduced motion, and both themes | The learner reviews, corrects, submits, and reopens | Equivalent content, actions, focus, and status meaning remain available | Chromium/design |
| No execution/advice | Checkpoint resources include inert files or financial context | They are selected or reopened | No content executes/renders actively and no quality, mastery, advice, or performance claim appears | component/security/language |

## Verification Commands

Run focused protected API tests with the isolated PostgreSQL DSN when required,
then:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/api/test_single_profile_project_submission_api.py
backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run apps/web/tests/unit/projectWorkspaceModel.test.ts apps/web/tests/component/projectWorkspace.test.tsx
npm --prefix apps/web run test:browser -- tests/browser/project-workspace
npm --prefix apps/web run build
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python dev-tools/design/check_design_system.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0128-deliver-project-learning-submission-browser-flow.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Generate reviewed artifacts before their `--check` commands. Submit one clean
exact candidate, record a fresh affected-check receipt, and obtain independent
technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document the protected completion route, generated-client/headless parity,
candidate-to-intent reconstruction, safe runtime closure checks, refusal and
retry behavior, retained evidence/history, completion meaning, accessibility,
no-execution/no-advice boundary, tests, exact candidate/receipt, assumptions,
and remaining JIT-E qualification. Store approval and reviewer records only in
ignored local control-plane storage.

## Stop Conditions

Stop for a breaking Project/Assessment contract change; new identity,
authorization, completion, validation, grading, mastery, AI, provider,
tenancy, commercial, recovery, queue, or execution authority; cross-module
persistence access; mutable accepted evidence/checkpoints; unsafe/private
response content; generated-client drift that requires a new external shape;
dependency or lockfile change; active file collision; conflicting canonical
source; or material CAP-0007/SLI-0032 drift.

Do not stop or reopen review for harmless whitespace, optional wording, or
nonfunctional early-stage styling. Correct it in scope or defer it to CAP-0031.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0128`; exact candidate and receipt; protected
completion and generated-client contracts; candidate/form/intent correlation;
refusal, replay, retained-history, completion, authorization, privacy, unsafe-
response, accessibility, anti-rigidity, no-execution, and headless evidence;
focused, architecture, security, design, planning, documentation, aggregate,
and independent-review results; documentation impact; assumptions; and
residual JIT-E gaps. Confirm no persistence, schema meaning, AI authority,
provider, queue, or external execution changed.

## Planning History

- 2026-10-17: Authored after WRK-0127 completed. The missing protected
  Learner-model completion read and the accessible generated-client flow form
  one reviewable learner outcome inside the approved CAP-0007/SLI-0032 package;
  no durable decision or lower-level approval gate was introduced.
