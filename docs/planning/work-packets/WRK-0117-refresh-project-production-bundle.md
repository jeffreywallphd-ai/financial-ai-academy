---
id: WRK-0117
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0007-correction
updated: 2026-10-16
parent: SLI-0030
capability: CAP-0007
depends_on: [WRK-0111]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/dist", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0030-create-independent-or-learning-project.md", "docs/planning/work-packets/WRK-0116-qualify-project-shell-origin-flow.md", "docs/planning/work-packets/WRK-0117-refresh-project-production-bundle.md"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Refresh the Project Production Bundle

## Objective and Deliverable

Regenerate the tracked static production bundle from the already accepted
Project browser source so the Python-served release artifact contains the
current Project create/reopen flow. Remove only obsolete hashed outputs and
prove a second clean build is reproducible without changing authored product
source, contracts, dependencies, or behavior.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through delivery planning, interface design,
testing-quality, and local deployment context; apply the change-impact matrix
and decision readiness; inspect CAP-0007, SLI-0030, WRK-0111, WRK-0116, the
Vite configuration and manifest, the accepted Project browser source, the
tracked `apps/web/dist` policy, Python static-serving checks, build tests, and
nearest READMEs.

## Decisions and Assumptions

The accepted WRK-0111 source and current locked Node/npm dependency graph are
authoritative. A normal pinned production build is deterministic for the
tracked static artifact. No shared design choice, public contract, Project
semantics, provider, identity, tenancy, execution, recovery, or AI-authority
decision is required.

## In Scope

- Run the pinned Vite production build from the accepted source and retain its
  exact tracked `apps/web/dist` output.
- Remove only obsolete hashed assets replaced by that build and verify every
  reference in `dist/index.html` resolves inside the bundle.
- Run the build a second time and prove it produces no further tracked diff.
- Run focused production-boundary, Project browser, planning,
  documentation, whitespace, affected-verification, and readiness checks.

## Out of Scope

Any authored TypeScript, React, CSS, SVG-source, backend, API, OpenAPI,
generated API-client, contract, migration, dependency, lockfile, test-fixture,
design-system, browser-copy, or runtime behavior change. Optional minification,
chunking, styling, performance, or bundle-size optimization remains outside
this correction.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Production bundle | Vite inputs, manifest, tracked output, Python static-serving checks | `apps/web/dist` only | Synchronize deployable bytes with accepted source |
| Planning | SLI-0030, WRK-0116, register | listed planning files | Record the bounded correction and unblock final qualification |
| Authored product | web/backend/contracts/configuration/dependencies | none | The correction must not change behavior or architecture |

## Contracts and Interfaces

Consume the existing Vite build contract and accepted browser source. Produce
only the static HTML, CSS, SVG copy, JavaScript, and source map already owned by
`apps/web/dist`; no public API, TypeScript client, runtime route, or dependency
interface changes.

## Dependencies and Parallel Safety

WRK-0111 is complete and supplies the accepted Project browser source. This
packet owns the complete tracked production bundle and shared SLI-0030
planning files, so it is not parallel-safe with another web build or slice
closure packet. WRK-0116 resumes only after this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Current production artifact | accepted Project browser source and exact locks | the pinned production build runs | `dist/index.html` references the newly generated assets and no obsolete chunk remains tracked | build/diff evidence |
| Reproducible output | the first regenerated bundle | the same pinned build runs again | no further tracked bundle change appears | second-build diff |
| Static boundary | regenerated output | architecture and production-boundary checks run | only browser artifacts exist and the Python static host remains the production process | architecture tests |
| Project behavior | unchanged authored source | focused Project Chromium tests run | create/list/reopen, idempotency recovery, accessibility, and responsive behavior remain available | Project browser suite |
| No scope escape | the correction candidate | changed paths are inspected | no authored source, contract, dependency, or configuration changed | Git diff and affected verification |

## Verification Commands

Run the pinned `npm --prefix apps/web run build` twice; inspect the exact
bundle diff and references; run repository-hygiene and approved-lesson
architecture tests, focused Project Chromium tests, planning and packet
validation, documentation, whitespace, affected exact-candidate verification,
`python dev-tools/agent/check_ready.py`, and the required independent technical
check. Use the repository-local temporary root on Windows where needed.

## Documentation and Evidence Update

Record the old and new hashed bundle identities, two-build reproducibility,
static-host boundary, focused Project behavior, exact checks, and confirmation
that authored product source and contracts did not change. Keep technical
disposition data only in ignored local storage.

## Stop Conditions

Stop for a nondeterministic second build; an unexpected authored-source,
contract, dependency, or configuration change; a missing bundle reference;
functional or accessibility regression; canonical conflict; active write
collision; or material CAP-0007 drift. Harmless line-ending warnings or
optional styling do not create another review loop.

## Required Handoff

Report the exact candidate and receipt, replaced and current bundle identities,
second-build result, static-host and Project-browser checks, changed files,
documentation impact, assumptions, residual limits, and confirmation that no
authored behavior or public interface changed.

## Planning History

- 2026-10-16: Authored as the bounded descendant correction after SLI-0030
  cumulative qualification proved the tracked production bundle was stale.
  The packet owns generated static output only and requires no new decision or
  lower-level approval.
