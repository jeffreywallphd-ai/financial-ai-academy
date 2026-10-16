# Learning Contracts

Portable learning-activity, competency, assessment, and evidence schemas live here when introduced through approved delivery work.

The semantic package boundary is accepted by [ADR-0007](../../docs/adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [versioned lesson content-package contract](../../docs/architecture/contracts/content-package-contract.md).

## Lesson Package v1

The executable Draft 2020-12 schemas are in [`lesson-package/v1/`](lesson-package/v1/README.md). The compatibility corpus in [`../compatibility/lesson-package/v1/`](../compatibility/lesson-package/v1/README.md) fixes:

- one approved synthetic lesson package;
- safe path, file-closure, integrity, media, markup, and resource-limit denials;
- canonical package-index bytes and the expected SHA-256 package digest;
- immutable package identity/version conflict behavior.

Run the contract evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/lesson_package
```

These contracts establish portable admission behavior only. They do not establish Content persistence, Assessment scoring, API, browser rendering, or local/cloud storage conformance.

## Assessment v1

[`assessment/v1/`](assessment/v1/README.md) defines the private single-select
definition, answer-safe learner presentation, exact-version submission, and
retained result/evidence shapes. The paired corpus in
[`../compatibility/assessment/v1/`](../compatibility/assessment/v1/README.md)
fixes correct and incorrect outcomes, denial behavior, definition/package
digests, and cross-record consistency.

```powershell
uv run --project backend pytest backend/tests/contract/assessment
```

This is direct contract evidence only; application scoring and persistence are
introduced separately.

## Assessment Practice v1

[`assessment/practice/v1/`](assessment/practice/v1/README.md) defines an
additive multi-item formative-practice definition and answer-safe presentation
for single select, multiple select exact set, and canonical fixed-decimal
numeric entry. Its compatibility corpus lives in
[`../compatibility/assessment-practice/v1/`](../compatibility/assessment-practice/v1/README.md).

```powershell
uv run --project backend pytest backend/tests/contract/assessment_practice
```

This family is transport-neutral so a protected API can serve browser and
headless clients through the same Assessment operation. The contract and pure
parser/projector do not yet admit packages, resolve placements, expose HTTP,
score responses, or retain learner evidence.

## Learning Discovery v1

[`discovery/v1/`](discovery/v1/README.md) defines the portable approved
learning-opportunity record and stable browse projection. The compatibility
corpus in [`../compatibility/discovery/v1/`](../compatibility/discovery/v1/README.md)
fixes exact lesson provenance, canonical source/generation digests, stable
ordering, and bounded denial behavior.

```powershell
uv run --project backend pytest backend/tests/contract/discovery
```

## Learning Discovery Query v1

[`discovery/query/v1/`](discovery/query/v1/README.md) defines deterministic
search, metadata filters, closed sorts, bounded pages, and generation-bound
cursors over unchanged discovery-v1 records. Its corpus lives in
[`../compatibility/discovery/query/v1/`](../compatibility/discovery/query/v1/README.md).

```powershell
uv run --project backend pytest backend/tests/contract/discovery_query
```

The current profile qualifies exact approved lesson records only. Persistence,
API authorization, generated clients, browser query behavior, and non-lesson
destinations require their owning implementation evidence. Discovery-query v1
has direct contract and shared-core policy evidence but does not itself qualify
an HTTP or interface consumer.

## Curriculum Graph v1

[`curriculum/v1/`](curriculum/v1/README.md) defines one immutable approved
Curriculum-owned graph with objectives, competencies, exact lesson and
assessment activities, required and optional branches, typed relationships,
partial presentation hints, source references, and a canonical digest. Its
compatibility corpus lives in
[`../compatibility/curriculum-graph/v1/`](../compatibility/curriculum-graph/v1/README.md).

```powershell
uv run --project backend pytest backend/tests/contract/curriculum_graph
```

The graph contract does not establish learner eligibility, completion,
recommendation, persistence, API authorization, or browser behavior.

## Adaptation Navigation State v1

[`adaptation/v1/`](adaptation/v1/README.md) defines the deterministic rule
baseline that composes one exact Curriculum graph and complete typed activity
source facts into orthogonal completion, eligibility, requirement, and
availability state with bounded reasons and replay digests. Its compatibility
corpus lives in
[`../compatibility/adaptation-navigation/v1/`](../compatibility/adaptation-navigation/v1/README.md).

```powershell
uv run --project backend pytest backend/tests/contract/adaptation_navigation
```

The contract and pure policy do not qualify public gateways, authentication,
API/generated clients, browser rendering, persistence, ranking, models, or
experiments.

## Adaptation Activity Launch v1

[`adaptation/v1/activity-launch.schema.json`](adaptation/v1/activity-launch.schema.json)
defines the closed transport-neutral result for resolving one exact eligible
lesson from a matching Curriculum graph and Navigation-state projection. Its
compatibility corpus lives in
[`../compatibility/adaptation-activity-launch/v1/`](../compatibility/adaptation-activity-launch/v1/README.md).

```powershell
uv run --project backend pytest backend/tests/contract/adaptation_activity_launch
```

The contract derives a same-origin lesson destination and carries exact graph,
projection, placement, and package provenance. It does not qualify an API,
permission check, generated client, browser transition, persistence, or
assessment launch.
