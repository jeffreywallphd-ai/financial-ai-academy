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
  and semantic invariants, stable query pages, query-bound continuations, and
  current/stale/unavailable reference history;
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

The newest pure seam adds no host operation yet. It defines closed query and
query-result documents over the learner's own bounded aggregate and a
record-ID-only refresh intent. Querying never calls Curriculum or Project.
Trusted refresh comparison preserves exact package/snapshot/artifact meaning,
allows bounded mutable Project-workspace facts to advance, and collapses every
missing, removed, denied, unavailable, or absent-adapter cause to one public
`unavailable` status. Application orchestration, PostgreSQL replay, protected
API/OpenAPI/generated-client, browser controls, and live recovery evidence
remain the next SLI-0072 packets.
