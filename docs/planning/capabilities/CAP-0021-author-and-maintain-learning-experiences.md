---
id: CAP-0021
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0005", "CAP-0006", "CAP-0007", "CAP-0025"]
decision_gates: ["DEC-0015"]
approval_model: cap-package-v1
slice_ids: ["SLI-0086", "SLI-0087", "SLI-0088", "SLI-0089"]
---

# Capability: Author and Maintain Learning Experiences

## Outcome

An authorized creator can develop, validate, review, version, publish, and
retire curricula, lessons, examples, assessments, projects, competency mappings,
and supporting sources through an accepted authoring and interoperability
workflow without weakening immutable published package semantics.

## Users and Value

Curriculum authors and reviewers need a controlled path from mutable drafts to
reproducible learner-visible releases. Value is observable when publication is
reviewed, deterministic, provenance-rich, reversible by new version, and unable
to rewrite evidence tied to prior versions.

## Scope

### In Scope

- The draft, review, validation, publication, retirement, import/export, and
  external-interoperability posture selected by DEC-0015.
- Versioned author identities/roles supplied by CAP-0025, source/license
  metadata, preview, validation, change comparison, review comments, and audit.
- Publication to existing Content, Curriculum, Assessment, and Project public
  contracts without direct persistence coupling.
- Accessible creator and reviewer workflows with safe failure and rollback by
  immutable new version or publication state.

### Out of Scope

- Rewriting published bytes or learner evidence, AI-autonomous publication,
  arbitrary active content, certification/accreditation, marketplace behavior,
  or unaccepted external standards.
- Organization tenancy or commercial licensing choices not accepted elsewhere.

## Canonical Context

- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Content-Package Contract](../../architecture/contracts/content-package-contract.md)
- [Platform-Native Human-Reviewed Content Authoring](../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
- [Content Authoring Workflow Contract](../../architecture/contracts/content-authoring-workflow-contract.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0005](CAP-0005-navigate-competency-based-curriculum.md)
- [CAP-0006](CAP-0006-practice-and-demonstrate-understanding.md)
- [CAP-0007](CAP-0007-complete-applied-projects.md)
- [CAP-0025](CAP-0025-manage-identities-organizations-roles-entitlements.md)

## Decision Gates and Constraints

- ADR-0017 selects platform-native revision-bound drafts, human review,
  deterministic immutable publication, and an optional future interoperability
  seam. No external learning standard is currently admitted or claimed.
- Published versions remain immutable, digest-bound, safely renderable, and
  separated from Assessment runtime scoring.
- Authorization, validation, review completion, and publication are
  deterministic; AI may draft only bounded material and never approve/publish.
- Exact creator, reviewer, and organization permissions come from CAP-0025;
  this CAP does not infer an organization tenancy or role model of its own.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0086 | An authorized creator drafts and validates versioned lesson/curriculum source with safe preview, citations, assets, and exact publication target. | First after dependencies, including CAP-0025, and ADR-0017; establishes revision-bound draft/review ownership. | Arbitrary active content, AI publication, or direct learner visibility changes the CAP package. | captured |
| SLI-0087 | The creator authors structured assessments, projects, competencies, and mappings through owning-module contracts with cross-reference validation. | After SLI-0086. | Authoring runtime scores, executing project artifacts, or cross-module persistence changes the CAP package. | captured |
| SLI-0088 | Authorized reviewers compare versions, request changes, and publish or retire an immutable release with source/license and audit provenance. | After SLI-0087. | Mutable published versions, unreviewed release, or accreditation claims changes the CAP package. | captured |
| SLI-0089 | Native authoring is qualified for validation, review separation, compatibility, rollback, native import/export, safe preview, authorization, accessibility, prior-evidence preservation, and narrow optional-adapter degradation. | Last; depends on SLI-0086 through SLI-0088. | Marketplace, real-time collaboration, or claiming an external standard without a new durable decision changes the CAP package. | captured |

## Capability Acceptance

- Draft and published states, roles, review decisions, source/license evidence,
  exact versions, digests, and compatibility are explicit and auditable.
- Invalid, unsafe, unauthorized, stale, or conflicting changes cannot publish;
  rollback creates an explicit state/version rather than rewriting history.
- Published output conforms to platform contracts and preserves all existing
  learner evidence references.
- Accessibility, security, interoperability, migration, and failure evidence
  matches the DEC-0015 boundary.

- Every slice includes focused failure and anti-rigidity tests; one unsupported
  content type or interoperability adapter cannot prevent publication of valid
  native packages.

## Risks and Non-Goals

Authoring can accidentally create a second content standard or let mutable
drafts redefine immutable evidence. This CAP excludes autonomous publication,
active untrusted content, accreditation, and an ungoverned marketplace.

## Documentation Impact

Delivery will add authoring/review/publication vocabulary, schemas, role and
audit policy, source/license controls, preview security, interoperability,
operations, accessibility, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 18 with manifest SLI-0086 through
  SLI-0089. DEC-0015 blocks CAP approval and delivery.
- 2026-10-15: DEC-0015 was promoted to ADR-0017, selecting platform-native
  human-reviewed authoring with optional future interoperability seams; the CAP
  returned to shaping for package refinement.
- 2026-10-16: Revalidation made the existing CAP-0025 author/reviewer role
  dependency explicit so this package cannot invent authorization policy. The
  complete four-slice manifest otherwise remains unchanged and has no internal
  durable decision gate.

