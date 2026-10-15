# Backend Hosts

Hosts are thin executable entry points:

- API host
- worker host
- CLI host

Hosts establish configuration, lifecycle, authentication/request/job context, and composition. They invoke public application operations and do not contain feature policy.

The API host exposes the queryless discovery catalog at
`GET /api/v1/curriculum/opportunities`. It resolves the opaque session on the
server, independently requires `curriculum.discovery.read`, invokes the
Curriculum public browse operation, and maps invalid, stale, or unavailable
projection state to bounded responses. Registration and rebuild remain
internal application operations rather than public HTTP mutations.

