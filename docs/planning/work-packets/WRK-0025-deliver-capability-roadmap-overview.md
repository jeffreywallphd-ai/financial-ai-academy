---
id: WRK-0025
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: SLI-0035
capability: CAP-0008
depends_on: ["WRK-0024"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/roadmap-review-site", "dev-tools/control-plane/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0035-review-capability-order-and-parallelism.md", "docs/planning/work-packets/WRK-0025-deliver-capability-roadmap-overview.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js"]
base_revision: eac534abe9154710db2599a429a1f05d9cf47867
claim_id: WRK-0025:9e29eda9-b8c6-4844-8d94-244182e9c66f
claimed_by: codex-roadmap-review
claimed_at: 2026-10-15T15:29:53Z
---

# Agent Work Packet: Deliver Capability Roadmap Overview

## Objective and Deliverable

Deliver a one-command loopback review host and a TypeScript overview that
renders all 26 candidates, lifecycle and planning state, proposed order,
unresolved ties, blockers, internal capabilities, and parallel evidence from the
live `roadmap-review-v1` projection with no planning mutation or static data copy.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/interface/testing
context, CAP-0008, SLI-0034 and SLI-0035, WRK-0024 contracts, control-plane
adapter/CLI/tests, design tokens and icon guidance, interface and testing
standards, security locality, and nearest READMEs before editing.

## Decisions and Assumptions

- The host is Python standard-library and loopback-default; it imports the
  existing adapter rather than spawning a shell command.
- The browser client is TypeScript. The start command automatically emits
  ignored JavaScript using the repository-pinned compiler, so UI code can remain
  typed without a committed build or data regeneration step.
- The UI consumes order and compatibility facts verbatim and does not calculate
  authority, dependencies, or parallel safety.
- Existing semantic tokens and reviewed icons are sufficient.

## In Scope

Server/API/static allowlist, automatic ignored compilation, overview model,
semantic UI, search/status/planning filters, proposed order/ties/blockers,
parallel evidence and accessible alternatives, internal-capability section,
refresh/theme controls, focused server/model/DOM/type/style tests, and README.

## Out of Scope

Detailed CAP/SLI/WRK views, plan-body rendering, write APIs, approvals, agents,
leases, hosted access, product app integration, new tokens/icons, or static
roadmap data.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Local host | Adapter and security contracts | Site `server.py` and tests | Serve live API and fixed assets safely |
| Client | `roadmap-review-v1`, shared tokens/icons | Site TypeScript/HTML/CSS/tests | Render accessible overview without semantic duplication |
| Tooling | Pinned TypeScript/runtime setup | Site package/tsconfig/compiler helper | Preserve one-command start and deterministic checking |
| Docs/planning | Control-plane/site README, SLI/WRK/register | Exact named files | Document and reconcile lifecycle evidence |

## Contracts and Interfaces

`GET /api/roadmap`, fixed static routes, `roadmap-review-v1`, semantic theme
tokens, same-origin reviewed icon sprite, capability links by stable catalog key,
and client overview functions that preserve unknown/incompatible evidence.

## Dependencies and Parallel Safety

WRK-0024 is complete. This packet owns the new host and overview directory and
is serial because it establishes routes and styles consumed by WRK-0026.

## Acceptance Scenarios

The SLI-0035 table is normative. Focused tests cover exact counts, unplanned and
planned cards, status/search filters, unresolved ties, empty safe sets, compatible
sets, unknown and incompatible counts, internal capabilities, refresh failure,
no-store API, GET/HEAD, denied mutations, traversal, fixed assets, loopback
default, theme parity, semantic structure, and the one-command path.

## Verification Commands

- `python dev-tools/roadmap-review-site/test_server.py`
- `node apps/web/node_modules/vitest/vitest.mjs run dev-tools/roadmap-review-site/tests`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document the exact start URL/command, refresh and failure behavior, dynamic data
sources, ignored compilation output, scope limits, tests, and extension seam.
Update slice/packet/register evidence without approval or reviewer metadata.

## Stop Conditions

Stop for remote binding, mutation, shell execution from requests, arbitrary file
serving, duplicated planning semantics, committed data projection, product-app
coupling, new theme/icon system, inaccessible graph-only content, unresolved
decision, or scope overlap.

## Required Handoff

Delivered the one-command loopback host, automatic ignored TypeScript build,
live no-store API, fixed asset allowlist, semantic all-candidate overview,
filters, order/ties/blockers, conservative parallel evidence, theme controls,
bounded failure state, and operator documentation. Server/security tests passed
7 scenarios outside the managed socket sandbox; client model/DOM tests passed 8
scenarios outside the sandbox because Vitest's atomic temporary-cache rename is
restricted there. TypeScript typecheck, the 8-test roadmap projection suite,
design-system validation (125 tokens and 56 icons), planning validation (51
artifacts), documentation validation (174 Markdown files plus catalogs), diff
checks, and all 25 aggregate readiness checks passed. The server exposes GET and
HEAD only on numeric loopback, sends no-store API responses, and rejects remote
binds, mutation, unknown assets, query-bearing routes, and traversal. Browser
engine screenshots and assistive-technology qualification remain explicitly for
SLI-0037. No migration or tracked generated roadmap data was introduced;
`.local-codex/roadmap-review-site/app.js` and `model.js` are reproducible ignored
outputs. Delivery conforms to SLI-0035 and CAP-0008 without changing planning or
parallel-safety semantics.

## Planning History

- 2026-10-15: Authored just in time as the sole SLI-0035 packet after WRK-0024.
- 2026-10-15: Delivered the dynamic overview and moved to verification after
  focused server, client, type, security, design, documentation, planning, and
  aggregate readiness checks passed.
