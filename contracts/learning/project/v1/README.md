# Project Workspace Contract v1

This additive contract family separates immutable learning source meaning from
one learner-owned Project shell. Content owns the approved learning-project
brief. Project owns the create intent, accepted origin, Project identity,
charter, lifecycle, and revision.

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

Run the compatibility evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/project_workspace backend/tests/unit/project/test_project_contract.py
```
