# Python Backend

This directory contains the CPython 3.14 modular monolith and its first approved-lesson API composition. [ADR-0009](../docs/adr/ADR-0009-initial-application-framework-runtime-baseline.md) sets FastAPI 0.141 and Pydantic 2.13 as the API boundary. Uvicorn 0.41 is the exact ASGI server used by the loopback-only qualification host.

Current structure:

```text
src/financial_ai_academy/
|-- modules/             module-first domain/application/ports/adapters
|-- platform/            database, storage, events, jobs, security, observability
|-- hosts/               API, worker, and CLI entry points
|-- bootstrap/           validated adapter selection and composition
`-- generated/           generated contract bindings
tests/
|-- unit/
|-- contract/
|-- integration/
|-- architecture/
`-- fixtures/
```

Do not add framework or provider dependencies to domain code. See `docs/architecture/system/modular-monolith.md` and the module dependency rules before implementation.

Content owns approved package admission and exact published-version reads.
Curriculum owns exact placement and lesson-open behavior. Identity supplies the
single-profile learner context. PostgreSQL repositories and the restrictive
filesystem object adapter remain private to their owning composition.

Assessment now owns exact private-definition parsing, safe knowledge-check
presentation, deterministic single-select scoring, reviewed feedback, and an
atomic PostgreSQL attempt/response/score/completion-evidence/outbox boundary.
Curriculum owns the exact placed-Assessment reference; Content exposes exact
validated private bytes only through its internal public module facade.
Learner model rebuilds bounded completion/history through Assessment's public
event query, while Audit appends canonical integrity/provenance references.
The protected FastAPI completion endpoint reconciles Audit before returning the
Learner-model view and never accepts a client-selected learner.

The protected practice boundary now exposes both answer-safe opening and
whole-attempt submission through the reviewed public API. The submission host
accepts only the closed versioned document, supplies learner identity from the
server session, and delegates scoring, replay, conflict, attempt limits, and
atomic evidence to Assessment. Its learner-safe result omits learner identity,
the internal request fingerprint, answer keys, and evaluator declarations.
OpenAPI and the generated TypeScript client retain the same operation for
browser, command-line, service, and future headless consumers; no separate AI
transport or browser-owned scoring path exists.

## Commands

Use the committed Python 3.14 lock:

```powershell
py -m uv sync --project backend --frozen
backend/.venv/Scripts/python.exe -m pytest backend/tests
```

PostgreSQL-marked tests require an isolated real server through
`FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN`. The live local qualification runner
starts and removes its own PostgreSQL 18.4 container when that variable is not
supplied:

```powershell
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
```

The focused Assessment database suite applies the root, Curriculum-reference,
and Assessment streams to an isolated database:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment
```

The runner requires the reviewed static web build and pinned Playwright
Chromium. It starts only the Python application process, opts into a bounded
three-classification discovery-query corpus, and directly qualifies combined
filters, stable multi-page ordering, cursor-query mismatch denial, context
confidentiality, accessibility, and the exact lesson/completion path. Node
remains build and test tooling.

Exact dependency patches and integrity data are committed in `pyproject.toml`
and `uv.lock`. Changing the accepted Python, FastAPI, Pydantic, or production
server boundary requires explicit compatibility review.
