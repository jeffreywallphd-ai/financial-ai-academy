# User-Facing Language Standards

- Status: accepted
- Canonical for: plain, clear English in learner-facing interfaces and messages
- Design application: [Content Style Guide](../design/content-style-guide.md)

## Purpose and Authority

Financial AI Academy should explain learning and financial concepts precisely
without making learners decode software, storage, contract, or data-pipeline
terminology. These standards govern presentation. They do not rename domain
concepts, public contracts, API fields, code, or technical records.

Product, domain, contract, architecture, risk, security, and accepted ADR
sources continue to own meaning. If simpler wording could change that meaning,
stop and return to the owning source. Never simplify away an educational-use,
financial-risk, privacy, authorization, evidence, version, or AI-authority
boundary.

The rules are informed by controlled-language, public-sector plain-language,
accessibility, and financial-disclosure guidance recorded in the
[external-source register](../external-sources/source-register.md). The project
does not claim ASD-STE100, ISO, WCAG, or regulatory conformance from these local
rules or automated checks.

## Required Outcomes

Learner-facing content must:

1. lead with the learner's task, result, or next safe action;
2. use familiar, consistent words unless a precise specialist term is needed;
3. keep one main idea in each sentence or list item where practical;
4. use active, direct construction when the actor matters;
5. use headings and labels that describe the content or action that follows;
6. explain status and failure in learner terms before implementation detail;
7. preserve exact evidence, version, provenance, and limitation meaning;
8. expose equivalent content and actions to visual, keyboard, and assistive-
   technology users in every supported theme and responsive layout; and
9. avoid implying mastery, suitability, advice, compliance, certainty, or a
   guaranteed outcome when the evidence does not support that claim.

These are outcome requirements, not a prescribed sentence template. Writers
may choose different clear wording when it preserves the same meaning and
interaction.

## Three Information Layers

### 1. Primary task content

Place the information needed to understand or complete the current task in the
main flow:

- what this page or control is for;
- the current learner-visible status;
- why an action is available or unavailable;
- the most important limitation; and
- the next safe action, when one exists.

Do not make a learner open a disclosure to learn why an action is blocked, what
a score means, whether a value is simulated, or whether content is educational
rather than advice.

### 2. Supporting explanation

Use concise supporting text for definitions, prerequisites, assumptions,
review context, confidence, or limitations that help the learner interpret the
primary content. Put the explanation near the affected value or action.

### 3. Technical record

Versions, stable identifiers, digests, source fingerprints, policy identifiers,
evaluation timestamps, schema names, and diagnostic references may appear in a
`Technical record` disclosure when they are not needed for the primary task.
The disclosure must:

- remain in the same authorized page and not require a new permission;
- use a native, keyboard-operable control with a meaningful accessible name;
- retain every required fact rather than replacing it with a vague summary;
- use definition lists, tables, or labeled groups instead of an unexplained
  value dump; and
- explain an unfamiliar label when the value is useful to learners or support.

Progressive disclosure changes prominence, not authority or retention.

## Word and Sentence Choices

- Prefer the common word that preserves the exact meaning: `use` over
  `utilize`, `start` over `initialize`, and `show` over `render` in primary UI.
- Use one term for one concept inside a flow. Do not rotate among synonyms for
  variety when consistency aids understanding.
- Put the action in the control label: `Show results`, `Open lesson`, `Try
  again`, or `Return to learning library`.
- Name the learner-visible object, not its implementation: `learning path`
  instead of `curriculum graph` in a page title, and `current catalog` instead
  of `catalog generation` in an error.
- Prefer active voice when it identifies a useful actor: `We could not start
  your learner session.` Passive voice remains valid when the actor is unknown,
  irrelevant, or would distract from the result.
- Put conditions before actions only when the learner needs the condition to
  interpret the action. Otherwise lead with the result.
- Use short paragraphs and lists to group related ideas. Do not split a precise
  financial or evidence statement merely to satisfy a sentence-length target.
- Expand an acronym on first learner-facing use unless the abbreviation is the
  ordinary name learners are expected to know in that context.

## Specialist Terms

A specialist term is valid when it is required for precision, belongs to the
product or domain vocabulary, or is the object the learner is studying. On
first use, pair it with a brief explanation, example, or nearby glossary/help
link. Do not replace a precise concept with an everyday word that changes its
scope.

Examples:

- Keep `standard deviation` in a statistics lesson, then explain what its
  magnitude represents in that example.
- Keep `provenance` in an advanced methodology explanation when the learner is
  studying provenance; use `Source and history` or `Technical record` as the
  ordinary page heading elsewhere.
- Keep a digest field label in a technical record when support needs the exact
  value; do not lead an ordinary status message with the digest.

## Status, Evidence, and Adaptive Learning

- State observable facts before interpretation: `Completed on 14 October` is
  clearer than a generic `success` label.
- Keep completion, eligibility, requirement, availability, competency, and
  mastery distinct. Never collapse them into one friendly-sounding status.
- Say what evidence supports a result. Prefer `This completion comes from your
  saved knowledge-check result` over storage or projection terminology.
- Explain deterministic learning-path status in terms of completed work and
  course rules. Do not imply that an AI system chose or required the learner's
  next action when it did not.
- Preserve calibrated uncertainty, unavailable evidence, and abstention. Do not
  turn `unknown` into a positive or negative claim merely to make copy shorter.

## Financial and AI Content

- Preserve the distinction among observed, calculated, simulated, predicted,
  and generated information.
- Keep units, currency, time basis, adjustment basis, assumptions, source,
  confidence, and educational-use limitations where they affect meaning.
- Avoid brokerage, urgency, profit-celebration, suitability, or personalized-
  advice language.
- Describe AI output as generated or estimated input with its source,
  limitations, review state, and deterministic fallback. Do not present it as
  authoritative grading, eligibility, authorization, or financial policy.

## Errors and Recovery

An error or unavailable state should answer, in this order:

1. What could not be completed?
2. Did the system protect or record anything important?
3. What can the learner do next?
4. Is technical detail useful to support, and if so, where is it available?

Do not expose stack traces, internal selectors, storage names, policy payloads,
learner identifiers, answers, or provider errors. Do not promise that retrying
will succeed. If no safe recovery exists, say so directly and provide the
nearest useful navigation action.

Prefer:

> We couldn't start your learner session. No private learning details were
> shown. Try again, or return to the learning library.

Avoid:

> Private learner session initialization failed during protected projection
> loading.

## Controls, Headings, and Help

- Buttons and links describe their result, not the mechanism.
- Field labels describe the expected value; placeholder text never substitutes
  for a visible label.
- Headings describe learner meaning and preserve a logical hierarchy.
- Tooltips supplement visible labels; they do not hold essential instructions.
- Help text appears before a likely error when it can prevent that error.
- Repeated controls use the same accessible name for the same action unless
  surrounding context must distinguish them.

## Verification Without Excessive Rigidity

### High-confidence defects

A changed-copy check may block when a learner-facing primary control or heading
contains a repository-defined raw enum, internal field name, known computing
term with an approved replacement, missing accessible name, or error that lacks
an available safe next action. Each blocking rule needs a focused positive and
negative corpus.

### Advisory review

Sentence length, passive voice, reading grade, noun clusters, acronyms,
synonyms, and possible jargon are advisory signals. They may prompt review but
must not independently fail delivery.

### Scope

Check changed learner-facing strings by default. Exclude generated clients,
schemas, code identifiers, tests whose fixture values intentionally mirror a
contract, logs, developer/operator documentation, and content inside an
explicit technical-record fixture unless a rule specifically owns that layer.

### Exceptions

A necessary exception must be local, reasoned, and narrow. It identifies the
term or rule, why precision requires it, and where the explanation appears. An
exception never disables unrelated checks and never authorizes a semantic or
risk change.

Automated tooling must not rewrite copy. Human review remains responsible for
meaning, financial nuance, tone, and comprehension.

## Review Checklist

- Can a learner identify the page purpose and next action from headings and
  controls alone?
- Does the copy use the same word for the same concept?
- Are specialist terms necessary and explained?
- Are error states actionable without exposing private implementation detail?
- Are exact versions and provenance still available?
- Are completion, eligibility, competency, mastery, and recommendation kept
  distinct?
- Are financial and AI limitations still accurate and prominent enough?
- Do keyboard, screen-reader, narrow, zoomed, forced-color, and themed views
  receive equivalent content and actions?
- Do tests protect meaning and interaction without freezing every sentence?

## Minimum Evidence

Copy-only implementation requires focused component or browser evidence for
changed accessible names, actions, content presence, failure recovery, and
progressive disclosure; documentation and design-system checks; and the fixed
aggregate readiness gate. Add contract, backend, database, or complete live
qualification only when the affected behavior actually crosses those
boundaries.

