# Project Module

Project owns learner Project identity, charter, immutable accepted origin,
lifecycle, revision, and—when later slices deliver them—the mutable workspace,
snapshots, and typed domain-resource links. Content owns approved learning-
project brief meaning. Curriculum owns exact placement in a learning path.
Assessment owns only an exact submitted snapshot and its evidence.

The Project seam remains transport-neutral:

- `ContractProjectAdapter.parse_brief` validates immutable Content-owned brief
  bytes and their canonical digest.
- `parse_intent` accepts exactly an independent or learning origin. A learning
  origin must correlate to the exact approved brief supplied by a future
  public Content operation.
- `parse_shell` reconstitutes an immutable learner-safe Project shell without
  requiring the source to remain current.
- document projectors produce the same JSON-compatible contract shapes for
  future API, command-line, browser, service, and headless AI clients.
- `ProjectService.create_project`, `list_projects`, and `open_project` apply
  the same domain policy for every host. Independent creation performs no
  learning lookup; learning creation resolves the exact public Curriculum
  placement and Content brief before persistence.
- `PostgresProjectRepository` owns learner-scoped shell persistence,
  canonical-request idempotency, deterministic list order, and contract
  revalidation on read. It imports no other module repository or schema.
- the protected public API derives learner identity and permissions from the
  server session. Browser and authenticated headless clients use the same
  operations and reviewed OpenAPI contract.

This seam has a Project-owned repository, migration, UTC/UUID adapters, and
public HTTP/client boundary. It still has no browser Project interface, edit,
event, artifact, snapshot, execution, Assessment submission, Learner-model
effect, Portfolio link, provider, or AI authority. Deterministic application
policy remains authoritative when those later boundaries are added.
