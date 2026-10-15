---
id: DEC-0015
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md
---

# Decision Request: Choose the Content Authoring and Interoperability Workflow

## Decision Needed

Choose the mutable draft/review/publication model and whether the first authoring
capability supports only the platform-native package or also an external
learning-standard import/export profile.

## Why Now

ADR-0007 fixes immutable published lesson packages but deliberately does not
choose authoring, collaboration, archive transport, or external interoperability.
CAP-0021 cannot infer those semantics from the learner read contract.

## Current Authority and Constraints

Published package identity/version/digest, constrained CommonMark, declared
passive assets, source provenance, and Assessment runtime ownership are fixed.
Published bytes and prior learner evidence cannot be rewritten; untrusted active
content and autonomous AI publication are excluded.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Platform-native drafts with human review and publication | Smallest semantic gap from ADR-0007, preserves exact validation, and defers unsupported interoperability. | Authors may need conversion tools and cannot exchange full courses through a standard initially. | Draft/review/publication contracts, creator roles, preview, package build, audit and rollback. | High; external adapters can be added later. |
| B. Native model plus one selected external import/export profile | Improves portability and author onboarding while retaining a canonical internal model. | Requires standard/version selection, lossy mapping policy, conformance corpus, and ongoing compatibility support. | Import/export adapters, mapping reports, package builder, validation and source provenance. | Medium; published interchange commitments persist. |

## Recommendation

Option A for the first authoring workflow. Design explicit adapter seams and
mapping diagnostics, but require evidence of a concrete interoperability need
before selecting and supporting a standard.

## Evidence Required

- Author/reviewer workflow prototype and package-build round trip.
- Role separation, safe preview, source/license, conflict, rollback, and audit review.
- Concrete interoperability user journeys and candidate standard/version
  conformance comparison if Option B is pursued.

## Required Authority

Product/content authority with Curriculum/Assessment/Project domain,
architecture, security, accessibility, and external-standard review.

## Decision Record and Promotion

[ADR-0017](../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
selects Option A: platform-native drafts with human review and publication. It
preserves an optional future interoperability-adapter and mapping-diagnostic
seam but accepts no external learning standard or current support claim.

## Dependent Planning Updates

Reconcile CAP-0021 and any external-standard claims in export or provider plans.

## Planning History

- 2026-10-15: Captured while shaping CAP-0021.
- 2026-10-15: Option A was selected and promoted to ADR-0017 with a
  non-authorizing future interoperability seam.

