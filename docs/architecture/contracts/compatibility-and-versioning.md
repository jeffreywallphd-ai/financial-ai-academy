# Compatibility and Versioning

- Status: accepted
- Canonical for: public contract evolution

## Policy

- Public contracts use semantic versions at the contract-family level.
- Additive optional fields and new capabilities are normally backward compatible.
- Removing or renaming fields, narrowing accepted values, changing meaning, or changing required behavior is breaking.
- Consumers ignore documented unknown additive fields while rejecting unknown operation or capability identities when safety depends on exact recognition.
- Deprecation identifies a replacement, migration path, observation period, and removal version.

## Evidence

Compatibility changes require:

- schema diff classification,
- representative old and new fixtures,
- provider and consumer conformance tests,
- generated-client regeneration,
- migration or dual-read/dual-write analysis when persistence is affected,
- release-note and architecture/context updates.

Breaking changes require an accepted ADR or explicit compatibility decision. Version translation belongs at adapters or migration boundaries, not throughout domain behavior.

Published lesson packages additionally preserve the immutable identity/version/digest rule in the [content-package contract](content-package-contract.md). A new schema version does not authorize mutation of an existing package version or silent substitution of a newer lesson or assessment.
