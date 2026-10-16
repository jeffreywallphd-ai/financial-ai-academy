---
id: SLI-0125
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: CAP-0030
depends_on: ["SLI-0122", "SLI-0123", "SLI-0124"]
decision_gates: []
---

# Vertical Slice: Sustain Plain-Language Interface Quality

## Outcome and User Scenario

A contributor changing learner-facing interface text gets fast, local feedback
for a small set of clear mistakes without being forced through a general prose
or visual-style gate. The check examines changed learner-facing copy by default,
distinguishes blocking defects from advisory observations, respects narrow
reasoned exceptions, and leaves generated, technical, test-fixture, operator,
and intentionally disclosed records alone.

Learners benefit because future interface work is less likely to reintroduce
internal field names or avoidable computing terms into primary tasks, while
specialist financial and learning language remains available when it is precise
and explained.

## Scope Boundaries

### In Scope

- A repository-local deterministic learner-language checker with stable human
  and machine-readable results.
- Diff-aware selection of changed learner-facing TypeScript/TSX strings, with a
  bounded explicit full-scope mode for controlled qualification.
- A small repository-owned corpus for high-confidence raw field names,
  internal values, and computing terms that already have approved learner
  replacements.
- Advisory observations for possible complexity, acronyms, noun clusters, and
  similar judgment-dependent patterns that never determine the exit code.
- Local, narrow, reasoned exceptions that identify one rule, one source region,
  and where the required specialist term is explained.
- Deterministic positive, negative, exclusion, exception, diff-scope, and
  anti-rigidity tests, including proof that harmless whitespace and
  nonfunctional style do not enter this language gate.
- Aggregate readiness integration and contributor documentation that preserve
  focused affected-check selection.

### Out of Scope

- Automatic rewriting, an external grammar or AI service, a mandatory reading
  grade, universal repository prose linting, or a controlled-vocabulary claim.
- Scanning generated clients, schemas, identifiers, logs, developer/operator
  documentation, test fixtures that mirror contracts, or values inside an
  explicit technical-record fixture by default.
- Treating sentence length, passive voice, unexplained-acronym guesses, noun
  clusters, possible jargon, formatting, or visual preference as blockers.
- Changing product/domain terminology, public contracts, financial or risk
  disclosures, assessment or learning policy, UI styling, layout, tokens,
  icons, browser behavior, or runtime code.
- Requalifying every completed interface or requiring unrelated backend,
  database, Docker, or live browser suites for a copy-only change.

## Canonical Context and Decisions

- CAP-0030 owns the approved four-slice package, changed-copy default,
  narrowly blocking corpus, advisory heuristics, local exceptions, and
  anti-rigidity posture.
- SLI-0122 established the normative learner-facing language standard, content
  style guide, preferred terms, progressive disclosure, and minimum evidence.
  SLI-0123 and SLI-0124 applied and qualified those rules in the learning-path
  and lesson/completion flows.
- The change-impact matrix requires focused meaning and accessibility evidence
  for learner copy while adding backend or live checks only when behavior
  crosses those boundaries.
- Testing standards require deterministic refusal paths and proportionate
  evidence. Aggregate readiness is a fixed allowlist, not authority to expand a
  copy change into unrelated product qualification.
- No identity, tenancy, licensing, model-authority, provider, queue,
  encryption, recovery, legal/commercial, or external-execution choice is
  introduced. Decision readiness is therefore sufficient.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Diff-aware tiered checker, narrow exceptions, readiness integration, and anti-rigidity qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Document a manual review checklist without executable feedback | yes | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 11 |
| C. Run a universal blocking readability and grammar linter over the repository | no - exceeds the CAP and makes subjective style a delivery gate | - | - | - | - | - | - | - |
| D. Send changed copy to an external AI or grammar service | no - external processing and provider authority are outside the approved package | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the highest-scoring eligible increment. It provides immediate
contributor feedback and sustained learner value across the complete path from
changed source selection through deterministic findings, local exceptions,
aggregate reporting, and qualification. Accepted standards settle its
authority and scope, the checker is isolated from runtime product behavior,
the corpus and refusal tests make results directly observable, and removal
requires no data or contract migration. Candidate B is safe but provides less
value, no automatic changed-copy boundary, and weaker regression evidence.
Candidates C and D violate the approved non-rigid and repository-local limits,
so they are not scored.

## Boundary Path

1. The accepted language standard and content guide remain the semantic source;
   the checker encodes only their explicitly high-confidence, automatable
   subset.
2. A tracked configuration identifies owned learner-facing source roots,
   narrow exclusions, blocking term/replacement pairs, advisory patterns, and
   reasoned source-local exceptions.
3. The CLI resolves changed lines from an explicit base revision or the local
   Git diff; controlled full-scope qualification is an explicit option rather
   than the everyday default.
4. Source selection extracts only candidate user-visible literals and excludes
   generated, test, technical-record, code-identifier, and non-interface
   regions before applying rules.
5. Blocking findings produce a nonzero result with file, line, rule, and plain
   remediation guidance. Advisory findings are reported separately and never
   change the exit code.
6. The fixed aggregate readiness runner invokes the checker with the same base
   revision it uses for lifecycle checks; local no-diff runs remain valid and
   fast.
7. Deterministic tests exercise true defects, ordinary clear copy, specialist
   terms with explanation, narrow exceptions, exclusions, changed-only scope,
   advisory-only text, whitespace, and unrelated styling.

## Contracts, Data, and Provenance

No public application schema, generated client, API, event, persistence,
identity, grading, learner-state, provider, or runtime contract changes. The
checker owns a small repository-internal configuration and a CLI result
contract. Human output names selected files and findings. Machine output may
contain repository-relative paths, line numbers, rule identifiers, severity,
and summaries; it must not contain approval data, learner data, secrets, or
external telemetry.

An exception is configuration, not authority. It is limited to one rule and
source region, includes a reason and explanation location, and cannot suppress
another rule. Advisory counts are evidence only and cannot fail readiness,
reopen completed CAPs, or imply language conformance.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Changed primary label contains an owned internal term | The checker reports the file, line, blocking rule, and approved learner wording and returns a failure | Checker unit/CLI test |
| Changed copy contains only a long sentence, passive construction, possible acronym, or possible jargon | The checker may report an advisory observation but returns success | Checker anti-rigidity test |
| A specialist term is precise and explained nearby | The term is accepted directly or through one narrow reasoned exception without disabling unrelated rules | Checker corpus/exception test |
| Generated, test-fixture, developer, log, identifier, or technical-record content contains technical vocabulary | Default changed-copy selection ignores the intentionally technical region | Selection/exclusion test |
| Only whitespace or nonfunctional CSS changes | The language check selects no learner copy and returns success without requesting review or broader suites | Diff-scope anti-rigidity test |
| One exception is malformed, stale, broad, or points outside an owned source | Configuration validation fails narrowly and identifies only the invalid exception | Configuration refusal test |
| A contributor runs aggregate readiness with a base revision | Readiness forwards the base to the language check and includes one privacy-minimized check result | Agent-readiness test |
| A controlled maintainer requests full-scope qualification | Owned learner-facing source is checked without expanding into schemas, generated output, or documentation | CLI integration test |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The planned dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| JIT-A | Implement the deterministic diff-aware checker, owned configuration, narrow exceptions, corpus, and direct unit/CLI evidence | SLI-0122, SLI-0123, SLI-0124 | none | planned |
| JIT-B | Integrate the checker with aggregate readiness, add anti-rigidity and forwarding evidence, reconcile documentation, and qualify the slice | JIT-A | none | planned |

## Verification and Qualification

Run the checker test suite and CLI integration scenarios, its controlled
full-scope qualification, the agent-readiness runner tests affected by the new
allowlisted check, planning and documentation validation, Git whitespace, and
`python dev-tools/agent/check_ready.py`. Run design-system validation because
the checker implements interface guidance, but do not select UI browser,
backend, database, Docker, or live qualification unless implementation changes
those boundaries.

Tests must assert rule identifiers, selected regions, severity, exit behavior,
and bounded exceptions rather than exact full prose or an arbitrary advisory
count. A pure formatting, CSS, or advisory-only fixture must remain green.

## Rollback and Migration

No data, contract, or runtime migration exists. Rollback removes the readiness
entry, checker/configuration, and its documentation/tests together. Existing
learner interfaces and the normative language guidance remain valid.

## Stop Conditions

Stop for automatic rewriting; external text processing; learner or repository
text egress; a universal reading-grade or prose gate; repository-wide blocking
outside owned learner-facing source; a new domain/API rename; semantic changes
to financial, risk, mastery, competency, recommendation, evidence, privacy, or
AI-authority language; a required browser/runtime change; conflicting canonical
guidance; an overlapping active file claim; or material CAP-0030 drift.

Do not stop, request approval, or reopen review for whitespace, advisory style
observations, or nonfunctional visual polish. Fix trivial local issues directly
or route optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery updates the development-tools index, agent-readiness documentation,
interface-language verification guidance, and the affected assurance map. It
records the checker/configuration boundary, exit semantics, exclusions,
exception format, base-ref behavior, exact test results, full-scope result,
aggregate readiness result, assumptions, known gaps, and confirmation that no
runtime or public contract changed.

## Planning History

- 2026-10-16: Refined as the final CAP-0030 increment after SLI-0122 through
  SLI-0124 completed. Candidate A scored 14/14 because it sustains the accepted
  language contract through a bounded changed-copy control and deterministic
  anti-rigidity evidence without turning subjective prose, formatting, or
  nonfunctional styling into delivery gates. Two just-in-time packet seams
  separate the reusable checker from readiness integration and final
  qualification. The refinement conforms to the approved CAP package and adds
  no decision gate.
