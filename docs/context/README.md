# AI Context Routing

- Status: accepted
- Canonical for: context-pack purpose and assembly

Context packs are compact, derived routing aids. They reduce indiscriminate repository loading but never replace product, domain, architecture, ADR, risk, security, or standards sources.

Always load `packs/index.pack.md`. Then use `prompt-routing.md` and `pack-catalog.json` to add one primary and normally no more than one adjacent pack. Read the canonical sources named by the selected packs and inspect current implementation/tests before acting.

No context pack may exceed 200 physical lines. When more detail is needed, improve the canonical source and link to it.

