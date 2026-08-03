# Local and Cloud Capability Parity

- Status: accepted
- Canonical for: edition relationship and permissible differences

## Invariant

Local and cloud profiles share domain rules, application use cases, contract versions, migrations, and standard provider interfaces.

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

