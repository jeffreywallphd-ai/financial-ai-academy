# Lesson Package v1 Compatibility Corpus

The corpus fixes the cross-language behavior of the version 1 logical package.

- `approved/intro-risk-return/` is the synthetic, source-attributed positive
  package. Its Assessment file is closure-only and has no runtime scoring
  authority.
- `approved/intro-risk-return-practice/` is the additive practice-bearing
  positive package. Its exact private practice definition is validated at
  admission and projected by Assessment, never returned directly to learners.
- `approved/intro-risk-return-project/` is the additive Project-brief package.
  It fixes exact brief identity/digest validation while leaving learner
  Project creation and ownership to the Project module.
- `cases/denials.json` defines stable hostile mutations and expected bounded
  diagnostic codes.
- `vectors/package-index.json` records the exact canonical UTF-8 index bytes,
  package digest, and individual file metadata for the approved package.
- `vectors/immutable-conflict.json` fixes the Content-owned immutable-version
  conflict outcome.

Fixtures contain no personal data, credentials, provider payloads, restricted
datasets, or investment recommendations.
