---
id: CAP-0030
kind: capability
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: null
depends_on: ["CAP-0001", "CAP-0004"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0122", "SLI-0123", "SLI-0124", "SLI-0125"]
---

# Capability: Use Plain Language in Learner Interfaces

## Outcome

Learners can understand available learning choices, curriculum state, lesson
completion, and recovery actions without needing software-development or data-
pipeline vocabulary. Precise versions, provenance, and diagnostic facts remain
available through clearly labeled progressive disclosure rather than competing
with the learner's task.

## Users and Value

Learners need to decide what to open, understand why work is available or
locked, interpret retained evidence, and recover from problems. Value is
observable when primary headings, labels, controls, status explanations, and
errors use familiar words and direct actions while reviewed technical evidence
and financial-learning limitations retain their exact meaning.

Contributors benefit from one lightweight content standard, reviewed term map,
and proportionate changed-copy checks. These controls should catch avoidable
jargon without turning writing heuristics into a release barrier.

## In Scope

- A repository-owned learner-facing language standard informed by ASD-STE100,
  Digital.gov, GOV.UK, W3C accessibility guidance, and the SEC Plain English
  Handbook without reproducing proprietary controlled-language material or
  claiming formal conformance.
- A content style guide and reviewed replacement map for avoidable computing,
  contract, storage, projection, and provenance terms in primary learner flows.
- Task-first headings, concise labels, active and direct explanations,
  actionable errors, and one clear next step where recovery is possible.
- Progressive disclosure that keeps versions, digests, identifiers, source
  records, and other technical evidence available under a plain label such as
  `Technical record` without weakening provenance.
- Plain-language improvements to the delivered learning catalog, opportunity
  detail/comparison, curriculum graph/navigation, lesson, knowledge-check, and
  retained-completion experiences, including the examples identified during
  the research review.
- Local deterministic changed-copy checks for a small set of high-confidence
  failures plus advisory reporting for sentence complexity, unexplained
  acronyms, noun clusters, and avoidable jargon.
- Focused component and browser evidence that content, actions, hierarchy,
  accessibility, responsive behavior, themes, and safe failure meaning remain
  equivalent after wording and information-architecture changes.

## Out of Scope

- Changing domain vocabulary, public API or schema field names, generated
  clients, authorization, eligibility, grading, financial calculations,
  evidence meaning, model authority, or durable state.
- Rewriting legal, financial-risk, educational-use, privacy, recovery, or
  provider disclosures without the separately required canonical review.
- Claiming ASD-STE100, ISO 24495, WCAG, or regulatory conformance from local
  guidance or automated checks.
- Vendoring proprietary standards, controlled dictionaries, or third-party
  copyrighted guidance; adding an external grammar, AI, or content-review
  service; or sending learner or repository text outside the local boundary.
- A visual redesign, new component library, localization system, translation,
  hosted user-research platform, or broad rewrite of developer/operator
  documentation that is intentionally technical.

## Canonical Context

- [Documentation Governance](../../README.md)
- [Interface Design System](../../design/README.md)
- [Interface Style Guide](../../design/style-guide.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [Change Impact Matrix](../../standards/change-impact-matrix.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Initial Glossary](../../domain/glossary.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)
- [CAP-0004](CAP-0004-discover-learning-opportunities.md)
- [CAP-0005](CAP-0005-navigate-competency-based-curriculum.md)

## Decision Gates and Constraints

- Presentation may become simpler only when the owning domain and contract
  semantics remain unchanged. Ambiguous or overloaded domain terms return to
  their canonical owner rather than being silently redefined in copy.
- Financial-risk, education-versus-advice, privacy, recovery, and model-
  authority language retains canonical meaning. A material disclosure change
  stops for the applicable risk, legal, security, or AI authority review.
- ASD-STE100 is used as an informative source of writing principles, not as a
  copied vocabulary or certification target. ISO or other paid standards are
  not reproduced.
- Technical evidence is moved behind progressive disclosure only when it
  remains reachable, labeled, accessible, and complete. It is never discarded
  to make a page appear simpler.
- Automated wording checks are diff-aware and tiered. Only narrowly defined,
  high-confidence defects may block; style heuristics remain advisory, allow a
  local reasoned exception, and never auto-rewrite user-facing text.
- Copy-only work selects focused content, component, browser, accessibility,
  documentation, and readiness checks. It does not automatically require the
  complete application suite unless affected behavior warrants it.
- Completed `SLI-0023` is the current curriculum-state presentation baseline.
  Later CAP-0005 slices must consume the language standard and term map rather
  than reintroducing avoidable technical language.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0122 | A learner can find, filter, inspect, compare, and open learning opportunities using task-focused headings and controls such as `Topic`, `Show results`, `Lesson version`, and `Open lesson`; the repository gains the shared language standard, content style guide, and initial term map. | First after CAP-0004; establishes the content contract used by later slices. | Domain/API renaming, new discovery behavior, changed risk disclosures, localization, or formal standards conformance changes the CAP package. | captured |
| SLI-0123 | A learner can understand the learning path, activity connections, completion and availability status, and recovery actions without graph/projection terminology, while the full technical record remains accessible. | After SLI-0122; reuses completed SLI-0023 graph and navigation-state semantics. | Eligibility changes, recommendation or mastery language, activity-launch behavior, or removal of provenance changes the CAP package. | captured |
| SLI-0124 | A learner can understand lesson loading, knowledge-check results, retained completion evidence, and session or safety failures in direct language with a clear next action where one exists. | After SLI-0122; may run in parallel with SLI-0123 only when exact file scopes are disjoint. | Grading/evidence changes, disclosure changes, answer exposure, or new session behavior changes the CAP package. | captured |
| SLI-0125 | Learner-facing language is qualified and sustained through a diff-aware checker, focused usability and accessibility evidence, documented exceptions, and anti-rigidity tests that prevent the guidance from becoming a universal prose gate. | Last; depends on SLI-0122 through SLI-0124. | External review services, automatic rewriting, a mandatory universal reading grade, or repository-wide blocking of technical content changes the CAP package. | captured |

## Capability Acceptance

- Primary learner controls and headings use familiar task language; the known
  `Topic slug`, `Apply query`, `Approved curriculum graph`, `Graph
  relationships`, `Exact package`, and `Open exact lesson` examples are
  replaced consistently across delivered routes and relevant tests.
- Curriculum state and retained completion are explained in plain language
  without changing deterministic eligibility, evidence, score, version, or
  provenance semantics and without implying mastery or recommendation.
- Errors say what happened in learner terms, avoid exposing private technical
  detail, and identify a safe next action when recovery is available.
- Technical identifiers, digests, versions, and source records remain complete,
  keyboard reachable, screen-reader understandable, and available in both
  themes through progressive disclosure.
- The standard defines preferred patterns, exceptions, ownership, and the
  boundary between learner copy and intentionally technical records.
- The checker blocks only a bounded high-confidence corpus, reports heuristics
  without blocking, ignores generated and intentionally technical material,
  and evaluates changed learner-facing strings by default.
- Anti-rigidity tests prove that specialist terms may remain when explained,
  justified exceptions do not disable unrelated checks, and copy-only changes
  do not trigger irrelevant full-suite work.
- Focused component and Chromium checks preserve actions, hierarchy, content
  completeness, accessibility, responsive behavior, forced colors, reduced
  motion, and light/dark/system-theme equivalence.

## Risks and Non-Goals

Oversimplification can hide material financial or evidence limitations, while
an overzealous checker can make ordinary copy work slower and less precise.
This capability keeps semantic owners authoritative, retains technical records,
uses narrow blocking rules, and treats most language heuristics as review aids.
It does not promise that every reader will understand every financial concept;
specialist terms remain valid when needed and explained at the point of use.

## Documentation Impact

Delivery is expected to add a learner-facing language standard and content
style guide; link them from interface, agent, context-routing, and planning
guidance; update affected web and feature documentation; and record focused
verification evidence. External source links and applicability notes may be
registered, but no proprietary source text or controlled vocabulary is copied
into the repository.

## Completion Evidence

All four approved manifest slices are complete. SLI-0122 established the
learner-facing language standard and applied it to discovery. SLI-0123 applied
the same task-first language and progressive technical records to curriculum
state. SLI-0124 clarified lesson, knowledge-check, completion, and recovery
language. SLI-0125 delivered the bounded changed-copy checker, narrow reasoned
exceptions, fixed readiness integration, candidate-bound affected selection,
and explicit anti-rigidity protection.

The first three slices retain focused component, mocked and isolated live
Chromium, keyboard, accessibility, responsive, forced-color, reduced-motion,
and light/dark/system-theme evidence for the learner routes changed by this
CAP. Their acceptance evidence also preserves exact eligibility, grading,
version, evidence, provenance, answer-secrecy, and safe-failure meaning. The
final tooling-only slice passed its two-packet completion structure, 3
readiness-runner tests, 14 checker tests, 24 affected-verification tests, 11
control-plane regression tests, a controlled scan of 275 regions in 17 files,
planning, documentation, design, compilation, whitespace, and all 29 aggregate
readiness checks. Two platform-capability cases were skipped as designed.

The delivered control blocks only the approved high-confidence corpus. It
keeps heuristics advisory, allows one-source-occurrence exceptions, ignores
generated and intentionally technical material, and does not select language
evaluation for CSS, whitespace, tool documentation, fixtures, or unrelated
implementation. The Windows sandbox's denied OS temporary directory caused an
environment-only first attempt; unchanged tests passed in the prepared local
temporary root and did not trigger a correction cycle.

No public contract, domain authority, runtime state, dependency, provider,
external service, or migration changed. Technical evidence remains complete
and accessible behind plain labels. The residual lexical limitation is
explicit: deterministic checks complement rather than replace human review of
meaning, financial nuance, comprehension, accessibility, and tone. CAP-0030
conforms to its approved package, has no unresolved decision gate, and is
complete.

## Planning History

- 2026-10-15: Shaped from an authorized plain-language and information-
  architecture review of current learner interfaces. The package separates
  discovery, curriculum, and lesson/completion outcomes, then qualifies the
  reusable guidance and deliberately non-rigid checks.
- 2026-10-16: Completed all four approved slices with cumulative learner-route,
  accessibility, browser, failure, provenance, theme, responsive, checker,
  anti-rigidity, and aggregate-readiness evidence. The capability moved to
  `complete` with no material package drift or unresolved durable decision.
