# Personal Workspace v1 Compatibility Corpus

This corpus fixes one empty workspace, one populated workspace, one valid
Curriculum note intent, three valid Project-reference intents, portable stale
and unavailable references, one deterministic query/result pair, and
representative semantic and privacy denials. The Project cases cover a mutable
workspace reference, an immutable snapshot reference, and an inert artifact-
manifest reference. Query and refresh denials prove that learner identity,
status, selector, and replacement facts are not caller-controlled. The fixtures
are synthetic and contain no account, provider, artifact content, or personal
data.

Run the direct evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace/test_workspace_contract.py
```

The corpus qualifies the portable contract, pure mutation/query/refresh core,
and focused public-operation Project adapter. It is not evidence for refresh
orchestration, persistence, API/client composition, browser behavior,
synchronization, or recovery.
