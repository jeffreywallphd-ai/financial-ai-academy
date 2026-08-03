# ADR-0004: Shared Core for Local and Cloud

- Status: accepted
- Date: 2026-08-03

## Context

The project requires a useful locally run open-source edition and a commercializable managed-cloud edition.

## Decision

Both profiles use the same domain rules, application operations, contract versions, migrations, and standard provider interfaces. Differences are expressed through infrastructure adapters, entitlements, operational services, provider availability, and deployment configuration.

## Consequences

- Integrity and security fixes apply to both profiles.
- Portable import/export remains a shared responsibility.
- Commercial differentiation cannot rely on contradictory domain semantics or a private replacement API.
- Current GPLv3 licensing and any future commercial/dual-license structure remain separate legal/product decisions.

## Rejected Alternatives

- Separate community and cloud implementations
- Cloud-only domain behavior
- Database or provider choices embedded directly in feature modules

