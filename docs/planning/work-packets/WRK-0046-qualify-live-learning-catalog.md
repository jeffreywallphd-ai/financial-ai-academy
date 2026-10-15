---
id: WRK-0046
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0018
capability: CAP-0004
depends_on: ["WRK-0045"]
decision_gates: []
parallel_safe_with: []
write_scope: ["deployments/local/serve.py", "deployments/local/README.md", "tests/e2e/approved-lesson/run.py", "tests/architecture/test_approved_lesson_boundaries.py", "apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/dist", "apps/web/README.md", "backend/src/financial_ai_academy/bootstrap/README.md", "docs/architecture/contracts/discovery-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0018-browse-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0046-qualify-live-learning-catalog.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Live Learning Catalog

## Objective and Deliverable

Compose the accepted discovery registration and projection rebuild into the
isolated local fixture, then qualify the complete learner path from a clean
PostgreSQL 18.4 database through the same-origin Python/static application and
pinned Chromium. The observable result is a fresh `/learn` catalog containing
one exact approved opportunity whose action opens the already qualified lesson,
with deterministic cleanup and no external search or Node application process.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the deployment-operations and
testing-quality context packs; read the change-impact matrix, decision
readiness, planning/concurrency guidance, CAP-0004, SLI-0018, WRK-0045,
ADR-0005, ADR-0006, ADR-0007, ADR-0009, the discovery and identity contracts,
local deployment guide, bootstrap and web READMEs, Curriculum public discovery
operations, local composition, cross-system runner, live browser tests,
architecture checks, assurance map, known verification gaps, and the nearest
affected tests and documentation.

## Decisions and Assumptions

The accepted local profile remains one loopback Python API/static process over
PostgreSQL and restrictive filesystem storage; Node remains build/test tooling.
The explicit synthetic-fixture flag may register one exact approved lesson
opportunity and synchronously rebuild its derived projection through public
Curriculum operations before the host starts accepting requests. This is
deterministic qualification seeding, not a production scheduler or mutation
API. The exact same discovery and generated-client contracts already delivered
by WRK-0043 through WRK-0045 remain unchanged.

## In Scope

- Extend explicit approved-fixture seeding to register a bounded available
  lesson classification and rebuild the Curriculum-owned discovery projection
  only after the exact Content package and Curriculum placement exist.
- Preserve replay safety through existing immutable registration and atomic
  projection operations; a failed seed/rebuild must stop startup rather than
  serve a fabricated or partial catalog.
- Build and retain the final reviewed static application artifacts used by the
  Python host for this slice.
- Extend the live Chromium path to open `/learn`, verify exact classification,
  version/provenance, availability meaning, and educational limitations, then
  follow the exact catalog action into the existing lesson/assessment path.
- Prove catalog authorization denial without a session and retain the existing
  missing-placement, security-header, opaque-cookie, completion-reopen, advice
  boundary, and axe evidence.
- Keep the isolated runner's unique PostgreSQL container, temporary filesystem,
  dynamic ports, bounded diagnostics, and exact-resource cleanup behavior.
- Update deployment, bootstrap, web, discovery, assurance, slice, packet, and
  register documentation with direct evidence and remaining unqualified scope.

## Out of Scope

Background or periodic rebuild jobs, public rebuild/registration endpoints,
search/filter/sort parameters, pagination, stale-serving policy, multiple
fixtures, non-lesson execution, external search, provider ingestion, learner
personalization, enrollment/eligibility, production startup seeding, queue
selection, remote/public binding, managed-cloud deployment, multi-browser
qualification, backup/recovery, or any new domain/API/browser contract.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Local fixture composition | Curriculum public operations, existing seed sequence, bootstrap boundary | `deployments/local/serve.py`, bootstrap README | Register and rebuild only through accepted application operations |
| Live qualification | Cross-system runner, Playwright configuration, approved-lesson scenario | Runner and approved-lesson live test | Prove the clean same-origin catalog-to-lesson path and cleanup |
| Static artifact | Current Vite source and tracked production bundle | `apps/web/dist` generated output only | Bind live evidence to the final WRK-0045 browser implementation |
| Architecture evidence | Existing local-composition fitness checks | Listed architecture test and assurance map | Prevent Node/external-search or private-repository shortcuts |
| Documentation and lifecycle | Deployment/web/discovery/known-gap docs, slice, packet, register | Listed documentation and planning files | Record exact direct coverage and remaining limits |

## Contracts and Interfaces

WRK-0046 consumes the exact accepted package, placement, discovery
classification, atomic rebuild, protected browse, generated client, and browser
validation seams. The fixture supplies one stable opportunity identity equal to
the existing placement identity, bounded Curriculum-owned catalog metadata, and
`available` status; Content remains authoritative for title, objectives,
version, digest, and provenance. The only output to later slices is a directly
qualified local browse baseline and retained static bundle. No public schema,
HTTP operation, generated client, permission, or production scheduling contract
changes.

## Dependencies and Parallel Safety

WRK-0045 is complete and supplies the reviewed catalog route. This packet owns
the final static bundle, local seed composition, shared live runner, and SLI-0018
closure evidence, so no other SLI-0018 packet may run concurrently. Its scope
does not authorize SLI-0019 query semantics or SLI-0020 detail/comparison work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Clean live browse | Empty PostgreSQL and filesystem roots plus the explicit approved-fixture flag | The local host starts and `/learn` opens | One exact approved card appears from the rebuilt projection with version, provenance, availability reason, and educational boundary | PostgreSQL/Python/Chromium |
| Exact continuation | The approved catalog card is visible | Its lesson action is followed | The existing exact placement opens without substitution and the assessment/completion path remains usable | live Chromium |
| Context denial | No opaque session cookie exists | The protected catalog API is requested | It returns bounded unauthorized output without record, learner, or provider detail | live HTTP/Chromium |
| Seed or rebuild failure | Registration or projection replacement fails | Explicit fixture startup runs | Startup fails; no partial catalog is served | focused composition test/operation behavior |
| Portable topology | The live runner inspects its environment | Qualification runs and cleans up | Only Python, PostgreSQL, static files, and the isolated filesystem are application resources; no external search or Node server is required | architecture/runner evidence |
| Interface integrity | Live catalog and continued lesson render | Axe and semantic assertions run | Content, actions, provenance, and limitations remain accessible and non-advisory | live Chromium/axe |
| Static boundary | Vite production output is rebuilt | Python serves the reviewed bundle | Only expected browser artifacts are present and the SPA/catalog route resolves from the same origin | build/architecture/live |

## Verification Commands

Run the work-packet validator, planning checks, claim/start controls, focused
architecture and live-browser checks, `npm --prefix apps/web run build`, and
`backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py` against its
isolated Docker-managed PostgreSQL 18.4 container. Also run the complete web
unit/component and affected browser suites; backend unit/contract/architecture
tests; OpenAPI/generated-client currency; TypeScript and lint; security,
design-system, documentation, planning, dependency, static-boundary, and diff
checks; affected control-plane verification; and
`python dev-tools/agent/check_ready.py`. Docker qualification is mandatory; an
unavailable host is an environmental blocker rather than evidence.

## Documentation and Evidence Update

Update the local deployment, bootstrap, web, discovery-contract, architecture
verification, and known-gap documents only for behavior directly exercised.
Update this packet, SLI-0018, and the planning register together. Completion
evidence must identify the exact fixture registration/rebuild sequence, static
bundle, clean database/runtime path, catalog-to-lesson assertions, denial and
cleanup results, checks, unsupported profiles, and residual gaps. Do not place
approval or reviewer records in tracked artifacts.

## Stop Conditions

Stop if the work requires changing discovery v1 or generated API shapes;
introducing a queue, scheduler, external search, new provider, or public
mutation; seeding without the explicit local fixture flag; using private module
internals or cross-module persistence; serving a partial projection after
failure; adding learner/ranking/eligibility authority; weakening loopback,
cookie, security-header, cleanup, or exact-version guarantees; overlapping an
active file lease; or materially changing CAP-0004/SLI-0018 outcome, ordering,
risk, or decision posture.

## Required Handoff

Report the fixture classification and rebuild result; exact live catalog and
lesson path; static artifact result; PostgreSQL, Python, filesystem, browser,
denial, accessibility, security-header, completion-reopen, and cleanup evidence;
all checks and results; documentation impact; unsupported profiles and residual
gaps; packet and slice lifecycle results; and whether SLI-0019 is ready for
just-in-time refinement.

## Planning History

- 2026-10-15: Authored just in time after WRK-0045 completion. The packet uses
  existing public discovery operations and the accepted local qualification
  topology, adds no durable decision, and remains within the approved
  SLI-0018 outcome.
