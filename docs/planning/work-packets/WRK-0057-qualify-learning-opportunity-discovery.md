---
id: WRK-0057
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0021
capability: CAP-0004
depends_on: ["WRK-0051", "WRK-0056"]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0021-qualify-learning-opportunity-discovery.md", "docs/planning/work-packets/WRK-0057-qualify-learning-opportunity-discovery.md"]
generated_artifacts: []
base_revision: 9ccd2061324ab4eb1133ee17652a943e3626cfc2
claim_id: WRK-0057:87315af5-5d47-4e89-9db7-8104bc99e4eb
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T21:25:24Z
---

# Agent Work Packet: Qualify Learning Opportunity Discovery

## Objective and Deliverable

Trace every CAP-0004 acceptance criterion to current direct evidence, run the
minimum fresh cumulative qualification required after SLI-0020, reconcile
assurance and known limits, and close SLI-0021 and CAP-0004 without changing
product behavior or overstating unsupported profiles.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through the delivery-planning, testing-quality, API/security,
deployment-operations, and interface-design context; apply the change-impact
matrix and decision readiness; inspect CAP-0004, all four slices, completed
packets WRK-0043 through WRK-0056, discovery/query contracts, owning and
consuming READMEs, assurance/known-gap sources, relevant tests, and local live
runner evidence.

## Decisions and Assumptions

The accepted Content/Curriculum ownership, discovery-v1 and query-v1 contracts,
single-profile protected API, static generated-client interface, and isolated
local topology are sufficient. Fresh WRK-0056 live evidence may be reused where
the exact candidate ancestry and unchanged affected files make it current; all
repository-level closure checks must still run against the final candidate.

## In Scope

- Map each CAP acceptance criterion to direct completed-slice evidence and note
  any residual limitation without inferring support.
- Reconcile projection rebuild, deterministic query, detail/comparison,
  authorization, exact continuation, accessibility, portability, and cleanup
  claims across current canonical documentation.
- Run focused cumulative checks where evidence freshness is required,
  affected verification, independent technical review, and the fixed aggregate
  readiness gate.
- Complete WRK-0057 and SLI-0021, and reconcile CAP-0004 lifecycle state in the
  register only after every acceptance criterion is directly supported.

## Out of Scope

Any runtime, contract, schema, generated-client, static asset, fixture,
migration, dependency, provider, identity, tenancy, search-ranking,
recommendation, commercial, enrollment, eligibility, progress, activity
execution, production deployment, or recovery behavior change.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Capability evidence | CAP-0004 and completed slices/packets | SLI-0021, WRK-0057, register | Trace criteria and close lifecycle without mutating the approved package |
| Assurance | architecture verification and known gaps | listed assurance files only if reconciliation requires it | Keep qualified and unsupported claims exact |
| Runtime/contracts/UI | all affected implementation, schemas, tests, generated outputs | none | Evidence-only closure must not alter product behavior |

## Contracts and Interfaces

Consumes unchanged discovery-v1, query-v1, protected browse/query operations,
generated client, detail/comparison route contracts, exact placement
destination, and local composition. Produces no new public contract or runtime
interface.

## Dependencies and Parallel Safety

All earlier CAP-0004 packets are complete. This packet owns shared capability,
slice, register, and assurance closure sources, so it is serial and not
parallel-safe.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Acceptance trace | all three delivery slices are complete | CAP criteria are reconciled | every criterion has direct current evidence or closure stops | CAP/slice/packet evidence |
| Cumulative behavior | unchanged final implementation | focused and live checks run | browse/query/detail/compare/exact continuation remain coherent | contract/backend/web/live checks |
| Closed failures | absent context or stale/malformed state | protected paths are exercised | no partial record, substitution, or confidential detail leaks | API/browser/live/security evidence |
| Portability | local isolated topology starts | qualification and cleanup complete | no external search or Node production server is required and no exact resource remains | live/architecture evidence |
| Anti-rigidity | optional richer corpus is absent | ordinary approved-fixture startup runs | basic local operation remains usable without test-only services or mandatory query fixtures | live startup evidence |
| Honest closure | unsupported profiles are reviewed | capability is closed | no external, cloud, non-lesson, non-Chromium, or manual-AT claim is made | assurance/known-gap docs |

## Verification Commands

Run planning and packet validation; direct contract/backend/web/architecture/
security/design checks selected by the acceptance trace; current generated
client, typecheck, lint, production build, dependency, documentation, and diff
checks; isolated live qualification where freshness is required; affected
control-plane verification; independent technical review; and
`python dev-tools/agent/check_ready.py` against the final candidate.

## Documentation and Evidence Update

Record a concise criterion-to-evidence trace, exact environment/check results,
cleanup, unchanged contract/runtime boundaries, and residual unsupported
profiles in SLI-0021, WRK-0057, the register, and only the assurance sources
that are actually stale. Preserve the approved CAP artifact byte-for-byte and
keep all approval/reviewer records local.

## Stop Conditions

Stop for missing criterion evidence; a product/control failure; stale or
contradictory canonical sources; any runtime fix outside declared evidence
scope; a new provider, identity, tenancy, licensing, model-authority,
commercial, recovery, or execution decision; overlapping active scope; or a
material change to the approved CAP outcome or manifest.

## Required Handoff

Report the acceptance trace, exact checks and results, environments and cleanup,
affected boundaries, documentation impact, assumptions, residual limits,
unresolved decisions, and CAP-package conformance.

## Qualification Evidence

- All eight CAP-0004 criteria map directly to completed SLI-0018, SLI-0019,
  and SLI-0020 contract, deterministic-policy, PostgreSQL, protected API,
  generated-client, component, Chromium, live-topology, architecture,
  security, design, and documentation evidence. The complete trace is recorded
  in SLI-0021 without modifying the approved CAP artifact.
- Runtime files are unchanged from corrected WRK-0056 candidate
  `7f8c7f0decb8cfb20eca9126244045abd438fe60`. Its five-scenario disposable
  PostgreSQL 18.4/Python/static/filesystem/Chromium run and exact cleanup remain
  current by ancestry; only planning evidence changed afterward.
- Fresh cumulative checks passed 13 architecture tests, 93 web tests and the
  generated-client check, TypeScript typecheck and lint, ten security control
  groups, design validation for 125 tokens and 56 icons, planning integrity for
  125 artifacts, documentation validation for 250 Markdown files, Git
  whitespace checks, and all 27 fixed aggregate readiness checks.
- Ordinary approved-fixture startup remains independent of the optional richer
  query corpus, and inspection/comparison adds no saved state or service. This
  retains the anti-rigidity guarantee proved by the architecture and live
  evidence.
- Architecture verification and known gaps were already exact, so neither
  needed a content edit. External search, managed cloud, broader identity,
  non-lesson execution, production rebuild scheduling, non-Chromium browsers,
  manual screen readers, and actual browser zoom remain unsupported.

## Planning History

- 2026-10-15: Authored just in time after SLI-0020 completion as one
  evidence-only cumulative qualification packet. The packet adds no runtime,
  contract, provider, or durable decision and stays within the approved
  CAP-0004 package.
- 2026-10-15: Claimed for serial cumulative qualification after every delivery
  dependency completed. The exact scope excludes runtime and the approved CAP
  package itself.
- 2026-10-15: Prepared the planning-only cumulative qualification candidate
  after all capability criteria had direct evidence and focused plus aggregate
  gates passed. Assurance sources required no reconciliation edit.
