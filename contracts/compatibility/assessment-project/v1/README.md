# Assessment Project Submission v1 Compatibility Corpus

This corpus fixes the first accepted transport-neutral Project learning-
submission family without authorizing persistence or an API.

The `approved/` records cover the closed snapshot candidate, learner intent,
deterministic accepted result, immutable evidence, safe completion event, and
ordered history. The candidate deliberately includes all four admitted
resource kinds and non-ASCII safe text. The evidence and event are examples of
later server metadata projection, not client-supplied authority.

The `vectors/` records prove that JSON object order and permitted mapping or
resource order do not change the request fingerprint. Changed source or
resource meaning must produce a different fingerprint.

The `cases/` records cover missing, repeated, unknown, stale, and cross-record
meaning plus prohibited private, executable, active, scoring, mastery, path,
byte, and callback expansions. Failures expose only bounded stable codes and
safe references.

Run from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_project backend/tests/unit/assessment/test_project_submission_contract.py
```
