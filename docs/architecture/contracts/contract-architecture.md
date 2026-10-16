# Contract Architecture

- Status: accepted
- Canonical for: contract classes, sources, generation, and ownership
- Related docs: `compatibility-and-versioning.md`, `provider-and-plugin-contracts.md`, `job-delivery-contract.md`, `identity-provider-contract.md`, `content-package-contract.md`, `content-authoring-workflow-contract.md`

## Contract Classes

| Contract | Representation | Authority |
| --- | --- | --- |
| REST API | OpenAPI 3.1 snapshot | Generated from validated API models and committed for review |
| Events | JSON Schema in a standard event envelope | Schema files under `contracts/events/` |
| Provider/plugin manifests | JSON Schema | Schema files under `contracts/providers/` |
| Portable learning and finance records | JSON Schema | Schema files under `contracts/learning/` and `contracts/finance/` |
| Internal application operations | Typed Python request/result models | Owning module public application surface |
| Frontend client | Generated TypeScript | Generated from reviewed OpenAPI; never hand-edited |

Portable versioned lesson packages additionally follow the [content-package contract](content-package-contract.md). Its logical package, immutability, integrity, ownership, and safe-rendering rules are canonical; exact field shapes belong in later executable JSON Schemas.

Mutable platform-native authoring additionally follows
[ADR-0017](../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
and the [content-authoring workflow contract](content-authoring-workflow-contract.md).
Draft revisions, review outcomes, preview, and future mapping reports remain
separate from immutable published packages. External-standard payloads stay in
optional adapters and cannot become platform content authority.

Portable applied-project artifacts additionally follow
[ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md). Project
manifests, environment declarations, datasets, notebooks, code, and results are
untrusted inert data; exact field shapes, limits, and media profiles belong in
later executable schemas and conformance tests.

Financial AI/ML experiment plans, run bundles, execution-provenance records,
and result bundles additionally follow
[ADR-0016](../../adr/ADR-0016-learner-managed-experiment-execution.md) and the
[experiment execution boundary](../ai-ml/experiment-execution-boundary.md).
Their meaning stays provider-neutral so learner-managed export/import and a
future optional execution adapter can share one contract family. These
contracts do not authorize execution, carry secrets, or expose provider job
payloads as domain meaning.

Durable asynchronous work additionally follows
[ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
and the [job-delivery contract](job-delivery-contract.md). Application modules
depend on versioned job operations and canonical at-least-once state meaning,
not PostgreSQL rows, future broker receipts, or provider job payloads.

Reusable project records additionally follow
[ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md). Exact schemas will
separate the mutable Project workspace, immutable digest-bound snapshots,
Assessment submissions by snapshot reference, and typed references to
independently owned learning and domain resources. A project-domain link never
transfers the referenced aggregate's authority to Project.

Portable financial methods, portfolio records, and simulation results
additionally follow
[ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md) and the
[financial method and simulation architecture](../finance/financial-method-and-simulation-architecture.md).
Every registered method has one semantic owner, stable ID/version, explicit
units/time/adjustment/missing/precision semantics, limitations, provenance, and
golden fixtures. Portable records distinguish observed, assumed, calculated,
and simulated values and cannot expose provider payloads as platform meaning.

## Ownership

- The platform owns canonical terminology and schemas.
- Providers translate to and from platform contracts.
- A contract has one owning module or cross-cutting owner, a version, compatibility policy, examples, and conformance tests.
- Exact wire shape belongs in executable schemas. Semantic rules and module ownership belong in canonical documentation.
- Assessment owns mutable practice-draft and deterministic retry-state
  contracts; Curriculum owns exact practice-review targets; Learner model owns
  rebuildable practice-history projections. Their shared provenance does not
  transfer table access or policy authority between modules.
- Browser and non-browser clients consume the same reviewed public APIs when
  those APIs are implemented. Contract families do not create a separate AI
  domain core or grant a client authority over identity, scoring, retry,
  eligibility, or durable state.

## Generation

- API models generate the OpenAPI snapshot.
- Language-neutral schemas generate or validate Python and TypeScript bindings where practical.
- Generation must be deterministic and reproducible from a documented command.
- CI should fail when generated output differs from committed output.

## Validation

Validate at every trust boundary. Validation confirms shape; application and domain code still enforce semantic invariants and authorization.
