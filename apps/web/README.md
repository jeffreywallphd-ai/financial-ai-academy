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

The generated client includes protected `browseLearningOpportunities` for
queryless `GET /api/v1/curriculum/opportunities` and
`queryLearningOpportunities` for bounded
`GET /api/v1/curriculum/opportunities/query`. The `/learn` route consumes the
query operation after establishing the private single-profile session. Native
GET controls keep bounded optional search, filters, sort, page size, and opaque
continuation in the URL; the route validates each closed page, presents the
canonical applied query and exact count/order, and fails closed on invalid,
stale, denied, or unavailable results. Neither client operation accepts
learner, permission, provider, or storage selectors.

The same generated client now includes `getCurriculumGraphVersion` for the
protected exact-version graph GET. Its path requires both curriculum identity
and semantic version and has no current/latest alias. The protected curriculum
graph route consumes this typed seam and validates the complete closed graph
before it presents any structure. The browser preserves server-owned facts and
uses optional presentation hints only for display order; it does not become a
source of graph, eligibility, completion, or mastery authority.

The generated client also includes `getCurriculumNavigationState` for the
protected exact-version Adaptation projection. It accepts only curriculum ID
and version; learner identity and navigation policy remain server-owned. No
browser-supplied learner or policy selector is accepted. The exact curriculum
route reads this projection with its graph as one all-or-nothing pair, validates
the complete graph-ordered activity closure and matching graph identity/digest,
and presents the server's separate completion, eligibility, requirement,
availability, reasons, and references. It does not reproduce Adaptation policy,
infer mastery, or calculate a path in the browser.

The generated client additionally includes `getCurriculumActivityLaunch` for
the protected bodyless activity-launch GET. It accepts only curriculum ID,
version, and activity ID. Learner identity, permissions, current state,
eligibility, placement, package, and destination remain server-owned. The
learning-path route uses that operation for `Start lesson` and `Review lesson`,
closes and correlates the returned graph/activity/resource/destination before
navigating, and never constructs a placement from displayed graph state. A new
server evaluation can legitimately carry a later evaluation time and
projection digest than the displayed state; the closed launch result remains
authoritative for that request.

The learning-catalog client also defines the reusable selection seam for
detail and comparison routes. One detail ID or two through four distinct
comparison IDs are accepted as navigation state; the protected queryless
browse operation is then read and its complete current envelope, record set,
provenance fingerprints, order, and generation are validated before any ID is
resolved. A missing ID invalidates the whole selection, so the browser never
shows a partial comparison or trusts URL- or storage-supplied record facts. An
optional same-origin `/learn` return reference may retain valid query/filter
state, but its transient cursor is removed and no saved comparison or cache is
created. The catalog exposes transient current-page comparison controls; it
serializes checked identities in learner selection order and never persists
the selection.

Node.js is build/test tooling only. Do not introduce a Node production server, SSR, React Server Components, server actions, a backend-for-frontend, framework-owned business API, React Router Framework Mode, or Next.js without a superseding architecture decision.

Exact dependency patches and integrity data belong in committed project metadata and lockfiles when approved delivery work introduces them. Do not use floating resolution as the framework baseline.

## Delivered Route

`/learn` is the application entry route and brand destination. It validates the
complete closed discovery response before presenting any record, preserves the
server-provided deterministic order, and accepts valid empty or variable-length
record sets and shared placements without a hard-coded opportunity. Curriculum
owns and validates Unicode `casefold()` ordering; the browser deliberately does
not duplicate that Python-specific policy. It instead preserves the response
order and recomputes each UTC-normalized owner-fact fingerprint plus the ordered
generation digest before rendering. The page uses learner-focused labels for
the library, filters, activities, versions, and actions. Cards keep
classification, objectives, duration, prerequisite summary, availability
reason, publisher, review date, and the educational-use notice in the normal
flow; exact package identity, digest, and source fingerprint remain reachable
under each accessible `Technical record` disclosure. Only an `available`
`lesson` exposes its exact same-origin placement link;
planned, unavailable, and non-lesson kinds remain non-navigable. Missing
authority, unavailable projection, network failure, or malformed success
responses produce bounded states without stale or partial records.

`/learn/opportunities/:opportunityId` resolves one selected identity only after
the complete current queryless discovery snapshot passes envelope, record,
fingerprint, order, and generation validation. It presents exact
classification, topics, objectives, level, duration, prerequisites,
availability, package identity/digest, publication facts, source fingerprint,
and projection context. Primary headings, labels, loading states, failures, and
actions use learner-focused language; package identity, digests, fingerprints,
generation, and schema remain complete under the accessible `Technical record`.
A cursor-free, same-origin `/learn` return reference
may preserve canonical query state. Only a validated available lesson exposes
its exact placement destination; malformed, changed, denied, unavailable, or
invalid responses show bounded states without partial or substituted facts.

`/learn/opportunities/compare` accepts two through four repeated, distinct
opportunity identities, resolves them only after the complete current queryless
snapshot passes validation, and presents exact educational, availability,
package, publication, and provenance facts in learner selection order. It does
not score, rank, recommend a winner, infer eligibility, or retain a saved
comparison. Learner-facing comparison and recovery language stays task-focused,
while exact package and projection facts remain reachable in accessible
`Technical record` disclosures. A missing current identity fails the whole view
rather than showing partial records. Every record keeps its detail link; only a
validated available lesson exposes its exact placement destination. The return
reference preserves canonical `/learn` query state without a transient cursor.

`/learn/curricula/:curriculumId/versions/:curriculumVersion` opens one exact
approved learning path. Its accessible list view is the default; a peer map
view presents the same objectives, competencies, learning groups, activities,
and connections with a responsive grouping layout rather than fixed canvas
coordinates. Optional or absent presentation hints, variable record counts,
same-kind shared branch memberships, activities outside groups, and empty group
or connection sets remain valid. Primary labels explain progress, readiness,
path requirement, learning-material availability, and the server-provided
reasons for each status. Exact activity/resource identity, state values, reason
codes/references, source references, schema, graph and policy identity,
evaluation time, and digests remain complete under accessible `Technical
record` disclosures. Both peer views preserve the four orthogonal
server-evaluated state dimensions and expose the same server-checked start or
review action only for available eligible lessons. Locked, unavailable, and
assessment activities retain their facts without a launch control. A returning
lesson marks a current activity in visible text and `aria-current` only after a
fresh exact graph confirms the identifier. This marker is presentation, not
authorization, mastery, recommendation, or browser-owned learner state. Links
that cannot be used, learner-access problems, missing versions, temporary
failures, and unsafe incomplete results show bounded task-focused states. They
never substitute another version or reveal partial learning-path details.

`/learn/placements/:placementId` establishes the explicitly configured
single-profile session and opens the exact placement through the generated
OpenAPI client. It renders only the closed safe body-node union and presents
objectives, reviewed sources, publication details, and the educational-use
limitation in the learner's main flow. Exact package identity, version, and
digest remain complete under an accessible `Technical record` disclosure.
Loading and bounded failures state the learner-visible result, protected-record
meaning, and existing safe action without exposing internal checks. Unknown
nodes, unsafe locators, denial, missing exact placement, integrity failure, and
unavailable responses continue to fail to bounded page states.
When a lesson was opened from a learning path, the route accepts only the
complete exact curriculum ID, version, and activity-ID return set. It derives a
same-origin learning-path link from those values; partial, duplicate, extra,
malformed, or absent context creates no return action and grants no access.
The same route reads the exact Assessment presentation and submits one
single-choice response through the generated client. Scoring and learner
identity remain server-authoritative; the browser never receives the answer
key.

The route first calls the protected exact-placement completion-history query.
When saved completion exists, the main flow shows the score, time, and bounded
non-mastery/non-advice meaning without requesting another knowledge-check
presentation. Exact source, lesson, Assessment, question, scoring-policy,
event, attempt, evidence, version, digest, and rebuild facts remain complete
under accessible `Technical record` disclosures. A just-submitted result uses
the same pattern for its exact result provenance. Empty history continues to
the answer-safe form. Denied, malformed, or unavailable history fails closed
with direct reload guidance and without fabricating a completion or erasing
evidence. The browser sends no learner selector and receives no answer key,
Audit row, or mastery interpretation.

`/learn/placements/:placementId/practice` establishes the same supported
single-profile session and opens one exact practice activity through the
generated public API client. The browser validates the complete answer-safe
presentation before showing the title, purpose, instructions, attempt-policy
meaning, learning and review material, and ordered single-select,
multiple-select, or fixed-decimal response controls. Learner-facing copy states
that responses entered during this opening step are neither checked nor saved.
There is no submission control, answer key, accepted numeric value or range,
private feedback, scoring authority, attempt evidence, local persistence, or
browser-selected learner. Exact placement, package, practice, definition,
question, policy, choice, resource, version, and digest facts remain available
under the accessible `Technical record`. Missing access, missing activity,
temporary failure, malformed content, unknown response types, extra private
fields, duplicate identities, or placement mismatch fails the whole view to a
bounded learner-focused state without partial questions or choices. The same
protected HTTP operation remains available to non-browser and future headless
clients; the page does not define a second contract or a separate AI mode.

The browser never selects the learner, reads the HttpOnly cookie, imports
backend code, parses CommonMark, uses an unsafe HTML sink, or accesses a
database/provider. Theme preference is the only local browser preference
persisted by this slice.

The application shell uses the canonical primary sidebar: expanded at wide
desktop widths, compact with labeled hover/focus disclosures at intermediate
desktop widths, and an accessible menu drawer on narrow viewports. `Learn` is
the only active destination in this slice. Future product areas are visibly
marked as planned and are not exposed as dead links or fictional routes.

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
`http://127.0.0.1:5173/learn`. Press
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
npm --prefix apps/web run test:browser -- tests/browser/learning-catalog tests/browser/lesson-reading tests/browser/curriculum-graph
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
Curriculum operations, publishes two exact immutable curriculum versions,
rebuilds its discovery projection, and runs the live Chromium checks from the protected
graph and `/learn` catalog through the exact lesson, assessment, and retained
completion against that same-origin Python host. The live graph and navigation
checks cover direct API/UI fact parity, complete graph-ordered activity state,
the same learner context before and after retained lesson completion, bounded
assessment-source unavailability, ordered reasons and references, list/map
parity, policy/source/projection provenance, an unbranched activity,
unsupported-selector and missing-version denial, themes, adaptive display
conditions, and accessibility. Browser assertions use learner-facing labels
first and open `Technical record` disclosures before comparing exact IDs,
state values, reason evidence, schema, policy, time, sources, and digests. The
same live run calls the protected launch API directly and through the generated
browser client, opens the server-derived lesson path, retains exact return
context through completion and reload, and shows fresh complete/current state
on return. Its two versions prove that an explicitly reused exact placement may
reuse retained evidence while a changed placement remains incomplete; neither
case uses inferred equivalence or browser policy. The
separate pinned browser fixture preserves
the wider same-kind shared-branch and variable-reference anti-rigidity cases;
the live approved graph does not invent those shapes for qualification.
See
[the local deployment guide](../../deployments/local/README.md)
for clean-start and teardown commands.

## Verification Boundaries

Vitest owns fail-closed content and discovery-response validation, session,
theme, component, generated-client, and static-browser-boundary checks.
Playwright Chromium owns the delivered catalog, detail, comparison, curriculum
graph, and lesson routes' light/dark/system equivalence,
automated accessibility scans, keyboard focus, responsive reflow, reduced
motion, forced colors, denial, and unknown-content/record paths. Lesson visual
baselines are platform-specific. The live cross-system suite additionally owns the real
PostgreSQL/filesystem, single-profile session, generated-client,
static-serving, three-classification query corpus, combined filters,
multi-page duration order, cursor-query mismatch denial, exact current detail,
ordered comparison, changed/malformed selection, approved catalog projection
and exact navigation, exact curriculum graph and protected navigation-state
and activity-launch API/list/map/provenance, two exact coexisting curriculum
versions, generated-client lesson start/review and return, complete
activity-state closure, same-context
completion transition, bounded assessment unavailability, shared/unbranched
fixture grouping, selector and missing-version denial, submission, repeated
retained-completion reopen, missing-context, stale-placement, security-header,
education-boundary, and catalog/detail/comparison/graph/completion axe paths.
Repeated cards preserve heading/list
semantics without creating redundant nested named landmarks. Real
screen-reader operation, actual browser
200-percent zoom controls, and browsers beyond the pinned Chromium runtime
require controlled manual or later multi-browser qualification.

## Interface Design System

All interface work must follow:

- [Interface Design System](../../docs/design/README.md)
- [Interface Style Guide](../../docs/design/style-guide.md)
- [Content Style Guide](../../docs/design/content-style-guide.md)
- [Interface Design Standards](../../docs/standards/interface-design-standards.md)
- [Learner-Facing Language Standards](../../docs/standards/user-facing-language-standards.md)
- [Executable tokens](src/design-system/tokens.css)
- [Production iconography](src/design-system/icons/README.md)

Feature code consumes semantic tokens and the reviewed icon pack. It must not introduce a parallel feature-local palette, spacing scale, theme map, shadow system, or icon set.

When shared visual behavior changes, update the design guide, executable assets, consumers, and relevant visual/accessibility tests together. Run:

```powershell
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
```
