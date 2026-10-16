# Project Workspace v1 Compatibility Corpus

This synthetic corpus fixes the first Project workspace contract family.

- `approved/brief.json` fixes Content-owned learning-project meaning and its
  canonical digest.
- `approved/independent-intent.json` and `approved/learning-intent.json` fix
  the two closed creation origins.
- `approved/independent-shell.json` and `approved/learning-shell.json` fix the
  learner-safe, server-owned Project representation.
- `approved/workspace.json` varies notes, HTTPS references, three inert
  artifact kinds, result classification, environment evidence, and one
  synthetic owner-validated typed reference without claiming a production
  Portfolio adapter.
- `approved/workspace-mutation-intent.json` fixes a client-authored artifact
  declaration at one expected live revision. Accepted identity, version, time,
  and storage facts remain server-owned.
- `approved/snapshot-close-intent.json` and `approved/snapshot.json` fix exact
  revision closure and canonical immutable references while the live workspace
  remains separate.
- `approved/evidence-export.json` fixes an authorized deterministic manifest
  with included and use-restricted inert files.
- `vectors/non-ascii-brief-digest.json` proves direct UTF-8 hashing without
  JSON ASCII escaping or implicit Unicode normalization.
- `vectors/non-ascii-snapshot-digest.json` applies that canonical rule to a
  non-ASCII workspace record used by snapshot construction.
- `cases/denials.json` and `cases/workspace-denials.json` fix bounded failures
  for unsupported, contradictory, client-authoritative, unsafe path,
  active-effect, incomplete-provenance, digest, and invalid lifecycle/time
  meaning.

Every identity and value is synthetic. The corpus contains no personal data,
credential, provider payload, host or storage path, executable control,
Assessment response, mastery claim, market observation, live Portfolio state,
investment recommendation, or suitability claim. The `portfolio` owner value
is a synthetic cross-module reference exercised through test-only semantics;
it is not a live adapter, validation source, or copied financial state.
