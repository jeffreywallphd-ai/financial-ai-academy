# Capability Roadmap Review Site

This local, read-only site dynamically reviews the product capability catalog
and governed CAP/SLI/WRK/DEC planning sources. It does not copy roadmap data into
the site and does not use `docs/planning/register.md` as a database.

From the repository root, run:

```text
python dev-tools/roadmap-review-site/server.py
```

Then open `http://127.0.0.1:8765`. The command compiles the TypeScript client
with the repository-pinned compiler into ignored
`.local-codex/roadmap-review-site/` output before starting. Browser refreshes
reproject the current JSON capability catalog, planning frontmatter and public
plan content, and CAP-0003 order/compatibility evidence. No data-generation,
approval, packet claim, or repository-wide test command is required to review
the roadmap.

The overview accounts for all 26 product candidates and distinguishes formal
CAP coverage from unplanned candidates. Its proposed-order card mirrors the
default control-plane allocation's currently active and dependency-ready lanes
in exact order. Singleton groups are identified as sequential lanes and
multi-capability groups as evidence-backed parallel-safe lanes. The broader
dependency order, unresolved ties, blockers, and full compatibility diagnostics
remain advisory context: they do not grant authority, acquire a lease, treat
unknown evidence as safe, or turn future ordering into a global lock. Internal
enabling CAPs remain separate from the product catalog.

The server binds to numeric loopback addresses only, accepts GET and HEAD only,
serves a fixed asset allowlist, and exposes no planning mutation. API responses
use `Cache-Control: no-store`; a refresh therefore reflects current sources.
Stable detail routes are resolved only against the current projection:

- `/capability/<catalog-key>` shows a product candidate and its mapped plan, or
  an honest not-yet-planned state.
- `/cap/<planning-id>` shows a formal mapped or internal capability.
- `/slice/<planning-id>` shows a refined plan and its work, or a useful declared
  placeholder before just-in-time refinement.
- `/work/<planning-id>` shows the current work plan and public completion
  evidence.
- `/decision/<planning-id>` shows the current decision-request details, public
  lifecycle state, and whether an outcome has been recorded.

Capability, slice, and work pages link their relevant decision requests and
show each request's current status. Slice pages inherit capability links, and
work pages inherit capability and slice links, so decisions remain visible at
the point of use without duplicating them in static site data. A missing
decision reference stays visible as a non-blocking local diagnostic. A
`complete` decision request means an outcome has been made even when no
separate ADR or decision-record file is linked. Private approval-ledger and
reviewer information is never projected.

Plan headings, paragraphs, lists, tables, and code are constructed as inert DOM
text from `roadmap-review-v1`. URL segments never become filesystem paths, and
there is no per-artifact route registration or generated detail page.

Focused checks:

```text
python dev-tools/roadmap-review-site/test_server.py
node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom dev-tools/roadmap-review-site/tests
node apps/web/node_modules/typescript/bin/tsc -p dev-tools/roadmap-review-site/tsconfig.json --noEmit
python dev-tools/roadmap-review-site/test_qualification.py
node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/tests/browser/roadmap-review.config.ts
```

The dependency-free qualification and projection suites are part of aggregate
agent readiness. TypeScript, live loopback, DOM, and Chromium/axe tests remain
focused affected-interface evidence; the fixed gate intentionally does not
require Node dependencies, a browser installation, or a socket for unrelated
repository work.

The reusable boundary is `roadmap-review-v1`, implemented by the project-neutral
control-plane projection and this repository's adapter. A future repository can
reuse that contract and the client view model while supplying its own catalog,
planning vocabulary, projection adapter, and semantic design assets.
