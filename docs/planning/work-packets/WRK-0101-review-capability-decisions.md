---
id: WRK-0101
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-roadmap-decision-review
updated: 2026-10-16
parent: SLI-0036
capability: CAP-0008
depends_on: ["WRK-0026", "WRK-0084"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/financial_academy_roadmap_review.py", "dev-tools/control-plane/roadmap_review.py", "dev-tools/control-plane/test_roadmap_review.py", "dev-tools/control-plane/README.md", "dev-tools/roadmap-review-site/README.md", "dev-tools/roadmap-review-site/server.py", "dev-tools/roadmap-review-site/test_server.py", "dev-tools/roadmap-review-site/test_qualification.py", "dev-tools/roadmap-review-site/src/app.ts", "dev-tools/roadmap-review-site/src/model.ts", "dev-tools/roadmap-review-site/tests/app.test.ts", "dev-tools/roadmap-review-site/tests/model.test.ts", "apps/web/tests/browser/roadmap-review/roadmap-review.e2e.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0036-navigate-capability-slice-and-work-plans.md", "docs/planning/work-packets/WRK-0101-review-capability-decisions.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js", "artifacts/playwright/roadmap-review"]
base_revision: b530b6d9163067c15a88e6daf0706ce04bc3a538
claim_id: WRK-0101:0a6dbc5c-9985-44df-803c-dbd931402515
claimed_by: codex-roadmap-decision-review
claimed_at: 2026-10-16T16:53:47Z
---

# Agent Work Packet: Review Capability Decisions

## Objective and Deliverable

Extend the dynamic roadmap review so a repository operator can follow relevant
decision links from CAP, SLI, and WRK pages, see each decision's current public
status next to the link, and open one dynamically projected, inert DEC detail
page that explains the request and whether its public lifecycle records a
decision.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning, interface,
and testing context, CAP-0008, SLI-0034 through SLI-0037, WRK-0024, WRK-0026,
WRK-0080 through WRK-0084, the planning and decision-request guides, decision
readiness, the projector/adapter/server/client and focused tests, design and
language standards, and the nearest READMEs before editing.

## Decisions and Assumptions

- Decision requests remain non-authoritative planning artifacts. The site
  projects public DEC lifecycle and canonical-record metadata only; it never
  reads or exposes the ignored approval/reviewer ledger.
- `decision_made` is true only when the public DEC artifact is `complete`.
  A captured, shaping, active, verifying, decision-blocked, or superseded DEC
  does not claim an approved outcome.
- A `complete` DEC may have no separate `decision_record` when the DEC and
  synchronized canonical planning guidance are themselves the durable record.
  The page states that absence rather than inventing an ADR link.
- A slice inherits relevant decisions from its CAP; a work packet inherits the
  deduplicated CAP and SLI set in addition to any directly declared gates.
- Missing referenced DEC artifacts produce a local, non-blocking missing state
  and diagnostic. They do not break unrelated roadmap pages or synthesize a
  detail page.

## In Scope

Additive DEC projection from structured decision-request frontmatter and public
plan text; status and decision-made fields; optional confined canonical-record
paths; dynamic relevant-decision links on CAP/SLI/WRK pages; stable
`/decision/<id>` routes; inherited and deduplicated relevance; inert DEC
details; useful deferred, resolved, missing, and no-record states; source
fingerprinting; focused projection, API, DOM, route, browser, accessibility,
privacy, confinement, freshness, and anti-rigidity tests; operator guidance.

## Out of Scope

Approval or reviewer identity/history, local-ledger reads, decision mutation,
recording or accepting a decision, arbitrary ADR/file browsing, active Markdown,
external links inferred from prose, CAP/SLI/WRK lifecycle changes, static DEC
pages, hosted access, new decision semantics, or any second user-requested
change that was not described.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Repository adapter | Planning artifact loader and public metadata mapping | `financial_academy_roadmap_review.py` and focused tests | Supply DEC artifacts without adding them to executable portfolio allocation |
| Generic projection | Inert documents, node hierarchy, diagnostics and fingerprint | `roadmap_review.py` and focused tests | Publish vocabulary-neutral decision summaries and bounded missing-reference facts |
| Loopback host | Fixed detail-route allowlist and server checks | Exact server/test files | Serve only validated DEC IDs through the existing shell |
| Typed interface | Model validation, route resolution, CAP/SLI/WRK details, DEC page | Exact TypeScript source/tests | Render status-bearing links and dynamic inert details |
| Qualification | Browser and dependency-free source contracts | Exact browser/qualification files | Prove dynamic, accessible, privacy-preserving behavior without broadening fixed readiness |
| Documentation/planning | Operator guides, SLI packet table/evidence, register and packet | Exact named files | Keep the extension, commands and lifecycle synchronized |

## Contracts and Interfaces

`roadmap-review-v1` gains an additive `decisions` array. Each entry contains
public planning ID, lifecycle status, title, confined source, dependencies,
optional confined `decision_record`, derived `decision_made`, and an inert
document. Existing node `decision_gates` remain the relevance source. The
typed client retains all existing routes and adds only
`/decision/<validated-id>`.

## Dependencies and Parallel Safety

WRK-0026 and WRK-0084 are complete. This packet owns the shared roadmap
projection and review client serially. It has no parallel-safe peer and must
not overlap the active product-delivery checkout.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification |
| --- | --- | --- |
| CAP decisions | A CAP with direct decision gates renders DEC links with current statuses | Projection and DOM tests |
| Inherited SLI/WRK decisions | Child pages show the deduplicated CAP, SLI, and WRK decision set with status | DOM and browser tests |
| Resolved decision | A complete DEC page states that a decision is recorded and shows its canonical record when present | Projection/model/DOM tests |
| Complete decision without separate record | The DEC page states that a decision is recorded and honestly reports no separate canonical record link | DOM test |
| Deferred decision | A captured DEC page shows its status and states that no decision is recorded | Projection/DOM/browser tests |
| Missing reference | One unknown gate is shown as missing without a link; a diagnostic is emitted and unrelated routes remain usable | Projection/model/DOM tests |
| Inert details | Script-like DEC prose remains text and cannot create active DOM or navigation | DOM/browser tests |
| Route confinement | Only projected validated decision IDs resolve; traversal and unknown IDs remain bounded not-found states | Server/model tests |
| Privacy | API payload contains no ignored approval/reviewer fields, identities, dates, or authority references | Projection/server tests |
| Anti-rigidity | Adding or changing a DEC artifact appears on refresh without route registration, static generation, approval, lease, or a universal Node/browser gate | Projection/server/qualification tests |

## Verification Commands

- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/roadmap-review-site/test_server.py`
- `node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `python dev-tools/roadmap-review-site/test_qualification.py`
- `node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/tests/browser/roadmap-review.config.ts`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `python -m compileall -q dev-tools/control-plane dev-tools/roadmap-review-site`
- `git diff --check`

## Documentation and Evidence Update

Document decision sources, derived decision-made meaning, inherited relevance,
stable route, missing/deferred behavior, privacy boundary, dynamic refresh and
focused checks. Update this packet, SLI-0036 and the planning register without
approval/reviewer metadata.

## Stop Conditions

Stop for local-ledger or identity disclosure, a requirement to display approval
history, arbitrary source paths, active Markdown, planning mutation, inferred
decision authority beyond public lifecycle, static pages, broken existing
routes, generic-core repository vocabulary, unresolved architecture choice,
scope overlap, or material CAP drift.

## Required Handoff

Report the additive projection and routes, exact inherited-link behavior,
resolved/deferred/missing evidence, checks and counts, documentation impact,
privacy and confinement results, generated ignored output, residual gaps, CAP
conformance, commit, branch, worktree, and integration instructions.

## Planning History

- 2026-10-16: Authored as one bounded SLI-0036 extension after the user
  requested dynamic DEC status links and detail pages. The packet reuses the
  approved CAP-0008 projection and route boundaries, adds no approval display
  or mutation, and explicitly excludes the undescribed second change.
- 2026-10-16: Promoted to ready after focused packet validation and the
  repository planning-integrity check passed with resolved dependencies,
  bounded scope, executable checks, and no durable decision gate.
- 2026-10-16: Activated on the isolated `codex/cap-0008-decision-pages`
  branch after the implementation gate passed and the packet received a
  current exact-scope claim.
