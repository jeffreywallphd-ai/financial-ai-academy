# Personal Workspace v1

This family freezes portable records for a learner's private notes, bookmarks,
collections, and exact learning or Project references.

The six Draft 2020-12 schemas cover:

- `learning-reference.schema.json`: closed Curriculum-owned learning targets
  plus Project-owned workspace, immutable-snapshot, and inert-artifact targets;
- `workspace.schema.json`: one bounded revisioned workspace projection;
- `workspace-export.schema.json`: one closed owner-level export envelope bound
  to the complete workspace projection and its canonical digest;
- `mutation-intent.schema.json`: closed, revision-bound mutation requests,
  including a record-ID-only reference refresh intent;
- `workspace-query.schema.json`: bounded safe-text, closed filter, stable-sort,
  page-size, and opaque-continuation query input; and
- `workspace-query-result.schema.json`: workspace-revision and query-digest-
  bound result pages containing only complete workspace-owned records.

Curriculum references retain exact package, placement, publication, validation,
and source provenance. Project references retain only safe shell/workspace
revision, snapshot identity/digest/time, or inert artifact-manifest facts.
They contain no Project charter, origin payload, workspace note/source,
snapshot material, artifact bytes, provenance URL, object key, download handle,
permission, provider payload, or execution control. No reference copies target
authority, grants access, or permits target mutation. Retained artifact logical
paths continue to satisfy Project's canonical confined-path profile; traversal,
ambiguous, reserved, control-character, backslash, over-240-character, and
non-NFC forms fail closed.

Every reference has one of three public status meanings: `available`, `stale`,
or `unavailable`. Historical safe facts remain retained when a source becomes
stale or unavailable. The pure refresh operation accepts an exact trusted owner
result or one confidential unavailable outcome; callers cannot supply status,
owner, selector, replacement facts, learner identity, or validation time.

Record queries normalize bounded Unicode text deterministically, compose only
closed filters, use stable record-ID tie-breaking, and bind continuations to the
workspace revision and canonical query digest. They search learner-authored
text and already-retained safe target labels/identifiers, never source content.

Canonical workspace and query digests are SHA-256 over compact, sorted-key
UTF-8 JSON. The export envelope repeats the embedded workspace's verified
canonical digest and adds only its v1 schema version and server-issued
generation time. It contains no mutation replay, authorization state,
credentials, storage keys, target content, artifact bytes, or provider payload.
The digest detects changed meaning; it is not a signature or permission grant.

The pure adapter reports record, collection, and collection-membership capacity
separately at the accepted maxima of 200, 50, and 100. Record and collection
removal affects only workspace-owned order and membership. Protected export
composition, public error mapping, persistence replay, API/OpenAPI/client,
browser, and live recovery behavior remain later SLI-0073 delivery seams.
