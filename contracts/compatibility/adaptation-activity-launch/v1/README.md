# Adaptation Activity Launch v1 Compatibility

This corpus fixes one exact successful lesson launch and the bounded denial
classes for unknown, locked, unavailable, unsupported, mismatched, tampered,
and unsafe requests. The approved record is derived only from the reviewed
Curriculum graph and Navigation-state v1 fixtures.

The runner validates the closed schema, exact graph and projection identity,
selected eligible lesson reference, and server-owned same-origin destination.
It returns no learner identity, source facts, answers, scores, provider data,
or filesystem paths.

Run from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/adaptation_activity_launch
```

This corpus does not qualify application composition, HTTP authorization,
generated clients, browser navigation, persistence, or assessment execution.
