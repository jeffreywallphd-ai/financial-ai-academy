# Assessment Practice Contract v1

This additive contract family defines one immutable multi-item formative
practice definition and its answer-safe learner presentation. It does not
change the existing `assessment/v1` knowledge-check family.

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

The definition digest is lowercase SHA-256 over the UTF-8 JSON bytes of the
private `practice` object serialized with sorted keys and compact separators.
JSON string content is encoded directly as UTF-8 (`ensure_ascii=false`):
non-ASCII characters are not replaced with JSON `\u` escapes. Producers must
normalize authoring text before contract creation if their source system can
represent canonically equivalent Unicode with different code-point sequences;
the contract does not perform implicit Unicode normalization.
The paired compatibility corpus is in
[`contracts/compatibility/assessment-practice/v1`](../../../../compatibility/assessment-practice/v1/README.md).

Run the contract evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_practice
```
