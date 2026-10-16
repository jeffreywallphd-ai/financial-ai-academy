# Project Module

Project owns learner Project identity, charter, immutable accepted origin,
lifecycle, revision, mutable workspace, inert artifact manifests and bytes,
and immutable snapshots. Content owns approved learning-
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
  revision-guarded workspace state, canonical-request idempotency, opaque
  artifact references, immutable snapshot records, deterministic list order,
  and contract revalidation on read. It imports no other module repository or
  schema.
- `ProjectFilesystemObjectStorage` maps Project's owned inert-byte port onto
  the restrictive local content-addressed store with a domain-separated opaque
  key. Application and domain code receive no host path or storage coordinate.
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
per-artifact declaration limit, NFC-normalized logical paths with case-folded
cross-platform collision checks,
credential-free HTTPS references, closed media and classification vocabularies,
canonical direct-UTF-8 digests, exact live
revision preconditions, and server-owned accepted identity/version/time.
Evidence exports bind the complete validated snapshot and workspace records and
their ordered correspondence, use closed embedded schemas, and account for
every snapshot artifact as included or explicitly excluded.

The protected API now exposes workspace read/mutation, inert artifact upload
and safe attachment download, snapshot close/list/read, and evidence export.
All state changes bind an expected live revision and idempotency fingerprint;
exact retries return their accepted record and stale or changed requests do not
overwrite work. Snapshots store the exact closed workspace record and remain
unchanged while later live work continues. OpenAPI and the generated client
give browser and headless consumers the same operations.

This seam does not yet render workspace UI or validate a production domain
owner.
The synthetic Portfolio-named fixture proves only that the provider-neutral
reference shape can represent another owner; no live Portfolio contract,
calculation, authorization, or copied state exists. Project still has no
kernel, subprocess, package, network, secret, runtime, provider-execution,
Assessment submission, completion, Learner-model, or autonomous AI authority.
