---
id: DEC-0005
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-08-04
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0009-initial-application-framework-runtime-baseline.md
---

# Decision Request: Set the Initial Application Framework and Runtime Baseline

## Decision Needed

Choose the supported Python runtime/framework line, Node/TypeScript build line, and browser application framework/rendering mode for the first production learner-facing vertical slice.

This request asks for three coordinated choices:

- **P1 or P2** for the Python baseline;
- **N1 or N2** for the Node/TypeScript build baseline; and
- **A, B, or C** for the browser framework and routing mode.

## Why Now

[SLI-0001](../vertical-slices/SLI-0001-open-approved-versioned-lesson.md) crosses the first executable Python API and TypeScript learner interface. ADR-0001 selects Python, TypeScript, FastAPI, and Pydantic at a high level, but it explicitly defers exact framework versions and does not choose a browser framework.

Without this decision, an implementation agent would silently establish runtime support, routing, data-loading, rendering, testing, deployment, dependency, and long-term migration contracts. Deferring the choice therefore blocks slice selection rather than merely delaying a package-install command.

## Current Authority and Constraints

- [ADR-0001](../../adr/ADR-0001-python-typescript-modular-monolith.md) requires a TypeScript web application and Python modular monolith; FastAPI and Pydantic are the intended API boundary.
- The [system overview](../../architecture/system/system-overview.md) assigns authenticated application operations and generated OpenAPI to the Python API host. A browser framework must not create a second domain/application backend or bypass the generated client.
- [Contract architecture](../../architecture/contracts/contract-architecture.md) requires reviewed OpenAPI, deterministic generation, and a generated TypeScript client.
- [Local/cloud parity](../../architecture/deployment/local-cloud-capability-parity.md) requires the same browser artifacts, domain behavior, and contract versions across deployment profiles.
- The local profile must remain reproducible and practical to package without requiring a commercial platform.
- The accepted [design system](../../design/README.md) and [interface standards](../../standards/interface-design-standards.md) remain framework-independent authority for tokens, themes, iconography, accessibility, and responsive behavior.
- Server-side rendering, React Server Components, a Node backend-for-frontend, server actions, and framework-owned business APIs are not required by CAP-0001 and would add an unaccepted runtime/application boundary.
- Dependency versions must be reproducibly locked, auditable, updateable, and separable from domain code. Exact patch versions may advance within the accepted major/minor line only through reviewed dependency updates and executable compatibility evidence.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| Backend architecture and API framework | ready | Python module-first modular monolith with FastAPI and Pydantic at the API boundary | Preserve the accepted ADR-0001 path | None - ADR-0001 |
| Python runtime/framework line | ready | P1. Python 3.14, FastAPI 0.141, Pydantic 2.13 | Accepted P1 - current stable bugfix Python line with the longer remaining support window | None - ADR-0009 |
| Node and TypeScript build line | ready | N1. Node 24 LTS and TypeScript 7 | Accepted N1 - newer supported LTS line satisfying the selected browser framework engines | None - ADR-0009 |
| Browser framework and routing mode | ready | A. React 19, React Router 8 Data Mode, Vite 8 client-rendered SPA | Accepted A - preserves generated-client data authority and static deployment with the least additional server/framework abstraction | None - ADR-0009 |
| API and data-access boundary | ready | Reviewed OpenAPI and deterministic generated TypeScript client calling the Python API; no direct database/provider access | Preserve contract architecture | None - contract architecture |
| Visual and accessibility authority | ready | Existing semantic tokens, reviewed SVG icon pack, light/dark/system parity, and WCAG-oriented interface standards | Preserve the accepted design-system boundary | None - interface design authority |
| Initial identity mode in SLI-0001 | constrained | Explicit local `single_profile` adapter behind the accepted provider-neutral learner context; other accepted modes remain deliverable later | Keep the first slice inside its declared local private-host boundary | None - ADR-0006 |
| Rendering server boundary | constrained | Static/client browser artifacts plus the Python API host; a Node server, SSR, RSC, server actions, or BFF requires a later architecture decision | Keep one backend/application authority for the first slice | None - ADR-0001 and system overview |

Canonical authority for the nonblocking rows:

- [ADR-0001](../../adr/ADR-0001-python-typescript-modular-monolith.md) and the [system overview](../../architecture/system/system-overview.md) establish the Python/FastAPI API and TypeScript browser split.
- [Contract architecture](../../architecture/contracts/contract-architecture.md) establishes OpenAPI and generated-client authority.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md) establishes the provider-neutral local learner context.
- [Interface design authority](../../design/README.md) establishes theme, token, icon, layout, and accessibility rules independent of the selected UI framework.

## Options

| Option | Benefits | Costs and risks | Affected contracts and operations | Reversibility |
| --- | --- | --- | --- | --- |
| P1. Python 3.14 + FastAPI 0.141 + Pydantic 2.13 | Uses the current stable Python bugfix line, retains support through 2030, and is explicitly represented in current FastAPI and Pydantic package metadata. | Newer language/runtime behavior may expose compatibility issues in database, native, analytical, or ML dependencies as those are added. Exact patch compatibility still requires a locked environment and CI matrix. | Python project metadata and lock, container base, generated OpenAPI, type checking, database drivers, local/cloud runtime qualification. | Medium to high. A Python-minor change affects the full backend runtime but should not change public contracts. |
| P2. Python 3.13 + FastAPI 0.141 + Pydantic 2.13 | Uses a mature stable Python bugfix line with broad package availability and support through 2029. | Shorter remaining support window and an earlier future runtime migration; selecting an older line without a demonstrated compatibility need adds maintenance sooner. | Same as P1. | Medium to high. |
| N1. Node 24 LTS + TypeScript 7 | Uses the newer supported LTS line, satisfies current Vite, React Router, and Next engine ranges, and provides the longer build-tool support horizon. | Developer/CI/container images must provide Node 24; exact TypeScript and tool patches still require lockfile and clean-build qualification. | Web package metadata and lock, build container, generated client, lint/type/test/browser tools, artifact production. | High while Node remains build-time only; lower if a Node runtime is later introduced. |
| N2. Node 22 LTS + TypeScript 7 | Meets current candidate engine minimums when kept at a sufficiently recent patch and may exist in more current environments. | Older LTS line with a shorter remaining window; React Router 8 requires at least Node 22.22, so loose Node 22 claims are unsafe. | Same as N1. | High while build-time only. |
| A. React 19 + React Router 8 Data Mode + Vite 8 SPA | Keeps routing, pending/error behavior, and code splitting in a mature component ecosystem while retaining explicit control over bundling, generated-client data access, and the absence of a Node application server. Vite emits static production assets. | The project must define its own app-shell, route, data-query/cache, form, error, testing, and accessibility conventions instead of receiving a full-stack framework's defaults. Client rendering requires deliberate loading and failure experiences. | Web folder structure, route contracts, generated-client integration, static asset serving, CSP, browser tests, component conventions, local/cloud packaging. | Medium to high. React and route components become durable UI implementation contracts, but the API and domain remain independent. |
| B. React 19 + React Router 8 Framework Mode, `ssr:false`, Vite 8 | Adds typed route modules, code splitting, SPA/static rendering strategies, and integrated route conventions while retaining a static deployment mode. | Framework loaders/actions and route conventions may overlap with generated-client/data-layer authority; the project must continuously prevent drift toward a second server/API abstraction. Framework-mode migration surface is larger. | Option A surfaces plus framework route modules, build plugin, generated route types, framework-specific testing and upgrade procedures. | Medium. |
| C. React 19 + Next.js 16 App Router, static export only | Supplies an integrated routing/component framework and can emit static assets served by ordinary web servers. | Static export disables server-dependent Next features. The framework's full-stack conventions create pressure toward a Node runtime, server components/actions, framework data APIs, or provider-specific hosting that duplicate or blur the Python boundary. | Option A surfaces plus Next build/export configuration, route conventions, static-feature compatibility, image handling, and framework deployment qualification. | Medium to low if server-only Next features or conventions spread. |

## Recommendation

**[ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md) establishes P1, N1, and A as canonical: Python 3.14 with FastAPI 0.141/Pydantic 2.13, Node 24 LTS with TypeScript 7, and a React 19 + React Router 8 Data Mode + Vite 8 client-rendered application.**

- **Verified:** Python 3.14 is in stable bugfix support through 2030; Python 3.13 is supported through 2029. Current FastAPI and Pydantic metadata includes Python 3.14, and FastAPI's own version guidance recommends pinning a known-working version.
- **Verified:** Node 24 is an LTS release. Current React Router and Vite engine ranges accept Node 24.
- **Verified:** React documents a Vite-based from-scratch path when application constraints are not well served by a full-stack framework. React Router identifies Data Mode for teams that want data features while controlling bundling, data, and server abstractions.
- **Verified:** Vite produces static production assets. React Router Framework Mode can run with server rendering disabled, and Next.js can produce a static export, so B and C remain technically viable.
- **Assumption to validate:** CAP-0001 and the foreseeable labs do not need search-indexable server rendering or framework-owned server actions; authenticated learning and analytical experiences can load through the Python API after the static shell starts.
- **Inference:** Option A best matches the existing contract-driven architecture because it adds browser composition without adding another server authority or framework-owned data protocol.
- **Explicit limitation:** this recommendation does not select a component library, state/query library, form library, Markdown parser, sanitizer, test runner, browser automation library, package manager, Python environment manager, database library, or deployment provider.

## Evidence Required

Prepared decision evidence:

- Satisfied for canonical promotion: [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md) records P1, N1, and A, the single Python production-server boundary, and the deferred executable dependency evidence.
- Current primary documentation for [Python version status](https://devguide.python.org/versions/), [Node release status](https://nodejs.org/en/about/previous-releases), [React application choices](https://react.dev/learn/creating-a-react-app), [React Router modes](https://reactrouter.com/start/modes), [React Router rendering strategies](https://reactrouter.com/start/framework/rendering), [Vite production builds](https://vite.dev/guide/build), and [Next.js static exports](https://nextjs.org/docs/app/guides/static-exports).
- Registry snapshot on 2026-08-04: React 19.2.8, React Router 8.3.0, Vite 8.2.0, TypeScript 7.0.2, Next.js 16.3.0, FastAPI 0.141.1, and Pydantic 2.13.4. These observations support the proposed major/minor lines but are not a tracked lockfile.
- Direct package licenses for the compared top-level packages are permissive according to npm/PyPI metadata; transitive license compatibility has not been qualified.

Required before implementation activation:

- resolve and commit exact patches and integrity data through the approved package/environment managers and lockfiles;
- perform clean Python and Node installs on supported development/CI platforms;
- run dependency-license inventory, vulnerability review, and transitive dependency review;
- prove FastAPI/Pydantic OpenAPI generation and deterministic TypeScript client generation;
- prove the selected browser stack emits static assets served with the Python API without a Node production server;
- define supported browser targets, CSP behavior, update cadence, and end-of-support policy; and
- run representative route, data-loading, error, accessibility, theme, and local-container smoke tests.

If those checks invalidate a selected major line before implementation, return this request to shaping rather than silently substituting a different framework or runtime.

## Required Authority

Future changes to the accepted major/minor runtime lines, routing/rendering mode, or production-server boundary require product-technical and architecture authority through a new or superseding durable decision. Dependency licensing and security qualification remain mandatory implementation gates; this request records no qualified legal or security conclusion.

## Decision Record and Promotion

[ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md) records the framework/runtime baseline. ADR-0001's deferred-version boundary, the system overview, deployment profiles, assurance gaps, application READMEs, decision readiness, and context guidance are synchronized with it. Exact resolved patches belong in executable project metadata and lockfiles, not solely in the ADR.

## Dependent Planning Updates

- DEC-0005 is removed from SLI-0001 after canonical promotion.
- SLI-0001 eligibility and deterministic scoring are re-run against ADR-0009.
- Author work packets only after the separately approved slice selection.

## Planning History

- 2026-08-04: Captured when SLI-0001 eligibility review found that the accepted language/runtime shape did not determine the frontend framework or exact supported runtime lines.
- 2026-08-04: Primary framework/runtime documentation and registry metadata were compared; P1, N1, and A were recommended for decision.
- 2026-08-04: ADR-0009 and synchronized runtime, deployment, application, assurance, readiness, and context guidance established the canonical baseline; DEC-0005 moved to complete. Executable manifests, lockfiles, and clean-build evidence remain delivery gaps.
