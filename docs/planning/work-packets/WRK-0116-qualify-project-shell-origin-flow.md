---
id: WRK-0116
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: SLI-0030
capability: CAP-0007
depends_on: [WRK-0111, WRK-0117]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0030-create-independent-or-learning-project.md", "docs/planning/work-packets/WRK-0116-qualify-project-shell-origin-flow.md"]
generated_artifacts: []
base_revision: 7ec80cd92eea9f11caf448fb85c0a190ddd7f573
claim_id: WRK-0116:241e03bb-c9cf-44f3-b29b-6c9cf7ca9391
claimed_by: codex-cap-0007
claimed_at: 2026-10-16T22:18:50Z
---

# Agent Work Packet: Qualify Project Shell and Origin Flow

## Objective and Deliverable

Trace every SLI-0030 acceptance scenario to current direct evidence, run the
minimum fresh cumulative qualification needed after WRK-0111, reconcile
assurance and known limits, and close SLI-0030 without changing product
behavior or overstating unsupported deployment, execution, or AI modes.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the delivery-planning, Project, API/security,
testing-quality, deployment-operations, and interface-design context; apply the
change-impact matrix and decision readiness; inspect CAP-0007, SLI-0030,
WRK-0109 through WRK-0111, ADR-0011, ADR-0012, Project workspace and public API
contracts, Project/Content/Curriculum implementations and public facades,
migrations, generated client, browser consumers, local composition, affected
tests, assurance sources, known gaps, and nearest READMEs.

## Decisions and Assumptions

Accepted inert-workspace, reusable-Project, single-learner identity,
module-owned PostgreSQL, generated-client, and static-browser decisions are
sufficient. Current exact-candidate receipts may be reused only where ancestry
and unchanged affected files keep them current. This packet adds no new
identity, tenancy, provider, execution, recovery, model-authority, or
commercial choice.

## In Scope

- Map each SLI-0030 acceptance scenario to direct current contract, domain,
  application, PostgreSQL, API, generated-client, browser, live, architecture,
  security, language, design, or documentation evidence.
- Run fresh cumulative qualification for independent and learning-origin
  creation, headless API use, idempotency, immutable provenance,
  authorization, safe source denial, absence of evidence side effects,
  accessible browser parity, restart persistence, and isolated cleanup.
- Reconcile architecture verification and known gaps only when current claims
  are stale; otherwise record that no assurance edit was needed.
- Complete WRK-0116 and SLI-0030 only after exact-candidate verification,
  completion structure, and aggregate readiness pass.

## Out of Scope

Any runtime, public-contract, schema, migration, generated-client, fixture,
browser, dependency, provider, identity, tenancy, artifact, snapshot,
submission, domain-link, Portfolio, execution, AI-mode, deployment, or
recovery behavior change. A functional gap returns this packet to shaping or
opens a separately bounded corrective packet instead of silently expanding
this evidence-only scope.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Slice evidence | SLI-0030 and completed WRK-0109 through WRK-0111 | SLI-0030, WRK-0116, register | Trace scenarios and close lifecycle without mutating the approved CAP package |
| Assurance | architecture verification and known gaps | listed assurance files only if reconciliation is necessary | Keep qualified and unsupported claims exact |
| Product and contracts | Project/Content/Curriculum, API, PostgreSQL, generated client, browser, local composition, tests | none | Qualification must observe the delivered boundary, not alter it |

## Contracts and Interfaces

Consume the unchanged learning-project brief, Curriculum placement, closed
Project origin, Project shell, protected Project HTTP operations, generated
TypeScript client, and local static-browser composition. Produce no new public
contract, schema, route, runtime interface, provider seam, or generated
artifact.

## Dependencies and Parallel Safety

WRK-0109 through WRK-0111 supply the exact contracts, implementation,
persistence, API, generated client, browser flow, and focused evidence.
WRK-0117 must also complete so the tracked production bundle is generated from
that accepted source. This packet owns shared slice/register closure sources
and is not parallel-safe with another SLI-0030 or Project qualification packet.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Independent and learning creation | both accepted origin types | authorized create and read/list operations run | stable active shells reopen with the correct immutable origin and no copied source bytes | contract/domain/API/PostgreSQL/browser/live |
| Headless parity | a supported non-browser caller | it uses the protected public Project operations | the same identity, authorization, validation, idempotency, and response shapes apply without browser state | API/client-usage/live |
| Retry and provenance | exact retries, conflicting keys, edits, and later source changes | create is repeated or recovered | exact intent is idempotent, changed intent uses a new key, and accepted origin never rewrites | domain/PostgreSQL/API/component/live |
| Safe denial | missing permission, guessed ownership, malformed input, or stale/unavailable source | read, option resolution, or create is attempted | failure is bounded and no shell, private fact, Assessment evidence, or Learner-model progress is created | application/API/security/live |
| Flexible and accessible use | varied valid copy, counts, ordering, viewport, input method, theme, and forced settings | list/create/detail flows run | behavior and meaning do not depend on one fixture or presentation and remain operable | unit/component/Chromium/design/language |
| Restart and containment | an isolated PostgreSQL/Python/static-browser topology | shells are created, services restart, and cleanup runs | state survives the normal restart and only exact isolated resources are removed | migration/live/cleanup evidence |
| Honest boundary | unsupported later Project capabilities and deployment profiles | slice evidence is reconciled | no artifact, snapshot, submission, Portfolio, execution, separate AI mode, managed-cloud, or production-recovery claim is made | slice/assurance/known-gap sources |

## Verification Commands

Run packet and planning validation; Project contract/domain/application and
protected API suites; real-PostgreSQL migration, persistence, isolation,
restart, idempotency, immutability, and evidence-non-effect checks selected by
the existing test topology; OpenAPI currency and generated-client reproduction;
TypeScript client-usage, focused Project unit/component/Chromium, complete web
unit/component, typecheck, lint, and production build; isolated live Project
qualification including a direct non-browser API observation and exact
cleanup; architecture, security, learner-language, design-system,
documentation, dependency, and whitespace checks; affected exact-candidate
verification; completion-structure validation; `python
dev-tools/agent/check_ready.py`; and the required independent technical check.
Use a repository-local temporary root on Windows where needed.

## Documentation and Evidence Update

Record a concise scenario-to-evidence trace, exact candidate and qualifying
receipt, environments and checks, headless/API parity, restart and cleanup,
unchanged runtime/contract boundaries, explicit non-effects, and residual
unsupported profiles in SLI-0030, WRK-0116, the register, and only assurance
sources that are actually stale. Keep approval and technical disposition data
only in ignored local storage and preserve CAP-0007 byte-for-byte.

## Stop Conditions

Stop for missing acceptance evidence; a product/control failure; stale or
contradictory canonical sources; any runtime fix outside the declared
evidence scope; a new identity, tenancy, licensing, model-authority, provider,
commercial, recovery, external-execution, or legal choice; overlapping active
scope; or material drift from the approved CAP-0007 package. Harmless
whitespace, optional wording, nonfunctional styling, and similar early-stage
polish do not trigger a new review loop; fix them locally where in scope or
defer them to CAP-0031.

## Required Handoff

Report the scenario-to-evidence trace, exact candidate and receipt, checks and
results, environments and cleanup, affected boundaries, documentation impact,
assumptions, residual limits, unresolved decisions, and SLI-0030 package
conformance. Confirm that no product behavior or later Project capability was
added.

## Planning History

- 2026-10-16: Authored just in time after WRK-0111 completed as the final
  evidence-only qualification packet for SLI-0030. It adds no runtime,
  contract, provider, execution, AI authority, or durable decision and remains
  inside the approved CAP-0007 package.
- 2026-10-16: Returned to ready after the first cumulative run proved the
  tracked production bundle was stale relative to the accepted browser source.
  WRK-0117 owns only that generated-artifact correction; already-passed
  product checks remain evidence for the unchanged source candidate.
