# Backend Modules

The proposed starting module map includes identity, content, curriculum, assessment, learner model, adaptation, market data, portfolio, AI orchestration, and audit.

Do not create a module merely because it appears in the proposed map. Validate its vocabulary, ownership, public application surface, and dependencies through a real vertical slice first.

Content, Curriculum, Identity, the deterministic Assessment core, and the
bounded Learner-model completion projection now have module-first public/
application/domain/port/adapter seams. Assessment depends synchronously only on
the Content and Curriculum public facades and owns its persistence and
completion-event meaning. Learner model consumes only Assessment's public event
query and owns its rebuildable projection schema.

Audit also consumes only the Assessment public event query. It owns an
append-oriented integrity/provenance schema and never becomes a second store of
Assessment or Learner-model business state.

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
