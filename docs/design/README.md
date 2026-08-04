# Interface Design System

- Status: accepted
- Canonical for: interface visual language, design-token usage, iconography, and design-artifact authority
- Implementation sources: [web design-system assets](../../apps/web/src/design-system/README.md)
- Directional references: [interface mockups](mockups/README.md)

## Purpose

This area converts the visual direction explored in the mockups into an explicit, accessible, maintainable interface system for Financial AI Academy. It applies to community and managed-cloud interfaces unless a later accepted decision establishes a documented exception.

## Authority Map

| Resource | Authority |
| --- | --- |
| [Interface Style Guide](style-guide.md) | Canonical for visual principles, semantic token roles, spacing, layout, typography, component presentation, charts, and theme behavior |
| [Design tokens](../../apps/web/src/design-system/tokens.css) | Executable source for exact light/dark values consumed by the web application |
| [Iconography pack](../../apps/web/src/design-system/icons/README.md) | Canonical usage rules and production SVG assets |
| [Mockups](mockups/README.md) | Directional only; never an implementation specification |

If a mockup conflicts with the style guide or executable tokens, the style guide and tokens govern. Product, domain, architecture, contract, security, risk, and accessibility requirements still take precedence over visual presentation.

## Required Use

Before changing a user-facing interface:

1. Read the [Interface Style Guide](style-guide.md).
2. Reuse semantic variables from [tokens.css](../../apps/web/src/design-system/tokens.css); do not add one-off colors, spacing values, shadows, or radii inside feature code.
3. Reuse an icon from the [iconography pack](../../apps/web/src/design-system/icons/README.md); do not use emoji, font glyphs, or unreviewed third-party icons as interface controls.
4. Preserve functional parity, readable contrast, and equivalent hierarchy in light and dark modes.
5. Treat mockups as composition references only.

## Update Rule

Keep the design system current in the same change that introduces or alters a shared visual decision:

- update the style guide when a visual rule or component pattern changes;
- update `tokens.css` when an exact token value or semantic role changes;
- update the SVG sprite, icon manifest, and icon documentation together when icon geometry or meaning changes;
- update affected mockups only when a new directional illustration is genuinely useful;
- update application components and visual/accessibility tests that consume the changed contract; and
- run both design-system and documentation validation.

Feature code must not silently become the source of a new global pattern. Promote a repeated pattern here before broad reuse.

## Verification

```powershell
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
```

The design check validates theme parity, required token roles, contrast thresholds, icon-manifest parity, SVG structure, and theme-neutral icon coloring.

## Known Gaps

- Production typeface files are not yet bundled; the token stacks use resilient local fallbacks.
- Responsive layouts require implementation-level browser and assistive-technology testing.
- The generated mockup brand mark is not an approved production logo.
- Component-library and chart-library selections remain implementation decisions.
