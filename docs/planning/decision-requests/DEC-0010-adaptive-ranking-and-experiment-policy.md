---
id: DEC-0010
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0014-governed-adaptive-learning-research-plane.md
---

# Decision Request: Choose Adaptive Inference, Assessment, Ranking, and Experiment Policy

## Decision Needed

Choose the AI/ML and statistical techniques used to infer evolving competency,
select informative assessments, rank eligible learning actions, and evaluate or
experiment with adaptive policies. Define consent, authority, fallback,
promotion, stopping, and rollback boundaries. DEC-0009 separately governs how
resulting estimates and recommendations may be presented to learners.

## Why Now

CAP-0009 needs a defensible learner-state estimate, while CAP-0010 needs both
deterministic eligibility and an adaptive ranking strategy. These policies
affect learner opportunity, evidence validity, and data use. An implicit
engagement optimizer or single uncalibrated model would violate the accepted
adaptive boundary and would not constitute state-of-the-art adaptive learning.

## Current Authority and Constraints

Prerequisites, permissions, exclusions, accessibility constraints, and course
requirements, content validity, and learner choice are deterministic gates.
Model output is advisory. Evaluation measures learning, retention, transfer,
burden, calibration, and harm or exclusion rather than engagement alone. A rule
baseline and deterministic fallback remain available.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Rule-based ranking without online experiments | Deterministic, explainable, low data risk, and easy to audit; establishes a stable baseline. | Less personalization and slower empirical improvement. | Recommendation policy/record, explanation UI, offline evaluation, fallback. | High; later strategies can be versioned against the baseline. |
| B. Governed probabilistic inference and offline/shadow ranking | Add interpretable Bayesian or psychometric learner-state estimates, information-based assessment selection, and model ranking evaluated offline and in shadow mode, but prohibit online exploratory assignment. | Improves inference and validation while containing learner risk, but cannot efficiently estimate every policy's causal effect and may inherit logged-policy bias. | Learner-state estimator, item/rubric models, candidate and propensity logs, model registry, calibration and shadow evaluation, DEC-0009 estimate contract. | High; no learner is assigned by an experimental policy. |
| C. Governed adaptive-learning research plane | Use interchangeable, versioned learner-state estimators and adaptive policies behind stable contracts: interpretable temporal Bayesian/psychometric champions; neural, graph, uncertainty-aware, and semantic challengers; active assessment; conservative contextual ranking; and separately governed, consented, bounded online experiments after offline and shadow qualification. | Highest research value and adaptability, but also the greatest consent, privacy, support, calibration, causal-inference, fairness, monitoring, operational, and statistical-complexity burden. Long-horizon reinforcement learning is especially vulnerable to sparse support and delayed-reward errors. | All Option B contracts plus experiment assignment, consent/opt-out, policy support and propensity data, online monitoring, stopping and rollback controls, promotion gates, and reproducible research datasets. | Medium-high if rollout is phased, deterministic fallback remains live, and policies are independently versioned; experiment and consent records remain durable. |

## Recommendation

Option C as the target architecture, introduced in controlled phases:

1. Ship the Option A rule baseline, event provenance, and deterministic fallback.
2. Add Option B's calibrated interpretable estimators, offline replay, leakage-
   resistant evaluation, and shadow challengers.
3. Permit a model to influence learners only after qualification for its stated
   population and prediction horizon.
4. Permit online exploration only under a separately reviewed experiment with
   explicit consent and opt-out, bounded exposure, support checks, monitoring,
   preregistered learning outcomes, stopping rules, and immediate rollback.

State of the art here means a governed champion-challenger portfolio and a
high-quality evaluation regime, not choosing the newest neural architecture by
default. An interpretable technique remains champion until a challenger shows
meaningful, calibrated, reproducible gains on learning-relevant outcomes.

## Initial Technique Portfolio

### Learner-State Estimation

- Use time-aware or hierarchical Bayesian Knowledge Tracing, logistic knowledge
  tracing, Bayesian item-response theory or multidimensional IRT, cognitive
  diagnosis, and Bayesian state-space learning/forgetting models as initial
  champions according to the evidence shape.
- Evaluate attention-based knowledge tracing, including AKT-style contextual
  attention; learning/forgetting-aware models such as LefoKT; and graph
  knowledge tracing as challengers. A graph model may consume only a reviewed,
  versioned competency/prerequisite graph.
- Preserve posterior uncertainty and support selective prediction or abstention.
- Treat semantic embeddings or LLM-derived item/competency features as
  experimental cold-start inputs only, with validation, provenance, and drift
  checks.

### Adaptive Assessment and Learning-Action Ranking

- First filter a valid item or action pool through deterministic competency
  coverage, accessibility, security, exposure, burden, content, and learner-
  choice constraints.
- Select assessments by expected information gain, posterior entropy reduction,
  or Fisher information. Stop when uncertainty and coverage targets are met;
  abstain when the burden limit is reached without sufficient evidence.
- Begin model ranking with a conservative contextual bandit restricted to
  eligible actions. Optimize delayed learning gain, retention, transfer,
  opportunity, and burden—not clicks, dwell time, or acceptance.
- Keep long-horizon reinforcement-learning or POMDP policies in offline or
  shadow research until logged support, delayed rewards, and safety evaluation
  are adequate. Learners can choose an eligible alternative.

## Estimate Contract for DEC-0009

Every estimate identifies the competency and competency-map version; evidence
cutoff and prediction horizon; posterior or calibrated probability and interval;
coverage and diversity; abstention, out-of-distribution, and drift indicators;
source evidence, item, rubric, dataset, feature, model, calibration, and
selection-policy versions; applicable-population limits; reproducible
explanation factors; and assignment propensity where applicable.

DEC-0009 decides whether and how this may become a learner-facing label or
recommendation explanation. DEC-0010 never directly publishes a mastery,
credential, readiness, professional-competence, or financial-suitability claim.

## Qualification and Evaluation

- Use learner-disjoint chronological splits and report cold-start performance
  for unseen learners, items, competencies, cohorts, and domains where relevant.
- Prevent future or same-event leakage when one observation informs multiple
  competencies.
- Evaluate log loss or negative log likelihood, Brier score, calibration and
  subgroup calibration, selective risk/coverage, and false-positive
  `demonstrated` risk. Treat AUC as secondary.
- Validate against delayed retention, novel transfer, external assessments, and
  reviewed project evidence—not only next-response prediction.
- Log eligible candidates, chosen action, policy version, and propensity. For
  offline policy evaluation, report support diagnostics and use inverse-
  propensity and doubly robust estimates with uncertainty or confidence
  sequences; abstain when support is inadequate.
- Online research requires explicit consent and opt-out, randomization only
  among eligible actions, preregistered learning/retention/burden/harm metrics,
  power and stopping rules, bounded exploration, subgroup monitoring, and
  rollback. It cannot affect grades, credentials, access, financial decisions,
  or other protected outcomes.

## Research Basis

The portfolio is grounded in [Evidence-Centered Design](https://www.ets.org/content/ets-org/research/policy_research_reports/publications/chapter/2016/jwau.html),
the [AKT contextual-attention model](https://www.kdd.org/kdd2020/accepted-papers/view/context-aware-attentive-knowledge-tracing.html),
the broad [pyKT benchmark](https://papers.neurips.cc/paper_files/paper/2022/hash/75ca2b23d9794f02a92449af65a57556-Abstract-Datasets_and_Benchmarks.html),
the leakage- and regime-focused [KTbench](https://arxiv.org/abs/2403.15304),
and the learning/forgetting-aware [LefoKT model](https://ojs.aaai.org/index.php/AAAI/article/view/34998).
The active-assessment direction is supported by
[BOBCAT](https://www.ijcai.org/proceedings/2021/0332.pdf) and
[BanditCAT/AutoIRT](https://proceedings.mlr.press/v264/sharpnack25a.html).
The experiment policy uses doubly robust and sequentially valid off-policy
evaluation ideas described by
[Jiang and Li](https://proceedings.mlr.press/v48/jiang16.html) and
[off-policy confidence sequences](https://proceedings.mlr.press/v139/karampatziakis21a.html).

## Evidence Required

- A versioned evidence schema, competency map, item/rubric models, prediction
  horizons, and representative research data with lawful usage terms.
- Rule, psychometric/Bayesian, and challenger baselines evaluated under the
  qualification protocol, with reproducibility and ablation results.
- Model records stating intended population, unsupported uses, calibration,
  subgroup results, drift thresholds, cost, and rollback.
- Privacy, consent, experiment-threat, accessibility, bias/harm, retention, and
  operational-failure reviews.
- Deterministic fallback, replay, shadow, monitoring, stopping, and rollback
  tests before online assignment.

## Required Authority

Product learning authority with assessment, learner-model, adaptation, AI/ML,
privacy, security, accessibility, education-risk, and research-ethics review.

## Decision Record and Promotion

[ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
establishes Option C's governed portfolio and phased authority boundary. It does
not approve a particular dataset, provider, online experiment, or production
model.

## Dependent Planning Updates

Reconcile DEC-0009, CAP-0009, CAP-0010, and later model-provider, data-license,
or learner-consent planning.

## Planning History

- 2026-10-15: Captured while shaping CAP-0010.
- 2026-10-15: Refined through adaptive-learning research; expanded from recommendation ranking to the governed inference, active-assessment, ranking, and experiment technique portfolio consumed by DEC-0009.
- 2026-10-15: ADR-0014 established the phased champion-challenger inference, active-assessment, ranking, qualification, and experiment-control architecture.

