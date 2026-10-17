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

Only exact Curriculum-owned learning opportunities and placed lessons are
admitted in v1. The module stores references rather than target business state
and cannot confer access to a target. It imports no other module internals and
has no repository, migration, network, clock, random, provider, model, or host
dependency.

Later CAP-0017 packets add persistence, protected API/client delivery, target
adapters, and browser experience without changing this ownership direction.
