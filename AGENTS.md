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

When creating, reviewing, or executing a planning artifact, read `docs/planning/README.md` and the relevant entry in `docs/planning/register.md`. At the beginning of a capability, create one CAP planning package that bounds the outcome and enumerates and sequences every intended vertical slice. Refine each slice and its bounded agent work packets incrementally immediately before that slice or packet starts. Treat `ready` as sufficient implementation detail, not as independent authority; delivery authority comes from the current approved CAP package. Revalidate every packet against the approved CAP package, current canonical sources, and decision readiness before changing implementation.

In user-facing progress, status, handoff, and next-work output, identify the full known planning lineage as `CAP-####.SLI-####.WRK-####`. If no packet or slice exists yet, stop the display at the most specific known level. This dotted form is reporting notation only; keep canonical artifact IDs, links, front matter, register rows, and tool arguments as their existing independent `CAP-*`, `SLI-*`, and `WRK-*` values.

Use the compatible skills cataloged in `docs/planning/skills/README.md`; use `guide-next-planning-action` for broad “what next?” requests. General planning or advice requests are read-only unless the user explicitly authorizes a file-changing action.

Keep `docs/planning/skills/` canonical and use `python docs/planning/skills/sync_skills.py --mode auto` when repository-local Codex discovery is needed. Verify an installed copy with `--check`; never edit the ignored `.agents/skills/` copy as a source.

**Before any planning skill changes a repository file, it must perform and report the Required Startup in this file and `docs/README.md`.** A skill, plan, approval field, or roadmap never overrides those instructions.

Use one human planning approval stage: approval of the complete CAP planning package before delivery begins. The package must include the capability outcome, scope, constraints, applicable decision posture, and the complete enumerated and sequenced `SLI-*` set. `SLI-*` and `WRK-*` readiness, activation, verification, and completion are deterministic lifecycle controls, not human approval stages. Incremental slice and packet refinements do not require approval when they remain within the approved CAP package. A material change to the CAP outcome, boundaries, slice membership, ordering constraints, or risk/decision posture returns the CAP package to shaping and requires renewed CAP-level approval. Durable `DEC-*` choices and external or destructive actions retain their own explicit human authority and are not planning-stage approvals. An agent may record an explicit authorized decision but may never self-approve or infer authority.

**Store every approval and reviewer record only in the ignored `.local-codex/approvals/ledger.json`.** Tracked artifacts, registers, histories, summaries, tests, fixtures, and examples must not contain an approver/reviewer identity or label, decision, date, authority reference, reviewed scope, approval metadata, or approval history. Never copy a person's name, account name, display name, email address, or other personal identifier from task context into tracked files.

Reserve planning IDs with `dev-tools/planning/reserve_id.py`. Before implementation, declare bounded `write_scope` and `generated_artifacts`, follow `docs/planning/concurrent-work.md`, and claim a packet whose parent slice is included in the current approved CAP package with `dev-tools/planning/claim_packet.py`. Execute packets one at a time in dependency order unless their scopes are explicitly parallel-safe; complete the current packet before claiming its dependent successor. An active packet must have one owner, a base revision, durable claim evidence, and no uncoordinated scope overlap. Update its artifact and `docs/planning/register.md` together.

Perform tracked implementation and documentation work on a named `codex/*` branch, never directly on `main`. Treat `main` as an integration branch: after the work is CAP-authorized, complete, verified, and approved for integration, merge or fast-forward the finished `codex/*` branch into local `main`. Push `main` to a remote only with explicit authority for that external action. If in-progress work is discovered on `main`, preserve it and move it to an appropriate `codex/*` branch before continuing; never discard or silently overwrite it.

## Completion Evidence

Report the outcome, affected boundaries, checks run and their results, documentation impact, assumptions, known gaps, and any decision still requiring approval.

Run `python dev-tools/agent/check_ready.py` before handing off a repository change. It is the fixed aggregate planning, skill, prompt-evaluation, documentation, and design-system gate. Also run any narrower domain, contract, security, build, or application checks required by the affected boundary; the aggregate command does not replace them.
