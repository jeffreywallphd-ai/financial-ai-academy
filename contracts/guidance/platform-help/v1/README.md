# Platform Help v1

`platform-help/v1` is an additive read-only contract family:

- `topic.schema.json` defines one immutable exact topic version with a closed
  inert body-node union, safe canonical-source facts, and a canonical digest.
- `search-request.schema.json` defines a bounded literal query, optional closed
  kind filter, page size, and opaque continuation cursor.
- `search-page.schema.json` defines stable exact-version search summaries with
  applicability, publication, and canonical-source facts plus a corpus-bound
  continuation cursor.

Canonical JSON uses UTF-8, sorted object keys, and compact separators. A topic
digest excludes only `topic_digest`; admitted Unicode text is not normalized or
rewritten. Search normalization is separate: it trims and collapses whitespace
and uses Unicode case folding only for matching.

Topic versions use the stable SemVer core form `major.minor.patch`. Prerelease
and build suffixes are not admitted in v1, which keeps exact-version ordering
unambiguous. Cursor envelopes bind the query, kind, corpus, position, and prior
exact result key with a deterministic integrity digest; altered encodings fail
closed. The digest detects modification but is not an authorization mechanism.

Exact reads require both `topic_id` and `topic_version`. There is no `latest`
selector. The contract contains no HTML, Markdown, URL, repository path,
component, script, style, learner identity, prompt, approval, reviewer, or
provider field.
