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
| Automated-development planning authority | ready | [Automated Development Planning](../planning/README.md#authority-model) and DEC-0006 | Use one complete CAP planning-package approval, then refine and deliver slices and packets deterministically; renew CAP approval only for material package change |
| First learning-loop module names and ownership | ready | ADR-0005 and architecture module map | Preserve the accepted Content, Curriculum, Assessment, Learner model, and Audit boundaries |
| Applied-project lifecycle ownership | ready | ADR-0012 and architecture module map | Use Project for learning-initiated and independent workspaces and immutable snapshots; keep Assessment submissions and domain-owned resources separate |
| Project links to portfolios and other domain resources | constrained | ADR-0012 | Permit typed many-valued references without copying domain state; do not implement a live Portfolio link until Portfolio public contracts and semantics are accepted |
| Applied-project artifact handling and experiment execution | constrained | ADR-0011, ADR-0016, and security architecture | Treat project and experiment artifacts as untrusted inert data; use learner-managed export/import and stable provider-neutral run/result semantics; any platform/provider runtime or sandbox still requires a new decision |
| Adaptive-learning authority | constrained | ADR-0014 and adaptive architecture | Use the phased governed portfolio, deterministic eligibility/publication, evidence-only and rule fallbacks, and qualification envelope; concrete model promotion and every online experiment require their own evidence and applicable review |
| Instructor review and learner-projection overrides | constrained | ADR-0019 and instructor review/override architecture | Preserve source evidence and reproducible base projections; permit only registered time-bounded overlays with distinct proposal/confirmation, learner-visible reason/history, expiration/reversal, and no grade, credential, permission, financial, or source mutation; implementation remains blocked on DEC-0016 authorization |
| AI/ML authority | constrained | ADR-0014 and AI/ML boundaries | Adaptive estimation and ranking may use bounded, versioned challengers under deterministic policy; provider, dataset, concrete promotion, and online experiment details remain separately governed |
| Learner identity and local authentication | ready | ADR-0006, identity-provider contract, and local identity security architecture | Preserve setup-selected single-profile, built-in, or OIDC adapters behind one learner-context contract |
| Organization tenancy and database policies | decision-required | Cloud profile | Do not infer tenant or placement policy |
| Cloud platform and deployment tooling | decision-required | Cloud profile | Keep documentation provider-neutral |
| Job queue and delivery guarantees | constrained | ADR-0018 and durable job-delivery contract | Use PostgreSQL-backed at-least-once delivery with leases/fencing, bounded classified retry, idempotent handlers, reconciliation, explicit cancellation/timeout uncertainty, and dead-letter handling; an external broker or different guarantee requires another decision |
| Provider admission and sandbox technology | constrained | ADR-0018 and provider-admission architecture | Admit only exact allowlisted reviewed packaged adapters in the initial in-process trust class; dynamic code discovery, an out-of-process host, elevated trust class, or sandbox requires another decision |
| Market-data providers and licensed uses | constrained | ADR-0020 and market-data licensing/source governance | Use the staged provider-neutral architecture with Alpha Vantage first only inside an exact current educational use profile; keep unspecified storage, cloud, export, redistribution, real-time, and AI/ML uses denied and review every later provider/profile independently |
| Financial analysis, simulated portfolio, and backtest semantics | constrained | ADR-0015 and financial method/simulation architecture | Use Market data and Portfolio ownership plus versioned pure registered methods; exact method/accounting versions need reviewed contracts and fixtures, and live execution/advice remains excluded |
| Model providers and local-model support | constrained | ADR-0013 and AI/ML governance | Local and external adapters require explicit per-provider opt-in, per-data-class permission, current admission evidence, and deterministic fallback; no provider is enabled by default in community |
| External learning standards | constrained | ADR-0017 and content-authoring workflow contract | No external standard is currently admitted or claimed; preserve optional adapter and mapping-report seams, and require a new durable decision before selecting a standard/version/profile |
| Versioned lesson package format | ready | ADR-0007 and versioned lesson content-package contract | Preserve the platform-owned directory model, immutable versions/digests, constrained CommonMark, declared assets, and Assessment ownership |
| Content authoring workflow and external learning interoperability | constrained | ADR-0017 and content-authoring workflow contract | Use platform-native revision-bound drafts, human review, deterministic immutable publication, and narrow adapter degradation; exact contracts remain CAP delivery work and external-standard selection remains decision-required |
| Community learner-evidence protection and recovery | ready | ADR-0008, community security boundary, and community backup/restore design | Preserve private-host protection, coordinated user-invoked recovery sets, empty-target restore, revoked restored sessions/recovery credentials, and no community RPO/RTO claim |
| Managed-cloud encryption, keys, backups, availability, RPO/RTO | decision-required | Managed-cloud profile | Do not infer managed-cloud controls or recovery objectives from the community decision |
| Commercial and dual-licensing structure | decision-required | GPLv3 license and product doc | Obtain qualified legal/product review |

If work reaches a `proposed` or `decision-required` boundary, stop and present options, consequences, and affected contracts. Update this register when an ADR is accepted or superseded.
