---
id: WRK-0051
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0019
capability: CAP-0004
depends_on: ["WRK-0050"]
decision_gates: []
parallel_safe_with: []
write_scope: ["deployments/local/serve.py", "deployments/local/README.md", "tests/e2e/approved-lesson/run.py", "tests/architecture/test_approved_lesson_boundaries.py", "apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/dist", "apps/web/README.md", "backend/README.md", "backend/src/financial_ai_academy/bootstrap/README.md", "backend/src/financial_ai_academy/modules/curriculum/README.md", "docs/architecture/contracts/discovery-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0019-query-approved-learning-opportunities.md", "docs/planning/work-packets/WRK-0051-qualify-live-discovery-query-path.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: e23ae3daf036c53472ef8998b3ecfe25bb651c91
claim_id: WRK-0051:5e3c3f29-d39c-4526-b187-f7304a226e2b
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T20:35:57Z
---

# Agent Work Packet: Qualify the Live Discovery Query Path

## Objective and Deliverable

Qualify the completed discovery query slice through a clean isolated
PostgreSQL 18.4 database, the same-origin Python/static application, restrictive
filesystem storage, and pinned Chromium. Deliver deterministic live evidence
for combined filters, stable ordering, multi-page continuation, query-bound
cursor-mismatch denial, authorization confidentiality, accessibility, portable
topology, and exact-resource cleanup without introducing a search provider,
background job, production seed, or new public contract.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through deployment-operations, API/security, interface, testing-quality, and
delivery-planning context; read the change-impact matrix, decision readiness,
planning/concurrency guidance, CAP-0004, SLI-0019, completed WRK-0048 through
WRK-0050, the discovery/query and Identity contracts, local deployment,
bootstrap, Curriculum, backend, and web READMEs, current fixture composition,
cross-system runner, live Chromium scenarios, architecture checks, assurance
map, known gaps, and nearest affected tests.

## Decisions and Assumptions

The accepted topology remains one loopback Python API/static process over
PostgreSQL and isolated filesystem storage; Node remains build/test tooling.
The existing approved lesson seed remains unchanged by default. A separate
explicit query-qualification flag may add a small bounded set of synthetic
Curriculum classifications against the already accepted exact placement, then
perform one atomic projection rebuild before readiness. This optional flag is
test-fixture composition, not a production scheduler, mutation API, provider,
or required workflow for ordinary local startup.

## In Scope

- Add an explicit, bounded query-qualification fixture option that requires the
  approved fixture, registers deterministic additional classifications only
  through the public Curriculum facade, and performs one atomic projection
  rebuild after all registrations.
- Preserve the current one-opportunity approved seed when the query option is
  absent. Reject incompatible flag combinations before service readiness, and
  stop startup on registration or rebuild failure rather than serving partial
  query data.
- Retain the reviewed static build used by the Python host and make the live
  runner identify the opt-in query corpus and exact static artifact digest.
- Exercise the live `/learn` controls and protected query API for a combined
  filter, deterministic duration order, page size one across multiple pages,
  no duplicate or omitted opportunity identities, exact total/applied state,
  and a query-mismatched cursor that produces the bounded invalid-query state without
  fallback records.
- Remove redundant nested region labels so repeated classifications of one
  exact lesson retain heading/list semantics without creating duplicate named
  landmarks.
- Prove no-session query denial, no record/count/cursor disclosure, existing
  cookie/security headers, exact lesson continuation, axe coverage, and
  deterministic teardown of only the unique container and temporary data root.
- Add focused architecture/composition regressions for opt-in behavior,
  public-operation order, fail-closed flag/rebuild behavior, topology limits,
  and the anti-rigidity guarantee that ordinary approved-fixture startup does
  not require the larger query corpus.
- Reconcile directly affected deployment, backend/web, Curriculum, discovery,
  assurance, known-gap, slice, packet, and register documentation.

## Out of Scope

Changing query-v1 or discovery-v1 semantics; API/OpenAPI/generated-client or
browser-source changes beyond the narrow accessibility correction above;
production fixture or automatic rebuild behavior;
background/periodic jobs; external or embedded search; new provider, queue,
cache, crawler, migration, dependency, or public mutation; personalized
ranking, recommendation, eligibility, enrollment, detail/comparison; remote
binding, cloud/tenant deployment, non-Chromium qualification, or backup and
recovery claims.

## Expected File and Boundary Impact

| Area | Allowed change | Boundary |
| --- | --- | --- |
| Local qualification composition | `deployments/local/serve.py` | Explicit synthetic flag and public Curriculum operations only |
| Live evidence | shared runner and approved-lesson Playwright scenario | PostgreSQL/Python/static/Chromium query behavior and cleanup |
| Browser accessibility | learning-catalog page only | Remove redundant nested landmark names; preserve content, headings, lists, and actions |
| Architecture evidence | listed architecture test | Optionality, public seams, fail-closed ordering, no extra runtime |
| Generated static artifact | `apps/web/dist` only | Rebuild the already reviewed WRK-0050 interface without source drift |
| Documentation/lifecycle | listed README, contract, assurance, SLI, packet, register files | Record direct coverage and residual limits only |

## Contracts and Interfaces

The packet consumes the accepted `RegisterLessonOpportunityRequest`, one atomic
`RebuildLearningOpportunityProjectionRequest`, protected
`GET /api/v1/curriculum/opportunities/query`, generated TypeScript client, and
URL-backed `/learn` interface unchanged. Synthetic opportunity identities and
classification facts are fixed qualification inputs. The browser treats the
cursor as opaque; query mismatch is produced by changing a public query
parameter, never by decoding or rewriting cursor payload fields.

## Dependencies and Parallel Safety

WRK-0050 is complete and supplies the final interface and static source. This
packet owns the shared local seed composition, live runner/scenario, final
static bundle, assurance evidence, and SLI-0019 closure files, so it is not
parallel-safe with another packet touching those seams.

## Acceptance Scenarios

| Scenario | Required outcome |
| --- | --- |
| Optional corpus | Approved-fixture startup without the query flag retains one opportunity; the query flag adds only the fixed bounded corpus and one final rebuild |
| Combined query | Live controls/API echo canonical filters and return the exact matching classification without recommendations or learner signals |
| Multi-page order | Page size one traverses every result once in deterministic duration order with a stable total and opaque continuation links |
| Mismatched cursor | Reusing a server cursor with changed query facts returns contract-defined bounded `invalid_query`; the UI offers a clear-query recovery and renders no fallback records |
| Context denial | No-session query requests disclose no records, count, cursor, learner, session, provider, or storage detail |
| Exact continuation | The available exact lesson action still opens the reviewed placement and retained learning path |
| Accessibility/security | Live query controls, results, failures, cookie posture, security headers, and axe checks remain equivalent and operable |
| Portable cleanup | Only PostgreSQL, Python, static files, Chromium, and isolated filesystem resources participate; the unique container/data root are removed |
| Anti-rigidity | Ordinary local approved-fixture qualification remains usable without the expanded corpus or unrelated services/checks |

## Verification Commands

Run packet/planning/claim/start and lease controls; focused architecture and
composition tests; complete web unit/component tests; focused mocked and live
Chromium suites; generated-client currency; web typecheck, lint, build, static
boundary, and dependency checks; backend unit/contract/integration/architecture
suites; OpenAPI currency; security, design, documentation, planning, and diff
checks; the isolated Docker/PostgreSQL qualification through
`backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py`; affected
control-plane verification; independent technical review; and
`python dev-tools/agent/check_ready.py`. Docker qualification is mandatory; an
unavailable host is environmental failure, not completion evidence.

## Documentation and Evidence Update

Record the exact opt-in seed facts and operation order, first/filter/page/stale
and denial outcomes, static digest, topology, accessibility/security posture,
cleanup, focused and aggregate checks, unsupported profiles, and residual gaps.
Do not place local approval or reviewer records in tracked artifacts.

## Stop Conditions

Stop for changed public query/discovery meaning; production or implicit
seeding; private repository/module access; partial readiness after a fixture or
rebuild failure; browser cursor decoding; a provider/index/cache, queue/job,
migration, dependency, remote bind, secret, learner-selected authority,
personalization, recommendation, eligibility, or enrollment; weakened cookie,
header, loopback, cleanup, or exact-version guarantees; overlapping edit
scope; an unresolved durable decision; or material CAP/SLI outcome, order,
risk, or decision drift.

## Required Handoff

Report the opt-in corpus and public-operation order; exact combined filter,
sort, pagination, stale-cursor, denial, lesson-continuation, accessibility,
security-header, static, PostgreSQL, Python, filesystem, Chromium, and cleanup
results; every check; documentation impact; residual gaps; packet and slice
lifecycle; and CAP-0004 dependency readiness.

## Planning History

- 2026-10-15: Authored just in time after WRK-0050 completion. The packet
  reuses the accepted local qualification topology, adds only an explicit
  bounded synthetic query corpus, preserves ordinary one-fixture startup, and
  introduces no durable decision or material CAP drift.
- 2026-10-15: Live qualification exposed redundant repeated-card landmark
  names and confirmed query-v1's durable distinction between query mismatch
  (`invalid_query`) and projection-generation drift (`stale_cursor`). Scope was
  incrementally refined for the narrow accessibility correction and
  contract-aligned live evidence without changing the slice outcome.
