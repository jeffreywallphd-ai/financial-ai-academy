# Interface Design Standards

- Status: accepted
- Canonical for: interface design-system use, theme parity, iconography, and synchronized visual-contract updates
- Design authority: [Interface Design System](../design/README.md)

## Required Sources

Before changing a user-facing interface, read:

1. [Interface Design System](../design/README.md)
2. [Interface Style Guide](../design/style-guide.md)
3. [Web design-system assets](../../apps/web/src/design-system/README.md)
4. [Iconography rules](../../apps/web/src/design-system/icons/README.md) when icons are involved

Mockups are directional references only and cannot authorize exact behavior, component structure, copy, calculations, data contracts, or accessibility exceptions.

## Token Discipline

- Use semantic variables from `apps/web/src/design-system/tokens.css`.
- Do not add raw color literals, arbitrary spacing, one-off radii, feature-local shadows, or duplicate theme maps in application components.
- Name new tokens for semantic purpose rather than a particular page or visual value.
- Prefer extending an existing role before adding a new token.
- Keep explicit dark mode and system-dark values synchronized.

## Theme Parity

- Light and dark modes expose the same content, actions, states, and hierarchy.
- Validate contrast, focus, charts, provider marks, disabled states, overlays, and status treatments separately in both themes.
- Do not use global inversion, reduced opacity, or image filters as a dark-mode implementation.
- Theme selection must support light, dark, and operating-system preference.

## Component and Layout Discipline

- Reuse the style guide's shell, grid, page-template, card, control, and responsive rules.
- Keep learning tasks visually primary and provenance or contextual actions secondary.
- Use border and surface hierarchy before adding elevation.
- Avoid nesting more than two visible card levels.
- Maintain the minimum target size and preserve logical reading order when rails stack on smaller screens.
- Do not shrink text or hide essential content to reproduce a desktop mockup at narrow widths.

## Iconography Discipline

- Use the reviewed SVG sprite and manifest.
- Icons inherit `currentColor`; theme values come from semantic tokens.
- Do not use emoji, icon fonts, generated raster icons, copied third-party SVGs, or provider marks as system icons.
- Icon-only controls require an accessible name and visible tooltip.
- Add a new icon only when the existing pack has no semantically suitable asset.

## Data and Financial Presentation

- Label sample, simulated, predicted, and observed values distinctly.
- Show units, effective time, currency, frequency, adjustment basis, assumptions, and provenance where applicable.
- Do not use color alone for positive/negative, risk, status, or chart-series meaning.
- Keep educational labs distinct from brokerage or execution interfaces.

## Same-Change Update Rule

When a shared visual decision changes, update all sources made stale in the same change:

- `docs/design/style-guide.md`;
- `apps/web/src/design-system/tokens.css`;
- the SVG sprite, manifest, icon CSS, and icon README when iconography changes;
- consuming components and affected visual/accessibility tests;
- this standard, context routing, or application documentation if their instructions change; and
- mockups only when a new directional reference is warranted.

Feature code must not become an undocumented alternative design system.

## Minimum Verification

```powershell
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
```

Interface implementation also requires focused browser checks for both themes, keyboard navigation, visible focus, responsive reflow, 200 percent zoom, reduced motion, forced colors, meaningful chart alternatives, and relevant assistive-technology behavior.
