---
id: WRK-0001
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0001
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/learning/lesson-package/v1", "contracts/compatibility/lesson-package/v1", "contracts/learning/README.md", "backend/pyproject.toml", "backend/uv.lock", "backend/tests/contract/lesson_package", "docs/architecture/contracts/content-package-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md"]
generated_artifacts: ["backend/uv.lock"]
base_revision: a9503220007fedb9b67113a1b3f1e6e498fc6205
claim_id: WRK-0001:24a92a20-83e6-455d-a9d6-b98f86065bb3
claimed_by: codex-agent
claimed_at: 2026-08-05T00:09:53Z
---

# Agent Work Packet: Establish Executable Lesson-Package Contracts

## Objective and Deliverable

Create the minimum executable version 1 lesson-package contract for SLI-0001: reviewed JSON Schemas, deterministic package-index and digest rules, a reusable conformance runner, and positive and hostile fixtures. The observable deliverable is a platform-neutral package corpus that accepts one approved lesson and deterministically rejects malformed, unsafe, unsupported, oversized, or integrity-invalid packages before any application or storage behavior depends on it.

## Required Context

Before changing files, prominently read and follow every applicable `AGENTS.md` and the repository-root `docs/README.md`. Route through `docs/context/packs/index.pack.md` with `architecture-contracts` as the primary pack and `security-risk` as the adjacent pack. Inspect SLI-0001, ADR-0005, ADR-0007, the content-package and compatibility contracts, `contracts/README.md`, `contracts/learning/README.md`, the current backend scaffold, affected tests, and the nearest READMEs.

## Decisions and Assumptions

- ADR-0007's directory model, immutable `(package_id, package_version, package_digest)` relationship, constrained CommonMark profile, declared passive assets, untrusted-input posture, and Content/Assessment ownership split are fixed.
- Version 1 covers manifest identity/version data, objectives, educational-source provenance, one lesson-body declaration, opaque assessment-file declarations needed for package closure, and declared PNG/JPEG/WebP assets. Assessment item meaning and runtime scoring are not introduced.
- `package_digest` is publication metadata computed by Content; it is not self-declared inside `manifest.json`. This avoids a circular digest while preserving the immutable publication tuple.
- The logical package index contains every package file exactly once and sorts normalized paths by UTF-8 byte order. Each entry has the fixed keys `path`, `media_type`, `size_bytes`, and lowercase `sha256`. Serialize the array as UTF-8 JSON with lexicographically sorted object keys, no insignificant whitespace, and no trailing newline, then hash those bytes with SHA-256. Committed cross-language vectors fix the exact bytes.
- Initial admission limits are 128 files, 32 MiB total measured bytes, 8 MiB per file, 256 KiB for the manifest, 1 MiB for lesson CommonMark, and 16 megapixels per raster image. A required implementation dependency that cannot enforce these limits or the accepted parser profile is a stop condition.
- Python dependency management uses `uv` with exact resolution in `backend/uv.lock`. Parser, schema, and media-inspection libraries remain replaceable implementation dependencies and require license, provenance, and security review before the packet can close.

## In Scope

- Draft 2020-12 schemas for the version 1 manifest, source/provenance records, file declarations, passive image declarations, and the minimum structural assessment-file references.
- Conservative path normalization, file-set closure, media-type sniffing, measured-size, per-file digest, package-index, package-digest, version/capability, CommonMark profile, HTTPS locator, and resource-limit validation.
- A representative approved introductory lesson fixture, deterministic digest vectors, and fixtures for every relevant denial path.
- A dependency-light Python contract runner and focused tests that are callable independently of Content persistence.
- Contract catalog, semantic documentation, and verification-map updates made necessary by the exact executable shape.

## Out of Scope

- Content or Curriculum application operations, publication persistence, filesystem object storage, PostgreSQL schemas, API routes, generated clients, or learner UI.
- Assessment item schemas, answer validation, scoring, attempts, completion evidence, or learner-state projection.
- Archive transport, remote imports, authoring, localization, signing, additional media, SVG, PDF, audio, video, active content, or external learning standards.
- Dependency installation, network access, publication, or implementation outside the declared scope without the later implementation gate.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Portable contracts | `contracts/` catalog and compatibility policy | `contracts/learning/lesson-package/v1/` | Exact version 1 package shapes |
| Conformance corpus | Existing compatibility fixtures | `contracts/compatibility/lesson-package/v1/` | Stable positive, negative, and digest vectors |
| Contract runner | Backend scaffold and dependency rules | `backend/tests/contract/lesson_package/` | Executable boundary evidence without application policy |
| Dependency metadata | ADR-0009 and backend README | `backend/pyproject.toml`, `backend/uv.lock` | Reproducible Python 3.14 test environment |
| Canonical docs | Content-package contract | Named contract and verification documents in `write_scope` | Synchronize exact delivery rules and evidence status |

## Contracts and Interfaces

The packet produces immutable version 1 schema identifiers, normalized-path rules, a fixed package-index byte algorithm, digest vectors, resource limits, safe-markup rules, structured diagnostic codes, and a representative package fixture. WRK-0002 consumes only these accepted artifacts; it must not reinterpret or duplicate them in persistence models.

Diagnostics expose stable codes and bounded file/package references but never raw untrusted markup, filesystem paths outside the logical package, stack traces, or file bytes. Unknown security-relevant capabilities fail closed.

## Dependencies and Parallel Safety

There is no preceding work packet. This packet establishes the compatibility-sensitive input for every later packet and therefore has no parallel-safe peer. WRK-0002 may start only after the schemas, digest vectors, resource limits, and conformance corpus are stable and this packet has completed its own verification.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Approved package | The reviewed lesson fixture contains normalized declared files and matching metadata | The conformance runner validates and indexes it | Validation succeeds and the package digest exactly matches the committed vector across repeated runs | Schema, semantic, and digest-vector tests |
| Deterministic ordering | The same logical files are presented in different enumeration orders | Both packages are indexed | Canonical index bytes and package digest are identical | Reordering fixture test |
| Malformed or unsupported input | Shape, schema version, capability, or semantic identifiers are invalid | Admission validation runs | Validation fails with a stable bounded diagnostic | Negative schema fixtures |
| Unsafe paths or file sets | A package contains traversal, absolute, hidden, linked, colliding, missing, duplicate, or extra paths | Closure validation runs | The entire package is rejected before publication | Path and closure corpus |
| Unsafe content | CommonMark contains raw HTML, an active construct, unsafe URL, undeclared asset, or implicit fetch | Markup validation runs | The package is rejected; no renderer-ready result is emitted | Renderer-security corpus |
| Integrity or media mismatch | Bytes, declared size, digest, extension, or sniffed type disagree | Integrity validation runs | The package is rejected with no partial accepted state | Integrity/media fixtures |
| Resource exhaustion | File count, individual size, total size, manifest/body size, nesting, or image pixels exceed limits | Validation runs | Processing stops within bounded resources and emits a safe diagnostic | Limit tests |
| Immutable conflict vector | One package identity/version is represented by two logical digests | Compatibility fixtures are evaluated | The conflict is identifiable for rejection by the Content owner | Immutable-conflict fixture |

## Verification Commands

```powershell
uv sync --project backend --frozen
uv run --project backend pytest backend/tests/contract/lesson_package
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

The packet must also run dependency license and vulnerability inspection using the selected locked toolchain. Any external advisory or registry lookup requires separate network authority and must be reported if not performed.

## Documentation and Evidence Update

Update `contracts/learning/README.md`, the content-package contract, architecture verification map, and known verification gaps only for claims directly established by the executable corpus. Do not upgrade storage, API, UI, local/cloud, or end-to-end coverage. Keep SLI-0001 and the planning register synchronized only when lifecycle state changes.

## Stop Conditions

- Exact schema or digest work would broaden ADR-0007 or create Assessment runtime semantics.
- Canonical JSON/index bytes cannot be reproduced across independent implementations.
- A parser or media dependency requires raw HTML, implicit network/filesystem access, unbounded processing, or an incompatible license.
- Security-relevant unknowns would be accepted rather than rejected.
- The work requires archive extraction, authoring, remote import, signing, or another out-of-scope policy.
- Canonical sources conflict, verification exposes a new durable decision, or another active packet overlaps the declared scope.

## Required Handoff

Report schema identifiers, every exact compatibility-sensitive rule, digest-vector bytes and results, fixture inventory, dependency and license evidence, commands and outcomes, documentation changes, residual parser/media risks, and all deliberately unsupported capabilities.

## Planning History

- 2026-08-04: Shaped from SLI-0001 boundary seam 1; planning approval and implementation activation remain separate local-only stages.
