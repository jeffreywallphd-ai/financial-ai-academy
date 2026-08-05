# Local Deployment and Approved-Lesson Qualification

The intended complete local profile includes the static web application,
Python API and worker, PostgreSQL, filesystem object storage, and DuckDB/Parquet
analytics. Only the read-only approved-lesson `single_profile` path is qualified
today. This is a development/CI qualification topology, not a production
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
  |-- Content/Curriculum application operations
  |-- restrictive filesystem object root
  `-- PostgreSQL 18.4
```

Node 24 builds and tests the exact static browser artifacts. It is not an
application process in the qualification topology. The Python host rejects
non-loopback configuration, serves `/assets` and SPA fallback on the API
origin, emits a restrictive Content Security Policy, applies empty-database
migrations, and admits the synthetic approved fixture only when the explicit
seed flag is present.

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
`http://127.0.0.1:5173`. Open
`http://127.0.0.1:5173/learn/placements/intro-risk-return-primary`.

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
Python host, runs the live browser checks, and removes only those exact
resources in `finally` cleanup. An external database is accepted only when
`FINANCIAL_AI_ACADEMY_E2E_EXTERNAL_DB_ACKNOWLEDGED=true` explicitly confirms
that it is isolated test data.

## Manual Inspection

The committed compose file starts only the disposable database:

```powershell
docker compose -f deployments/local/compose.qualify.yml up -d --wait
uv run --project backend python deployments/local/serve.py --postgres-dsn "postgresql://financial_ai_academy:qualification-only@127.0.0.1:55432/financial_ai_academy" --data-root ".test-data/approved-lesson" --host 127.0.0.1 --port 8000 --seed-approved-fixture
```

Open
`http://127.0.0.1:8000/learn/placements/intro-risk-return-primary`. Stop the
Python process, then tear down only this qualification composition:

```powershell
docker compose -f deployments/local/compose.qualify.yml down --volumes
```

The ignored `.test-data/approved-lesson` directory may be removed after
confirming the Python process is stopped and the resolved path is inside this
repository. Do not reuse these synthetic credentials or the qualification
database for retained learner data.

## Qualified and Unqualified Claims

Direct evidence covers one approved fixture, real PostgreSQL migrations and
repositories, restrictive local filesystem storage, loopback request policy,
opaque HttpOnly session cookie, reviewed OpenAPI/generated client, static
same-origin Python serving, Chromium success and denial paths, architecture
and security scans, and safe teardown.

The following remain unqualified: built-in credentials, OIDC, multiple
learners, remote/public binding, worker and analytics composition, passive
asset delivery, backup/restore, upgrade procedures beyond the tested slice
migrations, non-Chromium browsers, non-Windows visual baselines, managed
cloud, production distribution, and any RPO/RTO or availability claim.
