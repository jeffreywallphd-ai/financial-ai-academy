# AI Development Entry Point

This repository is documentation-led while its foundational product and architecture decisions are established.

## Required Startup for Non-Trivial Work

Before changing code or documentation:

1. Read `docs/README.md`.
2. Read `docs/context/packs/index.pack.md`.
3. Use `docs/context/prompt-routing.md` and `docs/context/pack-catalog.json` to select only materially relevant context.
4. Apply `docs/standards/change-impact-matrix.md`.
5. Consult `docs/adr/decision-readiness.md` for architecture-sensitive work.
6. Inspect the affected contracts, implementation, consumers, tests, and nearest README before editing.

## Authority

Accepted ADRs govern the decisions they record. Product and domain documentation governs intent and meaning. Executable schemas under `contracts/` govern exact external shapes. Architecture documentation governs ownership and dependency direction. Context packs are derived routing aids and never override canonical sources.

If canonical sources conflict, stop and surface the conflict. Do not silently select a convenient interpretation.

## Core Boundaries

- Preserve one shared domain/application core for local and cloud deployment profiles.
- Keep the backend a module-first Python modular monolith until extraction has evidence.
- Keep the web application TypeScript and dependent on generated public clients, not backend internals.
- Keep market-data, model, content, identity, storage, and job providers behind platform-owned ports.
- Keep provider-specific payloads out of domain models.
- Keep deterministic policy authoritative for eligibility, authorization, grading, financial calculations, and durable state changes.
- Treat AI and ML output as versioned, validated, observable input rather than unquestioned authority.
- Preserve provenance for learning evidence, recommendations, market observations, datasets, generated content, and portfolio results.
- Do not claim personalized financial advice, investment suitability, regulatory compliance, or guaranteed outcomes.

## Decision Gates

Stop before implementation when a task requires an unresolved identity, tenancy, data-license, model-authority, cloud-provider, queue, encryption, recovery, legal/commercial, or external-execution decision listed in the decision-readiness register.

## Completion Evidence

Report the outcome, affected boundaries, checks run and their results, documentation impact, assumptions, known gaps, and any decision still requiring approval.

For documentation, architecture, or context changes, run `python dev-tools/documentation/check_docs.py`.
