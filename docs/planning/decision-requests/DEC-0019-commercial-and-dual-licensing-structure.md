---
id: DEC-0019
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

# Decision Request: Choose the Commercial and Dual-Licensing Structure

## Decision Needed

Choose how the current GPLv3 repository, hosted service, proprietary modules,
extension distribution, contributor rights, and edition entitlements may relate.

## Why Now

CAP-0025 and CAP-0028 need truthful entitlement and managed-service boundaries.
Architecture cannot assume proprietary modules, dual licensing, or hosted-service
rights without qualified legal and product decisions.

## Current Authority and Constraints

The repository is GPLv3. Local and cloud share one semantic core; commercial
differences may use adapters, entitlements, operational services, and separately
reviewed modules, but legal effects and contributor rights are unresolved.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. GPLv3 community core plus hosted managed service, no relicensing assumption | Minimal governance change and clear open-source core; monetization focuses on operations/support. | May constrain proprietary distribution and some partnerships; hosted-service implications need legal review. | Edition capability/entitlement descriptions, service terms, packaging and contributor guidance. | Medium; later relicensing needs rights and community process. |
| B. Dual-license eligible code with contributor agreement and separated commercial modules | More commercial distribution flexibility and clearer proprietary extension path. | Significant legal, contributor, repository-boundary, governance, and community-trust cost. | License files, contribution workflow, module boundaries, packaging, entitlements and compliance operations. | Low; rights collection and ecosystem effects persist. |

## Recommendation

Defer to qualified legal/product review. Continue planning against Option A's
minimal assumptions and avoid proprietary-module or dual-license claims until a
decision is promoted.

## Evidence Required

- Qualified analysis of GPLv3, hosted use, linking/distribution, extensions,
  contributor ownership, trademark, and third-party dependencies.
- Business/product model and partner requirements.
- Contributor/community impact and repository-boundary proposal for Option B.

## Required Authority

Organizational product/commercial authority with qualified legal counsel and
open-source governance review.

## Decision Record and Promotion

Promote the selected structure to authoritative licensing, contribution,
edition/product, architecture, packaging, and decision-readiness documents.

## Dependent Planning Updates

Reconcile CAP-0025 and CAP-0028 plus any commercial provider/module plans.

## Planning History

- 2026-10-15: Captured from the existing explicit commercial/licensing readiness gate.

