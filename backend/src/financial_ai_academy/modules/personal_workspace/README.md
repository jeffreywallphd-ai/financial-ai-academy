# Personal Workspace Module

Personal workspace owns learner-authored notes, bookmarks, collections, and
their organization. Its first seam is a transport-neutral contract and pure
mutation core.

## Current public boundary

- immutable v1 domain values for records, references, collections, and intents;
- `PersonalWorkspaceContractPort` for parsing, projection, canonical digests,
  empty-workspace creation, pure mutation, deterministic record query, and
  trusted reference-refresh transitions;
- `ContractPersonalWorkspaceAdapter`, which validates closed JSON Schema shapes
  and semantic invariants, stable query pages, server-authenticated learner-
  and workspace-bound continuations, and current/stale/unavailable reference
  history;
- `PersonalWorkspaceService`, which serves the same read and mutation
  operations to protected HTTP, generated-client, and future headless callers;
- selector-based Curriculum resolution that keeps target facts under their
  owner and stores no lesson body or permission grant;
- additive Project workspace, immutable snapshot, and inert artifact-manifest
  reference values plus a focused adapter that uses only learner-bound Project
  public reads and never downloads artifact bytes;
- `PostgresPersonalWorkspaceRepository`, which owns current aggregate and exact
  replay state with optimistic revision and atomic first materialization.

The v1 union admits exact Curriculum-owned learning opportunities and placed
lessons plus safe Project workspace, snapshot, and artifact-manifest facts.
One closed dispatcher resolves every selector through its owner's public
surface with server-owned learner and validation-time context. The application
service, protected API, and generated client accept those same selector kinds;
Project-backed creates require `project.read`. The module stores references
rather than target business state and cannot confer access to a target. Its
adapters have no provider, model, external-network, file-content, or execution
dependency.

The protected API/client delivery is the primary product boundary for browser
and headless consumers. Source-bearing creates also require the owning module's
read permission; caller-selected learner query parameters are rejected before
workspace access. The generated-client Saved Learning browser flow and an
ordinary authenticated non-browser client use these same operations. The
current browser creates Curriculum references and exact Project workspace,
checkpoint, and inert-file references from contextual Project controls; the
same reviewed selectors remain available to headless clients. Isolated
PostgreSQL/Python/static-browser qualification directly proves mixed-reference
organization, exact Project correlation, artifact-byte exclusion, confidential
unavailable-Project isolation, exact replay, changed-key and stale-revision
denial, target-state isolation, normal restart without reseeding, and bounded
cleanup without changing this ownership direction.

The application and protected API now compose the query and refresh seam.
`POST /api/v1/personal-workspace/query` performs one pure bounded query over
the server-selected learner aggregate and never calls Curriculum or Project.
The additive record-ID-only `refresh_reference` mutation derives its selector
from retained state. Server permissions become a closed readable-reference-
kind set, so opportunity, lesson, and Project access cannot widen one another.
Exact replay runs before an owner call. Missing permission, removed or denied
targets, absent adapters, and source outages all persist the same confidential
`unavailable` meaning. Trusted refresh preserves package/snapshot/artifact
meaning, records immutable drift as `stale`, and can recover an exact later
result to `available`. Existing JSON aggregate and replay persistence admits
these additive states without a table migration. Browser controls and the
complete isolated live recovery journey remain later SLI-0072 packets.
