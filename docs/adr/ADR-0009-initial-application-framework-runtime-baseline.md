# ADR-0009: Initial Application Framework and Runtime Baseline

- Status: accepted
- Date: 2026-08-04
- Decision request: [DEC-0005](../planning/decision-requests/DEC-0005-initial-application-framework-runtime-baseline.md)

## Context

ADR-0001 selects a TypeScript browser application and a Python modular-monolith backend, with FastAPI and Pydantic at the API boundary. The first learner-facing vertical slice requires executable runtimes, build tooling, routing, and browser composition. Leaving those choices implicit would let dependency installation establish a durable architecture without review.

The platform already assigns authenticated application operations and OpenAPI generation to the Python API. The browser consumes a generated TypeScript client, and local and managed-cloud profiles must use the same application artifacts and contract versions. The initial web baseline therefore does not need a second application server, server-side rendering, or framework-owned business APIs.

## Decision

Adopt the following initial supported major/minor lines:

- **Backend runtime:** standard CPython 3.14.
- **Python API boundary:** FastAPI 0.141 and Pydantic 2.13.
- **Web build runtime:** Node.js 24 LTS, used for dependency management, generation, builds, tests, and development tooling rather than as a production application server.
- **Web language:** TypeScript 7.
- **Browser framework:** React 19.
- **Routing and browser data lifecycle:** React Router 8 Data Mode.
- **Development and production bundling:** Vite 8.
- **Rendering:** a client-rendered single-page application producing static browser assets.

The Python API remains the sole initial server-side application/transport boundary. The web application calls reviewed OpenAPI operations through a deterministically generated TypeScript client. React Router may own client navigation, route-level pending/error state, and browser composition, but it does not define domain operations, duplicate API models, access databases/providers, or introduce a framework-owned server protocol.

Production does not require a Node server. Server-side rendering, React Server Components, server actions, a Node backend-for-frontend, React Router Framework Mode, and Next.js are outside the initial boundary.

Executable project metadata must pin exact compatible patches and integrity data through committed lockfiles. An approved major/minor line is not permission to float dependency resolution. Patch updates require clean resolution, focused and aggregate tests, generated-output comparison, dependency-license inventory, vulnerability review, and supported-environment qualification. A change to a named runtime/framework major or minor line, rendering mode, or server boundary requires explicit compatibility review and an ADR update or supersession.

## Consequences

- Automated implementation has one reproducible target rather than choosing frameworks during delivery.
- Python remains the only production application runtime; local and cloud deployments can serve the same static web artifacts beside the same API.
- Generated OpenAPI clients remain the authoritative browser data seam.
- React Router Data Mode provides routing and pending/error behavior without importing a full-stack server abstraction.
- The project must define its own app-shell, query/cache, form, error, testing, and accessibility conventions within existing architecture and design authority.
- Exact package patches, package/environment managers, database libraries, parser/sanitizer libraries, test runners, browser automation, and component libraries remain delivery choices subject to their owning reviews.
- Runtime and framework upgrades become deliberate compatibility work rather than incidental dependency changes.

## Alternatives Rejected

- **Python 3.13 as the initial baseline.** It is viable but has a shorter remaining support window than the stable Python 3.14 line without a demonstrated dependency constraint requiring the older runtime.
- **Node.js 22 LTS as the initial build baseline.** It is viable at a sufficiently recent patch but has a shorter remaining support window; Node 24 satisfies the accepted framework engine ranges.
- **React Router Framework Mode with server rendering disabled.** It can emit a static SPA and supplies additional route conventions, but its framework loaders/actions and server-capable model add abstraction that can overlap the generated-client and Python-server boundary.
- **Next.js static export.** It can emit static assets, but its full-stack conventions and server-dependent feature set create pressure toward a second Node application boundary while static export disables those features.
- **A Node production server, SSR, RSC, server actions, or BFF.** CAP-0001 does not require them, and they would add an unaccepted application/server authority.

## Boundaries

This decision does not select exact patch versions, a package or environment manager, a component library, CSS framework, client query/cache library, form library, Markdown parser, sanitizer, database library, migration tool, test runner, browser automation tool, container base digest, hosting provider, or browser support matrix.

It does not authorize implementation, dependency installation, external publication, production deployment, or a framework-specific domain/application API. It does not change the accepted design-token, iconography, accessibility, security, identity, content-package, recovery, or local/cloud semantic boundaries.

## Verification Implications

Before delivery relies on this baseline:

- commit Python and Node project metadata plus exact lockfiles and integrity information;
- prove clean reproducible installs and builds in every supported development/CI environment;
- verify Python 3.14, FastAPI 0.141, and Pydantic 2.13 compatibility through API, OpenAPI, validation, and async lifecycle tests;
- verify Node 24, TypeScript 7, React 19, React Router 8 Data Mode, and Vite 8 through type checking, production build, route, error, accessibility, theme, and browser tests;
- prove generated TypeScript clients reproduce from the reviewed OpenAPI snapshot and application code does not hand-maintain duplicate API models;
- inspect dependency licenses, provenance, vulnerabilities, and transitive packages before activation and on updates;
- prove production web artifacts run without a Node application server and both deployment profiles use identical browser assets; and
- add architecture checks preventing frontend imports of backend internals, direct database/provider access, framework dependencies in backend domain code, and unaccepted server entry points.

Until executable manifests, locks, builds, and tests exist, these are accepted architecture claims with verification coverage classified as a gap.

## Supersession

None. Changes to the named major/minor lines, browser framework, router mode, rendering strategy, production runtime split, or generated-client authority require an ADR update or superseding decision with migration and compatibility evidence.
