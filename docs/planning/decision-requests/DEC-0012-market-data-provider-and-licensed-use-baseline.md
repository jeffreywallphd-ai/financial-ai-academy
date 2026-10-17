---
id: DEC-0012
kind: decision-request
planning_status: verifying
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md
---

# Decision Request: Set the Market-Data Provider and Licensed-Use Baseline

## Decision Needed

Choose the initial market-data sourcing architecture and the exact provider,
plan, deployment profile, and use combinations that may be admitted for local
community and managed-cloud operation. The decision must cover retrieval,
display, attribution, caching, persistent storage, backup, transformation,
export, redistribution, derived outputs, AI/ML use, retention, and provider
exit.

Provider admission is separate from sourcing architecture. Selecting an
architecture or naming a preferred provider does not grant a use right. Every
admitted combination still requires a current, versioned rights profile and
qualified licensing review.

## Why Now

Market exploration, financial analysis, portfolios, experiments, provider
governance, and local/cloud operation all depend on data that may be technically
accessible but contractually restricted. The initial choice must keep useful
community workflows possible without silently granting managed, commercial,
redistribution, or AI/ML rights.

## Current Authority and Constraints

- Provider terms and public-source notices remain authoritative and
  time-sensitive; repository summaries never replace them.
- Raw provider payloads stay inside adapters until validated and normalized.
  Canonical records preserve source, retrieval time, applicable-use profile,
  transformations, quality, and attribution references.
- Technical access, an API key, a paid plan, or a user-supplied key never by
  itself authorizes storage, cloud processing, export, redistribution,
  commercial use, derived-data publication, or AI/ML use.
- Rights are evaluated for an exact provider, dataset, plan or order form,
  deployment profile, product use, user class, data layer, and time period.
- Unsupported or expired rights fail closed and disable only the affected
  source/use path. User-supplied imports remain a provider-independent fallback,
  subject to provenance validation and the user's right to use the material.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| Initial sourcing architecture | ready | C. Staged hybrid with rights-profiled imports, public sources, Alpha Vantage, and later managed sources | Use Option C under ADR-0020. | none |
| Community-provider posture | constrained | Alpha Vantage first through an explicitly configured educational profile; authoritative public sources and validated imports remain available | Implement Alpha Vantage first without making it mandatory or provider-shaped. | none |
| Managed-cloud provider posture | constrained | No managed-cloud market-data provider is admitted by this decision | Keep managed use disabled until an exact written rights profile and qualified review exist. | none |
| Data-use enforcement | ready | Versioned default-deny use profiles for every provider/plan/deployment/use combination | An unspecified, ambiguous, expired, or conflicting right remains denied. | none |
| Alpha Vantage admission | constrained | Narrow educational/local integration for exact allowlisted datasets and uses covered by current evidence | Treat published education support as quota evidence; separately gate persistence, backup, export, redistribution, real-time, shared service, and AI/ML use. | none |

The constrained paths follow [ADR-0002](../../adr/ADR-0002-contract-driven-provider-architecture.md),
[ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md),
[Provider and Plugin Contracts](../../architecture/contracts/provider-and-plugin-contracts.md),
and [Market-Data Licensing and Attribution](../../risk-compliance/market-data-licensing-and-attribution.md).

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Reviewed free/open provider baseline plus per-adapter use profiles | Enables a useful built-in community baseline from authoritative or permissively usable sources with explicit coverage, delay, attribution, cache, export, and cloud limitations. | “Public” does not mean uniformly unrestricted; FRED and similar aggregators can carry third-party rights at the series level. Coverage is fragmented and may not meet equity-history needs. | Provider manifests, source register, series allowlists, cache/retention, attribution UI, export, provenance, and conformance tests. | Medium; adapters can be disabled, but retained and backed-up data still needs exit handling. |
| B. User-supplied local imports only | Avoids a built-in provider commitment, keeps acquisition with the user, and provides a durable fallback independent of vendor availability. | Poorer onboarding, harder provenance and rights validation, no common live-query behavior, and no relief from import-rights guidance. | Import contract, local storage, provenance, validation, rights acknowledgement, and export restrictions. | High; providers can be added later. |
| C. Staged hybrid with rights-profiled public, BYOK, and managed sources | Combines a universal import fallback, authoritative public sources, an optional community BYOK path, and separately negotiated managed service. Each stage can advance without granting rights to another stage. | More policy and conformance work; provider/plan/use matrices can drift, and the managed tier still depends on written commercial terms. Product behavior must remain honest when sources differ. | All Option A/B surfaces plus plan-aware credentials, deployment-specific provider admission, feature flags, rights-policy evaluation, recurring terms review, and provider-exit workflows. | Medium-high if provider-neutral contracts and source-specific disablement remain intact. |

### Option C Stages

1. **Universal fallback:** accept validated user-supplied local imports with exact
   source, acquisition, rights assertion, integrity, and transformation
   provenance. Import never implies redistribution or managed-cloud rights.
2. **Authoritative direct sources:** evaluate SEC, BLS, and BEA endpoints under
   source-specific profiles. Admit FRED only through an allowlist that reviews
   each series' source and restrictions; FRED aggregation is not treated as a
   universal license.
3. **Community BYOK:** qualify Tiingo as the leading candidate through its
   developer/BYOK path. Enforce plan-aware transient and retention behavior;
   never assume a free or user-held subscription authorizes platform storage or
   managed service use.
4. **Managed cloud:** seek written terms and an order form from Twelve Data
   first. Evaluate Massive as a higher-cost enterprise alternative when its
   order form expressly covers required display, non-display, derived, export,
   redistribution, and AI/ML uses.

Each stage is an independently admitted source/use profile. A later stage does
not replace the import fallback or broaden an earlier stage's rights.

## Candidate Source and Provider Assessment

This research snapshot was reviewed on 2026-10-16. Linked source terms and
notices remain authoritative and require archival plus qualified review before
admission.

| Source or provider | Candid fit | Current official evidence | Evidence still required |
| --- | --- | --- | --- |
| SEC EDGAR | Strong authoritative direct source for filing/submission facts, not a price-history provider. | [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [developer guidance](https://www.sec.gov/about/developer-resources), and [reuse FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions) describe public API access, fair-access expectations, and reuse caveats. | Endpoint-level attribution, third-party-content exceptions, cache/backup/export mapping, operational limits, and an archived review snapshot. |
| BLS | Strong authoritative direct source for labor and price-index series. | [API terms](https://www.bls.gov/developers/termsOfService.htm) and [API limits](https://www.bls.gov/developers/api_faqs.htm) describe source credit, public-data use, registration, and request limits. | Series coverage/refresh qualification, exact attribution presentation, operational budget, and archived terms evidence. |
| BEA | Strong authoritative direct source for national and regional economic statistics. | [API documentation](https://apps.bea.gov/API/docs/index.htm) and [reuse guidance](https://www.bea.gov/help/faq/147) describe the API and reuse of BEA-produced material. | Dataset/parameter allowlist, source credit, third-party exceptions, rate/outage behavior, and archived review evidence. |
| FRED/ALFRED | Useful macroeconomic aggregator only through a per-series allowlist. | [API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html) preserve source/third-party rights; [error guidance](https://fred.stlouisfed.org/docs/api/fred/errors.html) documents the 120-requests-per-minute limit; [ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html) provides vintage observations. | A rights and attribution record for every admitted series/source, vintage/retention mapping, export rules, and automated removal when a series becomes ineligible. |
| Tiingo | Strongest current community/BYOK candidate for historical market data, subject to plan-aware enforcement. | [Terms](https://app.tiingo.com/tos/) were updated 2026-10-06: the free Starter posture forbids persistent raw/derived storage; eligible paid plans permit retention only while subscribed, require raw-data deletion after cancellation/downgrade, and constrain derived outputs to non-reconstructible results. See also [developer/BYOK guidance](https://www.tiingo.com/documentation/appendix/developers), [pricing](https://www.tiingo.com/about/pricing), [end-of-day data](https://www.tiingo.com/documentation/end-of-day), and [corporate actions](https://www.tiingo.com/documentation/corporate-actions/splits). | Written confirmation for the exact desktop/community distribution, credential flow, transient caches, canonical storage, backups, exports, derived results, and platform support responsibilities. |
| Twelve Data | Best first managed-cloud negotiation target because its terms expose relevant rights categories. | [Terms](https://twelvedata.com/terms), updated 2026-01-01, distinguish internal, display, redistribution, non-display, and derived uses. [Usage guidance](https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage), [business pricing](https://twelvedata.com/pricing-business), [credit limits](https://support.twelvedata.com/en/articles/5615854-credits), and [adjustment guidance](https://support.twelvedata.com/en/articles/5179064-are-the-prices-adjusted) clarify plan and data behavior. | A written order form and rights matrix covering every intended managed use, user count/audience, machine-readable output, caching/retention/backups, exports, derived data, AI/ML, attribution, SLA, price, and exit deletion. |
| Massive | Credible higher-cost enterprise alternative when an order form expands the needed rights. | [Business terms](https://massive.com/legal/businesses-terms-of-service), updated 2026-10-06, state that standard business rights prohibit machine-readable end-user feeds and AI/ML training unless an order form expressly permits them. See [business](https://massive.com/business) and [individual](https://massive.com/pricing?product=stocks) pricing, [SLA](https://massive.com/legal/businesses-terms-of-service-sla), and [stocks overview](https://www.massive.com/docs/rest/stocks/overview). | Written order-form rights for all required uses, entitlements/exchanges, derived-data definitions, redistribution/export, AI/ML, retention/backup/deletion, SLA, support, and full cost. |
| Alpha Vantage | First external integration target for a narrow educational/local path, not an exclusive or automatically enabled baseline. | [Public terms](https://www.alphavantage.co/terms_of_service/) include private individual investment analysis, research, testing, and monitoring within the non-commercial grant while treating organizational and shared access separately. [Support guidance](https://www.alphavantage.co/support/) documents unlimited requests for verified open-source or educational projects. [Documentation](https://www.alphavantage.co/documentation/) and the [real-time policy](https://www.alphavantage.co/realtime_data_policy/) describe coverage and separate exchange-controlled real-time use. | Record the exact credential owner, dataset, deployment, audience, quota, attribution, retention, export, and exit profile. Public education support does not by itself authorize storage, backup, managed cloud, redistribution, real-time data, or AI/ML use. |
| User-supplied imports | Universal local fallback and useful for private research datasets. | No provider contract can supply rights for arbitrary user material; the platform can validate format, provenance, and a user rights assertion only. | Product policy for accepted formats, source/right declarations, prohibited data, cloud upload, retention, export, deletion, and dispute/takedown handling. |

## Default-Deny Use Profiles

Every admitted source receives a versioned profile for the exact provider,
dataset/series, plan/order form, deployment, user class, and product feature.
Missing, ambiguous, expired, or conflicting rights evaluate to `deny`.

| Use | Required profile evidence before allow |
| --- | --- |
| Retrieval and transient processing | Authorized endpoint/dataset, deployment, user class, credential posture, rate/quota, and permitted purpose. |
| Display and attribution | Audience, delayed/real-time status, exact attribution/branding, transformation disclosure, and entitlement requirements. |
| Cache | Permitted data layer, duration, location, refresh, encryption/access, and deletion trigger. |
| Persistent raw or canonical storage | Express retention right for the exact plan/use, permitted transformations, subscription dependency, and deletion/migration behavior. |
| Backup and recovery copies | Express inclusion, encryption/access, retention period, restore constraints, and purge behavior; storage permission does not automatically include backup permission. |
| Export | Permitted fields, format, audience, volume, attribution, entitlement, and machine-readable restrictions. |
| Redistribution | Express right for the recipient class and channel; internal use or display rights never imply redistribution. |
| Derived outputs | Provider definition, non-reconstructibility threshold, permitted audience/use, attribution, and exit treatment. “Derived” is not assumed merely because data was transformed. |
| AI/ML use | Express rights separately for feature generation, evaluation, inference context, training/fine-tuning, embedding, benchmark publication, and output retention. No initial AI/ML use is assumed. |

Profiles also record source/version/effective date, archival evidence digest,
review date, re-review deadline and triggers, responsible owning role, feature
flags, and exact disable/delete actions. Runtime policy enforces the profile;
adapters and product code do not interpret prose terms.

## Product Questions for Profile Expansion

1. Which datasets are required for the first learner outcome: macroeconomic
   series, filings/fundamentals, U.S. end-of-day equities, corporate actions,
   exchange coverage, or real-time/delayed observations?
2. Is BYOK acceptable for community onboarding, and may the platform ever
   persist data obtained through a user's plan?
3. Which managed-cloud actions are required: interactive display, server-side
   non-display calculations, persistent canonical history, bulk/machine-readable
   export, learner downloads, or downstream redistribution?
4. What offline-retention, backup, restore, and reproducibility periods are
   required after a subscription ends or terms change?
5. Are any market observations needed for AI/ML feature generation, evaluation,
   training, inference, or published benchmarks? If not, the initial profile
   should deny all AI/ML uses.
6. What launch markets, user classes, tenant sizes, request volumes, uptime,
   support, data-delay, and budget bounds must the managed provider meet?
7. What degraded behavior is acceptable when a provider, series, entitlement,
   or right is unavailable?

## Evidence Required Before Profile Activation or Expansion

- An archived copy and digest of each applicable official term, policy, dataset
  notice, plan, order form, exchange entitlement, and attribution rule, with
  source URL, version/effective date, review date, and re-review trigger.
- A provider-written rights matrix answering every default-deny use row for the
  exact community and managed product designs. Sales summaries and generic
  pricing pages are insufficient.
- Qualified licensing/legal review of the archived matrix and intended
  implementation, with product/data, risk, security/privacy, operations,
  recovery, and commercial review of their respective boundaries.
- Coverage, quality, calendar, adjustment, split/dividend/corporate-action,
  vintage, delay, correction, symbol-identity, and provenance qualification.
- Rate/quota, outage, cost, SLA/support, credential, egress, privacy/security,
  conformance, and local/cloud operational evidence.
- A tested source-disable and provider-exit plan covering retrieval shutdown,
  data/backup inventory, export cutoff, required deletion or migration,
  preserved non-provider audit evidence, user communication, and replacement.

## Recommendation

Use **Option C's staged sourcing architecture** and make Alpha Vantage the
first external integration target. Preserve validated imports and add
authoritative public or commercial providers through the same platform-owned
contracts as evidence and product needs justify them.

The Alpha Vantage adapter starts narrow: explicitly configured educational or
research use, allowlisted historical/end-of-day datasets, and transient
processing unless the exact recorded profile grants more. It is not a bundled
credential, exclusive source, managed-cloud authorization, real-time
entitlement, storage grant, redistribution right, or AI/ML dataset.
The initial plan posture is the free API with its standard published quota, or
the higher education/open-source quota only when the exact supplied credential
has current verification evidence; the platform does not assume a shared key.

[ADR-0020](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
records the provider-neutral contracts, default-deny rights profiles, initial
Alpha Vantage boundary, fallback behavior, provider evolution path, and
verification requirements.

## Recurring Terms Review and Provider Exit

Re-review each admitted profile at least annually and before renewal,
plan/order-form changes, new datasets or features, new deployment/user classes,
new export/redistribution/AI use, provider acquisition, or a material terms,
exchange-policy, attribution, pricing, SLA, or security change. Automated link
monitoring may flag review but cannot approve changed rights.

On expiration, ambiguity, downgrade, cancellation, or adverse terms change,
fail closed for new retrieval and affected uses; inventory raw, canonical,
derived, cache, export, and backup copies; execute the profile's deletion or
migration rules; preserve only permitted audit/provenance facts; and require a
new reviewed profile before re-enablement. Provider replacement never silently
changes canonical market semantics or historical result provenance.

## Required Authority

Product/data authority with qualified legal/licensing, risk, security/privacy,
operations, recovery, and commercial review. Provider-written clarification is
required wherever public terms do not expressly cover the intended use.

## Decision Record and Promotion

[ADR-0020](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
establishes the staged hybrid and Alpha Vantage-first integration boundary.
The external-source register, licensing guidance, and decision readiness carry
the current public-evidence and default-deny posture. Each activated provider
profile still requires versioned evidence so later admissions or rights changes
do not silently broaden the decision.

## Dependent Planning Updates

Reconcile CAP-0012, CAP-0016, CAP-0024, CAP-0027, and any export, portfolio,
analysis, experiment, or AI/ML path that consumes market data.

## Planning History

- 2026-10-15: Captured as a shared gate for market-data-dependent capabilities.
- 2026-10-16: Added provider research, a staged hybrid Option C, default-deny
  rights profiles, product questions, qualified-review evidence, and recurring
  terms-review/provider-exit obligations. The request remains captured pending
  written rights matrices and qualified licensing review.
- 2026-10-16: ADR-0020 selected Option C with Alpha Vantage as the first narrow
  educational integration. Provider-neutral contracts, synthetic fixtures,
  explicit configuration, and default-deny use profiles keep later providers
  additive and reserve undocumented storage, cloud, redistribution, real-time,
  export, and AI/ML uses.
