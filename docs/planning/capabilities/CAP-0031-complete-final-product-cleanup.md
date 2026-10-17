---
id: CAP-0031
kind: capability
planning_status: shaping
authority: noncanonical
owner: codex-final-cleanup
updated: 2026-10-16
parent: null
depends_on: ["CAP-0008", "CAP-0010", "CAP-0015", "CAP-0016", "CAP-0021", "CAP-0023", "CAP-0028", "CAP-0030"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0126", "SLI-0127", "SLI-0128", "SLI-0129"]
---

# Capability: Complete Final Product Cleanup

## Outcome

After the planned product capabilities are complete, learners and contributors
can review a consistent release-candidate experience without deferred
non-functional styling, presentation, copy-hygiene, or repository-hygiene
distractions. Cleanup remains separate from functional delivery, so minor polish
does not repeatedly interrupt earlier CAPs.

## Users and Value

Learners benefit from consistent presentation, spacing, alignment, responsive
behavior, and visual hierarchy across the completed product. Contributors and
operators benefit from one bounded place to reconcile low-consequence warnings,
formatting, minor documentation inconsistencies, and other deferred cleanup.

Value is observable when deferred items have been triaged, non-functional
polish is complete, no cleanup item is being used to hide a functional or safety
defect, and qualification focuses on the final integrated experience rather
than reopening every completed CAP.

## Scope

### In Scope

- A lightweight inventory of cleanup findings deferred from earlier CAPs,
  grouped by affected experience and consequence rather than by review round.
- Non-functional visual polish such as spacing, alignment, density, decorative
  consistency, token-compliant styling, and theme parity after feature structure
  is stable.
- Minor learner-copy, formatting, whitespace, warning, documentation, test-
  hygiene, and repository-hygiene work that does not change product meaning,
  behavior, contracts, data, authority, or required evidence.
- Removal of obsolete presentation scaffolding and duplication when the change
  remains behavior-preserving and is covered by affected verification.
- Focused final browser, responsive, theme, accessibility-presentation, design-
  system, documentation, and readiness evidence for the affected boundaries.
- An explicit route for the user to move a named cleanup item earlier without
  moving the entire capability or turning every advisory concern into a gate.

### Out of Scope

- Functional defects; broken actions; inaccessible names or interactions;
  keyboard/focus failures; required contrast failures; misleading hierarchy;
  unsafe responsive behavior; or impaired comprehension.
- Security, privacy, authorization, financial-calculation, eligibility,
  grading, AI-authority, provider, data-license, contract, persistence,
  recovery, or external-execution changes.
- A new visual identity, design system, component library, product workflow,
  domain term, public API, or release-management process.
- Treating advisory style heuristics, visual preference, or a zero-warning goal
  as universal blockers for functional capability delivery.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Interface Design System](../../design/README.md)
- [Interface Style Guide](../../design/style-guide.md)
- [Learner-Facing Content Style Guide](../../design/content-style-guide.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
- [Testing and Verification Standards](../../standards/testing-and-verification-standards.md)
- [Change Impact Matrix](../../standards/change-impact-matrix.md)
- [Concurrent Automated Work](../concurrent-work.md)
- [CAP-0030](CAP-0030-use-plain-language-in-learner-interfaces.md)

## Decision Gates and Constraints

- This capability begins only after the current terminal CAPs complete. Those
  dependencies place cleanup last transitively without adding artificial
  serial dependencies among earlier capabilities.
- A deferred item is eligible only when it cannot affect functionality,
  meaning, comprehension, accessibility, security, safety, data, contracts,
  policy, or required evidence. If triage discovers such an impact, route the
  item to the owning CAP or a bounded correction instead of relabeling it.
- The user may explicitly move a named item earlier. That changes scheduling,
  not its semantic owner, verification obligations, or decision gates.
- Existing semantic design tokens, reviewed icons, language rules, domain
  meaning, and risk limitations remain authoritative. Cleanup cannot create a
  parallel visual or terminology system.
- The cleanup inventory is advisory planning input. Its existence, count, or
  age does not block another CAP and does not constitute approval or review
  evidence.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0126 | Contributors can review one deduplicated inventory of deferred non-functional cleanup, see why each item is safe to defer, and route any misclassified functional or safety issue back to its owner. | First; consumes deferred observations after all predecessor CAPs complete. | A mandatory cross-CAP gate, tracked reviewer identity/history, or reclassification of a substantive defect changes the package. | captured |
| SLI-0127 | Learners receive consistent token-compliant visual polish across the completed light, dark, responsive, zoomed, and forced-color interfaces without changed behavior or information. | After SLI-0126; may be divided into disjoint route-level packets. | A new design system, component library, interaction, content hierarchy, required contrast exception, or functional behavior changes the package. | captured |
| SLI-0128 | Learners and contributors no longer encounter the accepted minor copy, formatting, warning, documentation, test-hygiene, and repository-hygiene inconsistencies that survived triage. | After SLI-0126; may run in parallel with SLI-0127 when exact files do not overlap. | Domain meaning, contract/schema changes, broad automated rewriting, dependency upgrades, or behavior-affecting refactors change the package. | captured |
| SLI-0129 | Contributors can qualify the integrated cleanup with focused affected checks and a final cross-interface review, while anti-rigidity evidence proves cosmetic preferences and advisory heuristics cannot reopen completed functional CAPs. | Last; depends on SLI-0127 and SLI-0128. | Release publication, production deployment, universal visual snapshot gating, or new external services changes the package. | captured |

## Capability Acceptance

- Every item in the final cleanup inventory is completed, explicitly retained
  with a bounded reason, or rerouted because it is actually substantive; there
  is no requirement to reach an arbitrary zero-advisory count.
- Learner-facing routes use the shared tokens and reviewed icons consistently,
  with equivalent content, actions, hierarchy, focus, contrast, and responsive
  behavior in supported themes.
- Minor language and documentation cleanup preserves exact domain, financial,
  evidence, provenance, adaptive-learning, privacy, and AI-authority meaning.
- Focused tests cover the changed presentation and hygiene boundaries. The
  design-system, documentation, planning, and aggregate readiness checks pass;
  broader browser or application checks run only where affected risk warrants.
- Anti-rigidity tests demonstrate that non-functional style preferences remain
  nonblocking, user-directed pull-forward is possible for one named item, and a
  functional/accessibility/safety issue cannot be hidden in the cleanup class.
- No completed predecessor CAP is reopened merely because this capability
  reconciles its deferred non-functional observations.

## Risks and Non-Goals

The main risk is turning “final cleanup” into an unlimited redesign, a zero-
warning mandate, or a place to bury substantive defects. The capability uses
consequence-based triage, existing design/language authority, bounded route-
level packets, and affected verification to avoid those outcomes. It does not
promise production readiness, launch approval, perfect aesthetics, or permanent
freedom from future cleanup.

## Documentation Impact

Delivery may update the style and content guides only when an existing shared
rule truly changes; otherwise it updates affected components, tests, nearest
READMEs, and the bounded cleanup inventory/evidence. Planning and review records
remain subject to the existing local-only authority rules. Any user-pulled-
forward item is recorded through ordinary planning and ownership metadata, not
as a new approval stage.

## Planning History

- 2026-10-16: Shaped from an explicit request to keep blank-line, early alpha/
  beta styling, and similarly inconsequential findings from interrupting
  functional CAP delivery. The package is placed after the current terminal
  capabilities and preserves a user-directed route to move a named item earlier.
- 2026-10-16: Reconciled the complete four-slice package with the current
  terminal dependency set and consequence-based cleanup policy. Cleanup cannot
  defer functional or safety defects, and the manifest has no unresolved
  durable decision gate.
