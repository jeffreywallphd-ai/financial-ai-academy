# Architecture Verification Map

- Status: proposed
- Canonical for: mapping architecture claims to executable evidence

Coverage values are `direct`, `representative`, or `gap`. A general passing test suite does not make a specific architectural claim direct.

| Invariant | Intended evidence | Current coverage |
| --- | --- | --- |
| Domain does not depend on frameworks, hosts, adapters, or provider SDKs | Import/dependency architecture check | gap |
| Modules do not deep-import another module's internals | Public-surface and forbidden-import check | gap |
| REST clients are generated from the reviewed OpenAPI snapshot | Deterministic generation and diff check | gap |
| Events and provider manifests validate against registered schemas | Contract catalog and fixture checks | gap |
| Providers pass reusable conformance suites | Provider-family contract tests | gap |
| Local and cloud use the same domain/application packages | Build and deployment-manifest inspection | gap |
| Adaptation applies deterministic eligibility and policy after ranking | Application tests with unsafe ranking fixtures | gap |
| AI output cannot directly mutate authoritative state | Application-port and use-case boundary tests | gap |
| Portfolio consumes canonical rather than raw provider data | Import and type-boundary checks | gap |
| PostgreSQL is the transactional target in both profiles | Configuration and deployment checks | gap |
| Documentation links, context paths, adjacency, and pack budgets remain valid | `python dev-tools/documentation/check_docs.py` | direct |

Update this map when implementation or verification is introduced. Do not promote coverage without a check that owns the stated invariant.
