# Contract Architecture

- Status: accepted
- Canonical for: contract classes, sources, generation, and ownership
- Related docs: `compatibility-and-versioning.md`, `provider-and-plugin-contracts.md`

## Contract Classes

| Contract | Representation | Authority |
| --- | --- | --- |
| REST API | OpenAPI 3.1 snapshot | Generated from validated API models and committed for review |
| Events | JSON Schema in a standard event envelope | Schema files under `contracts/events/` |
| Provider/plugin manifests | JSON Schema | Schema files under `contracts/providers/` |
| Portable learning and finance records | JSON Schema | Schema files under `contracts/learning/` and `contracts/finance/` |
| Internal application operations | Typed Python request/result models | Owning module public application surface |
| Frontend client | Generated TypeScript | Generated from reviewed OpenAPI; never hand-edited |

## Ownership

- The platform owns canonical terminology and schemas.
- Providers translate to and from platform contracts.
- A contract has one owning module or cross-cutting owner, a version, compatibility policy, examples, and conformance tests.
- Exact wire shape belongs in executable schemas. Semantic rules and module ownership belong in canonical documentation.

## Generation

- API models generate the OpenAPI snapshot.
- Language-neutral schemas generate or validate Python and TypeScript bindings where practical.
- Generation must be deterministic and reproducible from a documented command.
- CI should fail when generated output differs from committed output.

## Validation

Validate at every trust boundary. Validation confirms shape; application and domain code still enforce semantic invariants and authorization.

