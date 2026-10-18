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

The generated Guidance client includes exact protected platform-topic search,
topic read, contextual-help read, and feature-guidance resolution operations
shared with command-line, service, and future headless clients. The Web
boundary closes full contextual and feature-guidance responses before rendering
them. Delivered lesson, practice, Saved learning, Project, and AI-help surfaces
request only their fixed public keys and exact version, then show reviewed
plain-language explanations and exact topic destinations. Optional Guidance
failure never blocks or changes the owning task. Exact topic pages accept only
a closed same-origin return; the browser does not store routes in Guidance
content, select a different version, infer a condition, execute an action, or
invent a mapping.

The isolated local qualification reads all four exact context documents, all
five feature-condition resolutions, and every referenced topic through an
authenticated browser context, then repeats the same public reads with an
ordinary cookie-backed HTTP client before and after normal host restart. The
capture binds context, mapping, record, and topic digests; source fingerprints;
confidential missing/invalid-session denial; loopback-only GET traffic; and an
unchanged non-Identity database fingerprint. Focused feature suites retain the
owning status/action, link-label, safe-handler, fallback, accessibility, and
safe-return evidence, so live Guidance containment does not reclassify ordinary
learner-feature side effects as Help behavior.

The cumulative Platform Help qualification also reproduces the reviewed
OpenAPI client, runs the complete Web unit/component suite, TypeScript,
zero-warning lint, the production build, and focused Chromium accessibility
and safe-rendering checks. The same live run proves that browser and ordinary
headless clients receive equivalent exact Guidance before and after a normal
restart without adding a browser-only API or state path.

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

The lesson publication and each retained completion also expose a reusable
`Source and history` panel backed only by the generated public client. The
browser does not load this data until the learner asks. It validates the exact
root, ordered entries, owner/resource combinations, connections, diagnostic
notes, redaction counts, timestamps, and integrity codes before showing an
all-or-nothing record. Primary content uses plain learner language; exact
identifiers, enum values, versions, times, and digests remain available in the
technical disclosure. A separate protected export operation returns the
validated portable JSON record on demand. Read and export permissions remain
distinct, learner identity and review purpose stay server-owned, and the same
two API operations remain independently usable by command-line, service, and
future headless clients without rendering this interface.

`/learn/placements/:placementId/practice` establishes the same supported
single-profile session and opens one exact practice activity through the
generated public API client. The browser validates the complete answer-safe
presentation before showing the title, purpose, instructions, attempt-policy
meaning, learning and review material, and ordered single-select,
multiple-select, or fixed-decimal response controls. It also validates the
complete `getPlacedPracticeProgress` response before restoring any partial
answers, retry status, review destination, or attempt history. The learner can
save a valid empty or partial answer snapshot through generated
`savePlacedPracticeDraft`, or check one complete response set through generated
`submitPlacedPractice`. The browser copies exact presentation selectors,
creates one stable submission UUID, and sends no learner, score, time, evidence,
or policy override. An uncertain submission retry reuses the identical prepared
document and UUID rather than reading changed form state.

The page validates and correlates the complete closed result before it shows
the server-returned score, outcome, submitted values, applicable feedback,
review material, saved time, or evidence references. It never compares an
answer with an answer key or calculates correctness. Invalid or private-field-
bearing results fail closed without partial feedback. Incomplete input focuses
the first question to fix; session, stale-version, conflicting, completed,
unavailable, and unexpected outcomes have bounded learner-focused recovery
copy. A conditional draft save uses the current server revision; stale saves do
not replace newer work, and uncertain saves can retry the same snapshot. A
confirmed result refreshes the server-owned progress view before another
attempt is offered. The page shows ordered answer-free attempt summaries,
available internal review lessons, explicit unavailable review material, and
attempt exhaustion without inferring mastery or recommendation meaning.

Exact placement, package, practice, definition, question, policy, choice,
resource, result, attempt, evidence, version, digest, and time facts remain
available under accessible `Technical record` disclosures. The reviewed POST
remains independently usable by command-line, service, and future headless
clients. The page does not define a second contract or a separate AI mode.

The protected progress read returns the nullable server draft, deterministic
retry state, rebuildable attempt history, and latest targeted review
destinations; the protected write conditionally replaces one complete partial-
response snapshot. These operations use the same opaque session and same-origin
boundary for browser and headless clients. The browser adds no competing policy
or browser-only domain core: command-line, service, and future headless clients
can use the same operations without rendering this interface.

The browser never selects the learner, reads the HttpOnly cookie, imports
backend code, parses CommonMark, uses an unsafe HTML sink, or accesses a
database/provider. Theme preference is the only local browser preference
persisted by this slice.

The reviewed generated client also exposes queryless learning-preference
profile, history, and export reads plus the closed mutation operation. These
operations use server-owned learner identity and the same
`learner_preferences.read` or `learner_preferences.write` authorization for
browser and headless callers. `/preferences/learning` now consumes only those
generated operations. The learner can record, edit, order, archive, restore,
remove, reset, review, and export explicit goals, self-described experience,
and interests. The route validates the complete profile and correlated bounded
history before showing private details, uses exact revision and idempotency
envelopes for changes, and preserves an uncertain unchanged request for safe
retry. Changed or malformed responses fail closed without showing a partial
profile or creating a download. Primary content uses learner-task language;
exact identifiers, revisions, times, and integrity codes remain available in
accessible `Technical record` disclosures. The browser adds no learner
selector, authoritative local copy, inference, evidence, competency, adaptive
policy, recommendation, provider, financial, or external-action path.

The isolated approved-lesson qualification exercises this complete route with
Unicode and duplicate learner wording, variable ordering, archive/restore,
confirmed removal, reset, history, export, keyboard and focus behavior, narrow
reflow, themes, forced colors, and reduced motion. It then compares the same
closed profile, history, export, and exact replay through an ordinary
cookie-backed HTTP client, runs all three simultaneous-write outcome classes,
and reopens the retained meaning after a normal host restart. The browser and
headless paths therefore remain two clients of one protected API rather than
separate authorities.

The reviewed generated client also exposes the four learner-owned display-
choice operations for profile, complete replacement or reset, bounded history,
and export. They use server-owned learner identity and
`learner_presentation_preferences.read|write` for browser and headless callers.
The client accepts only the closed text-size, text-spacing, reading-width, and
motion values. It does not carry arbitrary CSS, medical or inferred labels,
evidence, policy, provider, or browser-local theme. The display settings UI and
runtime token application remain clients of this same headless boundary.

The generated client also exposes four protected learner AI-help choice
operations for profile, closed replacement or reset, bounded history, and
export. They use server-owned learner identity and
`learner_assistance_preferences.read|write` for browser and headless callers.
The only values are `off` and `on_request`; no request can select a provider,
grant data permission, call a model, create output, or carry the browser-local
reminder choice. `/preferences/assistance` is a client of this API plus the
separate local adapter, not an alternate authority. It validates one coherent
portable profile/history export before showing learner-owned state and rereads
that export before a download. Its save and confirmed reset send only the
closed mutation document; the same operations remain usable without the UI by
command-line, service, and future headless clients.

The same screen presents a separate future in-app reminder choice owned only
by the existing browser-local adapter. Local save, confirmed reset, and
download never establish a learner session or call the public API; the local
record contains no learner identity and has no headless meaning. Either branch
remains usable when the other is unavailable. The page states that neither AI
help nor reminder delivery is available there today, and it requests no model,
provider, data permission, notification permission, worker, timer, schedule,
subscription, or delivery action. Malformed data fails closed without partial
display or download. Focused component and Chromium coverage verifies separate
authority, reset, download, failure, reload, accessibility, narrow reflow,
scaled text, forced colors, reduced motion, and no execution side effect.
The complete isolated qualification also proves browser and ordinary headless
profile/history/export parity, exact replay, changed-payload conflict, stale-
revision handling, PostgreSQL row correlation, normal host restart, unrelated-
state noninterference, and cleanup. Network and platform observation confirms
that the journey makes no provider or model request, notification-permission
request, service-worker registration, schedule, subscription, or delivery
action. The focused assistance Chromium wrapper is part of affected-candidate
selection whenever this feature or its browser-local adapter changes.

The cumulative preference qualification composes these existing routes without
creating a combined settings API. In one disposable PostgreSQL, production-
host, and pinned-Chromium topology, each learner-owned family changes only its
own profile, change, and replay tables; the other two remain exact. All three
families retain distinct profile identities under one server-owned learner
context, survive restart, and remain available to ordinary headless clients.
Theme and reminder state stay in their two browser-local adapters and never
enter the learner APIs. This proves shared-core semantics for a future
deployment adapter, not managed-cloud operation or a headless AI mode.

`/preferences/display` validates one coherent profile/history export before it
shows private details, previews complete drafts through the four semantic root
attributes, sends one exact complete replacement or confirmed reset, and keeps
the local `system|light|dark` theme explicitly separate. Cancel and navigation
restore the last accepted profile; unavailable or malformed saved state leaves
the application at the complete accessible baseline. Exact version, revision,
times, and digest remain reachable through `Technical record`, and downloads
are produced only from a newly validated export matching the displayed
revision and digest.

The global presentation provider reads the same generated public client on a
fresh browser load and applies only a complete validated profile. It maps
`data-text-size`, `data-text-spacing`, `data-reading-width`, and `data-motion`
to shared design-system tokens on the document root. Browser zoom, text
scaling, forced colors, and more-protective reduced-motion signals retain
precedence. The focused unit, component, and Chromium suites cover all 16 safe
value combinations, draft restore, exact mutation fields, reset/theme
separation, invalid and unavailable fallback, keyboard/focus semantics, axe,
narrow reflow, 200-percent text, forced colors, and reduced motion. Final live
qualification now drives the same generated browser client and ordinary
headless HTTP clients against one Python host and PostgreSQL database. It
applies all 16 safe profiles, confirms preview/cancel/save/reset and local-theme
separation, reads the exact downloaded export, accepts only safe serialized
outcomes under simultaneous writes, and rechecks the profile, history, export,
replay rows, and unrelated source state after a normal host restart. The test
keeps 320-pixel, 200-percent-text, keyboard, forced-color, reduced-motion, axe,
and exact-cleanup evidence in the same disposable workflow.

`/saved-learning` opens the learner's private notes, bookmarks, and collections
through the generated Personal-workspace client. Available opportunity-detail
and lesson pages provide `Save to Saved learning` links that carry only the
closed resource selector to `/saved-learning/new`; learners never type internal
resource identifiers. The flow supports note/bookmark creation and editing,
ordered collection membership, record reordering, archive/restore, and bounded
removal. Collection membership preserves the server-returned learner order and
provides explicit earlier/later controls. The flow closes every complete
workspace response before display, uses the current server revision and a fresh
request identity for each new mutation, and preserves the complete original
request when a response is uncertain so an unchanged retry is idempotent. It never
selects learner, source, package, publication, digest, time, or permission
authority in the browser. Plain task language leads the flow while exact
workspace, record, collection, package, publication, validation, version, and
integrity facts remain available through accessible `Technical record`
disclosures. The same protected API remains independently usable by
command-line, service, and future headless clients; the UI adds no alternate
policy, storage, or AI path. Its generated types also expose the closed Project
workspace, snapshot, and artifact selectors for headless clients. Authorized
Project pages now provide contextual controls for the complete Project,
individual checkpoints, and exact file versions. Those controls carry only the
closed selector to `/saved-learning/new`; the browser derives the safe return
anchor and never accepts a caller-supplied Project destination. Curriculum and
Project records can be organized together without copying Project content or
adding a browser-only policy path.

The reviewed generated client also exposes `exportPersonalWorkspace` as a
direct JSON operation. It accepts no learner, time, digest, storage, or query
input and returns the same closed server-generated export to authenticated
browser and headless callers. The Saved learning page now offers an explicit
`Download saved learning` action. Its injected adapter deep-validates the
closed export, requires its revision and digest to match the workspace on
screen, and only then downloads UTF-8 JSON as
`saved-learning-export.json`. Changed or malformed responses create no file;
plain recovery guidance is announced, while format, generation time, revision,
and integrity details remain available in an accessible technical disclosure.
Distinct record, collection, and collection-member capacity codes explain the
accepted 200, 50, and 100 limits without replacing existing removal or exact
unchanged-request retry controls.

The disposable approved-lesson qualifier also reads the downloaded JSON back,
requires it to equal the generated-browser response, and compares that closed
workspace/digest meaning with a later bodyless headless export call. The
browser and headless clients therefore share one protected API and one export
shape; this does not turn the browser download into a recovery or import file.

The Saved learning screen and reviewed generated client use the protected
`queryPersonalWorkspace` operation and additive `refresh_reference` mutation
shared by browser, command-line, service, and future headless clients. The
browser maps one closed URL state to text, saved-item, source-area, source-type,
source-status, archive, collection, sort, page-size, and opaque-continuation
fields. Unknown, repeated, malformed, or over-broad values fail before learner
session or workspace access. The loader reproduces the server's canonical
Unicode query meaning and SHA-256 digest before it accepts a result. Continuation
links preserve the complete query meaning, and only a complete default result
whose record IDs exactly match canonical workspace order can expose record-
reordering controls.

Each record explains `Ready to open`, `Saved details changed`, or `Source
unavailable` in plain language. Only a ready source exposes its retained
destination; learner notes, bookmarks, collections, and technical history stay
visible for stale and unavailable sources. `Check source` sends only the saved
record ID inside the existing revision/idempotency envelope. The server remains
authoritative for learner, owner access, selector, validation time, replacement
facts, and status. The loader closes both the current workspace and query page,
requires one matching workspace revision, and rejects query records that do not
exactly match the opened workspace rather than mixing two states.

`/projects` lists the learner's current Projects and reviewed learning-based
starting points. `/projects/new` creates either an independent Project or one
bound to the exact current learning brief. `/projects/:projectId` consumes the
generated public client to open the Project shell, live workspace, and saved
checkpoint list as one closed view. It supports bounded notes and HTTPS source
records, inert files up to the accepted limit, explicit original-file
downloads, fixed evidence checkpoints, JSON evidence-record downloads, and
continued live work after a checkpoint. The browser recomputes upload byte
count and SHA-256, verifies downloaded file integrity, closes every returned
record before display, and keeps exact IDs, versions, revisions, and digests in
accessible `Technical record` disclosures. Server authorization, optimistic
revision checks, request replay, provenance rules, snapshot immutability, and
artifact admission remain authoritative in the public API and are equally
available to command-line, service, and future headless clients. Saved-learning
controls link back to stable workspace, checkpoint, and file-version anchors;
malformed, incomplete, or conflicting selectors fail before Project details
are displayed.

For a learning-started Project, each saved checkpoint links to
`/projects/:projectId/learning?snapshot=:snapshotId`. That route reads the
current candidate, retained submission history, and the Audit-reconciled
Learner-model completion projection through generated clients. It lets the
learner map only candidate-owned saved items to every milestone, reopens the
candidate immediately before submission, and reuses the exact request identity
and choices after a bounded refusal or uncertain response. An accepted request
redirects to the exact submission view; earlier submissions remain directly
reopenable. Primary copy states that structural acceptance is not a quality
grade, mastery judgment, competency claim, or financial advice. Exact policy,
snapshot, evidence, provenance, fingerprint, and time facts remain in
accessible `Technical record` disclosures. Saved-resource choices include a
distinct plain-language kind, identifier, and version or observation time;
their complete safe record, content, and owner-reference fingerprints remain
available through nested technical disclosures. Independent Projects expose
no learning-submission action and every direct learning-evidence selector
fails before a completion or evidence read. The same API remains usable headlessly without
rendering this route.

Project files are never executed, expanded, installed, sent to a provider, or
actively rendered. The route does not create live Portfolio state, financial
actions or advice, mastery or competency state, managed-cloud protection, or a
separate AI mode. Assessment evidence and bounded Project-activity completion
remain server-owned results of the public API. Typed records owned
by other modules can be displayed only when the API returns an admitted link;
the browser does not invent one.

The application shell uses the canonical primary sidebar: expanded at wide
desktop widths, compact with labeled hover/focus disclosures at intermediate
desktop widths, and an accessible menu drawer on narrow viewports. `Learn` and
`Projects` are active destinations. Future product areas are visibly marked as
planned and are not exposed as dead links or fictional routes.

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
admits one exact three-shape practice and its placement,
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
same run calls the protected practice GET repeatedly from a cookie-backed
non-browser client, compares bounded Assessment and learner-state storage
counts, and opens the identical answer-safe presentation through the generated
browser client. That browser saves a partial two-shape draft, reloads the same
responses, completes all three shapes, submits one attempt, and displays the
server-owned retry, answer-free history, and review-target state. A fresh
non-browser session reads the identical public progress document, saves and
exactly replays the captured partial snapshot as the next-attempt draft,
proves a different stale save cannot overwrite it, and observes the same state
after normal restart. Exact submission replay preserves both immutable
evidence counts and the newer draft. This proves confidentiality,
accessibility, and restart durability without a browser-only API. The
same live topology also exercises `/saved-learning` through the generated
client, compares the resulting closed workspace with ordinary authenticated
headless HTTP, proves exact replay plus changed-key and stale-revision denial,
checks target-domain count invariance, and reopens the same notes, bookmarks,
ordered collection, provenance, and revision after a normal restart. The live
Project journey runs first, after which contextual controls save the exact
Project workspace, immutable checkpoint, and inert-file manifest alongside a
Curriculum lesson. The qualifier correlates those references to the public
Project capture and PostgreSQL rows, refuses an unavailable Project without
changing unrelated records, excludes artifact bytes and execution actions,
and proves Project state remains unchanged. The
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
education-boundary, exact headless/browser practice opening, progress, draft,
and submission, three response shapes, conditional save, reload, exact replay,
stale conflict, server-owned retry/history/review state, practice storage-count
invariance, restart parity, bounded practice denial, generated-browser/headless
Personal-workspace parity, ordered collection membership, canonical Unicode
query/digest correlation, record-only source checking, exact refresh and final-
mutation replay, confidential changed-key and stale-revision denial, target-
state isolation, Personal-workspace restart durability, and
catalog/detail/comparison/graph/completion/practice axe paths.
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
