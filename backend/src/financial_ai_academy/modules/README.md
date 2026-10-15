# Backend Modules

The proposed starting module map includes identity, content, curriculum, assessment, learner model, adaptation, market data, portfolio, AI orchestration, and audit.

Do not create a module merely because it appears in the proposed map. Validate its vocabulary, ownership, public application surface, and dependencies through a real vertical slice first.

Content, Curriculum, Identity, and the initial deterministic Assessment core
now have module-first public/application/domain/port/adapter seams. Assessment
depends synchronously only on the Content and Curriculum public facades and
owns its persistence and completion-event meaning.

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
