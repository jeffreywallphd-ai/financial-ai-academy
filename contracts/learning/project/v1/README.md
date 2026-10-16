# Project Workspace Contract v1

This additive contract family separates immutable learning source meaning from
one learner-owned Project shell. Content owns the approved learning-project
brief. Project owns the create intent, accepted origin, Project identity,
charter, lifecycle, revision, bounded mutable workspace, inert-artifact
manifest, typed domain references, and immutable snapshots.

`brief.schema.json` fixes one immutable brief with stable identity and version,
plain-language title and purpose, one through twenty ordered milestones, and
one through twenty approved source references. `brief_digest` is lowercase
SHA-256 over compact, sorted-key UTF-8 JSON for the nested `brief` object with
`ensure_ascii=false`. No implicit Unicode normalization occurs.

`create-intent.schema.json` accepts an idempotency key, a title of 1 through
120 characters, a charter of 1 through 4000 characters, and exactly one closed
origin:

- `independent` contains only its discriminator and makes no lesson, progress,
  completion, or Portfolio claim.
- `learning` retains the exact package, brief, Curriculum, and placement IDs,
  semantic versions, and digests, plus the approved brief's safe title and
  purpose. The application must resolve these references through public
  Content and Curriculum operations before creation.

`shell.schema.json` adds server-owned Project and learner identity, the
`active` lifecycle, a positive revision, and canonical UTC timestamps. It is a
learner-safe public representation. The family carries no storage path,
credential, provider payload, executable control, artifact content,
Assessment result, mastery claim, recommendation, market observation,
Portfolio state, or personalized financial advice.

The schemas and compatibility runner are transport-neutral. Browser,
command-line, service, and future headless AI clients can use the same future
public API; this family grants no client authority over identity,
authorization, time, revision, persistence, or durable state changes.

`workspace.schema.json` closes one learner-owned live workspace at a positive
revision. It bounds notes, HTTPS reference metadata, inert artifact manifests,
and validated typed domain-resource references. Artifact paths are NFC-
normalized logical, relative names with canonical cross-platform segments;
case-folded aliases, traversal, reserved device names, and host paths fail
closed. Each artifact has a
closed kind, media type, inspection mode, byte count, lowercase SHA-256 digest,
source history, assumptions, and optional environment declaration. Results
must say whether they are observed, calculated, simulated, predicted,
generated, or narrative. Plain-text inspection is permitted only for `text/*`;
all other content is metadata-only in this contract.

`workspace-mutation-intent.schema.json` binds one add or replace operation to
an idempotency key and expected live revision. The client never supplies
learner identity, accepted record IDs, versions, times, storage locations, or
owner-validation results. Artifact bytes travel through a later bounded API;
the intent declares the exact byte count and digest that must be correlated.

`snapshot-close-intent.schema.json` binds closure to exact Project and
workspace revisions. `snapshot.schema.json` records server-owned snapshot
identity and time plus canonical material containing the exact Project shell
digest, live revision, and immutable note, reference, artifact, and link
version references. `snapshot_digest` is lowercase SHA-256 over that nested
`snapshot` object serialized as compact sorted-key JSON with direct UTF-8.
Later live changes cannot alter it.

`evidence-export.schema.json` is a deterministic manifest, not an execution or
restore package. It embeds the exact validated snapshot and workspace records,
binds every note, reference, artifact, and domain link to the snapshot digest
references in the same ordered sequence, and requires every snapshot artifact to be included or excluded
with a bounded reason. Included files repeat the exact logical path, media type,
byte count, content digest, and artifact-manifest digest. `export_digest` uses
the same canonical rule over the entire nested `export` object. HTTPS references
and provenance URLs reject embedded user credentials. The shape cannot carry
authorization state, object-store keys, host paths, callbacks, runtime controls,
or copied private domain-resource state.

The export schema carries closed embedded definitions for both records; a JSON
Schema validator can reject incomplete or expanded embedded shapes without
application-only knowledge.

No schema authorizes a kernel, interpreter, subprocess, package installation,
network, secret, active renderer, archive expansion, provider job, Portfolio
calculation, Assessment submission, completion evidence, or mastery effect.
Typed links record public references only and require a later owning-module
gateway to produce the accepted `available` record.

Run the compatibility evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/project_workspace backend/tests/unit/project/test_project_contract.py
```
