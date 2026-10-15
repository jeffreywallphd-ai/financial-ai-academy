---
id: WRK-0026
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: SLI-0036
capability: CAP-0008
depends_on: ["WRK-0025"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/roadmap_review.py", "dev-tools/control-plane/test_roadmap_review.py", "dev-tools/control-plane/README.md", "dev-tools/roadmap-review-site", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0036-navigate-capability-slice-and-work-plans.md", "docs/planning/work-packets/WRK-0026-deliver-dynamic-roadmap-plan-details.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js"]
base_revision: eac534abe9154710db2599a429a1f05d9cf47867
claim_id: WRK-0026:9fbb213a-2d66-4657-b30a-4a5a8d3f3eaf
claimed_by: codex-roadmap-review
claimed_at: 2026-10-15T15:35:12Z
---

# Agent Work Packet: Deliver Dynamic Roadmap Plan Details

## Objective and Deliverable

Extend the reusable roadmap hierarchy and local site so every product candidate,
internal CAP, declared slice, refined slice, and associated work packet has a
stable, current, safe detail view without generated pages or arbitrary file
access.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/interface/testing
context, CAP-0008, SLI-0034 through SLI-0036, WRK-0024/WRK-0025 contracts and
evidence, CAP-0003 hierarchy implementation, projector/adapter/server/client and
tests, planning artifacts, design tokens, decision readiness, and nearest
READMEs before editing.

## Decisions and Assumptions

- Internal and mapped capabilities use one additive projected slice/work shape.
- Browser routes resolve only against the current projection; URL segments never
  become source paths.
- Safe document blocks are rendered with DOM construction and `textContent`.
- A missing future slice is a useful placeholder, not an error or planning gate.
- Existing overview, theme, refresh, source fingerprint, and security behavior
  remain compatible.

## In Scope

Generic internal hierarchy enrichment; candidate/CAP/slice/work route resolution;
breadcrumbs; context/metadata; complete slice/work lists; inert document block
renderer; unplanned/missing/empty/not-found states; fixed server route shapes;
focused projection/server/model/DOM/security tests; README updates.

## Out of Scope

Write APIs, source editing, approval/identity data, arbitrary Markdown links or
paths, active HTML, static detail generation, graph editing, agents, leases,
hosted access, product integration, or cumulative browser qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generic projection | Current capability/slice/work assembly and tests | `roadmap_review.py`, focused tests | Give internal capabilities the same hierarchy without project vocabulary |
| Host routes | Fixed allowlist and denial tests | Review-site server/tests | Serve validated stable detail URL shapes only |
| Client | Overview model/app/style/tests | Review-site TypeScript/CSS/tests | Resolve and render complete safe hierarchy dynamically |
| Docs/planning | Site/control-plane READMEs and SLI/WRK/register | Exact named files | Document routes, missing states, evidence, and lifecycle |

## Contracts and Interfaces

Additive `roadmap-review-v1` internal `slices`, stable `/capability/<key>`,
`/cap/<id>`, `/slice/<id>`, and `/work/<id>` routes, existing inert document
block types, repository-relative displayed sources, and current fingerprint.

## Dependencies and Parallel Safety

WRK-0025 is complete. This packet owns the detail extension serially; no active
peer has reciprocal scope because projection, route, client, and style files are
shared.

## Acceptance Scenarios

The SLI-0036 table is normative. Focused tests cover product and internal CAPs,
unplanned candidates, manifest order, refined and missing slices, empty and
populated work lists, current work evidence, unknown keys/IDs, reloadable routes,
script-like text, all inert block types, traversal, no mutation, and absence of
manual generation or route registration per artifact.

## Verification Commands

- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/roadmap-review-site/test_server.py`
- `node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document stable routes, inert rendering, missing/refined behavior, dynamic
refresh, and the extension seam. Update packet/slice/register evidence without
approval or reviewer metadata.

## Stop Conditions

Stop for source-path parameters, active Markdown, ignored data, plan mutation,
static copied pages, inferred planning facts, broken overview compatibility,
remote binding, generic-core project vocabulary, unresolved decision, or scope
overlap.

## Required Handoff

Delivered additive internal-capability slice/work hierarchy, stable candidate/
CAP/slice/work routes, breadcrumbs, manifest-ordered child lists, unplanned and
unrefined states, inert structured plan rendering, current work completion text,
bounded unknown routes, and updated operator guidance. The 8-test projection
suite, 7 server/API/confinement scenarios, 11 client model/DOM/route/inertness
scenarios, and TypeScript typecheck passed. Design-system validation reported
125 tokens and 56 icons; planning validated 53 artifacts; documentation
validated 176 Markdown files plus catalogs; diff checks and all 25 aggregate
readiness checks passed. Server tests ran outside the socket-restricted sandbox,
and Vitest ran outside its temp-cache restriction. Browser-engine screenshots,
zoom, and assistive-technology evidence remain for SLI-0037. The additive
contract requires no migration; generated JavaScript remains ignored and
reproducible. No URL becomes a filesystem path, no active plan content is
created, and the delivery conforms to SLI-0036 and CAP-0008.

## Planning History

- 2026-10-15: Authored just in time as the sole SLI-0036 packet after the
  overview contract and route shell completed.
- 2026-10-15: Delivered dynamic hierarchy details and moved to verification
  after focused route, inert-content, server, type, design, documentation,
  planning, and aggregate checks passed.
