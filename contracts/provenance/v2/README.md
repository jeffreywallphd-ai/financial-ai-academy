# Cross-Domain Owner References v2

This additive Draft 2020-12 contract family defines closed, provider-neutral
provenance references for Project snapshots and future financial observations,
financial results, dataset snapshots, model versions and executions, simulation
results, recommendation records, and local administrative actions.

The family does not replace or reinterpret `provenance/v1`. Version 1 remains
the complete contract for the existing published-lesson and knowledge-check
lineage operations. Version 2 currently defines owner-issued references only;
it does not define a public lineage request or view.

`profile-catalog.json` is the executable closed catalog. Every envelope resource
and source reference uses exactly one catalog profile, owner, resource kind,
origin label, relation set, and identity variant. Financial results use an
explicit account-or-analysis discriminator. Market-observation resource IDs are
the canonical SHA-256 digest of the exact documented identity tuple, so no
independent observation ID can alter duplicate semantics. Unknown profiles and keys fail
closed. The catalog describes contract meaning, not implementation maturity:
only the Project profile has an implemented owner suitable for the real adapter
proof in this slice. Other approved compatibility records are synthetic.

Canonicalization uses compact sorted-key UTF-8 JSON with unescaped Unicode,
aware timestamps projected to UTC `Z`, and sources sorted by relation plus their
canonical reference. The compatibility vectors bind the resulting bytes and
digests. The conformance CLI also requires the approved corpus to cover the
closed profile catalog exactly. Identifiers, versions, times, digests, strings, producers, and source
counts are bounded. Exact identity reuse with changed provenance meaning is a
conflict.

The contract carries references, not business payloads. It contains no learner,
tenant, organization, administrator, provider, account-holder, or actor identity;
no market values, portfolio state, dataset rows, model input/output, prompt,
recommendation prose, Project content, permission, storage locator, credential,
active instruction, execution authority, financial advice, compliance claim, or
guarantee. Origin labels describe how evidence arose; they do not establish
truth, quality, mastery, suitability, permission, or authority.
