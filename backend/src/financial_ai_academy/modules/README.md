# Backend Modules

The proposed starting module map includes identity, content, curriculum, assessment, learner model, adaptation, market data, portfolio, AI orchestration, and audit.

Do not create a module merely because it appears in the proposed map. Validate its vocabulary, ownership, public application surface, and dependencies through a real vertical slice first.

An implemented module should normally contain:

```text
<module>/
|-- README.md
|-- domain/
|-- application/
|-- ports/
|-- adapters/
`-- tests/
```

