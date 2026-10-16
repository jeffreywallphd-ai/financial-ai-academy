---
id: WRK-0068
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0122
capability: CAP-0030
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["AGENTS.md", "docs/README.md", "docs/standards/README.md", "docs/standards/user-facing-language-standards.md", "docs/standards/interface-design-standards.md", "docs/standards/change-impact-matrix.md", "docs/design/README.md", "docs/design/content-style-guide.md", "docs/context/prompt-routing.md", "docs/context/pack-catalog.json", "docs/context/packs/index.pack.md", "docs/context/packs/interface-design.pack.md", "docs/external-sources/source-register.md", "docs/planning/README.md", "docs/planning/work-packets/WRK-0068-establish-learner-facing-language-standard.md", "docs/planning/vertical-slices/SLI-0122-choose-learning-opportunities-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: d3d737bca0680e4f766fa771bf33860bab044a73
claim_id: WRK-0068:1a63b064-d44f-4867-85d6-926143dc406e
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T08:57:42Z
---

# Agent Work Packet: Establish the Learner-Facing Language Standard

## Objective and Deliverable

Create one normative learner-facing language standard and one design content
style guide that turn the approved CAP-0030 principles into usable repository
rules. Supply an initial preferred-term map, actionable error and status
patterns, progressive-disclosure rules for technical evidence, narrowly scoped
source citations, and routing links that future agents can discover before
changing learner-facing copy.

The result must be useful without becoming a universal prose gate: it defines
required semantic outcomes and high-confidence defects while treating sentence
length, passive voice, reading level, and similar heuristics as review aids.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the interface-design and delivery-planning
context packs. Read CAP-0030, SLI-0122, the product vision, domain glossary,
education-versus-advice guidance, design README and style guide, interface and
documentation standards, change-impact matrix, planning guide, external-source
governance, and current context routing/catalog. Inspect the delivered catalog,
curriculum, lesson, assessment, and failure-state copy plus their component and
browser tests so the term map reflects real usage rather than hypothetical
examples.

## Decisions and Assumptions

- The standard is informed by ASD-STE100 controlled-language principles and
  public plain-language/accessibility guidance. The repository does not claim
  conformance, copy a controlled vocabulary, or make an external standard its
  product authority.
- Product, domain, contract, architecture, risk, and security owners continue
  to define meaning. The language standard governs learner presentation and
  must route semantic ambiguity back to the owning source.
- Primary learner copy leads with the task, status, reason, and next safe
  action. Exact identifiers, versions, digests, source records, and other
  diagnostics remain available under accessible progressive disclosure when
  they are not needed for the primary task.
- Necessary financial, learning, and evidence terms may remain when precise,
  introduced in familiar language, and explained at the point of use.
- This packet writes guidance and routing only. Application copy and automated
  checking follow in later dependency-ordered packets.

## In Scope

- Required principles for audience and purpose, familiar and consistent words,
  active/direct construction, one main idea at a time, front-loaded structure,
  meaningful headings and labels, actionable errors, and concise next steps.
- Rules for preserving financial nuance, educational limitations, deterministic
  policy meaning, evidence provenance, accessibility, and safe failure detail.
- A three-tier content model: primary task copy, supporting explanation, and
  optional technical record with explicit accessibility requirements.
- An initial term map covering the researched catalog, curriculum, navigation,
  lesson, session, knowledge-check, completion, evidence, and error examples.
- Preferred patterns for controls, headings, statuses, loading, empty states,
  denials, invalid data, retry/recovery, and specialist-term introduction.
- Non-rigid verification policy: bounded hard failures, advisory heuristics,
  changed-copy default, documented reasoned exceptions, no automatic rewrite,
  and exclusions for generated code and intentionally technical records.
- Informative external-source register entries with version/review posture,
  applicability, and re-review triggers.
- Discoverability links in agent startup, documentation/design/standards
  indexes, interface routing, context catalog/packs, change-impact analysis,
  and planning guidance.

## Out of Scope

Application component or test changes; a checker implementation; domain or API
renaming; localization; legal/risk disclosure changes; new design tokens,
icons, or component patterns; external services; copied standards text; formal
conformance claims; mandatory reading-grade thresholds; universal bans on
passive voice or sentence length; and any new approval stage.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Normative language guidance | product/domain/risk meaning and current learner copy | new user-facing language standard | Define presentation requirements without redefining semantics |
| Design content guidance | design character, interface hierarchy, existing controls/states | new content style guide plus design index link | Turn requirements into voice, term, and pattern examples |
| Repository routing | agent startup, docs/standards/planning indexes, change matrix, prompt routing and context packs | listed routing files only | Make the standard discoverable for future interface work |
| External-source posture | source-governance README and current register | source register | Record informative sources without promoting them above canonical owners |
| Planning evidence | CAP-0030, SLI-0122, current register | this packet, SLI-0122 packet table/history, register | Keep JIT status and scope coherent |

No application, contract, generated client, test, dependency, token, icon,
mockup, backend, deployment, or runtime file may change.

## Contracts and Interfaces

The standard's contract is textual but testable. It must distinguish mandatory
outcomes from advisory heuristics, name the canonical semantic owners, define
the primary/supporting/technical information layers, and provide a preferred-
term table with `avoid in primary UI`, `prefer`, `when the technical term is
valid`, and `reason` columns.

The external source register records direct primary URLs, source/version or
access posture, applicability, review date, re-review trigger, and the explicit
fact that the sources are informative rather than product authority. The
context catalog remains valid JSON and routes interface-copy changes to the
interface-design pack and new canonical sources.

## Dependencies and Parallel Safety

CAP-0030 is approved, SLI-0122 is ready, CAP-0001 and CAP-0004 are complete,
and no durable decision gate is open. This is the first slice packet. Its
routing and planning files are shared coordination surfaces, so it is not
parallel-safe with another packet editing repository guidance or planning
state. Later packets consume its accepted language contract and cannot start
before it completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Ordinary learner task | A contributor writes a heading, label, status, or instruction | The standard is applied | The task and next action use familiar, consistent words before implementation detail | standard/style examples |
| Technical evidence | A page must retain versions, digests, identifiers, or source records | Information hierarchy is chosen | Essential meaning remains in the primary flow and complete diagnostics remain in an accessible `Technical record` | information-layer contract |
| Necessary specialist term | A precise financial or learning term has no safe everyday substitute | The term is introduced | The precise term remains, with immediate plain explanation and canonical meaning intact | specialist-term rule |
| Safe error | A protected read is denied, missing, invalid, or unavailable | Error copy is written | It says what happened, exposes no private detail, and gives a safe next action when available | error pattern table |
| Heuristic warning | Copy has a long sentence, passive construction, or high reading grade | A future checker evaluates it | The issue is advisory unless a separately defined high-confidence defect is present | verification policy |
| Reasoned exception | A technical term is necessary in an explicitly labeled diagnostic record | The term is retained | A local reasoned exception affects only that occurrence and does not disable unrelated checks | exception contract |
| Source use | External writing guidance informs a rule | A contributor follows the repository standard | Canonical product/domain/risk meaning still wins and no conformance claim is made | source register and authority text |

## Verification Commands

Run:

```powershell
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python docs/planning/skills/validate_suite.py
python dev-tools/agent/check_ready.py
git diff --check
```

Also parse `docs/context/pack-catalog.json` as JSON and search changed guidance
for stale links, accidental approval/reviewer metadata, copied personal
identifiers, unsupported conformance claims, absolute bans on ordinary writing
heuristics, and language that makes external sources authoritative.

## Documentation and Evidence Update

Record the standard and style-guide sections delivered, the initial term-map
coverage, routing files updated, informative sources and re-review triggers,
validation results, anti-rigidity protections, assumptions, and known gaps in
this packet. Do not copy approval or reviewer identity, status, authority,
scope, dates, or history from ignored local state into tracked files.

## Stop Conditions

Stop for a domain, API, risk, privacy, legal, recovery, model-authority, or
financial-claims semantic decision; formal standards or regulatory conformance;
copied proprietary text or vocabulary; an external service or content egress;
new visual or accessibility behavior; a universal hard readability threshold;
removal of provenance; a new approval stage; active file-scope collision;
conflicting canonical authority; or material CAP/SLI drift.

## Required Handoff

Report the exact standard and content-guide paths; mandatory versus advisory
rules; information-layer and technical-record contract; initial term-map
coverage; source and licensing posture; routing changes; validation and
anti-rigidity results; changed paths; assumptions and known gaps; and
confirmation that no application, contract, domain, risk disclosure, runtime,
dependency, token, icon, or approval behavior changed. Leave JIT-B dependency-
ready or return a bounded blocker.

## Planning History

- 2026-10-16: Authored just in time as the first SLI-0122 packet. The packet
  creates the reusable language contract and routing needed by later UI work
  while excluding application behavior and rigid universal prose gates.
