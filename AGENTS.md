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

## Interface Design Contract

Before changing a user-facing interface:

1. Read `docs/design/README.md`, `docs/design/style-guide.md`, and `docs/standards/interface-design-standards.md`.
2. Use semantic variables from `apps/web/src/design-system/tokens.css`; do not create feature-local colors, spacing scales, shadows, radii, or theme maps.
3. Use the reviewed SVG pack in `apps/web/src/design-system/icons/`; do not substitute emoji, icon fonts, generated raster controls, or unreviewed third-party icons.
4. Preserve equivalent content, actions, hierarchy, contrast, focus, and responsive behavior in light and dark modes.
5. Treat `docs/design/mockups/` as directional guidance only, never as exact implementation authority.

When a shared visual decision changes, update the style guide, executable tokens or icon assets, consuming UI, and relevant tests in the same change. Run `python dev-tools/design/check_design_system.py` and the documentation check.

## Decision Gates

Stop before implementation when a task requires an unresolved identity, tenancy, data-license, model-authority, cloud-provider, queue, encryption, recovery, legal/commercial, or external-execution decision listed in the decision-readiness register.

## Planned Work

When creating, reviewing, or executing a planning artifact, read `docs/planning/README.md` and the relevant entry in `docs/planning/register.md`. Decompose substantial work from capability to vertical slice to bounded agent work packet. Treat `ready` as sufficient implementation detail, not as authority to begin work. Revalidate the packet against current canonical sources and decision readiness before changing implementation.

Use the compatible skills cataloged in `docs/planning/skills/README.md`; use `guide-next-planning-action` for broad “what next?” requests. General planning or advice requests are read-only unless the user explicitly authorizes a file-changing action.

Keep `docs/planning/skills/` canonical and use `python docs/planning/skills/sync_skills.py --mode auto` when repository-local Codex discovery is needed. Verify an installed copy with `--check`; never edit the ignored `.agents/skills/` copy as a source.

**Before any planning skill changes a repository file, it must perform and report the Required Startup in this file and `docs/README.md`.** A skill, plan, approval field, or roadmap never overrides those instructions.

Keep capability framing, durable decision, slice selection, plan readiness, implementation activation, and completion acceptance as separate human approval stages. An agent may record an explicit authorized decision but may not self-approve. Implementation requires approved slice selection, approved packet planning, separate implementation approval with scoped authority, and a current explicit user instruction to implement the named work.

Reserve planning IDs with `dev-tools/planning/reserve_id.py`. Before implementation, declare bounded `write_scope` and `generated_artifacts`, follow `docs/planning/concurrent-work.md`, and claim the approved packet with `dev-tools/planning/claim_packet.py`. An active packet must have one owner, a base revision, durable claim evidence, and no uncoordinated scope overlap. Update its artifact and `docs/planning/register.md` together.

## Completion Evidence

Report the outcome, affected boundaries, checks run and their results, documentation impact, assumptions, known gaps, and any decision still requiring approval.

Run `python dev-tools/agent/check_ready.py` before handing off a repository change. It is the fixed aggregate planning, skill, prompt-evaluation, documentation, and design-system gate. Also run any narrower domain, contract, security, build, or application checks required by the affected boundary; the aggregate command does not replace them.
