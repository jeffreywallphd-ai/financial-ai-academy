# Personal Workspace v1

This family freezes portable records for a learner's private notes, bookmarks,
collections, and exact learning references.

The three Draft 2020-12 schemas cover:

- `learning-reference.schema.json`: closed Curriculum-owned learning targets;
- `workspace.schema.json`: one bounded revisioned workspace projection;
- `mutation-intent.schema.json`: closed, revision-bound mutation requests.

References retain exact package, placement, publication, validation, and source
provenance. They do not copy target state, grant access, or allow this module to
mutate Curriculum or Content. Workspace records contain no provider payload,
storage location, access token, learner response, grade, mastery claim,
recommendation, or personalized financial advice.

Canonical workspace digests are SHA-256 over compact, sorted-key UTF-8 JSON
after removing `workspace_digest`. The pure Personal workspace adapter applies
the same rules for browser and headless callers. Persistence, identity binding,
HTTP, generated clients, and browser behavior are introduced by later packets.
