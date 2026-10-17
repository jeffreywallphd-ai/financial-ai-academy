# Personal Workspace v1 Compatibility Corpus

This corpus fixes one empty workspace, one populated workspace, one valid
Curriculum note intent, three valid Project-reference intents, portable stale
and unavailable references, one deterministic query/result pair, one complete
owner export view, and representative semantic and privacy denials. Export
denials cover digest substitution, invalid chronology, credentials, mutation
replay, storage keys, artifact bytes, provider payloads, and unknown fields.
The Project cases cover a mutable
workspace reference, an immutable snapshot reference, and an inert artifact-
manifest reference. Query and refresh denials prove that learner identity,
status, selector, and replacement facts are not caller-controlled. The fixtures
are synthetic and contain no account, provider, artifact content, or personal
data.

Run the direct evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace/test_workspace_contract.py
```

The corpus qualifies the portable contract, owner export view, exact capacity
classification, pure mutation/query/refresh core, removal cleanup, and focused
public-operation Project adapter. It is not evidence for protected export
composition, persistence, API/client export behavior, browser download,
synchronization, or recovery.
