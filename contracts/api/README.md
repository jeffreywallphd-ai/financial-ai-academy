# API Contracts

The reviewed OpenAPI 3.1 snapshot is generated from validated API models and
committed here. Generated TypeScript clients must be reproducible from that
snapshot.

`GET /api/v1/learner-assistance-preferences`, `GET
/api/v1/learner-assistance-preferences/history`, `GET
/api/v1/learner-assistance-preferences/export`, and `POST
/api/v1/learner-assistance-preferences/mutations` are the protected AI-help
choice boundary. Reads require `learner_assistance_preferences.read`; mutation
requires `learner_assistance_preferences.write`. All four derive learner
identity from the opaque server session and reject query-selected identity.
The only stored values are `off` and `on_request`; the latter records learner
intent but does not admit a provider, grant data permission, call a model,
create output, or promise availability. Browser and headless clients use the
same reviewed operations. The browser-local reminder setting is not API state.

`GET /api/v1/learner-presentation-preferences`, `GET
/api/v1/learner-presentation-preferences/history`, `GET
/api/v1/learner-presentation-preferences/export`, and `POST
/api/v1/learner-presentation-preferences/mutations` are the protected display-
choice boundary. The reads require
`learner_presentation_preferences.read`; mutation requires
`learner_presentation_preferences.write`. The opaque server session supplies
the learner and all routes reject query-selected authority. The POST accepts
only complete closed replacement or reset with exact expected revision and
idempotency key; arbitrary CSS, scales, theme, medical, evidence, policy,
provider, and model fields fail closed. Empty storage returns deterministic
safe revision-one choices without writing. Exact replay converges, while
changed-key reuse and stale revision write nothing. History retains at most
100 non-content summaries, and export contains the current profile, correlated
history, purpose, limitations, and server export time. Browser, command-line,
service, and future headless callers use the same reviewed OpenAPI operations.
Browser-local `system|light|dark` theme is not API state.

`GET /api/v1/learner-preferences`, `GET
/api/v1/learner-preferences/history`, `GET
/api/v1/learner-preferences/export`, and `POST
/api/v1/learner-preferences/mutations` are the protected Learner-model
preference boundary. The three reads require `learner_preferences.read`; the
mutation requires `learner_preferences.write`. All four bind learner identity
only from the opaque server session and reject query-selected authority. The
POST accepts the closed v1 expected-revision/idempotency envelope and one goal,
experience, interest, ordering, or reset operation. Server time, entry IDs,
next revision, digest, and result are not caller inputs. Exact replay returns
the accepted profile; changed-key reuse, stale revision, limits, missing
entries, integrity failure, and unavailability have stable safe errors. An
absent stored profile returns a deterministic revision-one empty response
without materializing it. History retains at most 100 non-content summaries;
export contains only the current closed profile, bounded history, purpose,
limitations, and server export time. Browser, command-line, service, and
future headless-AI callers use this same reviewed contract; no separate
authority or storage path exists.

`GET /api/v1/personal-workspace`,
`GET /api/v1/personal-workspace/export`, and
`POST /api/v1/personal-workspace/query`, together with
`POST /api/v1/personal-workspace/mutations`, are the protected Personal
workspace boundary. Reads and queries require `personal_workspace.read`;
writes require
`personal_workspace.read` and `personal_workspace.write` permissions and bind
the learner only from the opaque server session. Create-note and
create-bookmark inputs additionally require the owning module's read
permission: `curriculum.discovery.read` for a learning opportunity,
`curriculum.lesson.read` for a placed lesson, and `project.read` for a Project
workspace, immutable snapshot, or inert artifact manifest. They carry one
closed selector; title, route, package, publication, lifecycle, revisions,
digests, validation time, record identity, and other server-owned facts cannot
be selected by a caller. Project selectors never accept content, download,
storage, mutation, export, or execution fields. Exact retry returns the accepted
workspace while stale revision and changed key reuse fail without overwrite.
Both operations reject every query selector; workspace-owned missing records
or collections return the bounded `not_found` result.
The export GET requires `personal_workspace.read`, accepts no body or query
selectors, and returns only `schema_version`, `workspace_digest`, server-issued
`generated_at`, and the complete closed workspace. It exports a virtual empty
workspace without materializing it and includes no session, permission, replay,
storage, target-content, artifact-byte, provider, or execution data. Capacity
refusals use HTTP 409 with exact `record_limit`, `collection_limit`, or
`collection_member_limit` codes and safe removal guidance; they do not replace
the current aggregate or create replay state.
The query POST accepts one closed v1 body and returns normalized query meaning,
bounded records, workspace revision, query digest, and an authenticated opaque
continuation. It never calls Curriculum or Project and accepts no learner,
permission, owner, provider, or storage input. The mutation union also admits
`refresh_reference` with only a record ID. The server derives the retained
selector and exact readable reference kind; unavailable permission, target,
adapter, or source causes collapse to the same stored and public unavailable
status. Only an exact trusted result becomes available, while immutable drift
retains historical facts and becomes stale. Exact replay precedes source
resolution.
The reviewed OpenAPI and generated TypeScript types are identical for browser,
command-line, service, and future headless consumers. No separate AI authority
path is defined.

Project learning submission uses five protected operations on the same shared
API: `GET /api/v1/projects/{project_id}/snapshots/{snapshot_id}/submission-candidate`,
`POST /api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions`,
`GET /api/v1/projects/{project_id}/submissions`, and
`GET /api/v1/projects/{project_id}/submissions/{submission_id}`, plus the
Audit-reconciled Learner-model projection at
`GET /api/v1/projects/{project_id}/completion`. Reads require
`project.read`; submission requires `project.write`. All derive learner
identity from the opaque session and reject query-selected authority. The POST
accepts only the closed v1 milestone-to-snapshot mapping. A structural refusal
returns ordered safe issues with `evidence: null` and writes nothing; an
accepted result returns immutable exact evidence. History omits learner
identity and Project content while retaining exact correlation, provenance,
occurrence, time, and supersession facts. Browser and authenticated headless
clients use the same reviewed operation and generated types. The completion
document always includes its required `projection_version`; a missing version
is an invalid response rather than an implicit default.

`POST /api/v1/projects`, `GET /api/v1/projects`, and
`GET /api/v1/projects/{project_id}` are the protected Project shell boundary.
The POST accepts only the reviewed create intent and derives learner, Project
identity, active lifecycle, revision, and UTC times on the server. Exact
learner/idempotency replay returns the original shell; changed reuse conflicts.
List and read are learner-scoped and guessed cross-learner IDs are ordinary
not-found results. All three operations use the same transport-neutral Project
service for generated browser clients and authenticated headless HTTP clients;
there is no separate AI authority path.

`GET /api/v1/curriculum/placements/{placement_id}/practice` is the protected
answer-safe practice opening. It requires the opaque session and server-issued
lesson-read permission and accepts only the placement path identifier: no body,
query-selected learner, private definition, answer, provider, or version
override is accepted. The closed v1 response carries exact package and practice
provenance, bounded attempt metadata, resource references, and ordered
single-select, multiple-select, or numeric item presentations. It excludes
correct option IDs, numeric answers/ranges, and every feedback branch. Opening
is read-only. The reviewed OpenAPI and generated client are the same contract
for browser and headless HTTP consumers; no separate AI mode is defined.

`GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state`
is the protected exact-version learner navigation read. It requires the opaque
session and server-issued `adaptation.navigation.read`, derives the learner
only from server context, and accepts no learner, permission, policy, provider,
or latest-version selector. The closed v1 response contains every graph
activity in graph order with orthogonal completion, eligibility, requirement,
availability, bounded reasons, and exact graph/policy/source/result
provenance. Unknown exact graphs map to 404; unavailable composition maps to
503 without partial or alternate-version data.

`GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch`
is the protected current activity-launch read. It requires the opaque session
and both existing navigation-read and lesson-read permissions. Its only inputs
are the three exact path identifiers; it accepts no body, query authority,
learner, destination, placement, package, state, policy, or fallback version.
The closed v1 response carries exact graph/projection/package provenance and a
server-derived same-origin lesson destination. Invalid, missing, locked,
unavailable, and unsupported activities return bounded standard errors with no
destination.

`GET /api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}`
is the protected exact-version Curriculum graph read. It uses the opaque
session and server-issued `curriculum.graph.read` permission, accepts no
learner, permission, or latest-version selector, and returns only the closed
graph v1 aggregate. Unknown exact versions map to 404; invalid or unavailable
stored meaning maps to bounded 503 without partial or fallback data.

`GET /api/v1/curriculum/opportunities` is the protected, queryless discovery
browse operation. It requires the opaque session cookie, accepts no learner or
permission selector, and returns the closed discovery v1 envelope with no
provider, database, or learner identity fields.

The additive `GET /api/v1/curriculum/opportunities/query` operation uses the
same cookie and server-issued permission. It accepts bounded general and
prerequisite text, repeated topic/level/kind/availability filters, inclusive
duration bounds, one closed sort, page size, and an opaque cursor. Its closed
page echoes only the Curriculum core's canonical applied query. Invalid query
shape or semantics maps to 400, stale cursors and immutable conflicts map to
409, and invalid, stale, or unavailable projection state maps to 503 without
partial or queryless fallback results.

