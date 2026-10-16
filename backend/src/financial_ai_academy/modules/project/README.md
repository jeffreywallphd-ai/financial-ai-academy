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
- `ProjectService.create_project`, `list_projects`, `open_project`, and the
  list/exact learning-start reads apply
  the same domain policy for every host. Independent creation performs no
  learning lookup; learning creation resolves the exact public Curriculum
  placement and Content brief before persistence.
- `PostgresProjectRepository` owns learner-scoped shell persistence,
  canonical-request idempotency, deterministic list order, and contract
  revalidation on read. It imports no other module repository or schema.
- the protected public API derives learner identity and permissions from the
  server session. Browser and authenticated headless clients use the same
  operations and reviewed OpenAPI contract.
- learning-start listing stays bounded to exact Curriculum placements and
  resolves each safe title, purpose, and immutable origin through public
  Curriculum and Content operations. It creates no learner state.

This seam has a Project-owned repository, migration, UTC/UUID adapters, and
public HTTP/client boundary. The browser now composes list, create, and reopen
pages exclusively through that generated client; it adds no browser-only
authority.

The additive workspace contract seam now defines framework-free immutable
values and parser/projector behavior for bounded notes, HTTPS references,
inert-artifact manifests, typed domain-resource references, snapshot closure,
and evidence-export manifests. It fixes conservative counts and a 10 MiB
per-artifact declaration limit, NFC-normalized cross-platform logical paths,
credential-free HTTPS references, closed media and classification vocabularies,
canonical direct-UTF-8 digests, exact live
revision preconditions, and server-owned accepted identity/version/time.
Evidence exports bind the complete validated snapshot and workspace records and
account for every snapshot artifact as included or explicitly excluded.

This contract seam does not yet persist workspace metadata or bytes, expose a
workspace API, validate a production domain owner, or render workspace UI.
The synthetic Portfolio-named fixture proves only that the provider-neutral
reference shape can represent another owner; no live Portfolio contract,
calculation, authorization, or copied state exists. Project still has no
kernel, subprocess, package, network, secret, runtime, provider-execution,
Assessment submission, completion, Learner-model, or autonomous AI authority.
