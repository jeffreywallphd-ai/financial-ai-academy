# Local and Cloud Capability Parity

- Status: accepted
- Canonical for: edition relationship and permissible differences

## Invariant

Local and cloud profiles share domain rules, application use cases, contract versions, migrations, and standard provider interfaces.

Identity infrastructure may differ, but every profile uses the same opaque platform actor/learner meaning, server-owned session boundary, and application-authorization contract defined by ADR-0006.

Content storage infrastructure may differ, but every profile uses the same lesson package identity, semantic version, immutable digest, assessment ownership, and safe-rendering contract defined by ADR-0007.

Recovery infrastructure and service levels may differ, but every profile preserves the same installation, learner-binding, append-oriented evidence, exact content-version, projection, and audit meaning. ADR-0008 establishes only the community operational baseline; managed-cloud controls remain separately decision-required.

Application hosting infrastructure may differ, but every profile uses the same ADR-0009 client-rendered React/TypeScript artifacts and Python application/API runtime. Node remains build/test tooling only; a cloud-only Node backend-for-frontend, server-rendering boundary, or framework-owned business API is prohibited without a superseding durable decision.

## Permissible Differences

- infrastructure adapters,
- deployment scale and availability,
- managed identity and organization administration,
- billing and entitlements,
- premium or licensed providers,
- managed monitoring, support, and compliance controls,
- operational automation.

## Prohibited Differences

- contradictory grading, mastery, financial, or portfolio semantics,
- incompatible export formats,
- provider contracts available only through private internal APIs,
- migrations that make local data non-portable without an explicit product decision,
- cloud-only fixes to shared security or integrity defects,
- a separate cloud domain implementation.

Capability discovery is explicit. Clients render unsupported or unavailable capabilities honestly and do not infer entitlement or readiness from deployment type alone.
