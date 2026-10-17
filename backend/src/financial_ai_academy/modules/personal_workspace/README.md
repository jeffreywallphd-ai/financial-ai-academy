# Personal Workspace Module

Personal workspace owns learner-authored notes, bookmarks, collections, and
their organization. Its first seam is a transport-neutral contract and pure
mutation core.

## Current public boundary

- immutable v1 domain values for records, references, collections, and intents;
- `PersonalWorkspaceContractPort` for parsing, projection, canonical digests,
  empty-workspace creation, and pure mutation;
- `ContractPersonalWorkspaceAdapter`, which validates closed JSON Schema shapes
  and semantic invariants.
- `PersonalWorkspaceService`, which serves the same read and mutation
  operations to protected HTTP, generated-client, and future headless callers;
- selector-based Curriculum resolution that keeps target facts under their
  owner and stores no lesson body or permission grant;
- `PostgresPersonalWorkspaceRepository`, which owns current aggregate and exact
  replay state with optimistic revision and atomic first materialization.

Only exact Curriculum-owned learning opportunities and placed lessons are
admitted in v1. The module stores references rather than target business state
and cannot confer access to a target. It imports no other module internals and
has no provider, model, external-network, file, or execution dependency.

The protected API/client delivery is the primary product boundary for browser
and headless consumers. A later CAP-0017 packet adds the browser experience
without changing this ownership direction.
