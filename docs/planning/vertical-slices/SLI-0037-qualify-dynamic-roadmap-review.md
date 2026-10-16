---
id: SLI-0037
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: CAP-0008
depends_on: ["SLI-0034", "SLI-0035", "SLI-0036"]
decision_gates: []
---

# Vertical Slice: Qualify Dynamic Roadmap Review

## Outcome and User Scenario

A repository operator can trust the completed local roadmap review because its
dynamic catalog accounting, hierarchy, ordering, compatibility, freshness,
confinement, privacy, accessibility, responsive/theme behavior, and low-friction
operation have cumulative automated evidence. The always-on readiness gate gains
only dependency-free contract checks; browser and Node-heavy qualification stays
affected-scope evidence rather than becoming a barrier to unrelated work.

## Scope Boundaries

### In Scope

- A dependency-free roadmap-review qualification suite added to fixed readiness
  alongside the focused projection suite, covering contract wiring, read-only
  confinement, dynamic data, ignored output, responsive/accessibility source
  contracts, anti-rigidity, and presence of browser qualification.
- Focused source-change freshness, malformed/count/path/privacy/failure tests and
  cumulative projection, server, TypeScript, DOM, design, docs, and planning
  verification.
- Chromium Playwright coverage for overview and detail navigation, exact 26
  accounting, unplanned/unrefined states, keyboard focus, axe, themes, narrow
  reflow, forced colors, reduced motion, API failure, and inert content.
- Operator/test/known-gap documentation, including browser availability and
  explicitly unperformed manual/non-Chromium qualification.
- Deterministic cumulative CAP-0008 acceptance reconciliation and closure if all
  required evidence passes.

### Out of Scope

- Making browser installation, npm dependency setup, or a full UI suite part of
  every planning/documentation readiness run; hosted access; non-Chromium or
  multi-platform baselines; manual screen-reader certification; planning writes;
  product integration; or new roadmap semantics.

## Canonical Context and Decisions

CAP-0008 and completed SLI-0034 through SLI-0036, CAP-0003 contracts, testing
and interface standards, known verification gaps, fixed readiness architecture,
and site/control-plane guidance govern. No durable decision is introduced.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Lightweight fixed contract gates plus affected-scope Node/browser qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Run TypeScript, server sockets, browser installation, and Playwright in every readiness invocation | no — creates disproportionate friction for unrelated documentation/planning changes | — | — | — | — | — | — | — | — |
| C. Keep browser/accessibility behavior manual and outside executable evidence | no — leaves the delivered interface materially unqualified | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A keeps a fast universal safety net while directly qualifying the
affected interface with its real host and browser. It closes meaningful gaps
without turning a local review tool into a mandatory repository-wide UI build.

## Boundary Path

Fixed readiness invokes dependency-free projection and site-contract tests. The
focused command path retains TypeScript, DOM, live loopback server, and Chromium
Playwright/axe suites. The Playwright web server uses the public one-command host;
it neither bypasses the adapter nor introduces test-only data routes.

## Contracts, Data, and Provenance

Existing catalog/projection/route contracts remain unchanged. Browser artifacts
are ignored under `artifacts/`; generated client JavaScript remains ignored
under `.local-codex/`. Test results and completion prose contain counts and
outcomes, not ignored authority data or personal identifiers.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Fixed safety net | Readiness runs dependency-free roadmap projection and site contract checks without Node, browser, socket, or manual generation requirements | Aggregate readiness test |
| Live overview | Chromium sees 26 unique candidates, accurate planned/unplanned counts, order/ties/blockers, and conservative parallel evidence | Browser/axe test |
| Live hierarchy | Candidate, internal CAP, refined/unrefined slice, work, and unknown routes remain complete, stable, and inert | Browser/server test |
| Accessibility/themes | Axe has no violations; landmarks, headings, labels, live state, keyboard focus, light/dark/system parity, forced colors, reduced motion, and narrow reflow remain usable | Browser/design test |
| Freshness/failure | Sequential API projections can change fingerprints without build/regeneration; malformed sources and API failure remain bounded | Server/projection test |
| Confinement/privacy | Remote bind, mutation, traversal, unknown assets, active content, ignored authority keys, and absolute paths remain denied | Server/contract/browser test |
| Anti-rigidity | Normal use remains one start command and refresh; universal readiness adds no Node install, browser, approval, claim, lease, static generation, or full UI suite | Qualification test |
| Cumulative closure | Every CAP-0008 acceptance statement maps to direct evidence or an explicit known gap inside the approved boundary | Completion review |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0027 | Add proportionate fixed and affected-scope qualification, reconcile documentation/gaps, and close CAP-0008 | WRK-0026 | none | complete |
| WRK-0084 | Qualify the integrated executable-order projection, active-descendant promotion, and roadmap-card rendering as one exact candidate | WRK-0080, WRK-0081, WRK-0083 | none | active |

## Verification and Qualification

Run the new fixed qualification, all projection/server/client/type/browser/design
checks, planning/documentation integrity, local and CI-profile readiness, Python
compilation, diff checks, completion gates for SLI-0037 and the cumulative CAP
package, and record any external/manual gap precisely.

## Rollback and Migration

Qualification is additive. Rollback removes the fixed checks and browser suite
without changing roadmap data or runtime state. No migration exists.

## Stop Conditions

Stop for failed safety/accessibility evidence, hidden unknown state, browser
tests bypassing production routes, new universal Node/browser friction,
unresolved decision, privacy disclosure, hosted scope, weakened denials, stale
documentation, or material CAP drift.

## Documentation Impact and Completion Evidence

Added a dependency-free 6-test site contract suite and the 10-test roadmap
projection suite to fixed readiness; neither invokes Node, a browser, a server,
planning authority, or generated data. Added 3 live Chromium Playwright/axe
scenarios using the documented server command and existing public API/routes.
The 8-test live server suite proves fresh no-store reprojection, loopback-only
binding, GET/HEAD-only behavior, fixed assets/routes, traversal denial, exact
catalog accounting, and bounded failure. The 11-test TypeScript model/DOM suite
proves filtering, honest compatibility, stable route resolution, dynamic detail
hierarchy, inert content, missing states, refresh failure, and theme behavior.

Chromium showed all 26 candidates and passed axe on overview and detail,
keyboard skip focus, light/dark/system content parity, a 360-pixel viewport,
forced colors, reduced motion, candidate/CAP/slice/work deep links, unplanned and
unrefined states, unknown routes, and API failure. An initial narrow-screen run
failed on horizontal overflow; responsive grid/table constraints were corrected
and the full 3-test browser suite passed. Strict TypeScript typecheck, design
validation (125 tokens and 56 icons), planning integrity (55 artifacts),
documentation integrity (178 Markdown files plus catalogs), Python compilation,
and diff checks passed. Aggregate readiness passed 27 local and 26 CI-profile
checks with the new lightweight roadmap checks included.

Loopback, Vitest temporary-cache, and Chromium execution required their
established outside-sandbox paths. Manual screen-reader operation, actual
browser 200-percent zoom controls, non-Chromium browsers, and non-Windows visual
baselines were not performed and remain in the known-gap register. No migration,
backup, hosted qualification, tracked generated roadmap, or static page exists;
ignored compiled JavaScript and failure-only Playwright artifacts are
reproducible. Every SLI-0037 scenario and CAP-0008 acceptance boundary has direct
automated evidence or an explicit in-scope residual gap, and no material CAP
drift occurred.

## Planning History

- 2026-10-15: Refined as the final cumulative CAP-0008 slice. Candidate A
  scored 14/14 and explicitly prevents browser-heavy checks from becoming an
  unrelated-work gate while retaining direct affected-interface evidence.
- 2026-10-15: Activated after the implementation gate passed and WRK-0027 was
  claimed with cumulative qualification scope.
- 2026-10-15: Moved to verification after the complete fixed, focused, and live
  Chromium evidence passed following correction of detected narrow-screen
  overflow.
- 2026-10-15: Closed deterministically after WRK-0027 completed and the final
  slice completion structure, evidence, known gaps, and CAP conformance passed.
- 2026-10-16: Added bounded correction qualification WRK-0084 after separate
  allocator, projection, and site-consumer corrections converged on one exact
  candidate. The packet retains affected-scope evidence and adds no new CAP
  outcome or approval gate.
- 2026-10-16: Activated WRK-0084 against the pre-correction base after its
  completed dependencies, exact cumulative scope, checks, and absence of a
  decision gate were validated. The packet performs qualification only.
