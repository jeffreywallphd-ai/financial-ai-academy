# API Contracts

The reviewed OpenAPI 3.1 snapshot is generated from validated API models and
committed here. Generated TypeScript clients must be reproducible from that
snapshot.

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

