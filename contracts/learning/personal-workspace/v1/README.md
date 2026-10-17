# Personal Workspace v1

This family freezes portable records for a learner's private notes, bookmarks,
collections, and exact learning or Project references.

The three Draft 2020-12 schemas cover:

- `learning-reference.schema.json`: closed Curriculum-owned learning targets
  plus Project-owned workspace, immutable-snapshot, and inert-artifact targets;
- `workspace.schema.json`: one bounded revisioned workspace projection;
- `mutation-intent.schema.json`: closed, revision-bound mutation requests.

Curriculum references retain exact package, placement, publication, validation,
and source provenance. Project references retain only safe shell/workspace
revision, snapshot identity/digest/time, or inert artifact-manifest facts.
They contain no Project charter, origin payload, workspace note/source,
snapshot material, artifact bytes, provenance URL, object key, download handle,
permission, provider payload, or execution control. No reference copies target
authority, grants access, or permits target mutation. Retained artifact logical
paths continue to satisfy Project's canonical confined-path profile; traversal,
ambiguous, reserved, control-character, and non-NFC forms fail closed.

Canonical workspace digests are SHA-256 over compact, sorted-key UTF-8 JSON
after removing `workspace_digest`. The pure Personal workspace adapter applies
the same rules for browser and headless callers. The Project adapter uses only
learner-bound Project public reads; persistence/API/client/browser composition
for the new selector variants remains the next delivery seam.
