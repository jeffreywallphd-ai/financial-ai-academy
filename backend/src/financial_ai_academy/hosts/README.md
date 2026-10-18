# Backend Hosts

Hosts are thin executable entry points:

- API host
- worker host
- CLI host

Hosts establish configuration, lifecycle, authentication/request/job context, and composition. They invoke public application operations and do not contain feature policy.

The API host exposes Project shell creation, list, and exact read at
`POST /api/v1/projects`, `GET /api/v1/projects`, and
`GET /api/v1/projects/{project_id}`. It derives learner identity from the
opaque session, requires `project.create` or `project.read`, and delegates to
the Project public operations. The POST accepts no Project ID, learner,
lifecycle, revision, time, permission, storage, Assessment, Portfolio, provider,
or execution authority. These routes are the shared browser and headless HTTP
boundary; the host contains no alternate AI policy.

Project workspace operations extend that same boundary under
`/api/v1/projects/{project_id}`. `GET /workspace` opens the learner's bounded
workspace; `POST /workspace/mutations` applies one revision-bound note,
reference, or admitted link mutation; and `POST /artifacts` validates an inert
artifact manifest plus bounded canonical-base64 content. Exact artifact reads
use `/artifacts/{artifact_id}/versions/{artifact_version}` and always return an
attachment with `nosniff`, integrity, and declared-media metadata rather than
active inline content. Snapshot close/list/read and export operations live
under `/snapshots`. Writes require `project.write`; reads require
`project.read`. Every operation derives the learner from the opaque session and
is directly available to generated and non-browser/headless clients.

Saved-learning operations use the same API-first boundary.
`GET /api/v1/personal-workspace` opens the bounded learner aggregate,
`POST /api/v1/personal-workspace/query` applies a closed versioned search and
continuation document without consulting a source owner, and
`POST /api/v1/personal-workspace/mutations` includes the record-ID-only
`refresh_reference` operation. The host derives learner identity and readable
reference kinds from the opaque session; callers cannot supply learner,
permission, owner, selector, replacement facts, status, time, provenance, or
destination. Refresh without the exact owner-read permission follows the same
confidential unavailable transition as a missing, denied, removed, absent, or
failing source. Generated browser and ordinary headless clients use one
reviewed contract and no separate AI authority path.

Learning-started snapshot submission adds an Assessment-owned boundary beneath
the same Project resource. An exact snapshot candidate is read at
`/snapshots/{snapshot_id}/submission-candidate`; a closed mapping is posted to
`/snapshots/{snapshot_id}/submissions`; retained ordered history and exact
evidence are read from `/submissions` and `/submissions/{submission_id}`. The
bounded Project-activity completion projection is read at `/completion`; the
host first proves Project ownership, asks Audit to reconcile the public replay,
and then opens the Learner-model projection. The host only binds session
learner, permission, and route selectors before calling public operations.
Candidate assembly, deterministic validation,
side-effect-free refusal, replay, occurrence, supersession, and persistence
remain in the shared application core. Responses contain no workspace body,
artifact bytes, storage path, execution control, grading, mastery, or provider
authority. These operations are directly usable without the browser.

The API host exposes the queryless discovery catalog at
`GET /api/v1/curriculum/opportunities` and the additive bounded query at
`GET /api/v1/curriculum/opportunities/query`. It resolves the opaque session on
the server, independently requires `curriculum.discovery.read`, and invokes
the corresponding Curriculum public operation. Invalid query shape or
semantics maps to 400, stale cursors and immutable conflicts map to 409, and
invalid, stale, or unavailable projection state maps to 503 without partial or
queryless fallback results. Registration and rebuild remain internal
application operations rather than public HTTP mutations.

The API host also exposes the exact approved graph at
`GET /api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}`.
It independently requires `curriculum.graph.read`, accepts no identity,
permission, or fallback-version selector, and maps unknown versions to bounded
404 responses while corrupt or unavailable stored meaning maps to 503. Graph
admission remains an internal Curriculum operation.

The API host exposes the computed-on-read projection at
`GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state`.
It requires `adaptation.navigation.read`, resolves the learner only from the
opaque server-side session, and accepts no learner, permission, policy,
provider, or latest-version selector. The host maps the closed Adaptation
projection without recomputing state; exact graph absence maps to 404 and
unavailable source composition maps to 503 without a partial result.

The API host also exposes the current activity-launch decision at
`GET /api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch`.
It requires both `adaptation.navigation.read` and `curriculum.lesson.read`,
accepts no request body or authority query, and delegates the exact learner,
curriculum version, and activity to Adaptation. Missing activities map to 404,
locked or unsupported activities to 409, and unavailable current sources to
503. Every refusal omits a destination.

The isolated approved-lesson qualification calls this launch operation
directly and through the generated browser client across two exact curriculum
versions. It verifies the server-derived same-origin lesson destination,
complete return context, completion/current-state refresh, bounded refusal
confidentiality, explicit exact-source reuse, and changed-placement isolation.
The host remains usable without the browser; no UI-only policy or durable launch
state is introduced.

The API host exposes answer-safe practice opening at
`GET /api/v1/curriculum/placements/{placement_id}/practice`. It requires the
server-resolved learner session and current lesson-read permission, accepts no
learner, answer, policy, or version fallback selector, and delegates exact
placement/content resolution to Assessment through public module seams.
Unknown placements map to bounded 404 responses and unavailable or invalid
definitions to bounded failures without partial questions or private answers.

Whole-attempt submission is available at
`POST /api/v1/curriculum/placements/{placement_id}/practice/submissions`.
The same session and same-origin boundary supplies learner identity, rejects
route/body mismatch and caller-selected authority, and forwards the closed
versioned document to Assessment. The response returns ordered submitted
values, score, applicable reviewed feedback, review references, server evidence
IDs, exact public provenance, and time. It excludes learner identity, the
internal request fingerprint, correct answers, evaluator declarations, and
private diagnostics. The reviewed OpenAPI operation is directly usable without
the browser and is the only generated-client seam later UI work may call.

The isolated qualification calls the same operation repeatedly from a
cookie-backed non-browser HTTP client and through the generated browser client.
It proves exact three-shape provenance, absence of private answer/scoring/
feedback fields, unchanged Assessment and learner-state counts, bounded denial,
and stable meaning after a normal host restart without reseeding. This preserves
the API for future headless consumers without defining a separate AI mode.

Practice resume and comparison state is available at
`GET /api/v1/curriculum/placements/{placement_id}/practice/progress`. The host
uses the opaque session learner, composes the current Assessment draft and
retry state with the Learner-model history, and resolves only the latest
attempt's incorrect-item review references through Curriculum. Repeated
references deduplicate in stable item/reference order. Empty or all-correct
history returns no review targets, and an absent exact mapping remains an
explicit unavailable target rather than a ranked substitute.

`PUT /api/v1/curriculum/placements/{placement_id}/practice/draft` conditionally
saves one complete accepted draft snapshot. The route and body placement must
match, and the same-origin boundary supplies the learner rather than accepting
identity, revision, or time authority from a client. Both operations use the
reviewed OpenAPI/generated-client seam and are directly callable by browser or
headless clients. The host does not read module tables, score responses, infer
mastery, or create a separate AI mode.

Learning lineage is exposed at `POST /api/v1/audit/learning-lineage`. The
closed discriminated request names either one exact published lesson or one
exact knowledge-check completion occurrence. The host derives the learner
from the opaque session for completion reads, requires both
`audit.lineage.read` and `curriculum.lesson.read`, and delegates composition to
Audit through public Content and Assessment operations. Responses preserve the
bounded canonical graph and explicit incomplete links while excluding lesson
bodies, answers, feedback, learner identity, provider payloads, storage
locators, and permission state. Browser and authenticated headless clients use
the same reviewed OpenAPI operation; a caller cannot select a learner or gain
new authority through the lineage request.

