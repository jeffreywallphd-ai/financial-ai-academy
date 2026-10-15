# ADR-0011: Keep Applied-Project Artifacts Inert

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0008](../planning/decision-requests/DEC-0008-project-artifact-execution-boundary.md)

## Context

Applied projects need portable datasets, notebooks, code, saved results,
environment declarations, and reflections. The repository has no accepted code
sandbox, execution queue, runtime-image policy, egress or secret model, external
notebook provider, managed-cloud tenancy boundary, or compute cost posture.
Treating uploaded code or notebooks as executable would silently create all of
those obligations.

The first project capability can still preserve useful and reproducible learning
evidence when learners run tools in environments they control and return bounded
artifacts and result claims to the platform.

## Decision

The initial applied-project boundary stores, validates, inspects, downloads,
exports, and restores project artifacts as untrusted inert data. The platform
does not execute them.

- Learners run notebooks, code, analytical tools, and models outside the
  platform in environments they select and control.
- The platform provides no kernel, subprocess, package installation, runtime
  image, network access, secret access, provider callback, or execution job for
  a project artifact.
- Imported artifacts and results remain untrusted learner-supplied evidence.
  Deterministic policy may validate required presence, declared type, normalized
  path, size and count limits, digest, version, provenance, environment and
  dependency declarations, and result classification. Validation does not claim
  that code is safe, that a result is true, or that the platform reproduced it.
- Artifact handling uses a closed platform-owned manifest and content-addressed
  integrity references. Exact schemas and limits belong to executable contracts
  and qualification evidence.
- Unsafe active rendering is prohibited. Any preview must use a separately
  accepted passive renderer and allowlisted media profile; otherwise the
  artifact is available only through bounded metadata and download behavior.
- Paths are normalized and confined, links are not followed, archive expansion
  is not implied, and diagnostics must not expose artifact content, secrets,
  provider credentials, or sensitive host paths.
- Dataset, environment, model, and result records preserve source, version,
  license or use constraints where applicable, assumptions, and whether an
  output is observed, calculated, simulated, predicted, or generated.
- Community and managed-cloud adapters must preserve these semantics. This ADR
  supplies no managed-cloud storage, encryption, recovery, tenancy, quota, or
  service-level authority.

## Consequences

- CAP-0007 can deliver portable applied-project evidence without operating a
  high-risk execution service.
- Learners need external tools, and reproducibility is represented by declared
  evidence rather than guaranteed platform replay.
- Uploaded outputs can be false, malicious, oversized, mislabeled, licensed
  inappropriately, or privacy-sensitive; admission, storage, preview, export,
  and diagnostics must remain fail-closed and bounded.
- Stable artifact and provenance contracts can support a later sandbox or
  provider without changing the meaning of historical inert evidence.
- The platform must clearly distinguish artifact validation from code safety,
  result correctness, independent reproduction, and investment performance.

## Alternatives Rejected

- **Platform-managed isolated execution.** Rejected because it requires
  unresolved sandbox, supply-chain, queue, egress, secrets, quota, cost,
  isolation, cleanup, incident-response, and local/cloud operating decisions.
- **Configured external execution provider.** Rejected because it requires
  unresolved provider terms, learner-data egress, credentials, consent,
  callbacks, availability, cost, and result-normalization decisions.

## Boundaries

This decision does not select exact file formats, maximum sizes, malware tooling,
preview engines, storage implementations, export containers, or dataset
licenses. Those details require bounded contract and security qualification
inside the inert boundary.

Any platform-managed or provider-managed execution, active preview, artifact
egress, secret injection, remote callback, or claim of independent result
reproduction requires a new durable decision and its own security, operations,
provider, cost, and qualification evidence.

## Verification Implications

- Prove that no artifact path can reach a kernel, interpreter, subprocess,
  package installer, network client, secret store, or provider execution port.
- Reject malformed manifests, path traversal, links, unsupported active media,
  digest mismatch, oversized content, excessive file counts, partial writes,
  stale versions, and unauthorized or cross-learner access.
- Exercise interruption-safe admission, content-addressed integrity, immutable
  submission closure, export/import round trips, and restore revalidation.
- Confirm previews are passive and allowlisted, downloads use safe content
  handling, and diagnostics redact artifact content and sensitive paths.
- Preserve provenance and result classification through submission, projection,
  audit reference, export, and replay.

## Supersession

None.
