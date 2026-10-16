---
id: CAP-0005
kind: capability
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0022", "SLI-0023", "SLI-0024", "SLI-0025"]
---

# Capability: Navigate a Competency-Based Curriculum

## Outcome

An individual learner can understand a versioned curriculum's objectives,
competency relationships, prerequisites, required and optional branches,
current completion context, and deterministic requirements for advancing, then
choose and open an eligible activity without opaque adaptive ranking.

## Users and Value

Learners need to know where they are, what a curriculum expects, what remains
available, and why an activity is locked or eligible. Value is observable when
a learner can trace every eligibility statement to current curriculum and
completion evidence, distinguish required from optional work, and make an
informed choice without the system presenting a recommendation as a mandate.

Curriculum contributors and support operators benefit from one versioned graph
and explanation contract that can be validated independently of a particular
page layout or persistence adapter.

## Scope

### In Scope

- A versioned Curriculum-owned graph for one bounded curriculum containing
  competencies, objectives, activities, prerequisite relationships, required
  and optional branches, stable identities, and exact referenced Content and
  Assessment versions.
- Validation that rejects missing references, cycles where the model forbids
  them, ambiguous advancement rules, duplicate identities, and unsupported
  versions before a curriculum becomes navigable.
- Deterministic prerequisite and advancement evaluation using the current
  curriculum version, authorized learner context, and exact Learner-model
  completion projection; every eligible, complete, locked, optional, or
  unavailable state has a stable explanation.
- A learner-controlled map/list and activity-detail experience that shows
  objectives, relationships, current position, completion context, and exact
  reasons without model ranking or engagement optimization.
- Opening an eligible exact activity through its public destination while
  retaining curriculum and activity versions for later evidence.
- Safe curriculum-version change behavior that never rewrites prior evidence or
  silently transfers completion to semantically different requirements.
- Accessible, responsive light/dark/system-theme behavior and equivalent local
  and cloud domain and contract semantics.

### Out of Scope

- Personalized next-activity ranking, AI-generated pathways or explanations,
  experimentation, nudging, or engagement optimization.
- Mastery estimation, competency-strength scoring, predictive risk, or claims
  that completion proves professional or investment competence.
- Catalog search, enrollment, cohort assignment, instructor authoring, mutable
  curriculum drafts, publication workflow, or external learning standards.
- Organization tenancy, role/entitlement administration, certification,
  accreditation, billing, or managed-cloud operations.
- Instructor overrides, manual prerequisite waivers, exception workflows, or
  cross-curriculum credit transfer.
- Executing project, market-data, notebook, model, or external-provider work.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Initial Glossary](../../domain/glossary.md)
- [Module Map](../../architecture/modules/module-map.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [Versioned Lesson Package](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Interface Design System](../../design/README.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)

## Decision Gates and Constraints

- CAP-0001 supplies exact activity versions, learner context, Assessment
  evidence, and a rebuildable completion projection. CAP-0005 depends on that
  capability rather than recreating those owners.
- ADR-0005 assigns curriculum structure, competencies, prerequisites, and
  pathway relationships to Curriculum; completion and progress projections stay
  in Learner model; attempt and score evidence stays in Assessment.
- The accepted adaptive architecture requires deterministic eligibility before
  any future ranking. This CAP stops at eligibility, explanation, and learner
  choice and does not activate the still-constrained Adaptation boundary.
- Curriculum publication is versioned and immutable for navigation. Prior
  evidence keeps the exact curriculum/activity versions that gave it meaning.
- Authorization, prerequisite satisfaction, advancement rules, activity
  availability, and destination selection are deterministic and cannot be
  overridden by AI output or browser state.
- No unresolved durable decision is needed for this bounded, deterministic
  navigation path. Mastery semantics, adaptive ranking, authoring workflow,
  waivers, external standards, and organization policy remain separate gated
  capabilities.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0022 | A learner opens one approved curriculum and sees its versioned objectives, competencies, activities, required/optional branches, and relationship structure from a validated Curriculum-owned graph. | First after CAP-0001; establishes graph semantics, validation, publication/read operations, persistence, API/client representation, and a non-personalized map/list. | Mutable collaborative authoring, external-standard semantics, cross-organization catalogs, or moving ownership out of Curriculum changes the CAP package. | captured |
| SLI-0023 | The learner sees deterministic complete, eligible, locked, optional, and unavailable states with stable explanations derived from the exact curriculum version and current completion evidence. | After SLI-0022 and CAP-0001 completion projection; establishes prerequisite/advancement policy and denial evidence. | Mastery inference, model ranking, manual waivers, institution-specific policy, or client-authoritative eligibility changes the CAP package. | captured |
| SLI-0024 | The learner chooses and opens an eligible exact activity, returns to the same curriculum context, and sees current-position and completion markers without losing optional branches or rewriting prior history after a version change. | After SLI-0023; integrates public destinations and learner-controlled choice. It does not require CAP-0004 and may run independently of catalog discovery. | Enrollment, recommendations, automatic next-step selection, cross-curriculum credit, or silent completion migration changes the CAP package. | captured |
| SLI-0025 | The complete navigation flow is qualified for graph validation, deterministic eligibility, projection replay, exact-version behavior, authorization, interruption, accessibility, responsive/theme parity, and shared local/cloud semantics. | Last; depends on SLI-0022 through SLI-0024. | Qualifying adaptive models, organization tenancy, authoring, certification, or a specific cloud adapter changes the CAP package. | captured |

## Capability Acceptance

The capability is complete only when evidence demonstrates that:

- invalid curriculum references, disallowed cycles, duplicate identities,
  unsupported versions, and ambiguous advancement rules fail before
  publication or learner visibility;
- every learner-visible curriculum, competency, activity, relationship, and
  prerequisite is tied to a stable identity and exact approved version;
- complete, eligible, locked, optional, and unavailable states are reproducible
  from exact curriculum and learner-projection inputs and include concise,
  non-model-authored reason codes and explanations;
- missing, stale, tampered, cross-learner, or unauthorized context fails closed
  without exposing hidden activities or creating completion evidence;
- a learner can choose among eligible branches and open the exact destination,
  while the application—not the client—enforces eligibility and authorization;
- curriculum-version changes preserve old evidence meaning, surface changed
  requirements, and never silently substitute or transfer completion;
- projection rebuild and event replay reproduce current navigation state without
  mutating Assessment evidence or Curriculum history;
- local and cloud adapters can share graph, policy, contract, and evidence
  semantics without a deployment-specific domain fork; and
- map and list alternatives, keyboard order, focus, labels, relationship text,
  non-color states, zoom/reflow, reduced motion, forced colors, and both themes
  satisfy the interface contract.

## Risks and Non-Goals

- A visual graph can obscure prerequisite meaning or become inaccessible unless
  an equivalent ordered textual representation is first-class.
- Treating completion as mastery would overstate the evidence and collapse
  Learner-model concepts that require later decisions.
- Client-side eligibility or cached projections can create unauthorized routes
  unless the owning application operation rechecks current facts.
- Version migration can silently change evidence meaning unless prior versions
  and source references remain visible.
- CAP-0005 is not the adaptive recommendation, curriculum authoring, catalog
  discovery, learner analytics, instructor override, or certification capability.

## Documentation Impact

Delivery is expected to refine competency and curriculum vocabulary, graph and
eligibility contracts, Curriculum and Learner-model public seams, event and
projection behavior, API/generated-client contracts, accessible navigation
patterns, module READMEs, architecture verification, and known gaps.

## Completion Evidence

| Capability acceptance | Direct evidence |
| --- | --- |
| Invalid references, duplicate identities, unsupported versions, forbidden cycles, and ambiguous rules fail before visibility | Curriculum graph contract, domain, application, and API coverage in the 426-test backend suite |
| Learner-visible facts retain stable identity and exact approved versions | Reviewed OpenAPI/generated-client reproduction plus exact-version backend, 27 mocked Chromium, and eight live Chromium scenarios |
| Complete, eligible, locked, optional, and unavailable states are deterministic and explained | Navigation policy/contract/application tests plus live graph-ordered state and reason qualification |
| Missing, stale, tampered, cross-context, and unauthorized requests fail closed | Backend denial and confidentiality coverage, mocked browser denial paths, approved-lesson security's 10 control groups, and live denial scenarios |
| Learners choose eligible branches and the application rechecks exact launch authority | Protected launch API tests and the live exact lesson launch/return journey |
| Version changes preserve evidence meaning and do not silently substitute completion | Coexisting `investing-foundations@1.0.0` and `@1.1.0` live evidence plus exact-source completion reuse without changed-placement inheritance |
| Projection rebuild reproduces current navigation state without source mutation | Public API observation before and after an isolated test-only reset of two derived Learner-model tables: Assessment sources preserved, semantic state stable, three projections and one history row rebuilt after seed-free restart |
| Local and future cloud profiles share core semantics without a deployment fork | Fifteen architecture/import-boundary tests and deployment-neutral domain, application, contract, and provider-port checks |
| Map/list, keyboard, focus, labels, non-color state, reflow, reduced motion, forced colors, and themes remain equivalent | 151 web tests, 27 mocked Chromium scenarios, eight live scenarios, and design validation of 125 tokens and 56 icons |

The supported public session, graph, Navigation-state, and activity-launch APIs
remain available to browser, command-line, service, and future headless AI
clients. The live qualifier proves the non-browser path without importing
backend internals or relying on UI state. CAP-0005 does not plan or qualify a
separate AI mode, agent protocol, model provider, adaptive ranking, managed-
cloud adapter, organization tenancy, or production recovery profile.

The cumulative matrix also passes TypeScript typecheck, zero-warning lint,
production build, generated-client drift detection, 14 focused replay tests,
documentation and planning integrity, and all 29 fixed aggregate readiness
checks. No product behavior or public contract changed in the closure packet.

## Planning History

- 2026-10-15: Shaped from the catalog candidate “Navigate a competency-based
  curriculum” as a complete `cap-package-v1` manifest. It depends only on
  CAP-0001 and is intentionally parallel-safe at capability level with
  CAP-0004 and CAP-0006 once that foundation is complete; exact file-level
  compatibility remains a just-in-time packet concern.
- 2026-10-16: Resumed approved delivery at SLI-0024 after SLI-0022 and SLI-0023
  completed. The first exact launch-contract packet is active with no material
  package drift or unresolved decision.
- 2026-10-16: Completed the CAP-0005 cumulative qualification matrix through
  WRK-0091. Every acceptance statement has direct evidence, including a public-
  API headless observation around an isolated test-only derived-state reset and
  seed-free restart; the capability is ready for governed slice and CAP closure
  without a separate AI-mode plan or production recovery API.
