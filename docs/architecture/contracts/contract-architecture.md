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
[ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md). The additive
executable family separates the mutable Project workspace, immutable digest-
bound snapshots, and typed references to independently owned learning and
domain resources. A project-domain link never transfers the referenced
aggregate's authority to Project. Content-owned learning briefs and Project-
owned origins retain exact package, brief, Curriculum, and placement versions
and digests.

The Project seam now establishes its shell, workspace, inert-artifact manifest,
snapshot, evidence-export, PostgreSQL persistence, protected HTTP, reviewed
OpenAPI, and generated-client contracts. Workspace reads are side-effect free;
the first authorized mutation or snapshot close creates the empty revision-one
workspace when needed. Artifact upload has its own request shape and validates
the supplied bytes before either acceptance or idempotent replay. Assessment
submission by snapshot reference now has an additive transport-neutral schema,
pure validation, and evidence/event/history projection seam. Persistence,
public API, generated clients, consumers, and browser behavior remain separate
later seams.

Personal learning-workspace records additionally follow
[ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md). Personal
workspace owns learner-authored notes and the lifecycle and organization of
bookmarks, collections, and typed references. Each reference retains exact
owner, resource identity, applicable version or as-of evidence, provenance,
validation time, and bounded availability state, but never embeds target
business state or grants target permission. Owner-specific adapters use public
application operations and degrade independently. Browser and headless clients
share the same protected versioned API and server-owned mutation authority.

The implemented `personal-workspace-v1` family fixes bounded portable records,
exact Curriculum reference provenance, canonical digests, and closed
revision-bound mutation intents behind a pure contract port. It adds no
persistence, identity binding, API, browser, target refresh, or cross-module
mutation.

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
- Browser and non-browser clients consume the same reviewed public APIs. The
  protected practice-progress read and conditional draft save now expose the
  accepted draft, retry, exact review-target, and history meanings without a
  separate AI domain core or client authority over identity, scoring, retry,
  eligibility, or durable state.
- Content owns approved learning-project brief meaning. Project owns accepted
  origin, Project identity, charter, lifecycle, and revision. Curriculum owns
  exact placement and Assessment owns the exact submission, structural
  closure policy, immutable evidence meaning, and safe completion event for a
  submitted snapshot. Shared provenance transfers no persistence or policy
  authority. Structural closure is not qualitative grading or mastery.
- The implemented Project shell seam resolves learning references through
  public Content and Curriculum operations, persists only Project-owned state,
  and exposes one protected API to browser and headless clients. Independent
  creation bypasses those learning lookups; neither path creates Assessment,
  Learner-model, Portfolio, provider, execution, or AI authority.

## Generation

- API models generate the OpenAPI snapshot.
- Language-neutral schemas generate or validate Python and TypeScript bindings where practical.
- Generation must be deterministic and reproducible from a documented command.
- CI should fail when generated output differs from committed output.

## Validation

Validate at every trust boundary. Validation confirms shape; application and domain code still enforce semantic invariants and authorization.
