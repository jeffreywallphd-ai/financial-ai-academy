# Repository Structure

- Status: accepted
- Canonical for: intended top-level source organization

```text
apps/web/                 TypeScript learner-facing application
backend/                  Python modular monolith and API/worker/CLI hosts
contracts/                Executable language-neutral schemas and snapshots
extensions/               Independently packaged provider implementations
sdk/                      Public provider and client SDKs
data/                     Non-sensitive samples, fixtures, and schemas only
notebooks/                Exploration and evaluation; never production policy
deployments/              Local and cloud deployment profiles
docs/                     Canonical documentation and derived context
dev-tools/                Generation, architecture, docs, and evaluation checks
tests/                    Cross-process end-to-end and deployment tests
```

## Placement Rules

- Start first-party adapters inside the owning backend module. Move one to `extensions/` only when it needs independent installation, versioning, dependencies, or isolation.
- Keep executable schemas in `contracts/`; keep their meaning and evolution rules in `docs/architecture/contracts/` and `docs/contracts/`.
- Keep generated bindings under clearly named `generated/` directories and attach a regeneration command.
- Keep notebooks dependent on public application/data interfaces. Production modules must not import notebooks.
- Do not commit credentials, learner records, licensed market datasets, local databases, model weights without an explicit distribution decision, or generated user artifacts.
