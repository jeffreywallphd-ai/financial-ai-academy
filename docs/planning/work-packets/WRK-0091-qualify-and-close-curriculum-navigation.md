---
id: WRK-0091
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0025
capability: CAP-0005
depends_on: ["WRK-0090"]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/planning/capabilities/CAP-0005-navigate-competency-based-curriculum.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0025-qualify-complete-curriculum-navigation.md", "docs/planning/work-packets/WRK-0091-qualify-and-close-curriculum-navigation.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify and Close Curriculum Navigation

## Objective and Deliverable

Run the cumulative CAP-0005 qualification matrix against the completed exact-
version curriculum-navigation path, map every capability acceptance statement
to direct evidence, and reconcile the public planning artifacts so SLI-0025
and CAP-0005 can close without changing product behavior. API availability for
browser, command-line, service, and future headless AI clients is a first-class
acceptance condition; planning or implementing a separate AI mode is not part
of this packet.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, testing-quality, security-risk, interface-design, and
delivery-planning context packs. Read the change-impact matrix, decision
readiness, CAP-0005, SLI-0022 through SLI-0025, WRK-0090, ADR-0004, ADR-0005,
ADR-0014, the Curriculum graph, Navigation-state, and activity-launch
contracts, affected API and generated-client checks, live approved-lesson
qualification, concurrent-work rules, and the nearest testing and deployment
READMEs.

## Decisions and Assumptions

- The versioned public application API remains the product boundary. The web
  application is one generated-client consumer; a non-browser client must be
  able to establish the supported session and complete the observable graph,
  Navigation-state, and activity-launch path without browser-only authority.
- WRK-0090 supplies the isolated headless restart/replay observation. This
  packet consumes that evidence and reruns cumulative checks; it does not add a
  meta-runner, new product route, or duplicate live scenario.
- Existing CAP-0005 approval and the selected SLI-0025 manifest govern this
  bounded closure packet. No unresolved durable decision is activated.
- A separate AI runtime, agent protocol, model provider, tool interface, or
  adaptive recommendation plan remains deferred. Preserving API seams does not
  imply autonomous execution authority.

## In Scope

- Run focused Curriculum, Learner-model, Adaptation, Assessment, session,
  Navigation-state, activity-launch, generated-client, browser, accessibility,
  security, architecture, documentation, planning, build, and aggregate
  readiness checks that cover CAP-0005.
- Run the isolated approved-lesson qualifier, including its public-API-only
  headless observation, browser journey, restart, projection rebuild, source
  preservation, and exact cleanup behavior.
- Verify the reviewed OpenAPI snapshot and generated TypeScript client remain
  current and that no browser-only product operation is required for the
  supported navigation path.
- Record a concise evidence matrix for every CAP acceptance statement,
  including exact API/headless evidence, shared-core boundaries, assumptions,
  residual risks, and deliberately unqualified areas.
- Reconcile WRK-0091, SLI-0025, CAP-0005, and the planning register for the
  verification and completion lifecycle.

## Out of Scope

Any product domain, application, API, OpenAPI, generated-client, UI, database,
migration, dependency, fixture, deployment, or provider behavior change; a
separate headless AI mode or its plan; agent protocol, model provider, tool-
calling contract, recommendation, ranking, mastery, or automatic selection;
managed-cloud qualification, tenancy, external execution, or production
availability claims; and styling-only or other nonfunctional cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Capability evidence | CAP-0005 acceptance and completed slice evidence | CAP-0005 plan | Map each accepted outcome to direct cumulative evidence and residual boundaries |
| Slice closure | SLI-0025 acceptance, packet status, and qualification results | SLI-0025 plan | Record final evidence and lifecycle state |
| Packet evidence | commands, exact candidate, receipt, and review disposition | this packet | Make the bounded closure auditable |
| Portfolio state | CAP, slice, and packet public lifecycle | planning register | Keep work order and completion state synchronized |

No product source, executable contract, generated client, interface, schema,
migration, dependency, design-system asset, or deployment composition may
change.

## Contracts and Interfaces

Qualification must preserve and exercise the existing session,
`curriculum-graph-v1`, `adaptation-navigation-state-v1`, and
`activity-launch-v1` public operations. The headless route uses only public
HTTP plus the server-issued HttpOnly session cookie. The browser continues to
use the generated public client. Neither client may choose learner identity,
permission, eligibility, state, destination, completion, or policy result.

The evidence matrix may cite stable routes, contract identifiers, exact test
commands, and redacted result counts. It must not copy private learner data,
answers, credentials, provider payloads, approval records, or reviewer identity
into tracked files.

## Dependencies and Parallel Safety

WRK-0090 is complete and supplies the final live restart/replay evidence. This
packet owns the shared CAP, slice, and register artifacts and is therefore not
parallel-safe with another packet that changes CAP-0005 planning state. It must
complete before SLI-0025 and CAP-0005 are closed and before local `main` is
fast-forwarded.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Public headless path | The normal local composition is running | A fresh non-browser HTTP client establishes a supported session and reads graph, Navigation state, and eligible launch | Exact authorized results are available without UI state or backend-internal imports | isolated approved-lesson report and focused orchestration tests |
| Browser as API client | The reviewed OpenAPI and generated client are current | The complete learner browser journey runs | Browser behavior consumes the same authoritative operations and cannot bypass server policy | generated-client checks and Chromium qualification |
| Complete CAP matrix | SLI-0022 through SLI-0025 evidence is present | Cumulative qualification runs | Every CAP acceptance statement maps to a passing direct check or an explicitly bounded non-goal | recorded capability evidence matrix |
| Shared core | Local composition and provider-neutral core are inspected | Architecture checks run | No local/cloud domain fork or provider-specific payload enters the core | architecture/import-boundary checks |
| API drift | The executable OpenAPI or generated client differs from reviewed sources | Contract checks run | Qualification fails rather than closing the CAP | snapshot and generation checks |
| Nonfunctional noise | Harmless whitespace, optional styling, or evidence wording needs a bounded correction | Closure is prepared | It is fixed locally or deferred to CAP-0031 without reopening substantive review | planning and diff checks |

## Verification Commands

Run the repository commands that cover:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests
backend/.venv/Scripts/python.exe -m pytest tests/e2e/approved-lesson/test_replay_qualification.py
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run build
python dev-tools/contracts/check_openapi.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_security.py
python dev-tools/design/check_design_system.py
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Resolve exact supported script names from the repository before execution; do
not invent or permanently add a wrapper merely to match this list. Use the
documented prepared Node/npm environment where required. Submit one exact
candidate, generate a fresh affected-verification receipt, and obtain one
independent technical review. The live Docker/PostgreSQL/Chromium qualifier is
the authoritative composed-system check.

## Documentation and Evidence Update

Record the exact commands and results, exact candidate and receipt digest,
independent-review disposition, API/headless path, acceptance-to-evidence map,
affected boundaries, assumptions, known gaps, and documentation impact in this
packet, SLI-0025, and CAP-0005. Keep approval and reviewer records only in the
ignored local ledger. Do not claim a separate AI mode, managed cloud profile,
model authority, or production recovery guarantee.

## Stop Conditions

Stop for a failed functional, contract, authorization, privacy, provenance,
security, accessibility, architecture, build, API-snapshot, or live end-to-end
check that cannot be corrected inside this packet's documentation-only write
scope; conflicting canonical authority; material CAP-package drift; an
unresolved identity, tenancy, provider, model-authority, external-execution,
or legal/commercial choice; active write-scope collision; or inability to
prove the live database and cleanup are isolated.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional wording, or another inconsequential issue. Fix it locally or
defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; cumulative check matrix and results; public API and
headless-client evidence; OpenAPI/generated-client status; live restart/replay
result; affected boundaries; documentation impact; receipt and independent-
review disposition; assumptions; residual risks; and deliberately deferred AI,
cloud, and styling scope. Confirm whether SLI-0025 and CAP-0005 meet their
acceptance sets and are ready for deterministic closure and main fast-forward.

## Planning History

- 2026-10-16: Authored just in time after WRK-0090 completed. The packet makes
  public API availability and a non-browser headless path explicit in CAP
  closure while leaving a distinct AI mode and its planning deferred.
