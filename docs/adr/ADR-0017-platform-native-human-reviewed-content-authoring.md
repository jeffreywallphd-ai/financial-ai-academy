# ADR-0017: Platform-Native Human-Reviewed Content Authoring

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0015](../planning/decision-requests/DEC-0015-content-authoring-and-interoperability-workflow.md)
- Extends: [ADR-0007](ADR-0007-platform-owned-versioned-lesson-package.md)

## Context

ADR-0007 defines the immutable published lesson package but intentionally does
not define mutable authoring, review, publication, or external learning-standard
interoperability. CAP-0021 needs a path from creator work to reviewed published
packages without making a database representation, editor format, provider
payload, or external standard the new content authority.

The initial workflow should minimize the semantic gap from the existing package
contract. It should also preserve an honest extension point for future import
or export adapters without committing the product to a standard or making an
unsupported adapter a prerequisite for native publication.

## Decision

Use platform-native drafts with explicit human review and publication as the
initial content-authoring workflow.

- Content owns the authoring aggregate, draft identity, revision history,
  review/publication orchestration, package build, publication state, source and
  license provenance, and audit references.
- A draft is mutable only through recorded revisions. Each review targets one
  exact immutable draft revision and exact referenced Assessment, Curriculum,
  Project, competency, source, asset, and policy versions.
- Editing a reviewed revision creates a new revision and invalidates approval
  for the older revision as publication authority. Stale, conflicting, partial,
  or unauthorized review state cannot publish.
- Preview uses the same closed content and validation profiles intended for
  publication but remains visibly non-published. Preview does not bypass
  validation, execute active content, or create learner evidence.
- Publication is a deterministic application operation that requires an
  authorized human review outcome for the exact revision, rebuilds and validates
  the complete platform-native package, and atomically creates an immutable
  package version under ADR-0007. It never rewrites a published version.
- Retirement changes availability through an explicit state transition; it does
  not delete or mutate published bytes, referenced learner evidence, or audit
  history. Rollback publishes or reactivates an explicit valid version rather
  than changing history.
- Structured assessments, curriculum placement, projects, competency mappings,
  and other cross-module meaning remain owned by their modules. The authoring
  workflow coordinates through public application operations and versioned
  references; it does not copy their persistence or become a second scoring,
  prerequisite, project, or learner-state authority.
- AI may produce a bounded attributed draft proposal. AI output is untrusted,
  versioned input and cannot satisfy human review, authorize publication, or
  mutate a published package.

### Future Interoperability Seam

The platform-native authoring and package contracts remain canonical. A future
external-standard adapter may translate through a versioned import/export port,
but provider or standard payloads never become domain records.

The seam preserves:

- explicit standard name, version, profile, direction, and adapter version;
- source identity, license, attribution, digests, and import/export provenance;
- a deterministic mapping report classifying each semantic element as
  represented, transformed, lossy, unsupported, defaulted, or rejected;
- validation against platform-native ownership, safety, accessibility, package,
  and Assessment rules before publication; and
- narrow degradation: an absent, disabled, incompatible, or failed adapter does
  not block valid native drafting, review, preview, publication, or export of
  the platform-native package.

No external learning standard or version is accepted by this decision. Adding
one requires a durable decision based on concrete user journeys, licensing and
conformance evidence, loss policy, security analysis, compatibility support,
and an executable corpus.

## Consequences

- The first authoring workflow can reuse the accepted content-package semantics
  and validators instead of maintaining a second published content model.
- Human review remains a clear authority boundary; AI can accelerate drafting
  without becoming publisher or approver.
- Revision-bound review and atomic package publication protect immutable
  evidence and make conflicts, stale approvals, and rollback explicit.
- Authors initially lack full-course exchange through an external standard.
- Adapter and mapping-report seams reduce later migration cost without forcing
  speculative standard support or blocking native authoring.
- Exact role policy, collaboration mechanics, editor representation, wire
  shapes, resource limits, and user experience remain CAP/slice contract work
  within this boundary.

## Alternatives Rejected

- **Native model plus one external import/export profile now.** Rejected until a
  concrete interoperability journey and standard/version can justify long-lived
  mapping, security, licensing, and compatibility commitments.
- **External standard as the canonical authoring model.** Rejected because it
  would transfer platform meaning and evolution to an external specification
  and could weaken existing package and module ownership.
- **Direct editing of published packages.** Rejected because it would break
  immutable version and learner-evidence references.
- **AI-authorized publication.** Rejected because validation and generation do
  not supply accountable human review authority.
- **Require an interoperability adapter for publication.** Rejected because an
  optional integration must not make the native workflow brittle or unavailable.

## Boundaries

This decision does not choose a rich-text editor, database schema, real-time
collaboration protocol, archive format, source-control integration, content
marketplace, localization workflow, signing authority, accreditation workflow,
external learning standard, or exact creator/reviewer role matrix. It does not
approve active content, autonomous publication, or direct cross-module storage
access.

Exact contracts and UI behavior require approved CAP delivery. Organization
tenancy and authorization details remain governed by their own decisions.

## Verification Implications

- Prove review and publication bind the exact draft revision, referenced module
  versions, validator/policy versions, reviewer authority, package identity,
  version, and digest.
- Reject stale, conflicting, unauthorized, incomplete, invalid, unsafe, or
  inaccessible drafts atomically without partial publication.
- Prove preview and import remain non-executable, non-published, and unable to
  create learner evidence or bypass package validation.
- Prove publication produces deterministic ADR-0007 packages and cannot replace
  existing `(package_id, package_version)` bytes.
- Prove AI proposals cannot approve or publish and remain distinguishable from
  human-authored and human-reviewed state.
- Prove the native workflow remains usable when every future interoperability
  adapter is absent, disabled, incompatible, unsupported, or failing.
- Before accepting an external standard, qualify deterministic mapping reports,
  loss policy, round-trip expectations, malicious fixtures, provenance,
  licensing, accessibility, compatibility, and conformance.

## Supersession

Selecting an external learning standard, changing human publication authority,
making published versions mutable, permitting active content, or moving
cross-module meaning into Content requires a superseding or extending ADR.
Adding conforming native draft fields or an optional adapter seam does not
necessarily require supersession when authority and published semantics remain
unchanged.
