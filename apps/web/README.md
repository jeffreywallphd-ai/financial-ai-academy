# Web Application

This directory contains the React 19 and TypeScript 7 learner-facing application defined by [ADR-0009](../../docs/adr/ADR-0009-initial-application-framework-runtime-baseline.md). React Router 8 Data Mode owns browser routing and route-level pending/error behavior; Vite 8 produces the development and static production builds under Node.js 24 LTS.

Planned structure:

```text
src/
|-- app/                 routing and composition
|-- features/            module-aligned learner/admin experiences
|-- components/          shared presentational components
|-- design-system/       semantic tokens and production icon assets
|-- platform/            API, auth, configuration, and telemetry clients
`-- generated/api-client/ generated from reviewed OpenAPI
tests/
```

The web application uses public generated clients. It does not import backend internals, own authoritative domain policy, or access databases/providers directly.

Node.js is build/test tooling only. Do not introduce a Node production server, SSR, React Server Components, server actions, a backend-for-frontend, framework-owned business API, React Router Framework Mode, or Next.js without a superseding architecture decision.

Exact dependency patches and integrity data belong in committed project metadata and lockfiles when approved delivery work introduces them. Do not use floating resolution as the framework baseline.

## Delivered Route

`/learn/placements/:placementId` establishes the explicitly configured
single-profile session and opens the exact placement through the generated
OpenAPI client. It renders only the closed safe body-node union and presents
objectives, reviewed sources, package version/digest, and publication
provenance. Unknown nodes, unsafe locators, denial, missing exact placement,
integrity failure, and unavailable responses fail to bounded page states.

The browser never selects the learner, reads the HttpOnly cookie, imports
backend code, parses CommonMark, uses an unsafe HTML sink, or accesses a
database/provider. Theme preference is the only local browser preference
persisted by this slice.

## Commands

From the repository root, use the same bootstrap command in Git Bash or
PowerShell:

```text
npm --prefix apps/web run setup:dev
```

On first use it installs fnm through the exact `Schniz.fnm` WinGet package
when needed, installs Node 24.14.0, installs the exact npm 10.8.2 CLI below
ignored `.local-codex`, and invokes that CLI with the fnm-managed Node through
`fnm exec`. It does not replace the system Node/npm installation or edit either
shell profile. The full runner then verifies Python, Docker Compose, and Git;
creates an ignored local
uv tool environment; restores the exact Python and npm locks; installs pinned
Chromium; starts disposable PostgreSQL; runs the complete backend, contract,
client, web, browser, end-to-end, architecture, security, design,
documentation, planning, advisory, and readiness checks; then starts the
Python API and Vite hot-reload server. Open
`http://127.0.0.1:5173/learn/placements/intro-risk-return-primary`. Press
Ctrl+C to stop both servers and remove the exact disposable database and data
root created by the runner.

CPython 3.14, Docker with Compose, Git, and WinGet when fnm is initially
absent remain machine prerequisites. Prepare only the fnm-managed Node/npm
runtime with:

```text
npm --prefix apps/web run setup:dev -- --setup-only
```

To install dependencies and run all checks without leaving development servers
running, use:

```text
npm --prefix apps/web run setup:dev -- --verify-only
```

When the exact fnm-managed runtime is already active,
`npm --prefix apps/web run dev:full` remains available as the lower-level
entry point.

The individual commands remain available for focused work:

```text
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run apps/web/tests/unit apps/web/tests/component
npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading
npm --prefix apps/web run build
python tests/e2e/approved-lesson/run.py
```

`npm --prefix apps/web run dev` starts only the Vite development server. It proxies `/api` to
`http://127.0.0.1:8000` by default; a non-default local target may be supplied
through `FINANCIAL_AI_ACADEMY_API_ORIGIN`. For this proxied development
profile, configure the backend's exact public origin and allowed Host as
`http://127.0.0.1:5173`. The proxy preserves the browser origin so the
accepted Host/Origin and cookie boundary remains coherent.

The production build is static HTML, CSS, JavaScript, source-map, and reviewed
SVG-icon output. Serve those assets from the Python application origin with
SPA fallback to `index.html`; do not add a Node production server.

The cross-system runner requires the static build, starts an isolated
PostgreSQL 18.4 container when no explicitly acknowledged external test
database is supplied, starts `deployments/local/serve.py` as the only
application process, seeds the approved fixture through public Content and
Curriculum operations, and runs the live Chromium checks against that
same-origin Python host. See [the local deployment guide](../../deployments/local/README.md)
for clean-start and teardown commands.

## Verification Boundaries

Vitest owns fail-closed content validation, session, theme, component,
generated-client, and static-browser-boundary checks. Playwright Chromium owns
the delivered route's light/dark/system visual baselines, automated
accessibility scan, keyboard focus, responsive reflow, reduced motion, forced
colors, denial, and unknown-content paths. Visual baselines are
platform-specific. The live cross-system suite additionally owns the real
PostgreSQL/filesystem, single-profile session, generated-client,
static-serving, success, missing-context, stale-placement, security-header,
education-boundary, and axe path. Real screen-reader operation, actual browser
200-percent zoom controls, and browsers beyond the pinned Chromium runtime
require controlled manual or later multi-browser qualification.

## Interface Design System

All interface work must follow:

- [Interface Design System](../../docs/design/README.md)
- [Interface Style Guide](../../docs/design/style-guide.md)
- [Interface Design Standards](../../docs/standards/interface-design-standards.md)
- [Executable tokens](src/design-system/tokens.css)
- [Production iconography](src/design-system/icons/README.md)

Feature code consumes semantic tokens and the reviewed icon pack. It must not introduce a parallel feature-local palette, spacing scale, theme map, shadow system, or icon set.

When shared visual behavior changes, update the design guide, executable assets, consumers, and relevant visual/accessibility tests together. Run:

```powershell
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
```
