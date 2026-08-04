# Interface Style Guide

- Status: accepted
- Canonical for: visual foundations, theme behavior, layout primitives, component presentation, data visualization, and interface accessibility baselines
- Exact executable values: [tokens.css](../../apps/web/src/design-system/tokens.css)
- Icon source: [Financial AI Academy iconography](../../apps/web/src/design-system/icons/README.md)
- Directional references: [interface mockups](mockups/README.md)

## Design Character

Financial AI Academy should feel trustworthy, scholarly, calm, and modern. The interface combines an editorial reading experience with precise analytical tools:

- warm ivory and cream surfaces in light mode;
- near-black green and dark pine surfaces in dark mode;
- deep forest green as the primary identity color;
- restrained antique brass for emphasis, not decoration everywhere;
- serif display headings paired with compact sans-serif interface text;
- fine borders and controlled whitespace instead of heavy shadows;
- charts that feel analytical without resembling a brokerage terminal; and
- prominent provenance, educational-use, and AI-limitation cues.

The learner's next meaningful action should be clearer than secondary metrics. Dense analytical pages may show more information, but must retain hierarchy and breathing room.

## Design Principles

1. **Learning before trading.** Do not use buy/sell language, brokerage account patterns, profit celebrations, or urgency cues.
2. **Evidence before assertion.** Show sources, timestamps, assumptions, confidence, and review status near financial or AI-generated information.
3. **Semantic tokens before raw values.** Components consume `--faa-*` variables and do not embed arbitrary colors or spacing.
4. **Theme parity.** Light and dark modes contain the same information, hierarchy, states, and affordances.
5. **Borders before elevation.** Cards use one-pixel borders and subtle surface shifts. Reserve shadows for overlays and rare raised content.
6. **Accessible by construction.** Text contrast, focus visibility, target size, non-color state cues, reduced motion, and chart alternatives are baseline requirements.
7. **Progress without pressure.** Learning progress is encouraging and private; avoid competitive rankings or punitive red dashboards.

## Theme Contract

Use `data-theme="light"`, `data-theme="dark"`, or `data-theme="system"` on the document root. System mode follows `prefers-color-scheme`. Persist an explicit learner choice without changing content or component structure.

Feature code must use semantic variables from [tokens.css](../../apps/web/src/design-system/tokens.css). Raw hex values in component styles require a documented design-system change.

### Core Color Roles

| Semantic role | Light | Dark | Intended use |
| --- | --- | --- | --- |
| Canvas | `#F7F4EC` | `#081713` | Application background |
| Surface | `#FFFDF8` | `#0E211B` | Standard cards and reading surfaces |
| Raised surface | `#FFFFFF` | `#132A22` | Menus, active panels, overlays |
| Subtle surface | `#F1ECDD` | `#10261F` | Grouping, quiet callouts, table headers |
| Selected surface | `#E6EFE9` | `#1B3B30` | Selected rows, tabs, navigation states |
| Primary text | `#14231C` | `#F7F3E8` | Headings and essential content |
| Secondary text | `#43534A` | `#C4CEC6` | Body copy and labels |
| Muted text | `#65736B` | `#97A69C` | Metadata; never disabled text by opacity alone |
| Border | `#D9D2C2` | `#2D4A3F` | Cards, dividers, control outlines |
| Strong border | `#AFA58F` | `#4C6B5E` | Hover, emphasis, dense tables |
| Forest brand | `#0F4D3A` | `#75C08F` | Identity, links, active icons |
| Brass accent | `#C79A3B` | `#D6AD55` | Primary emphasis and highlighted data |
| Focus ring | `#1F6A50` | `#E0BC69` | Keyboard focus only |
| Success | `#287A4B` | `#75C08F` | Completed, healthy, correct |
| Warning | `#7A5700` | `#E0B85A` | Caution and review needed |
| Danger | `#A63D39` | `#F08B80` | Destructive or failed states |
| Information | `#285F8F` | `#82B4D9` | Neutral system information |

The executable tokens include hover, active, surface, navigation, chart, and foreground companions. Normal text combinations in the token file are validated at WCAG AA contrast or better. Decorative brass must not be used for small text on ivory unless the semantic foreground token passes contrast.

### Theme Behavior

- Do not implement dark mode by inverting colors or lowering global opacity.
- Preserve the same elevation ordering in both themes.
- Use brass more visibly for dark-mode primary actions and selection outlines; use forest green for light-mode primary actions.
- Charts must switch to the theme-specific series tokens.
- Images and provider logos need reviewed dark-mode treatments; do not apply automatic inversion to brand marks.
- Respect operating-system forced-color and contrast settings.

## Typography

### Families

| Role | Token | Stack |
| --- | --- | --- |
| Display | `--faa-font-display` | `Georgia, Cambria, "Times New Roman", serif` |
| Interface/body | `--faa-font-sans` | `Inter, ui-sans-serif, system-ui, sans-serif` |
| Data/code | `--faa-font-mono` | `"SFMono-Regular", Consolas, "Liberation Mono", monospace` |

The stacks are operational fallbacks, not a license to download fonts without dependency and license review.

### Type Scale

| Style | Size / line height | Weight | Use |
| --- | --- | --- | --- |
| Display | 48 / 56 px | 600 | Rare landing or major feature title |
| Page title | 36 / 44 px | 600 | Desktop page heading |
| Section title | 28 / 36 px | 600 | Major section |
| Card title | 20 / 28 px | 600 | Card and panel headings |
| Body large | 18 / 28 px | 400 | Lesson lead and important explanations |
| Body | 16 / 24 px | 400 | Default reading text |
| UI | 14 / 20 px | 500 | Controls, navigation, table text |
| Caption | 12 / 16 px | 500 | Metadata and helper labels |
| Data | 14 / 20 px | 500 | Tables and metrics, tabular numerals |

Use the serif family for page, section, and editorial card headings. Use sans-serif for navigation, controls, body text, tables, and dense analytical labels. Use tabular numerals for metrics, dates, percentages, money, and aligned tables.

Keep lesson reading lines between 55 and 75 characters. Never reduce essential explanatory text below 16 px.

## Spacing and Sizing

Use the 4 px base scale from `tokens.css`.

| Token step | Value | Typical use |
| --- | --- | --- |
| 1 | 4 px | Icon micro-gap |
| 2 | 8 px | Inline controls and compact metadata |
| 3 | 12 px | Compact card gaps |
| 4 | 16 px | Default control and compact card padding |
| 5 | 20 px | Comfortable component gap |
| 6 | 24 px | Standard card padding and grid gutter |
| 8 | 32 px | Section gap and desktop page gutter |
| 10 | 40 px | Large section separation |
| 12 | 48 px | Page rhythm |
| 16 | 64 px | Major layout separation |

Do not introduce intermediate spacing values unless a component has a documented optical requirement.

### Control and Icon Sizes

- Default interactive target: at least 44 by 44 px.
- Compact desktop control: 40 px only when an adjacent 44 px target or row target preserves usability.
- Standard input and primary button: 44 px high.
- Standard icon: 20 px; compact 16 px; navigation 20 or 24 px; feature icon 32 px.
- Icon-only controls require an accessible name and visible tooltip.

### Corners and Borders

| Role | Radius |
| --- | --- |
| Small chip or compact control | 6 px |
| Input and button | 8 px |
| Standard card | 12 px |
| Large feature panel or modal | 16 px |
| Pill and circular control | 999 px |

Standard borders are 1 px. Use 2 px only for selection or explicit emphasis. Avoid decorative double borders.

## Application Layout

### Shell

- Expanded navigation: 240 px.
- Compact navigation: 72 px.
- Top utility bar: 64 px.
- Maximum content width: 1440 px.
- Desktop page gutter: 32 px, increasing to 48 px on very wide screens.
- Standard grid: 12 columns with 24 px gutters.

The navigation uses the dedicated navigation tokens and retains strong separation from the canvas. Active navigation combines icon, text, and selected surface; color alone is insufficient.

### Page Templates

| Template | Grid | Intended pages |
| --- | --- | --- |
| Dashboard | 8-column primary plus 4-column rail | Dashboard, progress |
| Reading | minmax(0, 1fr) plus 320 px assistant rail | Lessons and methodology |
| Analytical | 9-column primary plus 3-column provenance/actions rail | Market data, portfolio, AI/ML labs |
| Catalog | 12-column search/filter header plus responsive card grid | Learning library, projects |
| Workspace | 8-column artifact table plus 4-column folders/activity rail | Saved work |
| Settings | 8-column settings forms plus 4-column summary rail | Profile and integrations |

Keep important content in the primary column. Side rails support context, provenance, and secondary actions; they must not contain the only route to completing a task.

### Responsive Breakpoints

| Name | Minimum width | Behavior |
| --- | --- | --- |
| Small | 0 | Single column; navigation drawer; full-width controls |
| Medium | 640 px | Two-column compact grids where content permits |
| Large | 1024 px | Compact navigation; rails move below primary content when needed |
| Extra large | 1280 px | Expanded navigation and primary/rail layouts |
| Wide | 1536 px | Larger outer gutters; content does not stretch beyond maximum width |

At narrow widths, preserve reading order: title, task controls, primary content, supporting rail. Tables require responsive columns, card views, or horizontal scrolling with a visible cue; never shrink text to fit.

## Cards and Panels

### Base Card

- Surface color: `--faa-color-surface`.
- Border: 1 px `--faa-color-border`.
- Radius: `--faa-radius-card` (12 px).
- Padding: 24 px, or 16 px for documented compact cards.
- Shadow: none by default.

### Variants

| Variant | Presentation |
| --- | --- |
| Quiet | Subtle surface, standard border, no shadow |
| Interactive | Base card plus hover border and subtle selected-surface shift |
| Selected | Selected surface with 2 px active outline and non-color state cue |
| Metric | Compact label, tabular primary value, comparison and time context |
| Notice | Semantic icon, title, body, and optional action; status surface plus border |
| Raised | Raised surface and small shadow; reserved for menus, overlays, and draggable items |
| Data panel | Tight header, chart/table body, provenance or timestamp footer |

Do not nest more than two visible card levels. Prefer dividers and headings inside a larger card when repeated boxes would create visual noise.

## Controls and States

- Primary actions use `--faa-color-action-primary` and its foreground token.
- Secondary actions use a surface, strong border, and primary text.
- Tertiary actions look like links or quiet buttons but retain a 44 px target.
- Destructive actions require the danger role and confirmation proportional to reversibility.
- Disabled controls use explicit disabled tokens and remain readable; do not use opacity below 60 percent for text.
- Hover never replaces focus. Keyboard focus uses a 3 px ring with a 2 px offset.
- Loading states preserve layout and provide text for longer operations.
- Empty states explain what is absent, why it matters, and the next safe action.

## Navigation, Tabs, and Filters

- Keep primary navigation stable across learner pages.
- Show at most one primary selected state per navigation level.
- Tabs represent peer views, not sequential steps.
- Steppers represent ordered work and must expose completed, current, and unavailable states in text.
- Filter chips include a visible selected or removable state.
- Breadcrumbs describe location and do not replace the page title.

## Data Tables and Metrics

- Align numeric columns right and labels left.
- Use tabular numerals and consistent decimal precision based on domain rules.
- Always show units, effective date/time, currency, frequency, and adjustment basis when relevant.
- Sticky headers are allowed on long tables; the first column should remain visible only when it materially aids comparison.
- Positive and negative values need signs or labels in addition to color.
- Sample or simulated values must be visibly identified.

## Charts and Financial Visualizations

Use the five theme-specific chart series tokens in order. Both palettes exceed 3:1 contrast against their canvases:

| Series | Light | Dark |
| --- | --- | --- |
| 1 | `#0F4D3A` | `#7BC09A` |
| 2 | `#9A6410` | `#E0B85A` |
| 3 | `#2C6E9B` | `#84B7D8` |
| 4 | `#76508F` | `#C39BE3` |
| 5 | `#A5483F` | `#F08F85` |

- Do not communicate meaning through color alone; pair series with labels, line styles, markers, or patterns.
- Use direct labels where space permits and keep legends close to plots.
- Grid lines are quiet and never compete with data.
- Tooltips are keyboard accessible and provide the same values through a table or textual summary.
- Do not use misleading truncated axes, decorative 3D charts, or unlabeled dual axes.
- Market observations, simulations, and model predictions must be visually distinguishable.

## Iconography

Use only the reviewed [SVG iconography pack](../../apps/web/src/design-system/icons/README.md) for general interface icons.

- Geometry is 24 by 24 with a 1.75 px rounded stroke.
- Icons inherit `currentColor`; light/dark colors come from semantic tokens.
- Keep icons at one color unless a documented status treatment requires an adjacent badge.
- Do not use emoji, Unicode symbols, icon fonts, screenshots, or provider logos as substitutes.
- Pair unfamiliar icons with text.
- Provider and partner marks are separate licensed assets and are not part of the system icon pack.

## Motion

- Standard transition: 160 ms; deliberate panel transition: 240 ms.
- Use ease-out for entrances and ease-in for exits.
- Motion may clarify state or spatial relationships but must not be required to understand a result.
- Honor `prefers-reduced-motion: reduce` by removing nonessential movement and animated chart interpolation.
- Avoid pulsing market values, celebratory confetti, parallax, and urgency animations.

## Accessibility Baseline

- Meet WCAG 2.2 AA for supported flows, with normal text at 4.5:1 and large text or meaningful graphics at 3:1.
- Keep focus visible, logical, and untrapped.
- Use landmarks, headings, labels, descriptions, and live regions appropriately.
- Provide names for icon-only controls and alternatives for charts.
- Do not use color, position, or motion as the only state signal.
- Support 200 percent zoom and reflow without loss of functionality.
- Respect forced colors, reduced motion, text scaling, and keyboard-only use.
- Validate both themes independently; passing light mode does not qualify dark mode.

## Content and Tone

- Prefer direct educational language over promotional language.
- Mark simulations, samples, and fictional assets clearly.
- Place education-versus-advice notices near the relevant experience without overwhelming every card.
- State AI limitations and cite sources where AI output appears.
- Use sentence case for controls and headings.
- Use concise action labels that describe outcomes, such as "Save dataset" or "Continue lesson".

## Change Checklist

When adding or changing a shared interface pattern:

1. Confirm that an existing semantic token, layout, card, control, or icon cannot satisfy the need.
2. Update this guide if the visual rule changes.
3. Update `tokens.css`, icon assets, and manifests when their contracts change.
4. Update consuming components and both theme states.
5. Verify keyboard, screen-reader, zoom, forced-color, reduced-motion, and chart alternatives as applicable.
6. Run `python dev-tools/design/check_design_system.py` and `python dev-tools/documentation/check_docs.py`.

Do not use a generated mockup as the sole justification for a new production rule.
