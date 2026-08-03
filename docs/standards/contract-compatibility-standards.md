# Contract Compatibility Standards

- Status: accepted
- Canonical for: contract review and compatibility evidence

Every public API, event, provider, plugin, and portable-record change must identify:

- owning contract family,
- current and proposed version,
- additive, deprecating, or breaking classification,
- affected producers and consumers,
- generated artifacts,
- old/new fixtures,
- conformance and compatibility evidence,
- migration or translation boundary,
- documentation and release impact.

Breaking changes require an accepted ADR or explicit compatibility decision. Provider-specific compatibility translation remains in adapters. Domain code operates on current canonical meaning.

