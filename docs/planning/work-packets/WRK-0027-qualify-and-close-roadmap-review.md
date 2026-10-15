---
id: WRK-0027
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: SLI-0037
capability: CAP-0008
depends_on: ["WRK-0026"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/test_roadmap_review.py", "dev-tools/roadmap-review-site", "dev-tools/agent/check_ready.py", "apps/web/tests/browser/roadmap-review", "apps/web/tests/browser/roadmap-review.config.ts", "dev-tools/control-plane/README.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/capabilities/CAP-0008-review-capability-delivery-roadmaps.md", "docs/planning/vertical-slices/SLI-0037-qualify-dynamic-roadmap-review.md", "docs/planning/work-packets/WRK-0027-qualify-and-close-roadmap-review.md"]
generated_artifacts: [".local-codex/roadmap-review-site/app.js", ".local-codex/roadmap-review-site/model.js", "artifacts/playwright/roadmap-review"]
base_revision: eac534abe9154710db2599a429a1f05d9cf47867
claim_id: WRK-0027:b4982f61-7187-4d7b-aa95-13d8b40d75ff
claimed_by: codex-roadmap-review
claimed_at: 2026-10-15T15:38:45Z
---

# Agent Work Packet: Qualify and Close Roadmap Review

## Objective and Deliverable

Deliver proportionate fixed and affected-scope qualification for the completed
dynamic roadmap review, reconcile operator and known-gap documentation, prove
CAP-0008 acceptance cumulatively, and close the capability if evidence passes.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/interface/testing
context, CAP-0008, SLI-0034 through SLI-0037 and their packets/evidence, CAP-0003
contracts/tests, review projector/host/client/tests/READMEs, fixed readiness and
CI workflow, existing browser/axe conventions, design tokens, decision
readiness, known verification gaps, and nearest READMEs before editing.

## Decisions and Assumptions

- Universal readiness receives only dependency-free Python checks.
- Node, live loopback sockets, and Chromium/axe remain explicit affected-scope
  evidence to avoid an unrelated-work barrier.
- Browser tests start the same documented server command and use only public
  routes/API.
- Non-Chromium and manual screen-reader/actual-browser-zoom evidence remain
  honest known gaps, consistent with repository-wide policy.

## In Scope

Pure-Python site contract qualification; aggregate integration; freshness and
cumulative failure/privacy assertions; Playwright config/tests for live overview
and hierarchy; axe, keyboard, themes, responsive, forced-color, reduced-motion,
failure and inertness evidence; README/gap/planning/CAP reconciliation.

## Out of Scope

Universal npm/browser setup, hosted CI deployment, non-Chromium baselines,
manual assistive-technology certification, planning mutation, product app code,
new projection/UI functionality, commit, merge, push, publish, or deploy.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Fixed readiness | Existing dependency-free checks and CI setup | `check_ready.py`, pure qualification test | Add fast roadmap safety coverage without new CI runtime dependencies |
| Focused browser | Existing Playwright/axe conventions | Roadmap config/spec under browser tests | Qualify the real local host and interface |
| Focused contracts | Projection/server/client suites | Existing focused tests/site test files | Close freshness, malformed, privacy, and anti-rigidity evidence |
| Docs/planning | Site/control-plane guidance, known gaps, CAP/SLI/WRK/register | Exact named files | Reconcile commands, evidence, lifecycle, and residual gaps |

## Contracts and Interfaces

Existing `capability-catalog-v1`, `roadmap-review-v1`, stable detail routes,
fixed check allowlist/report schema, repository Playwright conventions, ignored
artifact paths, and CAP approval/completion rules.

## Dependencies and Parallel Safety

WRK-0026 and every earlier CAP-0008 packet are complete. This cumulative packet
is serial because it qualifies and updates shared implementation and completion
evidence.

## Acceptance Scenarios

The SLI-0037 table and complete CAP-0008 acceptance list are normative. Tests
also assert that fixed readiness contains no Node/Playwright/server-start
command, generated roadmap data remains ignored, browser routes use the public
host, and safety/accessibility failures cannot be offset by friction budgets.

## Verification Commands

- `python dev-tools/roadmap-review-site/test_qualification.py`
- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/roadmap-review-site/test_server.py`
- `node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests`
- `node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit`
- `node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/tests/browser/roadmap-review.config.ts`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `python dev-tools/agent/check_ready.py --profile ci`
- `python -m compileall -q dev-tools/control-plane dev-tools/roadmap-review-site dev-tools/agent`
- `git diff --check`

## Documentation and Evidence Update

Document fixed-versus-focused qualification, browser start/troubleshooting, and
residual manual/non-Chromium gaps. Record exact outcomes and counts without
approval/reviewer metadata or generated browser artifacts.

## Stop Conditions

Stop for any failed hard safety/accessibility assertion, universal Node/browser
dependency, static data/page generation, remote exposure, active content,
privacy breach, unresolved decision, incomplete earlier slice, stale docs, or
CAP acceptance without mapped evidence.

## Required Handoff

Delivered a 6-test dependency-free site qualification, integrated it and the
10-test projection suite into fixed readiness, and retained Node/socket/browser
work as affected-scope evidence. The live server suite passed 8 scenarios; the
TypeScript client passed 11 model/DOM/route scenarios and strict typecheck; and
3 Chromium Playwright scenarios passed with zero axe violations across overview
and detail pages. Browser evidence covers exact 26 accounting, deep links,
unplanned/unrefined states, inert plan content, keyboard focus, light/dark/system
parity, 360-pixel reflow, forced colors, reduced motion, and bounded API failure.
The first narrow-browser run exposed horizontal overflow; grid and table sizing
were corrected and the complete suite then passed. Design validation reported
125 tokens and 56 icons; planning validated 55 artifacts; documentation
validated 178 Markdown files plus catalogs; Python compilation and diff checks
passed. Local readiness passed 27 checks and CI-profile readiness passed 26,
with no Node, socket, browser, approval, claim, lease, or generation dependency
in the fixed roadmap checks. Server/Vitest/browser suites used the established
outside-sandbox paths for loopback, temp cache, and Chromium. Manual screen
reader operation, actual browser 200-percent zoom, non-Chromium, and non-Windows
visual baselines remain documented gaps. No migration or tracked generated data
exists; ignored JavaScript and Playwright artifacts are reproducible. All
CAP-0008 acceptance is directly evidenced or explicitly bounded, with no
material drift.

## Planning History

- 2026-10-15: Authored just in time as the sole final CAP-0008 packet with a
  lightweight fixed gate and browser-heavy affected-scope qualification.
- 2026-10-15: Moved to verification after cumulative fixed, focused, browser,
  accessibility, responsive, security, local-profile, and CI-profile evidence
  passed and residual manual/non-Chromium gaps were reconciled.
