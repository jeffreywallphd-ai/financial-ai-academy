# Context Pack: Interface Design

## Use When

Work affects user-facing layouts, themes, typography, spacing, cards, controls, charts, responsive behavior, accessibility presentation, design tokens, or iconography.

## Preserve

- The style guide and executable semantic tokens govern shared visual decisions.
- Light and dark modes preserve equivalent content, actions, hierarchy, focus, contrast, and responsive behavior.
- Feature code does not create local palettes, spacing scales, shadow systems, theme maps, or icon sets.
- General interface icons come from the reviewed theme-neutral SVG sprite and inherit `currentColor`.
- Learning and provenance remain visually primary; analytical experiences do not imitate brokerage execution interfaces.
- Mockups remain directional and never define behavior, contracts, exact data, or accessibility exceptions.

## Canonical Sources

- `docs/design/README.md`
- `docs/design/style-guide.md`
- `docs/standards/interface-design-standards.md`
- `apps/web/src/design-system/tokens.css`
- `apps/web/src/design-system/icons/README.md`

## Verification

- `python dev-tools/design/check_design_system.py`
- `python dev-tools/documentation/check_docs.py`
- focused browser, keyboard, contrast, zoom, forced-color, reduced-motion, responsive, and assistive-technology checks for implemented UI

## Stop When

Work would treat a mockup as product authority, weaken accessibility or theme parity, invent unresolved financial/provider behavior, or introduce a new shared visual system without synchronizing its canonical sources and consumers.
