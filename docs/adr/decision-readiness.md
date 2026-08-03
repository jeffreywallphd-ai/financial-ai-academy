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
| Python/TypeScript modular-monolith shape | ready | ADR-0001 | Preserve module-first layers and thin hosts |
| Contract and provider architecture | ready | ADR-0002 | Use versioned platform-owned seams |
| PostgreSQL plus Parquet/DuckDB data split | ready | ADR-0003 | Preserve store responsibilities |
| Shared local/cloud core | ready | ADR-0004 | Do not create an edition fork |
| Initial module names and ownership | proposed | Architecture module map | Validate through domain discovery before implementation |
| Adaptive-learning authority | constrained | Adaptive architecture | Deterministic policy is fixed; detailed mastery/ranking models need decisions |
| AI/ML authority | constrained | AI/ML boundaries | Use only bounded, validated capabilities; provider/model details need decisions |
| Identity and local authentication | decision-required | Known architecture gaps | Present options before implementation |
| Organization tenancy and database policies | decision-required | Cloud profile | Do not infer tenant or placement policy |
| Cloud platform and deployment tooling | decision-required | Cloud profile | Keep documentation provider-neutral |
| Job queue and delivery guarantees | decision-required | Known architecture gaps | Do not select a queue or semantics silently |
| Provider admission and sandbox technology | decision-required | Provider architecture | Preserve trust boundary; select technology through ADR |
| Market-data providers and licensed uses | decision-required | Risk/source governance | Refresh terms and approve each provider/use |
| Model providers and local-model support | decision-required | AI/ML governance | Define capability, data-use, cost, and safety posture first |
| External learning standards | decision-required | Known architecture gaps | Decide required interoperability scope before claiming support |
| Content authoring/package format | decision-required | Known architecture gaps | Do not invent a durable format during feature work |
| Encryption, keys, backups, RPO/RTO | decision-required | Security/operations maps | Require explicit threat and recovery decisions |
| Commercial and dual-licensing structure | decision-required | GPLv3 license and product doc | Obtain qualified legal/product review |

If work reaches a `proposed` or `decision-required` boundary, stop and present options, consequences, and affected contracts. Update this register when an ADR is accepted or superseded.

