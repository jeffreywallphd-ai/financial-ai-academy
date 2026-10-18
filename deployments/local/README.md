# Local Deployment and Approved-Lesson Qualification

The intended complete local profile includes the static web application,
Python API and worker, PostgreSQL, filesystem object storage, and DuckDB/Parquet
analytics. Only the bounded approved-lesson, curriculum-graph, discovery-query,
deterministic-navigation-state, deterministic assessment, answer-safe practice
opening, retained-completion, Project list/create/reopen, learner preference,
display preference, AI-help preference, and Personal-workspace Saved Learning
`single_profile` paths are qualified today. The Personal-workspace
journey uses the same protected public API from generated-browser and ordinary
headless clients, survives a normal host restart without reseeding, and is
included in one stopped-source, empty-target disposable recovery exercise.
This is a development/CI qualification topology, not a supported backup tool,
production recovery, availability, or remote-hosting claim.

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
lesson and assessment placement, admits the exact three-shape practice package,
creates its lesson and practice placement, and publishes
`investing-foundations@1.0.0`. It also registers one exact Curriculum-owned
catalog classification and atomically rebuilds the derived discovery projection
through public application operations. The additional
`--seed-discovery-query-fixtures` flag requires that approved fixture and adds
two fixed classifications before the same single atomic rebuild. Normal
startup does not seed or rebuild data, and ordinary approved-fixture startup
does not require the larger query corpus.

The same explicit approved-fixture flag also admits one reviewed Project
package, publishes its exact Curriculum graph and placement, and makes the
learning brief available through the protected Project start-option API. The
Projects browser uses that same API as headless clients; the fixture is not a
production bootstrap rule.

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
The independently addressable practice fixture opens at
`/learn/placements/intro-risk-return-practice/practice`; its generated-client
form saves the first complete three-response attempt through the same public
POST available to non-browser clients.

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
and axe accessibility. It also opens the exact three-shape practice through a
cookie-backed non-browser HTTP client and the generated browser client, checks
all three controls and bounded denials, compares storage counts across repeated
reads, and proves the same presentation survives a normal restart without
reseeding. The browser then saves a partial draft, reloads it, completes all
three response shapes, submits one mixed result, and displays server-owned
retry, answer-free history, and review-target state. A fresh non-browser
session reads the same public progress document, saves and exactly replays the
partial snapshot as the next-attempt draft, proves a different stale save
cannot replace it, and verifies one atomic
attempt/response/score/completion/outbox aggregate. After normal restart, the
runner reopens the same progress and draft, exactly replays both accepted
documents, and confirms immutable counts and the newer draft remain unchanged.
The runner next drives the complete Learning preferences browser journey and
captures only the closed public profile, bounded history, portable export, and
safe expected correlations. Fresh cookie-backed headless clients read the same
meaning, exactly replay the browser mutation, and exercise same-key replay,
same-key conflict, and different-key stale-revision races through the public
API. Direct PostgreSQL inspection is evidence-only; it correlates the accepted
rows while privacy-safe fingerprints prove that unrelated learning state did
not change. The same profile, history, export, replay, and rows are checked
again after the normal host restart.
The same run then drives the Display and accessibility route through all 16
closed presentation profiles. It proves that preview and cancel do not write,
save and confirmed reset use the protected generated client, the downloaded
profile/history export matches a direct headless read, the browser-local theme
is excluded, and simultaneous exact replay, changed-payload, and stale-revision
requests produce one safe durable meaning. Direct PostgreSQL correlation and a
fresh headless session recheck the exact rows after the normal restart while
privacy-safe fingerprints prove unrelated application state did not change.
Chromium also checks keyboard operation, 320-pixel reflow with 200-percent
text, forced colors, reduced motion, focus visibility, and axe results before
the runner removes the capture and disposable topology.
The same run drives the AI help and reminders route with both choices initially
off. Browser and ordinary headless clients read the same learner-owned profile,
history, and export, exactly replay an accepted reset, and exercise same-key
replay, changed-payload conflict, and different-key stale-revision races.
PostgreSQL inspection correlates only the bounded assistance rows before and
after a normal restart. The reminder envelope remains browser-local, contains
no learner identity, survives only a browser reload, and is absent from every
public API document. Network and platform observation records no provider or
model call, notification permission, service worker, schedule, subscription,
or delivery side effect, while privacy-safe fingerprints prove unrelated
application state did not change.

The final preference-system phase composes all three retained families without
adding an aggregate endpoint. It snapshots the three profile/change/mutation
stores before and after each family journey, requires only the named family to
change, correlates three distinct profiles to one server-owned learner context,
and rechecks the exact composite after normal restart and headless reads. The
report also records that theme and reminders remain two browser-local adapters.
This is local shared-core evidence only; it does not qualify managed-cloud
composition or define a headless AI mode.

The runner also exercises the generated Saved Learning browser against the
same live host: it creates a Unicode note and bookmark for the exact approved
lesson, reorders them, creates ordered collection membership, archives and
restores a record, runs one Unicode combined query, explicitly checks one
current Project source, reloads the route, and captures only bounded public
state. A fresh non-browser session reads and queries the identical workspace,
reproduces the canonical applied query and digest, exactly replays the accepted
record-only refresh and final restore, proves changed-key and stale-revision
conflicts are confidential and side-effect free, and observes the same complete
state after restart. Direct PostgreSQL correlation binds the public workspace
ID, revision, accepted documents, request keys, and results to one Personal-
workspace aggregate and its eleven workspace-scoped mutation rows. The
Project browser journey runs before Saved Learning and contributes one exact
workspace, immutable checkpoint, and inert-file manifest selector. The mixed
collection survives headless replay and restart; an unavailable Project fails
confidentially without changing unrelated records; and the saved file record
contains no bytes, storage locator, download, preview, or execution seam.
Bounded before/after snapshots also compare privacy-safe, schema-wide exact-row
fingerprints and prove that the Saved Learning journey leaves Project workspace,
checkpoint and inert-artifact facts plus Content, Curriculum, Assessment,
Learner-model, and Audit state unchanged. The
companion isolated browser fixture, rather than the
live approved graph, qualifies same-kind shared branches and variable reference
counts without changing production fixture meaning.

After the normal restart checks, the default runner-owned topology stops the
application, creates one logical PostgreSQL dump, and copies the exact bounded
application-data root inside its ignored temporary directory. A second unique
PostgreSQL 18.4 container first receives a harmless marker: the recovery guard
refuses that populated target without applying the dump and leaves the marker
unchanged. The runner then empties the target, restores only the dump inside
the unique runner-owned root, compares privacy-safe row plus structural-catalog
fingerprints and file-tree digests, and revokes at least one restored session.
The ordinary application starts without seed flags against the restored
database and copied data root; the pre-restore cookie is denied before a fresh
headless session reproduces the same Personal-workspace read, query, export,
exact replay, mutation rows, and target-state fingerprints. The stopped source
remains byte- and row-stable;
both containers, the dump, copied data, and captures are removed in bounded
cleanup. An acknowledged external database never enters or claims this drill.

The runner also creates a fresh cookie-backed headless session and reads the
exact graph, Navigation state, and eligible launch through public APIs. It then
stops the application, deletes only the isolated
Learner-model completion history and projection rows, restarts the normal host
against the retained database and object root without reseeding, and proves
that a fresh API read rebuilds the same semantic navigation state from unchanged
Assessment evidence. This is an isolated replay check, not a product reset
route or production recovery procedure.

The same runner qualifies checked-in Platform, contextual, and feature-
condition Guidance through one browser session and a separate ordinary HTTP
session. It compares all four contexts, all five exact feature resolutions,
every referenced topic, publication/source facts, and all digests before and
after normal application restart; denies missing and invalid sessions
confidentially; observes browser Guidance traffic as loopback-only and GET-
only; and requires the complete non-Identity database fingerprint to remain
unchanged during the Guidance-only phase. Focused browser suites separately
cover owning feature links, safe action handlers, optional fallback, and
closed same-origin returns.

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
successor is independently available at version `1.1.0`. The answer-safe
practice is available at
`/learn/placements/intro-risk-return-practice/practice`. The Project list is
available at `/projects`; it can create independent work or start the exact
reviewed `Compare investment choices` brief and reopen the result through the
public Project API. Stop the Python process,
then tear down only this qualification composition:

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
accessibility, safe teardown, API-only graph/state/launch consumption, exact
three-shape practice opening, generated-browser partial save/reload and
submission, identical non-browser progress/draft use, exact replay, stale-save
refusal, server-owned retry/history/review state, atomic Assessment
evidence/outbox counts, bounded practice denial, practice restart parity, and
generated-browser/headless Personal-workspace parity, ordered collections,
canonical Unicode query/digest and closed export parity, record-only source checking,
confidential exact refresh/restore replay and conflict handling, source-state
isolation, Personal-workspace restart durability, and the stopped-source
disposable populated-target-refusal/empty-target recovery exercise described
above,
generated-browser/headless AI-help profile/history/export parity, exact replay,
safe simultaneous-write outcomes, browser-local reminder separation, normal-
restart durability, unrelated-state noninterference, and absence of model or
notification execution,
application-restart reconstruction of derived Learner-model state from
unchanged Assessment evidence without fixture reseeding.

The following remain unqualified: built-in credentials, OIDC, multiple
learners, remote/public binding, worker and analytics composition, passive
asset delivery, a supported backup/restore product, recovery manifest and
finalization tooling, production roles and permissions, scheduled or retained
recovery sets, failure/corruption and cross-version matrices, upgrade
procedures beyond the tested slice migrations, non-Chromium browsers,
non-Windows visual baselines, managed cloud, production distribution, and any
RPO/RTO or availability claim.
Additional live accepted attempts through the browser, an available live review
destination, downstream practice-event consumption, and production recovery
remain unqualified. The deterministic three-shape submission, feedback result,
bounded retry enforcement, conditional draft save/resume, answer-free history,
unavailable review guidance, atomic evidence/outbox append, exact replay,
stale conflict refusal, and normal-restart durability are qualified only in this
local single-profile fixture.
The qualification also does not define a headless AI mode, agent protocol,
model provider, or autonomous action authority; it preserves the public API
surface that such a separately planned consumer could use later.
