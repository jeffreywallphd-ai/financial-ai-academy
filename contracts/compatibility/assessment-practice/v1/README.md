# Assessment Practice v1 Compatibility Corpus

This synthetic corpus fixes the first deterministic multi-item practice
definition without changing the existing single-select knowledge-check corpus.

- `approved/definition.json` contains all three private item types.
- `approved/presentation.json` is the answer-safe exact projection.
- `approved/submission.json`, `result.json`, and `completion-event.json` fix one
  whole-attempt chain with mixed deterministic outcomes.
- `vectors/definition-digest.json` fixes canonical private meaning.
- `vectors/non-ascii-definition-digest.json` fixes raw UTF-8, unescaped
  non-ASCII digest behavior.
- `vectors/request-fingerprint.json` and `order-equivalent-submission.json` fix
  canonical response and multiple-selection order independence.
- `cases/denials.json` and `cases/submission-denials.json` name stable schema,
  definition, submission, result, and event failures.
- `approved/draft-save.json`, `draft.json`, and `retry-state.json` fix one
  partial conditional save, its server-owned representation, and visible retry
  state. `cases/draft-retry-denials.json` fixes stale, contradictory, private,
  and client-authority denials.

The approved request is intentionally not in definition order. Contract
validation correlates by item ID, scores against the exact private definition,
and emits results in definition order. The fixed result contains only submitted
values and the applicable safe feedback; correct answers, unused feedback
branches, and evaluator rules remain private.

The fixtures contain no personal information, provider payload, credential,
investment recommendation, suitability claim, or performance claim.

The additive draft and retry records do not change accepted practice bytes.
Empty through complete response subsets are valid drafts. Requests carry only
an expected revision; server drafts carry the positive revision, UTC save
time, and canonical response fingerprint. Retry state is derived from accepted
attempt count and the exact `formative-retry@1.0.0` policy for every limit from
1 through 10.
