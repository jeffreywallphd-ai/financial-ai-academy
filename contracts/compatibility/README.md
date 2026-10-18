# Compatibility Evidence

Old/new fixtures, schema-diff classifications, migration samples, and
explicitly approved breaking-change records live here.

- [`lesson-package/v1/`](lesson-package/v1/README.md) fixes portable package
  admission, integrity, canonicalization, and immutability behavior.
- [`assessment/v1/`](assessment/v1/README.md) fixes the deterministic
  single-select definition/presentation/submission/evidence/event chain,
  expected outcomes, denial codes, and immutable successor package.
- [`discovery/v1/`](discovery/v1/README.md) fixes the approved lesson
  opportunity, owner-fact fingerprint, browse generation, stable ordering, and
  bounded contract denials without implying ranking or non-lesson execution.
- [`discovery/query/v1/`](discovery/query/v1/README.md) fixes deterministic
  query normalization, filters, paging, and bounded denials over discovery v1.
- [`assessment-practice/v1/`](assessment-practice/v1/README.md) fixes
  multi-item practice, partial-draft, retry-state, result, and completion-event
  compatibility without changing accepted knowledge-check contracts.
- [`curriculum-practice-review/v1/`](curriculum-practice-review/v1/README.md)
  fixes exact review-resource mappings, safe unavailable behavior, and
  declaration-ordered selection.
- [`learner-model-practice-history/v1/`](learner-model-practice-history/v1/README.md)
  fixes rebuildable ordered attempt summaries, source digests, confidentiality,
  and duplicate-replay behavior.
- [`platform-help/v1/`](platform-help/v1/README.md) fixes exact-version safe
  topics, canonical digests, deterministic literal search, cursor binding, and
  bounded denials without admitting active content or private repository data.
- [`contextual-help/v1/`](contextual-help/v1/README.md) fixes exact safe
  feature-context mappings, canonical digests, closed purposes, and source/topic
  correlation without admitting routes, mutable feature state, or browser-only
  policy.
- [`feature-guidance/v1/`](feature-guidance/v1/README.md) fixes exact public
  condition mappings, reviewed limitation/recovery records, closed presentation
  actions, source/topic correlation, and confidentiality denials without
  granting Guidance feature or execution authority.
- [`provenance/v1/`](provenance/v1/README.md) fixes closed owner envelopes,
  exact learning roots, bounded deterministic lineage, explicit incomplete
  links, Unicode canonicalization, and safe denial behavior without copying
  owner payloads or granting permission.
- [`provenance/v2/`](provenance/v2/README.md) fixes nine closed cross-domain
  owner-reference profiles, exact identity variants, origin labels, source
  relations, canonicalization, v1 fingerprints, and safe denials without
  claiming that synthetic future-owner fixtures are implemented product data.
