---
id: WRK-0117
kind: work-packet
planning_status: verifying
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
base_revision: 6f7c1abf5ccf570e45eceb7194f13564fa91df69
claim_id: WRK-0117:3e95e7cf-09c1-49b3-a4f5-22fd7e15ebe6
claimed_by: codex-cap-0007-correction
claimed_at: 2026-10-16T22:23:51Z
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

## Completion Evidence

- The pinned Node 24/npm 10.8.2 Vite build replaced obsolete
  `index-CSLAcjng.js` and its source map with `index-BiYcwksJ.js` and its
  source map, and updated only the matching script reference in
  `dist/index.html`. Both new references and the existing CSS reference resolve
  inside the tracked bundle.
- Two consecutive production builds produced identical output. The current
  SHA-256 values are
  `D85C71850D5DF9AD47DBA49A076352620738F46214AD9CE6EFA03AE9F657969C`
  for `index.html`,
  `B6D6D94C75EA0929220C9CF5E6286E4BE6BB41C69AFE0B0C122852A7DB80BEC3`
  for the JavaScript chunk, and
  `CBA9C7A6637AA43F8D0B847963CE79D6236378653128C12ED08A1FE771ED7792`
  for its source map.
- Focused Project Chromium qualification passed all six create, list, reopen,
  unchanged-retry, conflict-recovery, in-flight-locking, stale-selection,
  responsive, accessibility, and plain-language scenarios. Static-boundary
  architecture passed 16 checks and aggregate agent readiness passed all 29
  checks with the repository-local Windows temp root.
- Planning validation covered 200 artifacts and documentation validation
  covered 344 Markdown files plus catalogs. Git scope inspection confirms no
  authored TypeScript, CSS, backend, contract, dependency, configuration, or
  test source changed.

## Planning History

- 2026-10-16: Authored as the bounded descendant correction after SLI-0030
  cumulative qualification proved the tracked production bundle was stale.
  The packet owns generated static output only and requires no new decision or
  lower-level approval.
- 2026-10-16: Prepared the exact generated-artifact candidate after two
  reproducible builds, static-reference validation, focused Project Chromium,
  architecture, planning, documentation, whitespace, and aggregate readiness
  checks passed.
