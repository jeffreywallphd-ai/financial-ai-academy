# Financial AI Academy Iconography

- Status: production asset baseline
- Canonical for: general interface icon geometry, names, semantics, and theme usage
- Sprite: [faa-icons.svg](faa-icons.svg)
- Manifest: [manifest.json](manifest.json)
- Styles: [icons.css](icons.css)
- Two-theme gallery: [preview.html](preview.html)
- Visual rules: [Interface Style Guide](../../../../../docs/design/style-guide.md)

## Pack Characteristics

The pack contains 56 original system icons covering navigation, learning, finance, AI/ML, files, common actions, and feedback states.

- Grid: 24 by 24
- Stroke: 1.75 px
- Caps and joins: round
- Fill: none
- Color: `currentColor`
- Theme strategy: one geometry set for both themes, colored through semantic CSS tokens

The assets contain no embedded light or dark colors. This prevents geometry drift between themes and keeps contrast decisions in the token contract.

Serve this directory over HTTP and open `preview.html` to inspect every icon in both themes. External SVG `use` references may not render when the preview is opened directly through a `file:` URL.

## Production Use

Copy or expose `faa-icons.svg` at a stable same-origin asset URL during the web build. Reference a symbol from a host SVG:

```html
<svg class="faa-icon" aria-hidden="true" focusable="false">
  <use href="/assets/faa-icons.svg#faa-icon-home"></use>
</svg>
```

For an icon-only button, the control owns the accessible name:

```html
<button class="faa-icon-button" type="button" aria-label="Save lesson">
  <svg class="faa-icon" aria-hidden="true" focusable="false">
    <use href="/assets/faa-icons.svg#faa-icon-save"></use>
  </svg>
</button>
```

When an icon itself conveys nonredundant content, put `role="img"` and an accessible name on the host SVG. Do not rely on titles inside reused symbols because browser and assistive-technology support is inconsistent.

## Theme Use

Import [tokens.css](../tokens.css) before [icons.css](icons.css). Use:

- `.faa-icon` for default secondary-text color;
- `.faa-icon--active` for selected navigation or active tools;
- `.faa-icon--accent` for restrained brass emphasis;
- semantic success, warning, and danger modifiers only when the icon represents that state; and
- `.faa-icon-button` for a standard 44 px icon-only control.

Do not apply global inversion, filters, opacity hacks, or hardcoded theme colors to the sprite.

## Semantic Rules

- Reuse one icon for one stable meaning across the application.
- Pair unfamiliar or domain-specific icons with visible text.
- An icon may support a state, but color and icon alone must not be its only label.
- Use `external-link` when an action leaves the current application context.
- Use `data-source` for datasets or providers and `integrations` for connections or plug-ins.
- Use `market-data` for observed market series and `portfolio` for allocation or simulation.
- Use `ai-ml` for model and experiment concepts, not as a generic sparkle on ordinary actions.
- Provider logos, exchange marks, and partner brands are separately licensed assets and are not part of this pack.

## Prohibited Substitutes

Do not use emoji, Unicode symbols, icon fonts, generated raster icons, copied provider marks, or feature-local SVG variants as production controls. If no existing icon is suitable, add a reviewed symbol and update the manifest, documentation, and validation in the same change.

## Change Requirements

1. Preserve the 24 by 24 view box and 1.75 px rounded stroke system.
2. Check legibility at 16, 20, 24, and 32 px in both themes.
3. Keep paths open and simple enough to remain clear at small sizes.
4. Add the symbol to `faa-icons.svg` and a sorted entry to `manifest.json`.
5. Update consuming semantics and screenshots when meaning changes.
6. Run `python dev-tools/design/check_design_system.py`.

The SVG geometry is authored for this project and distributed under the repository license.
