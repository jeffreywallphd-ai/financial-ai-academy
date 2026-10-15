---
id: DEC-0009
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["DEC-0010"]
decision_gates: []
decision_record: ../../adr/ADR-0014-governed-adaptive-learning-research-plane.md
---

# Decision Request: Choose Learner-Facing Competency and Adaptive Guidance Policy

## Decision Needed

Choose how versioned adaptive-learning estimates may become learner-facing
competency labels, evidence explanations, uncertainty and freshness language,
review guidance, and recommendation explanations. DEC-0010 governs the
underlying inference, assessment, ranking, and experiment techniques.

## Why Now

CAP-0009 and CAP-0010 require more than raw completion history. Without an
accepted policy, a score or UI label could silently become an unsupported claim
about mastery, ability, readiness, or the appropriateness of a financial action.

## Current Authority and Constraints

Learner model owns derived state; Assessment owns source evidence; completion is
not mastery; deterministic policy is authoritative; credentials and professional
or investment competence claims are excluded. Model output cannot independently
create a grade, credential, prerequisite, authorization, or durable protected-
state change.

## Boundary With DEC-0010

DEC-0010 must provide a versioned estimate contract containing the competency
and competency-map version; evidence cutoff and prediction horizon; calibrated
probability or posterior and uncertainty interval; evidence coverage;
abstention, out-of-distribution, and drift indicators; model, calibration,
dataset, feature, and selection-policy versions; exact source-evidence, item,
and rubric references; applicable-population limits; and reproducible
explanation factors.

DEC-0009 adds the learner-facing claim, plain-language explanation, evidence and
contradiction links, freshness or review status, and publication-policy version.
A missing, stale, poorly calibrated, out-of-distribution, or insufficiently
supported estimate must be publishable as an abstention rather than forced into
a positive label.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Evidence-threshold competency levels | Use reviewed per-competency evidence rules with `insufficient`, `developing`, and `demonstrated` states, explicit uncertainty, decay/review policy, and no global mastery score. | Requires policy authoring and calibration; may initially cover few competencies. | Learner-state projection, evidence mappings, progress UI, portable records, adaptation inputs. | High; policies are versioned and old projections remain reproducible. |
| B. Evidence-only progress with no competency state | Show source evidence and completion summaries only until later empirical work justifies a projection. | Safest but does not fully deliver competency projection or adaptive evidence goals. | Progress UI and export; adaptation remains limited to completion/prerequisites. | Very high; later policy can be added without migrating a prior claim. |
| C. Governed probabilistic competency projection | Consume DEC-0010's calibrated estimate, then apply a reviewed deterministic publication policy to emit `insufficient`, `developing`, or `demonstrated`, a separate `review_due` condition, uncertainty and coverage explanations, and bounded next-step recommendations. Publication considers posterior lower bounds, evidence diversity and recency, delayed retention, transfer evidence, contradictions, abstention, and out-of-distribution status. | Most faithful to adaptive learning and uncertainty, but requires calibration evidence, careful claims language, population monitoring, explanation design, and more operational governance. | All Option A contracts plus estimator/calibration provenance, confidence and abstention displays, correction and replay, review scheduling, and recommendation-explanation contracts. | High if estimate and publication policies are independently versioned and source evidence remains replayable. |

## Recommendation

Option C, introduced with Option A as its deterministic publication layer and
Option B as the mandatory fallback whenever evidence, calibration, freshness,
or applicability is inadequate.

This exposes useful adaptive guidance without presenting a raw model score as
truth. It also tells the learner what evidence supports a label, how certain and
current it is, and what eligible action may improve or test the estimate.
Recommendations explain a learning objective and evidence gap; they must not
imply investment suitability or financial advice.

## Evidence Interpretation Policy

- Use evidence-centered design: define the competency claim, supporting task
  evidence, and measurement model before collecting signals.
- Maintain reviewed item/rubric-to-competency mappings and a canonical
  prerequisite graph. Project work contributes rubric-dimension evidence, not
  an undifferentiated project score.
- Distinguish unassisted performance, transfer to a new context, and delayed
  retention. Model learning and forgetting over time.
- Treat hints, attempts, scaffolding, response time, and accommodations as
  context, not naive penalties that disadvantage accessible workflows.
- Do not treat completion, dwell time, clicks, engagement, or recommendation
  acceptance as competency evidence without a separately validated mapping.
- Treat an AI-produced score as a provenance-rich proposed observation. It may
  not establish competency by itself.
- Append corrections as superseding evidence and deterministically replay the
  projection while retaining old evidence and policy versions.

## Evidence Required

- Representative competency/evidence mappings, rubric dimensions, prediction
  horizons, and reviewed claims language.
- Calibration, false-positive `demonstrated`, selective-risk/coverage, delayed
  retention, transfer, accessibility, and subgroup analyses.
- Versioning, correction, forgetting/review, contradiction, abstention, and
  explanation prototypes tested with learners.
- Evidence that labels and uncertainty are understood and do not create a
  credential, professional-competence, or financial-suitability claim.
- A deterministic evidence-only fallback and replay test suite.

## Research Basis

The policy follows [Evidence-Centered Design](https://www.ets.org/content/ets-org/research/policy_research_reports/publications/chapter/2016/jwau.html)
and modern knowledge-tracing evidence that predictive accuracy alone is
insufficient. Comparisons should account for data regime, leakage, calibration,
and the meaning of the evidence being modeled, as emphasized by the
[pyKT benchmark](https://papers.neurips.cc/paper_files/paper/2022/hash/75ca2b23d9794f02a92449af65a57556-Abstract-Datasets_and_Benchmarks.html)
and [KTbench](https://arxiv.org/abs/2403.15304).

## Required Authority

Product/domain learning authority with assessment, learner-model, AI/ML,
education-risk, privacy, and accessibility review.

## Decision Record and Promotion

[ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
establishes Option C with the deterministic Option A publication layer and the
Option B evidence-only fallback. It does not approve a concrete model, dataset,
provider, online experiment, or learner-facing implementation.

## Dependent Planning Updates

Reconcile CAP-0009 and CAP-0010 acceptance, contracts, slice boundaries, UI
language, and evaluation evidence with DEC-0010 and the selected policy.

## Planning History

- 2026-10-15: Captured while shaping catalog candidates 6 and 7.
- 2026-10-15: Refined through adaptive-learning research; separated learner-facing publication policy from the inference and experimentation techniques governed by DEC-0010.
- 2026-10-15: ADR-0014 established governed probabilistic competency publication with deterministic labels and evidence-only abstention fallback.

