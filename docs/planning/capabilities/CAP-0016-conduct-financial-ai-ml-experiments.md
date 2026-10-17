---
id: CAP-0016
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0007", "CAP-0011", "CAP-0012"]
decision_gates: ["DEC-0011", "DEC-0014"]
approval_model: cap-package-v1
slice_ids: ["SLI-0066", "SLI-0067", "SLI-0068", "SLI-0069"]
---

# Capability: Conduct Financial AI and ML Experiments

## Outcome

An individual learner can define, conduct, compare, and document a reproducible
financial AI/ML experiment with versioned data, features, models, evaluation,
leakage and overfitting checks, model cards, and limitations under an explicitly
accepted execution boundary.

## Users and Value

Learners need to practice empirical modeling without treating a model as a
financial oracle or allowing opaque execution to become platform authority.
Value is observable when every result traces to exact data, code/method,
environment, parameters, evaluation, and declared execution provenance.

## Scope

### In Scope

- Project-owned experiment workspaces and immutable snapshots referencing
  permitted canonical datasets, inert artifacts, feature definitions, run
  manifests, results, model cards, and reflections.
- The execution and import posture selected by DEC-0014, plus provider/data-use
  controls selected by DEC-0011.
- Deterministic split, leakage, baseline, metric, reproducibility, comparison,
  promotion-not-claimed, and limitation checks.
- Accessible setup, evidence, comparison, failure, and export experiences.

### Out of Scope

- Autonomous trading, advice, guaranteed predictive value, model authority over
  finance or learning state, or unapproved secret/network access.
- Silent provider execution or treating imported results as trusted without
  validation and provenance.
- Production model promotion or serving without a separately approved use case.

## Canonical Context

- [AI/ML Governance](../../ai-ml/README.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [Inert Applied-Project Artifacts](../../adr/ADR-0011-inert-applied-project-artifacts.md)
- [Reusable Project Workspace](../../adr/ADR-0012-reusable-project-workspace.md)
- [Learner-Managed Experiment Execution](../../adr/ADR-0016-learner-managed-experiment-execution.md)
- [Experiment Execution Boundary](../../architecture/ai-ml/experiment-execution-boundary.md)
- [CAP-0007](CAP-0007-complete-applied-projects.md)
- [CAP-0012](CAP-0012-explore-canonical-market-data.md)

## Decision Gates and Constraints

- ADR-0016 fixes learner-managed external execution with validated import and
  provider-neutral run/result semantics. Its future analytics execution seam is
  optional and grants no current sandbox or provider runtime authority.
- ADR-0013 governs provider capability, data use, cost, retention, safety, and
  local-model support for any admitted model service.
- Project and experiment artifacts remain inert; deterministic validation,
  evaluation, provenance, and claims policy remain authoritative.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0066 | A learner creates a versioned experiment plan with dataset, target, split, feature, baseline, metric, leakage, environment, and limitation declarations. | First after dependencies and decisions; establishes experiment and snapshot contracts. | Unbounded execution, advice objectives, or missing data permission changes the CAP package. | captured |
| SLI-0067 | The learner exports an integrity-bound run bundle, executes it in an environment they control, and imports validated, provenance-bound results without model authority over protected state. | After SLI-0066. | Platform/provider execution, secret/network expansion, autonomous action, or unverifiable results changes the CAP package. | captured |
| SLI-0068 | The learner compares baselines and models, inspects leakage/overfitting and uncertainty, and publishes a bounded model card and project snapshot. | After SLI-0067. | Production promotion, suitability claims, or result cherry-picking without retained evidence changes the CAP package. | captured |
| SLI-0069 | The learner-managed experiment flow is qualified for dataset permission, reproducibility declarations, leakage, non-execution, failure, provenance, export/import, accessibility, and local/cloud honesty. | Last; depends on SLI-0066 through SLI-0068. | Production serving or any platform/provider execution runtime without a new durable decision changes the CAP package. | captured |

## Capability Acceptance

- Every run or imported result binds exact dataset, split, feature, method/model,
  environment, parameter, metric, code/snapshot, and execution provenance.
- Leakage, invalid splits, unsupported metrics, missing permissions, malformed
  artifacts, and partial runs fail explicitly.
- Comparisons include baselines, uncertainty, limitations, and retained adverse
  results; no output is presented as advice or guaranteed performance.
- Security, evaluation, reproducibility, accessibility, and export evidence
  matches the selected execution boundary.

- Every slice includes focused failure and anti-rigidity tests so optional
  models, datasets, and execution adapters do not block the reproducible
  manifest-and-import baseline.

## Risks and Non-Goals

Experiment environments combine untrusted code, licensed data, secrets, cost,
and misleading predictive claims. This CAP does not silently introduce a
runtime, promote models to production, or authorize financial action.

## Documentation Impact

Delivery will add experiment, dataset, feature, run, evaluation, model-card,
execution, security, cost, export, UI, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 13 with manifest SLI-0066 through
  SLI-0069. DEC-0011 and DEC-0014 block CAP approval and delivery.
- 2026-10-15: DEC-0014 was promoted to ADR-0016, selecting learner-managed
  execution with validated import and a non-authorizing future sandbox seam;
  the CAP returned to shaping for package refinement.
- 2026-10-16: Reconciled the complete four-slice package with ADR-0013,
  ADR-0016, and the provider-neutral market-data authority inherited through
  CAP-0012. Learner-managed execution remains the only admitted runtime; the
  manifest is unchanged.

