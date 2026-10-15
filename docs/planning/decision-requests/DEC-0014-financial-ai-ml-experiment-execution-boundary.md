---
id: DEC-0014
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0016-learner-managed-experiment-execution.md
---

# Decision Request: Choose the Financial AI/ML Experiment Execution Boundary

## Decision Needed

Choose whether the initial experiment capability validates learner-managed
external runs or supplies a platform/provider-managed runtime, and define the
network, secret, resource, artifact, provenance, and failure boundary.

## Why Now

CAP-0016 must not turn inert notebooks and code into an execution service by
accident. The two viable boundaries have materially different security, cost,
reproducibility, licensing, and support obligations.

## Current Authority and Constraints

ADR-0011 currently permits inert storage, validation, passive inspection,
download/export/restore, and learner-managed execution. Platform/provider
execution, secret access, and network access require a new accepted decision;
model output cannot own financial or durable state.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Learner-managed execution with validated import | Preserves ADR-0011, minimizes platform attack/cost surface, and still supports reproducible manifests/results. | More learner setup, weaker one-click experience, and imported results need careful validation. | Project experiment/run manifest, environment declaration, result import, provenance, export and guidance. | High; a managed runtime can be added later. |
| B. Bounded managed isolated runtime | Better onboarding and repeatability with centrally captured execution evidence. | Requires sandbox, network/secret policy, image supply chain, quotas, scheduling, abuse handling, cost and incident support. | Execution provider port, jobs, images/environments, artifacts, telemetry, security and operations. | Medium-low; runtime commitments and stored environments persist. |

## Recommendation

Option A for the initial capability. Preserve provider-neutral run manifests and
result validation so Option B can be evaluated later without changing experiment
meaning.

## Evidence Required

- External-run manifest and result-validation prototype.
- Threat model for both options, including malicious artifacts and data exfiltration.
- Reproducibility, dataset-license, environment, support, and cost comparison.
- If Option B remains viable, sandbox escape, quota, job, image, secret/network,
  incident, and cleanup qualification.

## Required Authority

Product/AI-ML authority with security, architecture, data licensing, operations,
cost, and education-risk review.

## Decision Record and Promotion

[ADR-0016](../../adr/ADR-0016-learner-managed-experiment-execution.md)
establishes Option A while preserving provider-neutral run/result contracts and
an optional future analytics execution-port seam. The seam grants no current
sandbox, platform/provider execution, network, secret, job, or callback
authority.

## Dependent Planning Updates

Reconcile CAP-0016 and any provider/job planning that assumes execution.

## Planning History

- 2026-10-15: Captured while shaping CAP-0016; ADR-0011 remains authoritative
  until a superseding decision is promoted.
- 2026-10-15: ADR-0016 established learner-managed execution with validated import and a provider-neutral future analytics/sandbox seam that does not grant execution authority.

