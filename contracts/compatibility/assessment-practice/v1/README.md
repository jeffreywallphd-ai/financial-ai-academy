# Assessment Practice v1 Compatibility Corpus

This synthetic corpus fixes the first deterministic multi-item practice
definition without changing the existing single-select knowledge-check corpus.

- `approved/definition.json` contains all three private item types.
- `approved/presentation.json` is the answer-safe exact projection.
- `vectors/definition-digest.json` fixes canonical private meaning.
- `vectors/non-ascii-definition-digest.json` fixes raw UTF-8, unescaped
  non-ASCII digest behavior.
- `cases/denials.json` names stable schema and semantic failures.

The fixtures contain no personal information, provider payload, credential,
investment recommendation, suitability claim, or performance claim.
