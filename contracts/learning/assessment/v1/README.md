# Assessment Contract v1

This contract family defines the first bounded Assessment-owned knowledge
check. Version 1 supports exactly one required `single_select` item, one
selected option, the `single-select-exact-match@1.0.0` scoring policy, integer
scores of zero or one, and reviewed plain-text feedback.

- `definition.schema.json` validates the private immutable definition.
- `presentation.schema.json` validates the answer-safe learner view.
- `submission.schema.json` validates one exact-version response command.
- `result.schema.json` validates the retained result and evidence record.

The definition digest is lowercase SHA-256 over the RFC 8259 UTF-8 JSON bytes
of the `assessment` object serialized with sorted keys and separators `,` and
`:`. It therefore identifies private definition meaning without requiring a
self-referential file digest. The lesson package separately retains the exact
file digest.

The presentation deliberately excludes `correct_option_id` and feedback. A
submission contains no learner selector or client timestamp. The application
supplies authenticated learner context, server time, and opaque evidence IDs.

Run the executable conformance evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/assessment
```

