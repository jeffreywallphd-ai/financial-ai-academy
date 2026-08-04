# Web Design System Assets

This directory contains executable, framework-neutral interface assets for the learner-facing web application.

## Sources

- [tokens.css](tokens.css) defines exact light/dark semantic variables, spacing, typography, layout, radii, shadows, motion, and z-index values.
- [icons/README.md](icons/README.md) documents the production SVG sprite, manifest, and icon CSS.
- [Interface Style Guide](../../../../docs/design/style-guide.md) defines the canonical design rules and intended use of these assets.

## Rules

- Import `tokens.css` once at the application root.
- Components consume semantic `--faa-*` variables rather than raw colors or arbitrary layout values.
- Use `data-theme="light"`, `data-theme="dark"`, or `data-theme="system"` on the document root.
- Reuse the icon sprite instead of adding icon fonts, emoji controls, or feature-local SVG copies.
- Update the style guide and executable assets together when a shared visual decision changes.

## Verification

```powershell
python dev-tools/design/check_design_system.py
```
