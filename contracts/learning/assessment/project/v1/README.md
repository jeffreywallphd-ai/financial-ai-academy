# Assessment Project Submission Contract v1

This additive family freezes deterministic evidence submission for one exact,
immutable snapshot of a learning-started Project. It does not create a runtime
operation, persist evidence, or grant a client authority over learner identity,
authorization, time, occurrence, completion, or supersession.

`snapshot-candidate.schema.json` is a closed, learner-safe view assembled from
public Project, Content, and Curriculum facts. It binds the exact Project and
snapshot digests, learning origin, ordered approved milestones, closure-policy
version, and the complete set of immutable snapshot resource references.
Resources can be versioned notes, safe sources, inert artifact manifests, or
validated domain-resource links. Artifact bytes, storage locations, mutable
workspace state, private owner payloads, and execution controls are excluded.

`submission.schema.json` maps every exact milestone to one or more references
already present in that snapshot. Pure policy rejects missing, repeated, or
unknown milestones and repeated, unknown, or stale resource references. This
is structural completion evidence only: it does not assess quality, truth,
code safety, independent reproducibility, mastery, competency, suitability,
financial performance, or advice.

`validation-result.schema.json` exposes bounded, learner-actionable issues. An
accepted result carries a SHA-256 request fingerprint over compact sorted-key
UTF-8 JSON with `ensure_ascii=false`. Before hashing, milestone mappings are
ordered by the approved brief and resource references by their complete
canonical JSON value. JSON object order and permitted mapping/resource order
therefore do not alter identity; any changed source or evidence meaning does.

`evidence.schema.json` adds server-owned learner, evidence, sequence,
occurrence, and canonical UTC facts to an accepted result. Later occurrences
can point forward from a new immutable record to a prior submission; they never
rewrite or delete prior evidence. `completion-event.schema.json` is the
learner-safe public signal `assessment.project.completed@1.0.0` and omits
learner identity and artifact-level mappings. `history.schema.json` retains an
ordered safe summary of every accepted occurrence.

All schemas are closed and versioned. No field requests execution, active
rendering, package installation, networking, provider work, Portfolio
calculation, market-data use, AI grading, or a durable external action.
