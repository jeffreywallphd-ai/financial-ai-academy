# Provenance Envelope and Bounded Lineage v1

These Draft 2020-12 schemas define the additive provider-neutral provenance
envelope, the two initial exact learning-lineage selectors, and the bounded
lineage view. Content and Assessment remain authoritative for their business
records. Audit may validate, correlate, and expose integrity references; it
does not copy owner payloads or grant access to a referenced record.

Canonicalization uses UTF-8 JSON with sorted object keys, compact separators,
unescaped Unicode, UTC `Z` timestamps, and the deterministic node, edge,
source, and incomplete-link ordering enforced by the Audit pure domain. The
`view_digest` is lowercase SHA-256 over the complete canonical view without its
own digest field.

Educational sources, published lessons, and assessment definitions use only a
`resource_version`. Knowledge-check events, completion evidence, and Audit
references use only an `occurrence`. Recorded times use an RFC 3339 offset and
at most six fractional digits; higher precision is rejected instead of silently
truncated. The schema rejects known unsafe control/format characters, while the
pure domain performs the authoritative Unicode alphanumeric-first and character
category validation.

Every envelope source in a lineage view is accounted for exactly once. A
`validated` source has one exact edge and an `incomplete` source has one
matching incomplete link. Incomplete links therefore describe declared source
references; they cannot create an undeclared relationship.

V1 admits only exact `published_lesson` and server-scoped
`knowledge_check_completion` roots. It contains no lesson body, answer,
feedback, learner identity, provider payload, secret, storage locator, arbitrary
URL/path, active content, permission, legal conclusion, or financial meaning.
Later root kinds require additive contract evolution and their owning CAP slice.
