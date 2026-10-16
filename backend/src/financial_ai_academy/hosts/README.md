# Backend Hosts

Hosts are thin executable entry points:

- API host
- worker host
- CLI host

Hosts establish configuration, lifecycle, authentication/request/job context, and composition. They invoke public application operations and do not contain feature policy.

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

