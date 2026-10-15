---
id: DEC-0009
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: null
---

# Decision Request: Choose the Initial Competency and Mastery Projection Policy

## Decision Needed

Choose what learner-facing competency or mastery projection may be derived from
the initial evidence set, including thresholds, uncertainty, correction, and
claims language.

## Why Now

CAP-0009 and CAP-0010 require more than raw completion history. Without an
accepted policy, a score or UI label could silently become an unsupported claim
about mastery, ability, or readiness.

## Current Authority and Constraints

Learner model owns derived state; Assessment owns source evidence; completion is
not mastery; deterministic policy is authoritative; credentials and professional
or investment competence claims are excluded.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Evidence-threshold competency levels | Use reviewed per-competency evidence rules with `insufficient`, `developing`, and `demonstrated` states, explicit uncertainty, decay/review policy, and no global mastery score. | Requires policy authoring and calibration; may initially cover few competencies. | Learner-state projection, evidence mappings, progress UI, portable records, adaptation inputs. | High; policies are versioned and old projections remain reproducible. |
| B. Evidence-only progress with no competency state | Show source evidence and completion summaries only until later empirical work justifies a projection. | Safest but does not fully deliver competency projection or adaptive evidence goals. | Progress UI and export; adaptation remains limited to completion/prerequisites. | Very high; later policy can be added without migrating a prior claim. |

## Recommendation

Option A, limited to reviewed competencies and explicit insufficient-evidence
states. It provides useful deterministic guidance without a universal score or
credential claim. Assumption: initial competencies can receive human-reviewed
evidence mappings and thresholds before implementation.

## Evidence Required

- A representative competency/evidence mapping and threshold review.
- False-positive/false-negative and accessibility impact analysis.
- Versioning, correction, decay/review, and explanation prototypes.
- Product/risk review of learner-facing claims language.

## Required Authority

Product/domain learning authority with assessment, learner-model, education-risk,
and accessibility review.

## Decision Record and Promotion

Promote the chosen policy to an ADR or learner-model architecture document and
update the decision-readiness register before dependent CAP approval.

## Dependent Planning Updates

Reconcile CAP-0009 and CAP-0010 acceptance, contracts, and slice boundaries to
the selected policy.

## Planning History

- 2026-10-15: Captured while shaping catalog candidates 6 and 7.

