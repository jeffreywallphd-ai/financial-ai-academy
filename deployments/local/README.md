# Local Deployment and Approved-Lesson Qualification

The intended complete local profile includes the static web application,
Python API and worker, PostgreSQL, filesystem object storage, and DuckDB/Parquet
analytics. Only the bounded approved-lesson, curriculum-graph, discovery-query,
deterministic-navigation-state, deterministic assessment, and
retained-completion `single_profile` path is qualified today.
This is a development/CI qualification topology, not a production
publication, backup, restore, availability, or remote-hosting claim.

## Qualified Topology

```text
Browser / pinned Chromium
        |
        | one loopback HTTP origin
        v
Python 3.14 + FastAPI/Uvicorn
  |-- reviewed static Vite artifacts
  |-- single-profile session/API
  |-- Content/Curriculum graph and discovery operations
  |-- restrictive filesystem object root
  `-- PostgreSQL 18.4
```

Node 24 builds and tests the exact static browser artifacts. It is not an
application process in the qualification topology. The Python host rejects
non-loopback configuration, serves `/assets` and SPA fallback on the API
origin, emits a restrictive Content Security Policy, applies empty-database
migrations, and admits the synthetic approved fixture only when the explicit
seed flag is present. Through public Curriculum operations, that flag binds the
reviewed graph shape to the admitted exact package, creates every referenced
lesson and assessment placement, and publishes
`investing-foundations@1.0.0`. It also registers one exact Curriculum-owned
catalog classification and atomically rebuilds the derived discovery projection
through public application operations. The additional
`--seed-discovery-query-fixtures` flag requires that approved fixture and adds
two fixed classifications before the same single atomic rebuild. Normal
startup does not seed or rebuild data, and ordinary approved-fixture startup
does not require the larger query corpus.

## One-Command Development

From the repository root, run the same command in Git Bash or PowerShell:

```text
npm --prefix apps/web run setup:dev
```

On its first run, the setup installs fnm through the exact `Schniz.fnm`
WinGet package when fnm is absent, accepting the WinGet source and package
agreements for that package. It then installs Node 24.14.0, installs the exact
npm 10.8.2 CLI below ignored `.local-codex`, and invokes that CLI with the
fnm-managed Node through `fnm exec`. It does not replace the system Node/npm
installation or edit PowerShell, Bash, or Git Bash profiles. Use the setup-only
form to prepare and verify the project runtime without installing application
dependencies or starting services:

```text
npm --prefix apps/web run setup:dev -- --setup-only
```

The full runner checks the remaining machine prerequisites, installs the exact
locked Python and web dependencies, installs pinned Chromium, starts an
isolated PostgreSQL 18.4 composition, and runs all required project checks. It
then recreates a clean disposable database and starts the Python API on
`http://127.0.0.1:8000` plus the Vite hot-reload application on
`http://127.0.0.1:5173`. Open `http://127.0.0.1:5173/learn`, then follow the
exact approved lesson action. The seeded successor package includes the exact
Assessment-owned single-choice knowledge check and deterministic feedback path.

Press Ctrl+C once to stop both development processes and tear down only the
runner's uniquely named Compose project and ignored synthetic data root. Node
and npm are project-local fnm-managed prerequisites; CPython 3.14, Docker with
Compose, Git, and WinGet when fnm is initially absent remain machine
prerequisites. The runner installs project dependencies and its exact uv
version under ignored local paths; it does not alter a global Python
environment. Use
`npm --prefix apps/web run setup:dev -- --verify-only` for install-and-check
behavior without starting persistent development servers.

If fnm, Node 24.14.0, and npm 10.8.2 are already active, the lower-level
`npm --prefix apps/web run dev:full` command remains available.

## Automated Clean Qualification

Prerequisites are Docker, CPython 3.14 with uv 0.11.29, Node 24/npm 10.8.2,
the committed locks, and the pinned Playwright Chromium runtime.

```powershell
py -m uv sync --project backend --frozen
npm --prefix apps/web ci
npm --prefix apps/web run build
npm --prefix apps/web exec -- playwright install chromium
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
```

The runner chooses unused loopback ports, creates a uniquely named
`postgres:18.4` container with an ephemeral data mount, creates an isolated
filesystem root below ignored `artifacts/tmp/`, waits for readiness, starts the
Python host, opts into three deterministic discovery classifications, and runs
the live browser checks for two exact curriculum versions and the protected
navigation-state and activity-launch APIs, complete graph-ordered activity
closure, generated-client start/review and exact return, same-context
before/after lesson completion, API/list/map state and reason parity, bounded
assessment-source unavailability, provenance, unbranched activity grouping,
selector, launch, and missing-version denial, changed-placement isolation,
reused exact-source evidence, responsive and adaptive display behavior,
combined filters,
three-page ordering, cursor-query mismatch denial, exact current-opportunity
detail, ordered two-record comparison, changed and malformed selection, exact
lesson continuation, retained completion, context denial, security headers,
and axe accessibility. The companion isolated browser fixture, rather than the
live approved graph, qualifies same-kind shared branches and variable reference
counts without changing production fixture meaning.

After the browser journey, the runner creates a fresh cookie-backed headless
session and reads the exact graph, Navigation state, and eligible launch through
public APIs. It then stops the application, deletes only the isolated
Learner-model completion history and projection rows, restarts the normal host
against the retained database and object root without reseeding, and proves
that a fresh API read rebuilds the same semantic navigation state from unchanged
Assessment evidence. This is an isolated replay check, not a product reset
route or production recovery procedure.

It removes only those exact resources in `finally` cleanup. An external database is accepted only when
`FINANCIAL_AI_ACADEMY_E2E_EXTERNAL_DB_ACKNOWLEDGED=true` explicitly confirms
that it is isolated test data.

## Manual Inspection

The committed compose file starts only the disposable database:

```powershell
docker compose -f deployments/local/compose.qualify.yml up -d --wait
uv run --project backend python deployments/local/serve.py --postgres-dsn "postgresql://financial_ai_academy:qualification-only@127.0.0.1:55432/financial_ai_academy" --data-root ".test-data/approved-lesson" --host 127.0.0.1 --port 8000 --seed-approved-fixture --seed-discovery-query-fixtures
```

Open `http://127.0.0.1:8000/learn`, then follow the exact approved lesson action
to `/learn/placements/intro-risk-return-primary`. The independently addressable
graph is available at
`/learn/curricula/investing-foundations/versions/1.0.0`; its qualification-only
successor is independently available at version `1.1.0`. Stop the Python
process, then tear down only this qualification composition:

```powershell
docker compose -f deployments/local/compose.qualify.yml down --volumes
```

The ignored `.test-data/approved-lesson` directory may be removed after
confirming the Python process is stopped and the resolved path is inside this
repository. Do not reuse these synthetic credentials or the qualification
database for retained learner data.

## Qualified and Unqualified Claims

Direct evidence covers one approved fixture plus two exact immutable curriculum
versions and an opt-in three-classification query corpus, real PostgreSQL migrations
and repositories, restrictive local filesystem storage, loopback request
policy, opaque HttpOnly session cookie, public-operation graph publication,
discovery registration and one atomic projection rebuild, reviewed
OpenAPI/generated client, static same-origin Python serving, exact graph,
navigation-state, and activity-launch API/list/map/provenance/denial paths,
generated-client lesson launch and exact return, same-context retained
completion transition, exact reused-source versus changed-placement behavior,
complete ordered activity closure, bounded assessment
unavailability, filter/pagination/cursor-denial, exact detail, ordered
comparison, changed/malformed selection, and
catalog-to-exact-lesson Chromium paths, architecture and security scans, axe
accessibility, safe teardown, API-only graph/state/launch consumption, and
application-restart reconstruction of derived Learner-model state from
unchanged Assessment evidence without fixture reseeding.

The following remain unqualified: built-in credentials, OIDC, multiple
learners, remote/public binding, worker and analytics composition, passive
asset delivery, backup/restore, upgrade procedures beyond the tested slice
migrations, non-Chromium browsers, non-Windows visual baselines, managed
cloud, production distribution, and any RPO/RTO or availability claim.
The qualification also does not define a headless AI mode, agent protocol,
model provider, or autonomous action authority; it preserves the public API
surface that such a separately planned consumer could use later.
