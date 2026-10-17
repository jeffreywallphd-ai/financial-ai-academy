# Personal Workspace v1 Compatibility Corpus

This corpus fixes one empty workspace, one populated workspace, one valid note
intent, and representative semantic and privacy denials. The fixtures are
synthetic and contain no account, provider, or personal data.

Run the direct evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace/test_workspace_contract.py
```

The corpus qualifies only the portable contract and pure mutation core. It is
not evidence for persistence, authorization, API, browser, synchronization, or
recovery behavior.
