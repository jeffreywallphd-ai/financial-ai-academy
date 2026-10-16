# Assessment Practice Contract v1

This additive contract family defines one immutable multi-item formative
practice definition, its answer-safe learner presentation, one whole-practice
submission, its deterministic result, and a correlated completion event. It
does not change the existing `assessment/v1` knowledge-check family.

Version 1 supports exactly three closed item types:

- `single_select` with `single-select-exact-match@1.0.0`;
- `multiple_select` with `multiple-select-exact-set@1.0.0` and no partial credit;
- `numeric_entry` with `numeric-exact-or-inclusive-range@1.0.0` over canonical
  fixed-decimal strings.

Every item is worth one point. The definition contains private answer and
feedback meaning. The presentation carries only exact identity/version/digest
provenance, learner-visible policy and references, prompts, options, and safe
input constraints. It excludes private answer values, ranges, correct option
identities, and feedback.

The submission contains one response for every definition item. Response array
order is not meaningful; item IDs correlate responses and results return in
definition order. Multiple selections are exact sets and are sorted with
responses by item ID before the canonical request fingerprint is calculated.
The fingerprint is lowercase SHA-256 over compact sorted-key UTF-8 JSON with
`ensure_ascii=false`. Numeric entries remain canonical fixed-decimal strings
at the definition's exact scale.

Every item scores zero or one. The activity score is their sum and the result
uses `all_correct` only when the total equals the maximum; otherwise it uses
`review_needed`. Results expose the submitted values and only the applicable
reviewed feedback/reference branch. They never expose correct answer values,
accepted numeric ranges, private evaluator objects, mastery, suitability, or
advice. `assessment.practice.completed@1.0.0` carries a bounded score and
provenance summary without submitted values or feedback, and correlates it to
server-issued learner, attempt, evidence, submission, event, and time metadata.

The definition digest is lowercase SHA-256 over the UTF-8 JSON bytes of the
private `practice` object serialized with sorted keys and compact separators.
JSON string content is encoded directly as UTF-8 (`ensure_ascii=false`):
non-ASCII characters are not replaced with JSON `\u` escapes. Producers must
normalize authoring text before contract creation if their source system can
represent canonically equivalent Unicode with different code-point sequences;
the contract does not perform implicit Unicode normalization.
The paired compatibility corpus is in
[`contracts/compatibility/assessment-practice/v1`](../../../../compatibility/assessment-practice/v1/README.md).

Schemas and the dependency-light compatibility runner are transport-neutral.
They do not authorize identity, issue time or IDs, persist evidence, publish an
event, expose HTTP, or create a separate browser or AI mode. Run their contract
evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_practice
```
