# Project Module

Project owns learner Project identity, charter, immutable accepted origin,
lifecycle, revision, and—when later slices deliver them—the mutable workspace,
snapshots, and typed domain-resource links. Content owns approved learning-
project brief meaning. Curriculum owns exact placement in a learning path.
Assessment owns only an exact submitted snapshot and its evidence.

The first additive seam is transport-neutral:

- `ContractProjectAdapter.parse_brief` validates immutable Content-owned brief
  bytes and their canonical digest.
- `parse_intent` accepts exactly an independent or learning origin. A learning
  origin must correlate to the exact approved brief supplied by a future
  public Content operation.
- `parse_shell` reconstitutes an immutable learner-safe Project shell without
  requiring the source to remain current.
- document projectors produce the same JSON-compatible contract shapes for
  future API, command-line, browser, service, and headless AI clients.

This seam has no repository, database, migration, clock, identity resolver,
authorization policy, HTTP operation, generated client, UI, event, artifact,
snapshot, execution, Assessment, Learner-model, Portfolio, provider, or AI
authority. Deterministic application policy remains authoritative when those
later boundaries are added.
