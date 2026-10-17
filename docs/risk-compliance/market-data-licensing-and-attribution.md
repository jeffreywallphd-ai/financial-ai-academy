# Market-Data Licensing and Attribution

- Status: accepted
- Canonical for: initial data-use and provider-admission posture

[ADR-0020](../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
selects a staged, rights-profiled hybrid and Alpha Vantage as the first narrow
educational integration. Alpha Vantage is an adapter target, not the canonical
data model, an exclusive provider, a bundled credential, or general license
authority. Validated imports remain available, and later public or commercial
sources use the same platform-owned contracts.

An accessible API does not imply unrestricted storage, transformation, display, redistribution, model training, or commercial use.

Before admitting a market-data provider or dataset, record:

- provider and authoritative terms source,
- permitted local, educational, research, cloud, and commercial uses,
- display and attribution requirements,
- caching and retention limits,
- redistribution and derived-data restrictions,
- training or model-use restrictions,
- user-supplied-key implications,
- review date and responsible decision,
- required deletion or migration behavior if permission changes.

Raw data, canonical records, derived features, example fixtures, and published datasets may have different permissions. Each layer retains provenance and an applicable-use reference.

Every provider/use profile defaults to deny for rights it does not state. For
the first Alpha Vantage profile, education-project quota support does not by
itself authorize persistent storage, backups, multi-user or managed-cloud
display, real-time or delayed exchange data, export, redistribution,
publication, or AI/ML use. Enable only the exact dataset, credential owner,
deployment, audience, processing, retention, and display combination supported
by current recorded evidence.

Repository tests, examples, screenshots, and published fixtures use synthetic
or expressly permitted data. A provider profile must define expiry, terms-change
review, disablement, retained-data inventory, deletion or migration, attribution,
and replacement behavior before activation.

