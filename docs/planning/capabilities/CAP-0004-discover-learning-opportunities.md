---
id: CAP-0004
kind: capability
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0018", "SLI-0019", "SLI-0020", "SLI-0021"]
---

# Capability: Discover Learning Opportunities

## Outcome

An individual learner can browse, search, filter, inspect, and compare approved
learning opportunities by topic, level, duration, prerequisites, kind, and
availability, with enough provenance and limitation context to choose where to
continue without the catalog making a personalized recommendation.

## Users and Value

Learners need a reliable way to understand what the academy offers before they
enter a curriculum or activity. Value is observable when a learner can narrow a
catalog, understand why an item is available or unavailable, compare a small set
of opportunities, and open an exact approved destination without stale metadata
or hidden ranking authority.

Content contributors and operators benefit indirectly from one versioned public
discovery projection rather than feature-local search indexes or provider
payloads leaking into the learner experience.

## Scope

### In Scope

- A platform-owned, versioned discovery record for approved courses, lessons,
  labs, and projects represented by accepted public Content and Curriculum
  operations, including stable identity, title, summary, objectives, topic,
  level, estimated duration, prerequisite summary, kind, availability, exact
  destination, version, and provenance.
- Deterministic visibility and availability policy that excludes drafts,
  rejected content, unauthorized opportunities, and unsupported destinations.
- Browse, query, filter, stable sort, bounded pagination, empty, stale, degraded,
  and unavailable behavior over approved discovery records.
- A detail and comparison experience that distinguishes opportunity kind,
  required prerequisites, expected outputs, availability limitations, and exact
  version without implying enrollment, eligibility, or personalized suitability.
- Rebuildable search/index projections derived from owning-module facts; the
  projection is never a second source of content, curriculum, or authorization
  truth.
- Accessible, responsive light/dark/system-theme catalog behavior through the
  generated public client and existing design system.
- Local/community operation without an external search service and a
  provider-neutral port for a future cloud search adapter with identical public
  semantics.

### Out of Scope

- Enrollment, cohort assignment, course administration, paid entitlements, or
  organization-specific visibility.
- Adaptive ranking, personalized recommendations, mastery-based sequencing,
  sponsored placement, behavioral optimization, or opaque relevance models.
- Content authoring, mutable drafts, publication review, provider ingestion, or
  external learning-standard interoperability.
- Executing lessons, assessments, labs, projects, notebooks, market-data jobs,
  or model workloads from the catalog.
- A general-purpose full-text search service, remote content crawler, or provider
  search proxy.
- User-generated ratings, reviews, social signals, marketing claims, or
  certification and employment-outcome claims.
- Managed-cloud tenancy, licensing, billing, and commercial catalog policy.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Product Non-Goals](../../product/non-goals.md)
- [Initial Glossary](../../domain/glossary.md)
- [Module Map](../../architecture/modules/module-map.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Versioned Lesson Package](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Content-Package Contract](../../architecture/contracts/content-package-contract.md)
- [Interface Design System](../../design/README.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)

## Decision Gates and Constraints

- CAP-0001 is the hard foundation because it proves exact published Content and
  Curriculum identities, safe lesson destinations, learner context, and the
  generated-client/browser seam. CAP-0004 does not reopen those contracts.
- Content remains authoritative for publication metadata and source provenance;
  Curriculum remains authoritative for placement, structure, prerequisites,
  and availability facts it owns. A discovery projection holds references and
  search fields, not duplicate business authority.
- Visibility, authorization, exact destination selection, availability, and
  prerequisite facts remain deterministic. Search scoring may order matching
  metadata only and cannot create eligibility or recommendation authority.
- Opportunity kinds whose execution semantics are not yet delivered may be
  represented only with honest availability and limitation states. Catalog
  presence cannot imply that a lab, project, or provider is executable.
- Local and cloud profiles share record and query semantics. A future external
  search provider remains behind a platform-owned port and requires its own
  data-use, tenancy, and operational decision before admission.
- No unresolved durable decision is needed for the bounded local discovery
  projection and metadata search described here. Personalized ranking,
  commercial placement, organization visibility, or external indexing would be
  a material CAP change and may require decisions.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0018 | A learner browses a deterministic catalog projection of approved opportunities and sees stable identity, kind, topic, level, duration, availability, version, and provenance without drafts or inaccessible records leaking into results. | First after CAP-0001; establishes the versioned discovery record, owning-module projection, visibility policy, local query port, and rebuild behavior. | Making the projection authoritative, ingesting provider payloads directly, adding organization tenancy, or implying undelivered execution changes the CAP package. | captured |
| SLI-0019 | The learner searches, filters, sorts, and pages the approved catalog with stable query semantics, explicit active filters, deterministic tie handling, and bounded empty, malformed, stale-index, and degraded states. | After SLI-0018; consumes its record and visibility contracts. | Personalized or model-ranked results, behavioral tracking as ranking authority, external search infrastructure, or unbounded full-text crawling changes the CAP package. | captured |
| SLI-0020 | The learner inspects and compares a bounded set of opportunities, understands prerequisites and availability limitations, and opens the exact approved destination without the catalog granting enrollment or eligibility. | After SLI-0018; may proceed in parallel with SLI-0019 once the discovery record is stable, then integrates with its query state. | Enrollment, entitlement, adaptive recommendation, learner suitability, or execution of activities changes the CAP package. | captured |
| SLI-0021 | The complete discovery flow is qualified for accessibility, responsive/theme parity, projection rebuild, deterministic queries, stale versions, authorization denial, local operation, and provider-neutral cloud semantics. | Last; depends on SLI-0019 and SLI-0020. | Qualifying a specific external search provider, managed-cloud tenancy, commercial placement, or unrelated activity execution changes the CAP package. | captured |

## Capability Acceptance

The capability is complete only when evidence demonstrates that:

- only approved and authorized opportunity versions appear and every result can
  be traced to the exact owning-module facts and provenance from which it was
  projected;
- projection replay and rebuild produce the same visible records and remove or
  mark withdrawn, superseded, stale, or no-longer-authorized records safely;
- topic, level, duration, prerequisite, kind, and availability filters have
  documented deterministic semantics and stable ordering/tie behavior;
- malformed queries, invalid cursors, unsupported filters, stale index state,
  missing destinations, and unavailable projections produce bounded responses
  without exposing drafts, provider payloads, or internal storage details;
- detail and comparison views distinguish lessons, labs, and projects and state
  honestly when execution or prerequisites are unavailable;
- opening an item uses its exact approved destination and never silently
  substitutes a newer version;
- local operation requires no external search dependency, while the public port
  and conformance scenarios are reusable by a future cloud adapter; and
- keyboard, focus, labels, filter state, result counts, empty/degraded states,
  200-percent zoom/reflow, both themes, forced colors, and assistive-technology
  behavior meet the interface contract without color-only meaning.

## Risks and Non-Goals

- A denormalized index can become accidental product authority unless rebuild,
  provenance, withdrawal, and authorization rules are enforced.
- Ranking language can drift into personalized recommendations even when the
  implementation only performs metadata matching.
- Showing an undelivered opportunity as available could mislead learners about
  platform capability; availability must be explicit and source-backed.
- Catalog copy must remain educational and cannot promise certification,
  employment, investment performance, or individualized suitability.
- CAP-0004 is not a curriculum navigator, adaptive pathway, content authoring
  system, enrollment service, or general enterprise search platform.

## Documentation Impact

Delivery is expected to add discovery record and query contracts, projection
ownership and rebuild rules, API/generated-client behavior, catalog interface
guidance, accessibility evidence, module READMEs, architecture verification,
and known-gap updates. Context packs change only after their canonical sources.

## Planning History

- 2026-10-15: Shaped from the catalog candidate “Discover learning
  opportunities” as a complete `cap-package-v1` manifest. CAP-0001 is the only
  hard capability dependency; CAP-0004 may run in parallel with CAP-0005 and
  CAP-0006 after that foundation is complete.
