# Decision Readiness

- Status: current
- Canonical for: whether architecture-sensitive implementation may proceed

## Values

- `ready`: accepted guidance is sufficient within the stated boundary
- `constrained`: accepted baseline exists; expansion requires another decision
- `proposed`: useful direction but not implementation authority
- `decision-required`: materially different choices remain open

| Area | Readiness | Current authority | Agent action |
| --- | --- | --- | --- |
| Python/TypeScript modular-monolith shape and Python API framework | ready | ADR-0001 | Preserve module-first layers, thin hosts, and the intended FastAPI/Pydantic API boundary |
| Initial Python/TypeScript runtime versions and browser framework | ready | ADR-0009 | Preserve Python 3.14/FastAPI 0.141/Pydantic 2.13 and Node 24/TypeScript 7/React 19/React Router 8 Data Mode/Vite 8 with a static client and no Node production server |
| Contract and provider architecture | ready | ADR-0002 | Use versioned platform-owned seams |
| PostgreSQL plus Parquet/DuckDB data split | ready | ADR-0003 | Preserve store responsibilities |
| Shared local/cloud core | ready | ADR-0004 | Do not create an edition fork |
| First learning-loop module names and ownership | ready | ADR-0005 and architecture module map | Preserve the accepted Content, Curriculum, Assessment, Learner model, and Audit boundaries |
| Adaptive-learning authority | constrained | Adaptive architecture | Deterministic policy is fixed; detailed mastery/ranking models need decisions |
| AI/ML authority | constrained | AI/ML boundaries | Use only bounded, validated capabilities; provider/model details need decisions |
| Learner identity and local authentication | ready | ADR-0006, identity-provider contract, and local identity security architecture | Preserve setup-selected single-profile, built-in, or OIDC adapters behind one learner-context contract |
| Organization tenancy and database policies | decision-required | Cloud profile | Do not infer tenant or placement policy |
| Cloud platform and deployment tooling | decision-required | Cloud profile | Keep documentation provider-neutral |
| Job queue and delivery guarantees | decision-required | Known architecture gaps | Do not select a queue or semantics silently |
| Provider admission and sandbox technology | decision-required | Provider architecture | Preserve trust boundary; select technology through ADR |
| Market-data providers and licensed uses | decision-required | Risk/source governance | Refresh terms and approve each provider/use |
| Model providers and local-model support | decision-required | AI/ML governance | Define capability, data-use, cost, and safety posture first |
| External learning standards | decision-required | Known architecture gaps | Decide required interoperability scope before claiming support |
| Versioned lesson package format | ready | ADR-0007 and versioned lesson content-package contract | Preserve the platform-owned directory model, immutable versions/digests, constrained CommonMark, declared assets, and Assessment ownership |
| Content authoring workflow and external learning interoperability | decision-required | Known architecture gaps | Do not infer mutable authoring or external-standard semantics from the published package contract |
| Community learner-evidence protection and recovery | ready | ADR-0008, community security boundary, and community backup/restore design | Preserve private-host protection, coordinated user-invoked recovery sets, empty-target restore, revoked restored sessions/recovery credentials, and no community RPO/RTO claim |
| Managed-cloud encryption, keys, backups, availability, RPO/RTO | decision-required | Managed-cloud profile | Do not infer managed-cloud controls or recovery objectives from the community decision |
| Commercial and dual-licensing structure | decision-required | GPLv3 license and product doc | Obtain qualified legal/product review |

If work reaches a `proposed` or `decision-required` boundary, stop and present options, consequences, and affected contracts. Update this register when an ADR is accepted or superseded.
