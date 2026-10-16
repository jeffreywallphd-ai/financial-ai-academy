# Learner-Facing Content Style Guide

- Status: accepted
- Canonical for: interface voice, preferred learner-facing terms, content hierarchy, and message patterns
- Normative requirements: [User-Facing Language Standards](../standards/user-facing-language-standards.md)

## Voice

Write as a calm, precise learning guide:

- direct without sounding abrupt;
- supportive without celebration, pressure, or judgment;
- confident about known facts and explicit about uncertainty;
- educational rather than promotional or advisory; and
- concise in the main flow, with exact supporting evidence still available.

Address the learner as `you` when it makes an action or result clearer. Use
`we` only for a platform action the product actually performs. Do not personify
an algorithm or imply that a model has intent.

## Page and Message Order

For ordinary learner pages, prefer this order:

1. task-focused page title;
2. one short orientation sentence when the title is not enough;
3. primary controls and current learner meaning;
4. supporting explanation and limitations;
5. publication details and educational-use notice; and
6. optional `Technical record` with exact diagnostic facts.

For errors, use: result, protection/recording fact, next action, then optional
technical detail.

## Preferred Terms

The table governs primary learner UI. Technical terms may remain in code,
contracts, developer documentation, or a labeled technical record when the
exact term is useful.

| Avoid in primary UI | Prefer | Technical term is valid when | Reason |
| --- | --- | --- | --- |
| Topic slug | Topic | A developer is documenting the URL or schema field | Learners choose a topic, not an identifier format |
| Apply query | Show results | A technical document explains query execution | The control's result is clearer than its mechanism |
| Exact package | Lesson version | A technical record labels the package ID or digest | Version conveys why a specific lesson is being opened |
| Open exact lesson | Open lesson | Supporting text already shows the version and no substitution occurs | The action remains accurate without implementation wording |
| Approved curriculum graph | Learning path | A methodology or technical record describes the graph contract | Learners navigate a path; approval/version facts remain nearby |
| Graph relationships | How these activities connect | A technical record names relationship types | The heading describes what the learner will understand |
| Current navigation state | Your progress and options | A technical record identifies the navigation-state response | Completion and availability are learner meanings |
| Catalog generation | Current learning catalog | A technical record names the generation value | Learners need to know the selection changed, not how snapshots are built |
| Projection | Progress view or current status | A technical record or methodology page teaches projection semantics | Primary copy should name the result, not the data architecture |
| Projection rebuilt | Progress updated | A technical record shows the rebuild time or source set | The learner cares about the current result |
| Retained completion | Saved completion | A technical record names retention or replay mechanics | Saved is familiar and preserves durable meaning |
| Reproduced from retained Assessment evidence | This completion comes from your saved knowledge-check result | A methodology or technical record explains evidence replay | The learner sees source and meaning without module/storage vocabulary |
| Evaluated by the server from bounded evidence | We use your completed work and course rules to show what is available | A technical record explains server authority and evidence bounds | The plain explanation preserves deterministic authority |
| Provenance | Publication details; Source and history; Technical record | An advanced learning topic explicitly teaches provenance | Choose the heading that describes the facts learners will find |
| Schema version | Data format version | A technical record contains the exact schema identifier | The ordinary label explains why the version exists |
| Graph digest | Learning-path integrity code | A technical record or support workflow needs the digest | Explain the value without hiding it |
| Source-set digest | Evidence-source integrity code | A technical record or support workflow needs the digest | Connect the code to its purpose |
| Projection digest | Progress integrity code | A technical record or support workflow needs the digest | Connect the code to the learner-visible result |
| Valid detail shape | Details we can safely show | Developer/test code names structural validation | Learners need the outcome, not validator terminology |
| Client-supplied detail | Details from this page or link | Technical security documentation distinguishes client authority | Avoid implementation-boundary vocabulary in errors |
| Complete projection | Complete current information | A technical record names an application projection | Explain what was missing or protected |
| Safe presentation checks | Safety checks | A technical record names the exact validators | A shorter phrase is actionable when paired with a next step |
| Private learner session | Learner session | Privacy or security guidance needs the exact boundary | Error copy should focus on starting the session and protecting details |

Do not apply replacements mechanically. Read the complete sentence and preserve
the owning contract's exact semantics.

## Controls

- Use a verb and object: `Show results`, `Open lesson`, `Compare selected`,
  `Try again`, `Return to learning library`.
- Avoid `Submit` when a more specific result is known. `Check answer` is better
  than `Submit` for the knowledge check.
- Use `Cancel` only when work is actually cancelled; use `Back` or `Return to…`
  when navigating without mutation.
- Keep labels short, but do not remove the object when several actions could be
  confused.

## Headings and Labels

- Page titles name the learner task or object: `Learning library`, `Learning
  path`, `Lesson`, `Compare learning opportunities`.
- Section headings describe the contained meaning: `How these activities
  connect`, `Your progress and options`, `Publication details`, `Technical
  record`.
- Status labels use observable meaning: `Completed`, `Available`, `Locked`,
  `Optional`, `Unavailable`.
- Do not use raw enum capitalization or punctuation as visible labels.

## Status Explanations

Use this pattern:

> **Status.** Reason in learner terms. Next action when one exists.

Examples:

- **Available.** You completed the required lesson. You can open this activity.
- **Locked.** Complete “Risk and return basics” first.
- **Optional.** This activity can deepen your understanding, but it is not
  required for the current path.
- **Completion unavailable.** This activity does not yet provide a saved
  completion result.

Keep completion, eligibility, requirement, and availability as separate facts
when the interface exposes all four.

## Loading, Empty, and Error States

### Loading

Name the task rather than the internal operation:

- `Loading your learning library…`
- `Loading this learning path and your current progress…`
- `Checking for a saved completion…`

### Empty

State what is absent and how to change the result when possible:

> No learning opportunities match these filters. Clear a filter or change the
> search words to see more results.

### Session error

> We couldn't start your learner session. No private learning details were
> shown. Try again.

### Changed or missing selection

> This opportunity is no longer in the current learning catalog. Return to the
> learning library to choose another.

### Invalid data

> We couldn't safely show these details. Try again, or return to the learning
> library.

Do not expose validator names, internal fields, selectors, stack traces, or
provider errors.

## Publication and Technical Evidence

Keep the educational-use notice in the normal flow. Use `Publication details`
for publisher, publication date, review date, and other facts learners can
interpret directly. Use `Technical record` for exact IDs, versions, digests,
source fingerprints, policy IDs, schema versions, and evaluation timestamps.

When a technical value is visible, pair it with a purpose-based label and
retain the exact value in selectable text. Do not abbreviate or silently alter
identifiers.

## Financial and AI Examples

- Prefer `Simulated return under these assumptions` over `Expected return`
  when the value is a scenario result rather than a forecast.
- Prefer `Model estimate` plus confidence and limitations over `Your level` when
  evidence does not establish a durable competency fact.
- Prefer `Why this is suggested` over `Why this is best`; recommendations must
  retain learner choice and deterministic eligibility.
- Keep the education-versus-advice notice near actions or conclusions that
  could otherwise be mistaken for investment guidance.

## Testing Content

Test accessible names, actions, required facts, status distinctions, safe next
steps, and technical-record reachability. Avoid exact whole-paragraph assertions
unless the wording itself is a reviewed safety, legal, or contract requirement.
Use small required phrases or semantic roles so clear copy can improve without
rewriting unrelated tests.

Include flexible-shape cases such as empty results, variable topic counts,
multiple reasons, unavailable evidence, and additional technical fields. Copy
must not assume one fixture count or one hard-coded record.

## Contributor Checklist

- What is the learner trying to do?
- Which fact or action must remain in the primary flow?
- Which precise terms are necessary, and where are they explained?
- Which facts belong in publication details or the technical record?
- Does the error protect private details and offer a real next action?
- Does the wording preserve financial, evidence, adaptive, and AI limitations?
- Will the same words and actions remain available to keyboard and assistive-
  technology users at narrow widths and in every theme?
- Do tests protect meaning without freezing prose unnecessarily?
