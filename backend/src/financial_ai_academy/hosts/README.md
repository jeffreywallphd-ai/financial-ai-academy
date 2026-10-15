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

