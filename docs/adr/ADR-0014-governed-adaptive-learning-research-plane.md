# ADR-0014: Governed Adaptive-Learning Research Plane

- Status: accepted
- Date: 2026-10-15
- Decision requests: [DEC-0010](../planning/decision-requests/DEC-0010-adaptive-ranking-and-experiment-policy.md), [DEC-0009](../planning/decision-requests/DEC-0009-mastery-and-competency-projection-policy.md)

## Context

The learner model must derive useful competency state from heterogeneous,
versioned evidence, and Adaptation must recommend eligible next actions without
turning prediction into authority. A fixed threshold-only system is explainable
but cannot represent uncertainty, forgetting, transfer, or the differing
information value of assessments. A model-only system can overstate noisy
evidence, obscure data limitations, optimize engagement instead of learning,
and expose learners to unsupported experiments.

The architecture therefore needs a research-capable technique portfolio and a
separate learner-facing publication policy. The research plane must support
state-of-the-art comparison while preserving deterministic eligibility,
reviewed evidence meaning, learner choice, provenance, and a usable no-model
baseline.

## Decision

Adopt a governed adaptive-learning research plane with a phased
champion-challenger model portfolio, and publish learner-facing competency and
recommendation guidance only through a separate deterministic policy.

### Evidence and Learner-State Estimation

Assessment remains the owner of scored and reviewed source evidence. Learner
model owns derived competency state. Each competency estimate identifies its
competency-map version, evidence cutoff, prediction horizon, calibrated
probability or posterior distribution and interval, evidence coverage and
diversity, abstention reason, out-of-distribution and drift indicators, source
evidence, and all dataset, feature, model, calibration, and selection-policy
versions needed for replay.

The initial champion family is selected according to the evidence shape from
time-aware or hierarchical Bayesian Knowledge Tracing, logistic knowledge
tracing, Bayesian IRT or multidimensional IRT, cognitive diagnosis, and
Bayesian state-space learning and forgetting models. Attention-based knowledge
tracing, learning/forgetting-aware neural models, graph knowledge tracing,
uncertainty-preserving hybrids, and semantic cold-start features are challengers
until they demonstrate calibrated, reproducible gains for the intended
population and prediction horizon.

Evidence follows an evidence-centered design: a reviewed competency claim maps
to tasks, items, or rubric dimensions and then to a measurement model. Project
work contributes reviewed rubric-dimension evidence rather than one global
project score. Unassisted performance, novel-context transfer, and delayed
retention remain distinguishable. Completion, dwell time, clicks, engagement,
recommendation acceptance, hints, response time, and accommodations do not
silently become competency evidence. AI-scored work is a provenance-rich
proposed observation and cannot establish competency alone.

### Adaptive Assessment and Recommendation Ranking

Curriculum and deterministic policy first restrict assessment items and
learning actions by prerequisites, permissions, content validity,
accessibility, exposure, burden, exclusions, and learner choice. Adaptive
assessment may select within the valid item pool by expected information gain,
posterior entropy reduction, Fisher information, or a comparably qualified
method. It stops when reviewed uncertainty and coverage targets are met and
abstains when burden limits are reached without adequate evidence.

Adaptation retains an explainable rule-based ranking baseline. A conservative
contextual bandit may become the first model-influenced ranking policy after
qualification, but it ranks only the deterministic eligible set and optimizes
delayed learning gain, retention, transfer, opportunity, and burden rather than
engagement alone. Long-horizon reinforcement-learning or POMDP policies remain
offline or in shadow research until logged support, delayed rewards, and safety
evidence are adequate. Learners may choose another eligible action.

### Learner-Facing Publication

Raw estimates and ranking scores are never displayed as authoritative mastery.
A reviewed deterministic publication policy consumes the versioned estimate
and may emit `insufficient`, `developing`, or `demonstrated`, with a separate
`review_due` freshness condition. It considers conservative posterior bounds,
uncertainty, evidence coverage and diversity, recency, delayed retention,
transfer, contradictions, abstention, out-of-distribution status, and drift.

Every label or recommendation explanation identifies the evidence and policy
that support it, the material limits, freshness, and an eligible next action
that can improve or test the estimate. Weak, stale, inapplicable, or poorly
calibrated evidence falls back to evidence-only progress rather than a forced
label. The presentation cannot imply a credential, professional competence,
investment suitability, or personalized financial advice.

### Qualification and Experiments

Delivery is phased:

1. Establish the deterministic evidence, eligibility, publication, and ranking
   baselines with complete provenance and replay.
2. Evaluate interpretable probabilistic champions and challengers offline with
   learner-disjoint chronological splits, cold-start regimes, leakage controls,
   calibration and subgroup calibration, log loss, Brier score, selective
   risk/coverage, false-positive `demonstrated` risk, retention, and transfer.
3. Run qualified challengers in shadow mode before any learner influence.
4. Permit model influence only for the supported population, evidence regime,
   and prediction horizon, with monitoring and immediate deterministic fallback.
5. Permit online exploration only through a separately reviewed experiment
   with explicit consent and opt-out, randomization solely among eligible
   actions, bounded exposure, support diagnostics, preregistered learning,
   retention, burden, and harm measures, stopping rules, and rollback.

Offline policy evaluation retains the complete eligible candidate set, chosen
action, policy version, and assignment propensity. It uses support diagnostics
and appropriate inverse-propensity, doubly robust, and uncertainty or confidence-
sequence methods, and abstains when logged support is inadequate.

## Consequences

- The platform can compare established psychometric and knowledge-tracing
  methods with modern neural, graph, semantic, and policy-learning challengers
  without binding product semantics to one model family.
- Estimate generation and learner-facing publication are independently
  versioned, so a model can improve without silently changing claims language.
- Calibration, selective prediction, abstention, retention, and transfer become
  first-class acceptance evidence rather than optional research metrics.
- The rule baseline and evidence-only presentation remain permanent degraded
  modes, preventing research infrastructure from blocking core learning.
- Rich provenance, replay, consent, monitoring, and subgroup evaluation add
  material data, operational, accessibility, privacy, and research-governance
  work.
- Corrections append superseding evidence and replay derived state; they do not
  erase the original evidence or silently rewrite prior policy versions.

## Alternatives Rejected

- **Threshold labels and rule ranking only.** Retained as the baseline and
  publication layer, but rejected as the target because it cannot adequately
  represent uncertainty, temporal learning and forgetting, active assessment,
  or empirical policy comparison.
- **Evidence-only progress with no competency projection.** Retained as the
  mandatory fallback, but rejected as the sole behavior because it withholds
  useful bounded guidance when evidence and calibration are adequate.
- **Probabilistic inference limited to offline or shadow operation forever.**
  Rejected as the target because carefully governed learner-impact research is
  needed to estimate causal learning outcomes, though online influence is not
  authorized until its separate experiment review succeeds.
- **Select one newest neural model as the architecture.** Rejected because
  benchmark leadership does not establish calibration, validity, fairness,
  transfer, or fitness for this evidence regime.
- **Optimize engagement or recommendation acceptance.** Rejected because those
  measures are not competency evidence and can conflict with learning,
  autonomy, accessibility, and burden objectives.

## Boundaries

This decision accepts the technique portfolio, stable estimate/publication
seams, phased qualification path, and experiment-control envelope. It does not
approve a concrete model or model version, dataset or data license, feature
pipeline, provider, promotion threshold, learner cohort, production experiment,
or automated protected-state mutation.

Deterministic policy remains authoritative for eligibility, prerequisites,
permissions, grading, evidence admission, publication, accessibility, exposure,
burden, and durable state. Online experiments cannot affect grades,
credentials, access, financial decisions, or other protected outcomes.

## Verification Implications

- Prove exact evidence provenance, deterministic replay, correction through
  superseding evidence, time-aware state, and absence of engagement-only
  competency signals.
- Prove estimates retain uncertainty, coverage, applicability, drift,
  calibration, model, dataset, feature, selection, and source-evidence versions.
- Prove invalid, stale, unsupported, out-of-distribution, or uncalibrated state
  abstains to evidence-only presentation without blocking the learner.
- Prove deterministic eligibility both before ranking and after advisory model
  output; ineligible actions never enter an experiment or recommendation.
- Qualify prediction with leakage-resistant chronological and cold-start splits,
  calibration and subgroup calibration, selective risk, delayed retention,
  transfer, accessibility, and false-positive demonstrated-state evidence.
- Prove a model/provider outage, disabled capability, quota, or policy failure
  returns immediately to the versioned rule baseline.
- Prove experiment consent, opt-out, candidate/propensity logging, support
  diagnostics, bounded assignment, stopping, monitoring, and rollback before
  any online exploration.
- Prove labels and explanations expose source evidence, limits, uncertainty,
  freshness, alternatives, and no credential, suitability, or advice meaning.

## Supersession

A change that makes a model authoritative, removes the deterministic or
evidence-only fallback, changes the learner-facing claim categories, admits
engagement as competency evidence, allows experiments outside the accepted
envelope, or changes protected-outcome authority requires a superseding ADR.
Replacing one qualified estimator or ranking strategy within these stable
contracts requires promotion evidence, not a new architecture decision.
