# Platform-Native Content Authoring Workflow Contract

- Status: accepted
- Canonical for: draft, review, preview, publication, retirement, and future interoperability-adapter semantics
- Decision: [ADR-0017](../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
- Published output: [Versioned Lesson Content-Package Contract](content-package-contract.md)

## Purpose

This contract separates mutable creator work from immutable learner-visible
packages. It defines semantic obligations only; exact API and portable record
shapes belong to later executable schemas.

## Ownership and Authority

Content owns the authoring aggregate and coordinates validation, review,
package build, publication, retirement, and audit references. Assessment,
Curriculum, Project, Learner model, and other modules retain their own meaning
and persistence. Authoring reaches them only through public application
operations and exact versioned references.

Only an authorized human review outcome for one exact draft revision can make
that revision eligible for publication. AI, provider, import, automated
validation, and adapter results are inputs, never approval or publication
authority.

## Revision and Review Model

- A stable authoring identity may have many recorded draft revisions.
- Every revision identifies its parent or creation basis, creator context,
  source/license evidence, referenced module versions, assets, validation
  profile, and change provenance.
- Review comments and outcomes bind one exact revision and the reviewer context.
- Any content-affecting or reference-affecting edit creates a new revision and
  prevents an approval of the older revision from authorizing the newer one.
- Conflicting concurrent edits are surfaced as a conflict or explicit merge;
  last-writer-wins cannot silently erase accepted work or review evidence.
- Rejection, requested changes, withdrawal, and supersession remain auditable.

Exact lifecycle labels may evolve, but draft, review, approved-for-publication,
published, and retired meanings cannot be conflated.

## Preview and Validation

Preview renders only the closed, safe intermediate representation admitted by
the target publication profile. It is visibly non-published and cannot create
learner attempts, completion, competency, or project-submission evidence.

Validation covers package shape, ownership references, integrity, sources and
licenses, accessibility requirements, content safety, assessment semantics
through Assessment, compatibility, configured bounds, and immutable-version
conflicts. Failed validation or preview creates no partial publication.

## Publication and Retirement

Publication consumes one authorized, approved exact revision. It deterministically
builds and validates the full platform-native package, then atomically records
one immutable `(package_id, package_version, package_digest)` and associated
provenance. A race, stale review, changed dependency, validation failure, or
identity/version conflict fails closed.

Retirement changes availability without changing package bytes or prior learner
evidence. Recovery or rollback uses an explicit valid version/state transition
and preserves audit history.

## Future Interoperability Port

No external learning-standard profile is currently admitted. A future adapter
must be optional and translate to or from the platform-native authoring/package
contracts. It must emit a bounded deterministic mapping report with standard,
profile, direction, adapter version, source/destination digests, provenance,
and represented, transformed, lossy, unsupported, defaulted, and rejected
elements.

External inputs remain untrusted and cannot bypass native validation, ownership,
safety, accessibility, review, or publication. Provider-specific and standard-
specific payloads stay inside adapters. Adapter absence or failure never blocks
native drafting, review, preview, package build, publication, or native export.

## Failure and Degradation

Malformed, unsafe, stale, conflicting, unauthorized, incomplete, oversized, or
unsupported input fails narrowly with bounded diagnostics and without replacing
valid drafts or published packages. Unsupported content or a future adapter
failure cannot invalidate unrelated valid native content.

## Explicit Non-Scope

Exact wire schemas, UI/editor technology, real-time collaboration, archive
transport, localization, content signing, marketplace behavior, external
standard selection, and organization role policy are not accepted here.
