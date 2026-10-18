---
id: CAP-0020
kind: capability
planning_status: complete
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0082", "SLI-0083", "SLI-0084", "SLI-0085"]
---

# Capability: Understand Platform Methods and Limitations

## Outcome

An individual learner can search and navigate current platform help,
financial/AI/ML glossary terms, methodology, provenance guidance, adaptive and
AI explanations, and education-versus-advice limitations tied to the applicable
feature and version.

## Users and Value

Learners and support contributors need explanations that remain discoverable at
the moment of use. Value is observable when a user can trace a term, method,
limitation, data distinction, or error to a reviewed versioned source without
mistaking documentation for financial, legal, or regulatory advice.

## Scope

### In Scope

- Versioned approved help, glossary, methodology, provenance, limitation, and
  troubleshooting content with source ownership and review status.
- Search, topic navigation, contextual deep links, version/applicability labels,
  related concepts, stale-content handling, and offline local availability.
- Education/advice, observed/calculated/simulated/predicted/generated, AI
  authority, data quality, and capability-availability explanations.
- Accessible content and search across supported themes and devices.

### Out of Scope

- Legal, tax, regulatory, accreditation, suitability, or support guarantees.
- AI-generated canonical help, unreviewed external content, learner-specific
  financial conclusions, or mutable product policy owned by the help system.

## Canonical Context

- [Documentation Governance](../../README.md)
- [Initial Glossary](../../domain/glossary.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [Interface Design System](../../design/README.md)

## Decision Gates and Constraints

- Canonical product, domain, architecture, contract, risk, security, and
  operations sources retain authority; help derives and links rather than
  silently redefining them.
- Search and rendering are deterministic and safe; active content and unreviewed
  external instructions are not executed or promoted.
- Feature-specific disclosures ship with the feature and register through a
  stable help contract so this CAP does not become a release bottleneck.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0082 | A learner browses and searches a versioned approved glossary/help corpus with applicability, source, and update metadata. | First after CAP-0001; establishes content and index contracts. | AI-authored canonical policy or active external content changes the CAP package. | captured |
| SLI-0083 | The learner opens contextual method, provenance, data-distinction, and education-versus-advice explanations from supported features. | After SLI-0082; uses stable contextual links. | Help becoming product-policy authority changes the CAP package. | captured |
| SLI-0084 | The learner sees feature/version limitations, unavailable/degraded capability guidance, and safe troubleshooting without revealing secrets or unsupported claims. | After SLI-0083. | Operational command execution or guarantee claims changes the CAP package. | captured |
| SLI-0085 | Help is qualified for source freshness, broken links, safe rendering, search quality, accessibility, offline local use, and anti-rigidity integration. | Last; depends on SLI-0082 through SLI-0084. | Hosted support workflow or unbounded external retrieval changes the CAP package. | captured |

## Capability Acceptance

- Search results and contextual links resolve to reviewed versioned content with
  clear ownership, applicability, and source.
- Distinctions among observed, calculated, simulated, predicted, and generated
  content and the education/advice boundary are consistently visible.
- Missing, stale, malformed, or unavailable content fails safely without
  blocking unrelated feature use.
- Accessibility, safe rendering, local availability, freshness checks, and
  extension guidance are directly verified.

- Every slice includes focused failure and anti-rigidity tests so stale or
  malformed content in one topic does not disable unrelated help and search.

## Risks and Non-Goals

Help can drift or be mistaken for authority. This CAP keeps canonical ownership
outside the presentation layer and does not provide legal, tax, regulatory,
financial, accreditation, or guaranteed support conclusions.

## Documentation Impact

Delivery will add the help-content/index contract, glossary synchronization,
context-link conventions, limitation patterns, safe rendering, accessibility,
freshness and broken-link checks, and contributor guidance.

## Planning History

- 2026-10-15: Shaped from catalog candidate 17 with manifest SLI-0082 through
  SLI-0085. The package awaits one CAP planning approval.
- 2026-10-18: Completed CAP-0020 after all four manifest slices closed with
  versioned source-bound Platform Help, contextual explanations, feature-limit
  guidance, deterministic source/graph/search quality checks, generated-client
  browser/headless parity, accessibility, normal-restart, read-only
  containment, disposable recovery, and anti-rigidity evidence. No material
  package drift or unresolved decision gate remains.
