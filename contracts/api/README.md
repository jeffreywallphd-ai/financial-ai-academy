# API Contracts

The reviewed OpenAPI 3.1 snapshot is generated from validated API models and
committed here. Generated TypeScript clients must be reproducible from that
snapshot.

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

