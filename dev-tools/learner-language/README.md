# Learner-Language Check

`check_learner_language.py` provides fast, deterministic feedback for changed
learner-facing copy. It implements only the small automatable subset of the
[user-facing language standard](../../docs/standards/user-facing-language-standards.md).
It is not a grammar service, writing authority, automatic rewriter, reading-
grade gate, or claim of plain-language conformance.

## Use

```powershell
python dev-tools/learner-language/check_learner_language.py
python dev-tools/learner-language/check_learner_language.py --base-ref <revision>
python dev-tools/learner-language/check_learner_language.py --all
python dev-tools/learner-language/check_learner_language.py --all --json
```

The default reads staged, unstaged, and untracked changes and ignores whitespace-
only diffs. `--base-ref` selects lines changed from one exact Git revision.
`--all` is an explicit controlled qualification of all owned learner-facing
TSX source; it is not the everyday mode.

Agent readiness invokes the ordinary changed-copy mode and forwards its exact
`--base-ref` when present. For exact-candidate verification, the affected-check
catalog binds owned application TSX to the submitted packet base revision. A
checker or rule change selects the direct test corpus and controlled full-scope
qualification instead. CSS, generated clients, UI tests/fixtures, tool
documentation, and unrelated code do not select a learner-copy check.

Exit codes are:

- `0`: no blocking finding, including advisory-only results;
- `1`: at least one configured high-confidence defect; and
- `2`: invalid invocation, configuration, source, exception, or Git evidence.

JSON output contains only the selection mode, counts, repository-relative
paths, line numbers, rule identifiers, severities, and bounded guidance. It
does not retain source payloads, approvals, learner information, secrets, or
telemetry.

## Scope and severity

[`rules.json`](rules.json) owns the learner-facing TSX roots, exclusions,
technical-record label, visible attributes, high-confidence rules, and
advisory settings. Generated clients, tests and fixtures, CSS, distribution
output, documentation, identifiers, comments, imports, `<code>` values, and
non-rendered quoted code values are not primary learner copy for this check.
Content inside a native `Technical record` disclosure is also excluded.

Blocking rules cover only reviewed internal phrases that have an accepted
learner replacement. Sentence length, possible jargon, and possible unexplained
acronyms are advisory. Advisory findings never change the exit code, require a
correction loop, reopen completed work, or select broader test suites.
Whitespace and nonfunctional visual styling are outside this tool.

## Narrow exceptions

When a configured blocking phrase is precise and explained, place one comment
immediately before the affected source line:

```tsx
{/* learner-language: allow primary.curriculum-graph; reason=the lesson teaches graph structure; explained=the paragraph below */}
<p>Curriculum graph</p>
```

The directive must name one known rule, give a specific reason, and say where
the explanation appears. It suppresses only that rule on the immediately
following nonblank line. Unknown, malformed, duplicate, or stale directives are
errors; an exception cannot disable a file, advisory output, or another rule.

## Verification

```powershell
python dev-tools/learner-language/test_learner_language.py
python dev-tools/learner-language/check_learner_language.py --all
```

The tests use disposable Git repositories to cover staged/unstaged and
base-revision changes, untracked source, whitespace and CSS changes, technical
records, narrow exceptions, invalid directives, stable JSON, and advisory-only
copy.
