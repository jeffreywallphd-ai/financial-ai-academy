# Accountable History v1

These Draft 2020-12 schemas define a purpose-limited read model over one
already authorized `provenance/v1` learning-lineage root. The contract helps a
learner understand **Source and history** and supports one ephemeral portable
evidence export. It is not a second history store and grants no access to an
owned record.

The request contains only the closed lesson or knowledge-check completion root.
The server binds learner identity, authorization, and operation purpose. An
inspection document uses `learner_review`; an export document uses
`portable_evidence`. Callers cannot supply another purpose, learner, tenant,
role, policy, field list, or redaction rule.

The disclosed document contains reviewed plain-English titles and explanations
plus bounded exact technical facts. Safe diagnostic codes describe incomplete
or invalid evidence without claiming malicious activity, compliance failure,
or tamper-proof storage. Redaction summaries contain only closed categories and
counts. They never echo protected values.

Canonical bytes use compact sorted-key UTF-8 JSON, unescaped Unicode, UTC `Z`
timestamps, and semantic array order. `history_digest` is lowercase SHA-256
over the disclosed document without that field. A portable export wraps the
same document, uses the document digest, and derives `exported_at` from the
latest disclosed source time. It contains no file path or retained download
identity.

The family contains no lesson body, answer, score detail, feedback, learner or
actor identity, provider payload, secret, internal error, storage coordinate,
arbitrary URL, active content, legal conclusion, financial advice, or
compliance claim. Meaning changes require an additive contract version.
